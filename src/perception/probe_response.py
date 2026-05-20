"""
probe_response.py
-----------------
Probe-response monitoring for topple-shift detection.

This module is intentionally runtime-agnostic so play_runtime can stay focused
on frame orchestration and publishing.
"""

from __future__ import annotations

import time

from perception_config import (
    PROBE_TARGET_BLOCK_ID_PLACEHOLDER,
    PROBE_TARGET_GAIN_MIN_PCT,
    PROBE_STABLE_DELTA_MAX_PCT,
    PROBE_ABOVE_LAYER_GAIN_MIN_PCT,
)


def _colour_pct(cell_result: dict | None, colour: str | None) -> float | None:
    if not cell_result or not colour:
        return None
    return float(cell_result.get("colours", {}).get(colour, {}).get("pct", 0.0))


def _build_probe_snapshot(
    tower: list[dict],
    pct_results: list[dict],
    n_layers: int,
    block_id: int,
) -> dict | None:
    target_layer = None
    target_pos = None
    target_colour = None
    target_orientation = None

    for layer in tower:
        for pos_idx, block in enumerate(layer.get("blocks", [])):
            if int(block.get("block_index", -1)) == int(block_id):
                if not block.get("present"):
                    return None
                target_layer = int(layer.get("layer", -1))
                target_pos = int(pos_idx)
                target_colour = str(block.get("colour", "unknown"))
                target_orientation = layer.get("orientation")
                break
        if target_layer is not None:
            break

    if target_layer is None or target_orientation not in ("left", "right"):
        return None

    row_idx = (n_layers - 1) - target_layer
    if row_idx < 0 or row_idx >= n_layers:
        return None

    left_idx = row_idx * 2
    right_idx = left_idx + 1
    if right_idx >= len(pct_results):
        return None

    target_cell = pct_results[left_idx] if target_orientation == "left" else pct_results[right_idx]

    same_layer_ref: dict[str, float] = {}
    layer_data = next((l for l in tower if int(l.get("layer", -1)) == target_layer), None)
    if layer_data is not None:
        for pos_idx, block in enumerate(layer_data.get("blocks", [])):
            if pos_idx == target_pos or not block.get("present"):
                continue
            colour = str(block.get("colour", "unknown"))
            if colour and colour != "unknown":
                pct = _colour_pct(target_cell, colour)
                if pct is not None:
                    same_layer_ref[colour] = pct

    above_front_colour = None
    above_mid_colour = None
    above_front_pct = None
    above_mid_pct = None
    above_layer = target_layer + 1
    if above_layer < n_layers:
        above_data = next((l for l in tower if int(l.get("layer", -1)) == above_layer), None)
        if above_data is not None and above_data.get("orientation") in ("left", "right"):
            above_row_idx = (n_layers - 1) - above_layer
            a_left_idx = above_row_idx * 2
            a_right_idx = a_left_idx + 1
            if a_right_idx < len(pct_results):
                above_cell = pct_results[a_left_idx] if above_data["orientation"] == "left" else pct_results[a_right_idx]
                above_blocks = above_data.get("blocks", [])
                if len(above_blocks) >= 2:
                    if above_blocks[0].get("present"):
                        above_front_colour = str(above_blocks[0].get("colour", "unknown"))
                        above_front_pct = _colour_pct(above_cell, above_front_colour)
                    if above_blocks[1].get("present"):
                        above_mid_colour = str(above_blocks[1].get("colour", "unknown"))
                        above_mid_pct = _colour_pct(above_cell, above_mid_colour)

    return {
        "block_id": int(block_id),
        "layer": int(target_layer),
        "target_pos": int(target_pos),
        "is_middle": bool(target_pos == 1),
        "target_colour": target_colour,
        "target_pct": _colour_pct(target_cell, target_colour),
        "same_layer_ref": same_layer_ref,
        "above_front_colour": above_front_colour,
        "above_mid_colour": above_mid_colour,
        "above_front_pct": above_front_pct,
        "above_mid_pct": above_mid_pct,
    }


def _assess_probe_response(baseline: dict, current: dict) -> dict:
    target_base = float(baseline.get("target_pct") or 0.0)
    target_now = float(current.get("target_pct") or 0.0)
    target_delta = target_now - target_base

    same_layer_deltas: dict[str, float] = {}
    for colour, base_pct in baseline.get("same_layer_ref", {}).items():
        now_pct = float(current.get("same_layer_ref", {}).get(colour, 0.0))
        same_layer_deltas[colour] = now_pct - float(base_pct)
    max_other_abs_delta = max((abs(v) for v in same_layer_deltas.values()), default=0.0)

    def _delta(now_val: float | None, base_val: float | None) -> float | None:
        if now_val is None or base_val is None:
            return None
        return float(now_val) - float(base_val)

    above_front_delta = _delta(current.get("above_front_pct"), baseline.get("above_front_pct"))
    above_mid_delta = _delta(current.get("above_mid_pct"), baseline.get("above_mid_pct"))
    above_shift = any(
        d is not None and d >= PROBE_ABOVE_LAYER_GAIN_MIN_PCT
        for d in (above_front_delta, above_mid_delta)
    )

    if not bool(current.get("is_middle", False)):
        status = "invalid_target_not_middle"
    elif above_shift:
        status = "tower_shifting"
    elif (
        target_delta >= PROBE_TARGET_GAIN_MIN_PCT
        and max_other_abs_delta <= PROBE_STABLE_DELTA_MAX_PCT
    ):
        status = "safe_to_remove"
    else:
        status = "monitoring"

    return {
        "status": status,
        "target_delta_pct": target_delta,
        "max_other_delta_pct": max_other_abs_delta,
        "above_front_delta_pct": above_front_delta,
        "above_mid_delta_pct": above_mid_delta,
        "same_layer_deltas": same_layer_deltas,
    }


class ProbeResponseMonitor:
    """Tracks probe-response state across frames and prints status updates."""

    def __init__(self) -> None:
        self._active_block_id: int | None = None
        self._baseline: dict | None = None
        self._last_status: str | None = None
        self._last_print_time: float = 0.0

    def _target_block_id(self) -> int | None:
        """Placeholder probe trigger source. Replace with topic/service later."""
        return PROBE_TARGET_BLOCK_ID_PLACEHOLDER

    def update(self, tower_state: list[dict], pct_results: list[dict], row_cells: list[tuple[dict, dict]]) -> None:
        probe_target_block_id = self._target_block_id()
        if probe_target_block_id is None:
            self._active_block_id = None
            self._baseline = None
            self._last_status = None
            return

        if not tower_state or not pct_results:
            return

        n_layers = len(row_cells)
        if self._active_block_id != int(probe_target_block_id):
            self._active_block_id = int(probe_target_block_id)
            self._baseline = _build_probe_snapshot(
                tower_state,
                pct_results,
                n_layers=n_layers,
                block_id=self._active_block_id,
            )
            self._last_status = None
            if self._baseline is not None:
                print(
                    f"[probe] started for block {self._active_block_id} "
                    f"(layer L{self._baseline['layer']}, "
                    f"middle={self._baseline['is_middle']})"
                )
            else:
                print(f"[probe] waiting for valid snapshot for block {self._active_block_id}")

        current_snapshot = _build_probe_snapshot(
            tower_state,
            pct_results,
            n_layers=n_layers,
            block_id=self._active_block_id,
        )

        if self._baseline is None or current_snapshot is None:
            return

        eval_result = _assess_probe_response(self._baseline, current_snapshot)
        now = time.monotonic()
        should_print = (
            eval_result["status"] != self._last_status
            or (now - self._last_print_time) >= 1.0
        )
        if should_print:
            print(
                "[probe] "
                f"block={self._active_block_id} status={eval_result['status']}  "
                f"target_d={eval_result['target_delta_pct']:+.2f}%  "
                f"same_layer_max_d={eval_result['max_other_delta_pct']:.2f}%  "
                f"above_front_d={eval_result['above_front_delta_pct']}  "
                f"above_mid_d={eval_result['above_mid_delta_pct']}"
            )
            self._last_print_time = now
        self._last_status = eval_result["status"]
