"""
edge_analysis.py
----------------
Edge detection and line finding on the colour mask produced by
colour_identification.classify_frame().

"""
from __future__ import annotations

import cv2
import numpy as np
from perception_config import (
    CANNY_GREY_LOW,
    CANNY_GREY_HIGH,
    HOUGH_THRESHOLD,
    HOUGH_MIN_LENGTH,
    HOUGH_MAX_GAP,
    MAX_HORIZ_DEG,
    MAX_VERT_DEG,
    EDGE_MERGE_ALONG_GAP_PX,
    EDGE_MERGE_MAX_ANGLE_DEG,
)


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def compute_edges(colour_img: np.ndarray) -> np.ndarray:
    """
    Compute edge image from the colour mask.

    Returns
    -------
    edges_grey : Canny on greyscale conversion of colour mask.
    """
    grey      = cv2.cvtColor(colour_img, cv2.COLOR_BGR2GRAY)
    edges_grey = cv2.Canny(grey, CANNY_GREY_LOW, CANNY_GREY_HIGH)

    return edges_grey


def find_lines(edges: np.ndarray) -> list[tuple]:
    """
    Run Hough line detection on an edge image.
    Returns list of (x1, y1, x2, y2) tuples.
    """
    lines = cv2.HoughLinesP(
        edges,
        rho=1, theta=np.pi / 180,
        threshold=HOUGH_THRESHOLD,
        minLineLength=HOUGH_MIN_LENGTH,
        maxLineGap=HOUGH_MAX_GAP,
    )
    if lines is None:
        return []
    return [tuple(l[0]) for l in lines]


def _classify_line(x1: int, y1: int, x2: int, y2: int) -> str | None:
    """Return 'horiz', 'vert', or None if the line doesn't match either."""
    angle = float(np.degrees(np.arctan2(abs(y2 - y1), abs(x2 - x1))))
    if angle <= MAX_HORIZ_DEG:
        return "horiz"
    if angle >= 90.0 - MAX_VERT_DEG:
        return "vert"
    return None


def draw_lines(base_img: np.ndarray, lines: list[tuple]) -> np.ndarray:
    """
    Draw filtered Hough lines on base_img.
    Horizontal → green, vertical → blue, others → skipped.
    """
    out = base_img.copy()
    for x1, y1, x2, y2 in lines:
        kind = _classify_line(x1, y1, x2, y2)
        if kind == "horiz":
            cv2.line(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        elif kind == "vert":
            cv2.line(out, (x1, y1), (x2, y2), (255, 100, 0), 1)
    return out


def _line_orientation_deg(x1: int, y1: int, x2: int, y2: int) -> float:
    """Return line orientation in [0, 180) degrees."""
    angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
    return (angle + 180.0) % 180.0


def _angle_diff_deg(a: float, b: float) -> float:
    """Smallest unsigned difference between orientations in [0, 90]."""
    d = abs(a - b)
    return min(d, 180.0 - d)


def merge_parallel_lines(
    lines: list[tuple],
    max_perp_dist_px: float,
    max_angle_diff_deg: float = EDGE_MERGE_MAX_ANGLE_DEG,
) -> list[tuple]:
    """Merge near-parallel duplicate lines into representative segments."""
    if not lines:
        return []

    def _interval_gap(a0: float, a1: float, b0: float, b1: float) -> float:
        if a1 < b0:
            return b0 - a1
        if b1 < a0:
            return a0 - b1
        return 0.0

    def _orientation_stats(theta_list: list[float]) -> tuple[float, np.ndarray, np.ndarray]:
        """Return merged orientation theta and unit direction/normal vectors."""
        c2 = float(np.mean([np.cos(2.0 * t) for t in theta_list]))
        s2 = float(np.mean([np.sin(2.0 * t) for t in theta_list]))
        theta = 0.5 * float(np.arctan2(s2, c2))
        d = np.array([np.cos(theta), np.sin(theta)], dtype=np.float32)
        n = np.array([-np.sin(theta), np.cos(theta)], dtype=np.float32)
        return theta % np.pi, d, n

    clusters: list[dict] = []
    for line in lines:
        x1, y1, x2, y2 = line
        theta = np.deg2rad(_line_orientation_deg(x1, y1, x2, y2))
        p1 = np.array([float(x1), float(y1)], dtype=np.float32)
        p2 = np.array([float(x2), float(y2)], dtype=np.float32)
        mid = 0.5 * (p1 + p2)

        placed = False
        for c in clusters:
            if _angle_diff_deg(np.rad2deg(theta), np.rad2deg(c["theta"])) > max_angle_diff_deg:
                continue

            perp_dist = abs(float(c["n"] @ mid) - c["rho"])
            if perp_dist > max_perp_dist_px:
                continue

            t1 = float(c["d"] @ p1)
            t2 = float(c["d"] @ p2)
            i0, i1 = (min(t1, t2), max(t1, t2))
            gap = _interval_gap(i0, i1, c["t_min"], c["t_max"])
            if gap > EDGE_MERGE_ALONG_GAP_PX:
                continue

            c["lines"].append(line)
            thetas = [np.deg2rad(_line_orientation_deg(*l)) for l in c["lines"]]
            c["theta"], c["d"], c["n"] = _orientation_stats(thetas)

            mids = []
            t_vals = []
            for lx1, ly1, lx2, ly2 in c["lines"]:
                lp1 = np.array([float(lx1), float(ly1)], dtype=np.float32)
                lp2 = np.array([float(lx2), float(ly2)], dtype=np.float32)
                mids.append(0.5 * (lp1 + lp2))
                t_vals.extend([float(c["d"] @ lp1), float(c["d"] @ lp2)])
            c["rho"] = float(np.mean([float(c["n"] @ m) for m in mids]))
            c["t_min"] = float(min(t_vals))
            c["t_max"] = float(max(t_vals))
            placed = True
            break

        if not placed:
            d = np.array([np.cos(theta), np.sin(theta)], dtype=np.float32)
            n = np.array([-np.sin(theta), np.cos(theta)], dtype=np.float32)
            t1 = float(d @ p1)
            t2 = float(d @ p2)
            clusters.append({
                "lines": [line],
                "theta": float(theta % np.pi),
                "d": d,
                "n": n,
                "rho": float(n @ mid),
                "t_min": float(min(t1, t2)),
                "t_max": float(max(t1, t2)),
            })

    merged: list[tuple] = []
    for c in clusters:
        if not c["lines"]:
            continue
        p0 = c["n"] * c["rho"]
        p1 = p0 + c["d"] * c["t_min"]
        p2 = p0 + c["d"] * c["t_max"]
        merged.append((
            int(round(float(p1[0]))),
            int(round(float(p1[1]))),
            int(round(float(p2[0]))),
            int(round(float(p2[1]))),
        ))
    return merged


def build_edge_display(colour_img: np.ndarray) -> tuple[np.ndarray, list[tuple]]:
    """
    Full pipeline: colour mask → grey edges → lines overlaid.

    Returns
    -------
    disp_grey : edges_grey with Hough lines drawn on top (BGR).
    lines_grey : raw Hough lines from grey edges.
    """
    edges_grey = compute_edges(colour_img)
    lines_grey = find_lines(edges_grey)
    disp_grey = draw_lines(cv2.cvtColor(edges_grey, cv2.COLOR_GRAY2BGR), lines_grey)
    return disp_grey, lines_grey
