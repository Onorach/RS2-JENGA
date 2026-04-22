"""
layer_analysis.py
-----------------
Analyses the Jenga tower structure layer by layer from per-cell colour percentages.
"""
from __future__ import annotations

import cv2
import numpy as np

from box_percentages import compute_percentages
from perception_config import COLOUR_BGR

SINGLE_DOMINANT_PCT = 55.0
BLOCK_PRESENT_MIN_PCT = 20.0


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


def _blocks_from_endon(pcts: dict[str, float]) -> list[dict]:
    present = {c: p for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT}
    if len(present) == 3:
        ordered = sorted(present.items(), key=lambda x: -x[1])
        return [{"colour": c, "present": True} for c, _ in ordered]
    if len(present) == 2:
        ordered = sorted(present.items(), key=lambda x: -x[1])
        top_colour = ordered[0][0]
        return [
            {"colour": "unknown", "present": False},
            {"colour": top_colour, "present": True},
            {"colour": ordered[1][0], "present": True},
        ]
    if len(present) == 1:
        c = list(present.keys())[0]
        return [
            {"colour": "unknown", "present": False},
            {"colour": "unknown", "present": False},
            {"colour": c, "present": True},
        ]
    return [{"colour": "unknown", "present": False}] * 3


def _blocks_from_sideon(pcts: dict[str, float]) -> list[dict]:
    present = sorted(
        [(c, p) for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT],
        key=lambda x: -x[1],
    )
    blocks = [{"colour": c, "present": True} for c, _ in present]
    while len(blocks) < 3:
        blocks.append({"colour": "unknown", "present": False})
    return blocks[:3]


def analyse_layer(left_result: dict, right_result: dict) -> dict:
    left_pcts = _colour_pcts(left_result)
    right_pcts = _colour_pcts(right_result)
    orientation = _detect_orientation(left_pcts, right_pcts)

    if orientation == "left":
        endon_pcts = left_pcts
        sideon_pcts = right_pcts
    else:
        endon_pcts = right_pcts
        sideon_pcts = left_pcts

    endon_blocks = _blocks_from_endon(endon_pcts)
    sideon_blocks = _blocks_from_sideon(sideon_pcts)
    sideon_colours = {b["colour"] for b in sideon_blocks if b["present"]}
    for b in endon_blocks:
        if b["colour"] == "unknown" and len(sideon_colours) == 1:
            b["colour"] = next(iter(sideon_colours))

    return {"orientation": orientation, "blocks": endon_blocks}


def analyse_tower(bgr_frame: np.ndarray, row_cells: list[tuple[dict, dict]]) -> list[dict]:
    tower = []
    for layer_idx, (left_def, right_def) in enumerate(row_cells):
        pct_results = compute_percentages(bgr_frame, cells=[left_def, right_def])
        layer = analyse_layer(pct_results[0], pct_results[1])
        layer["layer"] = layer_idx
        tower.append(layer)
    return tower


def build_tower_image(tower: list[dict]) -> np.ndarray:
    block_w, block_h, block_gap = 80, 28, 4
    layer_h, margin, label_w = block_h + block_gap, 40, 60
    n_layers, n_blocks = len(tower), 3
    img_w = margin * 2 + label_w + n_blocks * block_w + (n_blocks - 1) * block_gap
    img_h = margin * 2 + n_layers * layer_h
    canvas = np.full((img_h, img_w, 3), 30, dtype=np.uint8)

    for layer_data in tower:
        layer_idx = layer_data["layer"]
        orientation = layer_data["orientation"]
        blocks = layer_data["blocks"]
        row = n_layers - 1 - layer_idx
        y0, y1 = margin + row * layer_h, margin + row * layer_h + block_h
        cv2.putText(canvas, f"L{layer_idx}", (margin, y0 + block_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
        cv2.putText(canvas, "←" if orientation == "left" else "→",
                    (margin + label_w - 18, y0 + block_h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 80), 1, cv2.LINE_AA)
        x_start = margin + label_w
        for pos, block in enumerate(blocks):
            x0 = x_start + pos * (block_w + block_gap)
            x1 = x0 + block_w
            colour_name = block["colour"]
            bgr = COLOUR_BGR.get(colour_name, (60, 60, 60))
            if block["present"]:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), bgr, -1)
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (200, 200, 200), 1)
            else:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
                cv2.line(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
                cv2.line(canvas, (x1, y0), (x0, y1), (80, 80, 80), 1)
    return canvas
