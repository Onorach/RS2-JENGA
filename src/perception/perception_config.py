"""
perception_config.py
--------------------
Central configuration for all perception modules.
Tune values here; nothing else needs to change.
"""

TOWER_ANALYSIS = False

BLOCK_ANALYSIS = True

# Search area centre and fraction of the full frame
SEARCH_AREA = (0.502, 0.519, 0.347, 0.600)

# Crop margin around the search area
SEARCH_AREA_MARGIN     = 0.10

# Camera horizontal field of view — used for px → mm lateral conversion.
CAMERA_HFOV_DEG = 69.0

# Camera origin in the global/world frame (mm).
# Block global positions are computed as:
#   global = CAMERA_GLOBAL_POSITION_MM + CAMERA_LOCAL_AXIS_SIGN * local
# Local frame: +X = depth along optical axis, +Y = left in image, +Z = up.
# Camera is mounted flipped 180° about world Z vs the original rig: it faces
# global -X and image-left maps to global -Y.
CAMERA_GLOBAL_POSITION_MM = (318.5, 301.5, 0.0)
CAMERA_LOCAL_AXIS_SIGN = (-1.0, -1.0, 1.0)
# Image-space left/right seam heuristics are unchanged unless the sensor image
# itself is mirrored (set True only if near-face side tests need inverting).
CAMERA_MOUNT_FLIPPED = False
BLOCK_POSE_WORLD_FRAME = "world"

# Camera rotation in global frame is applied via CAMERA_LOCAL_AXIS_SIGN for
# position and BLOCK_YAW_DEG_ASSUMED for block orientation (+180° vs original).

# Block yaw about +Z in the global frame (45° original assumption + 180° mount flip).
BLOCK_YAW_DEG_ASSUMED = 225.0


GRID_LOCK_EDGE_ACCUMULATION_FRAMES = 40

# ---------------------------------------------------------------------------
# Probe / topple-response detection
# ---------------------------------------------------------------------------
#
# Placeholder input until a real topic/service is connected:
# set to an integer block_id (e.g. 4) to start monitoring that block probe.
# Use None to disable.
PROBE_TARGET_BLOCK_ID_PLACEHOLDER: int | None = None

# Minimum increase in the probed block's colour percentage to count as
# meaningful movement response.
PROBE_TARGET_GAIN_MIN_PCT = 3.0

# "Everything else remains similar" tolerance.
PROBE_STABLE_DELTA_MAX_PCT = 3.0

# Increase threshold on above-layer front/mid colours indicating tower shift.
PROBE_ABOVE_LAYER_GAIN_MIN_PCT = 3.0

# Centroid shift threshold (percentage of tower-width normalisation) used to
# decide that the tower moved and the probe result should abort.
CENTROID_ABORT_SHIFT_PCT = 99.0

# ---------------------------------------------------------------------------
# Colour Settings
# ---------------------------------------------------------------------------

# HSV ranges for colour identification
HSV_RANGES: dict[str, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
    "red": [
        ((  0, 175, 149), ( 11, 255, 255)),
        ((165, 175, 149), (179, 255, 255)),
    ],
    "yellow": [
        (( 20,  98, 133), ( 48, 255, 255)),
    ],
    "green": [
        (( 44, 139,  61), ( 90, 255, 255)),
    ],
    "blue": [
        (( 75, 213, 161), (107, 255, 255)),
    ],
    "purple": [
        ((110, 156,  70), (160, 255, 255)),
    ],
}

# Minimum connected-component area (in ROI pixels) kept per colour mask.
# Higher values reject more tiny blobs/noise before the mask is used elsewhere.
# Set to 0 to disable size filtering.
COLOUR_MIN_BLOB_AREA_PX = 195

# Colour-mask smoothing (tuned in colour mask setup).
COLOUR_MASK_MEDIAN_PX      = 4   # Median blur on HSV before inRange; 0 = disabled.
COLOUR_MASK_MORPH_CLOSE_PX = 9   # Close kernel — fills small holes. 0 = disabled.
COLOUR_MASK_MORPH_OPEN_PX  = 13   # Open kernel — removes specks. 0 = disabled.

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

TOWER_MASK_SAT_MIN                 = 196   # Min HSV saturation for tower foreground.
TOWER_MASK_BRIGHTNESS_MIN          = 150    # Min HSV value (brightness) for tower foreground.
TOWER_MASK_MORPH_CLOSE_PX          = 2    # Close kernel size — fills small mask holes. 0 = disabled.
TOWER_MASK_MORPH_OPEN_PX           = 18    # Open kernel size — removes noise blobs. 0 = disabled.

# ---------------------------------------------------------------------------
# Edge detection
# ---------------------------------------------------------------------------

# Valid-point x-bands (percent of ROI width): outer-left, centre, outer-right.
POINT_VALID_SIDE_BAND_PCT   = 11.0
POINT_VALID_CENTER_BAND_PCT = 15.0

# Canny thresholds used on the colour-mask image.
CANNY_MASK_LOW   = 0   # Lower = more edges.
CANNY_MASK_HIGH  = 0  # Higher = fewer, stronger edges only.

# Hough settings used for lines extracted from colour-mask edges.
HOUGH_MASK_THRESHOLD  = 8  # Min Hough votes to accept a line.
HOUGH_MASK_MIN_LENGTH = 80  # Min accepted line length (pixels).
HOUGH_MASK_MAX_GAP    = 30  # Max gap for joining broken line segments.

MAX_HORIZ_DEG    = 20.0  # Max angle from horizontal to classify as horizontal.
MAX_VERT_DEG     = 5.0   # Max deviation from 90° to classify as vertical.

# ---------------------------------------------------------------------------
# Centre-seam detection (vertical line down the tower's near corner)
# ---------------------------------------------------------------------------
#
# The tower stands at ~45° so each layer shows two faces meeting at a vertical
# corner down the middle. That corner is the centre column of the detection
# grid and later anchors the front block's centroid split.
#
# Method: for each layer band take the largest colour blob (the front block's
# near face) and find its closest-to-camera column from depth. On the recoloured
# image the seam has no colour edge (both faces are the same colour), so depth is
# used rather than Canny on the original frame. Solving per layer means the tower
# need not be perfectly vertical.
#
# Robust closest-depth estimate: take the closest this-% of valid depth pixels
# in the blob and use CENTRE_SEAM_X_STAT as the seam column. Median targets the
# near corner between faces; min/max hit an outer blob edge and break the grid.
CENTRE_SEAM_X_STAT = "median"

# Per-colour near-face split line for centroids (mean of closest-depth pixels).
NEAR_FACE_SEAM_X_STAT = "mean"

CENTRE_SEAM_CLOSEST_PCT = 20.0

# Minimum valid (non-zero, finite) depth pixels in a layer's blob before the
# depth seam is trusted for that band. Bands with fewer are skipped.
CENTRE_SEAM_MIN_VALID_PX = 30

# Minimum coloured pixels for a blob to be considered the layer's "largest
# colour" (rejects specks left after classification).
CENTRE_SEAM_MIN_COLOUR_PX = 80

# Horizontal grid lines within this many pixels are merged into one layer
# boundary when splitting the ROI into layer bands.
CENTRE_SEAM_ROW_MERGE_PX = 12

# Layer bands shorter than this (px) are discarded as noise.
CENTRE_SEAM_MIN_BAND_PX = 8


# ---------------------------------------------------------------------------
# Grid intersection pipeline
# ---------------------------------------------------------------------------


CLEAN_MASK_KERNEL_PX          = 7   # Morphological close on colour mask before Canny — fills fringe misclassification at block boundaries. 0 = disabled.
INTERSECTION_GAP_TOLERANCE_PX = 25  # How far outside a line segment an intersection may fall and still count.
CLUSTER_CELL_SIZE_PX          = 15  # Pass-1 grid-bucket cell size for deduplicating nearby intersection points.
CLUSTER_MERGE_RADIUS_PX       = 12  # Pass-2 merge radius for centroids that straddle bucket boundaries.

# After grid lock, extrapolate this many empty layer bands above the detected tower
# so newly placed blocks have cells to fill during live play.
GRID_EXTRA_LAYERS_ON_TOP = 3

# Extrapolated rows: extend centre-column vertical step by this % over the
# standard median row height (edges unchanged). Set to 0 to disable.
GRID_EXTRAPOLATED_CENTER_HEIGHT_EXTEND_PCT = 21.0

# ---------------------------------------------------------------------------
# Robot placement on extrapolated layers
# ---------------------------------------------------------------------------
#
# After pick-and-place, the block outer edge is measured as % of seam→outside
# span on the end-on face. Thresholds assign front / mid / back slots.
PLACEMENT_SLOT_FRONT_MAX_PCT = 50.0   # below → front (~33% nominal)
PLACEMENT_SLOT_MID_MAX_PCT = 83.0     # below → mid (~66% nominal), else back
# Min end-on-face pixels to accept a block as placed on an extrapolated layer.
# Lower-layer colour bleeding into the empty cell above is usually much smaller
# than a real block face; raise this if false placements still occur.
PLACEMENT_MIN_COLOUR_PX = 250

# Minimum connected-component area (px) for a colour blob in a grid cell to
# count as a block centroid. Filters thin slithers at slot boundaries.
BLOCK_CENTROID_MIN_BLOB_PX = 240

# When a block centroid is lost, search this radius (px) around the last known
# position before falling back to a full-cell colour search.
CENTROID_HINT_SEARCH_RADIUS_PX = 60

# Consecutive frames a slot must read absent before it is labeled "missing"
# in layer analysis and before placement search begins.
BLOCK_MISSING_CONFIRM_FRAMES = 4

# Consecutive absent frames before a block is dropped from /jenga/block_states.
# Until then the last published pose is held so brief detection gaps do not
# flicker the GUI.
BLOCK_STATE_PUBLISH_MISSING_CONFIRM_FRAMES = 5

# Backward-compatible alias for placement_tracker.
PLACEMENT_MISSING_CONFIRM_FRAMES = BLOCK_MISSING_CONFIRM_FRAMES

# If this many blocks drop out in one frame, treat it as camera occlusion —
# restore centroids but do not start placement searches.
PLACEMENT_OCCLUSION_MISSING_THRESHOLD = 4