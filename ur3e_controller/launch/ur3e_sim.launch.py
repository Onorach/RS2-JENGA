# Copyright 2025
# Launch UR3e in simulation (Gazebo + RViz + MoveIt) and the ur3e_controller node.
# Movement commands on /move_group/goal (PoseStamped) are planned by MoveIt and
# executed on the simulated robot via joint_trajectory_controller.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "ur_type",
            default_value="ur3e",
            description="UR robot type (e.g. ur3e, ur5e).",
        ),
        DeclareLaunchArgument(
            "velocity_scaling",
            default_value="0.5",
            description="Velocity scaling factor for MoveIt (0.01 to 1.0).",
        ),
        DeclareLaunchArgument(
            "planning_group",
            default_value="ur_manipulator",
            description="MoveIt planning group name.",
        ),
    ]

    ur_type = LaunchConfiguration("ur_type")
    velocity_scaling = LaunchConfiguration("velocity_scaling")
    planning_group = LaunchConfiguration("planning_group")

    # Gazebo + controller_manager + MoveIt (from Universal_Robots_ROS2_Gazebo_Simulation)
    ur_sim_moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("ur_simulation_gazebo"),
                "/launch",
                "/ur_sim_moveit.launch.py",
            ]
        ),
        launch_arguments={
            "ur_type": ur_type,
        }.items(),
    )

    # Our controller node: subscribes to /move_group/goal, plans with MoveIt, executes on sim
    ur3e_controller_node = Node(
        package="ur3e_controller",
        executable="ur_node",
        name="ur3e_controller",
        output="screen",
        parameters=[
            {"use_sim_time": True},
            {"velocity_scaling": velocity_scaling},
            {"planning_group": planning_group},
        ],
    )

    # Start controller node after a short delay so MoveIt and sim are coming up.
    # MoveGroupInterface will wait for move_group; no strict ordering required.
    return LaunchDescription(
        declared_arguments
        + [
            ur_sim_moveit_launch,
            ur3e_controller_node,
        ]
    )
