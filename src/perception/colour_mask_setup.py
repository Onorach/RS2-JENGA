"""
colour_mask_setup.py
--------------------
Interactive calibration for colour-identification mask smoothing
(median blur, gap fill, noise reduction, min blob area).

Opened after colour (HSV) setup when using play_live.py --setup.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from colour_identification import classify_roi_bgr, compute_roi
from colour_setup import load_hsv_ranges_from_config, load_search_area_from_config
from play_runtime import _init_opencv_gui, _warn_if_no_display, waiting_frame

_CONFIG_PATH = Path(__file__).resolve().parent / "perception_config.py"
_WINDOW = "Colour mask setup"

_MIN_WIDTH = 520
_PANEL_H = 100
_BTN_Y0 = 58
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 20
_MEDIAN_MAX = 15
_MORPH_MAX = 31
_BLOB_MAX = 2000


def load_colour_mask_from_config() -> tuple[int, int, int, int]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    med_m = re.search(r"^COLOUR_MASK_MEDIAN_PX\s*=\s*(\d+)", text, re.MULTILINE)
    close_m = re.search(r"^COLOUR_MASK_MORPH_CLOSE_PX\s*=\s*(\d+)", text, re.MULTILINE)
    open_m = re.search(r"^COLOUR_MASK_MORPH_OPEN_PX\s*=\s*(\d+)", text, re.MULTILINE)
    blob_m = re.search(r"^COLOUR_MIN_BLOB_AREA_PX\s*=\s*(\d+)", text, re.MULTILINE)
    if not med_m or not close_m or not open_m or not blob_m:
        raise RuntimeError(f"Could not parse colour mask settings in {_CONFIG_PATH}")
    return (
        int(med_m.group(1)),
        int(close_m.group(1)),
        int(open_m.group(1)),
        int(blob_m.group(1)),
    )


def save_colour_mask_to_config(
    median_px: int,
    morph_close_px: int,
    morph_open_px: int,
    min_blob_area_px: int,
) -> None:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    text, n1 = re.subn(
        r"^COLOUR_MASK_MEDIAN_PX\s*=\s*\d+.*$",
        f"COLOUR_MASK_MEDIAN_PX      = {median_px}   "
        "# Median blur on HSV before inRange; 0 = disabled.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n2 = re.subn(
        r"^COLOUR_MASK_MORPH_CLOSE_PX\s*=\s*\d+.*$",
        f"COLOUR_MASK_MORPH_CLOSE_PX = {morph_close_px}   "
        "# Close kernel — fills small holes. 0 = disabled.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n3 = re.subn(
        r"^COLOUR_MASK_MORPH_OPEN_PX\s*=\s*\d+.*$",
        f"COLOUR_MASK_MORPH_OPEN_PX  = {morph_open_px}   "
        "# Open kernel — removes specks. 0 = disabled.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n4 = re.subn(
        r"^COLOUR_MIN_BLOB_AREA_PX\s*=\s*\d+.*$",
        f"COLOUR_MIN_BLOB_AREA_PX = {min_blob_area_px}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n1 != 1 or n2 != 1 or n3 != 1 or n4 != 1:
        raise RuntimeError(f"Could not update colour mask settings in {_CONFIG_PATH}")
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


def _draw_control_strip(
    panel: np.ndarray,
    median_px: int,
    fill_gaps: int,
    reduce_noise: int,
    min_blob: int,
) -> None:
    panel[:] = (42, 42, 42)
    cv2.putText(
        panel,
        f"median {median_px}  |  fill gaps {fill_gaps}  |  "
        f"reduce noise {reduce_noise}  |  min blob {min_blob}  (0 = off)",
        (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "Live colour mask preview  |  s=Set  r=Reset  q=Cancel",
        (12, 44),
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


def _center_image_width(img: np.ndarray, width: int) -> np.ndarray:
    if img.shape[1] >= width:
        return img
    pad_total = width - img.shape[1]
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left
    return cv2.copyMakeBorder(
        img, 0, 0, pad_left, pad_right, cv2.BORDER_CONSTANT, value=(0, 0, 0),
    )


def run_colour_mask_setup(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
    search_area: tuple[float, float, float, float] | None = None,
) -> bool:
    """Colour mask smoothing UI. Returns True if Set was pressed (config saved)."""
    active_search_area = (
        search_area if search_area is not None else load_search_area_from_config()
    )
    hsv_ranges = load_hsv_ranges_from_config()
    orig_med, orig_close, orig_open, orig_blob = load_colour_mask_from_config()
    current = [orig_med, orig_close, orig_open, orig_blob]
    trackbars_ready = False
    done = False
    save_on_exit = False
    _updating_trackbars = False

    def _read_trackbars() -> tuple[int, int, int, int]:
        return (
            cv2.getTrackbarPos("median blur", _WINDOW),
            cv2.getTrackbarPos("fill gaps", _WINDOW),
            cv2.getTrackbarPos("reduce noise", _WINDOW),
            cv2.getTrackbarPos("min blob area", _WINDOW),
        )

    def _sync_trackbars() -> None:
        nonlocal _updating_trackbars
        if not trackbars_ready:
            return
        _updating_trackbars = True
        cv2.setTrackbarPos("median blur", _WINDOW, current[0])
        cv2.setTrackbarPos("fill gaps", _WINDOW, current[1])
        cv2.setTrackbarPos("reduce noise", _WINDOW, current[2])
        cv2.setTrackbarPos("min blob area", _WINDOW, current[3])
        _updating_trackbars = False

    def _on_trackbar(_pos: int) -> None:
        if _updating_trackbars:
            return
        current[:] = list(_read_trackbars())

    def _create_trackbars() -> None:
        nonlocal trackbars_ready
        if trackbars_ready:
            return
        cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(_WINDOW, _MIN_WIDTH, 640)
        cv2.createTrackbar("median blur", _WINDOW, current[0], _MEDIAN_MAX, _on_trackbar)
        cv2.createTrackbar("fill gaps", _WINDOW, current[1], _MORPH_MAX, _on_trackbar)
        cv2.createTrackbar("reduce noise", _WINDOW, current[2], _MORPH_MAX, _on_trackbar)
        cv2.createTrackbar("min blob area", _WINDOW, current[3], _BLOB_MAX, _on_trackbar)
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
            current[:] = [orig_med, orig_close, orig_open, orig_blob]
            _sync_trackbars()
        elif btn == "Cancel":
            done = True

    print(
        "Colour mask setup: tune median blur, fill gaps, reduce noise, min blob area, "
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
        if bgr_full is None:
            cv2.imshow(_WINDOW, placeholder)
        elif trackbars_ready:
            median_px, fill_gaps, reduce_noise, min_blob = _read_trackbars()
            current[:] = [median_px, fill_gaps, reduce_noise, min_blob]

            ih, iw = bgr_full.shape[:2]
            rx, ry, rw, rh = compute_roi(iw, ih, search_area=active_search_area)
            roi_bgr = bgr_full[ry : ry + rh, rx : rx + rw]
            colour_img, _ = classify_roi_bgr(
                roi_bgr,
                hsv_ranges,
                median_px=median_px,
                morph_close_px=fill_gaps,
                morph_open_px=reduce_noise,
                min_blob_area_px=min_blob,
            )

            layout_w = max(colour_img.shape[1], _MIN_WIDTH)
            view_disp = _center_image_width(colour_img, layout_w)
            panel = np.zeros((_PANEL_H, layout_w, 3), dtype=np.uint8)
            _draw_control_strip(panel, median_px, fill_gaps, reduce_noise, min_blob)
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
            current[:] = [orig_med, orig_close, orig_open, orig_blob]
            _sync_trackbars()

    try:
        current[:] = list(_read_trackbars())
    except cv2.error:
        pass
    try:
        cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)

    if save_on_exit:
        save_colour_mask_to_config(current[0], current[1], current[2], current[3])
        print(
            f"Saved colour mask: MEDIAN={current[0]}, CLOSE={current[1]}, "
            f"OPEN={current[2]}, MIN_BLOB={current[3]} to {_CONFIG_PATH}"
        )
        from tower_setup import run_tower_setup

        return run_tower_setup(get_frame_pair, search_area=active_search_area)
    print("Colour mask setup cancelled — colour mask settings unchanged.")
    return False
