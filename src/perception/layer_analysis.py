"""
layer_analysis.py
-----------------
Analyses the Jenga tower structure layer by layer using absolute lane-based detection.
"""
from __future__ import annotations

import time
import cv2
import numpy as np

from box_percentages import (
    compute_percentages,
)
from block_centroids import (
    compute_layer_centroids,
    compute_split_x_per_colour,
)
from block_pose_global import build_block_pose_mm
from perception_config import (
    COLOUR_BGR,
    CAMERA_HFOV_DEG,
    BLOCK_POSE_WORLD_FRAME,
)

CENTROID_OFFSET_MM = 26.52   # Distance from visible block face to block centroid (mm).
DEPTH_STEP_MM      = 17.68   # Depth step between neighbouring block centroids (mm).

SINGLE_DOMINANT_PCT   = 55.0   # One colour dominates → side-on face.
BLOCK_PRESENT_MIN_PCT = 15.0   # Minimum % for a block to be considered present.

PRINT_INTERVAL_S = 3.0
_last_print_time: float = 0.0
DEPTH_PATCH_RADIUS_PX = 2  # 5x5 local depth sampling window.


# ---------------------------------------------------------------------------
# Orientation detection
# ---------------------------------------------------------------------------

def _colour_pcts(cell_result: dict) -> dict[str, float]:
    return {
        c: info["pct"]
        for c, info in cell_result["colours"].items()
        if c != "none" and info["pct"] > 0
    }


def _dominant_colour(pcts: dict[str, float]) -> tuple[str, float] | None:
    if not pcts:
        return None
    c = max(pcts, key=lambda k: pcts[k])
    return c, pcts[c]


def _detect_orientation(left_pcts: dict[str, float], right_pcts: dict[str, float]) -> str:
    """
    Determine which side shows the end-on face.

    A single dominant colour (≥ SINGLE_DOMINANT_PCT) on one side indicates the
    side-on face is there, so the other side is end-on.  When both sides are
    ambiguous the side with the lower dominant percentage is taken as end-on.
    """
    left_dom  = _dominant_colour(left_pcts)
    right_dom = _dominant_colour(right_pcts)
    left_is_dominant  = left_dom  is not None and left_dom[1]  >= SINGLE_DOMINANT_PCT
    right_is_dominant = right_dom is not None and right_dom[1] >= SINGLE_DOMINANT_PCT

    if right_is_dominant and not left_is_dominant:
        return "left"
    if left_is_dominant and not right_is_dominant:
        return "right"

    left_max  = left_dom[1]  if left_dom  else 0
    right_max = right_dom[1] if right_dom else 0
    return "left" if left_max <= right_max else "right"


# ---------------------------------------------------------------------------
# Block detection from end-on face
# ---------------------------------------------------------------------------

def _blocks_from_endon(
    pcts: dict[str, float],
    mean_xy: dict[str, tuple[float, float]],
    cell: dict,
    orientation: str = "left",
    known_colours: list[str | None] | None = None,
) -> list[dict]:
    """
    One centroid per colour across the full end-on layer side (all pixels of
    that colour in the cell). Assign each colour to a front/mid/back lane by
    its mean x, then reorder lanes for tower orientation.

    known_colours
    -------------
    When provided (a list of three colour names in slot_idx order, i.e.
    [front, mid, back]), the x-lane assignment is SKIPPED.  Instead each
    slot is filled directly from the canonical colour.  This prevents identity
    flips when a pushed block's colour coverage temporarily drops below the
    detection threshold — we know which colour belongs in each slot.

    A half-height percentage threshold is used so blocks with reduced coverage
    (pushed far in depth) are still marked as present.
    """
    if known_colours is not None and any(c is not None for c in known_colours):
        LOW_PCT = BLOCK_PRESENT_MIN_PCT / 2.0
        res: list[dict] = []
        for slot_colour in known_colours:
            if slot_colour is None or slot_colour in ("unknown", ""):
                res.append({"colour": "unknown", "present": False, "depth_mm": None})
                continue
            xy  = mean_xy.get(slot_colour)
            pct = pcts.get(slot_colour, 0.0)
            if xy is not None and pct >= LOW_PCT:
                res.append({
                    "colour":    slot_colour,
                    "present":   True,
                    "mean_x_px": xy[0],
                    "mean_y_px": xy[1],
                })
            else:
                # Block not visible enough this frame: mark absent but keep
                # canonical colour so downstream can still name the slot.
                res.append({"colour": slot_colour, "present": False, "depth_mm": None})
        # known_colours is already in [front, mid, back] = slot_idx order.
        # No orientation reversal needed — canonical is orientation-agnostic.
        return res

    # ── Original x-lane detection (first frame / no canonical yet) ────────
    corners = cell["corners"]
    x_left_bound  = (corners[0][0] + corners[2][0]) / 2.0
    x_right_bound = (corners[1][0] + corners[3][0]) / 2.0
    lane_w = (x_right_bound - x_left_bound) / 3.0

    res = [{"colour": "unknown", "present": False, "depth_mm": None} for _ in range(3)]

    for colour, (mx, my) in mean_xy.items():
        pct = pcts.get(colour, 0.0)
        if pct < BLOCK_PRESENT_MIN_PCT:
            continue

        lane = max(0, min(2, int((mx - x_left_bound) // lane_w)))
        existing_pct = pcts.get(res[lane]["colour"], 0.0) if res[lane]["present"] else 0.0
        if not res[lane]["present"] or pct > existing_pct:
            res[lane] = {
                "colour":    colour,
                "present":   True,
                "mean_x_px": mx,
                "mean_y_px": my,
            }

    if orientation == "left":
        res = res[::-1]

    return res


# ---------------------------------------------------------------------------
# Single-layer analysis
# ---------------------------------------------------------------------------

def analyse_layer(
    bgr_frame: np.ndarray,
    depth_frame: np.ndarray,
    left_result:  dict,
    right_result: dict,
    left_cell:    dict,
    right_cell:   dict,
    frame_centre_x_px: float | None = None,
    frame_width_px: float | None = None,
    known_block_colours: list[str | None] | None = None,
) -> dict:
    left_pcts   = _colour_pcts(left_result)
    right_pcts  = _colour_pcts(right_result)
    orientation = _detect_orientation(left_pcts, right_pcts)

    endon_pcts, endon_cell = (
        (left_pcts, left_cell) if orientation == "left"
        else (right_pcts, right_cell)
    )

    # Build the required_colours set so compute_layer_centroids always
    # searches for canonical block colours even at low pixel coverage.
    required_colours: set[str] | None = None
    if known_block_colours is not None:
        rc = {c for c in known_block_colours if c not in (None, "unknown", "")}
        if rc:
            required_colours = rc

    # Compute near-face centroids for all colours in this layer.
    # Searches both cells so the front block's split (which may fall in the
    # opposite/side-on cell) is always found. Falls back to depth-gated mean
    # when no split is available (e.g. depth stream absent).
    mean_xy = compute_layer_centroids(
        bgr_frame,
        depth_frame,
        left_cell,
        right_cell,
        orientation,
        robust_stat="mean",
        require_split=False,
        required_colours=required_colours,
    )
    endon_blocks = _blocks_from_endon(
        endon_pcts, mean_xy, endon_cell,
        orientation=orientation,
        known_colours=known_block_colours,
    )

    frame_width    = float(frame_width_px) if frame_width_px is not None else float(bgr_frame.shape[1])
    frame_centre_x = float(frame_centre_x_px) if frame_centre_x_px is not None else (frame_width / 2.0)
    tan_half_hfov  = np.tan(np.deg2rad(CAMERA_HFOV_DEG) / 2.0)

    for block in endon_blocks:
        if block["present"] and "mean_x_px" in block:
            # Image x increases to the right; camera +Y is defined as left.
            lateral_px = frame_centre_x - block["mean_x_px"]
            mx = block.get("mean_x_px")
            my = block.get("mean_y_px")
            if mx is not None and my is not None:
                centroid_face = _centroid_face_depth_mm(depth_frame, mx, my)
                if centroid_face is not None and centroid_face > 0:
                    block["centroid_face_depth_mm"] = round(centroid_face, 1)
                    block["centroid_depth_mm"] = round(centroid_face + CENTROID_OFFSET_MM, 1)
                    block["face_depth_mm"] = round(centroid_face, 1)
                    block["depth_mm"] = round(centroid_face + CENTROID_OFFSET_MM, 1)
                    mm_per_px = 2.0 * centroid_face * tan_half_hfov / frame_width
                    block["lateral_px"] = float(lateral_px)
                    block["mm_per_px"] = float(mm_per_px)
                    block["lateral_mm"] = lateral_px * mm_per_px

    return {
        "orientation": orientation,
        "blocks": endon_blocks,
        "frame_centre_x": frame_centre_x,
        "frame_width_px": frame_width,
    }


# ---------------------------------------------------------------------------
# Full tower analysis
# ---------------------------------------------------------------------------

def _centroid_face_depth_mm(
    depth_frame: np.ndarray,
    mean_x_px: float,
    mean_y_px: float,
    window_radius_px: int = DEPTH_PATCH_RADIUS_PX,
) -> float | None:
    """
    Estimate face depth at the detected block centroid from a local depth patch.
    """
    h, w = depth_frame.shape[:2]
    cx = int(round(mean_x_px))
    cy = int(round(mean_y_px))
    if cx < 0 or cy < 0 or cx >= w or cy >= h:
        return None

    x0 = max(0, cx - window_radius_px)
    x1 = min(w, cx + window_radius_px + 1)
    y0 = max(0, cy - window_radius_px)
    y1 = min(h, cy + window_radius_px + 1)
    patch = depth_frame[y0:y1, x0:x1].astype(np.float32)
    valid = patch[(patch > 0) & np.isfinite(patch)]
    if valid.size == 0:
        return None
    return float(np.median(valid))


def _format_global_pose_xyz(block: dict) -> str:
    """Format global-frame position (mm) from pose_global_mm (same frame as JengaBlockState)."""
    pose = block.get("pose_global_mm")
    if not pose:
        return ""
    pos = pose.get("position", {})
    try:
        x_mm = float(pos["x"])
        y_mm = float(pos["y"])
        z_mm = float(pos["z"])
    except (KeyError, TypeError, ValueError):
        return ""
    return f" @x={x_mm:+.1f}mm @y={y_mm:+.1f}mm @z={z_mm:+.1f}mm"


def _block_abs_global_y(block: dict) -> float:
    """Sort key: smaller absolute global Y means closer to y=0."""
    pose = block.get("pose_global_mm")
    if not pose:
        return float("inf")
    pos = pose.get("position", {})
    try:
        return abs(float(pos["y"]))
    except (KeyError, TypeError, ValueError):
        return float("inf")


def _print_tower(tower: list[dict]) -> None:
    print(
        f"── Layer Analysis (L0 = bottom, blocks: front → mid → back, "
        f"{BLOCK_POSE_WORLD_FRAME} x/y/z mm) ────"
    )
    for layer in sorted(tower, key=lambda item: item["layer"]):
        idx         = layer["layer"]
        orientation = layer["orientation"]
        arrow       = "<-" if orientation == "left" else "->"
        labels      = ["front", " mid ", " back"]
        parts = []

        for label, block in zip(labels, layer["blocks"]):
            if block["present"]:
                xyz_str = _format_global_pose_xyz(block)
                parts.append(f"{label}: {block['colour']}{xyz_str}")
            else:
                parts.append(f"{label}: missing")

        print(f"  L{idx} {arrow}  " + "  |  ".join(parts))
    print()


def print_tower_state(tower: list[dict]) -> None:
    """Print an already-computed tower state without recomputing analysis."""
    if not tower:
        return
    _print_tower(tower)


def analyse_tower(
    bgr_frame: np.ndarray,
    depth_frame: np.ndarray,
    row_cells: list[tuple[dict, dict]],
    frame_centre_x_px: float | None = None,
    frame_width_px: float | None = None,
    print_enabled: bool = True,
    min_centroid_layer: int | None = None,
    identity_tracker=None,
) -> list[dict]:
    """
    Analyse the full tower layer by layer.

    identity_tracker : BlockIdentityTracker | None
        When provided and already initialized, the canonical colour-per-slot
        is queried for each layer and passed down so _blocks_from_endon can
        look for the KNOWN colour in each slot rather than re-detecting from
        x-lane positions.  This prevents identity flips when a pushed block's
        colour coverage drops temporarily.
    """
    global _last_print_time
    tower = []
    n_layers = len(row_cells)
    for row_idx, (left_def, right_def) in enumerate(row_cells):
        pct_results = compute_percentages(bgr_frame, cells=[left_def, right_def])
        # layer index: row_cells[0] is topmost in image → highest layer index
        layer_idx = (n_layers - 1) - row_idx

        # When monitoring a probe, skip all centroid/depth work for layers
        # below the target layer — they cannot move during a probe so there
        # is no need to recompute them, saving significant CPU per frame.
        skip_centroid = (
            min_centroid_layer is not None
            and layer_idx < int(min_centroid_layer)
        )

        # Fetch canonical colour assignments for this layer when available.
        # On the first frame (tracker not yet initialized) this returns all
        # None and _blocks_from_endon falls back to x-lane detection.
        known_colours: list[str | None] | None = None
        if identity_tracker is not None and identity_tracker.is_initialized():
            known_colours = identity_tracker.canonical_colours_for_layer(layer_idx)
            # If all None (e.g. layer not yet seen), fall back to free detection.
            if not any(c is not None for c in known_colours):
                known_colours = None

        layer = analyse_layer(
            bgr_frame,
            depth_frame if not skip_centroid else None,
            pct_results[0],
            pct_results[1],
            left_def,
            right_def,
            frame_centre_x_px=frame_centre_x_px,
            frame_width_px=frame_width_px,
            known_block_colours=known_colours,
        )
        layer["layer"] = layer_idx
        tower.append(layer)

    # L0 = bottom; block IDs 000–002 at bottom, then 003–005, … (motion-planning block_XX).
    tower.sort(key=lambda item: item["layer"])
    for list_idx, layer in enumerate(tower):
        for pos, block in enumerate(layer["blocks"]):
            if not block.get("present"):
                continue
            depth_mm = block.get("depth_mm")
            lateral_mm = block.get("lateral_mm")
            pose_camera_mm, pose_global_mm = build_block_pose_mm(
                depth_mm=depth_mm,
                lateral_mm=(None if lateral_mm is None else float(lateral_mm)),
                orientation=str(layer["orientation"]),
                layer_idx=int(layer["layer"]),
            )
            if pose_camera_mm is None or pose_global_mm is None:
                continue

            block["pose_camera_mm"] = pose_camera_mm
            block["pose_global_mm"] = pose_global_mm

        # Per-layer indexing rule: lowest index is block closest to y=0.
        sorted_block_positions = sorted(
            range(len(layer["blocks"])),
            key=lambda idx: (_block_abs_global_y(layer["blocks"][idx]), idx),
        )
        for local_rank, pos_idx in enumerate(sorted_block_positions):
            block = layer["blocks"][pos_idx]
            block_index = int(list_idx * 3 + local_rank)
            block["block_index"] = block_index
            block["id"] = f"{block_index:03d}"

    now = time.monotonic()
    if print_enabled and now - _last_print_time >= PRINT_INTERVAL_S:
        _print_tower(tower)
        _last_print_time = now

    return tower


def annotate_depth_split_lines_for_tower(
    bgr_frame: np.ndarray,
    depth_frame: np.ndarray | None,
    row_cells: list[tuple[dict, dict]],
    tower: list[dict],
    min_layer: int | None = None,
) -> list[dict]:
    """
    Add visual-only per-block depth split lines without affecting centroids.

    When min_layer is set, only layers >= min_layer are computed.
    """
    for layer in tower:
        for block in layer.get("blocks", []):
            block.pop("depth_split_x_px", None)

    if depth_frame is None or not tower or not row_cells:
        return tower

    n_layers = len(row_cells)
    for layer in tower:
        layer_idx = int(layer.get("layer", -1))
        if min_layer is not None and layer_idx < int(min_layer):
            continue

        orientation = str(layer.get("orientation", ""))
        if orientation not in ("left", "right"):
            continue

        row_idx = (n_layers - 1) - layer_idx
        if row_idx < 0 or row_idx >= n_layers:
            continue

        left_cell, right_cell = row_cells[row_idx]
        # Search BOTH cells so the front block's split line is always found
        # (its near face may be visible from the opposite/side-on cell).
        split_x_by_colour = compute_split_x_per_colour(
            bgr_frame,
            depth_frame,
            left_cell,
            right_cell,
            orientation,
        )
        # Only annotate the NEAREST (front) block per layer.
        # Multiple blocks can have split lines computed, but displaying all of
        # them clutters the overlay.  The front block (smallest face_depth_mm)
        # is the only one whose split line is meaningful for monitoring.
        nearest_block = None
        nearest_depth = float("inf")
        for block in layer.get("blocks", []):
            if not block.get("present"):
                continue
            d = block.get("face_depth_mm") or block.get("depth_mm")
            if d is not None and float(d) < nearest_depth:
                nearest_depth = float(d)
                nearest_block = block

        if nearest_block is not None:
            colour   = str(nearest_block.get("colour", ""))
            split_x  = split_x_by_colour.get(colour)
            if split_x is not None:
                nearest_block["depth_split_x_px"] = float(split_x)

    return tower


# ---------------------------------------------------------------------------
# Tower visualisation
# ---------------------------------------------------------------------------

TOWER_BLOCK_W = 80
TOWER_BLOCK_H = 28
TOWER_BLOCK_GAP = 4
TOWER_MARGIN = 40
TOWER_LABEL_W = 60


def _tower_block_rects(tower: list[dict]) -> list[tuple[int, int, int, int, dict]]:
    """Return image-space rectangles (x0, y0, x1, y1, block) for each tower slot."""
    layer_h = TOWER_BLOCK_H + TOWER_BLOCK_GAP
    n_layers = len(tower)
    rects: list[tuple[int, int, int, int, dict]] = []
    for layer_data in tower:
        layer_idx = int(layer_data["layer"])
        blocks = layer_data["blocks"]
        y0 = TOWER_MARGIN + (n_layers - 1 - layer_idx) * layer_h
        y1 = y0 + TOWER_BLOCK_H
        x_start = TOWER_MARGIN + TOWER_LABEL_W
        for pos, block in enumerate(blocks):
            x0 = x_start + pos * (TOWER_BLOCK_W + TOWER_BLOCK_GAP)
            x1 = x0 + TOWER_BLOCK_W
            rects.append((x0, y0, x1, y1, block))
    return rects


def block_id_from_tower_image_point(tower: list[dict], x: int, y: int) -> int | None:
    """Return block_index for the clicked slot in the Layer Analysis image."""
    for x0, y0, x1, y1, block in _tower_block_rects(tower):
        if x0 <= x <= x1 and y0 <= y <= y1:
            block_id = block.get("block_index")
            if block_id is None:
                return None
            try:
                return int(block_id)
            except (TypeError, ValueError):
                return None
    return None


def build_tower_image(
    tower: list[dict],
    selected_block_id: int | None = None,
    probe_status_text: str | None = None,
) -> np.ndarray:
    block_w, block_h, block_gap = TOWER_BLOCK_W, TOWER_BLOCK_H, TOWER_BLOCK_GAP
    layer_h = block_h + block_gap
    margin, label_w = TOWER_MARGIN, TOWER_LABEL_W
    n_layers, n_blocks = len(tower), 3
    img_w = margin * 2 + label_w + n_blocks * block_w + (n_blocks - 1) * block_gap
    img_h = margin * 2 + n_layers * layer_h
    canvas = np.full((img_h, img_w, 3), 30, dtype=np.uint8)

    if probe_status_text:
        cv2.putText(
            canvas,
            probe_status_text,
            (margin, margin - 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (230, 230, 230),
            1,
            cv2.LINE_AA,
        )

    for layer_data in tower:
        layer_idx   = layer_data["layer"]
        orientation = layer_data["orientation"]
        blocks      = layer_data["blocks"]
        # L0 at bottom of the diagram, highest layer index at top.
        y0 = margin + (n_layers - 1 - layer_idx) * layer_h
        y1 = y0 + block_h
        cv2.putText(canvas, f"L{layer_idx}", (margin, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(canvas, "<-" if orientation == "left" else "->",
                    (margin + label_w - 18, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 80), 1, cv2.LINE_AA)
        x_start = margin + label_w
        for pos, block in enumerate(blocks):
            x0  = x_start + pos * (block_w + block_gap)
            x1  = x0 + block_w
            bgr = COLOUR_BGR.get(block["colour"], (60, 60, 60))
            block_id = block.get("block_index")
            if block["present"]:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), bgr, -1)
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (200, 200, 200), 1)
            else:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
            if block_id is not None:
                cv2.putText(
                    canvas,
                    str(int(block_id)),
                    (x0 + 4, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.34,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
            if selected_block_id is not None and block_id is not None and int(block_id) == int(selected_block_id):
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (0, 255, 255), 2)

    return canvas