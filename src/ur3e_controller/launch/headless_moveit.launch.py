# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Launch Gazebo sim + MoveIt + motion planning without RViz (headless).
Use for testing RMRC, MoveIt OMPL, or MoveIt Cartesian planning via CLI/scripts.

planner:=rmrc       → RMRC planning (no MoveIt needed for planning).
planner:=moveit     → MoveIt OMPL joint-space planning.
planner:=moveit_cartesian → MoveIt Cartesian straight-line + OMPL fallback.

Both MoveIt planners start the move_group node automatically.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    planner_arg = DeclareLaunchArgument(
        "planner",
        default_value="rmrc",
        choices=["rmrc", "moveit", "moveit_cartesian"],
        description=(
            "Planning backend: 'rmrc' (DIY RMRC, no MoveIt), 'moveit' (OMPL), "
            "'moveit_cartesian' (Cartesian straight-line + OMPL fallback)."
        ),
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

    # MoveIt (no RViz) — started for both 'moveit' and 'moveit_cartesian' planners
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ur_moveit_config"), "/launch", "/ur_moveit.launch.py"]
        ),
        condition=IfCondition(
            PythonExpression(["'", LaunchConfiguration("planner"), "' != 'rmrc'"])
        ),
        launch_arguments={
            "ur_type": "ur3e",
            "use_sim_time": "true",
            "launch_rviz": "false",
            "use_fake_hardware": "true",
            # Prevent launch-arg name collision with ur3e_sim_control.launch.py which also declares
            # a global "description_file" defaulting to "ur3e_workspace.urdf.xacro".
            # ur_moveit.launch.py defaults description_package to "ur_description", so explicitly
            # pairing it with a valid file avoids the /opt/ros/.../ur3e_workspace... missing-file error.
            "description_package": "ur_description",
            "description_file": "ur.urdf.xacro",
        }.items(),
    )

    # Motion planning (RMRC, MoveIt OMPL, or MoveIt Cartesian)
    motion_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("motion_planning"), "/launch", "/motion_planning.launch.py"]
        ),
        launch_arguments={
            "planner": LaunchConfiguration("planner"),
        }.items(),
    )

    return LaunchDescription([
        planner_arg,
        sim_launch,
        moveit_launch,
        motion_launch,
    ])
