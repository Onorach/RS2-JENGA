"""
colour_identification.py
------------------------
Classifies every pixel in the search ROI by colour using HSV masks.

ROS topics published
--------------------
/jenga/colour_frame   (sensor_msgs/Image)   BGR image painted with class colours.
/jenga/colour_labels  (std_msgs/String)      JSON 2-D array of colour-name strings.
"""

import json

import cv2
import numpy as np

from perception_config import (
    HSV_RANGES,
    COLOUR_BGR,
    SEARCH_AREA,
    COLOUR_MIN_BLOB_AREA_PX,
)

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

# Spatial pre-filters applied before HSV classification.
# Median blur smooths fringe pixels; morphological open removes specks.
PREFILTER_MEDIAN_PX = 5  # 0 = disabled
PREFILTER_OPEN_PX   = 5  # 0 = disabled


def compute_roi(
    iw: int,
    ih: int,
    search_area: tuple[float, float, float, float] | None = None,
) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the search ROI in full-frame pixel coordinates."""
    cx_f, cy_f, w_f, h_f = search_area if search_area is not None else SEARCH_AREA
    cw = int(iw * w_f)
    ch = int(ih * h_f)
    x = max(0, min(int(iw * cx_f) - cw // 2, iw - cw))
    y = max(0, min(int(ih * cy_f) - ch // 2, ih - ch))
    return x, y, cw, ch


def _odd(k: int) -> int:
    return k if k % 2 == 1 else k + 1


def _remove_small_components(mask: np.ndarray, min_area_px: int) -> np.ndarray:
    """Drop connected components smaller than min_area_px from a binary mask."""
    if min_area_px <= 0:
        return mask

    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n_labels <= 1:
        return mask

    out = np.zeros_like(mask)
    for label_id in range(1, n_labels):  # label 0 is background
        area = int(stats[label_id, cv2.CC_STAT_AREA])
        if area >= min_area_px:
            out[labels == label_id] = 255
    return out


def classify_hsv(
    hsv: np.ndarray,
    colour: str,
    hsv_ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] | None = None,
) -> np.ndarray:
    """Return a boolean mask (H×W) that is True wherever hsv matches colour."""
    if PREFILTER_MEDIAN_PX > 0:
        hsv = cv2.medianBlur(hsv, _odd(PREFILTER_MEDIAN_PX))

    ranges_map = hsv_ranges if hsv_ranges is not None else HSV_RANGES
    combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in ranges_map[colour]:
        combined |= cv2.inRange(hsv, np.array(lo, dtype=np.uint8),
                                     np.array(hi, dtype=np.uint8))

    if PREFILTER_OPEN_PX > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(PREFILTER_OPEN_PX),) * 2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, k)

    combined = _remove_small_components(combined, int(COLOUR_MIN_BLOB_AREA_PX))

    return combined.astype(bool)


def classify_roi_bgr(
    roi_bgr: np.ndarray,
    hsv_ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Classify every pixel in a pre-cropped ROI BGR image."""
    ranges_map = hsv_ranges if hsv_ranges is not None else HSV_RANGES
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    rh, rw = roi_bgr.shape[:2]
    colour_img   = np.zeros((rh, rw, 3), dtype=np.uint8)
    label_grid   = np.full((rh, rw), "none", dtype=object)
    unclassified = np.ones((rh, rw), dtype=bool)

    for colour in ranges_map:
        mask = classify_hsv(hsv, colour, hsv_ranges) & unclassified
        colour_img[mask] = COLOUR_BGR[colour]
        label_grid[mask] = colour
        unclassified    &= ~mask

    return colour_img, label_grid


def classify_frame(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Classify every pixel in the search ROI.

    Returns
    -------
    colour_img : (H, W, 3) uint8 BGR — each pixel painted its class colour; black = none.
    label_grid : (H, W) string array — colour name per pixel.
    """
    ih, iw = bgr.shape[:2]
    rx, ry, rw, rh = compute_roi(iw, ih)
    return classify_roi_bgr(bgr[ry:ry + rh, rx:rx + rw])


class ColourIdentificationNode(Node):
    def __init__(self, color_topic: str = "/camera/camera/color/image_raw"):
        super().__init__("colour_identification")
        self._bridge = CvBridge()
        self.create_subscription(Image, color_topic, self._cb, 10)
        self._pub_img    = self.create_publisher(Image,  "/jenga/colour_frame",  10)
        self._pub_labels = self.create_publisher(String, "/jenga/colour_labels", 10)
        self.get_logger().info("ColourIdentificationNode ready")

    def _cb(self, msg: Image) -> None:
        bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        colour_img, label_grid = classify_frame(bgr)
        self._pub_img.publish(self._bridge.cv2_to_imgmsg(colour_img, encoding="bgr8"))
        label_msg = String()
        label_msg.data = json.dumps(label_grid.tolist())
        self._pub_labels.publish(label_msg)
