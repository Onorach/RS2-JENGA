// Simple MoveIt2 C++ demo node for the UR3e.
// Plans a motion for the "ur_manipulator" group to a hard-coded pose and executes it.

#include <memory>
#include <thread>

#include <geometry_msgs/msg/pose.hpp>
#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.h>

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);

  auto const logger = rclcpp::get_logger("ur3_cpp_node");

  rclcpp::NodeOptions node_options;
  node_options.automatically_declare_parameters_from_overrides(true);
  auto node = rclcpp::Node::make_shared("ur3_cpp_node", node_options);

  // Spin an executor so MoveGroupInterface can query TF/joint states.
  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread executor_thread([&executor]() { executor.spin(); });

  using moveit::planning_interface::MoveGroupInterface;
  MoveGroupInterface move_group_interface(node, "ur_manipulator");

  // Allow a short time for MoveIt / planning scene to come up.
  RCLCPP_INFO(logger, "Waiting for MoveIt to be ready...");
  rclcpp::sleep_for(std::chrono::seconds(2));

  geometry_msgs::msg::Pose target_pose;
  target_pose.orientation.w = 1.0;
  target_pose.position.x = 0.28;
  target_pose.position.y = -0.2;
  target_pose.position.z = 0.5;

  move_group_interface.setPoseTarget(target_pose);

  MoveGroupInterface::Plan plan;
  bool const success = static_cast<bool>(move_group_interface.plan(plan));

  if (success) {
    RCLCPP_INFO(logger, "Planning succeeded, executing trajectory...");
    auto const exec_result = move_group_interface.execute(plan);
    if (exec_result == moveit::core::MoveItErrorCode::SUCCESS) {
      RCLCPP_INFO(logger, "Execution finished successfully.");
    } else {
      RCLCPP_WARN(logger, "Execution finished with error code: %d", exec_result.val);
    }
  } else {
    RCLCPP_ERROR(logger, "Planning failed.");
  }

  rclcpp::shutdown();
  executor.cancel();
  if (executor_thread.joinable()) {
    executor_thread.join();
  }

  return 0;
}