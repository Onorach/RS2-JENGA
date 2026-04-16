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
    # Live camera (opens RealSense via pyrealsense2 — exclusive with another process)
    python play2.py

    # Same image topic as `ros2 launch realsense2_camera rs_launch.py` — no USB open here
    python play2.py --subscribe

    # Bag file (searched in camera_files/rgbd_raw/ and camera_files/rgbd_large/)
    python play2.py recording.bag
"""

from __future__ import annotations

import argparse
import os
import sys
import threading
from typing import Callable, Optional

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
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from cv_bridge import CvBridge
    from colour_identification import ColourIdentificationNode
    from box_percentages import BoxPercentagesNode
    from colour_blobs import ColourBlobsNode
    _ROS_AVAILABLE = True
except ImportError:
    Node = object  # type: ignore[misc, assignment]
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
# ROS image source (subscribe-only mode; no RealSense USB open)
# ============================================================================

if _ROS_AVAILABLE:

    class _Play2ImageNode(Node):
        """Latest colour frame from sensor_msgs/Image (bgr8 or rgb8)."""

        def __init__(self, color_topic: str) -> None:
            super().__init__("play2_image_bridge")
            self._bridge = CvBridge()
            self._lock = threading.Lock()
            self._bgr: Optional[np.ndarray] = None
            self.create_subscription(Image, color_topic, self._cb, 10)
            self.get_logger().info(f"play2: subscribed to {color_topic}")

        def _cb(self, msg: Image) -> None:
            try:
                enc = (msg.encoding or "").lower()
                if enc == "rgb8":
                    rgb = self._bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
                    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                else:
                    bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            except Exception as e:  # noqa: BLE001 — cv_bridge reports decode issues
                self.get_logger().warning(f"cv_bridge: {e}")
                return
            with self._lock:
                self._bgr = bgr

        def get_bgr(self) -> Optional[np.ndarray]:
            with self._lock:
                if self._bgr is None:
                    return None
                return self._bgr.copy()


# ============================================================================
# Main loop
# ============================================================================

def _run_loop(get_bgr: Callable[[], Optional[np.ndarray]]) -> None:
    """
    Processing + OpenCV windows. *get_bgr* returns the latest full colour frame (BGR)
    or None if not ready yet.
    """
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
        bgr = get_bgr()
        if bgr is None:
            if (cv2.waitKey(10) & 0xFF) == ord("q"):
                break
            continue
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


def _run(pipeline: rs.pipeline) -> None:
    def get_bgr() -> Optional[np.ndarray]:
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        color_frame = frames.get_color_frame()
        if color_frame is None:
            return None
        return np.asanyarray(color_frame.get_data())

    _run_loop(get_bgr)


def _run_subscribe(color_topic: str, ros_nodes: bool) -> None:
    """Live processing from a ROS colour topic only (RealSense driver owns USB elsewhere)."""
    assert _ROS_AVAILABLE
    rclpy.init()
    executor = SingleThreadedExecutor()
    bridge = _Play2ImageNode(color_topic)
    executor.add_node(bridge)
    all_nodes: list = [bridge]

    if ros_nodes:
        extra = [
            ColourIdentificationNode(color_topic),
            BoxPercentagesNode(color_topic),
            ColourBlobsNode(color_topic),
            DepthAnalysisNode(color_topic),
        ]
        for n in extra:
            executor.add_node(n)
        all_nodes.extend(extra)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    try:
        _run_loop(bridge.get_bgr)
    finally:
        executor.shutdown()
        for n in all_nodes:
            n.destroy_node()
        rclpy.shutdown()


# ============================================================================
# ROS2 spin (optional — launches nodes alongside the CV loop)
# ============================================================================

def _run_with_ros(pipeline: rs.pipeline, color_topic: str) -> None:
    """
    Initialise ROS2 publisher nodes on a background executor while the OpenCV loop
    reads frames from pyrealsense2 in the main thread.

    The nodes subscribe to *color_topic* (same stream the driver can publish when run
    separately). Default matches ``realsense2_camera`` namespaced topics.
    """
    rclpy.init()
    executor = SingleThreadedExecutor()
    nodes = [
        ColourIdentificationNode(color_topic),
        BoxPercentagesNode(color_topic),
        ColourBlobsNode(color_topic),
        DepthAnalysisNode(color_topic),
    ]
    for n in nodes:
        executor.add_node(n)

    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    try:
        _run(pipeline)   # blocks until Q pressed
    finally:
        executor.shutdown()
        for n in nodes:
            n.destroy_node()
        rclpy.shutdown()


# ============================================================================
# Entry point
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Jenga perception from RealSense or ROS image topic.")
    parser.add_argument(
        "bag",
        nargs="?",
        help="Optional .bag file for playback (pyrealsense2; not used with --subscribe).",
    )
    parser.add_argument(
        "--subscribe",
        action="store_true",
        help="Do not open the RealSense USB; subscribe to --color-topic (use while realsense2_camera runs).",
    )
    parser.add_argument(
        "--color-topic",
        default="/camera/camera/color/image_raw",
        help="sensor_msgs/Image topic for colour (bgr8 or rgb8).",
    )
    parser.add_argument(
        "--ros-nodes",
        action="store_true",
        help="With --subscribe, also run /jenga/* publisher nodes alongside the OpenCV windows.",
    )
    args = parser.parse_args()

    bag_arg = args.bag
    if args.subscribe:
        if bag_arg is not None:
            print("Cannot combine --subscribe with a bag file.", file=sys.stderr)
            sys.exit(1)
        if not _ROS_AVAILABLE:
            print("ROS 2 (rclpy, cv_bridge, sensor_msgs) required for --subscribe.", file=sys.stderr)
            sys.exit(1)
        _run_subscribe(args.color_topic, args.ros_nodes)
        cv2.destroyAllWindows()
        return

    live = bag_arg is None
    bag_path = _resolve_bag(bag_arg) if bag_arg else None

    pipeline = _start_pipeline(live, bag_path)

    try:
        if _ROS_AVAILABLE:
            _run_with_ros(pipeline, args.color_topic)
        else:
            _run(pipeline)
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()