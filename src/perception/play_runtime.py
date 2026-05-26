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
from geometry_msgs.msg import Pose
from jenga_interfaces.msg import JengaBlockState, JengaBlockStates

from colour_identification import classify_roi_bgr, compute_roi
from box_percentages import compute_percentages, build_debug_image
from layer_analysis import (
    analyse_tower,
    annotate_depth_split_lines_for_tower,
    build_tower_image,
    block_id_from_tower_image_point,
    print_tower_state,
)
from grid_generation import (
    build_edge_display,
    classify_lines,
    draw_classified_lines,
    cluster_points,
    find_hv_intersections_from_classified,
    filter_points_by_x_bands,
    build_layer_cells_from_points,
)
from tower_mask import (
    HEX_RECOMPUTE_INTERVAL,
    append_tower_info_panel,
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
    BLOCK_POSE_WORLD_FRAME,
    GRID_LOCK_EDGE_ACCUMULATION_FRAMES,
)
from probe_response import (
    ProbeResponseMonitor,
    block_id_for_pick_slot,
    parse_selected_goal_pick,
    recompute_tower_centroids_strict,
)
from probe_response import (
    ProbeResponseMonitor,
    block_id_for_pick_slot,
    parse_selected_goal_pick,
)
from probe_response import (
    ProbeResponseMonitor,
    block_id_for_pick_slot,
    parse_selected_goal_pick,
)
from probe_response import (
    ProbeResponseMonitor,
    block_id_for_pick_slot,
    parse_selected_goal_pick,
)
from block_identity_tracker import BlockIdentityTracker

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


# ---------------------------------------------------------------------------
# Dynamic cell building from locked grid points
# ---------------------------------------------------------------------------

# Runtime-only history and timing controls for the live grid pipeline.
EDGE_HISTORY_FRAMES         = 30
GRID_POINTS_MAX_INPUT_LINES = 500

_GRID_DETECTION_WINDOWS = (
    "Colour mask",
    "Canny (colour mask)",
    "Canny (original)",
    "Edges",
)

_POST_LOCK_WINDOWS = (
    "Box percentages",
    "Layer Analysis",
)

# ---------------------------------------------------------------------------
# Main display loop
# ---------------------------------------------------------------------------

def _destroy_windows(names: tuple[str, ...]) -> None:
    for name in names:
        try:
            cv2.destroyWindow(name)
        except cv2.error:
            pass
    cv2.waitKey(1)


def _open_grid_detection_windows() -> None:
    for name in _GRID_DETECTION_WINDOWS:
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)


def _run_loop(
    get_frame_pair,
    on_points_locked=None,
    publish_top_layer=None,
    probe_monitor: ProbeResponseMonitor | None = None,
    probe_bridge: "_ImageBridge | None" = None,
) -> None:
    if BLOCK_ANALYSIS:
        cv2.namedWindow("Live + grid", cv2.WINDOW_NORMAL)
    if TOWER_ANALYSIS:
        cv2.namedWindow("Tower finder", cv2.WINDOW_NORMAL)

    grid_detection_started = False
    grid_frame_n           = 0
    frame_n          = 0
    roi_margin       = SEARCH_AREA_MARGIN
    grey_line_history: deque[list[tuple]] = deque(maxlen=EDGE_HISTORY_FRAMES)
    points_locked    = False
    locked_layer_cells: list[list[dict]] = []
    live_valid_points_crop: list[tuple[int, int]] = []
    accumulated_grid_points: list[tuple[int, int]] = []
    _last_pct_results: list[dict] = []
    _last_tower_img:   np.ndarray | None = None
    _last_tower_state: list[dict] = []
    _selected_probe_block_id: int | None = None
    identity_tracker = BlockIdentityTracker()
    _last_tower_finder_print: float = 0.0
    if probe_monitor is None:
        probe_monitor = ProbeResponseMonitor()
    _cached_pts:   np.ndarray | None = None
    _hex_frame_n:  int = 0

    TOWER_PRINT_INTERVAL_S = 8.0
    _last_layer_print_time_s: float = 0.0

    def _on_layer_analysis_mouse(event: int, x: int, y: int, _flags: int, _userdata) -> None:
        nonlocal _selected_probe_block_id
        if probe_monitor.is_robot_controlled():
            return
        if event != cv2.EVENT_LBUTTONUP:
            return
        if not _last_tower_state:
            return
        clicked_block_id = block_id_from_tower_image_point(_last_tower_state, int(x), int(y))
        if clicked_block_id is None:
            return
        if _selected_probe_block_id == clicked_block_id:
            print(f"[probe] deselected block {clicked_block_id}")
            _selected_probe_block_id = None
            probe_monitor.set_target_block_id(None)
            return
        _selected_probe_block_id = int(clicked_block_id)
        probe_monitor.set_target_block_id(_selected_probe_block_id)
        print(f"[probe] selected block {_selected_probe_block_id} for probing")

    def _reset_grid_pipeline() -> None:
        nonlocal grid_detection_started, grid_frame_n, points_locked
        nonlocal locked_layer_cells, accumulated_grid_points, live_valid_points_crop
        nonlocal _last_pct_results, _last_tower_img, _last_tower_state
        nonlocal _selected_probe_block_id

        grid_detection_started = True
        points_locked = False
        grid_frame_n = 0
        locked_layer_cells.clear()
        accumulated_grid_points.clear()
        grey_line_history.clear()
        live_valid_points_crop.clear()
        _last_pct_results.clear()
        _last_tower_img = None
        _last_tower_state.clear()
        _selected_probe_block_id = None
        probe_monitor.set_target_block_id(None)
        identity_tracker.reset()
        _destroy_windows(_GRID_DETECTION_WINDOWS + _POST_LOCK_WINDOWS)

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

        bgr = bgr_full[dy1:dy2, dx1:dx2]
        depth_mm = None if depth_mm_full is None else depth_mm_full[dy1:dy2, dx1:dx2]
        camera_centre_x_crop = (iw / 2.0) - dx1

        # --- Live view (block analysis only) ---
        if BLOCK_ANALYSIS:
            live_disp = bgr.copy()
            if grid_detection_started:
                cv2.rectangle(live_disp, (roi_x, roi_y), (roi_x + rw, roi_y + rh), (255, 255, 0), 2)
                # Overlay layer-analysis face centroids (when available) on live view.
                for layer in _last_tower_state:
                    for block in layer.get("blocks", []):
                        if not block.get("present"):
                            continue
                        mx = block.get("mean_x_px")
                        my = block.get("mean_y_px")
                        if mx is None or my is None:
                            continue
                        cx = int(round(float(mx)))
                        cy = int(round(float(my)))
                        if 0 <= cx < live_disp.shape[1] and 0 <= cy < live_disp.shape[0]:
                            cv2.circle(live_disp, (cx, cy), 5, (255, 255, 255), -1)
                            cv2.circle(live_disp, (cx, cy), 2, (0, 0, 0), -1)
                if grid_frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES)):
                    for px, py in live_valid_points_crop:
                        if 0 <= px < live_disp.shape[1] and 0 <= py < live_disp.shape[0]:
                            cv2.circle(live_disp, (int(px), int(py)), 2, (0, 0, 255), -1)
                cx = int(round(camera_centre_x_crop))
                if 0 <= cx < live_disp.shape[1]:
                    cv2.line(live_disp, (cx, 0), (cx, live_disp.shape[0] - 1), (0, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow("Live + grid", live_disp)

        # --- Colour mask + edge pipeline (after SPACE, until grid lock) ---
        if BLOCK_ANALYSIS and grid_detection_started and not points_locked:
            roi_bgr = bgr[roi_y:roi_y + rh, roi_x:roi_x + rw]
            colour_img, _ = classify_roi_bgr(roi_bgr)
            cv2.imshow("Colour mask", colour_img)
            grid_frame_n += 1
            disp_grey, lines_grey, edges_colour, edges_original = build_edge_display(
                colour_img, roi_bgr,
            )
            cv2.imshow("Canny (colour mask)", edges_colour)
            cv2.imshow("Canny (original)",    edges_original)

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
            accumulated_grid_points.extend(last_grid_points)

            # Use accumulated points from frame 0 up to lock time.
            points_for_lock = cluster_points(accumulated_grid_points)
            if grid_frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES)):
                live_valid_points_crop = [
                    (int(ix + roi_x), int(iy + roi_y)) for ix, iy in points_for_lock
                ]
            for ix, iy in points_for_lock:
                cv2.circle(history_disp, (ix, iy), 3, (0, 0, 255), -1)
            cv2.imshow("Edges", history_disp)

        # --- Grid lock ---
        if (
            grid_detection_started
            and grid_frame_n >= max(1, int(POINTS_OVERLAY_PAUSE_FRAMES))
            and BLOCK_ANALYSIS
            and not points_locked
            and accumulated_grid_points
        ):
            points_for_lock = cluster_points(accumulated_grid_points)
            locked_layer_cells = build_layer_cells_from_points(
                points_for_lock, (roi_x, roi_y, rw, rh),
            )
            if locked_layer_cells:
                points_locked = True
                _destroy_windows(_GRID_DETECTION_WINDOWS)
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

            sat_disp = build_display(
                bgr,
                pts,
                centroid_x=(
                    None
                    if centroid_x is None
                    else (centroid_x - dx1)
                ),
                roi_xywh=(roi_x, roi_y, rw, rh),
            )

        else:
            pts = None
            sat_disp = None
            tower_depth = None
            tower_offset = None

        if TOWER_ANALYSIS and sat_disp is not None:
            info_lines: list[str] = []
            info_colors: list[tuple[int, int, int]] = []
            if tower_depth is not None:
                info_lines.append(f"Tower depth ~ {tower_depth['tower_depth_m']:.3f} m")
                info_colors.append((255, 255, 255))
            if tower_offset is not None:
                info_lines.append(
                    f"Offset from center: {tower_offset['dx_px']:+.0f}px"
                )
                info_colors.append((255, 255, 255))
            tf_parts: list[str] = []
            if tower_depth is not None:
                tf_parts.append(f"@d={tower_depth['depth_mm']:.1f}mm")
            if tower_offset is not None and tower_offset["lateral_mm"] is not None:
                tf_parts.append(f"@x={tower_offset['lateral_mm']:+.1f}mm")
            if tf_parts:
                info_lines.append("  ".join(tf_parts))
                info_colors.append((0, 255, 255))
                now = time.monotonic()
                if now - _last_tower_finder_print >= TOWER_PRINT_INTERVAL_S:
                    print("Tower finder:  " + "  ".join(tf_parts))
                    _last_tower_finder_print = now
            if tower_offset is not None:
                info_lines.append(
                    f"centroid_x={tower_offset['centroid_x_px']:.0f}px"
                    f"   |   frame centre={iw/2:.0f}px"
                )
                info_colors.append((255, 0, 255))

            tower_view = crop_tower_finder_display(sat_disp, (roi_x, roi_y, rw, rh))
            tower_view = append_tower_info_panel(
                tower_view, info_lines, line_colors=info_colors,
            )
            cv2.imshow("Tower finder", tower_view)

        # --- Box percentages + layer analysis (active after grid lock) ---
        if BLOCK_ANALYSIS and points_locked:
            row_cells = [(layer[0], layer[1]) for layer in locked_layer_cells]
            probe_active = probe_monitor.is_active()
            placing_active = probe_monitor.is_robot_placing()
            if (
                _last_tower_img is None
                or probe_active
                or placing_active
            ):
                active_cells = [cell for layer in locked_layer_cells for cell in layer]
                _last_pct_results = compute_percentages(bgr, cells=active_cells)
                depth_for_layers = (
                    depth_mm
                    if depth_mm is not None
                    else np.zeros(bgr.shape[:2], dtype=np.uint16)
                )
                # When a probe is active, skip centroid/depth work for layers
                # below the target — they cannot move and recomputing them
                # wastes CPU every frame.
                probe_min_layer = probe_monitor.monitoring_min_layer()
                tower = analyse_tower(
                    bgr,
                    depth_for_layers,
                    row_cells,
                    frame_centre_x_px=camera_centre_x_crop,
                    frame_width_px=float(iw),
                    print_enabled=False,
                    min_centroid_layer=probe_min_layer,
                    identity_tracker=identity_tracker,
                )
                if placing_active and not probe_active:
                    tower = recompute_tower_centroids_strict(
                        bgr,
                        depth_for_layers,
                        row_cells,
                        tower,
                        min_layer=0,
                    )
                identity_tracker.apply(tower)
                _last_tower_state = tower
                if tower and publish_top_layer:
                    # Bottom-first (L0 at index 0) so GUI L1 = bottom, L6 = top.
                    tower_bottom_up = sorted(tower, key=lambda layer: layer["layer"])
                    publish_top_layer(tower_bottom_up)

            if probe_bridge is not None:
                probe_bridge.sync_probe_from_robot(_last_tower_state)
            if probe_active or _last_tower_state:
                _last_tower_state = probe_monitor.update(
                    _last_tower_state,
                    frame_shape=bgr.shape[:2],
                    bgr_frame=bgr,
                    depth_frame=depth_mm,
                    row_cells=row_cells,
                )
            if (
                not probe_active
                and _last_tower_state
                and (time.monotonic() - _last_layer_print_time_s) >= TOWER_PRINT_INTERVAL_S
            ):
                print_tower_state(_last_tower_state)
                _last_layer_print_time_s = time.monotonic()
            robot_target = probe_monitor.robot_target_block_id()
            if robot_target is not None:
                _selected_probe_block_id = int(robot_target)
            elif not probe_monitor.is_active():
                _selected_probe_block_id = None
            if _last_tower_state:
                _last_tower_img = build_tower_image(
                    _last_tower_state,
                    selected_block_id=_selected_probe_block_id,
                    probe_status_text=probe_monitor.status_text(),
                )

            if _last_pct_results:
                active_cells = [cell for layer in locked_layer_cells for cell in layer]
                _ensure_window_open("Box percentages")
                cv2.imshow(
                    "Box percentages",
                    build_debug_image(
                        bgr,
                        _last_pct_results,
                        cells=active_cells,
                        tower=_last_tower_state,
                        row_cells=row_cells,
                        frame_centre_x_px=camera_centre_x_crop,
                    ),
                )
            if _last_tower_img is not None:
                _ensure_window_open("Layer Analysis")
                cv2.setMouseCallback("Layer Analysis", _on_layer_analysis_mouse)
                cv2.imshow("Layer Analysis", _last_tower_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" ") and BLOCK_ANALYSIS:
            first_start = not grid_detection_started
            _reset_grid_pipeline()
            _open_grid_detection_windows()
            if first_start:
                print("[play] grid detection started (colour + edge windows open)")
            else:
                print("[play] grid recalculation started")
        elif key == ord("q"):
            break


# ---------------------------------------------------------------------------
# ROS bridge node
# ---------------------------------------------------------------------------

class _ImageBridge(Node):
    def __init__(
        self,
        color_topic: str,
        depth_topic: str,
        probe_monitor: ProbeResponseMonitor | None = None,
    ) -> None:
        super().__init__("play_image_bridge")
        self._bridge = CvBridge()
        self._lock   = threading.Lock()
        self._bgr    = None
        self._depth_mm = None
        self._depth_shape_warned = False
        self._depth_enc_warned = False
        self._probe_monitor = probe_monitor
        self._robot_state_label = "STANDBY"
        self._goal_pick: tuple[int, int] | None = None
        self._blocks_by_slot: dict[tuple[int, int], int] = {}
        self.create_subscription(Image, color_topic, self._cb, 10)
        self.create_subscription(Image, depth_topic, self._depth_cb, 10)
        self.create_subscription(String, "/robot_state", self._cb_robot_state, 10)
        self.create_subscription(String, "/selected_goal", self._cb_selected_goal, 10)
        self.create_subscription(
            JengaBlockStates, "/jenga/block_states", self._cb_block_states, 10,
        )
        self.top_layer_pub = self.create_publisher(String, "/top_layer_state", 10)
        self.block_states_pub = self.create_publisher(
            JengaBlockStates, "/jenga/block_states", 10
        )
        self.topple_status_pub = self.create_publisher(
            String, "/tower_topple_status", 10
        )
        self.get_logger().info(f"Colour topic: {color_topic}")
        self.get_logger().info(f"Depth topic:  {depth_topic}")
        self.get_logger().info(
            "Subscribed to /robot_state and /selected_goal for probe monitoring"
        )

    def publish_topple_status(
        self,
        block_id: int,
        status: str,
        reason: str | None = None,
    ) -> None:
        """Publish final topple monitoring decision."""
        msg = String()
        payload: dict[str, object] = {
            "block_id": int(block_id),
            "status": str(status),
        }
        msg.data = json.dumps(payload)
        self.topple_status_pub.publish(msg)

    def _resolve_goal_block_id(self, tower: list[dict] | None = None) -> int | None:
        if self._goal_pick is None:
            return None
        layer, position = self._goal_pick
        block_id = self._blocks_by_slot.get((layer, position))
        if block_id is not None:
            return int(block_id)
        if tower:
            return block_id_for_pick_slot(tower, layer, position)
        return None

    def sync_probe_from_robot(self, tower: list[dict] | None = None) -> None:
        if self._probe_monitor is None:
            return
        self._probe_monitor.sync_from_robot(
            self._robot_state_label,
            self._resolve_goal_block_id(tower),
        )

    def _cb_robot_state(self, msg: String) -> None:
        self._robot_state_label = (msg.data or "").strip().upper()
        self.sync_probe_from_robot()

    def _cb_selected_goal(self, msg: String) -> None:
        self._goal_pick = parse_selected_goal_pick(msg.data)
        self.sync_probe_from_robot()

    def _cb_block_states(self, msg: JengaBlockStates) -> None:
        self._blocks_by_slot = {
            (int(b.layer), int(b.layer_position)): int(b.block_id)
            for b in msg.blocks
        }
        self.sync_probe_from_robot()

    def publish_top_layer(self, tower_data) -> None:
        """Publish full tower state (list of layer dicts) on /top_layer_state."""
        msg      = String()
        msg.data = json.dumps(tower_data)
        self.top_layer_pub.publish(msg)
        self.block_states_pub.publish(self._build_block_states_msg(tower_data))
        self.sync_probe_from_robot(tower_data)

    def _build_block_states_msg(self, tower_data) -> JengaBlockStates:
        """Build typed block-state message from tower JSON-like layer dicts."""
        out = JengaBlockStates()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = BLOCK_POSE_WORLD_FRAME

        blocks: list[JengaBlockState] = []
        for layer in tower_data:
            layer_idx = int(layer.get("layer", -1))
            for pos_idx, block in enumerate(layer.get("blocks", [])):
                if not block.get("present"):
                    continue
                pose_global_mm = block.get("pose_global_mm")
                if not pose_global_mm:
                    continue
                pos = pose_global_mm.get("position", {})
                ori = pose_global_mm.get("orientation", {})

                b = JengaBlockState()
                b.block_id = int(block.get("block_index", -1))
                b.colour = str(block.get("colour", "unknown"))
                b.layer = max(layer_idx, 0)
                # Per-layer slot: front=0, mid=1, back=2.
                b.layer_position = max(0, min(2, int(pos_idx)))

                pose = Pose()
                # geometry_msgs/Pose uses SI units (metres).
                pose.position.x = float(pos.get("x", 0.0)) / 1000.0
                pose.position.y = float(pos.get("y", 0.0)) / 1000.0
                pose.position.z = float(pos.get("z", 0.0)) / 1000.0
                pose.orientation.x = float(ori.get("x", 0.0))
                pose.orientation.y = float(ori.get("y", 0.0))
                pose.orientation.z = float(ori.get("z", 0.0))
                pose.orientation.w = float(ori.get("w", 1.0))
                b.pose = pose
                blocks.append(b)

        blocks.sort(key=lambda item: item.block_id)
        out.blocks = blocks
        self._blocks_by_slot = {
            (int(b.layer), int(b.layer_position)): int(b.block_id)
            for b in blocks
        }
        return out

    def _cb(self, msg: Image) -> None:
        enc = (msg.encoding or "").lower()
        bgr = (
            cv2.cvtColor(self._bridge.imgmsg_to_cv2(msg, "rgb8"), cv2.COLOR_RGB2BGR)
            if enc == "rgb8"
            else self._bridge.imgmsg_to_cv2(msg, "bgr8")
        )
        with self._lock:
            self._bgr = bgr

    def _depth_cb(self, msg: Image) -> None:
        enc = (msg.encoding or "").lower()
        if "16uc1" in enc or "mono16" in enc:
            depth_mm = self._bridge.imgmsg_to_cv2(msg, "16UC1")
        elif "32fc1" in enc:
            m        = self._bridge.imgmsg_to_cv2(msg, "32FC1")
            depth_mm = np.clip(m * 1000.0, 0, 65_535).astype(np.uint16)
        else:
            if not self._depth_enc_warned:
                self.get_logger().warning(
                    f"Ignoring depth: encoding {msg.encoding!r} "
                    "(need 16UC1/mono16 or 32FC1)."
                )
                self._depth_enc_warned = True
            return

        with self._lock:
            bgr_shape = None if self._bgr is None else self._bgr.shape[:2]

            if bgr_shape is None:
                return

            if depth_mm.shape[:2] != bgr_shape:
                if not self._depth_shape_warned:
                    self.get_logger().warning(
                        f"Ignoring depth: shape {depth_mm.shape[:2]} "
                        f"does not match colour {bgr_shape} (not aligned to colour)."
                    )
                    self._depth_shape_warned = True
                return

            self._depth_mm = depth_mm

    def get_frame_pair(self):
        with self._lock:
            bgr      = None if self._bgr      is None else self._bgr.copy()
            depth_mm = None if self._depth_mm is None else self._depth_mm.copy()
            return bgr, depth_mm


class _TowerStatePublisher(Node):
    """ROS publisher node used when running from bag/pipeline mode."""

    def __init__(self) -> None:
        super().__init__("play_bag_state_publisher")
        self.top_layer_pub = self.create_publisher(String, "/top_layer_state", 10)
        self.block_states_pub = self.create_publisher(
            JengaBlockStates, "/jenga/block_states", 10
        )

    def publish_top_layer(self, tower_data) -> None:
        msg = String()
        msg.data = json.dumps(tower_data)
        self.top_layer_pub.publish(msg)
        self.block_states_pub.publish(self._build_block_states_msg(tower_data))

    def _build_block_states_msg(self, tower_data) -> JengaBlockStates:
        out = JengaBlockStates()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = BLOCK_POSE_WORLD_FRAME

        blocks: list[JengaBlockState] = []
        for layer in tower_data:
            layer_idx = int(layer.get("layer", -1))
            for pos_idx, block in enumerate(layer.get("blocks", [])):
                if not block.get("present"):
                    continue
                pose_global_mm = block.get("pose_global_mm")
                if not pose_global_mm:
                    continue
                pos = pose_global_mm.get("position", {})
                ori = pose_global_mm.get("orientation", {})

                b = JengaBlockState()
                b.block_id = int(block.get("block_index", -1))
                b.colour = str(block.get("colour", "unknown"))
                b.layer = max(layer_idx, 0)
                b.layer_position = max(0, min(2, int(pos_idx)))

                pose = Pose()
                pose.position.x = float(pos.get("x", 0.0)) / 1000.0
                pose.position.y = float(pos.get("y", 0.0)) / 1000.0
                pose.position.z = float(pos.get("z", 0.0)) / 1000.0
                pose.orientation.x = float(ori.get("x", 0.0))
                pose.orientation.y = float(ori.get("y", 0.0))
                pose.orientation.z = float(ori.get("z", 0.0))
                pose.orientation.w = float(ori.get("w", 1.0))
                b.pose = pose
                blocks.append(b)

        blocks.sort(key=lambda item: item.block_id)
        out.blocks = blocks
        return out


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
    try:
        if rclpy.ok():
            rclpy.shutdown()
    except Exception:
        # Ignore duplicate/late shutdown races during Ctrl+C teardown.
        pass


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def run_with_pipeline(pipeline, target_fps: float | None = None) -> None:
    """Run the display loop reading frames from a RealSense pipeline object."""
    import pyrealsense2 as rs
    align = rs.align(rs.stream.color)
    frame_interval_s = (1.0 / float(target_fps)) if target_fps and target_fps > 0 else None
    last_frame_time_s: float | None = None

    def get_frame_pair():
        nonlocal last_frame_time_s
        if frame_interval_s is not None and last_frame_time_s is not None:
            now = time.monotonic()
            sleep_s = frame_interval_s - (now - last_frame_time_s)
            if sleep_s > 0:
                time.sleep(sleep_s)
        frames       = pipeline.wait_for_frames(timeout_ms=1000)
        aligned      = align.process(frames)
        color_frame  = aligned.get_color_frame()
        depth_frame  = aligned.get_depth_frame()
        if color_frame is None or not color_frame:
            return None, None
        if frame_interval_s is not None:
            last_frame_time_s = time.monotonic()

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

    rclpy.init()
    state_pub = _TowerStatePublisher()
    nodes: list = [state_pub]
    executor = _start_executor(nodes)
    try:
        _run_loop(get_frame_pair, publish_top_layer=state_pub.publish_top_layer)
    finally:
        _shutdown_executor(executor, nodes)


def run_subscribe(color_topic: str, depth_topic: str) -> None:
    """Run the display loop subscribed to ROS topics."""
    rclpy.init()
    probe_monitor = ProbeResponseMonitor()
    bridge = _ImageBridge(color_topic, depth_topic, probe_monitor=probe_monitor)
    probe_monitor.set_on_final_decision(bridge.publish_topple_status)
    nodes: list = [bridge]
    executor = _start_executor(nodes)

    try:
        _run_loop(
            bridge.get_frame_pair,
            publish_top_layer=bridge.publish_top_layer,
            probe_monitor=probe_monitor,
            probe_bridge=bridge,
        )
    finally:
        _shutdown_executor(executor, nodes)