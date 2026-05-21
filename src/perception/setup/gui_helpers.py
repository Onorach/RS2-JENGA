"""Shared OpenCV GUI helpers for perception setup windows."""

from __future__ import annotations

import os

import cv2
import numpy as np

_INIT_WINDOW = "__opencv_gui_init__"


def _warn_if_no_display() -> None:
    if not os.environ.get("DISPLAY"):
        print(
            "WARNING: DISPLAY is not set — OpenCV setup windows may not appear."
        )


def _init_opencv_gui() -> None:
    """Register the GUI backend on the main thread before ROS-driven frames."""
    _warn_if_no_display()
    try:
        cv2.namedWindow(_INIT_WINDOW, cv2.WINDOW_NORMAL)
        cv2.destroyWindow(_INIT_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)


def waiting_frame(width: int, height: int, message: str) -> np.ndarray:
    """Placeholder image shown until the first camera frame arrives."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (32, 32, 32)
    cv2.putText(
        img,
        message,
        (24, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (200, 200, 200),
        2,
        cv2.LINE_AA,
    )
    return img
