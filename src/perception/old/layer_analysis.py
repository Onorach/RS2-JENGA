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
    colour_mean_x_in_cell,
    colour_mean_depth_in_cell,
    compute_percentages,
)
from perception_config import COLOUR_BGR, HSV_RANGES, CAMERA_HFOV_DEG

BLOCK_LENGTH_MM = 75.0
CAMERA_ANGLE_DEG = 45.0

# Distance from visible face to centroid
CENTROID_OFFSET_MM = (BLOCK_LENGTH_MM / 2.0) * np.cos(
    np.deg2rad(CAMERA_ANGLE_DEG)
)

# Distance between neighbouring block centroids
BLOCK_WIDTH_MM = 25.0
DEPTH_STEP_MM = BLOCK_WIDTH_MM * np.sin(np.deg2rad(CAMERA_ANGLE_DEG))

SINGLE_DOMINANT_PCT = 55.0
# Increased threshold to 25% for better stability when blocks are removed
BLOCK_PRESENT_MIN_PCT = 25.0
# The rearmost block (lane 2) is partially occluded by the two front blocks,
# so it rarely reaches the normal threshold. Accept it at a lower value.
BACK_LANE_MIN_PCT = 10.0

# How often (seconds) to print the layer summary to stdout
PRINT_INTERVAL_S = 3.0
_last_print_time: float = 0.0


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
    left_dom = _dominant_colour(left_pcts)
    right_dom = _dominant_colour(right_pcts)
    left_is_dominant = left_dom is not None and left_dom[1] >= SINGLE_DOMINANT_PCT
    right_is_dominant = right_dom is not None and right_dom[1] >= SINGLE_DOMINANT_PCT

    if right_is_dominant and not left_is_dominant:
        return "left"
    if left_is_dominant and not right_is_dominant:
        return "right"

    left_max = left_dom[1] if left_dom else 0
    right_max = right_dom[1] if right_dom else 0
    return "left" if left_max <= right_max else "right"

def _blocks_from_endon(
    pcts: dict[str, float],
    mean_x: dict[str, float],
    mean_depth: dict[str, float],
    cell: dict,
    orientation: str = "left",
) -> list[dict]:

    corners = cell["corners"]

    x_left_bound  = (corners[0][0] + corners[2][0]) / 2.0
    x_right_bound = (corners[1][0] + corners[3][0]) / 2.0

    cell_w = x_right_bound - x_left_bound
    lane_w = cell_w / 3.0

    back_lane = 0 if orientation == "left" else 2

    res = [
        {
            "colour": "unknown",
            "present": False,
            "depth_mm": None,
        }
        for _ in range(3)
    ]

    for colour, mx in mean_x.items():

        pct = pcts.get(colour, 0.0)

        relative_x = mx - x_left_bound
        raw_lane = int(relative_x // lane_w)

        lane = max(0, min(2, raw_lane))

        threshold = (
            BACK_LANE_MIN_PCT
            if lane == back_lane
            else BLOCK_PRESENT_MIN_PCT
        )

        if pct < threshold:
            continue

        face_depth = mean_depth.get(colour)

        if face_depth is None:
            continue

        existing_pct = (
            pcts.get(res[lane]["colour"], 0.0)
            if res[lane]["present"]
            else 0.0
        )

        if (not res[lane]["present"]) or (pct > existing_pct):

            res[lane] = {
                "colour": colour,
                "present": True,
                "face_depth_mm": round(face_depth, 1),
                "mean_x_px": mx,
            }

    # Convert lane ordering to front->back ordering
    if orientation == "left":
        res = res[::-1]

    # Convert visible face depth to centroid depth
    for i, block in enumerate(res):

        if not block["present"]:
            continue

        block["depth_mm"] = round(block["face_depth_mm"] + CENTROID_OFFSET_MM, 1)

    return res

def _blocks_from_sideon(pcts: dict[str, float]) -> list[dict]:
    """Side-on usually sees one block; return the most dominant colors."""
    present = sorted(
        [(c, p) for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT],
        key=lambda x: -x[1],
    )
    blocks = [{"colour": c, "present": True, "pixel_u": None} for c, _ in present]
    while len(blocks) < 3:
        blocks.append({"colour": "unknown", "present": False, "pixel_u": None})
    return blocks[:3]

def analyse_layer(
    bgr_frame: np.ndarray,
    depth_frame: np.ndarray,
    left_result:  dict,
    right_result: dict,
    left_cell:    dict,
    right_cell:   dict,
) -> dict:
    left_pcts  = _colour_pcts(left_result)
    right_pcts = _colour_pcts(right_result)
    orientation = _detect_orientation(left_pcts, right_pcts)

    if orientation == "left":
        endon_pcts, endon_cell = left_pcts, left_cell
    else:
        endon_pcts, endon_cell = right_pcts, right_cell

    # Compute depth first — used both for block positions and to gate mean_x.
    # Depth gating removes side-face pixels from adjacent layers that share the
    # same colour but sit at a different depth, which otherwise biases mean_x
    # outward (most visible on -> layers as inflated lateral values).
    mean_depth = colour_mean_depth_in_cell(
        bgr_frame,
        depth_frame,
        endon_cell,
    )

    target_depth_mm = (
        float(np.mean(list(mean_depth.values()))) if mean_depth else None
    )

    mean_x = colour_mean_x_in_cell(
        bgr_frame,
        endon_cell,
        depth_frame=depth_frame,
        target_depth_mm=target_depth_mm,
        depth_tolerance_mm=40.0,
    )

    endon_blocks = _blocks_from_endon(
        endon_pcts,
        mean_x,
        mean_depth,
        endon_cell,
        orientation=orientation,
    )

    frame_width = bgr_frame.shape[1]
    frame_centre_x = frame_width / 2.0
    _tan_half_hfov = np.tan(np.deg2rad(CAMERA_HFOV_DEG) / 2.0)

    for block in endon_blocks:
        if block["present"] and "mean_x_px" in block:
            lateral_px = block["mean_x_px"] - frame_centre_x
            fd = block.get("face_depth_mm")
            if fd is not None and fd > 0:
                mm_per_px = 2.0 * fd * _tan_half_hfov / frame_width
                block["lateral_mm"] = lateral_px * mm_per_px

    return {"orientation": orientation, "blocks": endon_blocks, "frame_centre_x": frame_centre_x}


def _adjusted_depth(face_depth_mm: float) -> float:
    return face_depth_mm + 26.5


def _print_tower(tower: list[dict]) -> None:
    """Print a one-line-per-layer summary.

    Block positions come from the end-on cell only (left cell for left-oriented
    layers, right cell for right-oriented layers), so the face depths reported
    here already correspond to the correct side of the tower.
    """
    print("── Layer Analysis (front → mid → back) ────")
    for layer in tower:
        idx           = layer["layer"]
        orientation   = layer["orientation"]
        arrow         = "<-" if orientation == "left" else "->"
        frame_cx      = layer.get("frame_centre_x")
        labels        = ["front", " mid ", " back"]
        parts         = []
        px_debug      = []
        for label, block in zip(labels, layer["blocks"]):
            if block["present"]:
                fd  = block.get("face_depth_mm")
                lx  = block.get("lateral_mm")
                mx  = block.get("mean_x_px")
                d_str = f" @d={_adjusted_depth(fd):.1f}mm" if fd is not None else ""
                x_offset = 26.5 if orientation == "left" else -40
                x_str = f" @x={lx + x_offset:+.1f}mm" if lx is not None else ""
                parts.append(f"{label}: {block['colour']}{d_str}{x_str}")
                if mx is not None:
                    px_debug.append(f"{label.strip()}={mx:.0f}px")
            else:
                parts.append(f"{label}: missing")
        print(f"  L{idx} {arrow}  " + "  |  ".join(parts))
        centre_str = f"  centre={frame_cx:.0f}px" if frame_cx is not None else ""
        if px_debug:
            print(f"    [px debug]{centre_str}  " + "  ".join(px_debug))
    print()


def analyse_tower(bgr_frame: np.ndarray, depth_frame: np.ndarray, row_cells: list[tuple[dict, dict]]) -> list[dict]:
    global _last_print_time
    tower = []
    for layer_idx, (left_def, right_def) in enumerate(row_cells):
        pct_results = compute_percentages(bgr_frame, cells=[left_def, right_def])
        layer = analyse_layer(
            bgr_frame, depth_frame, pct_results[0], pct_results[1], left_def, right_def,
        )
        layer["layer"] = layer_idx
        tower.append(layer)

    now = time.monotonic()
    if now - _last_print_time >= PRINT_INTERVAL_S:
        _print_tower(tower)
        _last_print_time = now

    return tower


def build_tower_image(tower: list[dict]) -> np.ndarray:
    block_w, block_h, block_gap = 80, 28, 4
    layer_h, margin, label_w = block_h + block_gap, 40, 60
    n_layers, n_blocks = len(tower), 3
    img_w = margin * 2 + label_w + n_blocks * block_w + (n_blocks - 1) * block_gap
    img_h = margin * 2 + n_layers * layer_h
    canvas = np.full((img_h, img_w, 3), 30, dtype=np.uint8)

    for layer_data in tower:
        layer_idx, orientation, blocks = layer_data["layer"], layer_data["orientation"], layer_data["blocks"]
        y0 = margin + layer_idx * layer_h
        y1 = y0 + block_h
        cv2.putText(canvas, f"L{layer_idx}", (margin, y0 + block_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(canvas, "<-" if orientation == "left" else "->",
                    (margin + label_w - 18, y0 + block_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 80), 1, cv2.LINE_AA)
        x_start = margin + label_w
        for pos, block in enumerate(blocks):
            x0  = x_start + pos * (block_w + block_gap)
            x1  = x0 + block_w
            bgr = COLOUR_BGR.get(block["colour"], (60, 60, 60))
            if block["present"]:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), bgr, -1)
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (200, 200, 200), 1)
            else:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
    return canvas