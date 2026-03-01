import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # 1. Path fix: Point to 'urdf' and 'srdf' subfolders explicitly
    moveit_config = (
        MoveItConfigsBuilder("ur", package_name="ur_moveit_config")
        .robot_description(
            file_path="urdf/ur.urdf.xacro", # Path is urdf/ not config/
            mappings={
                "ur_type": "ur3",
                "safety_limits": "true",
                "safety_pos_margin": "0.15",
                "safety_k_position": "20",
            },
        )
        .robot_description_semantic(file_path="srdf/ur.srdf") # Path is srdf/ not config/
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    # 2. Start MoveGroup
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    # 3. Robot State Publisher (Calculates the TF tree)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description],
    )

    # 4. Joint State Publisher (Fake controller for simulation)
    # This allows MoveIt to 'move' the robot in RViz without real hardware
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[{"source_list": ["/move_group/fake_controller_joint_states"]}],
    )

    # 5. Start RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
    )

    # 6. Static TF for the world
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "world", "base_link"],
    )

    # 7. YOUR C++ NODE
    ur3_cpp_node = Node(
        package="ur3_moveit_mixed",
        executable="ur3_cpp_node",
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        static_tf,
        move_group_node,
        rviz_node,
        ur3_cpp_node,
    ])