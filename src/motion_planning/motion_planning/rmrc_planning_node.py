# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
RMRC planning node: subscribes to /goal_pose, plans Cartesian RMRC collision-free
trajectories, and executes via joint_trajectory_controller. Works without MoveIt GUI.
"""

from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter

from control_msgs.action import FollowJointTrajectory
from control_msgs.msg import JointTolerance
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

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
DEFAULT_MAX_VELOCITY = 0.5
DEFAULT_D_SAFE = 0.05
DEFAULT_K_REPULSION = 0.5


def _pose_stamped_to_pose_tuple(msg: PoseStamped) -> tuple:
    """Convert PoseStamped to (position [x,y,z], quaternion [x,y,z,w]) for planner."""
    import numpy as np
    p = msg.pose.position
    q = msg.pose.orientation
    pos = np.array([p.x, p.y, p.z], dtype=np.float64)
    quat = np.array([q.x, q.y, q.z, q.w], dtype=np.float64)
    return (pos, quat)


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
        self._plan_only = self.declare_parameter("plan_only", False).value
        self._exclusion_zones_file = self.declare_parameter(
            "exclusion_zones_file", ""
        ).value
        self._robot_description = self.declare_parameter(
            "robot_description", ""
        ).value

        self._cbg = ReentrantCallbackGroup()

        self._joint_ac = ActionClient(
            self,
            FollowJointTrajectory,
            self._joint_action,
            callback_group=self._cbg,
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
        self._exec_goal_handle = None
        self._handle_lock = threading.Lock()

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

        self.get_logger().info(
            "RMRCPlanningNode started. Publish geometry_msgs/PoseStamped to '/goal_pose'."
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
        if msg.data and not was:
            self._cancel_execution()

    def _on_estop_direct(self, msg: Bool) -> None:
        with self._estop_lock:
            was = self._estop_active
            self._estop_active = msg.data
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
                "(e.g. use_rmrc:=true with motion_planning.launch)."
            )
            return None
        try:
            self._planner = RMRCPlanner(
                rd,
                base_link=DEFAULT_PLANNING_FRAME,
                ee_link=DEFAULT_EE_LINK,
                joint_names=list(UR3E_JOINT_NAMES),
            )
            self.get_logger().info("RMRC planner initialized from robot_description.")
        except ImportError as e:
            self.get_logger().error(f"Failed to import ikpy: {e}")
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
            self._obstacles = obstacles_from_yaml_data(
                zones, frame_id=DEFAULT_PLANNING_FRAME
            )
            self.get_logger().info(
                f"Loaded {len(self._obstacles)} obstacles from {path}"
            )
        except Exception as e:
            self.get_logger().warn(f"Could not load exclusion zones: {e}")
        return self._obstacles

    def _on_goal(self, msg: PoseStamped) -> None:
        with self._estop_lock:
            if self._estop_active:
                self.get_logger().warn("E-stop active — ignoring goal.")
                return
        with self._busy_lock:
            if self._busy:
                self.get_logger().warn("Busy — ignoring goal.")
                return
            self._busy = True

        self.get_logger().info(
            f"Goal pose received: xyz=({msg.pose.position.x:.3f}, "
            f"{msg.pose.position.y:.3f}, {msg.pose.position.z:.3f})"
        )

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
        pose_target = _pose_stamped_to_pose_tuple(msg)

        try:
            traj_points = planner.plan_rmrc_trajectory(
                np.array(q_current, dtype=np.float64),
                pose_target,
                obstacles,
                path_resolution_m=self._path_resolution,
                max_velocity_scale=self._max_velocity,
                dt=0.02,
                d_safe=self._d_safe,
                k_repulsion=self._k_repulsion,
            )
        except Exception as e:
            self.get_logger().error(f"RMRC planning failed: {e}")
            self._set_free()
            return

        if not traj_points:
            self.get_logger().error("RMRC planner returned empty trajectory.")
            self._set_free()
            return

        waypoints = [(t, list(q)) for t, q in traj_points]
        joint_traj = build_trajectory(
            UR3E_JOINT_NAMES,
            waypoints,
            time_from_start_sec=None,
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

        if not self._joint_ac.wait_for_server(timeout_sec=5.0):
            self.get_logger().error(
                f"joint_trajectory_controller not available."
            )
            self._set_free()
            return

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = joint_traj
        # Lenient path tolerance to avoid PATH_TOLERANCE_VIOLATED during execution (0.1 rad ~ 6 deg)
        goal_msg.path_tolerance = [
            JointTolerance(name=name, position=0.1, velocity=-1.0, acceleration=-1.0)
            for name in UR3E_JOINT_NAMES
        ]
        # Lenient goal tolerance to avoid GOAL_TOLERANCE_VIOLATED (0.05 rad ~ 3 deg)
        goal_msg.goal_tolerance = [
            JointTolerance(name=name, position=0.05, velocity=-1.0, acceleration=-1.0)
            for name in UR3E_JOINT_NAMES
        ]
        future = self._joint_ac.send_goal_async(goal_msg)
        future.add_done_callback(self._on_exec_accepted)

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
        with self._busy_lock:
            self._busy = False


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
