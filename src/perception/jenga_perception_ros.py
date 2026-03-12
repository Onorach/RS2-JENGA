import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class Block:
    """
    Represents a single Jenga block.

    layer:      0 = bottom of tower
    index:      0, 1, 2 (left to right within a layer)
    bbox:       (x, y, w, h) in image pixels
    present:    whether block appears to be in place
    change_score: how different this cell is from the reference frame
                  (higher = more changed, likely missing or moved)

    # LOCALIZATION HOOK - not yet integrated
    # world_position: Optional[tuple] = None
    # (x, y, z) in 3D space, to be filled by depth processing later
    # orientation: Optional[float] = None
    # rotation in layer plane (radians)
    """
    layer: int
    index: int
    bbox: tuple             # (x, y, w, h) in image pixels
    present: bool = True
    confidence: float = 1.0
    change_score: float = 0.0   # diff score vs reference frame (0 = identical)

    # --- LOCALIZATION STUB ---
    # Uncomment and populate when integrating depth/3D estimation
    # world_position: Optional[tuple] = None   # (x, y, z) metres in camera frame
    # orientation: Optional[float] = None      # rotation in layer plane (radians)


@dataclass
class TowerState:
    """
    Holds the full detected state of the Jenga tower at one point in time.
    """
    blocks: list[Block] = field(default_factory=list)
    num_layers: int = 0
    tower_bbox: Optional[tuple] = None      # (x, y, w, h) bounding box of whole tower
    has_reference: bool = False             # whether a reference frame has been set
    missing_blocks: list[Block] = field(default_factory=list)   # convenience list

    # --- LOCALIZATION STUB ---
    # tower_base_world: Optional[tuple] = None  # 3D position of tower base
    # tower_axis: Optional[np.ndarray] = None   # unit vector of tower vertical axis

    def get_block(self, layer: int, index: int) -> Optional[Block]:
        """Retrieve a specific block by layer and index."""
        for b in self.blocks:
            if b.layer == layer and b.index == index:
                return b
        return None


class JengaPerceptionNode:
    def __init__(
        self,
        presence_threshold: int = 50,       # min intensity to count as a block present (fallback only)
        diff_threshold: int = 30,           # max mean pixel diff to count as "same as reference"
        redetect_interval: int = 10,        # how often to re-detect tower bounds (frames)
        change_score_missing: float = 40.0, # change_score above this → block flagged missing
        crop_cx: float = 0.5,               # centre crop X fraction (0-1), default = image centre
        crop_cy: float = 0.5,               # centre crop Y fraction (0-1), default = image centre
        crop_w: float = 0.35,               # crop width as fraction of image width
        crop_h: float = 0.75,               # crop height as fraction of image height
    ):
        self.BLOCKS_PER_LAYER = 3
        self.presence_threshold = presence_threshold
        self.diff_threshold = diff_threshold
        self.redetect_interval = redetect_interval
        self.change_score_missing = change_score_missing

        # Centre crop parameters — tower is always centred so we search
        # only this region to avoid picking up background contours
        self.crop_cx = crop_cx
        self.crop_cy = crop_cy
        self.crop_w  = crop_w
        self.crop_h  = crop_h

        self.last_tower_bbox: Optional[tuple] = None
        self.frame_count: int = 0

        # Reference frame state
        self.reference_image: Optional[np.ndarray] = None
        self.reference_state: Optional[TowerState] = None
        self.reference_set_time: Optional[float] = None

    # ------------------------------------------------------------------
    # Reference frame management
    # ------------------------------------------------------------------

    def set_reference(self, image: np.ndarray, state: TowerState) -> None:
        """
        Call this once on a known-complete tower (all blocks present).
        All future frames will be diffed against this reference.

        Args:
            image: the BGR image used to produce `state`
            state: the TowerState produced from that image
        """
        self.reference_image = image.copy()
        self.reference_state = state
        self.reference_set_time = time.time()
        print(f"[JengaPerception] Reference frame set — "
              f"{state.num_layers} layers, {len(state.blocks)} blocks tracked.")

    def clear_reference(self) -> None:
        """Reset the reference frame (e.g. after tower is rebuilt)."""
        self.reference_image = None
        self.reference_state = None
        self.reference_set_time = None
        print("[JengaPerception] Reference frame cleared.")

    @property
    def has_reference(self) -> bool:
        return self.reference_image is not None

    # ------------------------------------------------------------------
    # Tower detection
    # ------------------------------------------------------------------

    def _get_crop_region(self, image: np.ndarray) -> tuple:
        """
        Returns (cx, cy, cw, ch) — the pixel coordinates of the centre
        crop region to search for the tower.
        Since the tower is always centred and at a fixed distance, we
        only search this region to avoid picking up background contours.
        """
        ih, iw = image.shape[:2]
        cw = int(iw * self.crop_w)
        ch = int(ih * self.crop_h)
        cx = int(iw * self.crop_cx) - cw // 2
        cy = int(ih * self.crop_cy) - ch // 2
        # Clamp to image bounds
        cx = max(0, min(cx, iw - cw))
        cy = max(0, min(cy, ih - ch))
        return (cx, cy, cw, ch)

    def detect_tower_bbox(self, image: np.ndarray) -> Optional[tuple]:
        """
        Finds the bounding box of the whole tower within the centre crop region.
        Returns (x, y, w, h) in full image coordinates, or None if not found.

        Constraining the search to the centre crop prevents the background,
        table, and walls from being picked up as the largest contour.

        # LOCALIZATION NOTE: this bbox is the entry point for
        # projecting image coords → 3D using the depth frame later.
        """
        ih, iw = image.shape[:2]
        cx, cy, cw, ch = self._get_crop_region(image)

        # Work only within the crop region
        crop = image[cy:cy+ch, cx:cx+cw]

        # Use wood colour (warm brown/orange) to isolate the tower
        # This is more robust than edge detection for this specific scene
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        # Hue range for warm wood brown — tune if lighting changes
        lower_wood = np.array([5,  40,  40])
        upper_wood = np.array([30, 255, 255])
        wood_mask = cv2.inRange(hsv, lower_wood, upper_wood)

        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        wood_mask = cv2.morphologyEx(wood_mask, cv2.MORPH_CLOSE, kernel)
        wood_mask = cv2.morphologyEx(wood_mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(
            wood_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            # Fallback to edge-based detection within crop
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if not contours:
                return None

        # Find the largest contour in the crop — should be the tower
        largest = max(contours, key=cv2.contourArea)
        rx, ry, rw, rh = cv2.boundingRect(largest)

        # Sanity check: tower should be taller than wide
        if rh < rw:
            return None

        # Convert crop-relative coords back to full image coords
        return (cx + rx, cy + ry, rw, rh)

    def estimate_num_layers(self, tower_bbox: tuple, image: np.ndarray) -> int:
        """
        Estimates how many layers the tower currently has.
        Uses horizontal edge density within the tower bbox.
        """
        x, y, w, h = tower_bbox
        roi = image[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        row_sums = np.sum(edges, axis=1)
        threshold = np.max(row_sums) * 0.3
        layer_rows = np.where(row_sums > threshold)[0]

        if len(layer_rows) < 2:
            return 8    # fallback default

        total_edge_span = layer_rows[-1] - layer_rows[0]
        approx_layer_height = total_edge_span / max(len(layer_rows) - 1, 1)
        num_layers = int(h / approx_layer_height) if approx_layer_height > 0 else 8
        return max(1, min(num_layers, 20))

    # ------------------------------------------------------------------
    # Block grid construction
    # ------------------------------------------------------------------

    def subdivide_into_blocks(self, tower_bbox: tuple, num_layers: int) -> list[Block]:
        """
        Given the tower bounding box, divide it into a grid of Block objects.
        Each block gets a bbox in image pixel coordinates.

        # LOCALIZATION NOTE: each block's bbox can later be used with the
        # depth image to get a 3D centroid via camera intrinsics:
        #   Z = depth_image[cy, cx]
        #   X = (cx - ppx) * Z / fx
        #   Y = (cy - ppy) * Z / fy
        """
        x, y, w, h = tower_bbox
        block_w = w // self.BLOCKS_PER_LAYER
        block_h = h // num_layers

        blocks = []
        for layer in range(num_layers):
            for idx in range(self.BLOCKS_PER_LAYER):
                bx = x + idx * block_w
                by = y + (num_layers - 1 - layer) * block_h   # layer 0 = bottom
                blocks.append(Block(
                    layer=layer,
                    index=idx,
                    bbox=(bx, by, block_w, block_h)
                ))
        return blocks

    # ------------------------------------------------------------------
    # Block classification
    # ------------------------------------------------------------------

    def _classify_block_fallback(self, image: np.ndarray, block: Block) -> Block:
        """
        Fallback presence check using raw intensity.
        Used only when no reference frame is available.
        Fragile — use set_reference() as soon as possible.
        """
        x, y, w, h = block.bbox
        roi = image[y:y+h, x:x+w]
        if roi.size == 0:
            block.present = False
            block.confidence = 0.0
            return block

        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        mean_intensity = np.mean(gray_roi)
        block.present = mean_intensity > self.presence_threshold
        block.confidence = float(mean_intensity) / 255.0
        block.change_score = 0.0    # no reference, no diff score
        return block

    def _classify_block_with_reference(
        self, image: np.ndarray, block: Block
    ) -> Block:
        """
        Presence check by diffing against the reference frame.
        A high change_score means the cell looks very different from when
        the tower was complete → block is likely missing or displaced.

        Three signals are combined:
          1. Pixel diff vs reference         — catches removal and shifts
          2. Edge density in current ROI     — low edges = empty space
          3. Colour similarity to reference  — catches colour anomalies
        """
        x, y, w, h = block.bbox

        current_roi = image[y:y+h, x:x+w]
        ref_roi = self.reference_image[y:y+h, x:x+w]

        if current_roi.size == 0 or ref_roi.size == 0:
            block.present = False
            block.confidence = 0.0
            block.change_score = 255.0
            return block

        # --- Signal 1: pixel-level diff ---
        diff = cv2.absdiff(current_roi, ref_roi)
        mean_diff = float(np.mean(diff))

        # --- Signal 2: edge density (low = empty cell) ---
        gray_current = cv2.cvtColor(current_roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_current, 50, 150)
        edge_density = float(np.sum(edges > 0)) / max(edges.size, 1)

        gray_ref = cv2.cvtColor(ref_roi, cv2.COLOR_BGR2GRAY)
        ref_edges = cv2.Canny(gray_ref, 50, 150)
        ref_edge_density = float(np.sum(ref_edges > 0)) / max(ref_edges.size, 1)

        edge_drop = max(0.0, ref_edge_density - edge_density)  # 0–1, higher = more edges lost

        # --- Signal 3: mean colour diff in HSV (lighting-robust) ---
        hsv_current = cv2.cvtColor(current_roi, cv2.COLOR_BGR2HSV)
        hsv_ref = cv2.cvtColor(ref_roi, cv2.COLOR_BGR2HSV)
        colour_diff = float(np.mean(cv2.absdiff(hsv_current, hsv_ref)))

        # --- Combine into a single change score ---
        # Weighted sum — tune weights based on your camera/lighting
        change_score = (
            0.5 * mean_diff +
            0.3 * (edge_drop * 255) +
            0.2 * colour_diff
        )
        block.change_score = change_score

        # Present if change score is below threshold
        block.present = change_score < self.change_score_missing
        block.confidence = max(0.0, 1.0 - (change_score / 255.0))

        return block

    def classify_block(self, image: np.ndarray, block: Block) -> Block:
        """
        Classifies a single block as present or missing.
        Uses reference frame diff if available, falls back to intensity check.
        """
        if self.has_reference:
            return self._classify_block_with_reference(image, block)
        else:
            return self._classify_block_fallback(image, block)

    # ------------------------------------------------------------------
    # Main process loop
    # ------------------------------------------------------------------

    def process_frame(self, image: np.ndarray) -> TowerState:
        """
        Main entry point. Call this on each new frame.
        Returns a TowerState with all detected blocks.

        Workflow:
          1. Re-detect tower bounding box every `redetect_interval` frames
          2. Estimate number of layers
          3. Subdivide into block grid
          4. Classify each block (diff vs reference if available)
          5. Populate missing_blocks list for convenience
        """
        state = TowerState(has_reference=self.has_reference)
        self.frame_count += 1

        # Re-detect tower bounds periodically
        if self.frame_count % self.redetect_interval == 0 or self.last_tower_bbox is None:
            detected = self.detect_tower_bbox(image)
            if detected is not None:
                self.last_tower_bbox = detected

        if self.last_tower_bbox is None:
            return state    # tower not found yet

        state.tower_bbox = self.last_tower_bbox
        state.num_layers = self.estimate_num_layers(self.last_tower_bbox, image)

        # Build grid and classify every block
        blocks = self.subdivide_into_blocks(self.last_tower_bbox, state.num_layers)
        state.blocks = [self.classify_block(image, b) for b in blocks]

        # Convenience: collect missing blocks
        state.missing_blocks = [b for b in state.blocks if not b.present]

        return state

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def visualise(self, image: np.ndarray, state: TowerState) -> np.ndarray:
        """
        Draws detected blocks onto a copy of the image for debugging.

        Green  = present (confirmed vs reference)
        Red    = missing or significantly changed
        Yellow = present but no reference (fallback mode)
        White  = tower bounding box
        Cyan   = centre crop search region
        Grid lines are drawn across the full tower for easy visual checking.
        """
        vis = image.copy()

        # Draw the centre crop search region in cyan (dashed feel via thin line)
        cx, cy, cw, ch = self._get_crop_region(image)
        cv2.rectangle(vis, (cx, cy), (cx+cw, cy+ch), (255, 255, 0), 1)
        cv2.putText(vis, "search region", (cx+2, cy+12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 0), 1)

        # Draw tower bounding box in white
        if state.tower_bbox:
            tx, ty, tw, th = state.tower_bbox

            cv2.rectangle(vis, (tx, ty), (tx+tw, ty+th), (255, 255, 255), 2)

            # Draw the full block grid as lines across the whole tower
            # Horizontal lines (layer boundaries)
            if state.num_layers > 0:
                block_h = th // state.num_layers
                for layer_i in range(state.num_layers + 1):
                    ly = ty + layer_i * block_h
                    cv2.line(vis, (tx, ly), (tx + tw, ly), (200, 200, 200), 1)

            # Vertical lines (block boundaries within each layer)
            block_w = tw // self.BLOCKS_PER_LAYER
            for col_i in range(self.BLOCKS_PER_LAYER + 1):
                lx = tx + col_i * block_w
                cv2.line(vis, (lx, ty), (lx, ty + th), (200, 200, 200), 1)

        # Draw each block cell with colour fill and label
        for block in state.blocks:
            x, y, w, h = block.bbox

            if not block.present:
                color     = (0, 0, 255)       # red = missing
                fill      = (0, 0, 80)        # dark red fill
            elif state.has_reference:
                color     = (0, 255, 0)       # green = confirmed present
                fill      = None              # no fill when present with reference
            else:
                color     = (0, 255, 255)     # yellow = fallback mode
                fill      = None

            # Semi-transparent fill for missing blocks
            if fill is not None:
                overlay = vis.copy()
                cv2.rectangle(overlay, (x, y), (x+w, y+h), fill, -1)
                cv2.addWeighted(overlay, 0.4, vis, 0.6, 0, vis)

            # Block outline
            cv2.rectangle(vis, (x, y), (x+w, y+h), color, 2)

            # Layer:index label in top-left of cell
            label = f"L{block.layer}:{block.index}"
            cv2.putText(vis, label, (x+3, y+13),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

            # Change score in bottom-left of cell (only when reference is set)
            if state.has_reference:
                score_label = f"{block.change_score:.0f}"
                cv2.putText(vis, score_label, (x+3, y+h-4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.28, color, 1)

        # --- HUD ---
        hud_y = 20
        ref_text = (
            f"REF SET ({time.strftime('%H:%M:%S', time.localtime(self.reference_set_time))})"
            if self.has_reference else "NO REFERENCE — press R to set"
        )
        cv2.putText(vis, ref_text, (10, hud_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        missing_text = f"Missing: {len(state.missing_blocks)}"
        cv2.putText(vis, missing_text, (10, hud_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 255), 1)

        layers_text = f"Layers: {state.num_layers}"
        cv2.putText(vis, layers_text, (10, hud_y + 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # List missing block IDs on screen
        for i, b in enumerate(state.missing_blocks):
            mv_text = f"  MISSING L{b.layer}:{b.index}"
            cv2.putText(vis, mv_text, (10, hud_y + 70 + i * 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        return vis


# ----------------------------------------------------------------------
# Quick test: run on a single image file
# Usage: python jenga_perception.py <image_path>
# Press R to set the current frame as reference
# Press Q to quit
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    node = JengaPerceptionNode()

    if image_path:
        # Static image mode — useful for tuning
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image: {image_path}")
            sys.exit(1)

        state = node.process_frame(image)
        print(f"Tower detected: {state.tower_bbox}")
        print(f"Layers estimated: {state.num_layers}")
        print(f"Blocks found: {len(state.blocks)}")

        # Set this first frame as reference then reprocess to demo diff
        node.set_reference(image, state)
        state = node.process_frame(image)

        vis = node.visualise(image, state)
        cv2.imshow("Jenga Perception", vis)

        print("Press R to reset reference, Q to quit.")
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                node.set_reference(image, state)
                state = node.process_frame(image)
                vis = node.visualise(image, state)
                cv2.imshow("Jenga Perception", vis)

    else:
        # Live webcam mode
        cap = cv2.VideoCapture(0)
        print("Press R to set reference frame, Q to quit.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            state = node.process_frame(frame)
            vis = node.visualise(frame, state)
            cv2.imshow("Jenga Perception", vis)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                node.set_reference(frame, state)

        cap.release()

    cv2.destroyAllWindows()