"""
perception_config.py
--------------------
Central configuration for all perception modules.
Tune values here; nothing else needs to change.
"""

TOWER_ANALYSIS = True

BLOCK_ANALYSIS = True

# Search area centre and fraction of the full frame
SEARCH_AREA = (0.6, 0.44, 0.35, 0.45)

# Crop margin around the search area
SEARCH_AREA_MARGIN     = 0.10

# Camera horizontal field of view — used for px → mm lateral conversion.
CAMERA_HFOV_DEG = 69.0

# ---------------------------------------------------------------------------
# Colour Settings
# ---------------------------------------------------------------------------

# HSV ranges for colour identification
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "red": [
        ((0,   150, 140), (10,  255, 255)),
        ((170,  60, 140), (179, 255, 255)),
    ],
    "yellow": [
        ((18, 120, 140), (40, 255, 255)),
    ],
    "green": [
        ((40,  80, 100), (85, 255, 255)),
    ],
    "blue": [
        ((90, 160, 130), (104, 255, 255)),
    ],
    "purple": [
        ((105, 80, 50), (175, 255, 255)),
    ],
}

# BGR colours for visualisation
COLOUR_BGR: dict[str, tuple[int, int, int]] = {
    "red":    (0,   0,   220),
    "yellow": (0,   220, 220),
    "green":  (0,   200,   0),
    "blue":   (220,  80,   0),
    "purple": (180,   0, 180),
    "none":   (0,     0,   0),
}

# ---------------------------------------------------------------------------
# Tower mask
# ---------------------------------------------------------------------------

TOWER_MASK_SAT_MIN                 = 170   # Min HSV saturation for tower foreground.
TOWER_MASK_BRIGHTNESS_MIN          = 70    # Min HSV value (brightness) for tower foreground.
# TOWER_MASK_MORPH_CLOSE_PX        = 8     # Close kernel size — fills small mask holes.
# TOWER_MASK_MORPH_OPEN_PX         = 10    # Open kernel size — removes noise blobs.

# ---------------------------------------------------------------------------
# Edge detection
# ---------------------------------------------------------------------------

EDGE_HISTORY_FRAMES         = 30    # Frames kept in the line-history buffer.
POINTS_OVERLAY_PAUSE_FRAMES = 30    # Delay before overlaying detected points.

# Valid-point x-bands (percent of ROI width): outer-left, centre, outer-right.
POINT_VALID_SIDE_BAND_PCT   = 15.0
POINT_VALID_CENTER_BAND_PCT = 15.0


CANNY_GREY_LOW   = 30   # Lower = more edges.
CANNY_GREY_HIGH  = 80   # Higher = fewer, stronger edges only.
HOUGH_THRESHOLD  = 10   # Min Hough votes to accept a line.
HOUGH_MIN_LENGTH = 30   # Min accepted line length (pixels).
HOUGH_MAX_GAP    = 20   # Max gap for joining broken line segments.
MAX_HORIZ_DEG    = 30.0  # Max angle from horizontal to classify as horizontal.
MAX_VERT_DEG     = 5.0   # Max deviation from 90° to classify as vertical.


# ---------------------------------------------------------------------------
# Grid intersection pipeline
# ---------------------------------------------------------------------------

CLEAN_MASK_KERNEL_PX          = 7   # Morphological close on colour mask before Canny — fills fringe misclassification at block boundaries. 0 = disabled.
INTERSECTION_GAP_TOLERANCE_PX = 25  # How far outside a line segment an intersection may fall and still count.
CLUSTER_CELL_SIZE_PX          = 15  # Pass-1 grid-bucket cell size for deduplicating nearby intersection points.
CLUSTER_MERGE_RADIUS_PX       = 12  # Pass-2 merge radius for centroids that straddle bucket boundaries.