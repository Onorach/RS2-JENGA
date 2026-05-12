"""
tower_analysis.py
-----------------
Depth display and tower depth/offset estimation utilities.
"""
from __future__ import annotations

import cv2
import numpy as np

from tower_mask import build_hex_mask
from perception_config import CAMERA_HFOV_DEG, TOWER_ANALYSIS_DEPTH_PAD_PX

# Precomputed once — must match the value used in layer_analysis.py
_TAN_HALF_HFOV = np.tan(np.deg2rad(CAMERA_HFOV_DEG / 2.0))


def build_depth_feed_display(
    depth_mm: np.ndarray | None,
    bgr_shape: tuple[int, int, int],
    pts: np.ndarray | None,
) -> np.ndarray:
    """Render depth only inside the detected hex, with invalid-pixel highlighting."""
    h, w = bgr_shape[:2]
    if depth_mm is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.putText(canvas, "Depth feed unavailable", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (180, 180, 180), 2, cv2.LINE_AA)
        return canvas

    if pts is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.putText(canvas, "Hex not detected", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (180, 180, 180), 2, cv2.LINE_AA)
        return canvas

    in_hex = build_hex_mask(depth_mm.shape, pts) > 0
    valid = (depth_mm > 0) & in_hex
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    if np.any(valid):
        depth_m = depth_mm.astype(np.float32) / 1000.0
        d_min = float(np.percentile(depth_m[valid], 5))
        d_max = float(np.percentile(depth_m[valid], 95))
        if d_max <= d_min:
            d_max = d_min + 1e-6
        depth_norm = np.clip((depth_m - d_min) / (d_max - d_min), 0.0, 1.0)
        depth_u8 = (depth_norm * 255).astype(np.uint8)
        heatmap = cv2.applyColorMap(depth_u8, cv2.COLORMAP_JET)
        canvas[valid] = heatmap[valid]

    invalid_in_hex = in_hex & (~valid)
    canvas[invalid_in_hex] = (255, 0, 255)
    cv2.polylines(canvas, [pts], isClosed=True, color=(255, 255, 255), thickness=2)
    valid_n = int(valid.sum())
    total_n = int(in_hex.sum())
    cv2.putText(canvas, f"Depth valid in hex: {valid_n}/{total_n}", (12, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    x_min = max(0, int(np.min(pts[:, 0])) - TOWER_ANALYSIS_DEPTH_PAD_PX)
    x_max = min(w, int(np.max(pts[:, 0])) + TOWER_ANALYSIS_DEPTH_PAD_PX)
    y_min = max(0, int(np.min(pts[:, 1])) - TOWER_ANALYSIS_DEPTH_PAD_PX)
    y_max = min(h, int(np.max(pts[:, 1])) + TOWER_ANALYSIS_DEPTH_PAD_PX)
    return canvas[y_min:y_max, x_min:x_max]


def explain_tower_depth_skip(
    bgr: np.ndarray,
    depth_mm: np.ndarray | None,
    pts: np.ndarray | None,
) -> str:
    if depth_mm is None:
        return (
            "no depth image (enable depth in rs_launch, subscribe to "
            "aligned_depth_to_color, and ensure encoding is 16UC1/32FC1)"
        )
    hc, wc = bgr.shape[:2]
    hd, wd = depth_mm.shape[:2]
    if (hc, wc) != (hd, wd):
        return (
            f"depth {wd}x{hd} != colour {wc}x{hc} — use aligned depth-to-colour, not raw depth"
        )
    if pts is None:
        return "no tower hex detected (contrast/ROI; tune tower_mask in perception_config)"

    hex_mask = build_hex_mask(depth_mm.shape, pts) > 0
    valid = (depth_mm > 0) & hex_mask
    if not np.any(valid):
        return "zero/invalid depth inside hex (out of range, IR glare, or reflectivity)"
    return "internal error"


def estimate_tower_depth_stats(depth_mm: np.ndarray | None, pts: np.ndarray | None) -> dict | None:
    """Estimate tower depth as mean of the 95th-98th percentile band inside the hex."""
    if depth_mm is None or pts is None:
        return None

    hex_mask = build_hex_mask(depth_mm.shape, pts) > 0
    valid_depth = depth_mm > 0
    used = hex_mask & valid_depth
    if not np.any(used):
        return None

    depth_used_mm = depth_mm[used].astype(np.float32)
    sorted_mm = np.sort(depth_used_mm)
    n = int(sorted_mm.size)
    i95 = min(n - 1, max(0, int(np.floor(0.95 * (n - 1)))))
    i98 = min(n, max(i95 + 1, int(np.ceil(0.98 * (n - 1))) + 1))
    band = sorted_mm[i95:i98]
    if band.size == 0:
        band = sorted_mm[-1:]
    depth_raw_mm = float(band.mean())
    return {
        "tower_depth_m": depth_raw_mm / 1000.0,
        "depth_mm": depth_raw_mm,
    }


def estimate_tower_offset(
    pts: np.ndarray | None,
    image_width_px: int,
    depth_mm: float | None = None,
    depth_m: float | None = None,    # legacy — converted automatically
    image_shape: tuple[int, int] | None = None,
) -> dict | None:
    """
    Estimate the tower's left/right offset from the camera centre in mm.

    The lateral conversion uses the identical pinhole formula to layer_analysis.py::

        mm_per_px  = 2 * depth_mm * tan(HFOV/2) / image_width_px
        lateral_mm = dx_px * mm_per_px

    Centroid x
    ----------
    When ``image_shape`` (h, w) is supplied, centroid_x is the mean x over
    **all pixels inside the hex mask** — i.e. the mean x of the whole visible
    tower face.  This is the correct reference for robot positioning.

    Without image_shape the fallback is the mean of the 6 hex vertex
    x-coordinates, which is less stable.  Always pass image_shape.

    Parameters
    ----------
    pts            : (N, 2) int32 hex polygon vertices from tower_mask
    image_width_px : full frame width in pixels
    depth_mm       : tower depth in mm — pass estimate_tower_depth_stats["depth_mm"]
    depth_m        : legacy metres kwarg — ignored when depth_mm is given
    image_shape    : (h, w) of the full colour frame — pass bgr.shape[:2]

    Returns
    -------
    {
        "centroid_x_px" : float,   # mean x of hex pixels in frame coords
        "dx_px"         : float,   # signed offset from frame centre (+ = right)
        "lateral_mm"    : float,   # signed lateral offset in mm   (+ = right)
        "lateral_m"     : float,   # same in metres (legacy compat)
    }
    or None if pts is None.
    """
    if pts is None:
        return None

    # Normalise depth to mm regardless of which kwarg the caller used
    if depth_mm is None and depth_m is not None:
        depth_mm = depth_m * 1000.0

    center_x = (image_width_px - 1) / 2.0

    if image_shape is not None:
        # Mean over every pixel inside hex — the mean x of the whole tower
        hex_mask = build_hex_mask(image_shape, pts) > 0
        _, xs = np.where(hex_mask)
        centroid_x = float(np.mean(xs)) if len(xs) > 0 else float(np.mean(pts[:, 0]))
    else:
        # Less accurate fallback — pass image_shape to avoid this
        centroid_x = float(np.mean(pts[:, 0]))

    dx_px = centroid_x - center_x

    lateral_mm = None
    if depth_mm is not None:
        # Same formula as layer_analysis.py block lateral calculation
        mm_per_px  = 2.0 * depth_mm * _TAN_HALF_HFOV / image_width_px
        lateral_mm = dx_px * mm_per_px

    return {
        "centroid_x_px": centroid_x,
        "dx_px":         dx_px,
        "lateral_mm":    lateral_mm,
        "lateral_m":     lateral_mm / 1000.0 if lateral_mm is not None else None,
    }