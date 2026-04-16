"""
play.py
-------
Live / bag viewer with:
  - fixed search ROI rectangle (cyan)
  - window showing ROI + ~10% margin
  - non-even grid lines drawn from a user-provided 3x8 corner array

Keyboard:
  q = quit

Fill in GRID_CORNERS_3x8 with 56 corner points (row-major):
  grid[row][col] = (x_px, y_px) in the full camera frame.
"""

import os
import sys
from typing import Optional

import cv2
import numpy as np
import pyrealsense2 as rs
from analyze_box_colors import analyse_frame
from roi_color_view import update_roi_colour_window 
from update_box_colors import update_blob_box_window

# -----------------------------------------------------------------------------
# Search ROI (fractions of the full image size)
# -----------------------------------------------------------------------------
SEARCH_CX_FRAC = 0.495
SEARCH_CY_FRAC = 0.485
SEARCH_W_FRAC = 0.32
SEARCH_H_FRAC = 0.62

# -----------------------------------------------------------------------------
# Grid corners: 3 x 8 points (56 total)
# -----------------------------------------------------------------------------
# Corner order:
# - points[row][col] with 0<=row<8 and 0<=col<3
# - row lines connect horizontally (same row, adjacent cols)
# - col lines connect vertically (same col, adjacent rows)
#
# Fill in these pixel coordinates for your camera resolution (typically 1920x1080).
GRID_CORNERS_3x8: list[list[Optional[tuple[int, int]]]] = [
    # Row 0 (edit these or leave as None)
    [(664, 197), (920, 217), (1237, 215)],
    [(669, 282), (916, 315), (1228, 297)],
    [(695, 722), (914, 850), (1205, 742)],
    [None, None, None],
    [None, None, None],
    [None, None, None],
    [None, None, None],

]

GRID_COLS = 3
GRID_ROWS = 8


def _compute_search_roi(iw: int, ih: int) -> tuple[int, int, int, int]:
    cw = int(iw * SEARCH_W_FRAC)
    ch = int(ih * SEARCH_H_FRAC)
    cx = int(iw * SEARCH_CX_FRAC) - cw // 2
    cy = int(ih * SEARCH_CY_FRAC) - ch // 2
    x = max(0, min(cx, iw - cw))
    y = max(0, min(cy, ih - ch))
    return x, y, cw, ch


def _resolve_bag_path(arg_path: str) -> str:
    base = os.path.dirname(__file__)
    candidates = [
        arg_path,  # absolute / relative
        os.path.join(base, "camera_files", "rgbd_raw", arg_path),
        os.path.join(base, "camera_files", "rgbd_large", arg_path),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return os.path.join(base, "camera_files", "rgbd_raw", arg_path)


def _add_grid_lines(disp: np.ndarray, dx1: int, dy1: int) -> None:
    """
    Draw grid lines between adjacent points in the 3x8 corner array.
    Non-even grid: points can be irregular; lines are straight between points.
    """
    h, w = disp.shape[:2]
    _ = (h, w)

    def _is_xy_point(p: object) -> bool:
        return (
            isinstance(p, (tuple, list))
            and len(p) == 2
            and isinstance(p[0], (int, float))
            and isinstance(p[1], (int, float))
        )

    grid_rows = len(GRID_CORNERS_3x8)
    grid_cols = len(GRID_CORNERS_3x8[0]) if grid_rows > 0 else 0
    if grid_rows <= 0 or grid_cols <= 0:
        return

    # Horizontal lines: within each row, connect col->col+1
    for r in range(grid_rows):
        for c in range(grid_cols - 1):
            p1 = GRID_CORNERS_3x8[r][c]
            p2 = GRID_CORNERS_3x8[r][c + 1]
            if not _is_xy_point(p1) or not _is_xy_point(p2):
                continue
            x1, y1 = p1[0] - dx1, p1[1] - dy1
            x2, y2 = p2[0] - dx1, p2[1] - dy1
            cv2.line(disp, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 1)

    # Vertical lines: within each col, connect row->row+1
    for c in range(grid_cols):
        for r in range(grid_rows - 1):
            p1 = GRID_CORNERS_3x8[r][c]
            p2 = GRID_CORNERS_3x8[r + 1][c]
            if not _is_xy_point(p1) or not _is_xy_point(p2):
                continue
            x1, y1 = p1[0] - dx1, p1[1] - dy1
            x2, y2 = p2[0] - dx1, p2[1] - dy1
            cv2.line(disp, (int(x1), int(y1)), (int(x2), int(y2)), (255, 100, 0), 1)

    # Physical dot at each valid grid point
    h, w = disp.shape[:2]
    for r in range(grid_rows):
        for c in range(grid_cols):
            p = GRID_CORNERS_3x8[r][c]
            if not _is_xy_point(p):
                continue
            cx, cy = int(p[0] - dx1), int(p[1] - dy1)
            # Avoid excessive drawing outside the display crop.
            if cx < 0 or cx >= w or cy < 0 or cy >= h:
                continue
            cv2.circle(disp, (cx, cy), 5, (255, 255, 255), -1)


def _start_playback(live_mode: bool, bag_path: Optional[str]):
    pipeline = rs.pipeline()
    config = rs.config()

    if live_mode:
        config.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8, 30)
    else:
        # Robust playback: let the bag define stream details.
        rs.config.enable_device_from_file(config, bag_path, repeat_playback=True)  # type: ignore[arg-type]
        config.enable_stream(rs.stream.color)

    try:
        profile = pipeline.start(config)
    except Exception as e:
        if live_mode:
            raise
        # Final fallback: no explicit enable_stream constraints.
        pipeline = rs.pipeline()
        config2 = rs.config()
        rs.config.enable_device_from_file(config2, bag_path, repeat_playback=True)  # type: ignore[arg-type]
    return pipeline


def _show_window(pipeline) -> None:
    window = "Jenga Grid"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    roi_margin_frac = 0.10

    frame_counter = 0

    while True:
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        color_frame = frames.get_color_frame()
        if color_frame is None:
            continue

        color_bgr = np.asanyarray(color_frame.get_data())

        update_roi_colour_window(color_bgr)
        update_blob_box_window(color_bgr)

        frame_counter += 1 
        if frame_counter % 30 == 0: 
            analyse_frame(color_bgr) # uses full frame
        
        ih, iw = color_bgr.shape[:2]

        roi_x, roi_y, roi_w, roi_h = _compute_search_roi(iw, ih)

        mx = int(roi_w * roi_margin_frac)
        my = int(roi_h * roi_margin_frac)
        dx1 = max(0, roi_x - mx)
        dy1 = max(0, roi_y - my)
        dx2 = min(iw, roi_x + roi_w + mx)
        dy2 = min(ih, roi_y + roi_h + my)

        disp = color_bgr[dy1:dy2, dx1:dx2].copy()

        # Search ROI rectangle (cyan)
        cv2.rectangle(
            disp,
            (roi_x - dx1, roi_y - dy1),
            (roi_x + roi_w - dx1, roi_y + roi_h - dy1),
            (255, 255, 0),
            2,
        )

        # Grid lines from 3x8 corner points
        _add_grid_lines(disp=disp, dx1=dx1, dy1=dy1)

        cv2.imshow(window, disp)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


def main() -> None:
    bag_arg = sys.argv[1] if len(sys.argv) > 1 else None
    live_mode = bag_arg is None
    bag_path = _resolve_bag_path(bag_arg) if bag_arg is not None else None

    pipeline = _start_playback(live_mode=live_mode, bag_path=bag_path)
    try:
        _show_window(pipeline)
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
