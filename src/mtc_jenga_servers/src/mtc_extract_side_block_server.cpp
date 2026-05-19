#include <atomic>
#include <chrono>
#include <cmath>
#include <memory>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <jenga_interfaces/action/jenga_extract_side_block.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>

#include <Eigen/Geometry>

#include "mtc_jenga_servers/mtc_server_common.hpp"

namespace mtc = moveit::task_constructor;
using JengaExtractSideBlock = jenga_interfaces::action::JengaExtractSideBlock;
using ServerGoalHandle = rclcpp_action::ServerGoalHandle<JengaExtractSideBlock>;

namespace {

Eigen::Isometry3d rpyToIso(const double r, const double p, const double y) {
  Eigen::Isometry3d t = Eigen::Isometry3d::Identity();
  t.linear() = (Eigen::AngleAxisd(y, Eigen::Vector3d::UnitZ()) *
                Eigen::AngleAxisd(p, Eigen::Vector3d::UnitY()) *
                Eigen::AngleAxisd(r, Eigen::Vector3d::UnitX()))
                   .toRotationMatrix();
  return t;
}

std::optional<Eigen::Vector3d> axisToLocalVec(const std::string& axis) {
  if (axis.empty()) return std::nullopt;
  const bool neg = axis[0] == '-';
  const char a = (neg ? (axis.size() > 1 ? axis[1] : '\0') : axis[0]);
  const double s = neg ? -1.0 : 1.0;
  if (a == 'x') return Eigen::Vector3d{s, 0.0, 0.0};
  if (a == 'y') return Eigen::Vector3d{0.0, s, 0.0};
  if (a == 'z') return Eigen::Vector3d{0.0, 0.0, s};
  return std::nullopt;
}

geometry_msgs::msg::Vector3Stamped axisToDirInFrame(const std::string& axis_local,
                                                    const geometry_msgs::msg::PoseStamped& pose_in_frame,
                                                    const std::string& fallback_frame_id) {
  geometry_msgs::msg::Vector3Stamped v;
  v.header.frame_id = pose_in_frame.header.frame_id.empty() ? fallback_frame_id : pose_in_frame.header.frame_id;

  v.vector.x = 0.0;
  v.vector.y = 0.0;
  v.vector.z = 0.0;

  const auto local = axisToLocalVec(axis_local);
  if (!local) return v;

  const auto& q = pose_in_frame.pose.orientation;
  const Eigen::Quaterniond qe(q.w, q.x, q.y, q.z);
  const Eigen::Vector3d world = qe.normalized() * (*local);
  v.vector.x = world.x();
  v.vector.y = world.y();
  v.vector.z = world.z();
  return v;
}

}  // namespace

class MtcExtractSideBlockServer : public rclcpp::Node {
 public:
  explicit MtcExtractSideBlockServer(
      const rclcpp::NodeOptions& options =
          rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true))
  : rclcpp::Node("mtc_extract_side_block_server", options) {
    action_name_ = mtc_jenga::param<std::string>(this, "action_name", "jenga_extract_side_block");
    ur_onrobot_manipulator_ = mtc_jenga::param<std::string>(this, "arm_group", "ur_onrobot_manipulator");
    ur_onrobot_gripper_ = mtc_jenga::param<std::string>(this, "hand_group", "ur_onrobot_gripper");
    gripper_tcp_ = mtc_jenga::param<std::string>(this, "gripper_tcp", "gripper_tcp");
    open_state_ = mtc_jenga::param<std::string>(this, "gripper_open_state", "open");
    closed_state_ = mtc_jenga::param<std::string>(this, "gripper_closed_state", "grip_block_length");
    arm_home_state_ = mtc_jenga::param<std::string>(this, "arm_home_state", "test_configuration");

    box_x_ = mtc_jenga::param<double>(this, "block_box_x", 0.075);
    box_y_ = mtc_jenga::param<double>(this, "block_box_y", 0.025);
    box_z_ = mtc_jenga::param<double>(this, "block_box_z", 0.015);

    plan_max_attempts_ = static_cast<uint32_t>(mtc_jenga::param<int>(this, "plan_max_attempts", 1));
    plan_time_ = mtc_jenga::param<double>(this, "plan_time", 0.5);
    vel_scale_ = mtc_jenga::param<double>(this, "max_velocity_scaling_factor", 0.1);
    acc_scale_ = mtc_jenga::param<double>(this, "max_acceleration_scaling_factor", 0.1);
    cart_step_ = mtc_jenga::param<double>(this, "cartesian_step", 0.005);

    approach_min_ = mtc_jenga::param<double>(this, "approach_distance_min", 0.01);
    approach_max_ = mtc_jenga::param<double>(this, "approach_distance_max", 0.05);
    extract_min_ = mtc_jenga::param<double>(this, "extract_distance_min", 0.03);
    extract_max_ = mtc_jenga::param<double>(this, "extract_distance_max", 0.10);
    lift_after_extract_ = mtc_jenga::param<double>(this, "lift_after_extract_z", 0.0);

    // Use object frame axis by default (pull along block +X).
    extract_axis_ = mtc_jenga::param<std::string>(this, "extract_axis", "x");  // x|y|z|-x|-y|-z
    approach_axis_ = mtc_jenga::param<std::string>(this, "approach_axis", "-x");
    grasp_r_ = mtc_jenga::param<double>(this, "grasp_frame_roll", 0.0);
    grasp_p_ = mtc_jenga::param<double>(this, "grasp_frame_pitch", M_PI / 2.0);
    grasp_y_ = mtc_jenga::param<double>(this, "grasp_frame_yaw", 0.0);
    grasp_angle_delta_ = mtc_jenga::param<double>(this, "grasp_angle_delta", M_PI / 1.0);

    status_topic_ = mtc_jenga::param<std::string>(this, "status_topic", "mtc_extract_side_status");
    pub_status_ = create_publisher<std_msgs::msg::String>(status_topic_, 10);

    sub_estop_ = create_subscription<std_msgs::msg::Bool>(
        "/estop", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });
    sub_estop_active_ = create_subscription<std_msgs::msg::Bool>(
        "/estop_active", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });

    action_server_ = rclcpp_action::create_server<JengaExtractSideBlock>(
        this, action_name_,
        [this](const rclcpp_action::GoalUUID&, std::shared_ptr<const JengaExtractSideBlock::Goal>) {
          if (busy_.load() || estop_.load()) return rclcpp_action::GoalResponse::REJECT;
          return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        [this](const std::shared_ptr<ServerGoalHandle>) { return rclcpp_action::CancelResponse::ACCEPT; },
        [this](std::shared_ptr<ServerGoalHandle> h) { onActionAccepted(std::move(h)); });

    publishStatus("idle");
    RCLCPP_INFO(get_logger(), "mtc_extract_side_block_server: action=%s status=%s",
                action_name_.c_str(), status_topic_.c_str());
  }

 private:
  void publishStatus(const std::string& phase) {
    std_msgs::msg::String m;
    std::ostringstream o;
    o << "{\"state\":\"" << phase << "\",\"busy\":" << (busy_.load() ? "true" : "false")
      << ",\"executions_completed\":" << executions_completed_.load()
      << ",\"estop_active\":" << (estop_.load() ? "true" : "false") << "}";
    m.data = o.str();
    pub_status_->publish(m);
  }

  void setBusy(const bool b) {
    busy_.store(b);
    publishStatus(b ? "running" : "idle");
  }

  mtc::Task buildExtractTask(const std::string& block_id,
                             const geometry_msgs::msg::PoseStamped& place_in_world,
                             const geometry_msgs::msg::PoseStamped& block_pose) {
    mtc::Task task;
    task.stages()->setName("jenga_extract_side_block");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);

    task.setProperty("group", ur_onrobot_manipulator_);
    task.setProperty("eef", ur_onrobot_gripper_);
    task.setProperty("ik_frame", gripper_tcp_);

    mtc::Stage* current_state_ptr = nullptr;
    auto stage_state_current = std::make_unique<mtc::stages::CurrentState>("current");
    current_state_ptr = stage_state_current.get();
    task.add(std::move(stage_state_current));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarPathLengthOptimized");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", 2.0);
    sampling_planner->setProperty("enforce_joint_model_state_space", true);
    sampling_planner->setMaxVelocityScalingFactor(vel_scale_);
    sampling_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto interpolation_planner = std::make_shared<mtc::solvers::JointInterpolationPlanner>();
    interpolation_planner->setMaxVelocityScalingFactor(vel_scale_);
    interpolation_planner->setMaxAccelerationScalingFactor(acc_scale_);
    auto cartesian_planner = std::make_shared<mtc::solvers::CartesianPath>();
    cartesian_planner->setMaxVelocityScalingFactor(vel_scale_);
    cartesian_planner->setMaxAccelerationScalingFactor(acc_scale_);
    cartesian_planner->setStepSize(cart_step_);

    {
      auto stage_open = std::make_unique<mtc::stages::MoveTo>("open hand", interpolation_planner);
      stage_open->setGroup(ur_onrobot_gripper_);
      stage_open->setGoal(open_state_);
      task.add(std::move(stage_open));
    }
    {
      auto c = std::make_unique<mtc::stages::Connect>(
          "move to pre-grasp", mtc::stages::Connect::GroupPlannerVector{{ur_onrobot_manipulator_, sampling_planner}});
      c->setTimeout(plan_time_);
      c->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(c));
    }

    mtc::Stage* attach_object_stage = nullptr;
    {
      auto grasp = std::make_unique<mtc::SerialContainer>("side grasp + extract");
      task.properties().exposeTo(grasp->properties(), {"eef", "group", "ik_frame"});
      grasp->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group", "ik_frame"});

      {
        auto stage = std::make_unique<mtc::stages::GenerateGraspPose>("generate grasp pose");
        stage->properties().configureInitFrom(mtc::Stage::PARENT);
        stage->properties().set("marker_ns", "grasp_pose");
        stage->setPreGraspPose(open_state_);
        stage->setObject(block_id);
        stage->setAngleDelta(grasp_angle_delta_);
        stage->setMonitoredStage(current_state_ptr);

        auto w = std::make_unique<mtc::stages::ComputeIK>("grasp IK", std::move(stage));
        w->setMaxIKSolutions(8);
        w->setMinSolutionDistance(0.5);
        w->setIKFrame(rpyToIso(grasp_r_, grasp_p_, grasp_y_), gripper_tcp_);
        w->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        w->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        grasp->insert(std::move(w));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("approach (horizontal)", cartesian_planner);
        stage->properties().set("marker_ns", "approach");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(approach_min_, approach_max_);
        stage->setDirection(axisToDirInFrame(approach_axis_, block_pose, "world"));
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("allow collision (hand,block)");
        stage->allowCollisions(block_id,
                               task.getRobotModel()->getJointModelGroup(ur_onrobot_gripper_)
                                   ->getLinkModelNamesWithCollisionGeometry(),
                               true);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveTo>("close hand", interpolation_planner);
        stage->setGroup(ur_onrobot_gripper_);
        stage->setGoal(closed_state_);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("attach block");
        stage->attachObject(block_id, gripper_tcp_);
        attach_object_stage = stage.get();
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("extract (pull out)", cartesian_planner);
        stage->properties().set("marker_ns", "extract");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(extract_min_, extract_max_);
        stage->setDirection(axisToDirInFrame(extract_axis_, block_pose, "world"));
        grasp->insert(std::move(stage));
      }
      if (lift_after_extract_ > 1e-6) {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("lift after extract", cartesian_planner);
        stage->properties().set("marker_ns", "lift_after_extract");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(lift_after_extract_, lift_after_extract_);
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = "world";
        vec.vector.z = 1.0;
        stage->setDirection(vec);
        grasp->insert(std::move(stage));
      }
      task.add(std::move(grasp));
    }

    {
      auto c = std::make_unique<mtc::stages::Connect>(
          "move to place", mtc::stages::Connect::GroupPlannerVector{{ur_onrobot_manipulator_, sampling_planner}});
      c->setTimeout(plan_time_);
      c->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(c));
    }
    {
      auto place = std::make_unique<mtc::SerialContainer>("place");
      task.properties().exposeTo(place->properties(), {"eef", "group", "ik_frame"});
      place->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group", "ik_frame"});

      {
        auto stage = std::make_unique<mtc::stages::GeneratePlacePose>("generate place pose");
        stage->properties().configureInitFrom(mtc::Stage::PARENT);
        stage->properties().set("marker_ns", "place_pose");
        stage->setObject(block_id);
        stage->setPose(place_in_world);
        stage->setMonitoredStage(attach_object_stage);
        auto w = std::make_unique<mtc::stages::ComputeIK>("place IK", std::move(stage));
        w->setMaxIKSolutions(8);
        w->setMinSolutionDistance(0.5);
        w->setIKFrame(block_id);
        w->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        w->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        place->insert(std::move(w));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveTo>("open hand (place)", interpolation_planner);
        stage->setGroup(ur_onrobot_gripper_);
        stage->setGoal(open_state_);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("forbid collision (hand,block)");
        stage->allowCollisions(block_id,
                               task.getRobotModel()->getJointModelGroup(ur_onrobot_gripper_)
                                   ->getLinkModelNamesWithCollisionGeometry(),
                               false);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("detach block");
        stage->detachObject(block_id, gripper_tcp_);
        place->insert(std::move(stage));
      }
      task.add(std::move(place));
    }

    {
      auto stage = std::make_unique<mtc::stages::MoveTo>("return home", sampling_planner);
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setGoal(arm_home_state_);
      stage->setTimeout(plan_time_);
      task.add(std::move(stage));
    }

    return task;
  }

  bool runExtractMtc(const geometry_msgs::msg::PoseStamped& block_pose,
                     const geometry_msgs::msg::PoseStamped& place_pose,
                     const std::string& block_id) {
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop active: refusing to plan/execute MTC task");
      return false;
    }
    if (!axisToLocalVec(approach_axis_)) {
      RCLCPP_ERROR(get_logger(), "Invalid approach_axis: '%s' (expected x|y|z|-x|-y|-z)", approach_axis_.c_str());
      return false;
    }
    if (!axisToLocalVec(extract_axis_)) {
      RCLCPP_ERROR(get_logger(), "Invalid extract_axis: '%s' (expected x|y|z|-x|-y|-z)", extract_axis_.c_str());
      return false;
    }
    mtc_jenga::applyBlockBoxAt(block_id, block_pose.header.frame_id, block_pose.pose, box_x_, box_y_, box_z_);

    mtc::Task task = buildExtractTask(block_id, place_pose, block_pose);
    try {
      task.init();
    } catch (const mtc::InitStageException& e) {
      RCLCPP_ERROR(get_logger(), "MTC init failed: %s", e.what());
      return false;
    }
    if (!task.plan(plan_max_attempts_) || task.solutions().empty()) {
      RCLCPP_ERROR(get_logger(), "MTC plan failed");
      return false;
    }
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop became active after planning; skipping execution");
      return false;
    }

    mtc_jenga::retimeArmSubTrajectoriesWithTotg(*task.solutions().front(),
                                                ur_onrobot_manipulator_, vel_scale_, acc_scale_, get_logger());

    task.introspection().publishSolution(*task.solutions().front());
    auto res = task.execute(*task.solutions().front());
    if (res.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "MTC execute failed: %d", res.val);
      return false;
    }
    // Persist the block at its placed pose for subsequent plans.
    mtc_jenga::applyBlockBoxAt(block_id, place_pose.header.frame_id, place_pose.pose, box_x_, box_y_, box_z_);
    return true;
  }

  void onActionAccepted(std::shared_ptr<ServerGoalHandle> handle) {
    if (!handle) return;
    std::thread{[this, h = std::move(handle)]() { executeAction(h); }}.detach();
  }

  void executeAction(const std::shared_ptr<ServerGoalHandle> goal_handle) {
    setBusy(true);
    auto res = std::make_shared<JengaExtractSideBlock::Result>();
    if (estop_.load()) {
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
      setBusy(false);
      return;
    }

    const auto goal = goal_handle->get_goal();
    auto fb = std::make_shared<JengaExtractSideBlock::Feedback>();
    auto send_fb = [goal_handle, &fb](const char* s, const float p) {
      fb->current_stage = s;
      fb->progress_pct = p;
      goal_handle->publish_feedback(fb);
    };

    send_fb("extract_side_start", 0.0F);
    const std::string block_id = mtc_jenga::blockIdFromIndex(goal->block_index);
    const bool ok = runExtractMtc(goal->block_pose, goal->place_pose, block_id);
    send_fb("extract_side_done", 100.0F);

    if (estop_.load()) {
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
    } else if (ok) {
      res->success = true;
      res->message = "ok";
      res->error_code = 0;
      executions_completed_ += 1;
      goal_handle->succeed(res);
    } else {
      res->success = false;
      res->message = "mtc failed";
      res->error_code = 1;
      goal_handle->abort(res);
    }

    setBusy(false);
  }

  rclcpp_action::Server<JengaExtractSideBlock>::SharedPtr action_server_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;

  std::string action_name_;
  std::string ur_onrobot_manipulator_;
  std::string ur_onrobot_gripper_;
  std::string gripper_tcp_;
  std::string open_state_;
  std::string closed_state_;
  std::string arm_home_state_;
  std::string status_topic_;

  double box_x_{0.075}, box_y_{0.025}, box_z_{0.015};
  uint32_t plan_max_attempts_{3};
  double plan_time_{0.5};
  double vel_scale_{0.25};
  double acc_scale_{0.25};
  double cart_step_{0.005};

  double approach_min_{0.01}, approach_max_{0.05};
  double extract_min_{0.03}, extract_max_{0.10};
  double lift_after_extract_{0.0};
  std::string extract_axis_{"x"};
  std::string approach_axis_{"-x"};
  double grasp_r_{0.0}, grasp_p_{M_PI / 2.0}, grasp_y_{0.0};
  double grasp_angle_delta_{M_PI / 1.0};

  std::atomic<bool> busy_{false};
  std::atomic<int> executions_completed_{0};
  std::atomic<bool> estop_{false};
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto n = std::make_shared<MtcExtractSideBlockServer>();
  rclcpp::executors::MultiThreadedExecutor e(rclcpp::ExecutorOptions(), 4u);
  e.add_node(n);
  e.spin();
  rclcpp::shutdown();
  return 0;
}
