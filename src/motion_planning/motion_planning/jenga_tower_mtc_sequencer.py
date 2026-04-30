
"""
Sequencer: send repeated :action:`jenga_pick_place` goals for a six-layer Jenga tower (or a custom list).

- **parametric** layout: compute pick/place from stock and tower parameters (default).
- **from_file** layout: read explicit list of pick/place poses from YAML.

Publishes optional ``/remove_exclusion_zone`` (``std_msgs/String``) at start or when a
layer completes; tune :file:`config/jenga_tower_mtc_layout.yaml` to match your cell.
"""

from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path
from typing import Any

import rclpy
import yaml
from geometry_msgs.msg import Point, Pose, PoseStamped, Quaternion
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

from jenga_interfaces.action import JengaPickPlace


def _qdict_to_msg(d: dict[str, float]) -> Quaternion:
    return Quaternion(
        x=float(d.get("x", 0.0)),
        y=float(d.get("y", 0.0)),
        z=float(d.get("z", 0.0)),
        w=float(d.get("w", 1.0)),
    )


def _pdict_to_msg(d: dict[str, float]) -> Point:
    return Point(
        x=float(d.get("x", 0.0)),
        y=float(d.get("y", 0.0)),
        z=float(d.get("z", 0.0)),
    )


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


def _stock_pick_xyz_list(stock: dict[str, Any], *, n_tower: int) -> list[tuple[float, float, float]]:
    """Ordered (x, y, z) for each stock pick: rows in YAML order, y low -> high per row."""
    if "rows" in stock:
        rows = stock["rows"]
        y_centre = float(stock["y_centre"])
        z = float(stock["z"])
        step_y = float(stock["step_along_y"])
        bpr = int(stock["blocks_per_row"])
        half = (bpr - 1) / 2.0
        out: list[tuple[float, float, float]] = []
        for row in rows:
            x = float(row["x"])
            for j in range(bpr):
                y = y_centre + (j - half) * step_y
                out.append((x, y, z))
        n_stock = len(out)
        if n_stock != n_tower:
            warnings.warn(
                f"parametric.stock yields {n_stock} pick positions but tower needs "
                f"{n_tower} (blocks_per_layer * layers).",
                stacklevel=2,
            )
        return out[:n_tower] if n_stock > n_tower else out

    # Legacy: single row along -x from first_block
    s0 = stock.get("first_block", {"x": 0.3, "y": 0.3, "z": 0.02})
    step = float(stock.get("step_along_x", 0.025))
    return [
        (
            float(s0.get("x", 0.0)) - i * step,
            float(s0.get("y", 0.0)),
            float(s0.get("z", 0.0)),
        )
        for i in range(n_tower)
    ]


def _parametric_steps(data: dict[str, Any]) -> list[tuple[Pose, Pose]]:
    p = data.get("parametric", {})
    g = p.get("stock", {})
    t = p.get("tower", {})
    bpl = int(t.get("blocks_per_layer", 3))
    layers = int(t.get("layers", 6))
    n = bpl * layers
    t0 = t.get("base", {"x": 0.2, "y": 0.3, "z": 0.02})
    layer_dz = float(t.get("layer_dz", 0.018))
    slot_dx = float(t.get("slot_dx", 0.015))
    q_pick = _qdict_to_msg(p.get("orientation_pick", {"x": 0.0, "y": 0.0, "z": 0.707, "w": 0.707}))
    q_place = _qdict_to_msg(p.get("orientation_place", {"x": 0.0, "y": 0.0, "z": 0.707, "w": 0.707}))
    pick_xyz = _stock_pick_xyz_list(g, n_tower=n)
    if len(pick_xyz) < n:
        raise ValueError(
            f"Not enough stock pick positions ({len(pick_xyz)}) for tower ({n} blocks). "
            "Check parametric.stock (rows/blocks_per_row or first_block/step_along_x)."
        )
    steps_out: list[tuple[Pose, Pose]] = []
    for i in range(n):
        layer = i // bpl
        slot = i % bpl
        px, py, pz = pick_xyz[i]
        pick = Pose(
            position=Point(x=px, y=py, z=pz),
            orientation=q_pick,
        )
        slot_offset = (slot - 1.0) * slot_dx
        place = Pose(
            position=Point(
                x=float(t0.get("x", 0.0)) + slot_offset,
                y=float(t0.get("y", 0.0)),
                z=float(t0.get("z", 0.0)) + layer * layer_dz,
            ),
            orientation=q_place,
        )
        steps_out.append((pick, place))
    return steps_out


def _explicit_steps(data: dict[str, Any]) -> list[tuple[Pose, Pose]]:
    out: list[tuple[Pose, Pose]] = []
    for item in data.get("steps", []):
        pick_d = item.get("pick", {})
        pl_d = item.get("place", {})
        ppos = _pdict_to_msg(pick_d.get("position", pick_d))
        pq = _qdict_to_msg(pick_d.get("orientation", {"w": 1.0}))
        ppo = _pdict_to_msg(pl_d.get("position", pl_d))
        pq2 = _qdict_to_msg(pl_d.get("orientation", {"w": 1.0}))
        out.append(
            (Pose(position=ppos, orientation=pq), Pose(position=ppo, orientation=pq2))
        )
    return out


def _fb_log(node: Node):
    def _inner(fb) -> None:  # noqa: ANN001
        try:
            f = fb.feedback
            node.get_logger().info(
                f"  [feedback] {f.current_stage} {f.progress_pct:.0f}%"
            )
        except (AttributeError, TypeError):
            pass

    return _inner


def main(args: list[str] | None = None) -> int:
    rclpy.init(args=args)
    node = Node("jenga_tower_mtc_sequencer")
    layout_path_param = str(node.declare_parameter("layout_path", "").value)
    action_name = str(node.declare_parameter("action_name", "jenga_pick_place").value)
    goal_frame = str(node.declare_parameter("goal_frame", "world").value)
    pre_wait_sec = float(node.declare_parameter("pre_wait_sec", 5.0).value)
    step_pause_sec = float(node.declare_parameter("step_pause_sec", 0.5).value)
    per_goal_timeout_sec = float(
        node.declare_parameter("per_goal_timeout_sec", 600.0).value
    )
    if layout_path_param:
        path = layout_path_param
    else:
        from ament_index_python.packages import get_package_share_directory

        path = str(
            Path(get_package_share_directory("motion_planning"))
            / "config"
            / "jenga_tower_mtc_layout.yaml"
        )
    try:
        data = _load_yaml(path)
    except FileNotFoundError as e:
        node.get_logger().error(str(e))
        rclpy.shutdown()
        return 1
    mode = str(data.get("layout", "parametric"))
    if mode == "parametric":
        pairs = _parametric_steps(data)
    elif mode in ("from_file", "explicit", "steps"):
        pairs = _explicit_steps(data)
    else:
        node.get_logger().error(f"Unknown layout mode: {mode}")
        rclpy.shutdown()
        return 1
    if not pairs:
        node.get_logger().error("No pick/place steps in layout (check YAML).")
        rclpy.shutdown()
        return 1

    bpl = _blocks_per_layer(data)
    remove_start = [str(x) for x in data.get("remove_zones_before_start", [])]
    after_layer_map: dict[int, list[str]] = {}
    for e in data.get("remove_zones_after_layer", []):
        li = int(e.get("after_layer", -1))
        if li < 1:
            continue
        after_layer_map[li] = [str(x) for x in e.get("zone_ids", [])]

    rm_pub = node.create_publisher(
        String,
        "/remove_exclusion_zone",
        QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE),
    )
    for zid in remove_start:
        node.get_logger().info(f"Remove exclusion zone: {zid}")
        m = String()
        m.data = zid
        rm_pub.publish(m)
        time.sleep(0.2)

    node.get_logger().info(
        f"Loaded {len(pairs)} MTC pick/place step(s) from {path} (mode={mode}, bpl={bpl})"
    )
    if pre_wait_sec > 0.0:
        time.sleep(pre_wait_sec)

    client = ActionClient(node, JengaPickPlace, action_name)
    if not client.wait_for_server(timeout_sec=120.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 2

    for idx, (pick_pose, place_pose) in enumerate(pairs):
        stamp = node.get_clock().now().to_msg()
        goal = JengaPickPlace.Goal()
        goal.block_index = int(idx)
        pick_st = PoseStamped()
        pick_st.header.frame_id = goal_frame
        pick_st.header.stamp = stamp
        pick_st.pose = pick_pose
        place_st = PoseStamped()
        place_st.header.frame_id = goal_frame
        place_st.header.stamp = stamp
        place_st.pose = place_pose
        goal.pick_pose = pick_st
        goal.place_pose = place_st
        node.get_logger().info(
            f"Step {idx + 1}/{len(pairs)}: pick {pick_pose.position.x:.3f},"
            f"{pick_pose.position.y:.3f},{pick_pose.position.z:.3f} -> "
            f"place {place_pose.position.x:.3f},"
            f"{place_pose.position.y:.3f},{place_pose.position.z:.3f}"
        )
        send_f = client.send_goal_async(goal, feedback_callback=_fb_log(node))
        rclpy.spin_until_future_complete(node, send_f, timeout_sec=30.0)
        gh = send_f.result()
        if not gh or not gh.accepted:
            node.get_logger().error("Goal rejected")
            rclpy.shutdown()
            return 3
        r_f = gh.get_result_async()
        rclpy.spin_until_future_complete(node, r_f, timeout_sec=per_goal_timeout_sec)
        wr = r_f.result()
        if wr is None:
            node.get_logger().error("No result")
            rclpy.shutdown()
            return 4
        res = wr.result
        if not res.success:
            node.get_logger().error(
                f"MTC step failed: {res.message} (code {res.error_code})"
            )
            rclpy.shutdown()
            return 5
        if step_pause_sec > 0.0:
            time.sleep(step_pause_sec)
        if (idx + 1) % bpl == 0:
            layer_done = (idx + 1) // bpl
            for zid in after_layer_map.get(layer_done, []):
                node.get_logger().info(
                    f"After layer {layer_done}: remove exclusion zone {zid}"
                )
                msg = String()
                msg.data = zid
                rm_pub.publish(msg)
                time.sleep(0.2)

    node.get_logger().info("All MTC pick/place steps completed.")
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
