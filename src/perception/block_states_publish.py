"""Build /jenga/block_states with debounced removal for briefly absent blocks."""

from __future__ import annotations

from geometry_msgs.msg import Pose
from jenga_interfaces.msg import JengaBlockState, JengaBlockStates

from perception_config import (
    BLOCK_POSE_WORLD_FRAME,
    BLOCK_STATE_PUBLISH_MISSING_CONFIRM_FRAMES,
)
from layer_analysis import SlotAbsenceStreakTracker


def _block_state_from_tower_block(
    block: dict,
    layer_idx: int,
    pos_idx: int,
) -> JengaBlockState | None:
    pose_global_mm = block.get("pose_global_mm")
    if not pose_global_mm:
        return None
    pos = pose_global_mm.get("position", {})
    ori = pose_global_mm.get("orientation", {})

    block_id = int(block.get("block_index", -1))
    if block_id < 0:
        return None

    state = JengaBlockState()
    state.block_id = block_id
    state.colour = str(block.get("colour", "unknown"))
    state.layer = max(layer_idx, 0)
    state.layer_position = max(0, min(2, int(pos_idx)))

    pose = Pose()
    pose.position.x = float(pos.get("x", 0.0)) / 1000.0
    pose.position.y = float(pos.get("y", 0.0)) / 1000.0
    pose.position.z = float(pos.get("z", 0.0)) / 1000.0
    pose.orientation.x = float(ori.get("x", 0.0))
    pose.orientation.y = float(ori.get("y", 0.0))
    pose.orientation.z = float(ori.get("z", 0.0))
    pose.orientation.w = float(ori.get("w", 1.0))
    state.pose = pose
    return state


class BlockStatesPublishCache:
    """Last published block state per tower slot."""

    def __init__(self) -> None:
        self._by_slot: dict[tuple[int, int], JengaBlockState] = {}

    def reset(self) -> None:
        self._by_slot.clear()

    def get(self, layer_idx: int, pos_idx: int) -> JengaBlockState | None:
        return self._by_slot.get((int(layer_idx), int(pos_idx)))

    def store(self, layer_idx: int, pos_idx: int, state: JengaBlockState) -> None:
        self._by_slot[(int(layer_idx), int(pos_idx))] = state

    def drop(self, layer_idx: int, pos_idx: int) -> None:
        self._by_slot.pop((int(layer_idx), int(pos_idx)), None)


def build_block_states_msg(
    tower_data: list[dict],
    *,
    stamp,
    absence_streaks: SlotAbsenceStreakTracker | None = None,
    cache: BlockStatesPublishCache | None = None,
    confirm_frames: int = BLOCK_STATE_PUBLISH_MISSING_CONFIRM_FRAMES,
) -> JengaBlockStates:
    """Build block states, holding last pose until absence is confirmed."""
    out = JengaBlockStates()
    out.header.stamp = stamp
    out.header.frame_id = BLOCK_POSE_WORLD_FRAME

    confirm = max(1, int(confirm_frames))
    blocks: list[JengaBlockState] = []

    for layer in tower_data:
        layer_idx = int(layer.get("layer", -1))
        for pos_idx, block in enumerate(layer.get("blocks", [])):
            if block.get("present"):
                state = _block_state_from_tower_block(block, layer_idx, pos_idx)
                if state is None:
                    continue
                if cache is not None:
                    cache.store(layer_idx, pos_idx, state)
                blocks.append(state)
                continue

            streak = 0
            if absence_streaks is not None:
                streak = absence_streaks.absent_streak(layer_idx, pos_idx)

            if cache is not None and streak < confirm:
                held = cache.get(layer_idx, pos_idx)
                if held is not None:
                    blocks.append(held)
                    continue

            if cache is not None:
                cache.drop(layer_idx, pos_idx)

    blocks.sort(key=lambda item: item.block_id)
    out.blocks = blocks
    return out
