#!/usr/bin/env python3
"""
One-shot check: motion_planning block_XX indices vs JengaBlockStates.block_id.

Prints YAML tower layout index → collision id mapping, then optionally compares
one perception message on /jenga/block_states (or --topic).

Usage:
  ros2 run motion_planning verify_jenga_block_ids
  ros2 run motion_planning verify_jenga_block_ids --ros-args -p layout_path:=/path/to/layout.yaml
  ros2 run motion_planning verify_jenga_block_ids --ros-args -p wait_for_perception_sec:=5.0
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import rclpy
import yaml
from geometry_msgs.msg import Pose
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from jenga_interfaces.msg import JengaBlockStates
from motion_planning.jenga_blocks_scene import _collision_object_id
from motion_planning.jenga_tower_mtc_sequencer import tower_poses_from_layout_dict


def _load_yaml(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Layout file not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _pose_summary(pose: Pose) -> str:
    p = pose.position
    o = pose.orientation
    return (
        f"pos=({p.x:.4f}, {p.y:.4f}, {p.z:.4f}) "
        f"ori=({o.x:.3f}, {o.y:.3f}, {o.z:.3f}, {o.w:.3f})"
    )


class VerifyJengaBlockIdsNode(Node):
    def __init__(self) -> None:
        super().__init__("verify_jenga_block_ids")
        layout_path = str(self.declare_parameter("layout_path", "").value)
        topic = str(self.declare_parameter("block_states_topic", "/jenga/block_states").value)
        wait_sec = float(self.declare_parameter("wait_for_perception_sec", 3.0).value)
        max_pos_delta_m = float(self.declare_parameter("max_pos_delta_m", 0.05).value)

        if not layout_path:
            from ament_index_python.packages import get_package_share_directory

            layout_path = str(
                Path(get_package_share_directory("motion_planning"))
                / "config"
                / "jenga_tower_mtc_layout.yaml"
            )

        data = _load_yaml(layout_path)
        poses = tower_poses_from_layout_dict(data)
        n = len(poses)
        self.get_logger().info(f"YAML tower layout ({layout_path}): {n} blocks")
        for i, pose in enumerate(poses):
            self.get_logger().info(f"  {_collision_object_id(i)}  {_pose_summary(pose)}")

        if wait_sec <= 0.0:
            self.get_logger().info("wait_for_perception_sec<=0; skipping perception compare.")
            return

        self._max_pos_delta_m = max_pos_delta_m
        self._yaml_poses = poses
        self._got_msg = False
        self.create_subscription(
            JengaBlockStates,
            topic,
            self._on_block_states,
            qos_profile_sensor_data,
        )
        self.get_logger().info(f"Waiting up to {wait_sec:.1f}s for one message on {topic} ...")
        self._timer = self.create_timer(wait_sec, self._on_timeout)

    def _on_block_states(self, msg: JengaBlockStates) -> None:
        if self._got_msg:
            return
        self._got_msg = True
        self._timer.cancel()

        frame = msg.header.frame_id or "<empty>"
        self.get_logger().info(
            f"Perception message: frame_id={frame!r}, {len(msg.blocks)} block(s)"
        )
        mismatches = 0
        for block in sorted(msg.blocks, key=lambda b: int(b.block_id)):
            idx = int(block.block_id)
            cid = _collision_object_id(idx)
            self.get_logger().info(f"  {cid}  {_pose_summary(block.pose)}")
            if idx < 0 or idx >= len(self._yaml_poses):
                self.get_logger().warning(f"  {cid}: block_id out of YAML range 0..{len(self._yaml_poses)-1}")
                mismatches += 1
                continue
            yaml_pose = self._yaml_poses[idx]
            dx = float(block.pose.position.x) - float(yaml_pose.position.x)
            dy = float(block.pose.position.y) - float(yaml_pose.position.y)
            dz = float(block.pose.position.z) - float(yaml_pose.position.z)
            dist = (dx * dx + dy * dy + dz * dz) ** 0.5
            if dist > self._max_pos_delta_m:
                self.get_logger().warning(
                    f"  {cid}: position delta {dist*1000:.1f} mm vs YAML "
                    f"(threshold {self._max_pos_delta_m*1000:.0f} mm)"
                )
                mismatches += 1

        if mismatches:
            self.get_logger().error(
                f"Verification: {mismatches} issue(s). Align perception block_index with "
                "motion_planning block_XX or recalibrate frames."
            )
        else:
            self.get_logger().info(
                "Verification OK: all reported block_id values map to block_XX within threshold."
            )

    def _on_timeout(self) -> None:
        if not self._got_msg:
            self.get_logger().warning(
                "No JengaBlockStates received; YAML index table printed only. "
                "Start perception or publish to the topic and re-run."
            )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = VerifyJengaBlockIdsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
