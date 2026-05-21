"""
block_identity_tracker.py
-------------------------
Persistent ID assignment so block identities follow physical blocks across frames.
"""

from __future__ import annotations

import math


class BlockIdentityTracker:
    def __init__(self, max_match_px: float = 80.0, max_misses: int = 60) -> None:
        self._max_match_px = float(max_match_px)
        self._max_misses = int(max_misses)
        self._tracks: dict[int, dict] = {}
        self._next_id: int = 0
        self._initialized = False

    def reset(self) -> None:
        self._tracks.clear()
        self._next_id = 0
        self._initialized = False

    def _present_detections(self, tower_state: list[dict]) -> list[dict]:
        detections: list[dict] = []
        for layer in tower_state:
            for block in layer.get("blocks", []):
                if not block.get("present"):
                    continue
                mx = block.get("mean_x_px")
                my = block.get("mean_y_px")
                if mx is None or my is None:
                    continue
                detections.append(
                    {
                        "block": block,
                        "x": float(mx),
                        "y": float(my),
                        "colour": str(block.get("colour", "unknown")),
                    }
                )
        return detections

    def _clear_ids(self, tower_state: list[dict]) -> None:
        for layer in tower_state:
            for block in layer.get("blocks", []):
                block["block_index"] = None
                block["id"] = None

    def _initialize_from_existing(self, tower_state: list[dict]) -> None:
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
                "x": det["x"],
                "y": det["y"],
                "colour": det["colour"],
                "misses": 0,
            }
            block["block_index"] = bid
            block["id"] = f"{bid:03d}"
            max_existing = max(max_existing, bid)
        self._next_id = max_existing + 1 if max_existing >= 0 else 0
        self._initialized = True

    def apply(self, tower_state: list[dict]) -> None:
        if not tower_state:
            return
        if not self._initialized:
            self._initialize_from_existing(tower_state)
            return

        self._clear_ids(tower_state)
        detections = self._present_detections(tower_state)

        assigned_det: set[int] = set()
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
                    dist = math.hypot(det["x"] - float(track["x"]), det["y"] - float(track["y"]))
                    if dist <= max_dist_px:
                        candidates.append((dist, di, track_id))
            candidates.sort(key=lambda item: item[0])
            for _dist, di, track_id in candidates:
                if di in assigned_det or track_id in assigned_track:
                    continue
                assigned_det.add(di)
                assigned_track.add(track_id)
                assignments.append((di, track_id))

        greedy_assign(colour_strict=True, max_dist_px=self._max_match_px)
        greedy_assign(colour_strict=False, max_dist_px=self._max_match_px * 0.5)

        for di, track_id in assignments:
            det = detections[di]
            block = det["block"]
            block["block_index"] = int(track_id)
            block["id"] = f"{int(track_id):03d}"
            self._tracks[track_id] = {
                "x": det["x"],
                "y": det["y"],
                "colour": det["colour"],
                "misses": 0,
            }

        for di, det in enumerate(detections):
            if di in assigned_det:
                continue
            new_id = int(self._next_id)
            self._next_id += 1
            det["block"]["block_index"] = new_id
            det["block"]["id"] = f"{new_id:03d}"
            self._tracks[new_id] = {
                "x": det["x"],
                "y": det["y"],
                "colour": det["colour"],
                "misses": 0,
            }

        to_drop: list[int] = []
        for track_id, track in self._tracks.items():
            if track_id in assigned_track:
                continue
            misses = int(track.get("misses", 0)) + 1
            track["misses"] = misses
            if misses > self._max_misses:
                to_drop.append(track_id)
        for track_id in to_drop:
            self._tracks.pop(track_id, None)
