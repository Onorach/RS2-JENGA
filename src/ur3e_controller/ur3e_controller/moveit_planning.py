# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Motion planning and inverse kinematics via MoveIt2.
Provides collision-free Cartesian/joint planning, pose goals, and exclusion zones.
"""

from __future__ import annotations

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseStamped, Quaternion, Vector3
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    MotionPlanRequest,
    PlanningOptions,
    Constraints,
    PositionConstraint,
    OrientationConstraint,
    BoundingVolume,
    RobotState,
    RobotTrajectory,
)
from moveit_msgs.msg import PlanningScene, PlanningSceneWorld, CollisionObject
from shape_msgs.msg import SolidPrimitive
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from std_msgs.msg import Header

# Defaults for UR3e with ur_moveit_config
DEFAULT_MOVE_ACTION = "/move_action"
DEFAULT_PLANNING_GROUP = "manipulator"
DEFAULT_EE_LINK = "tool0"
DEFAULT_PLANNING_FRAME = "base_link"
# Small tolerance for position (point goal)
DEFAULT_POSITION_TOLERANCE_M = 0.001
# Orientation tolerance (radians) for each axis
DEFAULT_ORIENTATION_TOLERANCE_RAD = 0.01


def pose_stamped_to_goal_constraints(
    pose_stamped: PoseStamped,
    link_name: str = DEFAULT_EE_LINK,
    position_tolerance: float = DEFAULT_POSITION_TOLERANCE_M,
    orientation_tolerance: float = DEFAULT_ORIENTATION_TOLERANCE_RAD,
    frame_id: str | None = None,
) -> Constraints:
    """Build MoveIt Constraints for a pose goal (position + orientation)."""
    header = pose_stamped.header
    if frame_id is not None:
        header.frame_id = frame_id
    pose = pose_stamped.pose

    # Position constraint: point with small sphere tolerance
    pos_constraint = PositionConstraint()
    pos_constraint.header = header
    pos_constraint.link_name = link_name
    pos_constraint.target_point_offset = Vector3(x=0.0, y=0.0, z=0.0)
    sphere = SolidPrimitive()
    sphere.type = SolidPrimitive.SPHERE
    sphere.dimensions = [float(position_tolerance)]
    pos_constraint.constraint_region.primitives = [sphere]
    pos_constraint.constraint_region.primitive_poses = [Pose(position=pose.position, orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0))]
    pos_constraint.weight = 1.0

    # Orientation constraint
    orient_constraint = OrientationConstraint()
    orient_constraint.header = header
    orient_constraint.link_name = link_name
    orient_constraint.orientation = pose.orientation
    orient_constraint.absolute_x_axis_tolerance = orientation_tolerance
    orient_constraint.absolute_y_axis_tolerance = orientation_tolerance
    orient_constraint.absolute_z_axis_tolerance = orientation_tolerance
    orient_constraint.parameterization = OrientationConstraint.XYZ_EULER_ANGLES
    orient_constraint.weight = 1.0

    constraints = Constraints()
    constraints.name = "pose_goal"
    constraints.position_constraints = [pos_constraint]
    constraints.orientation_constraints = [orient_constraint]
    return constraints


def build_motion_plan_request(
    goal_constraints: Constraints,
    group_name: str = DEFAULT_PLANNING_GROUP,
    num_planning_attempts: int = 10,
    allowed_planning_time: float = 5.0,
    start_state: RobotState | None = None,
) -> MotionPlanRequest:
    """Build a MotionPlanRequest for MoveGroup action."""
    req = MotionPlanRequest()
    req.workspace_parameters.header.frame_id = DEFAULT_PLANNING_FRAME
    if start_state is not None:
        req.start_state = start_state
    req.goal_constraints = [goal_constraints]
    req.group_name = group_name
    req.num_planning_attempts = num_planning_attempts
    req.allowed_planning_time = allowed_planning_time
    req.max_velocity_scaling_factor = 1.0
    req.max_acceleration_scaling_factor = 1.0
    return req


def robot_trajectory_to_joint_trajectory(
    robot_trajectory: RobotTrajectory,
    joint_names: list[str] | None = None,
) -> JointTrajectory:
    """Convert MoveIt RobotTrajectory to trajectory_msgs/JointTrajectory for joint_trajectory_controller."""
    if not robot_trajectory.joint_trajectory.points:
        return JointTrajectory(joint_names=joint_names or [], points=[])

    traj = robot_trajectory.joint_trajectory
    out = JointTrajectory()
    out.joint_names = list(traj.joint_names)
    if joint_names is not None:
        out.joint_names = list(joint_names)
    out.points = []
    for pt in traj.points:
        jpt = JointTrajectoryPoint()
        jpt.positions = list(pt.positions)
        jpt.velocities = list(pt.velocities) if pt.velocities else []
        jpt.accelerations = list(pt.accelerations) if pt.accelerations else []
        if pt.time_from_start.sec != 0 or pt.time_from_start.nanosec != 0:
            jpt.time_from_start = pt.time_from_start
        else:
            jpt.time_from_start = Duration(sec=0, nanosec=0)
        out.points.append(jpt)
    return out


class MoveItPlanningInterface(Node):
    """
    ROS2 node for motion planning and IK via MoveIt2.
    Plans to Cartesian pose goals and returns joint trajectories for execution.
    """

    def __init__(
        self,
        move_action_name: str = DEFAULT_MOVE_ACTION,
        planning_group: str = DEFAULT_PLANNING_GROUP,
        ee_link: str = DEFAULT_EE_LINK,
        planning_frame: str = DEFAULT_PLANNING_FRAME,
        node_name: str = "moveit_planning_interface",
    ):
        super().__init__(node_name)
        self._move_action_name = self.declare_parameter("move_action_name", move_action_name).value
        self._planning_group = planning_group
        self._ee_link = ee_link
        self._planning_frame = planning_frame
        self._client = ActionClient(self, MoveGroup, self._move_action_name)
        self._planning_scene_pub = self.create_publisher(
            PlanningScene,
            "/planning_scene",
            10,
        )

    def wait_for_server(self, timeout_sec: float = 30.0) -> bool:
        """Wait for MoveGroup action server."""
        self.get_logger().info(
            "Waiting for MoveGroup action '%s' (timeout %.1fs)...",
            self._move_action_name,
            timeout_sec,
        )
        if not self._client.wait_for_server(timeout_sec=timeout_sec):
            self.get_logger().error("MoveGroup action server not available.")
            return False
        self.get_logger().info("MoveGroup action server available.")
        return True

    def plan_to_pose(
        self,
        pose_stamped: PoseStamped,
        plan_only: bool = True,
        position_tolerance: float = DEFAULT_POSITION_TOLERANCE_M,
        orientation_tolerance: float = DEFAULT_ORIENTATION_TOLERANCE_RAD,
        num_planning_attempts: int = 10,
        allowed_planning_time: float = 5.0,
    ) -> RobotTrajectory | None:
        """
        Plan a collision-free trajectory to a Cartesian pose.
        If plan_only is True, returns the planned trajectory without executing.
        Returns RobotTrajectory or None on failure.
        """
        goal_constraints = pose_stamped_to_goal_constraints(
            pose_stamped,
            link_name=self._ee_link,
            position_tolerance=position_tolerance,
            orientation_tolerance=orientation_tolerance,
        )
        request = build_motion_plan_request(
            goal_constraints,
            group_name=self._planning_group,
            num_planning_attempts=num_planning_attempts,
            allowed_planning_time=allowed_planning_time,
        )
        options = PlanningOptions()
        options.plan_only = plan_only

        goal_msg = MoveGroup.Goal()
        goal_msg.request = request
        goal_msg.planning_options = options

        self.get_logger().info("Sending plan request to MoveGroup (plan_only=%s).", plan_only)
        send_future = self._client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=60.0)
        goal_handle = send_future.result()
        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error("MoveGroup goal rejected.")
            return None

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=allowed_planning_time + 30.0)
        result = result_future.result()
        if result is None:
            self.get_logger().error("MoveGroup result did not complete.")
            return None

        res = result.result
        # MoveItErrorCodes: SUCCESS=1
        if res.error_code.val != 1:
            self.get_logger().warn(
                "Planning failed with error_code=%s.",
                res.error_code.val,
            )
            return None

        if not res.planned_trajectory.joint_trajectory.points:
            self.get_logger().warn("Planned trajectory is empty.")
            return None

        self.get_logger().info(
            "Planning succeeded (%d points).",
            len(res.planned_trajectory.joint_trajectory.points),
        )
        return res.planned_trajectory

    def add_floor_plane(
        self,
        floor_z: float = 0.0,
        frame_id: str = DEFAULT_PLANNING_FRAME,
    ) -> None:
        """
        Add a 10 m × 10 m collision slab whose top surface is at floor_z.
        This prevents any robot link from going below the horizontal plane:
        MoveIt2's collision checker will reject any configuration that intersects
        the slab, so all planned trajectories stay above floor_z.
        """
        from ur3e_controller.exclusion_zones_loader import (
            publish_floor_plane,
        )
        publish_floor_plane(self._planning_scene_pub, floor_z, frame_id)
        self.get_logger().info(
            "Floor-plane exclusion zone added: top at z=%.3f in '%s'.",
            floor_z,
            frame_id,
        )

    def remove_floor_plane(
        self,
        frame_id: str = DEFAULT_PLANNING_FRAME,
    ) -> None:
        """Remove the floor-plane collision object from the planning scene."""
        from ur3e_controller.exclusion_zones_loader import (
            publish_remove_floor_plane,
        )
        publish_remove_floor_plane(self._planning_scene_pub, frame_id)
        self.get_logger().info("Floor-plane exclusion zone removed.")
