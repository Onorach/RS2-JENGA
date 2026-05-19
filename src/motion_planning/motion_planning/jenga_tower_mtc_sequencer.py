
"""
Sequencer: send repeated :action:`jenga_pick_place` goals for a six-layer Jenga tower (or a custom list).

- **parametric** layout: compute pick/place from stock and tower parameters (default).
- **from_file** layout: read explicit list of pick/place poses from YAML.
"""

from __future__ import annotations

import math
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

from jenga_interfaces.action import JengaArmReady, JengaPickPlace


def _q_normalize(x: float, y: float, z: float, w: float) -> tuple[float, float, float, float]:
    n2 = x * x + y * y + z * z + w * w
    if n2 <= 0.0:
        return (0.0, 0.0, 0.0, 1.0)
    inv = 1.0 / math.sqrt(n2)
    return (x * inv, y * inv, z * inv, w * inv)


def _q_mul(
    ax: float, ay: float, az: float, aw: float, bx: float, by: float, bz: float, bw: float
) -> tuple[float, float, float, float]:
    # Hamilton product: q = a ⊗ b
    return (
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    )


def _q_from_yaw(yaw_rad: float) -> tuple[float, float, float, float]:
    h = 0.5 * yaw_rad
    return (0.0, 0.0, math.sin(h), math.cos(h))


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


def _stock_pick_xyz_list(stock: dict[str, Any], *, n_tower: int) -> list[tuple[float, float, float]]:
    """Ordered (x, y, z) for each stock pick: rows in YAML order (optional dz per row), y low -> high per row."""
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
            dz = float(row.get("dz", 0.0151))
            z_row = z + dz
            for j in range(bpr):
                y = y_centre + (j - half) * step_y
                out.append((x, y, z_row))
        n_stock = len(out)
        if n_stock != n_tower:
            warnings.warn(
                f"parametric.stock yields {n_stock} pick positions but tower needs "
                f"{n_tower} (blocks_per_layer * layers).",
                stacklevel=2,
            )
        return out[:n_tower] if n_stock > n_tower else out

    # Legacy: single row along -x from first_block
    s0 = stock.get("first_block", {"x": 0.3, "y": 0.297, "z": 0.0138})
    step = float(stock.get("step_along_x", 0.0251))
    return [
        (
            float(s0.get("x", 0.0)) - i * step,
            float(s0.get("y", 0.0)),
            float(s0.get("z", 0.0)),
        )
        for i in range(n_tower)
    ]


def _parametric_tower_poses(data: dict[str, Any]) -> list[Pose]:
    """Place poses for a parametric tower only (no stock / pick layout required)."""
    p = data.get("parametric", {})
    t = p.get("tower", {})
    bpl = int(t.get("blocks_per_layer", 3))
    layers = int(t.get("layers", 6))
    n = bpl * layers
    t0 = t.get("base", {"x": 0.2, "y": 0.297, "z": 0.0138})
    layer_dz = float(t.get("layer_dz", 0.0151))
    slot_dx = float(t.get("slot_dx", 0.0251))
    tower_yaw_deg = float(t.get("tower_yaw_deg", 45.0))
    tower_yaw_rad = math.radians(tower_yaw_deg)
    q_place = _qdict_to_msg(p.get("orientation_place", {"x": 0.0, "y": 0.0, "z": 0.707, "w": 0.707}))
    q_place_base = _q_normalize(q_place.x, q_place.y, q_place.z, q_place.w)
    out: list[Pose] = []
    c = math.cos(tower_yaw_rad)
    s = math.sin(tower_yaw_rad)
    for i in range(n):
        layer = i // bpl
        slot = i % bpl
        slot_offset = (slot - 1.0) * slot_dx
        if (layer % 2) == 0:
            off_lx, off_ly = slot_offset, 0.0
            layer_yaw = 0.0
        else:
            off_lx, off_ly = 0.0, slot_offset
            layer_yaw = 0.5 * math.pi
        off_x = c * off_lx - s * off_ly
        off_y = s * off_lx + c * off_ly
        q_yaw = _q_from_yaw(tower_yaw_rad + layer_yaw)
        qx, qy, qz, qw = _q_mul(q_yaw[0], q_yaw[1], q_yaw[2], q_yaw[3], *q_place_base)
        qx, qy, qz, qw = _q_normalize(qx, qy, qz, qw)
        out.append(
            Pose(
                position=Point(
                    x=float(t0.get("x", 0.0)) + off_x,
                    y=float(t0.get("y", 0.0)) + off_y,
                    z=float(t0.get("z", 0.0)) + layer * layer_dz,
                ),
                orientation=Quaternion(x=qx, y=qy, z=qz, w=qw),
            )
        )
    return out


def tower_poses_from_layout_dict(data: dict[str, Any]) -> list[Pose]:
    """Tower (assembled) poses per block index; same geometry as MTC place poses."""
    mode = str(data.get("layout", "parametric"))
    if mode == "parametric":
        return _parametric_tower_poses(data)
    if mode in ("from_file", "explicit", "steps"):
        return [place for _, place in _explicit_steps(data)]
    raise ValueError(f"Unknown layout mode: {mode}")


def _parametric_steps(data: dict[str, Any]) -> list[tuple[Pose, Pose]]:
    p = data.get("parametric", {})
    g = p.get("stock", {})
    t = p.get("tower", {})
    bpl = int(t.get("blocks_per_layer", 3))
    layers = int(t.get("layers", 6))
    n = bpl * layers
    q_pick = _qdict_to_msg(p.get("orientation_pick", {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}))
    pick_xyz = _stock_pick_xyz_list(g, n_tower=n)
    if len(pick_xyz) < n:
        raise ValueError(
            f"Not enough stock pick positions ({len(pick_xyz)}) for tower ({n} blocks). "
            "Check parametric.stock (rows/blocks_per_row or first_block/step_along_x)."
        )
    tower_poses = _parametric_tower_poses(data)
    steps_out: list[tuple[Pose, Pose]] = []
    for i in range(n):
        px, py, pz = pick_xyz[i]
        pick = Pose(
            position=Point(x=px, y=py, z=pz),
            orientation=q_pick,
        )
        steps_out.append((pick, tower_poses[i]))
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

def _run_arm_ready_action(
    node: Node,
    client: ActionClient,
    *,
    timeout_sec: float,
    label: str,
) -> int:
    """Send JengaArmReady with empty target_state (server default). Returns 0 on success."""
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
        node.get_logger().error(
            f"{label}: arm ready failed: {res.message} (code {res.error_code})"
        )
        return 8
    return 0

def main(args: list[str] | None = None) -> int:
    rclpy.init(args=args)
    node = Node("jenga_tower_mtc_sequencer")
    layout_path_param = str(node.declare_parameter("layout_path", "").value)
    action_name = str(node.declare_parameter("action_name", "jenga_pick_place").value)
    ready_action_name = str(node.declare_parameter("ready_action_name", "jenga_arm_ready").value)
    goal_frame = str(node.declare_parameter("goal_frame", "world").value)
    pre_wait_sec = float(node.declare_parameter("pre_wait_sec", 1.0).value)
    step_pause_sec = float(node.declare_parameter("step_pause_sec", 0.5).value)
    per_goal_timeout_sec = float(
        node.declare_parameter("per_goal_timeout_sec", 600.0).value
    )
    per_ready_timeout_sec = float(
        node.declare_parameter("per_ready_timeout_sec", per_goal_timeout_sec).value
    )
    start_block_index = int(node.declare_parameter("start_block_index", 0).value)
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

    n_pairs = len(pairs)
    if start_block_index < 0 or start_block_index > n_pairs:
        node.get_logger().error(
            f"Invalid start_block_index={start_block_index} for {n_pairs} step(s); "
            f"allowed range is 0 .. {n_pairs} inclusive (use {n_pairs} when all steps are already done)."
        )
        rclpy.shutdown()
        return 9

    node.get_logger().info(
        f"Loaded {n_pairs} MTC pick/place step(s) from {path} (mode={mode})"
    )
    if start_block_index > 0:
        node.get_logger().info(
            f"Resuming: first step to run is index {start_block_index} "
            f"(1-based step {start_block_index + 1}/{n_pairs}, block_index={start_block_index})."
        )
    if start_block_index == n_pairs:
        node.get_logger().info(
            "start_block_index equals step count: no pick/place goals will be sent; "
            "running arm-ready bookends only."
        )
    if pre_wait_sec > 0.0:
        time.sleep(pre_wait_sec)

    client = ActionClient(node, JengaPickPlace, action_name)
    if not client.wait_for_server(timeout_sec=120.0):
        node.get_logger().error(f"Action server not available: {action_name}")
        rclpy.shutdown()
        return 2

    ready_client = ActionClient(node, JengaArmReady, ready_action_name)
    if not ready_client.wait_for_server(timeout_sec=120.0):
        node.get_logger().error(f"Action server not available: {ready_action_name}")
        rclpy.shutdown()
        return 2
    rc = _run_arm_ready_action(
        node,
        ready_client,
        timeout_sec=per_ready_timeout_sec,
        label="Tower start",
    )
    if rc != 0:
        rclpy.shutdown()
        return rc

    for idx in range(start_block_index, n_pairs):
        pick_pose, place_pose = pairs[idx]
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
            f"Step {idx + 1}/{n_pairs} (block_index={idx}): pick {pick_pose.position.x:.3f},"
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

    if start_block_index >= n_pairs:
        node.get_logger().info("No MTC pick/place steps were run (empty run).")
    elif start_block_index > 0:
        node.get_logger().info("All remaining MTC pick/place steps completed.")
    else:
        node.get_logger().info("All MTC pick/place steps completed.")
    rc = _run_arm_ready_action(
        node,
        ready_client,
        timeout_sec=per_ready_timeout_sec,
        label="Tower end",
    )
    if rc != 0:
        rclpy.shutdown()
        return rc
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
