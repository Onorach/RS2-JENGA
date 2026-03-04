# Copyright 2025
# Launch only the ur3e_controller node for use with real UR3e hardware.
# Prerequisites: start the robot driver and MoveIt first, e.g.:
#   ros2 launch ur_bringup ur_control.launch.py ur_type:=ur3e robot_ip:=YOUR_ROBOT_IP
#   ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3e use_fake_hardware:=false
# Then run this launch file, or run it in a combined launch with the above.
# Movement commands on /move_group/goal (PoseStamped) are planned by MoveIt and
# executed on the hardware via the driver's joint trajectory controller.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    declared_arguments = [
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

    velocity_scaling = LaunchConfiguration("velocity_scaling")
    planning_group = LaunchConfiguration("planning_group")

    ur3e_controller_node = Node(
        package="ur3e_controller",
        executable="ur_node",
        name="ur3e_controller",
        output="screen",
        parameters=[
            {"use_sim_time": False},
            {"velocity_scaling": velocity_scaling},
            {"planning_group": planning_group},
        ],
    )

    return LaunchDescription(declared_arguments + [ur3e_controller_node])
