"""
analyze_box_colors.py
---------------------
Analyses the colour distribution inside predefined quadrilateral boxes.

Each box is defined by 4 corner points (top-left, top-right, bottom-left, bottom-right)
in full-camera-frame pixel coordinates.  The pixels inside the quadrilateral are
classified using HSV masks; anything that doesn't match a mask is counted as "none".

Usage
-----
Import and call  analyse_frame(bgr_frame)  from your play.py pipeline, or run this
file directly against a still image for a quick test:

    python analyze_box_colors.py path/to/image.png

The function prints a per-box colour breakdown every time it is called, and also
returns the data as a list of dicts so you can use it programmatically.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# HSV colour masks
# ---------------------------------------------------------------------------
# Each entry maps a colour name to one or more (lower, upper) HSV bound pairs.
# A pixel is classified as that colour if it falls inside ANY of its ranges.
# Colours are tested in definition order; the first match wins.
# Pixels that match no range are labelled "none".
# ---------------------------------------------------------------------------
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    # Red wraps around hue=0, so two ranges are required.
    "red": [
        ((0,   150, 140), (10,  255, 255)),
        ((170, 150, 140), (179, 255, 255)),
    ],
    # Yellow – slightly broader hue, lower S/V thresholds.
    "yellow": [
        ((18, 140, 140), (40, 255, 255)),
    ],
    "green": [
        ((40, 120, 100), (85, 255, 255)),
    ],
    # Blue – light blue, stops before purple.
    "blue": [
        ((90, 220, 130), (110, 255, 255)),
    ],
    # Purple / magenta – darker purples, allow low V but keep higher S.
    "purple": [
        ((110, 110, 50), (175, 255, 200)),
    ],
}

# ---------------------------------------------------------------------------
# Box definitions
# ---------------------------------------------------------------------------
# Each box is a list of 4 (x, y) points in pixel coordinates of the FULL
# camera frame.  Order: top-left, top-right, bottom-left, bottom-right
# (or any consistent winding order – cv2.fillPoly handles either).
#
# Box 0: left cell
# Box 1: right cell
# ---------------------------------------------------------------------------
BOXES: list[dict] = [
    {
        "name": "left_cell",
        # TL            TR            BL            BR
        "corners": [(664, 197), (920, 217), (669, 282), (916, 315)],
    },
    {
        "name": "right_cell",
        "corners": [(920, 217), (1237, 215), (916, 315), (1228, 297)],
    },
]


# ---------------------------------------------------------------------------
# Colour → BGR display colour for the debug window
# "none" pixels → black, outside all boxes → white
# ---------------------------------------------------------------------------
COLOUR_BGR: dict[str, tuple[int, int, int]] = {
    "red":    (0,   0,   220),
    "yellow": (0,   220, 220),
    "green":  (0,   200, 0),
    "blue":   (220, 80,  0),
    "purple": (180, 0,   180),
    "none":   (0,   0,   0),    # black inside quad but unmatched
}

DEBUG_WINDOW = "Colour debug"

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _build_colour_mask(hsv: np.ndarray, colour: str) -> np.ndarray:
    """Return a boolean mask that is True wherever *hsv* matches *colour*."""
    combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
    for lo, hi in HSV_RANGES[colour]:
        combined |= cv2.inRange(hsv, np.array(lo, dtype=np.uint8),
                                     np.array(hi, dtype=np.uint8))
    return combined.astype(bool)


def _quad_mask(shape: tuple[int, int], corners: list[tuple[int, int]]) -> np.ndarray:
    """
    Return a boolean mask (H×W) that is True inside the quadrilateral
    defined by *corners*.

    Corners are stored as [TL, TR, BL, BR].  Drawing them in that order
    produces a self-intersecting hourglass (two triangles).  Re-winding to
    TL→TR→BR→BL gives the correct parallelogram.
    """
    tl, tr, bl, br = corners
    ordered = [tl, tr, br, bl]
    pts = np.array(ordered, dtype=np.int32).reshape((-1, 1, 2))
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [pts], 255)
    return mask.astype(bool)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_frame(
    bgr_frame: np.ndarray,
    boxes: Optional[list[dict]] = None,
    hsv_ranges: Optional[dict] = None,
    print_results: bool = True,
    show_debug: bool = True,
) -> list[dict]:
    """
    Classify pixels inside each quadrilateral box by colour.

    Parameters
    ----------
    bgr_frame   : Full-resolution BGR image (e.g. from RealSense or cv2.imread).
    boxes       : List of box dicts with keys ``name`` and ``corners``.
                  Defaults to the module-level BOXES.
    hsv_ranges  : Colour→range mapping.  Defaults to the module-level HSV_RANGES.
    print_results: If True, print a formatted table to stdout.
    show_debug  : If True, open/update the colour debug window.

    Returns
    -------
    List of dicts, one per box.

        {
            "name": "left_cell",
            "total_pixels": 1234,
            "colours": {
                "red":    {"count": 10,  "pct": 0.81},
                "yellow": {"count": 0,   "pct": 0.00},
                ...
                "none":   {"count": 900, "pct": 72.94},
            }
        }
    """
    if boxes is None:
        boxes = BOXES
    if hsv_ranges is None:
        hsv_ranges = HSV_RANGES

    ih, iw = bgr_frame.shape[:2]
    hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

    results = []

    for box in boxes:
        name = box["name"]
        corners = box["corners"]

        # --- Pixel mask for the quadrilateral --------------------------------
        quad_mask = _quad_mask((ih, iw), corners)
        total = int(quad_mask.sum())

        if total == 0:
            # Box is outside the frame or degenerate
            results.append({"name": name, "total_pixels": 0, "colours": {}})
            continue

        # --- Classify each pixel in the quad ----------------------------------
        colour_counts: dict[str, int] = {}
        # Start with every pixel unclassified
        unclassified = quad_mask.copy()

        for colour in hsv_ranges:
            colour_mask = _build_colour_mask(hsv_frame, colour)
            # Only count pixels inside the quad AND matching this colour
            matched = quad_mask & colour_mask & unclassified
            count = int(matched.sum())
            colour_counts[colour] = count
            # Remove matched pixels from the unclassified pool
            unclassified &= ~matched

        # Remaining unclassified pixels → "none"
        colour_counts["none"] = int(unclassified.sum())

        # Build percentage table
        colours_table: dict[str, dict] = {}
        for label, count in colour_counts.items():
            colours_table[label] = {
                "count": count,
                "pct": round(count / total * 100, 2),
            }

        results.append({
            "name": name,
            "total_pixels": total,
            "colours": colours_table,
        })

    # --- Pretty-print --------------------------------------------------------
    if print_results:
        _print_results(results)

    # --- Debug window --------------------------------------------------------
    if show_debug:
        show_debug_window(bgr_frame, boxes=boxes, hsv_ranges=hsv_ranges)

    return results


def _print_results(results: list[dict]) -> None:
    sep = "─" * 52
    print(sep)
    for box in results:
        print(f"  Box: {box['name']}   ({box['total_pixels']} pixels inside quad)")
        if not box["colours"]:
            print("    [box has zero pixels – check corners are within frame]")
            continue
        print(f"  {'Colour':<10}  {'Count':>7}  {'Percent':>8}")
        print(f"  {'──────':<10}  {'─────':>7}  {'───────':>8}")
        for label, info in box["colours"].items():
            bar = "█" * int(info["pct"] / 2)  # 50 chars = 100%
            print(f"  {label:<10}  {info['count']:>7}  {info['pct']:>7.2f}%  {bar}")
        print()
    print(sep)


# ---------------------------------------------------------------------------
# Debug visualisation window
# ---------------------------------------------------------------------------

def show_debug_window(
    bgr_frame: np.ndarray,
    boxes: Optional[list[dict]] = None,
    hsv_ranges: Optional[dict] = None,
) -> None:
    """
    Open (or update) a debug window showing colour classification results.

    The canvas covers the bounding box of all quad corners plus a margin.
    - White background  = outside every quad
    - Black             = inside a quad but matched to "none"
    - Solid colour      = matched pixel (red/yellow/green/blue/purple)
    - Grid corner dots  = white circles with black outline
    - Quad outline      = thin white polyline connecting the 4 corners
    - Corner labels     = (x,y) text next to each dot

    The window is created with WINDOW_NORMAL so you can resize it freely.
    Call cv2.waitKey(1) in your main loop to keep it responsive.
    """
    if boxes is None:
        boxes = BOXES
    if hsv_ranges is None:
        hsv_ranges = HSV_RANGES

    ih, iw = bgr_frame.shape[:2]
    hsv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HSV)

    # ------------------------------------------------------------------ #
    # 1. Work out which region of the full frame we need to show          #
    # ------------------------------------------------------------------ #
    all_corners: list[tuple[int, int]] = []
    for box in boxes:
        all_corners.extend(box["corners"])

    if not all_corners:
        return

    margin = 40
    min_x = max(0, min(c[0] for c in all_corners) - margin)
    min_y = max(0, min(c[1] for c in all_corners) - margin)
    max_x = min(iw, max(c[0] for c in all_corners) + margin)
    max_y = min(ih, max(c[1] for c in all_corners) + margin)

    crop_w = max_x - min_x
    crop_h = max_y - min_y

    # ------------------------------------------------------------------ #
    # 2. Build the colour canvas (white = outside quads)                  #
    # ------------------------------------------------------------------ #
    canvas = np.full((crop_h, crop_w, 3), 255, dtype=np.uint8)

    for box in boxes:
        corners = box["corners"]

        # Full-frame quad mask (boolean, full resolution)
        quad_mask = _quad_mask((ih, iw), corners)
        unclassified = quad_mask.copy()

        # Paint each colour class
        for colour in hsv_ranges:
            colour_mask = _build_colour_mask(hsv_frame, colour)
            matched = quad_mask & colour_mask & unclassified
            unclassified &= ~matched

            bgr = COLOUR_BGR.get(colour, (128, 128, 128))
            # Slice to our crop region and paint matched pixels
            matched_crop = matched[min_y:max_y, min_x:max_x]
            canvas[matched_crop] = bgr

        # Remaining pixels inside quad → "none" = black
        none_crop = unclassified[min_y:max_y, min_x:max_x]
        canvas[none_crop] = COLOUR_BGR["none"]

    # ------------------------------------------------------------------ #
    # 3. Draw quad outlines and corner annotations                         #
    # ------------------------------------------------------------------ #
    for box in boxes:
        corners = box["corners"]

        # Corners in crop-local coordinates
        local = [(x - min_x, y - min_y) for x, y in corners]

        # Quad outline — close the polygon by connecting all corners in order:
        # TL→TR→BR→BL→TL  (the stored order is TL, TR, BL, BR so re-order)
        tl, tr, bl, br = local
        poly = np.array([tl, tr, br, bl], dtype=np.int32)
        cv2.polylines(canvas, [poly], isClosed=True, color=(255, 255, 255), thickness=1)

        # Corner dots + labels
        for (lx, ly), (ox, oy) in zip(local, corners):
            # White filled circle with dark outline
            cv2.circle(canvas, (lx, ly), 5, (30, 30, 30), -1)
            cv2.circle(canvas, (lx, ly), 5, (255, 255, 255), 1)
            # Coordinate label — nudge to avoid sitting on the dot
            label = f"({ox},{oy})"
            lx_text = lx + 8
            ly_text = ly - 8
            # Keep label inside canvas
            lx_text = min(lx_text, crop_w - len(label) * 7)
            ly_text = max(ly_text, 12)
            cv2.putText(
                canvas, label, (lx_text, ly_text),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (30, 30, 30), 1, cv2.LINE_AA
            )
            cv2.putText(
                canvas, label, (lx_text, ly_text),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (230, 230, 230), 1, cv2.LINE_AA
            )

    # ------------------------------------------------------------------ #
    # 4. Colour legend (bottom-left)                                       #
    # ------------------------------------------------------------------ #
    legend_items = list(COLOUR_BGR.items())  # [("red", bgr), ...]
    lx0, ly0 = 6, crop_h - len(legend_items) * 16 - 6
    for i, (name, bgr) in enumerate(legend_items):
        ly = ly0 + i * 16
        cv2.rectangle(canvas, (lx0, ly), (lx0 + 12, ly + 12), bgr, -1)
        cv2.rectangle(canvas, (lx0, ly), (lx0 + 12, ly + 12), (100, 100, 100), 1)
        cv2.putText(
            canvas, name, (lx0 + 16, ly + 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.38, (30, 30, 30), 1, cv2.LINE_AA
        )

    # ------------------------------------------------------------------ #
    # 5. Show                                                              #
    # ------------------------------------------------------------------ #
    cv2.namedWindow(DEBUG_WINDOW, cv2.WINDOW_NORMAL)
    cv2.imshow(DEBUG_WINDOW, canvas)


# ---------------------------------------------------------------------------
# Optional: draw boxes onto a frame for visual debugging
# ---------------------------------------------------------------------------

def draw_boxes(bgr_frame: np.ndarray, boxes: Optional[list[dict]] = None) -> np.ndarray:
    """Return a copy of *bgr_frame* with the quadrilateral boxes drawn on it."""
    if boxes is None:
        boxes = BOXES
    out = bgr_frame.copy()
    for i, box in enumerate(boxes):
        pts = np.array(box["corners"], dtype=np.int32).reshape((-1, 1, 2))
        colour = (0, 255, 255) if i % 2 == 0 else (255, 100, 0)
        cv2.polylines(out, [pts], isClosed=True, color=colour, thickness=2)
        # Label near the first corner
        x0, y0 = box["corners"][0]
        cv2.putText(out, box["name"], (x0, y0 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1, cv2.LINE_AA)
    return out


# ---------------------------------------------------------------------------
# Integration snippet for play.py
# ---------------------------------------------------------------------------
# In your _show_window loop:
#
#   1. analyse_frame fires every 30 frames — it updates the debug window
#      AND prints the percentage table to stdout.
#
#   2. The existing cv2.waitKey(1) at the bottom of the loop is enough to
#      keep BOTH windows (Jenga Grid + Colour debug) responsive — no extra
#      waitKey call is needed.
#
#     from analyze_box_colors import analyse_frame
#
#     frame_counter = 0   # before the while loop
#
#     # inside the while loop, right after color_bgr is assigned:
#     frame_counter += 1
#     if frame_counter % 30 == 0:
#         analyse_frame(color_bgr)   # show_debug=True by default
#
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CLI: test against a still image
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_box_colors.py <image_path>")
        print("       (provide any BGR image that matches your camera resolution)")
        sys.exit(1)

    path = sys.argv[1]
    frame = cv2.imread(path)
    if frame is None:
        print(f"Could not read image: {path}")
        sys.exit(1)

    print(f"Image size: {frame.shape[1]}×{frame.shape[0]}  (W×H)")
    analyse_frame(frame)

    # Optionally show the frame with boxes highlighted
    debug = draw_boxes(frame)
    cv2.imshow("Box debug", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()