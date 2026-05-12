"""
play_runtime.py
---------------
Shared display loop and ROS wiring used by play_bag and play_live.
"""

import threading
from collections import deque
import cv2
import numpy as np

import json
from std_msgs.msg import String

from colour_identification import classify_frame, compute_roi, ColourIdentificationNode
from box_percentages import BoxPercentagesNode, compute_percentages, build_debug_image, LAYER_CELLS
from layer_analysis import analyse_tower, build_tower_image
from grid_generation import (
    build_edge_display,
    classify_lines,
    draw_classified_lines,
    find_hv_intersections_from_classified,
)
from tower_mask import compute_hex_region, build_display
from tower_analysis import (
    build_depth_feed_display,
    explain_tower_depth_skip,
    estimate_tower_depth_stats,
    estimate_tower_offset,
)
from perception_config import (
    GRID_CORNERS,
    DIVIDE_LINE,
    TOWER_ANALYSIS_ENABLED,
    BOX_PERCENTAGES_ENABLED,
    PLAY_RUNTIME_ROI_MARGIN,
    TOWER_FINDER_GROW_RATIO,
    EDGE_DETECTION_ENABLED,
    EDGE_HISTORY_FRAMES,
    GRID_POINTS_ENABLED,
    GRID_POINTS_MAX_INPUT_LINES,
    POINTS_OVERLAY_PAUSE_FRAMES,
    POINT_VALID_SIDE_BAND_PCT,
    POINT_VALID_CENTER_BAND_PCT,
)

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def _draw_grid(disp: np.ndarray, offset_x: int, offset_y: int) -> None:
    def valid(p) -> bool:
        return isinstance(p, (tuple, list)) and len(p) == 2

    rows = len(GRID_CORNERS)
    cols = len(GRID_CORNERS[0]) if rows else 0

    for r in range(rows):
        for c in range(cols - 1):
            p1, p2 = GRID_CORNERS[r][c], GRID_CORNERS[r][c + 1]
            if valid(p1) and valid(p2):
                cv2.line(
                    disp,
                    (p1[0] - offset_x, p1[1] - offset_y),
                    (p2[0] - offset_x, p2[1] - offset_y),
                    (0, 255, 0),
                    1,
                )

    for c in range(cols):
        for r in range(rows - 1):
            p1, p2 = GRID_CORNERS[r][c], GRID_CORNERS[r + 1][c]
            if valid(p1) and valid(p2):
                cv2.line(
                    disp,
                    (p1[0] - offset_x, p1[1] - offset_y),
                    (p2[0] - offset_x, p2[1] - offset_y),
                    (255, 100, 0),
                    1,
                )


def _crop_tower_finder_display(
    tower_disp: np.ndarray,
    pts: np.ndarray | None,
    frame_width: int,
    frame_height: int,
    grow_ratio: float = TOWER_FINDER_GROW_RATIO,
) -> np.ndarray:
    """Crop Tower finder view to a box grown around the detected hex."""
    if pts is None:
        return tower_disp

    raw_x_min = int(np.min(pts[:, 0]))
    raw_x_max = int(np.max(pts[:, 0]))
    raw_y_min = int(np.min(pts[:, 1]))
    raw_y_max = int(np.max(pts[:, 1]))
    hex_w = max(1, raw_x_max - raw_x_min)
    hex_h = max(1, raw_y_max - raw_y_min)
    grow_x = int(round(hex_w * grow_ratio * 0.5))
    grow_y = int(round(hex_h * grow_ratio * 0.5))

    x_min = max(0, raw_x_min - grow_x)
    x_max = min(frame_width, raw_x_max + grow_x)
    y_min = max(0, raw_y_min - grow_y)
    y_max = min(frame_height, raw_y_max + grow_y)

    left = tower_disp[y_min:y_max, x_min:x_max]
    right = tower_disp[y_min:y_max, frame_width + x_min:frame_width + x_max]
    return np.hstack([left, right])


def _ensure_window_open(name: str) -> None:
    """Create/recreate a window if it is missing or closed."""
    try:
        visible = cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE)
        if visible < 1:
            cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    except cv2.error:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)


def _filter_points_by_x_bands(
    points_roi: list[tuple[int, int]],
    roi_width: int,
) -> list[tuple[int, int]]:
    """Keep only points in left/right outer bands and center band."""
    if roi_width <= 0 or not points_roi:
        return []

    side_frac = max(0.0, min(0.5, float(POINT_VALID_SIDE_BAND_PCT) / 100.0))
    center_frac = max(0.0, min(1.0, float(POINT_VALID_CENTER_BAND_PCT) / 100.0))
    half_center = center_frac * 0.5
    center_lo = 0.5 - half_center
    center_hi = 0.5 + half_center

    filtered: list[tuple[int, int]] = []
    denom = float(max(1, roi_width - 1))
    for ix, iy in points_roi:
        x_frac = float(ix) / denom
        in_left_outer = x_frac <= side_frac
        in_right_outer = x_frac >= (1.0 - side_frac)
        in_center = center_lo <= x_frac <= center_hi
        if in_left_outer or in_center or in_right_outer:
            filtered.append((ix, iy))
    return filtered


def _build_cells_from_locked_points(
    points_roi: list[tuple[int, int]],
    roi_xywh: tuple[int, int, int, int],
) -> list[list[dict]]:
    """
    Map detected points onto GRID_CORNERS template and build dynamic layer cells.
    """
    rx, ry, _, _ = roi_xywh
    if not points_roi:
        return []

    # Convert ROI points to full-frame coords.
    detected_full = np.array(
        [(int(ix + rx), int(iy + ry)) for ix, iy in points_roi],
        dtype=np.float32,
    )

    # Build rows directly from detected points.
    # Rule requested: num_layers = (total_points - 3) // 3
    # Each layer uses 2 rows of 3 corner points; therefore rows = num_layers + 1.
    cols = 3
    total_points = int(len(detected_full))
    num_layers = (total_points - 3) // 3
    if num_layers < 1:
        return []
    rows = num_layers + 1
    expected = rows * cols
    if total_points < expected:
        return []

    y_order = np.argsort(detected_full[:, 1])
    selected = detected_full[y_order][:expected]

    mapped_grid: list[list[tuple[int, int] | None]] = []
    for r in range(rows):
        row_points = selected[r * cols:(r + 1) * cols]
        if len(row_points) < cols:
            return []
        row_x_order = np.argsort(row_points[:, 0])
        ordered_row = row_points[row_x_order]
        mapped_grid.append(
            [(int(px), int(py)) for px, py in ordered_row]
        )

    dynamic_layers: list[list[dict]] = []
    for r in range(len(mapped_grid) - 1):
        top = mapped_grid[r]
        bot = mapped_grid[r + 1]
        if len(top) < 3 or len(bot) < 3:
            continue

        left_corners = [top[0], top[1], bot[0], bot[1]]
        right_corners = [top[1], top[2], bot[1], bot[2]]
        if any(c is None for c in left_corners + right_corners):
            continue

        dynamic_layers.append(
            [
                {"name": f"left_cell_r{r}", "corners": left_corners},
                {"name": f"right_cell_r{r}", "corners": right_corners},
            ]
        )
    return dynamic_layers


def _run_loop(get_frame_pair, on_points_locked=None, publish_top_layer=None) -> None:
    cv2.namedWindow("Live + grid", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Colour mask", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Box percentages", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Layer Analysis", cv2.WINDOW_NORMAL)
    if EDGE_DETECTION_ENABLED:
        cv2.namedWindow("Edges (grey)", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Edges (grey history)", cv2.WINDOW_NORMAL)
    if TOWER_ANALYSIS_ENABLED:
        cv2.namedWindow("Tower finder", cv2.WINDOW_NORMAL)
    if TOWER_ANALYSIS_ENABLED:
        cv2.namedWindow("Depth feed", cv2.WINDOW_NORMAL)


    frame_n = 0
    roi_margin = PLAY_RUNTIME_ROI_MARGIN
    grey_line_history: deque[list[tuple]] = deque(maxlen=EDGE_HISTORY_FRAMES)
    points_locked = False
    locked_layer_cells: list[list[dict]] = []
    live_valid_points_full: list[tuple[int, int]] = []
    _last_pct_results: list[dict] = []
    _last_tower_img: np.ndarray | None = None
    ANALYSIS_INTERVAL = 5  # re-run heavy analysis every N frames after lock

    while True:
        bgr, depth_mm = get_frame_pair()
        if bgr is None:
            if (cv2.waitKey(10) & 0xFF) == ord("q"):
                break
            continue

        ih, iw = bgr.shape[:2]
        frame_n += 1
        last_grid_points: list[tuple[int, int]] = []

        # --- live view ---
        rx, ry, rw, rh = compute_roi(iw, ih)
        mx, my = int(rw * roi_margin), int(rh * roi_margin)
        dx1 = max(0, rx - mx);  dy1 = max(0, ry - my)
        dx2 = min(iw, rx + rw + mx);  dy2 = min(ih, ry + rh + my)

        live_disp = bgr[dy1:dy2, dx1:dx2].copy()
        cv2.rectangle(live_disp, (rx - dx1, ry - dy1), (rx + rw - dx1, ry + rh - dy1), (255, 255, 0), 2)
        _draw_grid(live_disp, dx1, dy1)
        (fx1, fy1), (fx2, fy2) = DIVIDE_LINE
        cv2.line(live_disp, (fx1 - dx1, fy1 - dy1), (fx2 - dx1, fy2 - dy1), (255, 255, 255), 1, cv2.LINE_AA)
        if frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES)):
            for px, py in live_valid_points_full:
                lx, ly = int(px - dx1), int(py - dy1)
                if 0 <= lx < live_disp.shape[1] and 0 <= ly < live_disp.shape[0]:
                    cv2.circle(live_disp, (lx, ly), 2, (0, 0, 255), -1)
        cv2.imshow("Live + grid", live_disp)

        colour_img = None
        # --- colour mask ---
        # After lock, only classify if BOX_PERCENTAGES_ENABLED needs it; edge
        # detection history is frozen so we skip the expensive classify+edge path.
        if not points_locked or BOX_PERCENTAGES_ENABLED:
            colour_img, _ = classify_frame(bgr)
            cv2.imshow("Colour mask", colour_img)

        # --- edge detection ---
        if EDGE_DETECTION_ENABLED and colour_img is not None:
            disp_grey, lines_grey = build_edge_display(colour_img, bgr)
            if not points_locked:
                grey_line_history.append(lines_grey)
                history_lines_flat: list[tuple] = []
                line_cap = max(1, int(GRID_POINTS_MAX_INPUT_LINES))
                for hist_lines in reversed(grey_line_history):
                    for line in hist_lines:
                        history_lines_flat.append(line)
                        if len(history_lines_flat) >= line_cap:
                            break
                    if len(history_lines_flat) >= line_cap:
                        break
                horiz_hist, vert_hist = classify_lines(history_lines_flat)
                history_disp = draw_classified_lines(
                    np.zeros_like(disp_grey),
                    horiz_hist,
                    vert_hist,
                )
                if GRID_POINTS_ENABLED:
                    last_grid_points = find_hv_intersections_from_classified(
                        horiz_hist,
                        vert_hist,
                        history_disp.shape,
                    )
                    last_grid_points = _filter_points_by_x_bands(last_grid_points, rw)
                    if frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES)):
                        live_valid_points_full = [
                            (int(ix + rx), int(iy + ry)) for ix, iy in last_grid_points
                        ]
                    for ix, iy in last_grid_points:
                        cv2.circle(history_disp, (ix, iy), 3, (0, 0, 255), -1)
            else:
                history_disp = disp_grey.copy()
            cv2.imshow("Edges (grey)", disp_grey)
            cv2.imshow("Edges (grey history)", history_disp)

        if (
            frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES))
            and EDGE_DETECTION_ENABLED
            and not points_locked
            and GRID_POINTS_ENABLED
            and last_grid_points
        ):
            locked_layer_cells = _build_cells_from_locked_points(
                last_grid_points,
                (rx, ry, rw, rh),
            )
            if locked_layer_cells:
                points_locked = True
                if on_points_locked is not None:
                    on_points_locked()

        tower_analysis_active = TOWER_ANALYSIS_ENABLED
        pts = compute_hex_region(bgr) if tower_analysis_active else None
        sat_disp = build_display(bgr, pts) if tower_analysis_active else None
        tower_depth = estimate_tower_depth_stats(depth_mm, pts) if tower_analysis_active else None
        tower_offset = (
            estimate_tower_offset(
                pts=pts,
                image_width_px=iw,
                depth_m=None if tower_depth is None else tower_depth["tower_depth_m"],
            )
            if tower_analysis_active
            else None
        )
        if tower_analysis_active and sat_disp is not None:
            if tower_depth is not None:
                cv2.putText(
                    sat_disp,
                    f"Tower depth ~ {tower_depth['tower_depth_m']:.3f} m",
                    (10, 26),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
            if tower_offset is not None:
                if tower_offset["lateral_m"] is not None:
                    cv2.putText(
                        sat_disp,
                        f"Offset from center: {tower_offset['dx_px']:+.0f}px  (~{tower_offset['lateral_m']:+.3f} m)",
                        (10, 52),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.50,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )
                else:
                    cv2.putText(
                        sat_disp,
                        f"Offset from center: {tower_offset['dx_px']:+.0f}px",
                        (10, 52),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.50,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )
            cv2.imshow("Tower finder", _crop_tower_finder_display(sat_disp, pts, iw, ih))
        if tower_analysis_active:
            cv2.imshow("Depth feed", build_depth_feed_display(depth_mm, bgr.shape, pts))

        # --- box percentages + layer analysis (always active after lock) ---
        if points_locked:
            if frame_n % ANALYSIS_INTERVAL == 0:
                active_cells = [cell for layer in locked_layer_cells for cell in layer]
                _last_pct_results = compute_percentages(bgr, cells=active_cells)
                row_cells = [(layer[0], layer[1]) for layer in locked_layer_cells]
                tower = analyse_tower(bgr, depth_mm, row_cells)
                
                
                if tower and publish_top_layer:
                    # We send the top-most layer (0) to the GUI
                    publish_top_layer(tower[0])
                
                
                _last_tower_img = build_tower_image(tower)
            if _last_pct_results:
                active_cells = [cell for layer in locked_layer_cells for cell in layer]
                _ensure_window_open("Box percentages")
                cv2.imshow(
                    "Box percentages",
                    build_debug_image(bgr, _last_pct_results, cells=active_cells),
                )
            if _last_tower_img is not None:
                _ensure_window_open("Layer Analysis")
                cv2.imshow("Layer Analysis", _last_tower_img)
        elif BOX_PERCENTAGES_ENABLED and frame_n % 30 == 0:
            # Pre-lock periodic display using static LAYER_CELLS
            active_cells = [cell for layer in LAYER_CELLS for cell in layer]
            pct_results = compute_percentages(bgr, cells=active_cells)
            _ensure_window_open("Box percentages")
            cv2.imshow("Box percentages", build_debug_image(bgr, pct_results, cells=active_cells))
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

class _ImageBridge(Node):
    def __init__(self, color_topic: str, depth_topic: str | list[str] | tuple[str, ...]):
        super().__init__("play_image_bridge")
        self._bridge = CvBridge()
        self._lock = threading.Lock()
        self._bgr = None
        self._depth_mm = None
        self._depth_enc_warned = False
        self._active_depth_topic: str | None = None
        self._depth_subscriptions = []
        self.create_subscription(Image, color_topic, self._cb, 10)
        self.top_layer_pub = self.create_publisher(String, '/top_layer_state', 10)
        depth_topics = [depth_topic] if isinstance(depth_topic, str) else list(depth_topic)
        for topic in depth_topics:
            sub = self.create_subscription(
                Image,
                topic,
                lambda msg, t=topic: self._depth_cb(msg, t),
                10,
            )
            self._depth_subscriptions.append(sub)
        self.get_logger().info(
            "Depth topic candidates: " + ", ".join(depth_topics)
        )
    
    def publish_top_layer(self, layer_data):
        msg = String()
        msg.data = json.dumps(layer_data)
        self.top_layer_pub.publish(msg)

    def _cb(self, msg: Image):
        enc = (msg.encoding or "").lower()
        bgr = (
            cv2.cvtColor(self._bridge.imgmsg_to_cv2(msg, "rgb8"), cv2.COLOR_RGB2BGR)
            if enc == "rgb8"
            else self._bridge.imgmsg_to_cv2(msg, "bgr8")
        )
        with self._lock:
            self._bgr = bgr

    def _depth_cb(self, msg: Image, topic_name: str):
        if self._active_depth_topic is not None and topic_name != self._active_depth_topic:
            return
        enc = (msg.encoding or "").lower()
        if "16uc1" in enc or "mono16" in enc:
            depth_mm = self._bridge.imgmsg_to_cv2(msg, "16UC1")
        elif "32fc1" in enc:
            # Some stacks publish depth in metres
            m = self._bridge.imgmsg_to_cv2(msg, "32FC1")
            depth_mm = np.clip(m * 1000.0, 0, 65_535).astype(np.uint16)
        else:
            if not self._depth_enc_warned:
                self.get_logger().warning(
                    "Ignoring depth: encoding %r (need 16UC1/mono16 or 32FC1). "
                    "No depth will be used until the driver publishes a supported type."
                    % (msg.encoding,)
                )
                self._depth_enc_warned = True
            return
        with self._lock:
            self._depth_mm = depth_mm
        if self._active_depth_topic is None:
            self._active_depth_topic = topic_name
            self.get_logger().info(
                f"Using depth topic: {topic_name} (encoding={msg.encoding})"
            )

    def get_frame_pair(self):
        with self._lock:
            bgr = None if self._bgr is None else self._bgr.copy()
            depth_mm = None if self._depth_mm is None else self._depth_mm.copy()
            return bgr, depth_mm


def _start_executor(nodes: list) -> SingleThreadedExecutor:
    executor = SingleThreadedExecutor()
    for n in nodes:
        executor.add_node(n)
    threading.Thread(target=executor.spin, daemon=True).start()
    return executor


def _shutdown_executor(executor: SingleThreadedExecutor, nodes: list) -> None:
    executor.shutdown()
    for n in nodes:
        n.destroy_node()
    rclpy.shutdown()


def run_with_pipeline(pipeline) -> None:
    import pyrealsense2 as rs

    align = rs.align(rs.stream.color)

    def get_frame_pair():
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        aligned = align.process(frames)
        color_frame = aligned.get_color_frame()
        depth_frame = aligned.get_depth_frame()
        if color_frame is None or not color_frame:
            return None, None

        frame = np.asanyarray(color_frame.get_data())
        frame_format = str(color_frame.profile.format()).lower()

        # Newer recordings may be RGB8; normalize to BGR for OpenCV pipeline/display.
        if "rgb8" in frame_format and "bgr8" not in frame_format:
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            bgr = frame

        if depth_frame is None or not depth_frame:
            depth_mm = None
        else:
            try:
                depth_mm = np.asanyarray(depth_frame.get_data())
            except RuntimeError:
                # Some bags expose an invalid depth handle on certain frames.
                depth_mm = None
        return bgr, depth_mm

    _run_loop(get_frame_pair)


def run_subscribe(
    color_topic: str,
    depth_topic: str | list[str] | tuple[str, ...],
) -> None:
    rclpy.init()

    bridge = _ImageBridge(color_topic, depth_topic)
    nodes: list = [bridge]
    if EDGE_DETECTION_ENABLED:
        nodes.append(ColourIdentificationNode(color_topic))
    executor = _start_executor(nodes)
    box_node: BoxPercentagesNode | None = None

    def _start_box_percentages_node() -> None:
        nonlocal box_node
        if not BOX_PERCENTAGES_ENABLED or box_node is not None:
            return
        box_node = BoxPercentagesNode(color_topic)
        nodes.append(box_node)
        executor.add_node(box_node)

    try:
        _run_loop(
                    bridge.get_frame_pair, 
                    on_points_locked=_start_box_percentages_node,
                    publish_top_layer=bridge.publish_top_layer
                )
    finally:
        _shutdown_executor(executor, nodes)