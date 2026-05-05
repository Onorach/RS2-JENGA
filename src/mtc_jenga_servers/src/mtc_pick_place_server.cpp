
#include <cstdint>
#include <atomic>
#include <chrono>
#include <iomanip>
#include <memory>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <thread>

#include <rclcpp/rclcpp.hpp>
#include <rclcpp/executors/single_threaded_executor.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <jenga_interfaces/action/jenga_pick_place.hpp>
#include <moveit_task_constructor_msgs/action/execute_task_solution.hpp>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <moveit_msgs/msg/move_it_error_codes.hpp>
#include <moveit/task_constructor/solvers.h>
#include <moveit/task_constructor/stages.h>
#include <moveit/task_constructor/task.h>
#include <moveit/trajectory_processing/time_optimal_trajectory_generation.h>
#include <moveit/task_constructor/storage.h>
#include <shape_msgs/msg/solid_primitive.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>
#if __has_include(<tf2_eigen/tf2_eigen.hpp>)
#include <tf2_eigen/tf2_eigen.hpp>
#else
#include <tf2_eigen/tf2_eigen.h>
#endif
#if __has_include(<tf2_geometry_msgs/tf2_geometry_msgs.hpp>)
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#else
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#endif

#include <Eigen/Geometry>

#include "mtc_pick_place/mtc_server_common.hpp"

namespace mtc = moveit::task_constructor;
using JengaPickPlace = jenga_interfaces::action::JengaPickPlace;
using ServerGoalHandle = rclcpp_action::ServerGoalHandle<JengaPickPlace>;

class MtcPickPlaceServer : public rclcpp::Node {
 public:
  explicit MtcPickPlaceServer(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : rclcpp::Node("mtc_pick_place_server", options) {
    mode_ = declare_parameter("mode", "single_pose");
    ur_onrobot_manipulator = declare_parameter("arm_group", "ur_onrobot_manipulator");
    ur_onrobot_gripper = declare_parameter("hand_group", "ur_onrobot_gripper");
    gripper_tcp = declare_parameter("gripper_tcp", "gripper_tcp");
    ee_link_for_move_group_ = declare_parameter("ee_link", "gripper_tcp");
    object_id_ = declare_parameter("object_id", "object");
    box_x_ = declare_parameter("object_box_x", 0.075);
    box_y_ = declare_parameter("object_box_y", 0.025);
    box_z_ = declare_parameter("object_box_z", 0.015);
    open_state_ = declare_parameter("gripper_open_state", "open");
    closed_state_ = declare_parameter("gripper_closed_state", "grip_block_length");
    arm_home_state_ = declare_parameter("arm_home_state", "ready_position");
    plan_max_attempts_ = static_cast<uint32_t>(declare_parameter("plan_max_attempts", 3));
    status_topic_ = declare_parameter("status_topic", "mtc_status");
    const std::string goal_topic = declare_parameter("goal_topic", "goal_pose");
    add_demo_table_ = declare_parameter("add_demo_table", false);
    (void)declare_parameter("action_timeout_sec", 600);
    vel_scale_ = declare_parameter("max_velocity_scaling_factor", 0.1);
    acc_scale_ = declare_parameter("max_acceleration_scaling_factor", 0.1);

    action_server_ = rclcpp_action::create_server<JengaPickPlace>(
        this, "jenga_pick_place",
        [this](const rclcpp_action::GoalUUID& uuid, std::shared_ptr<const JengaPickPlace::Goal> goal) {
          (void)uuid;
          (void)goal;
          if (busy_.load()) {
            return rclcpp_action::GoalResponse::REJECT;
          }
          if (estop_.load()) {
            return rclcpp_action::GoalResponse::REJECT;
          }
          return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
        },
        [this](const std::shared_ptr<rclcpp_action::ServerGoalHandle<JengaPickPlace>> handle) {
          (void)handle;
          return rclcpp_action::CancelResponse::ACCEPT;
        },
        [this](std::shared_ptr<rclcpp_action::ServerGoalHandle<JengaPickPlace>> handle) {
          this->onActionAccepted(std::move(handle));
        });

    sub_goal_ = create_subscription<geometry_msgs::msg::PoseStamped>(
        goal_topic, 10, [this](const geometry_msgs::msg::PoseStamped::SharedPtr msg) { this->onGoalPose(*msg); });

    pub_status_ = create_publisher<std_msgs::msg::String>(status_topic_, 10);

    sub_estop_ = create_subscription<std_msgs::msg::Bool>(
        "/estop", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });
    // Prefer /estop_active when estop_node is running, but keep /estop for fallback.
    sub_estop_active_ = create_subscription<std_msgs::msg::Bool>(
        "/estop_active", 10, [this](const std_msgs::msg::Bool::SharedPtr msg) { estop_ = msg->data; });

    RCLCPP_INFO(get_logger(),
                "mtc_pick_place_server: mode=%s, status=%s, action=/jenga_pick_place, "
                "max_vel_scale=%.3f max_acc_scale=%.3f",
                mode_.c_str(), status_topic_.c_str(), vel_scale_, acc_scale_);
  }

  void onActionAccepted(std::shared_ptr<rclcpp_action::ServerGoalHandle<JengaPickPlace>> handle) {
    if (!handle) {
      return;
    }
    std::thread{[this, h = std::move(handle)]() { executeAction(h); }}.detach();
  }

 private:
  void publishStatus(const std::string& phase) {
    std::lock_guard<std::mutex> s(status_mutex_);
    status_phase_ = phase;
    const bool b = busy_.load();
    const int c = static_cast<int>(executions_completed_.load());
    const bool e = estop_.load();
    std::ostringstream o;
    o << "{\"state\":\"" << phase << "\",\"busy\":" << (b ? "true" : "false") << ",\"executions_completed\":" << c
      << ",\"estop_active\":" << (e ? "true" : "false") << "}";
    std_msgs::msg::String m;
    m.data = o.str();
    pub_status_->publish(m);
  }

  void setBusy(const bool b) {
    busy_.store(b);
    if (b) {
      publishStatus("running");
    } else {
      publishStatus("idle");
    }
  }

  static std::string blockIdFromIndex(const uint32_t idx) {
    std::ostringstream o;
    o << "block_" << std::setw(2) << std::setfill('0') << idx;
    return o.str();
  }

  void applyBlockAt(const std::string& block_id,
                    const std::string& frame_id,
                    const geometry_msgs::msg::Pose& pose) {
    moveit::planning_interface::PlanningSceneInterface psi;
    moveit_msgs::msg::CollisionObject co;
    co.id = block_id;
    co.header.frame_id = frame_id.empty() ? "world" : frame_id;
    co.primitives.resize(1);
    co.primitives[0].type = shape_msgs::msg::SolidPrimitive::BOX;
    co.primitives[0].dimensions = {box_x_, box_y_, box_z_};
    co.primitive_poses = {pose};
    // ADD acts as "add or replace", which is robust for updating poses.
    co.operation = moveit_msgs::msg::CollisionObject::ADD;
    psi.applyCollisionObject(co);
  }

  bool runMoveGroupToPose(const geometry_msgs::msg::PoseStamped& target) {
    try {
      moveit::planning_interface::MoveGroupInterface mgi(rclcpp::Node::shared_from_this(), ur_onrobot_manipulator);
      mgi.setEndEffectorLink(ee_link_for_move_group_);
      mgi.setPoseReferenceFrame(target.header.frame_id);
      mgi.setPoseTarget(target.pose, ee_link_for_move_group_);
      mgi.setMaxVelocityScalingFactor(vel_scale_);
      mgi.setMaxAccelerationScalingFactor(acc_scale_);
      moveit::core::MoveItErrorCode const code = mgi.move();
      return (code == moveit::core::MoveItErrorCode::SUCCESS);
    } catch (const std::exception& ex) {
      RCLCPP_ERROR(get_logger(), "MoveGroupInterface failed: %s", ex.what());
      return false;
    }
  }

  mtc::Task buildPickPlaceTask(const geometry_msgs::msg::PoseStamped& place_in_world,
                               const std::string& block_id) {
    mtc::Task task;
    task.stages()->setName("jenga_pick_place");
    rclcpp::Node::SharedPtr const node_ptr = rclcpp::Node::shared_from_this();
    task.loadRobotModel(node_ptr);
    task.setProperty("group", ur_onrobot_manipulator);
    task.setProperty("eef", ur_onrobot_gripper);
    task.setProperty("ik_frame", gripper_tcp);

    mtc::Stage* current_state_ptr = nullptr;
    auto stage_state_current = std::make_unique<mtc::stages::CurrentState>("current");
    current_state_ptr = stage_state_current.get();
    task.add(std::move(stage_state_current));

    auto sampling_planner = std::make_shared<mtc::solvers::PipelinePlanner>(node_ptr);
    sampling_planner->setPlannerId("RRTstarkConfigDefault");
    sampling_planner->setProperty("goal_joint_tolerance", 1e-4);
    sampling_planner->setProperty("planning_time", 2.0);  // seconds
    sampling_planner->setProperty("enforce_joint_model_state_space", true);
    sampling_planner->setMaxVelocityScalingFactor(vel_scale_);
    sampling_planner->setMaxAccelerationScalingFactor(acc_scale_);

    auto interpolation_planner = std::make_shared<mtc::solvers::JointInterpolationPlanner>();
    interpolation_planner->setMaxVelocityScalingFactor(vel_scale_);
    interpolation_planner->setMaxAccelerationScalingFactor(acc_scale_);
    auto cartesian_planner = std::make_shared<mtc::solvers::CartesianPath>();
    cartesian_planner->setMaxVelocityScalingFactor(vel_scale_);
    cartesian_planner->setMaxAccelerationScalingFactor(acc_scale_);
    cartesian_planner->setStepSize(0.005);

    {
      auto stage_open = std::make_unique<mtc::stages::MoveTo>("open hand", interpolation_planner);
      stage_open->setGroup(ur_onrobot_gripper);
      stage_open->setGoal(open_state_);
      task.add(std::move(stage_open));
    }
    {
      auto stage_mtp = std::make_unique<mtc::stages::Connect>(
          "move to pick", mtc::stages::Connect::GroupPlannerVector{{ur_onrobot_manipulator, sampling_planner}});
      stage_mtp->setTimeout(2.0);
      stage_mtp->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(stage_mtp));
    }

    mtc::Stage* attach_object_stage = nullptr;
    {
      auto grasp = std::make_unique<mtc::SerialContainer>("pick object");
      task.properties().exposeTo(grasp->properties(), {"eef", "group", "ik_frame"});
      grasp->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group", "ik_frame"});

      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("approach object", cartesian_planner);
        stage->properties().set("marker_ns", "approach_object");
        stage->properties().set("link", gripper_tcp);
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setMinMaxDistance(0.025, 0.1);
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = gripper_tcp;
        vec.vector.z = 1.0;
        stage->setDirection(vec);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::GenerateGraspPose>("generate grasp pose");
        stage->properties().configureInitFrom(mtc::Stage::PARENT);
        stage->properties().set("marker_ns", "grasp_pose");
        stage->setPreGraspPose(open_state_);
        stage->setObject(block_id);
        stage->setAngleDelta(M_PI / 1.0);
        stage->setMonitoredStage(current_state_ptr);
        // Ry(180°) flips the IK frame z-axis: GenerateGraspPose's upward target-z becomes
        // gripper_tcp z pointing downward — top-down approach within ~0° of vertical.
        // Y axis is preserved under Ry(180°), so the finger opening direction sweeps with
        // angle_delta and IK selects the wrist angle that keeps tips parallel to the
        // 2.5×1.5 cm block end faces.
        // Eigen::Isometry3d gft = Eigen::Isometry3d::Identity() * Eigen::AngleAxisd(M_PI / 2, Eigen::Vector3d::UnitZ());
        // gft.linear() = Eigen::AngleAxisd(M_PI, Eigen::Vector3d::UnitY()).matrix();
        Eigen::Isometry3d gft = Eigen::Isometry3d::Identity();
        gft = gft * Eigen::AngleAxisd(M_PI, Eigen::Vector3d::UnitY()) 
                  * Eigen::AngleAxisd(M_PI / 2, Eigen::Vector3d::UnitZ());
        // gft = gft * Eigen::AngleAxisd(M_PI, Eigen::Vector3d::UnitY());
        auto w = std::make_unique<mtc::stages::ComputeIK>("grasp pose IK", std::move(stage));
        w->setMaxIKSolutions(8);
        w->setMinSolutionDistance(0.5);
        w->setIKFrame(gft, gripper_tcp);
        w->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        w->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        grasp->insert(std::move(w));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("allow collision (hand,object)");
        stage->allowCollisions(block_id, task.getRobotModel()->getJointModelGroup(ur_onrobot_gripper)->getLinkModelNamesWithCollisionGeometry(), true);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveTo>("close hand", interpolation_planner);
        stage->setGroup(ur_onrobot_gripper);
        stage->setGoal(closed_state_);
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("attach object");
        stage->attachObject(block_id, gripper_tcp);
        attach_object_stage = stage.get();
        grasp->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("lift object", cartesian_planner);
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setMinMaxDistance(0.02, 0.1);
        stage->setIKFrame(gripper_tcp);
        stage->properties().set("marker_ns", "lift_object");
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
          "move to place", mtc::stages::Connect::GroupPlannerVector{{ur_onrobot_manipulator, sampling_planner}});
      c->setTimeout(2.0);
      c->properties().configureInitFrom(mtc::Stage::PARENT);
      task.add(std::move(c));
    }
    {
      auto place = std::make_unique<mtc::SerialContainer>("place object");
      task.properties().exposeTo(place->properties(), {"eef", "group", "ik_frame"});
      place->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group", "ik_frame"});

      // lower object is inserted first (analogous to approach object in pick), making it
      // a backward stage that creates the pre-place approach pose from the final IK state.
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("lower object", cartesian_planner);
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setIKFrame(gripper_tcp);
        stage->setMinMaxDistance(0.03, 0.10);
        stage->properties().set("marker_ns", "lower_object");
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = "world";
        vec.vector.z = -1.0;
        stage->setDirection(vec);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::GeneratePlacePose>("generate place pose");
        stage->properties().configureInitFrom(mtc::Stage::PARENT);
        stage->properties().set("marker_ns", "place_pose");
        stage->setObject(block_id);
        geometry_msgs::msg::PoseStamped target;
        target.header.frame_id = place_in_world.header.frame_id;
        target.header.stamp = place_in_world.header.stamp;
        target.pose = place_in_world.pose;
        stage->setPose(target);
        stage->setMonitoredStage(attach_object_stage);
        auto w = std::make_unique<mtc::stages::ComputeIK>("place pose IK", std::move(stage));
        w->setMaxIKSolutions(8);
        w->setMinSolutionDistance(0.5);
        w->setIKFrame(block_id);
        w->properties().configureInitFrom(mtc::Stage::PARENT, {"eef", "group"});
        w->properties().configureInitFrom(mtc::Stage::INTERFACE, {"target_pose"});
        place->insert(std::move(w));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveTo>("open hand (place)", interpolation_planner);
        stage->setGroup(ur_onrobot_gripper);
        stage->setGoal(open_state_);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("forbid collision (hand,object)");
        stage->allowCollisions(block_id, task.getRobotModel()->getJointModelGroup(ur_onrobot_gripper)->getLinkModelNamesWithCollisionGeometry(), false);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::ModifyPlanningScene>("detach object");
        stage->detachObject(block_id, gripper_tcp);
        place->insert(std::move(stage));
      }
      {
        auto stage = std::make_unique<mtc::stages::MoveRelative>("retreat", cartesian_planner);
        stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
        stage->setMinMaxDistance(0.02, 0.1);
        stage->setIKFrame(gripper_tcp);
        stage->properties().set("marker_ns", "retreat");
        geometry_msgs::msg::Vector3Stamped vec;
        vec.header.frame_id = "world";
        vec.vector.z = 1.0;
        stage->setDirection(vec);
        place->insert(std::move(stage));
      }
      task.add(std::move(place));
    }
    {
      auto stage = std::make_unique<mtc::stages::MoveTo>("return home", sampling_planner);
      stage->properties().configureInitFrom(mtc::Stage::PARENT, {"group"});
      stage->setGoal(arm_home_state_);
      stage->setTimeout(2.0);
      task.add(std::move(stage));
    }
    return task;
  }

  bool runPickPlaceMtc(const geometry_msgs::msg::PoseStamped& pick,
                       const geometry_msgs::msg::PoseStamped& place,
                       const std::string& block_id) {
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop active: refusing to plan/execute MTC task");
      return false;
    }
    if (pick.header.frame_id != "world" && !pick.header.frame_id.empty()) {
      RCLCPP_WARN(get_logger(), "For MTC, pick frame_id should typically be 'world' (got '%s')", pick.header.frame_id.c_str());
    }
    applyBlockAt(block_id, pick.header.frame_id, pick.pose);

    mtc::Task task = buildPickPlaceTask(place, block_id);
    try {
      task.init();
    } catch (const mtc::InitStageException& e) {
      RCLCPP_ERROR(get_logger(), "MTC init failed: %s", e.what());
      return false;
    }
    if (!task.plan(plan_max_attempts_)) {
      RCLCPP_ERROR(get_logger(), "MTC plan failed");
      return false;
    }
    if (task.solutions().empty()) {
      return false;
    }
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop became active after planning; skipping execution");
      return false;
    }
    
    // Re-parameterize arm sub-trajectories with TOTG to fix zero/duplicate
    // timestamps from OMPL's pipeline (moveit_task_constructor#624 / #578).
    // Done per-sub-trajectory so we don't disturb gripper or scene-only stages.
    trajectory_processing::TimeOptimalTrajectoryGeneration totg;
    const double vel_scale = vel_scale_;
    const double acc_scale = acc_scale_;

    // Safety net: if TOTG ever leaves a zero-duration segment, nudge it just
    // enough to keep monotonicity. With proper joint limits this rarely fires.
    auto enforce_monotonic = [](robot_trajectory::RobotTrajectory& t) {
      for (std::size_t i = 1; i < t.getWayPointCount(); ++i) {
        if (t.getWayPointDurationFromPrevious(i) < 1e-6) {
          t.setWayPointDurationFromPrevious(i, 1e-3);
        }
      }
    };

    std::function<void(const mtc::SolutionBase&)> walk =
        [&](const mtc::SolutionBase& s) {
          if (const auto* seq = dynamic_cast<const mtc::SolutionSequence*>(&s)) {
            for (const mtc::SolutionBase* sub : seq->solutions()) {
              if (sub) walk(*sub);
            }
            return;
          }
          if (const auto* st = dynamic_cast<const mtc::SubTrajectory*>(&s)) {
            auto traj_const = st->trajectory();
            if (!traj_const || traj_const->getWayPointCount() < 2) return;
            // Only re-time arm trajectories. Gripper traj is single-DOF
            // JointInterpolation and was executing fine.
            if (traj_const->getGroupName() != ur_onrobot_manipulator) return;
            auto traj = std::const_pointer_cast<robot_trajectory::RobotTrajectory>(traj_const);
            if (!totg.computeTimeStamps(*traj, vel_scale, acc_scale)) {
              RCLCPP_WARN(get_logger(),
                          "TOTG re-time failed on arm sub-trajectory; "
                          "falling back to monotonicity safety net");
            }
            enforce_monotonic(*traj);
          }
        };
    walk(*task.solutions().front());
    
    task.introspection().publishSolution(*task.solutions().front());
    auto res = task.execute(*task.solutions().front());
    if (res.val != moveit_msgs::msg::MoveItErrorCodes::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "MTC execute failed: %d", res.val);
      return false;
    }
    // Persist the block at its placed pose for subsequent plans.
    applyBlockAt(block_id, place.header.frame_id, place.pose);
    return true;
  }

  void executeAction(const std::shared_ptr<rclcpp_action::ServerGoalHandle<JengaPickPlace>> goal_handle) {
    setBusy(true);
    auto res = std::make_shared<JengaPickPlace::Result>();
    if (estop_.load()) {
      mtc_jenga::finish_action_goal_estop(goal_handle, res);
      setBusy(false);
      return;
    }
    const auto goal = goal_handle->get_goal();
    rclcpp::Rate rate(2.0);
    auto fb = std::make_shared<JengaPickPlace::Feedback>();
    auto send_fb = [goal_handle, &fb, &rate](const char* s, float p) {
      fb->current_stage = s;
      fb->progress_pct = p;
      goal_handle->publish_feedback(fb);
      rate.sleep();
    };
    send_fb("pick_place_start", 0.0F);
    const std::string block_id = blockIdFromIndex(goal->block_index);
    const bool ok = runPickPlaceMtc(goal->pick_pose, goal->place_pose, block_id);
    send_fb("pick_place_done", 100.0F);
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

  void onGoalPose(const geometry_msgs::msg::PoseStamped& msg) {
    if (estop_.load()) {
      RCLCPP_WARN(get_logger(), "E-stop: ignoring /goal_pose");
      return;
    }
    const bool awaiting_pair = waiting_for_pair_.load();
    if (busy_.load() && !awaiting_pair) {
      RCLCPP_WARN(get_logger(), "Busy: dropping /goal_pose");
      return;
    }
    if (mode_ == "paired_pose") {
      if (!awaiting_pair) {
        pending_pick_ = msg;
        busy_.store(true);
        waiting_for_pair_.store(true);
        publishStatus("waiting second pose (paired)");
        RCLCPP_INFO(get_logger(), "paired_pose: received first /goal_pose (pick) — send second for place");
        return;
      }
      waiting_for_pair_.store(false);
      const uint32_t idx = next_block_index_.fetch_add(1u);
      const std::string block_id = blockIdFromIndex(idx);
      const bool success = runPickPlaceMtc(*pending_pick_, msg, block_id);
      pending_pick_.reset();
      if (success) {
        executions_completed_ += 1;
      }
      setBusy(false);
      return;
    }
    setBusy(true);
    const bool success = runMoveGroupToPose(msg);
    if (success) {
      executions_completed_ += 1;
    }
    setBusy(false);
  }

  rclcpp_action::Server<JengaPickPlace>::SharedPtr action_server_;
  rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr sub_goal_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr sub_estop_active_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_status_;

  std::string mode_;
  std::string ur_onrobot_manipulator, ur_onrobot_gripper, gripper_tcp, ee_link_for_move_group_;
  std::string object_id_, open_state_, closed_state_, arm_home_state_;
  std::string status_topic_;
  bool add_demo_table_{false};
  double box_x_, box_y_, box_z_;
  double vel_scale_{0.1};
  double acc_scale_{0.1};
  uint32_t plan_max_attempts_{5};

  std::mutex status_mutex_;
  std::atomic<bool> busy_{false};
  std::atomic<bool> waiting_for_pair_{false};
  std::atomic<int> executions_completed_{0};
  std::string status_phase_{"idle"};
  std::atomic<bool> estop_{false};
  std::atomic<uint32_t> next_block_index_{0u};

  std::optional<geometry_msgs::msg::PoseStamped> pending_pick_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto n = std::make_shared<MtcPickPlaceServer>();
  // Several callbacks (action server, subscriptions) can run concurrently with goal work.
  rclcpp::executors::MultiThreadedExecutor e(rclcpp::ExecutorOptions(), 4u);
  e.add_node(n);
  e.spin();
  rclcpp::shutdown();
  return 0;
}
