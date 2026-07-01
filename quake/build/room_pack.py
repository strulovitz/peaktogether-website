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

        # nudge_doors sorts doors by perimeter position internally;
        # reorder bearings to match so tolerance check compares correctly.
        pre_sort_s = [x % P for x in doors_s]
        bearing_order = sorted(range(len(doors_bearings)), key=lambda k: pre_sort_s[k])
        sorted_bearings = [doors_bearings[k] for k in bearing_order]

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
        for i, (_, theta) in enumerate(sorted_bearings):
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

        # Unsort doors_s to match original bearing order (nudge_doors sorted them)
        unsort = [0.0] * len(bearing_order)
        for new_i, old_i in enumerate(bearing_order):
            unsort[old_i] = doors_s[new_i]
        doors_s = unsort

        H = max(cfg.room_min_h_m,
                max((pb.block_h_m for pb in pair_blocks), default=0) + cfg.room_headroom_m)
        return PackResult(W=W, D=D, H=H, doors_s=doors_s,
                          placements=placements, converged=True)

    raise ValueError(f"RoomTooDense: could not fit after {cfg.room_sizing_max_iters} iterations")
