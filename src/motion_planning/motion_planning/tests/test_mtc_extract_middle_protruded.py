"""
End-to-end test helper:
1) Set the MoveIt planning scene to the tower layout
2) Protrude a selected block along its local axis (planning-scene-only)
3) Send a JengaExtractMiddleBlock action to extract from the protruded pose
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path
from typing import Any
from typing import Optional

import rclpy
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion
from moveit_msgs.msg import PlanningScene
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from jenga_interfaces.action import JengaExtractMiddleBlock
from jenga_interfaces.srv import ProtrudeJengaBlock
from jenga_interfaces.srv import SetJengaBlocksLayout


def _on_feedback(fb) -> None:  # noqa: ANN001
    try:
        f = fb.feedback
        print(f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%")
    except (AttributeError, TypeError):
        pass


def _resolve_layout_path(layout_path_param: str) -> str:
    if layout_path_param:
        return layout_path_param
    from ament_index_python.packages import get_package_share_directory

    return str(
        Path(get_package_share_directory("motion_planning"))
        / "config"
        / "jenga_tower_mtc_layout.yaml"
    )


def _load_yaml(path: str) -> dict[str, Any]:
    import yaml

    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Layout file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _q_normalize(x: float, y: float, z: float, w: float) -> Quaternion:
    n2 = x * x + y * y + z * z + w * w
    if n2 <= 0.0:
        return Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
    inv = 1.0 / math.sqrt(n2)
    return Quaternion(x=x * inv, y=y * inv, z=z * inv, w=w * inv)


class _PlanningSceneCache:
    def __init__(self, node: Node, topic: str = "/planning_scene") -> None:
        self._node = node
        self._objects: dict[str, PoseStamped] = {}
        self._collision_objects: dict[str, Any] = {}
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
        subs = [node.create_subscription(PlanningScene, topic, self._on_scene, qos_volatile)]
        if topic != "/monitored_planning_scene":
            subs.append(node.create_subscription(PlanningScene, topic, self._on_scene, qos_transient))
        self._subs = subs

    def _on_scene(self, msg: PlanningScene) -> None:
        # We're interested in world collision objects (the Jenga blocks are primitives).
        for obj in msg.world.collision_objects:
            if not obj.id or not obj.primitive_poses:
                continue
            ps = PoseStamped()
            ps.header.frame_id = obj.header.frame_id or "world"
            ps.header.stamp = msg.robot_state.joint_state.header.stamp
            ps.pose = obj.primitive_poses[0]
            self._objects[obj.id] = ps
            # Keep the full collision object too (subframes live here).
            self._collision_objects[obj.id] = obj

    def wait_for_object_pose(
        self, object_id: str, *, timeout_sec: float = 2.0
    ) -> Optional[PoseStamped]:
        start = time.monotonic()
        while (time.monotonic() - start) < timeout_sec and rclpy.ok():
            if object_id in self._objects:
                return self._objects[object_id]
            rclpy.spin_once(self._node, timeout_sec=0.05)
        return None

    def wait_for_collision_object(self, object_id: str, *, timeout_sec: float = 2.0) -> Any:
        start = time.monotonic()
        while (time.monotonic() - start) < timeout_sec and rclpy.ok():
            if object_id in self._collision_objects:
                return self._collision_objects[object_id]
            rclpy.spin_once(self._node, timeout_sec=0.05)
        return None


def _assert_close(node: Node, label: str, got: float, expected: float, tol: float) -> None:
    if abs(got - expected) > tol:
        raise AssertionError(f"{label}: got {got:.6f} expected {expected:.6f} (tol {tol:.6f})")


def _validate_subframes(
    *,
    node: Node,
    obj: Any,
    box_x: float,
    grasp_offset_m: float,
    tol: float = 1e-6,
) -> None:
    names = list(getattr(obj, "subframe_names", []))
    poses = list(getattr(obj, "subframe_poses", []))
    if len(names) != 4 or len(poses) != 4:
        raise AssertionError(
            f"Expected 4 subframes; got names={len(names)} poses={len(poses)} for {getattr(obj, 'id', '<unknown>')}"
        )

    expected_names = {"end_plus", "end_minus", "grasp_plus", "grasp_minus"}
    if set(names) != expected_names:
        raise AssertionError(f"Unexpected subframe_names for {obj.id}: {names} (expected {sorted(expected_names)})")

    by_name = {n: p for n, p in zip(names, poses)}
    half_len = 0.5 * float(box_x)
    expected = {
        "end_plus": {"x": +half_len, "z": 0.0000},
        "end_minus": {"x": -half_len, "z": 0.0000},
        "grasp_plus": {"x": +float(grasp_offset_m), "z": 0.0075},
        "grasp_minus": {"x": -float(grasp_offset_m), "z": 0.0075},
    }
    for n, exp in expected.items():
        p = by_name[n]
        _assert_close(node, f"{obj.id}/{n}.position.x", float(p.position.x), exp["x"], tol)
        _assert_close(node, f"{obj.id}/{n}.position.y", float(p.position.y), 0.0, tol)
        _assert_close(node, f"{obj.id}/{n}.position.z", float(p.position.z), exp["z"], tol)
        _assert_close(node, f"{obj.id}/{n}.position.z", float(p.position.z), exp["z"], tol)
        # Orientation is expected identity in object-local coordinates.
        _assert_close(node, f"{obj.id}/{n}.orientation.x", float(p.orientation.x), 0.0, tol)
        _assert_close(node, f"{obj.id}/{n}.orientation.y", float(p.orientation.y), 0.0, tol)
        _assert_close(node, f"{obj.id}/{n}.orientation.z", float(p.orientation.z), 0.0, tol)
        _assert_close(node, f"{obj.id}/{n}.orientation.w", float(p.orientation.w), 1.0, tol)


def _call_set_layout(
    node: Node,
    target_layout: str,
    *,
    srv_name: str = "set_jenga_blocks_layout",
    timeout_sec: float = 10.0,
) -> bool:
    cli = node.create_client(SetJengaBlocksLayout, srv_name)
    if not cli.wait_for_service(timeout_sec=timeout_sec):
        node.get_logger().error(f"Service not available: {srv_name}")
        return False
    req = SetJengaBlocksLayout.Request()
    req.block_indices = []
    req.target_layout = target_layout
    fut = cli.call_async(req)
    rclpy.spin_until_future_complete(node, fut, timeout_sec=timeout_sec)
    resp = fut.result()
    if not resp or not resp.success:
        node.get_logger().error(
            f"{srv_name} ({target_layout}) failed: {getattr(resp, 'message', '<no message>')}"
        )
        return False
    node.get_logger().info(f"{srv_name} ({target_layout}): {resp.message}")
    return True


def _call_protrude(
    node: Node,
    *,
    block_index: int,
    distance_m: float,
    axis: str,
    srv_name: str = "protrude_jenga_block",
    timeout_sec: float = 10.0,
) -> bool:
    cli = node.create_client(ProtrudeJengaBlock, srv_name)
    if not cli.wait_for_service(timeout_sec=timeout_sec):
        node.get_logger().error(f"Service not available: {srv_name}")
        return False
    req = ProtrudeJengaBlock.Request()
    req.block_index = int(block_index)
    req.distance_m = float(distance_m)
    req.axis = str(axis)
    fut = cli.call_async(req)
    rclpy.spin_until_future_complete(node, fut, timeout_sec=timeout_sec)
    resp = fut.result()
    if not resp or not resp.success:
        node.get_logger().error(f"{srv_name} failed: {getattr(resp, 'message', '<no message>')}")
        return False
    node.get_logger().info(resp.message)
    return True


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("test_mtc_extract_middle_protruded")

    action_name = str(node.declare_parameter("action_name", "jenga_extract_middle_block").value)
    goal_frame = str(node.declare_parameter("goal_frame", "base_link").value)
    tf_timeout_sec = float(node.declare_parameter("tf_timeout_sec", 0.5).value)
    block_index = int(node.declare_parameter("block_index", 10).value)
    protrude_distance_m = float(node.declare_parameter("protrude_distance_m", 0.02).value)
    protrude_axis = str(node.declare_parameter("protrude_axis", "x").value)
    planning_scene_topic = str(node.declare_parameter("planning_scene_topic", "/planning_scene").value)
    scene_timeout_sec = float(node.declare_parameter("scene_timeout_sec", 2.0).value)
    validate_subframes = bool(node.declare_parameter("validate_subframes", True).value)
    subframe_tol = float(node.declare_parameter("subframe_tol", 1e-6).value)
    box_x = float(node.declare_parameter("block_box_x", 0.075).value)
    grasp_offset_m = float(node.declare_parameter("grasp_offset_m", 0.0325).value)

    layout_path_param = str(node.declare_parameter("layout_path", "").value)
    place_dx = float(node.declare_parameter("place_dx", -0.12).value)
    place_dy = float(node.declare_parameter("place_dy", -0.08).value)
    place_dz = float(node.declare_parameter("place_dz", 0.0).value)
    # Optional override: if set, passes this axis directly to the server instead of letting
    # the server auto-detect from the planning scene. Useful for debugging forced directions.
    extract_axis_override = str(node.declare_parameter("extract_axis", "").value).strip()

    scene_cache = _PlanningSceneCache(node, topic=planning_scene_topic)
    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node, spin_thread=False)

    # 1) Put blocks in tower layout in planning scene
    if not _call_trigger(node, "set_jenga_blocks_tower_layout", timeout_sec=10.0):
        rclpy.shutdown()
        return 10

    block_id = f"block_{block_index:02d}"
    warm = scene_cache.wait_for_object_pose(block_id, timeout_sec=scene_timeout_sec)
    if warm is None:
        node.get_logger().warn(
            f"Did not observe {block_id} on {planning_scene_topic} after set tower (timeout {scene_timeout_sec:.2f}s)"
        )
    elif validate_subframes:
        obj = scene_cache.wait_for_collision_object(block_id, timeout_sec=scene_timeout_sec)
        if obj is None:
            node.get_logger().warn(f"Did not observe full CollisionObject for {block_id} to validate subframes")
        else:
            _validate_subframes(node=node, obj=obj, box_x=box_x, grasp_offset_m=grasp_offset_m, tol=subframe_tol)
            node.get_logger().info(f"Validated subframes for {block_id} after set tower")

    # 2) Protrude selected block in planning scene
    if not _call_protrude(
        node,
        block_index=block_index,
        distance_m=protrude_distance_m,
        axis=protrude_axis,
        timeout_sec=10.0,
    ):
        rclpy.shutdown()
        return 11

    # 3) Send extract-middle action
    client = ActionClient(node, JengaExtractMiddleBlock, action_name)
    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 12

    block = scene_cache.wait_for_object_pose(block_id, timeout_sec=scene_timeout_sec)
    if block is None:
        node.get_logger().error(
            f"Failed to read pose for {block_id} from {planning_scene_topic} (timeout {scene_timeout_sec:.2f}s)"
        )
        rclpy.shutdown()
        return 16

    # Transform planning-scene pose into the goal_frame expected by MTC.
    src = (block.header.frame_id or "").strip() or "world"
    dst = (goal_frame or "").strip() or "world"
    if src != dst:
        try:
            tf = tf_buffer.lookup_transform(
                dst,
                src,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=float(tf_timeout_sec)),
            )
            block = do_transform_pose_stamped(block, tf)
            block.header.frame_id = dst
        except TransformException as exc:
            node.get_logger().warn(f"TF lookup failed: {src} -> {dst}: {exc}")

    if validate_subframes:
        obj = scene_cache.wait_for_collision_object(block_id, timeout_sec=scene_timeout_sec)
        if obj is None:
            node.get_logger().error(f"Failed to read CollisionObject for {block_id} from {planning_scene_topic}")
            rclpy.shutdown()
            return 18
        try:
            _validate_subframes(node=node, obj=obj, box_x=box_x, grasp_offset_m=grasp_offset_m, tol=subframe_tol)
            node.get_logger().info(f"Validated subframes for {block_id} before sending extract-middle goal")
        except AssertionError as exc:
            node.get_logger().error(f"Subframe validation failed for {block_id}: {exc}")
            rclpy.shutdown()
            return 19
    node.get_logger().info(
        f"Using planning-scene pose for {block_id} in frame '{block.header.frame_id}': "
        f"p=({block.pose.position.x:.3f},{block.pose.position.y:.3f},{block.pose.position.z:.3f})"
    )

    try:
        layout_path = _resolve_layout_path(layout_path_param)
        data = _load_yaml(layout_path)
        p = data.get("parametric", {})
        tower = p.get("tower", {})
        base = tower.get("base", {})
        base_x = float(base.get("x", 0.0))
        base_y = float(base.get("y", 0.0))
        base_z = float(base.get("z", float(p.get("stock", {}).get("z", 0.0138))))
        oq = p.get("orientation_place", {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0})
        q_place = _q_normalize(
            float(oq.get("x", 0.0)),
            float(oq.get("y", 0.0)),
            float(oq.get("z", 0.0)),
            float(oq.get("w", 1.0)),
        )
    except Exception as exc:
        node.get_logger().error(f"Failed to load/parse layout YAML for place pose: {exc}")
        rclpy.shutdown()
        return 17

    place = PoseStamped()
    place.header.frame_id = dst
    place.pose = Pose(
        position=Point(
            x=base_x + place_dx,
            y=base_y + place_dy,
            z=base_z + place_dz,
        ),
        orientation=q_place,
    )
    node.get_logger().info(
        f"Place pose near tower base from layout: frame='{place.header.frame_id}' "
        f"p=({place.pose.position.x:.3f},{place.pose.position.y:.3f},{place.pose.position.z:.3f})"
    )

    # Fresh stamps right before sending the goal (frame_id stays as computed).
    t = node.get_clock().now().to_msg()
    block.header.stamp = t
    place.header.stamp = t

    goal = JengaExtractMiddleBlock.Goal()
    goal.block_index = int(block_index)
    goal.block_pose = block
    goal.place_pose = place
    # Leave extract_axis empty so the server auto-detects from the planning scene,
    # unless an explicit override was supplied via --ros-args -p extract_axis:=x.
    goal.extract_axis = extract_axis_override

    axis_log = f"explicit override='{extract_axis_override}'" if extract_axis_override else "server auto-detect"
    node.get_logger().info(
        f"Sending extract-middle for block {block_index} after protrude {protrude_distance_m:.3f} m along {protrude_axis} "
        f"(extract_axis: {axis_log})..."
    )
    send_fut = client.send_goal_async(goal, feedback_callback=_on_feedback)
    rclpy.spin_until_future_complete(node, send_fut, timeout_sec=10.0)
    gh = send_fut.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Goal rejected")
        rclpy.shutdown()
        return 13

    res_fut = gh.get_result_async()
    rclpy.spin_until_future_complete(node, res_fut, timeout_sec=600.0)
    wrapped = res_fut.result()
    if wrapped is None:
        rclpy.shutdown()
        return 14

    jr = wrapped.result
    if jr.success:
        node.get_logger().info(f"Result OK: {jr.message}")
        rclpy.shutdown()
        return 0

    node.get_logger().error(f"Result FAIL: {jr.message} (code {jr.error_code})")
    rclpy.shutdown()
    return 15


if __name__ == "__main__":
    sys.exit(main())

