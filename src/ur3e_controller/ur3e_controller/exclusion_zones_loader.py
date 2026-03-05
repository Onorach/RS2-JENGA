# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
Floor-plane exclusion zone: prevents any robot link from moving below the horizontal.

Publishes a 10 m × 10 m × 0.2 m collision slab to the MoveIt2 planning scene whose
top surface sits at the configured floor height (default: z = 0 in base_link).  The
planner will then reject every IK/trajectory solution that would bring any link into
that slab, effectively keeping the whole robot above the table.
"""

from __future__ import annotations

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene, PlanningSceneWorld
from shape_msgs.msg import SolidPrimitive
from std_msgs.msg import Header

FLOOR_OBJECT_ID = "floor_plane"
DEFAULT_FLOOR_Z = 0.0       # top of slab in the planning frame (metres)
DEFAULT_FRAME_ID = "base_link"
_SLAB_THICKNESS = 0.20      # 20 cm slab below floor_z; large enough to block all planners


def build_floor_plane_collision_object(
    floor_z: float = DEFAULT_FLOOR_Z,
    frame_id: str = DEFAULT_FRAME_ID,
) -> CollisionObject:
    """
    Return a CollisionObject that is a 10 m × 10 m slab with its *top* surface at floor_z.
    Any robot link that would descend to floor_z will intersect this object and be rejected
    by MoveIt2's collision checker.
    """
    co = CollisionObject()
    co.header = Header(frame_id=frame_id)
    co.id = FLOOR_OBJECT_ID
    co.operation = CollisionObject.ADD

    slab = SolidPrimitive()
    slab.type = SolidPrimitive.BOX
    slab.dimensions = [10.0, 10.0, _SLAB_THICKNESS]   # X × Y × Z
    co.primitives = [slab]

    # Box is centred at its pose; push the centre down so the top face is at floor_z.
    pose = Pose()
    pose.position.x = 0.0
    pose.position.y = 0.0
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


def publish_floor_plane(
    publisher,
    floor_z: float = DEFAULT_FLOOR_Z,
    frame_id: str = DEFAULT_FRAME_ID,
) -> None:
    """Convenience: publish an *add* planning-scene diff for the floor plane."""
    scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
    scene.world.collision_objects = [build_floor_plane_collision_object(floor_z, frame_id)]
    publisher.publish(scene)


def publish_remove_floor_plane(
    publisher,
    frame_id: str = DEFAULT_FRAME_ID,
) -> None:
    """Convenience: publish a *remove* planning-scene diff for the floor plane."""
    scene = PlanningScene(is_diff=True, world=PlanningSceneWorld())
    scene.world.collision_objects = [remove_floor_plane_collision_object(frame_id)]
    publisher.publish(scene)


class FloorPlaneNode(Node):
    """
    Standalone ROS2 node that adds the floor-plane collision object on startup.

    Parameters
    ----------
    floor_z  : float  – z height of the floor surface in the planning frame (default 0.0 m)
    frame_id : str    – TF frame in which floor_z is expressed (default "base_link")
    """

    def __init__(self):
        super().__init__("floor_plane_node")
        self._floor_z = self.declare_parameter("floor_z", DEFAULT_FLOOR_Z).value
        self._frame_id = self.declare_parameter("frame_id", DEFAULT_FRAME_ID).value
        self._pub = self.create_publisher(PlanningScene, "/planning_scene", 10)
        # Delay one second so move_group has time to come up before we publish
        self._timer = self.create_timer(1.0, self._publish_once)
        self._done = False

    def _publish_once(self) -> None:
        if self._done:
            return
        self._done = True
        self._timer.cancel()
        publish_floor_plane(self._pub, self._floor_z, self._frame_id)
        self.get_logger().info(
            "Floor-plane exclusion zone published: top at z=%.3f in '%s'.",
            self._floor_z,
            self._frame_id,
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = FloorPlaneNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
