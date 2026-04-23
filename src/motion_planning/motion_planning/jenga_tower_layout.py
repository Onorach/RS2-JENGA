
"""YAML layout and Cartesian pick/place pose sequence for Jenga tower stacking."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from geometry_msgs.msg import Pose, PoseStamped


def _quat_mul_xyzw(qa: list[float], qb: list[float]) -> tuple[float, float, float, float]:
    ax, ay, az, aw = qa
    bx, by, bz, bw = qb
    x = aw * bx + ax * bw + ay * bz - az * by
    y = aw * by - ax * bz + ay * bw + az * bx
    z = aw * bz + ax * by - ay * bx + az * bw
    w = aw * bw - ax * bx - ay * by - az * bz
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return 0.0, 0.0, 0.0, 1.0
    inv = 1.0 / n
    return x * inv, y * inv, z * inv, w * inv


def quaternion_from_euler_rpy(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    """Fixed-frame XYZ: roll about X, then pitch Y, then yaw Z (radians). Returns xyzw."""
    cr, sr = math.cos(roll * 0.5), math.sin(roll * 0.5)
    cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
    cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return 0.0, 0.0, 0.0, 1.0
    inv = 1.0 / n
    return x * inv, y * inv, z * inv, w * inv


def _pose_from_position_rpy_deg(
    px: float, py: float, pz: float, rpy_deg: list[float]
) -> tuple[float, float, float, float, float, float, float]:
    r, p, y = math.radians(rpy_deg[0]), math.radians(rpy_deg[1]), math.radians(rpy_deg[2])
    qx, qy, qz, qw = quaternion_from_euler_rpy(r, p, y)
    return px, py, pz, qx, qy, qz, qw


def _read_vec3(d: dict[str, Any], key: str) -> tuple[float, float, float]:
    v = d[key]
    return float(v[0]), float(v[1]), float(v[2])


def _read_rpy_deg(d: dict[str, Any]) -> list[float]:
    if "rpy_deg" in d:
        r = d["rpy_deg"]
        return [float(r[0]), float(r[1]), float(r[2])]
    if "rpy" in d:
        r = d["rpy"]
        return [float(r[0]), float(r[1]), float(r[2])]
    return [180.0, 0.0, 0.0]


@dataclass(frozen=True)
class TowerLayout:
    frame_id: str
    approach_z_offset: float
    layer_height: float
    block_spacing_m: float
    place_yaw_step_deg: float
    tower_cx: float
    tower_cy: float
    tower_z0: float
    tower_base_rpy_deg: list[float]
    pickups: list[tuple[float, float, float, float, float, float, float]]
    pickup_cycle: bool


def load_tower_layout(path: str | Path) -> TowerLayout:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Layout YAML root must be a mapping: {p}")

    frame_id = str(data.get("frame_id", "base_link"))
    approach_z_offset = float(data.get("approach_z_offset", 0.06))
    layer_height = float(data.get("layer_height", 0.015))
    block_spacing_m = float(data.get("block_spacing_m", 0.048))
    place_yaw_step_deg = float(data.get("place_yaw_step_deg", 90.0))
    pickup_cycle = bool(data.get("pickup_cycle", False))

    origin = data.get("tower_origin", {})
    if not isinstance(origin, dict):
        raise ValueError("tower_origin must be a mapping with position and rpy_deg")
    cx, cy, cz = _read_vec3(origin, "position")
    tower_base_rpy_deg = _read_rpy_deg(origin)

    pickups_raw = data.get("pickups", [])
    if not pickups_raw:
        raise ValueError("pickups must be a non-empty list of {position, rpy_deg}")
    pickups: list[tuple[float, float, float, float, float, float, float]] = []
    for i, entry in enumerate(pickups_raw):
        if not isinstance(entry, dict):
            raise ValueError(f"pickups[{i}] must be a mapping")
        px, py, pz = _read_vec3(entry, "position")
        rpy_deg = _read_rpy_deg(entry)
        pickups.append(_pose_from_position_rpy_deg(px, py, pz, rpy_deg))

    return TowerLayout(
        frame_id=frame_id,
        approach_z_offset=approach_z_offset,
        layer_height=layer_height,
        block_spacing_m=block_spacing_m,
        place_yaw_step_deg=place_yaw_step_deg,
        tower_cx=cx,
        tower_cy=cy,
        tower_z0=cz,
        tower_base_rpy_deg=tower_base_rpy_deg,
        pickups=pickups,
        pickup_cycle=pickup_cycle,
    )


def _place_quaternion_for_layer(layout: TowerLayout, layer_index: int) -> tuple[float, float, float, float]:
    qx, qy, qz, qw = quaternion_from_euler_rpy(
        math.radians(layout.tower_base_rpy_deg[0]),
        math.radians(layout.tower_base_rpy_deg[1]),
        math.radians(layout.tower_base_rpy_deg[2]),
    )
    extra_yaw = math.radians(layout.place_yaw_step_deg * float(layer_index % 2))
    qyaw = [0.0, 0.0, math.sin(extra_yaw * 0.5), math.cos(extra_yaw * 0.5)]
    return _quat_mul_xyzw(qyaw, [qx, qy, qz, qw])


def place_pose_for_block(layout: TowerLayout, layer_index: int, block_index: int) -> Pose:
    """block_index 0..2 within the layer."""
    z = layout.tower_z0 + float(layer_index) * layout.layer_height
    s = layout.block_spacing_m
    if layer_index % 2 == 0:
        px = layout.tower_cx + (float(block_index) - 1.0) * s
        py = layout.tower_cy
    else:
        px = layout.tower_cx
        py = layout.tower_cy + (float(block_index) - 1.0) * s
    qx, qy, qz, qw = _place_quaternion_for_layer(layout, layer_index)
    pose = Pose()
    pose.position.x = px
    pose.position.y = py
    pose.position.z = z
    pose.orientation.x = qx
    pose.orientation.y = qy
    pose.orientation.z = qz
    pose.orientation.w = qw
    return pose


def pickup_pose_for_block_index(layout: TowerLayout, global_block_index: int) -> tuple[float, float, float, float, float, float, float]:
    n = len(layout.pickups)
    if layout.pickup_cycle:
        return layout.pickups[global_block_index % n]
    if global_block_index >= n:
        raise ValueError(
            f"pickup_cycle is false but need pickup index {global_block_index} with only {n} entries"
        )
    return layout.pickups[global_block_index]


def build_pose_stamped(layout: TowerLayout, pose: Pose) -> PoseStamped:
    msg = PoseStamped()
    msg.header.frame_id = layout.frame_id
    msg.pose = pose
    return msg


def iter_tower_motion_steps(
    layout: TowerLayout,
    max_layers: int,
) -> list[tuple[str, Pose]]:
    """
    Ordered motion steps: for each block, pre_pick, pick, post_pick, pre_place, place, post_place.
    max_layers: 1 for single-layer pass gate, up to 6 for full tower.
    """
    steps: list[tuple[str, Pose]] = []
    blocks_per_layer = 3
    total_blocks = max_layers * blocks_per_layer
    z_off = layout.approach_z_offset
    gbi = 0
    for layer in range(max_layers):
        for b in range(blocks_per_layer):
            px, py, pz, qx, qy, qz, qw = pickup_pose_for_block_index(layout, gbi)
            pick = Pose()
            pick.position.x, pick.position.y, pick.position.z = px, py, pz
            pick.orientation.x, pick.orientation.y = qx, qy
            pick.orientation.z, pick.orientation.w = qz, qw

            pre_pick = Pose()
            pre_pick.position.x, pre_pick.position.y = px, py
            pre_pick.position.z = pz + z_off
            pre_pick.orientation = pick.orientation

            post_pick = Pose()
            post_pick.position.x, post_pick.position.y = px, py
            post_pick.position.z = pz + z_off
            post_pick.orientation = pick.orientation

            place = place_pose_for_block(layout, layer, b)

            pre_place = Pose()
            pre_place.position.x = place.position.x
            pre_place.position.y = place.position.y
            pre_place.position.z = place.position.z + z_off
            pre_place.orientation = place.orientation

            post_place = Pose()
            post_place.position.x = place.position.x
            post_place.position.y = place.position.y
            post_place.position.z = place.position.z + z_off
            post_place.orientation = place.orientation

            prefix = f"L{layer}_B{b}"
            steps.append((f"{prefix}_pre_pick", pre_pick))
            steps.append((f"{prefix}_pick", pick))
            steps.append((f"{prefix}_post_pick", post_pick))
            steps.append((f"{prefix}_pre_place", pre_place))
            steps.append((f"{prefix}_place", place))
            steps.append((f"{prefix}_post_place", post_place))
            gbi += 1
    return steps
