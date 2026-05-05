"""
layer_analysis.py
-----------------
Analyses the Jenga tower structure layer by layer using absolute lane-based detection.
"""
from __future__ import annotations

import cv2
import numpy as np

from box_percentages import colour_mean_x_in_cell, compute_percentages
from perception_config import COLOUR_BGR, HSV_RANGES

SINGLE_DOMINANT_PCT = 55.0
# Increased threshold to 25% for better stability when blocks are removed
BLOCK_PRESENT_MIN_PCT = 25.0

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

def _blocks_from_endon(pcts: dict[str, float], mean_x: dict[str, float], cell: dict) -> list[dict]:
    """
    Maps detected colors to three absolute horizontal lanes: Left (0), Middle (1), Right (2).
    """
    corners = cell["corners"] # [TL, TR, BL, BR]
    # Calculate boundaries of the cell
    x_left_bound = (corners[0][0] + corners[2][0]) / 2.0
    x_right_bound = (corners[1][0] + corners[3][0]) / 2.0
    cell_w = x_right_bound - x_left_bound
    lane_w = cell_w / 3.0

    # Initialize 3 empty slots
    res = [{"colour": "unknown", "present": False} for _ in range(3)]
    
    # Filter for blocks that are actually present
    present_colours = {c: p for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT}
    
    for colour, pct in present_colours.items():
        mx = mean_x.get(colour)
        if mx is None:
            continue
        
        # Calculate lane index based on absolute horizontal position
        relative_x = mx - x_left_bound
        lane_idx = int(relative_x // lane_w)
        lane_idx = max(0, min(2, lane_idx)) # Ensure index is 0, 1, or 2
        
        # Assign the color to the lane. 
        # If two colors compete for a lane (noise), the one with higher coverage wins.
        if not res[lane_idx]["present"] or pct > present_colours.get(res[lane_idx]["colour"], 0):
            res[lane_idx] = {"colour": colour, "present": True}
            
    return res

def _blocks_from_sideon(pcts: dict[str, float]) -> list[dict]:
    """Side-on usually sees one block; return the most dominant colors."""
    present = sorted(
        [(c, p) for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT],
        key=lambda x: -x[1],
    )
    blocks = [{"colour": c, "present": True} for c, _ in present]
    while len(blocks) < 3:
        blocks.append({"colour": "unknown", "present": False})
    return blocks[:3]

def analyse_layer(
    bgr_frame: np.ndarray,
    left_result: dict,
    right_result: dict,
    left_cell: dict,
    right_cell: dict,
) -> dict:
    left_pcts = _colour_pcts(left_result)
    right_pcts = _colour_pcts(right_result)
    orientation = _detect_orientation(left_pcts, right_pcts)

    if orientation == "left":
        endon_pcts, sideon_pcts, endon_cell = left_pcts, right_pcts, left_cell
    else:
        endon_pcts, sideon_pcts, endon_cell = right_pcts, left_pcts, right_cell

    mean_x = colour_mean_x_in_cell(bgr_frame, endon_cell)
    
    # Pass the cell geometry to determine lanes
    endon_blocks = _blocks_from_endon(endon_pcts, mean_x, endon_cell)
    
    return {"orientation": orientation, "blocks": endon_blocks}

def analyse_tower(bgr_frame: np.ndarray, row_cells: list[tuple[dict, dict]]) -> list[dict]:
    tower = []
    for layer_idx, (left_def, right_def) in enumerate(row_cells):
        pct_results = compute_percentages(bgr_frame, cells=[left_def, right_def])
        layer = analyse_layer(
            bgr_frame, pct_results[0], pct_results[1], left_def, right_def
        )
        layer["layer"] = layer_idx
        tower.append(layer)
    return tower

def build_tower_image(tower: list[dict]) -> np.ndarray:
    # (Kept identical to original for visualisation consistency)
    block_w, block_h, block_gap = 80, 28, 4
    layer_h, margin, label_w = block_h + block_gap, 40, 60
    n_layers, n_blocks = len(tower), 3
    img_w = margin * 2 + label_w + n_blocks * block_w + (n_blocks - 1) * block_gap
    img_h = margin * 2 + n_layers * layer_h
    canvas = np.full((img_h, img_w, 3), 30, dtype=np.uint8)

    for layer_data in tower:
        layer_idx, orientation, blocks = layer_data["layer"], layer_data["orientation"], layer_data["blocks"]
        row = layer_idx
        y0 = margin + row * layer_h
        y1 = y0 + block_h
        cv2.putText(canvas, f"L{layer_idx}", (margin, y0 + block_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(canvas, "<-" if orientation == "left" else "->",
                    (margin + label_w - 18, y0 + block_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 80), 1, cv2.LINE_AA)
        x_start = margin + label_w
        for pos, block in enumerate(blocks):
            x0 = x_start + pos * (block_w + block_gap)
            x1 = x0 + block_w
            bgr = COLOUR_BGR.get(block["colour"], (60, 60, 60))
            if block["present"]:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), bgr, -1)
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (200, 200, 200), 1)
            else:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
    return canvas