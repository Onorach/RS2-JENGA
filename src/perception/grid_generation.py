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

from centre_seam import detect_centre_seam_lines
from perception_config import (
    CANNY_MASK_LOW,
    CANNY_MASK_HIGH,
    HOUGH_MASK_THRESHOLD,
    HOUGH_MASK_MIN_LENGTH,
    HOUGH_MASK_MAX_GAP,
    MAX_HORIZ_DEG,
    MAX_VERT_DEG,
    CLEAN_MASK_KERNEL_PX,
    INTERSECTION_GAP_TOLERANCE_PX,
    CLUSTER_CELL_SIZE_PX,
    CLUSTER_MERGE_RADIUS_PX,
    POINT_VALID_SIDE_BAND_PCT,
    POINT_VALID_CENTER_BAND_PCT,
    GRID_EXTRA_LAYERS_ON_TOP,
    GRID_EXTRAPOLATED_CENTER_HEIGHT_EXTEND_PCT,
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

def compute_edges(
    colour_img: np.ndarray,
    *,
    canny_low: int | None = None,
    canny_high: int | None = None,
) -> np.ndarray:
    """Compute Canny edges from the colour-mask image."""
    cleaned = clean_colour_mask(colour_img)
    grey = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)
    low = int(CANNY_MASK_LOW if canny_low is None else canny_low)
    high = int(CANNY_MASK_HIGH if canny_high is None else canny_high)
    return cv2.Canny(grey, low, high)


def preview_mask_canny(colour_img: np.ndarray, *, canny_low: int | None = None, canny_high: int | None = None) -> np.ndarray:
    """BGR preview of Canny edges from the colour-classification image."""
    edges = compute_edges(colour_img, canny_low=canny_low, canny_high=canny_high)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


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


def filter_vertical_lines_by_x_bands(
    vert_lines: list[tuple],
    roi_width: int,
) -> list[tuple]:
    """
    Keep only vertical lines in the left/right outer bands or the centre band.

    The colour mask produces a vertical Hough line wherever two differently
    coloured blocks meet, which clutters the interior of the tower with edges we
    do not use: the grid only cares about the two outer tower edges and the
    central seam.  This mirrors filter_points_by_x_bands but at the line level so
    the interior verticals are dropped before display AND intersection.
    """
    if roi_width <= 0 or not vert_lines:
        return []

    side_frac   = max(0.0, min(0.5, POINT_VALID_SIDE_BAND_PCT   / 100.0))
    half_center = max(0.0, POINT_VALID_CENTER_BAND_PCT / 100.0) * 0.5
    center_lo   = 0.5 - half_center
    center_hi   = 0.5 + half_center
    denom       = float(max(1, roi_width - 1))

    kept: list[tuple] = []
    for x1, y1, x2, y2 in vert_lines:
        x_frac = (0.5 * (float(x1) + float(x2))) / denom
        if (
            x_frac <= side_frac
            or x_frac >= 1.0 - side_frac
            or center_lo <= x_frac <= center_hi
        ):
            kept.append((x1, y1, x2, y2))
    return kept


def build_edge_display(
    colour_img: np.ndarray,
    depth_roi: np.ndarray | None = None,
) -> tuple[np.ndarray, list[tuple], np.ndarray, np.ndarray]:
    """
    Full pipeline: edges → lines → combined display.

    Behaviour:
      - Colour-mask Canny contributes BOTH horizontal and vertical Hough lines
        (layer boundaries + outer tower edges).
      - The tower's centre seam (the vertical line down its near corner) is the
        per-layer depth seam from centre_seam.detect_centre_seam_lines: for each
        layer band the largest colour blob's closest-to-camera column. Needs
        depth_roi; on the recoloured image the seam has no colour edge, which is
        why depth is used instead of Canny on the original frame.
      - The line sets are concatenated; the overlay shows them on top of the
        colour-mask edges with the detected seam.

    Returns
    -------
    disp_grey    : BGR image — edges with combined lines drawn.
    lines_all    : union of lines used for intersection detection.
    edges_colour : single-channel Canny from the colour mask.
    edges_seam   : single-channel image of the detected depth-seam columns,
                   rendered for the centre-seam preview window.
    """
    edges_colour = compute_edges(colour_img)
    # Colour-mask edges run on the full ROI.
    edges_colour_search = edges_colour

    lines_colour_all = find_lines(
        edges_colour_search,
        HOUGH_MASK_THRESHOLD,
        HOUGH_MASK_MIN_LENGTH,
        HOUGH_MASK_MAX_GAP,
    )
    horiz_colour, vert_colour = classify_lines(lines_colour_all)

    # Drop the interior colour-boundary verticals (block-to-block seams between
    # different colours): only the outer tower edges and the centre matter.
    vert_colour = filter_vertical_lines_by_x_bands(vert_colour, colour_img.shape[1])

    # Per-layer depth seam: one vertical segment per layer band drives the grid.
    vert_centre = detect_centre_seam_lines(colour_img, depth_roi, horiz_colour)

    # Render the detected seams into a single-channel image for the preview window.
    edges_seam = np.zeros(colour_img.shape[:2], dtype=np.uint8)
    for x1, y1, x2, y2 in vert_centre:
        cv2.line(edges_seam, (x1, y1), (x2, y2), 255, 1)

    lines_all = list(horiz_colour) + list(vert_colour) + list(vert_centre)

    combined = cv2.bitwise_or(edges_colour_search, edges_seam)
    horiz_lines, vert_lines = classify_lines(lines_all)
    disp_grey = draw_classified_lines(
        cv2.cvtColor(combined, cv2.COLOR_GRAY2BGR),
        horiz_lines,
        vert_lines,
    )
    return disp_grey, lines_all, edges_colour_search, edges_seam


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


def _median_row_step_y(mapped_grid: list[list[tuple[int, int]]]) -> float | None:
    """Typical vertical spacing between grid rows (image y increases downward)."""
    if len(mapped_grid) < 2:
        return None
    dys: list[float] = []
    for r in range(len(mapped_grid) - 1):
        dy = float(mapped_grid[r + 1][0][1] - mapped_grid[r][0][1])
        if dy > 0.0:
            dys.append(dy)
    if not dys:
        return None
    return float(np.median(dys))


def _extrapolate_rows_above(
    mapped_grid: list[list[tuple[int, int]]],
    extra_layers: int,
    center_height_extend_pct: float = GRID_EXTRAPOLATED_CENTER_HEIGHT_EXTEND_PCT,
) -> list[list[tuple[int, int]]]:
    """
    Prepend ``extra_layers`` synthetic grid rows above the detected top row.

    Left/right x and y use the median row step.  Centre x is unchanged; centre
    y uses the same step extended by ``center_height_extend_pct`` (perspective).
    """
    if extra_layers <= 0 or len(mapped_grid) < 2:
        return mapped_grid

    step_y = _median_row_step_y(mapped_grid)
    if step_y is None or step_y <= 0.0:
        return mapped_grid

    centre_scale = 1.0 + max(0.0, float(center_height_extend_pct)) / 100.0
    top_row = mapped_grid[0]
    extra_rows: list[list[tuple[int, int]]] = []
    for i in range(extra_layers, 0, -1):
        left_x, left_y = top_row[0]
        centre_x, centre_y = top_row[1]
        right_x, right_y = top_row[2]
        edge_y = int(round(left_y - step_y * i))
        centre_y_out = int(round(centre_y - step_y * i * centre_scale))
        right_y_out = int(round(right_y - step_y * i))
        extra_rows.append([
            (left_x, edge_y),
            (centre_x, centre_y_out),
            (right_x, right_y_out),
        ])
    return extra_rows + mapped_grid


def build_layer_cells_from_points(
    points_roi: list[tuple[int, int]],
    roi_xywh: tuple[int, int, int, int],
) -> list[list[dict]]:
    """
    Build dynamic layer cells from detected and locked grid points.

    Points are expected in ROI-space; returned cells use full-frame coordinates.
    Assumes a 3-column grid; derives the number of layers from the point count.
    After mapping detected points, ``GRID_EXTRA_LAYERS_ON_TOP`` empty layer bands
    are extrapolated above the tower for blocks placed during live play.
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

    extra_layers = max(0, int(GRID_EXTRA_LAYERS_ON_TOP))
    detected_layer_count = len(mapped_grid) - 1
    mapped_grid = _extrapolate_rows_above(mapped_grid, extra_layers)

    dynamic_layers: list[list[dict]] = []
    for r in range(len(mapped_grid) - 1):
        top, bot = mapped_grid[r], mapped_grid[r + 1]
        if len(top) < 3 or len(bot) < 3:
            continue
        left_corners  = [top[0], top[1], bot[0], bot[1]]
        right_corners = [top[1], top[2], bot[1], bot[2]]
        if any(c is None for c in left_corners + right_corners):
            continue
        extrapolated = r < extra_layers
        dynamic_layers.append([
            {
                "name": f"left_cell_r{r}",
                "corners": left_corners,
                "extrapolated": extrapolated,
            },
            {
                "name": f"right_cell_r{r}",
                "corners": right_corners,
                "extrapolated": extrapolated,
            },
        ])
    if extra_layers > 0 and dynamic_layers:
        print(
            f"[grid] locked {detected_layer_count} detected layer(s), "
            f"added {extra_layers} extrapolated on top "
            f"({len(dynamic_layers)} total layers)"
        )
    return dynamic_layers
