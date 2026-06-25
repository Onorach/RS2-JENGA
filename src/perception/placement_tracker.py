"""
placement_tracker.py
--------------------
Detect blocks removed from the tower and find them again by alternating
searches: last known location, then the active top placement layer, repeat.

The active top layer is the first extrapolated layer above the highest
complete layer (3 blocks). Partial layers stay targeted until full.

Slot on the top layer is inferred from each colour blob's outer edge on the
end-on face (seam → outside): ~33% front, ~66% mid, ~100% back.
"""
from __future__ import annotations

import cv2
import numpy as np

from box_percentages import (
    _quad_mask,
    endon_outside_edge_x,
    compute_percentages,
)
from block_centroids import blob_area_at_xy, recover_colour_centroid
from colour_identification import frame_colour_mask
from layer_analysis import _count_extrapolated_layers
from perception_config import (
    CENTROID_HINT_SEARCH_RADIUS_PX,
    BLOCK_CENTROID_MIN_BLOB_PX,
    PLACEMENT_MIN_COLOUR_PX,
    BLOCK_MISSING_CONFIRM_FRAMES,
    PLACEMENT_OCCLUSION_MISSING_THRESHOLD,
    PLACEMENT_SLOT_FRONT_MAX_PCT,
    PLACEMENT_SLOT_MID_MAX_PCT,
)

SLOT_NAMES = ("front", "mid", "back")


def _format_cell_colour_pcts(bgr_frame: np.ndarray, cell: dict) -> str:
    """Summarise non-zero colour percentages in a grid cell."""
    results = compute_percentages(bgr_frame, [cell])
    if not results:
        return "no data"
    colours = results[0].get("colours", {})
    parts = [
        f"{name}={info['pct']:.1f}%"
        for name, info in sorted(colours.items())
        if name != "none" and float(info.get("pct", 0.0)) > 0.0
    ]
    none_pct = float(colours.get("none", {}).get("pct", 0.0))
    if none_pct > 0.0:
        parts.append(f"none={none_pct:.1f}%")
    return ", ".join(parts) if parts else "all zero"


def _dbg(msg: str) -> None:
    print(f"[placement-debug] {msg}")


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


def _present_blocks(tower: list[dict]) -> dict[int, dict]:
    """Map block_id → {colour, layer, slot} for every present block."""
    out: dict[int, dict] = {}
    for layer in tower:
        layer_idx = int(layer.get("layer", -1))
        for slot_idx, block in enumerate(layer.get("blocks", [])):
            if not block.get("present"):
                continue
            bid = block.get("block_index")
            if bid is None:
                continue
            colour = block.get("colour", "unknown")
            if colour in (None, "", "unknown"):
                continue
            out[int(bid)] = {
                "colour": str(colour),
                "layer": layer_idx,
                "slot": int(slot_idx),
                "mean_x_px": block.get("mean_x_px"),
                "mean_y_px": block.get("mean_y_px"),
            }
    return out


def _block_at_home(
    tower: list[dict],
    block_id: int,
    *,
    layer_idx: int,
    slot_idx: int,
    expected_colour: str | None = None,
) -> bool:
    """True when the block is present at its canonical home slot."""
    layer_data = next(
        (layer for layer in tower if int(layer.get("layer", -1)) == layer_idx),
        None,
    )
    if layer_data is None:
        return False
    blocks = layer_data.get("blocks", [])
    if slot_idx < 0 or slot_idx >= len(blocks):
        return False
    block = blocks[slot_idx]
    if not block.get("present"):
        return False
    bid = block.get("block_index")
    if bid is not None and int(bid) == int(block_id):
        return True
    colour = str(block.get("colour", ""))
    if (
        expected_colour
        and expected_colour not in ("unknown", "")
        and colour == str(expected_colour)
    ):
        return True
    return False


def _centre_seam_x_for_layer(
    row_cells: list[tuple[dict, dict]],
    layer_idx: int,
) -> float | None:
    n_layers = len(row_cells)
    if layer_idx < 0 or layer_idx >= n_layers:
        return None
    row_idx = (n_layers - 1) - layer_idx
    left_cell, _right_cell = row_cells[row_idx]
    return float(left_cell["corners"][1][0])


def _outer_edge_x_on_endon_face(
    xs_side: np.ndarray,
    orientation: str,
) -> float:
    """Outermost x among end-on-face pixels (toward the tower outside edge)."""
    if orientation == "left":
        return float(np.min(xs_side))
    return float(np.max(xs_side))


def _slot_threshold_label(penetration_pct: float) -> str:
    if penetration_pct < float(PLACEMENT_SLOT_FRONT_MAX_PCT):
        return (
            f"front (penetration {penetration_pct:.1f}% "
            f"< {PLACEMENT_SLOT_FRONT_MAX_PCT}%)"
        )
    if penetration_pct < float(PLACEMENT_SLOT_MID_MAX_PCT):
        return (
            f"mid (penetration {penetration_pct:.1f}% "
            f">= {PLACEMENT_SLOT_FRONT_MAX_PCT}% "
            f"and < {PLACEMENT_SLOT_MID_MAX_PCT}%)"
        )
    return (
        f"back (penetration {penetration_pct:.1f}% "
        f">= {PLACEMENT_SLOT_MID_MAX_PCT}%)"
    )


def _format_blob_slot_reason(
    *,
    orientation: str,
    centre_seam_x: float,
    outside_x: float,
    outer_x: float,
    mean_x: float,
    penetration_pct: float,
    slot_idx: int,
    endon_px: int,
    full_px: int,
) -> str:
    if orientation == "left":
        span = float(centre_seam_x - outside_x)
    else:
        span = float(outside_x - centre_seam_x)
    return (
        f"slot={SLOT_NAMES[slot_idx]} ({_slot_threshold_label(penetration_pct)}); "
        f"orient={orientation} seam_x={centre_seam_x:.1f} outside_x={outside_x:.1f} "
        f"span={span:.1f}px outer_x={outer_x:.1f} mean_x={mean_x:.1f} "
        f"endon_px={endon_px}/{full_px}"
    )


def measure_slot_from_outer_edge(
    outer_edge_x: float,
    centre_seam_x: float,
    outside_edge_x: float,
    orientation: str,
) -> tuple[int, float]:
    if orientation == "left":
        span = float(centre_seam_x - outside_edge_x)
        if span <= 1.0:
            return 1, 50.0
        penetration = (float(centre_seam_x - outer_edge_x) / span) * 100.0
    else:
        span = float(outside_edge_x - centre_seam_x)
        if span <= 1.0:
            return 1, 50.0
        penetration = (float(outer_edge_x - centre_seam_x) / span) * 100.0

    penetration = float(np.clip(penetration, 0.0, 100.0))
    if penetration < float(PLACEMENT_SLOT_FRONT_MAX_PCT):
        slot = 0
    elif penetration < float(PLACEMENT_SLOT_MID_MAX_PCT):
        slot = 1
    else:
        slot = 2
    return slot, penetration


def colour_blobs_in_layer(
    bgr_frame: np.ndarray,
    row_cells: list[tuple[dict, dict]],
    layer_idx: int,
    orientation: str,
    colour: str,
) -> list[dict]:
    """
    Find separate colour blobs on the end-on face and assign each to one slot.
    One physical block → one blob → one slot.
    """
    cell = _endon_cell_for_layer(row_cells, layer_idx, orientation)
    if cell is None:
        return []

    centre_seam_x = _centre_seam_x_for_layer(row_cells, layer_idx)
    outside_x = endon_outside_edge_x(cell, orientation)
    if centre_seam_x is None:
        return []

    ih, iw = bgr_frame.shape[:2]
    quad = _quad_mask((ih, iw), cell["corners"])
    mask = (quad & frame_colour_mask(bgr_frame, colour)).astype(np.uint8)
    if int(mask.sum()) < max(1, int(BLOCK_CENTROID_MIN_BLOB_PX)):
        return []

    n_labels, labels, stats, _centroids = cv2.connectedComponentsWithStats(
        mask, connectivity=8,
    )
    min_area = int(BLOCK_CENTROID_MIN_BLOB_PX)
    blobs: list[dict] = []

    for label in range(1, n_labels):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < min_area:
            continue
        component = labels == label
        ys, xs = np.where(component)
        if len(xs) == 0:
            continue
        endon_side = xs >= centre_seam_x if orientation == "right" else xs <= centre_seam_x
        xs_side = xs[endon_side]
        ys_side = ys[endon_side]
        full_px = int(len(xs))
        endon_px = int(len(xs_side))
        if endon_px < min_area:
            continue
        mean_x = float(np.mean(xs_side))
        mean_y = float(np.mean(ys_side))
        outer_x = _outer_edge_x_on_endon_face(xs_side, orientation)
        slot_idx, penetration_pct = measure_slot_from_outer_edge(
            outer_x, centre_seam_x, outside_x, orientation,
        )
        slot_reason = _format_blob_slot_reason(
            orientation=orientation,
            centre_seam_x=centre_seam_x,
            outside_x=outside_x,
            outer_x=outer_x,
            mean_x=mean_x,
            penetration_pct=penetration_pct,
            slot_idx=slot_idx,
            endon_px=endon_px,
            full_px=full_px,
        )
        blobs.append({
            "slot_idx": int(slot_idx),
            "slot_name": SLOT_NAMES[slot_idx],
            "penetration_pct": round(penetration_pct, 1),
            "mean_x_px": mean_x,
            "mean_y_px": mean_y,
            "outer_x_px": outer_x,
            "centre_seam_x": centre_seam_x,
            "outside_x": outside_x,
            "endon_px": endon_px,
            "full_px": full_px,
            "slot_reason": slot_reason,
            "blob_key": (int(round(mean_x / 8.0)), int(round(mean_y / 8.0))),
        })

    return blobs


def count_present_blocks_on_layer(layer_data: dict) -> int:
    """Count blocks visibly present on a layer (not absent canonical entries)."""
    return sum(
        1 for block in layer_data.get("blocks", [])
        if block.get("present")
    )


class PlacementTracker:
    """
    Watches for blocks disappearing from the tower. While a block is missing,
    alternate single-frame searches between its last known layer and the active
    top placement layer until it is found.
    """

    def __init__(self) -> None:
        self._configured: bool = False
        self._prev_initialized: bool = False
        self._last_known: dict[int, dict] = {}
        self._pending_removals: dict[int, dict] = {}
        self._missing_streak: dict[int, int] = {}
        self._extrapolated_layers: list[int] = []
        self._claimed_blob_keys: set[tuple[int, int, int]] = set()
        self._occlusion_hold: bool = False
        self._last_absent_count: int = 0

    def reset(self) -> None:
        self._configured = False
        self._prev_initialized = False
        self._last_known.clear()
        self._pending_removals.clear()
        self._missing_streak.clear()
        self._extrapolated_layers.clear()
        self._claimed_blob_keys.clear()
        self._occlusion_hold = False
        self._last_absent_count = 0

    def has_pending(self) -> bool:
        """True while at least one block is missing and being searched for."""
        return bool(self._pending_removals)

    def blocks_skip_restore(self) -> set[int]:
        """Block ids actively being searched after confirmed removal."""
        return set(self._pending_removals.keys())

    def note_absences(
        self,
        tower: list[dict],
        identity_tracker,
    ) -> None:
        """
        Update missing streaks after restore/apply, when canonical ids and
        recovered centroids are reflected in the tower state.
        """
        if not self._configured or not tower or not self._prev_initialized:
            return

        watched = self._watched_blocks(identity_tracker)
        effective = self._effective_present(tower, identity_tracker)
        extrap = set(self._extrapolated_layers)
        absent_ids: list[int] = []
        for block_id, info in watched.items():
            bid = int(block_id)
            eff = effective.get(bid)
            if eff is not None and int(eff["layer"]) in extrap:
                continue
            if self._absent_from_home(tower, bid, info):
                absent_ids.append(bid)
        self._last_absent_count = len(absent_ids)
        threshold = int(PLACEMENT_OCCLUSION_MISSING_THRESHOLD)

        if len(absent_ids) >= threshold:
            if not self._occlusion_hold:
                details = ", ".join(
                    f"{bid:03d}@L{watched[bid]['layer']}s{watched[bid]['slot']}"
                    for bid in absent_ids
                )
                _dbg(
                    f"occlusion: {len(absent_ids)} blocks absent ({details}) "
                    f"— pausing missing detection and clearing search state"
                )
            self._occlusion_hold = True
            self._missing_streak.clear()
            self._pending_removals.clear()
            return

        if self._occlusion_hold:
            _dbg(
                f"occlusion cleared ({len(absent_ids)} block(s) still absent)"
            )
            self._occlusion_hold = False

        for block_id, info in watched.items():
            bid = int(block_id)
            eff = effective.get(bid)
            if eff is not None and int(eff["layer"]) in extrap:
                self._missing_streak.pop(bid, None)
                continue
            if not self._absent_from_home(tower, bid, info):
                self._missing_streak.pop(bid, None)
            elif bid not in self._pending_removals:
                streak = int(self._missing_streak.get(bid, 0)) + 1
                self._missing_streak[bid] = streak
                self._note_block_absent(bid, info, streak=streak)

    def _clear_block_from_tower_below(
        self,
        tower: list[dict],
        block_id: int,
    ) -> None:
        """Remove stale same-frame presence on non-extrapolated layers."""
        extrap = set(self._extrapolated_layers)
        bid = int(block_id)
        for layer in tower:
            layer_idx = int(layer.get("layer", -1))
            if layer_idx in extrap:
                continue
            for block in layer.get("blocks", []):
                if not block.get("present"):
                    continue
                present_id = block.get("block_index")
                if present_id is not None and int(present_id) == bid:
                    block["present"] = False
                    block.pop("block_index", None)
                    block.pop("id", None)
                    block["colour"] = "unknown"

    def extrapolated_layers(self) -> list[int]:
        return list(self._extrapolated_layers)

    def configure_layers(self, row_cells: list[list[dict]]) -> None:
        extra = _count_extrapolated_layers(row_cells)
        n_layers = len(row_cells)
        self._prev_initialized = False
        self._last_known.clear()
        self._pending_removals.clear()
        self._missing_streak.clear()
        self._claimed_blob_keys.clear()
        self._occlusion_hold = False
        self._last_absent_count = 0
        if extra <= 0:
            self._extrapolated_layers = []
            self._configured = False
            return
        base = n_layers - extra
        self._extrapolated_layers = list(range(base, n_layers))
        self._configured = True
        _dbg(
            f"configured: {n_layers} grid layers, extrapolated="
            f"{self._extrapolated_layers} (base={base})"
        )

    def _effective_present(
        self,
        tower: list[dict],
        identity_tracker,
    ) -> dict[int, dict]:
        present = _present_blocks(tower)
        for block_id, info in identity_tracker.registered_blocks_on_layers(
            self._extrapolated_layers,
        ).items():
            if block_id not in present:
                present[block_id] = dict(info)
        return present

    def _watched_blocks(self, identity_tracker) -> dict[int, dict]:
        """Canonical tower blocks whose home is not on extrapolated layers."""
        watched = identity_tracker.canonical_blocks_excluding_layers(
            set(self._extrapolated_layers),
        )
        for block_id in identity_tracker.registered_blocks_on_layers(
            self._extrapolated_layers,
        ):
            watched.pop(int(block_id), None)
        for block_id, info in watched.items():
            last = self._last_known.get(block_id)
            if last is None:
                continue
            merged = dict(info)
            if last.get("mean_x_px") is not None:
                merged["mean_x_px"] = last["mean_x_px"]
            if last.get("mean_y_px") is not None:
                merged["mean_y_px"] = last["mean_y_px"]
            watched[block_id] = merged
        return watched

    def _absent_from_home(
        self,
        tower: list[dict],
        block_id: int,
        info: dict,
    ) -> bool:
        return not _block_at_home(
            tower,
            block_id,
            layer_idx=int(info["layer"]),
            slot_idx=int(info["slot"]),
            expected_colour=str(info.get("colour", "")),
        )

    def _note_block_absent(
        self,
        block_id: int,
        info: dict,
        *,
        streak: int,
    ) -> None:
        confirm = int(BLOCK_MISSING_CONFIRM_FRAMES)
        if streak == confirm:
            _dbg(
                f"block {block_id:03d} ({info['colour']}) missing at "
                f"L{info['layer']} slot {info['slot']} "
                f"streak={streak}/{confirm}"
            )

    def _placement_target_layer(
        self,
        tower: list[dict],
        _identity_tracker=None,
    ) -> int | None:
        """
        Layer above the highest complete (3 present blocks) layer that still
        has fewer than 3 visible blocks. Works on any grid row — detected or
        extrapolated — so L6 is searched when L5 is the highest full layer.
        """
        if not tower:
            return None

        layer_by_idx = {int(layer.get("layer", -1)): layer for layer in tower}
        if not layer_by_idx:
            return None

        max_layer = max(layer_by_idx.keys())
        highest_complete: int | None = None
        for layer_idx in sorted(layer_by_idx.keys()):
            if count_present_blocks_on_layer(layer_by_idx[layer_idx]) >= 3:
                highest_complete = layer_idx

        if highest_complete is None:
            for layer_idx in sorted(layer_by_idx.keys()):
                if count_present_blocks_on_layer(layer_by_idx[layer_idx]) < 3:
                    return layer_idx
            return max_layer

        target = highest_complete + 1
        while target <= max_layer:
            layer_data = layer_by_idx[target]
            if count_present_blocks_on_layer(layer_data) < 3:
                return target
            highest_complete = target
            target += 1
        return target

    def _pending_info(self, pending: dict) -> dict:
        return {
            "colour": str(pending["colour"]),
            "layer": int(pending.get("from_layer", pending.get("layer", -1))),
            "slot": int(pending.get("from_slot", pending.get("slot", -1))),
            "mean_x_px": pending.get("mean_x_px"),
            "mean_y_px": pending.get("mean_y_px"),
        }

    def update(
        self,
        bgr_frame: np.ndarray,
        tower: list[dict],
        row_cells: list[tuple[dict, dict]],
        identity_tracker,
        depth_frame: np.ndarray | None = None,
    ) -> bool:
        if not self._configured or not tower:
            return False

        self._claimed_blob_keys.clear()
        current = self._effective_present(tower, identity_tracker)
        if not self._prev_initialized:
            self._last_known = {
                int(block_id): dict(info)
                for block_id, info in current.items()
            }
            self._prev_initialized = True
            return False

        for block_id, info in current.items():
            self._last_known[int(block_id)] = dict(info)

        changed = False

        for block_id in list(self._pending_removals.keys()):
            pending = self._pending_removals[block_id]
            home = {
                "layer": int(pending["from_layer"]),
                "slot": int(pending["from_slot"]),
            }
            if self._absent_from_home(tower, block_id, home):
                continue
            self._pending_removals.pop(block_id)
            print(
                f"[placement] block {block_id:03d} ({pending['colour']}) "
                f"back at home L{home['layer']} — search cancelled"
            )
            self._missing_streak.pop(block_id, None)
            changed = True

        if self._occlusion_hold:
            return changed

        new_missing: list[tuple[int, dict]] = []
        watched = self._watched_blocks(identity_tracker)

        for block_id, info in watched.items():
            if not self._absent_from_home(tower, block_id, info):
                continue
            if block_id in self._pending_removals:
                continue

            streak = int(self._missing_streak.get(block_id, 0))
            if streak < int(BLOCK_MISSING_CONFIRM_FRAMES):
                continue

            pending_info = dict(info)
            pending_info["from_layer"] = int(info["layer"])
            pending_info["from_slot"] = int(info["slot"])
            new_missing.append((int(block_id), pending_info))

        will_search = bool(self._pending_removals) or bool(new_missing)
        target_layer = (
            self._placement_target_layer(tower, identity_tracker)
            if will_search
            else None
        )

        for block_id, info in new_missing:
            if block_id in self._pending_removals:
                continue
            hint = identity_tracker.last_centroid_for_block(block_id)
            self._pending_removals[block_id] = {
                "block_id": block_id,
                "colour": str(info["colour"]),
                "from_layer": int(info["from_layer"]),
                "from_slot": int(info["from_slot"]),
                "mean_x_px": info.get("mean_x_px") or (hint[0] if hint else None),
                "mean_y_px": info.get("mean_y_px") or (hint[1] if hint else None),
                "search_phase": 0,
            }
            self._missing_streak.pop(block_id, None)
            layer_label = (
                f"L{target_layer}" if target_layer is not None else "top"
            )
            print(
                f"[placement] block {block_id:03d} ({info['colour']}) missing "
                f"from L{info['from_layer']} — alternating search "
                f"L{info['from_layer']} ↔ {layer_label}"
            )

        for block_id in list(self._pending_removals.keys()):
            pending = self._pending_removals[block_id]
            result = self._search_missing_block(
                bgr_frame,
                depth_frame,
                tower,
                row_cells,
                identity_tracker,
                target_layer=target_layer,
                block_id=int(block_id),
                pending=pending,
            )
            if result is None:
                continue
            del self._pending_removals[block_id]
            self._missing_streak.pop(block_id, None)
            changed = True

        return changed

    def _endon_pcts_for_layer(
        self,
        bgr_frame: np.ndarray,
        row_cells: list[tuple[dict, dict]],
        tower: list[dict],
        layer_idx: int,
    ) -> str:
        layer_data = next(
            (layer for layer in tower if int(layer.get("layer", -1)) == layer_idx),
            None,
        )
        if layer_data is None:
            return "no tower data"
        orientation = str(layer_data.get("orientation", ""))
        if orientation not in ("left", "right"):
            return f"orientation={orientation!r}"
        cell = _endon_cell_for_layer(row_cells, layer_idx, orientation)
        if cell is None:
            return "no end-on cell"
        return _format_cell_colour_pcts(bgr_frame, cell)

    def _search_missing_block(
        self,
        bgr_frame: np.ndarray,
        depth_frame: np.ndarray | None,
        tower: list[dict],
        row_cells: list[tuple[dict, dict]],
        identity_tracker,
        *,
        target_layer: int | None,
        block_id: int,
        pending: dict,
    ) -> str | None:
        info = self._pending_info(pending)
        colour = str(info["colour"])
        from_layer = int(info["layer"])
        phase = int(pending.get("search_phase", 0))

        if phase == 0:
            pcts = self._endon_pcts_for_layer(
                bgr_frame, row_cells, tower, from_layer,
            )
            fail_reason = self._try_recover_at_last_location(
                bgr_frame,
                depth_frame,
                tower,
                row_cells,
                identity_tracker,
                block_id=block_id,
                info=info,
                hint_only=True,
            )
            if fail_reason is None:
                _dbg(
                    f"block {block_id:03d} ({colour}): last-location "
                    f"L{from_layer} → FOUND [{pcts}]"
                )
                return "recovered"
            _dbg(
                f"block {block_id:03d} ({colour}): last-location "
                f"L{from_layer} → not found ({fail_reason}) [{pcts}]"
            )
            pending["search_phase"] = 1
            return None

        if target_layer is None:
            _dbg(
                f"block {block_id:03d} ({colour}): target layer → "
                f"skipped (no layer above complete tower)"
            )
            pending["search_phase"] = 0
            return None

        pcts = self._endon_pcts_for_layer(
            bgr_frame, row_cells, tower, int(target_layer),
        )
        extrap = int(target_layer) in self._extrapolated_layers
        layer_tag = (
            f"L{target_layer} (extrapolated)"
            if extrap
            else f"L{target_layer}"
        )
        top_hit, fail_reason = self._detect_on_target_layer(
            bgr_frame,
            row_cells,
            tower,
            identity_tracker,
            target_layer=target_layer,
            block_id=block_id,
            colour=colour,
            pending=pending,
        )
        if top_hit is not None:
            layer_idx, detection = top_hit
            _dbg(
                f"block {block_id:03d} ({colour}): target {layer_tag} "
                f"→ FOUND {detection['slot_name']} "
                f"({detection['penetration_pct']:.1f}%) [{pcts}]"
            )
            _dbg(
                f"block {block_id:03d}: placement reason → "
                f"{detection.get('slot_reason', 'no detail')}"
            )
            if detection.get("selection_reason"):
                _dbg(
                    f"block {block_id:03d}: blob chosen because "
                    f"{detection['selection_reason']}"
                )
            self._apply_top_layer_placement(
                tower,
                identity_tracker,
                block_id=block_id,
                colour=colour,
                layer_idx=layer_idx,
                detection=detection,
            )
            return "placed"
        _dbg(
            f"block {block_id:03d} ({colour}): target {layer_tag} "
            f"→ not found ({fail_reason}) [{pcts}]"
        )
        pending["search_phase"] = 0
        return None

    def _try_recover_at_last_location(
        self,
        bgr_frame: np.ndarray,
        depth_frame: np.ndarray | None,
        tower: list[dict],
        row_cells: list[tuple[dict, dict]],
        identity_tracker,
        *,
        block_id: int,
        info: dict,
        hint_only: bool = False,
    ) -> str | None:
        """
        Try to recover the block at its last known layer.

        Returns None on success (tower patched), else a short failure reason.
        """
        layer_idx = int(info["layer"])
        slot_idx = int(info["slot"])
        colour = str(info["colour"])
        if layer_idx in self._extrapolated_layers:
            return "from layer is extrapolated"

        layer_data = next(
            (layer for layer in tower if int(layer.get("layer", -1)) == layer_idx),
            None,
        )
        if layer_data is None:
            return "no tower data"

        orientation = str(layer_data.get("orientation", ""))
        if orientation not in ("left", "right"):
            return f"orientation={orientation!r}"

        n_layers = len(row_cells)
        row_idx = (n_layers - 1) - layer_idx
        if row_idx < 0 or row_idx >= n_layers:
            return "layer out of grid"
        left_cell, right_cell = row_cells[row_idx]

        hint_x = info.get("mean_x_px")
        hint_y = info.get("mean_y_px")
        if hint_x is None or hint_y is None:
            hint = identity_tracker.last_centroid_for_block(block_id)
            if hint is not None:
                hint_x, hint_y = hint
        hint_xy = None
        if hint_x is not None and hint_y is not None:
            hint_xy = (float(hint_x), float(hint_y))

        centroid = recover_colour_centroid(
            bgr_frame,
            depth_frame,
            left_cell,
            right_cell,
            orientation,
            colour,
            hint_xy=hint_xy,
            radius_px=float(CENTROID_HINT_SEARCH_RADIUS_PX),
            hint_only=hint_only,
        )
        if centroid is None:
            return (
                f"no {colour} within {CENTROID_HINT_SEARCH_RADIUS_PX}px of hint"
            )

        endon_cell = left_cell if orientation == "left" else right_cell
        blob_area = blob_area_at_xy(
            bgr_frame,
            endon_cell,
            colour,
            float(centroid[0]),
            float(centroid[1]),
        )
        if blob_area < int(BLOCK_CENTROID_MIN_BLOB_PX):
            return (
                f"blob area {blob_area} < min {BLOCK_CENTROID_MIN_BLOB_PX}"
            )

        blocks = layer_data.setdefault("blocks", [{}, {}, {}])
        while len(blocks) <= slot_idx:
            blocks.append({"colour": "unknown", "present": False})

        block = blocks[slot_idx]
        block["colour"] = colour
        block["present"] = True
        block["block_index"] = int(block_id)
        block["id"] = f"{int(block_id):03d}"
        block["mean_x_px"] = float(centroid[0])
        block["mean_y_px"] = float(centroid[1])
        info["mean_x_px"] = block["mean_x_px"]
        info["mean_y_px"] = block["mean_y_px"]
        print(
            f"[placement] recovered block {block_id:03d} ({colour}) at last "
            f"location L{layer_idx}"
        )
        return None

    def _occupied_slots_on_layer(
        self,
        tower: list[dict],
        layer_idx: int,
        block_id: int | None = None,
    ) -> set[int]:
        layer_data = next(
            (layer for layer in tower if int(layer.get("layer", -1)) == layer_idx),
            None,
        )
        occupied: set[int] = set()
        if layer_data is None:
            return occupied
        for slot_idx, block in enumerate(layer_data.get("blocks", [])):
            if not block.get("present"):
                continue
            bid = block.get("block_index")
            if block_id is not None and bid is not None and int(bid) == int(block_id):
                continue
            occupied.add(int(slot_idx))
        return occupied

    def _colour_mask_stats_in_layer(
        self,
        bgr_frame: np.ndarray,
        row_cells: list[tuple[dict, dict]],
        layer_idx: int,
        orientation: str,
        colour: str,
    ) -> dict:
        cell = _endon_cell_for_layer(row_cells, layer_idx, orientation)
        if cell is None:
            return {"error": "no cell"}
        ih, iw = bgr_frame.shape[:2]
        quad = _quad_mask((ih, iw), cell["corners"])
        mask = (quad & frame_colour_mask(bgr_frame, colour)).astype(np.uint8)
        total_px = int(mask.sum())
        n_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(
            mask, connectivity=8,
        )
        min_area = int(BLOCK_CENTROID_MIN_BLOB_PX)
        components = []
        for label in range(1, n_labels):
            area = int(stats[label, cv2.CC_STAT_AREA])
            components.append({
                "area": area,
                "accepted": area >= min_area,
            })
        return {
            "total_px": total_px,
            "min_blob_px": min_area,
            "components": components,
        }

    def _detect_on_target_layer(
        self,
        bgr_frame: np.ndarray,
        row_cells: list[tuple[dict, dict]],
        tower: list[dict],
        identity_tracker,
        *,
        target_layer: int,
        block_id: int,
        colour: str,
        pending: dict,
    ) -> tuple[tuple[int, dict] | None, str]:
        layer_data = next(
            (
                layer for layer in tower
                if int(layer.get("layer", -1)) == int(target_layer)
            ),
            None,
        )
        if layer_data is None:
            return None, "layer not in tower state"

        orientation = str(layer_data.get("orientation", ""))
        if orientation not in ("left", "right"):
            return None, f"orientation={orientation!r}"

        blobs = colour_blobs_in_layer(
            bgr_frame, row_cells, int(target_layer), orientation, colour,
        )
        if not blobs:
            mask_stats = self._colour_mask_stats_in_layer(
                bgr_frame, row_cells, int(target_layer), orientation, colour,
            )
            return None, (
                f"no accepted {colour} blobs "
                f"(mask_px={mask_stats.get('total_px')}, "
                f"components={mask_stats.get('components')})"
            )

        _dbg(
            f"block {block_id:03d} ({colour}): L{target_layer} "
            f"orientation={orientation} — {len(blobs)} blob(s):"
        )
        for i, blob in enumerate(blobs):
            _dbg(f"  blob[{i}] {blob.get('slot_reason', blob)}")

        occupied = self._occupied_slots_on_layer(
            tower, int(target_layer), block_id=block_id,
        )
        if occupied:
            _dbg(
                f"block {block_id:03d}: occupied slots on L{target_layer} "
                f"= {sorted(occupied)}"
            )

        hint_x = pending.get("mean_x_px")
        hint_y = pending.get("mean_y_px")

        candidates: list[tuple[float, dict]] = []
        for blob in blobs:
            slot_idx = int(blob["slot_idx"])
            blob_key = (int(target_layer),) + tuple(blob["blob_key"])
            if slot_idx in occupied:
                _dbg(
                    f"  blob slot {blob['slot_name']} rejected: "
                    f"slot {slot_idx} occupied"
                )
                continue
            if blob_key in self._claimed_blob_keys:
                _dbg(
                    f"  blob slot {blob['slot_name']} rejected: "
                    f"blob_key {blob_key} already claimed"
                )
                continue
            if hint_x is not None and hint_y is not None:
                dist = float(np.hypot(
                    float(blob["mean_x_px"]) - float(hint_x),
                    float(blob["mean_y_px"]) - float(hint_y),
                ))
            else:
                dist = 0.0
            candidates.append((dist, blob))

        if not candidates:
            return None, f"all {len(blobs)} blob(s) rejected (occupied/claimed)"

        candidates.sort(key=lambda item: item[0])
        dist, blob = candidates[0]
        if hint_x is not None and hint_y is not None:
            blob = dict(blob)
            blob["selection_reason"] = (
                f"nearest to last hint ({hint_x:.1f}, {hint_y:.1f}), "
                f"dist={dist:.1f}px (of {len(candidates)} candidate(s))"
            )
        else:
            blob = dict(blob)
            blob["selection_reason"] = (
                f"first unoccupied unclaimed blob "
                f"(of {len(candidates)} candidate(s), no hint)"
            )
        if len(candidates) > 1:
            others = ", ".join(
                f"{item[1]['slot_name']}@{item[0]:.0f}px"
                for item in candidates[1:]
            )
            blob["selection_reason"] += f"; other candidates: {others}"
        blob_key = (int(target_layer),) + tuple(blob["blob_key"])
        self._claimed_blob_keys.add(blob_key)
        return (int(target_layer), blob), "ok"

    def _apply_top_layer_placement(
        self,
        tower: list[dict],
        identity_tracker,
        *,
        block_id: int,
        colour: str,
        layer_idx: int,
        detection: dict,
    ) -> None:
        slot_idx = int(detection["slot_idx"])
        identity_tracker.mark_block_removed(block_id)
        identity_tracker.register_placed_block(
            layer_idx, slot_idx, block_id, colour,
        )
        self._clear_block_from_tower_below(tower, block_id)

        layer_data = next(
            (layer for layer in tower if int(layer.get("layer", -1)) == layer_idx),
            None,
        )
        if layer_data is None:
            return

        blocks = layer_data.setdefault("blocks", [{}, {}, {}])
        while len(blocks) < 3:
            blocks.append({"colour": "unknown", "present": False})

        block = blocks[slot_idx]
        block["colour"] = colour
        block["present"] = True
        block["block_index"] = block_id
        block["id"] = f"{block_id:03d}"
        if detection.get("mean_x_px") is not None:
            block["mean_x_px"] = float(detection["mean_x_px"])
        if detection.get("mean_y_px") is not None:
            block["mean_y_px"] = float(detection["mean_y_px"])
        block["placement_penetration_pct"] = detection["penetration_pct"]

        print(
            f"[placement] registered block {block_id:03d} ({colour}) on "
            f"L{layer_idx} {detection['slot_name']} "
            f"({detection['penetration_pct']:.1f}% seam→outside)"
        )
        print(
            f"[placement] slot decision: "
            f"{detection.get('slot_reason', 'no detail')}"
        )
        if detection.get("selection_reason"):
            print(
                f"[placement] blob selection: {detection['selection_reason']}"
            )
