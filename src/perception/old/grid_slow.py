"""
grid_generation.py
------------------
Edge-based line and grid-point generation for perception displays.

Intersection pipeline (v3):
  1. Colour mask is morphologically cleaned before Canny to reduce fringe
     misclassification noise at block boundaries.
  2. (Optional) Near-parallel lines within LINE_MERGE_BAND_PX are collapsed
     into one representative line.  The representative line uses MIN/MAX of
     endpoint coordinates to preserve full spatial extent — averaging (the
     v2 bug) produced short lines that caused edge intersections to be
     rejected because t/u fell outside the tolerance window.
  3. Intersections are found algebraically (line extension) with a configurable
     gap tolerance so corners where segments "almost meet" are recovered.
  4. Near-duplicate intersection points are clustered into single canonical
     corners via a fast grid-bucket approach.
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
    CLEAN_MASK_KERNEL_PX,
    LINE_MERGE_BAND_PX,
    LINE_MERGE_ENABLED,
    INTERSECTION_GAP_TOLERANCE_PX,
    CLUSTER_CELL_SIZE_PX,
)


# ---------------------------------------------------------------------------
# Colour mask cleaning
# ---------------------------------------------------------------------------

def clean_colour_mask(colour_img: np.ndarray) -> np.ndarray:
    """
    Morphologically close the colour-mask image to fill fringe pixels at block
    boundaries before edge detection.  If CLEAN_MASK_KERNEL_PX is 0 the image
    is returned unchanged.
    """
    if CLEAN_MASK_KERNEL_PX <= 0:
        return colour_img
    k = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (CLEAN_MASK_KERNEL_PX, CLEAN_MASK_KERNEL_PX),
    )
    return cv2.morphologyEx(colour_img, cv2.MORPH_CLOSE, k)


# ---------------------------------------------------------------------------
# Edge and line detection
# ---------------------------------------------------------------------------

def compute_edges(colour_img: np.ndarray) -> np.ndarray:
    """Compute Canny edges from a colour-mask image (after cleaning)."""
    cleaned = clean_colour_mask(colour_img)
    grey = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
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
    """Split lines into horizontal and vertical groups."""
    horiz_lines: list[tuple] = []
    vert_lines: list[tuple] = []
    for x1, y1, x2, y2 in lines:
        kind = _classify_line(x1, y1, x2, y2)
        if kind == "horiz":
            horiz_lines.append((x1, y1, x2, y2))
        elif kind == "vert":
            vert_lines.append((x1, y1, x2, y2))
    return horiz_lines, vert_lines


# ---------------------------------------------------------------------------
# Line merging  (optional — controlled by LINE_MERGE_ENABLED)
# ---------------------------------------------------------------------------

def _normalize_line(x1: int, y1: int, x2: int, y2: int) -> tuple:
    """Ensure the smaller coordinate comes first for consistent min/max."""
    if x1 > x2 or (x1 == x2 and y1 > y2):
        return (x2, y2, x1, y1)
    return (x1, y1, x2, y2)


def _merge_group(group: list[tuple], is_horiz: bool) -> tuple:
    """
    Produce one representative line for a group of near-parallel lines.

    KEY FIX vs v2: instead of averaging all four coordinates (which shrinks
    the line to cover only the central x/y portion of the group), we:
      • average the PERPENDICULAR coordinate  (y for horiz, x for vert)
      • take MIN/MAX of the PARALLEL coordinates to preserve full extent.

    Example — three horizontal sub-segments spanning the full width:
        (50, 100, 200, 101), (190, 99, 400, 100), (380, 100, 550, 100)
      v2 (broken):  x1=avg(50,190,380)=207, x2=avg(200,400,550)=383  ← too short
      v3 (fixed):   x1=min(50,190,380)=50,  x2=max(200,400,550)=550  ← full span
    """
    normed = [_normalize_line(*l) for l in group]

    if is_horiz:
        y = int(round(np.mean([(l[1] + l[3]) / 2.0 for l in normed])))
        x1 = min(l[0] for l in normed)
        x2 = max(l[2] for l in normed)
        return (x1, y, x2, y)
    else:
        x = int(round(np.mean([(l[0] + l[2]) / 2.0 for l in normed])))
        y1 = min(l[1] for l in normed)
        y2 = max(l[3] for l in normed)
        return (x, y1, x, y2)


def merge_colinear_lines(
    lines: list[tuple],
    is_horiz: bool,
    band: int = LINE_MERGE_BAND_PX,
) -> list[tuple]:
    """
    Collapse near-parallel lines within `band` pixels of each other into a
    single representative line.

    Groups are compared against their FIRST element (not the running tail) to
    prevent chaining.  Without this, y=100, 107, 114 with band=8 would all
    join one group even though the total spread is 14 px — each step is ≤ 8
    but the group as a whole spans much more.
    """
    if not lines:
        return []

    key_fn = (
        (lambda l: (l[1] + l[3]) // 2)
        if is_horiz
        else (lambda l: (l[0] + l[2]) // 2)
    )

    lines_sorted = sorted(lines, key=key_fn)
    merged: list[tuple] = []
    group = [lines_sorted[0]]
    group_anchor = key_fn(lines_sorted[0])   # always compare against FIRST element

    for line in lines_sorted[1:]:
        if abs(key_fn(line) - group_anchor) <= band:
            group.append(line)
        else:
            merged.append(_merge_group(group, is_horiz))
            group = [line]
            group_anchor = key_fn(line)

    merged.append(_merge_group(group, is_horiz))
    return merged


# ---------------------------------------------------------------------------
# Algebraic intersection with gap tolerance
# ---------------------------------------------------------------------------

def extend_and_intersect(
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
    image_shape: tuple,
    gap_tolerance: int = INTERSECTION_GAP_TOLERANCE_PX,
) -> list[tuple[int, int]]:
    """
    Find corners by solving the algebraic intersection of each horizontal line
    with each vertical line.

    Parametric form:
        P_H(t) = (hx1 + t*dx_h,  hy1 + t*dy_h)   t in [0,1] on the segment
        P_V(u) = (vx1 + u*dx_v,  vy1 + u*dy_v)   u in [0,1] on the segment

    A point is accepted when:
      • It falls inside the image bounds.
      • t ∈ [-tol_h, 1+tol_h]  where tol_h = gap_tolerance / length_h
      • u ∈ [-tol_v, 1+tol_v]  where tol_v = gap_tolerance / length_v

    The tolerance allows intersections that land slightly outside a segment
    endpoint — the primary failure mode when Hough segments stop just short
    of the physical corner.
    """
    if not horiz_lines or not vert_lines:
        return []

    img_h, img_w = int(image_shape[0]), int(image_shape[1])
    points: list[tuple[int, int]] = []

    for hx1, hy1, hx2, hy2 in horiz_lines:
        dx_h = hx2 - hx1
        dy_h = hy2 - hy1
        len_h = max(1.0, float(np.hypot(dx_h, dy_h)))
        tol_h = gap_tolerance / len_h

        for vx1, vy1, vx2, vy2 in vert_lines:
            dx_v = vx2 - vx1
            dy_v = vy2 - vy1
            len_v = max(1.0, float(np.hypot(dx_v, dy_v)))
            tol_v = gap_tolerance / len_v

            denom = dx_h * dy_v - dy_h * dx_v
            if abs(denom) < 1e-6:
                continue  # parallel or degenerate

            ox = vx1 - hx1
            oy = vy1 - hy1

            t = (ox * dy_v - oy * dx_v) / denom
            u = (ox * dy_h - oy * dx_h) / denom

            if not (-tol_h <= t <= 1.0 + tol_h):
                continue
            if not (-tol_v <= u <= 1.0 + tol_v):
                continue

            ix = int(round(hx1 + t * dx_h))
            iy = int(round(hy1 + t * dy_h))

            if 0 <= ix < img_w and 0 <= iy < img_h:
                points.append((ix, iy))

    return points


# ---------------------------------------------------------------------------
# Point clustering
# ---------------------------------------------------------------------------

def cluster_points(
    points: list[tuple[int, int]],
    cell_size: int = CLUSTER_CELL_SIZE_PX,
) -> list[tuple[int, int]]:
    """
    Merge near-duplicate intersection points into cluster centroids.
    O(N), produces one point per physical corner regardless of how many
    history-buffer lines contributed to it.
    """
    if not points:
        return []

    buckets: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for x, y in points:
        key = (x // cell_size, y // cell_size)
        buckets.setdefault(key, []).append((x, y))

    return [
        (
            int(round(np.mean([p[0] for p in pts]))),
            int(round(np.mean([p[1] for p in pts]))),
        )
        for pts in buckets.values()
    ]


# ---------------------------------------------------------------------------
# Public intersection entry-point (drop-in replacement)
# ---------------------------------------------------------------------------

def find_hv_intersections_from_classified(
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
    image_shape: tuple[int, int] | tuple[int, int, int],
    max_points: int = 400,
) -> list[tuple[int, int]]:
    """
    Find grid corner candidates from classified horizontal and vertical lines.

    Pipeline
    --------
    1. (Optional) Merge near-parallel lines per orientation to reduce the
       O(H×V) intersection loop.  Controlled by LINE_MERGE_ENABLED in config.
       When disabled, all history-buffer lines are used directly — the cluster
       step removes the resulting near-duplicate points efficiently.
    2. Algebraic intersection with gap tolerance.
    3. Cluster near-duplicate points into canonical corners.
    4. Hard-cap to `max_points`.

    Call signature is identical to the original so play_runtime.py is unchanged.
    """
    if LINE_MERGE_ENABLED:
        h_input = merge_colinear_lines(horiz_lines, is_horiz=True)
        v_input = merge_colinear_lines(vert_lines,  is_horiz=False)
    else:
        # Skip merge — cluster at the end handles duplicates.
        # Simpler and avoids any merge-coordinate artefacts.
        h_input = horiz_lines
        v_input = vert_lines

    raw_points = extend_and_intersect(h_input, v_input, image_shape)
    corners    = cluster_points(raw_points)

    if max_points > 0 and len(corners) > max_points:
        corners = corners[:max_points]

    return corners


# ---------------------------------------------------------------------------
# Display helpers  (unchanged public API)
# ---------------------------------------------------------------------------

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


def build_edge_display(colour_img: np.ndarray) -> tuple[np.ndarray, list[tuple]]:
    """
    Full pipeline: colour mask → (clean) → Canny edges → classified Hough lines.

    Colour mask is morphologically closed before Canny (CLEAN_MASK_KERNEL_PX)
    to suppress fringe-pixel noise at block boundaries.
    Returns the display image and raw line list for history accumulation.
    """
    edges_grey = compute_edges(colour_img)
    lines_grey = find_lines(edges_grey)
    horiz_lines, vert_lines = classify_lines(lines_grey)
    disp_grey = draw_classified_lines(
        cv2.cvtColor(edges_grey, cv2.COLOR_GRAY2BGR),
        horiz_lines,
        vert_lines,
    )
    return disp_grey, lines_grey