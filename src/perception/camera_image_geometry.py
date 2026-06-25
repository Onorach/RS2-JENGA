"""
camera_image_geometry.py
------------------------
Optional image-space x convention helpers when CAMERA_MOUNT_FLIPPED is set.

World-frame pose export uses CAMERA_LOCAL_AXIS_SIGN in block_pose_global.py;
grid seam and centroid logic normally stay on the original image heuristics.
"""

from __future__ import annotations

import numpy as np

from perception_config import CAMERA_MOUNT_FLIPPED, NEAR_FACE_SEAM_X_STAT


def near_face_on_high_x_side(orientation: str) -> bool:
    """True when the near (outside) face of a layer sits on high image x."""
    return (orientation == "right") ^ bool(CAMERA_MOUNT_FLIPPED)


def seam_x_from_near_pixels(xv: np.ndarray, stat: str | None = None) -> float:
    """Summarise image-x of closest-to-camera pixels into a seam / split line."""
    if len(xv) == 0:
        raise ValueError("xv must be non-empty")
    mode = (stat or NEAR_FACE_SEAM_X_STAT).strip().lower()
    if mode == "max":
        return float(np.max(xv))
    if mode == "min":
        return float(np.min(xv))
    if mode == "median":
        return float(np.median(xv))
    return float(np.mean(xv))


def near_face_x_mask(x_grid: np.ndarray, split_x: float, orientation: str) -> np.ndarray:
    """Boolean mask of pixels on the near-face side of a depth split line."""
    if near_face_on_high_x_side(orientation):
        return x_grid >= float(split_x)
    return x_grid <= float(split_x)


def endon_side_x_mask(
    x_grid: np.ndarray,
    centre_seam_x: float,
    orientation: str,
) -> np.ndarray:
    """Boolean mask of the end-on half of a layer (correct side of centre seam)."""
    if near_face_on_high_x_side(orientation):
        return x_grid >= float(centre_seam_x)
    return x_grid <= float(centre_seam_x)


def clamp_centroid_to_endon_side(
    cx: float,
    centre_seam_x: float,
    orientation: str,
) -> float:
    """Clamp centroid x to the end-on half of the layer."""
    if near_face_on_high_x_side(orientation):
        return max(cx, float(centre_seam_x))
    return min(cx, float(centre_seam_x))


def clamp_centroid_to_near_face_side(
    cx: float,
    split_x: float,
    orientation: str,
) -> float:
    """Clamp centroid x to the near-face side of a depth split line."""
    if near_face_on_high_x_side(orientation):
        return max(cx, float(split_x))
    return min(cx, float(split_x))


def endon_outside_edge_x(cell: dict, orientation: str) -> float:
    """Image x of the tower outside-face edge on the end-on cell quad."""
    corners = cell["corners"]
    low_x = float(min(corners[0][0], corners[2][0]))
    high_x = float(max(corners[1][0], corners[3][0]))
    if near_face_on_high_x_side(orientation):
        return high_x
    return low_x


def outer_edge_x_on_endon_face(xs_side: np.ndarray, orientation: str) -> float:
    """Outermost x among end-on-face pixels toward the tower outside edge."""
    if len(xs_side) == 0:
        raise ValueError("xs_side must be non-empty")
    if near_face_on_high_x_side(orientation):
        return float(np.max(xs_side))
    return float(np.min(xs_side))


def penetration_span_px(
    centre_seam_x: float,
    outside_edge_x: float,
    orientation: str,
) -> float:
    """Positive span in px from outside tower edge to centre seam."""
    if near_face_on_high_x_side(orientation):
        return float(outside_edge_x - centre_seam_x)
    return float(centre_seam_x - outside_edge_x)


def penetration_from_outer_edge_px(
    outer_edge_x: float,
    centre_seam_x: float,
    orientation: str,
) -> float:
    """How far the detected outer edge sits from outside toward the seam."""
    if near_face_on_high_x_side(orientation):
        return float(outer_edge_x - centre_seam_x)
    return float(centre_seam_x - outer_edge_x)
