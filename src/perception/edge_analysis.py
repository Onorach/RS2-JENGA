"""
edge_analysis.py
----------------
Edge detection and line finding on the colour mask produced by
colour_identification.classify_frame().

Standalone use
--------------
    python edge_analysis.py path/to/image.png
"""
from __future__ import annotations

import sys
import cv2
import numpy as np

from colour_identification import classify_frame

# ---------------------------------------------------------------------------
# Tunable parameters
# ---------------------------------------------------------------------------

CANNY_GREY_LOW    = 30
CANNY_GREY_HIGH   = 100
CANNY_HUE_LOW     = 10
CANNY_HUE_HIGH    = 50

HOUGH_THRESHOLD   = 60
HOUGH_MIN_LENGTH  = 50
HOUGH_MAX_GAP     = 20

MAX_HORIZ_DEG     = 25.0
MAX_VERT_DEG      = 4.0


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def compute_edges(colour_img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute two edge images from the colour mask.

    Returns
    -------
    edges_grey : Canny on greyscale conversion of colour mask.
    edges_hue  : Canny on hue channel of colour mask.
    """
    grey      = cv2.cvtColor(colour_img, cv2.COLOR_BGR2GRAY)
    edges_grey = cv2.Canny(grey, CANNY_GREY_LOW, CANNY_GREY_HIGH)

    hue        = cv2.cvtColor(colour_img, cv2.COLOR_BGR2HSV)[:, :, 0]
    edges_hue  = cv2.Canny(hue, CANNY_HUE_LOW, CANNY_HUE_HIGH)

    return edges_grey, edges_hue


def find_lines(edges: np.ndarray) -> list[tuple]:
    """
    Run Hough line detection on an edge image.
    Returns list of (x1, y1, x2, y2) tuples.
    """
    lines = cv2.HoughLinesP(
        edges,
        rho=1, theta=np.pi / 180,
        threshold=HOUGH_THRESHOLD,
        minLineLength=HOUGH_MIN_LENGTH,
        maxLineGap=HOUGH_MAX_GAP,
    )
    if lines is None:
        return []
    return [tuple(l[0]) for l in lines]


def _classify_line(x1: int, y1: int, x2: int, y2: int) -> str | None:
    """Return 'horiz', 'vert', or None if the line doesn't match either."""
    angle = float(np.degrees(np.arctan2(abs(y2 - y1), abs(x2 - x1))))
    if angle <= MAX_HORIZ_DEG:
        return "horiz"
    if angle >= 90.0 - MAX_VERT_DEG:
        return "vert"
    return None


def draw_lines(base_img: np.ndarray, lines: list[tuple]) -> np.ndarray:
    """
    Draw filtered Hough lines on base_img.
    Horizontal → green, vertical → blue, others → skipped.
    """
    out = base_img.copy()
    for x1, y1, x2, y2 in lines:
        kind = _classify_line(x1, y1, x2, y2)
        if kind == "horiz":
            cv2.line(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        elif kind == "vert":
            cv2.line(out, (x1, y1), (x2, y2), (255, 100, 0), 1)
    return out


def build_edge_display(colour_img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Full pipeline: colour mask → edges → lines overlaid.

    Returns
    -------
    disp_grey : edges_grey with Hough lines drawn on top (BGR).
    disp_hue  : edges_hue  with Hough lines drawn on top (BGR).
    """
    edges_grey, edges_hue = compute_edges(colour_img)

    lines_grey = find_lines(edges_grey)
    lines_hue  = find_lines(edges_hue)

    disp_grey = draw_lines(cv2.cvtColor(edges_grey, cv2.COLOR_GRAY2BGR), lines_grey)
    disp_hue  = draw_lines(cv2.cvtColor(edges_hue,  cv2.COLOR_GRAY2BGR), lines_hue)

    return disp_grey, disp_hue


# ---------------------------------------------------------------------------
# Standalone
# ---------------------------------------------------------------------------

def main_standalone(image_path: str) -> None:
    bgr = cv2.imread(image_path)
    if bgr is None:
        print(f"Cannot read: {image_path}")
        sys.exit(1)

    colour_img, _ = classify_frame(bgr)
    disp_grey, disp_hue = build_edge_display(colour_img)

    cv2.namedWindow("Edges (grey)", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Edges (hue)",  cv2.WINDOW_NORMAL)
    cv2.imshow("Edges (grey)", disp_grey)
    cv2.imshow("Edges (hue)",  disp_hue)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_standalone(sys.argv[1])
    else:
        print("Usage: python edge_analysis.py <image_path>")
        sys.exit(1)