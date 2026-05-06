#include <atomic>
#include <chrono>
#include <cmath>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <jenga_interfaces/action/jenga_extract_middle_block.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>
#include <tf2/LinearMath/Transform.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

#include <Eigen/Geometry>

#include "mtc_jenga_servers/mtc_server_common.hpp"

namespace mtc = moveit::task_constructor;
using JengaExtractMiddleBlock = jenga_interfaces::action::JengaExtractMiddleBlock;
using ServerGoalHandle = rclcpp_action::ServerGoalHandle<JengaExtractMiddleBlock>;

namespace {

Eigen::Isometry3d rpyToIso(const double r, const double p, const double y) {
  Eigen::Isometry3d t = Eigen::Isometry3d::Identity();
  t = t * (Eigen::AngleAxisd(y, Eigen::Vector3d::UnitZ()) *
            Eigen::AngleAxisd(p, Eigen::Vector3d::UnitY()) *
            Eigen::AngleAxisd(r, Eigen::Vector3d::UnitX()));
                // .toRotationMatrix();
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

class MtcExtractMiddleBlockServer : public rclcpp::Node {
 public:
  explicit MtcExtractMiddleBlockServer(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : rclcpp::Node("mtc_extract_middle_block_server", options) {
    action_name_ = declare_parameter("action_name", "jenga_extract_middle_block");
    arm_group_name = declare_parameter("arm_group", "ur_onrobot_manipulator");
    hand_group_name = declare_parameter("hand_group", "ur_onrobot_gripper");
    hand_frame = declare_parameter("gripper_tcp", "gripper_tcp");
    open_state_ = declare_parameter("gripper_open_state", "open");
    closed_state_ = declare_parameter("gripper_closed_state", "grip_block_width");
    arm_home_state_ = declare_parameter("arm_home_state", "ready_position");

    box_x_ = declare_parameter("block_box_x", 0.075);
    box_y_ = declare_parameter("block_box_y", 0.025);
    box_z_ = declare_parameter("block_box_z", 0.015);

    plan_max_attempts_ = static_cast<uint32_t>(declare_parameter("plan_max_attempts", 3));
    vel_scale_ = declare_parameter("max_velocity_scaling_factor", 0.1);
    acc_scale_ = declare_parameter("max_acceleration_scaling_factor", 0.1);
    cart_step_ = declare_parameter("cartesian_step", 0.004);

    approach_min_ = declare_parameter("approach_distance_min", 0.005);
    approach_max_ = declare_parameter("approach_distance_max", 0.03);
    extract_min_ = declare_parameter("extract_distance_min", 0.06);
    extract_max_ = declare_parameter("extract_distance_max", 0.10);
    lift_after_extract_ = declare_parameter("lift_after_extract_z", 0.0);

    extract_axis_ = declare_parameter("extract_axis", "x");
    approach_axis_ = declare_parameter("approach_axis", "-x");
    grasp_r_ = declare_parameter("grasp_frame_roll", 0.0);
    grasp_p_ = declare_parameter("grasp_frame_pitch", M_PI / 1.0);
    grasp_y_ = declare_parameter("grasp_frame_yaw", 0.0);
    grasp_angle_delta_ = declare_parameter("grasp_angle_delta", M_PI / 1.0);
    grasp_offset_m_ = declare_parameter("grasp_offset_m", 0.03);
    grasp_offset_z_ = declare_parameter("grasp_offset_z", 0.01);

    wiggle_enable_ = declare_parameter("wiggle_enable", false);
    wiggle_distance_ = declare_parameter("wiggle_distance", 0.003);

    status_topic_ = declare_parameter("status_topic", "mtc_extract_middle_status");
    pub_status_ = create_publisher<std_msgs::msg::String>(status_topic_, 10);

    sub_estop_ = create_subscription<std_msgs::msg::Bool>(
        "/estop", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });
    sub_estop_active_ = create_subscription<std_msgs::msg::Bool>(
        "/estop_active", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });

    action_server_ = rclcpp_action::create_server<JengaExtractMiddleBlock>(
        this, action_name_,
        [this](const rclcpp_action::GoalUUID&, std::shared_ptr<const JengaExtractMiddleBlock::Goal>) {
          if (busy_.load() || estop_.load()) return rclcpp_action::GoalResponse::REJECT;
          return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        [this](const std::shared_ptr<ServerGoalHandle>) { return rclcpp_action::CancelResponse::ACCEPT; },
        [this](std::shared_ptr<ServerGoalHandle> h) { onActionAccepted(std::move(h)); });

    publishStatus("idle");
    RCLCPP_INFO(get_logger(), "mtc_extract_middle_block_server: action=%s status=%s",
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
    task.stages()->setName("jenga_extract_middle_block");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);

    task.setProperty("group", arm_group_name);
    task.setProperty("eef", hand_group_name);
    task.setProperty("ik_frame", hand_frame);

    mtc::Stage* current_state_ptr = nullptr;
    auto stage_state_current = std::make_unique<mtc::stages::CurrentState>("current");
    current_state_ptr = stage_state_current.get();
    task.add(std::move(stage_state_current));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarkConfigDefault");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", 1.0);
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
      stage_open->setGroup(hand_group_name);
      stage_open->setGoal(open_state_);
      task.add(std::move(stage_open));
    }
    {
      auto c = std::make_unique<mtc::stages::Connect>(
          "move to pre-grasp", mtc::stages::Connect::GroupPlannerVector{{arm_group_name, sampling_planner}});
      c->setTimeout(2.0);
      c->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(c));
    }

    mtc::Stage* attach_object_stage = nullptr;
    {
      auto grasp = std::make_unique<mtc::SerialContainer>("middle grasp + extract");
      task.properties().exposeTo(grasp->properties(), {"eef", "group", "ik_frame"});
      grasp->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group", "ik_frame"});

      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("approach", cartesian_planner);
        stage->properties().set("marker_ns", "approach");
        stage->properties().set("link", hand_frame);
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        // stage->setIKFrame(hand_frame);
        stage->setMinMaxDistance(approach_min_, approach_max_);
        // stage->setDirection(axisToDirInFrame(approach_axis_, block_pose, "world"));
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = hand_frame;
        vec.vector.z = 1.0;
        stage->setDirection(vec);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::GenerateGraspPose>("generate grasp pose");
        stage->properties().configureInitFrom(mtc::Stage::PARENT);
        stage->properties().set("marker_ns", "grasp_pose");
        stage->setPreGraspPose(open_state_);
        const bool extract_positive = extract_axis_.empty() ? true : (extract_axis_[0] != '-');
        const std::string subframe = extract_positive ? "end_plus" : "end_minus";
        stage->setObject(block_id + "/" + subframe);

        // Log the numeric world-frame pose of the selected subframe target.
        // Convention: grasp_± are at x=±grasp_offset_m_, z=+0.0075 in object-local coordinates, identity rotation.
        {
          tf2::Transform T_world_obj;
          tf2::fromMsg(block_pose.pose, T_world_obj);
          tf2::Transform T_obj_sub;
          T_obj_sub.setIdentity();
          T_obj_sub.setOrigin(tf2::Vector3(extract_positive ? +grasp_offset_m_ : -grasp_offset_m_, 0.0, 0.0));
          const tf2::Transform T_world_sub = T_world_obj * T_obj_sub;
          const tf2::Vector3 p = T_world_sub.getOrigin();
          const std::string frame_id = block_pose.header.frame_id.empty() ? "world" : block_pose.header.frame_id;
          RCLCPP_INFO(get_logger(),
                      "target_pose: %s/%s in frame '%s' position (x=%.4f, y=%.4f, z=%.4f)",
                      block_id.c_str(), subframe.c_str(), frame_id.c_str(),
                      p.x(), p.y(), p.z());
        }
        stage->setAngleDelta(grasp_angle_delta_);
        stage->setMonitoredStage(current_state_ptr);

        auto w = std::make_unique<mtc::stages::ComputeIK>("grasp IK", std::move(stage));
        w->setMaxIKSolutions(4);
        w->setMinSolutionDistance(0.5);
        Eigen::Isometry3d grasp_ik_frame = rpyToIso(grasp_r_, grasp_p_, grasp_y_);
        grasp_ik_frame.translation() = Eigen::Vector3d(0.0, 0.0, grasp_offset_z_);
        w->setIKFrame(grasp_ik_frame, hand_frame);
        w->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        w->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        grasp->insert(std::move(w));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("allow collision (hand,block)");
        stage->allowCollisions(block_id,
                               task.getRobotModel()->getJointModelGroup(hand_group_name)
                                   ->getLinkModelNamesWithCollisionGeometry(),
                               true);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveTo>("close hand", interpolation_planner);
        stage->setGroup(hand_group_name);
        stage->setGoal(closed_state_);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("attach block");
        stage->attachObject(block_id, hand_frame);
        attach_object_stage = stage.get();
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("extract (pull out)", cartesian_planner);
        stage->properties().set("marker_ns", "extract");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(hand_frame);
        stage->setMinMaxDistance(extract_min_, extract_max_);
        stage->setDirection(axisToDirInFrame(extract_axis_, block_pose, "world"));
        grasp->insert(std::move(stage));
      }
      if (wiggle_enable_) {
        auto stage1 = std::make_unique<mtc::stages::MoveRelative>("wiggle +", cartesian_planner);
        stage1->properties().set("marker_ns", "wiggle_p");
        stage1->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage1->setIKFrame(hand_frame);
        stage1->setMinMaxDistance(wiggle_distance_, wiggle_distance_);
        stage1->setDirection(axisToDirInFrame(extract_axis_, block_pose, "world"));
        grasp->insert(std::move(stage1));

        // opposite direction
        std::string inv = extract_axis_;
        if (!inv.empty() && inv[0] == '-') inv = inv.substr(1);
        else inv = "-" + inv;
        auto stage2 = std::make_unique<mtc::stages::MoveRelative>("wiggle -", cartesian_planner);
        stage2->properties().set("marker_ns", "wiggle_n");
        stage2->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage2->setIKFrame(hand_frame);
        stage2->setMinMaxDistance(wiggle_distance_, wiggle_distance_);
        stage2->setDirection(axisToDirInFrame(inv, block_pose, "world"));
        grasp->insert(std::move(stage2));
      }
      if (lift_after_extract_ > 1e-6) {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("lift after extract", cartesian_planner);
        stage->properties().set("marker_ns", "lift_after_extract");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(hand_frame);
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
          "move to place", mtc::stages::Connect::GroupPlannerVector{{arm_group_name, sampling_planner}});
      c->setTimeout(2.0);
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
        w->setMaxIKSolutions(4);
        w->setMinSolutionDistance(0.5);
        w->setIKFrame(block_id);
        w->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        w->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        place->insert(std::move(w));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveTo>("open hand (place)", interpolation_planner);
        stage->setGroup(hand_group_name);
        stage->setGoal(open_state_);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("forbid collision (hand,block)");
        stage->allowCollisions(block_id,
                               task.getRobotModel()->getJointModelGroup(hand_group_name)
                                   ->getLinkModelNamesWithCollisionGeometry(),
                               false);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("detach block");
        stage->detachObject(block_id, hand_frame);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("retreat", cartesian_planner);
        stage->properties().set("marker_ns", "retreat");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(hand_frame);
        stage->setMinMaxDistance(0.05, 0.10); // Retreat 5 to 10 cm
        
        // Move straight up in the world frame
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = "world";
        vec.vector.z = 1.0;
        stage->setDirection(vec);
        place->insert(std::move(stage));
      }
      task.add(std::move(place));
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
    mtc_jenga::applyBlockBoxAt(block_id, block_pose.header.frame_id, block_pose.pose, box_x_, box_y_, box_z_,
                               grasp_offset_m_);

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
                                                arm_group_name, vel_scale_, acc_scale_, get_logger());

    task.introspection().publishSolution(*task.solutions().front());
    auto res = task.execute(*task.solutions().front());
    if (res.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "MTC execute failed: %d", res.val);
      return false;
    }
    mtc_jenga::applyBlockBoxAt(block_id, place_pose.header.frame_id, place_pose.pose, box_x_, box_y_, box_z_,
                               grasp_offset_m_);
    return true;
  }

  void onActionAccepted(std::shared_ptr<ServerGoalHandle> handle) {
    if (!handle) return;
    std::thread{[this, h = std::move(handle)]() { executeAction(h); }}.detach();
  }

  void executeAction(const std::shared_ptr<ServerGoalHandle> goal_handle) {
    setBusy(true);
    auto res = std::make_shared<JengaExtractMiddleBlock::Result>();
    if (estop_.load()) {
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
      setBusy(false);
      return;
    }

    const auto goal = goal_handle->get_goal();
    auto fb = std::make_shared<JengaExtractMiddleBlock::Feedback>();
    auto send_fb = [goal_handle, &fb](const char* s, const float p) {
      fb->current_stage = s;
      fb->progress_pct = p;
      goal_handle->publish_feedback(fb);
    };

    send_fb("extract_middle_start", 0.0F);
    const std::string block_id = mtc_jenga::blockIdFromIndex(goal->block_index);
    const bool ok = runExtractMtc(goal->block_pose, goal->place_pose, block_id);
    send_fb("extract_middle_done", 100.0F);

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

  rclcpp_action::Server<JengaExtractMiddleBlock>::SharedPtr action_server_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;

  std::string action_name_;
  std::string arm_group_name;
  std::string hand_group_name;
  std::string hand_frame;
  std::string open_state_;
  std::string closed_state_;
  std::string arm_home_state_;
  std::string status_topic_;

  double box_x_{0.075}, box_y_{0.025}, box_z_{0.015};
  uint32_t plan_max_attempts_{3};
  double vel_scale_{0.20};
  double acc_scale_{0.20};
  double cart_step_{0.004};

  double approach_min_{0.005}, approach_max_{0.03};
  double extract_min_{0.06}, extract_max_{0.10};
  double lift_after_extract_{0.0};
  std::string extract_axis_{"x"};
  std::string approach_axis_{"-x"};
  double grasp_r_{0.0}, grasp_p_{M_PI / 2.0}, grasp_y_{0.0};
  double grasp_angle_delta_{M_PI / 1.0};
  double grasp_offset_m_{0.05};
  double grasp_offset_z_{0.01};

  bool wiggle_enable_{false};
  double wiggle_distance_{0.003};

  std::atomic<bool> busy_{false};
  std::atomic<int> executions_completed_{0};
  std::atomic<bool> estop_{false};
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto n = std::make_shared<MtcExtractMiddleBlockServer>();
  rclcpp::executors::MultiThreadedExecutor e(rclcpp::ExecutorOptions(), 4u);
  e.add_node(n);
  e.spin();
  rclcpp::shutdown();
  return 0;
}

