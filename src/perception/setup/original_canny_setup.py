"""
original_canny_setup.py
-----------------------
Interactive calibration for CANNY_ORIGINAL_* and CANNY_CENTRE_BAND_PCT.

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
from setup.gui_helpers import _init_opencv_gui, _warn_if_no_display, waiting_frame
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


def load_original_canny_from_config() -> tuple[int, int, float]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    low_m = re.search(r"^CANNY_ORIGINAL_LOW\s*=\s*(\d+)", text, re.MULTILINE)
    high_m = re.search(r"^CANNY_ORIGINAL_HIGH\s*=\s*(\d+)", text, re.MULTILINE)
    band_m = re.search(r"^CANNY_CENTRE_BAND_PCT\s*=\s*([0-9.]+)", text, re.MULTILINE)
    if not low_m or not high_m or not band_m:
        raise RuntimeError(f"Could not parse original Canny settings in {_CONFIG_PATH}")
    return int(low_m.group(1)), int(high_m.group(1)), float(band_m.group(1))


def save_original_canny_to_config(
    canny_low: int,
    canny_high: int,
    centre_band_pct: float,
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
    if n1 != 1 or n2 != 1 or n3 != 1:
        raise RuntimeError(f"Could not update original Canny settings in {_CONFIG_PATH}")
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
    canny_low: int,
    canny_high: int,
    band_width_pct: float,
) -> None:
    panel[:] = (42, 42, 42)
    cv2.putText(
        panel,
        f"Canny low {canny_low}  |  Canny high {canny_high}  |  "
        f"band width {band_width_pct:.1f}%",
        (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "Original BGR Canny — yellow lines = band edges  |  s=Set  r=Reset  q=Cancel",
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


def _label_panel(img: np.ndarray, text: str) -> np.ndarray:
    out = img.copy()
    cv2.putText(
        out, text, (8, 22),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA,
    )
    return out


def _draw_band_guides(bgr: np.ndarray, band_width_pct: float) -> np.ndarray:
    """Overlay vertical lines at the centre-band width on a BGR preview."""
    out = bgr.copy()
    h, w = out.shape[:2]
    x_lo, x_hi = centre_band_x_bounds(w, band_width_pct)
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
) -> np.ndarray:
    full_bgr, band_bgr = preview_original_canny_views(
        roi_bgr,
        canny_low=canny_low,
        canny_high=canny_high,
        centre_band_pct=band_width_pct,
    )
    full_bgr = _draw_band_guides(
        _label_panel(full_bgr, "Canny (original BGR)"),
        band_width_pct,
    )
    band_bgr = _label_panel(band_bgr, f"Centre band ({band_width_pct:.1f}% width)")

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
) -> bool:
    """Original-image Canny + centre band width UI. Returns True if Set was pressed."""
    active_search_area = (
        search_area if search_area is not None else load_search_area_from_config()
    )
    orig_low, orig_high, orig_band = load_original_canny_from_config()
    current = [orig_low, orig_high, int(round(orig_band))]
    trackbars_ready = False
    done = False
    save_on_exit = False
    _updating_trackbars = False

    def _read_trackbars() -> tuple[int, int, float]:
        low = cv2.getTrackbarPos("Canny low", _WINDOW)
        high = cv2.getTrackbarPos("Canny high", _WINDOW)
        band = float(cv2.getTrackbarPos("band width %", _WINDOW))
        return low, high, band

    def _sync_trackbars() -> None:
        nonlocal _updating_trackbars
        if not trackbars_ready:
            return
        _updating_trackbars = True
        cv2.setTrackbarPos("Canny low", _WINDOW, current[0])
        cv2.setTrackbarPos("Canny high", _WINDOW, current[1])
        cv2.setTrackbarPos("band width %", _WINDOW, current[2])
        _updating_trackbars = False

    def _on_trackbar(_pos: int) -> None:
        if _updating_trackbars:
            return
        low, high, band = _read_trackbars()
        current[:] = [low, high, int(round(band))]

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
            current[:] = [orig_low, orig_high, int(round(orig_band))]
            _sync_trackbars()
        elif btn == "Cancel":
            done = True

    print(
        "Original Canny setup: tune Canny low/high and band width %, "
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
            low, high, band_i = _read_trackbars()
            current[:] = [low, high, band_i]
            band_pct = float(band_i)

            ih, iw = bgr_full.shape[:2]
            rx, ry, rw, rh = compute_roi(iw, ih, search_area=active_search_area)
            roi_bgr = bgr_full[ry : ry + rh, rx : rx + rw]

            view_disp = _build_preview(roi_bgr, low, high, band_pct)
            panel = np.zeros((_PANEL_H, view_disp.shape[1], 3), dtype=np.uint8)
            _draw_control_strip(panel, low, high, band_pct)
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
            current[:] = [orig_low, orig_high, int(round(orig_band))]
            _sync_trackbars()

    try:
        low, high, band = _read_trackbars()
        current[:] = [low, high, int(round(band))]
    except cv2.error:
        pass
    trackbars_ready = False
    try:
        cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)

    if save_on_exit:
        save_original_canny_to_config(current[0], current[1], float(current[2]))
        print(
            f"Saved original Canny: CANNY_ORIGINAL_LOW={current[0]}, "
            f"CANNY_ORIGINAL_HIGH={current[1]}, "
            f"CANNY_CENTRE_BAND_PCT={current[2]:.1f} to {_CONFIG_PATH}"
        )
        from setup.mask_canny_setup import run_mask_canny_setup

        return run_mask_canny_setup(get_frame_pair, search_area=active_search_area)
    print("Original Canny setup cancelled — settings unchanged.")
    return False
