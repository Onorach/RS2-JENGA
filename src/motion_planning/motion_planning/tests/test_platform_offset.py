"""Unit tests for parametric platform_offset in jenga_tower_mtc_layout.yaml."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from motion_planning.jenga_tower_mtc_sequencer import (
    _parametric_steps,
    _parametric_tower_poses,
    _stock_pick_xyz_list,
    parametric_platform_offset,
    tower_poses_from_layout_dict,
)

_LAYOUT = (
    Path(__file__).resolve().parents[2] / "config" / "jenga_tower_mtc_layout.yaml"
)


def _load_layout() -> dict:
    with _LAYOUT.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def test_parametric_platform_offset_defaults_to_zero():
    data = _load_layout()
    assert parametric_platform_offset(data) == (0.0, 0.0)


def test_platform_offset_shifts_tower_and_stock_equally():
    data = _load_layout()
    base = copy.deepcopy(data)
    shifted = copy.deepcopy(data)
    shifted["parametric"]["platform_offset"] = {"x": 0.01, "y": -0.02}

    ox, oy = 0.01, -0.02
    p = base["parametric"]
    t = p["tower"]
    n = int(t["blocks_per_layer"]) * int(t["layers"])

    tower_base = _parametric_tower_poses(base)[0].position
    tower_shift = _parametric_tower_poses(shifted)[0].position
    assert tower_shift.x == pytest.approx(tower_base.x + ox)
    assert tower_shift.y == pytest.approx(tower_base.y + oy)
    assert tower_shift.z == pytest.approx(tower_base.z)

    stock_base = _stock_pick_xyz_list(p["stock"], n_tower=n, xy_offset=(0.0, 0.0))[0]
    stock_shift = _stock_pick_xyz_list(
        shifted["parametric"]["stock"],
        n_tower=n,
        xy_offset=parametric_platform_offset(shifted),
    )[0]
    assert stock_shift[0] == pytest.approx(stock_base[0] + ox)
    assert stock_shift[1] == pytest.approx(stock_base[1] + oy)
    assert stock_shift[2] == pytest.approx(stock_base[2])

    pick_base, _ = _parametric_steps(base)[0]
    pick_shift, _ = _parametric_steps(shifted)[0]
    assert pick_shift.position.x == pytest.approx(pick_base.position.x + ox)
    assert pick_shift.position.y == pytest.approx(pick_base.position.y + oy)

    via_helper = tower_poses_from_layout_dict(shifted)[0].position
    assert via_helper.x == pytest.approx(tower_shift.x)
    assert via_helper.y == pytest.approx(tower_shift.y)
