#!/usr/bin/env python3
"""
RealSense .bag file viewer for Mac.
Plays back recorded RGB and depth streams from an Intel RealSense .bag file.
"""

import argparse
import sys

try:
    import pyrealsense2 as rs
except ImportError:
    try:
        import pyrealsense2_macosx as rs
    except ImportError:
        print("Error: RealSense Python bindings not found.")
        print("On Mac, install with: pip install pyrealsense2-macosx")
        print("On Linux/Windows: pip install pyrealsense2")
        sys.exit(1)

try:
    import numpy as np
    import cv2
except ImportError:
    print("Error: numpy and opencv-python are required.")
    print("Install with: pip install numpy opencv-python")
    sys.exit(1)


def colorize_depth(depth_frame, clip_max: float = None):
    """Convert depth frame to colormap for visualization."""
    depth_image = np.asanyarray(depth_frame.get_data())
    if clip_max is not None and clip_max > 0:
        depth_image = np.clip(depth_image, 0, clip_max)
    depth_colormap = cv2.applyColorMap(
        cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
    )
    return depth_colormap


def main():
    parser = argparse.ArgumentParser(description="View RealSense .bag recording")
    parser.add_argument(
        "bag_file",
        nargs="?",
        default=None,
        help="Path to the .bag file (e.g. recording.bag)",
    )
    parser.add_argument(
        "--depth-clip",
        type=float,
        default=4000.0,
        help="Max depth in mm for colormap (default: 4000)",
    )
    parser.add_argument(
        "--no-depth",
        action="store_true",
        help="Only show RGB stream (useful if bag has no depth)",
    )
    args = parser.parse_args()

    if not args.bag_file:
        parser.print_help()
        print("\nExample: python realsense_viewer.py recording.bag")
        sys.exit(1)

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(args.bag_file, repeat_playback=False)

    # Enable streams that are in the bag (we don't set resolution; bag defines it)
    config.enable_stream(rs.stream.color)
    if not args.no_depth:
        config.enable_stream(rs.stream.depth)

    try:
        profile = pipeline.start(config)
        device = profile.get_device()
        playback = device.as_playback()
        playback.set_real_time(False)  # Play as fast as we can read

        use_align = not args.no_depth
        align = rs.align(rs.stream.color) if use_align else None

        print("Playing .bag file. Press 'q' to quit, 's' to save a snapshot.")
        print("Close the window or press Ctrl+C to exit.")

        frame_count = 0
        while True:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=1000)
            except RuntimeError:
                print("End of recording or timeout.")
                break

            if use_align and align:
                frames = align.process(frames)
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame() if not args.no_depth else None

            if not color_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

            if depth_frame and not args.no_depth:
                depth_colormap = colorize_depth(depth_frame, clip_max=args.depth_clip)
                # Stack side by side: RGB | Depth
                h, w = color_image.shape[:2]
                depth_resized = cv2.resize(depth_colormap, (w, h))
                display = np.hstack((color_image, depth_resized))
            else:
                display = color_image

            cv2.putText(
                display,
                f"Frame {frame_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )
            cv2.imshow("RealSense .bag playback", display)
            frame_count += 1

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                h, w = display.shape[:2]

                # crop left half (RGB image)
                rgb_only = display[:, : w // 2]

                out_name = f"snapshot_{frame_count}.png"
                cv2.imwrite(out_name, rgb_only)

                print(f"Saved RGB snapshot {out_name}")

        pipeline.stop()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
