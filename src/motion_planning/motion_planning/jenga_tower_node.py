
"""
Jenga tower sequencer: publishes Cartesian goals to /goal_pose in order.

Use with rmrc_planning_node, pose_goal_node, or moveit_cartesian_node (already running).
Waits on planner status JSON (executions_completed) between steps, same contract as test_rmrc_pose.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String

from motion_planning.jenga_tower_layout import (
    build_pose_stamped,
    iter_tower_motion_steps,
    load_tower_layout,
)

_RE_BLOCK_PICK = re.compile(r"^L\d+_B\d+_pick$")
_RE_BLOCK_PLACE = re.compile(r"^L\d+_B\d+_place$")


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("jenga_tower_node")

    single_layer = bool(node.declare_parameter("single_layer", False).value)
    total_layers = 1 if single_layer else int(node.declare_parameter("total_layers", 6).value)
    total_layers = max(1, min(total_layers, 6))

    default_yaml = os.path.join(
        get_package_share_directory("motion_planning"),
        "config",
        "jenga_tower_layout.yaml",
    )
    layout_path = str(node.declare_parameter("tower_layout_file", default_yaml).value)
    status_topic = str(node.declare_parameter("status_topic", "rmrc_status").value)
    goal_topic = str(node.declare_parameter("goal_pose_topic", "goal_pose").value)
    goal_completion_timeout_sec = float(
        node.declare_parameter("goal_completion_timeout_sec", 180.0).value
    )
    start_delay_sec = float(node.declare_parameter("start_delay_sec", 2.0).value)
    pause_after_pick_sec = float(node.declare_parameter("pause_after_pick_sec", 0.0).value)
    pause_after_place_sec = float(node.declare_parameter("pause_after_place_sec", 0.0).value)

    try:
        layout = load_tower_layout(layout_path)
    except Exception as exc:
        node.get_logger().error(f"Failed to load tower layout '{layout_path}': {exc}")
        node.destroy_node()
        rclpy.shutdown()
        return 1

    latest_status: dict[str, int | bool | str] = {
        "executions_completed": 0,
        "busy": False,
        "state": "unknown",
    }

    def _on_status(msg: String) -> None:
        try:
            d = json.loads(msg.data)
            latest_status["executions_completed"] = int(d.get("executions_completed", 0))
            latest_status["busy"] = bool(d.get("busy", False))
            latest_status["state"] = str(d.get("state", ""))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    node.create_subscription(String, status_topic, _on_status, 10)
    pub = node.create_publisher(PoseStamped, goal_topic, 10)

    steps = iter_tower_motion_steps(layout, total_layers)
    mode = "single layer (1 of 6)" if single_layer else f"full tower ({total_layers} layers)"
    node.get_logger().info(
        f"Jenga tower sequence: {mode}, {len(steps)} pose steps, layout='{layout_path}', "
        f"status='{status_topic}', goals on '{goal_topic}'."
    )

    t_wait = time.monotonic() + max(start_delay_sec, 0.0)
    while time.monotonic() < t_wait and rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)

    for name, pose in steps:
        baseline = int(latest_status["executions_completed"])
        msg = build_pose_stamped(layout, pose)
        msg.header.stamp = node.get_clock().now().to_msg()
        pub.publish(msg)
        node.get_logger().info(
            f"Published '{name}' at xyz=({pose.position.x:.4f}, {pose.position.y:.4f}, {pose.position.z:.4f})"
        )

        if _RE_BLOCK_PICK.match(name) and pause_after_pick_sec > 0.0:
            node.get_logger().info(
                f"pause_after_pick_sec={pause_after_pick_sec:.2f} — operate gripper if needed."
            )
            deadline_spin = time.monotonic() + pause_after_pick_sec
            while time.monotonic() < deadline_spin and rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.05)

        if _RE_BLOCK_PLACE.match(name) and pause_after_place_sec > 0.0:
            node.get_logger().info(
                f"pause_after_place_sec={pause_after_place_sec:.2f} — operate gripper if needed."
            )
            deadline_spin = time.monotonic() + pause_after_place_sec
            while time.monotonic() < deadline_spin and rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.05)

        deadline = time.monotonic() + goal_completion_timeout_sec
        ok = False
        while time.monotonic() < deadline and rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            if int(latest_status["executions_completed"]) > baseline:
                ok = True
                break
        if not ok:
            node.get_logger().error(
                f"Timed out waiting for planner completion after '{name}' "
                f"(executions_completed stayed at {baseline}). "
                f"Is the planner running and publishing JSON on '{status_topic}'?"
            )
            node.destroy_node()
            rclpy.shutdown()
            return 2

    node.get_logger().info("Jenga tower sequence finished successfully.")
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
