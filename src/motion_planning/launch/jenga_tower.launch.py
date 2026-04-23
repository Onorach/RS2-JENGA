# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""Run the Jenga tower pose sequencer (after motion_planning + robot + MoveIt if used)."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg = "motion_planning"

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "single_layer",
                default_value="false",
                description="If true, build only the first layer (3 blocks). If false, build total_layers (default 6).",
            ),
            DeclareLaunchArgument(
                "total_layers",
                default_value="6",
                description="Number of layers when single_layer is false (clamped to 1–6).",
            ),
            DeclareLaunchArgument(
                "tower_layout_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare(pkg), "config", "jenga_tower_layout.yaml"]
                ),
                description="YAML file with tower_origin, pickups, and spacing.",
            ),
            DeclareLaunchArgument(
                "status_topic",
                default_value="rmrc_status",
                description=(
                    "Planner status JSON topic (executions_completed). Use rmrc_status for "
                    "planner:=rmrc, moveit_status for planner:=moveit, moveit_cartesian_status "
                    "for planner:=moveit_cartesian."
                ),
            ),
            DeclareLaunchArgument(
                "goal_pose_topic",
                default_value="goal_pose",
                description="PoseStamped topic the planner subscribes to (relative name → /goal_pose).",
            ),
            DeclareLaunchArgument(
                "goal_completion_timeout_sec",
                default_value="180.0",
                description="Seconds to wait for each motion step before aborting.",
            ),
            DeclareLaunchArgument(
                "start_delay_sec",
                default_value="2.0",
                description="Spin delay before first goal (allow planner discovery).",
            ),
            DeclareLaunchArgument(
                "pause_after_pick_sec",
                default_value="0.0",
                description="Optional dwell after each pick pose for gripper close.",
            ),
            DeclareLaunchArgument(
                "pause_after_place_sec",
                default_value="0.0",
                description="Optional dwell after each place pose for gripper open.",
            ),
            Node(
                package=pkg,
                executable="jenga_tower_node",
                name="jenga_tower_node",
                output="screen",
                parameters=[
                    {
                        "single_layer": LaunchConfiguration("single_layer"),
                        "total_layers": LaunchConfiguration("total_layers"),
                        "tower_layout_file": LaunchConfiguration("tower_layout_file"),
                        "status_topic": LaunchConfiguration("status_topic"),
                        "goal_pose_topic": LaunchConfiguration("goal_pose_topic"),
                        "goal_completion_timeout_sec": LaunchConfiguration(
                            "goal_completion_timeout_sec"
                        ),
                        "start_delay_sec": LaunchConfiguration("start_delay_sec"),
                        "pause_after_pick_sec": LaunchConfiguration("pause_after_pick_sec"),
                        "pause_after_place_sec": LaunchConfiguration("pause_after_place_sec"),
                    }
                ],
            ),
        ]
    )
