# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
General-purpose MoveIt2 exclusion-zone manager.

Loads named collision objects (boxes and spheres) from a YAML file and
publishes them to the MoveIt2 planning scene.  An optional built-in floor-plane
slab can be enabled via parameter or added later (e.g. from robot_gui).

At runtime, individual zones can be removed or re-added by publishing a
zone ID string to the appropriate topic:

    ros2 topic pub --once /remove_exclusion_zone std_msgs/msg/String "data: cabinet_body"
    ros2 topic pub --once /add_exclusion_zone    std_msgs/msg/String "data: cabinet_body"

YAML schema (see config/ur3e_cabinet.yaml for a worked example)
---------------------------------------------------------------
exclusion_zones:
  - type: box
    id: <string>
    frame_id: <tf_frame>        # e.g. base_link
    position: [x, y, z]        # metres – box centre
    size:     [x, y, z]        # metres – full extents

  - type: sphere
    id: <string>
    frame_id: <tf_frame>
    center: [x, y, z]          # metres – sphere centre
    radius: <float>             # metres
"""

from __future__ import annotations

import yaml

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene, PlanningSceneWorld
from shape_msgs.msg import SolidPrimitive
from std_msgs.msg import Header, String

# ── Floor-plane constants (kept for backward compatibility) ──────────────────

FLOOR_OBJECT_ID = "floor_plane"
DEFAULT_FLOOR_Z = 0.0       # top of slab in the frame (metres)
DEFAULT_FRAME_ID = "base_link"
DEFAULT_FLOOR_PLANE_FRAME_ID = "world"
_SLAB_THICKNESS = 0.20      # 20 cm slab below floor_z


# ── Low-level CollisionObject builders ──────────────────────────────────────

def build_floor_plane_collision_object(
    floor_z: float = DEFAULT_FLOOR_Z,
    frame_id: str = DEFAULT_FRAME_ID,
) -> CollisionObject:
    """Return a 10 m × 10 m slab with its *top* surface at floor_z."""
    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = FLOOR_OBJECT_ID
    co.operation = CollisionObject.ADD

    slab = SolidPrimitive()
    slab.type = SolidPrimitive.BOX
    slab.dimensions = [10.0, 10.0, _SLAB_THICKNESS]
    co.primitives = [slab]

    pose = Pose()
    pose.position.z = floor_z - _SLAB_THICKNESS / 2.0
    pose.orientation.w = 1.0
    co.primitive_poses = [pose]
    return co


def remove_floor_plane_collision_object(
    frame_id: str = DEFAULT_FRAME_ID,
) -> CollisionObject:
    """Return a CollisionObject that removes the floor slab from the planning scene."""
    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = FLOOR_OBJECT_ID
    co.operation = CollisionObject.REMOVE
    return co


def build_box_collision_object(
    zone_id: str,
    frame_id: str,
    position: list[float],
    size: list[float],
) -> CollisionObject:
    """Return a box CollisionObject centred at *position* with full extents *size*."""
    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = zone_id
    co.operation = CollisionObject.ADD

    box = SolidPrimitive()
    box.type = SolidPrimitive.BOX
    box.dimensions = [float(size[0]), float(size[1]), float(size[2])]
    co.primitives = [box]

    pose = Pose()
    pose.position.x = float(position[0])
    pose.position.y = float(position[1])
    pose.position.z = float(position[2])
    pose.orientation.w = 1.0
    co.primitive_poses = [pose]
    return co


def build_sphere_collision_object(
    zone_id: str,
    frame_id: str,
    center: list[float],
    radius: float,
) -> CollisionObject:
    """Return a sphere CollisionObject centred at *center* with the given *radius*."""
    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = zone_id
    co.operation = CollisionObject.ADD

    sphere = SolidPrimitive()
    sphere.type = SolidPrimitive.SPHERE
    sphere.dimensions = [float(radius)]
    co.primitives = [sphere]

    pose = Pose()
    pose.position.x = float(center[0])
    pose.position.y = float(center[1])
    pose.position.z = float(center[2])
    pose.orientation.w = 1.0
    co.primitive_poses = [pose]
    return co


# ── YAML loader ──────────────────────────────────────────────────────────────

def load_zones_from_yaml(path: str) -> list[CollisionObject]:
    """
    Parse an exclusion-zones YAML file and return a list of CollisionObjects.

    Raises ValueError for unrecognised zone types or missing required keys.
    """
    with open(path, "r") as fh:
        data = yaml.safe_load(fh)

    zones = data.get("exclusion_zones", [])
    objects: list[CollisionObject] = []

    for entry in zones:
        zone_type = entry.get("type", "").lower()
        zone_id = entry["id"]
        frame_id = entry.get("frame_id", DEFAULT_FRAME_ID)

        if zone_type == "box":
            co = build_box_collision_object(
                zone_id=zone_id,
                frame_id=frame_id,
                position=entry["position"],
                size=entry["size"],
            )
        elif zone_type == "sphere":
            co = build_sphere_collision_object(
                zone_id=zone_id,
                frame_id=frame_id,
                center=entry["center"],
                radius=entry["radius"],
            )
        else:
            raise ValueError(
                f"Unsupported exclusion zone type '{zone_type}' for zone '{zone_id}'. "
                "Expected 'box' or 'sphere'."
            )

        objects.append(co)

    return objects


# ── Planning-scene publish helpers (backward compat) ─────────────────────────

def publish_floor_plane(
    publisher,
    floor_z: float = DEFAULT_FLOOR_Z,
    frame_id: str = DEFAULT_FRAME_ID,
) -> None:
    """Convenience: publish an *add* planning-scene diff for the floor plane."""
    _publish_objects(publisher, [build_floor_plane_collision_object(floor_z, frame_id)])


def publish_remove_floor_plane(
    publisher,
    frame_id: str = DEFAULT_FRAME_ID,
) -> None:
    """Convenience: publish a *remove* planning-scene diff for the floor plane."""
    _publish_objects(publisher, [remove_floor_plane_collision_object(frame_id)])


def _publish_objects(publisher, objects: list[CollisionObject]) -> None:
    scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
    scene.world.collision_objects = objects
    publisher.publish(scene)


# ── Node ────────────────────────────────────────────────────────────────────

class ExclusionZonesNode(Node):
    """
    ROS2 node that manages MoveIt2 planning-scene exclusion zones.

    On startup it publishes YAML exclusion zones and optionally the floor-plane
    slab when *add_floor_plane* is true.

    At runtime two topics allow individual zones to be toggled by ID:

    /remove_exclusion_zone  (std_msgs/String)  – remove a zone from the scene
    /add_exclusion_zone     (std_msgs/String)  – re-add a previously-loaded zone

    Parameters
    ----------
    floor_z                 : float – z of the floor slab top surface in floor_plane_frame_id (default 0.0)
    floor_plane_frame_id    : str   – TF frame for the floor plane (default "world")
    frame_id                : str   – fallback frame for remove ops; YAML zones use their own frame_id
    exclusion_zones_file    : str   – absolute path to a YAML zones file (default "")
    add_floor_plane         : bool  – publish the built-in floor plane (default False)
    """

    def __init__(self):
        super().__init__("exclusion_zones_node")

        self._floor_z = self.declare_parameter("floor_z", DEFAULT_FLOOR_Z).value
        self._floor_plane_frame_id = self.declare_parameter(
            "floor_plane_frame_id", DEFAULT_FLOOR_PLANE_FRAME_ID
        ).value
        self._frame_id = self.declare_parameter("frame_id", DEFAULT_FRAME_ID).value
        self._zones_file = self.declare_parameter("exclusion_zones_file", "").value
        self._add_floor_plane = self.declare_parameter("add_floor_plane", False).value

        self._pub = self.create_publisher(PlanningScene, "/planning_scene", 10)

        # Maps zone_id → CollisionObject (ADD operation) for every zone loaded at startup.
        # Used to re-add zones after they have been removed at runtime.
        self._zone_registry: dict[str, CollisionObject] = {}
        # Tracks which zone IDs are currently active in the planning scene.
        self._active_ids: set[str] = set()

        self.create_subscription(String, "/remove_exclusion_zone", self._on_remove, 10)
        self.create_subscription(String, "/add_exclusion_zone", self._on_add, 10)

        # Wait 1 s for move_group to come up before publishing.
        self._done = False
        self._timer = self.create_timer(1.0, self._publish_all_once)

    # ── Startup ──────────────────────────────────────────────────────────────

    def _publish_all_once(self) -> None:
        if self._done:
            return
        self._done = True
        self._timer.cancel()

        objects: list[CollisionObject] = []

        if self._add_floor_plane:
            co = build_floor_plane_collision_object(
                self._floor_z, self._floor_plane_frame_id
            )
            self._zone_registry[FLOOR_OBJECT_ID] = co
            self._active_ids.add(FLOOR_OBJECT_ID)
            objects.append(co)
            self.get_logger().info(
                f"Floor-plane exclusion zone: top at z={self._floor_z:.3f} m in "
                f"'{self._floor_plane_frame_id}'."
            )

        if self._zones_file:
            try:
                yaml_objects = load_zones_from_yaml(self._zones_file)
            except Exception as exc:
                self.get_logger().error(
                    f"Failed to load exclusion zones from '{self._zones_file}': {exc}"
                )
                yaml_objects = []

            for co in yaml_objects:
                self._zone_registry[co.id] = co
                self._active_ids.add(co.id)
                objects.append(co)
                self.get_logger().info(f"Loaded exclusion zone: '{co.id}'.")
        elif not self._add_floor_plane:
            self.get_logger().warn(
                "No exclusion_zones_file set and add_floor_plane=false — "
                "no collision objects will be published."
            )

        if objects:
            _publish_objects(self._pub, objects)
            self.get_logger().info(
                f"Published {len(objects)} exclusion zone(s) to the planning scene."
            )

    # ── Runtime zone management ───────────────────────────────────────────────

    def _on_remove(self, msg: String) -> None:
        zone_id = msg.data.strip()
        if not zone_id:
            self.get_logger().warn("Received empty zone ID on /remove_exclusion_zone — ignoring.")
            return
        if zone_id not in self._active_ids:
            self.get_logger().warn(
                f"Zone '{zone_id}' is not currently active — nothing to remove."
            )
            return

        co = CollisionObject()
        # Use the original object's frame for removal (required for correct REMOVE)
        frame = (
            self._zone_registry[zone_id].header.frame_id
            if zone_id in self._zone_registry
            else self._frame_id
        )
        co.header = Header(frame_id=frame)
        co.id = zone_id
        co.operation = CollisionObject.REMOVE
        _publish_objects(self._pub, [co])
        self._active_ids.discard(zone_id)
        self.get_logger().info(f"Removed exclusion zone '{zone_id}' from the planning scene.")

    def _on_add(self, msg: String) -> None:
        zone_id = msg.data.strip()
        if not zone_id:
            self.get_logger().warn("Received empty zone ID on /add_exclusion_zone — ignoring.")
            return
        if zone_id not in self._zone_registry:
            self.get_logger().warn(
                f"Zone '{zone_id}' was not loaded at startup and cannot be re-added. "
                f"Known zones: {list(self._zone_registry.keys())}"
            )
            return
        if zone_id in self._active_ids:
            self.get_logger().info(
                f"Zone '{zone_id}' is already active — skipping."
            )
            return

        co = self._zone_registry[zone_id]
        _publish_objects(self._pub, [co])
        self._active_ids.add(zone_id)
        self.get_logger().info(f"Re-added exclusion zone '{zone_id}' to the planning scene.")


# Backward-compatible alias
FloorPlaneNode = ExclusionZonesNode


# ── Entry point ──────────────────────────────────────────────────────────────

def main(args=None) -> None:
    rclpy.init(args=args)
    node = ExclusionZonesNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
