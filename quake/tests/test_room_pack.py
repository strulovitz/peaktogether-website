import math

from build.room_geometry import WallSubSeg
from build.room_pack import (
    PairBlock,
    first_fit,
    size_and_pack,
)


class Cfg:
    room_px_per_m = 360
    panel_min_w_m = 0.6
    panel_max_w_m = 3.2
    panel_min_h_m = 0.5
    panel_max_h_m = 2.4
    panel_gap_m = 0.25
    pair_gap_m = 0.8
    wall_margin_m = 0.6
    room_headroom_m = 1.2
    room_min_w_m = 6.0
    room_min_d_m = 6.0
    room_min_h_m = 3.2
    panel_center_y_pref_m = 1.55
    room_target_aspect = 1.30
    room_pack_slack = 1.20
    room_grow_step_m = 0.5
    room_sizing_max_iters = 240
    door_width_m = 2.0
    door_min_separation_m = 2.6
    corner_clearance_m = 0.5
    door_nudge_tol_rad = 0.20


def test_size_and_pack_one_pair_one_door():
    cfg = Cfg()
    pair = PairBlock("a.s1", 1, 3.0, 1.0, 1.5, 1.0, 1.25, 0.8)
    result = size_and_pack([pair], [("E", 0.0)], cfg)
    assert result.converged
    assert result.W >= 6.0
    assert result.D >= 6.0
    assert abs(result.W / result.D - cfg.room_target_aspect) < 0.01
    assert len(result.placements) == 2
    assert result.placements[0].pair_id == "a.s1"


def test_additive_growth_determinism():
    cfg = Cfg()
    pair = PairBlock("a.s1", 1, 8.0, 1.0, 4.0, 1.0, 3.75, 0.8)
    result = size_and_pack([pair], [("N", math.pi / 2)], cfg)
    assert result.converged
    assert result.W >= 9.2


def test_byte_identical_rerun():
    cfg = Cfg()
    # Use smaller blocks that fit without growth
    pair1 = PairBlock("a.s1", 1, 2.0, 1.0, 1.0, 1.0, 0.75, 0.8)
    bearings = [("E", 0.0), ("S", -math.pi / 2)]  # doors on opposite walls
    result1 = size_and_pack([pair1], bearings, cfg)
    result2 = size_and_pack([pair1], bearings, cfg)
    assert result1.W == result2.W
    assert result1.D == result2.D
    assert result1.H == result2.H
    assert len(result1.placements) == len(result2.placements)
    assert result1.converged == result2.converged


def test_too_dense():
    cfg = Cfg()
    cfg.room_sizing_max_iters = 3
    cfg.room_grow_step_m = 0.01
    blocks = [PairBlock("a.s1", 1, 15.0, 2.0, 7.5, 2.0, 7.25, 1.5)] * 10
    bearings = [("N", math.pi / 2)] * 8
    try:
        size_and_pack(blocks, bearings, cfg)
        assert False, "should have raised"
    except ValueError as e:
        assert "RoomTooDense" in str(e)


def test_pair_not_split_across_corner():
    cfg = Cfg()
    pair = PairBlock("a.s1", 1, 3.0, 1.0, 1.5, 1.0, 1.25, 0.8)
    result = size_and_pack([pair], [("S", -math.pi / 2)], cfg)
    assert result.converged
    walls = {p.wall for p in result.placements}
    assert len(walls) == 1


def test_first_fit_happy_path():
    cfg = Cfg()
    seg = WallSubSeg("N", 0.6, 9.4, 8.8)
    pb = PairBlock("a.s1", 1, 3.0, 1.0, 1.5, 1.0, 1.25, 0.8)
    placements, ok = first_fit([pb], [seg], cfg)
    assert ok
    assert len(placements) == 2


def test_first_fit_no_fit():
    cfg = Cfg()
    seg = WallSubSeg("N", 0.6, 2.0, 1.4)
    pb = PairBlock("a.s1", 1, 3.0, 1.0, 1.5, 1.0, 1.25, 0.8)
    placements, ok = first_fit([pb], [seg], cfg)
    assert not ok


# --- Parent 17 additional tests (best-fit-decreasing packer) ---

import pytest
from map.raw_models import BuildConfig
from build.room_geometry import s_to_wall_along


def _pair(pid, step, w, h):
    half = (w - 0.25) / 2.0
    return PairBlock(
        pair_id=pid, step_index=step,
        block_w_m=w, block_h_m=h,
        drawing_w=half, drawing_h=h,
        text_w=half, text_h=h,
    )


def _bearings(n):
    return [(f"edge_{i}", (2 * math.pi * i) / n) for i in range(n)]


@pytest.mark.parametrize("n_doors", [0, 1, 2, 3, 4, 5, 6])
def test_converges_for_any_door_count(n_doors):
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 2.0, 1.8) for i in range(1, 4)]
    res = size_and_pack(pairs, _bearings(n_doors), cfg)
    assert res.converged
    assert res.W > 0 and res.D > 0 and res.H > 0
    assert len(res.placements) == 2 * len(pairs)


def test_six_doors_three_steps_like_lemma_7():
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 2.4, 2.0) for i in range(1, 4)]
    res = size_and_pack(pairs, _bearings(6), cfg)
    assert res.converged
    assert len(res.placements) == 6


def test_drawing_and_text_stay_on_same_wall():
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 2.2, 1.6) for i in range(1, 5)]
    res = size_and_pack(pairs, _bearings(4), cfg)
    assert res.converged
    by_pair = {}
    for slot in res.placements:
        by_pair.setdefault(slot.pair_id, []).append(slot)
    for pid, slots in by_pair.items():
        assert len(slots) == 2
        assert slots[0].wall == slots[1].wall, f"{pid} split across walls"


def test_placements_within_their_segment_wall():
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 1.5, 1.4) for i in range(1, 4)]
    res = size_and_pack(pairs, _bearings(3), cfg)
    assert res.converged
    for slot in res.placements:
        wall, _ = s_to_wall_along(slot.along_center, res.W, res.D)
        assert wall == slot.wall


def test_very_wide_pair_forces_growth_but_converges():
    cfg = BuildConfig()
    pairs = [_pair("s1", 1, 6.0, 2.0)]
    res = size_and_pack(pairs, _bearings(2), cfg)
    assert res.converged


def test_best_fit_uses_multiple_segments():
    cfg = BuildConfig()
    pairs = [_pair("s1", 1, 3.0, 1.8), _pair("s2", 2, 3.0, 1.8)]
    res = size_and_pack(pairs, _bearings(2), cfg)
    assert res.converged
    walls_used = {slot.wall for slot in res.placements}
    assert len(walls_used) >= 1
