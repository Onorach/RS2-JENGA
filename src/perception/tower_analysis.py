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

    # Return a view slightly larger than the detected hex area.
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
    """
    Human-readable reason when ``estimate_tower_depth_stats`` is None, for live debugging.
    """
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
    return "internal error"  # stats should be non-None if we reach here


def estimate_tower_depth_stats(depth_mm: np.ndarray | None, pts: np.ndarray | None) -> dict | None:
    """Estimate tower depth as mean of the 95th-98th percentile band inside the hex."""
    if depth_mm is None or pts is None:
        return None

    hex_mask = build_hex_mask(depth_mm.shape, pts) > 0
    valid_depth = depth_mm > 0
    used = hex_mask & valid_depth
    if not np.any(used):
        return None

    depth_used_m = depth_mm[used].astype(np.float32) / 1000.0
    sorted_depth_m = np.sort(depth_used_m)
    n = int(sorted_depth_m.size)
    i95 = min(n - 1, max(0, int(np.floor(0.95 * (n - 1)))))
    i98 = min(n, max(i95 + 1, int(np.ceil(0.98 * (n - 1))) + 1))
    band = sorted_depth_m[i95:i98]
    if band.size == 0:
        band = sorted_depth_m[-1:]
    return {
        "tower_depth_m": float(band.mean()),
    }


def estimate_tower_offset(
    pts: np.ndarray | None,
    image_width_px: int,
    depth_m: float | None,
) -> dict | None:
    """Estimate left/right tower offset from camera center."""
    if pts is None:
        return None

    centroid_x = float(np.mean(pts[:, 0]))
    center_x = (image_width_px - 1) / 2.0
    dx_px = centroid_x - center_x
    angle_deg = (dx_px / image_width_px) * CAMERA_HFOV_DEG

    lateral_m = None
    if depth_m is not None:
        lateral_m = float(depth_m * np.tan(np.deg2rad(angle_deg)))

    return {
        "centroid_x_px": centroid_x,
        "dx_px": dx_px,
        "lateral_m": lateral_m,
    }