"""
Shared configuration for perception scripts.

Centralize values used by active runtime modules.
Sections are grouped by file/purpose.
"""


# HSV ranges per colour (changes classification sensitivity).
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "red": [
        ((0, 150, 140), (10, 255, 255)),
        ((170, 150, 140), (179, 255, 255)),
    ],
    "yellow": [
        ((18, 140, 140), (40, 255, 255)),
    ],
    "green": [
        ((40, 120, 100), (85, 255, 255)),
    ],
    "blue": [
        ((95, 220, 130), (110, 255, 255)),
    ],
    "purple": [
        ((110, 110, 50), (175, 255, 200)),
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

# Search ROI: (cx_frac, cy_frac, w_frac, h_frac).
ROI_FRACS = (0.495, 0.485, 0.32, 0.62)  # Bigger w/h = wider search; cx/cy shifts ROI.

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
# play_runtime.py
# ---------------------------------------------------------------------------

# Enable tower finder/depth feed and tower depth/offset metrics.
tower_analysis = False  # False disables all tower-analysis windows/metrics.

# Live view crop margin around ROI.
PLAY_RUNTIME_ROI_MARGIN = 0.10  # Higher = more context around ROI.

# Tower finder crop growth around hex bounds (fractional total growth).
TOWER_FINDER_GROW_RATIO = 0.30  # Higher = larger Tower finder crop.

# Number of frames accumulated in grey-edge history.
EDGE_HISTORY_FRAMES = 30  # Higher = longer line trails.

# Master toggle for all edge-detection processing/windows.
EDGE_DETECTION_ENABLED = False  # False disables grey/grey-history/grey-merged.

# Grey-line merge controls for "Edges (grey merged)".
EDGE_MERGE_PERP_DIST_PX = 5  # Max perpendicular separation to merge.
EDGE_MERGE_ALONG_GAP_PX = 40  # Max along-line gap to still merge.
EDGE_MERGE_MAX_ANGLE_DEG = 15.0  # Max orientation delta to treat as parallel.


# ---------------------------------------------------------------------------
# edge_analysis.py
# ---------------------------------------------------------------------------

# Grey Canny thresholds.
CANNY_GREY_LOW = 30   # Lower = more edges/noise.
CANNY_GREY_HIGH = 100  # Higher = fewer, stronger edges.

# Hough votes needed before accepting a line.
HOUGH_THRESHOLD = 10  # Higher = fewer false lines, may miss weak lines.

# Minimum accepted Hough line length (pixels).
HOUGH_MIN_LENGTH = 60  # Higher = keeps longer/stabler segments.

# Max gap (pixels) for connecting broken line segments.
HOUGH_MAX_GAP = 20  # Higher = merges more fragmented segments.

# Max angle from horizontal for "horizontal" classification.
MAX_HORIZ_DEG = 30.0  # Higher = accepts more slanted horizontals.

# Max angle away from vertical (90 deg) for "vertical" classification.
MAX_VERT_DEG = 5.0  # Higher = accepts more slanted verticals.


# ---------------------------------------------------------------------------
# tower_mask.py
# ---------------------------------------------------------------------------

# Min saturation for tower-mask foreground.
TOWER_MASK_SAT_MIN = 100  # Lower = includes duller colours.

# Min brightness/value for tower-mask foreground.
TOWER_MASK_VAL_MIN = 80  # Lower = includes darker/shadow pixels.

# Morphological close kernel size (pixels) on tower mask.
TOWER_MASK_MORPH_CLOSE_PX = 15  # Higher = fills larger mask gaps.

# Morphological open kernel size (pixels) on tower mask.
TOWER_MASK_MORPH_OPEN_PX = 10  # Higher = removes larger noise blobs.

# Minimum connected foreground area (pixels) to accept as tower blob.
TOWER_MASK_MIN_AREA_PX = 5000  # Higher = ignores smaller blobs.


# ---------------------------------------------------------------------------
# tower_analysis.py
# ---------------------------------------------------------------------------

# Camera horizontal FOV (deg) for px->metres lateral conversion.
CAMERA_HFOV_DEG = 69.0  # Higher = larger lateral metres for same px shift.

# Pixel padding around tower hex for depth-feed crop.
TOWER_ANALYSIS_DEPTH_PAD_PX = 30  # Higher = larger depth-feed crop.

