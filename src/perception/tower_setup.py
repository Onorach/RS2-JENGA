"""
tower_setup.py
--------------
Interactive calibration for tower mask thresholds (saturation + brightness).

Shows the same side-by-side view as the Tower finder window (overlay | B&W mask).
Opened after colour setup when using play_live.py --setup.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from colour_identification import compute_roi
from perception_config import SEARCH_AREA_MARGIN
from tower_mask import build_display, compute_hex_region

_CONFIG_PATH = Path(__file__).resolve().parent / "perception_config.py"
_WINDOW = "Tower setup"

_MIN_WIDTH = 900
_PANEL_H = 100
_BTN_Y0 = 58
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 20
_SV_MAX = 255
_DISPLAY_MAX_W = 1280


def load_tower_mask_from_config() -> tuple[int, int]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    sat_m = re.search(r"^TOWER_MASK_SAT_MIN\s*=\s*(\d+)", text, re.MULTILINE)
    bri_m = re.search(r"^TOWER_MASK_BRIGHTNESS_MIN\s*=\s*(\d+)", text, re.MULTILINE)
    if not sat_m or not bri_m:
        raise RuntimeError(
            f"Could not parse TOWER_MASK_SAT_MIN / TOWER_MASK_BRIGHTNESS_MIN in {_CONFIG_PATH}"
        )
    return int(sat_m.group(1)), int(bri_m.group(1))


def save_tower_mask_to_config(sat_min: int, brightness_min: int) -> None:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    text, n1 = re.subn(
        r"^TOWER_MASK_SAT_MIN\s*=\s*\d+.*$",
        f"TOWER_MASK_SAT_MIN                 = {sat_min}   "
        "# Min HSV saturation for tower foreground.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n2 = re.subn(
        r"^TOWER_MASK_BRIGHTNESS_MIN\s*=\s*\d+.*$",
        f"TOWER_MASK_BRIGHTNESS_MIN          = {brightness_min}    "
        "# Min HSV value (brightness) for tower foreground.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n1 != 1 or n2 != 1:
        raise RuntimeError(f"Could not update tower mask settings in {_CONFIG_PATH}")
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


def _draw_control_strip(panel: np.ndarray, sat_min: int, brightness_min: int) -> None:
    panel[:] = (42, 42, 42)
    cv2.putText(
        panel,
        f"Min saturation (S) = {sat_min}   |   Min brightness (V) = {brightness_min}",
        (12, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "Left: tower overlay   Right: B&W mask (Tower finder)  |  s=Set  r=Reset  q=Cancel",
        (12, 46),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
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


def _fit_display_width(img: np.ndarray, max_w: int = _DISPLAY_MAX_W) -> np.ndarray:
    h, w = img.shape[:2]
    if w <= max_w:
        return img
    scale = max_w / w
    return cv2.resize(img, (max_w, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)


def _crop_for_tower(
    bgr_full: np.ndarray,
    search_area: tuple[float, float, float, float] | None,
) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    """Crop with search-area margin (same as play_runtime). Returns crop and ROI in crop coords."""
    ih, iw = bgr_full.shape[:2]
    rx, ry, rw, rh = compute_roi(iw, ih, search_area=search_area)
    mx, my = int(rw * SEARCH_AREA_MARGIN), int(rh * SEARCH_AREA_MARGIN)
    dx1 = max(0, rx - mx)
    dy1 = max(0, ry - my)
    dx2 = min(iw, rx + rw + mx)
    dy2 = min(ih, ry + rh + my)
    roi_x, roi_y = rx - dx1, ry - dy1
    return bgr_full[dy1:dy2, dx1:dx2], (roi_x, roi_y, rw, rh)


def run_tower_setup(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
    search_area: tuple[float, float, float, float] | None = None,
) -> bool:
    """Tower mask calibration UI. Returns True if Set was pressed (config saved)."""
    from colour_setup import load_search_area_from_config

    active_search_area = (
        search_area if search_area is not None else load_search_area_from_config()
    )
    orig_sat, orig_bri = load_tower_mask_from_config()
    current = [orig_sat, orig_bri]
    trackbars_ready = False
    done = False
    save_on_exit = False
    _updating_trackbars = False

    def _read_trackbars() -> tuple[int, int]:
        sat = cv2.getTrackbarPos("min saturation", _WINDOW)
        bri = cv2.getTrackbarPos("min brightness", _WINDOW)
        return sat, bri

    def _sync_trackbars() -> None:
        nonlocal _updating_trackbars
        if not trackbars_ready:
            return
        _updating_trackbars = True
        cv2.setTrackbarPos("min saturation", _WINDOW, current[0])
        cv2.setTrackbarPos("min brightness", _WINDOW, current[1])
        _updating_trackbars = False

    def _on_trackbar(_pos: int) -> None:
        if _updating_trackbars:
            return
        current[0], current[1] = _read_trackbars()

    def _create_trackbars() -> None:
        nonlocal trackbars_ready
        if trackbars_ready:
            return
        cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(_WINDOW, _MIN_WIDTH, 640)
        cv2.createTrackbar("min saturation", _WINDOW, current[0], _SV_MAX, _on_trackbar)
        cv2.createTrackbar("min brightness", _WINDOW, current[1], _SV_MAX, _on_trackbar)
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
            current[0], current[1] = orig_sat, orig_bri
            _sync_trackbars()
        elif btn == "Cancel":
            done = True

    print(
        "Tower setup: tune min saturation / brightness sliders to match the Tower finder mask, "
        "then Set / Reset / Cancel (or s / r / q)."
    )

    _create_trackbars()

    while not done:
        bgr_full, _ = get_frame_pair()
        if bgr_full is not None and trackbars_ready:
            sat_min, brightness_min = _read_trackbars()
            current[0], current[1] = sat_min, brightness_min

            bgr_crop, roi_xywh = _crop_for_tower(bgr_full, active_search_area)
            mask_kw = {"sat_min": sat_min, "brightness_min": brightness_min}
            pts = compute_hex_region(bgr_crop, roi_xywh=roi_xywh, **mask_kw)
            tower_view = build_display(
                bgr_crop, pts, roi_xywh=roi_xywh, **mask_kw,
            )
            tower_view = _fit_display_width(tower_view)

            layout_w = max(tower_view.shape[1], _MIN_WIDTH)
            view_disp = tower_view
            if view_disp.shape[1] < layout_w:
                pad = layout_w - view_disp.shape[1]
                view_disp = cv2.copyMakeBorder(
                    view_disp, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0),
                )

            panel = np.zeros((_PANEL_H, layout_w, 3), dtype=np.uint8)
            _draw_control_strip(panel, sat_min, brightness_min)
            composite = np.vstack([view_disp, panel])
            view_h = view_disp.shape[0]
            cv2.setMouseCallback(_WINDOW, _on_mouse, (view_h, layout_w))
            cv2.imshow(_WINDOW, composite)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            done = True
        elif key == ord("s"):
            save_on_exit = True
            done = True
        elif key == ord("r"):
            current[0], current[1] = orig_sat, orig_bri
            _sync_trackbars()

    try:
        current[0], current[1] = _read_trackbars()
    except cv2.error:
        pass
    try:
        cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)

    if save_on_exit:
        save_tower_mask_to_config(current[0], current[1])
        print(
            f"Saved TOWER_MASK_SAT_MIN={current[0]}, "
            f"TOWER_MASK_BRIGHTNESS_MIN={current[1]} to {_CONFIG_PATH}"
        )
    else:
        print("Tower setup cancelled — tower mask settings unchanged.")
    return save_on_exit


def run_tower_setup_subscribe(color_topic: str, depth_topic: str) -> None:
    """ROS entry point for tower mask setup only."""
    import rclpy

    from play_runtime import _ImageBridge, _shutdown_executor, _start_executor

    rclpy.init()
    bridge = _ImageBridge(color_topic, depth_topic)
    nodes = [bridge]
    executor = _start_executor(nodes)
    try:
        run_tower_setup(bridge.get_frame_pair)
    finally:
        _shutdown_executor(executor, nodes)
