# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Launch Motion Planning and Control: pose goal node, exclusion zones, and e-stop node.
Start this after MoveIt2 and the robot (sim or hardware) are running.

With use_rmrc:=true, runs RMRC planning node instead of MoveIt pose_goal_node
(no MoveIt GUI required). RMRC needs robot_description, built from ur_description.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_planning = "motion_planning"
    pkg_controller = "ur3e_controller"

    exclusion_zones_file_arg = DeclareLaunchArgument(
        "exclusion_zones_file",
        default_value=PathJoinSubstitution(
            [FindPackageShare(pkg_planning), "config", "ur3e_workspace.yaml"]
        ),
        description=(
            "Absolute path to a YAML file defining exclusion zones to load into the "
            "MoveIt2 planning scene. Defaults to ur3e_workspace.yaml (cabinet, platform, "
            "and Jenga tower matching ur3e_controller config/ur3e_workspace.world). "
            "Pass an empty string to load no YAML zones."
        ),
    )
    add_floor_plane_arg = DeclareLaunchArgument(
        "add_floor_plane",
        default_value="true",
        description=(
            "Whether to add the built-in floor-plane collision slab (top at floor_z). "
            "Prevents the robot from planning paths below the cabinet mounting surface."
        ),
    )
    floor_z_arg = DeclareLaunchArgument(
        "floor_z",
        default_value="0.0",
        description=(
            "Z height (metres) of the floor-plane slab top surface in floor_plane_frame_id. "
            "0.0 = ground plane when using world frame."
        ),
    )
    floor_plane_frame_id_arg = DeclareLaunchArgument(
        "floor_plane_frame_id",
        default_value="world",
        description=(
            "TF frame for the floor-plane collision object. "
            "'world' places it at the global ground; 'base_link' places it relative to the robot."
        ),
    )
    plan_only_arg = DeclareLaunchArgument(
        "plan_only",
        default_value="false",
        description="If true, pose_goal_node only plans and does not execute.",
    )
    move_action_arg = DeclareLaunchArgument(
        "move_action_name",
        default_value="/move_action",
        description="MoveGroup action name (from MoveIt2 move_group).",
    )
    joint_action_arg = DeclareLaunchArgument(
        "joint_trajectory_action",
        default_value="/joint_trajectory_controller/follow_joint_trajectory",
        description="FollowJointTrajectory action used by estop_node to cancel all goals.",
    )
    use_rmrc_arg = DeclareLaunchArgument(
        "use_rmrc",
        default_value="false",
        description="If true, run RMRC planning node instead of pose_goal_node (no MoveIt GUI).",
    )

    # robot_description for RMRC: built from ur_description xacro
    # ur3e_controllers.yaml stays in ur3e_controller (robot control config)
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("ur_description"), "urdf", "ur.urdf.xacro"]
            ),
            " ",
            "safety_limits:=true",
            " ",
            "safety_pos_margin:=0.15",
            " ",
            "safety_k_position:=20",
            " ",
            "name:=ur",
            " ",
            "ur_type:=ur3e",
            " ",
            'prefix:=""',
            " ",
            "sim_gazebo:=true",
            " ",
            "simulation_controllers:=",
            PathJoinSubstitution(
                [FindPackageShare(pkg_controller), "config", "ur3e_controllers.yaml"]
            ),
            " ",
            "initial_positions_file:=",
            PathJoinSubstitution(
                [FindPackageShare("ur_description"), "config", "initial_positions.yaml"]
            ),
        ]
    )

    pose_goal_node = Node(
        package=pkg_planning,
        executable="pose_goal_node",
        name="pose_goal_node",
        output="screen",
        condition=UnlessCondition(LaunchConfiguration("use_rmrc")),
        parameters=[
            {
                "plan_only": LaunchConfiguration("plan_only"),
                "move_action_name": LaunchConfiguration("move_action_name"),
            },
        ],
    )

    rmrc_planning_node = Node(
        package=pkg_planning,
        executable="rmrc_planning_node",
        name="rmrc_planning_node",
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_rmrc")),
        parameters=[
            {
                "robot_description": robot_description_content,
                "exclusion_zones_file": LaunchConfiguration("exclusion_zones_file"),
                "plan_only": LaunchConfiguration("plan_only"),
                "joint_trajectory_action": LaunchConfiguration("joint_trajectory_action"),
                "path_resolution": 0.002,
                "max_velocity": 0.5,
                "d_safe": 0.05,
                "k_repulsion": 0.5,
            },
        ],
    )

    exclusion_zones_node = Node(
        package=pkg_planning,
        executable="exclusion_zones_node",
        name="exclusion_zones_node",
        output="screen",
        parameters=[
            {
                "exclusion_zones_file": LaunchConfiguration("exclusion_zones_file"),
                "add_floor_plane": False,
                "floor_z": LaunchConfiguration("floor_z"),
                "floor_plane_frame_id": "world",
            },
        ],
    )

    estop_node = Node(
        package=pkg_controller,
        executable="estop_node",
        name="estop_node",
        output="screen",
        parameters=[
            {
                "joint_trajectory_action": LaunchConfiguration("joint_trajectory_action"),
            },
        ],
    )

    return LaunchDescription([
        exclusion_zones_file_arg,
        add_floor_plane_arg,
        floor_z_arg,
        floor_plane_frame_id_arg,
        plan_only_arg,
        move_action_arg,
        joint_action_arg,
        use_rmrc_arg,
        pose_goal_node,
        rmrc_planning_node,
        exclusion_zones_node,
        estop_node,
    ])
