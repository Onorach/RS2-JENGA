"""
grid_generation.py
------------------
Edge-based line and grid-point generation for perception displays.

Intersection pipeline:
  1. Colour mask is morphologically cleaned before Canny to reduce fringe noise.
  2. Intersections are solved algebraically via vectorised NumPy broadcasting.
  3. Near-duplicate points are collapsed in two passes:
       Pass 1 — grid-bucket grouping (O(N)).
       Pass 2 — greedy centroid merge for points straddling bucket boundaries.
"""
from __future__ import annotations

import cv2
import numpy as np

from colour_identification import compute_roi
from perception_config import (
    CANNY_MASK_LOW,
    CANNY_MASK_HIGH,
    CANNY_ORIGINAL_LOW,
    CANNY_ORIGINAL_HIGH,
    CANNY_CENTRE_BAND_PCT,
    HOUGH_MASK_THRESHOLD,
    HOUGH_MASK_MIN_LENGTH,
    HOUGH_MASK_MAX_GAP,
    HOUGH_ORIGINAL_THRESHOLD,
    HOUGH_ORIGINAL_MIN_LENGTH,
    HOUGH_ORIGINAL_MAX_GAP,
    MAX_HORIZ_DEG,
    MAX_VERT_DEG,
    CLEAN_MASK_KERNEL_PX,
    INTERSECTION_GAP_TOLERANCE_PX,
    CLUSTER_CELL_SIZE_PX,
    CLUSTER_MERGE_RADIUS_PX,
    POINT_VALID_SIDE_BAND_PCT,
    POINT_VALID_CENTER_BAND_PCT,
)


# ---------------------------------------------------------------------------
# Colour mask cleaning
# ---------------------------------------------------------------------------

def clean_colour_mask(colour_img: np.ndarray) -> np.ndarray:
    """Morphologically close the colour mask to fill fringe pixels at block boundaries."""
    if CLEAN_MASK_KERNEL_PX <= 0:
        return colour_img
    k = cv2.getStructuringElement(
        cv2.MORPH_RECT, (CLEAN_MASK_KERNEL_PX, CLEAN_MASK_KERNEL_PX),
    )
    return cv2.morphologyEx(colour_img, cv2.MORPH_CLOSE, k)


# ---------------------------------------------------------------------------
# Edge and line detection
# ---------------------------------------------------------------------------

def apply_centre_band_mask(img: np.ndarray) -> np.ndarray:
    """Zero pixels outside the centred horizontal band (CANNY_CENTRE_BAND_PCT)."""
    pct = float(CANNY_CENTRE_BAND_PCT)
    if pct >= 100.0 or pct <= 0.0:
        return img
    h, w = img.shape[:2]
    band_w = max(1, int(round(w * pct / 100.0)))
    x_lo   = max(0, (w - band_w) // 2)
    x_hi   = min(w, x_lo + band_w)
    masked = np.zeros_like(img)
    masked[:, x_lo:x_hi] = img[:, x_lo:x_hi]
    return masked


def compute_edges(colour_img: np.ndarray) -> np.ndarray:
    """Compute Canny edges from the colour-mask image."""
    cleaned = clean_colour_mask(colour_img)
    grey = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
    return cv2.Canny(grey, CANNY_MASK_LOW, CANNY_MASK_HIGH)


def compute_original_edges(
    original_bgr_img: np.ndarray,
    target_shape: tuple[int, int],
) -> np.ndarray:
    """
    Canny edges from the original image in ROI space.

    If original_bgr_img already matches target_shape, it is treated as a
    pre-cropped ROI. Otherwise, ROI is extracted via compute_roi.
    """
    th, tw = target_shape
    if original_bgr_img.shape[:2] == (th, tw):
        original_roi = original_bgr_img
    else:
        roi_x, roi_y, roi_w, roi_h = compute_roi(
            int(original_bgr_img.shape[1]), int(original_bgr_img.shape[0]),
        )
        original_roi = original_bgr_img[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    if original_roi.shape[:2] != (th, tw):
        original_roi = cv2.resize(
            original_roi, (int(tw), int(th)), interpolation=cv2.INTER_LINEAR,
        )
    return cv2.Canny(
        cv2.cvtColor(original_roi, cv2.COLOR_BGR2GRAY),
        CANNY_ORIGINAL_LOW,
        CANNY_ORIGINAL_HIGH,
    )


def compute_combined_edges(
    colour_img: np.ndarray,
    original_bgr_img: np.ndarray | None = None,
) -> np.ndarray:
    """OR-combine Canny from the colour mask and (optionally) the original BGR frame."""
    mask_edges = compute_edges(colour_img)
    if original_bgr_img is None:
        return mask_edges
    original_edges = compute_original_edges(original_bgr_img, colour_img.shape[:2])
    return cv2.bitwise_or(mask_edges, original_edges)


def find_lines(
    edges: np.ndarray,
    threshold: int,
    min_line_length: int,
    max_line_gap: int,
) -> list[tuple]:
    """Run probabilistic Hough transform and return raw line tuples."""
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=max(1, int(threshold)),
        minLineLength=max(1, int(min_line_length)),
        maxLineGap=max(0, int(max_line_gap)),
    )
    return [] if lines is None else [tuple(l[0]) for l in lines]


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
    vert_lines:  list[tuple] = []
    for x1, y1, x2, y2 in lines:
        kind = _classify_line(x1, y1, x2, y2)
        if kind == "horiz":
            horiz_lines.append((x1, y1, x2, y2))
        elif kind == "vert":
            vert_lines.append((x1, y1, x2, y2))
    return horiz_lines, vert_lines


# ---------------------------------------------------------------------------
# Vectorised algebraic intersection
# ---------------------------------------------------------------------------

def extend_and_intersect(
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
    image_shape: tuple,
    gap_tolerance: int = INTERSECTION_GAP_TOLERANCE_PX,
) -> list[tuple[int, int]]:
    """
    Find all H×V algebraic intersections via NumPy broadcasting.

    Each pair is solved parametrically using Cramer's rule.  A candidate
    corner is kept when both parameters are within gap_tolerance/length of
    [0, 1] and the pixel falls inside the image bounds.
    """
    if not horiz_lines or not vert_lines:
        return []

    img_h, img_w = int(image_shape[0]), int(image_shape[1])
    H = np.array(horiz_lines, dtype=np.float32)   # (N_h, 4)
    V = np.array(vert_lines,  dtype=np.float32)   # (N_v, 4)

    hx1 = H[:, None, 0]; hy1 = H[:, None, 1]
    hx2 = H[:, None, 2]; hy2 = H[:, None, 3]
    vx1 = V[None, :, 0]; vy1 = V[None, :, 1]
    vx2 = V[None, :, 2]; vy2 = V[None, :, 3]

    dx_h = hx2 - hx1; dy_h = hy2 - hy1
    dx_v = vx2 - vx1; dy_v = vy2 - vy1

    denom      = dx_h * dy_v - dy_h * dx_v
    valid      = np.abs(denom) > 1e-6
    denom_safe = np.where(valid, denom, 1.0)

    ox = vx1 - hx1
    oy = vy1 - hy1
    t  = (ox * dy_v - oy * dx_v) / denom_safe
    u  = (ox * dy_h - oy * dx_h) / denom_safe

    len_h = np.maximum(1.0, np.sqrt(dx_h ** 2 + dy_h ** 2))
    len_v = np.maximum(1.0, np.sqrt(dx_v ** 2 + dy_v ** 2))
    tol_h = gap_tolerance / len_h
    tol_v = gap_tolerance / len_v

    ix = np.round(hx1 + t * dx_h).astype(np.int32)
    iy = np.round(hy1 + t * dy_h).astype(np.int32)

    mask = (
        valid
        & (t >= -tol_h) & (t <= 1.0 + tol_h)
        & (u >= -tol_v) & (u <= 1.0 + tol_v)
        & (ix >= 0) & (ix < img_w)
        & (iy >= 0) & (iy < img_h)
    )

    return list(zip(ix[mask].tolist(), iy[mask].tolist()))


# ---------------------------------------------------------------------------
# Two-pass point clustering
# ---------------------------------------------------------------------------

def cluster_points(
    points: list[tuple[int, int]],
    cell_size: int = CLUSTER_CELL_SIZE_PX,
    merge_radius: int = CLUSTER_MERGE_RADIUS_PX,
) -> list[tuple[int, int]]:
    """
    Collapse near-duplicate intersection points into canonical corners.

    Pass 1 — grid-bucket grouping (O(N)): points in the same cell_size bucket
    are averaged.  Points straddling a bucket boundary produce two centroids.

    Pass 2 — greedy centroid merge (O(M²), M << N): any two centroids within
    merge_radius (Chebyshev distance) are merged to fix bucket-boundary splits.
    """
    if not points:
        return []

    # Pass 1: grid buckets.
    buckets: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for x, y in points:
        key = (x // cell_size, y // cell_size)
        buckets.setdefault(key, []).append((x, y))

    centroids = [
        (int(round(np.mean([p[0] for p in pts]))),
         int(round(np.mean([p[1] for p in pts]))))
        for pts in buckets.values()
    ]

    if len(centroids) <= 1 or merge_radius <= 0:
        return centroids

    # Pass 2: greedy merge.
    used   = [False] * len(centroids)
    merged: list[tuple[int, int]] = []

    for i, c1 in enumerate(centroids):
        if used[i]:
            continue
        group   = [c1]
        used[i] = True
        for j in range(i + 1, len(centroids)):
            if used[j]:
                continue
            c2 = centroids[j]
            if max(abs(c1[0] - c2[0]), abs(c1[1] - c2[1])) <= merge_radius:
                group.append(c2)
                used[j] = True
        merged.append(
            (int(round(np.mean([p[0] for p in group]))),
             int(round(np.mean([p[1] for p in group]))))
        )

    return merged


# ---------------------------------------------------------------------------
# Public intersection entry-point
# ---------------------------------------------------------------------------

def find_hv_intersections_from_classified(
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
    image_shape: tuple[int, int] | tuple[int, int, int],
    max_points: int = 400,
) -> list[tuple[int, int]]:
    """
    Full pipeline: vectorised intersection → clustering.
    Hard-caps output to max_points.
    """
    raw_points = extend_and_intersect(horiz_lines, vert_lines, image_shape)
    corners    = cluster_points(raw_points)

    if max_points > 0 and len(corners) > max_points:
        corners = corners[:max_points]

    return corners


# ---------------------------------------------------------------------------
# Display helpers
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


def build_edge_display(
    colour_img: np.ndarray,
    original_bgr_img: np.ndarray | None = None,
) -> tuple[np.ndarray, list[tuple], np.ndarray, np.ndarray]:
    """
    Full pipeline: Canny on each source → Hough lines → combined display.

    Behaviour:
      - Colour-mask Canny contributes BOTH horizontal and vertical Hough lines.
      - Original-image Canny contributes ONLY vertical Hough lines.
      - The two line sets are concatenated; the overlay shows them on top of
        the OR of both Canny edge images.

    Returns
    -------
    disp_grey      : BGR image — OR of both Canny edges with combined lines drawn.
    lines_all      : union of Hough lines used for intersection detection.
    edges_colour   : single-channel Canny from the colour mask.
    edges_original : single-channel Canny from the original BGR frame
                     (zeros if original_bgr_img was not provided).
    """
    edges_colour = compute_edges(colour_img)
    edges_original = (
        compute_original_edges(original_bgr_img, colour_img.shape[:2])
        if original_bgr_img is not None
        else np.zeros_like(edges_colour)
    )
    # Colour-mask edges run on the full ROI.
    edges_colour_search = edges_colour
    # Original-image edges are restricted to the configured centre band.
    edges_original_search = apply_centre_band_mask(edges_original)

    lines_colour_all = find_lines(
        edges_colour_search,
        HOUGH_MASK_THRESHOLD,
        HOUGH_MASK_MIN_LENGTH,
        HOUGH_MASK_MAX_GAP,
    )
    if original_bgr_img is not None:
        _, vert_original = classify_lines(
            find_lines(
                edges_original_search,
                HOUGH_ORIGINAL_THRESHOLD,
                HOUGH_ORIGINAL_MIN_LENGTH,
                HOUGH_ORIGINAL_MAX_GAP,
            )
        )
    else:
        vert_original = []

    lines_all = list(lines_colour_all) + list(vert_original)

    combined = cv2.bitwise_or(edges_colour_search, edges_original_search)
    horiz_lines, vert_lines = classify_lines(lines_all)
    disp_grey = draw_classified_lines(
        cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR),
        horiz_lines,
        vert_lines,
    )
    return disp_grey, lines_all, edges_colour_search, edges_original_search


# ---------------------------------------------------------------------------
# Grid-point filtering and cell building
# ---------------------------------------------------------------------------

def filter_points_by_x_bands(
    points_roi: list[tuple[int, int]],
    roi_width: int,
) -> list[tuple[int, int]]:
    """Keep only points in the left/right outer bands and the centre band."""
    if roi_width <= 0 or not points_roi:
        return []

    side_frac   = max(0.0, min(0.5, POINT_VALID_SIDE_BAND_PCT   / 100.0))
    half_center = max(0.0, POINT_VALID_CENTER_BAND_PCT / 100.0) * 0.5
    center_lo   = 0.5 - half_center
    center_hi   = 0.5 + half_center
    denom       = float(max(1, roi_width - 1))

    return [
        (ix, iy) for ix, iy in points_roi
        if (x_frac := float(ix) / denom) <= side_frac
        or x_frac >= 1.0 - side_frac
        or center_lo <= x_frac <= center_hi
    ]


def build_layer_cells_from_points(
    points_roi: list[tuple[int, int]],
    roi_xywh: tuple[int, int, int, int],
) -> list[list[dict]]:
    """
    Build dynamic layer cells from detected and locked grid points.

    Points are expected in ROI-space; returned cells use full-frame coordinates.
    Assumes a 3-column grid; derives the number of layers from the point count.
    """
    if not points_roi:
        return []

    rx, ry, _, _ = roi_xywh
    detected_full = np.array(
        [(int(ix + rx), int(iy + ry)) for ix, iy in points_roi],
        dtype=np.float32,
    )

    cols         = 3
    total_points = int(len(detected_full))
    num_layers   = (total_points - 3) // 3
    if num_layers < 1:
        return []
    rows     = num_layers + 1
    expected = rows * cols
    if total_points < expected:
        return []

    # Sort by y, take the top `expected` points, then sort each row by x.
    y_order  = np.argsort(detected_full[:, 1])
    selected = detected_full[y_order][:expected]

    mapped_grid: list[list[tuple[int, int]]] = []
    for r in range(rows):
        row_pts   = selected[r * cols:(r + 1) * cols]
        row_x_ord = np.argsort(row_pts[:, 0])
        mapped_grid.append([(int(px), int(py)) for px, py in row_pts[row_x_ord]])

    dynamic_layers: list[list[dict]] = []
    for r in range(len(mapped_grid) - 1):
        top, bot = mapped_grid[r], mapped_grid[r + 1]
        if len(top) < 3 or len(bot) < 3:
            continue
        left_corners  = [top[0], top[1], bot[0], bot[1]]
        right_corners = [top[1], top[2], bot[1], bot[2]]
        if any(c is None for c in left_corners + right_corners):
            continue
        dynamic_layers.append([
            {"name": f"left_cell_r{r}",  "corners": left_corners},
            {"name": f"right_cell_r{r}", "corners": right_corners},
        ])
    return dynamic_layers
