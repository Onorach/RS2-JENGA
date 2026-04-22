
"""
MoveIt Cartesian planning node: accepts geometry_msgs/PoseStamped on /goal_pose,
plans a straight-line Cartesian trajectory via the GetCartesianPath service,
then executes it through joint_trajectory_controller.

If the Cartesian path is blocked by a collision object (fraction < 1.0), the
node automatically falls back to OMPL joint-space planning via the MoveGroup
action.  OMPL paths are collision-free but not necessarily straight lines.

Architecture
------------
Everything lives in a single ROS2 node.  All planning and execution
are done with async callbacks — no blocking waits inside any callback.
This is the only pattern that works correctly inside a MultiThreadedExecutor.

Flow
----
/goal_pose (sub)
  → _on_goal()
      → _do_cartesian_plan()                ← GetCartesianPath service
          fraction >= threshold?
            YES → _do_execute(solution)
            NO  → _do_ompl_fallback()        ← MoveGroup action
                    → _on_ompl_accepted()
                        → _on_ompl_result()
                            → _do_execute(planned_trajectory)
          → _on_exec_accepted()
              → _on_exec_result()            ← done
"""

from __future__ import annotations

import json
import math
import threading
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import Pose, PoseStamped, Point, Quaternion
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import JointConstraint, PlanningOptions, RobotState
from moveit_msgs.srv import GetCartesianPath
from std_msgs.msg import Bool, String
from tf2_ros import Buffer, TransformListener

from ur3e_controller.move_client import UR3E_JOINT_NAMES
from motion_planning.moveit_planning import (
    build_cartesian_path_request,
    build_motion_plan_request,
    pose_stamped_to_goal_constraints,
    robot_trajectory_to_joint_trajectory,
    scale_trajectory_timing,
    DEFAULT_PLANNING_GROUP,
    DEFAULT_EE_LINK,
    DEFAULT_PLANNING_FRAME,
)

DEFAULT_MOVE_ACTION = "/move_action"
DEFAULT_JOINT_ACTION = "/joint_trajectory_controller/follow_joint_trajectory"
DEFAULT_CARTESIAN_SERVICE = "/compute_cartesian_path"
DEFAULT_MAX_STEP = 0.005
DEFAULT_JUMP_THRESHOLD = 5.0
DEFAULT_CARTESIAN_FRACTION_THRESHOLD = 1.0
DEFAULT_VELOCITY_SCALING = 0.1
DEFAULT_ACCELERATION_SCALING = 0.1
DEFAULT_MAX_CARTESIAN_SEGMENT = 0.08


def _slerp(q0: list[float], q1: list[float], t: float) -> Quaternion:
    """Spherical linear interpolation between two quaternions (xyzw)."""
    dot = sum(a * b for a, b in zip(q0, q1))
    if dot < 0.0:
        q1 = [-c for c in q1]
        dot = -dot
    dot = min(dot, 1.0)
    if dot > 0.9995:
        r = [a + t * (b - a) for a, b in zip(q0, q1)]
    else:
        theta = math.acos(dot)
        sin_t = math.sin(theta)
        w0 = math.sin((1.0 - t) * theta) / sin_t
        w1 = math.sin(t * theta) / sin_t
        r = [w0 * a + w1 * b for a, b in zip(q0, q1)]
    n = math.sqrt(sum(c * c for c in r))
    if n < 1e-12:
        return Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
    return Quaternion(x=r[0] / n, y=r[1] / n, z=r[2] / n, w=r[3] / n)


class MoveItCartesianNode(Node):
    """Plans to pose goals via MoveIt2 Cartesian path service, with OMPL fallback."""

    def __init__(self):
        super().__init__("moveit_cartesian_node")

        move_action = self.declare_parameter(
            "move_action_name", DEFAULT_MOVE_ACTION
        ).value
        joint_action = self.declare_parameter(
            "joint_trajectory_action", DEFAULT_JOINT_ACTION
        ).value
        cartesian_service = self.declare_parameter(
            "cartesian_service_name", DEFAULT_CARTESIAN_SERVICE
        ).value
        self._plan_only = self.declare_parameter("plan_only", False).value
        self._max_step = float(
            self.declare_parameter("max_step", DEFAULT_MAX_STEP).value
        )
        self._jump_threshold = float(
            self.declare_parameter("jump_threshold", DEFAULT_JUMP_THRESHOLD).value
        )
        self._fraction_threshold = float(
            self.declare_parameter(
                "cartesian_fraction_threshold",
                DEFAULT_CARTESIAN_FRACTION_THRESHOLD,
            ).value
        )
        self._velocity_scaling = float(
            self.declare_parameter(
                "max_velocity_scaling_factor", DEFAULT_VELOCITY_SCALING
            ).value
        )
        self._acceleration_scaling = float(
            self.declare_parameter(
                "max_acceleration_scaling_factor", DEFAULT_ACCELERATION_SCALING
            ).value
        )
        self._status_topic = str(
            self.declare_parameter("status_topic", "moveit_cartesian_status").value
        )
        self._max_segment = float(
            self.declare_parameter(
                "max_cartesian_segment", DEFAULT_MAX_CARTESIAN_SEGMENT
            ).value
        )

        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

        self._cbg = ReentrantCallbackGroup()

        self._cartesian_client = self.create_client(
            GetCartesianPath, cartesian_service, callback_group=self._cbg
        )
        self._move_ac = ActionClient(
            self, MoveGroup, move_action, callback_group=self._cbg
        )
        self._joint_ac = ActionClient(
            self, FollowJointTrajectory, joint_action, callback_group=self._cbg
        )

        self._status_pub = self.create_publisher(String, self._status_topic, 10)

        self.create_subscription(
            PoseStamped, "goal_pose", self._on_goal, 10, callback_group=self._cbg
        )

        self._busy = False
        self._busy_lock = threading.Lock()

        self._plan_goal_handle = None
        self._exec_goal_handle = None
        self._handle_lock = threading.Lock()

        self._status_lock = threading.Lock()
        self._status_phase: str = "idle"
        self._executions_completed: int = 0
        self._last_strategy: str = ""

        self._estop_active = False
        self._estop_lock = threading.Lock()
        self.create_subscription(
            Bool, "/estop_active", self._on_estop, 1, callback_group=self._cbg
        )
        self.create_subscription(
            Bool, "/estop", self._on_estop_direct, 1, callback_group=self._cbg
        )

        self._emit_status()
        self.get_logger().info(
            "MoveItCartesianNode started.  "
            "Publish geometry_msgs/PoseStamped to '/goal_pose'."
        )

    # ── Status ──────────────────────────────────────────────────────────────

    def _set_status_phase(self, phase: str) -> None:
        with self._status_lock:
            self._status_phase = phase
        self._emit_status()

    def _emit_status(self) -> None:
        with self._status_lock:
            phase = self._status_phase
            completed = self._executions_completed
            strategy = self._last_strategy
        with self._busy_lock:
            busy = self._busy
        with self._estop_lock:
            estop = self._estop_active
        payload = {
            "state": phase,
            "busy": busy,
            "executions_completed": completed,
            "estop_active": estop,
            "last_strategy": strategy,
        }
        out = String()
        out.data = json.dumps(payload, separators=(",", ":"))
        self._status_pub.publish(out)

    # ── E-stop ──────────────────────────────────────────────────────────────

    def _on_estop(self, msg: Bool) -> None:
        with self._estop_lock:
            was_active = self._estop_active
            self._estop_active = msg.data
        if msg.data and not was_active:
            self._cancel_in_flight_goals()

    def _on_estop_direct(self, msg: Bool) -> None:
        with self._estop_lock:
            was_active = self._estop_active
            self._estop_active = msg.data
        if msg.data and not was_active:
            self._cancel_in_flight_goals()

    def _cancel_in_flight_goals(self) -> None:
        self.get_logger().warn("E-stop received — cancelling in-flight goals.")
        with self._handle_lock:
            plan_handle = self._plan_goal_handle
            exec_handle = self._exec_goal_handle
            self._plan_goal_handle = None
            self._exec_goal_handle = None

        if plan_handle is not None:
            try:
                plan_handle.cancel_goal_async()
                self.get_logger().info("Planning goal cancel requested.")
            except Exception as exc:
                self.get_logger().warn(f"Could not cancel planning goal: {exc}")
        if exec_handle is not None:
            try:
                exec_handle.cancel_goal_async()
                self.get_logger().info("Execution goal cancel requested.")
            except Exception as exc:
                self.get_logger().warn(f"Could not cancel execution goal: {exc}")

        self._set_free()

    # ── Step 1: receive goal ────────────────────────────────────────────────

    def _on_goal(self, msg: PoseStamped) -> None:
        with self._estop_lock:
            if self._estop_active:
                self.get_logger().warn(
                    "E-stop is active — ignoring incoming pose goal."
                )
                return
        with self._busy_lock:
            if self._busy:
                self.get_logger().warn(
                    "Already executing a goal — ignoring incoming pose."
                )
                return
            self._busy = True

        pos = msg.pose.position
        frame = msg.header.frame_id or "(no frame)"
        self.get_logger().info(
            f"Goal pose received: xyz=({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f})  "
            f"frame='{frame}'"
        )
        self._set_status_phase("planning_cartesian")
        self._do_cartesian_plan(msg)

    # ── Step 2: Cartesian path service call ─────────────────────────────────

    def _interpolate_waypoints(
        self, goal: Pose, frame_id: str
    ) -> list[Pose]:
        """Return intermediate waypoints if the goal is far from the current EE pose.

        Looks up the current ``tool0`` position via TF.  If the Cartesian
        distance exceeds ``self._max_segment``, the segment is subdivided so
        that each sub-segment is at most ``self._max_segment`` long.  The
        orientation is linearly interpolated (slerp) between start and goal.
        Falls back to ``[goal]`` if the TF lookup fails.
        """
        try:
            tf = self._tf_buffer.lookup_transform(
                frame_id, DEFAULT_EE_LINK, rclpy.time.Time()
            )
        except Exception:
            return [goal]

        sx = tf.transform.translation.x
        sy = tf.transform.translation.y
        sz = tf.transform.translation.z
        gx, gy, gz = goal.position.x, goal.position.y, goal.position.z
        dist = math.sqrt((gx - sx) ** 2 + (gy - sy) ** 2 + (gz - sz) ** 2)

        if dist <= self._max_segment:
            return [goal]

        n_segs = math.ceil(dist / self._max_segment)
        sq = [
            tf.transform.rotation.x,
            tf.transform.rotation.y,
            tf.transform.rotation.z,
            tf.transform.rotation.w,
        ]
        gq = [
            goal.orientation.x,
            goal.orientation.y,
            goal.orientation.z,
            goal.orientation.w,
        ]

        waypoints: list[Pose] = []
        for i in range(1, n_segs + 1):
            t = i / n_segs
            p = Pose()
            p.position = Point(
                x=sx + t * (gx - sx),
                y=sy + t * (gy - sy),
                z=sz + t * (gz - sz),
            )
            p.orientation = _slerp(sq, gq, t)
            waypoints.append(p)
        return waypoints

    def _do_cartesian_plan(self, pose_stamped: PoseStamped) -> None:
        if not self._cartesian_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().warn(
                "GetCartesianPath service not available — "
                "falling back to OMPL immediately."
            )
            self._do_ompl_fallback(pose_stamped)
            return

        frame = pose_stamped.header.frame_id or DEFAULT_PLANNING_FRAME
        waypoints = self._interpolate_waypoints(pose_stamped.pose, frame)
        request = build_cartesian_path_request(
            goal_pose=pose_stamped.pose,
            max_step=self._max_step,
            jump_threshold=self._jump_threshold,
            avoid_collisions=True,
            max_velocity_scaling_factor=self._velocity_scaling,
            max_acceleration_scaling_factor=self._acceleration_scaling,
            frame_id=frame,
            waypoints=waypoints,
        )

        n_wp = len(waypoints)
        self.get_logger().info(
            f"Requesting Cartesian path ({n_wp} waypoint{'s' if n_wp != 1 else ''}, "
            f"max_step={self._max_step:.4f}, "
            f"jump_threshold={self._jump_threshold:.1f})…"
        )
        future = self._cartesian_client.call_async(request)
        future.add_done_callback(
            lambda f: self._on_cartesian_result(f, pose_stamped)
        )

    def _on_cartesian_result(self, future, pose_stamped: PoseStamped) -> None:
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f"Cartesian path service call failed: {exc}")
            self.get_logger().info("Falling back to OMPL…")
            self._do_ompl_fallback(pose_stamped)
            return

        fraction = response.fraction
        n_pts = len(response.solution.joint_trajectory.points)
        self.get_logger().info(
            f"Cartesian path result: fraction={fraction:.3f}, "
            f"waypoints={n_pts}"
        )

        if fraction >= self._fraction_threshold and n_pts > 0:
            with self._status_lock:
                self._last_strategy = "cartesian"
            self.get_logger().info(
                "Full Cartesian path found — executing straight-line trajectory."
            )
            scaled = scale_trajectory_timing(
                response.solution,
                velocity_scaling=self._velocity_scaling,
                acceleration_scaling=self._acceleration_scaling,
            )
            self._do_execute(scaled)
        else:
            reason = "empty trajectory" if n_pts == 0 else (
                f"fraction {fraction:.3f} < threshold {self._fraction_threshold:.3f}"
            )
            self.get_logger().warn(
                f"Cartesian path incomplete ({reason}), "
                "falling back to OMPL joint-space planning…"
            )
            self._do_ompl_fallback(pose_stamped)

    # ── Step 3 (fallback): OMPL via MoveGroup ───────────────────────────────

    def _do_ompl_fallback(self, pose_stamped: PoseStamped) -> None:
        self._set_status_phase("planning_ompl")

        constraints = pose_stamped_to_goal_constraints(pose_stamped)
        request = build_motion_plan_request(constraints)
        request.max_velocity_scaling_factor = self._velocity_scaling
        request.max_acceleration_scaling_factor = self._acceleration_scaling

        options = PlanningOptions()
        options.plan_only = True

        goal_msg = MoveGroup.Goal()
        goal_msg.request = request
        goal_msg.planning_options = options

        if not self._move_ac.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                "MoveGroup action server not available.  Is move_group running?"
            )
            self._set_free()
            return

        self.get_logger().info("Sending OMPL planning request to MoveGroup…")
        future = self._move_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_ompl_accepted)

    def _on_ompl_accepted(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Exception sending OMPL goal: {exc}")
            self._set_free()
            return

        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("MoveGroup rejected the OMPL planning goal.")
            self._set_free()
            return

        with self._handle_lock:
            self._plan_goal_handle = goal_handle

        self.get_logger().info("OMPL planning goal accepted — waiting for result…")
        goal_handle.get_result_async().add_done_callback(self._on_ompl_result)

    def _on_ompl_result(self, future) -> None:
        with self._handle_lock:
            self._plan_goal_handle = None

        try:
            wrapped = future.result()
        except Exception as exc:
            self.get_logger().error(f"Exception receiving OMPL result: {exc}")
            self._set_free()
            return

        res = wrapped.result
        if res.error_code.val != 1:
            self.get_logger().error(
                f"OMPL planning failed.  MoveIt error code: {res.error_code.val}  "
                "(−1=plan failed, −31=no IK, −10=start collision, −12=goal collision)"
            )
            self._set_free()
            return

        traj = res.planned_trajectory
        n_pts = len(traj.joint_trajectory.points)
        if n_pts == 0:
            self.get_logger().warn("OMPL planner returned an empty trajectory.")
            self._set_free()
            return

        last_t = traj.joint_trajectory.points[-1].time_from_start
        t_sec = last_t.sec + last_t.nanosec * 1e-9
        with self._status_lock:
            self._last_strategy = "ompl_fallback"
        self.get_logger().info(
            f"OMPL fallback succeeded: {n_pts} waypoints, "
            f"estimated {t_sec:.1f} s.  Executing…"
        )
        self._do_execute(traj)

    # ── Step 4: send trajectory to joint_trajectory_controller ──────────────

    def _do_execute(self, robot_trajectory) -> None:
        with self._estop_lock:
            estop = self._estop_active
        if estop:
            self.get_logger().warn(
                "E-stop is active — discarding planned trajectory."
            )
            self._set_free()
            return

        if self._plan_only:
            self.get_logger().info(
                "plan_only=true — trajectory planned but not sent to controller."
            )
            self._set_free()
            return

        joint_traj = robot_trajectory_to_joint_trajectory(
            robot_trajectory, joint_names=list(UR3E_JOINT_NAMES)
        )
        if not joint_traj.points:
            self.get_logger().error("Converted trajectory is empty — aborting.")
            self._set_free()
            return

        if not self._joint_ac.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                "joint_trajectory_controller action server not available."
            )
            self._set_free()
            return

        self._set_status_phase("executing")
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = joint_traj
        future = self._joint_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_exec_accepted)

    def _on_exec_accepted(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Exception sending execution goal: {exc}")
            self._set_free()
            return

        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error(
                "joint_trajectory_controller rejected the execution goal."
            )
            self._set_free()
            return

        with self._handle_lock:
            self._exec_goal_handle = goal_handle

        self.get_logger().info("Execution accepted — robot is moving…")
        goal_handle.get_result_async().add_done_callback(self._on_exec_result)

    def _on_exec_result(self, future) -> None:
        with self._handle_lock:
            self._exec_goal_handle = None

        try:
            wrapped = future.result()
        except Exception as exc:
            self.get_logger().error(f"Exception receiving execution result: {exc}")
            self._set_free()
            return

        err = wrapped.result.error_code
        if err == 0:
            self.get_logger().info(
                "Trajectory executed successfully — goal reached."
            )
        else:
            self.get_logger().warn(
                f"Execution finished with error code: {err}  "
                "(non-zero means the controller could not reach the goal exactly)"
            )
        self._set_free()

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _set_free(self) -> None:
        with self._busy_lock:
            self._busy = False
        with self._status_lock:
            self._executions_completed += 1
            self._status_phase = "idle"
        self._emit_status()


# ── Entry point ─────────────────────────────────────────────────────────────

def main(args=None) -> int:
    rclpy.init(args=args)
    node = MoveItCartesianNode()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    time.sleep(1.5)

    if node._cartesian_client.wait_for_service(timeout_sec=15.0):
        node.get_logger().info("Connected to GetCartesianPath service.")
    else:
        node.get_logger().warn(
            "GetCartesianPath service not found within 15 s — "
            "will fall back to OMPL on first goal."
        )

    if node._move_ac.wait_for_server(timeout_sec=10.0):
        node.get_logger().info("Connected to MoveGroup action server.")
    else:
        node.get_logger().warn(
            "MoveGroup action server not found — is move_group running?"
        )

    if node._joint_ac.wait_for_server(timeout_sec=10.0):
        node.get_logger().info("Connected to joint_trajectory_controller.")
    else:
        node.get_logger().warn(
            "joint_trajectory_controller not found — check controller state."
        )

    node.get_logger().info(
        "MoveItCartesianNode ready.  Publish to '/goal_pose' to plan and move."
    )

    try:
        ros_thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
