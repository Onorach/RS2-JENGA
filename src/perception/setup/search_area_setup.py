"""
search_area_setup.py
--------------------
Interactive calibration for SEARCH_AREA in perception_config.py.

Launched via play_live.py --setup.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from colour_identification import compute_roi
from colour_mask_setup import (
    load_colour_mask_from_config,
    run_colour_mask_setup,
    save_colour_mask_to_config,
)
from setup.colour_setup import (
    load_hsv_ranges_from_config,
    run_colour_setup,
    save_hsv_ranges_to_config,
)
from setup.depth_confirm_setup import run_depth_confirm_setup
from setup.mask_canny_setup import (
    load_mask_canny_from_config,
    run_mask_canny_setup,
    save_mask_canny_to_config,
)
from setup.original_canny_setup import (
    load_original_canny_from_config,
    run_original_canny_setup,
    save_original_canny_to_config,
)
from setup.tower_setup import (
    load_tower_mask_from_config,
    run_tower_setup,
    save_tower_mask_to_config,
)
from setup.gui_helpers import window_closed

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "perception_config.py"
_WINDOW = "Search area setup"

# Control strip below the live image (pixels)
_PANEL_H = 88
_BTN_Y0 = 42
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 20


def _frac_to_px(
    area: tuple[float, float, float, float],
    iw: int,
    ih: int,
) -> tuple[int, int, int, int]:
    cx_f, cy_f, w_f, h_f = area
    rw = max(1, int(iw * w_f))
    rh = max(1, int(ih * h_f))
    cx_px = int(round(iw * cx_f))
    cy_px = int(round(ih * cy_f))
    cx_px = max(0, min(cx_px, iw))
    cy_px = max(0, min(cy_px, ih))
    rw = max(1, min(rw, iw))
    rh = max(1, min(rh, ih))
    return cx_px, cy_px, rw, rh


def _px_to_frac(
    cx_px: int,
    cy_px: int,
    rw_px: int,
    rh_px: int,
    iw: int,
    ih: int,
) -> tuple[float, float, float, float]:
    return (
        cx_px / iw,
        cy_px / ih,
        rw_px / iw,
        rh_px / ih,
    )


def load_search_area_from_config() -> tuple[float, float, float, float]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^SEARCH_AREA\s*=\s*\(\s*"
        r"([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)\s*\)",
        text,
        re.MULTILINE,
    )
    if not match:
        raise RuntimeError(f"Could not parse SEARCH_AREA in {_CONFIG_PATH}")
    return tuple(float(g) for g in match.groups())  # type: ignore[return-value]


def save_search_area_to_config(values: tuple[float, float, float, float]) -> None:
    cx, cy, w, h = values
    replacement = f"SEARCH_AREA = ({cx:.3f}, {cy:.3f}, {w:.3f}, {h:.3f})"
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r"^SEARCH_AREA\s*=\s*\([^)]+\)",
        replacement,
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n != 1:
        raise RuntimeError(f"Could not update SEARCH_AREA in {_CONFIG_PATH}")
    _CONFIG_PATH.write_text(new_text, encoding="utf-8")


def _btn_x0(panel_w: int) -> int:
    return (panel_w - (3 * _BTN_W + 2 * _BTN_GAP)) // 2


def _draw_control_strip(
    panel: np.ndarray,
    cx_px: int,
    cy_px: int,
    rw_px: int,
    rh_px: int,
    iw: int,
    ih: int,
) -> None:
    panel[:] = (42, 42, 42)
    pw = panel.shape[1]
    info = (
        f"centre x={cx_px}px  centre y={cy_px}px  "
        f"width={rw_px}px  height={rh_px}px  "
        f"(frame {iw}x{ih})"
    )
    cv2.putText(
        panel, info, (12, 26),
        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 220, 220), 1, cv2.LINE_AA,
    )

    bx0 = _btn_x0(pw)
    for i, (label, colour) in enumerate(
        (("Back", (80, 140, 200)), ("Next", (80, 180, 80)), ("Finish", (80, 180, 80)))
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


def _button_at(panel_x: int, panel_y: int, panel_w: int) -> str | None:
    if not (_BTN_Y0 <= panel_y < _BTN_Y0 + _BTN_H):
        return None
    bx0 = _btn_x0(panel_w)
    for i, name in enumerate(("Back", "Next", "Finish")):
        x1 = bx0 + i * (_BTN_W + _BTN_GAP)
        if x1 <= panel_x < x1 + _BTN_W:
            return name
    return None


def _run_search_area_step(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
    initial_frac: tuple[float, float, float, float],
) -> tuple[str, tuple[float, float, float, float]]:
    """Search-area setup step. Returns action and current search-area fraction."""
    original_frac = initial_frac
    original_px: list[int] = [0, 0, 1, 1]
    current_px: list[int] = [0, 0, 1, 1]
    frame_size: tuple[int, int] = (0, 0)
    trackbar_size: tuple[int, int] = (0, 0)
    trackbars_ready = False
    done = False
    action = "cancel"

    def _clamp_to_frame() -> None:
        iw, ih = frame_size
        if iw <= 0 or ih <= 0:
            return
        current_px[0] = max(0, min(current_px[0], iw))
        current_px[1] = max(0, min(current_px[1], ih))
        current_px[2] = max(1, min(current_px[2], iw))
        current_px[3] = max(1, min(current_px[3], ih))

    def _sync_trackbars() -> None:
        if not trackbars_ready:
            return
        _clamp_to_frame()
        cv2.setTrackbarPos("centre x (px)", _WINDOW, current_px[0])
        cv2.setTrackbarPos("centre y (px)", _WINDOW, current_px[1])
        cv2.setTrackbarPos("width (px)", _WINDOW, current_px[2])
        cv2.setTrackbarPos("height (px)", _WINDOW, current_px[3])

    def _on_centre_x(pos: int) -> None:
        current_px[0] = pos

    def _on_centre_y(pos: int) -> None:
        current_px[1] = pos

    def _on_width(pos: int) -> None:
        current_px[2] = max(1, pos)

    def _on_height(pos: int) -> None:
        current_px[3] = max(1, pos)

    def _on_mouse(event: int, x: int, y: int, _flags: int, userdata) -> None:
        nonlocal done, action
        if event != cv2.EVENT_LBUTTONUP or userdata is None:
            return
        image_h, panel_w = userdata
        panel_y = y - image_h
        if panel_y < 0:
            return
        btn = _button_at(x, panel_y, panel_w)
        if btn == "Back":
            action = "back"
            done = True
        elif btn == "Next":
            action = "next"
            done = True
        elif btn == "Finish":
            action = "finish"
            done = True

    def _create_trackbars(iw: int, ih: int) -> None:
        nonlocal trackbars_ready, trackbar_size
        try:
            if cv2.getWindowProperty(_WINDOW, cv2.WND_PROP_AUTOSIZE) >= 0:
                cv2.destroyWindow(_WINDOW)
        except cv2.error:
            pass
        cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
        cv2.createTrackbar("centre x (px)", _WINDOW, current_px[0], iw, _on_centre_x)
        cv2.createTrackbar("centre y (px)", _WINDOW, current_px[1], ih, _on_centre_y)
        cv2.createTrackbar("width (px)", _WINDOW, current_px[2], iw, _on_width)
        cv2.createTrackbar("height (px)", _WINDOW, current_px[3], ih, _on_height)
        trackbar_size = (iw, ih)
        trackbars_ready = True
        _sync_trackbars()

    print("Search area setup: adjust sliders (pixels), then Back / Next / Finish (b / n / f).")

    while not done:
        if trackbars_ready and window_closed(_WINDOW):
            action = "cancel"
            done = True
            break
        bgr_full, _ = get_frame_pair()
        if bgr_full is not None:
            ih, iw = bgr_full.shape[:2]
            if (iw, ih) != frame_size:
                old_iw, old_ih = frame_size
                if old_iw > 0 and old_ih > 0:
                    area_frac = _px_to_frac(*current_px, old_iw, old_ih)
                    current_px[:] = _frac_to_px(area_frac, iw, ih)
                else:
                    current_px[:] = _frac_to_px(original_frac, iw, ih)
                frame_size = (iw, ih)
                original_px[:] = _frac_to_px(original_frac, iw, ih)

            if (iw, ih) != trackbar_size:
                _create_trackbars(iw, ih)

            _clamp_to_frame()
            cx_px, cy_px, rw_px, rh_px = current_px
            area_frac = _px_to_frac(cx_px, cy_px, rw_px, rh_px, iw, ih)
            rx, ry, rw, rh = compute_roi(iw, ih, search_area=area_frac)

            live_disp = bgr_full.copy()
            cv2.rectangle(live_disp, (rx, ry), (rx + rw, ry + rh), (0, 255, 255), 2)
            cv2.drawMarker(
                live_disp, (cx_px, cy_px), (0, 255, 255),
                markerType=cv2.MARKER_CROSS, markerSize=12, thickness=1,
            )

            panel_w = live_disp.shape[1]
            panel = np.zeros((_PANEL_H, panel_w, 3), dtype=np.uint8)
            _draw_control_strip(panel, cx_px, cy_px, rw_px, rh_px, iw, ih)

            composite = np.vstack([live_disp, panel])
            if trackbars_ready:
                cv2.setMouseCallback(_WINDOW, _on_mouse, (ih, panel_w))
                cv2.imshow(_WINDOW, composite)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            action = "cancel"
            done = True
        elif key == ord("b"):
            action = "back"
            done = True
        elif key == ord("n"):
            action = "next"
            done = True
        elif key == ord("f"):
            action = "finish"
            done = True

    try:
        if cv2.getWindowProperty(_WINDOW, cv2.WND_PROP_AUTOSIZE) >= 0:
            cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass

    iw, ih = frame_size
    if iw > 0 and ih > 0:
        _clamp_to_frame()
        values = _px_to_frac(*current_px, iw, ih)
        return action, values
    print("Could not continue setup — no camera frame received.")
    cv2.destroyAllWindows()
    return "cancel", original_frac


def _save_all_setup_values(
    search_area: tuple[float, float, float, float],
    hsv_ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]],
    colour_mask: tuple[int, int, int, int],
    original_canny: tuple[int, int, float, float],
    mask_canny: tuple[int, int],
    tower_mask: tuple[int, int, int, int],
) -> None:
    save_search_area_to_config(search_area)
    save_hsv_ranges_to_config(hsv_ranges)
    save_colour_mask_to_config(*colour_mask)
    save_original_canny_to_config(*original_canny)
    save_mask_canny_to_config(*mask_canny)
    save_tower_mask_to_config(*tower_mask)


def run_search_area_setup(get_frame_pair: Callable[[], tuple[np.ndarray | None, object]]) -> bool:
    """Run full setup wizard. Returns True only when Finish saves all config values."""
    staged_search_area = load_search_area_from_config()
    staged_hsv = load_hsv_ranges_from_config()
    staged_colour_mask = load_colour_mask_from_config()
    staged_original_canny = load_original_canny_from_config()
    staged_mask_canny = load_mask_canny_from_config()
    staged_tower_mask = load_tower_mask_from_config()

    step_idx = 0
    max_idx = 6
    while True:
        if step_idx == 0:
            action, staged_search_area = _run_search_area_step(get_frame_pair, staged_search_area)
        elif step_idx == 1:
            action, staged_hsv = run_colour_setup(
                get_frame_pair,
                search_area=staged_search_area,
                initial_ranges=staged_hsv,
            )
        elif step_idx == 2:
            action, staged_colour_mask = run_colour_mask_setup(
                get_frame_pair,
                search_area=staged_search_area,
                initial_values=staged_colour_mask,
                hsv_ranges=staged_hsv,
            )
        elif step_idx == 3:
            action, staged_original_canny = run_original_canny_setup(
                get_frame_pair,
                search_area=staged_search_area,
                initial_values=staged_original_canny,
            )
        elif step_idx == 4:
            action, staged_mask_canny = run_mask_canny_setup(
                get_frame_pair,
                search_area=staged_search_area,
                initial_values=staged_mask_canny,
                hsv_ranges=staged_hsv,
                colour_mask_values=staged_colour_mask,
            )
        elif step_idx == 5:
            action, staged_tower_mask = run_tower_setup(
                get_frame_pair,
                search_area=staged_search_area,
                initial_values=staged_tower_mask,
            )
        else:
            action = run_depth_confirm_setup(get_frame_pair)

        if action == "back":
            step_idx = max(0, step_idx - 1)
            continue
        if action == "next":
            if step_idx < max_idx:
                step_idx += 1
                continue
            action = "finish"
        if action == "finish":
            _save_all_setup_values(
                staged_search_area,
                staged_hsv,
                staged_colour_mask,
                staged_original_canny,
                staged_mask_canny,
                staged_tower_mask,
            )
            print(f"Saved setup config to {_CONFIG_PATH}")
            return True
        print("Setup cancelled — configuration unchanged.")
        cv2.destroyAllWindows()
        return False


def run_search_area_setup_subscribe(color_topic: str, depth_topic: str) -> None:
    """ROS live-camera entry point for search-area setup."""
    import rclpy

    from play_runtime import _ImageBridge, _shutdown_executor, _start_executor

    rclpy.init()
    bridge = _ImageBridge(color_topic, depth_topic)
    nodes = [bridge]
    executor = _start_executor(nodes)
    try:
        run_search_area_setup(bridge.get_frame_pair)
    finally:
        _shutdown_executor(executor, nodes)
