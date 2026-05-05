"""Shared launch defaults for velocity/acceleration scaling (moveit_cartesian + MTC)."""

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

# Keep in sync with mtc_jenga_servers/config/mtc_velocity_scaling.yaml
DEFAULT_MAX_VELOCITY_SCALING = "0.1"
DEFAULT_MAX_ACCELERATION_SCALING = "0.1"


def declare_mtc_velocity_scaling_arguments():
    """Declare launch args used by moveit_cartesian and MTC C++ servers."""
    return [
        DeclareLaunchArgument(
            "max_velocity_scaling_factor",
            default_value=DEFAULT_MAX_VELOCITY_SCALING,
            description=(
                "Scale (0,1] for max joint velocity: moveit_cartesian node and MTC "
                "servers (overrides values from mtc_jenga_servers/config/mtc_velocity_scaling.yaml "
                "when passed explicitly; default matches that file)."
            ),
        ),
        DeclareLaunchArgument(
            "max_acceleration_scaling_factor",
            default_value=DEFAULT_MAX_ACCELERATION_SCALING,
            description=(
                "Scale (0,1] for max joint acceleration: moveit_cartesian and MTC servers."
            ),
        ),
    ]


def mtc_velocity_scaling_ros_parameters():
    """Parameter dict to merge after the shared YAML so launch CLI overrides apply."""
    return {
        "max_velocity_scaling_factor": LaunchConfiguration("max_velocity_scaling_factor"),
        "max_acceleration_scaling_factor": LaunchConfiguration(
            "max_acceleration_scaling_factor"
        ),
    }
