"""
perception_config.py
--------------------
Central configuration for all perception modules.
Tune values here; nothing else needs to change.
"""

TOWER_ANALYSIS = False

BLOCK_ANALYSIS = True

# Search area centre and fraction of the full frame
SEARCH_AREA = (0.509, 0.654, 0.268, 0.456)

# Crop margin around the search area
SEARCH_AREA_MARGIN     = 0.10

# Camera horizontal field of view — used for px → mm lateral conversion.
CAMERA_HFOV_DEG = 69.0

# Camera origin in the global/world frame (mm).
# Block global positions are computed as:
#   block_global = block_camera_local + CAMERA_GLOBAL_POSITION_MM
CAMERA_GLOBAL_POSITION_MM = (-318.5, 301.5, 0.0)
BLOCK_POSE_WORLD_FRAME = "world"

# Camera rotation in global frame is currently treated as zero (identity).
# If a non-identity camera rotation is needed later, add a full transform here.

# Current temporary assumption: each block is rotated 45 degrees about +Z
# relative to the camera frame.
BLOCK_YAW_DEG_ASSUMED = 45.0


GRID_LOCK_EDGE_ACCUMULATION_FRAMES = 40

# ---------------------------------------------------------------------------
# Probe / topple-response detection
# ---------------------------------------------------------------------------
#
# Placeholder input until a real topic/service is connected:
# set to an integer block_id (e.g. 4) to start monitoring that block probe.
# Use None to disable.
PROBE_TARGET_BLOCK_ID_PLACEHOLDER: int | None = None

# Minimum increase in the probed middle-block colour percentage to count as
# meaningful movement response.
PROBE_TARGET_GAIN_MIN_PCT = 3.0

# "Everything else remains similar" tolerance.
PROBE_STABLE_DELTA_MAX_PCT = 3.0

# Increase threshold on above-layer front/mid colours indicating tower shift.
PROBE_ABOVE_LAYER_GAIN_MIN_PCT = 3.0

# Centroid shift threshold (percentage of tower-width normalisation) used to
# decide that the tower moved and the probe result should abort.
CENTROID_ABORT_SHIFT_PCT = 6.0

# ---------------------------------------------------------------------------
# Colour Settings
# ---------------------------------------------------------------------------

# HSV ranges for colour identification
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "red": [
        ((  0, 126,  78), ( 12, 255, 255)),
        ((171, 126,  78), (179, 255, 255)),
    ],
    "yellow": [
        (( 16,   0,  76), ( 44, 255, 255)),
    ],
    "green": [
        (( 55,  65,  62), ( 83, 255, 255)),
    ],
    "blue": [
        (( 82, 114,  88), (111, 255, 255)),
    ],
    "purple": [
        ((114, 118,  60), (169, 255, 255)),
    ],
}

# Minimum connected-component area (in ROI pixels) kept per colour mask.
# Higher values reject more tiny blobs/noise before the mask is used elsewhere.
# Set to 0 to disable size filtering.
COLOUR_MIN_BLOB_AREA_PX = 222

# Colour-mask smoothing (tuned in colour mask setup).
COLOUR_MASK_MEDIAN_PX      = 0   # Median blur on HSV before inRange; 0 = disabled.
COLOUR_MASK_MORPH_CLOSE_PX = 8   # Close kernel — fills small holes. 0 = disabled.
COLOUR_MASK_MORPH_OPEN_PX  = 14   # Open kernel — removes specks. 0 = disabled.

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

TOWER_MASK_SAT_MIN                 = 151   # Min HSV saturation for tower foreground.
TOWER_MASK_BRIGHTNESS_MIN          = 47    # Min HSV value (brightness) for tower foreground.
TOWER_MASK_MORPH_CLOSE_PX          = 0    # Close kernel size — fills small mask holes. 0 = disabled.
TOWER_MASK_MORPH_OPEN_PX           = 31    # Open kernel size — removes noise blobs. 0 = disabled.

# ---------------------------------------------------------------------------
# Edge detection
# ---------------------------------------------------------------------------

# Valid-point x-bands (percent of ROI width): outer-left, centre, outer-right.
POINT_VALID_SIDE_BAND_PCT   = 10.0
POINT_VALID_CENTER_BAND_PCT = 15.0

# Canny thresholds used on the colour-mask image.
CANNY_MASK_LOW   = 24   # Lower = more edges.
CANNY_MASK_HIGH  = 41  # Higher = fewer, stronger edges only.

# Canny thresholds used on the original BGR image.
CANNY_ORIGINAL_LOW  = 25   # Lower = more edges.
CANNY_ORIGINAL_HIGH = 62  # Higher = fewer, stronger edges only.

# Width of the horizontal band (centred on the ROI) where Canny edges are
# kept, as a percentage of ROI width. Edges outside this strip are zeroed
# before Hough line detection, so both visualisation and grid-point search
# are restricted to the middle slice. Set to 100.0 to disable.
CANNY_CENTRE_BAND_PCT = 6.0   # Centre band width (% of ROI) for original Canny / Hough.
CANNY_CENTRE_BAND_OFFSET_PCT = -1.0  # Horizontal offset of that band (% of ROI width): +right, -left.

# Hough settings used for lines extracted from colour-mask edges.
HOUGH_MASK_THRESHOLD  = 8  # Min Hough votes to accept a line.
HOUGH_MASK_MIN_LENGTH = 10  # Min accepted line length (pixels).
HOUGH_MASK_MAX_GAP    = 30  # Max gap for joining broken line segments.

# Hough settings used for lines extracted from original-image edges.
HOUGH_ORIGINAL_THRESHOLD  = 20
HOUGH_ORIGINAL_MIN_LENGTH = 40
HOUGH_ORIGINAL_MAX_GAP    = 5

MAX_HORIZ_DEG    = 12.0  # Max angle from horizontal to classify as horizontal.
MAX_VERT_DEG     = 5.0   # Max deviation from 90° to classify as vertical.


# ---------------------------------------------------------------------------
# Grid intersection pipeline
# ---------------------------------------------------------------------------


CLEAN_MASK_KERNEL_PX          = 7   # Morphological close on colour mask before Canny — fills fringe misclassification at block boundaries. 0 = disabled.
INTERSECTION_GAP_TOLERANCE_PX = 25  # How far outside a line segment an intersection may fall and still count.
CLUSTER_CELL_SIZE_PX          = 15  # Pass-1 grid-bucket cell size for deduplicating nearby intersection points.
CLUSTER_MERGE_RADIUS_PX       = 12  # Pass-2 merge radius for centroids that straddle bucket boundaries.