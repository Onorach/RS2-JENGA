"""
tower_analysis.py
-----------------
Analyses the Jenga tower structure layer by layer from the per-cell colour
percentages produced by box_percentages.compute_percentages().

Each layer has:
  - orientation: "left" (3-block face on left) or "right" (3-block face on right)
  - blocks: list of 3 block dicts ordered front→middle→back
      Each block has:
        - colour:  detected colour name
        - present: True / False (False = removed)

Orientation logic (camera is 45° to both faces, sees two faces per layer):
  "left"  — left_cell  shows a 3-way split (~33% each)
             right_cell shows a dominant single colour (side-on face)
  "right" — right_cell shows a 3-way split
             left_cell  shows a dominant single colour

Missing block logic:
  A block is considered removed when one colour in the end-on cell is
  significantly over-represented (~66%) compared to the expected ~33%.
  The over-represented colour is the block behind the gap, now visible
  through the empty slot (adds ~6% extra area as described).

Thresholds (all tunable at the top of the file):
  SINGLE_DOMINANT_PCT   — min % for a face to be called "side-on dominant"
  BLOCK_PRESENT_MIN_PCT — min % for a block to be considered present
  SPLIT_MAX_PCT         — max % for any colour in an end-on cell before
                          we consider it a dominant/missing-block case
"""
from __future__ import annotations

import sys
import cv2
import numpy as np

from box_percentages import compute_percentages, GRID_CELLS
from perception_config import COLOUR_BGR

# ---------------------------------------------------------------------------
# Tunable thresholds
# ---------------------------------------------------------------------------
SINGLE_DOMINANT_PCT  = 55.0   # side-on face: one colour above this → dominant
BLOCK_PRESENT_MIN_PCT = 20.0  # end-on face:  colour above this → block present
SPLIT_MAX_PCT         = 50.0  # end-on face:  no colour above this → clean 3-way split

# Expected share per block on the end-on face (3 blocks, equal width)
EXPECTED_BLOCK_PCT = 100.0 / 3  # ≈ 33.3 %

# If a block is missing, the one behind it shows ~6% more area
MISSING_BLOCK_EXTRA_PCT = 6.0


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _colour_pcts(cell_result: dict) -> dict[str, float]:
    """Extract {colour: pct} from a compute_percentages cell result, excluding 'none'."""
    return {
        c: info["pct"]
        for c, info in cell_result["colours"].items()
        if c != "none" and info["pct"] > 0
    }


def _dominant_colour(pcts: dict[str, float]) -> tuple[str, float] | None:
    """Return (colour, pct) of the most dominant colour, or None if empty."""
    if not pcts:
        return None
    c = max(pcts, key=lambda k: pcts[k])
    return c, pcts[c]


def _detect_orientation(left_pcts: dict[str, float],
                        right_pcts: dict[str, float]) -> str:
    """
    Return "left" if the end-on (3-way split) face is on the left,
    "right" if it is on the right.

    The side-on face has one colour clearly dominant (> SINGLE_DOMINANT_PCT).
    The end-on face has no single colour dominant.
    """
    left_dom  = _dominant_colour(left_pcts)
    right_dom = _dominant_colour(right_pcts)

    left_is_dominant  = left_dom  is not None and left_dom[1]  >= SINGLE_DOMINANT_PCT
    right_is_dominant = right_dom is not None and right_dom[1] >= SINGLE_DOMINANT_PCT

    if right_is_dominant and not left_is_dominant:
        return "left"   # end-on face is left → "left" orientation
    if left_is_dominant and not right_is_dominant:
        return "right"  # end-on face is right → "right" orientation

    # Ambiguous: fall back to whichever side has a lower max percentage
    # (more evenly split = more likely end-on)
    left_max  = left_dom[1]  if left_dom  else 0
    right_max = right_dom[1] if right_dom else 0
    return "left" if left_max <= right_max else "right"


def _blocks_from_endon(pcts: dict[str, float]) -> list[dict]:
    """
    Given colour percentages from the end-on cell, return a list of 3 block
    dicts ordered by x-centroid (front → back, approximated by left → right
    within the cell).

    A colour is 'present' if its share is >= BLOCK_PRESENT_MIN_PCT.
    When fewer than 3 colours clear the threshold, the missing slot is inferred
    from the over-represented colour (which shows ~6% extra area through the gap).
    """
    present = {c: p for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT}

    blocks: list[dict] = []

    if len(present) == 3:
        # All three blocks present — order by descending pct as proxy for
        # front-to-back (front block occludes less, appears slightly smaller)
        ordered = sorted(present.items(), key=lambda x: -x[1])
        blocks = [{"colour": c, "present": True} for c, _ in ordered]

    elif len(present) == 2:
        # One block removed — the over-represented colour gained ~6%
        ordered = sorted(present.items(), key=lambda x: -x[1])
        top_colour, top_pct = ordered[0]
        # The missing slot sits in front of the top colour
        blocks = [
            {"colour": "unknown", "present": False},   # removed block
            {"colour": top_colour, "present": True},   # now over-exposed
            {"colour": ordered[1][0], "present": True},
        ]

    elif len(present) == 1:
        # Two blocks removed
        c = list(present.keys())[0]
        blocks = [
            {"colour": "unknown", "present": False},
            {"colour": "unknown", "present": False},
            {"colour": c,         "present": True},
        ]

    else:
        # No blocks detected (layer may be empty or outside ROI)
        blocks = [{"colour": "unknown", "present": False}] * 3

    return blocks


def _blocks_from_sideon(pcts: dict[str, float]) -> list[dict]:
    """
    Given colour percentages from the side-on cell, return a list of block
    dicts.  On the side-on face each block spans the full depth so colours
    appear as horizontal bands ordered left→right (position 0→2).
    We use percentage share as a proxy for position width.
    """
    present = sorted(
        [(c, p) for c, p in pcts.items() if p >= BLOCK_PRESENT_MIN_PCT],
        key=lambda x: -x[1]
    )

    blocks = [{"colour": c, "present": True} for c, _ in present]

    # Pad to 3 if fewer detected
    while len(blocks) < 3:
        blocks.append({"colour": "unknown", "present": False})

    return blocks[:3]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyse_layer(left_result: dict, right_result: dict) -> dict:
    """
    Analyse a single layer from its left_cell and right_cell percentage dicts.

    Returns
    -------
    {
        "orientation": "left" | "right",
        "blocks": [
            {"colour": str, "present": bool},  # position 0 = front
            {"colour": str, "present": bool},  # position 1 = middle
            {"colour": str, "present": bool},  # position 2 = back
        ]
    }
    """
    left_pcts  = _colour_pcts(left_result)
    right_pcts = _colour_pcts(right_result)

    orientation = _detect_orientation(left_pcts, right_pcts)

    if orientation == "left":
        endon_pcts  = left_pcts
        sideon_pcts = right_pcts
    else:
        endon_pcts  = right_pcts
        sideon_pcts = left_pcts

    endon_blocks  = _blocks_from_endon(endon_pcts)
    sideon_blocks = _blocks_from_sideon(sideon_pcts)

    # Cross-validate: use side-on to fill unknown colours in end-on where possible
    sideon_colours = {b["colour"] for b in sideon_blocks if b["present"]}
    for b in endon_blocks:
        if b["colour"] == "unknown" and len(sideon_colours) == 1:
            b["colour"] = next(iter(sideon_colours))

    return {"orientation": orientation, "blocks": endon_blocks}


def analyse_tower(bgr_frame: np.ndarray,
                  row_cells: list[tuple[dict, dict]]) -> list[dict]:
    """
    Analyse all layers of the tower.

    Parameters
    ----------
    bgr_frame : Full-resolution BGR frame.
    row_cells : List of (left_cell_def, right_cell_def) pairs, one per layer,
                ordered bottom → top.  Each cell_def matches the GRID_CELLS
                format: {"name": str, "corners": [TL, TR, BL, BR]}.

    Returns
    -------
    List of layer dicts ordered bottom → top:
    [
        {
            "layer": 0,
            "orientation": "left" | "right",
            "blocks": [
                {"colour": str, "present": bool},  # front
                {"colour": str, "present": bool},  # middle
                {"colour": str, "present": bool},  # back
            ]
        },
        ...
    ]
    """
    tower = []
    for layer_idx, (left_def, right_def) in enumerate(row_cells):
        pct_results = compute_percentages(bgr_frame, cells=[left_def, right_def])
        left_result  = pct_results[0]
        right_result = pct_results[1]
        layer = analyse_layer(left_result, right_result)
        layer["layer"] = layer_idx
        tower.append(layer)
    return tower


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

_BLOCK_W   = 80
_BLOCK_H   = 28
_BLOCK_GAP = 4
_LAYER_H   = _BLOCK_H + _BLOCK_GAP
_MARGIN    = 40
_LABEL_W   = 60


def build_tower_image(tower: list[dict]) -> np.ndarray:
    """
    Render a schematic top-view diagram of the tower.

    Each layer is drawn as three coloured rectangles (front → back left→right).
    Missing blocks are drawn as hollow grey rectangles.
    Orientation arrow indicates which face is end-on.
    """
    n_layers = len(tower)
    n_blocks = 3

    img_w = _MARGIN * 2 + _LABEL_W + n_blocks * _BLOCK_W + (n_blocks - 1) * _BLOCK_GAP
    img_h = _MARGIN * 2 + n_layers * _LAYER_H

    canvas = np.full((img_h, img_w, 3), 30, dtype=np.uint8)  # dark background

    for layer_data in tower:
        layer_idx   = layer_data["layer"]
        orientation = layer_data["orientation"]
        blocks      = layer_data["blocks"]

        # Draw bottom layer at the bottom of the image
        row = (n_layers - 1 - layer_idx)
        y0  = _MARGIN + row * _LAYER_H
        y1  = y0 + _BLOCK_H

        # Layer label
        cv2.putText(canvas, f"L{layer_idx}",
                    (_MARGIN, y0 + _BLOCK_H - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)

        # Orientation indicator
        arrow = "←" if orientation == "left" else "→"
        cv2.putText(canvas, arrow,
                    (_MARGIN + _LABEL_W - 18, y0 + _BLOCK_H - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 80), 1, cv2.LINE_AA)

        x_start = _MARGIN + _LABEL_W
        for pos, block in enumerate(blocks):
            x0 = x_start + pos * (_BLOCK_W + _BLOCK_GAP)
            x1 = x0 + _BLOCK_W

            colour_name = block["colour"]
            bgr = COLOUR_BGR.get(colour_name, (60, 60, 60))

            if block["present"]:
                cv2.rectangle(canvas, (x0, y0), (x1, y1), bgr, -1)
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (200, 200, 200), 1)
                cv2.putText(canvas, colour_name[:3],
                            (x0 + 4, y0 + _BLOCK_H - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.32, (240, 240, 240), 1, cv2.LINE_AA)
            else:
                # Missing block — hollow with X
                cv2.rectangle(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
                cv2.line(canvas, (x0, y0), (x1, y1), (80, 80, 80), 1)
                cv2.line(canvas, (x1, y0), (x0, y1), (80, 80, 80), 1)

    # Column headers (front / mid / back)
    x_start = _MARGIN + _LABEL_W
    for i, label in enumerate(["front", "mid", "back"]):
        x0 = x_start + i * (_BLOCK_W + _BLOCK_GAP)
        cv2.putText(canvas, label,
                    (x0 + 4, _MARGIN - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (140, 140, 140), 1, cv2.LINE_AA)

    return canvas


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main_standalone(image_path: str) -> None:
    bgr = cv2.imread(image_path)
    if bgr is None:
        print(f"Cannot read: {image_path}")
        sys.exit(1)

    # For standalone use, treat the whole tower as one "layer" using the
    # default GRID_CELLS (left_cell + right_cell).  Per-row cell definitions
    # require calibration data that comes from perception_config / play scripts.
    from box_percentages import GRID_CELLS
    row_cells = [(GRID_CELLS[0], GRID_CELLS[1])]

    tower = analyse_tower(bgr, row_cells)

    for layer in tower:
        print(f"Layer {layer['layer']}  orientation={layer['orientation']}")
        for i, b in enumerate(layer["blocks"]):
            status = "present" if b["present"] else "REMOVED"
            print(f"  pos {i}: {b['colour']:<10}  {status}")

    vis = build_tower_image(tower)
    cv2.namedWindow("Tower analysis", cv2.WINDOW_NORMAL)
    cv2.imshow("Tower analysis", vis)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_standalone(sys.argv[1])
    else:
        print("Usage: python tower_analysis.py <image_path>")
        sys.exit(1)