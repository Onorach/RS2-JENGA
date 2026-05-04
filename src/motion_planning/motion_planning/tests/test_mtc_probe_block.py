"""
Send a JengaProbeBlock action to mtc_probe_block_server.
"""

from __future__ import annotations

import sys

import rclpy
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion
from rclpy.action import ActionClient
from rclpy.node import Node

from jenga_interfaces.action import JengaProbeBlock


def _on_feedback(fb) -> None:  # noqa: ANN001
    try:
        f = fb.feedback
        print(f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%")
    except (AttributeError, TypeError):
        pass


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("test_mtc_probe_block")
    action_name = str(node.declare_parameter("action_name", "jenga_probe_block").value)
    goal_frame = str(node.declare_parameter("goal_frame", "world").value)

    client = ActionClient(node, JengaProbeBlock, action_name)
    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 1

    t = node.get_clock().now().to_msg()
    block = PoseStamped()
    block.header.frame_id = goal_frame
    block.header.stamp = t
    block.pose = Pose(
        position=Point(x=0.0, y=0.30, z=0.03),
        orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
    )

    goal = JengaProbeBlock.Goal()
    goal.block_index = 0
    goal.block_pose = block

    node.get_logger().info("Sending MTC probe action...")
    send_fut = client.send_goal_async(goal, feedback_callback=_on_feedback)
    rclpy.spin_until_future_complete(node, send_fut, timeout_sec=10.0)
    gh = send_fut.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Goal rejected")
        rclpy.shutdown()
        return 2
    res_fut = gh.get_result_async()
    rclpy.spin_until_future_complete(node, res_fut, timeout_sec=600.0)
    wrapped = res_fut.result()
    if wrapped is None:
        rclpy.shutdown()
        return 3
    jr = wrapped.result
    if jr.success:
        node.get_logger().info(f"Result OK: {jr.message} score={jr.score:.3f}")
        rclpy.shutdown()
        return 0
    node.get_logger().error(f"Result FAIL: {jr.message} (code {jr.error_code}) score={jr.score:.3f}")
    rclpy.shutdown()
    return 4


if __name__ == "__main__":
    sys.exit(main())

