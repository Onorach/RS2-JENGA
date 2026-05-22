
"""
Send a JengaPickPlace action to mtc_pick_place_server (one pick + one place, full MTC pipeline).

1) Call set_jenga_blocks_layout: blocks below block_index at tower, block_index and above at stock
2) Load pick/place poses for block_index from layout YAML
3) Send JengaPickPlace for block_index

Prerequisites: MoveIt, ``jenga_blocks_scene`` (set_jenga_blocks_layout), and
``ros2 run mtc_jenga_servers mtc_pick_place_server`` (or the launch file).
Optionally: joint home before/after like :mod:`test_planner_pose`.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import rclpy
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import Pose, PoseStamped
from rclpy.action import ActionClient
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from jenga_interfaces.action import JengaPickPlace
from jenga_interfaces.srv import SetJengaBlocksLayout
from motion_planning.jenga_tower_mtc_sequencer import (
    _explicit_steps,
    _load_yaml,
    _parametric_steps,
)

UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]
HOME_DEG = [0.0, -90.0, 0.0, -90.0, 0.0, 0.0]


def _resolve_layout_path(layout_path_param: str) -> str:
    if layout_path_param:
        return layout_path_param
    from ament_index_python.packages import get_package_share_directory

    return str(
        Path(get_package_share_directory("motion_planning"))
        / "config"
        / "jenga_tower_mtc_layout.yaml"
    )


def _load_pick_place_pairs(layout_path: str) -> list[tuple[Pose, Pose]]:
    data = _load_yaml(layout_path)
    mode = str(data.get("layout", "parametric"))
    if mode == "parametric":
        return _parametric_steps(data)
    if mode in ("from_file", "explicit", "steps"):
        return _explicit_steps(data)
    raise ValueError(f"Unknown layout mode: {mode}")


def _call_set_layout(
    node: Node,
    target_layout: str,
    *,
    block_indices: list[int] | None = None,
    srv_name: str = "set_jenga_blocks_layout",
    timeout_sec: float = 10.0,
) -> bool:
    cli = node.create_client(SetJengaBlocksLayout, srv_name)
    if not cli.wait_for_service(timeout_sec=timeout_sec):
        node.get_logger().error(f"Service not available: {srv_name}")
        return False
    req = SetJengaBlocksLayout.Request()
    req.block_indices = [int(i) for i in block_indices] if block_indices else []
    req.target_layout = target_layout
    fut = cli.call_async(req)
    rclpy.spin_until_future_complete(node, fut, timeout_sec=timeout_sec)
    resp = fut.result()
    if not resp or not resp.success:
        node.get_logger().error(
            f"{srv_name} ({target_layout}) failed: {getattr(resp, 'message', '<no message>')}"
        )
        return False
    indices_msg = f" indices={req.block_indices}" if req.block_indices else ""
    node.get_logger().info(f"{srv_name} ({target_layout}){indices_msg}: {resp.message}")
    return True


def _setup_scene_for_pick_place(
    node: Node,
    block_index: int,
    *,
    srv_name: str,
    timeout_sec: float,
) -> bool:
    """Blocks 0..index-1 in tower; block_index and above in stock."""
    if not _call_set_layout(
        node, "stock", block_indices=[], srv_name=srv_name, timeout_sec=timeout_sec
    ):
        return False
    if block_index > 0:
        below = list(range(0, block_index))
        if not _call_set_layout(
            node, "tower", block_indices=below, srv_name=srv_name, timeout_sec=timeout_sec
        ):
            return False
    return True


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


def _on_feedback(fb) -> None:  # noqa: ANN001
    try:
        f = fb.feedback
        print(f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%")
    except (AttributeError, TypeError):
        pass


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("test_mtc_pick_place")

    action_name = str(node.declare_parameter("action_name", "jenga_pick_place").value)
    goal_frame = str(node.declare_parameter("goal_frame", "world").value)
    block_index = int(node.declare_parameter("block_index", 0).value)
    layout_path_param = str(node.declare_parameter("layout_path", "").value)
    set_layout_service = str(
        node.declare_parameter("set_layout_service", "set_jenga_blocks_layout").value
    )
    layout_service_timeout_sec = float(
        node.declare_parameter("layout_service_timeout_sec", 10.0).value
    )
    start_with_home_joints = bool(node.declare_parameter("start_with_home_joints", True).value)
    end_with_home_joints = bool(node.declare_parameter("end_with_home_joints", True).value)
    joint_home_duration_sec = int(node.declare_parameter("joint_home_duration_sec", 6).value)
    jta = str(
        node.declare_parameter(
            "joint_trajectory_action",
            "/joint_trajectory_controller/follow_joint_trajectory",
        ).value
    )

    try:
        layout_path = _resolve_layout_path(layout_path_param)
        pairs = _load_pick_place_pairs(layout_path)
    except (FileNotFoundError, ValueError) as exc:
        node.get_logger().error(str(exc))
        rclpy.shutdown()
        return 1

    n_pairs = len(pairs)
    if block_index < 0 or block_index >= n_pairs:
        node.get_logger().error(
            f"Invalid block_index={block_index} for {n_pairs} block(s); "
            f"allowed range is 0 .. {n_pairs - 1}."
        )
        rclpy.shutdown()
        return 9

    joint_ac = ActionClient(node, FollowJointTrajectory, jta)
    if start_with_home_joints:
        node.get_logger().info("Joint home (start)...")
        _move_joint_home(node, joint_ac, joint_home_duration_sec)

    node.get_logger().info(
        f"Setting planning scene: tower indices 0..{block_index - 1}, "
        f"stock indices {block_index}..{n_pairs - 1}"
    )
    if not _setup_scene_for_pick_place(
        node,
        block_index,
        srv_name=set_layout_service,
        timeout_sec=layout_service_timeout_sec,
    ):
        rclpy.shutdown()
        return 10

    client = ActionClient(node, JengaPickPlace, action_name)
    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 1

    pick_pose, place_pose = pairs[block_index]
    stamp = node.get_clock().now().to_msg()
    pick = PoseStamped()
    pick.header.frame_id = goal_frame
    pick.header.stamp = stamp
    pick.pose = pick_pose
    place = PoseStamped()
    place.header.frame_id = goal_frame
    place.header.stamp = stamp
    place.pose = place_pose

    goal = JengaPickPlace.Goal()
    goal.block_index = int(block_index)
    goal.pick_pose = pick
    goal.place_pose = place

    node.get_logger().info(
        f"Sending MTC pick+place for block_index={block_index}: pick "
        f"{pick_pose.position.x:.3f},{pick_pose.position.y:.3f},{pick_pose.position.z:.3f} -> "
        f"place {place_pose.position.x:.3f},{place_pose.position.y:.3f},{place_pose.position.z:.3f}"
    )
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


if __name__ == "__main__":
    sys.exit(main())
