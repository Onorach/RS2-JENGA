"""
jenga_perception_colour.py
-------------------------
Colour-based block detector/visualiser.

Goal:
- Detect blocks by colour (red, green, purple, blue, yellow)
- Draw bounding boxes and put the colour name at each block's centre

Input:
- BGR images (OpenCV default)

This is designed to be swappable with `jenga_perception_edges.JengaPerceptionNode`:
    node = JengaPerceptionNode()
    state = node.process_frame(color_bgr)
    node.show(color_bgr, state)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np


# ------------------------------------------------------------------------------
# Minimal state stubs (kept consistent with other perception modules)
# ------------------------------------------------------------------------------
@dataclass
class Block:
    color: str
    bbox: tuple[int, int, int, int]  # x, y, w, h
    center: tuple[int, int]          # cx, cy
    confidence: float = 1.0


@dataclass
class TowerState:
    blocks: list[Block] = field(default_factory=list)
    num_layers: int = 0
    tower_bbox: Optional[tuple] = None
    has_reference: bool = False
    missing_blocks: list = field(default_factory=list)


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def _clamp_crop(x: int, y: int, w: int, h: int, iw: int, ih: int) -> tuple[int, int, int, int]:
    x = max(0, min(x, iw - 1))
    y = max(0, min(y, ih - 1))
    w = max(1, min(w, iw - x))
    h = max(1, min(h, ih - y))
    return x, y, w, h


def _centre_of_bbox(x: int, y: int, w: int, h: int) -> tuple[int, int]:
    return int(x + w / 2), int(y + h / 2)


def _make_kernel(k: int) -> np.ndarray:
    k = int(k)
    k = max(1, k)
    if k % 2 == 0:
        k += 1
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


# ------------------------------------------------------------------------------
# Main node
# ------------------------------------------------------------------------------
class JengaPerceptionNode:
    def __init__(
        self,
        # Search crop (fractions of image size)
        crop_cx: float = 0.5,
        crop_cy: float = 0.5,
        crop_w: float = 0.35,
        crop_h: float = 0.65,
        # Preprocessing
        blur_ksize: int = 5,
        # Morphology for masks
        morph_open_ksize: int = 3,
        morph_close_ksize: int = 7,
        # Filtering
        min_area_px: int = 1500,
        max_area_px: int = 200_000,
        # Aspect ratio filtering (w/h or h/w depending on orientation)
        min_aspect: float = 1.5,
        max_aspect: float = 10.0,
        # Display
        margin: float = 0.10,
        **kwargs,
    ):
        self.crop_cx = crop_cx
        self.crop_cy = crop_cy
        self.crop_w = crop_w
        self.crop_h = crop_h
        self.blur_ksize = blur_ksize
        self.morph_open_ksize = morph_open_ksize
        self.morph_close_ksize = morph_close_ksize
        self.min_area_px = int(min_area_px)
        self.max_area_px = int(max_area_px)
        self.min_aspect = float(min_aspect)
        self.max_aspect = float(max_aspect)
        self.margin = float(margin)

        self._last_crop = (0, 0, 0, 0)
        self._last_masks: dict[str, np.ndarray] = {}

        # HSV thresholds (OpenCV H: 0..179)
        # NOTE: these are starter values; use the "Mask: <colour>" windows to tune.
        self.hsv_ranges: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
            # red wraps around hue=0, so it's two ranges
            "red": [
                ((0, 80, 60), (10, 255, 255)),
                ((170, 80, 60), (179, 255, 255)),
            ],
            # Yellow — slightly broader hue, lower S/V thresholds so more pixels are included
            "yellow": [
                ((18, 60, 60), (40, 255, 255)),
            ],
            "green": [
                ((40, 60, 50), (85, 255, 255)),
            ],
            # Blue — light blue, stop earlier so we don't eat into purple
            "blue": [
                ((90, 40, 80), (120, 255, 255)),
            ],
            # Purple / magenta — darker purples, allow low V but keep higher S
            "purple": [
                ((110, 80, 10), (175, 255, 200)),
            ],
        }

        # Drawing colours (BGR)
        self.draw_colours = {
            "red": (0, 0, 255),
            "yellow": (0, 255, 255),
            "green": (0, 255, 0),
            "blue": (255, 0, 0),
            "purple": (255, 0, 255),
        }

    # --------------------------------------------------------------------------
    # Crop
    # --------------------------------------------------------------------------
    def _get_crop_region(self, image: np.ndarray) -> tuple[int, int, int, int]:
        ih, iw = image.shape[:2]
        cw = int(iw * self.crop_w)
        ch = int(ih * self.crop_h)
        cx = int(iw * self.crop_cx) - cw // 2
        cy = int(ih * self.crop_cy) - ch // 2
        cx = max(0, min(cx, iw - cw))
        cy = max(0, min(cy, ih - ch))
        return cx, cy, cw, ch

    # --------------------------------------------------------------------------
    # Core processing
    # --------------------------------------------------------------------------
    def process_frame(self, image_bgr: np.ndarray) -> TowerState:
        cx, cy, cw, ch = self._get_crop_region(image_bgr)
        self._last_crop = (cx, cy, cw, ch)

        crop = image_bgr[cy : cy + ch, cx : cx + cw]
        if self.blur_ksize and self.blur_ksize > 1:
            crop = cv2.GaussianBlur(crop, (_make_kernel(self.blur_ksize).shape[0],) * 2, 0)

        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        state = TowerState()
        self._last_masks = {}

        open_k = _make_kernel(self.morph_open_ksize)
        close_k = _make_kernel(self.morph_close_ksize)

        for name, ranges in self.hsv_ranges.items():
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for (lo, hi) in ranges:
                lo_np = np.array(lo, dtype=np.uint8)
                hi_np = np.array(hi, dtype=np.uint8)
                mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo_np, hi_np))

            # Clean up mask
            if self.morph_open_ksize and self.morph_open_ksize > 1:
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_k)
            if self.morph_close_ksize and self.morph_close_ksize > 1:
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_k)

            self._last_masks[name] = mask

            # Find contours (blocks)
            contours, _hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < self.min_area_px or area > self.max_area_px:
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                if w <= 0 or h <= 0:
                    continue

                aspect = max(w / float(h), h / float(w))
                if aspect < self.min_aspect or aspect > self.max_aspect:
                    continue

                bx, by = cx + x, cy + y
                bcx, bcy = _centre_of_bbox(bx, by, w, h)
                state.blocks.append(Block(color=name, bbox=(bx, by, w, h), center=(bcx, bcy)))

        return state

    # --------------------------------------------------------------------------
    # Visualisation
    # --------------------------------------------------------------------------
    def visualise(self, image_bgr: np.ndarray, state: TowerState) -> np.ndarray:
        vis = image_bgr.copy()
        cx, cy, cw, ch = self._last_crop

        # Search region
        cv2.rectangle(vis, (cx, cy), (cx + cw, cy + ch), (255, 255, 0), 1)
        cv2.putText(vis, "search region", (cx + 2, cy + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)

        # Draw blocks + labels
        for b in state.blocks:
            x, y, w, h = b.bbox
            col = self.draw_colours.get(b.color, (255, 255, 255))
            cv2.rectangle(vis, (x, y), (x + w, y + h), col, 2)

            tx, ty = b.center
            cv2.putText(
                vis,
                b.color,
                (tx - 30, ty + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return vis

    def show(self, image_bgr: np.ndarray, state: TowerState, window: str = "Jenga Perception") -> None:
        vis = self.visualise(image_bgr, state)

        # Crop displayed view to search region + margin
        cx, cy, cw, ch = self._last_crop
        ih, iw = vis.shape[:2]
        mx = int(cw * self.margin)
        my = int(ch * self.margin)
        x1, y1 = cx - mx, cy - my
        x2, y2 = cx + cw + mx, cy + ch + my
        x1, y1, ww, hh = _clamp_crop(x1, y1, x2 - x1, y2 - y1, iw, ih)
        vis = vis[y1 : y1 + hh, x1 : x1 + ww]

        cv2.imshow(window, vis)

        # Optional: show per-colour masks for debugging/tuning
        for name, mask in self._last_masks.items():
            cv2.imshow(f"Mask: {name}", mask)

