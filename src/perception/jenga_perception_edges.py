"""
jenga_perception_edges.py
--------------------------
Simple edge and line visualiser — no tower detection, no grid, no block classification.
Just shows what Canny and Hough are detecting within the search region.

Change the import in read_bag_direct.py to:
    from jenga_perception_edges import JengaPerceptionNode

Windows shown:
    "Jenga Perception"        — full image with detected lines overlaid
    "Edges (Canny)"           — raw Canny edges within search region

Keyboard:
    R — does nothing (no reference needed)
    Q — quit
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import time


# Minimal stubs so read_bag_direct.py doesn't need to change
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
        # Centre crop — adjust to frame the tower
        crop_cx: float = 0.5,       # horizontal centre as fraction of image width
        crop_cy: float = 0.5,      # vertical centre as fraction of image height
        crop_w:  float = 0.3,      # crop width as fraction of image width
        crop_h:  float = 0.6,      # crop height as fraction of image height
        # Canny edge detection — lower values = more edges
        canny_low:  int = 30,
        canny_high: int = 90,
        # Hough line detection
        hough_threshold: int = 80,  # min votes — lower = more lines found
        min_line_length: int = 40,  # min pixel length to keep a line
        max_line_gap:    int = 40,  # max gap in pixels to bridge within a line
        # Angle filter
        max_horiz_angle_deg: float = 25.0,  # lines within this of horizontal → green
        max_vert_angle_deg:  float = 4.0,   # lines within this of vertical   → blue
        # Persistence display (in crop coordinates)
        persistence_frames: int = 50,
        persistence_min_hits: int = 20,
        # anything else → not drawn
        **kwargs,   # absorb any unused params from read_bag_direct.py
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

        self.persistence_frames = int(persistence_frames)
        self.persistence_min_hits = int(persistence_min_hits)

        # Persistent edge accumulator (crop-sized, uint16)
        self._edge_accum = None
        self._edge_frame_count = 0

    # Stubs so read_bag_direct.py works unchanged
    def set_reference(self, image, state): pass
    def clear_reference(self): pass
    has_reference = False

    def _get_crop_region(self, image: np.ndarray) -> tuple:
        ih, iw = image.shape[:2]
        cw = int(iw * self.crop_w)
        ch = int(ih * self.crop_h)
        cx = int(iw * self.crop_cx) - cw // 2
        cy = int(ih * self.crop_cy) - ch // 2
        cx = max(0, min(cx, iw - cw))
        cy = max(0, min(cy, ih - ch))
        return (cx, cy, cw, ch)

    def process_frame(self, image: np.ndarray) -> TowerState:
        cx, cy, cw, ch = self._get_crop_region(image)
        crop = image[cy:cy+ch, cx:cx+cw]

        # ----------------------------
        # Canny edges (in crop)
        # ----------------------------
        gray    = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges   = cv2.Canny(blurred, self.canny_low, self.canny_high)

        # ----------------------------
        # Display: Canny edges
        # ----------------------------
        edges_bright = cv2.convertScaleAbs(
            cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), alpha=2.0
        )
        cv2.imshow("Edges (Canny)", edges_bright)

        # ----------------------------
        # Persistence: edge-hit map over N frames
        # ----------------------------
        if self.persistence_frames > 0 and self.persistence_min_hits > 0:
            if self._edge_accum is None or self._edge_accum.shape != edges.shape:
                self._edge_accum = np.zeros(edges.shape, dtype=np.uint16)
                self._edge_frame_count = 0

            self._edge_accum += (edges > 0).astype(np.uint16)
            self._edge_frame_count += 1

            if self._edge_frame_count >= self.persistence_frames:
                mask = (self._edge_accum >= self.persistence_min_hits).astype(np.uint8) * 255
                cv2.imshow("Persistent edges", mask)  # black bg, white where stable edges exist
                self._edge_accum.fill(0)
                self._edge_frame_count = 0

        # ----------------------------
        # Hough lines
        # ----------------------------
        lines = cv2.HoughLinesP(
            edges,
            rho=1, theta=np.pi / 180,
            threshold=self.hough_threshold,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap,
        )

        # Store for visualise()
        self._last_lines  = lines
        self._last_crop   = (cx, cy, cw, ch)

        if lines is not None:
            h_count = sum(
                1 for l in lines
                if np.degrees(np.arctan2(abs(l[0][3]-l[0][1]), abs(l[0][2]-l[0][0])))
                <= self.max_horiz_angle_deg
            )
            # print(f"[Edges] {len(lines)} lines detected, ~{h_count} horizontal")

        return TowerState()

    def visualise(self, image: np.ndarray, state: TowerState) -> np.ndarray:
        vis = image.copy()
        cx, cy, cw, ch = self._last_crop

        # Draw search region in cyan
        cv2.rectangle(vis, (cx, cy), (cx+cw, cy+ch), (255, 255, 0), 1)
        cv2.putText(vis, "search region", (cx+2, cy+14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

        # Draw filtered lines on full image
        if self._last_lines is not None:
            for line in self._last_lines:
                x1, y1, x2, y2 = line[0]
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                length = np.sqrt(dx**2 + dy**2)
                if length == 0:
                    continue

                angle_deg = np.degrees(np.arctan2(dy, dx))
                is_horiz = angle_deg <= self.max_horiz_angle_deg
                is_vert  = angle_deg >= (90.0 - self.max_vert_angle_deg)

                if not is_horiz and not is_vert:
                    continue

                # Offset line coords from crop-space to full image space
                fx1, fy1 = cx + x1, cy + y1
                fx2, fy2 = cx + x2, cy + y2

                if is_horiz:
                    cv2.line(vis, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)   # green
                else:
                    cv2.line(vis, (fx1, fy1), (fx2, fy2), (255, 100, 0), 1) # blue

        cv2.putText(vis, "GREEN = horizontal  |  BLUE = vertical",
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return vis

    def show(self, image: np.ndarray, state: TowerState, margin: float = 0.10, window: str = "Jenga Perception") -> None:
        """
        Convenience display helper:
        - calls visualise()
        - shows only the search area plus `margin` (fraction of crop size)
        """
        vis = self.visualise(image, state)

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