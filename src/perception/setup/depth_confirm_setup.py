"""
depth_confirm_setup.py
----------------------
Final step of play_live.py --setup: live depth preview before exiting calibration.

Shows a colour-mapped aligned depth image. Confirm to finish setup, Cancel to abort.
"""

from __future__ import annotations

from typing import Callable

import cv2
import numpy as np

_WINDOW = "Confirm depth image"
_MIN_WIDTH = 640
_PANEL_H = 88
_BTN_Y0 = 46
_BTN_H = 36
_BTN_W = 140
_BTN_GAP = 24


def _btn_x0(panel_w: int) -> int:
    return (panel_w - (2 * _BTN_W + _BTN_GAP)) // 2


def _action_button_at(panel_x: int, panel_y: int, panel_w: int) -> str | None:
    if not (_BTN_Y0 <= panel_y < _BTN_Y0 + _BTN_H):
        return None
    bx0 = _btn_x0(panel_w)
    for i, name in enumerate(("Confirm", "Cancel")):
        x1 = bx0 + i * (_BTN_W + _BTN_GAP)
        if x1 <= panel_x < x1 + _BTN_W:
            return name
    return None


def _depth_stats(depth_mm: np.ndarray | None) -> tuple[str, float, float, float]:
    if depth_mm is None:
        return "No depth frame received (check depth topic / camera).", 0.0, 0.0, 0.0
    valid = depth_mm > 0
    n_valid = int(valid.sum())
    total = depth_mm.size
    if n_valid == 0:
        return "Depth frame has no valid pixels (>0 mm).", 0.0, 0.0, 0.0
    vals = depth_mm[valid].astype(np.float32)
    pct = 100.0 * n_valid / total
    return (
        f"Valid depth: {pct:.1f}% of pixels  |  "
        f"range {vals.min():.0f}–{vals.max():.0f} mm  |  "
        f"median {np.median(vals):.0f} mm",
        pct,
        float(vals.min()),
        float(np.median(vals)),
    )


def _depth_to_colour(depth_mm: np.ndarray | None) -> np.ndarray:
    """Render depth as a colour map for display (turbo: near=purple, far=yellow)."""
    if depth_mm is None:
        return np.zeros((_MIN_WIDTH, _MIN_WIDTH, 3), dtype=np.uint8)

    h, w = depth_mm.shape[:2]
    valid = depth_mm > 0
    if not np.any(valid):
        blank = np.zeros((h, w, 3), dtype=np.uint8)
        cv2.putText(
            blank,
            "No valid depth",
            (max(10, w // 2 - 80), max(20, h // 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
        return blank

    vals = depth_mm[valid].astype(np.float32)
    lo, hi = np.percentile(vals, [2, 98])
    if hi <= lo:
        hi = lo + 1.0
    norm = np.clip((depth_mm.astype(np.float32) - lo) / (hi - lo), 0, 1)
    norm = (norm * 255).astype(np.uint8)
    norm[~valid] = 0
    return cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)


def _draw_panel(panel: np.ndarray, info_line: str, aligned: bool) -> None:
    panel[:] = (42, 42, 42)
    align_txt = "aligned to colour" if aligned else "size mismatch with colour"
    cv2.putText(
        panel,
        info_line,
        (12, 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (220, 220, 220),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        panel,
        f"Depth is {align_txt}.  Confirm if the image looks correct (s / Enter).",
        (12, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (150, 150, 150),
        1,
        cv2.LINE_AA,
    )
    bx0 = _btn_x0(panel.shape[1])
    for i, (label, colour) in enumerate(
        (("Confirm", (80, 180, 80)), ("Cancel", (80, 80, 200)))
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


def run_depth_confirm_setup(
    get_frame_pair: Callable[[], tuple[np.ndarray | None, object]],
) -> bool:
    """
    Show live aligned depth. Returns True if the user confirms, False on cancel.
    """
    print("Depth confirm: check the depth image, then Confirm or Cancel (s / q).")

    cv2.namedWindow(_WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(_WINDOW, _MIN_WIDTH, 520)

    done = False
    confirmed = False

    def _on_mouse(event: int, x: int, y: int, _flags: int, userdata) -> None:
        nonlocal done, confirmed
        if event != cv2.EVENT_LBUTTONUP or userdata is None:
            return
        view_h, panel_w = userdata
        panel_y = y - view_h
        if panel_y < 0:
            return
        btn = _action_button_at(x, panel_y, panel_w)
        if btn == "Confirm":
            confirmed = True
            done = True
        elif btn == "Cancel":
            done = True

    while not done:
        bgr, depth_mm = get_frame_pair()
        depth_img = _depth_to_colour(
            depth_mm if depth_mm is None else np.asarray(depth_mm),
        )
        info_line, _pct, _dmin, _dmed = _depth_stats(
            None if depth_mm is None else np.asarray(depth_mm),
        )
        aligned = (
            bgr is not None
            and depth_mm is not None
            and bgr.shape[:2] == np.asarray(depth_mm).shape[:2]
        )

        layout_w = max(depth_img.shape[1], _MIN_WIDTH)
        if depth_img.shape[1] < layout_w:
            pad = layout_w - depth_img.shape[1]
            depth_img = cv2.copyMakeBorder(
                depth_img, 0, 0, 0, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0),
            )

        panel = np.zeros((_PANEL_H, layout_w, 3), dtype=np.uint8)
        _draw_panel(panel, info_line, aligned)
        composite = np.vstack([depth_img, panel])
        view_h = depth_img.shape[0]
        cv2.setMouseCallback(_WINDOW, _on_mouse, (view_h, layout_w))
        cv2.imshow(_WINDOW, composite)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            done = True
        elif key in (ord("s"), ord("\r"), 10):
            confirmed = True
            done = True

    try:
        cv2.destroyWindow(_WINDOW)
    except cv2.error:
        pass
    cv2.waitKey(1)

    if confirmed:
        print("Depth image confirmed — setup complete.")
    else:
        print("Depth confirm cancelled.")
    return confirmed
