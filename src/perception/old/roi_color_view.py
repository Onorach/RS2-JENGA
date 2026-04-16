"""
roi_color_view.py
-----------------
Opens a live window showing the full search ROI from play.py with every pixel
painted according to the HSV colour masks from analyze_box_colors.py.

- Matched pixels are shown in their classification colour (red/yellow/green/blue/purple)
- Unmatched pixels are shown in black ("none")
- The search ROI rectangle border is drawn in cyan, matching play.py

No terminal output — purely visual.

Integration
-----------
In play.py's _show_window loop, after color_bgr is assigned:

    from roi_color_view import update_roi_colour_window

    update_roi_colour_window(color_bgr)

The existing cv2.waitKey(1) at the bottom of the loop keeps this window
responsive — no extra waitKey needed.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

# Re-use ROI geometry and colour masks from the sibling files.
# play.py defines the ROI fractions; analyze_box_colors defines the masks.
from analyze_box_colors import HSV_RANGES, COLOUR_BGR, _build_colour_mask

# ---------------------------------------------------------------------------
# Mirror the ROI constants from play.py so this file is self-contained.
# Keep these in sync if you change them in play.py.
# ---------------------------------------------------------------------------
SEARCH_CX_FRAC = 0.495
SEARCH_CY_FRAC = 0.485
SEARCH_W_FRAC  = 0.32
SEARCH_H_FRAC  = 0.62

ROI_WINDOW = "ROI colour view"


def _compute_roi(iw: int, ih: int) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the search ROI in full-frame pixel coords."""
    cw = int(iw * SEARCH_W_FRAC)
    ch = int(ih * SEARCH_H_FRAC)
    cx = int(iw * SEARCH_CX_FRAC) - cw // 2
    cy = int(ih * SEARCH_CY_FRAC) - ch // 2
    x  = max(0, min(cx, iw - cw))
    y  = max(0, min(cy, ih - ch))
    return x, y, cw, ch


def update_roi_colour_window(
    bgr_frame: np.ndarray,
    hsv_ranges: Optional[dict] = None,
) -> None:
    """
    Classify every pixel in the search ROI and display the result.

    Parameters
    ----------
    bgr_frame  : Full-resolution BGR frame from the camera / bag.
    hsv_ranges : Colour→HSV-range mapping. Defaults to HSV_RANGES from
                 analyze_box_colors.py.
    """
    if hsv_ranges is None:
        hsv_ranges = HSV_RANGES

    ih, iw = bgr_frame.shape[:2]
    roi_x, roi_y, roi_w, roi_h = _compute_roi(iw, ih)

    # Crop to the ROI region only — all work is done on this smaller image.
    roi_bgr = bgr_frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    # Start with a black canvas (= "none" colour for every pixel).
    canvas = np.zeros_like(roi_bgr)

    # Track which pixels have already been classified (first match wins).
    unclassified = np.ones((roi_h, roi_w), dtype=bool)

    for colour, ranges in hsv_ranges.items():
        # Build combined mask for all ranges of this colour.
        combined = np.zeros((roi_h, roi_w), dtype=np.uint8)
        for lo, hi in ranges:
            combined |= cv2.inRange(
                roi_hsv,
                np.array(lo, dtype=np.uint8),
                np.array(hi, dtype=np.uint8),
            )
        matched = combined.astype(bool) & unclassified
        unclassified &= ~matched

        bgr = COLOUR_BGR.get(colour, (128, 128, 128))
        canvas[matched] = bgr

    # Thin cyan border matching the rectangle drawn in play.py.
    cv2.rectangle(canvas, (0, 0), (roi_w - 1, roi_h - 1), (255, 255, 0), 2)

    cv2.namedWindow(ROI_WINDOW, cv2.WINDOW_NORMAL)
    cv2.imshow(ROI_WINDOW, canvas)