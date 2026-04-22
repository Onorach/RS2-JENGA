
"""
RMRC (Resolved Motion Rate Control) planner for Cartesian collision-free trajectories.
Uses Jacobian-based velocity control with potential-field collision avoidance.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any

import numpy as np

from motion_planning.kinematics_backends import (
    KinematicsBackend,
    Pose,
    PyKDLKinematicsBackend,
    URAnalyticalIKBackend,
)

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

# Multi-point repulsion: link frame origins in base_link, with relative weights.
# Higher weights on upper_arm / forearm keep the middle of the arm away from cabinet/tower.
UR3E_REPULSION_LINK_SPECS: tuple[tuple[str, float], ...] = (
    ("shoulder_link", 0.35),
    ("upper_arm_link", 0.95),
    ("forearm_link", 0.95),
    ("wrist_1_link", 0.45),
    ("wrist_2_link", 0.35),
    ("wrist_3_link", 0.5),
)


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


def _repulsion_linear_at_point(
    point: np.ndarray, obstacles: list[Obstacle], d_safe: float
) -> np.ndarray:
    """
    Gradient of potential U = 1/d^2 for d < d_safe (linear part only).
    Points away from obstacles (same as -grad(U) direction along grad(d)).
    """
    p = np.array(point, dtype=np.float64)
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
                grad_d = diff / dist
                grad_linear += (2.0 / (d**3)) * grad_d
        else:
            half = np.array(obs.size_or_radius, dtype=np.float64) / 2.0
            d = _distance_point_to_box(p, c, half)
            if d < d_safe and d > 1e-6:
                q = np.clip(p, c - half, c + half)
                n = p - q
                n_norm = np.linalg.norm(n)
                if n_norm > 1e-9:
                    repulse_dir = n / n_norm
                else:
                    margins = half - np.abs(p - c)
                    axis = int(np.argmin(margins))
                    repulse_dir = np.zeros(3, dtype=np.float64)
                    repulse_dir[axis] = 1.0 if (p[axis] - c[axis]) >= 0.0 else -1.0
                grad_linear += (2.0 / (d**3)) * repulse_dir
    return grad_linear


def _repulsion_linear_weighted_multi(
    points: list[np.ndarray],
    weights: list[float],
    obstacles: list[Obstacle],
    d_safe: float,
    out_grad_cap: float | None = None,
) -> np.ndarray:
    """Sum weighted repulsion gradients at multiple points (e.g. EE + arm links)."""
    g = np.zeros(3, dtype=np.float64)
    for p, w in zip(points, weights):
        g += float(w) * _repulsion_linear_at_point(p, obstacles, d_safe)
    if out_grad_cap is not None and out_grad_cap > 0.0:
        gn = float(np.linalg.norm(g))
        if gn > out_grad_cap:
            g *= out_grad_cap / gn
    return g


def _repulsion_gradient(ee_pos: np.ndarray, obstacles: list[Obstacle], d_safe: float) -> np.ndarray:
    """
    Gradient of potential U = 1/d^2 for d < d_safe.
    Returns 6-vector (3 linear + 3 angular); angular part zero.
    """
    g = _repulsion_linear_at_point(ee_pos, obstacles, d_safe)
    return np.concatenate([g, np.zeros(3)])


def damped_pseudo_inverse(J: np.ndarray, lam: float = 0.01) -> np.ndarray:
    """Damped least-squares pseudo-inverse (consistent damping for square Jacobians)."""
    m, n = J.shape
    lam2 = lam * lam
    if m <= n:
        return np.linalg.inv(J.T @ J + lam2 * np.eye(n)) @ J.T
    return J.T @ np.linalg.inv(J @ J.T + lam2 * np.eye(m))


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


def quaternion_error_vector(q_current: np.ndarray, q_target: np.ndarray) -> np.ndarray:
    """Return 3D orientation error vector from current to target quaternion."""
    qc = np.array(q_current, dtype=np.float64)
    qt = np.array(q_target, dtype=np.float64)
    nc = np.linalg.norm(qc)
    nt = np.linalg.norm(qt)
    if nc < 1e-12 or nt < 1e-12:
        return np.zeros(3, dtype=np.float64)
    qc = qc / nc
    qt = qt / nt
    if np.dot(qc, qt) < 0.0:
        qt = -qt
    v1 = qc[:3]
    v2 = qt[:3]
    w1 = qc[3]
    w2 = qt[3]
    q_err_vec = w1 * v2 - w2 * v1 - np.cross(v2, v1)
    return 2.0 * q_err_vec


def merge_posture_joint_targets(
    q_ik: np.ndarray | None,
    q_start: np.ndarray,
    posture_targets: np.ndarray | None,
) -> np.ndarray | None:
    """
    Merge analytical IK seed with optional per-joint posture overrides (NaN = leave from IK/start).
    """
    if posture_targets is None:
        return q_ik
    pt = np.array(posture_targets, dtype=np.float64).reshape(-1)
    if pt.size != 6:
        return q_ik
    if not np.any(~np.isnan(pt)):
        return q_ik
    base = q_ik.copy() if q_ik is not None else q_start.copy()
    for i in range(6):
        if not np.isnan(pt[i]):
            base[i] = float(pt[i])
    return base


def link_clearance_sum(
    kin_backend: Any,
    q: np.ndarray,
    link_names: tuple[str, ...],
    obstacles: list[Obstacle],
) -> float:
    """Sum of per-link minimum signed distances to obstacles (higher = more clearance)."""
    if not obstacles or not hasattr(kin_backend, "compute_link_positions"):
        return 0.0
    try:
        lp = kin_backend.compute_link_positions(q, list(link_names))
    except Exception:
        return 0.0
    s = 0.0
    for p in lp:
        s += float(distance_to_obstacles(np.asarray(p, dtype=np.float64), obstacles))
    return s


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
    RMRC planner using backend kinematics and DLS Jacobian control.
    """

    def __init__(
        self,
        urdf_content: str,
        base_link: str = DEFAULT_BASE_LINK,
        ee_link: str = DEFAULT_EE_LINK,
        joint_names: list[str] | None = None,
        kinematics_backend: str = "hybrid",
    ):
        self._joint_names = joint_names or list(UR3E_JOINT_NAMES)
        self._base_link = str(base_link)
        self._ee_link = str(ee_link)
        self._kinematics_mode = str(kinematics_backend).lower()
        self._kin_backend: KinematicsBackend = PyKDLKinematicsBackend(
            urdf_content=urdf_content,
            base_link=self._base_link,
            ee_link=self._ee_link,
            joint_names=self._joint_names,
        )
        self._ik_backend: URAnalyticalIKBackend | None = None
        if self._kinematics_mode in ("hybrid", "analytical"):
            self._ik_backend = URAnalyticalIKBackend(joint_names=self._joint_names)
        if self._kinematics_mode == "pykdl":
            self._ik_backend = None
        self._repulsion_link_names = tuple(n for n, _ in UR3E_REPULSION_LINK_SPECS)
        self._repulsion_link_weight_base = tuple(w for _, w in UR3E_REPULSION_LINK_SPECS)
        self._last_rmrc_plan_debug: dict[str, Any] = {}

    def _active_q_from_input(self, q: list[float] | dict[str, float]) -> np.ndarray:
        if isinstance(q, dict):
            return np.array([float(q.get(name, 0.0)) for name in self._joint_names], dtype=np.float64)
        return np.array([float(v) for v in q], dtype=np.float64)

    def compute_ee_pose(self, q: list[float] | dict[str, float]) -> tuple[np.ndarray, np.ndarray]:
        """Returns (position 3-vec, quaternion [x,y,z,w])."""
        pose = self._kin_backend.compute_fk(self._active_q_from_input(q))
        return pose.position, pose.quaternion

    def compute_jacobian(self, q: list[float] | dict[str, float]) -> np.ndarray:
        """6 x n_active geometric Jacobian (linear + angular velocity)."""
        return self._kin_backend.compute_jacobian(self._active_q_from_input(q))

    def solve_ik_candidates(
        self,
        target_pose: tuple[np.ndarray, np.ndarray],
        seed_q: np.ndarray,
    ) -> list[np.ndarray]:
        if self._ik_backend is None:
            return []
        pose = Pose(
            position=np.array(target_pose[0], dtype=np.float64),
            quaternion=np.array(target_pose[1], dtype=np.float64),
        )
        return self._ik_backend.solve_ik(pose, np.array(seed_q, dtype=np.float64))

    def select_ik_candidate(
        self,
        candidates: list[np.ndarray],
        q_start: np.ndarray,
        obstacles: list[Obstacle],
        mode: str,
        w_elbow: float,
        w_clearance: float,
        w_start: float,
    ) -> np.ndarray | None:
        """
        Pick one analytical IK solution. Modes: nearest, elbow_up, clearance, composite.
        Composite maximizes w_elbow*elbow + w_clearance*link_clearance_sum - w_start*||q-q_start||.
        """
        if not candidates:
            return None
        m = str(mode or "composite").lower().strip()
        if m == "nearest":
            return min(candidates, key=lambda c: float(np.linalg.norm(c - q_start)))
        q0 = np.array(q_start, dtype=np.float64).reshape(-1)
        scored: list[tuple[float, np.ndarray]] = []
        for c in candidates:
            cc = np.array(c, dtype=np.float64).reshape(-1)
            elbow = float(cc[2]) if cc.size > 2 else 0.0
            clear_sum = link_clearance_sum(
                self._kin_backend, cc, self._repulsion_link_names, obstacles
            )
            dist = float(np.linalg.norm(cc - q0))
            if m == "elbow_up":
                sc = elbow
            elif m == "clearance":
                sc = clear_sum
            else:
                sc = float(w_elbow) * elbow + float(w_clearance) * clear_sum - float(w_start) * dist
            scored.append((sc, cc))
        best = max(scored, key=lambda t: t[0])
        return np.array(best[1], dtype=np.float64)

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
        q_bias: np.ndarray | None = None,
        k_bias: float = 0.0,
        body_link_weight: float = 0.55,
        max_cart_repulsion_linear: float = 0.75,
        use_multi_point_repulsion: bool = True,
        joint_secondary_weight: float = 0.0,
        joint_secondary_gain: float = 2.0,
        joint_secondary_w_epsilon: float = 0.025,
        joint_secondary_pref_clip: float = 0.45,
        repulsion_lp_state: np.ndarray | None = None,
        repulsion_smooth_alpha: float = 1.0,
        repulsion_dist_scale: bool = False,
        repulsion_out_grad_cap: float | None = 120.0,
        orientation_error_gain: float = 1.0,
    ) -> np.ndarray:
        """
        Compute q_dot for one RMRC step.
        v_desired: 6-vector [vx, vy, vz, wx, wy, wz]
        Repulsion is blended into the Cartesian linear velocity (primary task), not null-space,
        so it works for a 6x6 Jacobian. Optional body link samples reduce elbow/forearm scrapes.
        If joint_secondary_weight > 0, solves a damped least-squares blend with elbow/shoulder
        preference. Diagonal W uses weight * joint_secondary_w_epsilon so the secondary task
        stays subordinate to Cartesian tracking; joint preference is clipped (rad/s scale).
        Returns n_active joint velocities.
        """
        pos_ee, _ = self.compute_ee_pose(q.tolist())
        points = [np.array(pos_ee, dtype=np.float64)]
        weights = [1.0]
        if (
            use_multi_point_repulsion
            and obstacles
            and hasattr(self._kin_backend, "compute_link_positions")
        ):
            try:
                lp = self._kin_backend.compute_link_positions(
                    q, list(self._repulsion_link_names)
                )
                for p, w_base in zip(lp, self._repulsion_link_weight_base):
                    points.append(np.array(p, dtype=np.float64))
                    weights.append(float(body_link_weight) * float(w_base))
            except Exception:
                pass
        grad_linear = _repulsion_linear_weighted_multi(
            points, weights, obstacles, d_safe, out_grad_cap=repulsion_out_grad_cap
        )
        v_work = np.array(v_desired, dtype=np.float64)
        v_work[3:6] *= float(orientation_error_gain)
        k_rep_eff = float(k_repulsion)
        if obstacles and k_rep_eff > 0.0 and np.linalg.norm(grad_linear) > 1e-12:
            if repulsion_dist_scale:
                min_d = float("inf")
                for p in points:
                    min_d = min(min_d, float(distance_to_obstacles(p, obstacles)))
                if min_d < float("inf"):
                    k_rep_eff *= float(np.clip(min_d / max(d_safe, 1e-6), 0.2, 1.0))
            rep_cart = k_rep_eff * grad_linear
            if repulsion_lp_state is not None and repulsion_lp_state.shape[0] >= 3:
                alpha = float(np.clip(repulsion_smooth_alpha, 0.0, 1.0))
                if alpha < 1.0:
                    rep_cart = alpha * repulsion_lp_state[:3] + (1.0 - alpha) * rep_cart
                    repulsion_lp_state[:3] = rep_cart
            rn = float(np.linalg.norm(rep_cart))
            if rn > max_cart_repulsion_linear:
                rep_cart = rep_cart * (max_cart_repulsion_linear / rn)
            v_work[:3] = v_work[:3] + rep_cart
        J = self.compute_jacobian(q.tolist())
        n_j = J.shape[1]
        use_joint_secondary = (
            joint_secondary_weight > 0.0
            and q_bias is not None
            and float(joint_secondary_gain) != 0.0
        )
        if use_joint_secondary:
            w_eps = max(float(joint_secondary_w_epsilon), 0.0)
            w_mag = max(float(joint_secondary_weight), 0.0) * w_eps
            Wdiag = np.full(n_j, w_eps, dtype=np.float64)
            if n_j > 2:
                Wdiag[1] = w_mag
                Wdiag[2] = w_mag
            q_pref = np.zeros(n_j, dtype=np.float64)
            qb = np.array(q_bias, dtype=np.float64).reshape(-1)
            qq = np.array(q, dtype=np.float64).reshape(-1)
            clip = max(float(joint_secondary_pref_clip), 1e-6)
            if n_j > 2:
                g = float(joint_secondary_gain)
                q_pref[1] = float(np.clip(g * (qb[1] - qq[1]), -clip, clip))
                q_pref[2] = float(np.clip(g * (qb[2] - qq[2]), -clip, clip))
            lam2 = float(lambda_damped) ** 2
            A = J.T @ J + np.diag(Wdiag) + lam2 * np.eye(n_j)
            rhs = J.T @ v_work + Wdiag * q_pref
            try:
                q_dot = np.linalg.solve(A, rhs)
            except np.linalg.LinAlgError:
                Jpinv = damped_pseudo_inverse(J, lambda_damped)
                q_dot = Jpinv @ v_work
        else:
            Jpinv = damped_pseudo_inverse(J, lambda_damped)
            q_dot = Jpinv @ v_work
            if q_bias is not None and k_bias > 0.0:
                q_error = np.array(q_bias, dtype=np.float64) - q
                N = np.eye(J.shape[1]) - Jpinv @ J
                q_dot += k_bias * (N @ q_error)
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
        goal_pos_tolerance_m: float = 0.01,
        goal_ori_tolerance_rad: float = 0.2,
        ik_seed_gain: float = 0.0,
        posture_joint_targets: np.ndarray | None = None,
        posture_bias_gain: float = 0.0,
        body_link_weight: float = 0.55,
        max_cart_repulsion_linear: float = 0.75,
        use_multi_point_repulsion: bool = True,
        ik_score_mode: str = "composite",
        ik_score_w_elbow: float = 1.0,
        ik_score_w_clearance: float = 0.08,
        ik_score_w_start: float = 0.35,
        joint_secondary_weight: float = 0.0,
        joint_secondary_gain: float = 1.5,
        joint_secondary_w_epsilon: float = 0.025,
        joint_secondary_pref_clip: float = 0.45,
        repulsion_smooth_alpha: float = 0.45,
        repulsion_dist_scale: bool = True,
        repulsion_out_grad_cap: float | None = 120.0,
        orientation_error_gain: float = 1.15,
        path_fb_scale_cap: float | None = 2.5,
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
        path_vec = pose_target_pos - pos_start
        dist_travel = float(np.linalg.norm(path_vec))
        trajectory: list[tuple[float, np.ndarray]] = [(0.0, np.array(q_start, dtype=np.float64).copy())]
        q = np.array(q_start, dtype=np.float64)
        ik_candidates = self.solve_ik_candidates(pose_target, q_start)
        q_bias_ik = None
        if ik_candidates:
            q_bias_ik = self.select_ik_candidate(
                ik_candidates,
                q_start,
                obstacles,
                ik_score_mode,
                ik_score_w_elbow,
                ik_score_w_clearance,
                ik_score_w_start,
            )
        q_merged = merge_posture_joint_targets(
            q_bias_ik, q_start, posture_joint_targets
        )
        q_ref = q_merged
        if q_ref is None and float(joint_secondary_weight) > 0.0:
            q_ref = np.array(q_start, dtype=np.float64)
        k_bias_total = float(ik_seed_gain) + float(posture_bias_gain)
        rep_lp = np.zeros(3, dtype=np.float64)
        # Nominal time to traverse the straight line (position + SLERP orientation).
        v_line_nominal_m_s = 0.05 + 0.55 * float(max_velocity_scale)
        T_path = dist_travel / max(v_line_nominal_m_s, 1e-4)
        # Closed-loop gain: do not let small max_velocity_scale (e.g. 0.2 from the node)
        # kill Cartesian feedback during the approach.
        path_fb_scale = max(1.0, float(max_velocity_scale) * 4.0)
        if path_fb_scale_cap is not None and float(path_fb_scale_cap) > 0.0:
            path_fb_scale = min(path_fb_scale, float(path_fb_scale_cap))
        q0n = np.array(q_start_quat, dtype=np.float64)
        q1n = pose_target_quat
        # After s reaches 1, the reference sits on the goal but the EE often lags
        # (logs: exit at t≈T_path with pos_err_m~0.57 m). Keep integrating toward
        # pos_des=goal with a hold budget. Keep repulsion ON during hold so the arm
        # does not cut through exclusion zones (zero repulsion caused collisions).
        max_hold_steps = min(3000, max_steps)
        path_exit_pos_tol = max(8.0 * float(goal_pos_tolerance_m), 0.05)
        path_exit_ori_tol = max(1.5 * float(goal_ori_tolerance_rad), 0.45)
        hold_steps = 0
        q_dot_prev = np.zeros_like(q)
        t_total = 0.0
        t_elapsed = 0.0
        step = 0
        js_w = float(joint_secondary_weight)
        use_js = js_w > 0.0 and q_ref is not None
        q_step_bias = q_ref if use_js else q_merged
        while step < max_steps:
            s = min(1.0, t_elapsed / max(T_path, 1e-6))
            pos_des = pos_start + s * path_vec
            quat_des = slerp(q0n, q1n, s)
            pos_ee, quat_ee = self.compute_ee_pose(q.tolist())
            dt_step = dt
            in_hold = t_elapsed >= T_path - 1e-9
            # Ramp: full repulsion. Hold at goal: scale down (logs: full repulsion +
            # task in bad joint branches → 3000 hold steps, ori_err ~1.8, no progress).
            k_rep_path = float(k_repulsion) * (0.5 if in_hold else 1.0)
            v_linear = path_fb_scale * (pos_des - pos_ee) / max(dt_step, 1e-6)
            ori_g = float(orientation_error_gain)
            omega = (
                path_fb_scale
                * ori_g
                * quaternion_error_vector(quat_ee, quat_des)
                / max(dt_step, 1e-6)
            )
            v_desired = np.concatenate([v_linear, omega])
            q_dot = self.rmrc_step(
                q,
                v_desired,
                obstacles,
                d_safe=d_safe,
                k_repulsion=k_rep_path,
                max_joint_velocity=max_joint_velocity,
                q_bias=q_step_bias,
                k_bias=0.0 if use_js else k_bias_total,
                body_link_weight=body_link_weight,
                max_cart_repulsion_linear=max_cart_repulsion_linear,
                use_multi_point_repulsion=use_multi_point_repulsion,
                joint_secondary_weight=js_w if use_js else 0.0,
                joint_secondary_gain=float(joint_secondary_gain),
                joint_secondary_w_epsilon=float(joint_secondary_w_epsilon),
                joint_secondary_pref_clip=float(joint_secondary_pref_clip),
                repulsion_lp_state=rep_lp,
                repulsion_smooth_alpha=float(repulsion_smooth_alpha),
                repulsion_dist_scale=bool(repulsion_dist_scale),
                repulsion_out_grad_cap=repulsion_out_grad_cap,
                orientation_error_gain=1.0,
            )
            if max_joint_acceleration > 0.0:
                dqdot_limit = max_joint_acceleration * dt_step
                q_dot = np.clip(q_dot, q_dot_prev - dqdot_limit, q_dot_prev + dqdot_limit)
            q = q + q_dot * dt_step
            q_dot_prev = q_dot
            t_elapsed += dt_step
            t_total += dt_step
            trajectory.append((t_total, q.copy()))
            step += 1

            pe_line = float(np.linalg.norm(pose_target_pos - pos_ee))
            oe_line = float(
                np.linalg.norm(quaternion_error_vector(quat_ee, pose_target_quat))
            )
            if pe_line < path_exit_pos_tol and oe_line < path_exit_ori_tol:
                break
            if in_hold:
                hold_steps += 1
                if hold_steps >= max_hold_steps:
                    break

        # Final closed-loop convergence: integrate RMRC on Cartesian error.
        # Keep non-zero repulsion when far from goal (Cartesian blend avoids the old
        # null-space stall); scale down slightly near the goal for convergence.
        settle_steps = min(max_steps, 2500)
        settle_v_scale = max(float(max_velocity_scale), 1.0)
        settle_lambda = 0.004
        last_settle_k_rep = 0.0
        settle_iter_used = 0
        for si in range(settle_steps):
            pos_cur, quat_cur = self.compute_ee_pose(q.tolist())
            pos_err_vec = pose_target_pos - pos_cur
            pos_err = float(np.linalg.norm(pos_err_vec))
            ori_err_vec = quaternion_error_vector(quat_cur, pose_target_quat)
            ori_err = float(np.linalg.norm(ori_err_vec))
            if pos_err <= goal_pos_tolerance_m and ori_err <= goal_ori_tolerance_rad:
                settle_iter_used = si + 1
                break
            settle_iter_used = si + 1
            if pos_err > 0.10:
                settle_k_rep = float(k_repulsion) * 0.14
            else:
                settle_k_rep = float(k_repulsion) * 0.35
            last_settle_k_rep = float(settle_k_rep)
            settle_lambda = 0.008 if pos_err > 0.15 else 0.004
            v_linear = pos_err_vec / max(dt, 1e-6)
            ori_boost = (
                1.85
                if pos_err <= max(3.0 * float(goal_pos_tolerance_m), 0.03)
                else 1.0
            )
            omega = (
                ori_err_vec
                / max(dt, 1e-6)
                * ori_boost
                * float(orientation_error_gain)
            )
            v_desired = np.concatenate([v_linear * settle_v_scale, omega * settle_v_scale])
            q_dot = self.rmrc_step(
                q,
                v_desired,
                obstacles,
                d_safe=d_safe,
                k_repulsion=settle_k_rep,
                lambda_damped=settle_lambda,
                max_joint_velocity=max_joint_velocity,
                q_bias=q_step_bias,
                k_bias=0.0 if use_js else k_bias_total,
                body_link_weight=body_link_weight,
                max_cart_repulsion_linear=max_cart_repulsion_linear,
                use_multi_point_repulsion=use_multi_point_repulsion,
                joint_secondary_weight=js_w if use_js else 0.0,
                joint_secondary_gain=float(joint_secondary_gain),
                joint_secondary_w_epsilon=float(joint_secondary_w_epsilon),
                joint_secondary_pref_clip=float(joint_secondary_pref_clip),
                repulsion_lp_state=rep_lp,
                repulsion_smooth_alpha=float(repulsion_smooth_alpha),
                repulsion_dist_scale=bool(repulsion_dist_scale),
                repulsion_out_grad_cap=repulsion_out_grad_cap,
                orientation_error_gain=1.0,
            )
            if max_joint_acceleration > 0.0:
                dqdot_limit = max_joint_acceleration * dt
                q_dot = np.clip(q_dot, q_dot_prev - dqdot_limit, q_dot_prev + dqdot_limit)
            q = q + q_dot * dt
            q_dot_prev = q_dot
            t_total += dt
            trajectory.append((t_total, q.copy()))
        q_sel = q_bias_ik
        self._last_rmrc_plan_debug = {
            "ik_score_mode": str(ik_score_mode),
            "ik_candidates_count": int(len(ik_candidates)),
            "ik_selected_joints": [float(x) for x in np.asarray(q_sel).reshape(-1)]
            if q_sel is not None
            else [],
            "ik_selected_elbow_rad": float(q_sel[2]) if q_sel is not None and len(q_sel) > 2 else None,
            "q_start_joints": [float(x) for x in np.asarray(q_start).reshape(-1)],
            "joint_secondary_weight": float(joint_secondary_weight),
            "path_fb_scale": float(path_fb_scale),
            "traj_first_elbow_rad": float(trajectory[1][1][2]) if len(trajectory) > 1 else None,
            "traj_last_elbow_rad": float(trajectory[-1][1][2]) if trajectory else None,
        }
        return trajectory
