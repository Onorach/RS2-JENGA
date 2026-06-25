"""
block_centroids.py
------------------
All block centroid computation for the Jenga perception pipeline.

Design
------
Each Jenga layer shows two faces to the camera:
  - End-on face  : the camera sees the short end of the blocks in a row.
  - Side-on face : the camera sees the long sides of the blocks.

The end-on cell is where block colours are counted and centroids measured.

For each colour blob in the end-on cell the depth sensor lets us find a
"split line" — the x-column where the near face of the block meets the far
face.  Pixels on the outside of that line (near face) give a centroid that
sits on the visible face of the block rather than averaged across both faces.

Front-block rule
----------------
The FRONT block (closest to camera, index 0 in front→mid→back order) is
the only block whose near face may be partially or fully visible from the
OPPOSITE (side-on) cell.  Every call here searches both cells:

  1. End-on cell   — primary source for all three blocks.
  2. Opposite cell — secondary source, used when a colour has no valid
                     result from the end-on cell.

Because the side-on cell usually shows only one dominant colour (the long
face of the front block) the opposite-cell search rarely produces false
positives for mid/back blocks.

Two modes
---------
Normal analysis (called from analyse_layer every frame):
  - robust_stat = "mean"
  - require_split = False  (falls back to depth-gated mean if no split found)

Probe monitoring (called from update_tower_centroids_for_probe):
  - robust_stat = "median"
  - require_split = True   (only returns a centroid when a split is found)
  This is stricter because small errors in the baseline vs live comparison
  would create false shift signals.

Public API
----------
  compute_layer_centroids(bgr, depth, left_cell, right_cell, orientation,
                          robust_stat, require_split)
      -> dict[colour_str, (x_px, y_px)]

  compute_layer_blob_centroids(bgr, depth, left_cell, right_cell, orientation,
                               robust_stat)
      -> list[dict]  one entry per disconnected same-colour blob on end-on face

  compute_split_x_per_colour(bgr, depth, left_cell, right_cell, orientation)
      -> dict[colour_str, x_px]
      Used by annotate_depth_split_lines_for_tower for visualisation only.
"""
from __future__ import annotations

import numpy as np
import cv2

from colour_identification import frame_colour_mask
from centre_seam import closest_depth_column
from perception_config import (
    HSV_RANGES,
    CENTROID_HINT_SEARCH_RADIUS_PX,
    BLOCK_CENTROID_MIN_BLOB_PX,
)

# Minimum pixels for a colour blob to be considered valid.
MIN_COLOUR_PIXELS = 50
MIN_COLOUR_PCT    = 10.0   # % of cell area


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _components_ge_min_area(
    mask: np.ndarray,
    min_area_px: int,
) -> list[tuple[int, np.ndarray]]:
    if not bool(mask.any()):
        return []
    n_labels, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8,
    )
    out: list[tuple[int, np.ndarray]] = []
    for label in range(1, n_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= int(min_area_px):
            out.append((area, labels == label))
    return out


def filter_mask_to_primary_blob(
    mask: np.ndarray,
    min_area_px: int | None = None,
    prefer_xy: tuple[float, float] | None = None,
) -> np.ndarray:
    """
    Keep a single connected component from a boolean mask.

    Drops small colour slithers at block boundaries. When prefer_xy is given,
    prefer the component containing that point, otherwise the largest component.
    """
    min_area = int(BLOCK_CENTROID_MIN_BLOB_PX if min_area_px is None else min_area_px)
    comps = _components_ge_min_area(mask, min_area)
    if not comps:
        return np.zeros_like(mask, dtype=bool)

    if prefer_xy is not None:
        px, py = prefer_xy
        ix = int(round(float(px)))
        iy = int(round(float(py)))
        h, w = mask.shape[:2]
        if 0 <= ix < w and 0 <= iy < h:
            for _area, comp in sorted(comps, key=lambda item: -item[0]):
                if comp[iy, ix]:
                    return comp

        best_comp: np.ndarray | None = None
        best_dist = float("inf")
        for _area, comp in comps:
            ys, xs = np.where(comp)
            cx = float(np.mean(xs))
            cy = float(np.mean(ys))
            dist = (cx - float(px)) ** 2 + (cy - float(py)) ** 2
            if dist < best_dist:
                best_dist = dist
                best_comp = comp
        if best_comp is not None:
            return best_comp

    return max(comps, key=lambda item: item[0])[1]


def blob_area_at_xy(
    bgr: np.ndarray,
    cell: dict,
    colour: str,
    x_px: float,
    y_px: float,
    min_area_px: int | None = None,
) -> int:
    """Return connected-component area for colour blob containing (x, y) in cell."""
    min_area = int(BLOCK_CENTROID_MIN_BLOB_PX if min_area_px is None else min_area_px)
    ih, iw = bgr.shape[:2]
    quad = _quad_mask((ih, iw), cell["corners"])
    mask = quad & frame_colour_mask(bgr, colour)
    for area, comp in _components_ge_min_area(mask, min_area):
        iy = int(round(float(y_px)))
        ix = int(round(float(x_px)))
        if 0 <= iy < ih and 0 <= ix < iw and comp[iy, ix]:
            return area
    return 0


def _quad_mask(shape: tuple[int, int], corners: list) -> np.ndarray:
    """Boolean mask (H×W) True inside the quad [TL, TR, BL, BR]."""
    tl, tr, bl, br = corners
    pts = np.array([tl, tr, br, bl], dtype=np.int32).reshape(-1, 1, 2)
    m = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(m, [pts], 255)
    return m.astype(bool)


def _median_depth_in_cell(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    cell: dict,
) -> float | None:
    """
    Median depth (mm) of all valid depth pixels inside the cell quad.
    Used to build a depth gate that removes pixels from adjacent layers
    that share the same colour but sit at a different distance.
    """
    if depth is None:
        return None
    ih, iw = bgr.shape[:2]
    quad = _quad_mask((ih, iw), cell["corners"])
    d = depth[quad].astype(np.float32)
    valid = d[(d > 0) & np.isfinite(d)]
    return float(np.median(valid)) if len(valid) >= 10 else None


def _depth_gate(
    depth: np.ndarray,
    target_mm: float | None,
    tolerance_mm: float = 40.0,
) -> np.ndarray | None:
    """Boolean mask True where depth is within ±tolerance of target_mm."""
    if target_mm is None:
        return None
    df = depth.astype(np.float32)
    return (df > 0) & np.isfinite(df) & (np.abs(df - target_mm) <= tolerance_mm)


def _split_x_and_min_depth(
    depth: np.ndarray,
    mask: np.ndarray,
) -> tuple[float | None, float | None]:
    """
    Find the depth split line x AND the minimum depth value for a colour blob.

    Strategy: the near face of the block contains the closest (shallowest)
    depth pixels.  We find the minimum depth in the blob, collect all pixels
    within 1 mm of it (sensor quantisation noise) and return their mean x.  That
    x is the near-face edge — pixels outside this line belong to the near face.

    Delegates to centre_seam.closest_depth_column, the single shared
    closest-to-camera-column primitive also used for the grid centre seam.

    Returns (split_x, min_depth_mm).  Both are None when no valid pixels exist.
    min_depth_mm is exposed so callers can compare across cells to decide which
    cell is seeing the true near face (see _combined_split_x_per_colour).
    """
    return closest_depth_column(depth, mask, depth_tol_mm=1.0, stat="mean")


def _split_x_from_closest_pixels(
    depth: np.ndarray,
    mask: np.ndarray,
) -> float | None:
    """Convenience wrapper — returns only split_x (min_depth discarded)."""
    sx, _ = _split_x_and_min_depth(depth, mask)
    return sx


def _centre_seam_x(left_cell: dict) -> float:
    """X coordinate of the vertical seam between left and right lane cells."""
    return float(left_cell["corners"][1][0])


def _endon_side_x_mask(
    x_grid: np.ndarray,
    centre_seam_x: float,
    orientation: str,
) -> np.ndarray:
    """True where x lies on the end-on side of the layer centre seam."""
    if orientation == "left":
        return x_grid <= float(centre_seam_x)
    return x_grid >= float(centre_seam_x)


def _enforce_centroid_endon_side(
    cx: float,
    centre_seam_x: float,
    orientation: str,
) -> float:
    """Clamp centroid x to the end-on half of the layer (correct side of seam)."""
    if orientation == "left":
        return min(cx, float(centre_seam_x))
    return max(cx, float(centre_seam_x))


def _finalize_centroid_x(
    cx: float,
    *,
    centre_seam_x: float,
    orientation: str,
    split_x: float | None = None,
) -> float:
    if split_x is not None:
        cx = _enforce_centroid_face_side(cx, split_x, orientation)
    return _enforce_centroid_endon_side(cx, centre_seam_x, orientation)


def _enforce_centroid_face_side(cx: float, split_x: float, orientation: str) -> float:
    """
    Clamp a centroid x so it always sits on the near-face side of the split line.

    For a right-facing layer the near face is at HIGH x (cx >= split_x).
    For a left-facing layer the near face is at LOW x  (cx <= split_x).

    This must be applied to every path that returns a centroid so the position
    never drifts to the far-face side regardless of which fallback path ran.
    """
    if orientation == "left":
        return min(cx, float(split_x))
    else:
        return max(cx, float(split_x))


def _combined_split_info_per_colour(
    bgr: np.ndarray,
    depth: np.ndarray,
    endon_cell: dict,
    opposite_cell: dict,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
) -> dict[str, tuple[float, float]]:
    """
    Find split_x per colour by searching each cell independently and picking
    the one whose minimum depth is shallower (closer to the camera).

    WHY the depth gate is intentionally omitted here
    ------------------------------------------------
    Applying a ±40 mm depth gate before the min-depth search defeats the
    purpose: if the block has been pushed more than 40 mm from the cell
    median (forward or backward), its colour pixels are filtered out and the
    split_x search finds nothing.  The minimum-depth search is inherently
    self-discriminating — it looks for the shallowest pixels in the colour
    blob, which are always on the near face — so no gate is needed at this
    stage.  The depth gate is still used later in _compute_combined_centroid
    to keep same-colour pixels from adjacent layers out of the centroid.
    """
    ih, iw = bgr.shape[:2]

    endon_quad    = _quad_mask((ih, iw), endon_cell["corners"])
    opposite_quad = _quad_mask((ih, iw), opposite_cell["corners"])

    result: dict[str, tuple[float, float]] = {}
    for colour in HSV_RANGES:
        colour_hsv = frame_colour_mask(bgr, colour)

        # Raw colour masks — NO depth gate here (see docstring).
        endon_mask    = endon_quad & colour_hsv
        opposite_mask = opposite_quad & colour_hsv

        # Search each cell independently.
        sx_endon,    min_d_endon    = _split_x_and_min_depth(depth, endon_mask)
        sx_opposite, min_d_opposite = _split_x_and_min_depth(depth, opposite_mask)

        if sx_endon is None and sx_opposite is None:
            continue
        elif sx_endon is None:
            result[colour] = (float(sx_opposite), float(min_d_opposite))  # type: ignore[arg-type]
        elif sx_opposite is None:
            result[colour] = (float(sx_endon), float(min_d_endon))  # type: ignore[arg-type]
        else:
            # Both cells see this colour — the cell with the smaller (closer)
            # minimum depth is looking at the near face; use its split_x.
            if min_d_endon <= min_d_opposite:
                result[colour] = (float(sx_endon), float(min_d_endon))
            else:
                result[colour] = (float(sx_opposite), float(min_d_opposite))

    return result


def _combined_split_x_per_colour(
    bgr: np.ndarray,
    depth: np.ndarray,
    endon_cell: dict,
    opposite_cell: dict,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
) -> dict[str, float]:
    info = _combined_split_info_per_colour(
        bgr,
        depth,
        endon_cell,
        opposite_cell,
        endon_target_mm,
        opposite_target_mm,
    )
    return {colour: values[0] for colour, values in info.items()}


def _compute_combined_centroid(
    bgr: np.ndarray,
    depth: np.ndarray,
    endon_cell: dict,
    opposite_cell: dict,
    colour: str,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
    split_x: float,
    orientation: str,
    robust_stat: str,
    centre_seam_x: float,
) -> tuple[float, float] | None:
    """
    Compute the near-face centroid using end-on cell pixels on the correct
    side of the centre seam only.
    """
    del opposite_cell, opposite_target_mm
    ih, iw = bgr.shape[:2]
    colour_hsv = frame_colour_mask(bgr, colour)
    endon_quad = _quad_mask((ih, iw), endon_cell["corners"])
    endon_mask = endon_quad & colour_hsv

    endon_gate = _depth_gate(depth, endon_target_mm, tolerance_mm=80.0)
    if endon_gate is not None:
        gated = endon_mask & endon_gate
        if int(gated.sum()) >= MIN_COLOUR_PIXELS:
            endon_mask = gated

    endon_mask = filter_mask_to_primary_blob(endon_mask)
    if int(endon_mask.sum()) < MIN_COLOUR_PIXELS:
        return None

    fn = np.median if str(robust_stat).strip().lower() == "median" else np.mean
    x_grid = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    endon_side = _endon_side_x_mask(x_grid, centre_seam_x, orientation)

    if orientation == "left":
        face_mask = endon_mask & endon_side & (x_grid <= float(split_x))
    else:
        face_mask = endon_mask & endon_side & (x_grid >= float(split_x))

    ys, xs = np.where(face_mask)
    if len(xs) < max(10, MIN_COLOUR_PIXELS // 5):
        ys, xs = np.where(endon_mask & endon_side)
        if len(xs) < max(10, MIN_COLOUR_PIXELS // 5):
            return None

    cx = _finalize_centroid_x(
        float(fn(xs)),
        centre_seam_x=centre_seam_x,
        orientation=orientation,
        split_x=split_x,
    )
    return cx, float(fn(ys))


def _centroids_in_one_cell(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    cell: dict,
    orientation: str,
    target_depth_mm: float | None,
    robust_stat: str,
    require_split: bool,
    override_split_x: dict[str, float] | None = None,
    centre_seam_x: float | None = None,
) -> dict[str, tuple[float, float]]:
    """
    Compute near-face centroid (x, y) per colour in a single cell.

    orientation      : "left" or "right" — determines which side of the split
                       is the near (outside) face.
    require_split    : if True, only return a centroid when a split was found.
                       if False, fall back to depth-gated mean when no split.
    override_split_x : pre-computed split_x per colour from a combined
                       both-cell search (see _combined_split_x_per_colour).
                       When provided, skips the per-cell split_x search so
                       the front block's true near-face edge is always used.
    """
    ih, iw = bgr.shape[:2]
    quad   = _quad_mask((ih, iw), cell["corners"])
    total  = int(quad.sum())
    if total == 0:
        return {}

    gate    = _depth_gate(depth, target_depth_mm) if depth is not None else None
    use_med = str(robust_stat).strip().lower() == "median"
    x_grid  = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    endon_side = (
        _endon_side_x_mask(x_grid, centre_seam_x, orientation)
        if centre_seam_x is not None
        else np.ones((ih, iw), dtype=bool)
    )
    out: dict[str, tuple[float, float]] = {}

    for colour in HSV_RANGES:
        colour_mask = filter_mask_to_primary_blob(
            quad & frame_colour_mask(bgr, colour),
        )
        n = int(colour_mask.sum())
        if n < MIN_COLOUR_PIXELS or n / total * 100.0 < MIN_COLOUR_PCT:
            continue

        # Apply depth gate if available (removes same-colour pixels from
        # adjacent layers sitting at different depths).
        active = colour_mask & endon_side
        if gate is not None:
            gated = active & gate
            if int(gated.sum()) >= MIN_COLOUR_PIXELS:
                active = gated

        # Try to find the near-face split line.
        # Prefer the pre-computed combined split_x (from both cells) when
        # available — this ensures the front block's split is always found
        # even when its nearest pixels fall in the opposite cell.
        if depth is not None:
            if override_split_x is not None:
                split_x = override_split_x.get(colour)
            else:
                split_x = _split_x_from_closest_pixels(depth, active)
            if split_x is not None:
                if orientation == "left":
                    # Left-facing: near face is at LOW x (outside = left of split)
                    face_mask = active & (x_grid <= float(split_x))
                else:
                    # Right-facing: near face is at HIGH x (outside = right of split)
                    face_mask = active & (x_grid >= float(split_x))

                ys, xs = np.where(face_mask)
                if len(xs) >= max(10, MIN_COLOUR_PIXELS // 5):
                    fn = np.median if use_med else np.mean
                    cx = float(fn(xs))
                    if centre_seam_x is not None:
                        cx = _finalize_centroid_x(
                            cx,
                            centre_seam_x=centre_seam_x,
                            orientation=orientation,
                            split_x=float(split_x),
                        )
                    else:
                        cx = _enforce_centroid_face_side(
                            cx, float(split_x), orientation,
                        )
                    out[colour] = (cx, float(fn(ys)))
                    continue   # Successfully used split-based centroid.

        # No split found (or no depth).
        if require_split:
            continue   # Caller wants split-only — skip this colour.

        # Fallback: plain mean/median of depth-gated pixels.
        ys, xs = np.where(active)
        if len(xs) == 0:
            continue
        fn = np.median if use_med else np.mean
        cx = float(fn(xs))
        if centre_seam_x is not None:
            cx = _finalize_centroid_x(
                cx, centre_seam_x=centre_seam_x, orientation=orientation,
            )
        out[colour] = (cx, float(fn(ys)))

    return out


def _search_colour_near_hint(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    endon_cell: dict,
    opposite_cell: dict,
    colour: str,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
    orientation: str,
    robust_stat: str,
    hint_x: float,
    hint_y: float,
    radius_px: float,
    centre_seam_x: float,
) -> tuple[float, float] | None:
    """Search for a colour centroid within radius_px of a prior (x, y) location."""
    MIN_PIX = max(8, MIN_COLOUR_PIXELS // 4)
    radius_sq = float(radius_px) ** 2

    ih, iw = bgr.shape[:2]
    colour_hsv = frame_colour_mask(bgr, colour)
    endon_quad = _quad_mask((ih, iw), endon_cell["corners"])
    endon_mask = endon_quad & colour_hsv

    gate_e = _depth_gate(depth, endon_target_mm, tolerance_mm=120.0) if depth is not None else None
    if gate_e is not None:
        gated = endon_mask & gate_e
        if int(gated.sum()) >= MIN_PIX:
            endon_mask = gated

    x_grid = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    endon_side = _endon_side_x_mask(x_grid, centre_seam_x, orientation)
    combined = filter_mask_to_primary_blob(
        endon_mask & endon_side,
        prefer_xy=(float(hint_x), float(hint_y)),
    )

    ys, xs = np.where(combined)
    if len(xs) < MIN_PIX:
        return None

    dist_sq = (xs.astype(np.float32) - float(hint_x)) ** 2 + (
        ys.astype(np.float32) - float(hint_y)
    ) ** 2
    local = dist_sq <= radius_sq
    if int(local.sum()) < MIN_PIX:
        return None

    lx = xs[local]
    ly = ys[local]
    fn = np.median if str(robust_stat).strip().lower() == "median" else np.mean
    cx = _finalize_centroid_x(
        float(fn(lx)), centre_seam_x=centre_seam_x, orientation=orientation,
    )
    return cx, float(fn(ly))


def _search_required_colour(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    endon_cell: dict,
    opposite_cell: dict,
    colour: str,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
    orientation: str,
    robust_stat: str,
    centroid_hints: dict[str, tuple[float, float]] | None = None,
    radius_px: float = CENTROID_HINT_SEARCH_RADIUS_PX,
    centre_seam_x: float | None = None,
) -> tuple[float, float] | None:
    """Try last-known location first, then fall back to full-cell search."""
    if centre_seam_x is None:
        return None
    hint = centroid_hints.get(colour) if centroid_hints else None
    if hint is not None:
        near = _search_colour_near_hint(
            bgr, depth, endon_cell, opposite_cell, colour,
            endon_target_mm, opposite_target_mm,
            orientation, robust_stat,
            hint_x=float(hint[0]),
            hint_y=float(hint[1]),
            radius_px=float(radius_px),
            centre_seam_x=float(centre_seam_x),
        )
        if near is not None:
            return near
    return _search_colour_low_threshold(
        bgr, depth, endon_cell, opposite_cell, colour,
        endon_target_mm, opposite_target_mm,
        orientation, robust_stat,
        prefer_xy=hint,
        centre_seam_x=float(centre_seam_x),
    )


def recover_colour_centroid(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    left_cell: dict,
    right_cell: dict,
    orientation: str,
    colour: str,
    hint_xy: tuple[float, float] | None = None,
    radius_px: float = CENTROID_HINT_SEARCH_RADIUS_PX,
    robust_stat: str = "mean",
    hint_only: bool = False,
) -> tuple[float, float] | None:
    """
    Recover a block centroid near hint_xy.

    When hint_only is True, search only within radius_px of the hint on the
    same layer — no full-cell fallback.
    """
    endon_cell = left_cell if orientation == "left" else right_cell
    opposite_cell = right_cell if orientation == "left" else left_cell
    endon_target_mm = _median_depth_in_cell(bgr, depth, endon_cell)
    opposite_target_mm = _median_depth_in_cell(bgr, depth, opposite_cell)
    centre_seam_x = _centre_seam_x(left_cell)
    if hint_xy is not None:
        near = _search_colour_near_hint(
            bgr, depth, endon_cell, opposite_cell, colour,
            endon_target_mm, opposite_target_mm,
            orientation, robust_stat,
            hint_x=float(hint_xy[0]),
            hint_y=float(hint_xy[1]),
            radius_px=float(radius_px),
            centre_seam_x=centre_seam_x,
        )
        if near is not None:
            return near
    if hint_only:
        return None
    hints = {colour: hint_xy} if hint_xy is not None else None
    return _search_required_colour(
        bgr, depth, endon_cell, opposite_cell, colour,
        endon_target_mm, opposite_target_mm,
        orientation, robust_stat,
        centroid_hints=hints,
        radius_px=radius_px,
        centre_seam_x=centre_seam_x,
    )


def _search_colour_low_threshold(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    endon_cell: dict,
    opposite_cell: dict,
    colour: str,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
    orientation: str,
    robust_stat: str,
    prefer_xy: tuple[float, float] | None = None,
    centre_seam_x: float | None = None,
) -> tuple[float, float] | None:
    """
    Low-threshold centroid search for a colour that was not found by the
    normal pipeline.  Used for canonical (known) block colours that may
    have low pixel coverage because the block has been pushed far in depth.

    Differences from the normal path:
      - No MIN_COLOUR_PCT area check — just raw pixel count >= MIN_COLOUR_PIXELS/2.
      - Wide depth gate (120 mm) so pushed blocks are not excluded.
      - Face-side enforcement applied on all return paths.
    """
    MIN_PIX = max(10, MIN_COLOUR_PIXELS // 2)

    ih, iw = bgr.shape[:2]
    colour_hsv = frame_colour_mask(bgr, colour)

    endon_quad = _quad_mask((ih, iw), endon_cell["corners"])
    endon_mask = endon_quad & colour_hsv

    gate_e = _depth_gate(depth, endon_target_mm, tolerance_mm=120.0) if depth is not None else None
    if gate_e is not None:
        g = endon_mask & gate_e
        if int(g.sum()) >= MIN_PIX:
            endon_mask = g

    x_grid = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    if centre_seam_x is not None:
        endon_mask = endon_mask & _endon_side_x_mask(
            x_grid, centre_seam_x, orientation,
        )

    combined = filter_mask_to_primary_blob(endon_mask, prefer_xy=prefer_xy)
    if int(combined.sum()) < MIN_PIX:
        return None

    fn = np.median if str(robust_stat).strip().lower() == "median" else np.mean

    split_x: float | None = None
    if depth is not None and centre_seam_x is not None:
        info = _combined_split_info_per_colour(
            bgr, depth, endon_cell, opposite_cell,
            endon_target_mm, opposite_target_mm,
        )
        entry = info.get(colour)
        if entry is not None:
            split_x = entry[0]

    if split_x is not None and centre_seam_x is not None:
        centroid = _compute_combined_centroid(
            bgr, depth, endon_cell, opposite_cell, colour,
            endon_target_mm, opposite_target_mm,
            split_x, orientation, robust_stat, centre_seam_x,
        )
        if centroid is not None:
            return centroid

    ys, xs = np.where(combined)
    if len(xs) == 0:
        return None
    cx = float(fn(xs))
    cy = float(fn(ys))
    if centre_seam_x is not None:
        cx = _finalize_centroid_x(
            cx,
            centre_seam_x=centre_seam_x,
            orientation=orientation,
            split_x=split_x,
        )
    elif split_x is not None:
        cx = _enforce_centroid_face_side(cx, split_x, orientation)
    return cx, cy


def compute_layer_blob_centroids(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    left_cell: dict,
    right_cell: dict,
    orientation: str,
    robust_stat: str = "mean",
) -> list[dict]:
    """
    Find every disconnected colour blob on the end-on face of one layer.

    Unlike compute_layer_centroids (one centroid per colour), this keeps
    separate connected components so front and back blocks of the same colour
    are both returned when their masks do not touch.
    """
    endon_cell = left_cell if orientation == "left" else right_cell
    centre_seam_x = _centre_seam_x(left_cell)
    endon_target_mm = _median_depth_in_cell(bgr, depth, endon_cell)
    gate = _depth_gate(depth, endon_target_mm) if depth is not None else None

    ih, iw = bgr.shape[:2]
    quad = _quad_mask((ih, iw), endon_cell["corners"])
    if int(quad.sum()) == 0:
        return []

    x_grid = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    endon_side = _endon_side_x_mask(x_grid, centre_seam_x, orientation)
    use_med = str(robust_stat).strip().lower() == "median"
    fn = np.median if use_med else np.mean
    min_area = int(BLOCK_CENTROID_MIN_BLOB_PX)
    min_pixels = max(10, MIN_COLOUR_PIXELS // 2)
    blobs: list[dict] = []

    for colour in HSV_RANGES:
        colour_mask = quad & frame_colour_mask(bgr, colour)
        for area, comp in _components_ge_min_area(colour_mask, min_area):
            active = comp & endon_side
            if gate is not None:
                gated = active & gate
                if int(gated.sum()) >= min_pixels:
                    active = gated
            pixel_count = int(active.sum())
            if pixel_count < min_pixels:
                continue
            ys, xs = np.where(active)
            cx = _finalize_centroid_x(
                float(fn(xs)),
                centre_seam_x=centre_seam_x,
                orientation=orientation,
            )
            blobs.append({
                "colour": colour,
                "mean_x_px": cx,
                "mean_y_px": float(fn(ys)),
                "area": pixel_count,
            })

    return blobs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_layer_centroids(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    left_cell: dict,
    right_cell: dict,
    orientation: str,
    robust_stat: str = "mean",
    require_split: bool = False,
    required_colours: set[str] | None = None,
    split_x_out: dict[str, float] | None = None,
    centroid_hints: dict[str, tuple[float, float]] | None = None,
) -> dict[str, tuple[float, float]]:
    """
    Compute near-face centroid (x_px, y_px) per colour for one layer.

    Searches BOTH cells and merges results:
      - End-on cell result takes priority for every colour.
      - Opposite cell result is used for any colour missing from end-on.
        (This handles the front block whose split may fall in the side-on cell.)

    Parameters
    ----------
    bgr              : full-resolution BGR colour frame
    depth            : aligned depth frame (uint16 mm or None)
    left_cell        : left lane cell definition dict (corners key)
    right_cell       : right lane cell definition dict
    orientation      : "left" (end-on = left cell) or "right" (end-on = right cell)
    robust_stat      : "mean" (normal analysis) or "median" (probe monitoring)
    require_split    : True → only return centroids found via a depth split line
                       False → fall back to depth-gated mean when no split
    required_colours : set of colour names that MUST be returned even at low
                       coverage (canonical/known block colours). When a colour
                       in this set is not found by the normal path, a search
                       near the last-known centroid is tried first, then a
                       wide-gate full-cell fallback.
    centroid_hints   : optional colour → (x_px, y_px) anchors for the
                       required-colour search (typically from identity tracks).

    Returns
    -------
    dict mapping colour name → (x_px, y_px) image-space centroid
    """
    endon_cell        = left_cell  if orientation == "left"  else right_cell
    opposite_cell     = right_cell if orientation == "left"  else left_cell
    centre_seam_x     = _centre_seam_x(left_cell)

    endon_target_mm    = _median_depth_in_cell(bgr, depth, endon_cell)
    opposite_target_mm = _median_depth_in_cell(bgr, depth, opposite_cell)

    if depth is not None:
        # ── Step 1: find winning split_x per colour ────────────────────────
        # Each cell is searched independently; the cell with the shallower
        # (closer) min depth wins.  This lets the split_x track smoothly as
        # the front block is pushed from one side to the other.
        split_x_by_colour = _combined_split_x_per_colour(
            bgr, depth,
            endon_cell, opposite_cell,
            endon_target_mm, opposite_target_mm,
        )
        if split_x_out is not None:
            split_x_out.clear()
            split_x_out.update(split_x_by_colour)

        # ── Step 2: compute centroids from BOTH cells' pixels ──────────────
        # For every colour with a valid split_x, combine pixels from both
        # cells and apply the near-face mask.  This maximises the pixel count
        # for a stable centroid, especially when the front block straddles
        # the cell boundary.
        out: dict[str, tuple[float, float]] = {}
        for colour, split_x in split_x_by_colour.items():
            centroid = _compute_combined_centroid(
                bgr, depth,
                endon_cell, opposite_cell, colour,
                endon_target_mm, opposite_target_mm,
                split_x, orientation, robust_stat, centre_seam_x,
            )
            if centroid is not None:
                out[colour] = centroid

        if require_split:
            # Probe mode: only return centroids found via a depth split line.
            # Still check required colours with the low-threshold path so
            # canonical blocks pushed far aren't silently dropped.
            if required_colours:
                for colour in required_colours:
                    if colour in out:
                        continue
                    fallback = _search_required_colour(
                        bgr, depth,
                        endon_cell, opposite_cell, colour,
                        endon_target_mm, opposite_target_mm,
                        orientation, robust_stat,
                        centroid_hints=centroid_hints,
                        centre_seam_x=centre_seam_x,
                    )
                    if fallback is not None:
                        out[colour] = fallback
            return out

        # ── Step 3 (normal mode): depth-gated mean fallback ────────────────
        # For any colour where the split path yielded nothing, fall back to a
        # plain per-cell depth-gated mean.  Pass an empty override dict so
        # _centroids_in_one_cell always takes the fallback branch.
        _no_split: dict[str, float] = {}
        endon_fallback = _centroids_in_one_cell(
            bgr, depth, endon_cell, orientation,
            endon_target_mm, robust_stat, require_split=False,
            override_split_x=_no_split,
            centre_seam_x=centre_seam_x,
        )
        merged: dict[str, tuple[float, float]] = dict(endon_fallback)
        merged.update(out)

        # ── Required-colours fallback ──────────────────────────────────────
        # For canonical blocks not found by any path above (very low coverage
        # due to the block being pushed far), do a last-resort wide-gate search.
        if required_colours:
            for colour in required_colours:
                if colour in merged:
                    continue
                fallback = _search_required_colour(
                    bgr, depth,
                    endon_cell, opposite_cell, colour,
                    endon_target_mm, opposite_target_mm,
                    orientation, robust_stat,
                    centroid_hints=centroid_hints,
                    centre_seam_x=centre_seam_x,
                )
                if fallback is not None:
                    merged[colour] = fallback

        return merged

    if split_x_out is not None:
        split_x_out.clear()

    # ── No depth available: plain per-cell colour means ────────────────────
    endon_centroids = _centroids_in_one_cell(
        bgr, None, endon_cell, orientation, None,
        robust_stat, require_split=False,
        centre_seam_x=centre_seam_x,
    )
    merged = dict(endon_centroids)

    # ── Required-colours fallback (canonical blocks not found by normal path) ─
    # Run last regardless of depth availability so canonical blocks are always
    # returned with a centroid even when coverage is low (block pushed far).
    if required_colours:
        for colour in required_colours:
            if colour in merged:
                continue
            fallback = _search_required_colour(
                bgr, depth,
                endon_cell, opposite_cell, colour,
                endon_target_mm, opposite_target_mm,
                orientation, robust_stat,
                centroid_hints=centroid_hints,
                centre_seam_x=centre_seam_x,
            )
            if fallback is not None:
                merged[colour] = fallback

    return merged


def compute_split_x_per_colour(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    left_cell: dict,
    right_cell: dict,
    orientation: str,
) -> dict[str, float]:
    """
    Return the depth split line x (pixels) per colour for visualisation.

    Delegates to _combined_split_x_per_colour so the drawn split line always
    matches the split_x used by compute_layer_centroids — both now pick the
    cell with the closer (shallower) minimum depth rather than combining masks.
    """
    if depth is None:
        return {}

    endon_cell    = left_cell  if orientation == "left"  else right_cell
    opposite_cell = right_cell if orientation == "left"  else left_cell

    endon_target_mm    = _median_depth_in_cell(bgr, depth, endon_cell)
    opposite_target_mm = _median_depth_in_cell(bgr, depth, opposite_cell)

    return _combined_split_x_per_colour(
        bgr, depth,
        endon_cell, opposite_cell,
        endon_target_mm, opposite_target_mm,
    )


def compute_split_depth_mm_per_colour(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    left_cell: dict,
    right_cell: dict,
    orientation: str,
) -> dict[str, float]:
    """
    Return the minimum (closest) depth in mm used for each colour split line.
    """
    if depth is None:
        return {}

    endon_cell = left_cell if orientation == "left" else right_cell
    opposite_cell = right_cell if orientation == "left" else left_cell

    endon_target_mm = _median_depth_in_cell(bgr, depth, endon_cell)
    opposite_target_mm = _median_depth_in_cell(bgr, depth, opposite_cell)

    info = _combined_split_info_per_colour(
        bgr,
        depth,
        endon_cell,
        opposite_cell,
        endon_target_mm,
        opposite_target_mm,
    )
    return {colour: values[1] for colour, values in info.items()}