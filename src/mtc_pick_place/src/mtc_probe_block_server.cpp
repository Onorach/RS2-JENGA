#include <atomic>
#include <cmath>
#include <memory>
#include <sstream>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <jenga_interfaces/action/jenga_probe_block.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>

#include "mtc_pick_place/mtc_server_common.hpp"

namespace mtc = moveit::task_constructor;
using JengaProbeBlock = jenga_interfaces::action::JengaProbeBlock;
using ServerGoalHandle = rclcpp_action::ServerGoalHandle<JengaProbeBlock>;

namespace {

geometry_msgs::msg::Vector3Stamped axisToDir(const std::string& axis, const std::string& frame_id) {
  geometry_msgs::msg::Vector3Stamped v;
  v.header.frame_id = frame_id;
  v.vector.x = 0.0;
  v.vector.y = 0.0;
  v.vector.z = 0.0;
  const bool neg = !axis.empty() && axis[0] == '-';
  const char a = (neg ? axis[1] : axis[0]);
  const double s = neg ? -1.0 : 1.0;
  if (a == 'x') v.vector.x = s;
  if (a == 'y') v.vector.y = s;
  if (a == 'z') v.vector.z = s;
  return v;
}

}  // namespace

class MtcProbeBlockServer : public rclcpp::Node {
 public:
  explicit MtcProbeBlockServer(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : rclcpp::Node("mtc_probe_block_server", options) {
    action_name_ = declare_parameter("action_name", "jenga_probe_block");
    ur_onrobot_manipulator_ = declare_parameter("arm_group", "ur_onrobot_manipulator");
    gripper_tcp_ = declare_parameter("gripper_tcp", "gripper_tcp");
    arm_home_state_ = declare_parameter("arm_home_state", "test_configuration");

    box_x_ = declare_parameter("block_box_x", 0.075);
    box_y_ = declare_parameter("block_box_y", 0.025);
    box_z_ = declare_parameter("block_box_z", 0.015);

    plan_max_attempts_ = static_cast<uint32_t>(declare_parameter("plan_max_attempts", 3));
    vel_scale_ = declare_parameter("max_velocity_scaling_factor", 0.1);
    acc_scale_ = declare_parameter("max_acceleration_scaling_factor", 0.1);
    cart_step_ = declare_parameter("cartesian_step", 0.003);

    probe_axis_ = declare_parameter("probe_axis", "x");  // x|y|z|-x|-y|-z in block frame
    approach_axis_ = declare_parameter("approach_axis", "-x");
    approach_min_ = declare_parameter("approach_distance_min", 0.01);
    approach_max_ = declare_parameter("approach_distance_max", 0.05);
    push_distance_ = declare_parameter("push_distance", 0.004);
    pull_distance_ = declare_parameter("pull_distance", 0.008);
    retreat_distance_ = declare_parameter("retreat_distance", 0.02);

    status_topic_ = declare_parameter("status_topic", "mtc_probe_status");
    pub_status_ = create_publisher<std_msgs::msg::String>(status_topic_, 10);

    sub_estop_ = create_subscription<std_msgs::msg::Bool>(
        "/estop", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });
    sub_estop_active_ = create_subscription<std_msgs::msg::Bool>(
        "/estop_active", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });

    action_server_ = rclcpp_action::create_server<JengaProbeBlock>(
        this, action_name_,
        [this](const rclcpp_action::GoalUUID&, std::shared_ptr<const JengaProbeBlock::Goal>) {
          if (busy_.load() || estop_.load()) return rclcpp_action::GoalResponse::REJECT;
          return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        [this](const std::shared_ptr<ServerGoalHandle>) { return rclcpp_action::CancelResponse::ACCEPT; },
        [this](std::shared_ptr<ServerGoalHandle> h) { onActionAccepted(std::move(h)); });

    publishStatus("idle");
    RCLCPP_INFO(get_logger(), "mtc_probe_block_server: action=%s status=%s", action_name_.c_str(), status_topic_.c_str());
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

  mtc::Task buildProbeTask(const std::string& block_id) {
    mtc::Task task;
    task.stages()->setName("jenga_probe_block");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", ur_onrobot_manipulator_);
    task.setProperty("ik_frame", gripper_tcp_);

    auto stage_state_current = std::make_unique<mtc::stages::CurrentState>("current");
    task.add(std::move(stage_state_current));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarkConfigDefault");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", 2.0);
    sampling_planner->setProperty("enforce_joint_model_state_space", true);
    sampling_planner->setMaxVelocityScalingFactor(vel_scale_);
    sampling_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto cartesian_planner = std::make_shared<mtc::solvers::CartesianPath>();
    cartesian_planner->setMaxVelocityScalingFactor(vel_scale_);
    cartesian_planner->setMaxAccelerationScalingFactor(acc_scale_);
    cartesian_planner->setStepSize(cart_step_);

    {
      auto c = std::make_unique<mtc::stages::Connect>(
          "move to probe", mtc::stages::Connect::GroupPlannerVector{{ur_onrobot_manipulator_, sampling_planner}});
      c->setTimeout(3.0);
      c->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(c));
    }

    {
      auto probe = std::make_unique<mtc::SerialContainer>("probe push/pull");
      probe->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});

      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("approach probe", cartesian_planner);
        stage->properties().set("marker_ns", "probe_approach");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(approach_min_, approach_max_);
        stage->setDirection(axisToDir(approach_axis_, block_id));
        probe->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("push", cartesian_planner);
        stage->properties().set("marker_ns", "probe_push");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(push_distance_, push_distance_);
        stage->setDirection(axisToDir(probe_axis_, block_id));
        probe->insert(std::move(stage));
      }
      {
        // pull back in opposite direction; typically further than push
        std::string inv = probe_axis_;
        if (!inv.empty() && inv[0] == '-') inv = inv.substr(1);
        else inv = "-" + inv;

        auto stage = std::make_unique<mtc::stages::MoveRelative>("pull", cartesian_planner);
        stage->properties().set("marker_ns", "probe_pull");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(pull_distance_, pull_distance_);
        stage->setDirection(axisToDir(inv, block_id));
        probe->insert(std::move(stage));
      }
      {
        // retreat away from the tower along approach inverse
        std::string inv = approach_axis_;
        if (!inv.empty() && inv[0] == '-') inv = inv.substr(1);
        else inv = "-" + inv;

        auto stage = std::make_unique<mtc::stages::MoveRelative>("retreat", cartesian_planner);
        stage->properties().set("marker_ns", "probe_retreat");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(retreat_distance_, retreat_distance_);
        stage->setDirection(axisToDir(inv, block_id));
        probe->insert(std::move(stage));
      }

      task.add(std::move(probe));
    }

    {
      auto stage = std::make_unique<mtc::stages::MoveTo>("return home", sampling_planner);
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setGoal(arm_home_state_);
      stage->setTimeout(3.0);
      task.add(std::move(stage));
    }

    return task;
  }

  bool runProbeMtc(const geometry_msgs::msg::PoseStamped& block_pose, const std::string& block_id, float& score_out) {
    score_out = 0.0F;
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop active: refusing to plan/execute MTC task");
      return false;
    }
    mtc_jenga::applyBlockBoxAt(block_id, block_pose.header.frame_id, block_pose.pose, box_x_, box_y_, box_z_);

    mtc::Task task = buildProbeTask(block_id);
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

    // Without force/torque feedback, report a simple binary score for now.
    score_out = 1.0F;
    return true;
  }

  void onActionAccepted(std::shared_ptr<ServerGoalHandle> handle) {
    if (!handle) return;
    std::thread{[this, h = std::move(handle)]() { executeAction(h); }}.detach();
  }

  void executeAction(const std::shared_ptr<ServerGoalHandle> goal_handle) {
    setBusy(true);
    auto res = std::make_shared<JengaProbeBlock::Result>();
    if (estop_.load()) {
      res->score = 0.0F;
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
      setBusy(false);
      return;
    }

    const auto goal = goal_handle->get_goal();
    auto fb = std::make_shared<JengaProbeBlock::Feedback>();
    auto send_fb = [goal_handle, &fb](const char* s, const float p) {
      fb->current_stage = s;
      fb->progress_pct = p;
      goal_handle->publish_feedback(fb);
    };

    send_fb("probe_start", 0.0F);
    const std::string block_id = mtc_jenga::blockIdFromIndex(goal->block_index);
    float score = 0.0F;
    const bool ok = runProbeMtc(goal->block_pose, block_id, score);
    send_fb("probe_done", 100.0F);

    res->score = score;
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

  rclcpp_action::Server<JengaProbeBlock>::SharedPtr action_server_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;

  std::string action_name_;
  std::string ur_onrobot_manipulator_;
  std::string gripper_tcp_;
  std::string arm_home_state_;
  std::string status_topic_;

  double box_x_{0.075}, box_y_{0.025}, box_z_{0.015};
  uint32_t plan_max_attempts_{3};
  double vel_scale_{0.20};
  double acc_scale_{0.20};
  double cart_step_{0.003};

  std::string probe_axis_{"x"};
  std::string approach_axis_{"-x"};
  double approach_min_{0.01}, approach_max_{0.05};
  double push_distance_{0.004};
  double pull_distance_{0.008};
  double retreat_distance_{0.02};

  std::atomic<bool> busy_{false};
  std::atomic<int> executions_completed_{0};
  std::atomic<bool> estop_{false};
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto n = std::make_shared<MtcProbeBlockServer>();
  rclcpp::executors::MultiThreadedExecutor e(rclcpp::ExecutorOptions(), 4u);
  e.add_node(n);
  e.spin();
  rclcpp::shutdown();
  return 0;
}

