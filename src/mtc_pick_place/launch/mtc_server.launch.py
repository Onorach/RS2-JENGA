
"""Run the MTC pick/place action server (C++). Start MoveIt separately (e.g. ur3e_hw_moveit).

Default parameters target ``ur_onrobot`` SRDF (``ur_onrobot_manipulator``, ``ur_onrobot_gripper``,
``gripper_tcp``). If you use stock ``ur_moveit_config`` only, override *arm_group* / *ee_link* and
use ``mode:=single_pose`` (MoveGroup to pose); the full MTC pick/place path needs matching SRDF
with gripper groups and open/closed states.
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
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "mode",
                default_value="single_pose",
                description="single_pose: /goal_pose uses MoveGroup; paired_pose: two /goal_pose = pick+place MTC",
            ),
            DeclareLaunchArgument(
                "status_topic",
                default_value="mtc_status",
                description="JSON status topic for test_planner_pose",
            ),
            DeclareLaunchArgument(
                "max_velocity_scaling_factor",
                default_value="0.1",
                description="Keep default in sync with mtc_pick_place/config/mtc_velocity_scaling.yaml",
            ),
            DeclareLaunchArgument(
                "max_acceleration_scaling_factor",
                default_value="0.1",
                description="Keep default in sync with mtc_pick_place/config/mtc_velocity_scaling.yaml",
            ),
            Node(
                package="mtc_pick_place",
                executable="mtc_pick_place_server",
                name="mtc_pick_place_server",
                output="screen",
                respawn=True,
                parameters=[
                    mtc_velocity_yaml,
                    {
                        "max_velocity_scaling_factor": LaunchConfiguration(
                            "max_velocity_scaling_factor"
                        ),
                        "max_acceleration_scaling_factor": LaunchConfiguration(
                            "max_acceleration_scaling_factor"
                        ),
                        "mode": LaunchConfiguration("mode"),
                        "status_topic": LaunchConfiguration("status_topic"),
                        "arm_group": "ur_onrobot_manipulator",
                        "hand_group": "ur_onrobot_gripper",
                        "hand_frame": "gripper_tcp",
                        "ee_link": "gripper_tcp",
                    },
                ],
            ),
        ]
    )
