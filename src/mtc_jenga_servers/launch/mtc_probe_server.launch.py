"""
Launch the MTC probe action server (push/pull test).

Start MoveIt separately (move_group must be running with ExecuteTaskSolutionCapability).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    mtc_velocity_yaml = PathJoinSubstitution(
        [FindPackageShare("mtc_pick_place"), "config", "mtc_velocity_scaling.yaml"]
    )
    arm_group_arg = DeclareLaunchArgument("arm_group", default_value="ur_onrobot_manipulator")
    gripper_tcp_arg = DeclareLaunchArgument("gripper_tcp", default_value="gripper_tcp")
    max_vel_arg = DeclareLaunchArgument(
        "max_velocity_scaling_factor",
        default_value="0.1",
        description="Sync with mtc_pick_place/config/mtc_velocity_scaling.yaml",
    )
    max_acc_arg = DeclareLaunchArgument(
        "max_acceleration_scaling_factor",
        default_value="0.1",
        description="Sync with mtc_pick_place/config/mtc_velocity_scaling.yaml",
    )

    node = Node(
        package="mtc_pick_place",
        executable="mtc_probe_block_server",
        name="mtc_probe_block_server",
        output="screen",
        parameters=[
            mtc_velocity_yaml,
            {
                "max_velocity_scaling_factor": LaunchConfiguration("max_velocity_scaling_factor"),
                "max_acceleration_scaling_factor": LaunchConfiguration(
                    "max_acceleration_scaling_factor"
                ),
                "arm_group": LaunchConfiguration("arm_group"),
                "gripper_tcp": LaunchConfiguration("gripper_tcp"),
            },
        ],
    )

    return LaunchDescription([arm_group_arg, gripper_tcp_arg, max_vel_arg, max_acc_arg, node])

