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
    SEARCH_AREA_MARGIN,
)


def _odd(k: int) -> int:
    return k if k % 2 == 1 else k + 1


def compute_saturation_mask(
    bgr: np.ndarray,
    *,
    sat_min: int | None = None,
    brightness_min: int | None = None,
) -> np.ndarray:
    """Return a binary mask (HxW uint8) of high-saturation, sufficiently bright pixels."""
    s_min = TOWER_MASK_SAT_MIN if sat_min is None else sat_min
    v_min = TOWER_MASK_BRIGHTNESS_MIN if brightness_min is None else brightness_min

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    mask = (
        (hsv[:, :, 1] >= s_min)
        & (hsv[:, :, 2] >= v_min)
    ).astype(np.uint8) * 255

    return mask


def compute_hex_region(
    bgr: np.ndarray,
    roi_xywh: tuple[int, int, int, int] | None = None,
    *,
    sat_min: int | None = None,
    brightness_min: int | None = None,
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
        roi, sat_min=sat_min, brightness_min=brightness_min,
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

    peri = cv2.arcLength(hull, True)

    for factor in np.arange(0.02, 0.5, 0.01):
        approx = cv2.approxPolyDP(
            hull,
            factor * peri,
            True,
        )

        if len(approx) <= 6:
            break

    pts = approx.reshape(-1, 2).astype(np.int32)

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

            cv2.putText(
                overlay,
                f"centroid_x={cx}px",
                (cx + 8, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 0, 255),
                2,
                cv2.LINE_AA,
            )


    return np.hstack([overlay, sat_colour])


def crop_tower_finder_display(
    tower_disp: np.ndarray,
    pts: np.ndarray | None,
    frame_width: int,
    frame_height: int,
) -> np.ndarray:
    """
    Crop the tower finder display around the polygon.
    """

    if pts is None:
        return tower_disp

    xs, ys = pts[:, 0], pts[:, 1]

    pad_x = int(
        max(1, xs.max() - xs.min()) * SEARCH_AREA_MARGIN
    )

    pad_y = int(
        max(1, ys.max() - ys.min()) * SEARCH_AREA_MARGIN
    )

    x_min = max(
        0,
        int(xs.min()) - pad_x,
    )

    x_max = min(
        frame_width,
        int(xs.max()) + pad_x,
    )

    y_min = max(
        0,
        int(ys.min()) - pad_y,
    )

    y_max = min(
        frame_height,
        int(ys.max()) + pad_y,
    )

    left = tower_disp[
        y_min:y_max,
        x_min:x_max,
    ]

    right = tower_disp[
        y_min:y_max,
        frame_width + x_min:frame_width + x_max,
    ]

    return np.hstack([left, right])