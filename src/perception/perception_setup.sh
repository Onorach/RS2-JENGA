#!/bin/bash

echo "Perception setup"

# Source ROS 2
source /opt/ros/humble/setup.bash

echo "Updating apt"
sudo apt update

echo "Installing Intel RealSense SDK"
sudo apt install -y librealsense2-dev librealsense2-utils librealsense2-dkms

echo "Installing ROS2 RealSense packages"
sudo apt install -y ros-humble-librealsense2* ros-humble-realsense2-* ros-humble-realsense2-camera realsense2-camera

echo "Installing Python RealSense bindings"
python3 -m pip install --upgrade pip
python3 -m pip install pyrealsense2

echo "Listing installed ROS2 RealSense packages"
ros2 pkg list | grep realsense2

echo "Setup complete."