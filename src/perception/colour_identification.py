"""
colour_identification.py
------------------------
ROS2 node that classifies every pixel in the search ROI by colour using HSV
masks and publishes the results for other nodes to consume.

Published topics
----------------
/jenga/colour_frame   (sensor_msgs/Image)
    BGR image the same size as the ROI where each pixel is painted with its
    classified colour (or black for unmatched pixels).

/jenga/colour_labels  (std_msgs/String)
    JSON string — a flat 2-D array (rows × cols) of colour-name strings,
    e.g. "green", "red", "none".  Consumers can parse this directly.

The node also exposes the following as module-level constants so other nodes
can import them without going through ROS topics:

    HSV_RANGES       — the colour → HSV bound dict
    COLOUR_BGR       — colour name → BGR display tuple
    ROI_FRACS        — (cx, cy, w, h) as fractions of frame size
    DIVIDE_LINE      — ((x1,y1), (x2,y2)) full-frame face-dividing line

Standalone use (no ROS)
-----------------------
    python colour_identification.py path/to/image.png

Publishes nothing but prints a pixel-count summary and shows the colour frame.
"""

from __future__ import annotations

import json
import sys
from typing import Optional

import cv2
import numpy as np

# ── try ROS2 import; degrade gracefully if not available ────────────────────
try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import String
    from cv_bridge import CvBridge
    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False
    Node = object  # fallback base so class definition works

# ============================================================================
# Configuration — edit these to match your setup
# ============================================================================

# HSV colour ranges.  Each colour maps to one or more (lower, upper) bound
# pairs.  Colours are tested in order; the first match wins.
# S and V floors are kept deliberately high to avoid fringe/shadow pixels.
HSV_RANGES: dict[str, list[tuple[tuple[int,int,int], tuple[int,int,int]]]] = {
    # Red wraps around hue=0, so two ranges are required.
    "red": [
        ((0,   150, 140), (10,  255, 255)),
        ((170, 150, 140), (179, 255, 255)),
    ],
    # Yellow – slightly broader hue, lower S/V thresholds.
    "yellow": [
        ((18, 140, 140), (40, 255, 255)),
    ],
    "green": [
        ((40, 120, 100), (85, 255, 255)),
    ],
    # Blue – light blue, stops before purple.
    "blue": [
        ((90, 220, 130), (110, 255, 255)),
    ],
    # Purple / magenta – darker purples, allow low V but keep higher S.
    "purple": [
        ((110, 110, 50), (175, 255, 200)),
    ],
}

# BGR display colour per class (used when painting the colour frame).
COLOUR_BGR: dict[str, tuple[int,int,int]] = {
    "red":    (0,   0,   220),
    "yellow": (0,   220, 220),
    "green":  (0,   200, 0),
    "blue":   (220, 80,  0),
    "purple": (180, 0,   180),
    "none":   (0,   0,   0),
}

# Search ROI — fractions of the full frame (cx_frac, cy_frac, w_frac, h_frac).
ROI_FRACS = (0.495, 0.485, 0.32, 0.62)

# Face-dividing line in full-frame pixel coordinates.
# Blobs on opposite sides of this line are kept separate.
DIVIDE_LINE = ((920, 217), (914, 850))

# Spatial pre-filters applied before range matching.
# Median blur smooths fringe pixels; morphological open removes specks.
PREFILTER_MEDIAN_PX = 5   # 0 = disabled
PREFILTER_OPEN_PX   = 5   # 0 = disabled

# ============================================================================
# Core classification helpers (importable by other modules)
# ============================================================================

def compute_roi(iw: int, ih: int) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the search ROI in full-frame pixel coords."""
    cx_f, cy_f, w_f, h_f = ROI_FRACS
    cw = int(iw * w_f)
    ch = int(ih * h_f)
    cx = int(iw * cx_f) - cw // 2
    cy = int(ih * cy_f) - ch // 2
    x  = max(0, min(cx, iw - cw))
    y  = max(0, min(cy, ih - ch))
    return x, y, cw, ch


def _odd(k: int) -> int:
    return k if k % 2 == 1 else k + 1


def classify_hsv(hsv: np.ndarray, colour: str) -> np.ndarray:
    """
    Return a boolean mask (HxW) that is True wherever *hsv* matches *colour*.

    Applies median blur and morphological open to suppress fringe pixels before
    range matching.
    """
    if PREFILTER_MEDIAN_PX > 0:
        hsv = cv2.medianBlur(hsv, _odd(PREFILTER_MEDIAN_PX))

    combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in HSV_RANGES[colour]:
        combined |= cv2.inRange(hsv,
                                np.array(lo, dtype=np.uint8),
                                np.array(hi, dtype=np.uint8))

    if PREFILTER_OPEN_PX > 0:
        k = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (_odd(PREFILTER_OPEN_PX),) * 2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, k)

    return combined.astype(bool)


def classify_frame(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Classify every pixel in the search ROI of *bgr*.

    Returns
    -------
    colour_img : (H, W, 3) uint8 BGR image — each pixel painted with its
                 class colour; black = "none".
    label_grid : (H, W) array of strings — colour name per pixel.
    """
    ih, iw = bgr.shape[:2]
    rx, ry, rw, rh = compute_roi(iw, ih)
    roi = bgr[ry:ry + rh, rx:rx + rw]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    colour_img  = np.zeros((rh, rw, 3), dtype=np.uint8)   # black = none
    label_grid  = np.full((rh, rw), "none", dtype=object)
    unclassified = np.ones((rh, rw), dtype=bool)

    for colour in HSV_RANGES:
        mask = classify_hsv(hsv, colour) 
        colour_img[mask]  = COLOUR_BGR[colour]
        label_grid[mask]  = colour

    return colour_img, label_grid


# ============================================================================
# ROS2 node
# ============================================================================

class ColourIdentificationNode(Node):
    """
    Subscribes to /camera/color/image_raw, classifies every pixel in the ROI
    and publishes the colour frame + label grid every frame.
    """

    def __init__(self):
        super().__init__("colour_identification")
        self._bridge = CvBridge()

        self._sub = self.create_subscription(
            Image, "/camera/color/image_raw", self._cb, 10)

        self._pub_img = self.create_publisher(
            Image, "/jenga/colour_frame", 10)
        self._pub_labels = self.create_publisher(
            String, "/jenga/colour_labels", 10)

        self.get_logger().info("ColourIdentificationNode ready")

    def _cb(self, msg: Image) -> None:
        bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        colour_img, label_grid = classify_frame(bgr)

        # Publish colour image
        self._pub_img.publish(
            self._bridge.cv2_to_imgmsg(colour_img, encoding="bgr8"))

        # Publish label grid as JSON
        label_msg = String()
        label_msg.data = json.dumps(label_grid.tolist())
        self._pub_labels.publish(label_msg)


# ============================================================================
# Entry points
# ============================================================================

def main_ros():
    rclpy.init()
    node = ColourIdentificationNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def main_standalone(image_path: str):
    bgr = cv2.imread(image_path)
    if bgr is None:
        print(f"Cannot read: {image_path}")
        sys.exit(1)

    colour_img, label_grid = classify_frame(bgr)

    # Summary
    colours, counts = np.unique(label_grid, return_counts=True)
    total = label_grid.size
    print(f"ROI size: {label_grid.shape[1]}×{label_grid.shape[0]}")
    for c, n in sorted(zip(colours, counts), key=lambda x: -x[1]):
        print(f"  {c:<10} {n:>7} px  ({n/total*100:.1f}%)")

    cv2.namedWindow("Colour identification", cv2.WINDOW_NORMAL)
    cv2.imshow("Colour identification", colour_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_standalone(sys.argv[1])
    elif _ROS_AVAILABLE:
        main_ros()
    else:
        print("Usage: python colour_identification.py <image_path>")
        sys.exit(1)
