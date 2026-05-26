"""
Publish persistent Jenga block collision objects to the MoveIt2 planning scene.

Optional startup publish via ROS parameter ``initial_layout`` (``none`` default,
``stock`` or ``tower`` to spawn all blocks after ``startup_delay_sec``).

- ``set_jenga_blocks_layout`` (SetJengaBlocksLayout): republish selected indices (or all
  when ``block_indices`` is empty) at either stock or tower layout.
- ``protrude_jenga_block`` (ProtrudeJengaBlock): offset one block along an axis.
- Optional ``perception_updates``: subscribe to ``jenga_interfaces/JengaBlockStates`` and
  refine poses for reported ``block_id`` values (hybrid: does not remove unreported blocks).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import rclpy
import yaml
from geometry_msgs.msg import Point, Pose, Quaternion

from motion_planning.jenga_tower_mtc_sequencer import (
    _stock_pick_xyz_list,
    parametric_platform_offset,
    tower_poses_from_layout_dict,
)
from moveit_msgs.msg import CollisionObject, ObjectColor, PlanningScene, PlanningSceneWorld
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from shape_msgs.msg import SolidPrimitive
from std_msgs.msg import ColorRGBA, Header

from jenga_interfaces.msg import JengaBlockStates
from jenga_interfaces.srv import ProtrudeJengaBlock
from jenga_interfaces.srv import SetJengaBlocksLayout

import math
import time


@dataclass(frozen=True)
class _BlockDims:
    x: float
    y: float
    z: float


def _load_yaml(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Layout file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _blocks_per_layer(data: dict[str, Any]) -> int:
    t = data.get("parametric", {}).get("tower", {})
    if t and "blocks_per_layer" in t:
        return int(t["blocks_per_layer"])
    return int(data.get("blocks_per_layer", 3))


def _layers(data: dict[str, Any]) -> int:
    t = data.get("parametric", {}).get("tower", {})
    if t and "layers" in t:
        return int(t["layers"])
    return int(data.get("layers", 6))


def _build_block_object(
    *,
    block_id: str,
    frame_id: str,
    pose: Pose,
    dims: _BlockDims,
    grasp_offset_m: float,
    probe_offset_m: float,
    operation: int,
) -> CollisionObject:
    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = block_id
    co.operation = operation

    box = SolidPrimitive()
    box.type = SolidPrimitive.BOX
    box.dimensions = [float(dims.x), float(dims.y), float(dims.z)]
    co.primitives = [box]
    co.primitive_poses = [pose]

    # Define standard subframes in object-local coordinates.
    # Subframe naming convention follows MoveIt: usable frames become "<id>/<subframe>".
    half_len = 0.5 * float(dims.x)
    co.subframe_names = ["end_plus", "end_minus", "grasp_plus", "grasp_minus", "probe_plus", "probe_minus"]
    co.subframe_poses = [
        Pose(position=Point(x=+half_len, y=0.0, z=0.0), orientation=Quaternion(w=1.0)),
        Pose(position=Point(x=-half_len, y=0.0, z=0.0), orientation=Quaternion(w=1.0)),
        Pose(
            position=Point(x=+float(grasp_offset_m), y=0.0, z=0.0075),
            orientation=Quaternion(w=1.0),
        ),
        Pose(
            position=Point(x=-float(grasp_offset_m), y=0.0, z=0.0075),
            orientation=Quaternion(w=1.0),
        ),
        Pose(
            position=Point(x=+float(probe_offset_m), y=0.0, z=0.00),
            orientation=Quaternion(w=1.0),
        ),
        Pose(
            position=Point(x=-float(probe_offset_m), y=0.0, z=0.00),
            orientation=Quaternion(w=1.0),
        ),
    ]
    return co


def _axis_to_local_vec(axis: str) -> tuple[float, float, float] | None:
    a = (axis or "").strip()
    if not a:
        return None
    neg = a.startswith("-")
    core = a[1:] if neg else a
    if core not in ("x", "y", "z"):
        return None
    s = -1.0 if neg else 1.0
    if core == "x":
        return (s, 0.0, 0.0)
    if core == "y":
        return (0.0, s, 0.0)
    return (0.0, 0.0, s)


def _quat_rotate_vec(q: Quaternion, v: tuple[float, float, float]) -> tuple[float, float, float]:
    # Rotate vector v by unit quaternion q (x,y,z,w).
    # Using quaternion-vector multiplication: v' = q * (v,0) * q_conj
    x, y, z, w = float(q.x), float(q.y), float(q.z), float(q.w)
    vx, vy, vz = v
    # normalize defensively
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return v
    x, y, z, w = x / n, y / n, z / n, w / n
    # t = 2 * cross(q_vec, v)
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    # v' = v + w*t + cross(q_vec, t)
    vpx = vx + w * tx + (y * tz - z * ty)
    vpy = vy + w * ty + (z * tx - x * tz)
    vpz = vz + w * tz + (x * ty - y * tx)
    return (vpx, vpy, vpz)


def _collision_object_id(block_index: int) -> str:
    return f"block_{int(block_index):02d}"


def _as_bool(val: object) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on")
    return bool(val)


class JengaBlocksSceneNode(Node):
    def __init__(self) -> None:
        super().__init__("jenga_blocks_scene")

        self._layout_path = str(self.declare_parameter("layout_path", "").value)
        self._frame_id = str(self.declare_parameter("frame_id", "world").value)
        self._startup_delay_sec = float(
            self.declare_parameter("startup_delay_sec", 1.0).value
        )
        self._publish_period_sec = float(
            self.declare_parameter("publish_period_sec", 0.0).value
        )
        self._dims = _BlockDims(
            x=float(self.declare_parameter("block_box_x", 0.075).value),
            y=float(self.declare_parameter("block_box_y", 0.025).value),
            z=float(self.declare_parameter("block_box_z", 0.015).value),
        )
        self._grasp_offset_m = float(
            self.declare_parameter("grasp_offset_m", 0.0325).value
        )
        self._probe_offset_m = float(
            self.declare_parameter("probe_offset_m", 0.0375).value
        )
        initial_layout_raw = str(self.declare_parameter("initial_layout", "none").value)
        self._initial_layout = self._parse_initial_layout(initial_layout_raw)

        self._perception_updates = _as_bool(
            self.declare_parameter("perception_updates", False).value
        )
        self._block_states_topic = str(
            self.declare_parameter("block_states_topic", "/jenga/block_states").value
        )
        self._max_update_rate_hz = float(
            self.declare_parameter("max_update_rate_hz", 2.0).value
        )
        self._require_frame_match = _as_bool(
            self.declare_parameter("require_frame_match", True).value
        )
        self._last_perception_apply_mono: float = 0.0
        self._block_states_sub = None

        # Use transient-local durability so late subscribers still receive the latest
        # published scene (important since we often publish only once at startup).
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self._pub = self.create_publisher(PlanningScene, "/planning_scene", qos)
        self._srv_set_layout = self.create_service(
            SetJengaBlocksLayout, "set_jenga_blocks_layout", self._on_set_layout
        )
        self._srv_protrude = self.create_service(
            ProtrudeJengaBlock, "protrude_jenga_block", self._on_protrude
        )

        self._cached_objects: list[CollisionObject] = []
        self._wood_color = ColorRGBA(r=0.8, g=0.5, b=0.3, a=1.0)
        self._done = False
        self._timer = None
        if self._initial_layout is None:
            self.get_logger().info(
                "initial_layout is 'none'; skipping startup planning scene publish."
            )
            self._done = True
        elif self._initial_layout == "__invalid__":
            self.get_logger().error(
                f"Unknown initial_layout '{initial_layout_raw}'; "
                "expected none, stock, or tower. Skipping startup publish."
            )
            self._done = True
        else:
            self._timer = self.create_timer(self._startup_delay_sec, self._publish_once)
        self._republish_timer = None
        if self._publish_period_sec and self._publish_period_sec > 0.0:
            self._republish_timer = self.create_timer(
                self._publish_period_sec, self._republish_cached
            )

        if self._perception_updates:
            sub_qos = QoSProfile(
                history=HistoryPolicy.KEEP_LAST,
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE,
            )
            self._block_states_sub = self.create_subscription(
                JengaBlockStates,
                self._block_states_topic,
                self._on_block_states,
                sub_qos,
            )
            rate_msg = (
                f"{self._max_update_rate_hz:.2f} Hz max"
                if self._max_update_rate_hz > 0.0
                else "unlimited rate"
            )
            self.get_logger().info(
                f"Perception updates enabled: subscribing to {self._block_states_topic} "
                f"({rate_msg})."
            )

    @staticmethod
    def _parse_initial_layout(raw: str) -> str | None:
        layout = (raw or "").strip().lower()
        if layout in ("", "none", "off", "skip"):
            return None
        if layout in ("stock", "tower"):
            return layout
        return "__invalid__"

    def _resolve_layout_path(self) -> str:
        if self._layout_path:
            return self._layout_path
        from ament_index_python.packages import get_package_share_directory

        return str(
            Path(get_package_share_directory("motion_planning"))
            / "config"
            / "jenga_tower_mtc_layout.yaml"
        )

    def _compute_stock_poses(self, data: dict[str, Any]) -> list[Pose]:
        p = data.get("parametric", {})
        stock = p.get("stock", {})
        n = _blocks_per_layer(data) * _layers(data)
        oq = p.get("orientation_pick", {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0})
        q_pick = Quaternion(
            x=float(oq.get("x", 0.0)),
            y=float(oq.get("y", 0.0)),
            z=float(oq.get("z", 0.0)),
            w=float(oq.get("w", 1.0)),
        )
        pick_xyz = _stock_pick_xyz_list(stock, n_tower=n, xyz_offset=parametric_platform_offset(data))
        if len(pick_xyz) < n:
            raise ValueError(
                f"Not enough stock pick positions ({len(pick_xyz)}) for {n} blocks."
            )

        poses: list[Pose] = []
        for i in range(n):
            px, py, pz = pick_xyz[i]
            pose = Pose(
                position=Point(x=px, y=py, z=pz),
                orientation=q_pick,
            )
            poses.append(pose)
        return poses

    def _build_objects_at_poses(self, poses: list[Pose]) -> list[CollisionObject]:
        if len(poses) != 18:
            self.get_logger().warn(
                f"Layout implies {len(poses)} blocks (expected 18). "
                "Will publish that many collision objects."
            )
        objects: list[CollisionObject] = []
        for i, pose in enumerate(poses):
            block_id = _collision_object_id(i)
            objects.append(
                _build_block_object(
                    block_id=block_id,
                    frame_id=self._frame_id,
                    pose=pose,
                    dims=self._dims,
                    grasp_offset_m=self._grasp_offset_m,
                    probe_offset_m=self._probe_offset_m,
                    operation=CollisionObject.ADD,
                )
            )
        return objects

    def _build_initial_objects(self) -> list[CollisionObject]:
        if self._initial_layout is None or self._initial_layout == "__invalid__":
            return []
        path = self._resolve_layout_path()
        data = _load_yaml(path)
        poses = self._poses_for_layout(data=data, target_layout=self._initial_layout)
        return self._build_objects_at_poses(poses)

    def _publish_objects(self, objects: list[CollisionObject]) -> None:
        scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
        scene.world.collision_objects = objects

        scene.object_colors = [ObjectColor(id=obj.id, color=self._wood_color) for obj in objects]
        self._pub.publish(scene)

    def _publish_object(self, obj: CollisionObject) -> None:
        scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
        scene.world.collision_objects = [obj]
        scene.object_colors = [ObjectColor(id=obj.id, color=self._wood_color)]
        self._pub.publish(scene)

    def _publish_once(self) -> None:
        if self._done:
            return
        self._done = True
        if self._timer is not None:
            self._timer.cancel()

        try:
            self._cached_objects = self._build_initial_objects()
        except Exception as exc:
            self.get_logger().error(f"Failed to build Jenga blocks from YAML: {exc}")
            self._cached_objects = []
            return

        if self._cached_objects:
            self._publish_objects(self._cached_objects)
            self.get_logger().info(
                f"Published {len(self._cached_objects)} Jenga block collision object(s) "
                f"at {self._initial_layout} layout."
            )

    def _republish_cached(self) -> None:
        if not self._cached_objects:
            return
        self._publish_objects(self._cached_objects)

    def _poses_for_layout(self, *, data: dict[str, Any], target_layout: str) -> list[Pose]:
        tl = (target_layout or "").strip().lower()
        if tl == "stock":
            return self._compute_stock_poses(data)
        if tl == "tower":
            return tower_poses_from_layout_dict(data)
        raise ValueError(f"invalid target_layout '{target_layout}' (expected 'stock' or 'tower')")

    def _apply_layout(
        self,
        *,
        target_layout: str,
        block_indices: list[int] | None,
    ) -> tuple[bool, str]:
        path = self._resolve_layout_path()
        data = _load_yaml(path)
        poses = self._poses_for_layout(data=data, target_layout=target_layout)
        if not poses:
            return (False, f"{target_layout} layout: no block poses (check YAML).")
        objects = self._build_objects_at_poses(poses)
        n = len(objects)

        if not block_indices:
            self._cached_objects = objects
            self._publish_objects(objects)
            return (True, f"Republished {n} Jenga block collision object(s) at {target_layout} layout.")

        if not self._cached_objects:
            return (
                False,
                "no cached objects yet (call set_jenga_blocks_layout with empty "
                "block_indices for a full layout first)",
            )
        if len(self._cached_objects) != n:
            return (
                False,
                f"cached object count mismatch ({len(self._cached_objects)} vs {n}); "
                "call a full layout service once, then retry.",
            )

        uniq = sorted(set(int(i) for i in block_indices))
        bad = [i for i in uniq if i < 0 or i >= n]
        if bad:
            return (False, f"invalid block_indices {bad} (valid range 0..{n-1})")

        selected = [objects[i] for i in uniq]
        for i in uniq:
            self._cached_objects[i] = objects[i]
        self._publish_objects(selected)
        return (
            True,
            f"Republished {len(selected)} Jenga block collision object(s) at {target_layout} layout: indices={uniq}",
        )

    def _on_set_layout(
        self,
        request: SetJengaBlocksLayout.Request,
        response: SetJengaBlocksLayout.Response,
    ) -> SetJengaBlocksLayout.Response:
        try:
            indices = [int(i) for i in request.block_indices]
            ok, msg = self._apply_layout(
                target_layout=str(request.target_layout),
                block_indices=indices if indices else None,
            )
            response.success = bool(ok)
            response.message = msg
        except Exception as exc:
            response.success = False
            response.message = f"set layout failed: {exc}"
        return response

    def _min_perception_interval_sec(self) -> float:
        if self._max_update_rate_hz <= 0.0:
            return 0.0
        return 1.0 / self._max_update_rate_hz

    def _upsert_cached_object(self, obj: CollisionObject) -> None:
        for i, existing in enumerate(self._cached_objects):
            if existing.id == obj.id:
                self._cached_objects[i] = obj
                return
        self._cached_objects.append(obj)

    def _on_block_states(self, msg: JengaBlockStates) -> None:
        if not self._perception_updates:
            return
        min_interval = self._min_perception_interval_sec()
        if min_interval > 0.0:
            now = time.monotonic()
            if (now - self._last_perception_apply_mono) < min_interval:
                return
            self._last_perception_apply_mono = now

        msg_frame = (msg.header.frame_id or "").strip()
        if self._require_frame_match and msg_frame and msg_frame != self._frame_id:
            self.get_logger().warning(
                f"Skipping JengaBlockStates: frame_id '{msg_frame}' "
                f"!= configured frame_id '{self._frame_id}'."
            )
            return

        updated, skipped = self._apply_block_states(msg)
        if updated:
            self._publish_objects(updated)
            self.get_logger().debug(
                f"Perception: published {len(updated)} block collision update(s) "
                f"(skipped {skipped})."
            )

    def _apply_block_states(
        self, msg: JengaBlockStates
    ) -> tuple[list[CollisionObject], int]:
        """Update cached poses for reported blocks; hybrid mode keeps unreported blocks."""
        updated: list[CollisionObject] = []
        skipped = 0
        for block in msg.blocks:
            idx = int(block.block_id)
            if idx < 0:
                skipped += 1
                continue
            collision_id = _collision_object_id(idx)
            obj = _build_block_object(
                block_id=collision_id,
                frame_id=self._frame_id,
                pose=block.pose,
                dims=self._dims,
                grasp_offset_m=self._grasp_offset_m,
                probe_offset_m=self._probe_offset_m,
                operation=CollisionObject.ADD,
            )
            self._upsert_cached_object(obj)
            updated.append(obj)
        return updated, skipped

    def _on_protrude(
        self, request: ProtrudeJengaBlock.Request, response: ProtrudeJengaBlock.Response
    ) -> ProtrudeJengaBlock.Response:
        block_id = _collision_object_id(int(request.block_index))
        axis = str(request.axis) if request.axis else "x"
        dist = float(request.distance_m)

        local = _axis_to_local_vec(axis)
        if local is None:
            response.success = False
            response.message = f"invalid axis '{axis}' (expected x|y|z|-x|-y|-z)"
            return response

        if not self._cached_objects:
            response.success = False
            response.message = (
                "no cached objects yet (call set_jenga_blocks_layout with empty "
                "block_indices for a full layout first)"
            )
            return response

        # Find the cached collision object and adjust its pose in-place.
        obj = next((o for o in self._cached_objects if o.id == block_id), None)
        if obj is None or not obj.primitive_poses:
            response.success = False
            response.message = f"block not found in cached planning scene: {block_id}"
            return response

        pose = obj.primitive_poses[0]
        dx, dy, dz = _quat_rotate_vec(pose.orientation, local)
        pose.position.x += dist * dx
        pose.position.y += dist * dy
        pose.position.z += dist * dz
        obj.primitive_poses[0] = pose
        obj.header.frame_id = self._frame_id
        obj.operation = CollisionObject.ADD

        self._publish_object(obj)
        response.success = True
        response.message = f"protruded {block_id} by {dist:.4f} m along {axis} (planning scene)"
        return response


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = JengaBlocksSceneNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

