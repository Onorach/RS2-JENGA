"""
jenga_perception_edges.py
--------------------------
Simple edge and line visualiser with persistence accumulation.

After `accumulate_frames` frames, opens an extra windows:
  - "Line frequency heatmap" — all lines coloured by how often they appeared

Windows always shown:
    "Jenga Perception"   — full image with live detected lines overlaid
    "Edges (Canny)"      — raw Canny edges within search region

Change the import in read_bag_direct.py to:
    from jenga_perception_edges import JengaPerceptionNode
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import time


# Minimal stubs so read_bag_direct.py works unchanged
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


class JengaPerceptionNode:
    def __init__(
        self,
        # Centre crop
        crop_cx: float = 0.5,
        crop_cy: float = 0.55,
        crop_w:  float = 0.45,
        crop_h:  float = 0.75,
        # Canny
        canny_low:  int = 80,
        canny_high: int = 240,
        # Hough
        hough_threshold: int = 80,
        min_line_length: int = 10,
        max_line_gap:    int = 40,
        # Angle filter
        max_horiz_angle_deg: float = 25.0,
        max_vert_angle_deg:  float = 3.0,
        # Persistence
        accumulate_frames: int = 50,    # how many frames to accumulate
        min_detections:    int = 20,    # min times a pixel must appear to be shown
        **kwargs,
    ):
        self.crop_cx = crop_cx
        self.crop_cy = crop_cy
        self.crop_w  = crop_w
        self.crop_h  = crop_h
        self.canny_low  = canny_low
        self.canny_high = canny_high
        self.hough_threshold     = hough_threshold
        self.min_line_length     = min_line_length
        self.max_line_gap        = max_line_gap
        self.max_horiz_angle_deg = max_horiz_angle_deg
        self.max_vert_angle_deg  = max_vert_angle_deg
        self.accumulate_frames   = accumulate_frames
        self.min_detections      = min_detections

        self._last_lines  = None
        self._last_crop   = (0, 0, 0, 0)
        self._accumulator = None   # int32 array, same size as image
        self._frame_count = 0
        self._last_frame  = None   # kept for persistence display

    # Stubs
    def set_reference(self, image, state): pass
    def clear_reference(self): pass
    has_reference = False

    # ------------------------------------------------------------------

    def _get_crop_region(self, image: np.ndarray) -> tuple:
        ih, iw = image.shape[:2]
        cw = int(iw * self.crop_w)
        ch = int(ih * self.crop_h)
        cx = int(iw * self.crop_cx) - cw // 2
        cy = int(ih * self.crop_cy) - ch // 2
        cx = max(0, min(cx, iw - cw))
        cy = max(0, min(cy, ih - ch))
        return (cx, cy, cw, ch)

    def _filter_lines(self, lines):
        """Split raw Hough lines into horizontal, vertical, and discard diagonals."""
        h_lines, v_lines = [], []
        if lines is None:
            return h_lines, v_lines
        for line in lines:
            x1, y1, x2, y2 = line[0]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            length = np.sqrt(dx**2 + dy**2)
            if length == 0:
                continue
            angle_deg = np.degrees(np.arctan2(dy, dx))
            if angle_deg <= self.max_horiz_angle_deg:
                h_lines.append((x1, y1, x2, y2))
            elif angle_deg >= (90.0 - self.max_vert_angle_deg):
                v_lines.append((x1, y1, x2, y2))
            # else: diagonal — discard silently
        return h_lines, v_lines

    # ------------------------------------------------------------------

    def process_frame(self, image: np.ndarray) -> TowerState:
        self._last_frame = image
        cx, cy, cw, ch = self._get_crop_region(image)
        crop = image[cy:cy+ch, cx:cx+cw]

        # Canny
        gray    = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges   = cv2.Canny(blurred, self.canny_low, self.canny_high)
        cv2.imshow("Edges (Canny)",
                   cv2.convertScaleAbs(cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), alpha=2.0))

        # Hough
        raw_lines = cv2.HoughLinesP(
            edges,
            rho=1, theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap,
        )

        h_lines, v_lines = self._filter_lines(raw_lines)
        self._last_lines = (h_lines, v_lines)
        self._last_crop  = (cx, cy, cw, ch)

        print(f"[Edges] Frame {self._frame_count + 1}/{self.accumulate_frames} "
              f"— {len(h_lines)} horizontal, {len(v_lines)} vertical lines")

        # --- Accumulate into pixel counter ---
        if self._accumulator is None:
            ih, iw = image.shape[:2]
            self._accumulator = np.zeros((ih, iw), dtype=np.int32)

        for (x1, y1, x2, y2) in h_lines + v_lines:
            cv2.line(self._accumulator,
                     (cx + x1, cy + y1),
                     (cx + x2, cy + y2), 1, 1)

        self._frame_count += 1

        if self._frame_count == self.accumulate_frames:
            self._show_persistence_image()

        return TowerState()

    # ------------------------------------------------------------------

    def _show_persistence_image(self) -> None:
        if self._accumulator is None or self._last_frame is None:
            return

        # Pixels seen >= min_detections times
        mask = (self._accumulator >= self.min_detections).astype(np.uint8) * 255

        # Frequency heatmap
        norm = cv2.normalize(
            self._accumulator.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)
        cv2.imshow("Line frequency heatmap", cv2.applyColorMap(norm, cv2.COLORMAP_HOT))

        pixel_count = int(np.sum(mask > 0))
        print(f"[Edges] Persistence image ready — {pixel_count} pixels seen >={self.min_detections} times")

    # ------------------------------------------------------------------

    def visualise(self, image: np.ndarray, state: TowerState) -> np.ndarray:
        vis = image.copy()
        cx, cy, cw, ch = self._last_crop

        # Search region in cyan
        cv2.rectangle(vis, (cx, cy), (cx+cw, cy+ch), (255, 255, 0), 1)
        cv2.putText(vis, "search region", (cx+2, cy+14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

        if self._last_lines is not None:
            h_lines, v_lines = self._last_lines
            for (x1, y1, x2, y2) in h_lines:
                cv2.line(vis, (cx+x1, cy+y1), (cx+x2, cy+y2), (0, 255, 0), 2)
            for (x1, y1, x2, y2) in v_lines:
                cv2.line(vis, (cx+x1, cy+y1), (cx+x2, cy+y2), (255, 100, 0), 1)

        # Progress bar toward persistence snapshot
        if self._frame_count < self.accumulate_frames:
            iw = image.shape[1]
            progress = int(iw * self._frame_count / self.accumulate_frames)
            cv2.rectangle(vis, (0, 0), (progress, 6), (0, 200, 255), -1)
            cv2.putText(vis,
                        f"Accumulating: {self._frame_count}/{self.accumulate_frames}",
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
        else:
            cv2.putText(vis, "Persistence image ready",
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.putText(vis, "GREEN=horizontal  BLUE=vertical",
                    (10, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        return vis