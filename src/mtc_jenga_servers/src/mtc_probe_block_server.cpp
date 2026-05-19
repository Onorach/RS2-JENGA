#include <atomic>
#include <cmath>
#include <memory>
#include <mutex>
#include <optional>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <jenga_interfaces/action/jenga_probe_block.hpp>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>

#include <Eigen/Geometry>

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

Eigen::Isometry3d rpyToIso(const double r, const double p, const double y) {
  Eigen::Isometry3d t = Eigen::Isometry3d::Identity();
  t.linear() = (Eigen::AngleAxisd(y, Eigen::Vector3d::UnitZ()) *
                Eigen::AngleAxisd(p, Eigen::Vector3d::UnitY()) *
                Eigen::AngleAxisd(r, Eigen::Vector3d::UnitX()))
                   .toRotationMatrix();
  return t;
}

}  // namespace

class MtcProbeBlockServer : public rclcpp::Node {
 public:
  explicit MtcProbeBlockServer(
      const rclcpp::NodeOptions& options =
          rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true))
  explicit MtcProbeBlockServer(
      const rclcpp::NodeOptions& options =
          rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true))
  : rclcpp::Node("mtc_probe_block_server", options) {
    action_name_ = mtc_jenga::param<std::string>(this, "action_name", "jenga_probe_block");
    arm_group_name_ = mtc_jenga::param<std::string>(this, "arm_group", "ur_onrobot_manipulator");
    hand_group_name_ = mtc_jenga::param<std::string>(this, "hand_group", "ur_onrobot_gripper");
    gripper_tcp_ = mtc_jenga::param<std::string>(this, "gripper_tcp", "gripper_tcp");
    arm_home_state_ = mtc_jenga::param<std::string>(this, "arm_home_state", "test_configuration");
    closed_state_ = mtc_jenga::param<std::string>(this, "gripper_closed_state", "closed");

    box_x_ = mtc_jenga::param<double>(this, "block_box_x", 0.075);
    box_y_ = mtc_jenga::param<double>(this, "block_box_y", 0.025);
    box_z_ = mtc_jenga::param<double>(this, "block_box_z", 0.015);

    plan_max_attempts_ = static_cast<uint32_t>(mtc_jenga::param<int>(this, "plan_max_attempts", 1));
    plan_time_ = mtc_jenga::param<double>(this, "plan_time", 0.5);
    vel_scale_ = mtc_jenga::param<double>(this, "max_velocity_scaling_factor", 0.1);
    acc_scale_ = mtc_jenga::param<double>(this, "max_acceleration_scaling_factor", 0.1);
    cart_step_ = mtc_jenga::param<double>(this, "cartesian_step", 0.003);
    plan_max_attempts_ = static_cast<uint32_t>(mtc_jenga::param<int>(this, "plan_max_attempts", 1));
    plan_time_ = mtc_jenga::param<double>(this, "plan_time", 0.5);
    vel_scale_ = mtc_jenga::param<double>(this, "max_velocity_scaling_factor", 0.1);
    acc_scale_ = mtc_jenga::param<double>(this, "max_acceleration_scaling_factor", 0.1);
    cart_step_ = mtc_jenga::param<double>(this, "cartesian_step", 0.003);

    approach_min_ = mtc_jenga::param<double>(this, "approach_distance_min", 0.01);
    approach_max_ = mtc_jenga::param<double>(this, "approach_distance_max", 0.05);
    retreat_distance_ = mtc_jenga::param<double>(this, "retreat_distance", 0.02);

    ft_sensor_topic_ = mtc_jenga::param<std::string>(this, "ft_topic", "force_torque_sensor_broadcaster/wrench");
    stuck_force_threshold_n_ = mtc_jenga::param<double>(this, "stuck_force_threshold_n", 10.0);
    emergency_force_threshold_n_ = mtc_jenga::param<double>(this, "emergency_force_threshold_n", 30.0);
    stuck_dwell_samples_ = static_cast<int>(mtc_jenga::param<int>(this, "stuck_dwell_samples", 5));
    protrusion_target_m_ = mtc_jenga::param<double>(this, "protrusion_target_m", 0.02);
    push_velocity_m_s_ = mtc_jenga::param<double>(this, "push_velocity_m_s", 0.005);
    push_step_m_ = mtc_jenga::param<double>(this, "push_step_m", 0.002);

    probe_subframe_ = mtc_jenga::param<std::string>(this, "probe_subframe", "probe_plus");
    probe_r_ = mtc_jenga::param<double>(this, "probe_frame_roll",  0.0);
    probe_p_ = mtc_jenga::param<double>(this, "probe_frame_pitch", M_PI / 2.0);
    probe_y_ = mtc_jenga::param<double>(this, "probe_frame_yaw",   0.0);
    probe_offset_m_ = mtc_jenga::param<double>(this, "probe_offset_m", 0.045);

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
    RCLCPP_INFO(get_logger(), "mtc_probe_block_server: action=%s status=%s ft=%s",
                action_name_.c_str(), status_topic_.c_str(), ft_sensor_topic_.c_str());
  }

 private:
  // ---------------------------------------------------------------------------
  // Status helpers
  // ---------------------------------------------------------------------------
  // ---------------------------------------------------------------------------
  // Status helpers
  // ---------------------------------------------------------------------------
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
    task.stages()->setName("jenga_probe_approach");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", arm_group_name_);
    task.setProperty("eef", hand_group_name_);
    task.setProperty("ik_frame", gripper_tcp_);

    mtc::Stage* current_state_ptr = nullptr;
    {
      auto stage = std::make_unique<mtc::stages::CurrentState>("current");
      current_state_ptr = stage.get();
      task.add(std::move(stage));
    }

    auto interpolation_planner = std::make_shared<mtc::solvers::JointInterpolationPlanner>();
    interpolation_planner->setMaxVelocityScalingFactor(vel_scale_);
    interpolation_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarPathLengthOptimized");
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
      auto stage = std::make_unique<mtc::stages::MoveTo>("close gripper", interpolation_planner);
      stage->setGroup(hand_group_name_);
      stage->setGoal(closed_state_);
      task.add(std::move(stage));
    }
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
        stage->setIKFrame(gripper_tcp_);
        stage->setMinMaxDistance(approach_min_, approach_max_);
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = gripper_tcp_;
        vec.vector.x = -1.0;
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
        gen->setMonitoredStage(current_state_ptr);

        auto ik = std::make_unique<mtc::stages::ComputeIK>("probe IK", std::move(gen));
        ik->setMaxIKSolutions(8);
        ik->setMinSolutionDistance(0.5);
        ik->setIKFrame(rpyToIso(probe_r_, probe_p_, probe_y_), gripper_tcp_);
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
  mtc::Task buildRetreatTask() {
    mtc::Task task;
    task.stages()->setName("jenga_probe_retreat");
    auto node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", arm_group_name_);
    task.setProperty("ik_frame", gripper_tcp_);

    task.add(std::make_unique<mtc::stages::CurrentState>("current"));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarPathLengthOptimized");
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
      auto stage = std::make_unique<mtc::stages::MoveRelative>("retreat", cartesian_planner);
      stage->properties().set("marker_ns", "probe_retreat");
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setIKFrame(gripper_tcp_);
      stage->setMinMaxDistance(retreat_distance_, retreat_distance_);

      geometry_msgs::msg::Vector3Stamped vec;
      vec.header.frame_id = gripper_tcp_;
      vec.vector.x = 1.0;
      stage->setDirection(vec);
      task.add(std::move(stage));
    }
    {
      auto stage = std::make_unique<mtc::stages::MoveTo>("return home", sampling_planner);
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setGoal(arm_home_state_);
      stage->setTimeout(plan_time_);
      stage->setTimeout(plan_time_);
      task.add(std::move(stage));
    }

    return task;
  }

  // ---------------------------------------------------------------------------
  // MTC plan + execute helper
  // ---------------------------------------------------------------------------
  bool planAndExecuteMtc(mtc::Task& task, const char* label) {
  // ---------------------------------------------------------------------------
  // MTC plan + execute helper
  // ---------------------------------------------------------------------------
  bool planAndExecuteMtc(mtc::Task& task, const char* label) {
    try {
      task.init();
    } catch (const mtc::InitStageException& e) {
      RCLCPP_ERROR(get_logger(), "%s: MTC init failed: %s", label, e.what());
      RCLCPP_ERROR(get_logger(), "%s: MTC init failed: %s", label, e.what());
      return false;
    }
    if (!task.plan(plan_max_attempts_) || task.solutions().empty()) {
      RCLCPP_ERROR(get_logger(), "%s: MTC plan failed", label);
      RCLCPP_ERROR(get_logger(), "%s: MTC plan failed", label);
      return false;
    }
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "%s: E-stop active after planning; skipping execution", label);
      RCLCPP_WARN(get_logger(), "%s: E-stop active after planning; skipping execution", label);
      return false;
    }

    mtc_jenga::retimeArmSubTrajectoriesWithTotg(*task.solutions().front(),
                                                arm_group_name_, vel_scale_, acc_scale_, get_logger());
                                                arm_group_name_, vel_scale_, acc_scale_, get_logger());

    task.introspection().publishSolution(*task.solutions().front());
    auto res = task.execute(*task.solutions().front());
    if (res.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "%s: MTC execute failed: %d", label, res.val);
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
      move_group_->setEndEffectorLink(gripper_tcp_);
      RCLCPP_INFO(get_logger(), "MoveGroupInterface initialized for '%s' with EE '%s'",
                  arm_group_name_.c_str(), gripper_tcp_.c_str());
    }
  }

  Eigen::Vector3d probeAxisInWorld() const {
    auto pose_msg = move_group_->getCurrentPose(gripper_tcp_);
    const auto& q = pose_msg.pose.orientation;
    const Eigen::Quaterniond quat(q.w, q.x, q.y, q.z);
    return quat.normalized() * Eigen::Vector3d(-1.0, 0.0, 0.0);
  }

  PushResult runFtPushLoop() {
    PushResult result;
    ensureMoveGroup();

    // Tare: record bias wrench before contact
    Eigen::Vector3d wrench_bias = Eigen::Vector3d::Zero();
    auto w0 = getLatestWrench();
    if (w0) {
      wrench_bias = wrenchForceVec(*w0);
      RCLCPP_INFO(get_logger(), "FT tare: bias=(%.2f, %.2f, %.2f) N",
                  wrench_bias.x(), wrench_bias.y(), wrench_bias.z());
    } else {
      RCLCPP_WARN(get_logger(), "No FT data available for taring; proceeding with zero bias");
    }

    const double push_vel_scale = std::clamp(push_velocity_m_s_ / 0.1, 0.01, 1.0);
    int stuck_count = 0;

    while (rclcpp::ok()) {
      if (estop_.load()) {
        RCLCPP_WARN(get_logger(), "E-stop during push loop");
        result.outcome = PROBE_ERROR;
        break;
      }

      // Get current TCP pose and compute target waypoint
      auto current_pose = move_group_->getCurrentPose(gripper_tcp_);
      const Eigen::Vector3d push_dir = probeAxisInWorld();

      geometry_msgs::msg::Pose target = current_pose.pose;
      target.position.x += push_dir.x() * push_step_m_;
      target.position.y += push_dir.y() * push_step_m_;
      target.position.z += push_dir.z() * push_step_m_;

      // Plan a Cartesian path for this small step
      std::vector<geometry_msgs::msg::Pose> waypoints;
      waypoints.push_back(target);

      moveit_msgs::msg::RobotTrajectory trajectory_msg;
      const double fraction = move_group_->computeCartesianPath(
          waypoints, cart_step_, 0.0 /* jump_threshold */, trajectory_msg);

      if (fraction < 0.95) {
        RCLCPP_ERROR(get_logger(), "Cartesian path planning failed (fraction=%.2f)", fraction);
        result.outcome = PROBE_ERROR;
        break;
      }

      // Slow down the trajectory for the push
      auto& points = trajectory_msg.joint_trajectory.points;
      for (auto& pt : points) {
        double t_sec = pt.time_from_start.sec + pt.time_from_start.nanosec * 1e-9;
        t_sec /= std::max(push_vel_scale, 0.01);
        pt.time_from_start.sec = static_cast<int32_t>(t_sec);
        pt.time_from_start.nanosec = static_cast<uint32_t>((t_sec - pt.time_from_start.sec) * 1e9);
      }

      moveit::planning_interface::MoveGroupInterface::Plan plan;
      plan.trajectory_ = trajectory_msg;
      auto exec_result = move_group_->execute(plan);
      if (exec_result != moveit::core::MoveItErrorCode::SUCCESS) {
        RCLCPP_ERROR(get_logger(), "Push segment execute failed: %d", exec_result.val);
        result.outcome = PROBE_ERROR;
        break;
      }

      result.displacement_m += push_step_m_;

      // Read F/T and compute contact force along probe axis
      auto wrench = getLatestWrench();
      if (wrench) {
        const Eigen::Vector3d force = wrenchForceVec(*wrench) - wrench_bias;
        const Eigen::Vector3d probe_dir = probeAxisInWorld();
        const double contact_force = force.dot(probe_dir);
        const double force_magnitude = std::abs(contact_force);

        result.max_force_n = std::max(result.max_force_n, force_magnitude);

        RCLCPP_DEBUG(get_logger(), "Push: disp=%.4f m, force=%.2f N (threshold=%.1f N)",
                    result.displacement_m, force_magnitude, stuck_force_threshold_n_);

        if (force_magnitude >= emergency_force_threshold_n_) {
          RCLCPP_WARN(get_logger(), "Emergency force threshold exceeded: %.2f N >= %.1f N",
                      force_magnitude, emergency_force_threshold_n_);
          result.outcome = PROBE_STUCK;
          break;
        }

        if (force_magnitude >= stuck_force_threshold_n_) {
          ++stuck_count;
          if (stuck_count >= stuck_dwell_samples_) {
            RCLCPP_INFO(get_logger(), "Block is STUCK: force=%.2f N sustained for %d samples",
                        force_magnitude, stuck_count);
            result.outcome = PROBE_STUCK;
            break;
          }
        } else {
          stuck_count = 0;
        }
      }

      if (result.displacement_m >= protrusion_target_m_) {
        RCLCPP_INFO(get_logger(), "Block is LOOSE: pushed %.4f m (target %.4f m), max_force=%.2f N",
                    result.displacement_m, protrusion_target_m_, result.max_force_n);
        result.outcome = PROBE_LOOSE;
        break;
      }
    }

    // Back away along +X in gripper_tcp (reverse of push direction)
    if (result.displacement_m > 1e-6) {
      RCLCPP_INFO(get_logger(), "Backing away %.4f m along probe reverse axis", result.displacement_m);
      auto current_pose = move_group_->getCurrentPose(gripper_tcp_);
      const Eigen::Vector3d retreat_dir = probeAxisInWorld() * -1.0;

      geometry_msgs::msg::Pose retreat_target = current_pose.pose;
      retreat_target.position.x += retreat_dir.x() * result.displacement_m;
      retreat_target.position.y += retreat_dir.y() * result.displacement_m;
      retreat_target.position.z += retreat_dir.z() * result.displacement_m;

      std::vector<geometry_msgs::msg::Pose> waypoints;
      waypoints.push_back(retreat_target);

      moveit_msgs::msg::RobotTrajectory traj_msg;
      const double fraction = move_group_->computeCartesianPath(
          waypoints, cart_step_, 0.0, traj_msg);

      if (fraction >= 0.95) {
        moveit::planning_interface::MoveGroupInterface::Plan plan;
        plan.trajectory_ = traj_msg;
        auto exec_result = move_group_->execute(plan);
        if (exec_result != moveit::core::MoveItErrorCode::SUCCESS) {
          RCLCPP_WARN(get_logger(), "Back-away execute failed: %d", exec_result.val);
        }
      } else {
        RCLCPP_WARN(get_logger(), "Back-away Cartesian path planning failed (fraction=%.2f)", fraction);
      }
    }

    return result;
  }

  // ---------------------------------------------------------------------------
  // Three-phase orchestrator
  // ---------------------------------------------------------------------------
  bool runProbe(const geometry_msgs::msg::PoseStamped& block_pose,
                const std::string& block_id,
                PushResult& push_result_out) {
    push_result_out = {};

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

    // Phase 2: FT-monitored push
    RCLCPP_INFO(get_logger(), "Phase 2: FT-monitored push (target=%.4f m, stuck_threshold=%.1f N)",
                protrusion_target_m_, stuck_force_threshold_n_);
    push_result_out = runFtPushLoop();

    // Phase 3: MTC retreat + return home
    RCLCPP_INFO(get_logger(), "Phase 3: MTC retreat + home");
    mtc::Task retreat_task = buildRetreatTask();
    if (!planAndExecuteMtc(retreat_task, "Phase3-Retreat")) {
      RCLCPP_WARN(get_logger(), "Phase 3 retreat failed; probe result is still valid");
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
    setBusy(true);
    auto res = std::make_shared<JengaProbeBlock::Result>();
    if (estop_.load()) {
      res->score = 0.0F;
      res->probe_outcome = PROBE_ERROR;
      res->probe_outcome = PROBE_ERROR;
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

    send_fb("probe_approach", 0.0F);
    send_fb("probe_approach", 0.0F);
    const std::string block_id = mtc_jenga::blockIdFromIndex(goal->block_index);

    PushResult push_result;
    const bool ok = runProbe(goal->block_pose, block_id, push_result);


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
      res->message = (push_result.outcome == PROBE_LOOSE) ? "loose" : "stuck";
      res->error_code = 0;
      executions_completed_ += 1;
      goal_handle->succeed(res);
    } else {
      res->success = false;
      res->message = "probe failed";
      res->message = "probe failed";
      res->error_code = 1;
      goal_handle->abort(res);
    }

    setBusy(false);
  }

  // ---------------------------------------------------------------------------
  // Members
  // ---------------------------------------------------------------------------
  // ---------------------------------------------------------------------------
  // Members
  // ---------------------------------------------------------------------------
  rclcpp_action::Server<JengaProbeBlock>::SharedPtr action_server_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Subscription<geometry_msgs::msg::WrenchStamped>::SharedPtr sub_ft_;
  rclcpp::Subscription<geometry_msgs::msg::WrenchStamped>::SharedPtr sub_ft_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;

  mutable std::mutex ft_mutex_;
  geometry_msgs::msg::WrenchStamped ft_latest_;
  bool ft_received_{false};

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_;

  mutable std::mutex ft_mutex_;
  geometry_msgs::msg::WrenchStamped ft_latest_;
  bool ft_received_{false};

  std::shared_ptr<moveit::planning_interface::MoveGroupInterface> move_group_;

  std::string action_name_;
  std::string arm_group_name_;
  std::string hand_group_name_;
  std::string arm_group_name_;
  std::string hand_group_name_;
  std::string gripper_tcp_;
  std::string arm_home_state_;
  std::string closed_state_;
  std::string closed_state_;
  std::string status_topic_;
  std::string ft_sensor_topic_;

  double box_x_{0.075}, box_y_{0.025}, box_z_{0.015};
  uint32_t plan_max_attempts_{3};
  double plan_time_{0.5};
  double plan_time_{0.5};
  double vel_scale_{0.20};
  double acc_scale_{0.20};
  double cart_step_{0.003};

  double approach_min_{0.01}, approach_max_{0.05};
  double retreat_distance_{0.02};

  double stuck_force_threshold_n_{10.0};
  double emergency_force_threshold_n_{30.0};
  int stuck_dwell_samples_{5};
  double protrusion_target_m_{0.02};
  double push_velocity_m_s_{0.005};
  double push_step_m_{0.002};

  std::string probe_subframe_{"probe_plus"};
  double probe_r_{0.0};
  double probe_p_{M_PI / 2.0};
  double probe_y_{0.0};
  double probe_offset_m_{0.045};

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
