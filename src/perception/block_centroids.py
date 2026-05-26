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

  compute_split_x_per_colour(bgr, depth, left_cell, right_cell, orientation)
      -> dict[colour_str, x_px]
      Used by annotate_depth_split_lines_for_tower for visualisation only.
"""
from __future__ import annotations

import numpy as np
import cv2

from colour_identification import classify_hsv
from perception_config import HSV_RANGES

# Minimum pixels for a colour blob to be considered valid.
MIN_COLOUR_PIXELS = 50
MIN_COLOUR_PCT    = 10.0   # % of cell area


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

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
    at that depth (within 1 mm tolerance) and return their mean x.  That x
    is the near-face edge — pixels outside this line belong to the near face.

    Returns (split_x, min_depth_mm).  Both are None when no valid pixels exist.
    min_depth_mm is exposed so callers can compare across cells to decide which
    cell is seeing the true near face (see _combined_split_x_per_colour).
    """
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None, None
    depths = depth[ys, xs].astype(np.float32)
    valid  = (depths > 0) & np.isfinite(depths)
    if not np.any(valid):
        return None, None
    dv    = depths[valid]
    xv    = xs[valid]
    min_d = float(np.min(dv))
    # Accept pixels within 1 mm of the minimum (sensor quantisation noise).
    near = dv <= (min_d + 1.0)
    return float(np.mean(xv[near])), min_d


def _split_x_from_closest_pixels(
    depth: np.ndarray,
    mask: np.ndarray,
) -> float | None:
    """Convenience wrapper — returns only split_x (min_depth discarded)."""
    sx, _ = _split_x_and_min_depth(depth, mask)
    return sx


def _combined_split_x_per_colour(
    bgr: np.ndarray,
    depth: np.ndarray,
    endon_cell: dict,
    opposite_cell: dict,
    endon_target_mm: float | None,
    opposite_target_mm: float | None,
) -> dict[str, float]:
    """
    Find split_x per colour by searching each cell independently and picking
    the one whose minimum depth is shallower (closer to the camera).

    WHY: The front block's near face can straddle the cell boundary as it is
    pushed.  The previous approach combined both cell masks before searching,
    which caused the minimum-depth cluster to land at the boundary — the
    split_x would get stuck there.

    By comparing per-cell minimum depths independently, the cell that is
    actually seeing the near face (lower depth) naturally takes over as the
    block moves, so the split_x tracks smoothly from one side to the other.
    """
    ih, iw = bgr.shape[:2]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    endon_quad    = _quad_mask((ih, iw), endon_cell["corners"])
    opposite_quad = _quad_mask((ih, iw), opposite_cell["corners"])
    endon_gate    = _depth_gate(depth, endon_target_mm)
    opposite_gate = _depth_gate(depth, opposite_target_mm)

    result: dict[str, float] = {}
    for colour in HSV_RANGES:
        colour_hsv = classify_hsv(hsv, colour)

        # End-on cell mask with its own depth gate.
        endon_mask = endon_quad & colour_hsv
        if endon_gate is not None:
            gated = endon_mask & endon_gate
            if int(gated.sum()) >= MIN_COLOUR_PIXELS:
                endon_mask = gated

        # Opposite cell mask with its own depth gate.
        opposite_mask = opposite_quad & colour_hsv
        if opposite_gate is not None:
            gated = opposite_mask & opposite_gate
            if int(gated.sum()) >= MIN_COLOUR_PIXELS:
                opposite_mask = gated

        # Search each cell independently.
        sx_endon,    min_d_endon    = _split_x_and_min_depth(depth, endon_mask)
        sx_opposite, min_d_opposite = _split_x_and_min_depth(depth, opposite_mask)

        if sx_endon is None and sx_opposite is None:
            continue
        elif sx_endon is None:
            result[colour] = sx_opposite  # type: ignore[assignment]
        elif sx_opposite is None:
            result[colour] = sx_endon
        else:
            # Both cells see this colour — the cell with the smaller (closer)
            # minimum depth is looking at the near face; use its split_x.
            result[colour] = sx_endon if min_d_endon <= min_d_opposite else sx_opposite

    return result


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
) -> tuple[float, float] | None:
    """
    Compute the near-face centroid for one colour using pixels from BOTH cells.

    After the winning split_x is known (from whichever cell saw the closer
    depth), this function builds a combined pixel set from both cells, applies
    the near-face mask (orientation determines which side of split_x is the
    near face), and returns the robust centroid of those pixels.

    Using both cells gives more stable pixel counts, especially for the front
    block whose visible near face can straddle the cell boundary.
    """
    ih, iw   = bgr.shape[:2]
    hsv      = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    colour_hsv = classify_hsv(hsv, colour)

    endon_quad    = _quad_mask((ih, iw), endon_cell["corners"])
    opposite_quad = _quad_mask((ih, iw), opposite_cell["corners"])

    endon_mask    = endon_quad & colour_hsv
    opposite_mask = opposite_quad & colour_hsv

    # Depth-gate each cell independently.
    endon_gate = _depth_gate(depth, endon_target_mm)
    if endon_gate is not None:
        gated = endon_mask & endon_gate
        if int(gated.sum()) >= MIN_COLOUR_PIXELS:
            endon_mask = gated

    opposite_gate = _depth_gate(depth, opposite_target_mm)
    if opposite_gate is not None:
        gated = opposite_mask & opposite_gate
        if int(gated.sum()) >= MIN_COLOUR_PIXELS:
            opposite_mask = gated

    endon_n    = int(endon_mask.sum())
    opposite_n = int(opposite_mask.sum())

    if endon_n < MIN_COLOUR_PIXELS and opposite_n < MIN_COLOUR_PIXELS:
        return None

    fn = np.median if str(robust_stat).strip().lower() == "median" else np.mean

    # If the opposite cell has no significant pixels for this colour, the
    # front block's side face isn't contributing — the end-on cell alone
    # gives the near-face centroid directly without any face mask.
    # Applying the face mask here would halve the pixel set and can push the
    # centroid to the wrong side of split_x, so skip it.
    if opposite_n < MIN_COLOUR_PIXELS:
        source = endon_mask if endon_n >= MIN_COLOUR_PIXELS else opposite_mask
        ys, xs = np.where(source)
        return float(fn(xs)), float(fn(ys))

    # Both cells have significant pixels: the front block's side face is
    # visible in the opposite cell and would bias the centroid away from the
    # near-face position.  Apply the face mask to isolate near-face pixels.
    combined = endon_mask | opposite_mask
    x_grid   = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    if orientation == "left":
        face_mask = combined & (x_grid <= float(split_x))
    else:
        face_mask = combined & (x_grid >= float(split_x))

    ys, xs = np.where(face_mask)
    if len(xs) >= max(10, MIN_COLOUR_PIXELS // 5):
        return float(fn(xs)), float(fn(ys))

    # Face mask yielded too few pixels (split_x edge case): fall back to
    # the end-on cell pixels only — they are always the near face.
    ys, xs = np.where(endon_mask)
    if len(xs) == 0:
        return None
    return float(fn(xs)), float(fn(ys))


def _centroids_in_one_cell(
    bgr: np.ndarray,
    depth: np.ndarray | None,
    cell: dict,
    orientation: str,
    target_depth_mm: float | None,
    robust_stat: str,
    require_split: bool,
    override_split_x: dict[str, float] | None = None,
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
    hsv    = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    quad   = _quad_mask((ih, iw), cell["corners"])
    total  = int(quad.sum())
    if total == 0:
        return {}

    gate    = _depth_gate(depth, target_depth_mm) if depth is not None else None
    use_med = str(robust_stat).strip().lower() == "median"
    x_grid  = np.broadcast_to(np.arange(iw, dtype=np.float32), (ih, iw))
    out: dict[str, tuple[float, float]] = {}

    for colour in HSV_RANGES:
        colour_mask = quad & classify_hsv(hsv, colour)
        n = int(colour_mask.sum())
        if n < MIN_COLOUR_PIXELS or n / total * 100.0 < MIN_COLOUR_PCT:
            continue

        # Apply depth gate if available (removes same-colour pixels from
        # adjacent layers sitting at different depths).
        active = colour_mask
        if gate is not None:
            gated = colour_mask & gate
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
                    out[colour] = (float(fn(xs)), float(fn(ys)))
                    continue   # Successfully used split-based centroid.

        # No split found (or no depth).
        if require_split:
            continue   # Caller wants split-only — skip this colour.

        # Fallback: plain mean/median of depth-gated pixels.
        ys, xs = np.where(active)
        if len(xs) == 0:
            continue
        fn = np.median if use_med else np.mean
        out[colour] = (float(fn(xs)), float(fn(ys)))

    return out


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
) -> dict[str, tuple[float, float]]:
    """
    Compute near-face centroid (x_px, y_px) per colour for one layer.

    Searches BOTH cells and merges results:
      - End-on cell result takes priority for every colour.
      - Opposite cell result is used for any colour missing from end-on.
        (This handles the front block whose split may fall in the side-on cell.)

    Parameters
    ----------
    bgr         : full-resolution BGR colour frame
    depth       : aligned depth frame (uint16 mm or None)
    left_cell   : left lane cell definition dict (corners key)
    right_cell  : right lane cell definition dict
    orientation : "left" (end-on = left cell) or "right" (end-on = right cell)
    robust_stat : "mean" (normal analysis) or "median" (probe monitoring)
    require_split : True → only return centroids found via a depth split line
                   False → fall back to depth-gated mean when no split

    Returns
    -------
    dict mapping colour name → (x_px, y_px) image-space centroid
    """
    endon_cell        = left_cell  if orientation == "left"  else right_cell
    opposite_cell     = right_cell if orientation == "left"  else left_cell
    opposite_orient   = "right"    if orientation == "left"  else "left"

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
                split_x, orientation, robust_stat,
            )
            if centroid is not None:
                out[colour] = centroid

        if require_split:
            # Probe mode: only return centroids found via a depth split line.
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
        )
        opposite_fallback = _centroids_in_one_cell(
            bgr, depth, opposite_cell, opposite_orient,
            opposite_target_mm, robust_stat, require_split=False,
            override_split_x=_no_split,
        )
        # Priority: split-based (both-cell) > end-on fallback > opposite fallback.
        merged: dict[str, tuple[float, float]] = dict(opposite_fallback)
        merged.update(endon_fallback)
        merged.update(out)
        return merged

    # ── No depth available: plain per-cell colour means ────────────────────
    endon_centroids = _centroids_in_one_cell(
        bgr, None, endon_cell, orientation, None,
        robust_stat, require_split=False,
    )
    opposite_centroids = _centroids_in_one_cell(
        bgr, None, opposite_cell, opposite_orient, None,
        robust_stat, require_split=False,
    )
    merged = dict(opposite_centroids)
    merged.update(endon_centroids)
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
