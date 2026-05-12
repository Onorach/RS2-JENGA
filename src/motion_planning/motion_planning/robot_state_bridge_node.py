
"""
Robot State Bridge Node.

Publishes /robot_state (std_msgs/String) by aggregating JSON status messages
from the five MTC action servers, and handles /ee_override_array
(std_msgs/Int8MultiArray) from the GUI to drive the gripper via the MoveGroup
action when an override is active.

Topics subscribed
-----------------
/estop_active               std_msgs/Bool
/ee_override_array          std_msgs/Int8MultiArray  [close, open, release]
mtc_status                  std_msgs/String  (pick-place server)
mtc_probe_status            std_msgs/String  (probe-block server)
mtc_extract_side_status     std_msgs/String  (extract-side server)
mtc_extract_middle_status   std_msgs/String  (extract-middle server)
mtc_arm_ready_status        std_msgs/String  (arm-ready server)

Topics published
----------------
/robot_state    std_msgs/String  (5 Hz, human-readable label)

Actions used
------------
/move_action    moveit_msgs/action/MoveGroup  (gripper open/close override)

Parameters
----------
hand_group              (str)   gripper planning group   default: ur_onrobot_gripper
move_action             (str)   MoveGroup action name    default: /move_action
gripper_joint_name      (str)   gripper width joint      default: finger_width
gripper_open_position   (float) open gap in metres       default: 0.100
gripper_closed_position (float) closed gap in metres     default: 0.0

Gripper override behaviour
--------------------------
The operator's desired state (_desired_override: "none" | "close" | "open") is
recorded immediately on every button press and persists until Release Override
is pressed.  The MoveGroup goal is only dispatched when ALL MTC servers are
idle, preventing any race with execute_task_solution.  If MTC is busy when the
button is pressed the override is queued; it fires automatically once the last
busy server reports idle.  Pressing Release Override at any time cancels any
in-flight goal and clears the desired state.
"""

from __future__ import annotations

import json
import threading

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    JointConstraint,
    MotionPlanRequest,
    PlanningOptions,
)
from std_msgs.msg import Bool, Int8MultiArray, String
from jenga_interfaces.action import (
    JengaArmReady,
    JengaExtractMiddleBlock,
    JengaExtractSideBlock,
    JengaPickPlace,
    JengaProbeBlock,
)


# MTC action servers — (action_name, action_type) pairs used for cancellation.
_MTC_ACTION_CLIENTS: list[tuple[str, type]] = [
    ("jenga_pick_place",           JengaPickPlace),
    ("jenga_probe_block",          JengaProbeBlock),
    ("jenga_extract_side_block",   JengaExtractSideBlock),
    ("jenga_extract_middle_block", JengaExtractMiddleBlock),
    ("jenga_arm_ready",            JengaArmReady),
]

# Mapping from MTC status topic name → human-readable /robot_state label.
# Checked in order; the first busy server wins.
_MTC_TOPICS: dict[str, str] = {
    "mtc_status":                 "PICK & PLACE",
    "mtc_extract_side_status":    "EXTRACTING (SIDE)",
    "mtc_extract_middle_status":  "EXTRACTING (MIDDLE)",
    "mtc_arm_ready_status":       "HOMING",
    "mtc_probe_status":           "PROBING",
}


class RobotStateBridgeNode(Node):
    """
    Aggregates MTC server statuses into /robot_state and handles gripper
    override commands from /ee_override_array.

    The /ee_override_array message is an Int8MultiArray of three elements:
      index 0 = 1 → close gripper override desired
      index 1 = 1 → open gripper override desired
      index 2 = 1 → release override (normal motion-planner control restored)
    Only one element is non-zero at a time (enforced by the GUI).
    """

    def __init__(self) -> None:
        super().__init__("robot_state_bridge_node")

        # ── Parameters ─────────────────────────────────────────────────────
        self._hand_group: str = self.declare_parameter(
            "hand_group", "ur_onrobot_gripper"
        ).value
        self._move_action: str = self.declare_parameter(
            "move_action", "/move_action"
        ).value
        self._gripper_joint: str = self.declare_parameter(
            "gripper_joint_name", "finger_width"
        ).value
        self._open_pos: float = self.declare_parameter(
            "gripper_open_position", 0.100
        ).value
        self._closed_pos: float = self.declare_parameter(
            "gripper_closed_position", 0.0
        ).value

        # ── Internal state ──────────────────────────────────────────────────
        self._lock = threading.Lock()
        self._estop: bool = False
        self._server_busy: dict[str, bool] = {k: False for k in _MTC_TOPICS}
        # What the operator currently wants ("none" | "close" | "open").
        # Persists across MTC activity; cleared only by Release Override.
        self._desired_override: str = "none"
        # True while a MoveGroup gripper goal is in the air.
        self._override_in_flight: bool = False
        self._gripper_goal_handle = None

        # ── Callback group (reentrant so async action callbacks can fire) ───
        self._cbg = ReentrantCallbackGroup()

        # ── Subscriptions ───────────────────────────────────────────────────
        self.create_subscription(Bool, "/estop_active", self._cb_estop, 10)

        for topic in _MTC_TOPICS:
            self.create_subscription(
                String, topic, self._make_status_cb(topic), 10
            )

        self.create_subscription(
            Int8MultiArray, "/ee_override_array", self._cb_override, 10
        )

        # ── Publisher ───────────────────────────────────────────────────────
        self._pub_state = self.create_publisher(String, "/robot_state", 10)

        # ── 5 Hz publish timer ──────────────────────────────────────────────
        self.create_timer(0.2, self._publish_state)

        # ── 2 Hz override retry timer ───────────────────────────────────────
        # Guarantees the queued override fires even if the busy→idle edge in
        # _make_status_cb is missed (e.g. topic latency, MTC cancelled without
        # publishing a final status update).
        self.create_timer(0.5, self._override_retry_tick)

        # ── MoveGroup action client (gripper) ───────────────────────────────
        self._gripper_client = ActionClient(
            self, MoveGroup, self._move_action, callback_group=self._cbg
        )

        # ── MTC action clients (cancellation only) ──────────────────────────
        self._mtc_clients: list[ActionClient] = [
            ActionClient(self, action_type, action_name, callback_group=self._cbg)
            for action_name, action_type in _MTC_ACTION_CLIENTS
        ]

        self.get_logger().info(
            f"RobotStateBridgeNode ready — group='{self._hand_group}', "
            f"joint='{self._gripper_joint}', "
            f"closed={self._closed_pos:.3f} m, open={self._open_pos:.3f} m"
        )

    # ── Subscription callbacks ──────────────────────────────────────────────

    def _cb_estop(self, msg: Bool) -> None:
        with self._lock:
            self._estop = msg.data

    def _make_status_cb(self, topic: str):
        """Return a closure that updates the busy flag for *topic*.

        When a server transitions from busy → idle, attempt to apply any
        queued gripper override that was blocked while MTC was running.
        """
        def _cb(msg: String) -> None:
            try:
                data = json.loads(msg.data)
                busy = bool(data.get("busy", False))
            except (json.JSONDecodeError, TypeError):
                busy = False
            with self._lock:
                was_busy = self._server_busy[topic]
                self._server_busy[topic] = busy
                became_idle = was_busy and not busy
            if became_idle:
                self._try_apply_override()

        return _cb

    def _cb_override(self, msg: Int8MultiArray) -> None:
        """Record the operator's desired gripper state, then try to apply it."""
        data = list(msg.data)
        if len(data) < 3:
            self.get_logger().warn(
                f"/ee_override_array has {len(data)} element(s); expected 3 — ignoring"
            )
            return

        with self._lock:
            if bool(data[0]):
                self._desired_override = "close"
            elif bool(data[1]):
                self._desired_override = "open"
            else:
                self._desired_override = "none"
            desired = self._desired_override

        if desired == "none":
            self._cancel_override_goal()
        else:
            self._try_apply_override()

    # ── State publishing ────────────────────────────────────────────────────

    def _publish_state(self) -> None:
        msg = String()
        msg.data = self._compute_state()
        self._pub_state.publish(msg)

    def _compute_state(self) -> str:
        """Return the highest-priority human-readable robot state string."""
        with self._lock:
            if self._estop:
                return "ESTOP ACTIVE"
            mtc_busy = any(self._server_busy.values())
            if self._desired_override != "none":
                base = (
                    "OVERRIDE: CLOSING"
                    if self._desired_override == "close"
                    else "OVERRIDE: OPENING"
                )
                return f"{base} [QUEUED]" if mtc_busy else base
            if mtc_busy:
                for topic, label in _MTC_TOPICS.items():
                    if self._server_busy.get(topic, False):
                        return label
        return "STANDBY"

    # ── Gripper override logic ──────────────────────────────────────────────

    def _try_apply_override(self) -> None:
        """Attempt to send a MoveGroup gripper goal if conditions allow.

        Guards (checked inside lock):
          - desired_override must be set
          - no goal already in flight
          - no MTC server currently busy

        All async work (cancel dispatch, goal send) is done AFTER releasing the
        lock to avoid interacting with the ROS2 executor's callback queue while
        the lock is held, which could silently stall cancel requests.
        """
        with self._lock:
            desired = self._desired_override
            if desired == "none":
                return
            if self._override_in_flight:
                return
            mtc_busy = any(self._server_busy.values())
            if not mtc_busy:
                # Pre-claim the in-flight slot while the lock is still held so
                # concurrent calls (timer + status callback) cannot both proceed.
                target = self._closed_pos if desired == "close" else self._open_pos
                self._override_in_flight = True
        # Lock released — safe to call async APIs

        if mtc_busy:
            self.get_logger().info(
                f"Gripper override '{desired}' — cancelling active MTC goals"
            )
            self._cancel_all_mtc_goals()
            return  # _override_retry_tick will retry once all servers report idle

        if not self._gripper_client.server_is_ready():
            self.get_logger().warn(
                "MoveGroup action server not ready — gripper override deferred"
            )
            with self._lock:
                self._override_in_flight = False
            return

        label = "OVERRIDE: CLOSING" if desired == "close" else "OVERRIDE: OPENING"
        self.get_logger().info(f"Gripper override: {label} (target={target:.4f} m)")
        goal = self._build_gripper_goal(target)
        future = self._gripper_client.send_goal_async(goal)
        future.add_done_callback(self._on_gripper_goal_sent)

    def _override_retry_tick(self) -> None:
        """2 Hz fallback: retry a queued override if MTC has since gone idle.

        Complements the busy→idle edge trigger in _make_status_cb.  Either
        path can deliver the gripper command; _override_in_flight prevents
        duplicate sends.
        """
        with self._lock:
            if self._desired_override == "none" or self._override_in_flight:
                return
        self._try_apply_override()

    def _cancel_all_mtc_goals(self) -> None:
        """Send cancel-all requests to every MTC action server (fire-and-forget).

        Called when an override is activated while MTC is busy.  Each server's
        busy flag will drop to False when the cancellation propagates, which
        triggers _make_status_cb → _try_apply_override() automatically.
        """
        for client in self._mtc_clients:
            if client.server_is_ready():
                client.cancel_all_goals_async()

    def _cancel_override_goal(self) -> None:
        """Cancel any in-flight gripper goal and clear both override fields."""
        with self._lock:
            handle = self._gripper_goal_handle
            self._desired_override = "none"
            self._override_in_flight = False
        if handle is not None:
            self.get_logger().info("Cancelling active gripper override goal")
            handle.cancel_goal_async()

    # ── MoveGroup goal helpers ──────────────────────────────────────────────

    def _build_gripper_goal(self, target_pos: float) -> MoveGroup.Goal:
        """Build a MoveGroup goal that moves finger_width to *target_pos*."""
        jc = JointConstraint(
            joint_name=self._gripper_joint,
            position=float(target_pos),
            tolerance_above=0.005,
            tolerance_below=0.005,
            weight=1.0,
        )

        req = MotionPlanRequest()
        req.group_name = self._hand_group
        req.start_state.is_diff = True
        req.goal_constraints = [Constraints(joint_constraints=[jc])]
        req.num_planning_attempts = 3
        req.allowed_planning_time = 3.0
        req.max_velocity_scaling_factor = 1.0
        req.max_acceleration_scaling_factor = 1.0

        opts = PlanningOptions()
        opts.plan_only = False
        opts.replan = False

        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options = opts
        return goal

    def _on_gripper_goal_sent(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().warn("Gripper override goal rejected by move_group")
            with self._lock:
                self._override_in_flight = False
            return
        with self._lock:
            self._gripper_goal_handle = goal_handle
        goal_handle.get_result_async().add_done_callback(self._on_gripper_result)

    def _on_gripper_result(self, future) -> None:
        result = future.result()
        if result is None:
            self.get_logger().warn("Gripper override result future returned None")
        else:
            self.get_logger().info(
                f"Gripper override complete (MoveIt error_code={result.result.error_code.val})"
            )
        with self._lock:
            self._override_in_flight = False
            self._gripper_goal_handle = None
        # _desired_override is intentionally NOT cleared here — the operator's
        # choice persists until they explicitly press Release Override.


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = RobotStateBridgeNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
