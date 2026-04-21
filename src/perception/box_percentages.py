"""
box_percentages.py
------------------
Per-cell colour percentages and single-layer tower analysis.

Standalone use
--------------
    python box_percentages.py path/to/image.png
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

from colour_identification import classify_frame, compute_roi
from perception_config import HSV_RANGES, COLOUR_BGR, DIVIDE_LINE

# ---------------------------------------------------------------------------
# Grid cell definitions — full-frame pixel coords [TL, TR, BL, BR]
# ---------------------------------------------------------------------------
from perception_config import HSV_RANGES, COLOUR_BGR, DIVIDE_LINE, GRID_CORNERS

LAYER_CELLS: list[list[dict]] = [
    [
        {"name": "left_cell",  "corners": [GRID_CORNERS[r][0], GRID_CORNERS[r][1], GRID_CORNERS[r+1][0], GRID_CORNERS[r+1][1]]},
        {"name": "right_cell", "corners": [GRID_CORNERS[r][1], GRID_CORNERS[r][2], GRID_CORNERS[r+1][1], GRID_CORNERS[r+1][2]]},
    ]
    for r in range(len(GRID_CORNERS) - 1)
    if None not in GRID_CORNERS[r] and None not in GRID_CORNERS[r + 1]
]

GRID_CELLS: list[dict] = [cell for layer in LAYER_CELLS for cell in layer]

DOMINANT_PCT = 55.0  # above this → side-on face
MIN_COLOUR_PCT = 10.0  # colour must cover at least this % of the cell to count

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _quad_mask(shape: tuple[int, int], corners: list[tuple[int, int]]) -> np.ndarray:
    """Boolean mask (H×W) True inside the quad defined by [TL, TR, BL, BR]."""
    tl, tr, bl, br = corners
    pts = np.array([tl, tr, br, bl], dtype=np.int32).reshape(-1, 1, 2)
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask.astype(bool)


def _divide_x_per_row(ih: int) -> np.ndarray:
    """Return an (ih,) array of interpolated divide-line x values per image row."""
    (lx1, ly1), (lx2, ly2) = DIVIDE_LINE
    t = np.clip((np.arange(ih) - ly1) / (ly2 - ly1), 0.0, 1.0)
    return (lx1 + t * (lx2 - lx1)).astype(np.float32)


# ---------------------------------------------------------------------------
# Percentages
# ---------------------------------------------------------------------------

def compute_percentages(bgr_frame: np.ndarray,
                        cells: list[dict] | None = None) -> list[dict]:
    """Return per-cell colour percentage dicts for each cell in cells."""
    if cells is None:
        cells = GRID_CELLS

    ih, iw = bgr_frame.shape[:2]
    hsv = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

    label_img    = np.full((ih, iw), "none", dtype=object)
    unclassified = np.ones((ih, iw), dtype=bool)

    for colour, ranges in HSV_RANGES.items():
        combined = np.zeros((ih, iw), dtype=np.uint8)
        for lo, hi in ranges:
            combined |= cv2.inRange(hsv, np.array(lo, dtype=np.uint8),
                                         np.array(hi, dtype=np.uint8))
        matched = combined.astype(bool) & unclassified
        label_img[matched] = colour
        unclassified &= ~matched

    results = []
    for cell in cells:
        quad  = _quad_mask((ih, iw), cell["corners"])
        total = int(quad.sum())
        if total == 0:
            results.append({"name": cell["name"], "total_pixels": 0, "colours": {}})
            continue
        labels = label_img[quad]
        colours_table = {
            c: {"count": int(np.sum(labels == c)),
                "pct":   round(float(np.sum(labels == c)) / total * 100, 2)}
            for c in list(HSV_RANGES.keys()) + ["none"]
        }
        results.append({"name": cell["name"], "total_pixels": total,
                        "colours": colours_table})
    return results


# ---------------------------------------------------------------------------
# Layer analysis
# ---------------------------------------------------------------------------

def _colour_centroids(bgr_frame: np.ndarray, cell: dict) -> dict[str, float]:
    ih, iw = bgr_frame.shape[:2]
    hsv      = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)
    quad     = _quad_mask((ih, iw), cell["corners"])
    divide_x = _divide_x_per_row(ih)
    total    = int(quad.sum())

    centroids: dict[str, float] = {}
    for colour, ranges in HSV_RANGES.items():
        combined = np.zeros((ih, iw), dtype=np.uint8)
        for lo, hi in ranges:
            combined |= cv2.inRange(hsv, np.array(lo, dtype=np.uint8),
                                         np.array(hi, dtype=np.uint8))
        mask = quad & combined.astype(bool)
        ys, xs = np.where(mask)
        if len(xs) == 0:
            continue
        if len(xs) / total * 100 < MIN_COLOUR_PCT:
            continue
        centroids[colour] = float(np.mean(xs)) - float(divide_x[int(np.mean(ys))])
    return centroids

def analyse_layer(bgr_frame: np.ndarray,
                  left_result: dict, right_result: dict,
                  left_cell: dict,  right_cell: dict) -> dict:
    """
    Determine orientation and block positions for one layer.

    Returns
    -------
    {
        "orientation": "left" | "right",
        "blocks": [
            {"colour": str, "position": float, "present": bool},
            ...
        ]  # sorted front-to-back (smallest abs distance from divide line first)
    }
    """
    def _max_pct(result: dict) -> float:
        pcts = [i["pct"] for c, i in result["colours"].items() if c != "none"]
        return max(pcts, default=0.0)

    left_dom  = _max_pct(left_result)  >= DOMINANT_PCT
    right_dom = _max_pct(right_result) >= DOMINANT_PCT

    if right_dom and not left_dom:
        orientation, endon_cell = "left",  left_cell
    elif left_dom and not right_dom:
        orientation, endon_cell = "right", right_cell
    else:
        # Ambiguous — treat the less-dominant side as end-on
        if _max_pct(left_result) <= _max_pct(right_result):
            orientation, endon_cell = "left",  left_cell
        else:
            orientation, endon_cell = "right", right_cell

    centroids = _colour_centroids(bgr_frame, endon_cell)
    blocks = sorted(
        [{"colour": c, "position": dist, "present": True}
         for c, dist in centroids.items()],
        key=lambda b: abs(b["position"])
    )
    return {"orientation": orientation, "blocks": blocks}


# ---------------------------------------------------------------------------
# Debug visualisation
# ---------------------------------------------------------------------------

def build_debug_image(bgr_frame: np.ndarray, results: list[dict],
                      cells: list[dict] | None = None) -> np.ndarray:
    if cells is None:
        cells = GRID_CELLS

    ih, iw   = bgr_frame.shape[:2]
    hsv      = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

    all_corners = [c for cell in cells for c in cell["corners"]]
    margin  = 40
    min_x = max(0,  min(c[0] for c in all_corners) - margin)
    min_y = max(0,  min(c[1] for c in all_corners) - margin)
    max_x = min(iw, max(c[0] for c in all_corners) + margin)
    max_y = min(ih, max(c[1] for c in all_corners) + margin)
    cw, ch  = max_x - min_x, max_y - min_y
    canvas  = np.full((ch, cw, 3), 255, dtype=np.uint8)

    for cell in cells:
        quad         = _quad_mask((ih, iw), cell["corners"])
        unclassified = quad.copy()

        for colour, ranges in HSV_RANGES.items():
            combined = np.zeros((ih, iw), dtype=np.uint8)
            for lo, hi in ranges:
                combined |= cv2.inRange(hsv, np.array(lo, dtype=np.uint8),
                                             np.array(hi, dtype=np.uint8))
            matched = quad & combined.astype(bool) & unclassified
            unclassified &= ~matched
            canvas[matched[min_y:max_y, min_x:max_x]] = COLOUR_BGR[colour]

        canvas[unclassified[min_y:max_y, min_x:max_x]] = COLOUR_BGR["none"]

        tl, tr, bl, br = cell["corners"]
        poly = np.array([(x - min_x, y - min_y) for x, y in [tl, tr, br, bl]], dtype=np.int32)
        cv2.polylines(canvas, [poly], True, (180, 180, 180), 1)
        for ox, oy in cell["corners"]:
            lx, ly = ox - min_x, oy - min_y
            cv2.circle(canvas, (lx, ly), 4, (30, 30, 30), -1)

    # Legend
    for i, (name, bgr) in enumerate(COLOUR_BGR.items()):
        ly = ch - (len(COLOUR_BGR) - i) * 16
        cv2.rectangle(canvas, (6, ly), (18, ly + 12), bgr, -1)
        cv2.putText(canvas, name, (22, ly + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (30, 30, 30), 1, cv2.LINE_AA)

    return canvas


# ---------------------------------------------------------------------------
# ROS node
# ---------------------------------------------------------------------------

class BoxPercentagesNode(Node):
    def __init__(self, color_topic: str = "/camera/camera/color/image_raw"):
        super().__init__("box_percentages")
        self._bridge = CvBridge()
        self.create_subscription(Image, color_topic, self._cb, 10)
        self._pub_pct = self.create_publisher(String, "/jenga/box_percentages", 10)
        self._pub_img = self.create_publisher(Image,  "/jenga/box_debug_image", 10)
        self.get_logger().info("BoxPercentagesNode ready")

    def _cb(self, msg: Image) -> None:
        bgr     = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        results = compute_percentages(bgr)
        pct_msg = String()
        pct_msg.data = json.dumps(results)
        self._pub_pct.publish(pct_msg)
        self._pub_img.publish(
            self._bridge.cv2_to_imgmsg(build_debug_image(bgr, results), encoding="bgr8"))


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

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
    for cell in results:
        print(f"\n{cell['name']}  ({cell['total_pixels']} px)")
        for colour, info in cell["colours"].items():
            if info["pct"] > 0:
                print(f"  {colour:<10} {info['pct']:>6.1f}%")

    left  = next(r for r in results if r["name"] == "left_cell")
    right = next(r for r in results if r["name"] == "right_cell")
    lc    = next(c for c in GRID_CELLS if c["name"] == "left_cell")
    rc    = next(c for c in GRID_CELLS if c["name"] == "right_cell")
    layer = analyse_layer(bgr, left, right, lc, rc)
    print(f"\nOrientation: {layer['orientation']}")
    for i, b in enumerate(layer["blocks"]):
        print(f"  pos {i}: {b['colour']:<10}  dist={b['position']:+.1f}px")

    cv2.namedWindow("Box percentages", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Box percentages", 960, 300)
    cv2.imshow("Box percentages", build_debug_image(bgr, results))
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