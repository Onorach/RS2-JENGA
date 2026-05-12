"""
grid_generation.py
------------------
Edge-based line and grid-point generation for perception displays.

Intersection pipeline (v4):
  1. Colour mask is morphologically cleaned before Canny to reduce fringe
     misclassification noise at block boundaries.
  2. (Optional) Near-parallel lines within LINE_MERGE_BAND_PX are collapsed
     into one representative line using MIN/MAX extent preservation.
  3. Intersections are solved algebraically via a fully vectorised NumPy
     broadcast — all H×V pairs are evaluated simultaneously, replacing the
     v3 Python double-for-loop that cost ~122 K iterations per frame.
  4. Near-duplicate points are collapsed in two passes:
       Pass 1 — fast grid-bucket grouping (O(N)).
       Pass 2 — greedy centroid merge for points that straddle bucket
                 boundaries (O(M²) on the small centroid set, typically M<100).
"""
from __future__ import annotations

import cv2
import numpy as np

from colour_identification import compute_roi
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
    CLUSTER_MERGE_RADIUS_PX,
)


# ---------------------------------------------------------------------------
# Colour mask cleaning
# ---------------------------------------------------------------------------

def clean_colour_mask(colour_img: np.ndarray) -> np.ndarray:
    """
    Morphologically close the colour-mask image to fill fringe pixels at block
    boundaries before edge detection.  CLEAN_MASK_KERNEL_PX = 0 disables this.
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


def compute_combined_edges(
    colour_img: np.ndarray,
    original_bgr_img: np.ndarray | None = None,
) -> np.ndarray:
    """
    Combine edges from the generated colour mask and original BGR frame.

    The colour-mask edges remain the primary signal; optional original-frame
    edges are OR-combined to recover boundaries that may be weak in the mask.
    """
    mask_edges = compute_edges(colour_img)
    if original_bgr_img is None:
        return mask_edges

    roi_x, roi_y, roi_w, roi_h = compute_roi(
        int(original_bgr_img.shape[1]),
        int(original_bgr_img.shape[0]),
    )
    original_roi = original_bgr_img[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    if original_roi.shape[:2] != colour_img.shape[:2]:
        original_roi = cv2.resize(
            original_roi,
            (int(colour_img.shape[1]), int(colour_img.shape[0])),
            interpolation=cv2.INTER_LINEAR,
        )

    original_grey = cv2.cvtColor(original_roi, cv2.COLOR_BGR2GRAY)
    original_edges = cv2.Canny(original_grey, CANNY_GREY_LOW, CANNY_GREY_HIGH)
    return cv2.bitwise_or(mask_edges, original_edges)


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

    Uses MIN/MAX for the extent coordinates (parallel axis) so that short
    sub-segments from different frames combine into a line that spans the
    full physical edge rather than just the averaged centre portion.
    The perpendicular coordinate is averaged to get the best position estimate.
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
    Collapse near-parallel lines within `band` pixels of each other.
    Groups compare against their first element (not the running tail) to
    prevent chaining across multiple physical boundaries.
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
    group_anchor = key_fn(lines_sorted[0])

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
# Vectorised algebraic intersection  (replaces Python double-for-loop)
# ---------------------------------------------------------------------------

def extend_and_intersect(
    horiz_lines: list[tuple],
    vert_lines: list[tuple],
    image_shape: tuple,
    gap_tolerance: int = INTERSECTION_GAP_TOLERANCE_PX,
) -> list[tuple[int, int]]:
    """
    Find all H×V algebraic intersections in one vectorised NumPy pass.

    Why this is fast
    ----------------
    The v3 implementation used a Python double-for-loop over every
    (horiz, vert) pair.  With 350 horiz × 350 vert history lines that is
    ~122,500 Python iterations — slow because each iteration pays Python
    interpreter overhead (~100 ns each → ~12 ms just in loop cost).

    Here every pair is evaluated simultaneously using NumPy broadcasting:
      H  reshaped to (N_h, 1, 4)
      V  reshaped to (1,  N_v, 4)
    All arithmetic produces (N_h, N_v) arrays and runs in compiled C,
    typically 50-200× faster than the equivalent Python loop.

    Parametric form
    ---------------
        P_H(t) = (hx1 + t·dx_h,  hy1 + t·dy_h)
        P_V(u) = (vx1 + u·dx_v,  vy1 + u·dy_v)

    Solving P_H(t) = P_V(u) gives t and u via Cramer's rule.
    A candidate corner is kept when:
      • t ∈ [-tol_h, 1+tol_h]   (near the horiz segment, tol = gap/length)
      • u ∈ [-tol_v, 1+tol_v]   (near the vert  segment)
      • pixel (ix, iy) is inside the image bounds
    """
    if not horiz_lines or not vert_lines:
        return []

    img_h, img_w = int(image_shape[0]), int(image_shape[1])

    # Build float32 arrays: shape (N, 4)
    H = np.array(horiz_lines, dtype=np.float32)  # (N_h, 4)
    V = np.array(vert_lines,  dtype=np.float32)  # (N_v, 4)

    # Broadcast to (N_h, N_v) by inserting size-1 dimensions
    # H[:, None, :] → (N_h, 1,   4)
    # V[None, :, :] → (1,   N_v, 4)
    hx1 = H[:, None, 0];  hy1 = H[:, None, 1]
    hx2 = H[:, None, 2];  hy2 = H[:, None, 3]
    vx1 = V[None, :, 0];  vy1 = V[None, :, 1]
    vx2 = V[None, :, 2];  vy2 = V[None, :, 3]

    dx_h = hx2 - hx1;  dy_h = hy2 - hy1   # (N_h, 1)
    dx_v = vx2 - vx1;  dy_v = vy2 - vy1   # (1, N_v)

    denom = dx_h * dy_v - dy_h * dx_v      # (N_h, N_v)

    # Mask out parallel pairs to avoid divide-by-zero
    valid = np.abs(denom) > 1e-6
    denom_safe = np.where(valid, denom, 1.0)

    ox = vx1 - hx1  # (N_h, N_v)
    oy = vy1 - hy1

    t = (ox * dy_v - oy * dx_v) / denom_safe
    u = (ox * dy_h - oy * dx_h) / denom_safe

    # Per-pair gap tolerances
    len_h = np.maximum(1.0, np.sqrt(dx_h ** 2 + dy_h ** 2))  # (N_h, 1)
    len_v = np.maximum(1.0, np.sqrt(dx_v ** 2 + dy_v ** 2))  # (1, N_v)
    tol_h = gap_tolerance / len_h
    tol_v = gap_tolerance / len_v

    # Intersection pixel coordinates
    ix = np.round(hx1 + t * dx_h).astype(np.int32)
    iy = np.round(hy1 + t * dy_h).astype(np.int32)

    # Combined acceptance mask
    mask = (
        valid
        & (t >= -tol_h) & (t <= 1.0 + tol_h)
        & (u >= -tol_v) & (u <= 1.0 + tol_v)
        & (ix >= 0) & (ix < img_w)
        & (iy >= 0) & (iy < img_h)
    )

    xs = ix[mask]
    ys = iy[mask]

    return list(zip(xs.tolist(), ys.tolist()))


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

    Pass 1 — grid bucket (O(N))
    ---------------------------
    Each point is assigned to a (x//cell_size, y//cell_size) bucket.
    Points in the same bucket are averaged into one centroid.

    This handles the bulk of duplicates very cheaply, but it has a boundary
    artefact: two real duplicates that straddle a bucket edge (e.g. at x=14
    and x=16 with cell_size=15) land in adjacent buckets and produce two
    centroids instead of one.

    Pass 2 — greedy centroid merge (O(M²) on the centroid set, M << N)
    -------------------------------------------------------------------
    After Pass 1 we typically have M < 100 centroids.  A greedy scan merges
    any two centroids whose Chebyshev distance is within `merge_radius`.
    This resolves the bucket-boundary artefact without re-examining all N
    raw points.

    Both passes together are fast because N (raw points) is large but the
    O(N) pass reduces it to M, and M² is small.
    """
    if not points:
        return []

    # --- Pass 1: grid buckets ---
    buckets: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for x, y in points:
        key = (x // cell_size, y // cell_size)
        buckets.setdefault(key, []).append((x, y))

    centroids: list[tuple[int, int]] = [
        (
            int(round(np.mean([p[0] for p in pts]))),
            int(round(np.mean([p[1] for p in pts]))),
        )
        for pts in buckets.values()
    ]

    if len(centroids) <= 1 or merge_radius <= 0:
        return centroids

    # --- Pass 2: greedy merge of nearby centroids ---
    used = [False] * len(centroids)
    merged: list[tuple[int, int]] = []

    for i, c1 in enumerate(centroids):
        if used[i]:
            continue
        group = [c1]
        used[i] = True
        for j in range(i + 1, len(centroids)):
            if used[j]:
                continue
            c2 = centroids[j]
            # Chebyshev distance (max of |dx|, |dy|) — cheap, no sqrt
            if max(abs(c1[0] - c2[0]), abs(c1[1] - c2[1])) <= merge_radius:
                group.append(c2)
                used[j] = True
        merged.append(
            (
                int(round(np.mean([p[0] for p in group]))),
                int(round(np.mean([p[1] for p in group]))),
            )
        )

    return merged


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
    1. (Optional) Merge near-parallel lines per orientation (LINE_MERGE_ENABLED).
       When False, all history-buffer lines feed directly into the intersection
       step — deduplication is handled by the cluster step instead.
    2. Vectorised algebraic intersection (NumPy broadcast, no Python loop).
    3. Two-pass point clustering into canonical corners.
    4. Hard-cap to `max_points`.

    Call signature is identical to the original so play_runtime.py is unchanged.
    """
    if LINE_MERGE_ENABLED:
        h_input = merge_colinear_lines(horiz_lines, is_horiz=True)
        v_input = merge_colinear_lines(vert_lines,  is_horiz=False)
    else:
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


def build_edge_display(
    colour_img: np.ndarray,
    original_bgr_img: np.ndarray | None = None,
) -> tuple[np.ndarray, list[tuple]]:
    """
    Full pipeline: combined edges → classified Hough lines.

    Edges are extracted from:
      1) generated colour mask (with optional pre-clean), and
      2) original BGR frame (when provided),
    then merged prior to Hough and point generation.
    Returns the display image and raw line list for history accumulation.
    """
    edges_grey = compute_combined_edges(colour_img, original_bgr_img)
    lines_grey = find_lines(edges_grey)
    horiz_lines, vert_lines = classify_lines(lines_grey)
    disp_grey = draw_classified_lines(
        cv2.cvtColor(edges_grey, cv2.COLOR_GRAY2BGR),
        horiz_lines,
        vert_lines,
    )
    return disp_grey, lines_grey