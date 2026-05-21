"""
probe_response.py
-----------------
Probe-response monitoring for topple-shift detection.

This module is intentionally runtime-agnostic so play_runtime can stay focused
on frame orchestration and publishing.
"""

from __future__ import annotations

import time

from perception_config import PROBE_TARGET_BLOCK_ID_PLACEHOLDER

CENTROID_ABORT_SHIFT_PCT = 5.0
PROBE_PRINT_INTERVAL_S = 0.2

def _to_int_or_none(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _build_probe_snapshot(
    tower: list[dict],
    block_id: int,
    frame_shape: tuple[int, int] | None = None,
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
    for layer in tower:
        layer_idx = int(layer.get("layer", -1))
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
        "monitor_centroid_ids": monitor_centroid_ids,
        "target_dist_px": target_dist_px,
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
        shift_px = float(((cxy[0] - bxy[0]) ** 2 + (cxy[1] - bxy[1]) ** 2) ** 0.5)
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

    if not bool(current.get("is_middle", False)):
        status = "invalid_target_not_middle"
    elif avg_other_centroid_shift_pct > CENTROID_ABORT_SHIFT_PCT:
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
        self._manual_override_enabled: bool = False
        self._manual_target_block_id: int | None = None
        self._active_block_id: int | None = None
        self._baseline: dict | None = None
        self._last_status: str | None = None
        self._last_eval: dict | None = None
        self._last_print_time: float = 0.0

    def _target_block_id(self) -> int | None:
        """Placeholder probe trigger source. Replace with topic/service later."""
        if self._manual_override_enabled:
            return self._manual_target_block_id
        return PROBE_TARGET_BLOCK_ID_PLACEHOLDER

    def set_target_block_id(self, block_id: int | None) -> None:
        """Set active probe target from UI/runtime input."""
        self._manual_override_enabled = True
        self._manual_target_block_id = None if block_id is None else int(block_id)

    def _status_label(self, status: str | None) -> str:
        if status == "safe_to_remove":
            return "SAFE_TO_REMOVE"
        if status == "tower_shifting":
            return "ABORT_TOWER_MOVED"
        if status == "invalid_target_not_middle":
            return "ABORT_INVALID_TARGET_NOT_MIDDLE"
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

    def _print_final_decision(self) -> None:
        if self._active_block_id is None:
            return
        label = self._status_label(self._last_status)
        if label == "SAFE_TO_REMOVE":
            print(f"[probe] final block={self._active_block_id} decision=SAFE (safe to remove)")
            return
        if label.startswith("ABORT_"):
            print(f"[probe] final block={self._active_block_id} decision=ABORT ({label})")
            return
        print(f"[probe] final block={self._active_block_id} decision=INCONCLUSIVE ({label})")

    def update(
        self,
        tower_state: list[dict],
        frame_shape: tuple[int, int] | None = None,
    ) -> None:
        probe_target_block_id = self._target_block_id()
        if probe_target_block_id is None:
            if self._active_block_id is not None:
                self._print_final_decision()
            self._active_block_id = None
            self._baseline = None
            self._last_status = None
            self._last_eval = None
            return

        if not tower_state:
            return

        if self._active_block_id != int(probe_target_block_id):
            self._active_block_id = int(probe_target_block_id)
            self._baseline = _build_probe_snapshot(
                tower_state,
                block_id=self._active_block_id,
                frame_shape=frame_shape,
            )
            self._last_status = None
            self._last_eval = None
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
            block_id=self._active_block_id,
            frame_shape=frame_shape,
        )

        if self._baseline is None or current_snapshot is None:
            return

        eval_result = _assess_probe_response(self._baseline, current_snapshot)
        now = time.monotonic()
        should_print = (
            eval_result["status"] != self._last_status
            or (now - self._last_print_time) >= PROBE_PRINT_INTERVAL_S
        )
        if should_print:
            dx = eval_result.get("target_dx_px")
            dy = eval_result.get("target_dy_px")
            if dx is None or dy is None:
                movement_xy = "(n/a,n/a)"
            else:
                movement_xy = f"({dx:+.1f},{dy:+.1f})"
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
                # End monitoring immediately after tower-shift abort.
                ended_block = self._active_block_id
                self.set_target_block_id(None)
                self._active_block_id = None
                self._baseline = None
                self._last_status = None
                self._last_eval = None
                print(f"[probe] monitoring ended for block={ended_block} after ABORT")
                return
            elif label == "ABORT_INVALID_TARGET_NOT_MIDDLE":
                print(
                    f"[probe] decision block={self._active_block_id}: "
                    "ABORT (selected block is not a middle block)"
                )
        self._last_status = eval_result["status"]
        self._last_eval = eval_result
