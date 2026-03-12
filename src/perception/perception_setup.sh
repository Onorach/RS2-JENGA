#!/bin/bash

echo "Perception setup"

source /opt/ros/humble/setup.bash

echo "Installing librealsense2"
sudo apt install ros-humble-librealsense2*
sudo apt install ros-humble-realsense2-*

echo "Listing realsense packages"
ros2 pkg list | grep realsense



#opencv-python>=4.5.0
