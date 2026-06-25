"""
centre_seam.py
--------------
Single home for the "split between the two visible faces" technique — the
closest-to-camera column of a masked region — used in two places:

  * grid generation  — the tower's near vertical corner ("centre seam") that
    anchors the centre column of the detection grid, and
  * centroid analysis — the per-colour near-face split line used by
    block_centroids / box_percentages so a centroid sits on the near face only.

Why this exists
---------------
The tower stands at ~45° to the camera, so every layer shows two faces that
meet at a vertical corner running down the middle of the tower.  That corner is
the line that splits the left and right side of the tower.

On the recoloured colour-classification image this corner is invisible — both
faces of a block classify to the same colour, so there is no colour edge there.
We therefore use a depth cue: the near corner is, by definition, the column
closest to the camera.

Public API
----------
    closest_depth_column(depth, mask, ...) -> (column_x, min_depth_mm)
        The shared primitive. Selects the closest-to-camera pixels of a masked
        region and returns their representative column x (the split/seam) plus
        the region's minimum depth. Reused by block_centroids and box_percentages.

    detect_centre_seam_lines(colour_img, depth_roi, horiz_lines)
        -> list[(x, y_top, x, y_bot)]
        Grid-generation wrapper: for each layer band, take the LARGEST colour
        blob (the front block's near face) and emit one vertical seam segment at
        its closest_depth_column. Solved per layer, so the tower need not be
        perfectly vertical. Feeds the intersection/cluster/cell pipeline.
"""
from __future__ import annotations

import numpy as np

from perception_config import (
    COLOUR_BGR,
    CENTRE_SEAM_CLOSEST_PCT,
    CENTRE_SEAM_MIN_VALID_PX,
    CENTRE_SEAM_MIN_COLOUR_PX,
    CENTRE_SEAM_ROW_MERGE_PX,
    CENTRE_SEAM_MIN_BAND_PX,
)


def closest_depth_column(
    depth: np.ndarray,
    mask: np.ndarray,
    *,
    depth_tol_mm: float = 1.0,
    closest_pct: float | None = None,
    stat: str = "mean",
    min_valid_px: int = 1,
) -> tuple[float | None, float | None]:
    """
    Find the column closest to the camera for a masked region — the shared
    "split between the two visible faces" primitive.

    This is the single technique reused across the pipeline:
      * grid generation  — the tower's centre seam (near vertical corner), and
      * centroid analysis — the near-face split line that separates a block's
        two visible faces so the centroid sits on the near face only.

    The nearest face is, by definition, the closest-to-camera pixels of the
    region.  We select those pixels and return the representative column x.

    Parameters
    ----------
    depth        : depth image (mm); 0 / non-finite treated as invalid.
    mask         : boolean mask of the region (colour blob) to search.
    depth_tol_mm : when closest_pct is None, "near" pixels are those within this
                   many mm of the minimum depth.  (block_centroids uses 1.0;
                   box_percentages used 0.0 i.e. exactly the minimum.)
    closest_pct  : if set, "near" pixels are the closest this-% of valid depths
                   (percentile gate) instead of the depth_tol_mm gate.  Used by
                   the grid seam for a noise-robust estimate.
    stat         : "mean" or "median" of the near pixels' x.
    min_valid_px : minimum valid-depth pixels required before a result is given.

    Returns
    -------
    (column_x, min_depth_mm) — column_x is the chosen seam/split x; min_depth_mm
    is the region's closest depth (callers compare it across cells to decide
    which cell sees the true near face).  Both None when there is no usable
    depth under the mask.
    """
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None, None
    d = depth[ys, xs].astype(np.float32)
    valid = (d > 0) & np.isfinite(d)
    if int(valid.sum()) < max(1, int(min_valid_px)):
        return None, None
    dv = d[valid]
    xv = xs[valid]
    min_d = float(np.min(dv))
    if closest_pct is not None:
        thr = float(np.percentile(dv, float(closest_pct)))
    else:
        thr = min_d + float(depth_tol_mm)
    near = dv <= thr
    if not np.any(near):
        return None, None
    fn = np.median if str(stat).strip().lower() == "median" else np.mean
    return float(fn(xv[near])), min_d


def _cluster_sorted_values(values: list[float], merge_px: float) -> list[float]:
    """Group 1-D values within merge_px of each other; return one mean per group."""
    if not values:
        return []
    svals = sorted(values)
    groups: list[list[float]] = [[svals[0]]]
    for v in svals[1:]:
        if v - groups[-1][-1] <= merge_px:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [float(np.mean(g)) for g in groups]


def _layer_bands_from_horizontals(
    horiz_lines: list[tuple],
    roi_h: int,
    merge_px: float = CENTRE_SEAM_ROW_MERGE_PX,
    min_band_px: int = CENTRE_SEAM_MIN_BAND_PX,
) -> list[tuple[int, int]]:
    """
    Split the ROI height into layer bands using the colour-mask horizontal
    lines as layer boundaries.

    Returns a list of (y_top, y_bot) bands.  Falls back to a single full-height
    band when fewer than two distinct boundaries are found, so a seam is still
    attempted before the grid is established.
    """
    ys = [(float(y1) + float(y2)) / 2.0 for (_x1, y1, _x2, y2) in horiz_lines]
    boundaries = _cluster_sorted_values(ys, merge_px)
    if len(boundaries) < 2:
        return [(0, max(1, int(roi_h) - 1))]

    bands: list[tuple[int, int]] = []
    for i in range(len(boundaries) - 1):
        y_top = int(round(boundaries[i]))
        y_bot = int(round(boundaries[i + 1]))
        if y_bot - y_top >= int(min_band_px):
            bands.append((y_top, y_bot))
    if not bands:
        return [(0, max(1, int(roi_h) - 1))]
    return bands


def _largest_colour_mask_in_band(
    colour_img: np.ndarray,
    y_top: int,
    y_bot: int,
    min_colour_px: int = CENTRE_SEAM_MIN_COLOUR_PX,
) -> np.ndarray | None:
    """
    Boolean mask (full ROI shape) of the largest single colour blob inside the
    band [y_top, y_bot).  Colours are read straight from the recoloured image
    (each colour is painted its unique COLOUR_BGR value; black = none).

    Returns None when no colour clears min_colour_px.
    """
    roi_h, roi_w = colour_img.shape[:2]
    y0 = max(0, int(y_top))
    y1 = min(int(roi_h), int(y_bot))
    if y1 - y0 <= 0:
        return None

    band = colour_img[y0:y1, :]
    best_count = 0
    best_band_mask: np.ndarray | None = None
    for colour, bgr in COLOUR_BGR.items():
        if colour == "none":
            continue
        m = np.all(band == np.array(bgr, dtype=np.uint8), axis=2)
        count = int(m.sum())
        if count > best_count:
            best_count = count
            best_band_mask = m

    if best_band_mask is None or best_count < int(min_colour_px):
        return None

    full = np.zeros((roi_h, roi_w), dtype=bool)
    full[y0:y1, :] = best_band_mask
    return full


def _robust_closest_x(
    depth_roi: np.ndarray,
    mask: np.ndarray,
    closest_pct: float = CENTRE_SEAM_CLOSEST_PCT,
    min_valid_px: int = CENTRE_SEAM_MIN_VALID_PX,
) -> float | None:
    """
    Median x of the closest closest_pct% of valid-depth pixels under mask.

    Thin wrapper over closest_depth_column with the grid seam's robust settings;
    returns only the column x (the seam's depth is not needed here).
    """
    seam_x, _ = closest_depth_column(
        depth_roi,
        mask,
        closest_pct=closest_pct,
        stat="median",
        min_valid_px=min_valid_px,
    )
    return seam_x


def detect_centre_seam_lines(
    colour_img: np.ndarray,
    depth_roi: np.ndarray | None,
    horiz_lines: list[tuple],
    *,
    closest_pct: float = CENTRE_SEAM_CLOSEST_PCT,
    min_valid_px: int = CENTRE_SEAM_MIN_VALID_PX,
) -> list[tuple[int, int, int, int]]:
    """
    Per-layer centre-seam vertical segments from depth + the recoloured image.

    Parameters
    ----------
    colour_img  : recoloured colour-classification image (ROI space, BGR).
    depth_roi   : aligned depth (mm) cropped to the same ROI, or None.
    horiz_lines : colour-mask horizontal Hough lines, used to split the ROI
                  into layer bands.

    Returns
    -------
    List of (x, y_top, x, y_bot) vertical segments — one per layer band that
    yielded a confident seam.  Empty when depth is unavailable/mismatched.
    """
    if depth_roi is None:
        return []
    roi_h, roi_w = colour_img.shape[:2]
    if depth_roi.shape[:2] != (roi_h, roi_w):
        return []

    bands = _layer_bands_from_horizontals(horiz_lines, roi_h)
    lines: list[tuple[int, int, int, int]] = []
    for y_top, y_bot in bands:
        mask = _largest_colour_mask_in_band(colour_img, y_top, y_bot)
        if mask is None:
            continue
        seam_x = _robust_closest_x(
            depth_roi, mask, closest_pct=closest_pct, min_valid_px=min_valid_px,
        )
        if seam_x is None:
            continue
        x = int(round(seam_x))
        if 0 <= x < roi_w:
            lines.append((x, int(y_top), x, int(y_bot)))
    return lines
