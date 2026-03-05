#!/usr/bin/env python3

"""
Simple Python demo node that sends a FollowJointTrajectory goal to the UR3e
fake controller. This does not depend on the Python MoveIt2 bindings so it
works in a plain Humble + MoveIt2 installation.
"""

from typing import List

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


class UR3PyDemo(Node):
    def __init__(self) -> None:
        super().__init__("ur3_py_node")

        self._joint_names: List[str] = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        # This should match the fake controller name in fake_controllers.yaml.
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            "/fake_arm_controller/follow_joint_trajectory",
        )

        self.get_logger().info("Waiting for fake_arm_controller action server...")
        self._action_client.wait_for_server()
        self.get_logger().info("Connected to fake_arm_controller.")

        self.send_demo_goal()

    def send_demo_goal(self) -> None:
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = self._joint_names

        point = JointTrajectoryPoint()
        point.positions = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]
        point.time_from_start.sec = 5

        goal_msg.trajectory.points.append(point)

        self.get_logger().info("Sending demo joint-space goal to fake controller...")
        send_future = self._action_client.send_goal_async(goal_msg)
        send_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rejected by fake_arm_controller.")
            rclpy.shutdown()
            return

        self.get_logger().info("Goal accepted, waiting for result...")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future) -> None:
        result = future.result().result
        self.get_logger().info(f"FollowJointTrajectory finished with error_code={result.error_code}")
        rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = UR3PyDemo()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
