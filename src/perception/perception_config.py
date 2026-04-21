"""
Shared configuration for perception scripts.

Centralize values that multiple modules use:
- HSV masks and display colours
- ROI and divide line
- Grid corners
- OpenCV window defaults
"""


# HSV colour ranges. Each colour maps to one or more (lower, upper) bounds.
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
        ((90, 220, 130), (110, 255, 255)),
    ],
    "purple": [
        ((110, 110, 50), (175, 255, 200)),
    ],
}

# BGR display colour per class.
COLOUR_BGR: dict[str, tuple[int, int, int]] = {
    "red": (0, 0, 220),
    "yellow": (0, 220, 220),
    "green": (0, 200, 0),
    "blue": (220, 80, 0),
    "purple": (180, 0, 180),
    "none": (0, 0, 0),
}

# Search ROI: (cx_frac, cy_frac, w_frac, h_frac).
ROI_FRACS = (0.495, 0.485, 0.32, 0.62)

# Face-dividing line in full-frame coordinates.
DIVIDE_LINE = ((920, 217), (914, 850))

# Grid corners used by play overlays.
GRID_CORNERS: list[list[tuple[int, int] | None]] = [
    [(664, 197), (920, 217), (1237, 215)],
    [(669, 282), (916, 315), (1228, 297)],
    [(675, 359), (918, 410), (1224, 380)],
]

# Initial OpenCV window size (width, height) for all play windows.
DEFAULT_WINDOW_SIZE = (960, 540)

