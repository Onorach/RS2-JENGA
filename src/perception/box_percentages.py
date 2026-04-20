"""
box_percentages.py
------------------
ROS2 node that subscribes to the colour label grid from colour_identification,
maps it onto the predefined quadrilateral grid cells, and publishes the
percentage of each colour within each cell.

Subscribes
----------
/jenga/colour_labels  (std_msgs/String)
    JSON label grid produced by colour_identification.

Published topics
----------------
/jenga/box_percentages  (std_msgs/String)
    JSON list of per-box results:
    [
      {
        "name": "left_cell",
        "total_pixels": 1234,
        "colours": {
          "red":    {"count": 10,  "pct": 0.81},
          "green":  {"count": 900, "pct": 72.94},
          ...
          "none":   {"count": 100, "pct": 8.10}
        }
      },
      ...
    ]

/jenga/box_debug_image  (sensor_msgs/Image)
    Visual debug window: white background, coloured pixels inside each quad,
    corner dots and labels, colour legend.

"""


import json
import sys
from typing import Optional

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

from colour_identification import classify_frame, compute_roi
from perception_config import HSV_RANGES, COLOUR_BGR

# ============================================================================
# Grid cell definitions — full-frame pixel coords [TL, TR, BL, BR]
# ============================================================================

GRID_CELLS: list[dict] = [
    {
        "name": "left_cell",
        "corners": [(664, 197), (920, 217), (669, 282), (916, 315)],
    },
    {
        "name": "right_cell",
        "corners": [(920, 217), (1237, 215), (916, 315), (1228, 297)],
    },
]

# ============================================================================
# Helpers
# ============================================================================

def _quad_mask(shape: tuple[int,int],
               corners: list[tuple[int,int]]) -> np.ndarray:
    """
    Boolean mask (H×W) True inside the quad defined by [TL, TR, BL, BR].
    Re-wound to TL→TR→BR→BL so it fills as a parallelogram, not an hourglass.
    """
    tl, tr, bl, br = corners
    pts = np.array([tl, tr, br, bl], dtype=np.int32).reshape(-1, 1, 2)
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask.astype(bool)


def compute_percentages(
    bgr_frame: np.ndarray,
    cells: list[dict] | None = None,
) -> list[dict]:
    """
    For each grid cell, count how many pixels fall into each colour class.

    Parameters
    ----------
    bgr_frame : Full-resolution BGR frame.
    cells     : List of cell dicts (name + corners). Defaults to GRID_CELLS.

    Returns
    -------
    List of dicts — one per cell — with keys: name, total_pixels, colours.
    """
    if cells is None:
        cells = GRID_CELLS

    ih, iw = bgr_frame.shape[:2]
    hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

    # Build a full-frame classification label array (strings)
    # We use the raw (non-clean) masks here for accurate pixel counts.
    label_img = np.full((ih, iw), "none", dtype=object)
    unclassified = np.ones((ih, iw), dtype=bool)

    for colour, ranges in HSV_RANGES.items():
        combined = np.zeros((ih, iw), dtype=np.uint8)
        for lo, hi in ranges:
            combined |= cv2.inRange(hsv_frame,
                                    np.array(lo, dtype=np.uint8),
                                    np.array(hi, dtype=np.uint8))
        matched = combined.astype(bool) & unclassified
        label_img[matched] = colour
        unclassified &= ~matched

    results = []

    for cell in cells:
        name    = cell["name"]
        corners = cell["corners"]

        quad = _quad_mask((ih, iw), corners)
        total = int(quad.sum())

        if total == 0:
            results.append({"name": name, "total_pixels": 0, "colours": {}})
            continue

        colour_counts: dict[str, int] = {c: 0 for c in HSV_RANGES}
        colour_counts["none"] = 0

        labels_in_quad = label_img[quad]
        for c in colour_counts:
            colour_counts[c] = int(np.sum(labels_in_quad == c))

        colours_table = {
            label: {"count": cnt, "pct": round(cnt / total * 100, 2)}
            for label, cnt in colour_counts.items()
        }
        results.append({
            "name": name,
            "total_pixels": total,
            "colours": colours_table,
        })

    return results


def build_debug_image(
    bgr_frame: np.ndarray,
    results: list[dict],
    cells: list[dict] | None = None,
) -> np.ndarray:
    """
    Render the debug window: white background, pixels inside each quad painted
    with their classification colour, corner dots + labels, legend.
    """
    if cells is None:
        cells = GRID_CELLS

    ih, iw = bgr_frame.shape[:2]
    hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

    all_corners = [c for cell in cells for c in cell["corners"]]
    if not all_corners:
        return np.full((100, 100, 3), 255, dtype=np.uint8)

    margin = 40
    min_x = max(0, min(c[0] for c in all_corners) - margin)
    min_y = max(0, min(c[1] for c in all_corners) - margin)
    max_x = min(iw, max(c[0] for c in all_corners) + margin)
    max_y = min(ih, max(c[1] for c in all_corners) + margin)
    cw, ch = max_x - min_x, max_y - min_y

    canvas = np.full((ch, cw, 3), 255, dtype=np.uint8)

    for cell in cells:
        corners = cell["corners"]
        quad = _quad_mask((ih, iw), corners)
        unclassified = quad.copy()

        for colour, ranges in HSV_RANGES.items():
            combined = np.zeros((ih, iw), dtype=np.uint8)
            for lo, hi in ranges:
                combined |= cv2.inRange(hsv_frame,
                                        np.array(lo, dtype=np.uint8),
                                        np.array(hi, dtype=np.uint8))
            matched = quad & combined.astype(bool) & unclassified
            unclassified &= ~matched
            bgr = COLOUR_BGR[colour]
            canvas[matched[min_y:max_y, min_x:max_x]] = bgr

        canvas[unclassified[min_y:max_y, min_x:max_x]] = COLOUR_BGR["none"]

        # Quad outline + corner dots
        tl, tr, bl, br = cell["corners"]
        local = [(x - min_x, y - min_y) for x, y in [tl, tr, br, bl]]
        poly = np.array(local, dtype=np.int32)
        cv2.polylines(canvas, [poly], True, (255, 255, 255), 1)

        for (lx, ly), (ox, oy) in zip(
                [(x - min_x, y - min_y) for x, y in cell["corners"]],
                cell["corners"]):
            cv2.circle(canvas, (lx, ly), 5, (30, 30, 30), -1)
            cv2.circle(canvas, (lx, ly), 5, (255, 255, 255), 1)
            label = f"({ox},{oy})"
            tx = min(lx + 8, cw - len(label) * 7)
            ty = max(ly - 8, 12)
            cv2.putText(canvas, label, (tx, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (230, 230, 230),
                        1, cv2.LINE_AA)

    # Legend
    items = list(COLOUR_BGR.items())
    lx0 = 6
    ly0 = ch - len(items) * 16 - 6
    for i, (name, bgr) in enumerate(items):
        ly = ly0 + i * 16
        cv2.rectangle(canvas, (lx0, ly), (lx0 + 12, ly + 12), bgr, -1)
        cv2.rectangle(canvas, (lx0, ly), (lx0 + 12, ly + 12), (100, 100, 100), 1)
        cv2.putText(canvas, name, (lx0 + 16, ly + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (30, 30, 30), 1, cv2.LINE_AA)

    return canvas


def print_results(results: list[dict]) -> None:
    sep = "─" * 52
    print(sep)
    for box in results:
        print(f"  Box: {box['name']}   ({box['total_pixels']} pixels)")
        if not box["colours"]:
            print("    [no pixels — check corners are within frame]")
            continue
        print(f"  {'Colour':<10}  {'Count':>7}  {'Percent':>8}")
        print(f"  {'──────':<10}  {'─────':>7}  {'───────':>8}")
        for label, info in box["colours"].items():
            bar = "█" * int(info["pct"] / 2)
            print(f"  {label:<10}  {info['count']:>7}  {info['pct']:>7.2f}%  {bar}")
        print()
    print(sep)


# ============================================================================
# ROS2 node
# ============================================================================

class BoxPercentagesNode(Node):
    """
    Subscribes to the camera color image, computes per-cell colour percentages
    and publishes JSON results + a debug image.
    """

    def __init__(self, color_topic: str = "/camera/camera/color/image_raw"):
        super().__init__("box_percentages")
        self._bridge = CvBridge()

        self._sub = self.create_subscription(
            Image, color_topic, self._cb, 10)

        self._pub_pct = self.create_publisher(
            String, "/jenga/box_percentages", 10)
        self._pub_img = self.create_publisher(
            Image, "/jenga/box_debug_image", 10)

        self.get_logger().info("BoxPercentagesNode ready")

    def _cb(self, msg: Image) -> None:
        bgr = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        results = compute_percentages(bgr)

        pct_msg = String()
        pct_msg.data = json.dumps(results)
        self._pub_pct.publish(pct_msg)

        debug_img = build_debug_image(bgr, results)
        self._pub_img.publish(
            self._bridge.cv2_to_imgmsg(debug_img, encoding="bgr8"))


# ============================================================================
# Entry points
# ============================================================================

def main_ros():
    rclpy.init()
    node = BoxPercentagesNode()
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

    results = compute_percentages(bgr)
    print_results(results)

    debug = build_debug_image(bgr, results)
    cv2.namedWindow("Box percentages", cv2.WINDOW_NORMAL)
    cv2.imshow("Box percentages", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_standalone(sys.argv[1])
    elif _ROS_AVAILABLE:
        main_ros()
    else:
        print("Usage: python box_percentages.py <image_path>")
        sys.exit(1)
