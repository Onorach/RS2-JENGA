"""
colour_setup.py
---------------
Interactive HSV mask calibration (colour identification debug view).

Opened automatically after saving search area in play_live.py --setup.
"""

from __future__ import annotations

import ast
import copy
import re
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from colour_identification import classify_roi_bgr, compute_roi
from play_runtime import _apply_boost

_CONFIG_PATH = Path(__file__).resolve().parent / "perception_config.py"
_WINDOW = "Colour setup"

_MIN_WIDTH = 520
_HEADER_H = 44
_PANEL_H = 118
_ARROW_BTN = 36
_ARROW_Y0 = 4
_ARROW_X0 = 16
_BTN_Y0 = 72
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 20

_MASK_COLOURS = ("red", "yellow", "green", "blue", "purple")
_NUM_MASKS = len(_MASK_COLOURS)

_H_MAX = 179
_SV_MAX = 255
_RED_H_WRAP_MAX = 179


def _deep_copy_ranges(
    ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]],
) -> dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]]:
    return copy.deepcopy(ranges)


def _find_hsv_dict_bounds(text: str) -> tuple[int, int]:
    marker = "HSV_RANGES"
    start = text.index(marker)
    brace_start = text.index("{", start)
    depth = 0
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return brace_start, i + 1
    raise RuntimeError(f"Could not find end of HSV_RANGES in {_CONFIG_PATH}")


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


def _ensure_red_two_bands(
    ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]],
) -> None:
    """Red: two hue wrap bands with shared S/V."""
    red = ranges.setdefault("red", [])
    if len(red) == 0:
        red.extend([
            ((0, 150, 140), (10, 255, 255)),
            ((170, 150, 140), (179, 255, 255)),
        ])
    elif len(red) == 1:
        lo, hi = red[0]
        red.append(((170, lo[1], lo[2]), (_RED_H_WRAP_MAX, hi[1], hi[2])))
    if len(red) >= 2:
        (lo0, hi0), (lo1, _hi1) = red[0], red[1]
        s_lo, v_lo = lo0[1], lo0[2]
        s_hi, v_hi = hi0[1], hi0[2]
        red[0] = ((0, s_lo, v_lo), (hi0[0], s_hi, v_hi))
        red[1] = ((lo1[0], s_lo, v_lo), (_RED_H_WRAP_MAX, s_hi, v_hi))


def load_hsv_ranges_from_config() -> dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]]:
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    brace_start, brace_end = _find_hsv_dict_bounds(text)
    ranges = ast.literal_eval(text[brace_start:brace_end])
    _ensure_red_two_bands(ranges)
    return ranges


def _format_hsv_dict_body(
    ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]],
) -> str:
    lines = ["{"]
    for colour in _MASK_COLOURS:
        bands = ranges.get(colour, [])
        lines.append(f'    "{colour}": [')
        for lo, hi in bands:
            lines.append(
                f"        (({lo[0]:3d}, {lo[1]:3d}, {lo[2]:3d}), "
                f"({hi[0]:3d}, {hi[1]:3d}, {hi[2]:3d})),"
            )
        lines.append("    ],")
    lines.append("}")
    return "\n".join(lines)


def save_hsv_ranges_to_config(
    ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]],
) -> None:
    _ensure_red_two_bands(ranges)
    text = _CONFIG_PATH.read_text(encoding="utf-8")
    marker = "HSV_RANGES"
    dict_start = text.index(marker)
    brace_start, brace_end = _find_hsv_dict_bounds(text)
    header = text[dict_start:brace_start]
    new_text = text[:dict_start] + header + _format_hsv_dict_body(ranges) + text[brace_end:]
    _CONFIG_PATH.write_text(new_text, encoding="utf-8")


def _btn_x0(panel_w: int) -> int:
    return (panel_w - (3 * _BTN_W + 2 * _BTN_GAP)) // 2


def _draw_arrow_button(panel: np.ndarray, x1: int, label: str) -> None:
    y1, y2 = _ARROW_Y0, _ARROW_Y0 + _ARROW_BTN
    x2 = x1 + _ARROW_BTN
    cv2.rectangle(panel, (x1, y1), (x2, y2), (70, 70, 70), -1)
    cv2.rectangle(panel, (x1, y1), (x2, y2), (200, 200, 200), 1)
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    tx = x1 + (_ARROW_BTN - tw) // 2
    ty = y1 + (_ARROW_BTN + th) // 2
    cv2.putText(
        panel, label, (tx, ty),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA,
    )


def _draw_mask_header(panel: np.ndarray, mask_label: str, mask_index: int) -> None:
    pw = panel.shape[1]
    panel[:] = (50, 50, 50)
    _draw_arrow_button(panel, _ARROW_X0, "<")
    _draw_arrow_button(panel, pw - _ARROW_X0 - _ARROW_BTN, ">")
    title = f"{mask_label}  ({mask_index + 1}/{_NUM_MASKS})"
    (tw, th), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.72, 2)
    tx = (pw - tw) // 2
    ty = _ARROW_Y0 + (_ARROW_BTN + th) // 2
    cv2.putText(
        panel, title, (tx, ty),
        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA,
    )


def _arrow_at(panel_x: int, panel_y: int, panel_w: int) -> str | None:
    if not (_ARROW_Y0 <= panel_y < _ARROW_Y0 + _ARROW_BTN):
        return None
    if _ARROW_X0 <= panel_x < _ARROW_X0 + _ARROW_BTN:
        return "left"
    right_x0 = panel_w - _ARROW_X0 - _ARROW_BTN
    if right_x0 <= panel_x < right_x0 + _ARROW_BTN:
        return "right"
    return None


def _action_button_at(panel_x: int, panel_y: int, panel_w: int) -> str | None:
    if not (_BTN_Y0 <= panel_y < _BTN_Y0 + _BTN_H):
        return None
    bx0 = _btn_x0(panel_w)
    for i, name in enumerate(("Set", "Reset", "Cancel")):
        x1 = bx0 + i * (_BTN_W + _BTN_GAP)
        if x1 <= panel_x < x1 + _BTN_W:
            return name
    return None


def _info_line_for_colour(
    colour: str,
    ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]],
) -> str:
    if colour == "red":
        (lo0, hi0), (lo1, _hi1) = ranges["red"][0], ranges["red"][1]
        return (
            f"H min {lo1[0]} (wrap {lo1[0]}-{_RED_H_WRAP_MAX})  "
            f"H max {hi0[0]} (wrap 0-{hi0[0]})  "
            f"S[{lo0[1]}-{hi0[1]}]  V[{lo0[2]}-{hi0[2]}]"
        )
    lo, hi = ranges[colour][0]
    return f"H[{lo[0]}-{hi[0]}]   S[{lo[1]}-{hi[1]}]   V[{lo[2]}-{hi[2]}]"


def _draw_control_strip(panel: np.ndarray, info_line: str) -> None:
    panel[:] = (42, 42, 42)
    hsv_line = info_line
    cv2.putText(
        panel, hsv_line, (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (220, 220, 220), 1, cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        "Set saves all masks  |  Reset restores all masks",
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


def _ordered_lo_hi(h_lo: int, h_hi: int, s_lo: int, s_hi: int, v_lo: int, v_hi: int) -> tuple[
    tuple[int, int, int], tuple[int, int, int]
]:
    return (
        (min(h_lo, h_hi), min(s_lo, s_hi), min(v_lo, v_hi)),
        (max(h_lo, h_hi), max(s_lo, s_hi), max(v_lo, v_hi)),
    )


def run_colour_setup(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
    search_area: tuple[float, float, float, float] | None = None,
) -> None:
    """HSV mask calibration UI; returns after Set, Cancel, or quit."""
    active_search_area = search_area if search_area is not None else load_search_area_from_config()

    original_ranges = load_hsv_ranges_from_config()
    _ensure_red_two_bands(original_ranges)
    current_ranges = _deep_copy_ranges(original_ranges)
    mask_index = [0]
    trackbars_ready = False
    done = False
    save_on_exit = False
    _updating_trackbars = False

    def _active_colour() -> str:
        return _MASK_COLOURS[mask_index[0]]

    def _is_red() -> bool:
        return _active_colour() == "red"

    def _read_standard_trackbars() -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        h_lo = cv2.getTrackbarPos("H min", _WINDOW)
        h_hi = cv2.getTrackbarPos("H max", _WINDOW)
        s_lo = cv2.getTrackbarPos("S min", _WINDOW)
        s_hi = cv2.getTrackbarPos("S max", _WINDOW)
        v_lo = cv2.getTrackbarPos("V min", _WINDOW)
        v_hi = cv2.getTrackbarPos("V max", _WINDOW)
        return _ordered_lo_hi(h_lo, h_hi, s_lo, s_hi, v_lo, v_hi)

    def _write_red_from_trackbars() -> None:
        h_min = cv2.getTrackbarPos("H min", _WINDOW)
        h_max = cv2.getTrackbarPos("H max", _WINDOW)
        s_lo = cv2.getTrackbarPos("S min", _WINDOW)
        s_hi = cv2.getTrackbarPos("S max", _WINDOW)
        v_lo = cv2.getTrackbarPos("V min", _WINDOW)
        v_hi = cv2.getTrackbarPos("V max", _WINDOW)
        band_near_zero = _ordered_lo_hi(0, h_max, s_lo, s_hi, v_lo, v_hi)
        band_near_max = _ordered_lo_hi(h_min, _RED_H_WRAP_MAX, s_lo, s_hi, v_lo, v_hi)
        current_ranges["red"] = [band_near_zero, band_near_max]

    def _write_active_range_from_trackbars() -> None:
        if _is_red():
            _write_red_from_trackbars()
        else:
            current_ranges[_active_colour()][0] = _read_standard_trackbars()

    def _sync_trackbars_from_active() -> None:
        nonlocal _updating_trackbars
        if not trackbars_ready:
            return
        _updating_trackbars = True
        if _is_red():
            (lo0, hi0), (lo1, _hi1) = current_ranges["red"][0], current_ranges["red"][1]
            cv2.setTrackbarPos("H min", _WINDOW, lo1[0])
            cv2.setTrackbarPos("H max", _WINDOW, hi0[0])
            cv2.setTrackbarPos("S min", _WINDOW, lo0[1])
            cv2.setTrackbarPos("S max", _WINDOW, hi0[1])
            cv2.setTrackbarPos("V min", _WINDOW, lo0[2])
            cv2.setTrackbarPos("V max", _WINDOW, hi0[2])
        else:
            lo, hi = current_ranges[_active_colour()][0]
            cv2.setTrackbarPos("H min", _WINDOW, lo[0])
            cv2.setTrackbarPos("H max", _WINDOW, hi[0])
            cv2.setTrackbarPos("S min", _WINDOW, lo[1])
            cv2.setTrackbarPos("S max", _WINDOW, hi[1])
            cv2.setTrackbarPos("V min", _WINDOW, lo[2])
            cv2.setTrackbarPos("V max", _WINDOW, hi[2])
        _updating_trackbars = False

    def _on_hsv_change(_pos: int) -> None:
        if _updating_trackbars:
            return
        _write_active_range_from_trackbars()

    def _create_trackbars() -> None:
        nonlocal trackbars_ready
        if trackbars_ready:
            return
        cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(_WINDOW, _MIN_WIDTH, 720)
        if _is_red():
            (lo0, hi0), (lo1, _hi1) = current_ranges["red"][0], current_ranges["red"][1]
            lo, hi = lo1, hi0
        else:
            lo, hi = current_ranges[_active_colour()][0]
        cv2.createTrackbar("H min", _WINDOW, lo[0], _H_MAX, _on_hsv_change)
        cv2.createTrackbar("H max", _WINDOW, hi[0], _H_MAX, _on_hsv_change)
        cv2.createTrackbar("S min", _WINDOW, lo[1], _SV_MAX, _on_hsv_change)
        cv2.createTrackbar("S max", _WINDOW, hi[1], _SV_MAX, _on_hsv_change)
        cv2.createTrackbar("V min", _WINDOW, lo[2], _SV_MAX, _on_hsv_change)
        cv2.createTrackbar("V max", _WINDOW, hi[2], _SV_MAX, _on_hsv_change)
        trackbars_ready = True
        _sync_trackbars_from_active()

    def _cycle_mask(delta: int) -> None:
        _write_active_range_from_trackbars()
        mask_index[0] = (mask_index[0] + delta) % _NUM_MASKS
        _sync_trackbars_from_active()

    def _on_mouse(event: int, x: int, y: int, _flags: int, userdata) -> None:
        nonlocal done, save_on_exit
        if event != cv2.EVENT_LBUTTONUP or userdata is None:
            return
        header_h, colour_h, panel_w = userdata
        if y < header_h:
            arrow = _arrow_at(x, y, panel_w)
            if arrow == "left":
                _cycle_mask(-1)
            elif arrow == "right":
                _cycle_mask(1)
            return
        panel_y = y - header_h - colour_h
        if panel_y < 0:
            return
        btn = _action_button_at(x, panel_y, panel_w)
        if btn == "Set":
            save_on_exit = True
            done = True
        elif btn == "Reset":
            current_ranges.clear()
            current_ranges.update(_deep_copy_ranges(original_ranges))
            _ensure_red_two_bands(current_ranges)
            _sync_trackbars_from_active()
        elif btn == "Cancel":
            done = True

    print(
        "Colour setup: use < > arrows (or , . keys) to change mask, "
        "tune H/S/V sliders, Set saves all masks, Reset restores all."
    )

    _create_trackbars()

    while not done:
        bgr_full, _ = get_frame_pair()
        if bgr_full is not None and trackbars_ready:
            ih, iw = bgr_full.shape[:2]
            rx, ry, rw, rh = compute_roi(iw, ih, search_area=active_search_area)
            roi_bgr = _apply_boost(bgr_full[ry : ry + rh, rx : rx + rw])
            colour_img, _ = classify_roi_bgr(roi_bgr, current_ranges)

            colour = _active_colour()
            mask_label = colour
            info_line = _info_line_for_colour(colour, current_ranges)

            layout_w = max(colour_img.shape[1], _MIN_WIDTH)
            header = np.zeros((_HEADER_H, layout_w, 3), dtype=np.uint8)
            _draw_mask_header(header, mask_label, mask_index[0])
            colour_disp = _center_image_width(colour_img, layout_w)
            panel = np.zeros((_PANEL_H, layout_w, 3), dtype=np.uint8)
            _draw_control_strip(panel, info_line)

            composite = np.vstack([header, colour_disp, panel])
            colour_h = colour_disp.shape[0]
            cv2.setMouseCallback(_WINDOW, _on_mouse, (_HEADER_H, colour_h, layout_w))
            cv2.imshow(_WINDOW, composite)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            done = True
        elif key == ord("s"):
            save_on_exit = True
            done = True
        elif key == ord("r"):
            current_ranges.clear()
            current_ranges.update(_deep_copy_ranges(original_ranges))
            _ensure_red_two_bands(current_ranges)
            _sync_trackbars_from_active()
        elif key == ord(",") or key == 81:
            _cycle_mask(-1)
        elif key == ord(".") or key == 83:
            _cycle_mask(1)

    _write_active_range_from_trackbars()
    cv2.destroyAllWindows()

    if save_on_exit:
        save_hsv_ranges_to_config(current_ranges)
        print(f"Saved all HSV_RANGES to {_CONFIG_PATH}")
    else:
        print("Colour setup cancelled — HSV_RANGES unchanged.")
