"""
Jenga Block Edge Detection
--------------------------
Looks for a PNG file in INPUT_FOLDER, detects block edges,
and displays 4 key processing steps in separate windows.

Usage:
    python jenga_edge_detect.py                        # auto-picks first PNG in camera_files/
    python jenga_edge_detect.py snapshot_26.png        # specific PNG in camera_files/
    python jenga_edge_detect.py 20260310_125846.bag    # .bag file in camera_files/rgbd_raw/
"""

import cv2
import numpy as np
import os
import sys
import glob
from pathlib import Path

INPUT_FOLDER    = str(Path(__file__).resolve().parent / "camera_files" / "snapshots")
RGBD_RAW_FOLDER = str(Path(__file__).resolve().parent / "camera_files" / "rgbd_raw")

MAX_DISPLAY_DIM = 1920


def load_image(folder: str, image_path: str | None = None) -> np.ndarray:
    if image_path is None:
        pattern = os.path.join(folder, "*.png")
        files = sorted(glob.glob(pattern))
        if not files:
            sys.exit(f"[ERROR] No PNG files found in: {folder}")
        path = files[0]
    else:
        candidate = Path(image_path)
        suffix = candidate.suffix.lower()

        if suffix == ".bag":
            resolved = Path(RGBD_RAW_FOLDER) / candidate.name
            if not resolved.exists():
                sys.exit(f"[ERROR] .bag file not found: {resolved}")
            return load_bag(str(resolved))
        else:
            if not candidate.is_absolute() and candidate.parent == Path("."):
                candidate = Path(folder) / candidate.name
            path = str(candidate)

    print(f"[INFO] Loading: {path}")
    img = cv2.imread(path)
    if img is None:
        sys.exit(f"[ERROR] cv2 could not read: {path}")
    h, w = img.shape[:2]
    print(f"[INFO] Loaded image resolution: {w}x{h}")
    return img


def load_bag(bag_path: str) -> np.ndarray:
    """Extract the first colour frame from a RealSense .bag file."""
    try:
        import pyrealsense2 as rs
    except ImportError:
        sys.exit("[ERROR] pyrealsense2 not installed. Run: pip install pyrealsense2")

    print(f"[INFO] Loading .bag: {bag_path}")
    pipeline_rs = rs.pipeline()
    config = rs.config()
    # Let the bag decide its own stream format — don't force resolution
    config.enable_device_from_file(bag_path, repeat_playback=False)

    # Probe what streams are actually recorded in the bag before starting
    try:
        pipeline_profile = config.resolve(rs.pipeline_wrapper(pipeline_rs))
        device = pipeline_profile.get_device()
        print(f"[INFO] Device from bag: {device.get_info(rs.camera_info.name)}")
        for sensor in device.query_sensors():
            for profile in sensor.get_stream_profiles():
                if profile.stream_type() == rs.stream.color:
                    vp = profile.as_video_stream_profile()
                    print(f"[INFO] Colour stream available: {vp.width()}x{vp.height()} "
                          f"@ {vp.fps()}fps  fmt={profile.format()}")
    except Exception as e:
        print(f"[WARN] Could not probe bag streams: {e}")

    pipeline_rs.start(config)
    try:
        for _ in range(60):
            frames = pipeline_rs.wait_for_frames(timeout_ms=2000)
            colour_frame = frames.get_color_frame()
            if colour_frame:
                img = np.asanyarray(colour_frame.get_data())
                h, w = img.shape[:2]
                print(f"[INFO] Extracted colour frame {frames.get_frame_number()} — {w}x{h}")
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                return img
    finally:
        pipeline_rs.stop()

    sys.exit("[ERROR] No colour frame found in .bag file.")


def mask_table(edges: np.ndarray) -> np.ndarray:
    h, w = edges.shape
    row_sums = np.sum(edges, axis=1) / 255
    search_start = int(h * 0.4)
    smoothed = np.convolve(row_sums[search_start:], np.ones(15) / 15, mode='same')
    threshold = np.max(smoothed) * 0.35
    candidates = np.where(smoothed > threshold)[0]
    if len(candidates) == 0:
        return edges
    tower_base = search_start + int(candidates[-1]) + 20
    tower_base = min(tower_base, h - 1)
    masked = edges.copy()
    masked[tower_base:, :] = 0
    return masked


def pipeline(bgr: np.ndarray) -> dict[str, np.ndarray]:
    h, w = bgr.shape[:2]
    print(f"[INFO] Processing at: {w}x{h}")

    scale = min(1.0, MAX_DISPLAY_DIM / max(h, w))
    if scale < 1.0:
        resized = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        print(f"[INFO] Resized to: {resized.shape[1]}x{resized.shape[0]}")
    else:
        resized = bgr.copy()

    grey = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(grey)

    bilateral = cv2.bilateralFilter(enhanced, d=15, sigmaColor=90, sigmaSpace=90)

    edges = cv2.Canny(bilateral, threshold1=25, threshold2=70)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)

    edges_masked = mask_table(edges_dilated)

    overlay = resized.copy()
    overlay[edges_masked > 0] = (0, 0, 255)

    return {
        "1. Original":                      resized,
        "2. Enhanced (CLAHE + Bilateral)":  cv2.cvtColor(bilateral, cv2.COLOR_GRAY2BGR),
        "3. Canny Edges (masked)":          cv2.cvtColor(edges_masked, cv2.COLOR_GRAY2BGR),
        "4. Edges on Image":                overlay,
    }


def show_steps(steps: dict[str, np.ndarray]) -> None:
    tile_w, tile_h = 960, 540
    for idx, (title, img) in enumerate(steps.items()):
        display = cv2.resize(img, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
        col = idx % 2
        row = idx // 2
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.moveWindow(title, col * (tile_w + 10), row * (tile_h + 40))
        cv2.resizeWindow(title, tile_w, tile_h)
        cv2.imshow(title, display)

    print("[INFO] Press any key inside a window to close all.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main() -> None:
    image_path = sys.argv[1] if len(sys.argv) >= 2 else None
    bgr = load_image(INPUT_FOLDER, image_path=image_path)
    steps = pipeline(bgr)
    show_steps(steps)


if __name__ == "__main__":
    main()