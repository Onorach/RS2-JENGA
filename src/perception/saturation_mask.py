"""
saturation_mask.py
------------------
Finds the high-saturation foreground (the Jenga tower) and fits a
6-sided convex hull around it to use as a clean search region.

Standalone use
--------------
    python saturation_mask.py path/to/image.png
"""
from __future__ import annotations

import sys
import cv2
import numpy as np
from colour_identification import compute_roi


# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------

SAT_MIN        = 200    # minimum saturation to be considered foreground
VAL_MIN        = 0    # minimum value (brightness) — filters dark shadows
MORPH_CLOSE_PX = 15    # close small gaps in the saturation mask
MORPH_OPEN_PX  = 10    # remove small noise blobs
MIN_AREA_PX    = 5000  # ignore tiny foreground regions


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def compute_saturation_mask(bgr: np.ndarray) -> np.ndarray:
    """Return a binary mask (H×W uint8) of high-saturation pixels."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = (
        (hsv[:, :, 1] >= SAT_MIN) &
        (hsv[:, :, 2] >= VAL_MIN)
    ).astype(np.uint8) * 255

    def _odd(k: int) -> int:
        return k if k % 2 == 1 else k + 1

    if MORPH_CLOSE_PX > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(MORPH_CLOSE_PX),) * 2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    if MORPH_OPEN_PX > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (_odd(MORPH_OPEN_PX),) * 2)
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
    if cv2.contourArea(largest) < MIN_AREA_PX:
        return None

    hull  = cv2.convexHull(largest)
    peri  = cv2.arcLength(hull, True)
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
    # Draw the original ROI in yellow
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


# ---------------------------------------------------------------------------
# Standalone
# ---------------------------------------------------------------------------

def main_standalone(image_path: str) -> None:
    bgr = cv2.imread(image_path)
    if bgr is None:
        print(f"Cannot read: {image_path}")
        sys.exit(1)

    pts = compute_hex_region(bgr)
    if pts is None:
        print("No foreground region found — try lowering SAT_MIN.")
    else:
        print(f"Hex region ({len(pts)} vertices):")
        for i, (x, y) in enumerate(pts):
            print(f"  {i}: ({x}, {y})")

    disp = build_display(bgr, pts)
    cv2.namedWindow("Saturation region", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Saturation region", 1280, 540)
    cv2.imshow("Saturation region", disp)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_standalone(sys.argv[1])
    else:
        print("Usage: python saturation_mask.py <image_path>")
        sys.exit(1)