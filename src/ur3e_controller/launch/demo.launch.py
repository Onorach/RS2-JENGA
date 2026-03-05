# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""Launch the UR3e demo node (sends a short trajectory). Start sim or real robot first."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "action_name",
            default_value="/joint_trajectory_controller/follow_joint_trajectory",
            description="FollowJointTrajectory action name (for namespaced controllers).",
        ),
        Node(
            package="rs2_jenga",
            executable="move_ur3e_demo",
            name="ur3e_demo",
            output="screen",
            parameters=[{
                "action_name": LaunchConfiguration("action_name"),
            }],
        ),
    ])
