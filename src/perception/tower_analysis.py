"""
tower_analysis.py
-----------------
Three responsibilities:
  1. Estimate the tower's depth (distance from camera) using the 95-98th
     percentile of valid depth pixels inside the detected hex polygon.
  2. Estimate the tower's lateral (left/right) offset from the camera centre
     in real-world mm using the camera's horizontal FOV.
"""
from __future__ import annotations

import numpy as np

from tower_mask import build_hex_mask
from perception_config import CAMERA_HFOV_DEG

# Pre-compute once at import time — used in every offset calculation
_TAN_HALF_HFOV = np.tan(np.deg2rad(CAMERA_HFOV_DEG / 2.0))


# ---------------------------------------------------------------------------
# Depth estimation
# ---------------------------------------------------------------------------

def estimate_tower_depth_stats(
    depth_mm: np.ndarray | None,
    pts: np.ndarray | None,
) -> dict | None:
    """
    Estimate the tower's depth as the mean of the 95th to 98th percentile
    """
    if depth_mm is None or pts is None:
        return None

    valid_pixels = (build_hex_mask(depth_mm.shape, pts) > 0) & (depth_mm > 0)
    if not np.any(valid_pixels):
        return None

    vals = depth_mm[valid_pixels].astype(np.float32)

    # Isolate the 95th–98th percentile band to target the tower back face
    p95  = float(np.percentile(vals, 95))
    p98  = float(np.percentile(vals, 98))
    band = vals[(vals >= p95) & (vals <= p98)]

    if band.size == 0:
        band = vals[-1:]

    depth_raw_mm = float(band.mean())

    return {
        "tower_depth_m": depth_raw_mm / 1000.0,
        "depth_mm": depth_raw_mm,
    }


# ---------------------------------------------------------------------------
# Lateral offset estimation
# ---------------------------------------------------------------------------

def estimate_tower_offset(
    pts: np.ndarray | None,
    image_width_px: int,
    depth_mm: float | None = None,
    image_shape: tuple[int, int] | None = None,
) -> dict | None:
    """
    Estimate the tower's left/right offset from the camera centre.

    Pinhole formula:
        lateral_mm =
            dx_px * (2 * depth_mm * tan(HFOV/2) / image_width)

    image_shape (h, w):
        when provided, centroid is computed from the filled mask
        rather than averaging polygon vertices.
    """
    if pts is None:
        return None

    center_x = image_width_px / 2.0

    # Pixel-level centroid is more accurate than vertex centroid
    hex_mask = build_hex_mask(image_shape, pts) > 0

    _, xs = np.where(hex_mask)

    centroid_x = (
        float(np.mean(xs))
        if len(xs) > 0
        else float(np.mean(pts[:, 0]))
    )

    dx_px = centroid_x - center_x

    lateral_mm = None

    if depth_mm is not None:
        mm_per_px = (
            2.0 * depth_mm * _TAN_HALF_HFOV / image_width_px
        )

        lateral_mm = dx_px * mm_per_px

    return {
        "centroid_x_px": centroid_x,
        "dx_px": dx_px,
        "lateral_mm": lateral_mm,
    }