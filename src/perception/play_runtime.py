"""
play_runtime.py
---------------
Shared display loop and ROS wiring used by play_bag and play_live.
"""

import threading
import cv2
import numpy as np

from colour_identification import classify_frame, compute_roi, ColourIdentificationNode
from box_percentages import BoxPercentagesNode, compute_percentages, build_debug_image, analyse_layer, GRID_CELLS, LAYER_CELLS
from edge_analysis import build_edge_display
from saturation_mask import compute_hex_region, build_display
from perception_config import GRID_CORNERS, DIVIDE_LINE

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


def _run_loop(get_bgr) -> None:
    cv2.namedWindow("Live + grid", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Colour mask", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Box percentages", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Edges (grey)", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Edges (hue)",  cv2.WINDOW_NORMAL) 
    cv2.namedWindow("Saturation region", cv2.WINDOW_NORMAL)


    frame_n = 0
    roi_margin = 0.10

    while True:
        bgr = get_bgr()
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
        disp_grey, disp_hue = build_edge_display(colour_img)
        cv2.imshow("Edges (grey)", disp_grey)
        cv2.imshow("Edges (hue)",  disp_hue)

        pts = compute_hex_region(bgr)
        cv2.imshow("Saturation region", build_display(bgr, pts))    

        if frame_n % 30 == 0:
            pct_results = compute_percentages(bgr)
            cv2.imshow("Box percentages", build_debug_image(bgr, pct_results))

            # pct_results is ordered the same as GRID_CELLS: [l0, r0, l1, r1, ...]
            for i, (left_cell, right_cell) in enumerate(LAYER_CELLS):
                left_result  = pct_results[i * 2]
                right_result = pct_results[i * 2 + 1]
                layer = analyse_layer(bgr, left_result, right_result, left_cell, right_cell)
                print(f"layer {i}  orientation={layer['orientation']}  "
                    + "  ".join(f"{b['colour']}({b['position']:+.0f}px)" for b in layer["blocks"]))

        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break

class _ImageBridge(Node):
    def __init__(self, color_topic: str):
        super().__init__("play_image_bridge")
        self._bridge = CvBridge()
        self._lock = threading.Lock()
        self._bgr = None
        self.create_subscription(Image, color_topic, self._cb, 10)

    def _cb(self, msg: Image):
        enc = (msg.encoding or "").lower()
        bgr = (
            cv2.cvtColor(self._bridge.imgmsg_to_cv2(msg, "rgb8"), cv2.COLOR_RGB2BGR)
            if enc == "rgb8"
            else self._bridge.imgmsg_to_cv2(msg, "bgr8")
        )
        with self._lock:
            self._bgr = bgr

    def get_bgr(self):
        with self._lock:
            return None if self._bgr is None else self._bgr.copy()


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
    def get_bgr():
        frames = pipeline.wait_for_frames(timeout_ms=1000)
        color_frame = frames.get_color_frame()
        return None if color_frame is None else np.asanyarray(color_frame.get_data())

    _run_loop(get_bgr)


def run_subscribe(color_topic: str, depth_topic: str) -> None:
    rclpy.init()

    bridge = _ImageBridge(color_topic)
    colour_node = ColourIdentificationNode(color_topic)
    box_node = BoxPercentagesNode(color_topic)

    nodes = [bridge, colour_node, box_node]
    executor = _start_executor(nodes)

    try:
        _run_loop(bridge.get_bgr)
    finally:
        _shutdown_executor(executor, nodes)
