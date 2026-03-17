"""
Usage:
    python3 play_rgbd.py <bag file name>  — will used specified file
    python3 play_rgbd.py                  — will use live camera
    
Keyboard shortcuts:
    SPACE — pause / resume
    Q     — quit
"""

import sys
import cv2
import numpy as np
import pyrealsense2 as rs
import os
from datetime import datetime

# Edge detector node
from jenga_perception_edges import JengaPerceptionNode

# ------------------------------------------------------------------------------
# Camera configuration
# ------------------------------------------------------------------------------

# Each entry: (name, RealSense option, boost)
# boost in [-1, 1] mapped from min → default → max.
camera_configuration_settings = [
    ("sharpness", rs.option.sharpness, 1.0),
    ("saturation", rs.option.saturation, 0.25),
    ("gamma",      rs.option.gamma,      0.0),
    ("contrast",   rs.option.contrast,   0.0),
    ("brightness", rs.option.brightness, 0.0),
]


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def _boost_from_default(rng, boost: float) -> float:
    """
    Return a value based on boost in [-1, 1]:
      -1 → min, 0 → default, +1 → max.
    """
    boost = float(boost)
    boost = max(-1.0, min(1.0, boost))

    if boost >= 0.0:
        target = rng.default + boost * (rng.max - rng.default)
    else:
        target = rng.default + boost * (rng.default - rng.min)

    if getattr(rng, "step", 0) and rng.step > 0:
        target = round((target - rng.min) / rng.step) * rng.step + rng.min
    return float(max(rng.min, min(rng.max, target)))


def _set_to_default_then_value(sensor, opt, boost: float):
    """Reset option to default, then apply boosted value."""
    if not sensor.supports(opt):
        return
    rng = sensor.get_option_range(opt)
    # "Clear" any persisted value by returning to default first.
    sensor.set_option(opt, float(rng.default))
    sensor.set_option(opt, _boost_from_default(rng, boost))


def _get_rgb_sensor(device):
    for s in device.query_sensors():
        try:
            if s.get_info(rs.camera_info.name) == "RGB Camera":
                return s
        except Exception:
            continue
    return None


def _apply_all_camera_settings(sensor, settings):
    for _name, opt, boost in settings:
        _set_to_default_then_value(sensor, opt, boost)


def _apply_one_camera_setting(sensor, settings, idx: int):
    name, opt, boost = settings[idx]
    _set_to_default_then_value(sensor, opt, boost)
    print(f"[camera] {name} boost={boost:.2f}")

# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------

def main():
    bag_path = sys.argv[1] if len(sys.argv) > 1 else None
    if bag_path is not None:
        bag_path = os.path.join(os.path.dirname(__file__), 'camera_files', 'rgbd_raw', bag_path)
    live_mode = bag_path is None

    # --- Set up RealSense pipeline ---
    pipeline = rs.pipeline()
    config = rs.config()

    # --- Runtime state ---
    color_sensor = None
    selected_setting_idx = 0
    recorder = None  # rs.recorder for live .bag recording

    # ===================================
    # LIVE MODE
    # ===================================
    if live_mode:
        print("Mode: LIVE (no bag file specified)")

        # Streams
        config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

        # Preconfigure recording to a .bag file (we'll pause it immediately)
        base_dir = os.path.join(os.path.dirname(__file__), "camera_files", "rgbd_raw")
        os.makedirs(base_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bag_out = os.path.join(base_dir, f"live_{ts}.bag")
        config.enable_record_to_file(bag_out)

        # Start camera + recorder
        try:
            profile = pipeline.start(config)
        except Exception as e:
            print(f"Failed to start pipeline: {e}")
            print("Make sure pyrealsense2 is installed: pip install pyrealsense2")
            sys.exit(1)

        try:
            device = profile.get_device()
            recorder = device.as_recorder()
            recorder.pause()  # start with recording paused
            print(f"[record] Ready to record to {bag_out} (press R to start/stop)")
        except Exception as e:
            print(f"[record] Warning: recorder not available: {e}")

        # Apply camera settings (sharpness/saturation/etc)
        try:
            if 'device' not in locals():
                device = profile.get_device()
            color_sensor = _get_rgb_sensor(device)
            if color_sensor is not None:
                # Lock auto-exposure / auto-white-balance off for stability, if supported
                if color_sensor.supports(rs.option.enable_auto_exposure):
                    color_sensor.set_option(rs.option.enable_auto_exposure, 0.0)
                if color_sensor.supports(rs.option.enable_auto_white_balance):
                    color_sensor.set_option(rs.option.enable_auto_white_balance, 1.0)

                _apply_all_camera_settings(color_sensor, camera_configuration_settings)
        except Exception as e:
            print(f"Warning: failed to configure colour sensor options: {e}")

        print("Controls: \n - Left/Right: select camera option \n - Up/Down: change boost by 0.25\n - R: start/stop .bag recording\n - SPACE: pause\n - Q: quit")

    # ===================================
    # PLAYBACK MODE 
    # ===================================
    else:
        print(f"Mode: PLAYBACK (bag={bag_path})")

        # Streams from bag
        rs.config.enable_device_from_file(config, bag_path, repeat_playback=True)
        config.enable_stream(rs.stream.color)
        config.enable_stream(rs.stream.depth)

        # Start playback
        try:
            profile = pipeline.start(config)
        except Exception as e:
            print(f"Failed to start pipeline: {e}")
            sys.exit(1)

        # Playback speed
        playback = profile.get_device().as_playback()
        playback.set_real_time(False)   # play bag as fast as possible

    # --- Set up perception node ---
    node = JengaPerceptionNode()

    # --- Align depth to colour frame ---
    align = rs.align(rs.stream.color)

    paused = False
    recording = False

    try:
        while True:
            if paused:
                key = cv2.waitKey(100)
                if (key & 0xFF) == ord('q'):
                    break
                elif (key & 0xFF) == ord(' '):
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
            color_bgr = np.asanyarray(color_frame.get_data())
            # Live stream uses BGR8. Recorded bags from our live session also store BGR8,
            # so playback uses data as-is. (Older bags recorded as RGB8 would need
            # cv2.cvtColor(..., cv2.COLOR_RGB2BGR) here.)

            # Run perception on colour frame and show (cropped to search region + margin)
            state = node.process_frame(color_bgr)
            node.show(color_bgr, state)

            key = cv2.waitKey(1)

            # Arrow-key live tuning (only meaningful for live camera)
            if live_mode and color_sensor is not None:
                # OpenCV arrow key codes vary by backend; handle common Linux codes
                LEFT_KEYS = {81, 2424832}
                RIGHT_KEYS = {83, 2555904}
                UP_KEYS = {82, 2490368}
                DOWN_KEYS = {84, 2621440}

                if key in LEFT_KEYS:
                    selected_setting_idx = (selected_setting_idx - 1) % len(camera_configuration_settings)
                    name, _opt, boost = camera_configuration_settings[selected_setting_idx]
                    print(f"[camera] selected: {name} (boost={boost:.2f})")
                elif key in RIGHT_KEYS:
                    selected_setting_idx = (selected_setting_idx + 1) % len(camera_configuration_settings)
                    name, _opt, boost = camera_configuration_settings[selected_setting_idx]
                    print(f"[camera] selected: {name} (boost={boost:.2f})")
                elif key in UP_KEYS or key in DOWN_KEYS:
                    name, opt, boost = camera_configuration_settings[selected_setting_idx]
                    step = 0.25
                    if key in UP_KEYS:
                        boost = min(1.0, boost + step)
                    else:
                        boost = max(-1.0, boost - step)
                    camera_configuration_settings[selected_setting_idx] = (name, opt, boost)
                    try:
                        _apply_one_camera_setting(color_sensor, camera_configuration_settings, selected_setting_idx)
                    except Exception as e:
                        print(f"Warning: failed to set {name}: {e}")

            # Recording toggle (live mode only, .bag via recorder pause/resume)
            if live_mode and recorder is not None and (key & 0xFF) == ord('r'):
                try:
                    if not recording:
                        recorder.resume()
                        recording = True
                        print("[record] STARTED (.bag) — press R again to pause")
                    else:
                        recorder.pause()
                        recording = False
                        print("[record] PAUSED (.bag) — press R again to resume")
                except Exception as e:
                    print(f"[record] Warning: failed to toggle recorder: {e}")

            if (key & 0xFF) == ord('q'):
                break
            elif (key & 0xFF) == ord(' '):
                paused = True
                print("Paused.")

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()