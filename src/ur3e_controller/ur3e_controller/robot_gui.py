#!/usr/bin/env python3
# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Tkinter GUI for controlling the UR3e robot (simulation or hardware).

Two control modes:
  Cartesian – publishes a PoseStamped to /goal_pose; handled by pose_goal_node
              which calls MoveIt2, plans a collision-free trajectory, then executes it.
  Joint     – sends a FollowJointTrajectory action goal directly to
              /joint_trajectory_controller/follow_joint_trajectory (bypasses MoveIt2).

Planning-scene panel adds or removes the floor-plane exclusion zone so that
MoveIt2 rejects any trajectory where a robot link would drop below the table surface.

Force/torque readings (if available) are displayed in real time.

Usage:
    # source the workspace, then:
    ros2 run ur3e_controller robot_gui
"""

from __future__ import annotations

import datetime
import math
import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from typing import Optional

import rclpy
import rclpy.time
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import Pose, PoseStamped, WrenchStamped
from moveit_msgs.msg import CollisionObject, PlanningScene, PlanningSceneWorld
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from shape_msgs.msg import SolidPrimitive
from action_msgs.srv import CancelGoal as CancelGoalSrv
from std_msgs.msg import Bool, Header
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import tf2_ros

from ur3e_controller.exclusion_zones_loader import (
    publish_floor_plane,
    publish_remove_floor_plane,
)

# ──────────────────────────────────────────────────────────────────────────────
# Robot constants
# ──────────────────────────────────────────────────────────────────────────────

UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

JOINT_SHORT_NAMES = ["Pan", "Lift", "Elbow", "Wrist 1", "Wrist 2", "Wrist 3"]

# (min_deg, max_deg) – conservative values; the URDF safety limits apply anyway
JOINT_LIMITS_DEG = [(-360, 360), (-360, 360), (-180, 180), (-360, 360), (-360, 360), (-360, 360)]

# Safe upright home position
HOME_POSITIONS_RAD = [0.0, -math.pi / 2, 0.0, -math.pi / 2, 0.0, 0.0]
HOME_POSITIONS_DEG = [math.degrees(r) for r in HOME_POSITIONS_RAD]

# Preset positions useful for Jenga: (label, [deg × 6])
PRESETS = [
    ("Home",          [   0.0, -90.0,   0.0, -90.0,  0.0,  0.0]),
    ("Ready",         [   0.0, -45.0,  90.0, -90.0,  0.0,  0.0]),
    ("Look Down",     [   0.0, -70.0,  70.0, -90.0,  0.0,  0.0]),
    ("Approach Left", [-45.0,  -60.0,  80.0, -90.0,  0.0,  0.0]),
    ("Approach Right",[ 45.0,  -60.0,  80.0, -90.0,  0.0,  0.0]),
]

DEFAULT_DURATION_SEC = 5.0

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def euler_to_quaternion(roll_rad: float, pitch_rad: float, yaw_rad: float) -> tuple:
    """RPY → quaternion (x, y, z, w)."""
    cr, sr = math.cos(roll_rad / 2), math.sin(roll_rad / 2)
    cp, sp = math.cos(pitch_rad / 2), math.sin(pitch_rad / 2)
    cy, sy = math.cos(yaw_rad / 2), math.sin(yaw_rad / 2)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def quaternion_to_euler(qx: float, qy: float, qz: float, qw: float) -> tuple:
    """Quaternion → (roll, pitch, yaw) in radians."""
    # Roll (rotation around X)
    sinr_cosp = 2.0 * (qw * qx + qy * qz)
    cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    # Pitch (rotation around Y) — clamped for numerical safety
    sinp = 2.0 * (qw * qy - qz * qx)
    pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1.0 else math.asin(sinp)
    # Yaw (rotation around Z)
    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


# ──────────────────────────────────────────────────────────────────────────────
# ROS2 node (runs in background thread)
# ──────────────────────────────────────────────────────────────────────────────

class RobotControlNode(Node):
    """All ROS2 I/O for the GUI: publishers, subscribers, action client."""

    # TF frames to track for live Cartesian pose display
    BASE_FRAME = "base_link"
    EE_FRAME   = "tool0"

    def __init__(self, log_queue: queue.Queue):
        super().__init__("robot_gui_node")
        self._log_q = log_queue
        self._lock = threading.Lock()
        self._joint_positions: dict[str, float] = {}
        self._ft: Optional[WrenchStamped] = None
        self._estop_active = False
        # Tracks the most recent GUI-originated FollowJointTrajectory goal handle
        # so we can cancel it immediately if e-stop fires.
        self._goal_handle = None
        self._goal_handle_lock = threading.Lock()

        # Publishers
        self._goal_pose_pub = self.create_publisher(PoseStamped, "/goal_pose", 10)
        self._scene_pub = self.create_publisher(PlanningScene, "/planning_scene", 10)
        self._estop_pub = self.create_publisher(Bool, "/estop", 1)

        # Action client (joint space)
        self._joint_ac = ActionClient(
            self,
            FollowJointTrajectory,
            "/joint_trajectory_controller/follow_joint_trajectory",
        )

        # E-stop service clients
        self._estop_client = self.create_client(Trigger, "/estop")
        self._estop_resume_client = self.create_client(Trigger, "/estop_resume")

        # Direct cancel client for the trajectory controller's action server.
        # Sending CancelGoal with an all-zero goal_id cancels ALL in-flight goals
        # (including those sent by RViz's MotionPlanning plugin or any other node).
        _joint_action = "/joint_trajectory_controller/follow_joint_trajectory"
        self._traj_cancel_client = self.create_client(
            CancelGoalSrv,
            f"{_joint_action}/_action/cancel_goal",
        )

        # TF2 buffer + listener for live EE Cartesian pose
        self._tf_buffer = tf2_ros.Buffer()
        self._tf_listener = tf2_ros.TransformListener(self._tf_buffer, self)

        # Subscribers
        self.create_subscription(JointState, "/joint_states", self._on_joint_state, 10)
        self.create_subscription(WrenchStamped, "/ft_data", self._on_ft, 10)
        self.create_subscription(Bool, "/estop_active", self._on_estop_active, 1)

    # ── callbacks ──────────────────────────────────────────────────────────

    def _on_joint_state(self, msg: JointState) -> None:
        with self._lock:
            for name, pos in zip(msg.name, msg.position):
                self._joint_positions[name] = pos

    def _on_ft(self, msg: WrenchStamped) -> None:
        with self._lock:
            self._ft = msg

    def _on_estop_active(self, msg: Bool) -> None:
        with self._lock:
            self._estop_active = msg.data

    # ── state getters (thread-safe) ───────────────────────────────────────

    def get_joint_positions(self) -> dict[str, float]:
        with self._lock:
            return dict(self._joint_positions)

    def get_ft(self) -> Optional[WrenchStamped]:
        with self._lock:
            return self._ft

    def get_estop_active(self) -> bool:
        with self._lock:
            return self._estop_active

    def get_ee_pose(
        self,
        base_frame: str = BASE_FRAME,
        ee_frame: str = EE_FRAME,
    ) -> Optional[tuple]:
        """
        Look up the latest TF transform and return
        (x_m, y_m, z_m, roll_deg, pitch_deg, yaw_deg), or None if unavailable.
        Uses the latest available transform (no blocking wait).
        """
        try:
            t = self._tf_buffer.lookup_transform(
                base_frame,
                ee_frame,
                rclpy.time.Time(),   # latest available
            )
            tr = t.transform.translation
            ro = t.transform.rotation
            roll, pitch, yaw = quaternion_to_euler(ro.x, ro.y, ro.z, ro.w)
            return (
                tr.x, tr.y, tr.z,
                math.degrees(roll), math.degrees(pitch), math.degrees(yaw),
            )
        except Exception:
            return None

    # ── commands ──────────────────────────────────────────────────────────

    def trigger_estop(self) -> None:
        """Engage the e-stop: cancel all in-flight goals on the controller."""
        # 1. Cancel any goal this node sent directly (Joint / Presets tabs)
        with self._goal_handle_lock:
            handle = self._goal_handle
            self._goal_handle = None
        if handle is not None:
            try:
                handle.cancel_goal_async()
                self._log("GUI trajectory goal cancel requested.")
            except Exception as exc:
                self._log(f"Could not cancel GUI trajectory goal: {exc}")

        # 2. Cancel ALL in-flight goals on the controller via the built-in cancel
        #    service (zero goal_id = cancel every goal, from any client including
        #    RViz MotionPlanning plugin).
        if self._traj_cancel_client.service_is_ready():
            self._traj_cancel_client.call_async(CancelGoalSrv.Request()).add_done_callback(
                self._on_traj_cancel_done
            )
        else:
            self._log("WARNING: trajectory controller cancel service not reachable.")

        # 3. Publish the /estop Bool topic so pose_goal_node cancels its own handles too
        msg = Bool()
        msg.data = True
        self._estop_pub.publish(msg)
        with self._lock:
            self._estop_active = True

        # 4. Forward to estop_node service if it is running (keeps its state in sync)
        if self._estop_client.service_is_ready():
            self._estop_client.call_async(Trigger.Request()).add_done_callback(
                self._on_estop_service_done
            )

    def resume_estop(self) -> None:
        """Clear the e-stop: publish topic and call service (best-effort)."""
        msg = Bool()
        msg.data = False
        self._estop_pub.publish(msg)
        with self._lock:
            self._estop_active = False

        if self._estop_resume_client.service_is_ready():
            self._estop_resume_client.call_async(Trigger.Request()).add_done_callback(
                self._on_resume_service_done
            )
        else:
            self._log("E-stop cleared via topic.")

    def _on_traj_cancel_done(self, future) -> None:
        try:
            result = future.result()
            n = len(result.goals_canceling)
            if n > 0:
                self._log(f"E-stop: controller cancelling {n} goal(s).")
            else:
                self._log("E-stop: no active goals found on controller.")
        except Exception as exc:
            self._log(f"E-stop cancel service error: {exc}")

    def _on_estop_service_done(self, future) -> None:
        try:
            res = future.result()
            self._log(f"E-stop service: {res.message}")
        except Exception as exc:
            self._log(f"E-stop service call error: {exc}")

    def _on_resume_service_done(self, future) -> None:
        try:
            res = future.result()
            self._log(f"E-stop resume: {res.message}")
        except Exception as exc:
            self._log(f"E-stop resume call error: {exc}")

    def publish_goal_pose(
        self,
        x: float, y: float, z: float,
        roll_deg: float, pitch_deg: float, yaw_deg: float,
        frame_id: str = "base_link",
    ) -> None:
        """Publish a PoseStamped goal — pose_goal_node will plan and execute."""
        qx, qy, qz, qw = euler_to_quaternion(
            math.radians(roll_deg), math.radians(pitch_deg), math.radians(yaw_deg),
        )
        ps = PoseStamped()
        ps.header.frame_id = frame_id
        ps.header.stamp = self.get_clock().now().to_msg()
        ps.pose.position.x = float(x)
        ps.pose.position.y = float(y)
        ps.pose.position.z = float(z)
        ps.pose.orientation.x = qx
        ps.pose.orientation.y = qy
        ps.pose.orientation.z = qz
        ps.pose.orientation.w = qw
        self._goal_pose_pub.publish(ps)
        self._log(
            f"→ /goal_pose published: xyz=({x:.3f}, {y:.3f}, {z:.3f}) m  "
            f"RPY=({roll_deg:.1f}°, {pitch_deg:.1f}°, {yaw_deg:.1f}°)  frame='{frame_id}'"
        )
        self._log("  Planning and execution status appears in the pose_goal_node terminal.")

    def send_joint_goal(
        self,
        positions_rad: list[float],
        duration_sec: float = DEFAULT_DURATION_SEC,
    ) -> None:
        """Send a FollowJointTrajectory action goal directly."""
        if self.get_estop_active():
            self._log("ERROR: E-stop is active — clear it before sending goals.")
            return
        if not self._joint_ac.wait_for_server(timeout_sec=3.0):
            self._log("ERROR: joint_trajectory_controller action server not available.")
            return

        traj = JointTrajectory()
        traj.joint_names = list(UR3E_JOINT_NAMES)
        pt = JointTrajectoryPoint()
        pt.positions = list(positions_rad)
        pt.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        traj.points = [pt]

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = traj
        future = self._joint_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_goal_accepted)

        deg_str = ", ".join(f"{math.degrees(p):.1f}°" for p in positions_rad)
        self._log(f"Joint goal sent ({duration_sec:.1f}s): [{deg_str}]")

    def _on_goal_accepted(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self._log(f"Exception getting joint goal handle: {exc}")
            return
        if not goal_handle or not goal_handle.accepted:
            self._log("Joint goal rejected by controller.")
            return
        with self._goal_handle_lock:
            self._goal_handle = goal_handle
        self._log("Joint goal accepted — executing…")
        goal_handle.get_result_async().add_done_callback(self._on_goal_done)

    def _on_goal_done(self, future) -> None:
        with self._goal_handle_lock:
            self._goal_handle = None
        try:
            result = future.result()
            if result is not None and result.result.error_code == 0:
                self._log("Joint goal completed successfully.")
            else:
                err = result.result.error_code if result else "timeout"
                self._log(f"Joint goal finished with error code: {err}")
        except Exception as exc:
            self._log(f"Exception receiving joint goal result: {exc}")

    def add_floor_plane(self, floor_z: float = 0.0, frame_id: str = "base_link") -> None:
        """Add 10 m × 10 m slab to block all robot motion below floor_z."""
        publish_floor_plane(self._scene_pub, floor_z, frame_id)
        self._log(f"Floor plane added: top at z={floor_z:.3f} m  frame='{frame_id}'")

    def remove_floor_plane(self, frame_id: str = "base_link") -> None:
        """Remove the floor-plane collision object."""
        publish_remove_floor_plane(self._scene_pub, frame_id)
        self._log("Floor plane removed from planning scene.")

    def _log(self, msg: str) -> None:
        self._log_q.put(msg)


# ──────────────────────────────────────────────────────────────────────────────
# GUI
# ──────────────────────────────────────────────────────────────────────────────

class RobotGUI:
    """
    Main GUI window.

    Layout
    ------
    Top row  : live joint positions + F/T sensor readings
    Middle   : Notebook tabs → Cartesian | Joint | Presets
    Bottom   : Planning-scene controls (floor plane) + log
    """

    PAD = 8
    ENTRY_W = 9

    def __init__(self, root: tk.Tk, node: RobotControlNode, log_queue: queue.Queue):
        self._root = root
        self._node = node
        self._log_q = log_queue

        root.title("UR3e Robot Control")
        root.resizable(True, True)
        root.configure(bg="#f0f0f0")
        root.minsize(680, 620)

        self._build_ui()
        self._schedule_updates()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = self._root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(2, weight=1)  # notebook expands
        root.rowconfigure(4, weight=1)  # log expands

        # 0 – e-stop strip (always visible at the top)
        self._build_estop_strip(root)

        # 1 – state strip
        state_frame = ttk.LabelFrame(root, text="Live Robot State", padding=self.PAD)
        state_frame.grid(row=1, column=0, sticky="ew", padx=self.PAD, pady=(4, 4))
        self._build_state_strip(state_frame)

        # 2 – control notebook
        nb_outer = ttk.Frame(root, padding=(self.PAD, 0))
        nb_outer.grid(row=2, column=0, sticky="nsew")
        nb_outer.columnconfigure(0, weight=1)
        nb_outer.rowconfigure(0, weight=1)

        self._nb = ttk.Notebook(nb_outer)
        self._nb.grid(sticky="nsew")

        cart_tab   = ttk.Frame(self._nb, padding=self.PAD)
        joint_tab  = ttk.Frame(self._nb, padding=self.PAD)
        preset_tab = ttk.Frame(self._nb, padding=self.PAD)
        self._nb.add(cart_tab,   text="  Cartesian  ")
        self._nb.add(joint_tab,  text="  Joint  ")
        self._nb.add(preset_tab, text="  Presets  ")

        self._build_cartesian_tab(cart_tab)
        self._build_joint_tab(joint_tab)
        self._build_presets_tab(preset_tab)

        # 3 – planning scene strip
        scene_frame = ttk.LabelFrame(root, text="Planning Scene — Exclusion Zones", padding=self.PAD)
        scene_frame.grid(row=3, column=0, sticky="ew", padx=self.PAD, pady=(4, 4))
        self._build_scene_strip(scene_frame)

        # 4 – log
        log_frame = ttk.LabelFrame(root, text="Log", padding=self.PAD)
        log_frame.grid(row=4, column=0, sticky="nsew", padx=self.PAD, pady=(0, self.PAD))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self._log_text = scrolledtext.ScrolledText(
            log_frame, height=7, state="disabled", font=("Courier", 9)
        )
        self._log_text.grid(row=0, column=0, sticky="nsew")

    # ── e-stop strip ───────────────────────────────────────────────────────

    def _build_estop_strip(self, root: tk.Tk) -> None:
        """Prominent e-stop bar pinned to row 0 of the root window."""
        frame = tk.Frame(root, bg="#cc0000", padx=6, pady=4)
        frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        frame.columnconfigure(1, weight=1)

        # Large E-STOP button
        self._estop_btn = tk.Button(
            frame,
            text="⏹  E-STOP",
            font=("", 13, "bold"),
            bg="#ff0000",
            fg="white",
            activebackground="#aa0000",
            activeforeground="white",
            relief="raised",
            bd=3,
            width=14,
            command=self._on_estop,
        )
        self._estop_btn.grid(row=0, column=0, padx=(4, 10), pady=2)

        # Status label
        self._estop_status_var = tk.StringVar(value="READY")
        self._estop_status_lbl = tk.Label(
            frame,
            textvariable=self._estop_status_var,
            font=("", 12, "bold"),
            bg="#cc0000",
            fg="#aaffaa",
            width=18,
        )
        self._estop_status_lbl.grid(row=0, column=1, padx=4)

        # Resume button (insensitive until e-stop is active)
        self._resume_btn = tk.Button(
            frame,
            text="▶  Resume",
            font=("", 11, "bold"),
            bg="#555555",
            fg="#cccccc",
            activebackground="#228822",
            activeforeground="white",
            relief="raised",
            bd=3,
            width=12,
            state="disabled",
            command=self._on_estop_resume,
        )
        self._resume_btn.grid(row=0, column=2, padx=(10, 4), pady=2)

    # ── state strip ────────────────────────────────────────────────────────

    def _build_state_strip(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        # ── Row 0, col 0: Joint angles ──
        jf = ttk.LabelFrame(parent, text="Joint Angles (°)", padding=(4, 2))
        jf.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 4))
        self._joint_sv: dict[str, tk.StringVar] = {}
        for i, (full, short) in enumerate(zip(UR3E_JOINT_NAMES, JOINT_SHORT_NAMES)):
            ttk.Label(jf, text=short + ":").grid(row=0, column=i * 2, sticky="e", padx=(6, 1))
            sv = tk.StringVar(value="   ---  ")
            ttk.Label(jf, textvariable=sv, width=8, anchor="e",
                      font=("Courier", 9)).grid(row=0, column=i * 2 + 1, sticky="w")
            self._joint_sv[full] = sv

        # ── Row 0, col 1: Live EE Cartesian pose ──
        eef = ttk.LabelFrame(
            parent,
            text=f"EE Pose  ({RobotControlNode.BASE_FRAME} → {RobotControlNode.EE_FRAME})",
            padding=(4, 2),
        )
        eef.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 4))
        self._ee_sv: dict[str, tk.StringVar] = {}
        # Position row
        for i, name in enumerate(["X (m)", "Y (m)", "Z (m)"]):
            ttk.Label(eef, text=name + ":").grid(row=0, column=i * 2, sticky="e", padx=(6, 1))
            sv = tk.StringVar(value="   ---  ")
            ttk.Label(eef, textvariable=sv, width=8, anchor="e",
                      font=("Courier", 9)).grid(row=0, column=i * 2 + 1, sticky="w")
            self._ee_sv[name] = sv
        # Orientation row
        for i, name in enumerate(["Roll°", "Pitch°", "Yaw°"]):
            ttk.Label(eef, text=name + ":").grid(row=1, column=i * 2, sticky="e", padx=(6, 1))
            sv = tk.StringVar(value="   ---  ")
            ttk.Label(eef, textvariable=sv, width=8, anchor="e",
                      font=("Courier", 9)).grid(row=1, column=i * 2 + 1, sticky="w")
            self._ee_sv[name] = sv

        # ── Row 1: Force/Torque, spanning both columns ──
        ftf = ttk.LabelFrame(parent, text="Force/Torque (N, N·m)", padding=(4, 2))
        ftf.grid(row=1, column=0, columnspan=2, sticky="ew")
        self._ft_sv: dict[str, tk.StringVar] = {}
        ft_labels = [
            ("Fx", 0, 0), ("Fy", 0, 2), ("Fz", 0, 4),
            ("Tx", 0, 6), ("Ty", 0, 8), ("Tz", 0, 10),
        ]
        for name, row, col in ft_labels:
            ttk.Label(ftf, text=name + ":").grid(row=row, column=col, sticky="e", padx=(8, 1))
            sv = tk.StringVar(value="   --  ")
            ttk.Label(ftf, textvariable=sv, width=8, anchor="e",
                      font=("Courier", 9)).grid(row=row, column=col + 1, sticky="w")
            self._ft_sv[name] = sv

    # ── Cartesian tab ──────────────────────────────────────────────────────

    def _build_cartesian_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure((1, 3, 5), weight=1)

        row = 0
        ttk.Label(parent, text="Frame:").grid(row=row, column=0, sticky="e", padx=(0, 4))
        self._cart_frame_cb = ttk.Combobox(
            parent, values=["base_link", "world", "base"], width=11, state="normal"
        )
        self._cart_frame_cb.set("base_link")
        self._cart_frame_cb.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, columnspan=6, sticky="ew", pady=(8, 4)
        )

        row += 1
        ttk.Label(parent, text="Position (m)", font=("", 9, "bold")).grid(
            row=row, column=0, columnspan=6, sticky="w"
        )

        row += 1
        self._cart_sv: dict[str, tk.StringVar] = {}
        pos_fields = [("X", "0.300"), ("Y", "0.000"), ("Z", "0.400")]
        for col, (label, default) in enumerate(pos_fields):
            ttk.Label(parent, text=label + " (m):").grid(row=row, column=col * 2, sticky="e", padx=(0, 4))
            sv = tk.StringVar(value=default)
            ttk.Entry(parent, textvariable=sv, width=self.ENTRY_W).grid(
                row=row, column=col * 2 + 1, sticky="w", padx=(0, 8)
            )
            self._cart_sv[label] = sv

        row += 1
        ttk.Label(parent, text="Orientation (°)", font=("", 9, "bold")).grid(
            row=row, column=0, columnspan=6, sticky="w", pady=(8, 0)
        )

        row += 1
        ori_fields = [("Roll", "180.0"), ("Pitch", "0.0"), ("Yaw", "0.0")]
        for col, (label, default) in enumerate(ori_fields):
            ttk.Label(parent, text=label + ":").grid(row=row, column=col * 2, sticky="e", padx=(0, 4))
            sv = tk.StringVar(value=default)
            ttk.Entry(parent, textvariable=sv, width=self.ENTRY_W).grid(
                row=row, column=col * 2 + 1, sticky="w", padx=(0, 8)
            )
            self._cart_sv[label] = sv

        row += 1
        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, columnspan=6, sticky="ew", pady=(8, 4)
        )

        row += 1
        btn_f = ttk.Frame(parent)
        btn_f.grid(row=row, column=0, columnspan=6, sticky="w")
        ttk.Button(btn_f, text="Plan & Execute", command=self._on_cart_send, width=16).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(
            btn_f, text="Copy Current EE Pose", command=self._on_cart_use_current, width=20
        ).pack(side="left", padx=(0, 6))

        row += 1
        ttk.Label(
            parent,
            text="Requires pose_goal_node running.  RPY default = end-effector pointing down.",
            foreground="#666",
            font=("", 8),
        ).grid(row=row, column=0, columnspan=6, sticky="w", pady=(6, 0))

    # ── Joint tab ──────────────────────────────────────────────────────────

    def _build_joint_tab(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(2, weight=1)

        self._joint_slider_vars: list[tk.DoubleVar] = []
        self._joint_entry_vars: list[tk.StringVar] = []

        for i, (short, (lo, hi), default) in enumerate(
            zip(JOINT_SHORT_NAMES, JOINT_LIMITS_DEG, HOME_POSITIONS_DEG)
        ):
            ttk.Label(parent, text=short + ":", width=8, anchor="e").grid(
                row=i, column=0, sticky="e", padx=(0, 4)
            )

            dvar = tk.DoubleVar(value=default)
            evar = tk.StringVar(value=f"{default:.1f}")
            self._joint_slider_vars.append(dvar)
            self._joint_entry_vars.append(evar)

            scale = ttk.Scale(parent, from_=lo, to=hi, orient="horizontal", variable=dvar)
            scale.configure(command=self._make_scale_cmd(evar))
            scale.grid(row=i, column=1, sticky="ew", padx=4)

            entry = ttk.Entry(parent, textvariable=evar, width=7)
            entry.grid(row=i, column=2, padx=(0, 2))
            ttk.Label(parent, text="°").grid(row=i, column=3, sticky="w")

            entry.bind("<Return>",   self._make_entry_commit(dvar, evar))
            entry.bind("<FocusOut>", self._make_entry_commit(dvar, evar))

        # Duration
        row = len(JOINT_SHORT_NAMES)
        dur_f = ttk.Frame(parent)
        dur_f.grid(row=row, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Label(dur_f, text="Duration (s):").pack(side="left", padx=(0, 4))
        self._joint_dur = tk.StringVar(value="5.0")
        ttk.Entry(dur_f, textvariable=self._joint_dur, width=6).pack(side="left")

        # Buttons
        row += 1
        btn_f = ttk.Frame(parent)
        btn_f.grid(row=row, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(btn_f, text="Send Joint Goal", command=self._on_joint_send).pack(side="left", padx=(0, 6))
        ttk.Button(btn_f, text="Go Home",         command=self._on_go_home).pack(side="left", padx=(0, 6))
        ttk.Button(btn_f, text="Sync from Robot", command=self._on_sync_joints).pack(side="left")

    @staticmethod
    def _make_scale_cmd(evar: tk.StringVar):
        def _cmd(val):
            evar.set(f"{float(val):.1f}")
        return _cmd

    @staticmethod
    def _make_entry_commit(dvar: tk.DoubleVar, evar: tk.StringVar):
        def _cb(event=None):
            try:
                dvar.set(float(evar.get()))
            except (ValueError, tk.TclError):
                evar.set(f"{dvar.get():.1f}")
        return _cb

    # ── Presets tab ────────────────────────────────────────────────────────

    def _build_presets_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="Move directly to a named joint configuration (bypasses MoveIt2).",
            foreground="#444",
            font=("", 9),
        ).pack(anchor="w", pady=(0, 10))

        self._preset_dur = tk.StringVar(value="4.0")
        dur_f = ttk.Frame(parent)
        dur_f.pack(anchor="w", pady=(0, 8))
        ttk.Label(dur_f, text="Duration (s):").pack(side="left", padx=(0, 4))
        ttk.Entry(dur_f, textvariable=self._preset_dur, width=6).pack(side="left")

        for label, deg_list in PRESETS:
            btn = ttk.Button(
                parent,
                text=label,
                width=20,
                command=self._make_preset_cmd(deg_list),
            )
            btn.pack(anchor="w", pady=3)

    def _make_preset_cmd(self, deg_list: list[float]):
        def _cmd():
            try:
                dur = float(self._preset_dur.get())
            except ValueError:
                dur = DEFAULT_DURATION_SEC
            rad_list = [math.radians(d) for d in deg_list]
            # Sync sliders to preset values
            for sv, d in zip(self._joint_slider_vars, deg_list):
                sv.set(d)
            self._node.send_joint_goal(rad_list, dur)
        return _cmd

    # ── Scene strip ────────────────────────────────────────────────────────

    def _build_scene_strip(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="Floor-plane z (m):",
        ).grid(row=0, column=0, sticky="e", padx=(0, 4))

        self._floor_z_sv = tk.StringVar(value="0.0")
        ttk.Entry(parent, textvariable=self._floor_z_sv, width=7).grid(row=0, column=1, sticky="w")

        ttk.Label(parent, text="Frame:").grid(row=0, column=2, sticky="e", padx=(12, 4))
        self._scene_frame_cb = ttk.Combobox(
            parent, values=["base_link", "world", "base"], width=10, state="normal"
        )
        self._scene_frame_cb.set("base_link")
        self._scene_frame_cb.grid(row=0, column=3, sticky="w")

        ttk.Button(
            parent, text="Add Floor Plane", command=self._on_add_floor
        ).grid(row=0, column=4, padx=(16, 4))
        ttk.Button(
            parent, text="Remove Floor Plane", command=self._on_remove_floor
        ).grid(row=0, column=5, padx=(0, 4))

        ttk.Label(
            parent,
            text="  Adds a 10 m × 10 m slab — MoveIt2 will reject any pose that takes a link below this height.",
            foreground="#666",
            font=("", 8),
        ).grid(row=1, column=0, columnspan=6, sticky="w", pady=(4, 0))

    # ── Callbacks ──────────────────────────────────────────────────────────

    def _on_cart_send(self) -> None:
        try:
            x     = float(self._cart_sv["X"].get())
            y     = float(self._cart_sv["Y"].get())
            z     = float(self._cart_sv["Z"].get())
            roll  = float(self._cart_sv["Roll"].get())
            pitch = float(self._cart_sv["Pitch"].get())
            yaw   = float(self._cart_sv["Yaw"].get())
            frame = self._cart_frame_cb.get().strip() or "base_link"
        except ValueError as exc:
            messagebox.showerror("Input Error", f"Invalid number: {exc}")
            return
        self._node.publish_goal_pose(x, y, z, roll, pitch, yaw, frame)

    def _on_cart_use_current(self) -> None:
        """Copy the live EE pose (from TF2) into the Cartesian goal-pose input fields."""
        ee = self._node.get_ee_pose()
        if ee is None:
            messagebox.showwarning(
                "TF Not Available",
                "Could not read the end-effector pose from TF2.\n\n"
                "Make sure robot_state_publisher and the joint_state_broadcaster "
                "are running (sim or hardware).",
            )
            return
        x, y, z, roll, pitch, yaw = ee
        self._cart_sv["X"].set(f"{x:.4f}")
        self._cart_sv["Y"].set(f"{y:.4f}")
        self._cart_sv["Z"].set(f"{z:.4f}")
        self._cart_sv["Roll"].set(f"{roll:.2f}")
        self._cart_sv["Pitch"].set(f"{pitch:.2f}")
        self._cart_sv["Yaw"].set(f"{yaw:.2f}")

    def _on_joint_send(self) -> None:
        try:
            positions_rad = [math.radians(sv.get()) for sv in self._joint_slider_vars]
            duration      = float(self._joint_dur.get())
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Input Error", f"Invalid input: {exc}")
            return
        self._node.send_joint_goal(positions_rad, duration)

    def _on_go_home(self) -> None:
        for sv, deg in zip(self._joint_slider_vars, HOME_POSITIONS_DEG):
            sv.set(deg)
        self._node.send_joint_goal(list(HOME_POSITIONS_RAD), float(self._joint_dur.get()))

    def _on_sync_joints(self) -> None:
        """Set sliders to the current robot joint positions."""
        positions = self._node.get_joint_positions()
        for sv, name in zip(self._joint_slider_vars, UR3E_JOINT_NAMES):
            if name in positions:
                sv.set(math.degrees(positions[name]))

    def _on_estop(self) -> None:
        self._node.trigger_estop()
        self._set_estop_ui(active=True)

    def _on_estop_resume(self) -> None:
        self._node.resume_estop()
        self._set_estop_ui(active=False)

    def _set_estop_ui(self, active: bool) -> None:
        if active:
            self._estop_status_var.set("⛔  STOPPED")
            self._estop_status_lbl.configure(fg="#ffff00")
            self._estop_btn.configure(state="disabled", bg="#880000")
            self._resume_btn.configure(state="normal", bg="#228822", fg="white")
        else:
            self._estop_status_var.set("READY")
            self._estop_status_lbl.configure(fg="#aaffaa")
            self._estop_btn.configure(state="normal", bg="#ff0000")
            self._resume_btn.configure(state="disabled", bg="#555555", fg="#cccccc")

    def _on_add_floor(self) -> None:
        try:
            z = float(self._floor_z_sv.get())
        except ValueError:
            messagebox.showerror("Input Error", "Floor z must be a number (e.g. 0.0).")
            return
        frame = self._scene_frame_cb.get().strip() or "base_link"
        self._node.add_floor_plane(z, frame)

    def _on_remove_floor(self) -> None:
        frame = self._scene_frame_cb.get().strip() or "base_link"
        self._node.remove_floor_plane(frame)

    # ── Periodic update ────────────────────────────────────────────────────

    def _schedule_updates(self) -> None:
        self._update_state_display()
        self._drain_log()
        self._root.after(100, self._schedule_updates)

    def _update_state_display(self) -> None:
        # Sync e-stop button state with ROS-reported state (handles external triggers)
        ros_estop = self._node.get_estop_active()
        ui_stopped = self._estop_status_var.get().startswith("⛔")
        if ros_estop and not ui_stopped:
            self._set_estop_ui(active=True)
        elif not ros_estop and ui_stopped:
            self._set_estop_ui(active=False)

        # Joint angles
        positions = self._node.get_joint_positions()
        for name, sv in self._joint_sv.items():
            if name in positions:
                sv.set(f"{math.degrees(positions[name]):+7.2f}")

        # Live EE Cartesian pose from TF2
        ee = self._node.get_ee_pose()
        if ee is not None:
            x, y, z, roll, pitch, yaw = ee
            self._ee_sv["X (m)"].set(f"{x:+7.4f}")
            self._ee_sv["Y (m)"].set(f"{y:+7.4f}")
            self._ee_sv["Z (m)"].set(f"{z:+7.4f}")
            self._ee_sv["Roll°"].set(f"{roll:+7.2f}")
            self._ee_sv["Pitch°"].set(f"{pitch:+7.2f}")
            self._ee_sv["Yaw°"].set(f"{yaw:+7.2f}")

        # Force/torque
        ft = self._node.get_ft()
        if ft is not None:
            self._ft_sv["Fx"].set(f"{ft.wrench.force.x:+7.2f}")
            self._ft_sv["Fy"].set(f"{ft.wrench.force.y:+7.2f}")
            self._ft_sv["Fz"].set(f"{ft.wrench.force.z:+7.2f}")
            self._ft_sv["Tx"].set(f"{ft.wrench.torque.x:+7.3f}")
            self._ft_sv["Ty"].set(f"{ft.wrench.torque.y:+7.3f}")
            self._ft_sv["Tz"].set(f"{ft.wrench.torque.z:+7.3f}")

    def _drain_log(self) -> None:
        while not self._log_q.empty():
            msg = self._log_q.get_nowait()
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self._log_text.configure(state="normal")
            self._log_text.insert("end", f"[{ts}] {msg}\n")
            self._log_text.see("end")
            self._log_text.configure(state="disabled")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main(args=None) -> int:
    rclpy.init(args=args)
    log_q: queue.Queue = queue.Queue()
    node = RobotControlNode(log_q)

    executor = MultiThreadedExecutor()
    executor.add_node(node)
    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    root = tk.Tk()
    try:
        # Improve scaling on HiDPI displays
        root.tk.call("tk", "scaling", 1.4)
    except Exception:
        pass

    gui = RobotGUI(root, node, log_q)
    log_q.put("GUI ready.  ROS2 node: robot_gui_node")
    log_q.put(
        "Cartesian tab: publishes to /goal_pose (needs pose_goal_node running)."
    )
    log_q.put("Joint tab / Presets: send directly to joint_trajectory_controller.")

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
