"""
grid_generation.py
------------------
Edge-based line and grid-point generation for perception displays.
"""
from __future__ import annotations

import cv2
import numpy as np

from perception_config import (
    CANNY_GREY_LOW,
    CANNY_GREY_HIGH,
    HOUGH_THRESHOLD,
    HOUGH_MIN_LENGTH,
    HOUGH_MAX_GAP,
    MAX_HORIZ_DEG,
    MAX_VERT_DEG,
)


def compute_edges(colour_img: np.ndarray) -> np.ndarray:
    """Compute Canny edges from colour-mask image."""
    grey = cv2.cvtColor(colour_img, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(grey, CANNY_GREY_LOW, CANNY_GREY_HIGH)


def find_lines(edges: np.ndarray) -> list[tuple]:
    """Run probabilistic Hough transform and return raw line tuples."""
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=HOUGH_THRESHOLD,
        minLineLength=HOUGH_MIN_LENGTH,
        maxLineGap=HOUGH_MAX_GAP,
    )
    if lines is None:
        return []
    return [tuple(l[0]) for l in lines]


def _classify_line(x1: int, y1: int, x2: int, y2: int) -> str | None:
    angle = float(np.degrees(np.arctan2(abs(y2 - y1), abs(x2 - x1))))
    if angle <= MAX_HORIZ_DEG:
        return "horiz"
    if angle >= 90.0 - MAX_VERT_DEG:
        return "vert"
    return None


def classify_lines(lines: list[tuple]) -> tuple[list[tuple], list[tuple]]:
    """Split lines into horizontal and vertical groups once."""
    horiz_lines: list[tuple] = []
    vert_lines: list[tuple] = []
    for x1, y1, x2, y2 in lines:
        kind = _classify_line(x1, y1, x2, y2)
        if kind == "horiz":
            horiz_lines.append((x1, y1, x2, y2))
        elif kind == "vert":
            vert_lines.append((x1, y1, x2, y2))
    return horiz_lines, vert_lines


def draw_classified_lines(
    base_img: np.ndarray,
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
) -> np.ndarray:
    out = base_img.copy()
    for x1, y1, x2, y2 in horiz_lines:
        cv2.line(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
    for x1, y1, x2, y2 in vert_lines:
        cv2.line(out, (x1, y1), (x2, y2), (255, 100, 0), 1)
    return out


def draw_lines(base_img: np.ndarray, lines: list[tuple]) -> np.ndarray:
    horiz_lines, vert_lines = classify_lines(lines)
    return draw_classified_lines(base_img, horiz_lines, vert_lines)


def find_hv_intersections_from_classified(
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
    image_shape: tuple[int, int] | tuple[int, int, int],
    max_points: int = 400,
) -> list[tuple[int, int]]:
    """Find intersection pixels using horizontal/vertical raster masks."""
    if not horiz_lines or not vert_lines:
        return []

    img_h, img_w = int(image_shape[0]), int(image_shape[1])
    horiz_mask = np.zeros((img_h, img_w), dtype=np.uint8)
    vert_mask = np.zeros((img_h, img_w), dtype=np.uint8)

    for line in horiz_lines:
        x1, y1, x2, y2 = line
        cv2.line(horiz_mask, (x1, y1), (x2, y2), 255, 1)
    for line in vert_lines:
        x1, y1, x2, y2 = line
        cv2.line(vert_mask, (x1, y1), (x2, y2), 255, 1)

    overlap = cv2.bitwise_and(horiz_mask, vert_mask)
    ys, xs = np.where(overlap > 0)
    if len(xs) == 0:
        return []
    if max_points > 0 and len(xs) > max_points:
        xs = xs[:max_points]
        ys = ys[:max_points]
    return [(int(x), int(y)) for x, y in zip(xs, ys)]


def build_edge_display(colour_img: np.ndarray) -> tuple[np.ndarray, list[tuple]]:
    """Full pipeline: colour mask -> grey edges -> classified line overlay."""
    edges_grey = compute_edges(colour_img)
    lines_grey = find_lines(edges_grey)
    horiz_lines, vert_lines = classify_lines(lines_grey)
    disp_grey = draw_classified_lines(
        cv2.cvtColor(edges_grey, cv2.COLOR_GRAY2BGR),
        horiz_lines,
        vert_lines,
    )
    return disp_grey, lines_grey
