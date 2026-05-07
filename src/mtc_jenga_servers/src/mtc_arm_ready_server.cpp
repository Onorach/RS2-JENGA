#include <atomic>
#include <memory>
#include <sstream>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <jenga_interfaces/action/jenga_arm_ready.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>

#include "mtc_jenga_servers/mtc_server_common.hpp"

namespace mtc = moveit::task_constructor;
using JengaArmReady = jenga_interfaces::action::JengaArmReady;
using ServerGoalHandle = rclcpp_action::ServerGoalHandle<JengaArmReady>;

class MtcArmReadyServer : public rclcpp::Node {
 public:
  explicit MtcArmReadyServer(
      const rclcpp::NodeOptions& options =
          rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true))
  : rclcpp::Node("mtc_arm_ready_server", options) {
    action_name_ = declare_parameter("action_name", "jenga_arm_ready");
    arm_group_name = declare_parameter("arm_group", "ur_onrobot_manipulator");
    arm_home_state_ = declare_parameter("arm_home_state", "ready_position");
    plan_max_attempts_ = static_cast<uint32_t>(declare_parameter("plan_max_attempts", 3));
    vel_scale_ = declare_parameter("max_velocity_scaling_factor", 0.1);
    acc_scale_ = declare_parameter("max_acceleration_scaling_factor", 0.1);
    status_topic_ = declare_parameter("status_topic", "mtc_arm_ready_status");

    pub_status_ = create_publisher<std_msgs::msg::String>(status_topic_, 10);
    sub_estop_ = create_subscription<std_msgs::msg::Bool>(
        "/estop", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });
    sub_estop_active_ = create_subscription<std_msgs::msg::Bool>(
        "/estop_active", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });

    action_server_ = rclcpp_action::create_server<JengaArmReady>(
        this, action_name_,
        [this](const rclcpp_action::GoalUUID&, std::shared_ptr<const JengaArmReady::Goal> g) {
          (void)g;
          if (busy_.load() || estop_.load()) return rclcpp_action::GoalResponse::REJECT;
          return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        [this](const std::shared_ptr<ServerGoalHandle>) { return rclcpp_action::CancelResponse::ACCEPT; },
        [this](std::shared_ptr<ServerGoalHandle> h) { onActionAccepted(std::move(h)); });

    publishStatus("idle");
    RCLCPP_INFO(get_logger(), "mtc_arm_ready_server: action=%s status=%s", action_name_.c_str(),
                status_topic_.c_str());
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

  mtc::Task buildReadyTask(const std::string& named_state) {
    mtc::Task task;
    task.stages()->setName("jenga_arm_ready");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", arm_group_name);
    task.setProperty("group", arm_group_name);

    auto stage_state_current = std::make_unique<mtc::stages::CurrentState>("current");
    task.add(std::move(stage_state_current));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarArmReadyOptimized");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", 4.0);
    sampling_planner->setProperty("enforce_joint_model_state_space", true);
    sampling_planner->setMaxVelocityScalingFactor(vel_scale_);
    sampling_planner->setMaxAccelerationScalingFactor(acc_scale_);

    {
      auto stage = std::make_unique<mtc::stages::MoveTo>("move to ready", sampling_planner);
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setGoal(named_state);
      stage->setTimeout(8.0);
      task.add(std::move(stage));
    }
    return task;
  }

  bool runReadyMtc(const std::string& named_state) {
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop active: refusing to plan/execute MTC task");
      return false;
    }
    mtc::Task task = buildReadyTask(named_state);
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

    mtc_jenga::retimeArmSubTrajectoriesWithTotg(*task.solutions().front(), arm_group_name, vel_scale_,
    mtc_jenga::retimeArmSubTrajectoriesWithTotg(*task.solutions().front(), arm_group_name, vel_scale_,
                                                acc_scale_, get_logger());

    task.introspection().publishSolution(*task.solutions().front());
    auto res = task.execute(*task.solutions().front());
    if (res.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "MTC execute failed: %d", res.val);
      return false;
    }
    return true;
  }

  void onActionAccepted(std::shared_ptr<ServerGoalHandle> handle) {
    if (!handle) return;
    std::thread{[this, h = std::move(handle)]() { executeAction(h); }}.detach();
  }

  void executeAction(const std::shared_ptr<ServerGoalHandle> goal_handle) {
    setBusy(true);
    auto res = std::make_shared<JengaArmReady::Result>();
    if (estop_.load()) {
      res->success = false;
      res->message = "estop";
      res->error_code = 4;
      goal_handle->canceled(res);
      setBusy(false);
      return;
    }
    const auto goal = goal_handle->get_goal();
    std::string state = goal->target_state;
    if (state.empty()) {
      state = arm_home_state_;
    }
    rclcpp::Rate rate(2.0);
    auto fb = std::make_shared<JengaArmReady::Feedback>();
    auto send_fb = [goal_handle, &fb, &rate](const char* s, float p) {
      fb->current_stage = s;
      fb->progress_pct = p;
      goal_handle->publish_feedback(fb);
      rate.sleep();
    };
    send_fb("arm_ready_start", 0.0F);
    const bool ok = runReadyMtc(state);
    send_fb("arm_ready_done", 100.0F);
    if (estop_.load()) {
      res->success = false;
      res->message = "estop";
      res->error_code = 4;
      goal_handle->canceled(res);
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

  rclcpp_action::Server<JengaArmReady>::SharedPtr action_server_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;

  std::string action_name_;
  std::string arm_group_name;
  std::string arm_group_name;
  std::string arm_home_state_;
  std::string status_topic_;
  uint32_t plan_max_attempts_{3};
  double plan_time_{2.0};
  double vel_scale_{0.1};
  double acc_scale_{0.1};

  std::atomic<bool> busy_{false};
  std::atomic<int> executions_completed_{0};
  std::atomic<bool> estop_{false};
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto n = std::make_shared<MtcArmReadyServer>();
  rclcpp::executors::MultiThreadedExecutor e(rclcpp::ExecutorOptions(), 4u);
  e.add_node(n);
  e.spin();
  rclcpp::shutdown();
  return 0;
}
