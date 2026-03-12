#!/bin/bash

# Source ROS2
source /opt/ros/humble/setup.bash

# Launch RealSense camera
ros2 launch realsense2_camera rs_launch.py \
enable_color:=true \
enable_depth:=true \
align_depth.enable:=true \
pointcloud.enable:=true &

# Give the camera time to start
sleep 3

# Start RViz
rviz2