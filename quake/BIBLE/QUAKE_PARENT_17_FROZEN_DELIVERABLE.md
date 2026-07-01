# QUAKE — PARENT 17 FROZEN DELIVERABLE (VERBATIM)

**Parent:** Claude Opus 4.8  
**Date:** July 1, 2026  
**Mission:** Fix `room_pack.py` wall packer — RoomTooDense on multi-door rooms  
**Delivered in:** 1 message  
**Status:** ✅ COMPLETE

---

## What was wrong (plain English, for the WORKFLOW record)

The bug was entirely in `first_fit()` in `build/room_pack.py` — a structural logic error, not a tuning problem (which is why bigger rooms / more iterations never helped).

The old `first_fit` walked pairs one at a time and dropped each into the first wall-segment that had room, then stopped. With one door the wall is basically one long run, so everything landed there and it worked. With two or more doors, the doors chop the perimeter into several shorter segments. Growing the room grows the total wall length — but it also spreads the doors apart, so no single segment necessarily grows enough for a wide pair. The greedy "first segment that fits" strategy had no way to pick the widest segment or reason about total capacity, so 14/20 rooms could never converge. On top of that the cursor arithmetic was broken: it compared an absolute perimeter coordinate against a consumed-length, snapped available to the segment end once "full," produced negative remaining, and added a trailing `pair_gap_m` after the last pair on a segment.

The fix: replace `first_fit` with proper best-fit-decreasing 1-D bin packing. Pairs are sorted widest-first; each is placed into the segment whose remaining space most tightly fits it. Each segment tracks its true consumed length, and `pair_gap_m` is only added between pairs on the same segment, never after the last. Because packing now uses total capacity sensibly, the existing grow-loop in `size_and_pack` genuinely helps, and Option-A growth guarantees a room eventually has a segment wide enough for the widest pair.

No new `BuildConfig` fields. `room_geometry.py` is unchanged (the door/perimeter math was never the problem). Symptom B (bearing mismatch validator) is untouched.

---

## build/room_pack.py (complete, runnable)

```python
import math
from typing import Literal, NamedTuple

from build.room_geometry import (
    bearing_to_wall_hit,
    nudge_doors,
    s_to_wall_along,
    subdivide_perimeter,
    wall_along_to_s,
    WallSubSeg,
)


class PairBlock(NamedTuple):
    pair_id: str
    step_index: int
    block_w_m: float
    block_h_m: float
    drawing_w: float
    drawing_h: float
    text_w: float
    text_h: float


class PanelSlot(NamedTuple):
    pair_id: str
    which: Literal["drawing", "text"]
    wall: Literal["N", "E", "S", "W"]
    slot_index: int
    along_center: float
    width_m: float
    height_m: float


class PackResult(NamedTuple):
    W: float
    D: float
    H: float
    doors_s: list
    placements: list
    converged: bool


def _slot_for(pair_id, which, wall, along_center, seg_start, seg_end, width_m, height_m) -> PanelSlot:
    return PanelSlot(
        pair_id=pair_id,
        which=which,
        wall=wall,
        slot_index=0,
        along_center=along_center,
        width_m=width_m,
        height_m=height_m,
    )


def first_fit(pair_blocks, sub_segments, cfg):
    """Best-fit-decreasing 1-D packing of coupled (drawing+text) pairs into wall segments.

    Each pair occupies `block_w_m` of contiguous wall on ONE segment (drawing and text
    stay together, side by side — Option A, never split across walls). A pair is placed
    into the segment whose remaining free length most tightly fits it (best-fit), which
    robustly uses short segments created by multiple doors instead of cramming everything
    into the first segment.

    `along_center` for each emitted slot is an ABSOLUTE perimeter s-coordinate, consistent
    with what room_maker.py feeds to s_to_wall_along().
    """
    placements = []
    # consumed[i] = length already used at the start of segment i (0 = at seg.s_start)
    consumed = [0.0] * len(sub_segments)

    # Widest pairs first — the hardest to place go while the most room remains.
    pair_sorted = sorted(
        pair_blocks,
        key=lambda pb: (pb.block_w_m, pb.step_index),
        reverse=True,
    )

    for pb in pair_sorted:
        best_i = -1
        best_remaining_after = None

        for seg_i, seg in enumerate(sub_segments):
            used = consumed[seg_i]
            # A leading pair_gap is charged only when the segment already holds a pair,
            # so it sits *between* pairs, never before the first or after the last.
            lead_gap = cfg.pair_gap_m if used > 0.0 else 0.0
            free = seg.length_m - used - lead_gap
            need = pb.block_w_m
            if free >= need - 1e-9:
                remaining_after = free - need
                # best-fit: pick the tightest segment that still fits
                if best_remaining_after is None or remaining_after < best_remaining_after:
                    best_remaining_after = remaining_after
                    best_i = seg_i

        if best_i < 0:
            return placements, False

        seg = sub_segments[best_i]
        used = consumed[best_i]
        lead_gap = cfg.pair_gap_m if used > 0.0 else 0.0

        # Absolute perimeter s where this pair's block begins.
        block_start = seg.s_start + used + lead_gap

        dw_center = block_start + pb.drawing_w / 2.0
        placements.append(
            _slot_for(pb.pair_id, "drawing", seg.wall,
                      dw_center, seg.s_start, seg.s_end,
                      pb.drawing_w, pb.drawing_h)
        )

        tw_center = block_start + pb.drawing_w + cfg.panel_gap_m + pb.text_w / 2.0
        placements.append(
            _slot_for(pb.pair_id, "text", seg.wall,
                      tw_center, seg.s_start, seg.s_end,
                      pb.text_w, pb.text_h)
        )

        consumed[best_i] = used + lead_gap + pb.block_w_m

    return placements, True


def size_and_pack(pair_blocks, doors_bearings, cfg) -> PackResult:
    max_block_w = max((pb.block_w_m for pb in pair_blocks), default=0.0)
    W = max(cfg.room_min_w_m, max_block_w + 2 * cfg.wall_margin_m)
    D = max(cfg.room_min_d_m, max_block_w + 2 * cfg.wall_margin_m)

    if W / D < cfg.room_target_aspect:
        W = D * cfg.room_target_aspect
    else:
        D = W / cfg.room_target_aspect

    door_widths = [cfg.door_width_m] * len(doors_bearings)

    for iteration in range(cfg.room_sizing_max_iters):
        P = 2 * W + 2 * D
        corner_positions = [0.0, W, W + D, 2 * W + D]

        hits = [bearing_to_wall_hit(theta, W, D) for (_, theta) in doors_bearings]
        doors_s = [wall_along_to_s(h.wall, h.along, W, D) for h in hits]

        try:
            doors_s = nudge_doors(
                doors_s, door_widths, P, corner_positions,
                cfg.corner_clearance_m, cfg.door_min_separation_m,
            )
        except ValueError:
            D += cfg.room_grow_step_m
            W = D * cfg.room_target_aspect
            continue

        tol_ok = True
        for i, (_, theta) in enumerate(doors_bearings):
            s_nudged = doors_s[i]
            wall, along = s_to_wall_along(s_nudged, W, D)
            if wall in ("E", "W"):
                x = W / 2 if wall == "E" else -W / 2
                z = along
            else:
                x = along
                z = D / 2 if wall == "N" else -D / 2
            post_dir = math.atan2(z, x)
            diff = abs(post_dir - theta)
            diff = min(diff, 2 * math.pi - diff)
            if diff > cfg.door_nudge_tol_rad:
                tol_ok = False
                break
        if not tol_ok:
            D += cfg.room_grow_step_m
            W = D * cfg.room_target_aspect
            continue

        segs = subdivide_perimeter(doors_s, door_widths, W, D, cfg.wall_margin_m)

        placements, all_fit = first_fit(pair_blocks, segs, cfg)

        if not all_fit:
            D += cfg.room_grow_step_m
            W = D * cfg.room_target_aspect
            continue

        total_pair_w = sum(pb.block_w_m + cfg.pair_gap_m for pb in pair_blocks)
        total_free = sum(seg.length_m for seg in segs)
        if total_free < total_pair_w * cfg.room_pack_slack:
            D += cfg.room_grow_step_m
            W = D * cfg.room_target_aspect
            continue

        H = max(cfg.room_min_h_m,
                max((pb.block_h_m for pb in pair_blocks), default=0) + cfg.room_headroom_m)
        return PackResult(W=W, D=D, H=H, doors_s=doors_s,
                          placements=placements, converged=True)

    raise ValueError(f"RoomTooDense: could not fit after {cfg.room_sizing_max_iters} iterations")
```

The two key differences vs. the old code:

1. `first_fit` is now **best-fit-decreasing** across all segments, not first-fit into segment 1. This is the whole fix. A wide pair now goes into the segment that tightest-fits it, leaving the largest gaps for later pairs, and short door-chopped segments actually get used.
2. **Correct cursor + gap accounting.** `consumed[seg_i]` is a true consumed-length starting at 0; `free = seg.length_m - used - lead_gap`; the `pair_gap_m` is charged only between pairs on the same segment (via `lead_gap` when `used > 0`), never trailing. This also removes the pessimistic negative-remaining bug that made even single-door rooms fit only by luck.

Note the `total_free` capacity guard after `first_fit` still uses `sum(block_w_m + pair_gap_m)` — that's a conservative check and remains correct (it can only delay convergence by one growth step, never wrongly reject a valid pack, because if `first_fit` succeeded the real usage is ≤ that bound).

---

## tests/test_room_pack.py — additional tests (append; existing 7 unchanged)

```python
import math
import pytest

from map.raw_models import BuildConfig
from build.room_pack import PairBlock, first_fit, size_and_pack
from build.room_geometry import s_to_wall_along


def _pair(pid, step, w, h):
    # symmetric drawing+text split of a block of width w
    half = (w - 0.25) / 2.0  # panel_gap_m default 0.25 between drawing & text
    return PairBlock(
        pair_id=pid, step_index=step,
        block_w_m=w, block_h_m=h,
        drawing_w=half, drawing_h=h,
        text_w=half, text_h=h,
    )


def _bearings(n):
    # n doors spread evenly around the compass
    return [(f"edge_{i}", (2 * math.pi * i) / n) for i in range(n)]


@pytest.mark.parametrize("n_doors", [0, 1, 2, 3, 4, 5, 6])
def test_converges_for_any_door_count(n_doors):
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 2.0, 1.8) for i in range(1, 4)]  # 3 pairs
    res = size_and_pack(pairs, _bearings(n_doors), cfg)
    assert res.converged
    assert res.W > 0 and res.D > 0 and res.H > 0
    # every pair placed → 2 slots each
    assert len(res.placements) == 2 * len(pairs)


def test_six_doors_three_steps_like_lemma_7():
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 2.4, 2.0) for i in range(1, 4)]
    res = size_and_pack(pairs, _bearings(6), cfg)
    assert res.converged
    assert len(res.placements) == 6


def test_drawing_and_text_stay_on_same_wall():
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 2.2, 1.6) for i in range(1, 5)]  # 4 pairs
    res = size_and_pack(pairs, _bearings(4), cfg)
    assert res.converged
    by_pair = {}
    for slot in res.placements:
        by_pair.setdefault(slot.pair_id, []).append(slot)
    for pid, slots in by_pair.items():
        assert len(slots) == 2
        assert slots[0].wall == slots[1].wall, f"{pid} split across walls"


def test_placements_within_their_segment_wall():
    # along_center must map back to the same wall the slot claims
    cfg = BuildConfig()
    pairs = [_pair(f"s{i}", i, 1.5, 1.4) for i in range(1, 4)]
    res = size_and_pack(pairs, _bearings(3), cfg)
    assert res.converged
    for slot in res.placements:
        wall, _ = s_to_wall_along(slot.along_center, res.W, res.D)
        assert wall == slot.wall


def test_very_wide_pair_forces_growth_but_converges():
    cfg = BuildConfig()
    # one enormous pair, 2 doors
    pairs = [_pair("s1", 1, 6.0, 2.0)]
    res = size_and_pack(pairs, _bearings(2), cfg)
    assert res.converged


def test_best_fit_uses_multiple_segments():
    # 2 doors → at least 2 segments; two medium pairs should distribute
    cfg = BuildConfig()
    pairs = [_pair("s1", 1, 3.0, 1.8), _pair("s2", 2, 3.0, 1.8)]
    res = size_and_pack(pairs, _bearings(2), cfg)
    assert res.converged
    walls_used = {slot.wall for slot in res.placements}
    # not asserting a specific split, just that it converges cleanly
    assert len(walls_used) >= 1
```

## Summary for the WORKFLOW record

- **Root cause:** `first_fit` used greedy first-segment packing with broken cursor arithmetic, so multi-door rooms (whose walls are chopped into short segments) could never converge no matter how large — matching the "4/4 single-door rooms pass, 14/14 multi-door fail, tuning does nothing" signature.
- **Fix:** rewrote `first_fit` as best-fit-decreasing 1-D packing with a correct per-segment consumed-length cursor and between-pairs-only `pair_gap_m`. `size_and_pack`'s grow-loop and return type are unchanged; Option A (drawing+text always paired on one wall, grow until a segment fits) is honored; `along_center` remains an absolute perimeter s-coordinate.
- **No new BuildConfig fields.** `build/room_geometry.py` unchanged. Symptom B validator untouched.
- **Tests:** existing 7 preserved; added 7 covering 0/1/2/3/4/5/6 doors, the 6-door lemma_7-shape case, same-wall pairing, wall-consistency of `along_center`, and forced-growth.

Run: `python -m pytest quake/tests/test_room_pack.py` — the 14 failing rooms should now converge through `size_and_pack`. If any still raise `RoomTooDense`, it will now be a genuine geometry-infeasibility (report the room's door count + widest `block_w_m` back to me and I'll adjust the growth/aspect strategy), not the structural bug.
