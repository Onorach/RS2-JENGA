# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Emergency Stop Node.

Provides a software e-stop that immediately cancels any in-flight trajectory
on the joint_trajectory_controller (works in simulation and on real hardware).
On real UR hardware the dashboard stop command is also attempted (best-effort).

How cancellation works
----------------------
The joint_trajectory_controller exposes a ROS2 action server.  Every ROS2
action server provides a built-in cancel service at:

    <action_name>/_action/cancel_goal   (type: action_msgs/srv/CancelGoal)

Sending a CancelGoal request with an all-zero goal_id AND zero timestamp
instructs the server to cancel ALL in-progress goals, regardless of which
action client originally sent them.  This is the approach used here — it does
not require the estop_node to have ever sent a trajectory goal itself.

Interfaces
----------
Service  /estop                     std_srvs/srv/SetBool   → data=true: engage, data=false: clear
Topic    /estop        (subscribed)  std_msgs/msg/Bool      → True = engage, False = resume
Topic    /estop_active (published)   std_msgs/msg/Bool      → True while e-stop is active

Usage
-----
    ros2 run ur3e_controller estop_node

    # Engage via service:
    ros2 service call /estop std_srvs/srv/SetBool 'data: true'

    # Clear via service:
    ros2 service call /estop std_srvs/srv/SetBool 'data: false'

    # Engage via topic:
    ros2 topic pub --once /estop std_msgs/msg/Bool 'data: true'

    # Clear via topic:
    ros2 topic pub --once /estop std_msgs/msg/Bool 'data: false'
"""

from __future__ import annotations

import threading

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from action_msgs.msg import GoalStatus, GoalStatusArray
from action_msgs.srv import CancelGoal as CancelGoalSrv
from std_msgs.msg import Bool
from std_srvs.srv import SetBool, Trigger

DEFAULT_JOINT_ACTION = "/joint_trajectory_controller/follow_joint_trajectory"
# UR robot driver dashboard service — only present on real hardware
DASHBOARD_STOP_SERVICE = "/dashboard_client/stop"


class EstopNode(Node):
    """
    Monitors for e-stop requests and cancels all in-flight trajectory goals.

    The node is intentionally lightweight: it does not run any trajectory
    itself; it only sends cancellations and broadcasts state.
    """

    def __init__(self):
        super().__init__("estop_node")

        joint_action = self.declare_parameter(
            "joint_trajectory_action", DEFAULT_JOINT_ACTION
        ).value

        self._cbg = ReentrantCallbackGroup()
        self._lock = threading.Lock()
        self._active = False

        # Direct client to the action server's built-in cancel service.
        # Sending CancelGoal with all-zero goal_id + zero timestamp cancels ALL goals.
        cancel_service = f"{joint_action}/_action/cancel_goal"
        self._cancel_client = self.create_client(
            CancelGoalSrv, cancel_service, callback_group=self._cbg
        )
        self.get_logger().info(f"Cancel service endpoint: {cancel_service}")

        # Publisher: broadcast e-stop state so other nodes (PoseGoalNode, GUI) can react
        self._state_pub = self.create_publisher(Bool, "/estop_active", 1)

        # Single service: /estop — data=True engages, data=False clears
        self.create_service(
            SetBool, "/estop", self._on_estop_service, callback_group=self._cbg
        )

        # Topic: Bool — True = engage e-stop, False = resume
        self.create_subscription(
            Bool, "/estop", self._on_estop_topic, 10, callback_group=self._cbg
        )

        # Subscribe to the trajectory controller's action status topic.
        # While the e-stop is active, any goal that transitions to EXECUTING or
        # ACCEPTED is immediately cancelled — this covers trajectories sent by
        # external nodes (RViz MotionPlanning plugin, scripts, etc.) after the
        # e-stop was engaged.
        self.create_subscription(
            GoalStatusArray,
            f"{joint_action}/_action/status",
            self._on_action_status,
            10,
            callback_group=self._cbg,
        )

        # UR dashboard stop service (real hardware only, ignored gracefully in sim)
        self._dashboard_stop = self.create_client(
            Trigger, DASHBOARD_STOP_SERVICE, callback_group=self._cbg
        )

        self.get_logger().info(
            "EstopNode ready.\n"
            "  Engage:  ros2 service call /estop std_srvs/srv/SetBool 'data: true'\n"
            "  Clear:   ros2 service call /estop std_srvs/srv/SetBool 'data: false'\n"
            "  Topic:   ros2 topic pub --once /estop std_msgs/msg/Bool 'data: true'"
        )

    # ── service callback ──────────────────────────────────────────────────

    def _on_estop_service(
        self, req: SetBool.Request, res: SetBool.Response
    ) -> SetBool.Response:
        if req.data:
            self._do_estop()
            res.message = "E-stop engaged — all trajectory goals cancelled."
        else:
            self._do_resume()
            res.message = "E-stop cleared — robot is ready."
        res.success = True
        return res

    # ── topic callback ────────────────────────────────────────────────────

    def _on_estop_topic(self, msg: Bool) -> None:
        if msg.data:
            self._do_estop()
        else:
            self._do_resume()

    # ── core e-stop logic ─────────────────────────────────────────────────

    def _do_estop(self) -> None:
        with self._lock:
            already_active = self._active
            self._active = True

        if already_active:
            self.get_logger().warn("E-stop is already active.")
            return

        self.get_logger().warn(
            "!!! E-STOP ENGAGED — cancelling all in-flight trajectory goals !!!"
        )
        self._publish_state(True)
        self._send_cancel_all()

        # Best-effort: call UR dashboard stop (only present on real hardware)
        if self._dashboard_stop.service_is_ready():
            self.get_logger().info("Calling UR dashboard stop service…")
            self._dashboard_stop.call_async(Trigger.Request()).add_done_callback(
                self._on_dashboard_stop_done
            )
        else:
            self.get_logger().debug(
                "UR dashboard stop service not available "
                "(running in simulation or driver not started)."
            )

    def _do_resume(self) -> None:
        with self._lock:
            if not self._active:
                return
            self._active = False
        self.get_logger().info("E-stop cleared — robot ready to receive new goals.")
        self._publish_state(False)

    def _send_cancel_all(self) -> None:
        """
        Send a CancelGoal request with all-zero goal_id to the trajectory
        controller's action server, which cancels every in-flight goal.
        """
        if not self._cancel_client.service_is_ready():
            self.get_logger().error(
                "joint_trajectory_controller cancel service not reachable — "
                "is the controller running?"
            )
            return

        # Default CancelGoal.Request() has zero goal_id and zero timestamp,
        # which the action server interprets as "cancel all goals".
        req = CancelGoalSrv.Request()
        try:
            self._cancel_client.call_async(req).add_done_callback(
                self._on_cancel_done
            )
        except Exception as exc:
            self.get_logger().error(f"Failed to send cancel request: {exc}")

    # ── internal callbacks ────────────────────────────────────────────────

    def _on_action_status(self, msg: GoalStatusArray) -> None:
        """
        Re-cancel any goal that appears while the e-stop is active.

        The trajectory controller publishes goal status at ~10 Hz.  If a new
        goal arrives from an external source (RViz, another node) after the
        e-stop was engaged, it will show up here as ACCEPTED or EXECUTING.
        Sending a cancel-all immediately stops it.
        """
        if not self.is_active:
            return
        live_statuses = {GoalStatus.STATUS_ACCEPTED, GoalStatus.STATUS_EXECUTING}
        if any(s.status in live_statuses for s in msg.status_list):
            self.get_logger().warn(
                "E-stop active: new goal detected on trajectory controller — cancelling."
            )
            self._send_cancel_all()

    def _on_cancel_done(self, future) -> None:
        try:
            result = future.result()
            n = len(result.goals_canceling)
            if n > 0:
                self.get_logger().info(f"Controller is cancelling {n} goal(s).")
            else:
                self.get_logger().info(
                    "Cancel request sent — no active goals were found on the controller."
                )
        except Exception as exc:
            self.get_logger().error(f"Error receiving cancel response: {exc}")

    def _on_dashboard_stop_done(self, future) -> None:
        try:
            res = future.result()
            if res.success:
                self.get_logger().info(f"UR dashboard stop: {res.message}")
            else:
                self.get_logger().warn(f"UR dashboard stop returned failure: {res.message}")
        except Exception as exc:
            self.get_logger().warn(f"UR dashboard stop call failed: {exc}")

    def _publish_state(self, active: bool) -> None:
        msg = Bool()
        msg.data = active
        self._state_pub.publish(msg)

    # ── public helpers ────────────────────────────────────────────────────

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._active


# ── entry point ────────────────────────────────────────────────────────────────

def main(args=None) -> int:
    rclpy.init(args=args)
    node = EstopNode()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
