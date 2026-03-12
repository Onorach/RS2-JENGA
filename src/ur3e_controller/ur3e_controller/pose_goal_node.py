
"""
Pose-goal node: accepts geometry_msgs/PoseStamped on /goal_pose,
plans a collision-free trajectory with MoveIt2 (plan-only via MoveGroup),
then executes it through joint_trajectory_controller.

Architecture
------------
Everything lives in a single ROS2 node.  All planning and execution
are done with async callbacks — no blocking waits inside any callback.
This is the only pattern that works correctly inside a MultiThreadedExecutor.

Flow
----
/goal_pose (sub)
  → _on_goal()
      → send_goal_async(MoveGroup, plan_only=True)
          → _on_plan_accepted()
              → get_result_async()
                  → _on_plan_result()       ← has the planned trajectory
                      → send_goal_async(FollowJointTrajectory)
                          → _on_exec_accepted()
                              → get_result_async()
                                  → _on_exec_result()   ← done
"""

from __future__ import annotations

import threading
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from control_msgs.action import FollowJointTrajectory
from geometry_msgs.msg import PoseStamped, WrenchStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import PlanningOptions
from std_msgs.msg import Bool
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from ur3e_controller.move_client import UR3E_JOINT_NAMES
from ur3e_controller.moveit_planning import (
    build_motion_plan_request,
    pose_stamped_to_goal_constraints,
    robot_trajectory_to_joint_trajectory,
)

DEFAULT_MOVE_ACTION = "/move_action"
DEFAULT_JOINT_ACTION = "/joint_trajectory_controller/follow_joint_trajectory"
DEFAULT_FT_TOPIC = "/ft_data"


class PoseGoalNode(Node):
    """Plans to pose goals via MoveIt2 (plan-only) then executes via joint_trajectory_controller."""

    def __init__(self):
        super().__init__("pose_goal_node")

        move_action  = self.declare_parameter("move_action_name",      DEFAULT_MOVE_ACTION).value
        joint_action = self.declare_parameter("joint_trajectory_action", DEFAULT_JOINT_ACTION).value
        ft_topic     = self.declare_parameter("ft_topic",               DEFAULT_FT_TOPIC).value

        # All subscriptions, action clients, and their callback chains share one
        # ReentrantCallbackGroup so they can run concurrently without deadlocking.
        self._cbg = ReentrantCallbackGroup()

        # Action client → MoveGroup (plan only)
        self._move_ac = ActionClient(
            self, MoveGroup, move_action, callback_group=self._cbg
        )
        # Action client → joint_trajectory_controller
        self._joint_ac = ActionClient(
            self, FollowJointTrajectory, joint_action, callback_group=self._cbg
        )

        # F/T feedback
        self._ft_lock = threading.Lock()
        self._ft: WrenchStamped | None = None
        self.create_subscription(
            WrenchStamped, ft_topic, self._on_ft, 10, callback_group=self._cbg
        )

        # Goal subscription
        self.create_subscription(
            PoseStamped, "goal_pose", self._on_goal, 10, callback_group=self._cbg
        )

        # Guard against concurrent goals
        self._busy = False
        self._busy_lock = threading.Lock()

        # In-flight goal handles (set when goals are accepted, cleared on completion/cancel)
        self._plan_goal_handle = None
        self._exec_goal_handle = None
        self._handle_lock = threading.Lock()

        # E-stop subscription — reacts to /estop_active broadcast from estop_node
        # Also subscribes directly to /estop Bool so it works without estop_node running
        self.create_subscription(
            Bool, "/estop_active", self._on_estop, 1, callback_group=self._cbg
        )
        self.create_subscription(
            Bool, "/estop", self._on_estop_direct, 1, callback_group=self._cbg
        )

        self.get_logger().info(
            "PoseGoalNode started.  Publish geometry_msgs/PoseStamped to '/goal_pose'."
        )

    # ── F/T ──────────────────────────────────────────────────────────────────

    def _on_ft(self, msg: WrenchStamped) -> None:
        with self._ft_lock:
            self._ft = msg

    def get_latest_wrench(self) -> WrenchStamped | None:
        with self._ft_lock:
            return self._ft

    # ── E-stop ───────────────────────────────────────────────────────────────

    def _on_estop(self, msg: Bool) -> None:
        """Reacts to /estop_active state broadcast from estop_node."""
        if msg.data:
            self._cancel_in_flight_goals()

    def _on_estop_direct(self, msg: Bool) -> None:
        """Reacts to direct /estop Bool topic (True = engage)."""
        if msg.data:
            self._cancel_in_flight_goals()

    def _cancel_in_flight_goals(self) -> None:
        """Cancel any currently active planning or execution goal and free the busy flag."""
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

    # ── Step 1: receive goal ─────────────────────────────────────────────────

    def _on_goal(self, msg: PoseStamped) -> None:
        with self._busy_lock:
            if self._busy:
                self.get_logger().warn("Already executing a goal — ignoring incoming pose.")
                return
            self._busy = True

        pos = msg.pose.position
        frame = msg.header.frame_id or "(no frame)"
        self.get_logger().info(
            f"Goal pose received: xyz=({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f})  frame='{frame}'"
        )
        self._do_plan(msg)

    # ── Step 2: send plan request to MoveGroup ───────────────────────────────

    def _do_plan(self, pose_stamped: PoseStamped) -> None:
        constraints = pose_stamped_to_goal_constraints(pose_stamped)
        request = build_motion_plan_request(constraints)

        options = PlanningOptions()
        options.plan_only = True   # PLAN ONLY — execution is done by us below

        goal_msg = MoveGroup.Goal()
        goal_msg.request = request
        goal_msg.planning_options = options

        if not self._move_ac.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                f"MoveGroup action server '{self._move_ac._action_name}' not available.  Is move_group running?"
            )
            self._set_free()
            return

        self.get_logger().info("Sending planning request to MoveGroup…")
        future = self._move_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_plan_accepted)

    # ── Step 3: planning goal accepted callback ───────────────────────────────

    def _on_plan_accepted(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f"Exception sending plan goal: {exc}")
            self._set_free()
            return

        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("MoveGroup rejected the planning goal.")
            self._set_free()
            return

        with self._handle_lock:
            self._plan_goal_handle = goal_handle

        self.get_logger().info("Planning goal accepted — waiting for result…")
        goal_handle.get_result_async().add_done_callback(self._on_plan_result)

    # ── Step 4: plan result callback ─────────────────────────────────────────

    def _on_plan_result(self, future) -> None:
        with self._handle_lock:
            self._plan_goal_handle = None

        try:
            wrapped = future.result()
        except Exception as exc:
            self.get_logger().error(f"Exception receiving plan result: {exc}")
            self._set_free()
            return

        res = wrapped.result
        # MoveItErrorCodes: SUCCESS=1; –31=no IK; –1=plan failed; –10/–12=collision
        if res.error_code.val != 1:
            self.get_logger().error(
                f"Planning failed.  MoveIt error code: {res.error_code.val}  "
                "(–1=plan failed, –31=no IK solution, –10=start in collision, –12=goal in collision)"
            )
            self._set_free()
            return

        traj = res.planned_trajectory
        n_pts = len(traj.joint_trajectory.points)
        if n_pts == 0:
            self.get_logger().warn("Planner returned an empty trajectory.")
            self._set_free()
            return

        # Estimated duration from the last waypoint's time_from_start
        last_t = traj.joint_trajectory.points[-1].time_from_start
        t_sec = last_t.sec + last_t.nanosec * 1e-9
        self.get_logger().info(
            f"Plan succeeded: {n_pts} waypoints, estimated {t_sec:.1f} s.  Executing…"
        )
        self._do_execute(traj)

    # ── Step 5: send trajectory to joint_trajectory_controller ───────────────

    def _do_execute(self, robot_trajectory) -> None:
        joint_traj = robot_trajectory_to_joint_trajectory(
            robot_trajectory, joint_names=list(UR3E_JOINT_NAMES)
        )
        if not joint_traj.points:
            self.get_logger().error("Converted trajectory is empty — aborting.")
            self._set_free()
            return

        if not self._joint_ac.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                f"joint_trajectory_controller action server '{self._joint_ac._action_name}' not available."
            )
            self._set_free()
            return

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = joint_traj
        future = self._joint_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_exec_accepted)

    # ── Step 6: execution goal accepted callback ──────────────────────────────

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

    # ── Step 7: execution result callback ────────────────────────────────────

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
            self.get_logger().info("Trajectory executed successfully — goal reached.")
        else:
            self.get_logger().warn(
                f"Execution finished with error code: {err}  "
                "(non-zero means the controller could not reach the goal exactly)"
            )
        self._set_free()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _set_free(self) -> None:
        with self._busy_lock:
            self._busy = False


# ── Entry point ───────────────────────────────────────────────────────────────

def main(args=None) -> int:
    rclpy.init(args=args)
    node = PoseGoalNode()

    executor = MultiThreadedExecutor()
    executor.add_node(node)

    # Spin in a background thread so we can do the wait_for_server checks below.
    ros_thread = threading.Thread(target=executor.spin, daemon=True)
    ros_thread.start()

    # Give DDS time to discover action servers before we check.
    time.sleep(1.5)

    if node._move_ac.wait_for_server(timeout_sec=15.0):
        node.get_logger().info("Connected to MoveGroup action server.")
    else:
        node.get_logger().warn(
            "MoveGroup action server not found within 15 s — is move_group running?"
        )

    if node._joint_ac.wait_for_server(timeout_sec=10.0):
        node.get_logger().info("Connected to joint_trajectory_controller.")
    else:
        node.get_logger().warn(
            "joint_trajectory_controller not found — check controller state."
        )

    node.get_logger().info("PoseGoalNode ready.  Publish to '/goal_pose' to plan and move.")

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
