from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

import numpy as np

if TYPE_CHECKING:
    import PyKDL as kdl  # type: ignore

def _rotation_matrix_to_quaternion(R: np.ndarray) -> np.ndarray:
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


@dataclass
class Pose:
    position: np.ndarray
    quaternion: np.ndarray


class KinematicsBackend(ABC):
    """Interface for RMRC kinematics providers."""

    @property
    @abstractmethod
    def joint_names(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def compute_fk(self, q: np.ndarray) -> Pose:
        raise NotImplementedError

    @abstractmethod
    def compute_jacobian(self, q: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def solve_ik(self, target_pose: Pose, seed_q: np.ndarray) -> list[np.ndarray]:
        raise NotImplementedError


class PyKDLKinematicsBackend(KinematicsBackend):
    """PyKDL-based FK/Jacobian backend for URDF-defined chains."""

    def __init__(
        self,
        urdf_content: str,
        base_link: str,
        ee_link: str,
        joint_names: list[str],
    ) -> None:
        try:
            import PyKDL as kdl
            from kdl_parser_py.urdf import treeFromUrdfModel  # type: ignore
            from urdf_parser_py.urdf import URDF
        except ImportError as exc:
            missing = str(exc)
            py = "<unknown>"
            try:
                import sys

                py = sys.executable
            except Exception:
                pass
            raise ImportError(
                "PyKDL backend import failed. "
                f"Missing/unavailable module: {missing}. "
                "Install dependencies: python3-pykdl, ros-${ROS_DISTRO}-kdl-parser-py, "
                "and ros-humble-urdfdom-py. "
                f"(python={py})"
            ) from exc

        self._kdl = kdl
        self._joint_names = list(joint_names)
        robot = URDF.from_xml_string(urdf_content)
        ok, tree = treeFromUrdfModel(robot)
        if not ok:
            raise ValueError("Could not build KDL tree from URDF.")

        self._tree = tree
        self._robot = robot
        self._base_link_name = str(base_link)
        self._link_fk_cache: dict[str, tuple] = {}

        chain = tree.getChain(str(base_link), str(ee_link))
        if chain.getNrOfSegments() == 0:
            raise ValueError(f"KDL chain is empty for base='{base_link}' ee='{ee_link}'.")
        self._chain = chain
        self._fk_solver = kdl.ChainFkSolverPos_recursive(chain)
        self._jac_solver = kdl.ChainJntToJacSolver(chain)
        self._kdl_joint_names: list[str] = []
        # Only *movable* joints appear in KDL JntArray indexing.
        # Some URDF fixed joints may still have names; those must be excluded here.
        seg_debug: list[dict] = []
        for i in range(chain.getNrOfSegments()):
            j = chain.getSegment(i).getJoint()
            name = ""
            try:
                name = str(j.getName())
            except Exception:
                name = ""
            # Use URDF semantics (stable) rather than PyKDL getType() (can be inconsistent).
            urdf_type = None
            is_movable = True
            try:
                if name and name in robot.joint_map:
                    urdf_type = str(robot.joint_map[name].type)
                    is_movable = urdf_type != "fixed"
            except Exception:
                pass
            try:
                jt_i = int(j.getType())
            except Exception:
                jt_i = None
            try:
                seg_debug.append(
                    {
                        "i": int(i),
                        "joint_name": name,
                        "joint_type": jt_i,
                        "urdf_type": urdf_type,
                        "is_movable": bool(is_movable),
                    }
                )
            except Exception:
                pass
            if not is_movable:
                continue
            if not name or name == "NoName":
                continue
            self._kdl_joint_names.append(str(name))

        self._kdl_joint_count = len(self._kdl_joint_names)
        self._name_to_kdl_index = {name: idx for idx, name in enumerate(self._kdl_joint_names)}
        missing = [name for name in self._joint_names if name not in self._name_to_kdl_index]
        if missing:
            raise ValueError(
                f"Requested joint names not present in KDL chain: {missing}. "
                f"Available: {self._kdl_joint_names}"
            )
        self._active_indices = [self._name_to_kdl_index[name] for name in self._joint_names]

    @property
    def joint_names(self) -> list[str]:
        return list(self._joint_names)

    def _to_kdl_jnt_array(self, q_active: np.ndarray) -> "kdl.JntArray":
        if q_active.shape[0] != len(self._joint_names):
            raise ValueError(
                f"Expected {len(self._joint_names)} active joints, got {q_active.shape[0]}."
            )
        arr = self._kdl.JntArray(self._kdl_joint_count)
        for idx in range(self._kdl_joint_count):
            arr[idx] = 0.0
        for local_idx, kdl_idx in enumerate(self._active_indices):
            arr[kdl_idx] = float(q_active[local_idx])
        return arr

    def compute_fk(self, q: np.ndarray) -> Pose:
        q_np = np.array(q, dtype=np.float64).reshape(-1)
        q_arr = self._to_kdl_jnt_array(q_np)
        frame = self._kdl.Frame()
        status = self._fk_solver.JntToCart(q_arr, frame)
        if status < 0:
            raise RuntimeError(f"PyKDL FK failed with code {status}.")
        pos = np.array([frame.p[0], frame.p[1], frame.p[2]], dtype=np.float64)
        rot = np.array(
            [
                [frame.M[0, 0], frame.M[0, 1], frame.M[0, 2]],
                [frame.M[1, 0], frame.M[1, 1], frame.M[1, 2]],
                [frame.M[2, 0], frame.M[2, 1], frame.M[2, 2]],
            ],
            dtype=np.float64,
        )
        quat = _rotation_matrix_to_quaternion(rot)
        return Pose(position=pos, quaternion=quat)

    def _movable_joint_names_in_chain(self, chain: "kdl.Chain") -> list[str]:
        """Ordered movable joint names along a KDL subchain (URDF semantics)."""
        names: list[str] = []
        for i in range(chain.getNrOfSegments()):
            j = chain.getSegment(i).getJoint()
            name = ""
            try:
                name = str(j.getName())
            except Exception:
                name = ""
            is_movable = True
            try:
                if name and name in self._robot.joint_map:
                    is_movable = str(self._robot.joint_map[name].type) != "fixed"
            except Exception:
                pass
            if not is_movable:
                continue
            if not name or name == "NoName":
                continue
            names.append(str(name))
        return names

    def compute_link_positions(self, q: np.ndarray, link_names: list[str]) -> list[np.ndarray]:
        """
        FK positions of link frame origins in base_link (metres).
        Same joint convention as compute_fk / compute_jacobian.
        """
        if not link_names:
            return []
        q_np = np.array(q, dtype=np.float64).reshape(-1)
        q_full = self._to_kdl_jnt_array(q_np)
        out: list[np.ndarray] = []
        for link_name in link_names:
            if link_name not in self._link_fk_cache:
                sub = self._tree.getChain(self._base_link_name, str(link_name))
                if sub.getNrOfSegments() == 0:
                    raise ValueError(
                        f"KDL chain empty: '{self._base_link_name}' -> '{link_name}'."
                    )
                names = self._movable_joint_names_in_chain(sub)
                fk = self._kdl.ChainFkSolverPos_recursive(sub)
                self._link_fk_cache[link_name] = (fk, names)
            fk, names = self._link_fk_cache[link_name]
            nj = len(names)
            jnt_arr = self._kdl.JntArray(nj)
            for i, name in enumerate(names):
                jnt_arr[i] = q_full[self._name_to_kdl_index[name]]
            frame = self._kdl.Frame()
            status = fk.JntToCart(jnt_arr, frame)
            if status < 0:
                raise RuntimeError(f"PyKDL FK failed for link '{link_name}' (code {status}).")
            out.append(
                np.array([frame.p[0], frame.p[1], frame.p[2]], dtype=np.float64)
            )
        return out

    def compute_jacobian(self, q: np.ndarray) -> np.ndarray:
        q_arr = self._to_kdl_jnt_array(np.array(q, dtype=np.float64))
        jac = self._kdl.Jacobian(self._kdl_joint_count)
        status = self._jac_solver.JntToJac(q_arr, jac)
        if status < 0:
            raise RuntimeError(f"PyKDL Jacobian failed with code {status}.")
        J_full = np.zeros((6, self._kdl_joint_count), dtype=np.float64)
        for r in range(6):
            for c in range(self._kdl_joint_count):
                J_full[r, c] = jac[r, c]
        return J_full[:, self._active_indices]

    def solve_ik(self, target_pose: Pose, seed_q: np.ndarray) -> list[np.ndarray]:
        # PyKDL backend is used for high-rate FK/Jacobian; analytical IK is delegated.
        _ = target_pose
        _ = seed_q
        return []


class URAnalyticalIKBackend(KinematicsBackend):
    """
    Optional analytical IK adapter.

    It wraps a callable solver returning candidate 6-DOF joint arrays.
    """

    def __init__(
        self,
        joint_names: list[str],
        solver: Callable[[Pose, np.ndarray], list[np.ndarray]] | None = None,
    ) -> None:
        self._joint_names = list(joint_names)
        self._solver = solver or self._load_solver()

    @property
    def joint_names(self) -> list[str]:
        return list(self._joint_names)

    def _load_solver(self) -> Callable[[Pose, np.ndarray], list[np.ndarray]] | None:
        try:
            from ur_ikfast import ur_kinematics  # type: ignore
        except Exception:
            return None

        ur_solver = ur_kinematics.URKinematics("ur3e")

        def _solve(pose: Pose, seed: np.ndarray) -> list[np.ndarray]:
            _ = seed
            q = pose.quaternion
            x, y, z = float(pose.position[0]), float(pose.position[1]), float(pose.position[2])
            # ur_ikfast accepts [x, y, z, qx, qy, qz, qw].
            sols = ur_solver.inverse([x, y, z, float(q[0]), float(q[1]), float(q[2]), float(q[3])])
            if sols is None:
                return []
            out: list[np.ndarray] = []
            for s in sols:
                if len(s) == len(self._joint_names):
                    out.append(np.array(s, dtype=np.float64))
            return out

        return _solve

    def compute_fk(self, q: np.ndarray) -> Pose:
        _ = q
        raise NotImplementedError("URAnalyticalIKBackend provides IK only.")

    def compute_jacobian(self, q: np.ndarray) -> np.ndarray:
        _ = q
        raise NotImplementedError("URAnalyticalIKBackend provides IK only.")

    def solve_ik(self, target_pose: Pose, seed_q: np.ndarray) -> list[np.ndarray]:
        if self._solver is None:
            return []
        return self._solver(target_pose, np.array(seed_q, dtype=np.float64))
