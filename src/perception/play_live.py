"""
play_live.py
------------
Live mode for Jenga perception from a RealSense camera via ROS topics.

Usage
-----
    python3 play_live.py [--setup] [--no-ros-nodes]
"""
import argparse

from play_runtime import run_subscribe
from search_area_setup import run_search_area_setup_subscribe

COLOR_TOPIC = "/camera/camera/color/image_raw"
DEPTH_TOPIC = [
    "/camera/camera/aligned_depth_to_color/image_raw",
    "/camera/aligned_depth_to_color/image_raw",
    "/camera/camera/depth/image_rect_raw",
    "/camera/depth/image_rect_raw",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Live Jenga perception from ROS camera topics.")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Open search-area calibration (live view + sliders, Set/Reset/Cancel).",
    )
    args = parser.parse_args()

    if args.setup:
        run_search_area_setup_subscribe(COLOR_TOPIC, DEPTH_TOPIC)
    else:
        run_subscribe(COLOR_TOPIC, DEPTH_TOPIC)


if __name__ == "__main__":
    main()
