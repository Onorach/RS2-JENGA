"""
depth_analysis.py
-----------------
ROS2 node that fuses the per-pixel colour labels from colour_identification
with the RealSense depth frame to produce:

  - A per-pixel depth map restricted to classified (non-"none") pixels in the ROI
  - The 3-D centroid of the Jenga tower:
        cx_px  — mean x pixel position of all classified pixels
        cy_px  — mean y pixel position of all classified pixels
        depth_m — mean depth (metres) at those pixels

Published topics
----------------
/jenga/tower_centroid   (geometry_msgs/PointStamped)
    x = mean pixel column (px)
    y = mean pixel row    (px)
    z = mean depth        (metres)

/jenga/depth_overlay    (sensor_msgs/Image)
    BGR visualisation: ROI crop with a false-colour depth heatmap painted
    only on classified pixels; unclassified pixels shown as dark grey.
    The centroid is marked with a crosshair.

How it works
------------
1. Align the depth frame to the colour frame using rs.align so every pixel in
   the colour image has a corresponding depth value.
2. Crop both to the search ROI (same region as colour_identification).
3. Build a mask of all pixels where the colour label is not "none".
4. Read depth values at those pixels (in millimetres from the RealSense SDK,
   converted to metres).
5. Filter out zero/invalid depth readings (sensor returns 0 for out-of-range).
6. Compute:
       cx_px  = mean column index of valid classified pixels
       cy_px  = mean row index    of valid classified pixels
       depth_m = mean depth       of valid classified pixels
7. Publish the centroid and render the overlay image.

Standalone use (no ROS)
-----------------------
Requires a live RealSense camera (depth + colour) or a bag file:

    python depth_analysis.py [recording.bag]

Press Q to quit.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np
import pyrealsense2 as rs

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import String
    from geometry_msgs.msg import PointStamped
    from cv_bridge import CvBridge
    import rclpy.time
    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False
    Node = object

from colour_identification import classify_frame, compute_roi, COLOUR_BGR

# ============================================================================
# Configuration
# ============================================================================

# Depth value range to display in the heatmap (metres).
# Pixels outside this range are clamped to the ends of the colour scale.
DEPTH_MIN_M = 0.001
DEPTH_MAX_M = 2.0

# Zero depth from the sensor means "no reading" — ignore these pixels.
DEPTH_INVALID_MM = 0

# Crosshair size drawn at the centroid.
CROSSHAIR_RADIUS = 18
CROSSHAIR_COLOUR = (255, 255, 255)   # white
CROSSHAIR_THICKNESS = 2

DEPTH_WINDOW = "Depth analysis"
DEBUG_MASKS_WINDOW = "Depth debug masks"

# ============================================================================
# Core helpers
# ============================================================================

def _align_and_crop(
    color_frame: rs.frame,
    depth_frame: rs.frame,
    aligned_depth: rs.frame,
    iw: int,
    ih: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (colour_roi, depth_roi) as numpy arrays, both cropped to the ROI.
    depth_roi values are in millimetres (uint16).
    """
    rx, ry, rw, rh = compute_roi(iw, ih)

    color_bgr  = np.asanyarray(color_frame.get_data())
    depth_mm   = np.asanyarray(aligned_depth.get_data())   # uint16, mm

    color_roi = color_bgr[ry:ry + rh, rx:rx + rw]
    depth_roi = depth_mm [ry:ry + rh, rx:rx + rw]

    return color_roi, depth_roi


def compute_centroid(
    color_roi: np.ndarray,
    depth_roi: np.ndarray,
) -> Optional[dict]:
    """
    Fuse colour classification with depth to find the tower centroid.

    Parameters
    ----------
    color_roi : (H, W, 3) BGR crop aligned to the ROI.
    depth_roi : (H, W)    uint16 depth in millimetres, same spatial extent.

    Returns
    -------
    dict with keys:
        cx_px   — mean pixel column of classified pixels (float)
        cy_px   — mean pixel row    of classified pixels (float)
        depth_m — mean depth in metres of classified pixels (float)
        n_pixels — number of valid classified pixels used (int)
    Returns None if there are no valid pixels.
    """
    # Classify every pixel in the colour ROI
    # classify_frame expects a full frame but we pass the crop — we need the
    # ROI mask, so we classify directly on the crop (same HSV logic, offset 0).
    import cv2 as _cv2
    from colour_identification import HSV_RANGES, classify_hsv

    hsv = _cv2.cvtColor(color_roi, _cv2.COLOR_BGR2HSV)

    # Build a boolean mask: True where any colour is matched (not "none")
    classified = np.zeros(hsv.shape[:2], dtype=bool)
    for colour in HSV_RANGES:
        classified |= classify_hsv(hsv, colour)

    # Also require a valid (non-zero) depth reading
    valid_depth = depth_roi > DEPTH_INVALID_MM
    mask = classified & valid_depth

    n = int(mask.sum())
    if n == 0:
        return None

    # Pixel coordinates of valid classified pixels
    rows, cols = np.where(mask)

    cx_px   = float(cols.mean())
    cy_px   = float(rows.mean())
    depth_m = float(depth_roi[mask].mean()) / 1000.0   # mm → m

    return {
        "cx_px":   cx_px,
        "cy_px":   cy_px,
        "depth_m": depth_m,
        "n_pixels": n,
    }


def build_depth_overlay(
    color_roi:  np.ndarray,
    depth_roi:  np.ndarray,
    centroid:   Optional[dict],
) -> np.ndarray:
    """
    Render the depth overlay image:
    - Dark grey background for unclassified / invalid-depth pixels
    - False-colour heatmap (COLORMAP_JET) for classified pixels
    - White crosshair at the centroid
    - Text annotation showing cx, cy, depth
    """
    from colour_identification import HSV_RANGES, classify_hsv

    h, w = color_roi.shape[:2]
    hsv  = cv2.cvtColor(color_roi, cv2.COLOR_BGR2HSV)

    classified = np.zeros((h, w), dtype=bool)
    for colour in HSV_RANGES:
        classified |= classify_hsv(hsv, colour)

    valid = depth_roi > DEPTH_INVALID_MM
    show  = classified & valid

    # Normalise depth values to 0–255 for the colourmap
    depth_f   = depth_roi.astype(np.float32) / 1000.0   # metres
    depth_norm = np.clip(
        (depth_f - DEPTH_MIN_M) / (DEPTH_MAX_M - DEPTH_MIN_M), 0.0, 1.0
    )
    depth_u8  = (depth_norm * 255).astype(np.uint8)
    heatmap   = cv2.applyColorMap(depth_u8, cv2.COLORMAP_JET)

    # Canvas: start with a dimmed version of the original colour crop
    canvas = (color_roi.astype(np.float32) * 0.25).astype(np.uint8)

    # Paint heatmap only where we have classified + valid depth
    canvas[show] = heatmap[show]

    # Crosshair at centroid
    if centroid is not None:
        cx = int(round(centroid["cx_px"]))
        cy = int(round(centroid["cy_px"]))
        r  = CROSSHAIR_RADIUS
        t  = CROSSHAIR_THICKNESS
        cv2.line(canvas, (cx - r, cy), (cx + r, cy), CROSSHAIR_COLOUR, t, cv2.LINE_AA)
        cv2.line(canvas, (cx, cy - r), (cx, cy + r), CROSSHAIR_COLOUR, t, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), 4, CROSSHAIR_COLOUR, -1)

        label = (f"x={cx}px  y={cy}px  "
                 f"d={centroid['depth_m']:.3f}m  "
                 f"n={centroid['n_pixels']}")
        # Dark shadow + white text
        cv2.putText(canvas, label, (9, h - 11),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (20, 20, 20), 2, cv2.LINE_AA)
        cv2.putText(canvas, label, (8, h - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (240, 240, 240), 1, cv2.LINE_AA)

    # Depth scale legend (right edge, vertical gradient)
    bar_w, bar_h = 14, h - 20
    bar_x = w - bar_w - 6
    bar_y = 10
    for i in range(bar_h):
        v  = int((1.0 - i / bar_h) * 255)
        c  = cv2.applyColorMap(np.array([[v]], dtype=np.uint8), cv2.COLORMAP_JET)[0, 0]
        cv2.rectangle(canvas,
                      (bar_x, bar_y + i),
                      (bar_x + bar_w, bar_y + i + 1),
                      c.tolist(), -1)
    cv2.putText(canvas, f"{DEPTH_MIN_M:.1f}m",
                (bar_x - 2, bar_y + bar_h + 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(canvas, f"{DEPTH_MAX_M:.1f}m",
                (bar_x - 2, bar_y - 3),
                cv2.FONT_HERSHEY_SIMPLEX, 0.32, (200, 200, 200), 1, cv2.LINE_AA)

    return canvas


def build_debug_masks_visual(
    color_roi: np.ndarray,
    depth_roi: np.ndarray,
) -> np.ndarray:
    """
    Visualise why pixels are dim:
      - Left: valid depth mask
      - Middle: colour-classified mask
      - Right: overlap (used for heatmap)
    """
    from colour_identification import HSV_RANGES, classify_hsv

    h, w = color_roi.shape[:2]
    hsv = cv2.cvtColor(color_roi, cv2.COLOR_BGR2HSV)

    classified = np.zeros((h, w), dtype=bool)
    for colour in HSV_RANGES:
        classified |= classify_hsv(hsv, colour)

    valid_depth = depth_roi > DEPTH_INVALID_MM
    used = classified & valid_depth

    valid_vis = np.zeros((h, w, 3), dtype=np.uint8)
    class_vis = np.zeros((h, w, 3), dtype=np.uint8)
    used_vis = np.zeros((h, w, 3), dtype=np.uint8)

    valid_vis[valid_depth] = (0, 255, 0)
    class_vis[classified] = (255, 255, 0)
    used_vis[used] = (0, 255, 255)

    cv2.putText(valid_vis, "valid depth", (8, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(class_vis, "classified colour", (8, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(used_vis, "used (AND)", (8, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)

    combined = np.hstack((valid_vis, class_vis, used_vis))
    return combined


# ============================================================================
# ROS2 node
# ============================================================================

class DepthAnalysisNode(Node):
    """
    Subscribes to aligned colour + depth images, computes the tower centroid
    and publishes it as a PointStamped plus a debug overlay image.

    Expects colour + aligned-depth topics (defaults match realsense2_camera rs_launch
    with a namespace, e.g. camera/camera/...).
    """

    def __init__(
        self,
        color_topic: str = "/camera/camera/color/image_raw",
        depth_topic: str = "/camera/camera/aligned_depth_to_color/image_raw",
    ):
        super().__init__("depth_analysis")
        self._bridge = CvBridge()

        from message_filters import ApproximateTimeSynchronizer, Subscriber
        color_sub = Subscriber(self, Image, color_topic)
        depth_sub = Subscriber(self, Image, depth_topic)

        self._sync = ApproximateTimeSynchronizer(
            [color_sub, depth_sub], queue_size=10, slop=0.05)
        self._sync.registerCallback(self._cb)

        self._pub_centroid = self.create_publisher(
            PointStamped, "/jenga/tower_centroid", 10)
        self._pub_overlay  = self.create_publisher(
            Image, "/jenga/depth_overlay", 10)

        self.get_logger().info("DepthAnalysisNode ready")

    def _cb(self, color_msg: Image, depth_msg: Image) -> None:
        color_roi = self._bridge.imgmsg_to_cv2(color_msg, "bgr8")
        depth_roi = self._bridge.imgmsg_to_cv2(depth_msg, "16UC1")

        ih, iw = color_roi.shape[:2]
        rx, ry, rw, rh = compute_roi(iw, ih)
        color_roi = color_roi[ry:ry + rh, rx:rx + rw]
        depth_roi = depth_roi[ry:ry + rh, rx:rx + rw]

        centroid = compute_centroid(color_roi, depth_roi)

        if centroid is not None:
            pt = PointStamped()
            pt.header = color_msg.header
            pt.point.x = centroid["cx_px"]
            pt.point.y = centroid["cy_px"]
            pt.point.z = centroid["depth_m"]
            self._pub_centroid.publish(pt)

        overlay = build_depth_overlay(color_roi, depth_roi, centroid)
        self._pub_overlay.publish(
            self._bridge.cv2_to_imgmsg(overlay, encoding="bgr8"))


# ============================================================================
# Standalone (direct RealSense SDK — no ROS broker needed)
# ============================================================================

def main_ros() -> None:
    rclpy.init()
    node = DepthAnalysisNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

