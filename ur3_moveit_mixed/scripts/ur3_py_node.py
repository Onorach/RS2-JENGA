#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from moveit.planning import MoveItPy
from geometry_msgs.msg import Pose

def main(args=None):
    rclpy.init(args=args)
    
    # Initialize node
    node = Node("ur3_py_node")
    node.get_logger().info("Starting UR3 Python MoveIt Node...")

    # Instantiate MoveItPy
    # This requires proper parameters loaded via a launch file!
    ur3_moveit = MoveItPy(node_name="ur3_py_node")
    ur_manipulator = ur3_moveit.get_planning_component("ur_manipulator")

    # Set target pose
    target_pose = Pose()
    target_pose.orientation.w = 1.0
    target_pose.position.x = 0.28
    target_pose.position.y = -0.2
    target_pose.position.z = 0.5

    ur_manipulator.set_goal_state(pose_stamped_msg=target_pose, pose_link="tool0")

    # Plan
    node.get_logger().info("Planning trajectory...")
    plan_result = ur_manipulator.plan()

    if plan_result:
        node.get_logger().info("Plan found! Executing...")
        ur3_moveit.execute(plan_result.trajectory, controllers=[])
    else:
        node.get_logger().error("Planning failed.")

    rclpy.shutdown()

if __name__ == '__main__':
    main()