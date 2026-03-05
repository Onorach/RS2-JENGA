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
    ur_description_path = get_package_share_directory("ur_description")
    moveit_config_path = get_package_share_directory("ur_moveit_config")

    rviz_config_file = os.path.join(
        get_package_share_directory("ur3_moveit_mixed"),
        "config",
        "moveit.rviz",
    )

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
                "joint_limit_params": os.path.join(
                    ur_description_path, "config", "ur3", "joint_limits.yaml"
                ),
                "kinematics_params": os.path.join(
                    ur_description_path, "config", "ur3", "default_kinematics.yaml"
                ),
                "physical_params": os.path.join(
                    ur_description_path, "config", "ur3", "physical_parameters.yaml"
                ),
                "visual_params": os.path.join(
                    ur_description_path, "config", "ur3", "visual_parameters.yaml"
                ),
            },
        )
        .robot_description_semantic(
            file_path=os.path.join(moveit_config_path, "srdf", "ur.srdf.xacro"),
            mappings={"ur_type": "ur3", "name": "ur"},
        )
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .to_moveit_configs()
    )

    # Hardware controllers that should match the controllers exposed by ur_robot_driver.
    hardware_controllers_yaml = os.path.join(
        get_package_share_directory("ur3_moveit_mixed"),
        "config",
        "hardware_controllers.yaml",
    )
    with open(hardware_controllers_yaml, "r") as f:
        hardware_controllers = yaml.safe_load(f)

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            hardware_controllers,
        ],
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[moveit_config.to_dict()],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )

    return LaunchDescription(
        [
            use_rviz_arg,
            robot_state_publisher,
            move_group_node,
            rviz_node,
        ]
    )

