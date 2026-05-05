"""
Launch the MTC extraction servers (side + middle).

Start MoveIt separately (move_group must be running with ExecuteTaskSolutionCapability).
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    mtc_velocity_yaml = PathJoinSubstitution(
        [FindPackageShare("mtc_jenga_servers"), "config", "mtc_velocity_scaling.yaml"]
    )
    which_arg = DeclareLaunchArgument(
        "which",
        default_value="side",
        description="Which extract server to launch: side|middle|both",
    )
    arm_group_arg = DeclareLaunchArgument("arm_group", default_value="ur_onrobot_manipulator")
    hand_group_arg = DeclareLaunchArgument("hand_group", default_value="ur_onrobot_gripper")
    gripper_tcp_arg = DeclareLaunchArgument("gripper_tcp", default_value="gripper_tcp")
    max_vel_arg = DeclareLaunchArgument(
        "max_velocity_scaling_factor",
        default_value="0.1",
        description="Sync with mtc_jenga_servers/config/mtc_velocity_scaling.yaml",
    )
    max_acc_arg = DeclareLaunchArgument(
        "max_acceleration_scaling_factor",
        default_value="0.1",
        description="Sync with mtc_jenga_servers/config/mtc_velocity_scaling.yaml",
    )

    common_params = [
        mtc_velocity_yaml,
        {
            "max_velocity_scaling_factor": LaunchConfiguration("max_velocity_scaling_factor"),
            "max_acceleration_scaling_factor": LaunchConfiguration(
                "max_acceleration_scaling_factor"
            ),
            "arm_group": LaunchConfiguration("arm_group"),
            "hand_group": LaunchConfiguration("hand_group"),
            "gripper_tcp": LaunchConfiguration("gripper_tcp"),
        },
    ]

    side = Node(
        package="mtc_jenga_servers",
        executable="mtc_extract_side_block_server",
        name="mtc_extract_side_block_server",
        output="screen",
        condition=IfCondition(
            PythonExpression(
                [
                    "('",
                    LaunchConfiguration("which"),
                    "' == 'side') or ('",
                    LaunchConfiguration("which"),
                    "' == 'both')",
                ]
            )
        ),
        parameters=common_params,
    )

    middle = Node(
        package="mtc_jenga_servers",
        executable="mtc_extract_middle_block_server",
        name="mtc_extract_middle_block_server",
        output="screen",
        condition=IfCondition(
            PythonExpression(
                [
                    "('",
                    LaunchConfiguration("which"),
                    "' == 'middle') or ('",
                    LaunchConfiguration("which"),
                    "' == 'both')",
                ]
            )
        ),
        parameters=common_params,
    )

    return LaunchDescription(
        [
            which_arg,
            arm_group_arg,
            hand_group_arg,
            gripper_tcp_arg,
            max_vel_arg,
            max_acc_arg,
            side,
            middle,
        ]
    )

