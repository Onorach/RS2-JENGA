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
    TOWER_MASK_VAL_MIN,
    TOWER_MASK_MORPH_CLOSE_PX,
    TOWER_MASK_MORPH_OPEN_PX,
    TOWER_MASK_MIN_AREA_PX,
)


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def compute_saturation_mask(bgr: np.ndarray) -> np.ndarray:
    """Return a binary mask (H×W uint8) of high-saturation pixels."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = (
        (hsv[:, :, 1] >= TOWER_MASK_SAT_MIN) &
        (hsv[:, :, 2] >= TOWER_MASK_VAL_MIN)
    ).astype(np.uint8) * 255

    def _odd(k: int) -> int:
        return k if k % 2 == 1 else k + 1

    if TOWER_MASK_MORPH_CLOSE_PX > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(TOWER_MASK_MORPH_CLOSE_PX),) * 2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    if TOWER_MASK_MORPH_OPEN_PX > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(TOWER_MASK_MORPH_OPEN_PX),) * 2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    return mask


def compute_hex_region(bgr: np.ndarray) -> np.ndarray | None:
    """
    Find the largest high-saturation blob within the ROI and fit a
    6-sided polygon around it, returned in full-frame coordinates.
    """
    ih, iw = bgr.shape[:2]
    rx, ry, rw, rh = compute_roi(iw, ih)
    roi = bgr[ry:ry + rh, rx:rx + rw]

    mask = compute_saturation_mask(roi)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < TOWER_MASK_MIN_AREA_PX:
        return None

    hull = cv2.convexHull(largest)
    peri = cv2.arcLength(hull, True)
    for factor in np.arange(0.02, 0.5, 0.01):
        approx = cv2.approxPolyDP(hull, factor * peri, True)
        if len(approx) <= 6:
            break

    # Offset back to full-frame coords
    pts = approx.reshape(-1, 2).astype(np.int32)
    pts[:, 0] += rx
    pts[:, 1] += ry
    return pts


def build_hex_mask(shape: tuple[int, int], pts: np.ndarray) -> np.ndarray:
    """Return a binary mask (H×W) filled inside the hex polygon."""
    mask = np.zeros(shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask


def build_display(bgr: np.ndarray, pts: np.ndarray | None) -> np.ndarray:
    """Draw the ROI box, 6-sided region, and saturation mask side by side."""
    ih, iw = bgr.shape[:2]
    rx, ry, rw, rh = compute_roi(iw, ih)

    # Saturation mask computed on ROI, pasted back into full-frame image
    roi_mask = compute_saturation_mask(bgr[ry:ry + rh, rx:rx + rw])
    sat_colour = np.zeros((ih, iw), dtype=np.uint8)
    sat_colour[ry:ry + rh, rx:rx + rw] = roi_mask
    sat_colour = cv2.cvtColor(sat_colour, cv2.COLOR_GRAY2BGR)

    overlay = bgr.copy()
    cv2.rectangle(overlay, (rx, ry), (rx + rw, ry + rh), (0, 255, 255), 1)

    if pts is not None:
        cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 255), thickness=2)
        filled = overlay.copy()
        cv2.fillPoly(filled, [pts], (0, 255, 255))
        cv2.addWeighted(filled, 0.15, overlay, 0.85, 0, overlay)
        for i, (x, y) in enumerate(pts):
            cv2.circle(overlay, (x, y), 5, (0, 200, 255), -1)
            cv2.putText(overlay, str(i), (x + 6, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1, cv2.LINE_AA)

    return np.hstack([overlay, sat_colour])
