"""
play_live.py
------------
Live mode for Jenga perception from a RealSense camera via ROS topics.

Usage
-----
    python3 play_live.py [--no-ros-nodes]
"""
from play_runtime import run_subscribe

COLOR_TOPIC = "/camera/camera/color/image_raw"
DEPTH_TOPIC = "/camera/camera/aligned_depth_to_color/image_raw"


def main() -> None:

    run_subscribe(COLOR_TOPIC, DEPTH_TOPIC)


if __name__ == "__main__":
    main()
