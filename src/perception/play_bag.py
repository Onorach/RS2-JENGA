"""
play_bag.py
-----------
Bag playback mode for Jenga perception.

Usage
-----
    python3 play_bag.py <bag_file> [--setup]
"""

import argparse
import os
import time

import cv2
import numpy as np
import pyrealsense2 as rs

from play_runtime import run_with_pipeline
from setup.search_area_setup import run_search_area_setup


def _resolve_bag(path: str) -> str:
    base = os.path.dirname(__file__)
    for candidate in (
        path,
        os.path.join(base, "camera_files/rgbd_raw", path),
    ):
        if os.path.exists(candidate):
            return candidate
    return os.path.join(base, "camera_files/rgbd_raw", path)


def _start_pipeline(bag_path: str, *, real_time: bool) -> rs.pipeline:
    pipeline = rs.pipeline()
    config = rs.config()

    rs.config.enable_device_from_file(config, bag_path, repeat_playback=True)
    config.enable_stream(rs.stream.color)
    config.enable_stream(rs.stream.depth)

    profile = pipeline.start(config)

    playback = profile.get_device().as_playback()
    playback.set_real_time(real_time)

    return pipeline


def _pipeline_frame_reader(pipeline, target_fps: float | None = None):
    """Return a get_frame_pair() callable compatible with setup/runtime loops."""
    align = rs.align(rs.stream.color)
    frame_interval_s = (1.0 / float(target_fps)) if target_fps and target_fps > 0 else None
    last_frame_time_s: float | None = None

    def get_frame_pair():
        nonlocal last_frame_time_s
        if frame_interval_s is not None and last_frame_time_s is not None:
            now = time.monotonic()
            sleep_s = frame_interval_s - (now - last_frame_time_s)
            if sleep_s > 0:
                time.sleep(sleep_s)
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        aligned = align.process(frames)
        color_frame = aligned.get_color_frame()
        depth_frame = aligned.get_depth_frame()
        if color_frame is None or not color_frame:
            return None, None
        if frame_interval_s is not None:
            last_frame_time_s = time.monotonic()

        frame = np.asanyarray(color_frame.get_data())
        frame_format = str(color_frame.profile.format()).lower()
        bgr = (
            cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if "rgb8" in frame_format and "bgr8" not in frame_format
            else frame
        )

        if depth_frame is None or not depth_frame:
            depth_mm = None
        else:
            try:
                depth_mm = np.asanyarray(depth_frame.get_data())
            except RuntimeError:
                depth_mm = None

        return bgr, depth_mm

    return get_frame_pair



def main() -> None:
    parser = argparse.ArgumentParser(description="Jenga perception from a RealSense bag.")
    parser.add_argument("bag", help="Path or filename of the .bag recording.")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run search-area, colour, tower mask, and depth confirm calibration using the bag.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Optional playback cap for bag processing/display (frames per second).",
    )
   
    args = parser.parse_args()

    target_fps = None if args.fps is None or args.fps <= 0 else float(args.fps)
    # Default behaviour: real-time playback from recorded timestamps.
    # When an FPS cap is requested, disable RealSense real-time pacing and pace in Python.
    pipeline = _start_pipeline(_resolve_bag(args.bag), real_time=(target_fps is None))
    
    try:
        if args.setup:
            run_search_area_setup(_pipeline_frame_reader(pipeline, target_fps=target_fps))
        else:
            run_with_pipeline(pipeline, target_fps=target_fps)
    finally:
        pipeline.stop()


if __name__ == "__main__":
    main()
