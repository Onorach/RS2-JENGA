"""
play_live.py
------------
Live mode for Jenga perception from a RealSense camera via ROS topics.

Usage
-----
    cd src/perception
    python3 play_live.py [--setup]

Or from the repo root (RS2-JENGA/):

    python3 src/perception/play_live.py [--setup]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure local imports (play_runtime, setup.*) resolve regardless of cwd.
_PERCEPTION_DIR = Path(__file__).resolve().parent
if str(_PERCEPTION_DIR) not in sys.path:
    sys.path.insert(0, str(_PERCEPTION_DIR))

from play_runtime import run_subscribe

COLOR_TOPIC = "/camera/camera/color/image_raw"
DEPTH_TOPIC = "/camera/camera/aligned_depth_to_color/image_raw"


def main() -> None:
    parser = argparse.ArgumentParser(description="Live Jenga perception from ROS camera topics.")
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run search-area, colour, tower mask, and depth confirm calibration.",
    )
    args = parser.parse_args()

    if args.setup:
        from setup.search_area_setup import run_search_area_setup_subscribe

        run_search_area_setup_subscribe(COLOR_TOPIC, DEPTH_TOPIC)
    else:
        run_subscribe(COLOR_TOPIC, DEPTH_TOPIC)


if __name__ == "__main__":
    main()
