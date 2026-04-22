from setuptools import find_packages, setup
import os
from glob import glob

package_name = "motion_planning"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools", "numpy"],
    zip_safe=True,
    maintainer="RS2-JENGA",
    maintainer_email="user@example.com",
    description="Motion planning for UR3e: RMRC planner, MoveIt interface, pose goals, and exclusion zones.",
    license="BSD-3-Clause",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pose_goal_node = motion_planning.pose_goal_node:main",
            "exclusion_zones_node = motion_planning.exclusion_zones_loader:main",
            "rmrc_planning_node = motion_planning.rmrc_planning_node:main",
            "moveit_cartesian_node = motion_planning.moveit_cartesian_node:main",
            "test_rmrc_pose = motion_planning.test_rmrc_pose:main",
            "test_planner_pose = motion_planning.test_planner_pose:main",
            "robot_gui = motion_planning.robot_gui:main",
        ],
    },
)
