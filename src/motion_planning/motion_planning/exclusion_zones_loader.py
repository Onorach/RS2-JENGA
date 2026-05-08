"""
General-purpose MoveIt2 exclusion-zone manager.

Loads named collision objects (boxes, spheres, and meshes) from a YAML file
and publishes them to the MoveIt2 planning scene.  An optional built-in
floor-plane slab can be enabled via parameter or added later.

At runtime, individual zones can be removed or re-added by publishing a
zone ID string to the appropriate topic:

    ros2 topic pub --once /remove_exclusion_zone std_msgs/msg/String "data: cabinet_body"
    ros2 topic pub --once /add_exclusion_zone    std_msgs/msg/String "data: cabinet_body"

YAML schema
-----------
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

  - type: mesh
    id: <string>
    frame_id: <tf_frame>
    mesh_path: "package://<pkg>/meshes/<file>.dae"  # or .stl
    position: [x, y, z]        # metres – mesh origin offset in frame_id
    orientation: [x, y, z, w]  # quaternion (default: identity)
    color: [r, g, b, a]        # optional RGBA 0–1 (mesh default: [0.5, 0.5, 0.5, 0.4])

Any zone type supports an optional 'color' key to override the default colour in
RViz.  Omit it to keep the MoveIt default (opaque pink for boxes/spheres).
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET

import numpy as np
import yaml

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Pose
from moveit_msgs.msg import CollisionObject, ObjectColor, PlanningScene, PlanningSceneWorld
from shape_msgs.msg import Mesh as RosMesh, MeshTriangle, SolidPrimitive
from std_msgs.msg import ColorRGBA, Header, String

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


# ── Mesh helpers ─────────────────────────────────────────────────────────────

def _resolve_package_url(url: str) -> str:
    """Convert ``package://<pkg>/...`` to an absolute filesystem path."""
    if url.startswith("package://"):
        from ament_index_python.packages import get_package_share_directory
        rest = url[len("package://"):]
        pkg, rel = rest.split("/", 1)
        return os.path.join(get_package_share_directory(pkg), rel)
    return url


def _load_dae_as_ros_mesh(path: str) -> RosMesh:
    """Parse a COLLADA .dae file and return a ``shape_msgs/Mesh``.

    Node transform matrices defined in ``<library_visual_scenes>`` are applied
    so that vertex coordinates are in metres and in the correct orientation.
    Multiple geometries in the same file are merged into one mesh.
    """
    COLLADA_NS = "http://www.collada.org/2005/11/COLLADASchema"
    pre = f"{{{COLLADA_NS}}}"

    tree = ET.parse(path)
    root = tree.getroot()

    # Build geometry library: geo_id -> {'verts': list[(x,y,z)], 'faces': list[(a,b,c)]}
    geo_lib: dict = {}

    for geometry in root.findall(f".//{pre}geometry"):
        geo_id = geometry.get("id")
        mesh_el = geometry.find(f"{pre}mesh")
        if mesh_el is None:
            continue

        vertices_el = mesh_el.find(f"{pre}vertices")
        if vertices_el is None:
            continue
        pos_input = vertices_el.find(f'{pre}input[@semantic="POSITION"]')
        if pos_input is None:
            continue
        source_id = pos_input.get("source", "").lstrip("#")

        source_el = mesh_el.find(f'{pre}source[@id="{source_id}"]')
        if source_el is None:
            continue
        float_array_el = source_el.find(f"{pre}float_array")
        if float_array_el is None or not float_array_el.text:
            continue

        vals = list(map(float, float_array_el.text.split()))
        verts = [(vals[i], vals[i + 1], vals[i + 2]) for i in range(0, len(vals) - 2, 3)]

        faces: list = []
        for tri_el in list(mesh_el.findall(f"{pre}triangles")) + list(
            mesh_el.findall(f"{pre}polylist")
        ):
            inputs = tri_el.findall(f"{pre}input")
            stride = (
                max(int(inp.get("offset", 0)) for inp in inputs) + 1 if inputs else 1
            )
            v_offset = 0
            for inp in inputs:
                if inp.get("semantic") == "VERTEX":
                    v_offset = int(inp.get("offset", 0))
                    break

            p_el = tri_el.find(f"{pre}p")
            if p_el is None or not p_el.text:
                continue
            indices = list(map(int, p_el.text.split()))

            if tri_el.tag == f"{pre}triangles":
                for i in range(0, len(indices), stride * 3):
                    a = indices[i + v_offset]
                    b = indices[i + stride + v_offset]
                    c = indices[i + stride * 2 + v_offset]
                    faces.append((a, b, c))
            else:
                # polylist — fan-triangulate each polygon
                vcount_el = tri_el.find(f"{pre}vcount")
                if vcount_el is None or not vcount_el.text:
                    continue
                vcounts = list(map(int, vcount_el.text.split()))
                raw_idx = 0
                for vc in vcounts:
                    if vc >= 3:
                        a0 = indices[raw_idx * stride + v_offset]
                        for j in range(1, vc - 1):
                            b = indices[(raw_idx + j) * stride + v_offset]
                            c = indices[(raw_idx + j + 1) * stride + v_offset]
                            faces.append((a0, b, c))
                    raw_idx += vc

        geo_lib[geo_id] = {"verts": verts, "faces": faces}

    # Walk visual_scene nodes to collect transforms and instance_geometry refs
    all_verts: list = []
    all_faces: list = []

    visual_scene = root.find(f".//{pre}visual_scene")
    if visual_scene is None:
        for geo_data in geo_lib.values():
            v_off = len(all_verts)
            all_verts.extend(geo_data["verts"])
            all_faces.extend((a + v_off, b + v_off, c + v_off) for a, b, c in geo_data["faces"])
    else:
        for node in visual_scene.iter(f"{pre}node"):
            matrix_el = node.find(f"{pre}matrix")
            if matrix_el is not None and matrix_el.text:
                M = np.array(list(map(float, matrix_el.text.split())), dtype=float).reshape(4, 4)
            else:
                M = np.eye(4)

            for inst_geo in node.findall(f"{pre}instance_geometry"):
                geo_id = inst_geo.get("url", "").lstrip("#")
                if geo_id not in geo_lib:
                    continue
                geo_data = geo_lib[geo_id]
                v_off = len(all_verts)

                verts_arr = np.ones((len(geo_data["verts"]), 4))
                verts_arr[:, :3] = geo_data["verts"]
                transformed = (M @ verts_arr.T).T  # shape (N, 4)
                all_verts.extend(
                    (float(r[0]), float(r[1]), float(r[2])) for r in transformed
                )
                all_faces.extend(
                    (a + v_off, b + v_off, c + v_off) for a, b, c in geo_data["faces"]
                )

    ros_mesh = RosMesh()
    ros_mesh.vertices = [Point(x=v[0], y=v[1], z=v[2]) for v in all_verts]
    ros_mesh.triangles = [MeshTriangle(vertex_indices=[int(a), int(b), int(c)]) for a, b, c in all_faces]
    return ros_mesh


def _load_stl_as_ros_mesh(path: str) -> RosMesh:
    """Parse a binary STL file and return a ``shape_msgs/Mesh``."""
    import struct

    with open(path, "rb") as f:
        header = f.read(80)
        if header.lstrip()[:5] == b"solid":
            raise ValueError(
                "ASCII STL detected; please convert to binary STL before use."
            )
        num_triangles = struct.unpack("<I", f.read(4))[0]

        verts_index: dict = {}
        verts_list: list = []
        faces: list = []

        for _ in range(num_triangles):
            f.read(12)  # skip normal
            tri: list = []
            for _ in range(3):
                xyz = struct.unpack("<fff", f.read(12))
                if xyz not in verts_index:
                    verts_index[xyz] = len(verts_list)
                    verts_list.append(xyz)
                tri.append(verts_index[xyz])
            f.read(2)  # attribute byte count
            faces.append(tri)

    ros_mesh = RosMesh()
    ros_mesh.vertices = [Point(x=float(v[0]), y=float(v[1]), z=float(v[2])) for v in verts_list]
    ros_mesh.triangles = [MeshTriangle(vertex_indices=f) for f in faces]
    return ros_mesh


def build_mesh_collision_object(
    zone_id: str,
    frame_id: str,
    mesh_path: str,
    position: list[float],
    orientation: list[float],
) -> CollisionObject:
    """Return a mesh ``CollisionObject`` loaded from a ``.dae`` or ``.stl`` file.

    *mesh_path* may use the ``package://`` URL scheme.
    *position* is the [x, y, z] offset of the mesh origin in *frame_id*.
    *orientation* is an [x, y, z, w] quaternion (identity if omitted).
    """
    resolved = _resolve_package_url(mesh_path)
    ext = os.path.splitext(resolved)[1].lower()
    if ext == ".dae":
        ros_mesh = _load_dae_as_ros_mesh(resolved)
    elif ext in (".stl", ".stlb"):
        ros_mesh = _load_stl_as_ros_mesh(resolved)
    else:
        raise ValueError(
            f"Unsupported mesh format '{ext}' for zone '{zone_id}'. Use .dae or .stl."
        )

    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = zone_id
    co.operation = CollisionObject.ADD
    co.meshes = [ros_mesh]

    pose = Pose()
    pose.position.x = float(position[0])
    pose.position.y = float(position[1])
    pose.position.z = float(position[2])
    ox, oy, oz, ow = (float(v) for v in orientation)
    pose.orientation.x = ox
    pose.orientation.y = oy
    pose.orientation.z = oz
    pose.orientation.w = ow
    co.mesh_poses = [pose]
    return co


def build_object_color(zone_id: str, rgba: list[float]) -> ObjectColor:
    """Return an ``ObjectColor`` message for the given zone and RGBA values (0–1)."""
    oc = ObjectColor()
    oc.id = zone_id
    oc.color = ColorRGBA(
        r=float(rgba[0]),
        g=float(rgba[1]),
        b=float(rgba[2]),
        a=float(rgba[3]),
    )
    return oc


# Default colour applied to mesh-type zones without an explicit 'color' key.
_MESH_DEFAULT_COLOR = [0.78, 0.78, 0.80, 1.0]  # stainless steel (cool silver, fully opaque)


# ── YAML loader ──────────────────────────────────────────────────────────────

def load_zones_from_yaml(
    path: str,
) -> tuple[list[CollisionObject], list[ObjectColor]]:
    """
    Parse an exclusion-zones YAML file.

    Returns a tuple of:
      - list of CollisionObjects to add to the planning scene
      - list of ObjectColors (non-empty only for zones with a 'color' key or
        mesh-type zones which default to semi-transparent grey)

    Raises ValueError for unrecognised zone types or missing required keys.
    """
    with open(path, "r") as fh:
        data = yaml.safe_load(fh)

    zones = data.get("exclusion_zones", [])
    objects: list[CollisionObject] = []
    colors: list[ObjectColor] = []

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
        elif zone_type == "mesh":
            co = build_mesh_collision_object(
                zone_id=zone_id,
                frame_id=frame_id,
                mesh_path=entry["mesh_path"],
                position=entry.get("position", [0.0, 0.0, 0.0]),
                orientation=entry.get("orientation", [0.0, 0.0, 0.0, 1.0]),
            )
        else:
            raise ValueError(
                f"Unsupported exclusion zone type '{zone_type}' for zone '{zone_id}'. "
                "Expected 'box', 'sphere', or 'mesh'."
            )

        objects.append(co)

        # Resolve color: explicit YAML key wins; mesh zones fall back to
        # semi-transparent grey; other zone types get no colour override.
        if "color" in entry:
            colors.append(build_object_color(zone_id, entry["color"]))
        elif zone_type == "mesh":
            colors.append(build_object_color(zone_id, _MESH_DEFAULT_COLOR))

    return objects, colors


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


def _publish_objects(
    publisher,
    objects: list[CollisionObject],
    colors: list[ObjectColor] | None = None,
) -> None:
    scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
    scene.world.collision_objects = objects
    if colors:
        scene.object_colors = colors
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
        # Maps zone_id → ObjectColor for zones that carry a colour override.
        self._zone_colors: dict[str, ObjectColor] = {}
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
                yaml_objects, yaml_colors = load_zones_from_yaml(self._zones_file)
            except Exception as exc:
                self.get_logger().error(
                    f"Failed to load exclusion zones from '{self._zones_file}': {exc}"
                )
                yaml_objects, yaml_colors = [], []

            color_map = {oc.id: oc for oc in yaml_colors}
            for co in yaml_objects:
                self._zone_registry[co.id] = co
                if co.id in color_map:
                    self._zone_colors[co.id] = color_map[co.id]
                self._active_ids.add(co.id)
                objects.append(co)
                self.get_logger().info(f"Loaded exclusion zone: '{co.id}'.")
        elif not self._add_floor_plane:
            self.get_logger().warn(
                "No exclusion_zones_file set and add_floor_plane=false — "
                "no collision objects will be published."
            )

        if objects:
            active_colors = [
                self._zone_colors[co.id]
                for co in objects
                if co.id in self._zone_colors
            ]
            _publish_objects(self._pub, objects, active_colors or None)
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
        color = self._zone_colors.get(zone_id)
        _publish_objects(self._pub, [co], [color] if color else None)
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
