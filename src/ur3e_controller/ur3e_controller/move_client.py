# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""Client helper for sending joint trajectory goals to UR3e (simulation or hardware)."""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

# Default joint names for UR3e (must match joint_trajectory_controller config)
UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

DEFAULT_ACTION_NAME = "/joint_trajectory_controller/follow_joint_trajectory"


def build_trajectory(
    joint_names,
    waypoints,
    time_from_start_sec=None,
):
    """
    Build a JointTrajectory message from waypoints.

    Args:
        joint_names: List of joint names (order must match controller).
        waypoints: List of (time_from_start_sec, [j1, j2, j3, j4, j5, j6]) or
                   list of [j1, j2, j3, j4, j5, j6] if time_from_start_sec is a list.
        time_from_start_sec: If waypoints are just positions, this is a list of times (sec).
                             If None and waypoints are (time, positions), times come from waypoints.

    Returns:
        trajectory_msgs/JointTrajectory
    """
    def to_duration(t_sec):
        sec = int(t_sec)
        nsec = int(round((t_sec - sec) * 1e9))
        if nsec >= 1e9:
            nsec = 0
            sec += 1
        return Duration(sec=sec, nanosec=nsec)

    points = []
    if time_from_start_sec is not None:
        for t, pos in zip(time_from_start_sec, waypoints):
            points.append(
                JointTrajectoryPoint(positions=pos, time_from_start=to_duration(t))
            )
    else:
        for wp in waypoints:
            t, pos = wp[0], wp[1]
            points.append(
                JointTrajectoryPoint(positions=pos, time_from_start=to_duration(t))
            )
    return JointTrajectory(joint_names=joint_names, points=points)


class UR3eMoveClient(Node):
    """
    ROS2 node that sends FollowJointTrajectory goals to the UR3e
    (works with Gazebo sim and real robot when joint_trajectory_controller is active).
    """

    def __init__(
        self,
        action_name=DEFAULT_ACTION_NAME,
        joint_names=None,
        wait_for_server_timeout=30.0,
        node_name="ur3e_move_client",
    ):
        super().__init__(node_name)
        self._action_name = self.declare_parameter("action_name", action_name).value
        self._joint_names = joint_names or list(UR3E_JOINT_NAMES)
        self._client = ActionClient(self, FollowJointTrajectory, self._action_name)
        self._wait_timeout = wait_for_server_timeout

    def wait_for_server(self):
        """Block until the action server is available."""
        self.get_logger().info(
            "Waiting for action server '%s' (timeout %.1fs)...",
            self._action_name,
            self._wait_timeout,
        )
        if not self._client.wait_for_server(timeout_sec=self._wait_timeout):
            raise RuntimeError(
                f"Action server '{self._action_name}' not available within {self._wait_timeout}s. "
                "Is the sim/hardware and joint_trajectory_controller running?"
            )
        self.get_logger().info("Action server available.")

    def send_trajectory(self, trajectory):
        """
        Send a JointTrajectory and wait for result.

        Args:
            trajectory: trajectory_msgs/JointTrajectory

        Returns:
            FollowJointTrajectory.Result or None on failure
        """
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory

        self.get_logger().info("Sending trajectory goal (%d points).", len(trajectory.points))
        send_future = self._client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future)
        goal_handle = send_future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("Goal was rejected.")
            return None

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=60.0)
        result = result_future.result()
        if result is None:
            self.get_logger().error("Result future did not complete.")
            return None
        res = result.result
        if res.error_code == FollowJointTrajectory.Result.SUCCESSFUL:
            self.get_logger().info("Trajectory completed successfully.")
        else:
            self.get_logger().warn(
                "Trajectory finished with error_code=%d: %s",
                res.error_code,
                res.error_string,
            )
        return res

    def move_to_positions(self, positions, duration_sec=5.0):
        """
        Move to a single joint position.

        Args:
            positions: List of 6 joint positions (rad).
            duration_sec: Time to reach the goal.

        Returns:
            FollowJointTrajectory.Result or None
        """
        trajectory = JointTrajectory(
            joint_names=self._joint_names,
            points=[
                JointTrajectoryPoint(
                    positions=list(positions),
                    time_from_start=Duration(sec=int(duration_sec), nanosec=0),
                )
            ],
        )
        return self.send_trajectory(trajectory)
