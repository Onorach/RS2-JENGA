"""
play_bag.py
-----------
Bag playback mode for Jenga perception.

Usage
-----
    python3 play_bag.py <bag_file>
"""

import argparse
import os

import cv2
import pyrealsense2 as rs

from play_runtime import run_with_pipeline


def _resolve_bag(path: str) -> str:
    base = os.path.dirname(__file__)
    for candidate in (
        path,
        os.path.join(base, "camera_files", "rgbd_raw", path),
        os.path.join(base, "camera_files", "rgbd_large", path),
    ):
        if os.path.exists(candidate):
            return candidate
    return os.path.join(base, "camera_files", "rgbd_raw", path)


def _start_pipeline(bag_path: str) -> rs.pipeline:
    pipeline = rs.pipeline()
    config = rs.config()

    rs.config.enable_device_from_file(config, bag_path, repeat_playback=True)
    config.enable_stream(rs.stream.color)

    profile = pipeline.start(config)

    playback = profile.get_device().as_playback()
    playback.set_real_time(False)

    return pipeline



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", help="Path or filename of the .bag recording.")
   
    args = parser.parse_args()

    pipeline = _start_pipeline(_resolve_bag(args.bag))
    
    try:
        run_with_pipeline(pipeline)
    finally:
        pipeline.stop()


if __name__ == "__main__":
    main()