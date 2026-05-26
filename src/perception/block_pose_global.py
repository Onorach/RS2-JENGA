"""
block_pose_global.py
--------------------
Helpers for building per-block camera/global poses from layer-analysis outputs.
"""

from __future__ import annotations

import numpy as np

from perception_config import (
    CAMERA_GLOBAL_POSITION_MM,
    BLOCK_YAW_DEG_ASSUMED,
)


def _display_lateral_mm(lateral_mm: float | None, orientation: str) -> float | None:
    """
    Return orientation-adjusted lateral offset used for pose_camera_mm y.
    """
    if lateral_mm is None:
        return None
    x_offset = -26.5 if orientation == "left" else 26.5
    return float(lateral_mm + x_offset)


def _assumed_orientation_xyzw() -> dict[str, float]:
    """
    Quaternion for fixed yaw-only orientation assumption.
    """
    half_yaw_rad = np.deg2rad(BLOCK_YAW_DEG_ASSUMED) / 2.0
    return {
        "x": 0.0,
        "y": 0.0,
        "z": float(np.sin(half_yaw_rad)),
        "w": float(np.cos(half_yaw_rad)),
    }


def build_block_pose_mm(
    *,
    depth_mm: float | None,
    lateral_mm: float | None,
    orientation: str,
    layer_idx: int,
) -> tuple[dict[str, object], dict[str, object]] | tuple[None, None]:
    """
    Build (pose_camera_mm, pose_global_mm) for a block.

    Returns (None, None) when required inputs are unavailable.
    """
    lateral_display_mm = _display_lateral_mm(lateral_mm, orientation)
    if depth_mm is None or lateral_display_mm is None:
        return None, None

    z_local_mm = 15.0 * (float(layer_idx) + 1.0) - 7.5
    x_local_mm = float(depth_mm)
    y_local_mm = float(lateral_display_mm)
    orientation_xyzw = _assumed_orientation_xyzw()

    pose_camera_mm: dict[str, object] = {
        "position": {
            "x": x_local_mm,
            "y": y_local_mm,
            "z": z_local_mm,
        },
        "orientation": orientation_xyzw,
    }
    pose_global_mm: dict[str, object] = {
        "position": {
            "x": x_local_mm + float(CAMERA_GLOBAL_POSITION_MM[0]),
            "y": y_local_mm + float(CAMERA_GLOBAL_POSITION_MM[1]),
            "z": z_local_mm + float(CAMERA_GLOBAL_POSITION_MM[2]),
        },
        "orientation": orientation_xyzw,
    }
    return pose_camera_mm, pose_global_mm

