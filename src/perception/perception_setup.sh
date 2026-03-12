print("Perception setup")

source /opt/ros/humble/setup.bash

sudo apt install ros-humble-librealsense2*
sudo apt install ros-humble-realsense2-*

ros2 pkg list | grep realsense



#opencv-python>=4.5.0
