#!/usr/bin/env python3
"""
Simple RealSense .bag RGB viewer (with optional depth view)
- Looks in camera_files/rgbd_raw/
- Auto-picks first .bag if no argument given
- q = quit,  s = save RGB snapshot
- Use --depth or -d to show color | depth side-by-side
"""

import sys
from pathlib import Path
import cv2
import numpy as np

try:
    import pyrealsense2 as rs
except ImportError:
    print("Error: pyrealsense2 not found.")
    print("Install with: pip install pyrealsense2")
    sys.exit(1)


def colorize_depth(depth_frame, clip_max=4000.0):
    """Convert depth frame to JET colormap for visualization."""
    depth_image = np.asanyarray(depth_frame.get_data())
    depth_image = np.clip(depth_image, 0, clip_max)
    depth_colormap = cv2.applyColorMap(
        cv2.convertScaleAbs(depth_image, alpha=0.03),
        cv2.COLORMAP_JET
    )
    return depth_colormap


def main():
    import argparse

    parser = argparse.ArgumentParser(description="View RealSense .bag file (RGB + optional depth)")
    parser.add_argument("bag_file", nargs="?", default=None,
                        help="Filename of .bag in camera_files/rgbd_raw/ (e.g. 3.bag)")
    parser.add_argument("--depth", "-d", action="store_true",
                        help="Show color image | depth colormap side-by-side")
    args = parser.parse_args()

    # Where .bag files live
    BAG_DIR = Path(__file__).resolve().parent / "camera_files" / "rgbd_raw"

    if not BAG_DIR.is_dir():
        print(f"Error: Directory not found: {BAG_DIR}")
        sys.exit(1)

    # Get filename from command line or auto-select
    if args.bag_file:
        bag_path = (BAG_DIR / args.bag_file).resolve()
        if not bag_path.is_file():
            print(f"Error: File not found: {bag_path}")
            print(f"(looked in: {BAG_DIR})")
            sys.exit(1)
    else:
        bag_files = sorted(BAG_DIR.glob("*.bag"))
        if not bag_files:
            print(f"Error: No .bag files found in {BAG_DIR}")
            sys.exit(1)
        bag_path = bag_files[0]
        print(f"No file specified → using: {bag_path.name}")

    print(f"Opening: {bag_path}")
    if args.depth:
        print("Showing: RGB | Depth colormap")
    else:
        print("Showing: RGB only  (use --depth to show depth too)")

    # ────────────────────────────────────────
    #  Playback setup
    # ────────────────────────────────────────
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    config.enable_stream(rs.stream.color)
    if args.depth:
        config.enable_stream(rs.stream.depth)

    try:
        profile = pipeline.start(config)
    except RuntimeError as e:
        print(f"Failed to open bag file: {e}")
        sys.exit(1)

    print("Controls:  q = quit,  s = save RGB snapshot")

    cv2.namedWindow("RealSense Playback", cv2.WINDOW_NORMAL)

    frame_count = 0

    while True:
        try:
            frames = pipeline.wait_for_frames(timeout_ms=500)
        except RuntimeError:
            print("Reached end of bag file.")
            break

        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

        if args.depth:
            depth_frame = frames.get_depth_frame()
            if depth_frame:
                depth_colormap = colorize_depth(depth_frame, clip_max=4000.0)
                # Resize depth to match color if needed
                h, w = color_image.shape[:2]
                depth_resized = cv2.resize(depth_colormap, (w, h))
                display = np.hstack((color_image, depth_resized))
            else:
                display = color_image  # fallback if depth missing in this frame
        else:
            display = color_image

        cv2.imshow("RealSense Playback", display)
        frame_count += 1

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Quit requested.")
            break

        if key == ord('s'):
            save_dir = Path(__file__).resolve().parent / "camera_files" / "snapshots"
            save_dir.mkdir(parents=True, exist_ok=True)

            if args.depth:
                # Save only left half (RGB)
                h, w = display.shape[:2]
                rgb_only = display[:, :w//2]
                save_img = rgb_only
            else:
                save_img = display

            filename = f"{bag_path.stem}_frame_{frame_count:03d}.png"
            save_path = save_dir / filename

            cv2.imwrite(str(save_path), save_img)
            print(f"Saved RGB snapshot: {save_path}")

    pipeline.stop()
    cv2.destroyAllWindows()
    print("Done.")


if __name__ == "__main__":
    main()