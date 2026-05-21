"""
mask_canny_setup.py
-------------------
Interactive calibration for CANNY_MASK_LOW / CANNY_MASK_HIGH.

Uses the colour-classification image (separate from original BGR Canny).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from colour_identification import classify_roi_bgr, compute_roi
from grid_generation import preview_mask_canny
from setup.colour_setup import load_hsv_ranges_from_config, load_search_area_from_config
from setup.gui_helpers import _init_opencv_gui, _warn_if_no_display, waiting_frame

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "perception_config.py"
_WINDOW = "Mask Canny setup"

_MIN_WIDTH = 720
_PANEL_H = 100
_BTN_Y0 = 58
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 20
_CANNY_MAX = 255


def load_mask_canny_from_config() -> tuple[int, int]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    low_m = re.search(r"^CANNY_MASK_LOW\s*=\s*(\d+)", text, re.MULTILINE)
    high_m = re.search(r"^CANNY_MASK_HIGH\s*=\s*(\d+)", text, re.MULTILINE)
    if not low_m or not high_m:
        raise RuntimeError(f"Could not parse mask Canny settings in {_CONFIG_PATH}")
    return int(low_m.group(1)), int(high_m.group(1))


def save_mask_canny_to_config(canny_low: int, canny_high: int) -> None:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    text, n1 = re.subn(
        r"^CANNY_MASK_LOW\s*=\s*\d+.*$",
        f"CANNY_MASK_LOW   = {canny_low}   # Lower = more edges.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n2 = re.subn(
        r"^CANNY_MASK_HIGH\s*=\s*\d+.*$",
        f"CANNY_MASK_HIGH  = {canny_high}  # Higher = fewer, stronger edges only.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n1 != 1 or n2 != 1:
        raise RuntimeError(f"Could not update mask Canny settings in {_CONFIG_PATH}")
    _CONFIG_PATH.write_text(text, encoding="utf-8")


def _btn_x0(panel_w: int) -> int:
    return (panel_w - (3 * _BTN_W + 2 * _BTN_GAP)) // 2


def _action_button_at(panel_x: int, panel_y: int, panel_w: int) -> str | None:
    if not (_BTN_Y0 <= panel_y < _BTN_Y0 + _BTN_H):
        return None
    bx0 = _btn_x0(panel_w)
    for i, name in enumerate(("Set", "Reset", "Cancel")):
        x1 = bx0 + i * (_BTN_W + _BTN_GAP)
        if x1 <= panel_x < x1 + _BTN_W:
            return name
    return None


def _draw_control_strip(panel: np.ndarray, canny_low: int, canny_high: int) -> None:
    panel[:] = (42, 42, 42)
    cv2.putText(
        panel,
        f"Canny low {canny_low}  |  Canny high {canny_high}",
        (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "Canny on colour mask image  |  s=Set  r=Reset  q=Cancel",
        (12, 44),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (150, 150, 150),
        1,
        cv2.LINE_AA,
    )
    bx0 = _btn_x0(panel.shape[1])
    for i, (label, colour) in enumerate(
        (("Set", (80, 180, 80)), ("Reset", (80, 140, 200)), ("Cancel", (80, 80, 200)))
    ):
        x1 = bx0 + i * (_BTN_W + _BTN_GAP)
        y1, y2 = _BTN_Y0, _BTN_Y0 + _BTN_H
        x2 = x1 + _BTN_W
        cv2.rectangle(panel, (x1, y1), (x2, y2), colour, -1)
        cv2.rectangle(panel, (x1, y1), (x2, y2), (240, 240, 240), 1)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
        tx = x1 + (_BTN_W - tw) // 2
        ty = y1 + (_BTN_H + th) // 2
        cv2.putText(
            panel, label, (tx, ty),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA,
        )


def _center_image_width(img: np.ndarray, target_w: int) -> np.ndarray:
    h, w = img.shape[:2]
    if w >= target_w:
        return img
    pad = target_w - w
    return cv2.copyMakeBorder(
        img, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0),
    )


def _build_preview(colour_img: np.ndarray, canny_low: int, canny_high: int) -> np.ndarray:
    edges_bgr = preview_mask_canny(colour_img, canny_low=canny_low, canny_high=canny_high)
    out = edges_bgr.copy()
    cv2.putText(
        out, "Canny (colour mask)", (8, 22),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA,
    )
    layout_w = max(out.shape[1], _MIN_WIDTH)
    return _center_image_width(out, layout_w)


def run_mask_canny_setup(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
    search_area: tuple[float, float, float, float] | None = None,
) -> bool:
    """Colour-mask Canny calibration UI. Returns True if Set was pressed."""
    active_search_area = (
        search_area if search_area is not None else load_search_area_from_config()
    )
    hsv_ranges = load_hsv_ranges_from_config()
    orig_low, orig_high = load_mask_canny_from_config()
    current = [orig_low, orig_high]
    trackbars_ready = False
    done = False
    save_on_exit = False
    _updating_trackbars = False

    def _read_trackbars() -> tuple[int, int]:
        return (
            cv2.getTrackbarPos("Canny low", _WINDOW),
            cv2.getTrackbarPos("Canny high", _WINDOW),
        )

    def _sync_trackbars() -> None:
        nonlocal _updating_trackbars
        if not trackbars_ready:
            return
        _updating_trackbars = True
        cv2.setTrackbarPos("Canny low", _WINDOW, current[0])
        cv2.setTrackbarPos("Canny high", _WINDOW, current[1])
        _updating_trackbars = False

    def _on_trackbar(_pos: int) -> None:
        if _updating_trackbars:
            return
        current[:] = list(_read_trackbars())

    def _create_trackbars() -> None:
        nonlocal trackbars_ready, _updating_trackbars
        if trackbars_ready:
            return
        _updating_trackbars = True
        cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(_WINDOW, _MIN_WIDTH, 480)
        cv2.createTrackbar("Canny low", _WINDOW, current[0], _CANNY_MAX, _on_trackbar)
        cv2.createTrackbar("Canny high", _WINDOW, current[1], _CANNY_MAX, _on_trackbar)
        _updating_trackbars = False
        trackbars_ready = True
        _sync_trackbars()

    def _on_mouse(event: int, x: int, y: int, _flags: int, userdata) -> None:
        nonlocal done, save_on_exit
        if event != cv2.EVENT_LBUTTONUP or userdata is None:
            return
        view_h, panel_w = userdata
        panel_y = y - view_h
        if panel_y < 0:
            return
        btn = _action_button_at(x, panel_y, panel_w)
        if btn == "Set":
            save_on_exit = True
            done = True
        elif btn == "Reset":
            current[:] = [orig_low, orig_high]
            _sync_trackbars()
        elif btn == "Cancel":
            done = True

    print(
        "Mask Canny setup: tune Canny low/high on the colour mask, "
        "then Set / Reset / Cancel (or s / r / q)."
    )
    _init_opencv_gui()
    _warn_if_no_display()
    _create_trackbars()
    placeholder = waiting_frame(_MIN_WIDTH, 360, "Waiting for camera…")
    cv2.imshow(_WINDOW, placeholder)
    cv2.waitKey(1)

    while not done:
        bgr_full, _ = get_frame_pair()
        if bgr_full is not None and trackbars_ready:
            low, high = _read_trackbars()
            current[:] = [low, high]

            ih, iw = bgr_full.shape[:2]
            rx, ry, rw, rh = compute_roi(iw, ih, search_area=active_search_area)
            roi_bgr = bgr_full[ry : ry + rh, rx : rx + rw]
            colour_img, _ = classify_roi_bgr(roi_bgr, hsv_ranges)

            view_disp = _build_preview(colour_img, low, high)
            panel = np.zeros((_PANEL_H, view_disp.shape[1], 3), dtype=np.uint8)
            _draw_control_strip(panel, low, high)
            composite = np.vstack([view_disp, panel])
            view_h = view_disp.shape[0]
            cv2.setMouseCallback(_WINDOW, _on_mouse, (view_h, view_disp.shape[1]))
            cv2.imshow(_WINDOW, composite)
        elif trackbars_ready:
            cv2.imshow(_WINDOW, placeholder)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            done = True
        elif key == ord("s"):
            save_on_exit = True
            done = True
        elif key == ord("r"):
            current[:] = [orig_low, orig_high]
            _sync_trackbars()

    try:
        current[:] = list(_read_trackbars())
    except cv2.error:
        pass
    trackbars_ready = False
    try:
        cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)

    if save_on_exit:
        save_mask_canny_to_config(current[0], current[1])
        print(
            f"Saved mask Canny: CANNY_MASK_LOW={current[0]}, "
            f"CANNY_MASK_HIGH={current[1]} to {_CONFIG_PATH}"
        )
        from setup.tower_setup import run_tower_setup

        return bool(run_tower_setup(get_frame_pair, search_area=active_search_area))
    print("Mask Canny setup cancelled — settings unchanged.")
    return False
