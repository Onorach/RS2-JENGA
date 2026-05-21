"""Backward-compatible alias — use original_canny_setup / mask_canny_setup."""

from setup.original_canny_setup import run_original_canny_setup as run_edge_setup

__all__ = ["run_edge_setup"]
