"""
Sequencer: arm-ready -> extract-middle (to handoff) -> pick+place (handoff to tower top) -> arm-ready.

Assumptions:
- The target block has already been probed and is protruding (~2cm) in the planning scene.
- The MoveIt planning scene contains collision objects `block_XX` for the tower blocks.
- MTC action servers are running:
  - `jenga_arm_ready`
  - `jenga_extract_middle_block`
  - `jenga_pick_place`
"""

from __future__ import annotations

import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

import rclpy
import yaml
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion
from moveit_msgs.msg import PlanningScene
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from jenga_interfaces.action import JengaArmReady, JengaExtractMiddleBlock, JengaPickPlace


def _q_normalize(x: float, y: float, z: float, w: float) -> tuple[float, float, float, float]:
    n2 = x * x + y * y + z * z + w * w
    if n2 <= 0.0:
        return (0.0, 0.0, 0.0, 1.0)
    inv = 1.0 / math.sqrt(n2)
    return (x * inv, y * inv, z * inv, w * inv)


def _q_mul(
    ax: float, ay: float, az: float, aw: float, bx: float, by: float, bz: float, bw: float
) -> tuple[float, float, float, float]:
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _q_from_yaw(yaw_rad: float) -> tuple[float, float, float, float]:
    h = 0.5 * yaw_rad
    return (0.0, 0.0, math.sin(h), math.cos(h))


def _compose_poses(parent: Pose, child: Pose) -> Pose:
    """Return the SE3 composition: world_pose = parent (object anchor) * child (shape offset).

    Handles both CollisionObject serialisation styles:
      - Old style: parent = identity, child = world pose  → result = world pose
      - New style: parent = world pose, child = identity   → result = world pose
    A zero-norm parent quaternion (ROS default Quaternion()) is treated as identity.
    """
    px = float(parent.orientation.x)
    py = float(parent.orientation.y)
    pz = float(parent.orientation.z)
    pw = float(parent.orientation.w)
    if px * px + py * py + pz * pz + pw * pw < 1e-12:
        pw = 1.0
    px, py, pz, pw = _q_normalize(px, py, pz, pw)

    cx = float(child.position.x)
    cy = float(child.position.y)
    cz = float(child.position.z)
    tx = 2.0 * (py * cz - pz * cy)
    ty = 2.0 * (pz * cx - px * cz)
    tz = 2.0 * (px * cy - py * cx)
    rx = cx + pw * tx + (py * tz - pz * ty)
    ry = cy + pw * ty + (pz * tx - px * tz)
    rz = cz + pw * tz + (px * ty - py * tx)

    cqx = float(child.orientation.x)
    cqy = float(child.orientation.y)
    cqz = float(child.orientation.z)
    cqw = float(child.orientation.w)
    qx, qy, qz, qw = _q_mul(px, py, pz, pw, cqx, cqy, cqz, cqw)
    qx, qy, qz, qw = _q_normalize(qx, qy, qz, qw)

    return Pose(
        position=Point(
            x=float(parent.position.x) + rx,
            y=float(parent.position.y) + ry,
            z=float(parent.position.z) + rz,
        ),
        orientation=Quaternion(x=qx, y=qy, z=qz, w=qw),
    )


def _compose_poses(parent: Pose, child: Pose) -> Pose:
    """Return the SE3 composition: world_pose = parent (object anchor) * child (shape offset).

    Handles both CollisionObject serialisation styles:
      - Old style: parent = identity, child = world pose  → result = world pose
      - New style: parent = world pose, child = identity   → result = world pose
    A zero-norm parent quaternion (ROS default Quaternion()) is treated as identity.
    """
    px = float(parent.orientation.x)
    py = float(parent.orientation.y)
    pz = float(parent.orientation.z)
    pw = float(parent.orientation.w)
    if px * px + py * py + pz * pz + pw * pw < 1e-12:
        pw = 1.0
    px, py, pz, pw = _q_normalize(px, py, pz, pw)

    cx = float(child.position.x)
    cy = float(child.position.y)
    cz = float(child.position.z)
    tx = 2.0 * (py * cz - pz * cy)
    ty = 2.0 * (pz * cx - px * cz)
    tz = 2.0 * (px * cy - py * cx)
    rx = cx + pw * tx + (py * tz - pz * ty)
    ry = cy + pw * ty + (pz * tx - px * tz)
    rz = cz + pw * tz + (px * ty - py * tx)

    cqx = float(child.orientation.x)
    cqy = float(child.orientation.y)
    cqz = float(child.orientation.z)
    cqw = float(child.orientation.w)
    qx, qy, qz, qw = _q_mul(px, py, pz, pw, cqx, cqy, cqz, cqw)
    qx, qy, qz, qw = _q_normalize(qx, qy, qz, qw)

    return Pose(
        position=Point(
            x=float(parent.position.x) + rx,
            y=float(parent.position.y) + ry,
            z=float(parent.position.z) + rz,
        ),
        orientation=Quaternion(x=qx, y=qy, z=qz, w=qw),
    )


def _qdict_to_msg(d: dict[str, float]) -> Quaternion:
    return Quaternion(
        x=float(d.get("x", 0.0)),
        y=float(d.get("y", 0.0)),
        z=float(d.get("z", 0.0)),
        w=float(d.get("w", 1.0)),
    )


def _load_yaml(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Layout file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _resolve_layout_path(node: Node, layout_path_param: str) -> str:
    if layout_path_param:
        return layout_path_param
    from ament_index_python.packages import get_package_share_directory

    return str(Path(get_package_share_directory("motion_planning")) / "config" / "jenga_tower_mtc_layout.yaml")


class _PlanningSceneCache:
    def __init__(self, node: Node, topic: str = "/planning_scene") -> None:
        self._node = node
        self._poses: dict[str, PoseStamped] = {}
        qos_volatile = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
        qos_transient = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        subs = [
            node.create_subscription(PlanningScene, topic, self._on_scene, qos_volatile),
            node.create_subscription(PlanningScene, topic, self._on_scene, qos_transient),
        ]
        subs = [
            node.create_subscription(PlanningScene, topic, self._on_scene, qos_volatile),
            node.create_subscription(PlanningScene, topic, self._on_scene, qos_transient),
        ]
        self._subs = subs

    def _on_scene(self, msg: PlanningScene) -> None:
        for obj in msg.world.collision_objects:
            if not obj.id or not obj.primitive_poses:
                continue
            ps = PoseStamped()
            ps.header.frame_id = obj.header.frame_id or "world"
            ps.header.stamp = msg.robot_state.joint_state.header.stamp
            ps.pose = _compose_poses(obj.pose, obj.primitive_poses[0])
            self._poses[obj.id] = ps

    def wait_for_object_pose(self, object_id: str, *, timeout_sec: float) -> Optional[PoseStamped]:
        start = time.monotonic()
        while (time.monotonic() - start) < timeout_sec and rclpy.ok():
            if object_id in self._poses:
                return self._poses[object_id]
            rclpy.spin_once(self._node, timeout_sec=0.05)
        return None

    def snapshot(self) -> dict[str, PoseStamped]:
        return dict(self._poses)


def _normalize_frame_id(frame_id: str) -> str:
    fid = (frame_id or "").strip()
    return fid if fid else "world"


def _tf_transform_pose(
    node: Node,
    tf_buffer: Buffer,
    ps: PoseStamped,
    *,
    target_frame: str,
    timeout_sec: float,
) -> PoseStamped:
    src = _normalize_frame_id(ps.header.frame_id)
    dst = _normalize_frame_id(target_frame)
    if src == dst:
        out = PoseStamped()
        out.header.frame_id = dst
        out.header.stamp = ps.header.stamp
        out.pose = ps.pose
        return out
    try:
        tf = tf_buffer.lookup_transform(
            dst,
            src,
            rclpy.time.Time(),
            timeout=rclpy.duration.Duration(seconds=float(timeout_sec)),
        )
    except TransformException as exc:
        node.get_logger().warn(f"TF lookup failed: {src} -> {dst}: {exc}")
        out = PoseStamped()
        out.header.frame_id = src
        out.header.stamp = ps.header.stamp
        out.pose = ps.pose
        return out
    out = do_transform_pose_stamped(ps, tf)
    out.header.frame_id = dst
    return out


@dataclass(frozen=True)
class _TowerParams:
    frame_id: str
    base_x: float
    base_y: float
    base_z: float
    tower_yaw_rad: float
    blocks_per_layer: int
    layer_dz: float
    slot_dx: float
    q_place_base: tuple[float, float, float, float]


def _tower_params_from_layout(data: dict[str, Any], *, frame_id: str) -> _TowerParams:
    p = data.get("parametric", {})
    t = p.get("tower", {})
    base = t.get("base", {})
    tower_yaw_deg = float(t.get("tower_yaw_deg", 45.0))
    oq = p.get("orientation_place", {"x": 0.0, "y": 0.0, "z": 0.707, "w": 0.707})
    q_place = _qdict_to_msg(oq)
    q_place_base = _q_normalize(q_place.x, q_place.y, q_place.z, q_place.w)

    return _TowerParams(
        frame_id=frame_id,
        base_x=float(base.get("x", 0.0)),
        base_y=float(base.get("y", 0.0)),
        base_z=float(base.get("z", float(p.get("stock", {}).get("z", 0.0138)))),
        tower_yaw_rad=math.radians(tower_yaw_deg),
        blocks_per_layer=int(t.get("blocks_per_layer", 3)),
        layer_dz=float(t.get("layer_dz", 0.0151)),
        slot_dx=float(t.get("slot_dx", 0.0251)),
        q_place_base=q_place_base,
    )


def _expected_slot_pose(tp: _TowerParams, *, layer: int, slot: int) -> Pose:
    slot_offset = (float(slot) - 1.0) * float(tp.slot_dx)
    if (layer % 2) == 0:
        off_lx, off_ly = slot_offset, 0.0
        layer_yaw = 0.0
    else:
        off_lx, off_ly = 0.0, slot_offset
        layer_yaw = 0.5 * math.pi

    c = math.cos(tp.tower_yaw_rad)
    s = math.sin(tp.tower_yaw_rad)
    off_x = c * off_lx - s * off_ly
    off_y = s * off_lx + c * off_ly

    q_yaw = _q_from_yaw(tp.tower_yaw_rad + layer_yaw)
    qx, qy, qz, qw = _q_mul(q_yaw[0], q_yaw[1], q_yaw[2], q_yaw[3], *tp.q_place_base)
    qx, qy, qz, qw = _q_normalize(qx, qy, qz, qw)

    return Pose(
        position=Point(
            x=float(tp.base_x) + off_x,
            y=float(tp.base_y) + off_y,
            z=float(tp.base_z) + float(layer) * float(tp.layer_dz),
        ),
        orientation=Quaternion(x=qx, y=qy, z=qz, w=qw),
    )


def _dist_xy(a: Point, b: Point) -> float:
    dx = float(a.x) - float(b.x)
    dy = float(a.y) - float(b.y)
    return math.hypot(dx, dy)


def _detect_next_free_top_slot(
    *,
    node: Node,
    tp: _TowerParams,
    scene_poses: dict[str, PoseStamped],
    slot_xy_tol_m: float,
    slot_z_tol_m: float,
    tower_radius_m: float,
    max_extra_layers: int,
) -> tuple[int, int, Pose]:
    # Filter observed blocks roughly within the tower footprint.
    tower_center = Point(x=tp.base_x, y=tp.base_y, z=tp.base_z)
    observed: list[PoseStamped] = []
    for ps in scene_poses.values():
        if _dist_xy(ps.pose.position, tower_center) <= tower_radius_m:
            observed.append(ps)

    def slot_occupied(exp_pose: Pose) -> bool:
        for ps in observed:
            if abs(float(ps.pose.position.z) - float(exp_pose.position.z)) > slot_z_tol_m:
                continue
            if _dist_xy(ps.pose.position, exp_pose.position) <= slot_xy_tol_m:
                return True
        return False

    # Compute occupancy for layers up to "layout layers + extras". If layout omits layers,
    # the extra budget still allows growth beyond the YAML.
    base_layers = max(1, int((len(observed) + tp.blocks_per_layer - 1) / tp.blocks_per_layer))
    layer_limit = base_layers + max_extra_layers

    occupied: dict[tuple[int, int], bool] = {}
    highest_any = -1
    for layer in range(layer_limit):
        any_in_layer = False
        for slot in range(tp.blocks_per_layer):
            exp = _expected_slot_pose(tp, layer=layer, slot=slot)
            occ = slot_occupied(exp)
            occupied[(layer, slot)] = occ
            any_in_layer = any_in_layer or occ
        if any_in_layer:
            highest_any = layer

    if highest_any < 0:
        # Empty tower: start at layer 0 slot 0.
        layer = 0
        slot = 0
        return (layer, slot, _expected_slot_pose(tp, layer=layer, slot=slot))

    # Choose the next free slot on the highest occupied layer, else start a new layer.
    for slot in range(tp.blocks_per_layer):
        if not occupied.get((highest_any, slot), False):
            return (highest_any, slot, _expected_slot_pose(tp, layer=highest_any, slot=slot))

    layer = highest_any + 1
    slot = 0
    return (layer, slot, _expected_slot_pose(tp, layer=layer, slot=slot))


def _fb_log(node: Node):
    def _inner(fb) -> None:  # noqa: ANN001
        try:
            f = fb.feedback
            node.get_logger().info(f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%")
        except (AttributeError, TypeError):
            pass

    return _inner


def _run_arm_ready_action(
    node: Node,
    client: ActionClient,
    *,
    timeout_sec: float,
    label: str,
) -> int:
    goal = JengaArmReady.Goal()
    goal.target_state = ""
    node.get_logger().info(f"{label}: move to ready/standby (jenga_arm_ready)")
    send_f = client.send_goal_async(goal, feedback_callback=_fb_log(node))
    rclpy.spin_until_future_complete(node, send_f, timeout_sec=30.0)
    gh = send_f.result()
    if not gh or not gh.accepted:
        node.get_logger().error(f"{label}: arm ready goal rejected")
        return 6
    r_f = gh.get_result_async()
    rclpy.spin_until_future_complete(node, r_f, timeout_sec=timeout_sec)
    wr = r_f.result()
    if wr is None:
        node.get_logger().error(f"{label}: arm ready no result")
        return 7
    res = wr.result
    if not res.success:
        node.get_logger().error(f"{label}: arm ready failed: {res.message} (code {res.error_code})")
        return 8
    return 0


def _block_index_from_params(node: Node) -> int:
    block_id = str(node.declare_parameter("block_id", "").value).strip()
    if block_id:
        # Accept "block_10" or "10".
        if block_id.startswith("block_"):
            return int(block_id.split("_", 1)[1])
        return int(block_id)
    return int(node.declare_parameter("block_index", 0).value)


def _resolve_place_top_target(
    node: Node,
    tp: _TowerParams,
    *,
    place_top_indices: Sequence[int],
    place_top_layer: int,
    place_top_slot: int,
) -> tuple[int, int, bool] | None:
    """Return (layer, slot, is_manual) or None if parameters are invalid.

    is_manual False means caller should run auto slot detection; layer/slot are dummies.
    Resolution: explicit ``place_top_indices`` [layer, slot] when both are >= 0; else explicit
    ``place_top_layer`` and ``place_top_slot`` when both are >= 0; else auto when all are
    negative; partial specifications are rejected.
    """
    idx = [int(x) for x in place_top_indices]
    arr_explicit: tuple[int, int] | None = None
    if len(idx) == 0:
        pass
    elif len(idx) == 1:
        node.get_logger().error("place_top_indices must be empty or length 2, got length 1")
        return None
    elif len(idx) > 2:
        node.get_logger().error(f"place_top_indices must have at most 2 elements, got {len(idx)}")
        return None
    else:
        l_a, s_a = idx[0], idx[1]
        if l_a >= 0 and s_a >= 0:
            arr_explicit = (l_a, s_a)
        elif l_a < 0 and s_a < 0:
            pass
        else:
            node.get_logger().error(
                "place_top_indices mixes negative and non-negative values (partial spec); "
                "use both >= 0 for manual placement or both < 0 for auto"
            )
            return None

    if arr_explicit is not None:
        l, s = arr_explicit
        if s >= tp.blocks_per_layer:
            node.get_logger().error(
                f"place_top_indices [{l}, {s}] invalid: need "
                f"0 <= slot < blocks_per_layer ({tp.blocks_per_layer})"
            )
            return None
        return (l, s, True)

    if place_top_layer >= 0 and place_top_slot >= 0:
        if place_top_slot >= tp.blocks_per_layer:
            node.get_logger().error(
                f"place_top_slot {place_top_slot} out of range; "
                f"need 0 <= slot < blocks_per_layer ({tp.blocks_per_layer})"
            )
            return None
        return (place_top_layer, place_top_slot, True)

    if place_top_layer < 0 and place_top_slot < 0:
        return (0, 0, False)

    node.get_logger().error(
        "place_top_layer / place_top_slot partial spec: set both >= 0 for manual placement "
        "or both < 0 for auto"
    )
    return None


def main(args: list[str] | None = None) -> int:
    rclpy.init(args=args)
    node = Node("jenga_extract_middle_to_top_sequencer")

    block_index = _block_index_from_params(node)
    goal_frame = str(node.declare_parameter("goal_frame", "base_link").value)
    tf_timeout_sec = float(node.declare_parameter("tf_timeout_sec", 0.5).value)

    arm_ready_action_name = str(node.declare_parameter("arm_ready_action_name", "jenga_arm_ready").value)
    extract_action_name = str(node.declare_parameter("extract_action_name", "jenga_extract_middle_block").value)
    pick_place_action_name = str(node.declare_parameter("pick_place_action_name", "jenga_pick_place").value)

    planning_scene_topic = str(
        node.declare_parameter("planning_scene_topic", "/monitored_planning_scene").value
    )
    scene_timeout_sec = float(node.declare_parameter("scene_timeout_sec", 2.0).value)

    layout_path_param = str(node.declare_parameter("layout_path", "").value)

    per_ready_timeout_sec = float(node.declare_parameter("per_ready_timeout_sec", 600.0).value)
    per_extract_timeout_sec = float(node.declare_parameter("per_extract_timeout_sec", 900.0).value)
    per_pick_place_timeout_sec = float(node.declare_parameter("per_pick_place_timeout_sec", 900.0).value)

    slot_xy_tol_m = float(node.declare_parameter("slot_xy_tol_m", 0.015).value)
    slot_z_tol_m = float(node.declare_parameter("slot_z_tol_m", 0.012).value)
    tower_radius_m = float(node.declare_parameter("tower_radius_m", 0.25).value)
    max_extra_layers = int(node.declare_parameter("max_extra_layers", 6).value)

    place_top_indices_raw = node.declare_parameter("place_top_indices", [-1, -1]).value
    place_top_indices = [int(x) for x in (place_top_indices_raw or [])]
    place_top_layer = int(node.declare_parameter("place_top_layer", -1).value)
    place_top_slot = int(node.declare_parameter("place_top_slot", -1).value)

    # Handoff pose relative to tower base (defaults copied from extract-middle protruded test).
    handoff_dx = float(node.declare_parameter("handoff_dx", -0.15).value)
    handoff_dy = float(node.declare_parameter("handoff_dy", -0.12).value)
    handoff_dz = float(node.declare_parameter("handoff_dz", 0.0).value)

    scene_cache = _PlanningSceneCache(node, topic=planning_scene_topic)
    fallback_topic = "/planning_scene" if planning_scene_topic == "/monitored_planning_scene" else "/monitored_planning_scene"
    fallback_cache = _PlanningSceneCache(node, topic=fallback_topic)
    block_id = f"block_{int(block_index):02d}"

    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node, spin_thread=False)

    # Action clients
    ready_client = ActionClient(node, JengaArmReady, arm_ready_action_name)
    extract_client = ActionClient(node, JengaExtractMiddleBlock, extract_action_name)
    pick_place_client = ActionClient(node, JengaPickPlace, pick_place_action_name)

    for name, c in [
        (arm_ready_action_name, ready_client),
        (extract_action_name, extract_client),
        (pick_place_action_name, pick_place_client),
    ]:
        if not c.wait_for_server(timeout_sec=120.0):
            node.get_logger().error(f"Action server not available: {name}")
            rclpy.shutdown()
            return 2

    rc = _run_arm_ready_action(node, ready_client, timeout_sec=per_ready_timeout_sec, label="Sequence start")
    if rc != 0:
        rclpy.shutdown()
        return rc

    block_pose = scene_cache.wait_for_object_pose(block_id, timeout_sec=scene_timeout_sec)
    if block_pose is None:
        node.get_logger().warn(
            f"Did not observe {block_id} on {planning_scene_topic}; trying fallback topic {fallback_topic}..."
        )
        block_pose = fallback_cache.wait_for_object_pose(block_id, timeout_sec=scene_timeout_sec)
    if block_pose is None:
        snap = {}
        snap.update(fallback_cache.snapshot())
        snap.update(scene_cache.snapshot())
        known = sorted(snap.keys())
        hint = (
            "Tip: verify which topic carries PlanningScene in your setup; common values are "
            "`/monitored_planning_scene` and `/planning_scene`. You can override with "
            "`--ros-args -p planning_scene_topic:=...`."
        )
        node.get_logger().error(
            f"Failed to read pose for {block_id} from {planning_scene_topic} "
            f"(timeout {scene_timeout_sec:.2f}s). "
            f"Observed {len(known)} object id(s): {known[:10]}{'...' if len(known) > 10 else ''}. "
            f"{hint}"
        )
        rclpy.shutdown()
        return 16

    block_pose.header.frame_id = _normalize_frame_id(block_pose.header.frame_id)
    block_pose = _tf_transform_pose(
        node,
        tf_buffer,
        block_pose,
        target_frame=goal_frame,
        timeout_sec=tf_timeout_sec,
    )

    # Load layout and compute top-slot target.
    try:
        layout_path = _resolve_layout_path(node, layout_path_param)
        layout = _load_yaml(layout_path)
        tp = _tower_params_from_layout(layout, frame_id=goal_frame)
    except Exception as exc:
        node.get_logger().error(f"Failed to load/parse layout YAML: {exc}")
        rclpy.shutdown()
        return 17

    resolved = _resolve_place_top_target(
        node,
        tp,
        place_top_indices=place_top_indices,
        place_top_layer=place_top_layer,
        place_top_slot=place_top_slot,
    )
    if resolved is None:
        rclpy.shutdown()
        return 18

    layer, slot, place_manual = resolved
    if place_manual:
        top_pose = _expected_slot_pose(tp, layer=layer, slot=slot)
        node.get_logger().info(f"Top slot manual: layer={layer} slot={slot}")
    else:
        snap = {}
        snap.update(fallback_cache.snapshot())
        snap.update(scene_cache.snapshot())
        layer, slot, top_pose = _detect_next_free_top_slot(
            node=node,
            tp=tp,
            scene_poses=snap,
            slot_xy_tol_m=slot_xy_tol_m,
            slot_z_tol_m=slot_z_tol_m,
            tower_radius_m=tower_radius_m,
            max_extra_layers=max_extra_layers,
        )
        node.get_logger().info(f"Top slot selection: layer={layer} slot={slot}")

    # Build handoff pose (extract places here).
    handoff_pose = PoseStamped()
    handoff_pose.header.frame_id = goal_frame
    handoff_pose.pose = Pose(
        position=Point(
            x=float(tp.base_x) + handoff_dx,
            y=float(tp.base_y) + handoff_dy,
            z=float(tp.base_z) + handoff_dz,
        ),
        orientation=Quaternion(
            x=float(tp.q_place_base[0]),
            y=float(tp.q_place_base[1]),
            z=float(tp.q_place_base[2]),
            w=float(tp.q_place_base[3]),
        ),
    )

    # Fresh stamps right before sending each goal.
    t = node.get_clock().now().to_msg()
    block_pose.header.stamp = t
    handoff_pose.header.stamp = t

    # 1) Extract to handoff.
    extract_goal = JengaExtractMiddleBlock.Goal()
    extract_goal.block_index = int(block_index)
    extract_goal.block_pose = block_pose
    extract_goal.place_pose = handoff_pose
    node.get_logger().info(f"Extract-middle: {block_id} -> handoff (dx={handoff_dx:.3f},dy={handoff_dy:.3f})")
    send_f = extract_client.send_goal_async(extract_goal, feedback_callback=_fb_log(node))
    rclpy.spin_until_future_complete(node, send_f, timeout_sec=30.0)
    gh = send_f.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Extract-middle goal rejected")
        rclpy.shutdown()
        return 3
    r_f = gh.get_result_async()
    rclpy.spin_until_future_complete(node, r_f, timeout_sec=per_extract_timeout_sec)
    wr = r_f.result()
    if wr is None or not wr.result.success:
        msg = getattr(getattr(wr, "result", None), "message", "<no result>")
        code = getattr(getattr(wr, "result", None), "error_code", -1)
        node.get_logger().error(f"Extract-middle failed: {msg} (code {code})")
        rclpy.shutdown()
        return 5

    # 2) Pick pose: prefer planning-scene readback post-extract.
    pick_pose = scene_cache.wait_for_object_pose(block_id, timeout_sec=scene_timeout_sec)
    if pick_pose is None:
        node.get_logger().warn("Pick pose readback timed out; falling back to configured handoff pose")
        pick_pose = handoff_pose

    # 3) Pick+place to top slot.
    place_pose = PoseStamped()
    place_pose.header.frame_id = goal_frame
    place_pose.pose = top_pose
    t = node.get_clock().now().to_msg()
    pick_pose.header.stamp = t
    place_pose.header.stamp = t

    pp_goal = JengaPickPlace.Goal()
    pp_goal.block_index = int(block_index)
    pp_goal.pick_pose = pick_pose
    pp_goal.place_pose = place_pose
    node.get_logger().info(f"Pick+place: handoff -> top (layer={layer} slot={slot})")
    send_f = pick_place_client.send_goal_async(pp_goal, feedback_callback=_fb_log(node))
    rclpy.spin_until_future_complete(node, send_f, timeout_sec=30.0)
    gh = send_f.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Pick+place goal rejected")
        rclpy.shutdown()
        return 3
    r_f = gh.get_result_async()
    rclpy.spin_until_future_complete(node, r_f, timeout_sec=per_pick_place_timeout_sec)
    wr = r_f.result()
    if wr is None or not wr.result.success:
        msg = getattr(getattr(wr, "result", None), "message", "<no result>")
        code = getattr(getattr(wr, "result", None), "error_code", -1)
        node.get_logger().error(f"Pick+place failed: {msg} (code {code})")
        rclpy.shutdown()
        return 5

    rc = _run_arm_ready_action(node, ready_client, timeout_sec=per_ready_timeout_sec, label="Sequence end")
    if rc != 0:
        rclpy.shutdown()
        return rc

    node.get_logger().info("Sequence complete.")
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())

