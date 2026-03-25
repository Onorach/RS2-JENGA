"""
roi_blob_boxes.py
-----------------
Finds blobs of each HSV colour in the search ROI and approximates each blob
as a 4-sided polygon (quadrilateral).  Results are shown as a colour-coded
overlay on the original camera image crop.

How it works
------------
1. Build an HSV classification mask for the full ROI (same as roi_color_view).
2. For each colour, clean up the mask (morphological close + open to remove
   noise and fill small holes).
3. Find contours on the cleaned mask.
4. Keep contours above a minimum area threshold.
5. Fit a minimum-area rotated rectangle (cv2.minAreaRect) then optionally
   refine it to a 4-point approximation via cv2.approxPolyDP.
6. Draw the quads on a dimmed copy of the original crop and show them in a
   new window.

Integration
-----------
In play.py's _show_window loop, after color_bgr is assigned:

    from roi_blob_boxes import update_blob_box_window

    update_blob_box_window(color_bgr)

The existing cv2.waitKey(1) keeps the window responsive.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from analyze_box_colors import HSV_RANGES, COLOUR_BGR, _build_colour_mask

# ---------------------------------------------------------------------------
# ROI geometry — keep in sync with play.py
# ---------------------------------------------------------------------------
SEARCH_CX_FRAC = 0.495
SEARCH_CY_FRAC = 0.485
SEARCH_W_FRAC  = 0.32
SEARCH_H_FRAC  = 0.62

# ---------------------------------------------------------------------------
# Face-dividing line — full-frame pixel coordinates
# Blobs are not allowed to cross this line; the mask is split along it before
# contour detection so same-colour blocks on opposite faces stay separate.
# ---------------------------------------------------------------------------
DIVIDE_LINE_TOP    = (920, 217)   # full-frame (x, y)
DIVIDE_LINE_BOTTOM = (914, 850)   # full-frame (x, y)

# ---------------------------------------------------------------------------
# Blob detection parameters — tune these to taste
# ---------------------------------------------------------------------------

# Minimum contour area (pixels²) to be considered a real blob.
MIN_BLOB_AREA = 400

# Morphological close: fills holes / connects nearby blobs of same colour.
MORPH_CLOSE_PX = 9

# Minimum blob width in pixels.
# Any part of a blob narrower than this is eroded away before fitting.
# This is the primary fix for tendrils — set to ~30 to match your requirement.
MIN_WIDTH_PX = 30

# After eroding by MIN_WIDTH_PX we dilate back by this amount to roughly
# restore the original blob size without re-growing the tendrils.
# Typically slightly less than MIN_WIDTH_PX so we don't over-expand.
WIDTH_RESTORE_PX = 22

# Solidity filter: ratio of contour area to its convex hull area.
# A solid rhombus-like shape scores ~0.9+.
# Spiky or crescent blobs score much lower — reject below this threshold.
MIN_SOLIDITY = 0.72

# Quad fit quality: ratio of contour area to fitted quad area.
# If the contour only covers a small fraction of the quad it means the quad
# has been pulled out of shape by a tendril.  Reject below this threshold.
MIN_QUAD_FILL = 0.50

# Polygon approximation epsilon as fraction of perimeter.
POLY_EPSILON_FRAC = 0.04

# How much to dim the original crop in the background (0.0=black, 1.0=full).
BG_DIM = 0.35

# Outline thickness for drawn quads.
QUAD_THICKNESS = 2

# Colours for the quad outlines — slightly brighter than the fill colours.
OUTLINE_BGR: dict[str, tuple[int, int, int]] = {
    "red":    (80,  80,  255),
    "yellow": (80,  255, 255),
    "green":  (80,  255, 80),
    "blue":   (255, 160, 80),
    "purple": (255, 80,  255),
}

BLOB_WINDOW = "Colour blob boxes"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_roi(iw: int, ih: int) -> tuple[int, int, int, int]:
    cw = int(iw * SEARCH_W_FRAC)
    ch = int(ih * SEARCH_H_FRAC)
    cx = int(iw * SEARCH_CX_FRAC) - cw // 2
    cy = int(ih * SEARCH_CY_FRAC) - ch // 2
    x  = max(0, min(cx, iw - cw))
    y  = max(0, min(cy, ih - ch))
    return x, y, cw, ch


def _kernel(px: int) -> np.ndarray:
    k = max(1, px if px % 2 == 1 else px + 1)
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


def _morph_close(mask: np.ndarray, close_px: int) -> np.ndarray:
    """Fill holes and bridge small gaps."""
    if close_px > 0:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, _kernel(close_px))
    return mask


def _remove_thin_regions(mask: np.ndarray, min_width_px: int, restore_px: int) -> np.ndarray:
    """
    Remove any part of the mask that is thinner than *min_width_px*.

    Uses the distance transform: each foreground pixel's value is its distance
    to the nearest background pixel.  Pixels with distance < min_width_px/2 are
    closer to the edge than half the minimum width, meaning they sit on a tendril
    narrower than the threshold.  Eroding by that radius removes them.

    We then dilate back by *restore_px* to roughly recover the core blob size
    without re-introducing the tendrils.
    """
    if min_width_px <= 0:
        return mask

    # Erode by half the minimum width — kills anything narrower than min_width_px
    erode_r = max(1, min_width_px // 2)
    eroded = cv2.erode(mask, _kernel(erode_r * 2 + 1))

    if restore_px > 0:
        eroded = cv2.dilate(eroded, _kernel(restore_px * 2 + 1))

    return eroded


def _solidity(contour: np.ndarray) -> float:
    """Ratio of contour area to convex hull area.  1.0 = perfectly convex."""
    area = cv2.contourArea(contour)
    if area <= 0:
        return 0.0
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    if hull_area <= 0:
        return 0.0
    return area / hull_area


def _quad_fill_ratio(contour: np.ndarray, quad: np.ndarray) -> float:
    """
    Ratio of contour area to the area of the fitted quad.
    Low values mean the quad has been pulled far outside the actual blob.
    """
    cnt_area = cv2.contourArea(contour)
    quad_area = cv2.contourArea(quad.reshape(-1, 1, 2).astype(np.float32))
    if quad_area <= 0:
        return 0.0
    return cnt_area / quad_area


def _build_side_masks(
    mask: np.ndarray,
    roi_x: int,
    roi_y: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Split *mask* (in ROI-local coordinates) into two halves along the
    face-dividing line defined by DIVIDE_LINE_TOP / DIVIDE_LINE_BOTTOM.

    The dividing line is converted from full-frame coords to ROI-local coords,
    then a filled polygon is used to produce a "left-side" boolean mask and a
    "right-side" boolean mask.  ANDing each with the colour mask keeps only
    pixels on the respective side of the line.

    Returns (left_mask, right_mask) — both uint8, same shape as *mask*.
    """
    h, w = mask.shape[:2]

    # Convert divide-line endpoints to ROI-local coords
    tx = DIVIDE_LINE_TOP[0]    - roi_x
    ty = DIVIDE_LINE_TOP[1]    - roi_y
    bx = DIVIDE_LINE_BOTTOM[0] - roi_x
    by = DIVIDE_LINE_BOTTOM[1] - roi_y

    # Left-side polygon: left edge of ROI → top of line → bottom of line → bottom-left
    left_poly = np.array([
        [0,   0],
        [tx,  ty],
        [bx,  by],
        [0,   h],
    ], dtype=np.int32)

    left_side = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(left_side, [left_poly], 255)

    # Right side is simply the inverse
    right_side = cv2.bitwise_not(left_side)

    left_mask  = cv2.bitwise_and(mask, left_side)
    right_mask = cv2.bitwise_and(mask, right_side)
    return left_mask, right_mask


def _contour_to_quad(contour: np.ndarray, epsilon_frac: float) -> np.ndarray:
    """
    Approximate a contour as a 4-sided polygon.

    Strategy:
    1. Try approxPolyDP with increasing epsilon until we get ≤ 4 points.
    2. If we can't get to 4, fall back to the 4 corners of minAreaRect.

    Returns an (4, 2) int32 array of (x, y) points.
    """
    peri = cv2.arcLength(contour, True)
    if peri < 1:
        rect = cv2.minAreaRect(contour)
        return np.int32(cv2.boxPoints(rect))

    # Try progressively larger epsilons
    for factor in [epsilon_frac, epsilon_frac * 2, epsilon_frac * 4,
                   epsilon_frac * 8, epsilon_frac * 16]:
        approx = cv2.approxPolyDP(contour, factor * peri, True)
        if len(approx) <= 4:
            break

    if len(approx) == 4:
        return approx.reshape(4, 2).astype(np.int32)

    # More than 4 sides even at large epsilon — use the rotated bounding rect
    rect = cv2.minAreaRect(contour)
    return np.int32(cv2.boxPoints(rect))


def find_colour_blobs(
    roi_bgr: np.ndarray,
    hsv_ranges: dict | None = None,
    min_area: int = MIN_BLOB_AREA,
    close_px: int = MORPH_CLOSE_PX,
    min_width_px: int = MIN_WIDTH_PX,
    restore_px: int = WIDTH_RESTORE_PX,
    min_solidity: float = MIN_SOLIDITY,
    min_quad_fill: float = MIN_QUAD_FILL,
    epsilon_frac: float = POLY_EPSILON_FRAC,
    roi_x: int = 0,
    roi_y: int = 0,
) -> dict[str, list[np.ndarray]]:
    """
    Find colour blobs in *roi_bgr* and return their 4-point polygons.

    Pipeline per colour
    -------------------
    1. Build HSV mask.
    2. Morphological close  — fills holes within a block.
    3. Width filter         — erode by MIN_WIDTH_PX/2, then dilate back.
                              Kills tendrils narrower than MIN_WIDTH_PX.
    4. Split on divide line — left/right halves processed independently.
    5. Find contours.
    6. Area filter          — skip tiny fragments.
    7. Solidity filter      — skip crescent / spiky shapes.
    8. Fit quad             — approxPolyDP → minAreaRect fallback.
    9. Quad-fill filter     — skip quads where most of the box is empty.
    """
    if hsv_ranges is None:
        hsv_ranges = HSV_RANGES

    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    h, w    = roi_bgr.shape[:2]

    result: dict[str, list[np.ndarray]] = {c: [] for c in hsv_ranges}

    for colour, ranges in hsv_ranges.items():
        # 1. HSV mask
        combined = np.zeros((h, w), dtype=np.uint8)
        for lo, hi in ranges:
            combined |= cv2.inRange(
                roi_hsv,
                np.array(lo, dtype=np.uint8),
                np.array(hi, dtype=np.uint8),
            )

        # 2. Close holes
        cleaned = _morph_close(combined, close_px)

        # 3. Width filter — removes tendrils before the divide split so
        #    morphology doesn't bridge the boundary
        cleaned = _remove_thin_regions(cleaned, min_width_px, restore_px)

        # 4. Split along the face-dividing line
        left_mask, right_mask = _build_side_masks(cleaned, roi_x, roi_y)

        for half_mask in (left_mask, right_mask):
            contours, _ = cv2.findContours(
                half_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            for cnt in contours:
                # 5. Area filter
                if cv2.contourArea(cnt) < min_area:
                    continue

                # 6. Solidity filter — reject spiky / crescent shapes
                if _solidity(cnt) < min_solidity:
                    continue

                # 7. Fit quad
                quad = _contour_to_quad(cnt, epsilon_frac)

                # 8. Quad-fill filter — reject quads skewed by tendrils
                if _quad_fill_ratio(cnt, quad) < min_quad_fill:
                    continue

                result[colour].append(quad)

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def update_blob_box_window(
    bgr_frame: np.ndarray,
    hsv_ranges: dict | None = None,
) -> None:
    """
    Detect colour blobs in the search ROI and display their quad outlines.

    Parameters
    ----------
    bgr_frame  : Full-resolution BGR frame from the camera / bag.
    hsv_ranges : HSV mask dict.  Defaults to HSV_RANGES.
    """
    if hsv_ranges is None:
        hsv_ranges = HSV_RANGES

    ih, iw = bgr_frame.shape[:2]
    roi_x, roi_y, roi_w, roi_h = _compute_roi(iw, ih)
    roi_bgr = bgr_frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]

    # Dimmed original crop as background so context is visible
    canvas = (roi_bgr.astype(np.float32) * BG_DIM).astype(np.uint8)

    # Find all blobs — pass ROI origin so the divide line can be localised
    blobs = find_colour_blobs(roi_bgr, hsv_ranges, roi_x=roi_x, roi_y=roi_y)

    # Draw each quad
    for colour, quads in blobs.items():
        fill_bgr    = COLOUR_BGR.get(colour, (128, 128, 128))
        outline_bgr = OUTLINE_BGR.get(colour, (255, 255, 255))

        for quad in quads:
            pts = quad.reshape((-1, 1, 2))

            # Semi-transparent fill — blend the colour into the canvas
            overlay = canvas.copy()
            cv2.fillPoly(overlay, [pts], fill_bgr)
            cv2.addWeighted(overlay, 0.30, canvas, 0.70, 0, canvas)

            # Solid outline
            cv2.polylines(canvas, [pts], isClosed=True,
                          color=outline_bgr, thickness=QUAD_THICKNESS,
                          lineType=cv2.LINE_AA)

            # Label: colour name at centroid
            M = cv2.moments(pts)
            if M["m00"] > 0:
                cx_lbl = int(M["m10"] / M["m00"])
                cy_lbl = int(M["m01"] / M["m00"])
                # Dark shadow then bright text
                cv2.putText(canvas, colour,
                            (cx_lbl - 1, cy_lbl + 1),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            (20, 20, 20), 1, cv2.LINE_AA)
                cv2.putText(canvas, colour,
                            (cx_lbl, cy_lbl),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            outline_bgr, 1, cv2.LINE_AA)

    # ROI border in cyan
    cv2.rectangle(canvas, (0, 0), (roi_w - 1, roi_h - 1), (255, 255, 0), 1)

    # Draw the face-dividing line in white so it's clearly visible
    dl_top    = (DIVIDE_LINE_TOP[0]    - roi_x, DIVIDE_LINE_TOP[1]    - roi_y)
    dl_bottom = (DIVIDE_LINE_BOTTOM[0] - roi_x, DIVIDE_LINE_BOTTOM[1] - roi_y)
    cv2.line(canvas, dl_top, dl_bottom, (255, 255, 255), 1, cv2.LINE_AA)
    # Small label
    cv2.putText(canvas, "divide", (dl_top[0] + 4, dl_top[1] + 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1, cv2.LINE_AA)

    cv2.namedWindow(BLOB_WINDOW, cv2.WINDOW_NORMAL)
    cv2.imshow(BLOB_WINDOW, canvas)