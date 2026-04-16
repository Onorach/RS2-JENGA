"""
box_colour_probe.py
--------------------
While video plays, compute per-box colour percentages by examining every pixel inside each box.

The box locations are taken from `play.py` as `BOX6_POINTS`.
Colour assignment uses the HSV ranges from `jenga_perception_colour.py` (via `JengaPerceptionNode`).

Prints box percentages every 2 seconds and overlays the current percentages in the window.

Keyboard: q = quit
"""

from __future__ import annotations

import sys
import time

import cv2
import numpy as np
from jenga_perception_colour import JengaPerceptionNode

# Reuse playback + ROI display logic from play.py
import play as play_view


# Use the boxes from play.py (shared configuration)
BOX6_POINTS = play_view.BOX6_POINTS


def _points_to_boxes(box6: list[tuple[int, int]]) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
      box1_pts (4,2), box2_pts (4,2) as float32 arrays.
    """
    if len(box6) != 6:
        raise ValueError("BOX6_POINTS must contain exactly 6 points.")

    p0, p1, p2, p3, p4, p5 = box6
    box1 = np.array([p0, p1, p4, p5], dtype=np.int32)
    box2 = np.array([p1, p2, p3, p4], dtype=np.int32)
    return box1, box2


def _fill_box_mask(h: int, w: int, quad_pts_int: np.ndarray) -> np.ndarray:
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillConvexPoly(mask, quad_pts_int, 1)
    return mask


def compute_box_colour_percentages(bgr: np.ndarray, quad_pts: np.ndarray, hsv_ranges: dict) -> dict[str, float]:
    """
    Returns percentages for each named colour plus "none".
    Percentages sum to ~100.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, w = hsv.shape[:2]

    box_mask = _fill_box_mask(h, w, quad_pts)
    total = int(np.count_nonzero(box_mask))
    if total <= 0:
        return {"none": 100.0}

    assigned = np.zeros((h, w), dtype=bool)
    remaining_mask = box_mask.astype(bool)

    # Stable precedence order using the dict insertion order from hsv_ranges.
    result: dict[str, float] = {}
    assigned_any = np.zeros((h, w), dtype=bool)

    for colour_name, ranges in hsv_ranges.items():
        colour_mask = np.zeros((h, w), dtype=np.uint8)
        for (lo, hi) in ranges:
            lo_np = np.array(lo, dtype=np.uint8)
            hi_np = np.array(hi, dtype=np.uint8)
            colour_mask = cv2.bitwise_or(colour_mask, cv2.inRange(hsv, lo_np, hi_np))

        colour_hits = (colour_mask > 0) & remaining_mask
        cnt = int(np.count_nonzero(colour_hits))
        result[colour_name] = 100.0 * cnt / float(total)

        assigned_any |= colour_hits
        remaining_mask &= ~colour_hits

    none_cnt = int(np.count_nonzero(remaining_mask))
    result["none"] = 100.0 * none_cnt / float(total)
    return result


def _format_percentages(pcts: dict[str, float]) -> str:
    # Order some keys if present
    order = ["blue", "green", "red", "yellow", "purple", "none"]
    parts = []
    used = set()
    for k in order:
        if k in pcts:
            parts.append(f"{k} {pcts[k]:.0f}%")
            used.add(k)
    for k in pcts.keys():
        if k not in used:
            parts.append(f"{k} {pcts[k]:.0f}%")
    return ", ".join(parts)


def _draw_quad(bgr: np.ndarray, quad_pts: np.ndarray, colour: tuple[int, int, int]) -> None:
    cv2.polylines(bgr, [quad_pts.astype(np.int32)], isClosed=True, color=colour, thickness=2)


def _main_loop(pipeline) -> None:
    # HSV ranges from your existing colour module.
    node = JengaPerceptionNode()
    hsv_ranges = node.hsv_ranges

    box1_pts = None
    box2_pts = None
    if len(BOX6_POINTS) == 6:
        box1_pts, box2_pts = _points_to_boxes(BOX6_POINTS)
    else:
        print("BOX6_POINTS is empty/invalid. Fill it in `play.py` with 6 points to define two boxes.")

    last_print = 0.0
    print_period_s = 2.0

    while True:
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        colour_frame = frames.get_color_frame()
        if colour_frame is None:
            continue

        bgr = np.asanyarray(colour_frame.get_data())

        # Match the same ROI+margin display strategy as play.py
        ih, iw = bgr.shape[:2]
        roi_x, roi_y, roi_w, roi_h = play_view._compute_search_roi(iw, ih)
        roi_margin_frac = 0.10
        mx = int(roi_w * roi_margin_frac)
        my = int(roi_h * roi_margin_frac)
        dx1 = max(0, roi_x - mx)
        dy1 = max(0, roi_y - my)
        dx2 = min(iw, roi_x + roi_w + mx)
        dy2 = min(ih, roi_y + roi_h + my)

        disp = bgr[dy1:dy2, dx1:dx2].copy()

        # ROI rectangle on display crop
        cv2.rectangle(
            disp,
            (roi_x - dx1, roi_y - dy1),
            (roi_x + roi_w - dx1, roi_y + roi_h - dy1),
            (255, 255, 0),
            2,
        )

        box1_text = ""
        box2_text = ""
        if box1_pts is not None and box2_pts is not None:
            p1 = compute_box_colour_percentages(bgr, box1_pts, hsv_ranges)
            p2 = compute_box_colour_percentages(bgr, box2_pts, hsv_ranges)

            # Draw quads on the display crop with translated coordinates
            b1 = box1_pts.copy()
            b2 = box2_pts.copy()
            b1[:, 0] -= dx1
            b1[:, 1] -= dy1
            b2[:, 0] -= dx1
            b2[:, 1] -= dy1
            _draw_quad(disp, b1, (0, 255, 0))
            _draw_quad(disp, b2, (255, 100, 0))

            box1_text = _format_percentages(p1)
            box2_text = _format_percentages(p2)

            now = time.time()
            if now - last_print >= print_period_s:
                print(f"[Box Colour] Box1: {box1_text} | Box2: {box2_text}")
                last_print = now

        if box1_pts is not None and box2_pts is not None:
            cv2.putText(disp, f"Box1: {box1_text}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(disp, f"Box2: {box2_text}", (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Box Colour Probe", disp)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


def main() -> None:
    bag_arg = sys.argv[1] if len(sys.argv) > 1 else None
    live_mode = bag_arg is None
    bag_path = play_view._resolve_bag_path(bag_arg) if bag_arg is not None else None
    pipeline = play_view._start_playback(live_mode=live_mode, bag_path=bag_path)
    try:
        _main_loop(pipeline)
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

