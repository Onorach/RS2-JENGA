"""
original_canny_setup.py
-----------------------
Interactive calibration for CANNY_ORIGINAL_* and CANNY_CENTRE_BAND_*.

Separate window from colour-mask Canny (CANNY_MASK_*).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from colour_identification import compute_roi
from grid_generation import centre_band_x_bounds, preview_original_canny_views
from setup.gui_helpers import _init_opencv_gui, _warn_if_no_display, waiting_frame, window_closed
from setup.colour_setup import load_search_area_from_config

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "perception_config.py"
_WINDOW = "Original Canny setup"

_MIN_WIDTH = 720
_PANEL_H = 110
_BTN_Y0 = 68
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 20
_CANNY_MAX = 255
_BAND_MAX = 100
_OFFSET_RANGE = 100
_OFFSET_TRACKBAR_MAX = _OFFSET_RANGE * 2
_OFFSET_TRACKBAR_ZERO = _OFFSET_RANGE


def load_original_canny_from_config() -> tuple[int, int, float, float]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    low_m = re.search(r"^CANNY_ORIGINAL_LOW\s*=\s*(\d+)", text, re.MULTILINE)
    high_m = re.search(r"^CANNY_ORIGINAL_HIGH\s*=\s*(\d+)", text, re.MULTILINE)
    band_m = re.search(r"^CANNY_CENTRE_BAND_PCT\s*=\s*([0-9.]+)", text, re.MULTILINE)
    offset_m = re.search(
        r"^CANNY_CENTRE_BAND_OFFSET_PCT\s*=\s*([+-]?[0-9.]+)",
        text,
        re.MULTILINE,
    )
    if not low_m or not high_m or not band_m:
        raise RuntimeError(f"Could not parse original Canny settings in {_CONFIG_PATH}")
    offset = float(offset_m.group(1)) if offset_m else 0.0
    return int(low_m.group(1)), int(high_m.group(1)), float(band_m.group(1)), offset


def save_original_canny_to_config(
    canny_low: int,
    canny_high: int,
    centre_band_pct: float,
    centre_band_offset_pct: float,
) -> None:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    text, n1 = re.subn(
        r"^CANNY_ORIGINAL_LOW\s*=\s*\d+.*$",
        f"CANNY_ORIGINAL_LOW  = {canny_low}   # Lower = more edges.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n2 = re.subn(
        r"^CANNY_ORIGINAL_HIGH\s*=\s*\d+.*$",
        f"CANNY_ORIGINAL_HIGH = {canny_high}  # Higher = fewer, stronger edges only.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n3 = re.subn(
        r"^CANNY_CENTRE_BAND_PCT\s*=\s*[0-9.]+.*$",
        f"CANNY_CENTRE_BAND_PCT = {centre_band_pct:.1f}   "
        "# Centre band width (% of ROI) for original Canny / Hough.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n4 = re.subn(
        r"^CANNY_CENTRE_BAND_OFFSET_PCT\s*=\s*[+-]?[0-9.]+.*$",
        f"CANNY_CENTRE_BAND_OFFSET_PCT = {centre_band_offset_pct:.1f}  "
        "# Horizontal offset of that band (% of ROI width): +right, -left.",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n1 != 1 or n2 != 1 or n3 != 1 or n4 != 1:
        raise RuntimeError(f"Could not update original Canny settings in {_CONFIG_PATH}")
    _CONFIG_PATH.write_text(text, encoding="utf-8")


def _btn_x0(panel_w: int) -> int:
    return (panel_w - (3 * _BTN_W + 2 * _BTN_GAP)) // 2


def _action_button_at(panel_x: int, panel_y: int, panel_w: int) -> str | None:
    if not (_BTN_Y0 <= panel_y < _BTN_Y0 + _BTN_H):
        return None
    bx0 = _btn_x0(panel_w)
    for i, name in enumerate(("Back", "Next", "Finish")):
        x1 = bx0 + i * (_BTN_W + _BTN_GAP)
        if x1 <= panel_x < x1 + _BTN_W:
            return name
    return None


def _draw_control_strip(
    panel: np.ndarray,
    canny_low: int,
    canny_high: int,
    band_width_pct: float,
    band_offset_pct: float,
) -> None:
    panel[:] = (42, 42, 42)
    cv2.putText(
        panel,
        f"Canny low {canny_low}  |  Canny high {canny_high}  |  "
        f"band width {band_width_pct:.1f}%  |  band offset {band_offset_pct:+.1f}%",
        (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "Original BGR Canny — yellow lines = band edges  |  b=Back  n=Next  f=Finish",
        (12, 44),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.4,
        (150, 150, 150),
        1,
        cv2.LINE_AA,
    )
    bx0 = _btn_x0(panel.shape[1])
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


def _label_panel(img: np.ndarray, text: str) -> np.ndarray:
    out = img.copy()
    cv2.putText(
        out, text, (8, 22),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA,
    )
    return out


def _draw_band_guides(
    bgr: np.ndarray,
    band_width_pct: float,
    band_offset_pct: float,
) -> np.ndarray:
    """Overlay vertical lines at the configured original-edge band bounds."""
    out = bgr.copy()
    h, w = out.shape[:2]
    x_lo, x_hi = centre_band_x_bounds(w, band_width_pct, band_offset_pct)
    if x_hi <= x_lo:
        return out
    cv2.line(out, (x_lo, 0), (x_lo, h - 1), (0, 255, 255), 1, cv2.LINE_AA)
    cv2.line(out, (x_hi - 1, 0), (x_hi - 1, h - 1), (0, 255, 255), 1, cv2.LINE_AA)
    shade = out.copy()
    if x_lo > 0:
        shade[:, :x_lo] = (shade[:, :x_lo] * 0.35).astype(np.uint8)
    if x_hi < w:
        shade[:, x_hi:] = (shade[:, x_hi:] * 0.35).astype(np.uint8)
    return shade


def _build_preview(
    roi_bgr: np.ndarray,
    canny_low: int,
    canny_high: int,
    band_width_pct: float,
    band_offset_pct: float,
) -> np.ndarray:
    full_bgr, band_bgr = preview_original_canny_views(
        roi_bgr,
        canny_low=canny_low,
        canny_high=canny_high,
        centre_band_pct=band_width_pct,
        centre_band_offset_pct=band_offset_pct,
    )
    full_bgr = _draw_band_guides(
        _label_panel(full_bgr, "Canny (original BGR)"),
        band_width_pct,
        band_offset_pct,
    )
    band_bgr = _label_panel(
        band_bgr,
        f"Band ({band_width_pct:.1f}% width, {band_offset_pct:+.1f}% offset)",
    )

    h, w = full_bgr.shape[:2]
    sep = np.zeros((6, w, 3), dtype=np.uint8)
    sep[:] = (80, 80, 80)
    stacked = np.vstack([full_bgr, sep, band_bgr])

    layout_w = max(stacked.shape[1], _MIN_WIDTH)
    if stacked.shape[1] < layout_w:
        pad = layout_w - stacked.shape[1]
        stacked = cv2.copyMakeBorder(
            stacked, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0),
        )
    return stacked


def run_original_canny_setup(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
    search_area: tuple[float, float, float, float] | None = None,
    initial_values: tuple[int, int, float, float] | None = None,
) -> tuple[str, tuple[int, int, float, float]]:
    """Original-image Canny + centre band width UI. Returns action and values."""
    active_search_area = (
        search_area if search_area is not None else load_search_area_from_config()
    )
    loaded = (
        initial_values if initial_values is not None else load_original_canny_from_config()
    )
    if len(loaded) == 3:
        orig_low, orig_high, orig_band = loaded
        orig_offset = 0.0
    else:
        orig_low, orig_high, orig_band, orig_offset = loaded
    current = [orig_low, orig_high, int(round(orig_band)), int(round(orig_offset))]
    trackbars_ready = False
    done = False
    action = "cancel"
    _updating_trackbars = False

    def _read_trackbars() -> tuple[int, int, float, float]:
        low = cv2.getTrackbarPos("Canny low", _WINDOW)
        high = cv2.getTrackbarPos("Canny high", _WINDOW)
        band = float(cv2.getTrackbarPos("band width %", _WINDOW))
        offset = float(
            cv2.getTrackbarPos("band offset %", _WINDOW) - _OFFSET_TRACKBAR_ZERO
        )
        return low, high, band, offset

    def _sync_trackbars() -> None:
        nonlocal _updating_trackbars
        if not trackbars_ready:
            return
        _updating_trackbars = True
        cv2.setTrackbarPos("Canny low", _WINDOW, current[0])
        cv2.setTrackbarPos("Canny high", _WINDOW, current[1])
        cv2.setTrackbarPos("band width %", _WINDOW, current[2])
        cv2.setTrackbarPos(
            "band offset %",
            _WINDOW,
            max(0, min(_OFFSET_TRACKBAR_MAX, current[3] + _OFFSET_TRACKBAR_ZERO)),
        )
        _updating_trackbars = False

    def _on_trackbar(_pos: int) -> None:
        if _updating_trackbars:
            return
        low, high, band, offset = _read_trackbars()
        current[:] = [low, high, int(round(band)), int(round(offset))]

    def _create_trackbars() -> None:
        nonlocal trackbars_ready, _updating_trackbars
        if trackbars_ready:
            return
        _updating_trackbars = True
        cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(_WINDOW, _MIN_WIDTH, 640)
        cv2.createTrackbar("Canny low", _WINDOW, current[0], _CANNY_MAX, _on_trackbar)
        cv2.createTrackbar("Canny high", _WINDOW, current[1], _CANNY_MAX, _on_trackbar)
        cv2.createTrackbar("band width %", _WINDOW, current[2], _BAND_MAX, _on_trackbar)
        cv2.createTrackbar(
            "band offset %",
            _WINDOW,
            max(0, min(_OFFSET_TRACKBAR_MAX, current[3] + _OFFSET_TRACKBAR_ZERO)),
            _OFFSET_TRACKBAR_MAX,
            _on_trackbar,
        )
        _updating_trackbars = False
        trackbars_ready = True
        _sync_trackbars()

    def _on_mouse(event: int, x: int, y: int, _flags: int, userdata) -> None:
        nonlocal done, action
        if event != cv2.EVENT_LBUTTONUP or userdata is None:
            return
        view_h, panel_w = userdata
        panel_y = y - view_h
        if panel_y < 0:
            return
        btn = _action_button_at(x, panel_y, panel_w)
        if btn == "Back":
            action = "back"
            done = True
        elif btn == "Next":
            action = "next"
            done = True
        elif btn == "Finish":
            action = "finish"
            done = True

    print(
        "Original Canny setup: tune Canny low/high, band width %, and band offset %, "
        "then Back / Next / Finish (b / n / f)."
    )
    _init_opencv_gui()
    _warn_if_no_display()
    _create_trackbars()
    placeholder = waiting_frame(_MIN_WIDTH, 360, "Waiting for camera…")
    cv2.imshow(_WINDOW, placeholder)
    cv2.waitKey(1)

    while not done:
        if trackbars_ready and window_closed(_WINDOW):
            action = "cancel"
            done = True
            break
        bgr_full, _ = get_frame_pair()
        if bgr_full is not None and trackbars_ready:
            low, high, band_i, offset_i = _read_trackbars()
            current[:] = [low, high, int(round(band_i)), int(round(offset_i))]
            band_pct = float(band_i)
            band_offset_pct = float(offset_i)

            ih, iw = bgr_full.shape[:2]
            rx, ry, rw, rh = compute_roi(iw, ih, search_area=active_search_area)
            roi_bgr = bgr_full[ry : ry + rh, rx : rx + rw]

            view_disp = _build_preview(roi_bgr, low, high, band_pct, band_offset_pct)
            panel = np.zeros((_PANEL_H, view_disp.shape[1], 3), dtype=np.uint8)
            _draw_control_strip(panel, low, high, band_pct, band_offset_pct)
            composite = np.vstack([view_disp, panel])
            view_h = view_disp.shape[0]
            cv2.setMouseCallback(_WINDOW, _on_mouse, (view_h, view_disp.shape[1]))
            cv2.imshow(_WINDOW, composite)
        elif trackbars_ready:
            cv2.imshow(_WINDOW, placeholder)

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
        low, high, band, offset = _read_trackbars()
        current[:] = [low, high, int(round(band)), int(round(offset))]
    except cv2.error:
        pass
    trackbars_ready = False
    try:
        cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)

    if action == "back":
        print("Original Canny setup: moving to previous step.")
    elif action == "next":
        print("Original Canny setup: moving to next step.")
    elif action == "finish":
        print("Original Canny setup: finishing setup.")
    else:
        print("Original Canny setup cancelled — settings unchanged.")
    return action, (current[0], current[1], float(current[2]), float(current[3]))
