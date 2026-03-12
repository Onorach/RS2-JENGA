"""
Jenga block box detection
-------------------------

Uses the edge map from `detect_edges.py` to find rectangular candidates
whose side-length ratios roughly match Jenga block faces:

    - 1.5 : 2.5  (≈ 1.67)
    - 2.5 : 7.5  (≈ 3.0)

The rectangles don't need to be perfectly axis-aligned, perfectly parallel,
or meet exactly at the corners – we just require:
    - quadrilateral contour
    - opposite sides roughly parallel
    - adjacent side length ratios near one of the target ratios
"""

from __future__ import annotations

import math
from typing import Iterable, Tuple

import cv2
import numpy as np

from .detect_edges import INPUT_FOLDER, load_image, pipeline


RatioPair = Tuple[float, float]


TARGET_RATIOS: tuple[float, ...] = (2.5 / 1.5, 7.5 / 2.5)  # ≈ (1.67, 3.0)
RATIO_TOLERANCE = 0.30  # ±30%
PARALLEL_ANGLE_DEG = 15.0  # max angle difference between opposite sides
RIGHT_ANGLE_DEG = 30.0  # allow block perspective (not perfectly 90°)


def _edge_image_from_pipeline(steps: dict[str, np.ndarray]) -> np.ndarray:
    edges_bgr = steps["3. Canny Edges"]
    edges_gray = cv2.cvtColor(edges_bgr, cv2.COLOR_BGR2GRAY)
    return edges_gray


def _side_lengths_and_vectors(quad: np.ndarray) -> tuple[list[float], list[np.ndarray]]:
    # quad is (4, 1, 2) or (4, 2)
    pts = quad.reshape(-1, 2).astype(np.float32)
    lengths: list[float] = []
    vecs: list[np.ndarray] = []
    for i in range(4):
        p1 = pts[i]
        p2 = pts[(i + 1) % 4]
        v = p2 - p1
        vecs.append(v)
        lengths.append(float(np.linalg.norm(v)))
    return lengths, vecs


def _angle_deg(v: np.ndarray) -> float:
    return math.degrees(math.atan2(float(v[1]), float(v[0])))


def _angle_diff_deg(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


def _approx_rectangle_ok(lengths: Iterable[float], vecs: Iterable[np.ndarray]) -> bool:
    lengths = list(lengths)
    vecs = list(vecs)

    # Basic sanity checks
    if len(lengths) != 4 or len(vecs) != 4:
        return False

    # All sides must be non-trivial length
    if min(lengths) < 10.0:
        return False

    # Opposite sides should be roughly parallel
    ang = [_angle_deg(v) for v in vecs]
    if _angle_diff_deg(ang[0], ang[2]) > PARALLEL_ANGLE_DEG:
        return False
    if _angle_diff_deg(ang[1], ang[3]) > PARALLEL_ANGLE_DEG:
        return False

    # Adjacent sides should be roughly perpendicular-ish (but allow perspective)
    if 90.0 - RIGHT_ANGLE_DEG > _angle_diff_deg(ang[0], ang[1]) < 90.0 + RIGHT_ANGLE_DEG:
        pass  # ok

    # Group into two long and two short sides
    sorted_lengths = sorted(lengths, reverse=True)
    long_avg = 0.5 * (sorted_lengths[0] + sorted_lengths[1])
    short_avg = 0.5 * (sorted_lengths[2] + sorted_lengths[3])
    if short_avg <= 0:
        return False
    ratio = long_avg / short_avg

    for target in TARGET_RATIOS:
        if abs(ratio - target) / target <= RATIO_TOLERANCE:
            return True

    # Also accept the inverse ratio (in case we swapped long/short)
    inv_ratio = short_avg / long_avg
    for target in TARGET_RATIOS:
        if abs(inv_ratio - target) / target <= RATIO_TOLERANCE:
            return True

    return False


def detect_boxes_from_edges(
    bgr: np.ndarray,
    *,
    min_area_fraction: float = 0.001,
    max_area_fraction: float = 0.1,
) -> tuple[np.ndarray, list[np.ndarray]]:
    """
    Detect candidate Jenga blocks and draw them on a copy of `bgr`.
    Returns (output_image, list_of_quads).
    """
    steps = pipeline(bgr)
    edges = _edge_image_from_pipeline(steps)

    h, w = edges.shape[:2]
    img_area = float(h * w)

    # Find contours on the edge map.
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    quads: list[np.ndarray] = []
    output = steps["4. Edges on Image"].copy()

    for c in contours:
        area = float(cv2.contourArea(c))
        if area < img_area * min_area_fraction:
            continue
        if area > img_area * max_area_fraction:
            continue

        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        if len(approx) != 4:
            continue

        lengths, vecs = _side_lengths_and_vectors(approx)
        if not _approx_rectangle_ok(lengths, vecs):
            continue

        quads.append(approx)
        cv2.polylines(output, [approx], isClosed=True, color=(0, 255, 0), thickness=2)

    return output, quads


def main() -> None:
    import sys

    image_path = sys.argv[1] if len(sys.argv) >= 2 else None
    bgr = load_image(INPUT_FOLDER, image_path=image_path)
    output, quads = detect_boxes_from_edges(bgr)
    print(f"[INFO] Detected {len(quads)} candidate blocks.")

    cv2.namedWindow("Detected Jenga blocks", cv2.WINDOW_NORMAL)
    cv2.imshow("Detected Jenga blocks", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

