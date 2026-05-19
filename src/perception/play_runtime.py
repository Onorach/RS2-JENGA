"""
play_runtime.py
---------------
Shared display loop and ROS wiring used by play_bag and play_live.
All perception logic lives in the dedicated modules; this file only
orchestrates frames, windows, and ROS bridging.
"""

import threading
import time
import json
from collections import deque

import cv2
import numpy as np
from std_msgs.msg import String

from colour_identification import classify_roi_bgr, compute_roi
from box_percentages import compute_percentages, build_debug_image
from layer_analysis import analyse_tower, build_tower_image
from grid_generation import (
    build_edge_display,
    classify_lines,
    draw_classified_lines,
    find_hv_intersections_from_classified,
    filter_points_by_x_bands,
    build_layer_cells_from_points,
)
from tower_mask import (
    compute_hex_region,
    build_display,
    crop_tower_finder_display,
)

from tower_analysis import (
    estimate_tower_depth_stats,
    estimate_tower_offset,
)
from perception_config import (
    TOWER_ANALYSIS,
    BLOCK_ANALYSIS,
    SEARCH_AREA_MARGIN,
    BOOST_ENABLED,
    BOOST_SEARCH_CROP_ONLY,
    SATURATION_BOOST,
    CONTRAST_BOOST,
)

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _ensure_window_open(name: str) -> None:
    """Create or re-create an OpenCV window if it has been closed."""
    try:
        if cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) < 1:
            cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    except cv2.error:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)


def _boost_saturation_contrast(
    bgr: np.ndarray,
    sat_factor: float,
    contrast_factor: float,
) -> np.ndarray:
    """Boost HSV saturation and (V-channel) contrast in a single conversion."""
    if bgr is None or (sat_factor == 1.0 and contrast_factor == 1.0):
        return bgr
    hsv     = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    if sat_factor != 1.0:
        s = np.clip(s.astype(np.float32) * float(sat_factor), 0, 255).astype(np.uint8)
    if contrast_factor != 1.0:
        v = np.clip(
            (v.astype(np.float32) - 128.0) * float(contrast_factor) + 128.0,
            0,
            255,
        ).astype(np.uint8)
    return cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR)


def _apply_boost(bgr: np.ndarray) -> np.ndarray:
    """Apply configured saturation/contrast boost to a frame."""
    if not BOOST_ENABLED:
        return bgr
    return _boost_saturation_contrast(bgr, SATURATION_BOOST, CONTRAST_BOOST)


# ---------------------------------------------------------------------------
# Dynamic cell building from locked grid points
# ---------------------------------------------------------------------------

# Runtime-only history and timing controls for the live grid pipeline.
EDGE_HISTORY_FRAMES         = 30
POINTS_OVERLAY_PAUSE_FRAMES = 60
GRID_POINTS_MAX_INPUT_LINES = 500

# ---------------------------------------------------------------------------
# Main display loop
# ---------------------------------------------------------------------------

def _run_loop(get_frame_pair, on_points_locked=None, publish_top_layer=None) -> None:
    cv2.namedWindow("Live + grid",         cv2.WINDOW_NORMAL)
    cv2.namedWindow("Raw crop",            cv2.WINDOW_NORMAL)
    if BLOCK_ANALYSIS:
        cv2.namedWindow("Colour mask",         cv2.WINDOW_NORMAL)
        cv2.namedWindow("Canny (colour mask)", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Canny (original)",    cv2.WINDOW_NORMAL)
        cv2.namedWindow("Edges",               cv2.WINDOW_NORMAL)
        cv2.namedWindow("Box percentages",     cv2.WINDOW_NORMAL)
        cv2.namedWindow("Layer Analysis",      cv2.WINDOW_NORMAL)
    if TOWER_ANALYSIS:
        cv2.namedWindow("Tower finder", cv2.WINDOW_NORMAL)

    frame_n          = 0
    roi_margin       = SEARCH_AREA_MARGIN
    grey_line_history: deque[list[tuple]] = deque(maxlen=EDGE_HISTORY_FRAMES)
    points_locked    = False
    locked_layer_cells: list[list[dict]] = []
    live_valid_points_crop: list[tuple[int, int]] = []
    _last_pct_results: list[dict] = []
    _last_tower_img:   np.ndarray | None = None
    _last_tower_finder_print: float = 0.0
    _cached_pts:   np.ndarray | None = None
    _hex_frame_n:  int = 0

    HEX_RECOMPUTE_INTERVAL = 60   # Recompute hex detection every N frames.
    ANALYSIS_INTERVAL      = 5    # Re-run heavy analysis every N frames after lock.
    TOWER_PRINT_INTERVAL_S = 3.0

    while True:
        bgr_full, depth_mm_full = get_frame_pair()
        if bgr_full is None:
            if (cv2.waitKey(10) & 0xFF) == ord("q"):
                break
            continue

        ih, iw = bgr_full.shape[:2]
        frame_n += 1
        last_grid_points: list[tuple[int, int]] = []

        # --- Crop setup (search area + margin) ---
        rx, ry, rw, rh = compute_roi(iw, ih)
        mx, my  = int(rw * roi_margin), int(rh * roi_margin)
        dx1 = max(0, rx - mx);  dy1 = max(0, ry - my)
        dx2 = min(iw, rx + rw + mx); dy2 = min(ih, ry + rh + my)
        roi_x, roi_y = rx - dx1, ry - dy1

        raw_crop = bgr_full[dy1:dy2, dx1:dx2]
        if BOOST_SEARCH_CROP_ONLY:
            bgr = _apply_boost(raw_crop)
        else:
            bgr = _apply_boost(bgr_full)[dy1:dy2, dx1:dx2]
        depth_mm = None if depth_mm_full is None else depth_mm_full[dy1:dy2, dx1:dx2]

        # --- Live view ---
        live_disp = bgr.copy()
        cv2.imshow("Raw crop", raw_crop)
        cv2.rectangle(live_disp, (roi_x, roi_y), (roi_x + rw, roi_y + rh), (255, 255, 0), 2)
        if frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES)):
            for px, py in live_valid_points_crop:
                if 0 <= px < live_disp.shape[1] and 0 <= py < live_disp.shape[0]:
                    cv2.circle(live_disp, (int(px), int(py)), 2, (0, 0, 255), -1)
        cx = (iw // 2) - dx1
        if 0 <= cx < live_disp.shape[1]:
            cv2.line(live_disp, (cx, 0), (cx, live_disp.shape[0] - 1), (0, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("Live + grid", live_disp)

        # --- Colour mask + edge detection ---
        colour_img = None
        if BLOCK_ANALYSIS:
            roi_bgr = bgr[roi_y:roi_y + rh, roi_x:roi_x + rw]
            colour_img, _ = classify_roi_bgr(roi_bgr)
            cv2.imshow("Colour mask", colour_img)

            disp_grey, lines_grey, edges_colour, edges_original = build_edge_display(
                colour_img, roi_bgr,
            )
            cv2.imshow("Canny (colour mask)", edges_colour)
            cv2.imshow("Canny (original)",    edges_original)
            if not points_locked:
                grey_line_history.append(lines_grey)
                line_cap = max(1, int(GRID_POINTS_MAX_INPUT_LINES))
                history_lines_flat: list[tuple] = []
                for hist_lines in reversed(grey_line_history):
                    for line in hist_lines:
                        history_lines_flat.append(line)
                        if len(history_lines_flat) >= line_cap:
                            break
                    if len(history_lines_flat) >= line_cap:
                        break
                horiz_hist, vert_hist = classify_lines(history_lines_flat)
                history_disp = draw_classified_lines(np.zeros_like(disp_grey), horiz_hist, vert_hist)
                last_grid_points = find_hv_intersections_from_classified(
                    horiz_hist, vert_hist, history_disp.shape,
                )
                last_grid_points = filter_points_by_x_bands(last_grid_points, rw)
                if frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES)):
                    live_valid_points_crop = [
                        (int(ix + roi_x), int(iy + roi_y)) for ix, iy in last_grid_points
                    ]
                for ix, iy in last_grid_points:
                    cv2.circle(history_disp, (ix, iy), 3, (0, 0, 255), -1)
            else:
                history_disp = disp_grey.copy()
            cv2.imshow("Edges", history_disp)

        # --- Grid lock ---
        if (
            frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES))
            and BLOCK_ANALYSIS
            and not points_locked
            and last_grid_points
        ):
            locked_layer_cells = build_layer_cells_from_points(
                last_grid_points, (roi_x, roi_y, rw, rh),
            )
            if locked_layer_cells:
                points_locked = True
                if on_points_locked is not None:
                    on_points_locked()

        # --- Tower analysis ---
                # --- Tower analysis ---
        if TOWER_ANALYSIS:

            _hex_frame_n += 1

            if (
                _hex_frame_n >= HEX_RECOMPUTE_INTERVAL
                or _cached_pts is None
            ):
                _cached_pts = compute_hex_region(
                    bgr,
                    roi_xywh=(roi_x, roi_y, rw, rh),
                )
                _hex_frame_n = 0

            pts = _cached_pts
            pts_full = (
                None
                if pts is None
                else (pts + np.array([dx1, dy1], dtype=np.int32))
            )

            # -------------------------------------------------
            # Depth estimate
            # -------------------------------------------------

            tower_depth = estimate_tower_depth_stats(
                depth_mm,
                pts,
            )

            # -------------------------------------------------
            # Lateral offset estimate
            # -------------------------------------------------

            tower_offset = estimate_tower_offset(
                pts=pts_full,
                image_width_px=iw,
                depth_mm=(
                    None
                    if tower_depth is None
                    else tower_depth["depth_mm"]
                ),
                image_shape=(ih, iw),
            )

            # -------------------------------------------------
            # Extract centroid_x
            # -------------------------------------------------

            centroid_x = None

            if tower_offset is not None:
                centroid_x = tower_offset[
                    "centroid_x_px"
                ]

            # -------------------------------------------------
            # Build display
            # -------------------------------------------------

            sat_disp = (
                build_display(
                    bgr,
                    pts,
                    centroid_x=(
                        None
                        if centroid_x is None
                        else (centroid_x - dx1)
                    ),
                    roi_xywh=(roi_x, roi_y, rw, rh),
                )
                if pts is not None
                else None
            )

        else:
            pts = None
            sat_disp = None
            tower_depth = None
            tower_offset = None

        if TOWER_ANALYSIS and sat_disp is not None:
            if tower_depth is not None:
                cv2.putText(sat_disp, f"Tower depth ~ {tower_depth['tower_depth_m']:.3f} m",
                            (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            if tower_offset is not None:
                off_txt = f"Offset from center: {tower_offset['dx_px']:+.0f}px"
                cv2.putText(sat_disp, off_txt, (10, 52),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2, cv2.LINE_AA)
            tf_parts = []
            if tower_depth is not None:
                tf_parts.append(f"@d={tower_depth['depth_mm']:.1f}mm")
            if tower_offset is not None and tower_offset["lateral_mm"] is not None:
                tf_parts.append(f"@x={tower_offset['lateral_mm']:+.1f}mm")
            if tf_parts:
                cv2.putText(sat_disp, "  ".join(tf_parts), (10, 78),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 255), 2, cv2.LINE_AA)
                now = time.monotonic()
                if now - _last_tower_finder_print >= TOWER_PRINT_INTERVAL_S:
                    cx_str = (
                        f"  [px debug] centroid={tower_offset['centroid_x_px']:.0f}px"
                        f"  frame_centre={iw/2:.0f}px"
                    )
                    print("Tower finder:  " + "  ".join(tf_parts) + cx_str)
                    _last_tower_finder_print = now
            cv2.imshow(
                "Tower finder",
                crop_tower_finder_display(
                    sat_disp,
                    pts,
                    bgr.shape[1],
                    bgr.shape[0],
                ),
            )

        # --- Box percentages + layer analysis (active after grid lock) ---
        if BLOCK_ANALYSIS and points_locked:
            if frame_n % ANALYSIS_INTERVAL == 0:
                active_cells      = [cell for layer in locked_layer_cells for cell in layer]
                _last_pct_results = compute_percentages(bgr, cells=active_cells)
                if depth_mm is not None:
                    row_cells = [(layer[0], layer[1]) for layer in locked_layer_cells]
                    tower     = analyse_tower(bgr, depth_mm, row_cells)
                    if tower and publish_top_layer:
                        publish_top_layer(tower[0])
                    _last_tower_img = build_tower_image(tower)
            if _last_pct_results:
                active_cells = [cell for layer in locked_layer_cells for cell in layer]
                _ensure_window_open("Box percentages")
                cv2.imshow("Box percentages", build_debug_image(bgr, _last_pct_results, cells=active_cells))
            if _last_tower_img is not None:
                _ensure_window_open("Layer Analysis")
                cv2.imshow("Layer Analysis", _last_tower_img)

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


# ---------------------------------------------------------------------------
# ROS bridge node
# ---------------------------------------------------------------------------

class _ImageBridge(Node):
    def __init__(
        self,
        color_topic: str,
        depth_topic: str | list[str] | tuple[str, ...],
    ):
        super().__init__("play_image_bridge")
        self._bridge = CvBridge()
        self._lock   = threading.Lock()
        self._bgr    = None
        self._depth_mm = None
        self._depth_enc_warned: set[str] = set()
        self._active_depth_topic: str | None = None
        self._depth_subscriptions: list = []
        self.create_subscription(Image, color_topic, self._cb, 10)
        self.top_layer_pub = self.create_publisher(String, "/top_layer_state", 10)

        depth_topics = (
            [depth_topic] if isinstance(depth_topic, str) else list(depth_topic)
        )
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

    def publish_top_layer(self, layer_data) -> None:
        msg      = String()
        msg.data = json.dumps(layer_data)
        self.top_layer_pub.publish(msg)

    def _cb(self, msg: Image) -> None:
        enc = (msg.encoding or "").lower()
        bgr = (
            cv2.cvtColor(self._bridge.imgmsg_to_cv2(msg, "rgb8"), cv2.COLOR_RGB2BGR)
            if enc == "rgb8"
            else self._bridge.imgmsg_to_cv2(msg, "bgr8")
        )
        with self._lock:
            self._bgr = bgr

    def _depth_cb(self, msg: Image, topic: str) -> None:
        enc = (msg.encoding or "").lower()
        if "16uc1" in enc or "mono16" in enc:
            depth_mm = self._bridge.imgmsg_to_cv2(msg, "16UC1")
        elif "32fc1" in enc:
            m        = self._bridge.imgmsg_to_cv2(msg, "32FC1")
            depth_mm = np.clip(m * 1000.0, 0, 65_535).astype(np.uint16)
        else:
            if topic not in self._depth_enc_warned:
                self.get_logger().warning(
                    f"Ignoring depth from {topic}: encoding {msg.encoding!r} "
                    "(need 16UC1/mono16 or 32FC1)."
                )
                self._depth_enc_warned.add(topic)
            return

        with self._lock:
            bgr_shape = None if self._bgr is None else self._bgr.shape[:2]

            if bgr_shape is None:
                # No colour reference yet — defer; can't validate alignment.
                return

            if depth_mm.shape[:2] != bgr_shape:
                if topic not in self._depth_enc_warned:
                    self.get_logger().warning(
                        f"Ignoring depth from {topic}: shape {depth_mm.shape[:2]} "
                        f"does not match colour {bgr_shape} (not aligned to colour)."
                    )
                    self._depth_enc_warned.add(topic)
                return

            if self._active_depth_topic is None:
                self._active_depth_topic = topic
                self.get_logger().info(f"Depth source locked to: {topic}")
            elif topic != self._active_depth_topic:
                return
            self._depth_mm = depth_mm

    def get_frame_pair(self):
        with self._lock:
            bgr      = None if self._bgr      is None else self._bgr.copy()
            depth_mm = None if self._depth_mm is None else self._depth_mm.copy()
            return bgr, depth_mm


# ---------------------------------------------------------------------------
# Executor helpers
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def run_with_pipeline(pipeline) -> None:
    """Run the display loop reading frames from a RealSense pipeline object."""
    import pyrealsense2 as rs
    align = rs.align(rs.stream.color)

    def get_frame_pair():
        frames       = pipeline.wait_for_frames(timeout_ms=1000)
        aligned      = align.process(frames)
        color_frame  = aligned.get_color_frame()
        depth_frame  = aligned.get_depth_frame()
        if color_frame is None or not color_frame:
            return None, None

        frame        = np.asanyarray(color_frame.get_data())
        frame_format = str(color_frame.profile.format()).lower()
        bgr = (
            cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if "rgb8" in frame_format and "bgr8" not in frame_format
            else frame
        )

        if depth_frame is None or not depth_frame:
            depth_mm = None
        else:
            try:
                depth_mm = np.asanyarray(depth_frame.get_data())
            except RuntimeError:
                depth_mm = None

        return bgr, depth_mm

    _run_loop(get_frame_pair)


def run_subscribe(
    color_topic: str,
    depth_topic: str | list[str] | tuple[str, ...],
) -> None:
    """Run the display loop subscribed to ROS topics."""
    rclpy.init()
    bridge = _ImageBridge(color_topic, depth_topic)
    nodes: list = [bridge]
    executor = _start_executor(nodes)

    try:
        _run_loop(
            bridge.get_frame_pair,
            publish_top_layer=bridge.publish_top_layer,
        )
    finally:
        _shutdown_executor(executor, nodes)