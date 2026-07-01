# PARENT 17 — MISSION: FIX THE WALL PACKER (room_pack.py / room_geometry.py)

> **Role:** You are a fresh Opus 4.8 architect. You implement this yourself — **no children.**
> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (this project's map)
> 2. Old Testament (Fusion's master doctrine)
> 3. New Testament (Opus's two-legs design)
> 4. **This handoff (the mission brief)**
>
> **Additional files you may request (whole or section, via Nir→DeepSeek):**
> - `quake/BIBLE/QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md` — Room System v3
> - `quake/BIBLE/QUAKE_PARENT_5_GOLDEN_FIXTURE_PACK.md` — golden floorplan/manifest/room specs
> - Any other scripture from the catalog (Commentaries §2)

---

## §0 — YOUR ONE JOB

Make `size_and_pack()` in `build/room_pack.py` (and its helper `build/room_geometry.py`) reliably fit doors + panel pairs into rectangular rooms, for **any number of doors and any number of panel pairs**, without hitting `RoomTooDense`.

---

## §1 — WHAT THIS MODULE DOES (just so you know the lay of the land)

`size_and_pack()` is called by `build/room_maker.py` (line 114) during the build pipeline. It receives:

- **`pair_blocks`** — list of `PairBlock` objects. Each is one step-pair (= one drawing panel + one text panel, placed side-by-side on the same wall). Each has a width (`block_w_m`) and a height (`block_h_m`). Sorted by step index.
- **`doors_bearings`** — list of `(edge_id, bearing_rad)`. One per connecting corridor. The bearing is the TRUE map bearing of the corridor (frozen: matches the floorplan). Doors must open toward that bearing.
- **`cfg`** — a `BuildConfig` (see §4 below). Contains all sizing knobs.

It must return a `PackResult` with room dimensions (W, D, H), door positions along the perimeter (`doors_s`), and panel placements. The room maker then builds a `RoomRuntime` from this.

The room is a **rectangular box** (Wolfenstein-grade, 4 walls: N/E/S/W). Floor and ceiling are Y=0 and Y=H. Each wall's perimeter is parameterized as a 1D "s-coordinate" running 0..P clockwise (P = 2W+2D). Doors are placed on this perimeter via `bearing_to_wall_hit` → `nudge_doors` → `subdivide_perimeter`. Panels are then fit into the remaining wall segments by `first_fit()`.

---

## §2 — THE PATIENT'S SYMPTOMS (what we observe — no diagnosis from us)

### Symptom A: RoomTooDense on most rooms

During the full build pipeline (20 Principia rooms), **14 out of 20 rooms** fail at Stage 6 with:

```
RoomTooDense: could not fit after N iterations
```

Even after increasing `room_sizing_max_iters` to 1000 and `room_grow_step_m` to 1.5m. The 4 rooms that succeed all have exactly **1 door**. Every room with 2+ doors fails, regardless of panel count.

Here are the exact failing rooms with their door counts and step counts:

| Room | Doors | Steps | Fails? |
|------|-------|-------|--------|
| lemma_5 | 1 | 2 | ✅ |
| lemma_12 | 1 | 1 | ✅ |
| law_2 | 2 | 2 | ✅ |
| prop_7 | 1 | 3 | ✅ |
| lemma_2 | 2 | 3 | ❌ |
| lemma_3 | 3 | 2 | ❌ |
| lemma_4 | 2 | 3 | ❌ |
| lemma_6 | 2 | 3 | ❌ |
| lemma_7 | 6 | 3 | ❌ |
| lemma_10 | 3 | 2 | ❌ |
| lemma_11 | 4 | 3 | ❌ |
| prop_1 | 5 | 4 | ❌ |
| prop_2 | 2 | 3 | ❌ |
| prop_4 | 3 | 2 | ❌ |
| prop_6 | 6 | 4 | ❌ |
| prop_11 | 4 | 5 | ❌ |
| prop_15 | 2 | 2 | ❌ |

*(3 additional rooms fail with a DIFFERENT error — door bearing mismatch — see Symptom B below. Those are lemma_9, law_1, prop_13.)*

### Symptom B: Door bearing mismatch on 3 rooms

Three rooms pass the packing but fail room validation with:

```
Door <edge_id> pre-nudge direction X differs from bearing_rad Y (diff 0.05-0.20 rad > 1e-9)
```

The differences are small (0.05–0.20 rad ≈ 3–11 degrees). This is a **separate** validator check in `room_validate.py`, NOT inside `size_and_pack`. You do NOT need to fix this — but if your changes to the packing affect door placement, be aware this validator exists.

### What we tried (did NOT help)

- Increased `room_px_per_m` from 300 → 800 (makes rooms physically bigger)
- Increased `room_sizing_max_iters` from 240 → 1000
- Increased `room_grow_step_m` from 0.5 → 1.5
- Reduced `room_pack_slack` from 1.20 → 0.90
- Reduced wall margins, panel gaps, pair gaps

None of these moved the needle. The 4 rooms that work continue to work; the 14 that fail continue to fail. This suggests the algorithm itself has a structural issue, not a parameter-tuning issue.

---

## §3 — THE TWO FILES YOU ARE OPERATING ON

### File 1: `build/room_pack.py` (161 lines)

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
    placements = []
    seg_cursors = [0.0] * len(sub_segments)
    pair_sorted = sorted(pair_blocks, key=lambda pb: pb.step_index)

    for pb in pair_sorted:
        placed = False
        for seg_i, seg in enumerate(sub_segments):
            available = (seg.s_start + seg_cursors[seg_i]) if seg_cursors[seg_i] < seg.length_m else seg.s_end
            remaining = seg.s_end - available
            need = pb.block_w_m + cfg.pair_gap_m

            if remaining >= need:
                dw_center = available + pb.drawing_w / 2.0
                drawing_slot = _slot_for(pb.pair_id, "drawing", seg.wall,
                                         dw_center, seg.s_start, seg.s_end,
                                         pb.drawing_w, pb.drawing_h)
                placements.append(drawing_slot)

                tw_center = available + pb.drawing_w + cfg.panel_gap_m + pb.text_w / 2.0
                text_slot = _slot_for(pb.pair_id, "text", seg.wall,
                                      tw_center, seg.s_start, seg.s_end,
                                      pb.text_w, pb.text_h)
                placements.append(text_slot)

                seg_cursors[seg_i] += need
                placed = True
                break
        if not placed:
            return placements, False

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

### File 2: `build/room_geometry.py` (188 lines)

```python
import math
from typing import List, Literal, NamedTuple, Tuple

Wall = Literal["N", "E", "S", "W"]


class WallHit(NamedTuple):
    wall: Wall
    along: float


class WallSubSeg(NamedTuple):
    wall: Wall
    s_start: float
    s_end: float
    length_m: float


def bearing_to_wall_hit(theta: float, W: float, D: float) -> WallHit:
    hx = W / 2.0
    hz = D / 2.0
    c = math.cos(theta)
    s_val = math.sin(theta)
    tx = hx / abs(c) if c != 0 else math.inf
    tz = hz / abs(s_val) if s_val != 0 else math.inf

    if abs(tx - tz) < 1e-9:
        use_x = abs(c) >= abs(s_val)
    else:
        use_x = tx < tz

    if use_x:
        t = tx
        wall = "E" if c > 0 else "W"
        along = t * s_val
    else:
        t = tz
        wall = "N" if s_val > 0 else "S"
        along = t * c
    return WallHit(wall, along)


def wall_along_to_s(wall: Wall, along: float, W: float, D: float) -> float:
    hx = W / 2.0
    hz = D / 2.0
    if wall == "N":
        return along + hx
    elif wall == "E":
        return W + (hz - along)
    elif wall == "S":
        return W + D + (hx - along)
    elif wall == "W":
        return 2 * W + D + (along + hz)
    raise ValueError("bad wall")


def s_to_wall_along(s_val: float, W: float, D: float) -> Tuple[Wall, float]:
    hx = W / 2.0
    hz = D / 2.0
    p = s_val % (2 * W + 2 * D)
    if p < W:
        return ("N", p - hx)
    elif p < W + D:
        return ("E", hz - (p - W))
    elif p < 2 * W + D:
        return ("S", hx - (p - (W + D)))
    else:
        return ("W", (p - (2 * W + D)) - hz)


def nudge_doors(doors_s, widths, P, corner_positions,
                corner_clearance_m, door_min_separation_m) -> List[float]:
    n = len(doors_s)
    if n == 0:
        return []

    s = [float(x) % P for x in doors_s]
    w = list(widths)
    total_push = 0.0

    # (a) corner clearance
    for i in range(n):
        clear = corner_clearance_m + w[i] / 2.0
        changed = True
        guard = 0
        while changed:
            changed = False
            guard += 1
            if guard > 4 * len(corner_positions) + 8:
                break
            for s_c in corner_positions:
                for cc in (s_c, s_c - P, s_c + P):
                    if abs(s[i] - cc) < clear:
                        target = cc + clear
                        push = (target - s[i]) % P
                        s[i] = (s[i] + push) % P
                        total_push += push
                        changed = True

    # (b) sort
    order = sorted(range(n), key=lambda k: s[k])
    s = [s[k] for k in order]
    w = [w[k] for k in order]

    # (c) min-separation sweep
    def needed_gap(a, b):
        return (w[a] + w[b]) / 2.0 + door_min_separation_m

    def sweep_func():
        nonlocal total_push
        for i in range(1, n):
            gap = s[i] - s[i - 1]
            need = needed_gap(i - 1, i)
            if gap < need - 1e-12:
                push = need - gap
                s[i] = s[i] + push
                total_push += push

    sweep_func()
    if n >= 2:
        gap = (s[0] + P) - s[n - 1]
        need = needed_gap(n - 1, 0)
        if gap < need - 1e-12:
            push = need - gap
            for i in range(n):
                s[i] = s[i] + push
            total_push += push * n
            sweep_func()

    # (d) feasibility
    if total_push > P:
        raise ValueError("NudgeInfeasible")
    base = min(s)
    if any(x - base >= P for x in s):
        raise ValueError("NudgeInfeasible")
    span = max(s) - min(s)
    if n >= 2 and span >= P:
        raise ValueError("NudgeInfeasible")

    return [x % P for x in s]


def subdivide_perimeter(doors_s, widths, W, D, wall_margin_m) -> List[WallSubSeg]:
    P = 2 * W + 2 * D

    def in_door(point_s):
        for ds, wd in zip(doors_s, widths):
            a = (ds - wd / 2.0) % P
            b = (ds + wd / 2.0) % P
            if a <= b:
                if a - 1e-12 < point_s < b + 1e-12:
                    return True
            else:
                if point_s > a - 1e-12 or point_s < b + 1e-12:
                    return True
        return False

    # collect all boundary points
    pts = {0.0, P}
    corners = [0.0, W, W + D, 2 * W + D]
    for c in corners:
        pts.add(c)
    for ds, wd in zip(doors_s, widths):
        a = (ds - wd / 2.0) % P
        b = (ds + wd / 2.0) % P
        pts.add(a)
        pts.add(b)
    sorted_pts = sorted(pts)

    result = []
    for i in range(len(sorted_pts) - 1):
        lo = sorted_pts[i]
        hi = sorted_pts[i + 1]
        if hi - lo <= 1e-12:
            continue
        mid = (lo + hi) / 2.0
        if in_door(mid):
            continue
        s_start = lo + wall_margin_m
        s_end = hi - wall_margin_m
        length = max(0.0, s_end - s_start)
        if length <= 1e-12:
            continue
        wall, _ = s_to_wall_along(mid % P, W, D)
        result.append(WallSubSeg(wall, s_start, s_end, length))

    result.sort(key=lambda seg: seg.s_start)
    return result
```

---

## §4 — THE KNOBS (BuildConfig, from `map/raw_models.py`)

```python
class BuildConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    # bake
    bake_dpi_wall: int = 220
    bake_dpi_master: int = 600
    bake_trim_alpha: int = 8
    bake_pad_px: int = 16
    # layout
    layout_seed: int = 1729001
    layout_scale_m: float = 28.0
    height_delta_m: float = 4.5
    max_height_levels_warn: int = 7
    max_height_levels_fail: int = 12
    guide_w_imp: float = 0.6
    guide_w_dist: float = 0.4
    guide_max_lines: int = 3
    # room / panel sizing
    room_px_per_m: float = 360
    panel_min_w_m: float = 0.6
    panel_max_w_m: float = 3.2
    panel_min_h_m: float = 0.5
    panel_max_h_m: float = 2.4
    panel_gap_m: float = 0.25
    pair_gap_m: float = 0.8
    wall_margin_m: float = 0.6
    room_headroom_m: float = 1.2
    room_min_w_m: float = 6.0
    room_min_d_m: float = 6.0
    room_min_h_m: float = 3.2
    panel_center_y_pref_m: float = 1.55
    importance_w_indeg: float = 0.6
    importance_w_hint: float = 0.4
    # room v3 door/placement
    door_width_m: float = 2.0
    door_height_m: float = 2.6
    door_min_separation_m: float = 2.6
    corner_clearance_m: float = 0.5
    room_target_aspect: float = 1.30
    room_pack_slack: float = 1.20
    room_grow_step_m: float = 0.5
    room_sizing_max_iters: int = 240
    aisle_depth_m: float = 1.6
    demon_offset_m: float = 1.0
    door_nudge_tol_rad: float = 0.20
```

Any of these can be adjusted. New fields can be added (they'll be accepted by pydantic). The defaults above are the shipped values; the build script (`build/build_all.py`) overrides some at construction time.

---

## §5 — THE CALL SITE (room_maker.py line 114)

The caller does:

```python
from build.room_pack import PairBlock, size_and_pack

# ... builds pair_blocks from RoomSource + manifest ...
# ... builds doors_bearings from RoomPortalSpec ...

pack = size_and_pack(pair_blocks, doors_bearings, cfg)
```

The returned `PackResult` is used to construct `WallSlot`, `PanelPlacementRT`, `DoorRT`, `CeilingEqRT`, and finally `RoomRuntime`.

**The call site is FROZEN.** You may change `size_and_pack`'s internals and its return type, but NOT:
- The function name and its parameter types (pair_blocks, doors_bearings, cfg)
- The fields of `PackResult` that `room_maker.py` depends on (W, D, H, doors_s, placements)
- The `PairBlock` and `PanelSlot` types that `room_maker.py` imports

---

## §6 — THE FOUR EXISTING TESTS (room_pack.py is covered by test_room_pack.py)

The existing tests in `tests/test_room_pack.py` (7 tests, all green) exercise:
- Single pair, single door
- Multiple pairs, additive growth
- Determinism
- Too-dense → ValueError
- First-fit happy path
- First-fit no-fit

You may add tests but must not break the existing ones.

---

## §7 — DATA FLOW MAP (for orientation)

```
ConceptGraph + Floorplan
        │
        ▼
  portal_spec() ──► RoomPortalSpec (incident edges with bearing_rad)
        │
        ▼
  room_maker.build_room_runtime()
        │
        ├─► builds pair_blocks from RoomSource blocks + manifest PNG sizes
        ├─► builds doors_bearings from RoomPortalSpec
        │
        ▼
  size_and_pack(pair_blocks, doors_bearings, cfg)   ◄── YOU ARE HERE
        │
        ▼
  PackResult ──► RoomRuntime (wall slots, door RTs, panel placements)
```

---

## §8 — WHAT IS FROZEN (do not touch)

1. **The 4-wall rectangular box room shape** — Wolfenstein-grade, frozen by Nir
2. **Door bearing = true map bearing** — from Room System v3 (Apocrypha)
3. **TARDIS rooms** — room size is determined by content, not by the map
4. **Room axes parallel to map axes** — global compass
5. **`concept_graph.json` and `floorplan.json`** — already validated, frozen
6. **`BuildConfig` existing field names** — may add new fields, may NOT rename/remove existing ones
7. **`room_maker.py`'s call site** — function signature unchanged
8. **`portal_spec.py`** — must not change

---

## §9 — OUTPUT OF YOUR WORK

1. **Updated `build/room_pack.py`** (and `build/room_geometry.py` if needed) — complete, runnable code
2. **Updated `tests/test_room_pack.py`** if needed
3. **Any new `BuildConfig` fields** (list them with defaults and descriptions)
4. **A short plain-English explanation of what was wrong and how you fixed it** (for the WORKFLOW record)

---

## §10 — RULES FOR THIS MISSION

- **Talk first.** State your diagnosis and proposed fix BEFORE writing code. Wait for Nir to confirm.
- **Minimum batches.** Try to deliver in 1–2 messages total. Don't burn context on dozens of back-and-forths.
- **No children.** You implement this yourself.
- **No re-deciding frozen contracts.** Read §8 carefully.
- **Test the edge cases.** Rooms with 0 doors, 1 door, 6 doors. Small panels, big panels. Single step, many steps.
- **The build must still pass:** `python -m pytest quake/tests/test_room_pack.py`

---

*Written by DeepSeek, July 1, 2026, after the build pipeline marathon. 20/20 rooms emitted; 16/20 figures compiled; ALL text + ceilings baked; but only 4/20 room runtimes due to this wall packer issue. Fix this and we ship.*
