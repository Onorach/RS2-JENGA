# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Launch Gazebo sim + MoveIt + motion planning without RViz (headless).
Use for testing RMRC or MoveIt planning via CLI/scripts without the GUI.

With use_rmrc:=true, uses RMRC planning (no MoveIt needed for planning).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_rmrc_arg = DeclareLaunchArgument(
        "use_rmrc",
        default_value="true",
        description="Use RMRC planning (true) or MoveIt pose_goal (false).",
    )

    # Gazebo sim (no RViz)
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ur3e_controller"), "/launch", "/ur3e_sim_control.launch.py"]
        ),
        launch_arguments={
            "launch_rviz": "false",
        }.items(),
    )

    # MoveIt (no RViz) - only when not using RMRC
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ur_moveit_config"), "/launch", "/ur_moveit.launch.py"]
        ),
        condition=IfCondition(
            PythonExpression(["'", LaunchConfiguration("use_rmrc"), "' == 'false'"])
        ),
        launch_arguments={
            "ur_type": "ur3e",
            "use_sim_time": "true",
            "launch_rviz": "false",
            "use_fake_hardware": "true",
        }.items(),
    )

    # Motion planning (RMRC or MoveIt)
    motion_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("motion_planning"), "/launch", "/motion_planning.launch.py"]
        ),
        launch_arguments={
            "use_rmrc": LaunchConfiguration("use_rmrc"),
        }.items(),
    )

    return LaunchDescription([
        use_rmrc_arg,
        sim_launch,
        moveit_launch,
        motion_launch,
    ])
