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
    SEARCH_AREA_MARGIN,
    COLOUR_MIN_BLOB_AREA_PX,
    COLOUR_MASK_MEDIAN_PX,
    COLOUR_MASK_MORPH_CLOSE_PX,
    COLOUR_MASK_MORPH_OPEN_PX,
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


def compute_display_crop(
    iw: int,
    ih: int,
    search_area: tuple[float, float, float, float] | None = None,
    margin: float = SEARCH_AREA_MARGIN,
) -> tuple[int, int, int, int, int, int, int, int]:
    """
    Full-frame crop for live / box-percentages views.

    Horizontal: search area plus margin on left and right.
    Vertical: from the top of the camera frame down through the search area
    plus margin below.
    """
    rx, ry, rw, rh = compute_roi(iw, ih, search_area=search_area)
    mx = int(rw * margin)
    my = int(rh * margin)
    dx1 = max(0, rx - mx)
    dy1 = 0
    dx2 = min(iw, rx + rw + mx)
    dy2 = min(ih, ry + rh + my)
    roi_x = rx - dx1
    roi_y = ry - dy1
    return dx1, dy1, dx2, dy2, roi_x, roi_y, rw, rh


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
    *,
    median_px: int | None = None,
    morph_close_px: int | None = None,
    morph_open_px: int | None = None,
    min_blob_area_px: int | None = None,
) -> np.ndarray:
    """Return a boolean mask (H×W) that is True wherever hsv matches colour."""
    med = int(COLOUR_MASK_MEDIAN_PX if median_px is None else median_px)
    close_px = int(COLOUR_MASK_MORPH_CLOSE_PX if morph_close_px is None else morph_close_px)
    open_px = int(COLOUR_MASK_MORPH_OPEN_PX if morph_open_px is None else morph_open_px)
    min_blob = int(COLOUR_MIN_BLOB_AREA_PX if min_blob_area_px is None else min_blob_area_px)

    work = hsv
    if med > 0:
        work = cv2.medianBlur(work, _odd(med))

    ranges_map = hsv_ranges if hsv_ranges is not None else HSV_RANGES
    combined = np.zeros(work.shape[:2], dtype=np.uint8)
    for lo, hi in ranges_map[colour]:
        combined |= cv2.inRange(work, np.array(lo, dtype=np.uint8),
                                    np.array(hi, dtype=np.uint8))

    if close_px > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(close_px),) * 2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, k)
    if open_px > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(open_px),) * 2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, k)

    combined = _remove_small_components(combined, min_blob)

    return combined.astype(bool)


# ---------------------------------------------------------------------------
# Per-frame colour cache
# ---------------------------------------------------------------------------
# The analysis pipeline (percentages, centroids, depth splits, seam detection)
# repeatedly needs the full-frame HSV image and the per-colour boolean masks for
# the SAME frame.  Recomputing cv2.cvtColor + classify_hsv inside every helper is
# what dominates per-frame CPU during probe monitoring.  This caches both for the
# current frame so each is computed exactly once and shared everywhere.
#
# The cache is keyed on the identity of the bgr array AND keeps a reference to it.
# Holding the reference guarantees the array stays alive while cached, so its
# id() cannot be reused by a different array — an id() match is therefore a true
# identity match (no stale-cache risk across frames).  A new frame is a new array
# (new id), which transparently invalidates and rebuilds the cache.

class _FrameColourCache:
    def __init__(self) -> None:
        self._frame_ref: np.ndarray | None = None
        self._frame_id: int | None = None
        self._hsv: np.ndarray | None = None
        self._masks: dict[str, np.ndarray] = {}

    def _ensure(self, bgr: np.ndarray) -> None:
        if self._frame_id == id(bgr) and self._frame_ref is bgr:
            return
        self._frame_ref = bgr           # keep alive so its id() stays unique
        self._frame_id = id(bgr)
        self._hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        self._masks = {}

    def hsv(self, bgr: np.ndarray) -> np.ndarray:
        self._ensure(bgr)
        return self._hsv  # type: ignore[return-value]

    def mask(self, bgr: np.ndarray, colour: str) -> np.ndarray:
        self._ensure(bgr)
        cached = self._masks.get(colour)
        if cached is None:
            cached = classify_hsv(self._hsv, colour)
            self._masks[colour] = cached
        return cached


_FRAME_COLOUR_CACHE = _FrameColourCache()


def frame_hsv(bgr: np.ndarray) -> np.ndarray:
    """Full-frame HSV for bgr, computed once per frame and cached."""
    return _FRAME_COLOUR_CACHE.hsv(bgr)


def frame_colour_mask(bgr: np.ndarray, colour: str) -> np.ndarray:
    """
    Boolean H×W mask of `colour` over the full frame, cached per frame.

    Equivalent to classify_hsv(cv2.cvtColor(bgr, BGR2HSV), colour) with default
    config params — but the HSV conversion and the per-colour classification are
    each computed only once per frame and reused across the whole pipeline.

    The returned array is the cached object; callers must treat it as read-only
    (use it in non-mutating expressions like `quad & mask`).  All current callers
    do this.
    """
    return _FRAME_COLOUR_CACHE.mask(bgr, colour)


def classify_roi_bgr(
    roi_bgr: np.ndarray,
    hsv_ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] | None = None,
    *,
    median_px: int | None = None,
    morph_close_px: int | None = None,
    morph_open_px: int | None = None,
    min_blob_area_px: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Classify every pixel in a pre-cropped ROI BGR image."""
    ranges_map = hsv_ranges if hsv_ranges is not None else HSV_RANGES
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    rh, rw = roi_bgr.shape[:2]
    colour_img   = np.zeros((rh, rw, 3), dtype=np.uint8)
    label_grid   = np.full((rh, rw), "none", dtype=object)
    unclassified = np.ones((rh, rw), dtype=bool)

    for colour in ranges_map:
        mask = classify_hsv(
            hsv,
            colour,
            hsv_ranges,
            median_px=median_px,
            morph_close_px=morph_close_px,
            morph_open_px=morph_open_px,
            min_blob_area_px=min_blob_area_px,
        ) & unclassified
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
