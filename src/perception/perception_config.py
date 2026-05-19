"""
perception_config.py
--------------------
Central configuration for all perception modules.
Tune values here; nothing else needs to change.
"""

TOWER_ANALYSIS = False

BLOCK_ANALYSIS = True

# Search area centre and fraction of the full frame
SEARCH_AREA = (0.492, 0.553, 0.259, 0.388)

# Crop margin around the search area
SEARCH_AREA_MARGIN     = 0.10

# Camera horizontal field of view — used for px → mm lateral conversion.
CAMERA_HFOV_DEG = 69.0

# Master toggle for the artificial saturation/contrast boost for both live
# (ROS) and bag/pipeline frames. The boost requires a BGR <-> HSV round-trip
# per frame, so disable it if frame rate is suffering.
BOOST_ENABLED = True

# Apply boost only on the search-area crop (+ SEARCH_AREA_MARGIN) instead of
# the full frame. This reduces per-frame boost cost.
BOOST_SEARCH_CROP_ONLY = True

# Multiplier applied to the HSV S-channel of every incoming frame before any
# perception runs. 1.0 = unchanged, >1.0 boosts saturation, <1.0 desaturates.
SATURATION_BOOST = 1.9

# Contrast multiplier applied to the HSV V-channel of every incoming frame
# around mid-grey (128). 1.0 = unchanged, >1.0 stretches contrast, <1.0
# flattens it.
CONTRAST_BOOST = 1.2

# ---------------------------------------------------------------------------
# Colour Settings
# ---------------------------------------------------------------------------

# HSV ranges for colour identification
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "red": [
        ((  0, 150, 118), ( 10, 255, 255)),
        ((170, 150, 118), (179, 255, 255)),
    ],
    "yellow": [
        (( 18, 120, 140), ( 39, 255, 255)),
    ],
    "green": [
        (( 39,  51,  79), ( 85, 255, 255)),
    ],
    "blue": [
        (( 90, 171, 105), (110, 255, 255)),
    ],
    "purple": [
        ((109,  56,  37), (140, 255, 255)),
    ],
}

# Minimum connected-component area (in ROI pixels) kept per colour mask.
# Higher values reject more tiny blobs/noise before the mask is used elsewhere.
# Set to 0 to disable size filtering.
COLOUR_MIN_BLOB_AREA_PX = 200

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

TOWER_MASK_SAT_MIN                 = 140   # Min HSV saturation for tower foreground.
TOWER_MASK_BRIGHTNESS_MIN          = 60    # Min HSV value (brightness) for tower foreground.
# TOWER_MASK_MORPH_CLOSE_PX        = 8     # Close kernel size — fills small mask holes.
# TOWER_MASK_MORPH_OPEN_PX         = 10    # Open kernel size — removes noise blobs.

# ---------------------------------------------------------------------------
# Edge detection
# ---------------------------------------------------------------------------

# Valid-point x-bands (percent of ROI width): outer-left, centre, outer-right.
POINT_VALID_SIDE_BAND_PCT   = 10.0
POINT_VALID_CENTER_BAND_PCT = 15.0

# Canny thresholds used on the colour-mask image.
CANNY_MASK_LOW   = 5   # Lower = more edges.
CANNY_MASK_HIGH  = 15  # Higher = fewer, stronger edges only.

# Canny thresholds used on the original BGR image.
CANNY_ORIGINAL_LOW  = 40
CANNY_ORIGINAL_HIGH = 120

# Width of the horizontal band (centred on the ROI) where Canny edges are
# kept, as a percentage of ROI width. Edges outside this strip are zeroed
# before Hough line detection, so both visualisation and grid-point search
# are restricted to the middle slice. Set to 100.0 to disable.
CANNY_CENTRE_BAND_PCT = 8.0

# Hough settings used for lines extracted from colour-mask edges.
HOUGH_MASK_THRESHOLD  = 10  # Min Hough votes to accept a line.
HOUGH_MASK_MIN_LENGTH = 30  # Min accepted line length (pixels).
HOUGH_MASK_MAX_GAP    = 20  # Max gap for joining broken line segments.

# Hough settings used for lines extracted from original-image edges.
HOUGH_ORIGINAL_THRESHOLD  = 20
HOUGH_ORIGINAL_MIN_LENGTH = 40
HOUGH_ORIGINAL_MAX_GAP    = 5

MAX_HORIZ_DEG    = 30.0  # Max angle from horizontal to classify as horizontal.
MAX_VERT_DEG     = 5.0   # Max deviation from 90° to classify as vertical.


# ---------------------------------------------------------------------------
# Grid intersection pipeline
# ---------------------------------------------------------------------------

CLEAN_MASK_KERNEL_PX          = 7   # Morphological close on colour mask before Canny — fills fringe misclassification at block boundaries. 0 = disabled.
INTERSECTION_GAP_TOLERANCE_PX = 25  # How far outside a line segment an intersection may fall and still count.
CLUSTER_CELL_SIZE_PX          = 15  # Pass-1 grid-bucket cell size for deduplicating nearby intersection points.
CLUSTER_MERGE_RADIUS_PX       = 12  # Pass-2 merge radius for centroids that straddle bucket boundaries.