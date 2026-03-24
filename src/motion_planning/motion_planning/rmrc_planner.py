# Copyright 2025 RS2-JENGA
# BSD-3-Clause

"""
RMRC (Resolved Motion Rate Control) planner for Cartesian collision-free trajectories.
Uses Jacobian-based velocity control with potential-field collision avoidance.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Any

import numpy as np

# Shape primitives (shape_msgs/SolidPrimitive)
SOLID_PRIMITIVE_BOX = 1
SOLID_PRIMITIVE_SPHERE = 2

# Joint names for UR3e (must match controller order)
UR3E_JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

# Default chain: base_link to tool0 for UR3e
DEFAULT_BASE_LINK = "base_link"
DEFAULT_EE_LINK = "tool0"


@dataclass
class Obstacle:
    """Obstacle for collision avoidance (frame_id = base_link)."""

    obs_type: str  # "box" or "sphere"
    center: tuple[float, float, float]
    size_or_radius: tuple[float, ...]  # (x,y,z) for box, (r,) for sphere


def _collision_object_to_obstacle(co: Any, frame_id: str = "base_link") -> Obstacle | None:
    """
    Convert a moveit_msgs CollisionObject to an Obstacle.
    Assumes object frame_id matches or is transformable to frame_id.
    """
    if co.header.frame_id != frame_id:
        return None
    if not co.primitives or not co.primitive_poses:
        return None
    prim = co.primitives[0]
    pose = co.primitive_poses[0]
    cx = pose.position.x
    cy = pose.position.y
    cz = pose.position.z
    center = (cx, cy, cz)
    if prim.type == SOLID_PRIMITIVE_BOX:
        return Obstacle("box", center, (prim.dimensions[0], prim.dimensions[1], prim.dimensions[2]))
    if prim.type == SOLID_PRIMITIVE_SPHERE:
        return Obstacle("sphere", center, (prim.dimensions[0],))
    return None


def obstacles_from_yaml_data(zones: list[dict], frame_id: str = "base_link") -> list[Obstacle]:
    """Build Obstacle list from exclusion_zones YAML structure."""
    result: list[Obstacle] = []
    for entry in zones:
        f = entry.get("frame_id", frame_id)
        if f != frame_id:
            continue
        t = entry.get("type", "").lower()
        if t == "box":
            pos = entry["position"]
            sz = entry["size"]
            result.append(Obstacle("box", (float(pos[0]), float(pos[1]), float(pos[2])), (float(sz[0]), float(sz[1]), float(sz[2]))))
        elif t == "sphere":
            cen = entry["center"]
            r = entry["radius"]
            result.append(Obstacle("sphere", (float(cen[0]), float(cen[1]), float(cen[2])), (float(r),)))
    return result


def _distance_point_to_box(point: np.ndarray, center: np.ndarray, half_extents: np.ndarray) -> float:
    """Signed distance from point to axis-aligned box (positive outside)."""
    d = np.abs(point - center) - half_extents
    return float(np.linalg.norm(np.maximum(d, 0)) + min(0, np.max(d)))


def _distance_point_to_sphere(point: np.ndarray, center: np.ndarray, radius: float) -> float:
    """Signed distance from point to sphere (positive outside)."""
    return float(np.linalg.norm(point - center) - radius)


def distance_to_obstacles(ee_pos: np.ndarray, obstacles: list[Obstacle]) -> float:
    """
    Minimum signed distance from ee_pos to any obstacle.
    Positive = outside, negative = inside.
    """
    p = np.array(ee_pos, dtype=np.float64)
    min_d = float("inf")
    for obs in obstacles:
        c = np.array(obs.center, dtype=np.float64)
        if obs.obs_type == "box":
            half = np.array(obs.size_or_radius, dtype=np.float64) / 2.0
            d = _distance_point_to_box(p, c, half)
        else:
            r = obs.size_or_radius[0]
            d = _distance_point_to_sphere(p, c, r)
        min_d = min(min_d, d)
    return min_d if obstacles else float("inf")


def _repulsion_gradient(ee_pos: np.ndarray, obstacles: list[Obstacle], d_safe: float) -> np.ndarray:
    """
    Gradient of potential U = 1/d^2 for d < d_safe.
    Returns 6-vector (3 linear + 3 angular); angular part zero (repulsion affects position).
    """
    p = np.array(ee_pos, dtype=np.float64)
    grad_linear = np.zeros(3)
    for obs in obstacles:
        c = np.array(obs.center, dtype=np.float64)
        if obs.obs_type == "sphere":
            diff = p - c
            dist = np.linalg.norm(diff)
            if dist < 1e-8:
                continue
            d = dist - obs.size_or_radius[0]
            if d < d_safe and d > 1e-6:
                # U = 1/d^2, grad_U = -2/d^3 * (p - c) / |p - c| * (derivative of d w.r.t. p)
                # d = |p - c| - r, so grad d = (p - c) / |p - c|
                grad_d = diff / dist
                grad_U = -2.0 / (d**3) * grad_d
                grad_linear += grad_U
        else:
            half = np.array(obs.size_or_radius, dtype=np.float64) / 2.0
            d = _distance_point_to_box(p, c, half)
            if d < d_safe and d > 1e-6:
                # Approximate gradient for box: push along shortest direction to surface
                to_center = c - p
                for i in range(3):
                    if p[i] < c[i] - half[i]:
                        grad_linear[i] += 2.0 / (d**3)
                    elif p[i] > c[i] + half[i]:
                        grad_linear[i] -= 2.0 / (d**3)
    return np.concatenate([grad_linear, np.zeros(3)])


def damped_pseudo_inverse(J: np.ndarray, lam: float = 0.01) -> np.ndarray:
    """Damped least-squares pseudo-inverse: J+ = J^T (J J^T + lam^2 I)^-1."""
    m, n = J.shape
    if m <= n:
        return np.linalg.pinv(J, rcond=1e-6)
    JJt = J @ J.T + (lam**2) * np.eye(m)
    return J.T @ np.linalg.inv(JJt)


def quaternion_to_rotation_matrix(q: np.ndarray) -> np.ndarray:
    """q = [x, y, z, w], returns 3x3 R."""
    x, y, z, w = q[0], q[1], q[2], q[3]
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
        [2*(x*y + z*w), 1 - 2*(x*x + z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x*x + y*y)],
    ], dtype=np.float64)


def rotation_matrix_to_quaternion(R: np.ndarray) -> np.ndarray:
    """3x3 R -> [x, y, z, w]."""
    trace = np.trace(R)
    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        w = 0.25 / s
        x = (R[2, 1] - R[1, 2]) * s
        y = (R[0, 2] - R[2, 0]) * s
        z = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    q = np.array([x, y, z, w], dtype=np.float64)
    return q / np.linalg.norm(q)


def slerp(q0: np.ndarray, q1: np.ndarray, t: float) -> np.ndarray:
    """Spherical linear interpolation between quaternions. t in [0, 1]."""
    dot = np.dot(q0, q1)
    if dot < 0:
        q1 = -q1
        dot = -dot
    if dot > 0.9995:
        result = q0 + t * (q1 - q0)
        return result / np.linalg.norm(result)
    theta_0 = np.arccos(np.clip(dot, -1, 1))
    sin_theta = np.sin(theta_0)
    a = np.sin((1 - t) * theta_0) / sin_theta
    b = np.sin(t * theta_0) / sin_theta
    return a * q0 + b * q1


def cartesian_path_interpolation(
    pose_start: tuple[np.ndarray, np.ndarray],
    pose_end: tuple[np.ndarray, np.ndarray],
    resolution_m: float = 0.002,
    max_duration_s: float = 30.0,
) -> list[tuple[float, np.ndarray, np.ndarray]]:
    """
    Linear interpolation in position, SLERP in orientation.
    pose_start, pose_end: (position 3-vec, quaternion [x,y,z,w])
    Returns list of (t, position, quaternion) with t in seconds.
    """
    pos0, q0 = np.array(pose_start[0]), np.array(pose_start[1])
    pos1, q1 = np.array(pose_end[0]), np.array(pose_end[1])
    dist = np.linalg.norm(pos1 - pos0)
    n_steps = max(1, int(dist / resolution_m))
    n_steps = min(n_steps, int(max_duration_s / 0.02))
    result: list[tuple[float, np.ndarray, np.ndarray]] = []
    for i in range(n_steps + 1):
        s = i / n_steps if n_steps > 0 else 1.0
        t = s * max_duration_s * (dist / (resolution_m * n_steps)) if dist > 1e-9 else s * 2.0
        pos = pos0 + s * (pos1 - pos0)
        q = slerp(q0, q1, s)
        result.append((t, pos, q))
    return result


class RMRCPlanner:
    """
    RMRC planner using ikpy for kinematics and numerical Jacobian.
    """

    def __init__(
        self,
        urdf_content: str,
        base_link: str = DEFAULT_BASE_LINK,
        ee_link: str = DEFAULT_EE_LINK,
        joint_names: list[str] | None = None,
    ):
        try:
            from ikpy.chain import Chain
        except ImportError:
            raise ImportError("ikpy is required for RMRC. Install with: pip install ikpy")
        self._joint_names = joint_names or list(UR3E_JOINT_NAMES)
        # ikpy does not support "continuous" joints; UR robots use it for shoulder_pan.
        # Replace with "revolute" (mathematically identical for FK/IK).
        urdf_content = urdf_content.replace('type="continuous"', 'type="revolute"')
        urdf_content = urdf_content.replace("type='continuous'", "type='revolute'")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".urdf", delete=False) as f:
            f.write(urdf_content)
            urdf_path = f.name
        try:
            chain_raw = Chain.from_urdf_file(
                urdf_path,
                base_elements=[base_link],
                last_link_vector=[0, 0, 0],
                active_links_mask=None,
            )
        finally:
            os.unlink(urdf_path)
        # Rebuild with mask so only revolute joints are active (fixes 10 vs 6 DoF mismatch).
        revolute_mask = []
        for link in chain_raw.links:
            jt = getattr(link, "joint_type", "fixed")
            revolute_mask.append(jt in ("revolute", "prismatic"))
        revolute_mask[-1] = False  # last link always inactive per ikpy
        self._chain = Chain(
            chain_raw.links,
            active_links_mask=revolute_mask,
            name=chain_raw.name,
            urdf_metadata=getattr(chain_raw, "_urdf_metadata", None),
        )
        self._base_link = base_link
        self._ee_link = ee_link
        self._n_active = int(np.sum(self._chain.active_links_mask))
        self._jacobian_eps = 1e-6

    def _chain_joints_from_dict(self, q_dict: dict[str, float]) -> list[float]:
        """Map joint names to chain order (all links including fixed)."""
        full = [0.0] * len(self._chain.links)
        for i, link in enumerate(self._chain.links):
            name = getattr(link, "name", None)
            if name and name in q_dict:
                full[i] = float(q_dict[name])
        return full

    def _chain_joints_from_list(self, q: list[float]) -> list[float]:
        """Map our n_active joint values to full chain using active_to_full."""
        n_links = len(self._chain.links)
        n_q = len(q)
        if n_q == n_links:
            return list(q)
        active = np.array([float(x) for x in q], dtype=np.float64)
        initial = np.zeros(n_links, dtype=np.float64)
        full = self._chain.active_to_full(active, initial)
        return full.tolist()

    def compute_ee_pose(self, q: list[float] | dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
        """Returns (position 3-vec, quaternion [x,y,z,w])."""
        if isinstance(q, dict):
            j = self._chain_joints_from_dict(q)
        else:
            j = self._chain_joints_from_list(q)
        T = self._chain.forward_kinematics(j)
        pos = T[:3, 3].copy()
        R = T[:3, :3]
        quat = rotation_matrix_to_quaternion(R)
        return pos, quat

    def compute_jacobian(self, q: list[float] | dict[str, float]) -> np.ndarray:
        """6 x n_active geometric Jacobian (linear + angular velocity)."""
        if isinstance(q, dict):
            j = self._chain_joints_from_dict(q)
        else:
            j = self._chain_joints_from_list(q)
        j = np.array(j, dtype=np.float64)
        n = len(j)
        pos, _ = self.compute_ee_pose(list(j))
        R = self._chain.forward_kinematics(list(j))[:3, :3]
        J = np.zeros((6, n))
        eps = self._jacobian_eps
        for i in range(n):
            jp = j.copy()
            jp[i] += eps
            pos_p, _ = self.compute_ee_pose(list(jp))
            Rp = self._chain.forward_kinematics(list(jp))[:3, :3]
            J[:3, i] = (pos_p - pos) / eps
            dR = (Rp - R) / eps
            skew = dR @ R.T
            J[3, i] = skew[2, 1]
            J[4, i] = skew[0, 2]
            J[5, i] = skew[1, 0]
        active = self._chain.active_links_mask
        if active is not None and np.any(~active):
            J = J[:, active]
        return J

    def rmrc_step(
        self,
        q: np.ndarray,
        v_desired: np.ndarray,
        obstacles: list[Obstacle],
        d_safe: float = 0.05,
        k_repulsion: float = 0.5,
        lambda_damped: float = 0.01,
        q_min: np.ndarray | None = None,
        q_max: np.ndarray | None = None,
        max_joint_velocity: float | None = None,
    ) -> np.ndarray:
        """
        Compute q_dot for one RMRC step.
        v_desired: 6-vector [vx, vy, vz, wx, wy, wz]
        Returns n_active joint velocities.
        """
        pos, _ = self.compute_ee_pose(q.tolist())
        J = self.compute_jacobian(q.tolist())
        Jpinv = damped_pseudo_inverse(J, lambda_damped)
        q_dot_main = Jpinv @ np.array(v_desired, dtype=np.float64)
        q_dot_null = _repulsion_gradient(pos, obstacles, d_safe)
        N = np.eye(J.shape[1]) - Jpinv @ J
        q_dot_null_proj = N @ (Jpinv @ np.zeros(6))
        if np.linalg.norm(q_dot_null) > 1e-8:
            q_dot_null_proj = N @ (Jpinv @ q_dot_null)
        q_dot = q_dot_main + k_repulsion * q_dot_null_proj
        if q_min is not None and q_max is not None:
            for i in range(len(q_dot)):
                if q[i] <= q_min[i] and q_dot[i] < 0:
                    q_dot[i] = 0.0
                elif q[i] >= q_max[i] and q_dot[i] > 0:
                    q_dot[i] = 0.0
        if max_joint_velocity is not None and max_joint_velocity > 0.0:
            q_dot = np.clip(q_dot, -max_joint_velocity, max_joint_velocity)
        return q_dot

    def plan_rmrc_trajectory(
        self,
        q_start: np.ndarray,
        pose_target: tuple[np.ndarray, np.ndarray],
        obstacles: list[Obstacle],
        path_resolution_m: float = 0.002,
        max_velocity_scale: float = 0.5,
        dt: float = 0.02,
        d_safe: float = 0.05,
        k_repulsion: float = 0.5,
        max_joint_velocity: float = 0.6,
        max_joint_acceleration: float = 1.2,
        max_steps: int = 10000,
    ) -> list[tuple[float, np.ndarray]]:
        """
        Plan collision-free RMRC trajectory from q_start to target pose.
        Returns list of (time_from_start, joint_positions).
        """
        pos_start, q_start_quat = self.compute_ee_pose(q_start.tolist())
        pose_target_pos = np.array(pose_target[0], dtype=np.float64)
        pose_target_quat = np.array(pose_target[1], dtype=np.float64)
        path = cartesian_path_interpolation(
            (pos_start, q_start_quat),
            (pose_target_pos, pose_target_quat),
            resolution_m=path_resolution_m,
        )
        if len(path) < 2:
            return [(0.0, q_start)]
        trajectory: list[tuple[float, np.ndarray]] = [(0.0, np.array(q_start, dtype=np.float64).copy())]
        q = np.array(q_start, dtype=np.float64)
        q_dot_prev = np.zeros_like(q)
        t_total = 0.0
        prev_pos, prev_quat = path[0][1], path[0][2]
        for step in range(max_steps):
            idx = min(step + 1, len(path) - 1)
            t_next, pos_next, q_next = path[idx]
            dt_step = min(dt, t_next - (path[idx - 1][0] if idx > 0 else 0))
            if dt_step <= 0:
                dt_step = dt
            v_linear = (pos_next - prev_pos) / dt_step
            dq_q = q_next - prev_quat
            if np.dot(prev_quat, dq_q) < 0:
                dq_q = -dq_q
            angle = np.arccos(np.clip(np.dot(prev_quat, q_next), -1, 1))
            if angle > 1e-8:
                axis = np.cross(prev_quat[:3], q_next[:3]) + prev_quat[3] * q_next[:3] - q_next[3] * prev_quat[:3]
                n = np.linalg.norm(axis)
                if n > 1e-8:
                    omega = axis / n * (angle / dt_step)
                else:
                    omega = np.zeros(3)
            else:
                omega = np.zeros(3)
            v_desired = np.concatenate([v_linear * max_velocity_scale, omega * max_velocity_scale])
            q_dot = self.rmrc_step(
                q,
                v_desired,
                obstacles,
                d_safe=d_safe,
                k_repulsion=k_repulsion,
                max_joint_velocity=max_joint_velocity,
            )
            if max_joint_acceleration > 0.0:
                dqdot_limit = max_joint_acceleration * dt_step
                q_dot = np.clip(q_dot, q_dot_prev - dqdot_limit, q_dot_prev + dqdot_limit)
            q = q + q_dot * dt_step
            q_dot_prev = q_dot
            t_total += dt_step
            trajectory.append((t_total, q.copy()))
            prev_pos, prev_quat = pos_next, q_next
            if idx >= len(path) - 1:
                break
        return trajectory
