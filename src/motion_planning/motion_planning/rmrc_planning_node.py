
"""
RMRC planning node: subscribes to /goal_pose, plans Cartesian RMRC collision-free
trajectories, and executes via joint_trajectory_controller. Works without MoveIt GUI.
"""

from __future__ import annotations

import json
import os
import threading
import time
import math
from copy import deepcopy
from pathlib import Path

import numpy as np
import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.duration import Duration as RclDuration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool
from std_msgs.msg import Float64MultiArray
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from tf2_ros import Buffer, TransformListener
from tf2_ros import TransformException
import tf2_geometry_msgs

from ur3e_controller.move_client import (
    UR3E_JOINT_NAMES,
    build_trajectory,
)
from motion_planning.rmrc_planner import (
    RMRCPlanner,
    Obstacle,
    obstacles_from_yaml_data,
)
from motion_planning.moveit_planning import DEFAULT_PLANNING_FRAME, DEFAULT_EE_LINK

DEFAULT_JOINT_ACTION = "/joint_trajectory_controller/follow_joint_trajectory"
DEFAULT_PATH_RESOLUTION_M = 0.002
DEFAULT_MAX_VELOCITY = 0.2
DEFAULT_D_SAFE = 0.15
DEFAULT_K_REPULSION = 1.0
DEFAULT_EXEC_START_DELAY = 1.0
DEFAULT_GOAL_TIME_TOLERANCE = 2.0
DEFAULT_MAX_JOINT_VELOCITY = 0.25
DEFAULT_MAX_JOINT_ACCELERATION = 0.5
DEFAULT_REQUIRE_GOAL_CONVERGENCE = True
DEFAULT_FINAL_POS_TOLERANCE_M = 0.02
DEFAULT_FINAL_ORI_TOLERANCE_RAD = 0.35
DEFAULT_EXECUTION_MODE = "trajectory"
DEFAULT_KINEMATICS_BACKEND = "hybrid"
DEFAULT_VELOCITY_COMMAND_TOPIC = "/joint_group_velocity_controller/commands"
DEFAULT_IK_SEED_GAIN = 0.0
DEFAULT_BODY_LINK_WEIGHT = 1.5
DEFAULT_MAX_CART_REPULSION_LINEAR = 0.75
DEFAULT_USE_MULTI_POINT_REPULSION = True
DEFAULT_POSTURE_BIAS_GAIN = 0.0
DEFAULT_POSTURE_APPLY_SHOULDER_LIFT = True
DEFAULT_POSTURE_APPLY_ELBOW = True
DEFAULT_POSTURE_SHOULDER_LIFT_RAD = -1.57
DEFAULT_POSTURE_ELBOW_RAD = 0.87
DEFAULT_IK_SCORE_MODE = "composite"
DEFAULT_IK_SCORE_W_ELBOW = 10000000000.0
DEFAULT_IK_SCORE_W_CLEARANCE = 0.08
DEFAULT_IK_SCORE_W_START = 0.35
DEFAULT_JOINT_SECONDARY_WEIGHT = 1000000000.0
DEFAULT_JOINT_SECONDARY_GAIN = 1.5
DEFAULT_JOINT_SECONDARY_W_EPSILON = 0.025
DEFAULT_JOINT_SECONDARY_PREF_CLIP = 0.45
DEFAULT_REPULSION_SMOOTH_ALPHA = 0.85
DEFAULT_REPULSION_DIST_SCALE = True
DEFAULT_REPULSION_OUT_GRAD_CAP = 120.0
DEFAULT_ORIENTATION_ERROR_GAIN = 1.15
DEFAULT_PATH_FB_SCALE_CAP = 2.5


def _pose_stamped_to_pose_tuple(msg: PoseStamped) -> tuple:
    """Convert PoseStamped to (position [x,y,z], quaternion [x,y,z,w]) for planner."""
    p = msg.pose.position
    q = msg.pose.orientation
    pos = np.array([p.x, p.y, p.z], dtype=np.float64)
    quat = np.array([q.x, q.y, q.z, q.w], dtype=np.float64)
    return (pos, quat)


def _unwrap_to_nearest(angle: float, reference: float) -> float:
    """Return angle equivalent (mod 2*pi) nearest to reference."""
    two_pi = 2.0 * math.pi
    return angle + two_pi * round((reference - angle) / two_pi)


def _quat_angle_error_rad(q_target, q_actual) -> float:
    """Return shortest angular distance between two quaternions in radians."""
    import numpy as np

    qt = np.array(q_target, dtype=np.float64)
    qa = np.array(q_actual, dtype=np.float64)
    nt = np.linalg.norm(qt)
    na = np.linalg.norm(qa)
    if nt < 1e-12 or na < 1e-12:
        return float("inf")
    qt = qt / nt
    qa = qa / na
    # q and -q represent the same orientation.
    dot = abs(float(np.dot(qt, qa)))
    dot = max(-1.0, min(1.0, dot))
    return 2.0 * math.acos(dot)


class RMRCPlanningNode(Node):
    """
    Plans Cartesian RMRC trajectories to pose goals and executes them.
    Subscribes to /goal_pose; does not require MoveIt GUI.
    """

    def __init__(self):
        super().__init__("rmrc_planning_node")

        self._joint_action = self.declare_parameter(
            "joint_trajectory_action", DEFAULT_JOINT_ACTION
        ).value
        self._path_resolution = self.declare_parameter(
            "path_resolution", DEFAULT_PATH_RESOLUTION_M
        ).value
        self._max_velocity = self.declare_parameter(
            "max_velocity", DEFAULT_MAX_VELOCITY
        ).value
        self._d_safe = self.declare_parameter("d_safe", DEFAULT_D_SAFE).value
        self._k_repulsion = self.declare_parameter(
            "k_repulsion", DEFAULT_K_REPULSION
        ).value
        self._exec_start_delay = self.declare_parameter(
            "execution_start_delay", DEFAULT_EXEC_START_DELAY
        ).value
        self._goal_time_tolerance = self.declare_parameter(
            "goal_time_tolerance", DEFAULT_GOAL_TIME_TOLERANCE
        ).value
        self._max_joint_velocity = self.declare_parameter(
            "max_joint_velocity", DEFAULT_MAX_JOINT_VELOCITY
        ).value
        self._max_joint_acceleration = self.declare_parameter(
            "max_joint_acceleration", DEFAULT_MAX_JOINT_ACCELERATION
        ).value
        self._require_goal_convergence = self.declare_parameter(
            "require_goal_convergence", DEFAULT_REQUIRE_GOAL_CONVERGENCE
        ).value
        self._final_pos_tolerance_m = self.declare_parameter(
            "final_pos_tolerance_m", DEFAULT_FINAL_POS_TOLERANCE_M
        ).value
        self._final_ori_tolerance_rad = self.declare_parameter(
            "final_ori_tolerance_rad", DEFAULT_FINAL_ORI_TOLERANCE_RAD
        ).value
        self._plan_only = self.declare_parameter("plan_only", False).value
        self._exclusion_zones_file = self.declare_parameter(
            "exclusion_zones_file", ""
        ).value
        self._robot_description = self.declare_parameter(
            "robot_description", ""
        ).value
        self._planning_frame = self.declare_parameter(
            "planning_frame", DEFAULT_PLANNING_FRAME
        ).value
        self._execution_mode = str(
            self.declare_parameter("execution_mode", DEFAULT_EXECUTION_MODE).value
        ).lower()
        self._kinematics_backend = str(
            self.declare_parameter("kinematics_backend", DEFAULT_KINEMATICS_BACKEND).value
        ).lower()
        self._velocity_command_topic = self.declare_parameter(
            "velocity_command_topic", DEFAULT_VELOCITY_COMMAND_TOPIC
        ).value
        self._ik_seed_gain = float(
            self.declare_parameter("ik_seed_gain", DEFAULT_IK_SEED_GAIN).value
        )
        self._body_link_weight = float(
            self.declare_parameter("body_link_weight", DEFAULT_BODY_LINK_WEIGHT).value
        )
        self._max_cart_repulsion_linear = float(
            self.declare_parameter(
                "max_cart_repulsion_linear", DEFAULT_MAX_CART_REPULSION_LINEAR
            ).value
        )
        self._use_multi_point_repulsion = bool(
            self.declare_parameter(
                "use_multi_point_repulsion", DEFAULT_USE_MULTI_POINT_REPULSION
            ).value
        )
        self._posture_bias_gain = float(
            self.declare_parameter("posture_bias_gain", DEFAULT_POSTURE_BIAS_GAIN).value
        )
        self._posture_apply_shoulder_lift = bool(
            self.declare_parameter("posture_apply_shoulder_lift", DEFAULT_POSTURE_APPLY_SHOULDER_LIFT).value
        )
        self._posture_shoulder_lift_rad = float(
            self.declare_parameter(
                "posture_shoulder_lift_target_rad", DEFAULT_POSTURE_SHOULDER_LIFT_RAD
            ).value
        )
        self._posture_apply_elbow = bool(
            self.declare_parameter("posture_apply_elbow", DEFAULT_POSTURE_APPLY_ELBOW).value
        )
        self._posture_elbow_rad = float(
            self.declare_parameter("posture_elbow_target_rad", DEFAULT_POSTURE_ELBOW_RAD).value
        )
        self._ik_score_mode = str(
            self.declare_parameter("ik_score_mode", DEFAULT_IK_SCORE_MODE).value
        ).lower()
        self._ik_score_w_elbow = float(
            self.declare_parameter("ik_score_w_elbow", DEFAULT_IK_SCORE_W_ELBOW).value
        )
        self._ik_score_w_clearance = float(
            self.declare_parameter("ik_score_w_clearance", DEFAULT_IK_SCORE_W_CLEARANCE).value
        )
        self._ik_score_w_start = float(
            self.declare_parameter("ik_score_w_start", DEFAULT_IK_SCORE_W_START).value
        )
        self._joint_secondary_weight = float(
            self.declare_parameter("joint_secondary_weight", DEFAULT_JOINT_SECONDARY_WEIGHT).value
        )
        self._joint_secondary_gain = float(
            self.declare_parameter("joint_secondary_gain", DEFAULT_JOINT_SECONDARY_GAIN).value
        )
        self._joint_secondary_w_epsilon = float(
            self.declare_parameter(
                "joint_secondary_w_epsilon", DEFAULT_JOINT_SECONDARY_W_EPSILON
            ).value
        )
        self._joint_secondary_pref_clip = float(
            self.declare_parameter(
                "joint_secondary_pref_clip", DEFAULT_JOINT_SECONDARY_PREF_CLIP
            ).value
        )
        self._repulsion_smooth_alpha = float(
            self.declare_parameter("repulsion_smooth_alpha", DEFAULT_REPULSION_SMOOTH_ALPHA).value
        )
        self._repulsion_dist_scale = bool(
            self.declare_parameter("repulsion_dist_scale", DEFAULT_REPULSION_DIST_SCALE).value
        )
        self._repulsion_out_grad_cap = float(
            self.declare_parameter("repulsion_out_grad_cap", DEFAULT_REPULSION_OUT_GRAD_CAP).value
        )
        self._orientation_error_gain = float(
            self.declare_parameter("orientation_error_gain", DEFAULT_ORIENTATION_ERROR_GAIN).value
        )
        self._path_fb_scale_cap = self.declare_parameter(
            "path_fb_scale_cap", DEFAULT_PATH_FB_SCALE_CAP
        ).value
        self._status_topic = str(
            self.declare_parameter("status_topic", "rmrc_status").value
        )
        self._status_publish_rate_hz = float(
            self.declare_parameter("status_publish_rate_hz", 0.0).value
        )

        self._cbg = ReentrantCallbackGroup()
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

        self._joint_ac = ActionClient(
            self,
            FollowJointTrajectory,
            self._joint_action,
            callback_group=self._cbg,
        )
        self._velocity_pub = self.create_publisher(
            Float64MultiArray,
            str(self._velocity_command_topic),
            10,
        )
        self._status_pub = self.create_publisher(
            String,
            self._status_topic,
            10,
        )

        self._joint_states_lock = threading.Lock()
        self._joint_states: JointState | None = None
        self.create_subscription(
            JointState,
            "/joint_states",
            self._on_joint_states,
            10,
            callback_group=self._cbg,
        )

        self.create_subscription(
            PoseStamped,
            "goal_pose",
            self._on_goal,
            10,
            callback_group=self._cbg,
        )

        self._busy = False
        self._busy_lock = threading.Lock()
        self._pending_goal_lock = threading.Lock()
        self._pending_goal: PoseStamped | None = None
        self._exec_goal_handle = None
        self._handle_lock = threading.Lock()

        self._status_lock = threading.Lock()
        self._status_phase: str = "idle"
        self._executions_completed: int = 0

        self._estop_active = False
        self._estop_lock = threading.Lock()
        self.create_subscription(
            Bool, "/estop_active", self._on_estop, 1, callback_group=self._cbg
        )
        self.create_subscription(
            Bool, "/estop", self._on_estop_direct, 1, callback_group=self._cbg
        )

        self._planner: RMRCPlanner | None = None
        self._obstacles: list[Obstacle] = []

        if self._status_publish_rate_hz > 0.0:
            period = 1.0 / max(self._status_publish_rate_hz, 1e-6)
            self.create_timer(period, self._emit_status)

        self._emit_status()
        self.get_logger().info(
            "RMRCPlanningNode started. Publish geometry_msgs/PoseStamped to '/goal_pose'."
        )
        self.get_logger().info(
            f"RMRC status JSON on '{self._status_topic}' "
            f"(executions_completed increments after each goal cycle finishes)."
        )

    def _on_joint_states(self, msg: JointState) -> None:
        with self._joint_states_lock:
            self._joint_states = msg

    def _get_current_joint_positions(self) -> list[float] | None:
        """Get current joint positions in UR3E_JOINT_NAMES order."""
        with self._joint_states_lock:
            js = self._joint_states
        if js is None or not js.name or not js.position:
            return None
        name_to_pos = dict(zip(js.name, js.position))
        out = []
        for name in UR3E_JOINT_NAMES:
            if name in name_to_pos:
                out.append(float(name_to_pos[name]))
            else:
                return None
        return out if len(out) == 6 else None

    def _on_estop(self, msg: Bool) -> None:
        with self._estop_lock:
            was = self._estop_active
            self._estop_active = msg.data
        if msg.data:
            with self._pending_goal_lock:
                self._pending_goal = None
        if msg.data and not was:
            self._cancel_execution()

    def _on_estop_direct(self, msg: Bool) -> None:
        with self._estop_lock:
            was = self._estop_active
            self._estop_active = msg.data
        if msg.data:
            with self._pending_goal_lock:
                self._pending_goal = None
        if msg.data and not was:
            self._cancel_execution()

    def _cancel_execution(self) -> None:
        self.get_logger().warn("E-stop received — cancelling execution.")
        with self._handle_lock:
            h = self._exec_goal_handle
            self._exec_goal_handle = None
        if h is not None:
            try:
                h.cancel_goal_async()
            except Exception as e:
                self.get_logger().warn(f"Could not cancel: {e}")
        self._set_free()

    def _ensure_planner(self) -> RMRCPlanner | None:
        """Lazy init planner from robot_description parameter."""
        if self._planner is not None:
            return self._planner
        rd = self._robot_description
        if not rd or not isinstance(rd, str):
            self.get_logger().error(
                "robot_description parameter not set. Pass it via the launch file "
                "(e.g. planner:=rmrc with motion_planning.launch)."
            )
            return None
        try:
            self._planner = RMRCPlanner(
                rd,
                base_link=str(self._planning_frame),
                ee_link=DEFAULT_EE_LINK,
                joint_names=list(UR3E_JOINT_NAMES),
                kinematics_backend=str(self._kinematics_backend),
            )
            self.get_logger().info(
                f"RMRC planner initialized from robot_description (backend={self._kinematics_backend})."
            )
        except ImportError as e:
            self.get_logger().error(f"Failed to initialize kinematics backend: {e}")
            return None
        except Exception as e:
            self.get_logger().error(f"Failed to create RMRC planner: {e}")
            return None
        return self._planner

    def _load_obstacles(self) -> list[Obstacle]:
        """Load obstacles from exclusion zones YAML if configured."""
        if self._obstacles:
            return self._obstacles
        path = self._exclusion_zones_file
        if not path or not os.path.isfile(path):
            self.get_logger().debug("No exclusion zones file or file not found.")
            return []
        try:
            import yaml
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            zones = data.get("exclusion_zones", [])
            self._obstacles = obstacles_from_yaml_data(zones, frame_id=str(self._planning_frame))
            self.get_logger().info(
                f"Loaded {len(self._obstacles)} obstacles from {path}"
            )
        except Exception as e:
            self.get_logger().warn(f"Could not load exclusion zones: {e}")
        return self._obstacles

    def _build_posture_joint_targets(self) -> np.ndarray | None:
        """
        Optional NaN-padded 6-vector: merged with analytical IK seed in RMRC null space.
        Use shoulder/elbow hints to discourage inverted-V postures toward the cabinet.
        """
        if self._posture_apply_shoulder_lift or self._posture_apply_elbow:
            pt = np.full(6, np.nan, dtype=np.float64)
            if self._posture_apply_shoulder_lift:
                pt[1] = float(self._posture_shoulder_lift_rad)
            if self._posture_apply_elbow:
                pt[2] = float(self._posture_elbow_rad)
            return pt
        return None

    def _set_status_phase(self, phase: str) -> None:
        with self._status_lock:
            self._status_phase = phase
        self._emit_status()

    def _emit_status(self) -> None:
        with self._status_lock:
            phase = self._status_phase
            completed = self._executions_completed
        with self._busy_lock:
            busy = self._busy
        with self._pending_goal_lock:
            has_buffered = self._pending_goal is not None
        with self._estop_lock:
            estop = self._estop_active
        payload = {
            "state": phase,
            "busy": busy,
            "has_buffered_goal": has_buffered,
            "executions_completed": completed,
            "estop_active": estop,
            "execution_mode": self._execution_mode,
        }
        out = String()
        out.data = json.dumps(payload, separators=(",", ":"))
        self._status_pub.publish(out)

    def _on_goal(self, msg: PoseStamped) -> None:
        with self._estop_lock:
            if self._estop_active:
                self.get_logger().warn("E-stop active — ignoring goal.")
                return
        with self._busy_lock:
            if self._busy:
                with self._pending_goal_lock:
                    self._pending_goal = deepcopy(msg)
                self.get_logger().warn(
                    "Busy — buffering latest goal (replacing any previously buffered goal)."
                )
                return
            self._busy = True

        self._set_status_phase("planning")

        planner = self._ensure_planner()
        if planner is None:
            self._set_free()
            return

        q_current = self._get_current_joint_positions()
        if q_current is None:
            self.get_logger().error(
                "No joint states available. Is /joint_states being published?"
            )
            self._set_free()
            return

        import numpy as np
        obstacles = self._load_obstacles()
        source_frame = str(msg.header.frame_id or "<empty>")
        planning_frame = str(self._planning_frame)
        goal_msg = deepcopy(msg)
        if source_frame != "<empty>" and source_frame != planning_frame:
            try:
                goal_msg = self._tf_buffer.transform(
                    goal_msg,
                    planning_frame,
                    timeout=RclDuration(seconds=0.5),
                )
            except TransformException as e:
                self.get_logger().error(
                    f"Cannot transform goal from '{source_frame}' to '{planning_frame}': {e}"
                )
                self._set_free()
                return
        pose_target = _pose_stamped_to_pose_tuple(goal_msg)
        target_pos, target_quat = pose_target
        self.get_logger().info(
            "RMRC goal received: "
            f"frame='{source_frame}' planning_frame='{planning_frame}' "
            f"goal_in_{planning_frame} "
            f"xyz=({float(target_pos[0]):.3f}, {float(target_pos[1]):.3f}, {float(target_pos[2]):.3f}) "
            f"quat=({float(target_quat[0]):.3f}, {float(target_quat[1]):.3f}, "
            f"{float(target_quat[2]):.3f}, {float(target_quat[3]):.3f})"
        )
        self.get_logger().info(
            "RMRC settings: "
            f"ik_score_mode={self._ik_score_mode} "
            f"joint_secondary_w={float(self._joint_secondary_weight):.3f} "
            f"rep_smooth_alpha={float(self._repulsion_smooth_alpha):.3f} "
            f"ori_gain={float(self._orientation_error_gain):.3f}"
        )

        try:
            try:
                pfc = float(self._path_fb_scale_cap)
            except (TypeError, ValueError):
                pfc = 0.0
            path_cap = pfc if pfc > 0.0 else None
            rep_cap = float(self._repulsion_out_grad_cap)
            traj_points = planner.plan_rmrc_trajectory(
                np.array(q_current, dtype=np.float64),
                pose_target,
                obstacles,
                path_resolution_m=self._path_resolution,
                max_velocity_scale=self._max_velocity,
                dt=0.02,
                d_safe=self._d_safe,
                k_repulsion=self._k_repulsion,
                max_joint_velocity=float(self._max_joint_velocity),
                max_joint_acceleration=float(self._max_joint_acceleration),
                goal_pos_tolerance_m=float(self._final_pos_tolerance_m),
                goal_ori_tolerance_rad=float(self._final_ori_tolerance_rad),
                ik_seed_gain=float(self._ik_seed_gain),
                posture_joint_targets=self._build_posture_joint_targets(),
                posture_bias_gain=float(self._posture_bias_gain),
                body_link_weight=float(self._body_link_weight),
                max_cart_repulsion_linear=float(self._max_cart_repulsion_linear),
                use_multi_point_repulsion=bool(self._use_multi_point_repulsion),
                ik_score_mode=str(self._ik_score_mode),
                ik_score_w_elbow=float(self._ik_score_w_elbow),
                ik_score_w_clearance=float(self._ik_score_w_clearance),
                ik_score_w_start=float(self._ik_score_w_start),
                joint_secondary_weight=float(self._joint_secondary_weight),
                joint_secondary_gain=float(self._joint_secondary_gain),
                joint_secondary_w_epsilon=float(self._joint_secondary_w_epsilon),
                joint_secondary_pref_clip=float(self._joint_secondary_pref_clip),
                repulsion_smooth_alpha=float(self._repulsion_smooth_alpha),
                repulsion_dist_scale=bool(self._repulsion_dist_scale),
                repulsion_out_grad_cap=rep_cap if rep_cap > 0.0 else None,
                orientation_error_gain=float(self._orientation_error_gain),
                path_fb_scale_cap=path_cap,
            )
        except Exception as e:
            self.get_logger().error(f"RMRC planning failed: {e}")
            self._set_free()
            return

        if not traj_points:
            self.get_logger().error("RMRC planner returned empty trajectory.")
            self._set_free()
            return
        try:
            q_final = np.array(traj_points[-1][1], dtype=np.float64)
            ee_final_pos, ee_final_quat = planner.compute_ee_pose(q_final.tolist())
            pos_err = float(np.linalg.norm(np.array(target_pos, dtype=np.float64) - ee_final_pos))
            ori_err = float(_quat_angle_error_rad(target_quat, ee_final_quat))
            self.get_logger().info(
                "RMRC planned final EE pose (planner frame): "
                f"xyz=({float(ee_final_pos[0]):.3f}, {float(ee_final_pos[1]):.3f}, {float(ee_final_pos[2]):.3f}) "
                f"quat=({float(ee_final_quat[0]):.3f}, {float(ee_final_quat[1]):.3f}, "
                f"{float(ee_final_quat[2]):.3f}, {float(ee_final_quat[3]):.3f}), "
                f"pos_err={pos_err:.3f} m, ori_err={ori_err:.3f} rad"
            )
            if bool(self._require_goal_convergence):
                pos_tol = float(self._final_pos_tolerance_m)
                ori_tol = float(self._final_ori_tolerance_rad)
                if pos_err > pos_tol or ori_err > ori_tol:
                    self.get_logger().error(
                        "RMRC convergence check failed: "
                        f"pos_err={pos_err:.3f} m (tol {pos_tol:.3f}), "
                        f"ori_err={ori_err:.3f} rad (tol {ori_tol:.3f}). "
                        "Not executing trajectory."
                    )
                    self._set_free()
                    return
        except Exception as e:
            self.get_logger().warn(f"Could not compute planned final FK pose for diagnostics: {e}")

        # Keep joint trajectory continuous in controller space:
        # unwrap each waypoint to the nearest equivalent angle and force
        # first command to exactly match current measured joints.
        waypoints = []
        prev = list(q_current)
        for idx, (t, q) in enumerate(traj_points):
            q_list = [float(v) for v in q]
            if idx == 0:
                q_adj = list(prev)
            else:
                q_adj = [_unwrap_to_nearest(q_list[j], prev[j]) for j in range(6)]
            waypoints.append((t, q_adj))
            prev = q_adj
        joint_traj = build_trajectory(
            UR3E_JOINT_NAMES,
            waypoints,
            time_from_start_sec=None,
        )
        joint_traj = self._offset_trajectory_times(
            joint_traj, float(self._exec_start_delay)
        )

        dbg = getattr(planner, "_last_rmrc_plan_debug", None)
        if isinstance(dbg, dict) and dbg:
            self.get_logger().info(
                "RMRC plan diagnostics: "
                f"ik_mode={dbg.get('ik_score_mode')} "
                f"ik_candidates={dbg.get('ik_candidates_count')} "
                f"ik_elbow_sel_rad={dbg.get('ik_selected_elbow_rad')} "
                f"traj_first_elbow_rad={dbg.get('traj_first_elbow_rad')} "
                f"traj_last_elbow_rad={dbg.get('traj_last_elbow_rad')} "
                f"path_fb_scale={dbg.get('path_fb_scale')}"
            )
        self.get_logger().info(
            f"RMRC plan succeeded: {len(traj_points)} waypoints."
        )

        if self._plan_only:
            self.get_logger().info(
                "plan_only=true — trajectory planned but not executed."
            )
            self._set_free()
            return

        with self._estop_lock:
            if self._estop_active:
                self.get_logger().warn("E-stop active — not executing.")
                self._set_free()
                return

        if self._execution_mode == "velocity":
            self._set_status_phase("executing")
            self._execute_velocity_waypoints(waypoints)
            return

        if not self._joint_ac.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                "joint_trajectory_controller not available."
            )
            self._set_free()
            return

        self._set_status_phase("executing")
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = joint_traj
        goal_msg.path_tolerance = []
        goal_msg.goal_tolerance = []
        goal_msg.goal_time_tolerance = Duration(
            sec=int(self._goal_time_tolerance),
            nanosec=int(
                round((float(self._goal_time_tolerance) - int(self._goal_time_tolerance)) * 1e9)
            ),
        )
        future = self._joint_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_exec_accepted)

    def _execute_velocity_waypoints(self, waypoints: list[tuple[float, list[float]]]) -> None:
        if len(waypoints) < 2:
            self.get_logger().warn("Not enough RMRC waypoints for velocity execution.")
            self._set_free()
            return
        self.get_logger().info(
            f"Executing RMRC as velocity stream on '{self._velocity_command_topic}'."
        )
        last_t, last_q = waypoints[0]
        try:
            for t, q in waypoints[1:]:
                with self._estop_lock:
                    if self._estop_active:
                        self.get_logger().warn("E-stop active — stopping velocity stream.")
                        self._publish_zero_velocity()
                        self._set_free()
                        return
                dt = max(1e-3, float(t - last_t))
                dq = np.array(q, dtype=np.float64) - np.array(last_q, dtype=np.float64)
                vel = np.clip(
                    dq / dt,
                    -float(self._max_joint_velocity),
                    float(self._max_joint_velocity),
                )
                msg = Float64MultiArray()
                msg.data = [float(v) for v in vel]
                self._velocity_pub.publish(msg)
                time.sleep(dt)
                last_t, last_q = t, q
            self._publish_zero_velocity()
            self.get_logger().info("Velocity execution completed.")
        except Exception as e:
            self.get_logger().error(f"Velocity execution failed: {e}")
            self._publish_zero_velocity()
        self._set_free()

    def _publish_zero_velocity(self) -> None:
        stop_msg = Float64MultiArray()
        stop_msg.data = [0.0] * len(UR3E_JOINT_NAMES)
        self._velocity_pub.publish(stop_msg)

    def _on_exec_accepted(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as e:
            self.get_logger().error(f"Exception sending exec goal: {e}")
            self._set_free()
            return
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("Execution goal rejected.")
            self._set_free()
            return
        with self._handle_lock:
            self._exec_goal_handle = goal_handle
        self.get_logger().info("Execution accepted — robot moving.")
        goal_handle.get_result_async().add_done_callback(self._on_exec_result)

    def _on_exec_result(self, future) -> None:
        with self._handle_lock:
            self._exec_goal_handle = None
        try:
            wrapped = future.result()
        except Exception as e:
            self.get_logger().error(f"Exception in exec result: {e}")
            self._set_free()
            return
        err = wrapped.result.error_code
        if err == 0:
            self.get_logger().info("RMRC trajectory executed successfully.")
        else:
            self.get_logger().warn(
                f"Execution finished with error code {err}: {wrapped.result.error_string}"
            )
        self._set_free()

    def _set_free(self) -> None:
        next_goal = None
        with self._busy_lock:
            self._busy = False
        with self._pending_goal_lock:
            if self._pending_goal is not None:
                next_goal = self._pending_goal
                self._pending_goal = None
        with self._status_lock:
            self._executions_completed += 1
            self._status_phase = "idle"
        self._emit_status()
        if next_goal is not None:
            self.get_logger().info("Processing buffered goal.")
            self._on_goal(next_goal)

    @staticmethod
    def _offset_trajectory_times(
        trajectory: JointTrajectory, delay_sec: float
    ) -> JointTrajectory:
        """Shift all trajectory timestamps by delay_sec."""
        if delay_sec <= 0.0 or not trajectory.points:
            return trajectory
        sec = int(delay_sec)
        nsec = int(round((delay_sec - sec) * 1e9))
        if nsec >= 1_000_000_000:
            sec += 1
            nsec -= 1_000_000_000
        for pt in trajectory.points:
            total_nsec = pt.time_from_start.nanosec + nsec
            carry = total_nsec // 1_000_000_000
            pt.time_from_start = Duration(
                sec=pt.time_from_start.sec + sec + carry,
                nanosec=total_nsec % 1_000_000_000,
            )
        return trajectory


def main(args=None) -> int:
    rclpy.init(args=args)
    node = RMRCPlanningNode()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    time.sleep(1.5)

    if node._joint_ac.wait_for_server(timeout_sec=10.0):
        node.get_logger().info("Connected to joint_trajectory_controller.")
    else:
        node.get_logger().warn(
            "joint_trajectory_controller not found — will retry on goal."
        )

    node.get_logger().info(
        "RMRCPlanningNode ready. Publish to /goal_pose to plan and move."
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
