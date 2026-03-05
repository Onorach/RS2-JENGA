# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Launch Motion Planning and Control: pose goal node and optional exclusion zones.
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
        default_value="",
        description="Path to YAML file with exclusion zones (optional). "
        "Use 'default' to load config/exclusion_zones_example.yaml from the package.",
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

    # Optional: loads exclusion zones from YAML and adds them to the planning scene.
    # Leave exclusion_zones_file empty to skip. Otherwise pass a path or use the example:
    #   ros2 launch ur3e_controller motion_planning.launch.py exclusion_zones_file:=$(ros2 pkg prefix ur3e_controller)/share/ur3e_controller/config/exclusion_zones_example.yaml
    exclusion_zones_node = Node(
        package=pkg,
        executable="exclusion_zones_node",
        name="exclusion_zones_node",
        output="screen",
        parameters=[
            {
                "exclusion_zones_file": LaunchConfiguration("exclusion_zones_file"),
            },
        ],
    )

    return LaunchDescription([
        exclusion_zones_file_arg,
        plan_only_arg,
        move_action_arg,
        pose_goal_node,
        exclusion_zones_node,
    ])
