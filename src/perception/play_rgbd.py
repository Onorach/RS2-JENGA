"""
play_rgbd.py
------------
Plays back a RealSense .bag file and displays the RGBD frames in a side-by-side window or plays the live camera.

Usage
-----
    python3 play_rgbd.py <path_to_bag> 

    e.g.
    python3 play_rgbd.py ~/src/RS2-JENGA/src/perception/camera_files/rgbd_raw/1.bag

    or without a bag file, python3 play_rgbd.py will start the live camera.
    
Keyboard shortcuts (OpenCV window must be focused):
    R     — set current frame as reference
    SPACE — pause / resume
    Q     — quit

Requirements
------------
    pip install pyrealsense2 opencv-python numpy
"""

import sys
import cv2
import numpy as np
import pyrealsense2 as rs

# Import perception pipeline from same directory
from jenga_perception_edges import JengaPerceptionNode


def main():
    bag_path = sys.argv[1] if len(sys.argv) > 1 else None
    live_mode = bag_path is None

    # --- Set up RealSense pipeline ---
    pipeline = rs.pipeline()
    config = rs.config()

    if live_mode:
        # Live camera — stream at 640x480 30fps
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        print("No bag file provided — starting live camera.")
    else:
        # Bag file playback
        rs.config.enable_device_from_file(config, bag_path, repeat_playback=True)
        config.enable_stream(rs.stream.color)
        config.enable_stream(rs.stream.depth)
        print(f"Opened bag: {bag_path}")

    try:
        profile = pipeline.start(config)
    except Exception as e:
        print(f"Failed to start pipeline: {e}")
        print("Make sure pyrealsense2 is installed: pip install pyrealsense2")
        sys.exit(1)

    if not live_mode:
        playback = profile.get_device().as_playback()
        playback.set_real_time(False)   # play bag as fast as possible

    print("Press R to set reference frame, SPACE to pause, Q to quit.")

    # --- Set up perception node ---
    node = JengaPerceptionNode()

    # --- Align depth to colour frame ---
    align = rs.align(rs.stream.color)

    paused = False

    try:
        while True:
            if paused:
                key = cv2.waitKey(100) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord(' '):
                    paused = False
                continue

            # Get next frameset
            try:
                frames = pipeline.wait_for_frames(timeout_ms=1000)
            except RuntimeError:
                print("End of bag file.")
                break

            # Align depth to colour
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()

            if not color_frame:
                continue

            # Convert to numpy
            color_image = np.asanyarray(color_frame.get_data())
            color_bgr = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

            # Run perception on colour frame
            state = node.process_frame(color_bgr)

            # Print missing blocks to terminal
            if state.missing_blocks:
                missing = [(b.layer, b.index) for b in state.missing_blocks]
                print(f"Missing blocks: {missing}")

            # Show visualisation
            vis = node.visualise(color_bgr, state)

            # Optionally overlay depth as a colourmap in a second window
            if depth_frame:
                depth_image = np.asanyarray(depth_frame.get_data())
                depth_colourmap = cv2.applyColorMap(
                    cv2.convertScaleAbs(depth_image, alpha=0.03),
                    cv2.COLORMAP_JET
                )
                cv2.imshow("Depth", depth_colourmap)

            cv2.imshow("Jenga Perception", vis)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                node.set_reference(color_bgr, state)
                print("Reference frame set.")
            elif key == ord(' '):
                paused = True
                print("Paused.")

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()