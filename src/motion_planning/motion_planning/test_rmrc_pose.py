# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""RMRC test: draw XY rectangle above tower, then return home joints."""

import sys
import time
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import PoseStamped
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

HOME_DEG = [0.0, -90.0, 0.0, -90.0, 0.0, 0.0]


def main(args=None):
    rclpy.init(args=args)
    node = Node("test_rmrc_pose")
    goal_frame = node.declare_parameter("goal_frame", "world").value
    margin_xy = float(node.declare_parameter("rectangle_margin_xy", 0.03).value)
    z_clearance = float(node.declare_parameter("z_clearance_above_tower", 0.05).value)
    pub = node.create_publisher(PoseStamped, "goal_pose", 10)
    joint_ac = ActionClient(
        node,
        FollowJointTrajectory,
        "/joint_trajectory_controller/follow_joint_trajectory",
    )
    time.sleep(1.0)

    # Tower in WORLD frame from ur3e_workspace.world.
    tower_cx, tower_cy = 0.35, 0.0
    tower_half_x, tower_half_y = 0.075 / 2.0, 0.075 / 2.0
    tower_top_z = 1.2045 + 0.015 / 2.0  # highest block center + half height
    z = tower_top_z + z_clearance

    x_min = tower_cx - tower_half_x - margin_xy
    x_max = tower_cx + tower_half_x + margin_xy
    y_min = tower_cy - tower_half_y - margin_xy
    y_max = tower_cy + tower_half_y + margin_xy

    poses = [
        (x_min, y_min, z, 0.0, 0.0, 0.0, 1.0),
        (x_max, y_min, z, 0.0, 0.0, 0.0, 1.0),
        (x_max, y_max, z, 0.0, 0.0, 0.0, 1.0),
        (x_min, y_max, z, 0.0, 0.0, 0.0, 1.0),
        (x_min, y_min, z, 0.0, 0.0, 0.0, 1.0),
    ]

    node.get_logger().info(
        f"Publishing {len(poses)} rectangle corner poses in frame '{goal_frame}' "
        f"(z={z:.3f}, margin_xy={margin_xy:.3f}) to /goal_pose."
    )

    for i, (x, y, z, qx, qy, qz, qw) in enumerate(poses):
        msg = PoseStamped()
        msg.header.frame_id = str(goal_frame)
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.position.z = float(z)
        msg.pose.orientation.x = float(qx)
        msg.pose.orientation.y = float(qy)
        msg.pose.orientation.z = float(qz)
        msg.pose.orientation.w = float(qw)
        pub.publish(msg)
        node.get_logger().info(
            f"Published corner {i + 1}/{len(poses)}: xyz=({x:.3f}, {y:.3f}, {z:.3f})"
        )
        time.sleep(8.0)

    node.get_logger().info("Rectangle complete. Returning to home joint pose.")
    if not joint_ac.wait_for_server(timeout_sec=5.0):
        node.get_logger().error(
            "joint_trajectory_controller action server unavailable; cannot return home."
        )
    else:
        home_rad = [math.radians(v) for v in HOME_DEG]
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = JointTrajectory(
            joint_names=UR3E_JOINT_NAMES,
            points=[
                JointTrajectoryPoint(
                    positions=home_rad,
                    time_from_start=Duration(sec=6, nanosec=0),
                )
            ],
        )
        send_future = joint_ac.send_goal_async(goal)
        rclpy.spin_until_future_complete(node, send_future, timeout_sec=8.0)
        goal_handle = send_future.result()
        if not goal_handle or not goal_handle.accepted:
            node.get_logger().error("Home joint goal was rejected.")
        else:
            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(node, result_future, timeout_sec=10.0)
            wrapped = result_future.result()
            if wrapped is None:
                node.get_logger().error("Timed out waiting for home joint result.")
            elif wrapped.result.error_code == 0:
                node.get_logger().info("Returned to home joint pose successfully.")
            else:
                node.get_logger().warn(
                    f"Home joint motion finished with code {wrapped.result.error_code}: "
                    f"{wrapped.result.error_string}"
                )

    node.get_logger().info("Done.")
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
