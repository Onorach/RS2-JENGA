"""
play.py
-------
Main entry point.  Reads from a RealSense camera (live) or a .bag file and
runs all three processing nodes:

    colour_identification  — per-pixel HSV classification → colour frame
    box_percentages        — colour % per grid cell → debug window
    colour_blobs           — blob detection + quad fitting → debug window

When ROS2 is available each processor runs as a proper Node and frames are
passed via the in-process executor (no network overhead — same process).
When ROS2 is not available they run as plain Python objects.

Windows
-------
    "Jenga live"        — raw camera feed with search-ROI rectangle and grid
    "Colour frame"      — per-pixel classification (colour_identification)
    "Box percentages"   — quad cells coloured by pixel class (box_percentages)
    "Colour blobs"      — detected block quads overlaid (colour_blobs)

Keyboard
--------
    Q  — quit

Usage
-----
    # Live camera
    python play.py

    # Bag file (searched in camera_files/rgbd_raw/ and camera_files/rgbd_large/)
    python play.py recording.bag
"""

from __future__ import annotations

import os
import sys
from typing import Optional

import cv2
import numpy as np
import pyrealsense2 as rs

# ── local modules ──────────────────────────────────────────────────────────
from colour_identification import (
    classify_frame, compute_roi,
    COLOUR_BGR, DIVIDE_LINE,
)
from box_percentages import (
    compute_percentages, build_debug_image as build_pct_debug,
    GRID_CELLS,
)
from colour_blobs import (
    find_blobs, build_debug_image as build_blob_debug,
)

from depth_analysis import DepthAnalysisNode


# ── optional ROS2 ──────────────────────────────────────────────────────────
try:
    import rclpy
    from rclpy.executors import SingleThreadedExecutor
    from colour_identification import ColourIdentificationNode
    from box_percentages import BoxPercentagesNode
    from colour_blobs import ColourBlobsNode
    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False

# ============================================================================
# Grid overlay — drawn on the live window
# ============================================================================

# 3 × N array of corner points (full-frame coords).
# None = not yet measured.  Fill in all rows for a complete grid.
GRID_CORNERS: list[list[Optional[tuple[int,int]]]] = [
    [(664, 197),  (920, 217),  (1237, 215)],
    [(669, 282),  (916, 315),  (1228, 297)],
    [None, None, None],
    [None, None, None],
    [None, None, None],
    [None, None, None],
    [None, None, None],
]


def _draw_grid(disp: np.ndarray, offset_x: int, offset_y: int) -> None:
    """Draw grid lines and corner dots onto *disp* (a cropped sub-image)."""

    def valid(p) -> bool:
        return isinstance(p, (tuple, list)) and len(p) == 2

    rows = len(GRID_CORNERS)
    cols = len(GRID_CORNERS[0]) if rows else 0

    # Horizontal lines
    for r in range(rows):
        for c in range(cols - 1):
            p1, p2 = GRID_CORNERS[r][c], GRID_CORNERS[r][c + 1]
            if not (valid(p1) and valid(p2)):
                continue
            cv2.line(disp,
                     (p1[0] - offset_x, p1[1] - offset_y),
                     (p2[0] - offset_x, p2[1] - offset_y),
                     (0, 255, 0), 1)

    # Vertical lines
    for c in range(cols):
        for r in range(rows - 1):
            p1, p2 = GRID_CORNERS[r][c], GRID_CORNERS[r + 1][c]
            if not (valid(p1) and valid(p2)):
                continue
            cv2.line(disp,
                     (p1[0] - offset_x, p1[1] - offset_y),
                     (p2[0] - offset_x, p2[1] - offset_y),
                     (255, 100, 0), 1)

    # Corner dots
    h, w = disp.shape[:2]
    for r in range(rows):
        for c in range(cols):
            p = GRID_CORNERS[r][c]
            if not valid(p):
                continue
            lx, ly = p[0] - offset_x, p[1] - offset_y
            if 0 <= lx < w and 0 <= ly < h:
                cv2.circle(disp, (lx, ly), 5, (255, 255, 255), -1)


# ============================================================================
# Camera / bag helpers
# ============================================================================

def _resolve_bag(path: str) -> str:
    base = os.path.dirname(__file__)
    for candidate in [
        path,
        os.path.join(base, "camera_files", "rgbd_raw",   path),
        os.path.join(base, "camera_files", "rgbd_large", path),
    ]:
        if os.path.exists(candidate):
            return candidate
    return os.path.join(base, "camera_files", "rgbd_raw", path)


def _start_pipeline(live: bool, bag_path: Optional[str]) -> rs.pipeline:
    pipeline = rs.pipeline()
    config   = rs.config()

    if live:
        config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
    else:
        rs.config.enable_device_from_file(config, bag_path, repeat_playback=True)
        config.enable_stream(rs.stream.color)

    try:
        pipeline.start(config)
    except Exception:
        if live:
            raise
        pipeline = rs.pipeline()
        config2  = rs.config()
        rs.config.enable_device_from_file(config2, bag_path, repeat_playback=True)
        pipeline.start(config2)

    return pipeline


# ============================================================================
# Main loop
# ============================================================================

def _run(pipeline: rs.pipeline) -> None:
    roi_margin = 0.10
    frame_n    = 0

    # Window names
    WIN_LIVE  = "Jenga live"
    WIN_COL   = "Colour frame"
    WIN_PCT   = "Box percentages"
    WIN_BLOB  = "Colour blobs"

    for win in (WIN_LIVE, WIN_COL, WIN_PCT, WIN_BLOB):
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    while True:
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        color_frame = frames.get_color_frame()
        if color_frame is None:
            continue

        bgr = np.asanyarray(color_frame.get_data())
        ih, iw = bgr.shape[:2]
        frame_n += 1

        # ── ROI crop for the live window ───────────────────────────────────
        rx, ry, rw, rh = compute_roi(iw, ih)
        mx = int(rw * roi_margin)
        my = int(rh * roi_margin)
        dx1 = max(0, rx - mx)
        dy1 = max(0, ry - my)
        dx2 = min(iw, rx + rw + mx)
        dy2 = min(ih, ry + rh + my)

        live_disp = bgr[dy1:dy2, dx1:dx2].copy()

        # Search ROI rectangle (cyan)
        cv2.rectangle(live_disp,
                      (rx - dx1, ry - dy1),
                      (rx + rw - dx1, ry + rh - dy1),
                      (255, 255, 0), 2)

        # Grid lines
        _draw_grid(live_disp, dx1, dy1)

        # Divide line
        (fx1, fy1), (fx2, fy2) = DIVIDE_LINE
        cv2.line(live_disp,
                 (fx1 - dx1, fy1 - dy1),
                 (fx2 - dx1, fy2 - dy1),
                 (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow(WIN_LIVE, live_disp)

        # ── colour identification (every frame — cheap) ────────────────────
        colour_img, _ = classify_frame(bgr)
        cv2.imshow(WIN_COL, colour_img)

        # ── box percentages (every 30 frames) ─────────────────────────────
        if frame_n % 30 == 0:
            results   = compute_percentages(bgr)
            pct_debug = build_pct_debug(bgr, results)
            cv2.imshow(WIN_PCT, pct_debug)

        # ── colour blobs (every 10 frames — moderate cost) ─────────────────
        if frame_n % 10 == 0:
            blobs, roi_x, roi_y = find_blobs(bgr)
            blob_debug = build_blob_debug(bgr, blobs, roi_x, roi_y)
            cv2.imshow(WIN_BLOB, blob_debug)

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


# ============================================================================
# ROS2 spin (optional — launches nodes alongside the CV loop)
# ============================================================================

def _run_with_ros(pipeline: rs.pipeline) -> None:
    """
    Initialise ROS2 nodes alongside the OpenCV loop.
    The nodes receive frames via their /camera/color/image_raw subscription
    (published by the RealSense ROS2 driver running separately).
    The OpenCV windows are still driven directly here for low-latency display.
    """
    rclpy.init()
    executor = SingleThreadedExecutor()
    nodes = [
        ColourIdentificationNode(),
        BoxPercentagesNode(),
        ColourBlobsNode(),
        DepthAnalysisNode(),
    ]
    for n in nodes:
        executor.add_node(n)

    try:
        _run(pipeline)   # blocks until Q pressed
        # Spin briefly to flush any pending callbacks
        executor.spin_once(timeout_sec=0.0)
    finally:
        for n in nodes:
            n.destroy_node()
        rclpy.shutdown()


# ============================================================================
# Entry point
# ============================================================================

def main() -> None:
    bag_arg  = sys.argv[1] if len(sys.argv) > 1 else None
    live     = bag_arg is None
    bag_path = _resolve_bag(bag_arg) if bag_arg else None

    pipeline = _start_pipeline(live, bag_path)

    try:
        if _ROS_AVAILABLE:
            _run_with_ros(pipeline)
        else:
            _run(pipeline)
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()