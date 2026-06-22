"""
block_identity_tracker.py
-------------------------
Persistent ID assignment so block identities follow physical blocks across frames.

Design
------
Block identities are established on the FIRST frame after the grid locks and
are then FROZEN for the rest of the game.  Every subsequent frame re-uses the
canonical (layer_idx, slot_idx) → (block_id, colour) mapping instead of
re-detecting from colour percentages and x-lane positions.

This prevents identity flips caused by:
  - A pushed block whose colour coverage temporarily drops below the detection
    threshold.
  - Two blocks of similar colour swapping centroid proximity.

The only legitimate identity change is block REMOVAL: when the robot picks a
block its slot is marked empty via mark_block_removed() and the canonical
entry for that slot is deleted so the slot is not filled again.

Public API
----------
  tracker.apply(tower_state)                  — assign / freeze IDs each frame
  tracker.canonical_colours_for_layer(idx)   — [front_colour, mid_colour, back_colour]
  tracker.is_initialized()                   — True after first apply()
  tracker.mark_block_removed(block_id)       — call when a block is picked out
  tracker.register_placed_block(...)         — register block on extrapolated layer
  tracker.reset()                             — clear all state (grid reset)
"""
from __future__ import annotations

import math


class BlockIdentityTracker:
    def __init__(self, max_match_px: float = 80.0, max_misses: int = 60) -> None:
        self._max_match_px = float(max_match_px)
        self._max_misses   = int(max_misses)
        self._tracks: dict[int, dict] = {}
        self._next_id: int = 0
        self._initialized  = False
        # Canonical structure: frozen after first apply.
        # Keys: (layer_idx, slot_idx); values: {"block_id": int, "colour": str}
        self._canonical_slots: dict[tuple[int, int], dict] = {}
        # Block IDs that have been explicitly removed (picked by robot).
        self._removed_block_ids: set[int] = set()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        self._tracks.clear()
        self._next_id = 0
        self._initialized = False
        self._canonical_slots.clear()
        self._removed_block_ids.clear()

    def is_initialized(self) -> bool:
        return self._initialized

    def canonical_colours_for_layer(self, layer_idx: int) -> list[str | None]:
        """
        Return [front_colour, mid_colour, back_colour] (slot_idx order) for a
        layer from the frozen canonical structure.  Slots that were never seen
        or whose block has been removed return None.
        """
        result: list[str | None] = [None, None, None]
        for slot_idx in range(3):
            entry = self._canonical_slots.get((layer_idx, slot_idx))
            if entry is None:
                continue
            if entry["block_id"] in self._removed_block_ids:
                continue
            result[slot_idx] = entry["colour"]
        return result

    def mark_block_removed(self, block_id: int) -> None:
        """
        Mark a block as permanently removed (picked by the robot).
        Its canonical slot is cleared so it is never re-populated.
        """
        bid = int(block_id)
        self._removed_block_ids.add(bid)
        # Delete the canonical slot entry so the slot shows as empty.
        stale = [k for k, v in self._canonical_slots.items() if v["block_id"] == bid]
        for k in stale:
            del self._canonical_slots[k]
        # Remove from live tracks too.
        self._tracks.pop(bid, None)

    def register_placed_block(
        self,
        layer_idx: int,
        slot_idx: int,
        block_id: int,
        colour: str,
    ) -> None:
        """
        Register a block the robot placed on an extrapolated top layer.

        Re-uses the picked block's id on the new (layer_idx, slot_idx).
        """
        bid = int(block_id)
        self._removed_block_ids.discard(bid)
        self._canonical_slots[(int(layer_idx), int(slot_idx))] = {
            "block_id": bid,
            "colour":   str(colour),
        }
        if not self._initialized:
            self._initialized = True
        self._next_id = max(int(self._next_id), bid + 1)

    def registered_blocks_on_layers(
        self, layer_indices: list[int],
    ) -> dict[int, dict]:
        """
        Canonical block_id → {colour, layer, slot} for slots on the given layers.
        """
        allowed = {int(layer_idx) for layer_idx in layer_indices}
        out: dict[int, dict] = {}
        for (layer_idx, slot_idx), entry in self._canonical_slots.items():
            if int(layer_idx) not in allowed:
                continue
            bid = int(entry["block_id"])
            if bid in self._removed_block_ids:
                continue
            out[bid] = {
                "colour": str(entry["colour"]),
                "layer": int(layer_idx),
                "slot": int(slot_idx),
            }
        return out

    def canonical_blocks_excluding_layers(
        self,
        exclude_layer_indices: set[int],
    ) -> dict[int, dict]:
        """
        Canonical home blocks on all layers except the excluded set (typically
        extrapolated top bands). Includes last-known centroid when tracked.
        """
        exclude = {int(layer_idx) for layer_idx in exclude_layer_indices}
        out: dict[int, dict] = {}
        for (layer_idx, slot_idx), entry in self._canonical_slots.items():
            if int(layer_idx) in exclude:
                continue
            bid = int(entry["block_id"])
            if bid in self._removed_block_ids:
                continue
            hint = self.last_centroid_for_block(bid)
            out[bid] = {
                "colour": str(entry["colour"]),
                "layer": int(layer_idx),
                "slot": int(slot_idx),
                "mean_x_px": hint[0] if hint is not None else None,
                "mean_y_px": hint[1] if hint is not None else None,
            }
        return out

    def block_id_at_slot(self, layer_idx: int, slot_idx: int) -> int | None:
        entry = self._canonical_slots.get((int(layer_idx), int(slot_idx)))
        if entry is None:
            return None
        bid = int(entry["block_id"])
        if bid in self._removed_block_ids:
            return None
        return bid

    def centroid_hints_for_layer(
        self, layer_idx: int,
    ) -> dict[str, tuple[float, float]]:
        """
        Last-known (x, y) centroid per canonical colour on this layer.
        Used to anchor local colour searches when a block briefly drops out.
        """
        hints: dict[str, tuple[float, float]] = {}
        for slot_idx in range(3):
            entry = self._canonical_slots.get((int(layer_idx), slot_idx))
            if entry is None:
                continue
            bid = int(entry["block_id"])
            if bid in self._removed_block_ids:
                continue
            track = self._tracks.get(bid)
            if track is None:
                continue
            hints[str(entry["colour"])] = (
                float(track["x"]),
                float(track["y"]),
            )
        return hints

    def last_centroid_for_block(self, block_id: int) -> tuple[float, float] | None:
        track = self._tracks.get(int(block_id))
        if track is None:
            return None
        return float(track["x"]), float(track["y"])

    def restore_absent_canonical_centroids(
        self,
        bgr_frame,
        depth_frame,
        row_cells: list[tuple[dict, dict]],
        tower: list[dict],
        skip_layer_indices: set[int],
        skip_block_ids: set[int] | None = None,
    ) -> bool:
        """
        Re-find canonical blocks that analyse_tower marked absent using their
        last known centroid as a search hint.
        """
        from block_centroids import recover_colour_centroid
        from perception_config import CENTROID_HINT_SEARCH_RADIUS_PX

        changed = False
        n_layers = len(row_cells)
        skip_blocks = skip_block_ids or set()
        for layer in tower:
            layer_idx = int(layer.get("layer", -1))
            if layer_idx in skip_layer_indices:
                continue
            orientation = str(layer.get("orientation", ""))
            if orientation not in ("left", "right"):
                continue
            row_idx = (n_layers - 1) - layer_idx
            if row_idx < 0 or row_idx >= n_layers:
                continue
            left_cell, right_cell = row_cells[row_idx]
            for slot_idx, block in enumerate(layer.get("blocks", [])):
                if block.get("present"):
                    continue
                entry = self._canonical_slots.get((layer_idx, slot_idx))
                if entry is None:
                    continue
                bid = int(entry["block_id"])
                if bid in self._removed_block_ids:
                    continue
                if bid in skip_blocks:
                    continue
                colour = str(entry["colour"])
                hint = self.last_centroid_for_block(bid)
                centroid = recover_colour_centroid(
                    bgr_frame,
                    depth_frame,
                    left_cell,
                    right_cell,
                    orientation,
                    colour,
                    hint_xy=hint,
                    radius_px=float(CENTROID_HINT_SEARCH_RADIUS_PX),
                )
                if centroid is None:
                    continue
                block["colour"] = colour
                block["present"] = True
                block["block_index"] = bid
                block["id"] = f"{bid:03d}"
                block["mean_x_px"] = float(centroid[0])
                block["mean_y_px"] = float(centroid[1])
                self._tracks[bid] = {
                    "x": float(centroid[0]),
                    "y": float(centroid[1]),
                    "colour": colour,
                    "misses": 0,
                }
                changed = True
        return changed

    def colour_for_block(self, block_id: int) -> str | None:
        """Return last known canonical colour for a block id, if any."""
        bid = int(block_id)
        for entry in self._canonical_slots.values():
            if int(entry["block_id"]) == bid:
                return str(entry["colour"])
        track = self._tracks.get(bid)
        if track is not None:
            return str(track.get("colour"))
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _present_detections(self, tower_state: list[dict]) -> list[dict]:
        """Collect all present blocks with their image-space centroid."""
        detections: list[dict] = []
        for layer in tower_state:
            layer_idx = int(layer.get("layer", -1))
            for slot_idx, block in enumerate(layer.get("blocks", [])):
                if not block.get("present"):
                    continue
                mx = block.get("mean_x_px")
                my = block.get("mean_y_px")
                if mx is None or my is None:
                    continue
                detections.append({
                    "block":     block,
                    "layer_idx": layer_idx,
                    "slot_idx":  slot_idx,
                    "x":         float(mx),
                    "y":         float(my),
                    "colour":    str(block.get("colour", "unknown")),
                })
        return detections

    def _clear_ids(self, tower_state: list[dict]) -> None:
        for layer in tower_state:
            for block in layer.get("blocks", []):
                block["block_index"] = None
                block["id"] = None

    def _initialize_from_existing(self, tower_state: list[dict]) -> None:
        """Seed tracks from any block_index values already in the tower state."""
        self._tracks.clear()
        detections = self._present_detections(tower_state)
        max_existing = -1
        for det in detections:
            block = det["block"]
            existing_id = block.get("block_index")
            if existing_id is None:
                continue
            try:
                bid = int(existing_id)
            except (TypeError, ValueError):
                continue
            self._tracks[bid] = {
                "x":      det["x"],
                "y":      det["y"],
                "colour": det["colour"],
                "misses": 0,
            }
            block["block_index"] = bid
            block["id"] = f"{bid:03d}"
            max_existing = max(max_existing, bid)
        self._next_id = max_existing + 1 if max_existing >= 0 else 0
        self._initialized = True

    def _update_canonical_slots(self, tower_state: list[dict]) -> None:
        """
        Record first-seen slot assignments as canonical.
        First-write-wins — slots already in _canonical_slots are never
        overwritten so identities stay frozen.
        """
        for layer in tower_state:
            layer_idx = int(layer.get("layer", -1))
            for slot_idx, block in enumerate(layer.get("blocks", [])):
                key = (layer_idx, slot_idx)
                if key in self._canonical_slots:
                    continue  # Already frozen — never overwrite.
                block_id = block.get("block_index")
                colour   = block.get("colour", "unknown")
                if (
                    block_id is not None
                    and block.get("present")
                    and colour not in ("unknown", None, "")
                    and int(block_id) not in self._removed_block_ids
                ):
                    self._canonical_slots[key] = {
                        "block_id": int(block_id),
                        "colour":   str(colour),
                    }

    def _enforce_canonical(self, tower_state: list[dict]) -> None:
        """
        After normal ID assignment, re-impose the frozen canonical structure.

        For every slot that has a canonical entry:
          - The block at that slot gets the canonical block_id and colour,
            regardless of what colour was detected this frame.  This prevents
            identity flips caused by low colour coverage or centroid drift.
          - If the slot is currently absent (block not detected) but the
            canonical block has NOT been removed, the slot is left absent —
            we do not manufacture presence, but we do not flip the identity
            of adjacent blocks.
        """
        for layer in tower_state:
            layer_idx = int(layer.get("layer", -1))
            for slot_idx, block in enumerate(layer.get("blocks", [])):
                key = (layer_idx, slot_idx)
                entry = self._canonical_slots.get(key)
                if entry is None:
                    continue
                if entry["block_id"] in self._removed_block_ids:
                    continue
                if not block.get("present"):
                    # Block not detected this frame — leave absent but keep
                    # colour label so downstream callers can still name it.
                    block["colour"] = entry["colour"]
                    continue
                # Block is present: lock in the canonical identity.
                bid = entry["block_id"]
                block["block_index"] = bid
                block["id"]          = f"{bid:03d}"
                block["colour"]      = entry["colour"]
                # Keep the live track position up to date.
                mx = block.get("mean_x_px")
                my = block.get("mean_y_px")
                if mx is not None and my is not None:
                    self._tracks[bid] = {
                        "x":      float(mx),
                        "y":      float(my),
                        "colour": entry["colour"],
                        "misses": 0,
                    }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def apply(self, tower_state: list[dict]) -> None:
        if not tower_state:
            return

        if not self._initialized:
            self._initialize_from_existing(tower_state)
            # Seed canonical from the very first frame's assignments.
            self._update_canonical_slots(tower_state)
            return

        # ── Normal frame: greedy proximity + colour matching ───────────────
        self._clear_ids(tower_state)
        detections = self._present_detections(tower_state)

        assigned_det: set[int]   = set()
        assigned_track: set[int] = set()
        assignments: list[tuple[int, int]] = []

        def greedy_assign(colour_strict: bool, max_dist_px: float) -> None:
            candidates: list[tuple[float, int, int]] = []
            for di, det in enumerate(detections):
                if di in assigned_det:
                    continue
                for track_id, track in self._tracks.items():
                    if track_id in assigned_track:
                        continue
                    if colour_strict and track.get("colour") != det["colour"]:
                        continue
                    dist = math.hypot(
                        det["x"] - float(track["x"]),
                        det["y"] - float(track["y"]),
                    )
                    if dist <= max_dist_px:
                        candidates.append((dist, di, track_id))
            candidates.sort(key=lambda item: item[0])
            for _dist, di, track_id in candidates:
                if di in assigned_det or track_id in assigned_track:
                    continue
                assigned_det.add(di)
                assigned_track.add(track_id)
                assignments.append((di, track_id))

        greedy_assign(colour_strict=True,  max_dist_px=self._max_match_px)
        greedy_assign(colour_strict=False, max_dist_px=self._max_match_px * 0.5)

        for di, track_id in assignments:
            det   = detections[di]
            block = det["block"]
            block["block_index"] = int(track_id)
            block["id"]          = f"{int(track_id):03d}"
            self._tracks[track_id] = {
                "x":      det["x"],
                "y":      det["y"],
                "colour": det["colour"],
                "misses": 0,
            }

        for di, det in enumerate(detections):
            if di in assigned_det:
                continue
            new_id = int(self._next_id)
            self._next_id += 1
            det["block"]["block_index"] = new_id
            det["block"]["id"]          = f"{new_id:03d}"
            self._tracks[new_id] = {
                "x":      det["x"],
                "y":      det["y"],
                "colour": det["colour"],
                "misses": 0,
            }

        to_drop: list[int] = []
        canonical_ids = {
            int(entry["block_id"])
            for entry in self._canonical_slots.values()
            if int(entry["block_id"]) not in self._removed_block_ids
        }
        for track_id, track in self._tracks.items():
            if track_id in assigned_track:
                continue
            if track_id in canonical_ids:
                track["misses"] = 0
                continue
            misses = int(track.get("misses", 0)) + 1
            track["misses"] = misses
            if misses > self._max_misses:
                to_drop.append(track_id)
        for track_id in to_drop:
            self._tracks.pop(track_id, None)

        # ── Freeze: enforce canonical identities on top of greedy result ───
        # This is the key step that prevents identity flips: regardless of
        # what colour the greedy matcher found in each slot, we stamp the
        # frozen canonical block_id and colour back in.
        self._enforce_canonical(tower_state)

        # Update canonical with any NEW slots seen for the first time
        # (e.g. after the grid first locks on the initial board state).
        self._update_canonical_slots(tower_state)