"""
Publish persistent Jenga block collision objects to the MoveIt2 planning scene.

This node spawns all blocks once (as BOX primitives) and keeps them present so
planning always considers the full stock + tower state.

- ``reset_jenga_blocks`` (Trigger): republish blocks at **stock** poses from YAML.
- ``set_jenga_blocks_tower`` (Trigger): republish blocks at **assembled tower**
  poses (planning scene only; does not move Gazebo or hardware).
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
    tower_poses_from_layout_dict,
)
from moveit_msgs.msg import CollisionObject, PlanningScene, PlanningSceneWorld
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive
from std_msgs.msg import Header
from std_srvs.srv import Trigger

from moveit_msgs.msg import CollisionObject, PlanningScene, PlanningSceneWorld, ObjectColor
from std_msgs.msg import Header, ColorRGBA


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
    return co


class JengaBlocksSceneNode(Node):
    def __init__(self) -> None:
        super().__init__("jenga_blocks_scene")

        self._layout_path = str(self.declare_parameter("layout_path", "").value)
        self._frame_id = str(self.declare_parameter("frame_id", "world").value)
        self._startup_delay_sec = float(
            self.declare_parameter("startup_delay_sec", 1.0).value
        )
        self._dims = _BlockDims(
            x=float(self.declare_parameter("block_box_x", 0.075).value),
            y=float(self.declare_parameter("block_box_y", 0.025).value),
            z=float(self.declare_parameter("block_box_z", 0.015).value),
        )

        self._pub = self.create_publisher(PlanningScene, "/planning_scene", 10)
        self._srv = self.create_service(Trigger, "reset_jenga_blocks", self._on_reset)
        self._srv_tower = self.create_service(
            Trigger, "set_jenga_blocks_tower", self._on_set_tower
        )

        self._cached_objects: list[CollisionObject] = []
        self._done = False
        self._timer = self.create_timer(self._startup_delay_sec, self._publish_once)

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
        pick_xyz = _stock_pick_xyz_list(stock, n_tower=n)
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
            block_id = f"block_{i:02d}"
            objects.append(
                _build_block_object(
                    block_id=block_id,
                    frame_id=self._frame_id,
                    pose=pose,
                    dims=self._dims,
                    operation=CollisionObject.ADD,
                )
            )
        return objects

    def _build_initial_objects(self) -> list[CollisionObject]:
        path = self._resolve_layout_path()
        data = _load_yaml(path)
        poses = self._compute_stock_poses(data)
        return self._build_objects_at_poses(poses)

    def _publish_objects(self, objects: list[CollisionObject]) -> None:
        scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
        scene.world.collision_objects = objects
        
        wood_color = ColorRGBA(r=0.8, g=0.5, b=0.3, a=1.0)
        scene.object_colors = [
            ObjectColor(id=obj.id, color=wood_color) 
            for obj in objects
        ]
        
        self._pub.publish(scene)

    def _publish_once(self) -> None:
        if self._done:
            return
        self._done = True
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
                f"Published {len(self._cached_objects)} Jenga block collision object(s)."
            )

    def _on_reset(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        try:
            objects = self._build_initial_objects()
            self._cached_objects = objects
            self._publish_objects(objects)
            response.success = True
            response.message = f"Republished {len(objects)} Jenga block collision object(s) at stock layout."
        except Exception as exc:
            response.success = False
            response.message = f"reset failed: {exc}"
        return response

    def _on_set_tower(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        try:
            path = self._resolve_layout_path()
            data = _load_yaml(path)
            poses = tower_poses_from_layout_dict(data)
            if not poses:
                response.success = False
                response.message = "tower layout: no block poses (check YAML)."
                return response
            objects = self._build_objects_at_poses(poses)
            self._cached_objects = objects
            self._publish_objects(objects)
            response.success = True
            response.message = (
                f"Republished {len(objects)} Jenga block collision object(s) at tower layout."
            )
        except ValueError as exc:
            response.success = False
            response.message = f"set tower failed: {exc}"
        except Exception as exc:
            response.success = False
            response.message = f"set tower failed: {exc}"
        return response


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = JengaBlocksSceneNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

