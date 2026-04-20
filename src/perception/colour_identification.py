"""
colour_identification.py
------------------------
Classifies every pixel in the search ROI by colour using HSV masks.

Published topics
----------------
/jenga/colour_frame   (sensor_msgs/Image)   BGR image with each pixel painted
                                             its classified colour (black = none).
/jenga/colour_labels  (std_msgs/String)      JSON 2-D array of colour-name strings.

"""

import json
import sys

import cv2
import numpy as np

from perception_config import HSV_RANGES, COLOUR_BGR, ROI_FRACS

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

# Spatial pre-filters: median blur smooths fringe pixels, morphological open removes specks.
PREFILTER_MEDIAN_PX = 5  # 0 = disabled
PREFILTER_OPEN_PX   = 5  # 0 = disabled


def compute_roi(iw: int, ih: int) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the search ROI in full-frame pixel coords."""
    cx_f, cy_f, w_f, h_f = ROI_FRACS
    cw = int(iw * w_f)
    ch = int(ih * h_f)
    x = max(0, min(int(iw * cx_f) - cw // 2, iw - cw))
    y = max(0, min(int(ih * cy_f) - ch // 2, ih - ch))
    return x, y, cw, ch


def _odd(k: int) -> int:
    return k if k % 2 == 1 else k + 1


def classify_hsv(hsv: np.ndarray, colour: str) -> np.ndarray:
    """Return a boolean mask (H×W) that is True wherever hsv matches colour."""
    if PREFILTER_MEDIAN_PX > 0:
        hsv = cv2.medianBlur(hsv, _odd(PREFILTER_MEDIAN_PX))

    combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in HSV_RANGES[colour]:
        combined |= cv2.inRange(hsv, np.array(lo, dtype=np.uint8),
                                     np.array(hi, dtype=np.uint8))

    if PREFILTER_OPEN_PX > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(PREFILTER_OPEN_PX),) * 2)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, k)

    return combined.astype(bool)


def classify_frame(bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Classify every pixel in the search ROI of bgr.

    Returns
    -------
    colour_img : (H, W, 3) uint8 BGR — each pixel painted its class colour; black = none.
    label_grid : (H, W) string array — colour name per pixel.
    """
    ih, iw = bgr.shape[:2]
    rx, ry, rw, rh = compute_roi(iw, ih)
    hsv = cv2.cvtColor(bgr[ry:ry + rh, rx:rx + rw], cv2.COLOR_BGR2HSV)

    colour_img   = np.zeros((rh, rw, 3), dtype=np.uint8)
    label_grid   = np.full((rh, rw), "none", dtype=object)
    unclassified = np.ones((rh, rw), dtype=bool)

    for colour in HSV_RANGES:
        mask = classify_hsv(hsv, colour) & unclassified
        colour_img[mask] = COLOUR_BGR[colour]
        label_grid[mask] = colour
        unclassified    &= ~mask

    return colour_img, label_grid


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

    colours, counts = np.unique(label_grid, return_counts=True)
    total = label_grid.size
    print(f"ROI size: {label_grid.shape[1]}×{label_grid.shape[0]}")
    for c, n in sorted(zip(colours, counts), key=lambda x: -x[1]):
        print(f"  {c:<10} {n:>7} px  ({n / total * 100:.1f}%)")

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