#!/usr/bin/env python3
"""
Demo node: sends a short joint trajectory to the UR3e.
Works with both Gazebo simulation and real hardware (same action interface).
"""

import rclpy
from rclpy.node import Node

from ur3e_controller.move_client import (
    UR3eMoveClient,
    build_trajectory,
    UR3E_JOINT_NAMES,
    DEFAULT_ACTION_NAME,
)


def main(args=None):
    rclpy.init(args=args)
    node = UR3eMoveClient(
        action_name=DEFAULT_ACTION_NAME,
        joint_names=list(UR3E_JOINT_NAMES),
        wait_for_server_timeout=30.0,
        node_name="ur3e_demo",
    )

    try:
        node.wait_for_server()
    except RuntimeError as e:
        node.get_logger().error(str(e))
        node.destroy_node()
        rclpy.shutdown()
        return 1

    # Example waypoints (radians): small motion so safe in sim and on hardware.
    # UR3e home-like pose then a slight offset.
    waypoints = [
        (0.0, [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]),   # t=0s
        (3.0, [0.2, -1.4, 0.2, -1.4, 0.0, 0.2]),    # t=3s
        (6.0, [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]),   # back
    ]
    trajectory = build_trajectory(UR3E_JOINT_NAMES, waypoints, time_from_start_sec=None)

    node.get_logger().info("Sending demo trajectory (3 waypoints, ~6s).")
    result = node.send_trajectory(trajectory)
    if result is not None and result.error_code == 0:
        node.get_logger().info("Demo finished successfully.")
    else:
        node.get_logger().warn("Demo finished with errors.")

    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    exit(main())
