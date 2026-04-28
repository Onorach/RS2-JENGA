
"""
Full stack: UR+OnRobot driver, MoveIt, and motion_planning (MTC + exclusion zones + e-stop).

Start order: ``start_robot`` and ``ur_onrobot_moveit`` at launch; ``motion_planning`` is delayed
so ``move_group`` is usually ready before ``mtc_pick_place_server`` starts.

Example (fake hardware, no RViz on driver; RViz from MoveIt)::

    ros2 launch motion_planning ur_onrobot_mtc_bringup.launch.py

Example (real robot IP, scaled trajectory + world TF for MTC)::

    ros2 launch motion_planning ur_onrobot_mtc_bringup.launch.py \\
        use_fake_hardware:=false robot_ip:=192.168.56.101 \\
        publish_world_to_base_tf:=true base_height:=0.0 base_yaw:=0.0
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("ur_type", default_value="ur3e", description="UR model."),
            DeclareLaunchArgument(
                "onrobot_type", default_value="rg2", description="OnRobot gripper type."
            ),
            DeclareLaunchArgument(
                "robot_ip",
                default_value="192.168.56.101",
                description="UR controller IP (used when not fake hardware).",
            ),
            DeclareLaunchArgument(
                "use_fake_hardware",
                default_value="true",
                description="If true, use ros2_control fake hardware.",
            ),
            DeclareLaunchArgument(
                "launch_rviz_robot",
                default_value="false",
                description="RViz in ur_onrobot_control (usually off when MoveIt RViz is on).",
            ),
            DeclareLaunchArgument(
                "launch_rviz_moveit",
                default_value="true",
                description="RViz from ur_onrobot_moveit_config.",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Set true when using Gazebo or another sim clock source.",
            ),
            DeclareLaunchArgument(
                "launch_servo",
                default_value="false",
                description="Start MoveIt Servo (optional; default off for MTC Jenga).",
            ),
            DeclareLaunchArgument(
                "motion_planning_delay_sec",
                default_value="12.0",
                description="Wait before starting motion_planning (move_group + controllers).",
            ),
            DeclareLaunchArgument(
                "mtc_server_mode",
                default_value="single_pose",
                description="MTC server: single_pose = jenga_pick_place action; "
                "paired_pose = two /goal_pose = pick+place.",
            ),
            DeclareLaunchArgument(
                "joint_trajectory_action",
                default_value="/scaled_joint_trajectory_controller/follow_joint_trajectory",
                description="FollowJointTrajectory action for e-stop; match active arm controller.",
            ),
            DeclareLaunchArgument(
                "publish_world_to_base_tf",
                default_value="false",
                description="Publish static TF world->base_link. Keep false when using "
                "ur_onrobot_control (robot_state_publisher already publishes world->base_link "
                "from the URDF). Set true only for standalone MTC testing without the driver.",
            ),
            DeclareLaunchArgument(
                "base_height",
                default_value="0.0",
                description="Z (m) for static world->base_link when publish_world_to_base_tf is true.",
            ),
            DeclareLaunchArgument(
                "base_yaw",
                default_value="0.0",
                description="Yaw (rad) for static world->base_link when publish_world_to_base_tf is true.",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("ur_onrobot_control"),
                        "/launch",
                        "/start_robot.launch.py",
                    ]
                ),
                launch_arguments={
                    "ur_type": LaunchConfiguration("ur_type"),
                    "onrobot_type": LaunchConfiguration("onrobot_type"),
                    "robot_ip": LaunchConfiguration("robot_ip"),
                    "use_fake_hardware": LaunchConfiguration("use_fake_hardware"),
                    "launch_rviz": LaunchConfiguration("launch_rviz_robot"),
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("ur_onrobot_moveit_config"),
                        "/launch",
                        "/ur_onrobot_moveit.launch.py",
                    ]
                ),
                launch_arguments={
                    "ur_type": LaunchConfiguration("ur_type"),
                    "onrobot_type": LaunchConfiguration("onrobot_type"),
                    "use_sim_time": LaunchConfiguration("use_sim_time"),
                    "launch_rviz": LaunchConfiguration("launch_rviz_moveit"),
                    "launch_servo": LaunchConfiguration("launch_servo"),
                }.items(),
            ),
            TimerAction(
                period=LaunchConfiguration("motion_planning_delay_sec"),
                actions=[
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            [
                                FindPackageShare("motion_planning"),
                                "/launch",
                                "/motion_planning.launch.py",
                            ]
                        ),
                        launch_arguments=_motion_launch_args(),
                    )
                ],
            ),
        ]
    )


def _motion_launch_args():
    # Omit exclusion_zones_file so motion_planning uses its default (ur3e_workspace.yaml);
    # override with a separate motion_planning launch if needed.
    return {
        "planner": "mtc",
        "mtc_server_mode": LaunchConfiguration("mtc_server_mode"),
        "joint_trajectory_action": LaunchConfiguration("joint_trajectory_action"),
        "publish_world_to_base_tf": LaunchConfiguration("publish_world_to_base_tf"),
        "base_height": LaunchConfiguration("base_height"),
        "base_yaw": LaunchConfiguration("base_yaw"),
    }.items()
