"""
Simplified Jenga Block Edge Detection
-------------------------------------
Uses only Gaussian blur + Canny edge detection.
Displays 4 key processing steps.

Usage:
    python jenga_simple_edge.py                        # auto-picks first PNG
    python jenga_simple_edge.py snapshot_26.png        # specific file
    python jenga_simple_edge.py 20260310_125846.bag     # .bag file
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
    """Extract first colour frame from RealSense .bag file"""
    try:
        import pyrealsense2 as rs
    except ImportError:
        sys.exit("[ERROR] pyrealsense2 not installed. Run: pip install pyrealsense2")

    print(f"[INFO] Loading .bag: {bag_path}")
    pipeline_rs = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(bag_path, repeat_playback=False)

    pipeline_rs.start(config)
    try:
        for _ in range(60):
            frames = pipeline_rs.wait_for_frames(timeout_ms=2000)
            colour_frame = frames.get_color_frame()
            if colour_frame:
                img = np.asanyarray(colour_frame.get_data())
                h, w = img.shape[:2]
                print(f"[INFO] Extracted colour frame — {w}x{h}")
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                return img
    finally:
        pipeline_rs.stop()

    sys.exit("[ERROR] No colour frame found in .bag file.")


def pipeline(bgr: np.ndarray) -> dict[str, np.ndarray]:
    h, w = bgr.shape[:2]
    print(f"[INFO] Processing at: {w}x{h}")

    # Optional modest resize — helps with speed & noise
    scale = min(1.0, MAX_DISPLAY_DIM / max(h, w))
    if scale < 1.0:
        resized = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        print(f"[INFO] Resized to: {resized.shape[1]}x{resized.shape[0]}")
    else:
        resized = bgr.copy()

    # Convert to grayscale
    grey = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # === The simple classic pipeline ===
    # 1. Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(grey, (5, 5), sigmaX=1.5)

    # 2. Canny edge detection
    #    — you can tune these two thresholds depending on your lighting / contrast
    edges = cv2.Canny(blurred, threshold1=40, threshold2=120)

    # Create colour versions for display
    overlay = resized.copy()
    overlay[edges > 0] = (0, 0, 255)           # red edges

    return {
        "1. Original (resized)":           resized,
        "2. Grayscale + Gaussian Blur":    cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR),
        "3. Canny Edges":                  cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR),
        "4. Edges on Image":               overlay,
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