
"""
Send a JengaPickPlace action to mtc_pick_place_server (one pick + one place, full MTC pipeline).

Prerequisites: MoveIt and ``ros2 run mtc_jenga_servers mtc_pick_place_server`` (or the launch file).
Optionally: joint home before/after like :mod:`test_planner_pose`.
"""

from __future__ import annotations

import math
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from jenga_interfaces.action import JengaPickPlace

UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]
HOME_DEG = [0.0, -90.0, 0.0, -90.0, 0.0, 0.0]


def _move_joint_home(
    node: Node,
    joint_ac: ActionClient,
    duration_sec: int,
) -> bool:
    if not joint_ac.wait_for_server(timeout_sec=5.0):
        return False
    home_rad = [math.radians(v) for v in HOME_DEG]
    goal = FollowJointTrajectory.Goal()
    goal.trajectory = JointTrajectory(
        joint_names=UR3E_JOINT_NAMES,
        points=[
            JointTrajectoryPoint(
                positions=home_rad,
                time_from_start=Duration(sec=int(duration_sec), nanosec=0),
            )
        ],
    )
    send_future = joint_ac.send_goal_async(goal)
    rclpy.spin_until_future_complete(node, send_future, timeout_sec=8.0)
    goal_handle = send_future.result()
    if not goal_handle or not goal_handle.accepted:
        return False
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future, timeout_sec=float(duration_sec) + 5.0)
    wrapped = result_future.result()
    if wrapped is None:
        return False
    r = wrapped.result
    if r.error_code != 0:  # FollowJointTrajectory
        return False
    return True


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("test_mtc_pick_place")
    action_name = str(node.declare_parameter("action_name", "jenga_pick_place").value)
    goal_frame = str(node.declare_parameter("goal_frame", "world").value)
    start_with_home_joints = bool(node.declare_parameter("start_with_home_joints", True).value)
    end_with_home_joints = bool(node.declare_parameter("end_with_home_joints", True).value)
    joint_home_duration_sec = int(node.declare_parameter("joint_home_duration_sec", 6).value)
    jta = str(
        node.declare_parameter(
            "joint_trajectory_action",
            "/joint_trajectory_controller/follow_joint_trajectory",
        ).value
    )
    joint_ac = ActionClient(node, FollowJointTrajectory, jta)
    if start_with_home_joints:
        node.get_logger().info("Joint home (start)...")
        _move_joint_home(node, joint_ac, joint_home_duration_sec)

    client = ActionClient(node, JengaPickPlace, action_name)
    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 1

    t = node.get_clock().now().to_msg()
    pick = PoseStamped()
    pick.header.frame_id = goal_frame
    pick.header.stamp = t
    pick.pose = Pose(
        position=Point(x=0.20, y=0.30, z=0.02),
        orientation=Quaternion(x=0.0, y=0.0, z=0.707, w=0.707),
    )
    place = PoseStamped()
    place.header.frame_id = goal_frame
    place.header.stamp = t
    place.pose = Pose(
        position=Point(x=-0.20, y=0.30, z=0.02),
        orientation=Quaternion(x=0.0, y=0.0, z=0.707, w=0.707),
    )

    goal = JengaPickPlace.Goal()
    goal.block_index = 0
    goal.pick_pose = pick
    goal.place_pose = place

    node.get_logger().info("Sending MTC pick+place action...")
    send_fut = client.send_goal_async(goal, feedback_callback=_on_feedback)
    rclpy.spin_until_future_complete(node, send_fut, timeout_sec=10.0)
    gh = send_fut.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Goal rejected")
        rclpy.shutdown()
        return 2
    res_fut = gh.get_result_async()
    rclpy.spin_until_future_complete(node, res_fut, timeout_sec=300.0)
    wrapped = res_fut.result()
    if wrapped is None:
        rclpy.shutdown()
        return 3
    jr = wrapped.result
    if jr.success:
        node.get_logger().info(f"MTC result OK: {jr.message}")
    else:
        node.get_logger().error(f"MTC result FAIL: {jr.message} (code {jr.error_code})")
        rclpy.shutdown()
        return 4

    if end_with_home_joints:
        node.get_logger().info("Joint home (end)...")
        _move_joint_home(node, joint_ac, joint_home_duration_sec)
    rclpy.shutdown()
    return 0


def _on_feedback(fb) -> None:  # noqa: ANN001
    try:
        f = fb.feedback
        print(f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%")
    except (AttributeError, TypeError):
        pass


if __name__ == "__main__":
    sys.exit(main())
