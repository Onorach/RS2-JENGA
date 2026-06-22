"""
probe_response.py
-----------------
Probe-response monitoring for topple-shift detection.

This module is intentionally runtime-agnostic so play_runtime can stay focused
on frame orchestration and publishing.
"""

from __future__ import annotations

import copy
import json
import time
from collections import deque

from box_percentages import endon_outside_edge_x
from block_centroids import compute_layer_centroids
from perception_config import PROBE_TARGET_BLOCK_ID_PLACEHOLDER, CENTROID_ABORT_SHIFT_PCT
PROBE_PRINT_INTERVAL_S = 0.2

ROBOT_STATE_PROBING = "PROBING"
ROBOT_STATE_PICK_PLACE = "PICK & PLACE"
ROBOT_STATE_PLACING = "PICKING AND PLACING"
ROBOT_STATE_PLACING_LABELS = frozenset({ROBOT_STATE_PICK_PLACE, ROBOT_STATE_PLACING})


def parse_selected_goal_pick(data: str) -> tuple[int, int] | None:
    """
    Parse /selected_goal JSON from the GUI.

    Returns (layer, position) for the pick target, or None if unavailable.
    """
    text = (data or "").strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
        pick = payload.get("pick")
        if not isinstance(pick, dict):
            return None
        layer = _to_int_or_none(pick.get("layer"))
        position = _to_int_or_none(pick.get("position"))
        if layer is None or position is None:
            return None
        return int(layer), int(position)
    except (json.JSONDecodeError, TypeError):
        return None


def block_id_for_pick_slot(
    tower: list[dict],
    pick_layer: int,
    pick_position: int,
) -> int | None:
    """Resolve block_index from tower state using GUI layer + slot (0–2)."""
    for layer in tower:
        if int(layer.get("layer", -1)) != int(pick_layer):
            continue
        blocks = layer.get("blocks", [])
        if pick_position < 0 or pick_position >= len(blocks):
            return None
        block = blocks[pick_position]
        if not block.get("present"):
            return None
        return _to_int_or_none(block.get("block_index"))
    return None


def _to_int_or_none(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _endon_cell_for_layer(
    row_cells: list[tuple[dict, dict]],
    layer_idx: int,
    orientation: str,
) -> dict | None:
    n_layers = len(row_cells)
    if layer_idx < 0 or layer_idx >= n_layers:
        return None
    row_idx = (n_layers - 1) - layer_idx
    left_cell, right_cell = row_cells[row_idx]
    return left_cell if orientation == "left" else right_cell


def _layer_outside_edge_x(
    row_cells: list[tuple[dict, dict]] | None,
    layer_idx: int,
    orientation: str,
    fallback_centroid_xs: list[float],
) -> float | None:
    if row_cells is not None:
        cell = _endon_cell_for_layer(row_cells, layer_idx, orientation)
        if cell is not None:
            return endon_outside_edge_x(cell, orientation)
    if not fallback_centroid_xs:
        return None
    return (
        min(fallback_centroid_xs) if orientation == "left" else max(fallback_centroid_xs)
    )


def update_tower_centroids_for_probe(
    bgr_frame,
    depth_frame,
    row_cells: list[tuple[dict, dict]],
    tower: list[dict],
    baseline: dict,
) -> list[dict]:
    """
    Recompute near-face centroids (median, split-required) for all layers at or
    above the target block layer.  Layers below the target have their centroid
    values **frozen to baseline** — they are written back from the baseline
    snapshot so the shift comparison in _assess_probe_response always sees
    stable positions rather than freshly recomputed (depth-free, jittery)
    colour-blob means produced by analyse_tower.

    Uses compute_layer_centroids which always searches BOTH the end-on and
    opposite cells via a combined split_x search, so the front block's split
    (which may fall in the side-on cell) is never missed.
    """
    tower_out    = [dict(layer, blocks=[dict(b) for b in layer.get("blocks", [])]) for layer in tower]
    target_layer = _to_int_or_none(baseline.get("layer"))
    min_recompute_layer = None if target_layer is None else max(0, int(target_layer) - 1)
    n_layers     = len(row_cells)
    # Baseline centroid positions keyed by block_id — used to freeze layers
    # below the probe target so the shift comparison never sees jitter from
    # depth-free recomputation in analyse_tower.
    baseline_centroids: dict[int, tuple[float, float]] = baseline.get("all_centroids_px", {})

    for layer in tower_out:
        layer_idx = int(layer.get("layer", -1))

        # Layers below the probe target cannot move during a probe.
        # Write baseline centroid values back so _build_probe_snapshot always
        # compares against frozen positions rather than freshly recomputed
        # (possibly depth-free, jittery) colour-blob means.
        if min_recompute_layer is not None and layer_idx < int(min_recompute_layer):
            for block in layer.get("blocks", []):
                if not block.get("present"):
                    continue
                bid = _to_int_or_none(block.get("block_index"))
                if bid is None:
                    continue
                base_xy = baseline_centroids.get(bid)
                if base_xy is not None:
                    block["mean_x_px"] = float(base_xy[0])
                    block["mean_y_px"] = float(base_xy[1])
            continue

        orientation = str(layer.get("orientation", ""))
        if orientation not in ("left", "right"):
            continue

        row_idx = (n_layers - 1) - layer_idx
        if row_idx < 0 or row_idx >= n_layers:
            continue
        left_cell, right_cell = row_cells[row_idx]

        split_x_by_colour: dict[str, float] = {}
        centroids = compute_layer_centroids(
            bgr_frame,
            depth_frame,
            left_cell,
            right_cell,
            orientation,
            robust_stat="median",
            require_split=True,
            split_x_out=split_x_by_colour,
        )

        for block in layer.get("blocks", []):
            if not block.get("present"):
                block.pop("depth_split_x_px", None)
                continue
            colour = str(block.get("colour", ""))
            if colour in centroids:
                block["mean_x_px"] = float(centroids[colour][0])
                block["mean_y_px"] = float(centroids[colour][1])
            split_x = split_x_by_colour.get(colour)
            if split_x is not None:
                block["depth_split_x_px"] = float(split_x)
            else:
                block.pop("depth_split_x_px", None)

    return tower_out


def recompute_tower_centroids_strict(
    bgr_frame,
    depth_frame,
    row_cells: list[tuple[dict, dict]],
    tower: list[dict],
    min_layer: int = 0,
) -> list[dict]:
    """
    Recompute centroids using probe-style strict centroiding for tower layers.

    Used by PICKING AND PLACING mode to refresh all centroids without engaging
    probe monitoring/decision side effects.
    """
    tower_out = copy.deepcopy(tower)
    n_layers = len(row_cells)
    min_layer_idx = int(min_layer)

    for layer in tower_out:
        layer_idx = int(layer.get("layer", -1))
        if layer_idx < min_layer_idx:
            continue

        orientation = str(layer.get("orientation", ""))
        if orientation not in ("left", "right"):
            continue

        row_idx = (n_layers - 1) - layer_idx
        if row_idx < 0 or row_idx >= n_layers:
            continue
        left_cell, right_cell = row_cells[row_idx]

        centroids = compute_layer_centroids(
            bgr_frame,
            depth_frame,
            left_cell,
            right_cell,
            orientation,
            robust_stat="median",
            require_split=True,
        )

        for block in layer.get("blocks", []):
            if not block.get("present"):
                continue
            colour = str(block.get("colour", ""))
            if colour in centroids:
                block["mean_x_px"] = float(centroids[colour][0])
                block["mean_y_px"] = float(centroids[colour][1])

    return tower_out


def _build_probe_snapshot(
    tower: list[dict],
    block_id: int,
    frame_shape: tuple[int, int] | None = None,
    row_cells: list[tuple[dict, dict]] | None = None,
) -> dict | None:
    target_layer = None
    target_pos = None
    target_orientation = None

    for layer in tower:
        for pos_idx, block in enumerate(layer.get("blocks", [])):
            block_idx = _to_int_or_none(block.get("block_index"))
            if block_idx is None:
                continue
            if block_idx == int(block_id):
                target_layer = int(layer.get("layer", -1))
                target_pos = int(pos_idx)
                target_orientation = layer.get("orientation")
                break
        if target_layer is not None:
            break

    if target_layer is None or target_orientation not in ("left", "right"):
        return None

    behind_block_ids: list[int] = []
    layer_data = next((l for l in tower if int(l.get("layer", -1)) == target_layer), None)
    if layer_data is not None:
        for pos_idx, block in enumerate(layer_data.get("blocks", [])):
            block_idx = _to_int_or_none(block.get("block_index"))
            if block_idx is not None and block_idx >= 0:
                if pos_idx > target_pos:
                    behind_block_ids.append(block_idx)

    all_centroids_px: dict[int, tuple[float, float]] = {}
    block_layer_by_id: dict[int, int] = {}
    layer_orientation_by_idx: dict[int, str] = {}
    for layer in tower:
        layer_idx = int(layer.get("layer", -1))
        orientation = str(layer.get("orientation", ""))
        if orientation in ("left", "right"):
            layer_orientation_by_idx[layer_idx] = orientation
        for block in layer.get("blocks", []):
            if not block.get("present"):
                continue
            bid = _to_int_or_none(block.get("block_index"))
            mx = block.get("mean_x_px")
            my = block.get("mean_y_px")
            if bid is None or bid < 0 or mx is None or my is None:
                continue
            all_centroids_px[bid] = (float(mx), float(my))
            block_layer_by_id[bid] = layer_idx

    # Per-layer outside-edge x (geometric end-on cell edge when row_cells known).
    layer_edge_x_by_layer: dict[int, float] = {}
    for layer_idx, orientation in layer_orientation_by_idx.items():
        layer_xs = [
            xy[0]
            for bid, xy in all_centroids_px.items()
            if block_layer_by_id.get(bid) == layer_idx
        ]
        edge_x = _layer_outside_edge_x(row_cells, layer_idx, orientation, layer_xs)
        if edge_x is not None:
            layer_edge_x_by_layer[layer_idx] = float(edge_x)

    # Baseline outside-edge offset per block: block_x - layer_outside_edge_x.
    block_edge_offset_x: dict[int, float] = {}
    for bid, xy in all_centroids_px.items():
        layer_idx = block_layer_by_id.get(bid)
        if layer_idx is None:
            continue
        edge_x = layer_edge_x_by_layer.get(layer_idx)
        if edge_x is None:
            continue
        block_edge_offset_x[bid] = float(xy[0] - edge_x)

    excluded_centroid_ids = set([int(block_id)] + behind_block_ids)
    monitor_centroid_ids = sorted(
        bid for bid in all_centroids_px
        if (
            bid not in excluded_centroid_ids
            and block_layer_by_id.get(bid, -1) >= int(target_layer)
        )
    )

    target_centroid = all_centroids_px.get(int(block_id))
    monitor_points = [all_centroids_px[bid] for bid in monitor_centroid_ids if bid in all_centroids_px]
    if monitor_points:
        cx = float(sum(p[0] for p in monitor_points) / len(monitor_points))
        cy = float(sum(p[1] for p in monitor_points) / len(monitor_points))
        monitor_centroid_centre = (cx, cy)
    else:
        monitor_centroid_centre = None

    target_dist_px = None
    if target_centroid is not None and monitor_centroid_centre is not None:
        target_dist_px = (
            (target_centroid[0] - monitor_centroid_centre[0]) ** 2
            + (target_centroid[1] - monitor_centroid_centre[1]) ** 2
        ) ** 0.5

    # Outside-edge reference proxy for target layer:
    # use the outermost layer x-centroid on the visible end-on side.
    target_layer_xs = [
        all_centroids_px[bid][0]
        for bid, lyr in block_layer_by_id.items()
        if lyr == int(target_layer) and bid in all_centroids_px
    ]
    target_layer_outside_edge_x = _layer_outside_edge_x(
        row_cells,
        int(target_layer),
        target_orientation,
        target_layer_xs,
    )

    # Normalize centroid shifts by in-image block width (px), not frame size.
    target_layer_centroids = []
    if layer_data is not None:
        for block in layer_data.get("blocks", []):
            bid = _to_int_or_none(block.get("block_index"))
            if bid is None:
                continue
            xy = all_centroids_px.get(bid)
            if xy is not None:
                target_layer_centroids.append((xy[0], xy[1]))
    target_layer_centroids.sort(key=lambda p: p[0])
    adjacent_distances = [
        abs(target_layer_centroids[i + 1][0] - target_layer_centroids[i][0])
        for i in range(len(target_layer_centroids) - 1)
    ]
    block_width_px = None
    if adjacent_distances:
        block_width_px = float(sum(adjacent_distances) / len(adjacent_distances))
    elif frame_shape is not None:
        fh, fw = int(frame_shape[0]), int(frame_shape[1])
        if fh > 0 and fw > 0:
            block_width_px = float((fh * fh + fw * fw) ** 0.5)

    return {
        "block_id": int(block_id),
        "layer": int(target_layer),
        "target_pos": int(target_pos),
        "is_middle": bool(target_pos == 1),
        "behind_block_ids": behind_block_ids,
        "all_centroids_px": all_centroids_px,
        "block_layer_by_id": block_layer_by_id,
        "layer_edge_x_by_layer": layer_edge_x_by_layer,
        "block_edge_offset_x": block_edge_offset_x,
        "monitor_centroid_ids": monitor_centroid_ids,
        "target_dist_px": target_dist_px,
        "target_layer_outside_edge_x": target_layer_outside_edge_x,
        "block_width_px": block_width_px,
    }


def _assess_probe_response(baseline: dict, current: dict) -> dict:
    norm_px = float(
        current.get("block_width_px")
        or baseline.get("block_width_px")
        or 1.0
    )
    monitor_ids = list(baseline.get("monitor_centroid_ids", []))
    centroid_shift_pcts: list[float] = []
    for bid in monitor_ids:
        bxy = baseline.get("all_centroids_px", {}).get(bid)
        cxy = current.get("all_centroids_px", {}).get(bid)
        if bxy is None or cxy is None:
            continue

        # Tower centroids during monitoring already use anchored x + blob mean y.
        shift_px = float(
            ((float(cxy[0]) - float(bxy[0])) ** 2 + (float(cxy[1]) - float(bxy[1])) ** 2) ** 0.5
        )
        centroid_shift_pcts.append((shift_px / norm_px) * 100.0)
    avg_other_centroid_shift_pct = (
        float(sum(centroid_shift_pcts) / len(centroid_shift_pcts))
        if centroid_shift_pcts else 0.0
    )

    target_id = int(baseline.get("block_id", -1))
    base_target_xy = baseline.get("all_centroids_px", {}).get(target_id)
    now_target_xy = current.get("all_centroids_px", {}).get(target_id)
    target_dx_px = None
    target_dy_px = None
    if base_target_xy is not None and now_target_xy is not None:
        target_dx_px = float(now_target_xy[0]) - float(base_target_xy[0])
        target_dy_px = float(now_target_xy[1]) - float(base_target_xy[1])

    target_shift_pct = None
    if target_dx_px is not None and target_dy_px is not None:
        target_shift_pct = (((target_dx_px ** 2 + target_dy_px ** 2) ** 0.5) / norm_px) * 100.0
    target_moved = (
        target_dx_px is not None
        and target_dy_px is not None
        and ((target_dx_px ** 2 + target_dy_px ** 2) ** 0.5) > 0.0
    )

    if avg_other_centroid_shift_pct > CENTROID_ABORT_SHIFT_PCT:
        status = "tower_shifting"
    elif target_moved:
        status = "safe_to_remove"
    else:
        status = "monitoring"

    return {
        "status": status,
        "avg_other_centroid_shift_pct": avg_other_centroid_shift_pct,
        "target_dx_px": target_dx_px,
        "target_dy_px": target_dy_px,
        "target_shift_pct": target_shift_pct,
    }


class ProbeResponseMonitor:
    """Tracks probe-response state across frames and prints status updates."""

    def __init__(self) -> None:
        self._on_final_decision = None
        self._final_decision_sent: bool = False
        self._robot_control_enabled: bool = False
        self._robot_target_block_id: int | None = None
        self._manual_override_enabled: bool = False
        self._manual_target_block_id: int | None = None
        self._active_block_id: int | None = None
        self._baseline: dict | None = None
        self._last_status: str | None = None
        self._last_eval: dict | None = None
        self._last_print_time: float = 0.0
        self._centroid_shift_avg_window = deque(maxlen=3)
        self._robot_state_label: str = "STANDBY"
        # When an abort is raised while robot-controlled probing is active,
        # suppress immediate auto-restart on the same block until robot state
        # changes away from PROBING (or target block changes).
        self._aborted_robot_block_latch: int | None = None
        self._last_probed_block_id: int | None = None

    def last_probed_block_id(self) -> int | None:
        """Block id from the most recent robot-controlled probe session."""
        return self._last_probed_block_id

    def _target_block_id(self) -> int | None:
        if self._robot_control_enabled:
            return self._robot_target_block_id
        if self._manual_override_enabled:
            return self._manual_target_block_id
        return PROBE_TARGET_BLOCK_ID_PLACEHOLDER

    def is_robot_controlled(self) -> bool:
        """True when /robot_state is PROBING and a goal block is known."""
        return self._robot_control_enabled

    def robot_target_block_id(self) -> int | None:
        return self._robot_target_block_id if self._robot_control_enabled else None

    def sync_from_robot(self, robot_state_label: str | None, block_id: int | None) -> None:
        """
        Start/stop monitoring from /robot_state and a resolved goal block id.

        Monitoring runs when the label is PROBING and block_id is set.
        """
        label = (robot_state_label or "").strip().upper()
        self._robot_state_label = label
        bid = _to_int_or_none(block_id)

        if label == ROBOT_STATE_PROBING:
            if bid is not None:
                if (
                    self._aborted_robot_block_latch is not None
                    and int(bid) == int(self._aborted_robot_block_latch)
                ):
                    # Stay stopped after abort for this target until state/goal changes.
                    self._robot_control_enabled = False
                    self._robot_target_block_id = None
                    return
                # New target clears abort latch.
                if self._aborted_robot_block_latch is not None:
                    self._aborted_robot_block_latch = None
                if (
                    not self._robot_control_enabled
                    or self._robot_target_block_id != bid
                ):
                    print(f"[probe] robot PROBING — monitoring block {bid}")
                self._robot_control_enabled = True
                self._robot_target_block_id = int(bid)
                self._last_probed_block_id = int(bid)
                self._manual_override_enabled = False
                self._manual_target_block_id = None
            # PROBING but goal not resolved yet: do not clear an active session.
            return

        if self._robot_control_enabled:
            print(f"[probe] robot {label or 'IDLE'} — stopping monitoring")
        self._robot_control_enabled = False
        self._robot_target_block_id = None
        if self._aborted_robot_block_latch is not None:
            self._aborted_robot_block_latch = None

    def is_robot_placing(self) -> bool:
        """True when /robot_state reports an active pick-and-place operation."""
        return self._robot_state_label in ROBOT_STATE_PLACING_LABELS

    def set_target_block_id(self, block_id: int | None) -> None:
        """Set active probe target from Layer Analysis clicks (ignored while robot probes)."""
        if self._robot_control_enabled:
            return
        self._manual_override_enabled = True
        self._manual_target_block_id = None if block_id is None else int(block_id)

    def _status_label(self, status: str | None) -> str:
        if status == "safe_to_remove":
            return "SAFE_TO_REMOVE"
        if status == "tower_shifting":
            return "ABORT_TOWER_MOVED"
        if status == "monitoring":
            return "MONITORING"
        return "IDLE"

    def status_text(self) -> str:
        """Short status text for UI overlays."""
        if self._active_block_id is None:
            return "probe: idle"
        return f"probe: block {self._active_block_id}  {self._status_label(self._last_status)}"

    def is_active(self) -> bool:
        """True when a probe target is currently selected/active."""
        return self._target_block_id() is not None

    def baseline_snapshot(self) -> dict | None:
        """Baseline probe snapshot (blob centroids at monitoring start), if any."""
        return self._baseline

    def is_monitoring_mode(self) -> bool:
        """True only while probe state is actively MONITORING."""
        return (
            self._active_block_id is not None
            and self._baseline is not None
            and self._last_status == "monitoring"
        )

    def monitoring_min_layer(self) -> int | None:
        """
        Minimum layer index for monitoring overlays.

        Returns one layer below the target block (clamped to 0) while in
        monitoring mode, else None.
        """
        if not self.is_monitoring_mode() or self._baseline is None:
            return None
        target_layer = _to_int_or_none(self._baseline.get("layer"))
        if target_layer is None:
            return None
        return max(0, int(target_layer) - 1)

    def active_session_min_layer(self) -> int | None:
        """
        Minimum layer index for active topple-monitoring session overlays.

        Returns one layer below the target block (clamped to 0) whenever a
        probe session has a valid baseline.
        """
        if self._active_block_id is None or self._baseline is None:
            return None
        target_layer = _to_int_or_none(self._baseline.get("layer"))
        if target_layer is None:
            return None
        return max(0, int(target_layer) - 1)

    def set_on_final_decision(self, cb) -> None:
        """Set callback called once per monitoring session."""
        self._on_final_decision = cb

    def _emit_final_decision(
        self,
        block_id: int,
        status: str,
        reason: str | None = None,
    ) -> None:
        if self._final_decision_sent:
            return
        self._final_decision_sent = True
        if self._on_final_decision is None:
            return
        try:
            self._on_final_decision(block_id, status, reason)
        except Exception:
            # Never break perception loop due to a notification failure.
            pass

    def _print_final_decision(self) -> None:
        if self._active_block_id is None:
            return
        label = self._status_label(self._last_status)
        block_id = int(self._active_block_id)
        if label == "SAFE_TO_REMOVE":
            self._emit_final_decision(block_id, "safe", label)
            print(f"[probe] final block={self._active_block_id} decision=SAFE (safe to remove)")
            return
        if label.startswith("ABORT_"):
            self._emit_final_decision(block_id, "abort", label)
            print(f"[probe] final block={self._active_block_id} decision=ABORT ({label})")
            return
        # Any other end state: treat as abort for external signalling.
        self._emit_final_decision(block_id, "abort", label)
        print(f"[probe] final block={self._active_block_id} decision=INCONCLUSIVE ({label})")

    def _stop_monitoring_after_abort(self) -> None:
        """Stop active monitoring immediately after an abort decision."""
        if self._active_block_id is not None and self._robot_control_enabled:
            self._aborted_robot_block_latch = int(self._active_block_id)
        self._active_block_id = None
        self._baseline = None
        self._last_status = None
        self._last_eval = None
        self._centroid_shift_avg_window.clear()
        self._robot_control_enabled = False
        self._robot_target_block_id = None

    def update(
        self,
        tower_state: list[dict],
        frame_shape: tuple[int, int] | None = None,
        *,
        bgr_frame=None,
        depth_frame=None,
        row_cells: list[tuple[dict, dict]] | None = None,
    ) -> list[dict]:
        """
        Run probe logic on tower_state (raw blob centroids from layer analysis).

        Returns tower_state with monitoring centroids applied when a baseline exists.
        """
        probe_target_block_id = self._target_block_id()
        if probe_target_block_id is None:
            if self._active_block_id is not None:
                self._print_final_decision()
            self._active_block_id = None
            self._baseline = None
            self._last_status = None
            self._last_eval = None
            self._centroid_shift_avg_window.clear()
            return tower_state

        if not tower_state:
            return tower_state

        if self._active_block_id != int(probe_target_block_id):
            self._active_block_id = int(probe_target_block_id)
            self._final_decision_sent = False
            self._baseline = _build_probe_snapshot(
                tower_state,
                block_id=self._active_block_id,
                frame_shape=frame_shape,
                row_cells=row_cells,
            )
            self._last_status = None
            self._last_eval = None
            self._centroid_shift_avg_window.clear()
            if self._baseline is not None:
                slot_names = ("front", "mid", "back")
                pos = int(self._baseline.get("target_pos", -1))
                slot = slot_names[pos] if 0 <= pos < len(slot_names) else f"slot{pos}"
                print(
                    f"[probe] started for block {self._active_block_id} "
                    f"(layer L{self._baseline['layer']}, {slot})"
                )
            else:
                print(f"[probe] waiting for valid snapshot for block {self._active_block_id}")

        tower_for_eval = tower_state
        if (
            self._baseline is not None
            and bgr_frame is not None
            and row_cells is not None
        ):
            tower_for_eval = update_tower_centroids_for_probe(
                bgr_frame,
                depth_frame,
                row_cells,
                tower_state,
                self._baseline,
            )

        current_snapshot = _build_probe_snapshot(
            tower_for_eval,
            block_id=self._active_block_id,
            frame_shape=frame_shape,
            row_cells=row_cells,
        )

        if self._baseline is None or current_snapshot is None:
            return tower_for_eval

        eval_result = _assess_probe_response(self._baseline, current_snapshot)

        # Smooth tower-motion metric over 3 checks (rolling average).
        raw_centroid_shift_avg = float(eval_result.get("avg_other_centroid_shift_pct", 0.0))
        self._centroid_shift_avg_window.append(raw_centroid_shift_avg)
        centroid_shift_avg_smoothed = (
            float(sum(self._centroid_shift_avg_window) / len(self._centroid_shift_avg_window))
            if self._centroid_shift_avg_window
            else 0.0
        )

        # Use the smoothed tower-motion metric for the "safe vs abort" decision.
        dx = eval_result.get("target_dx_px")
        dy = eval_result.get("target_dy_px")
        target_moved = (
            dx is not None
            and dy is not None
            and ((float(dx) ** 2 + float(dy) ** 2) ** 0.5) > 0.0
        )
        if centroid_shift_avg_smoothed > float(CENTROID_ABORT_SHIFT_PCT):
            eval_result["status"] = "tower_shifting"
        elif target_moved:
            eval_result["status"] = "safe_to_remove"
        else:
            eval_result["status"] = "monitoring"
        eval_result["avg_other_centroid_shift_pct"] = centroid_shift_avg_smoothed

        now = time.monotonic()
        should_print = (
            eval_result["status"] != self._last_status
            or (now - self._last_print_time) >= PROBE_PRINT_INTERVAL_S
        )
        if should_print:
            # Only print once the smoothed value is a true "3 checks" average.
            if len(self._centroid_shift_avg_window) < 3:
                should_print = False
            if dx is None or dy is None:
                movement_xy = "(n/a,n/a)"
            else:
                movement_xy = f"({dx:+.1f},{dy:+.1f})"
            if should_print:
                print(
                    "[probe] "
                    f"block={self._active_block_id} status={eval_result['status']}  "
                    f"centroid_shift_avg={eval_result['avg_other_centroid_shift_pct']:.2f}%  "
                    f"centroid_movement_px={movement_xy}"
                )
                self._last_print_time = now
        if eval_result["status"] != self._last_status:
            label = self._status_label(eval_result["status"])
            if label == "ABORT_TOWER_MOVED":
                print(f"[probe] decision block={self._active_block_id}: ABORT (tower moved)")
                self._emit_final_decision(int(self._active_block_id), "abort", label)
                self._stop_monitoring_after_abort()
                return tower_for_eval
        self._last_status = eval_result["status"]
        self._last_eval = eval_result
        return tower_for_eval