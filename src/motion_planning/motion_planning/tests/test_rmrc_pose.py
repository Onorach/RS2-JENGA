"""RMRC test: optional joint-space home, rectangle pose goals above tower, then joint home."""

import json
import sys
import time
import math

import numpy as np
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
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


def _move_joint_home(
    node: Node,
    joint_ac: ActionClient,
    duration_sec: int,
    log_label: str,
) -> bool:
    """
    Send FollowJointTrajectory to HOME_DEG via joint_trajectory_controller.
    Returns True if the goal completed with error_code == 0.
    """
    if not joint_ac.wait_for_server(timeout_sec=5.0):
        node.get_logger().error(
            f"{log_label}: joint_trajectory_controller action server unavailable."
        )
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
        node.get_logger().error(f"{log_label}: joint goal was rejected.")
        return False
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future, timeout_sec=float(duration_sec) + 5.0)
    wrapped = result_future.result()
    if wrapped is None:
        node.get_logger().error(f"{log_label}: timed out waiting for result.")
        return False
    if wrapped.result.error_code != 0:
        node.get_logger().warn(
            f"{log_label}: finished with code {wrapped.result.error_code}: "
            f"{wrapped.result.error_string}"
        )
        return False
    node.get_logger().info(f"{log_label}: completed successfully.")
    return True


def _quat_mul_xyzw(qa: np.ndarray, qb: np.ndarray) -> np.ndarray:
    """Hamilton product; quaternions as [x, y, z, w]."""
    ax, ay, az, aw = qa
    bx, by, bz, bw = qb
    x = aw * bx + ax * bw + ay * bz - az * by
    y = aw * by - ax * bz + ay * bw + az * bx
    z = aw * bz + ax * by - ay * bx + az * bw
    w = aw * bw - ax * bx - ay * by - az * bz
    return np.array([x, y, z, w], dtype=np.float64)


def quat_tool_down_face_point(
    px: float, py: float, look_at_x: float, look_at_y: float
) -> tuple[float, float, float, float]:
    """
    Orientation in base/world frame: tool0 Z along -Z (point down), with a yaw so
    the tool X axis nominally faces (look_at_x, look_at_y) in the XY plane.
    Uses R = R_z(yaw) @ R_x(pi) with geometry_msgs order (x,y,z,w).
    """
    yaw = math.atan2(look_at_y - py, look_at_x - px)
    cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
    qz = np.array([0.0, 0.0, sy, cy], dtype=np.float64)
    qx = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)  # 180 deg about X
    q = _quat_mul_xyzw(qz, qx)
    n = float(np.linalg.norm(q))
    if n < 1e-12:
        return 0.0, 0.0, 0.0, 1.0
    q = q / n
    return float(q[0]), float(q[1]), float(q[2]), float(q[3])


def main(args=None):
    rclpy.init(args=args)
    node = Node("test_rmrc_pose")
    execution_mode = str(node.declare_parameter("execution_mode", "trajectory").value).lower()
    goal_frame = node.declare_parameter("goal_frame", "world").value
    margin_xy = float(node.declare_parameter("rectangle_margin_xy", 0.05).value)
    z_clearance = float(node.declare_parameter("z_clearance_above_tower", 0.05).value)
    wait_for_goal_completion = bool(
        node.declare_parameter("wait_for_goal_completion", True).value
    )
    goal_completion_timeout_sec = float(
        node.declare_parameter("goal_completion_timeout_sec", 120.0).value
    )
    sleep_between_poses_sec = float(
        node.declare_parameter("sleep_between_poses_sec", 8.0).value
    )
    status_topic = str(node.declare_parameter("status_topic", "rmrc_status").value)
    start_with_home_joints = bool(
        node.declare_parameter("start_with_home_joints", True).value
    )
    end_with_home_joints = bool(
        node.declare_parameter("end_with_home_joints", True).value
    )
    joint_home_duration_sec = int(
        node.declare_parameter("joint_home_duration_sec", 6).value
    )
    latest_status = {"executions_completed": 0}

    def _on_rmrc_status(msg: String) -> None:
        try:
            d = json.loads(msg.data)
            latest_status["executions_completed"] = int(d.get("executions_completed", 0))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    if wait_for_goal_completion:
        node.create_subscription(String, status_topic, _on_rmrc_status, 10)

    pub = node.create_publisher(PoseStamped, "goal_pose", 10)
    joint_ac = ActionClient(
        node,
        FollowJointTrajectory,
        "/joint_trajectory_controller/follow_joint_trajectory",
    )
    # Allow rmrc_planning_node (robot_description, TF) to come up before first goal.
    time.sleep(1.0)

    if start_with_home_joints:
        node.get_logger().info(
            "Moving to HOME_DEG via joint_trajectory_controller (before RMRC rectangle)."
        )
        _move_joint_home(
            node,
            joint_ac,
            joint_home_duration_sec,
            "Start joint home",
        )

    # Tower in WORLD frame from ur3e_workspace.world.
    tower_cx, tower_cy = 0.35, 0.0
    tower_half_x, tower_half_y = 0.075 / 2.0, 0.075 / 2.0
    tower_top_z = 1.08 + (8 * 0.015) + 0.02 # highest block center + half height + half height of the tower
    z = tower_top_z + z_clearance

    x_min = tower_cx - tower_half_x - margin_xy
    x_max = tower_cx + tower_half_x + margin_xy
    y_min = tower_cy - tower_half_y - margin_xy
    y_max = tower_cy + tower_half_y + margin_xy

    # Point tool down (-base Z) and yaw toward tower centre for a natural approach.
    corners = [
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max),
        (x_min, y_min),
    ]
    poses = []
    for x, y in corners:
        qx, qy, qz, qw = quat_tool_down_face_point(x, y, tower_cx, tower_cy)
        poses.append((x, y, z, qx, qy, qz, qw))

    node.get_logger().info(
        f"Rectangle: {len(poses)} corners in '{goal_frame}' "
        f"(z={z:.3f}, margin_xy={margin_xy:.3f}, tool-down + yaw toward tower)."
    )
    if wait_for_goal_completion:
        node.get_logger().info(
            "wait_for_goal_completion=true — advancing after each pose when rmrc_status "
            "reports executions_completed (see rmrc_planning_node)."
        )
    else:
        node.get_logger().info(
            f"wait_for_goal_completion=false — using sleep_between_poses_sec={sleep_between_poses_sec:.1f} "
            "(poses may overwrite buffered goals if faster than execution)."
        )

    if wait_for_goal_completion:
        t0 = time.monotonic()
        while time.monotonic() - t0 < 2.0 and rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)

    node.get_logger().info(
        f"Publishing {len(poses)} pose goals to /goal_pose (frame '{goal_frame}')."
    )

    for i, (x, y, z, qx, qy, qz, qw) in enumerate(poses):
        baseline = latest_status["executions_completed"] if wait_for_goal_completion else 0
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
        if wait_for_goal_completion:
            deadline = time.monotonic() + goal_completion_timeout_sec
            ok = False
            while time.monotonic() < deadline and rclpy.ok():
                rclpy.spin_once(node, timeout_sec=0.05)
                if latest_status["executions_completed"] > baseline:
                    ok = True
                    break
            if not ok:
                node.get_logger().error(
                    f"Timed out waiting for RMRC completion (executions_completed > {baseline}). "
                    f"Is rmrc_planning_node running and publishing '{status_topic}'?"
                )
                break
        else:
            time.sleep(sleep_between_poses_sec)

    if execution_mode == "velocity":
        node.get_logger().info(
            "Rectangle complete. Skipping end joint home in velocity mode "
            "(set execution_mode:=trajectory for joint home at end)."
        )
        node.get_logger().info("Done.")
        node.destroy_node()
        rclpy.shutdown()
        return 0

    if end_with_home_joints:
        node.get_logger().info("Rectangle complete. Returning to home joint pose.")
        _move_joint_home(
            node,
            joint_ac,
            joint_home_duration_sec,
            "End joint home",
        )
    else:
        node.get_logger().info("Rectangle complete (end_with_home_joints=false).")

    node.get_logger().info("Done.")
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
