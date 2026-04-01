"""
colour_blobs.py
---------------
ROS2 node that finds blobs of each colour in the search ROI, fits a
4-sided polygon to each blob, and publishes the results.

The mask is split along the face-dividing line before contour detection so
same-colour blocks on opposite faces of the tower are never merged.

Subscribes
----------
/camera/color/image_raw  (sensor_msgs/Image)

Published topics
----------------
/jenga/colour_blobs  (std_msgs/String)
    JSON dict:  { "red": [ [[x0,y0],[x1,y1],[x2,y2],[x3,y3]], ... ], ... }
    Coordinates are in ROI-local pixels.

/jenga/blob_debug_image  (sensor_msgs/Image)
    Dimmed original crop with semi-transparent quad fills, bright outlines,
    colour-name labels, divide line and ROI border.

Standalone use (no ROS)
-----------------------
    python colour_blobs.py path/to/image.png
"""

from __future__ import annotations

import json
import sys

import cv2
import numpy as np

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import String
    from cv_bridge import CvBridge
    _ROS_AVAILABLE = True
except ImportError:
    _ROS_AVAILABLE = False
    Node = object

from colour_identification import (
    HSV_RANGES, COLOUR_BGR, compute_roi,
    classify_hsv, DIVIDE_LINE,
)

# ============================================================================
# Configuration
# ============================================================================

# Minimum blob area in pixels² — smaller blobs are discarded.
MIN_BLOB_AREA   = 400

# Morphological close kernel: fills holes within a block before splitting.
MORPH_CLOSE_PX  = 9

# Width filter: erode by this radius to remove tendrils narrower than
# 2 × MIN_WIDTH_PX, then dilate back by RESTORE_PX.
MIN_WIDTH_PX    = 30
RESTORE_PX      = 22

# Shape quality thresholds.
MIN_SOLIDITY    = 0.72   # contour area / convex hull area
MIN_QUAD_FILL   = 0.50   # contour area / fitted quad area

# Polygon approximation — fraction of perimeter used as epsilon.
POLY_EPS_FRAC   = 0.04

# Display
BG_DIM          = 0.35   # how much to dim the background crop
QUAD_THICKNESS  = 2

OUTLINE_BGR: dict[str, tuple[int,int,int]] = {
    "red":    (80,  80,  255),
    "yellow": (80,  255, 255),
    "green":  (80,  255, 80),
    "blue":   (255, 160, 80),
    "purple": (255, 80,  255),
}

# ============================================================================
# Helpers
# ============================================================================

def _odd(k: int) -> int:
    return max(1, k if k % 2 == 1 else k + 1)


def _kernel(px: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(px),) * 2)


def _morph_close(mask: np.ndarray, px: int) -> np.ndarray:
    if px > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, _kernel(px))
    return mask


def _remove_thin_regions(mask: np.ndarray,
                          min_w: int, restore: int) -> np.ndarray:
    """Erode to kill tendrils < min_w px wide, then dilate back."""
    if min_w <= 0:
        return mask
    erode_r = max(1, min_w // 2)
    mask = cv2.erode(mask, _kernel(erode_r * 2 + 1))
    if restore > 0:
        mask = cv2.dilate(mask, _kernel(restore * 2 + 1))
    return mask


def _split_on_divide(mask: np.ndarray,
                     roi_x: int, roi_y: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Split *mask* (ROI-local coords) into two halves along DIVIDE_LINE.
    Returns (left_mask, right_mask).
    """
    h, w = mask.shape[:2]
    (fx1, fy1), (fx2, fy2) = DIVIDE_LINE
    tx, ty = fx1 - roi_x, fy1 - roi_y
    bx, by = fx2 - roi_x, fy2 - roi_y

    left_poly = np.array([[0, 0], [tx, ty], [bx, by], [0, h]], dtype=np.int32)
    left_side = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(left_side, [left_poly], 255)

    right_side = cv2.bitwise_not(left_side)
    return cv2.bitwise_and(mask, left_side), cv2.bitwise_and(mask, right_side)


def _solidity(cnt: np.ndarray) -> float:
    area = cv2.contourArea(cnt)
    if area <= 0:
        return 0.0
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    return area / hull_area if hull_area > 0 else 0.0


def _quad_fill(cnt: np.ndarray, quad: np.ndarray) -> float:
    cnt_area  = cv2.contourArea(cnt)
    quad_area = cv2.contourArea(quad.reshape(-1, 1, 2).astype(np.float32))
    return cnt_area / quad_area if quad_area > 0 else 0.0


def _contour_to_quad(cnt: np.ndarray, eps_frac: float) -> np.ndarray:
    """Fit contour to a 4-sided polygon, falling back to minAreaRect."""
    peri = cv2.arcLength(cnt, True)
    if peri < 1:
        return np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))

    approx = cnt
    for f in [eps_frac, eps_frac*2, eps_frac*4, eps_frac*8, eps_frac*16]:
        approx = cv2.approxPolyDP(cnt, f * peri, True)
        if len(approx) <= 4:
            break

    if len(approx) == 4:
        return approx.reshape(4, 2).astype(np.int32)

    return np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))


# ============================================================================
# Core blob finder
# ============================================================================

def find_blobs(
    bgr_frame: np.ndarray,
) -> tuple[dict[str, list[np.ndarray]], int, int]:
    """
    Find colour blobs in the search ROI of *bgr_frame*.

    Returns
    -------
    blobs   : dict colour → list of (4,2) int32 quad arrays (ROI-local coords)
    roi_x   : ROI left edge in full-frame pixels
    roi_y   : ROI top edge in full-frame pixels
    """
    ih, iw = bgr_frame.shape[:2]
    roi_x, roi_y, roi_w, roi_h = compute_roi(iw, ih)
    roi_bgr = bgr_frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    blobs: dict[str, list[np.ndarray]] = {c: [] for c in HSV_RANGES}

    for colour in HSV_RANGES:
        # 1. Clean mask via colour_identification's filtered classifier
        mask = classify_hsv(roi_hsv, colour).astype(np.uint8) * 255

        # 2. Close holes
        mask = _morph_close(mask, MORPH_CLOSE_PX)

        # 3. Remove tendrils
        mask = _remove_thin_regions(mask, MIN_WIDTH_PX, RESTORE_PX)

        # 4. Split on face-dividing line
        left, right = _split_on_divide(mask, roi_x, roi_y)

        for half in (left, right):
            contours, _ = cv2.findContours(
                half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) < MIN_BLOB_AREA:
                    continue
                if _solidity(cnt) < MIN_SOLIDITY:
                    continue
                quad = _contour_to_quad(cnt, POLY_EPS_FRAC)
                if _quad_fill(cnt, quad) < MIN_QUAD_FILL:
                    continue
                blobs[colour].append(quad)

    return blobs, roi_x, roi_y


def build_debug_image(bgr_frame: np.ndarray,
                      blobs: dict[str, list[np.ndarray]],
                      roi_x: int, roi_y: int) -> np.ndarray:
    ih, iw = bgr_frame.shape[:2]
    _, _, roi_w, roi_h = compute_roi(iw, ih)
    roi_bgr = bgr_frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

    canvas = (roi_bgr.astype(np.float32) * BG_DIM).astype(np.uint8)

    for colour, quads in blobs.items():
        fill    = COLOUR_BGR.get(colour, (128, 128, 128))
        outline = OUTLINE_BGR.get(colour, (255, 255, 255))

        for quad in quads:
            pts = quad.reshape(-1, 1, 2)

            overlay = canvas.copy()
            cv2.fillPoly(overlay, [pts], fill)
            cv2.addWeighted(overlay, 0.30, canvas, 0.70, 0, canvas)

            cv2.polylines(canvas, [pts], True, outline,
                          QUAD_THICKNESS, cv2.LINE_AA)

            M = cv2.moments(pts)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.putText(canvas, colour, (cx - 1, cy + 1),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            (20, 20, 20), 1, cv2.LINE_AA)
                cv2.putText(canvas, colour, (cx, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            outline, 1, cv2.LINE_AA)

    # ROI border
    cv2.rectangle(canvas, (0, 0), (roi_w - 1, roi_h - 1), (255, 255, 0), 1)

    # Divide line
    (fx1, fy1), (fx2, fy2) = DIVIDE_LINE
    dl_top = (fx1 - roi_x, fy1 - roi_y)
    dl_bot = (fx2 - roi_x, fy2 - roi_y)
    cv2.line(canvas, dl_top, dl_bot, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(canvas, "divide", (dl_top[0] + 4, dl_top[1] + 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1, cv2.LINE_AA)

    return canvas


# ============================================================================
# ROS2 node
# ============================================================================

class ColourBlobsNode(Node):
    def __init__(self):
        super().__init__("colour_blobs")
        self._bridge = CvBridge()

        self._sub = self.create_subscription(
            Image, "/camera/color/image_raw", self._cb, 10)

        self._pub_blobs = self.create_publisher(
            String, "/jenga/colour_blobs", 10)
        self._pub_img = self.create_publisher(
            Image, "/jenga/blob_debug_image", 10)

        self.get_logger().info("ColourBlobsNode ready")

    def _cb(self, msg: Image) -> None:
        bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        blobs, roi_x, roi_y = find_blobs(bgr)

        # Serialise quads as lists for JSON
        serialisable = {
            colour: [q.tolist() for q in quads]
            for colour, quads in blobs.items()
        }
        blob_msg = String()
        blob_msg.data = json.dumps(serialisable)
        self._pub_blobs.publish(blob_msg)

        debug = build_debug_image(bgr, blobs, roi_x, roi_y)
        self._pub_img.publish(
            self._bridge.cv2_to_imgmsg(debug, encoding="bgr8"))


# ============================================================================
# Entry points
# ============================================================================

def main_ros():
    rclpy.init()
    node = ColourBlobsNode()
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

    blobs, roi_x, roi_y = find_blobs(bgr)

    total = sum(len(v) for v in blobs.values())
    print(f"Found {total} blobs:")
    for colour, quads in blobs.items():
        if quads:
            print(f"  {colour}: {len(quads)}")

    debug = build_debug_image(bgr, blobs, roi_x, roi_y)
    cv2.namedWindow("Colour blobs", cv2.WINDOW_NORMAL)
    cv2.imshow("Colour blobs", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_standalone(sys.argv[1])
    elif _ROS_AVAILABLE:
        main_ros()
    else:
        print("Usage: python colour_blobs.py <image_path>")
        sys.exit(1)
