import os
import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # 1. Path fix: Point to 'urdf' and 'srdf' subfolders explicitly
    ur_description_path = get_package_share_directory('ur_description')
    moveit_config_path = get_package_share_directory('ur_moveit_config')
    
    rviz_config_file = os.path.join(
        get_package_share_directory('ur3_moveit_mixed'),
        'config',
        'moveit.rviz',
    )

    # Launch arguments
    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Start RViz with the MoveIt MotionPlanning plugin.",
    )

    moveit_config = (
        MoveItConfigsBuilder("ur", package_name="ur_moveit_config")
        .robot_description(
            file_path=os.path.join(ur_description_path, "urdf", "ur.urdf.xacro"),
            mappings={
                "ur_type": "ur3",
                "name": "ur",
                "safety_limits": "true",
                "safety_pos_margin": "0.15",
                "safety_k_position": "20",
                # Now using the correct variable name: ur_description_path
                "joint_limit_params": os.path.join(ur_description_path, "config", "ur3", "joint_limits.yaml"),
                "kinematics_params": os.path.join(ur_description_path, "config", "ur3", "default_kinematics.yaml"),
                "physical_params": os.path.join(ur_description_path, "config", "ur3", "physical_parameters.yaml"),
                "visual_params": os.path.join(ur_description_path, "config", "ur3", "visual_parameters.yaml"),
            },
        )
        .robot_description_semantic(
            file_path=os.path.join(moveit_config_path, "srdf", "ur.srdf.xacro"),
            mappings={"ur_type": "ur3", "name": "ur"}
        )
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .to_moveit_configs()
    )

    # Define the fake controller configuration
    fake_controllers_yaml = os.path.join(
        get_package_share_directory('ur3_moveit_mixed'),
        'config',
        'fake_controllers.yaml'
    )
    with open(fake_controllers_yaml, 'r') as f:
        fake_controllers = yaml.safe_load(f)

    # 2. Start MoveGroup
    move_group_node = Node(
        package="moveit_ros_move_group",
    executable="move_group",
    output="screen",
    parameters=[
            moveit_config.to_dict(),
            {"moveit_manage_controllers": True},
            {"moveit_controller_manager": 
                "moveit_fake_controller_manager/MoveItFakeControllerManager"},
            fake_controllers,
        ],
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
        parameters=[{
            "source_list": ["/fake_arm_controller/joint_states"]
        }],
    )

    # 5. Start RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[moveit_config.to_dict()],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
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

    return LaunchDescription(
        [
            use_rviz_arg,
            robot_state_publisher,
            joint_state_publisher,
            static_tf,
            move_group_node,
            rviz_node,
            ur3_cpp_node,
        ]
    )