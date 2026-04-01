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
        crop_w:  float = 0.35,      # crop width as fraction of image width
        crop_h:  float = 0.65,      # crop height as fraction of image height
        # Canny edge detection — lower values = more edges
        canny_low:  int = 30,
        canny_high: int = 90,
        # Hough line detection
        hough_threshold: int = 80,  # min votes — lower = more lines found
        min_line_length: int = 70,  # min pixel length to keep a line
        max_line_gap:    int = 40,  # max gap in pixels to bridge within a line
        # Angle filter
        max_horiz_angle_deg: float = 25.0,  # lines within this of horizontal → green
        max_vert_angle_deg:  float = 4.0,   # lines within this of vertical   → blue
        # Persistence display (in crop coordinates)
        persistence_frames: int = 50,
        persistence_min_hits: int = 5,
        persistence_source: str = "hough",  # "canny" | "hough" | "hsv"
        # HSV-mask persistence (only used when persistence_source="hsv")
        hsv_s_min: int = 40,
        hsv_v_min: int = 40,
        hsv_edge_close_px: int = 5,
        # Jenga "face" rectangle detection (ratio-only, scale unknown)
        box_ratio_tol: float = 0.22,          # relative tolerance on aspect ratio (e.g. 0.22 → ±22%)
        box_min_short_side_px: int = 10,      # reject tiny boxes
        box_min_area_px: int = 500,           # reject tiny contours
        box_edge_dilate_px: int = 3,          # connect broken edges
        box_edge_close_px: int = 7,           # close gaps in edges
        box_perimeter_thickness_px: int = 2,  # thickness when rasterizing candidate rectangle
        box_perimeter_dilate_px: int = 5,     # dilation for "edge support" scoring
        box_min_perimeter_support: float = 0.18,  # overlap(edges, perimeter)/perimeter
        box_min_side_supports: int = 2,       # require at least N sides supported by edges
        box_side_support_thresh: float = 0.12, # per-side support threshold
        box_window: str = "Jenga boxes",      # extra window for box detections
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
        self.persistence_source = str(persistence_source).strip().lower()
        self.hsv_s_min = int(hsv_s_min)
        self.hsv_v_min = int(hsv_v_min)
        self.hsv_edge_close_px = int(hsv_edge_close_px)

        self.box_ratio_tol = float(box_ratio_tol)
        self.box_min_short_side_px = int(box_min_short_side_px)
        self.box_min_area_px = int(box_min_area_px)
        self.box_edge_dilate_px = int(box_edge_dilate_px)
        self.box_edge_close_px = int(box_edge_close_px)
        self.box_perimeter_thickness_px = int(box_perimeter_thickness_px)
        self.box_perimeter_dilate_px = int(box_perimeter_dilate_px)
        self.box_min_perimeter_support = float(box_min_perimeter_support)
        self.box_min_side_supports = int(box_min_side_supports)
        self.box_side_support_thresh = float(box_side_support_thresh)
        self.box_window = str(box_window)

        # Persistent edge accumulator (crop-sized, uint16)
        self._edge_accum = None
        self._edge_frame_count = 0

        self._last_boxes = []
        self._last_edges = None
        self._last_crop_bgr = None
        self._last_hough_mask = None

    # Stubs so read_bag_direct.py works unchanged
    def set_reference(self, image, state): pass
    def clear_reference(self): pass
    has_reference = False

    def _build_hough_mask(self, edges_shape: tuple[int, int], lines) -> np.ndarray:
        """
        Rasterize (filtered) Hough segments into a binary mask (crop coords).
        Only horizontal/vertical-ish segments (same filter as visualisation) are kept.
        """
        h, w = edges_shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        if lines is None:
            return mask

        for line in lines:
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
            cv2.line(mask, (x1, y1), (x2, y2), 255, 2)

        return mask

    def _build_hsv_edge_mask(self, crop_bgr: np.ndarray) -> np.ndarray:
        """
        Basic HSV-mask boundary image:
        - Mask pixels with S,V above thresholds
        - Close small gaps
        - Return mask boundary (morph gradient)
        """
        hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]
        mask = ((s >= self.hsv_s_min) & (v >= self.hsv_v_min)).astype(np.uint8) * 255

        k = int(self.hsv_edge_close_px)
        if k > 0:
            k = k if (k % 2 == 1) else (k + 1)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        boundary = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        return boundary

    @staticmethod
    def _aspect_ratio_matches(ar: float, targets: list[float], rel_tol: float) -> bool:
        # Compare against targets using relative tolerance: |ar - t| / t <= rel_tol
        for t in targets:
            if t <= 0:
                continue
            if abs(ar - t) / t <= rel_tol:
                return True
        return False

    def _detect_jenga_face_boxes(self, edges: np.ndarray) -> list[tuple]:
        """
        Detect rotated rectangles consistent with Jenga block face ratios.

        Returns list of cv2.minAreaRect tuples in crop coordinates:
          ((cx, cy), (w, h), angle)
        """
        if edges is None or edges.size == 0:
            return []

        # Target aspect ratios for the three possible faces (scale unknown):
        # 75x25 → 3.0, 75x15 → 5.0, 25x15 → 1.666...
        targets = [3.0, 5.0, 25.0 / 15.0]

        edges0 = edges
        bw = edges

        # Connect partial edges so "2-3 sides" can still form a contour.
        if self.box_edge_dilate_px > 0:
            k = int(self.box_edge_dilate_px)
            k = k if (k % 2 == 1) else (k + 1)
            bw = cv2.dilate(bw, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)), iterations=1)
        if self.box_edge_close_px > 0:
            k = int(self.box_edge_close_px)
            k = k if (k % 2 == 1) else (k + 1)
            bw = cv2.morphologyEx(
                bw,
                cv2.MORPH_CLOSE,
                cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)),
                iterations=1,
            )

        contours, _hier = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.box_min_area_px:
                continue

            rect = cv2.minAreaRect(cnt)  # ((cx,cy),(w,h),angle)
            (_rcx, _rcy), (w, h), _ang = rect
            w = float(w)
            h = float(h)
            if w <= 1.0 or h <= 1.0:
                continue
            short = min(w, h)
            long = max(w, h)
            if short < self.box_min_short_side_px:
                continue

            ar = long / short
            if not self._aspect_ratio_matches(ar, targets, self.box_ratio_tol):
                continue

            # Score by how well the ORIGINAL edge map supports the rectangle perimeter.
            h0, w0 = edges0.shape[:2]
            perim_mask = np.zeros((h0, w0), dtype=np.uint8)
            pts = cv2.boxPoints(rect)
            pts = np.int32(pts)

            thickness = max(1, int(self.box_perimeter_thickness_px))
            cv2.polylines(perim_mask, [pts], isClosed=True, color=255, thickness=thickness)

            # Dilate the perimeter so slightly-misaligned edges still count.
            if self.box_perimeter_dilate_px > 0:
                kd = int(self.box_perimeter_dilate_px)
                kd = kd if (kd % 2 == 1) else (kd + 1)
                perim_mask = cv2.dilate(
                    perim_mask,
                    cv2.getStructuringElement(cv2.MORPH_RECT, (kd, kd)),
                    iterations=1,
                )

            perim_pixels = int(np.count_nonzero(perim_mask))
            if perim_pixels <= 0:
                continue

            overlap = cv2.bitwise_and(edges0, perim_mask)
            support = float(np.count_nonzero(overlap)) / float(perim_pixels)
            if support < self.box_min_perimeter_support:
                continue

            # Per-side support: accept "2–3 sides" faces, reject blobs/circles.
            side_supports = 0
            for i in range(4):
                side_mask = np.zeros((h0, w0), dtype=np.uint8)
                p1 = tuple(int(v) for v in pts[i])
                p2 = tuple(int(v) for v in pts[(i + 1) % 4])
                cv2.line(side_mask, p1, p2, 255, thickness=thickness)
                if self.box_perimeter_dilate_px > 0:
                    kd = int(self.box_perimeter_dilate_px)
                    kd = kd if (kd % 2 == 1) else (kd + 1)
                    side_mask = cv2.dilate(
                        side_mask,
                        cv2.getStructuringElement(cv2.MORPH_RECT, (kd, kd)),
                        iterations=1,
                    )
                denom = int(np.count_nonzero(side_mask))
                if denom <= 0:
                    continue
                side_overlap = cv2.bitwise_and(edges0, side_mask)
                side_score = float(np.count_nonzero(side_overlap)) / float(denom)
                if side_score >= self.box_side_support_thresh:
                    side_supports += 1

            if side_supports < self.box_min_side_supports:
                continue

            boxes.append((rect, support, side_supports))

        # Sort: strongest support first, then biggest area.
        boxes.sort(key=lambda x: (x[1], x[0][1][0] * x[0][1][1]), reverse=True)
        return [b[0] for b in boxes[:25]]

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
        self._last_crop_bgr = crop

        # ----------------------------
        # Canny edges (in crop)
        # ----------------------------
        gray    = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges   = cv2.Canny(blurred, self.canny_low, self.canny_high)
        self._last_edges = edges

        # ----------------------------
        # Display: Canny edges
        # ----------------------------
        edges_bright = cv2.convertScaleAbs(
            cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), alpha=2.0
        )
        cv2.imshow("Edges (Canny)", edges_bright)

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

        # ----------------------------
        # Persistence: edge-hit map over N frames
        #   - "canny": raw Canny edges
        #   - "hough": only pixels on/near Hough segments (default)
        #   - "hsv": boundary of a simple HSV mask (experimental)
        # ----------------------------
        if self.persistence_frames > 0 and self.persistence_min_hits > 0:
            if self.persistence_source == "canny":
                persist_src = edges
            elif self.persistence_source == "hsv":
                persist_src = self._build_hsv_edge_mask(crop)
            else:
                hough_mask = self._build_hough_mask(edges.shape, lines)
                self._last_hough_mask = hough_mask
                persist_src = hough_mask

            if self._edge_accum is None or self._edge_accum.shape != persist_src.shape:
                self._edge_accum = np.zeros(persist_src.shape, dtype=np.uint16)
                self._edge_frame_count = 0

            self._edge_accum += (persist_src > 0).astype(np.uint16)
            self._edge_frame_count += 1

            if self._edge_frame_count >= self.persistence_frames:
                mask = (self._edge_accum >= self.persistence_min_hits).astype(np.uint8) * 255
                cv2.imshow("Persistent edges", mask)
                self._edge_accum.fill(0)
                self._edge_frame_count = 0

        # ----------------------------
        # Detect Jenga face boxes (in crop)
        # ----------------------------
        self._last_boxes = self._detect_jenga_face_boxes(edges)

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

        # Draw detected Jenga face boxes (rotated rectangles)
        if getattr(self, "_last_boxes", None):
            for rect in self._last_boxes:
                box_pts = cv2.boxPoints(rect)  # 4x2 float
                box_pts = np.int32(box_pts)
                # Offset from crop to full image
                box_pts[:, 0] += cx
                box_pts[:, 1] += cy
                cv2.polylines(vis, [box_pts], isClosed=True, color=(255, 0, 255), thickness=2)

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

        # Extra window: crop with detected boxes overlaid (ratio-based face candidates)
        try:
            if self._last_crop_bgr is not None:
                box_vis = self._last_crop_bgr.copy()
                if getattr(self, "_last_boxes", None):
                    for rect in self._last_boxes:
                        box_pts = cv2.boxPoints(rect)
                        box_pts = np.int32(box_pts)
                        cv2.polylines(box_vis, [box_pts], isClosed=True, color=(255, 0, 255), thickness=2)
                cv2.imshow(self.box_window, box_vis)
        except Exception:
            pass