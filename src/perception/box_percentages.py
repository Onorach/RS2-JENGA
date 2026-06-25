"""
box_percentages.py
------------------
Per-cell colour percentages used by the layer analysis pipeline.

Standalone use
--------------
    python box_percentages.py path/to/image.png
"""
from __future__ import annotations

import json

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

from colour_identification import frame_colour_mask
from centre_seam import closest_depth_column
from camera_image_geometry import endon_outside_edge_x as _geometry_outside_edge_x
from camera_image_geometry import near_face_x_mask
from perception_config import HSV_RANGES, COLOUR_BGR, NEAR_FACE_SEAM_X_STAT

DOMINANT_PCT      = 55.0   # Above this → side-on face.
MIN_COLOUR_PCT    = 10.0   # Colour must cover at least this % of the cell to count.
MIN_COLOUR_PIXELS = 50     # Absolute floor regardless of cell size.

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _quad_mask(shape: tuple[int, int], corners: list[tuple[int, int]]) -> np.ndarray:
    """Boolean mask (H×W) True inside the quad defined by [TL, TR, BL, BR]."""
    tl, tr, bl, br = corners
    pts = np.array([tl, tr, br, bl], dtype=np.int32).reshape(-1, 1, 2)
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask.astype(bool)


def endon_outside_edge_x(cell: dict, orientation: str) -> float:
    """Image x of the tower's outside face edge on the end-on cell quad."""
    return _geometry_outside_edge_x(cell, orientation)


def _lane_strip_masks(shape: tuple[int, int], cell: dict) -> list[np.ndarray]:
    """Three boolean masks (front/mid/back lanes, left-to-right in image space)."""
    ih, iw = shape
    corners = cell["corners"]
    tl, tr, bl, br = corners
    x_left = (tl[0] + bl[0]) / 2.0
    x_right = (tr[0] + br[0]) / 2.0
    lane_w = (x_right - x_left) / 3.0
    quad = _quad_mask(shape, corners)
    x_grid = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    masks: list[np.ndarray] = []
    for lane in range(3):
        x0 = x_left + lane * lane_w
        x1 = x_left + (lane + 1) * lane_w
        if lane < 2:
            masks.append(quad & (x_grid >= x0) & (x_grid < x1))
        else:
            masks.append(quad & (x_grid >= x0) & (x_grid <= x1))
    return masks


# ---------------------------------------------------------------------------
# Per-cell colour percentages
# ---------------------------------------------------------------------------

def compute_percentages(bgr_frame: np.ndarray, cells: list[dict]) -> list[dict]:
    """Return per-cell colour percentage dicts for each cell."""
    ih, iw = bgr_frame.shape[:2]

    label_img    = np.full((ih, iw), "none", dtype=object)
    unclassified = np.ones((ih, iw), dtype=bool)

    for colour in HSV_RANGES:
        matched = frame_colour_mask(bgr_frame, colour) & unclassified
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
# Per-cell colour statistics used by layer_analysis
# ---------------------------------------------------------------------------

def colour_mean_x_in_cell(
    bgr_frame: np.ndarray,
    cell: dict,
    depth_frame: np.ndarray | None = None,
    target_depth_mm: float | None = None,
    depth_tolerance_mm: float = 40.0,
) -> dict[str, float]:
    """
    Mean image-space x-coordinate per colour inside cell.

    Only colours covering at least MIN_COLOUR_PCT (or MIN_COLOUR_PIXELS) are
    returned.  Used to assign blocks to lanes left-to-right on the end-on face.

    Optional depth gating
    ---------------------
    When depth_frame and target_depth_mm are supplied, each colour's pixel set
    is filtered to pixels within target_depth_mm ± depth_tolerance_mm.  This
    removes side-face pixels from adjacent layers that share the same colour
    but sit at a different depth, which would otherwise bias mean-x outward.
    The percentage threshold is evaluated on the un-gated mask so partially-
    visible back blocks are not inadvertently rejected.
    """
    ih, iw = bgr_frame.shape[:2]
    quad   = _quad_mask((ih, iw), cell["corners"])
    total  = int(quad.sum())
    if total == 0:
        return {}

    if depth_frame is not None and target_depth_mm is not None:
        df = depth_frame.astype(np.float32)
        depth_gate: np.ndarray | None = (
            (df > 0)
            & np.isfinite(df)
            & (np.abs(df - target_depth_mm) <= depth_tolerance_mm)
        )
    else:
        depth_gate = None

    out: dict[str, float] = {}

    for colour in HSV_RANGES:
        colour_mask = quad & frame_colour_mask(bgr_frame, colour)

        n_colour = int(colour_mask.sum())
        if n_colour < MIN_COLOUR_PIXELS:
            continue
        if n_colour / total * 100.0 < MIN_COLOUR_PCT:
            continue

        if depth_gate is not None:
            gated = colour_mask & depth_gate
            _, gated_xs = np.where(gated)
            if len(gated_xs) >= MIN_COLOUR_PIXELS:
                out[colour] = float(np.mean(gated_xs))
                continue
            # Depth gate removed too many pixels — fall back to un-gated mean.

        _, xs = np.where(colour_mask)
        out[colour] = float(np.mean(xs))

    return out


def _colour_mean_xy_in_region(
    bgr_frame: np.ndarray,
    region_mask: np.ndarray,
    depth_gate: np.ndarray | None,
) -> dict[str, tuple[float, float]]:
    """Mean (x, y) per colour blob inside region_mask (all matching pixels)."""
    total = int(region_mask.sum())
    if total == 0:
        return {}

    out: dict[str, tuple[float, float]] = {}
    for colour in HSV_RANGES:
        colour_mask = region_mask & frame_colour_mask(bgr_frame, colour)
        n_colour = int(colour_mask.sum())
        if n_colour < MIN_COLOUR_PIXELS:
            continue
        if n_colour / total * 100.0 < MIN_COLOUR_PCT:
            continue

        if depth_gate is not None:
            gated = colour_mask & depth_gate
            ys, xs = np.where(gated)
            if len(xs) >= MIN_COLOUR_PIXELS:
                out[colour] = (float(np.mean(xs)), float(np.mean(ys)))
                continue

        ys, xs = np.where(colour_mask)
        out[colour] = (float(np.mean(xs)), float(np.mean(ys)))

    return out


def _depth_split_x_from_closest_pixels(
    depth_frame: np.ndarray,
    mask: np.ndarray,
) -> float | None:
    """
    Estimate split x for a colour blob using the closest (smallest) depth.

    Delegates to centre_seam.closest_depth_column, the single shared
    closest-to-camera-column primitive (here gated to exactly the minimum depth).
    """
    split_x, _ = closest_depth_column(
        depth_frame, mask, depth_tol_mm=0.0, stat=NEAR_FACE_SEAM_X_STAT,
    )
    return split_x


def colour_mean_xy_in_cell(
    bgr_frame: np.ndarray,
    cell: dict,
    depth_frame: np.ndarray | None = None,
    target_depth_mm: float | None = None,
    depth_tolerance_mm: float = 40.0,
    orientation: str | None = None,
    use_outside_of_split: bool = False,
    robust_stat: str = "mean",
    require_split_for_output: bool = False,
) -> dict[str, tuple[float, float]]:
    """
    Mean image-space centroid (x, y) per colour inside cell.

    Uses the same mask/depth-gating logic as colour_mean_x_in_cell so centroid
    markers match the pixels used for depth/offset estimates.
    """
    ih, iw = bgr_frame.shape[:2]
    quad = _quad_mask((ih, iw), cell["corners"])
    if int(quad.sum()) == 0:
        return {}

    if depth_frame is not None and target_depth_mm is not None:
        df = depth_frame.astype(np.float32)
        depth_gate: np.ndarray | None = (
            (df > 0)
            & np.isfinite(df)
            & (np.abs(df - target_depth_mm) <= depth_tolerance_mm)
        )
    else:
        depth_gate = None

    if (
        not use_outside_of_split
        or orientation not in ("left", "right")
        or depth_frame is None
    ):
        if use_outside_of_split and require_split_for_output:
            return {}
        return _colour_mean_xy_in_region(bgr_frame, quad, depth_gate)

    total = int(quad.sum())
    out: dict[str, tuple[float, float]] = {}
    use_median = str(robust_stat).strip().lower() == "median"
    x_grid = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))

    for colour in HSV_RANGES:
        colour_mask = quad & frame_colour_mask(bgr_frame, colour)
        n_colour = int(colour_mask.sum())
        if n_colour < MIN_COLOUR_PIXELS:
            continue
        if n_colour / total * 100.0 < MIN_COLOUR_PCT:
            continue

        active_mask = colour_mask
        if depth_gate is not None:
            gated = colour_mask & depth_gate
            if int(gated.sum()) >= MIN_COLOUR_PIXELS:
                active_mask = gated

        split_x = _depth_split_x_from_closest_pixels(depth_frame, active_mask)
        if split_x is not None:
            outside_mask = active_mask & near_face_x_mask(
                x_grid, float(split_x), orientation,
            )
            ys, xs = np.where(outside_mask)
            if len(xs) >= max(10, MIN_COLOUR_PIXELS // 5):
                if use_median:
                    out[colour] = (float(np.median(xs)), float(np.median(ys)))
                else:
                    out[colour] = (float(np.mean(xs)), float(np.mean(ys)))
                continue
        if require_split_for_output:
            continue

        ys, xs = np.where(active_mask)
        if len(xs) == 0:
            continue
        if use_median:
            out[colour] = (float(np.median(xs)), float(np.median(ys)))
        else:
            out[colour] = (float(np.mean(xs)), float(np.mean(ys)))

    return out


def colour_depth_split_x_in_cell(
    bgr_frame: np.ndarray,
    depth_frame: np.ndarray | None,
    cell: dict,
) -> dict[str, float]:
    """
    Vertical split x per colour blob in a cell, using closest depth pixels.
    """
    if depth_frame is None:
        return {}

    ih, iw = bgr_frame.shape[:2]
    quad = _quad_mask((ih, iw), cell["corners"])
    total = int(quad.sum())
    if total == 0:
        return {}

    out: dict[str, float] = {}
    for colour in HSV_RANGES:
        colour_mask = quad & frame_colour_mask(bgr_frame, colour)
        n_colour = int(colour_mask.sum())
        if n_colour < MIN_COLOUR_PIXELS:
            continue
        if n_colour / total * 100.0 < MIN_COLOUR_PCT:
            continue

        split_x = _depth_split_x_from_closest_pixels(depth_frame, colour_mask)
        if split_x is not None:
            out[colour] = float(split_x)
    return out


def colour_mean_xy_per_lane_in_cell(
    bgr_frame: np.ndarray,
    cell: dict,
    depth_frame: np.ndarray | None = None,
    target_depth_mm: float | None = None,
    depth_tolerance_mm: float = 40.0,
) -> list[dict[str, tuple[float, float]]]:
    """
    Per-lane colour blob centroids: mean (x, y) of all pixels of each colour
    inside each front/mid/back lane strip of the end-on cell.
    """
    ih, iw = bgr_frame.shape[:2]
    lane_masks = _lane_strip_masks((ih, iw), cell)
    if not any(int(m.sum()) > 0 for m in lane_masks):
        return [{}, {}, {}]

    if depth_frame is not None and target_depth_mm is not None:
        df = depth_frame.astype(np.float32)
        depth_gate: np.ndarray | None = (
            (df > 0)
            & np.isfinite(df)
            & (np.abs(df - target_depth_mm) <= depth_tolerance_mm)
        )
    else:
        depth_gate = None

    return [_colour_mean_xy_in_region(bgr_frame, lane_mask, depth_gate) for lane_mask in lane_masks]


def colour_mean_depth_in_cell(
    bgr_frame: np.ndarray,
    depth_frame: np.ndarray,
    cell: dict,
) -> dict[str, float]:
    """Median depth (mm) per colour inside a cell.  Uses eroded masks for stability."""
    if depth_frame is None:
        return {}
    ih, iw = bgr_frame.shape[:2]
    quad   = _quad_mask((ih, iw), cell["corners"])
    total  = int(quad.sum())
    if total == 0:
        return {}

    kernel = np.ones((5, 5), np.uint8)
    out: dict[str, float] = {}

    for colour in HSV_RANGES:
        mask = quad & frame_colour_mask(bgr_frame, colour)
        mask = cv2.erode(mask.astype(np.uint8), kernel, iterations=2).astype(bool)

        if float(mask.sum()) / total * 100.0 < MIN_COLOUR_PCT:
            continue

        depth_values = depth_frame[mask]
        depth_values = depth_values[(depth_values > 0) & np.isfinite(depth_values)]

        if len(depth_values) < 20:
            continue

        out[colour] = float(np.median(depth_values))

    return out


# ---------------------------------------------------------------------------
# Debug visualisation
# ---------------------------------------------------------------------------

def build_debug_image(
    bgr_frame: np.ndarray,
    results: list[dict],
    cells: list[dict],
    tower: list[dict] | None = None,
    row_cells: list[tuple[dict, dict]] | None = None,
    frame_centre_x_px: float | None = None,
) -> np.ndarray:
    ih, iw = bgr_frame.shape[:2]

    # Use the full input crop (caller sets horizontal margin + top-of-frame height).
    min_x = 0
    min_y = 0
    max_x = iw
    max_y = ih
    cw, ch = max_x - min_x, max_y - min_y
    canvas = np.full((ch, cw, 3), 255, dtype=np.uint8)

    for cell in cells:
        quad         = _quad_mask((ih, iw), cell["corners"])
        unclassified = quad.copy()

        for colour in HSV_RANGES:
            matched = quad & frame_colour_mask(bgr_frame, colour) & unclassified
            unclassified &= ~matched
            canvas[matched[min_y:max_y, min_x:max_x]] = COLOUR_BGR[colour]

        canvas[unclassified[min_y:max_y, min_x:max_x]] = COLOUR_BGR["none"]

        tl, tr, bl, br = cell["corners"]
        poly = np.array([(x - min_x, y - min_y) for x, y in [tl, tr, br, bl]], dtype=np.int32)
        cv2.polylines(canvas, [poly], True, (180, 180, 180), 1)
        for ox, oy in cell["corners"]:
            cv2.circle(canvas, (ox - min_x, oy - min_y), 4, (30, 30, 30), -1)

    for i, (name, bgr) in enumerate(COLOUR_BGR.items()):
        ly = ch - (len(COLOUR_BGR) - i) * 16
        cv2.rectangle(canvas, (6, ly), (18, ly + 12), bgr, -1)
        cv2.putText(canvas, name, (22, ly + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (30, 30, 30), 1, cv2.LINE_AA)

    # Frame-center reference line (camera-frame center projected into this crop).
    cx_frame = (iw / 2.0) if frame_centre_x_px is None else float(frame_centre_x_px)
    cx_canvas = int(round(cx_frame - min_x))
    if 0 <= cx_canvas < cw:
        cv2.line(canvas, (cx_canvas, 0), (cx_canvas, ch - 1), (0, 0, 0), 1, cv2.LINE_AA)

    if tower and row_cells:
        n_layers = len(row_cells)
        for layer in tower:
            orientation = layer.get("orientation")
            layer_idx = layer.get("layer")
            blocks = layer.get("blocks", [])
            if orientation not in ("left", "right") or not isinstance(layer_idx, int):
                continue

            row_idx = (n_layers - 1) - layer_idx
            if row_idx < 0 or row_idx >= n_layers:
                continue

            for block in blocks:
                if not block.get("present"):
                    continue

                cx = block.get("mean_x_px")
                cy = block.get("mean_y_px")
                if cx is None or cy is None:
                    continue

                x = int(round(float(cx) - min_x))
                y = int(round(float(cy) - min_y))
                if not (0 <= x < cw and 0 <= y < ch):
                    continue

                split_x = block.get("depth_split_x_px")
                if split_x is not None:
                    sx = int(round(float(split_x) - min_x))
                    if 0 <= sx < cw:
                        y0 = max(0, y - 18)
                        y1 = min(ch - 1, y + 18)
                        cv2.line(canvas, (sx, y0), (sx, y1), (255, 255, 255), 1, cv2.LINE_AA)

                cv2.circle(canvas, (x, y), 6, (255, 255, 255), -1)
                cv2.circle(canvas, (x, y), 3, (0, 0, 0), -1)

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
