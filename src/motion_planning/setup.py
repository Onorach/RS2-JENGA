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
        (os.path.join("share", package_name, "meshes"), glob("meshes/*")),
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
            "jenga_tower_node = motion_planning.jenga_tower_node:main",
            "pose_goal_node = motion_planning.pose_goal_node:main",
            "exclusion_zones_node = motion_planning.exclusion_zones_loader:main",
            "jenga_blocks_scene = motion_planning.jenga_blocks_scene:main",
            "rmrc_planning_node = motion_planning.rmrc_planning_node:main",
            "moveit_cartesian_node = motion_planning.moveit_cartesian_node:main",
            "test_rmrc_pose = motion_planning.tests.test_rmrc_pose:main",
            "test_planner_pose = motion_planning.tests.test_planner_pose:main",
            "test_mtc_pick_place = motion_planning.tests.test_mtc_pick_place:main",
            "test_mtc_extract_side = motion_planning.tests.test_mtc_extract_side:main",
            "test_mtc_extract_middle = motion_planning.tests.test_mtc_extract_middle:main",
            "test_mtc_extract_middle_protruded = motion_planning.tests.test_mtc_extract_middle_protruded:main",
            "test_mtc_probe_block = motion_planning.tests.test_mtc_probe_block:main",
            "mtc_action_client = motion_planning.mtc_action_client:main",
            "jenga_tower_mtc_sequencer = motion_planning.jenga_tower_mtc_sequencer:main",
            "jenga_extract_middle_to_top_sequencer = motion_planning.jenga_extract_middle_to_top_sequencer:main",
            "robot_gui = motion_planning.robot_gui:main",
            "robot_state_bridge_node = motion_planning.robot_state_bridge_node:main",
        ],
    },
)
