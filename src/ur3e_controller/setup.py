from setuptools import find_packages, setup
import os
from glob import glob

package_name = "rs2_jenga"

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
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="RS2-JENGA",
    maintainer_email="user@example.com",
    description="Interface to send joint trajectory commands to UR3e (simulation and hardware).",
    license="BSD-3-Clause",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "move_ur3e_demo = ur3e_controller.demo_node:main",
            "initials_demo = ur3e_controller.demo_node:main",
            "pose_goal_node = ur3e_controller.pose_goal_node:main",
            "exclusion_zones_node = ur3e_controller.exclusion_zones_loader:main",
            "robot_gui = ur3e_controller.robot_gui:main",
            "estop_node = ur3e_controller.estop_node:main",
        ],
    },
)
