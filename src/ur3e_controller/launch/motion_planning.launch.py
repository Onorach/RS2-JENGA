# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Launch Motion Planning and Control: pose goal node, exclusion zones, and e-stop node.
Start this after MoveIt2 and the robot (sim or hardware) are running.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = "ur3e_controller"

    exclusion_zones_file_arg = DeclareLaunchArgument(
        "exclusion_zones_file",
        default_value=PathJoinSubstitution(
            [FindPackageShare(pkg), "config", "ur3e_workspace.yaml"]
        ),
        description=(
            "Absolute path to a YAML file defining exclusion zones to load into the "
            "MoveIt2 planning scene. Defaults to ur3e_workspace.yaml (cabinet, platform, "
            "and Jenga tower matching config/ur3e_workspace.world). For hardware setups, "
            "pass config/ur3e_cabinet.yaml. Pass an empty string to load no YAML zones."
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

    pose_goal_node = Node(
        package=pkg,
        executable="pose_goal_node",
        name="pose_goal_node",
        output="screen",
        parameters=[
            {
                "plan_only": LaunchConfiguration("plan_only"),
                "move_action_name": LaunchConfiguration("move_action_name"),
            },
        ],
    )

    # Loads exclusion zones from YAML and publishes them to the MoveIt2 planning scene.
    # At runtime, individual zones can be toggled:
    #   ros2 topic pub --once /remove_exclusion_zone std_msgs/msg/String "data: cabinet_body"
    #   ros2 topic pub --once /add_exclusion_zone    std_msgs/msg/String "data: cabinet_body"
    exclusion_zones_node = Node(
        package=pkg,
        executable="exclusion_zones_node",
        name="exclusion_zones_node",
        output="screen",
        parameters=[
            {
                "exclusion_zones_file": LaunchConfiguration("exclusion_zones_file"),
                "add_floor_plane": False,  # Floor plane only via GUI or service call, not at startup
                "floor_z": LaunchConfiguration("floor_z"),
                # Hardcode "world" so the floor plane loads at global ground (not base_link).
                # For hardware, edit to "base_link" or pass via exclusion_zones_params.yaml.
                "floor_plane_frame_id": "world",
            },
        ],
    )

    # E-stop node: provides /estop and /estop_resume services and broadcasts
    # /estop_active so any terminal or external node can halt the robot instantly.
    #
    #   Engage:  ros2 service call /estop std_srvs/srv/Trigger '{}'
    #   Resume:  ros2 service call /estop_resume std_srvs/srv/Trigger '{}'
    #   Topic:   ros2 topic pub --once /estop std_msgs/msg/Bool 'data: true'
    estop_node = Node(
        package=pkg,
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
        pose_goal_node,
        exclusion_zones_node,
        estop_node,
    ])
