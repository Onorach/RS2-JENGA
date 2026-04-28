# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Launch MoveIt + motion planning for the real UR3e hardware.

Run the UR robot driver in a separate terminal FIRST:

    ros2 launch ur_robot_driver ur_control.launch.py \
        ur_type:=ur3e robot_ip:=<ROBOT_IP> launch_rviz:=false

Then start external control on the teach pendant, and run this launch:

    ros2 launch ur3e_controller ur3e_hw_moveit.launch.py planner:=moveit

planner:=rmrc             → RMRC planning (no MoveIt move_group needed).
planner:=moveit           → MoveIt OMPL joint-space planning.
planner:=moveit_cartesian → MoveIt Cartesian straight-line + OMPL fallback.

Both MoveIt planners start the move_group node automatically.
On real hardware the driver uses scaled_joint_trajectory_controller
(respects the teach-pendant speed slider); this launch overrides the
joint_trajectory_action accordingly.
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
        default_value="moveit",
        choices=["rmrc", "moveit", "moveit_cartesian", "mtc"],
        description=(
            "Planning backend: 'rmrc' (DIY RMRC, no MoveIt), 'moveit' (OMPL), "
            "'moveit_cartesian' (Cartesian straight-line + OMPL fallback), "
            "'mtc' (MoveIt Task Constructor pick-and-place)."
        ),
    )

    launch_rviz_arg = DeclareLaunchArgument(
        "launch_rviz",
        default_value="true",
        description="Launch RViz with MoveIt motion-planning plugin.",
    )

    base_height_arg = DeclareLaunchArgument(
        "base_height",
        default_value="0.0",
        description=(
            "Z offset (metres) from world to base_link. On real hardware "
            "the driver places base_link at the robot base, so world and "
            "base_link are co-located (0.0)."
        ),
    )

    base_yaw_arg = DeclareLaunchArgument(
        "base_yaw",
        default_value="1.5707963",
        description=(
            "Yaw rotation (radians) for world->base_link static TF. "
            "Default -pi/2 matches the sim workspace URDF. Flip sign "
            "if the hardware robot is rotated in the opposite direction."
        ),
    )

    # MoveIt move_group — started for 'moveit' and 'moveit_cartesian' planners.
    # The UR driver already publishes robot_description and runs the controller
    # manager, so we only need move_group here (no fake hardware, no sim time).
    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("ur_moveit_config"), "/launch", "/ur_moveit.launch.py"]
        ),
        condition=IfCondition(
            PythonExpression(["'", LaunchConfiguration("planner"), "' != 'rmrc'"])
        ),
        launch_arguments={
            "ur_type": "ur3e",
            "use_sim_time": "false",
            "launch_rviz": LaunchConfiguration("launch_rviz"),
            "use_fake_hardware": "false",
            "description_package": "ur_description",
            "description_file": "ur.urdf.xacro",
        }.items(),
    )

    # Motion planning nodes (pose_goal_node, moveit_cartesian_node, or
    # rmrc_planning_node, plus exclusion_zones_node and estop_node).
    # Override joint_trajectory_action to the scaled controller used by the
    # UR driver on real hardware.  The driver's URDF (ur_description) does
    # not include a 'world' frame, so we publish a static world->base_link
    # TF at the configured base_height.
    motion_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [FindPackageShare("motion_planning"), "/launch", "/motion_planning.launch.py"]
        ),
        launch_arguments={
            "planner": LaunchConfiguration("planner"),
            "joint_trajectory_action": "/scaled_joint_trajectory_controller/follow_joint_trajectory",
            "publish_world_to_base_tf": "true",
            "base_height": LaunchConfiguration("base_height"),
            "base_yaw": LaunchConfiguration("base_yaw"),
        }.items(),
    )

    return LaunchDescription([
        planner_arg,
        launch_rviz_arg,
        base_height_arg,
        base_yaw_arg,
        moveit_launch,
        motion_launch,
    ])
