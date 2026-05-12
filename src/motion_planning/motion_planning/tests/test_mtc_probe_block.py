"""
Send a JengaProbeBlock action to mtc_probe_block_server.

1) Call set_jenga_blocks_tower_layout (planning scene assembled tower)
2) Read the selected block pose from the planning scene
3) Send the probe action with block_index and that pose (optional TF into goal_frame)
"""

from __future__ import annotations

import sys
import time
from typing import Any, Optional
import time
from typing import Any, Optional

import rclpy
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import PlanningScene
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import PlanningScene
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_srvs.srv import Trigger
from tf2_geometry_msgs import do_transform_pose_stamped
from tf2_ros import Buffer, TransformException, TransformListener

from jenga_interfaces.action import JengaProbeBlock

_OUTCOME_NAMES = {0: "UNKNOWN", 1: "LOOSE", 2: "STUCK", 3: "ERROR"}


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
        for obj in msg.world.collision_objects:
            if not obj.id or not obj.primitive_poses:
                continue
            ps = PoseStamped()
            ps.header.frame_id = obj.header.frame_id or "world"
            ps.header.stamp = msg.robot_state.joint_state.header.stamp
            ps.pose = obj.primitive_poses[0]
            self._objects[obj.id] = ps
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


def _call_trigger(node: Node, name: str, timeout_sec: float = 10.0) -> bool:
    cli = node.create_client(Trigger, name)
    if not cli.wait_for_service(timeout_sec=timeout_sec):
        node.get_logger().error(f"Service not available: {name}")
        return False
    fut = cli.call_async(Trigger.Request())
    rclpy.spin_until_future_complete(node, fut, timeout_sec=timeout_sec)
    resp = fut.result()
    if not resp or not resp.success:
        node.get_logger().error(f"{name} failed: {getattr(resp, 'message', '<no message>')}")
        return False
    node.get_logger().info(f"{name}: {resp.message}")
    return True


def _on_feedback(fb) -> None:  # noqa: ANN001
    try:
        f = fb.feedback
        print(f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%")
    except (AttributeError, TypeError):
        pass


def _format_result(jr) -> str:
    outcome_str = _OUTCOME_NAMES.get(jr.probe_outcome, f"?({jr.probe_outcome})")
    return (
        f"message={jr.message} score={jr.score:.3f} "
        f"outcome={outcome_str} displacement={jr.displacement_m:.4f} m "
        f"max_force={jr.max_force_n:.2f} N"
    )


def _format_result(jr) -> str:
    outcome_str = _OUTCOME_NAMES.get(jr.probe_outcome, f"?({jr.probe_outcome})")
    return (
        f"message={jr.message} score={jr.score:.3f} "
        f"outcome={outcome_str} displacement={jr.displacement_m:.4f} m "
        f"max_force={jr.max_force_n:.2f} N"
    )


def main(args=None) -> int:
    rclpy.init(args=args)
    node = Node("test_mtc_probe_block")


    action_name = str(node.declare_parameter("action_name", "jenga_probe_block").value)
    goal_frame = str(node.declare_parameter("goal_frame", "world").value)
    block_index = int(node.declare_parameter("block_index", 0).value)
    planning_scene_topic = str(node.declare_parameter("planning_scene_topic", "/planning_scene").value)
    scene_timeout_sec = float(node.declare_parameter("scene_timeout_sec", 2.0).value)
    tf_timeout_sec = float(node.declare_parameter("tf_timeout_sec", 0.5).value)
    set_tower_service = str(
        node.declare_parameter("set_tower_service", "set_jenga_blocks_tower_layout").value
    )

    scene_cache = _PlanningSceneCache(node, topic=planning_scene_topic)
    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node, spin_thread=False)

    if not _call_trigger(node, set_tower_service, timeout_sec=10.0):
        rclpy.shutdown()
        return 10

    block_id = f"block_{block_index:02d}"
    block = scene_cache.wait_for_object_pose(block_id, timeout_sec=scene_timeout_sec)
    if block is None:
        node.get_logger().error(
            f"Failed to read pose for {block_id} from {planning_scene_topic} "
            f"(timeout {scene_timeout_sec:.2f}s)"
        )
        rclpy.shutdown()
        return 16

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

    block.header.stamp = node.get_clock().now().to_msg()
    node.get_logger().info(
        f"Using planning-scene pose for {block_id} in frame '{block.header.frame_id}': "
        f"p=({block.pose.position.x:.3f},{block.pose.position.y:.3f},{block.pose.position.z:.3f})"
    )

    client = ActionClient(node, JengaProbeBlock, action_name)
    if not client.wait_for_server(timeout_sec=30.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 1

    goal = JengaProbeBlock.Goal()
    goal.block_index = block_index
    goal.block_index = block_index
    goal.block_pose = block

    node.get_logger().info("Sending FT-guided probe action...")
    node.get_logger().info("Sending FT-guided probe action...")
    send_fut = client.send_goal_async(goal, feedback_callback=_on_feedback)
    rclpy.spin_until_future_complete(node, send_fut, timeout_sec=10.0)
    gh = send_fut.result()
    if not gh or not gh.accepted:
        node.get_logger().error("Goal rejected")
        rclpy.shutdown()
        return 2
    res_fut = gh.get_result_async()
    rclpy.spin_until_future_complete(node, res_fut, timeout_sec=600.0)
    wrapped = res_fut.result()
    if wrapped is None:
        rclpy.shutdown()
        return 3
    jr = wrapped.result
    if jr.success:
        node.get_logger().info(f"Result OK: {_format_result(jr)}")
        node.get_logger().info(f"Result OK: {_format_result(jr)}")
        rclpy.shutdown()
        return 0
    node.get_logger().error(f"Result FAIL: (code {jr.error_code}) {_format_result(jr)}")
    node.get_logger().error(f"Result FAIL: (code {jr.error_code}) {_format_result(jr)}")
    rclpy.shutdown()
    return 4


if __name__ == "__main__":
    sys.exit(main())
