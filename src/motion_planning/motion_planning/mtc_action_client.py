"""
Thin JengaPickPlace action client. Waits for the mtc_pick_place action server, sends one
pick/place goal (default poses), and prints the result. Use for smoke tests; prefer
:mod:`test_mtc_pick_place` for scripted tests.
"""

from __future__ import annotations

import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseStamped

from jenga_interfaces.action import JengaPickPlace


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("mtc_action_client")
    action_name = str(node.declare_parameter("action_name", "jenga_pick_place").value)
    client = ActionClient(node, JengaPickPlace, action_name)
    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error(f"Action server '{action_name}' not available.")
        rclpy.shutdown()
        return 1

    goal = JengaPickPlace.Goal()
    goal.block_index = 0
    goal.pick_pose, goal.place_pose = _default_goal_poses(node)
    node.get_logger().info(f"Sending JengaPickPlace goal to '{action_name}'...")
    send_fut = client.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, send_fut, timeout_sec=5.0)
    gh = send_fut.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Goal rejected.")
        rclpy.shutdown()
        return 2

    res_fut = gh.get_result_async()
    rclpy.spin_until_future_complete(node, res_fut, timeout_sec=300.0)
    wrapped = res_fut.result()
    if wrapped is None:
        node.get_logger().error("No result wrapper.")
        rclpy.shutdown()
        return 3
    jenga = wrapped.result
    if jenga.success:
        node.get_logger().info(f"Success: {jenga.message}")
        rclpy.shutdown()
        return 0
    node.get_logger().error(f"Failed: {jenga.message} (error_code {jenga.error_code})")
    rclpy.shutdown()
    return 4


def _default_goal_poses(node: Node) -> tuple[PoseStamped, PoseStamped]:
    from geometry_msgs.msg import Point, Quaternion

    frame = "world"
    t = node.get_clock().now().to_msg()
    pick = PoseStamped()
    pick.header.frame_id = frame
    pick.header.stamp = t
    pick.pose = Pose(
        position=Point(x=0.30, y=-0.20, z=0.10),
        orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
    )
    place = PoseStamped()
    place.header.frame_id = frame
    place.header.stamp = t
    place.pose = Pose(
        position=Point(x=0.40, y=0.10, z=0.12),
        orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
    )
    return pick, place


if __name__ == "__main__":
    sys.exit(main())
