# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Test script: publishes pose goals to /goal_pose for RMRC testing.
Run after launching sim + motion_planning with use_rmrc:=true.
"""

import sys
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped


def main(args=None):
    rclpy.init(args=args)
    node = Node("test_rmrc_pose")
    pub = node.create_publisher(PoseStamped, "goal_pose", 10)
    time.sleep(1.0)

    poses = [
        (0.25, 0.0, 0.35, 0, 0, 0, 1),
        (0.2, 0.1, 0.3, 0, 0, 0, 1),
        (0.25, 0.0, 0.35, 0, 0, 0, 1),
    ]

    node.get_logger().info(
        f"Publishing {len(poses)} test poses to /goal_pose. "
        "Ensure RMRC node and sim are running."
    )

    for i, (x, y, z, qx, qy, qz, qw) in enumerate(poses):
        msg = PoseStamped()
        msg.header.frame_id = "base_link"
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.position.z = float(z)
        msg.pose.orientation.x = float(qx)
        msg.pose.orientation.y = float(qy)
        msg.pose.orientation.z = float(qz)
        msg.pose.orientation.w = float(qw)
        pub.publish(msg)
        node.get_logger().info(f"Published pose {i + 1}/{len(poses)}: xyz=({x}, {y}, {z})")
        time.sleep(8.0)

    node.get_logger().info("Done.")
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
