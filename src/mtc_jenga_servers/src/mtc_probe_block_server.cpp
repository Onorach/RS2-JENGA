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
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <jenga_interfaces/action/jenga_probe_block.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>

#include <Eigen/Geometry>

#include "mtc_jenga_servers/mtc_server_common.hpp"

namespace mtc = moveit::task_constructor;
using JengaProbeBlock = jenga_interfaces::action::JengaProbeBlock;
using ServerGoalHandle = rclcpp_action::ServerGoalHandle<JengaProbeBlock>;

namespace {

constexpr uint8_t PROBE_UNKNOWN = 0;
constexpr uint8_t PROBE_LOOSE = 1;
constexpr uint8_t PROBE_STUCK = 2;
constexpr uint8_t PROBE_ERROR = 3;

}  // namespace

class MtcProbeBlockServer : public rclcpp::Node {
  public:
  explicit MtcProbeBlockServer(
      const rclcpp::NodeOptions& options =
          rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true))
  : rclcpp::Node("mtc_probe_block_server", options) {
    action_name_ = mtc_jenga::param<std::string>(this, "action_name", "jenga_probe_block");
    arm_group_name_ = mtc_jenga::param<std::string>(this, "arm_group", "ur_onrobot_manipulator");
    hand_group_name_ = mtc_jenga::param<std::string>(this, "hand_group", "ur_onrobot_gripper");
    // gripper_tcp kept for launch compatibility; probe motion uses probe_frame only.
    (void)mtc_jenga::param<std::string>(this, "gripper_tcp", "gripper_tcp");
    probe_frame_ = mtc_jenga::param<std::string>(this, "probe_frame", "probe_tip");
    arm_home_state_ = mtc_jenga::param<std::string>(this, "arm_home_state", "test_configuration");
    closed_state_ = mtc_jenga::param<std::string>(this, "gripper_closed_state", "closed");

    box_x_ = mtc_jenga::param<double>(this, "block_box_x", 0.075);
    box_y_ = mtc_jenga::param<double>(this, "block_box_y", 0.025);
    box_z_ = mtc_jenga::param<double>(this, "block_box_z", 0.015);

    plan_max_attempts_ = static_cast<uint32_t>(mtc_jenga::param<int>(this, "plan_max_attempts", 1));
    plan_time_ = mtc_jenga::param<double>(this, "plan_time", 5.0);
    vel_scale_ = mtc_jenga::param<double>(this, "max_velocity_scaling_factor", 0.1);
    acc_scale_ = mtc_jenga::param<double>(this, "max_acceleration_scaling_factor", 0.1);
    cart_step_ = mtc_jenga::param<double>(this, "cartesian_step", 0.001);

    approach_min_ = mtc_jenga::param<double>(this, "approach_distance_min", 0.01);
    approach_max_ = mtc_jenga::param<double>(this, "approach_distance_max", 0.05);
    retreat_distance_ = mtc_jenga::param<double>(this, "retreat_distance", 0.02);

    probe_r_ = mtc_jenga::param<double>(this, "probe_frame_roll", 0.0);
    probe_p_ = mtc_jenga::param<double>(this, "probe_frame_pitch", M_PI / 1.0);
    probe_y_ = mtc_jenga::param<double>(this, "probe_frame_yaw", 0.0);

    ft_sensor_topic_ = mtc_jenga::param<std::string>(this, "ft_topic", "force_torque_sensor_broadcaster/wrench");
    stuck_force_threshold_n_ = mtc_jenga::param<double>(this, "stuck_force_threshold_n", 0.05);
    emergency_force_threshold_n_ = mtc_jenga::param<double>(this, "emergency_force_threshold_n", 30.0);
    stuck_dwell_samples_ = static_cast<int>(mtc_jenga::param<int>(this, "stuck_dwell_samples", 5));
    protrusion_target_m_ = mtc_jenga::param<double>(this, "protrusion_target_m", 0.02);
    push_velocity_m_s_ = mtc_jenga::param<double>(this, "push_velocity_m_s", 0.005);
    push_step_m_ = mtc_jenga::param<double>(this, "push_step_m", 0.001);

    push_cartesian_min_fraction_ =
        mtc_jenga::param<double>(this, "push_cartesian_min_fraction", 0.95);
    push_cartesian_max_consecutive_failures_ =
        static_cast<int>(mtc_jenga::param<int>(this, "push_cartesian_max_consecutive_failures", 3));
    push_cartesian_target_pos_tol_m_ =
        mtc_jenga::param<double>(this, "push_cartesian_target_pos_tol_m", 0.002);
    push_cartesian_retry_wait_s_ =
        mtc_jenga::param<double>(this, "push_cartesian_retry_wait_s", 0.05);
    push_cartesian_step_scales_ = mtc_jenga::param<std::vector<double>>(
        this, "push_cartesian_step_scales", std::vector<double>{1.0, 0.5, 0.25});

    probe_subframe_ = mtc_jenga::param<std::string>(this, "probe_subframe", "end_plus");
    probe_offset_m_ = mtc_jenga::param<double>(this, "probe_offset_m", 0.045);
    use_sim_block_attach_ = mtc_jenga::param<bool>(this, "use_sim_block_attach", true);

    status_topic_ = mtc_jenga::param<std::string>(this, "status_topic", "mtc_probe_status");
    pub_status_ = create_publisher<std_msgs::msg::String>(status_topic_, 10);

    sub_estop_ = create_subscription<std_msgs::msg::Bool>(
        "/estop", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });
    sub_estop_active_ = create_subscription<std_msgs::msg::Bool>(
        "/estop_active", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });

    sub_ft_ = create_subscription<geometry_msgs::msg::WrenchStamped>(
        ft_sensor_topic_, 10, [this](const geometry_msgs::msg::WrenchStamped::SharedPtr msg) {
          std::lock_guard<std::mutex> lk(ft_mutex_);
          ft_latest_ = *msg;
          ft_received_ = true;
        });

    action_server_ = rclcpp_action::create_server<JengaProbeBlock>(
        this, action_name_,
        [this](const rclcpp_action::GoalUUID&, std::shared_ptr<const JengaProbeBlock::Goal>) {
          if (busy_.load() || estop_.load()) return rclcpp_action::GoalResponse::REJECT;
          return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        [this](const std::shared_ptr<ServerGoalHandle>) { return rclcpp_action::CancelResponse::ACCEPT; },
        [this](std::shared_ptr<ServerGoalHandle> h) { onActionAccepted(std::move(h)); });

    publishStatus("idle");
    RCLCPP_INFO(get_logger(),
                "mtc_probe_block_server: action=%s status=%s ft=%s probe_frame=%s "
                "use_sim_block_attach=%s",
                action_name_.c_str(), status_topic_.c_str(), ft_sensor_topic_.c_str(),
                probe_frame_.c_str(), use_sim_block_attach_ ? "true" : "false");

    servo_pub_ = create_publisher<geometry_msgs::msg::TwistStamped>("servo_node/delta_twist_cmds", 10);
  }

  private:
  // ---------------------------------------------------------------------------
  // Status helpers
  // ---------------------------------------------------------------------------
  void publishStatus(const std::string& phase) {
    std_msgs::msg::String m;
    std::ostringstream o;
    o << "{\"state\":\"" << phase << "\",\"busy\":" << (busy_.load() ? "true" : "false")
      << ",\"executions_completed\":" << executions_completed_.load()
      << ",\"estop_active\":" << (estop_.load() ? "true" : "false");
    const int block_idx = active_block_index_.load();
    if (block_idx >= 0) {
      o << ",\"block_index\":" << block_idx;
    }
    o << "}";
    m.data = o.str();
    pub_status_->publish(m);
  }

  void setBusy(const bool b) {
    busy_.store(b);
    if (!b) {
      active_block_index_.store(-1);
    }
    publishStatus(b ? "running" : "idle");
  }

  // ---------------------------------------------------------------------------
  // F/T helpers
  // ---------------------------------------------------------------------------
  std::optional<geometry_msgs::msg::WrenchStamped> getLatestWrench() const {
    std::lock_guard<std::mutex> lk(ft_mutex_);
    if (!ft_received_) return std::nullopt;
    return ft_latest_;
  }

  static Eigen::Vector3d wrenchForceVec(const geometry_msgs::msg::WrenchStamped& w) {
    return {w.wrench.force.x, w.wrench.force.y, w.wrench.force.z};
  }

  // ---------------------------------------------------------------------------
  // Phase 1: MTC Approach Task
  // ---------------------------------------------------------------------------
  mtc::Task buildApproachTask(const std::string& block_id) {
    mtc::Task task;
    task.stages()->setName("jenga_probe_approach");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", arm_group_name_);
    task.setProperty("eef", hand_group_name_);
    task.setProperty("ik_frame", probe_frame_);

    // mtc::Stage* current_state_ptr = nullptr;
    {
      auto stage = std::make_unique<mtc::stages::CurrentState>("current");
      // current_state_ptr = stage.get();
      task.add(std::move(stage));
    }

    mtc::Stage* allow_collision_ptr = nullptr;
    {
      auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("allow collision (probe,block)");
      stage->allowCollisions(block_id, mtc_jenga::probeCollisionLinkNames(), true);
      allow_collision_ptr = stage.get(); // Save the pointer for the generator
      task.add(std::move(stage));
    }

    auto interpolation_planner = std::make_shared<mtc::solvers::JointInterpolationPlanner>();
    interpolation_planner->setMaxVelocityScalingFactor(vel_scale_);
    interpolation_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarPathLengthOptimized");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", plan_time_);
    sampling_planner->setProperty("enforce_joint_model_state_space", true);
    sampling_planner->setMaxVelocityScalingFactor(vel_scale_);
    sampling_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto cartesian_planner = std::make_shared<mtc::solvers::CartesianPath>();
    cartesian_planner->setMaxVelocityScalingFactor(vel_scale_);
    cartesian_planner->setMaxAccelerationScalingFactor(acc_scale_);
    cartesian_planner->setStepSize(cart_step_);

    {
      auto stage = std::make_unique<mtc::stages::MoveTo>("close gripper", interpolation_planner);
      stage->setGroup(hand_group_name_);
      stage->setGoal(closed_state_);
      task.add(std::move(stage));
    }
    {
      auto c = std::make_unique<mtc::stages::Connect>(
          "move to probe", mtc::stages::Connect::GroupPlannerVector{{arm_group_name_, sampling_planner}});
      c->setTimeout(plan_time_);
      c->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(c));
    }
    {
      auto approach = std::make_unique<mtc::SerialContainer>("probe approach");
      task.properties().exposeTo(approach->properties(), {"eef", "group", "ik_frame"});
      approach->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group", "ik_frame"});

      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("approach to contact", cartesian_planner);
        stage->properties().set("marker_ns", "probe_approach");
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(probe_frame_);
        stage->setMinMaxDistance(approach_min_, approach_max_);
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = probe_frame_;
        vec.vector.x = 1.0;
        stage->setDirection(vec);
        approach->insert(std::move(stage));
      }

      {
        auto gen = std::make_unique<mtc::stages::GeneratePose>("generate probe target");
        gen->properties().configureInitFrom(mtc::Stage::PARENT);
        gen->properties().set("marker_ns", "probe_target");
        geometry_msgs::msg::PoseStamped target;
        target.header.frame_id = block_id + "/" + probe_subframe_;
        target.pose.orientation.w = 1.0;
        gen->setPose(target);
        
        gen->setMonitoredStage(allow_collision_ptr);

        Eigen::Isometry3d probe_ft = Eigen::Isometry3d::Identity();
        probe_ft = probe_ft * Eigen::AngleAxisd(probe_r_, Eigen::Vector3d::UnitX())
                            * Eigen::AngleAxisd(probe_p_, Eigen::Vector3d::UnitY())
                            * Eigen::AngleAxisd(probe_y_, Eigen::Vector3d::UnitZ());
        auto ik = std::make_unique<mtc::stages::ComputeIK>("probe IK", std::move(gen));
        ik->setMaxIKSolutions(64);
        ik->setMinSolutionDistance(0.05);
        ik->setIKFrame(probe_ft, probe_frame_);
        ik->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        ik->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        approach->insert(std::move(ik));
      }

      task.add(std::move(approach));
    }

    return task;
  }

  // ---------------------------------------------------------------------------
  // Phase 3: MTC Retreat Task
  // ---------------------------------------------------------------------------
  mtc::Task buildRetreatTask(const std::string& block_id) {
    mtc::Task task;
    task.stages()->setName("jenga_probe_retreat");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", arm_group_name_);
    task.setProperty("ik_frame", probe_frame_);

    task.add(std::make_unique<mtc::stages::CurrentState>("current"));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarPathLengthOptimized");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", plan_time_);
    sampling_planner->setProperty("enforce_joint_model_state_space", true);
    sampling_planner->setMaxVelocityScalingFactor(vel_scale_);
    sampling_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto cartesian_planner = std::make_shared<mtc::solvers::CartesianPath>();
    cartesian_planner->setMaxVelocityScalingFactor(vel_scale_);
    cartesian_planner->setMaxAccelerationScalingFactor(acc_scale_);
    cartesian_planner->setStepSize(cart_step_);

    {
      auto stage = std::make_unique<mtc::stages::MoveRelative>("retreat", cartesian_planner);
      stage->properties().set("marker_ns", "probe_retreat");
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setIKFrame(probe_frame_);
      stage->setMinMaxDistance(0.02 + retreat_distance_, 0.05 + retreat_distance_);

      geometry_msgs::msg::Vector3Stamped vec;
      vec.header.frame_id = probe_frame_;
      vec.vector.x = -1.0;
      stage->setDirection(vec);
      task.add(std::move(stage));
    }
    {
      auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("forbid collision (probe,block)");
      stage->allowCollisions(block_id, mtc_jenga::probeCollisionLinkNames(), false);
      task.add(std::move(stage));
    }

    return task;
  }

  bool attachBlockForSim(const std::string& block_id) {
    if (!use_sim_block_attach_) {
      RCLCPP_INFO(get_logger(),
                  "Skipping sim block attach (use_sim_block_attach=false; use perception pose updates)");
      return false;
    }
    return mtc_jenga::attachBlockToLink(block_id, probe_frame_, get_logger());
  }

  void detachBlockIfAttached(const std::string& block_id, bool& block_attached) {
    if (!block_attached) return;
    mtc_jenga::detachBlock(block_id, probe_frame_, get_logger());
    block_attached = false;
  }

  // ---------------------------------------------------------------------------
  // MTC plan + execute helper
  // ---------------------------------------------------------------------------
  bool planAndExecuteMtc(mtc::Task& task, const char* label) {
    try {
      task.init();
    } catch (const mtc::InitStageException& e) {
      RCLCPP_ERROR(get_logger(), "%s: MTC init failed: %s", label, e.what());
      return false;
    }
    if (!task.plan(plan_max_attempts_) || task.solutions().empty()) {
      RCLCPP_ERROR(get_logger(), "%s: MTC plan failed", label);
      return false;
    }
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "%s: E-stop active after planning; skipping execution", label);
      return false;
    }

    mtc_jenga::retimeArmSubTrajectoriesWithTotg(*task.solutions().front(),
                                                arm_group_name_, vel_scale_, acc_scale_, get_logger());

    task.introspection().publishSolution(*task.solutions().front());
    auto res = task.execute(*task.solutions().front());
    if (res.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "%s: MTC execute failed: %d", label, res.val);
      return false;
    }
    return true;
  }

  // ---------------------------------------------------------------------------
  // Phase 2: FT-monitored Cartesian push using MoveGroupInterface
  // ---------------------------------------------------------------------------
  struct PushResult {
    uint8_t outcome = PROBE_UNKNOWN;
    double displacement_m = 0.0;
    double max_force_n = 0.0;
  };

  void ensureMoveGroup() {
    if (!move_group_) {
      move_group_ = std::make_shared<moveit::planning_interface::MoveGroupInterface>(
          shared_from_this(), arm_group_name_);
      move_group_->setEndEffectorLink(probe_frame_);
      RCLCPP_INFO(get_logger(), "MoveGroupInterface initialized for '%s' with EE '%s'",
                  arm_group_name_.c_str(), probe_frame_.c_str());
    }
  }

  Eigen::Vector3d probeAxisInWorld() const {
    auto pose_msg = move_group_->getCurrentPose(probe_frame_);
    const auto& q = pose_msg.pose.orientation;
    const Eigen::Quaterniond quat(q.w, q.x, q.y, q.z);
    return quat.normalized() * Eigen::Vector3d(1.0, 0.0, 0.0);
  }

  PushResult runFtPushLoop() {
    PushResult result;
    ensureMoveGroup();
    
    // 1. Tare FT sensor (Bias calculation)
    Eigen::Vector3d wrench_bias = Eigen::Vector3d::Zero();
    auto w0 = getLatestWrench();
    if (w0) {
      wrench_bias = wrenchForceVec(*w0);
    }
  
    // 2. Setup Loop timing (Servo typically expects commands at 50-100Hz)
    rclcpp::Rate rate(50); 
    auto start_pose_msg = move_group_->getCurrentPose(probe_frame_);
    Eigen::Vector3d start_pos(start_pose_msg.pose.position.x, 
                              start_pose_msg.pose.position.y, 
                              start_pose_msg.pose.position.z);
  
    RCLCPP_INFO(get_logger(), "Starting velocity-based push at %.3f m/s", push_velocity_m_s_);
  
    while (rclcpp::ok()) {
      if (estop_.load()) {
        result.outcome = PROBE_ERROR;
        break;
      }
    
      // 3. Create Twist command in the probe frame
      // Moving along the X-axis of the probe_frame_ simplifies the math significantly.
      geometry_msgs::msg::TwistStamped twist;
      twist.header.stamp = now();
      twist.header.frame_id = probe_frame_; // Command relative to the probe tip
      twist.twist.linear.x = push_velocity_m_s_; 
      servo_pub_->publish(twist);
  
      // 4. Calculate Displacement
      auto current_pose = move_group_->getCurrentPose(probe_frame_);
      Eigen::Vector3d current_pos(current_pose.pose.position.x, 
                                  current_pose.pose.position.y, 
                                  current_pose.pose.position.z);
      result.displacement_m = (current_pos - start_pos).norm();
  
      // 5. Monitor Force
      auto wrench = getLatestWrench();
      if (wrench) {
        // Since we move along the probe's X-axis, we care about the force on that axis
        const Eigen::Vector3d force = wrenchForceVec(*wrench) - wrench_bias;
        
        // We need the probe's direction in the FT sensor frame, 
        // but for simplicity, we check the magnitude of the force vector projected
        // onto the movement direction if they are in the same frame.
        double force_magnitude = force.norm(); 
        result.max_force_n = std::max(result.max_force_n, force_magnitude);
  
        if (force_magnitude >= emergency_force_threshold_n_) {
          RCLCPP_WARN(get_logger(), "Emergency Force! %.2f N", force_magnitude);
          result.outcome = PROBE_STUCK;
          break;
        }
  
        if (force_magnitude >= stuck_force_threshold_n_) {
          // You could add a 'stuck_count' here like in your original code
          result.outcome = PROBE_STUCK;
          break;
        }
      }
  
      // 6. Check Displacement Target
      if (result.displacement_m >= protrusion_target_m_) {
        result.outcome = PROBE_LOOSE;
        break;
      }
  
      rate.sleep();
    }
    
    // 7. Stop the robot (Send zero velocity)
    geometry_msgs::msg::TwistStamped stop_twist;
    stop_twist.header.stamp = now();
    stop_twist.header.frame_id = probe_frame_;
    servo_pub_->publish(stop_twist);
  
    return result;
  }

  // ---------------------------------------------------------------------------
  // Three-phase orchestrator
  // ---------------------------------------------------------------------------
  bool runProbe(const geometry_msgs::msg::PoseStamped& block_pose,
                const std::string& block_id,
                PushResult& push_result_out) {
    push_result_out = {};
    bool block_attached = false;

    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop active: refusing to run probe");
      push_result_out.outcome = PROBE_ERROR;
      return false;
    }

    mtc_jenga::applyBlockBoxAt(block_id, block_pose.header.frame_id, block_pose.pose,
                               box_x_, box_y_, box_z_,
                               0.035 /* grasp_offset_m default */, probe_offset_m_);

    // Phase 1: MTC approach (close gripper + move to contact pose)
    RCLCPP_INFO(get_logger(), "Phase 1: MTC approach");
    mtc::Task approach_task = buildApproachTask(block_id);
    if (!planAndExecuteMtc(approach_task, "Phase1-Approach")) {
      push_result_out.outcome = PROBE_ERROR;
      return false;
    }

    block_attached = attachBlockForSim(block_id);

    // Phase 2: FT-monitored push
    RCLCPP_INFO(get_logger(), "Phase 2: FT-monitored push (target=%.4f m, stuck_threshold=%.1f N)",
                protrusion_target_m_, stuck_force_threshold_n_);
    push_result_out = runFtPushLoop();
    detachBlockIfAttached(block_id, block_attached);

    // Phase 3: MTC retreat + return home
    RCLCPP_INFO(get_logger(), "Phase 3: MTC retreat + home");
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop active before Phase 3; skipping retreat");
    } else {
      mtc::Task retreat_task = buildRetreatTask(block_id);
      if (!planAndExecuteMtc(retreat_task, "Phase3-Retreat")) {
        RCLCPP_WARN(get_logger(), "Phase 3 retreat failed; probe result is still valid");
      }
    }

    return push_result_out.outcome != PROBE_ERROR;
  }

  // ---------------------------------------------------------------------------
  // Action handling
  // ---------------------------------------------------------------------------
  void onActionAccepted(std::shared_ptr<ServerGoalHandle> handle) {
    if (!handle) return;
    std::thread{[this, h = std::move(handle)]() { executeAction(h); }}.detach();
  }

  void executeAction(const std::shared_ptr<ServerGoalHandle> goal_handle) {
    auto res = std::make_shared<JengaProbeBlock::Result>();
    if (estop_.load()) {
      res->score = 0.0F;
      res->probe_outcome = PROBE_ERROR;
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
      setBusy(false);
      return;
    }

    const auto goal = goal_handle->get_goal();
    active_block_index_.store(static_cast<int>(goal->block_index));
    setBusy(true);
    auto fb = std::make_shared<JengaProbeBlock::Feedback>();
    auto send_fb = [goal_handle, &fb](const char* s, const float p) {
      fb->current_stage = s;
      fb->progress_pct = p;
      goal_handle->publish_feedback(fb);
    };

    send_fb("probe_approach", 0.0F);
    const std::string block_id = mtc_jenga::blockIdFromIndex(goal->block_index);

    PushResult push_result;
    const bool ok = runProbe(goal->block_pose, block_id, push_result);

    send_fb("probe_done", 100.0F);

    res->probe_outcome = push_result.outcome;
    res->displacement_m = static_cast<float>(push_result.displacement_m);
    res->max_force_n = static_cast<float>(push_result.max_force_n);

    // Score: 1.0 for LOOSE (good candidate), 0.0 for STUCK, -1.0 for ERROR
    if (push_result.outcome == PROBE_LOOSE)
      res->score = 1.0F;
    else if (push_result.outcome == PROBE_STUCK)
      res->score = 0.0F;
    else
      res->score = -1.0F;

    if (estop_.load()) {
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
    } else if (ok) {
      res->success = true;
      res->message = (push_result.outcome == PROBE_LOOSE) ? "loose" : "stuck";
      res->error_code = 0;
      executions_completed_ += 1;
      goal_handle->succeed(res);
    } else {
      res->success = false;
      res->message = "probe failed";
      res->error_code = 1;
      goal_handle->abort(res);
    }

    setBusy(false);
  }

  // ---------------------------------------------------------------------------
  // Members
  // ---------------------------------------------------------------------------
  rclcpp_action::Server<JengaProbeBlock>::SharedPtr action_server_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Subscription<geometry_msgs::msg::WrenchStamped>::SharedPtr sub_ft_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr servo_pub_;

  mutable std::mutex ft_mutex_;
  geometry_msgs::msg::WrenchStamped ft_latest_;
  bool ft_received_{false};

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_;

  std::string action_name_;
  std::string arm_group_name_;
  std::string hand_group_name_;
  std::string probe_frame_;
  std::string arm_home_state_;
  std::string closed_state_;
  std::string status_topic_;
  std::string ft_sensor_topic_;

  double box_x_{0.075}, box_y_{0.025}, box_z_{0.015};
  uint32_t plan_max_attempts_{1};
  double plan_time_{3.0};
  double vel_scale_{0.20};
  double acc_scale_{0.20};
  double cart_step_{0.001};

  double approach_min_{0.01}, approach_max_{0.05};
  double retreat_distance_{0.02};

  double probe_r_{0.0}, probe_p_{M_PI / 2.0}, probe_y_{0.0};

  double stuck_force_threshold_n_{10.0};
  double emergency_force_threshold_n_{30.0};
  int stuck_dwell_samples_{5};
  double protrusion_target_m_{0.02};
  double push_velocity_m_s_{0.005};
  double push_step_m_{0.001};

  double push_cartesian_min_fraction_{0.95};
  int push_cartesian_max_consecutive_failures_{3};
  double push_cartesian_target_pos_tol_m_{0.002};
  double push_cartesian_retry_wait_s_{0.05};
  std::vector<double> push_cartesian_step_scales_{1.0, 0.5, 0.25};

  std::string probe_subframe_{"probe_plus"};
  double probe_offset_m_{0.045};
  bool use_sim_block_attach_{true};

  std::atomic<bool> busy_{false};
  std::atomic<int> active_block_index_{-1};
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
