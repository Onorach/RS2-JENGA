"""
tower_mask.py
-------------
Finds the high-saturation foreground (the Jenga tower) and fits a
6-sided convex hull around it to use as a clean search region.
"""
from __future__ import annotations

import cv2
import numpy as np

from colour_identification import compute_roi

from perception_config import (
    TOWER_MASK_SAT_MIN,
    TOWER_MASK_BRIGHTNESS_MIN,
    TOWER_MASK_MORPH_CLOSE_PX,
    TOWER_MASK_MORPH_OPEN_PX,
    SEARCH_AREA_MARGIN,
)


def _odd(k: int) -> int:
    return k if k % 2 == 1 else k + 1


_HEX_VERTICES = 6
HEX_RECOMPUTE_INTERVAL = 10   # Recompute tower hex polygon every N frames (live + setup).


def _order_vertices_ccw(pts: np.ndarray) -> np.ndarray:
    """Sort polygon vertices counter-clockwise so polylines do not cross the shape."""
    pts = np.asarray(pts, dtype=np.float64).reshape(-1, 2)
    if len(pts) <= 2:
        return pts.astype(np.int32)
    centre = pts.mean(axis=0)
    order = np.argsort(np.arctan2(pts[:, 1] - centre[1], pts[:, 0] - centre[0]))
    return pts[order].astype(np.int32)


def _hex_from_hull_by_angle(hull: np.ndarray, n: int = _HEX_VERTICES) -> np.ndarray:
    """
    Pick n vertices on the convex hull by taking the outermost hull point in each
    angular sector around the hull centroid (stable 6-gon for tower outlines).
    """
    pts = hull.reshape(-1, 2).astype(np.float64)
    if len(pts) < 3:
        return pts.astype(np.int32)

    centre = pts.mean(axis=0)
    angles = np.arctan2(pts[:, 1] - centre[1], pts[:, 0] - centre[0])
    dists = np.hypot(pts[:, 0] - centre[0], pts[:, 1] - centre[1])

    used: set[int] = set()
    hex_pts: list[np.ndarray] = []
    for i in range(n):
        a0 = -np.pi + (2 * np.pi * i) / n
        a1 = -np.pi + (2 * np.pi * (i + 1)) / n
        if i == n - 1:
            in_wedge = (angles >= a0) | (angles < a1)
        else:
            in_wedge = (angles >= a0) & (angles < a1)
        candidates = np.flatnonzero(in_wedge)
        if candidates.size == 0:
            candidates = np.arange(len(pts))

        best_idx: int | None = None
        best_dist = -1.0
        for idx in candidates:
            if idx in used and candidates.size > 1:
                continue
            if dists[idx] > best_dist:
                best_dist = dists[idx]
                best_idx = int(idx)
        if best_idx is None:
            best_idx = int(candidates[np.argmax(dists[candidates])])
        used.add(best_idx)
        hex_pts.append(pts[best_idx])

    return _order_vertices_ccw(np.array(hex_pts))


def _approx_hex_vertices(hull: np.ndarray, target: int = _HEX_VERTICES) -> np.ndarray:
    """Simplify a convex hull to exactly ``target`` vertices when possible."""
    peri = cv2.arcLength(hull, True)
    if peri <= 0:
        return _hex_from_hull_by_angle(hull, target)

    best: np.ndarray | None = None
    best_delta = 10**9

    for factor in np.linspace(0.005, 0.5, 60):
        approx = cv2.approxPolyDP(hull, float(factor) * peri, True)
        n = len(approx)
        delta = abs(n - target)
        if delta < best_delta:
            best_delta = delta
            best = approx.reshape(-1, 2)
        if n == target:
            return _order_vertices_ccw(best)

    assert best is not None
    if len(best) == target:
        return _order_vertices_ccw(best)
    return _hex_from_hull_by_angle(hull, target)


def compute_saturation_mask(
    bgr: np.ndarray,
    *,
    sat_min: int | None = None,
    brightness_min: int | None = None,
    morph_close_px: int | None = None,
    morph_open_px: int | None = None,
) -> np.ndarray:
    """Return a binary mask (HxW uint8) of high-saturation, sufficiently bright pixels."""
    s_min = TOWER_MASK_SAT_MIN if sat_min is None else sat_min
    v_min = TOWER_MASK_BRIGHTNESS_MIN if brightness_min is None else brightness_min
    close_px = TOWER_MASK_MORPH_CLOSE_PX if morph_close_px is None else morph_close_px
    open_px = TOWER_MASK_MORPH_OPEN_PX if morph_open_px is None else morph_open_px

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    mask = (
        (hsv[:, :, 1] >= s_min)
        & (hsv[:, :, 2] >= v_min)
    ).astype(np.uint8) * 255

    if close_px > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(close_px),) * 2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    if open_px > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(open_px),) * 2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    return mask


def compute_hex_region(
    bgr: np.ndarray,
    roi_xywh: tuple[int, int, int, int] | None = None,
    *,
    sat_min: int | None = None,
    brightness_min: int | None = None,
    morph_close_px: int | None = None,
    morph_open_px: int | None = None,
) -> np.ndarray | None:
    """
    Find the largest high-saturation blob within the ROI and fit a
    6-sided polygon around it.
    """

    ih, iw = bgr.shape[:2]
    if roi_xywh is None:
        rx, ry, rw, rh = compute_roi(iw, ih)
    else:
        rx, ry, rw, rh = roi_xywh

    roi = bgr[ry:ry + rh, rx:rx + rw]

    mask = compute_saturation_mask(
        roi,
        sat_min=sat_min,
        brightness_min=brightness_min,
        morph_close_px=morph_close_px,
        morph_open_px=morph_open_px,
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)

    hull = cv2.convexHull(largest)
    pts = _order_vertices_ccw(_approx_hex_vertices(hull))
    if len(pts) != _HEX_VERTICES:
        return None

    pts[:, 0] += rx
    pts[:, 1] += ry

    return pts


def build_hex_mask(
    shape: tuple[int, int],
    pts: np.ndarray,
) -> np.ndarray:
    """Return a binary mask filled inside the polygon."""

    mask = np.zeros(shape[:2], dtype=np.uint8)

    cv2.fillPoly(mask, [pts], 255)

    return mask


def build_display(
    bgr: np.ndarray,
    pts: np.ndarray | None,
    centroid_x: float | None = None,
    roi_xywh: tuple[int, int, int, int] | None = None,
    *,
    sat_min: int | None = None,
    brightness_min: int | None = None,
    morph_close_px: int | None = None,
    morph_open_px: int | None = None,
) -> np.ndarray:
    """
    Draw the ROI box, polygon, centroid line,
    and saturation mask side by side.
    """

    ih, iw = bgr.shape[:2]
    if roi_xywh is None:
        rx, ry, rw, rh = compute_roi(iw, ih)
    else:
        rx, ry, rw, rh = roi_xywh

    # ---------------------------------------------------------
    # Right panel — saturation mask
    # ---------------------------------------------------------

    roi_mask = compute_saturation_mask(
        bgr[ry:ry + rh, rx:rx + rw],
        sat_min=sat_min,
        brightness_min=brightness_min,
        morph_close_px=morph_close_px,
        morph_open_px=morph_open_px,
    )

    sat_colour = np.zeros((ih, iw), dtype=np.uint8)

    sat_colour[ry:ry + rh, rx:rx + rw] = roi_mask

    sat_colour = cv2.cvtColor(
        sat_colour,
        cv2.COLOR_GRAY2BGR,
    )

    # ---------------------------------------------------------
    # Left panel — overlay
    # ---------------------------------------------------------

    overlay = bgr.copy()

    cv2.rectangle(
        overlay,
        (rx, ry),
        (rx + rw, ry + rh),
        (0, 255, 255),
        1,
    )

    if pts is not None:

        # Polygon outline
        cv2.polylines(
            overlay,
            [pts],
            isClosed=True,
            color=(0, 255, 255),
            thickness=2,
        )

        # Transparent polygon fill
        filled = overlay.copy()

        cv2.fillPoly(
            filled,
            [pts],
            (0, 255, 255),
        )

        cv2.addWeighted(
            filled,
            0.15,
            overlay,
            0.85,
            0,
            overlay,
        )

        # Vertex markers
        for i, (x, y) in enumerate(pts):

            cv2.circle(
                overlay,
                (x, y),
                5,
                (0, 200, 255),
                -1,
            )

            cv2.putText(
                overlay,
                str(i),
                (x + 6, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 200, 255),
                1,
                cv2.LINE_AA,
            )

        # -----------------------------------------------------
        # Centroid line
        # -----------------------------------------------------

        if centroid_x is not None:

            cx = int(round(centroid_x))

            cv2.line(
                overlay,
                (cx, 0),
                (cx, ih - 1),
                (255, 0, 255),
                2,
                cv2.LINE_AA,
            )

    return np.hstack([overlay, sat_colour])


def append_tower_info_panel(
    tower_view: np.ndarray,
    lines: list[str],
    *,
    line_colors: list[tuple[int, int, int]] | None = None,
) -> np.ndarray:
    """Stack a text strip below the tower finder image (overlay | mask)."""
    if not lines:
        return tower_view

    panel_w = tower_view.shape[1]
    line_h = 22
    panel_h = 10 + len(lines) * line_h
    panel = np.zeros((panel_h, panel_w, 3), dtype=np.uint8)
    panel[:] = (36, 36, 36)

    default_color = (220, 220, 220)
    for i, text in enumerate(lines):
        colour = default_color
        if line_colors is not None and i < len(line_colors):
            colour = line_colors[i]
        cv2.putText(
            panel,
            text,
            (10, 16 + i * line_h),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            colour,
            1,
            cv2.LINE_AA,
        )

    return np.vstack([tower_view, panel])


def crop_tower_finder_display(
    tower_disp: np.ndarray,
    roi_xywh: tuple[int, int, int, int],
) -> np.ndarray:
    """
    Crop overlay and mask panels to search area + SEARCH_AREA_MARGIN.

    Fixed window size (does not shrink/grow with the detected hex polygon).
    """
    rx, ry, rw, rh = roi_xywh
    panel_h, full_w = tower_disp.shape[:2]
    panel_w = full_w // 2

    mx = int(rw * SEARCH_AREA_MARGIN)
    my = int(rh * SEARCH_AREA_MARGIN)

    x_min = max(0, rx - mx)
    y_min = max(0, ry - my)
    x_max = min(panel_w, rx + rw + mx)
    y_max = min(panel_h, ry + rh + my)

    if x_max <= x_min or y_max <= y_min:
        return tower_disp

    left = tower_disp[y_min:y_max, x_min:x_max]
    right = tower_disp[y_min:y_max, panel_w + x_min : panel_w + x_max]
    return np.hstack([left, right])