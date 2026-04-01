"""
jenga_perception_hsv_edges.py
-----------------------------
Pipeline:
  1) Crop to the same search region concept used elsewhere
  2) Build HSV masks (same style as `jenga_perception_colour.py`)
  3) Run edge detection *within each mask*
  4) Combine (OR) all per-mask edges into one edge image
  5) (Optional) run Hough on the combined edges for display

Designed to be swappable with other nodes:
  node = JengaPerceptionNode()
  state = node.process_frame(color_bgr)
  node.show(color_bgr, state)

Windows:
  - "Edges (HSV combined)"  : OR of per-colour edge maps (crop coords)
  - "Jenga Perception"      : main display with combined Hough lines overlaid
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np


# Minimal stubs so existing drivers can swap nodes without changes
@dataclass
class Block:
    layer: int = 0
    index: int = 0
    bbox: tuple = (0, 0, 0, 0)
    present: bool = True
    confidence: float = 1.0
    change_score: float = 0.0


@dataclass
class TowerState:
    blocks: list = field(default_factory=list)
    num_layers: int = 0
    tower_bbox: Optional[tuple] = None
    has_reference: bool = False
    missing_blocks: list = field(default_factory=list)


def _make_kernel(k: int, shape=cv2.MORPH_ELLIPSE) -> np.ndarray:
    k = int(k)
    k = max(1, k)
    if k % 2 == 0:
        k += 1
    return cv2.getStructuringElement(shape, (k, k))


class JengaPerceptionNode:
    def __init__(
        self,
        # Crop
        crop_cx: float = 0.5,
        crop_cy: float = 0.5,
        crop_w: float = 0.35,
        crop_h: float = 0.65,
        # HSV mask cleanup
        morph_open_ksize: int = 3,
        morph_close_ksize: int = 7,
        # Edge detection on masked regions
        edge_blur_ksize: int = 5,
        canny_low: int = 30,
        canny_high: int = 90,
        # Optional: Hough on combined edges (for overlay)
        use_hough: bool = True,
        hough_threshold: int = 80,
        min_line_length: int = 60,
        max_line_gap: int = 40,
        max_horiz_angle_deg: float = 25.0,
        max_vert_angle_deg: float = 4.0,
        # Display
        show_masks: bool = False,  # if True, show "Mask: <colour>" windows
        **kwargs,
    ):
        self.crop_cx = float(crop_cx)
        self.crop_cy = float(crop_cy)
        self.crop_w = float(crop_w)
        self.crop_h = float(crop_h)

        self.morph_open_ksize = int(morph_open_ksize)
        self.morph_close_ksize = int(morph_close_ksize)

        self.edge_blur_ksize = int(edge_blur_ksize)
        self.canny_low = int(canny_low)
        self.canny_high = int(canny_high)

        self.use_hough = bool(use_hough)
        self.hough_threshold = int(hough_threshold)
        self.min_line_length = int(min_line_length)
        self.max_line_gap = int(max_line_gap)
        self.max_horiz_angle_deg = float(max_horiz_angle_deg)
        self.max_vert_angle_deg = float(max_vert_angle_deg)

        self.show_masks = bool(show_masks)

        self._last_crop = (0, 0, 0, 0)
        self._last_lines = None
        self._last_edges_combined = None

        # HSV thresholds (copied from `jenga_perception_colour.py` starter values)
        self.hsv_ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
             "red": [
                ((0, 150, 140), (10, 255, 255)),
                ((170, 150, 140), (179, 255, 255)),
            ],
            # Yellow — slightly broader hue, lower S/V thresholds so more pixels are included
            "yellow": [
                ((18, 140, 140), (40, 255, 255)),
            ],
            "green": [
                ((40, 120, 100), (85, 255, 255)),
            ],
            # Blue — light blue, stop earlier so we don't eat into purple
            "blue": [
                ((90, 220, 130), (110, 255, 255)),
            ],
            # Purple / magenta — darker purples, allow low V but keep higher S
            "purple": [
                ((110, 110, 50), (175, 255, 200)),
            ],
        }

    # Stubs so read_bag_direct.py works unchanged
    def set_reference(self, image, state):  # noqa: ARG002
        pass

    def clear_reference(self):
        pass

    has_reference = False

    def _get_crop_region(self, image: np.ndarray) -> tuple[int, int, int, int]:
        ih, iw = image.shape[:2]
        cw = int(iw * self.crop_w)
        ch = int(ih * self.crop_h)
        cx = int(iw * self.crop_cx) - cw // 2
        cy = int(ih * self.crop_cy) - ch // 2
        cx = max(0, min(cx, iw - cw))
        cy = max(0, min(cy, ih - ch))
        return (cx, cy, cw, ch)

    def _mask_to_edges(self, crop_bgr: np.ndarray, mask: np.ndarray) -> np.ndarray:
        # Only keep pixels inside mask; background goes black.
        masked = cv2.bitwise_and(crop_bgr, crop_bgr, mask=mask)
        gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
        if self.edge_blur_ksize and self.edge_blur_ksize > 1:
            k = _make_kernel(self.edge_blur_ksize, shape=cv2.MORPH_ELLIPSE).shape[0]
            gray = cv2.GaussianBlur(gray, (k, k), 0)
        edges = cv2.Canny(gray, self.canny_low, self.canny_high)
        # Gate edges by mask (helps avoid edges on the black background)
        edges = cv2.bitwise_and(edges, edges, mask=mask)
        return edges

    def process_frame(self, image_bgr: np.ndarray) -> TowerState:
        cx, cy, cw, ch = self._get_crop_region(image_bgr)
        self._last_crop = (cx, cy, cw, ch)

        crop = image_bgr[cy : cy + ch, cx : cx + cw]
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        open_k = _make_kernel(self.morph_open_ksize)
        close_k = _make_kernel(self.morph_close_ksize)

        combined = np.zeros(hsv.shape[:2], dtype=np.uint8)

        for name, ranges in self.hsv_ranges.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for (lo, hi) in ranges:
                lo_np = np.array(lo, dtype=np.uint8)
                hi_np = np.array(hi, dtype=np.uint8)
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo_np, hi_np))

            if self.morph_open_ksize and self.morph_open_ksize > 1:
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_k)
            if self.morph_close_ksize and self.morph_close_ksize > 1:
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_k)

            if self.show_masks:
                cv2.imshow(f"Mask: {name}", mask)

            edges = self._mask_to_edges(crop, mask)
            combined = cv2.bitwise_or(combined, edges)

        self._last_edges_combined = combined

        # Display combined edges (crop coords)
        cv2.imshow("Edges (HSV combined)", cv2.convertScaleAbs(combined, alpha=2.0))

        # Hough on combined edges for overlay
        self._last_lines = None
        if self.use_hough:
            lines = cv2.HoughLinesP(
                combined,
                rho=1,
                theta=np.pi / 180,
                threshold=self.hough_threshold,
                minLineLength=self.min_line_length,
                maxLineGap=self.max_line_gap,
            )
            self._last_lines = lines

        return TowerState()

    def visualise(self, image_bgr: np.ndarray, state: TowerState) -> np.ndarray:  # noqa: ARG002
        vis = image_bgr.copy()
        cx, cy, cw, ch = self._last_crop

        # Search region
        cv2.rectangle(vis, (cx, cy), (cx + cw, cy + ch), (255, 255, 0), 1)
        cv2.putText(vis, "search region", (cx + 2, cy + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)

        if self._last_lines is not None:
            for line in self._last_lines:
                x1, y1, x2, y2 = line[0]
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                if dx == 0 and dy == 0:
                    continue
                angle_deg = float(np.degrees(np.arctan2(dy, dx)))
                is_horiz = angle_deg <= self.max_horiz_angle_deg
                is_vert = angle_deg >= (90.0 - self.max_vert_angle_deg)
                if not (is_horiz or is_vert):
                    continue

                fx1, fy1 = cx + x1, cy + y1
                fx2, fy2 = cx + x2, cy + y2
                if is_horiz:
                    cv2.line(vis, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
                else:
                    cv2.line(vis, (fx1, fy1), (fx2, fy2), (255, 100, 0), 1)

        cv2.putText(
            vis,
            "HSV masks -> edges -> OR  |  GREEN=horiz  BLUE=vert",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )
        return vis

    def show(self, image_bgr: np.ndarray, state: TowerState, margin: float = 0.10, window: str = "Jenga Perception") -> None:
        vis = self.visualise(image_bgr, state)

        try:
            cx, cy, cw, ch = self._last_crop
            ih, iw = vis.shape[:2]
            mx = int(cw * float(margin))
            my = int(ch * float(margin))
            x1 = max(0, cx - mx)
            y1 = max(0, cy - my)
            x2 = min(iw, cx + cw + mx)
            y2 = min(ih, cy + ch + my)
            vis = vis[y1:y2, x1:x2]
        except Exception:
            pass

        cv2.imshow(window, vis)

