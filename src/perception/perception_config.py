"""
Shared configuration for perception scripts.

Centralize values used by active runtime modules.
"""

# Activation 

# Tower finder, depth feed, depth/offset metrics and related prints.
TOWER_ANALYSIS_ENABLED = True

# Grey edge windows (Edges grey / history) and processing.
EDGE_DETECTION_ENABLED = True

# ---------------------------------------------------------------------------
# Core shared settings (ROI, colour identification, overlays)
# ---------------------------------------------------------------------------

# Search Area: (cx_frac, cy_frac, w_frac, h_frac).
SEARCH_AREA = (0.6, 0.44, 0.35, 0.45) # Bigger w/h = wider search; cx/cy shifts ROI.

# HSV ranges per colour (changes classification sensitivity).
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "red": [
        ((0, 150, 140), (10, 255, 255)),
        ((170, 60, 140), (179, 255, 255)),
    ],
    "yellow": [
        ((18, 120, 140), (40, 255, 255)),
    ],
    "green": [
        ((40, 80, 100), (85, 255, 255)),
    ],
    "blue": [
        ((90, 160, 130), (104, 255, 255)),
    ],
    "purple": [
        ((105, 80,50), (175, 255, 255)),
    ],
}

# BGR display colours per class (visualization only).
COLOUR_BGR: dict[str, tuple[int, int, int]] = {
    "red": (0, 0, 220),
    "yellow": (0, 220, 220),
    "green": (0, 200, 0),
    "blue": (220, 80, 0),
    "purple": (180, 0, 180),
    "none": (0, 0, 0),
}



# Face-dividing line in full-frame coordinates.
DIVIDE_LINE = ((920, 217), (914, 850))  # Moves left/right position sign reference.

# Grid corners used by play overlays and cell sampling.
GRID_CORNERS: list[list[tuple[int, int] | None]] = [
    [(664, 197), (920, 217), (1237, 215)],
    [(669, 282), (916, 315), (1228, 297)],
    [(675, 359), (918, 410), (1224, 380)],
]

# Initial OpenCV window size (width, height) for play windows.
DEFAULT_WINDOW_SIZE = (960, 540)  # UI sizing only; no processing effect.



# ---------------------------------------------------------------------------
# Tower analysis + tower mask
# ---------------------------------------------------------------------------

# ---------------- Saturation Mask ----------------

# Min saturation for tower-mask foreground.
TOWER_MASK_SAT_MIN = 170  # Lower = includes duller colours.

# Min brightness/value for tower-mask foreground.
TOWER_MASK_VAL_MIN = 70  # Lower = includes darker/shadow pixels.

# Morphological close kernel size (pixels) on tower mask.
TOWER_MASK_MORPH_CLOSE_PX = 8  # Higher = fills larger mask gaps.

# Morphological open kernel size (pixels) on tower mask.
TOWER_MASK_MORPH_OPEN_PX = 10  # Higher = removes larger noise blobs.

# Minimum connected foreground area (pixels) to accept as tower blob.
TOWER_MASK_MIN_AREA_PX = 5000  # Higher = ignores smaller blobs.

# ---------------- Hex Finder ----------------

# Live view crop margin around ROI.
PLAY_RUNTIME_ROI_MARGIN = 0.10  # Higher = more context around ROI.

# Tower finder crop growth around hex bounds (fractional total growth).
TOWER_FINDER_GROW_RATIO = 0.30  # Higher = larger Tower finder crop.

# Camera horizontal FOV (deg) for px->metres lateral conversion.
CAMERA_HFOV_DEG = 69.0  # Higher = larger lateral metres for same px shift.

# Pixel padding around tower hex for depth-feed crop.
TOWER_ANALYSIS_DEPTH_PAD_PX = 30  # Higher = larger depth-feed crop.




# ---------------------------------------------------------------------------
# Edge detection
# ---------------------------------------------------------------------------

# Number of frames accumulated in grey-edge history.
EDGE_HISTORY_FRAMES = 30  # Higher = longer line trails.

# Pause every N frames and show points on original image.
POINTS_OVERLAY_PAUSE_FRAMES = 30

# Valid-point horizontal bands in ROI coordinates (percent of ROI width):
# valid = left outer band + center band + right outer band.
# With defaults below:
#   valid:   0-15%, 42.5-57.5%, 85-100%
#   invalid: 15-42.5%, 57.5-85%
POINT_VALID_SIDE_BAND_PCT = 15.0
POINT_VALID_CENTER_BAND_PCT = 15.0

# Max pixel distance when assigning detected points to template grid corners.
# Increase if lock often fails due to camera angle/pose variation.
POINT_LOCK_MAX_ASSIGN_DIST_PX = 120

# Grey Canny thresholds.
CANNY_GREY_LOW = 30   # Lower = more edges/noise.
CANNY_GREY_HIGH = 80  # Higher = fewer, stronger edges.

# Hough votes needed before accepting a line.
HOUGH_THRESHOLD = 10  # Higher = fewer false lines, may miss weak lines.

# Minimum accepted Hough line length (pixels).
HOUGH_MIN_LENGTH = 30  # Higher = keeps longer/stabler segments.

# Max gap (pixels) for connecting broken line segments.
HOUGH_MAX_GAP = 20  # Higher = merges more fragmented segments.

# Max angle from horizontal for "horizontal" classification.
MAX_HORIZ_DEG = 30.0  # Higher = accepts more slanted horizontals.

# Max angle away from vertical (90 deg) for "vertical" classification.
MAX_VERT_DEG = 5.0  # Higher = accepts more slanted verticals.

# Overlay intersection points on "Edges (grey history)".
GRID_POINTS_ENABLED = True

# Max history lines used when computing intersection points.
GRID_POINTS_MAX_INPUT_LINES = 700  # Hard cap to prevent heavy point computations.


# ---------------------------------------------------------------------------
# Grid intersection pipeline
# ---------------------------------------------------------------------------

# Morphological close kernel applied to the colour mask before Canny.
# Fills fringe misclassification pixels at block boundaries (e.g. thin
# purple halos between differently-coloured adjacent blocks).
# 0 = disabled.  Increase if colour mask still has noisy borders.
CLEAN_MASK_KERNEL_PX = 7

# Whether to merge near-parallel lines before computing intersections.
# True  → fewer lines → smaller intersection arrays, but requires correct merge.
# False → all history lines used directly; cluster step removes duplicates.
#         Recommended default — simpler and no merge-artefact risk.
LINE_MERGE_ENABLED = False

# Max pixel distance between parallel lines to be merged into one
# (only used when LINE_MERGE_ENABLED = True).
LINE_MERGE_BAND_PX = 10

# How far (pixels) an algebraic intersection may fall *outside* a line-segment
# endpoint and still count as a valid corner.
# Increase if corners at image edges are still missed.
INTERSECTION_GAP_TOLERANCE_PX = 25

# --- Clustering (two-pass deduplication) ---

# Pass 1: grid cell size (pixels).  Points in the same cell are averaged.
# Larger = coarser grouping, fewer output corners.
CLUSTER_CELL_SIZE_PX = 15

# Pass 2: after grid-bucket averaging, any two centroids whose Chebyshev
# distance (max of |dx|, |dy|) is within this radius are merged again.
# This fixes the bucket-boundary artefact where a real duplicate straddles
# two adjacent cells and survives Pass 1 as two separate points.
# Set to 0 to disable Pass 2.
CLUSTER_MERGE_RADIUS_PX = 12


# ---------------------------------------------------------------------------
# Box percentages
# ---------------------------------------------------------------------------

# Box-percentages window, layer stdout, and BoxPercentages ROS node.
BOX_PERCENTAGES_ENABLED = True