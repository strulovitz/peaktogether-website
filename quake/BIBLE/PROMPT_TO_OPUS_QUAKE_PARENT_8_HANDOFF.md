# PROMPT TO OPUS — QUAKE PARENT 8 — Layout-Engine Hardening + 3D Map Viewer

> Paste this into a FRESH Claude Opus 4.8 chat, AFTER pasting the three baseline documents (the Commentaries, the Old Testament, the New Testament). This handoff is self-contained for the mission; everything else you need, you request verbatim from Nir stage-by-stage (see §2).

---

## §0 — WHO YOU ARE, AND THE RULES

You are **Parent 8**, the architect for this mission. In this project, the working model is: architects (you) write design and—when asked—code; fresh "child" chats sometimes implement modules; **DeepSeek** (the Runner, in OpenCode on Nir's Windows PC) integrates code, runs tests, and pushes to git; **Nir** decides everything and carries text between chats. **Nir knows no code and no math** — never ask him to read code or verify math; ask him only to paste material or to eyeball whether something *looks* right.

**Nir's explicit decisions for THIS mission:**
1. **YOU implement this yourself — NOT a child.** This fix is holistic and touches several modules at once; splitting it across children would lose the whole-picture view. So you produce the actual, complete, ready-to-drop-in Python file contents yourself (in fenced code blocks), and DeepSeek drops them in and runs the tests.
2. **NO hardcoded magic numbers for level size — anywhere.** The bug below was born from testing only a hand-built 4-node toy. Do not write "4" or "20" or any fixed room/node/edge count into the engine or the tests. Everything must **scale with the graph** and the tests must be **general** (generated/parametrized), proving the engine works for *any* size.

**Iron rules (from the Commentaries):** never re-decide a frozen contract; before changing anything contracted, request that exact section verbatim and design *with* it; invent nothing; mark genuine gaps; never assert an external library's API from memory (let the compile/test loop confirm); anything Nir copy-pastes must be prose or fenced code blocks, **never Markdown tables**.

---

## §1 — WHERE THE PROJECT IS (one breath)

QUAKE is a first-person, true-3D game that turns a geometry-rich book (first: Newton's *Principia*) into a walkable 3D concept-graph dungeon: each idea = a room, each logical dependency = a corridor, and because a force-directed graph layout inevitably crosses, corridors cross at different heights as **bridges/underpasses** — which is *why* it must be true 3D ("Quake"), not flat.

The runtime engine is **built and green: 285/285 tests.** Parents 1–6 built and wired it. **Parent 7** just delivered the first REAL level — Newton's Book 1, Sections I–III, "First & Last Ratios → the Inverse-Square Law": **20 rooms, 28 dependency edges**, a valid concept graph (`concept_graph.json`) that passes every data contract.

Then DeepSeek ran the very first real build step — feeding that 20-node graph into the layout engine (`level_maker`) — **and the engine broke down at real scale.** That is your mission.

---

## §2 — ⚠️ HOW YOU GET INFORMATION (READ THIS — IT KEEPS YOU ALIVE) ⚠️

You have **no internet, no file access, no memory** — you only know what is in this chat. The project's codebase is large; if Nir pastes too much at once, your context window fills and you "die." So we feed you material **stage by stage, verbatim, only when you ask.**

**This handoff already inlines the code you need for STAGE 1 (the engine fix): see §6.** For everything else, ask Nir in plain language, e.g.:
- *"Nir, please ask DeepSeek to paste the full `render_wire.py` (the Mode-A wireframe renderer) and `camera.py` — verbatim."* (you'll want these for the map viewer, §9)
- *"Nir, please ask DeepSeek to paste `gfx_context.py`, `shaders.py`, and `input_actions.py` verbatim."*
- *"Nir, please ask DeepSeek to paste the full `tests/test_layout_height.py` and `tests/test_layout_force.py`."*
- *"Nir, please ask DeepSeek to paste `tests/golden_pack/floorplan.json`"* (a known-good small floorplan to test the viewer against).
- *"Nir, please ask DeepSeek to paste Second Canon §4.4 (the floorplan schema)."*

DeepSeek will fetch the exact text from disk/GitHub and Nir will paste it back. **Ask for one or two things at a time. Only request a whole file when you truly need its full flow.** When in doubt, ask DeepSeek to *search* and return only the relevant excerpt rather than a whole file.

---

## §3 — YOUR MISSION (two parts; you implement both yourself)

**PART A — Harden the map-layout engine** so it produces a *healthy* floorplan for a real-size graph, robustly and at any scale, and add the real-scale regression tests that should have existed.

**PART B — Build a standalone 3D wireframe "map-viewer" utility** that loads a `floorplan.json` and lets a human **fly around it** (arrow keys + WASD) to inspect the whole level in 3D — seeing rooms, corridors, and the bridges/underpasses at their true heights. This is (1) Nir's eyes, so he can *see* whether a layout is healthy before we build rooms on it, and (2) the seed of the future **in-game "map mode"** (like pressing TAB in Doom to see the automap — but ours is 3D wireframe and free-fly, because of the bridges).

Deliver Part A first (it unblocks everything); Part B can follow in the same session or the next.

---

## §4 — THE BUG (evidence / reproduction)

DeepSeek authored Parent 7's graph to `levels/principia_bk1_inverse_square/concept_graph.json` (20 nodes, 28 edges, valid DAG, fully connected) and ran `build_floorplan(graph, seed=1729001, LevelMakerConfig())`. Result:

```
nodes / rooms:     20 / 20        (OK)
edges / corridors: 28 / 28        (OK)
DAG:               True           (OK)
weakly connected:  True           (OK)
crossings:         191            (PATHOLOGICAL — a clean 20-room map should have ~a couple dozen)
height levels:     [0,1,2,3,4,5]  (6 layers; under the soft cap of 7, but only by luck)
```

Two failure signatures:
1. **191 crossings** out of only 28 corridors — that is roughly *half of all possible corridor pairs* reported as crossing. A correctly-spread 20-node / 28-edge graph should yield far fewer.
2. **Impossible crossing coordinates.** While every room sits within ±100 m, many reported crossing points are absurdly far away, e.g.:
   ```
   crossing_55:  at = (1661.31, -579.53)
   crossing_117: at = (-22484.20, -10650.62)
   crossing_121: at = (-20138.30, -9536.69)
   crossing_125: at = (-15245.92, -7227.48)
   crossing_130: at = (-16554.87, -7850.21)
   ```
   A crossing point that lies *between two corridors whose endpoints are all within ±100 m* can never be at (-22484, -10650). These are spurious.

(Side note, FYI, not your concern: the run also empirically confirmed that node degrees `lemma_7 = 6` and `prop_11 = 4`, correcting two miscounts in Parent 7's prose. The graph data itself is fine.)

---

## §5 — DEEPSEEK'S DIAGNOSIS (offered as *data*, not as your decree — think holistically)

Two compounding causes; you decide the real fix:

1. **The force layout collapses at scale.** `place_nodes` calls `networkx.spring_layout(G, k=None, seed=..., iterations=200)` and scales the unit output by `scale_m=40`. With `k=None`, the ideal spring distance shrinks as node count grows, so 20 nodes (with hub nodes of degree 6) pile into tight clusters; many corridors then genuinely pass through the same choke points → real-but-excessive crossings. This was only ever exercised on a 4-node graph.

2. **The crossing detector is not numerically robust.** In `layout_height._segments_intersect`, the crossing predicate uses raw floating-point orientation values compared with `!=` (`if o1 != o2 and o3 != o4`). For nearly-parallel / nearly-collinear corridor pairs, those orientations are ~0 but can get *opposite signs from floating-point noise*, falsely passing the test; the code then computes the intersection of the two **infinite lines** (denominator ≈ 0 ⇒ huge `t`), producing the far-away phantom points. There is also **no check that the computed intersection actually lies within both segments' spans** — a correct segment intersection point can never be out of both bounding boxes.

A robust crossing test typically: (a) treats orientations within an epsilon of 0 as collinear (→ not a proper crossing), and (b) after computing the point, verifies it lies within both segments (e.g. parameters `t, u ∈ [0,1]`, or a bounding-box containment check). You may redesign `place_nodes` and/or `detect_crossings`/`_segments_intersect` as you see fit, as long as the contracts and existing tests below hold.

---

## §6 — THE ACTUAL CODE YOU ARE FIXING (verbatim)

### 6.1 — `map/layout_force.py` (the node placement)

```python
"""Force-directed 2D node placement using networkx spring_layout."""

from __future__ import annotations

import math

import networkx as nx
from pydantic import BaseModel, ConfigDict

from map.raw_models import ConceptGraph, NodeId, Vec2


class LayoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scale_m: float = 40.0     # world half-extent in meters
    iterations: int = 200     # spring_layout iterations


def place_nodes(graph: ConceptGraph, seed: int, cfg: "LayoutConfig") -> dict[NodeId, Vec2]:
    """Force-directed layout. Returns {node_id: (x, z)} in world meters."""
    # CANONICALIZE: sort nodes and edges for order-independence.
    sorted_node_ids = sorted(n.id for n in graph.nodes)
    sorted_edges = sorted(
        ((e.source, e.target) for e in graph.edges),
        key=lambda st: (st[0], st[1]),
    )

    # Build DiGraph: nodes first (sorted), then edges (sorted).
    G = nx.DiGraph()
    for node_id in sorted_node_ids:
        G.add_node(node_id)
    for source, target in sorted_edges:
        G.add_edge(source, target)

    # Run spring_layout from scratch (no pre-set positions).
    unit_pos = nx.spring_layout(
        G,
        k=None,
        seed=seed,
        iterations=cfg.iterations,
    )

    # Scale unit coordinates to world meters; map networkx y -> our z.
    result: dict[NodeId, Vec2] = {}
    for node_id in sorted_node_ids:
        ux, uy = unit_pos[node_id]
        result[node_id] = (float(ux) * cfg.scale_m, float(uy) * cfg.scale_m)

    return result
```

### 6.2 — `map/layout_height.py` (crossing detection + height assignment — the bug lives here)

```python
"""Crossings detection and greedy height assignment.

Pure, deterministic functions for detecting which corridors (edges) cross in
2D and assigning height levels so crossing corridors get different heights.
"""
from __future__ import annotations

import math
import warnings
from itertools import combinations

from pydantic import BaseModel, ConfigDict

from map.raw_models import ConceptGraph, NodeId, Vec2


class HeightConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    socket_clearance_m: float = 2.0    # ignore intersections nearer than this to a node
    layer_warn: int = 7                 # warn if max_layer exceeds this
    layer_fail: int = 12                # raise if max_layer exceeds this
    base_y: float = 0.0                 # base height in meters
    delta_y: float = 3.0                # height per layer in meters


def _orientation(p, q, r):
    """Cross product of (q-p) and (r-q). >0 CCW, <0 CW, ==0 collinear."""
    return (q[0] - p[0]) * (r[1] - q[1]) - (q[1] - p[1]) * (r[0] - q[0])


def _on_segment(p, q, r):
    """True if point q lies on segment pr (collinear check)."""
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))


def _segments_intersect(p1, p2, p3, p4):
    """Return intersection point Vec2 or None."""
    o1 = _orientation(p1, p2, p3)
    o2 = _orientation(p1, p2, p4)
    o3 = _orientation(p3, p4, p1)
    o4 = _orientation(p3, p4, p2)

    if o1 != o2 and o3 != o4:  # general case: they cross
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy)

    # Collinear / touching cases: not a crossing
    return None


def detect_crossings(
    positions: dict[NodeId, Vec2],
    graph: ConceptGraph,
    cfg: "HeightConfig",
) -> list[tuple[str, str, Vec2]]:
    """
    Returns list of (corridor_id_A, corridor_id_B, intersection_point).
    corridor ids are edge ids from the graph.
    """
    edges = sorted(graph.edges, key=lambda e: e.id)
    crossings: list[tuple[str, str, Vec2]] = []

    for ea, eb in combinations(edges, 2):
        # Skip if they share an endpoint
        if ea.source == eb.source or ea.target == eb.target:
            continue
        if ea.source == eb.target or ea.target == eb.source:
            continue

        a1 = positions[ea.source]
        a2 = positions[ea.target]
        b1 = positions[eb.source]
        b2 = positions[eb.target]

        ipt = _segments_intersect(a1, a2, b1, b2)
        if ipt is None:
            continue

        # Skip intersections within socket_clearance_m of any node position.
        too_close = any(
            math.dist(ipt, pos) < cfg.socket_clearance_m
            for pos in positions.values()
        )
        if too_close:
            continue

        ida, idb = ea.id, eb.id
        if ida > idb:
            ida, idb = idb, ida
        crossings.append((ida, idb, ipt))

    crossings.sort(key=lambda c: (c[0], c[1]))
    return crossings


def assign_heights(
    crossings: list[tuple[str, str, Vec2]],
    graph: ConceptGraph,
    cfg: "HeightConfig",
) -> dict[str, int]:
    """
    Returns dict mapping corridor_id → height_level (int, 0-based).
    Greedy coloring of the crossing conflict graph.
    """
    # Build conflict adjacency.
    conflicts: dict[str, set[str]] = {e.id: set() for e in graph.edges}
    for a, b, _ in crossings:
        conflicts.setdefault(a, set()).add(b)
        conflicts.setdefault(b, set()).add(a)

    # Fixed processing order: weight DESC, source ASC, target ASC.
    ordered = sorted(
        graph.edges,
        key=lambda e: (-e.weight, e.source, e.target),
    )

    heights: dict[str, int] = {}
    for edge in ordered:
        used = {
            heights[nbr]
            for nbr in conflicts.get(edge.id, set())
            if nbr in heights
        }
        layer = 0
        while layer in used:
            layer += 1
        heights[edge.id] = layer

    max_layer = max(heights.values()) if heights else 0

    if max_layer >= cfg.layer_fail:
        raise ValueError(
            f"Height overflow: {max_layer} layers needed "
            f"(cap {cfg.layer_fail}). Re-seed or widen scale."
        )
    if max_layer > cfg.layer_warn:
        warnings.warn(f"Height layers needed: {max_layer} exceeds warn threshold {cfg.layer_warn}.")

    return heights
```

### 6.3 — `map/level_maker.py` (the integrator that calls the two modules above)

```python
from __future__ import annotations

import math
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from map.raw_models import (
    ConceptGraph, Floorplan, FloorRoom, Corridor, Crossing, Hex, NodeId, Vec2,
)
from map.layout_force import place_nodes, LayoutConfig
from map.layout_height import detect_crossings, assign_heights, HeightConfig


_DEV_PALETTE: dict[int, Hex] = {1: "#4F6D7A", 2: "#3FA796", 3: "#E6B800", 4: "#E8743B", 5: "#D81B60"}


class LevelMakerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layout: LayoutConfig = LayoutConfig()
    height: HeightConfig = HeightConfig()
    map_radius_base_m: float = 2.0
    map_radius_per_importance_m: float = 1.0
    corridor_width_m: float = 3.0
    palette_map_importance: dict[int, Hex] = {}


def build_floorplan(graph: ConceptGraph, seed: int, cfg: "LevelMakerConfig") -> Floorplan:
    positions = place_nodes(graph, seed, cfg.layout)                      # STEP 1 — POSITIONS
    crossings_raw = detect_crossings(positions, graph, cfg.height)        # STEP 2 — CROSSINGS
    heights = assign_heights(crossings_raw, graph, cfg.height)            # STEP 3 — HEIGHTS

    rooms: list[FloorRoom] = []                                           # STEP 4 — ROOMS
    for node in graph.nodes:
        importance = node.importance
        map_radius_m = cfg.map_radius_base_m + (importance - 1) * cfg.map_radius_per_importance_m
        map_color = cfg.palette_map_importance.get(importance, _DEV_PALETTE.get(importance, "#999999"))
        rooms.append(FloorRoom(room_id=node.id, map_xz=positions[node.id], importance=importance,
                               map_radius_m=map_radius_m, map_color=map_color, socket_y=0.0))

    crossings_by_corridor: dict[str, list[Vec2]] = {}
    for (corr_a, corr_b, at_xz) in crossings_raw:
        crossings_by_corridor.setdefault(corr_a, []).append(at_xz)
        crossings_by_corridor.setdefault(corr_b, []).append(at_xz)

    corridors: list[Corridor] = []                                       # STEP 5 — CORRIDORS
    for edge in graph.edges:
        corridor_id = edge.id
        src_pos = positions[edge.source]
        tgt_pos = positions[edge.target]
        height_level = heights[edge.id]
        if height_level == 0:
            path_xz: list[Vec2] = [src_pos, tgt_pos]
        else:
            pts = crossings_by_corridor.get(corridor_id, [])
            sorted_pts = sorted(pts, key=lambda p: (p[0]-src_pos[0])**2 + (p[1]-src_pos[1])**2)
            path_xz = [src_pos] + list(sorted_pts) + [tgt_pos]
        cruise_y = cfg.height.base_y + height_level * cfg.height.delta_y
        corridors.append(Corridor(corridor_id=corridor_id, source=edge.source, target=edge.target,
                                  height_level=height_level, width_m=cfg.corridor_width_m,
                                  path_xz=path_xz, cruise_y=cruise_y))

    crossings: list[Crossing] = []                                       # STEP 6 — CROSSINGS
    for i, (corr_a, corr_b, at_xz) in enumerate(crossings_raw):
        h_a = heights[corr_a]; h_b = heights[corr_b]
        if h_a > h_b:   over_corridor, under_corridor = corr_a, corr_b
        elif h_b > h_a: over_corridor, under_corridor = corr_b, corr_a
        else:           over_corridor, under_corridor = (corr_a, corr_b) if corr_a <= corr_b else (corr_b, corr_a)
        over_y = cfg.height.base_y + heights[over_corridor] * cfg.height.delta_y
        under_y = cfg.height.base_y + heights[under_corridor] * cfg.height.delta_y
        assert over_y > under_y
        crossings.append(Crossing(crossing_id=f"crossing_{i}", over_corridor=over_corridor,
                                  under_corridor=under_corridor, at_xz=at_xz, over_y=over_y, under_y=under_y))

    rooms.sort(key=lambda r: r.room_id)                                  # STEP 7 — EMIT
    corridors.sort(key=lambda c: c.corridor_id)
    return Floorplan(schema_version="1.0", level_id=graph.level_id, seed=seed,
                     rooms=rooms, corridors=corridors, crossings=crossings)
```

### 6.4 — The frozen data contracts (from `map/raw_models.py`) — DO NOT change these shapes

```python
NodeId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
LevelId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]
Hex  = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]

class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: NodeId; name: str; kind: str
    importance: int = Field(ge=1, le=5)
    pages: list[str]; summary: str; tags: list[str] = []

class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    source: NodeId; target: NodeId
    kind: str = "depends_on"; weight: float = 1.0; label: str = ""

class ConceptGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]; level_id: LevelId
    title: str; edition: str; seed: int
    nodes: list[Node]; edges: list[Edge]

class FloorRoom(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_id: NodeId; map_xz: Vec2; importance: int = Field(ge=1, le=5)
    map_radius_m: float; map_color: Hex; socket_y: float = 0.0

class Corridor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corridor_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    source: NodeId; target: NodeId
    height_level: int; cruise_y: float; path_xz: list[Vec2]; width_m: float

class Crossing(BaseModel):
    model_config = ConfigDict(extra="forbid")
    crossing_id: str; over_corridor: str; under_corridor: str
    at_xz: Vec2; over_y: float; under_y: float

class Floorplan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]; level_id: LevelId; seed: int
    rooms: list[FloorRoom]; corridors: list[Corridor]; crossings: list[Crossing]
```

You MAY add **new, defaulted** fields to the `*Config` classes (they are `extra="forbid"`, so defaults keep old callers working). You may NOT change `Floorplan/FloorRoom/Corridor/Crossing/ConceptGraph` shapes (the runtime + `load_pack` depend on them).

---

## §7 — THE TEST GAP (precise audit — what exists vs. what's missing)

**Existing tests you MUST keep green** (do not delete or weaken their intent):

- `tests/test_layout_force.py` (7): determinism (same inputs → identical dict), completeness (all ids once), finiteness + bounds (|x|,|z| < scale·1.5, finite), order-independence (shuffled input → identical output via canonicalization), different-seeds-differ, single-node-no-crash. **All on ≤4 hand-built nodes.**
- `tests/test_layout_height.py` (5): one hand-placed crossing at (0,0); collinear → zero crossings; three hand-placed mutual crossings → 3 layers {0,1,2}; synthetic layer-overflow raises `ValueError("Height overflow")`; socket-clearance filters a near-node crossing. **All use hand-placed integer-ish positions that cross cleanly.**
- `tests/test_level_maker.py` (5): 4-node "one crossing" floorplan (≥1 crossing, over_y>under_y); spine equality (room_ids == node_ids); determinism; 3-collinear → 0 crossings & all height 0; importance→radius. **Largest graph tested = 5 nodes.**

**Why the bug slipped through (the gap you must close):**
1. The crossing detector was **never fed near-parallel / nearly-collinear / floating-point-degenerate** segments, so its non-robustness was invisible.
2. **No test ever asserts the returned crossing point lies within both segments' bounding boxes** — so the "phantom far-away intersection" failure mode was untestable.
3. `place_nodes` is **never tested for layout quality at scale** (clustering / minimum separation) — only finiteness on ≤4 nodes.
4. `build_floorplan` is **never run on a real-size graph** with health assertions.

**New tests to add (general / generated — NO hardcoded counts):**
- A **robustness** unit test: construct near-parallel and nearly-collinear segment pairs (parametrized over several offsets/angles) and assert `_segments_intersect` / `detect_crossings` never returns a point outside both segments' bounding boxes (and treats true near-parallels as non-crossing).
- An **in-bounds invariant** test over generated graphs of *several* sizes N (e.g. a helper that builds a random-but-seeded N-node graph): assert **every** crossing's `at_xz` lies within the bounding box of all room positions (with a small epsilon). This is the assertion that would have caught (-22484, -10650).
- A **scale/health** test: over generated graphs of increasing N, assert the crossing count grows *reasonably* — express the bound as a function of edges/nodes (e.g. relative to corridor count), **not** a magic constant — and that height-layer count stays within the configured caps.
- Keep everything **deterministic & order-independent** (existing tests pin this).

DeepSeek will additionally run your fixed engine on Parent 7's real `concept_graph.json` and report the new crossing count + confirm all coords are in-bounds.

---

## §8 — HARD CONSTRAINTS (Part A)

1. **No hardcoded level sizes** anywhere in engine or tests. Scale with the graph.
2. **Frozen contracts**: `Floorplan/FloorRoom/Corridor/Crossing/ConceptGraph` shapes unchanged. New `*Config` fields must be additive + defaulted.
3. **All 285 existing tests stay green**, including the determinism/order-independence/overflow/socket-clearance behaviors.
4. **Pure & deterministic**: `place_nodes`, `detect_crossings`, `assign_heights`, `build_floorplan` take inputs → return outputs, no IO/network, same-seed-same-output. (The existing determinism tests enforce this.)
5. **Stack**: all-Python, Windows-first. `networkx` is already a dependency. Don't add heavy new deps without flagging to Nir first.
6. If you find you must touch a contract or a frozen format, **STOP and request that exact section** (§4.4 floorplan schema, etc.) and design with it; don't guess.

---

## §9 — PART B: THE 3D MAP-VIEWER UTILITY (detailed requirements)

**Goal.** A standalone Python utility (Windows-first, moderngl + pyglet — the project's existing render stack) that **loads a `floorplan.json` and renders it as a navigable 3D wireframe**, so a human can fly through and inspect the whole level. Same core later becomes the **in-game map mode** (press a key in the real game → this view of the level you're inside).

**Why 3D and not a flat 2D automap:** our corridors cross at different heights as **bridges/underpasses**; a flat map can't show over/under. So the viewer must show height.

**What it draws (from `floorplan.json` — request the schema via Second Canon §4.4 if you want it):**
- **Rooms**: a marker/ring at each `FloorRoom.map_xz` placed at `socket_y`, sized by `map_radius_m`, tinted by `map_color` (and/or by `importance`).
- **Corridors**: each `Corridor` as a wireframe line/tube following its `path_xz` at its `cruise_y` (height_level × delta_y), width ~ `width_m`.
- **Crossings**: render the over/under explicitly — the `over_corridor` at `over_y`, `under_corridor` at `under_y` — so bridges and underpasses are visually obvious.
- Optional niceties: a ground grid, height-layer color/opacity cue, room labels (request `concept_graph.json` for `name`s), an on-screen HUD of counts (rooms / corridors / crossings).

**Navigation (Nir's explicit ask):** a **free-fly camera** driven by **arrow keys + WASD** (and optionally mouse-look) — move forward/back/strafe, turn, rise/fall — so the user can get to and inspect *any* section of the map from any angle.

**Reuse, don't reinvent:** the project already has, in the runtime engine, a **Mode-A wireframe renderer** (`render_wire.py`) that draws the corridor graph as depth-tested white→grey line-quads, a **decoupled camera** (`camera.py`), a GL context helper (`gfx_context.py`), shader programs (`shaders.py`), and a semantic input layer with WASD (`input_actions.py`). **Ask Nir to have DeepSeek paste any of these verbatim** when you reach this part — design the viewer to share code with Mode A so it can graduate into the in-game map mode rather than being a throwaway.

**Constraints:** takes **any** floorplan (no hardcoded level); pure-presentation (never mutates the floorplan); window/GL code guarded so headless CI doesn't break (the project uses a `skip_if_no_gl` pattern — ask DeepSeek for `glguard.py`/`conftest.py` if useful).

---

## §10 — YOUR DELIVERABLE FORMAT

Because you implement directly and DeepSeek drops your files in, produce:
1. **Complete file contents** for each changed/new `.py` file, each in its own fenced code block, with the path as a header line (e.g. `# map/layout_height.py`). Full files, not diffs.
2. **The new test file(s)**, same way.
3. A short **CHANGELOG** (prose): what you changed in each module and *why*, and which existing tests you verified your change preserves.
4. If a step needs a file you don't have, **stop and request it** (per §2) rather than guessing its contents.

Do Part A as one deliverable; then Part B (you may request the render/camera/gl/input files first).

---

## §11 — ACCEPTANCE GATES

- **G1.** All 285 prior tests still green (zero regressions).
- **G2.** New robustness test green: `detect_crossings` never returns a point outside both segments' bounding boxes; near-parallel pairs are not reported as crossings.
- **G3.** New in-bounds invariant green on generated graphs of several sizes: every crossing `at_xz` lies within the room-position bounding box (+ε).
- **G4.** New scale/health test green: crossing count and height-layer count stay within graph-relative bounds as N grows (no magic numbers).
- **G5.** DeepSeek re-runs the fixed engine on Parent 7's real `concept_graph.json` → a **sane** crossing count (down from 191) and **all** coords in-bounds. DeepSeek reports the numbers.
- **G6.** Map viewer runs on a `floorplan.json` and lets a human fly around with arrows + WASD and see bridges/underpasses. (Nir eyeballs it.)

---

## §12 — SEQUENCING (so you don't worry about it)

Parent 7's `concept_graph.json` is **valid DATA** and is NOT your concern — **do not modify it.** You are fixing the **machine** (the layout engine). After you deliver, DeepSeek re-runs the same data through your fixed engine and Nir inspects the result with your map viewer. If — and only if — the map then still looks too tangled *with a correct engine*, a future parent may simplify Parent 7's graph. That is not pre-decided and not your job now.

---

**That's the mission, Parent 8: make the map-maker robust and scale-free, prove it with general tests, and give Nir 3D eyes on the level. Ask for any file you need, one or two at a time, verbatim. Go.** 🗝️
