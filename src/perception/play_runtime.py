"""
play_runtime.py
---------------
Shared display loop and ROS wiring used by play_bag and play_live.
"""

import threading
from collections import deque
import cv2
import numpy as np

from colour_identification import classify_frame, compute_roi, ColourIdentificationNode
from box_percentages import BoxPercentagesNode, compute_percentages, build_debug_image, analyse_layer, LAYER_CELLS
from edge_analysis import build_edge_display, draw_lines, merge_parallel_lines
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
    tower_analysis,
    BOX_PERCENTAGES_ENABLED,
    PLAY_RUNTIME_ROI_MARGIN,
    TOWER_FINDER_GROW_RATIO,
    EDGE_DETECTION_ENABLED,
    EDGE_HISTORY_FRAMES,
    EDGE_MERGE_PERP_DIST_PX,
    EDGE_MERGE_MAX_ANGLE_DEG,
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


def _run_loop(get_frame_pair) -> None:
    cv2.namedWindow("Live + grid", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Colour mask", cv2.WINDOW_NORMAL)
    if BOX_PERCENTAGES_ENABLED:
        cv2.namedWindow("Box percentages", cv2.WINDOW_NORMAL)
    if EDGE_DETECTION_ENABLED:
        cv2.namedWindow("Edges (grey)", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Edges (grey history)", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Edges (grey merged)", cv2.WINDOW_NORMAL)
    if tower_analysis:
        cv2.namedWindow("Tower finder", cv2.WINDOW_NORMAL)
    if tower_analysis:
        cv2.namedWindow("Depth feed", cv2.WINDOW_NORMAL)


    frame_n = 0
    roi_margin = PLAY_RUNTIME_ROI_MARGIN
    grey_line_history: deque[list[tuple]] = deque(maxlen=EDGE_HISTORY_FRAMES)

    while True:
        bgr, depth_mm = get_frame_pair()
        if bgr is None:
            if (cv2.waitKey(10) & 0xFF) == ord("q"):
                break
            continue

        ih, iw = bgr.shape[:2]
        frame_n += 1

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
        cv2.imshow("Live + grid", live_disp)

        # --- colour mask ---
        colour_img, _ = classify_frame(bgr)
        cv2.imshow("Colour mask", colour_img)

        # --- edge detection ---
        if EDGE_DETECTION_ENABLED:
            disp_grey, lines_grey = build_edge_display(colour_img)
            grey_line_history.append(lines_grey)
            history_disp = np.zeros_like(disp_grey)
            for hist_lines in grey_line_history:
                history_disp = draw_lines(history_disp, hist_lines)
            history_lines_flat = [line for hist_lines in grey_line_history for line in hist_lines]
            merged_lines = merge_parallel_lines(
                history_lines_flat,
                EDGE_MERGE_PERP_DIST_PX,
                EDGE_MERGE_MAX_ANGLE_DEG,
            )
            merged_disp = draw_lines(np.zeros_like(disp_grey), merged_lines)
            cv2.imshow("Edges (grey)", disp_grey)
            cv2.imshow("Edges (grey history)", history_disp)
            cv2.imshow("Edges (grey merged)", merged_disp)

        pts = compute_hex_region(bgr) if tower_analysis else None
        sat_disp = build_display(bgr, pts) if tower_analysis else None
        tower_depth = estimate_tower_depth_stats(depth_mm, pts) if tower_analysis else None
        tower_offset = (
            estimate_tower_offset(
                pts=pts,
                image_width_px=iw,
                depth_m=None if tower_depth is None else tower_depth["tower_depth_m"],
            )
            if tower_analysis
            else None
        )
        if tower_analysis and sat_disp is not None:
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
        if tower_analysis:
            cv2.imshow("Depth feed", build_depth_feed_display(depth_mm, bgr.shape, pts))

        if frame_n % 30 == 0:
            if BOX_PERCENTAGES_ENABLED:
                pct_results = compute_percentages(bgr)
                cv2.imshow("Box percentages", build_debug_image(bgr, pct_results))

                # pct_results order matches grid cells: [l0, r0, l1, r1, ...]
                for i, (left_cell, right_cell) in enumerate(LAYER_CELLS):
                    left_result = pct_results[i * 2]
                    right_result = pct_results[i * 2 + 1]
                    layer = analyse_layer(bgr, left_result, right_result, left_cell, right_cell)
                    print(
                        f"layer {i}  orientation={layer['orientation']}  "
                        + "  ".join(
                            f"{b['colour']}({b['position']:+.0f}px)" for b in layer["blocks"]
                        )
                    )
            if tower_analysis and tower_depth is not None:
                print("tower depth = " + f"{tower_depth['tower_depth_m']:.3f}m")
            elif tower_analysis:
                print("tower distance unavailable — " + explain_tower_depth_skip(bgr, depth_mm, pts))
            if tower_analysis and tower_offset is not None:
                if tower_offset["lateral_m"] is None:
                    print(
                        "tower offset "
                        + f"dx_px={tower_offset['dx_px']:+.1f}px"
                    )
                else:
                    print(
                        "tower offset "
                        + f"dx_px={tower_offset['dx_px']:+.1f}px  "
                        + f"lateral={tower_offset['lateral_m']:+.3f}m"
                    )

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
    colour_node = ColourIdentificationNode(color_topic)
    nodes: list = [bridge, colour_node]
    if BOX_PERCENTAGES_ENABLED:
        nodes.append(BoxPercentagesNode(color_topic))
    executor = _start_executor(nodes)

    try:
        _run_loop(bridge.get_frame_pair)
    finally:
        _shutdown_executor(executor, nodes)
