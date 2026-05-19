#pragma once

#include <cstdint>
#include <iomanip>
#include <memory>
#include <sstream>
#include <string>

#include <geometry_msgs/msg/pose.hpp>
#include <moveit/planning_scene_interface/planning_scene_interface.h>
#include <moveit/task_constructor/storage.h>
#include <moveit/task_constructor/task.h>
#include <moveit/trajectory_processing/time_optimal_trajectory_generation.h>
#include <moveit_msgs/msg/collision_object.hpp>
#include <rclcpp/logger.hpp>
#include <rclcpp/node.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <shape_msgs/msg/solid_primitive.hpp>

namespace mtc_jenga {

/// Declare a parameter if not already declared, then return its current value.
/// Use this instead of bare declare_parameter() when the node was constructed
/// with automatically_declare_parameters_from_overrides(true), which may have
/// pre-declared some parameters from params-file overrides.
template<typename T>
inline T param(rclcpp::Node* node, const std::string& name, const T& default_value) {
  if (!node->has_parameter(name)) {
    node->declare_parameter<T>(name, default_value);
  }
  return node->get_parameter(name).get_value<T>();
}

/// Terminal outcome for e-stop (and similar server-side stops). Uses `canceled()` only when the
/// client requested cancel (`is_canceling()`); otherwise `abort()`, which matches ROS 2 action FSM
/// rules and avoids RCLError from calling `canceled()` while still in plain EXECUTING.
template <typename ActionT>
inline void finish_action_goal_estop(
    const std::shared_ptr<rclcpp_action::ServerGoalHandle<ActionT>>& goal_handle,
    const std::shared_ptr<typename ActionT::Result>& res) {
  res->success = false;
  res->message = "estop";
  res->error_code = 4;
  if (goal_handle->is_canceling()) {
    goal_handle->canceled(res);
  } else {
    goal_handle->abort(res);
  }
}

inline std::string blockIdFromIndex(const uint32_t idx) {
  std::ostringstream o;
  o << "block_" << std::setw(2) << std::setfill('0') << idx;
  return o.str();
}

inline void applyBlockBoxAt(const std::string& block_id,
                            const std::string& frame_id,
                            const geometry_msgs::msg::Pose& pose,
                            const double box_x,
                            const double box_y,
                            const double box_z,
                            const double grasp_offset_m = 0.035,
                            const double probe_offset_m = -1.0) {
  moveit::planning_interface::PlanningSceneInterface psi;
  moveit_msgs::msg::CollisionObject co;
  co.id = block_id;
  co.header.frame_id = frame_id.empty() ? "world" : frame_id;
  co.primitives.resize(1);
  co.primitives[0].type = shape_msgs::msg::SolidPrimitive::BOX;
  co.primitives[0].dimensions = {box_x, box_y, box_z};
  co.primitive_poses = {pose};

  // Define standard subframes in object-local coordinates.
  // Subframe naming convention follows MoveIt: usable frames become "<id>/<subframe>".
  const double half_len = 0.5 * box_x;
  const double eff_probe = (probe_offset_m < 0.0) ? half_len : probe_offset_m;

  auto make_subframe_pose = [](const double dx, const double dy = 0.0, const double dz = 0.0) {
    geometry_msgs::msg::Pose p;
    p.orientation.w = 1.0;
    p.position.x = dx;
    p.position.y = dy;
    p.position.z = dz;
    return p;
  };

  co.subframe_names = {"end_plus", "end_minus", "grasp_plus", "grasp_minus",
                       "probe_plus", "probe_minus"};
  co.subframe_poses = {make_subframe_pose(+half_len),
                       make_subframe_pose(-half_len),
                       make_subframe_pose(+grasp_offset_m),
                       make_subframe_pose(-grasp_offset_m),
                       make_subframe_pose(+eff_probe),
                       make_subframe_pose(-eff_probe)};

  // ADD acts as "add or replace", which is robust for updating poses.
  co.operation = moveit_msgs::msg::CollisionObject::ADD;
  psi.applyCollisionObject(co);
}

inline void retimeArmSubTrajectoriesWithTotg(const moveit::task_constructor::SolutionBase& root_solution,
                                             const std::string& arm_group,
                                             const double vel_scale,
                                             const double acc_scale,
                                             const rclcpp::Logger& logger) {
  trajectory_processing::TimeOptimalTrajectoryGeneration totg;
  auto enforce_monotonic = [](robot_trajectory::RobotTrajectory& t) {
    for (std::size_t i = 1; i < t.getWayPointCount(); ++i) {
      if (t.getWayPointDurationFromPrevious(i) < 1e-6) {
        t.setWayPointDurationFromPrevious(i, 1e-3);
      }
    }
  };

  std::function<void(const moveit::task_constructor::SolutionBase&)> walk =
      [&](const moveit::task_constructor::SolutionBase& s) {
        if (const auto* seq = dynamic_cast<const moveit::task_constructor::SolutionSequence*>(&s)) {
          for (const moveit::task_constructor::SolutionBase* sub : seq->solutions()) {
            if (sub) walk(*sub);
          }
          return;
        }
        if (const auto* st = dynamic_cast<const moveit::task_constructor::SubTrajectory*>(&s)) {
          auto traj_const = st->trajectory();
          if (!traj_const || traj_const->getWayPointCount() < 2) return;
          if (traj_const->getGroupName() != arm_group) return;
          auto traj = std::const_pointer_cast<robot_trajectory::RobotTrajectory>(traj_const);
          if (!totg.computeTimeStamps(*traj, vel_scale, acc_scale)) {
            RCLCPP_WARN(logger,
                        "TOTG re-time failed on arm sub-trajectory; falling back to monotonicity safety net");
          }
          enforce_monotonic(*traj);
        }
      };
  walk(root_solution);
}

}  // namespace mtc_jenga

