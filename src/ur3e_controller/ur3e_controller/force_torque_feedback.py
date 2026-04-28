"""
Force/torque feedback from the robot gripper (or tool flange).
Subscribes to the FT sensor topic and caches the latest wrench for use in control or monitoring.
"""

from __future__ import annotations

import threading
from geometry_msgs.msg import WrenchStamped


class ForceTorqueFeedback:
    """
    Holds the latest force/torque reading and optional thresholds for monitoring.
    Thread-safe for concurrent read/write from subscription and user code.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._latest: WrenchStamped | None = None

    def update(self, msg: WrenchStamped) -> None:
        """Update with a new WrenchStamped message (called from subscription callback)."""
        with self._lock:
            self._latest = msg

    def get_latest(self) -> WrenchStamped | None:
        """Return the most recent WrenchStamped, or None if none received yet."""
        with self._lock:
            return self._latest

    def get_force_xyz(self) -> tuple[float, float, float] | None:
        """Return (fx, fy, fz) in N, or None if no data."""
        w = self.get_latest()
        if w is None:
            return None
        return (w.wrench.force.x, w.wrench.force.y, w.wrench.force.z)

    def get_torque_xyz(self) -> tuple[float, float, float] | None:
        """Return (tx, ty, tz) in N⋅m, or None if no data."""
        w = self.get_latest()
        if w is None:
            return None
        return (w.wrench.torque.x, w.wrench.torque.y, w.wrench.torque.z)

    def force_magnitude(self) -> float | None:
        """Return magnitude of force in N, or None if no data."""
        f = self.get_force_xyz()
        if f is None:
            return None
        return (f[0] ** 2 + f[1] ** 2 + f[2] ** 2) ** 0.5

    def torque_magnitude(self) -> float | None:
        """Return magnitude of torque in N⋅m, or None if no data."""
        t = self.get_torque_xyz()
        if t is None:
            return None
        return (t[0] ** 2 + t[1] ** 2 + t[2] ** 2) ** 0.5
