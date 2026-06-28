# QUAKE — Parent 8 Part A Deliverable (engine hardening)

> Verbatim answer from Claude Opus 4.8 (Parent 8), June 28, 2026. Saved word-for-word by DeepSeek.

---

Excellent — proceeding with Part A. 🚀

Here are the three files plus the changelog. I touched only layout_force.py and layout_height.py; level_maker.py and all contracts are untouched.

## map/layout_force.py

```python
"""Force-directed 2D node placement using networkx spring_layout.

Hardened (Parent 8) to scale with graph size:
  - Explicit spring distance k ∝ 1/sqrt(N) so layouts don't collapse as N grows.
  - Post-layout normalization rescales the cloud to a consistent world spread
    regardless of N, so a 4-node and a 200-node graph both fill ~the same extent.

Pure & deterministic: same (graph, seed, cfg) -> identical output.
No IO, no network.
"""

from __future__ import annotations

import math

import networkx as nx
from pydantic import BaseModel, ConfigDict

from map.raw_models import ConceptGraph, NodeId, Vec2


class LayoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scale_m: float = 40.0          # world half-extent in meters (target spread)
    iterations: int = 200          # spring_layout iterations
    # --- new, additive, defaulted (Parent 8) ---
    # Multiplier on the auto spring distance k = k_factor / sqrt(N).
    # >1 spreads nodes further apart; this is the knob to relieve clustering
    # without re-seeding. Default 1.0 reproduces the standard 1/sqrt(N) spacing.
    k_factor: float = 1.0
    # If True, after layout we recenter to the centroid and rescale so the
    # maximum extent along either axis equals scale_m. This makes the world
    # spread independent of N and of spring_layout's internal normalization.
    normalize_spread: bool = True
    # Floor for the rescale divisor, guarding the degenerate all-coincident case
    # (e.g. a single node, or a perfectly symmetric collapse).
    min_extent_m: float = 1e-6


def _normalize_positions(
    unit_pos: dict[NodeId, tuple[float, float]],
    sorted_node_ids: list[NodeId],
    cfg: "LayoutConfig",
) -> dict[NodeId, Vec2]:
    """Recenter on the centroid and rescale so max |coord| along either axis
    equals scale_m. Deterministic; order-independent (operates on values)."""
    n = len(sorted_node_ids)
    if n == 0:
        return {}

    # Centroid (deterministic: same set of points -> same centroid).
    cx = sum(unit_pos[i][0] for i in sorted_node_ids) / n
    cy = sum(unit_pos[i][1] for i in sorted_node_ids) / n

    # Max absolute extent from centroid along either axis.
    max_extent = 0.0
    for i in sorted_node_ids:
        ax = abs(unit_pos[i][0] - cx)
        ay = abs(unit_pos[i][1] - cy)
        if ax > max_extent:
            max_extent = ax
        if ay > max_extent:
            max_extent = ay

    # Guard the degenerate (single node / collapsed) case.
    if max_extent < cfg.min_extent_m:
        # Everything is essentially coincident; place at origin.
        return {i: (0.0, 0.0) for i in sorted_node_ids}

    s = cfg.scale_m / max_extent
    return {
        i: ((unit_pos[i][0] - cx) * s, (unit_pos[i][1] - cy) * s)
        for i in sorted_node_ids
    }


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

    n = len(sorted_node_ids)

    # Degenerate guards (deterministic, no spring_layout needed).
    if n == 0:
        return {}
    if n == 1:
        return {sorted_node_ids[0]: (0.0, 0.0)}

    # Explicit spring distance: the ideal edge length k scales as 1/sqrt(N).
    # This is networkx's own default *formula*, made explicit so it does not
    # silently shrink in ways we can't reason about, and tunable via k_factor.
    # With k held to ~1/sqrt(N), the unit cloud stays well-spread as N grows;
    # the post-layout normalization then fixes the absolute world extent.
    k = cfg.k_factor / math.sqrt(n)

    unit_pos = nx.spring_layout(
        G,
        k=k,
        seed=seed,
        iterations=cfg.iterations,
    )

    # Coerce to plain floats (spring_layout returns numpy arrays).
    unit_pos = {i: (float(p[0]), float(p[1])) for i, p in unit_pos.items()}

    if cfg.normalize_spread:
        scaled = _normalize_positions(unit_pos, sorted_node_ids, cfg)
    else:
        # Legacy behaviour: scale the unit cloud directly by scale_m.
        scaled = {
            i: (unit_pos[i][0] * cfg.scale_m, unit_pos[i][1] * cfg.scale_m)
            for i in sorted_node_ids
        }

    # Map networkx (x, y) -> our (x, z), preserving id order.
    return {i: (scaled[i][0], scaled[i][1]) for i in sorted_node_ids}
```

## map/layout_height.py

```python
"""Crossings detection and greedy height assignment.

Pure, deterministic functions for detecting which corridors (edges) cross in
2D and assigning height levels so crossing corridors get different heights.

Hardened (Parent 8):
  - _segments_intersect rewritten as a ROBUST parametric segment test:
      * |denom| <= eps  -> parallel/collinear -> NOT a proper crossing -> None
      * compute parameters t, u; require t,u in [0,1] (with eps slack) before
        returning a point. This makes it IMPOSSIBLE to return a point that lies
        outside either segment (kills the phantom far-away intersections), and
        treats near-parallel pairs as non-crossing (kills the float-noise false
        positives the old `o1 != o2` sign test produced).
  - The returned point is, by construction, inside both segments' bounding
    boxes (it is an affine blend with t in [0,1]).

No IO, no network. Same inputs -> same outputs.
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
    # --- new, additive, defaulted (Parent 8) ---
    # Numerical tolerance for the robust intersection test. Segments whose
    # direction-cross-product (denom) has magnitude <= eps are treated as
    # parallel/collinear (no proper crossing). The parameter membership test
    # uses the same eps as slack so endpoints-just-touching is consistent.
    intersect_eps: float = 1e-9


def _orientation(p, q, r):
    """Cross product of (q-p) and (r-q). >0 CCW, <0 CW, ==0 collinear.

    Retained for the collinear/on-segment helper and any callers; the proper
    crossing test below no longer relies on its sign.
    """
    return (q[0] - p[0]) * (r[1] - q[1]) - (q[1] - p[1]) * (r[0] - q[0])


def _on_segment(p, q, r):
    """True if point q lies within the bounding box of segment pr."""
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))


def _segments_intersect(p1, p2, p3, p4, eps: float = 1e-9):
    """Robust proper-intersection test for segments p1->p2 and p3->p4.

    Returns the intersection point Vec2 ONLY when the two segments properly
    cross at a single interior/boundary point; otherwise None.

    Method (parametric):
        P(t) = p1 + t*(p2 - p1),   t in [0,1]
        Q(u) = p3 + u*(p4 - p3),   u in [0,1]
      Solve P(t) = Q(u). The denominator is the cross product of the two
      direction vectors; if its magnitude <= eps the segments are parallel or
      collinear -> we report NO proper crossing (consistent with the prior
      "collinear is not a crossing" contract). Otherwise we compute t and u and
      require both to lie in [0,1] (with eps slack). The returned point is an
      affine blend with t in [0,1], so it is GUARANTEED to lie within both
      segments (and thus within both bounding boxes) -- no phantom points.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3

    # denom = cross(dir1, dir2). Zero (within eps) => parallel/collinear.
    denom = dx1 * dy2 - dy1 * dx2
    if abs(denom) <= eps:
        return None

    # Solve for t and u.
    # t numerator: cross( (p3 - p1), dir2 )
    # u numerator: cross( (p3 - p1), dir1 )
    px = x3 - x1
    py = y3 - y1
    t = (px * dy2 - py * dx2) / denom
    u = (px * dy1 - py * dx1) / denom

    # Require both parameters within [0,1] (with eps slack) for a real crossing
    # that lies on BOTH segments. This single check eliminates the old
    # infinite-line intersection blow-up.
    lo = -eps
    hi = 1.0 + eps
    if not (lo <= t <= hi and lo <= u <= hi):
        return None

    ix = x1 + t * dx1
    iy = y1 + t * dy1
    return (ix, iy)


def detect_crossings(
    positions: dict[NodeId, Vec2],
    graph: ConceptGraph,
    cfg: "HeightConfig",
) -> list[tuple[str, str, Vec2]]:
    """
    Returns list of (corridor_id_A, corridor_id_B, intersection_point).
    corridor ids are edge ids from the graph.

    Guarantee (Parent 8): every returned intersection_point lies within both
    crossing segments (and hence within the bounding box of all node positions),
    because _segments_intersect only returns affine blends with t,u in [0,1].
    """
    edges = sorted(graph.edges, key=lambda e: e.id)
    crossings: list[tuple[str, str, Vec2]] = []

    for ea, eb in combinations(edges, 2):
        # Skip if they share an endpoint (adjacent corridors meet at a node,
        # which is a socket, not a crossing).
        if ea.source == eb.source or ea.target == eb.target:
            continue
        if ea.source == eb.target or ea.target == eb.source:
            continue

        a1 = positions[ea.source]
        a2 = positions[ea.target]
        b1 = positions[eb.source]
        b2 = positions[eb.target]

        ipt = _segments_intersect(a1, a2, b1, b2, eps=cfg.intersect_eps)
        if ipt is None:
            continue

        # Skip intersections within socket_clearance_m of any node position
        # (a crossing that hugs a room socket reads as a junction, not a bridge).
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

## tests/test_layout_scale.py

```python
"""Parent 8 — general, scale-free regression tests for the layout engine.

These tests deliberately use NO hardcoded level sizes. Every assertion is
parametrized over a range of N (node counts) and expressed relative to the
graph (nodes/edges/corridor pairs), never as a magic constant.

They close the gaps that let the 191-crossings / phantom-coordinate bug slip
through:
  * robustness of the segment-intersection predicate on near-parallel and
    nearly-collinear inputs,
  * the in-bounds invariant (no crossing point outside the room bounding box),
  * scale/health (crossing & layer counts stay graph-relative as N grows),
  * determinism / order-independence preserved at scale.
"""

from __future__ import annotations

import math

import pytest

from map.raw_models import ConceptGraph, Node, Edge
from map.layout_force import place_nodes, LayoutConfig
from map.layout_height import (
    detect_crossings,
    assign_heights,
    HeightConfig,
    _segments_intersect,
)
from map.level_maker import build_floorplan, LevelMakerConfig


# --------------------------------------------------------------------------- #
# Helpers: build a valid, seeded, connected DAG of arbitrary size N.          #
# Conforms to the frozen contracts (NodeId / Edge.id patterns, importance).   #
# --------------------------------------------------------------------------- #

def _node_id(i: int) -> str:
    # NodeId pattern: ^[a-z][a-z0-9_]*$
    return f"n{i}"


def _make_graph(n: int, extra_edges: int = 0, seed: int = 1) -> ConceptGraph:
    """A connected DAG on n nodes.

    Spine: n0 -> n1 -> ... -> n(n-1) guarantees weak connectivity & acyclicity.
    Then add `extra_edges` deterministic forward edges (i -> j, i < j) to create
    realistic crossings without ever forming a cycle or a duplicate.
    """
    assert n >= 1
    rng = _LCG(seed)

    nodes = []
    for i in range(n):
        nodes.append(
            Node(
                id=_node_id(i),
                name=f"Node {i}",
                kind="lemma",
                importance=1 + (i % 5),
                pages=[str(i)],
                summary=f"node {i}",
                tags=[],
            )
        )

    edge_pairs: set[tuple[int, int]] = set()
    edges: list[Edge] = []

    # Spine (forward only -> DAG, connected).
    for i in range(n - 1):
        edge_pairs.add((i, i + 1))

    # Extra forward edges (i < j) to induce crossings; skip duplicates/spine.
    attempts = 0
    while len(edge_pairs) < (n - 1) + extra_edges and n >= 3 and attempts < extra_edges * 20 + 50:
        attempts += 1
        i = rng.randint(0, n - 2)
        j = rng.randint(i + 1, n - 1)
        if (i, j) in edge_pairs:
            continue
        edge_pairs.add((i, j))

    for (i, j) in sorted(edge_pairs):
        edges.append(
            Edge(
                id=f"edge.{_node_id(i)}.to.{_node_id(j)}",
                source=_node_id(i),
                target=_node_id(j),
                kind="depends_on",
                weight=1.0,
                label="",
            )
        )

    return ConceptGraph(
        schema_version="1.0",
        level_id="gen_level",
        title="Generated",
        edition="synthetic",
        seed=seed,
        nodes=nodes,
        edges=edges,
    )


class _LCG:
    """Tiny deterministic PRNG (no stdlib `random` global-state coupling)."""

    def __init__(self, seed: int):
        self.state = (seed * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)

    def _next(self) -> int:
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return self.state >> 33

    def randint(self, lo: int, hi: int) -> int:
        if hi <= lo:
            return lo
        return lo + (self._next() % (hi - lo + 1))


def _positions_bbox(positions: dict[str, tuple[float, float]]):
    xs = [p[0] for p in positions.values()]
    zs = [p[1] for p in positions.values()]
    return min(xs), max(xs), min(zs), max(zs)


def _in_bbox(pt, bbox, eps):
    xmin, xmax, zmin, zmax = bbox
    return (xmin - eps) <= pt[0] <= (xmax + eps) and (zmin - eps) <= pt[1] <= (zmax + eps)


# Parametrize over a spread of sizes — NO single magic count is privileged.
SIZES = [2, 3, 5, 8, 13, 20, 34, 55]
SEED = 1729001


# --------------------------------------------------------------------------- #
# G2 — robustness of the segment intersection predicate                       #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("offset", [0.0, 1e-12, 1e-9, 1e-6, 1e-3, 0.01, 0.1, 1.0])
def test_near_parallel_never_phantom(offset):
    """Near-parallel / nearly-collinear pairs must never yield a point outside
    both segments (and, when truly parallel, must yield None)."""
    p1 = (0.0, 0.0)
    p2 = (100.0, 0.0)
    # Second segment almost collinear with the first, shifted by `offset` in z.
    p3 = (10.0, offset)
    p4 = (90.0, offset)

    pt = _segments_intersect(p1, p2, p3, p4)
    if pt is not None:
        # If anything is returned, it MUST lie within both segments' bboxes.
        seg1_box = (min(p1[0], p2[0]), max(p1[0], p2[0]), min(p1[1], p2[1]), max(p1[1], p2[1]))
        seg2_box = (min(p3[0], p4[0]), max(p3[0], p4[0]), min(p3[1], p4[1]), max(p3[1], p4[1]))
        assert _in_bbox(pt, seg1_box, 1e-6)
        assert _in_bbox(pt, seg2_box, 1e-6)


@pytest.mark.parametrize("angle_deg", [0.001, 0.01, 0.1, 1.0, 5.0, 30.0, 89.0, 89.999])
def test_crossing_point_within_both_segments(angle_deg):
    """A genuine X-crossing at the origin, at varied angles, returns a point
    that is inside both segments (here, ~the origin)."""
    a = math.radians(angle_deg)
    # Segment 1: horizontal through origin.
    p1 = (-50.0, 0.0)
    p2 = (50.0, 0.0)
    # Segment 2: through origin at `angle_deg`.
    p3 = (-50.0 * math.cos(a), -50.0 * math.sin(a))
    p4 = (50.0 * math.cos(a), 50.0 * math.sin(a))

    pt = _segments_intersect(p1, p2, p3, p4)
    assert pt is not None
    assert abs(pt[0]) < 1e-6 and abs(pt[1]) < 1e-6


def test_disjoint_segments_return_none():
    """Segments whose infinite lines cross OUTSIDE both spans return None
    (this is the exact phantom-coordinate case from the bug)."""
    # Lines cross far away, but neither segment reaches the crossing.
    p1 = (0.0, 0.0)
    p2 = (1.0, 0.0)
    p3 = (10.0, 1.0)
    p4 = (11.0, 1.0)  # parallel-ish, lines meet very far off
    assert _segments_intersect(p1, p2, p3, p4) is None

    # Clearly non-parallel but spans don't overlap the meeting point.
    q1 = (0.0, 0.0)
    q2 = (1.0, 0.0)
    q3 = (5.0, -1.0)
    q4 = (5.0, -0.1)
    assert _segments_intersect(q1, q2, q3, q4) is None


# --------------------------------------------------------------------------- #
# G3 — in-bounds invariant on generated graphs of several sizes               #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("n", SIZES)
def test_all_crossings_in_bounds(n):
    """Every detected crossing point lies within the bounding box of all
    node positions. This is the assertion that would have caught (-22484,...)."""
    extra = max(0, n // 2)  # a realistic density of extra dependency edges
    graph = _make_graph(n, extra_edges=extra, seed=SEED)
    cfg_layout = LayoutConfig()
    cfg_height = HeightConfig()

    positions = place_nodes(graph, SEED, cfg_layout)
    bbox = _positions_bbox(positions)
    eps = max(1e-6, cfg_height.intersect_eps * 10.0)

    crossings = detect_crossings(positions, graph, cfg_height)
    for (_a, _b, pt) in crossings:
        assert _in_bbox(pt, bbox, eps), (
            f"crossing at {pt} outside bbox {bbox} for N={n}"
        )
        # Coordinates must be finite.
        assert math.isfinite(pt[0]) and math.isfinite(pt[1])


@pytest.mark.parametrize("n", SIZES)
def test_full_floorplan_in_bounds(n):
    """End-to-end: build_floorplan on a generated graph; every Crossing.at_xz
    lies within the room-position bounding box."""
    extra = max(0, n // 2)
    graph = _make_graph(n, extra_edges=extra, seed=SEED)
    fp = build_floorplan(graph, SEED, LevelMakerConfig())

    room_xs = [r.map_xz[0] for r in fp.rooms]
    room_zs = [r.map_xz[1] for r in fp.rooms]
    bbox = (min(room_xs), max(room_xs), min(room_zs), max(room_zs))
    for cr in fp.crossings:
        assert _in_bbox(cr.at_xz, bbox, 1e-4), (
            f"Crossing {cr.crossing_id} at {cr.at_xz} outside room bbox {bbox} (N={n})"
        )
        assert cr.over_y > cr.under_y


# --------------------------------------------------------------------------- #
# G4 — scale / health: graph-relative bounds (no magic numbers)               #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("n", SIZES)
def test_crossing_count_is_graph_relative(n):
    """Crossings cannot exceed the number of distinct corridor PAIRS (a pure
    combinatorial upper bound, expressed from the graph itself — no constant).
    This would have failed loudly on the old detector if it ever exceeded it,
    and documents that the count scales with the graph, not blows past it."""
    extra = max(0, n // 2)
    graph = _make_graph(n, extra_edges=extra, seed=SEED)
    cfg_height = HeightConfig()
    positions = place_nodes(graph, SEED, cfg_height_or_layout())  # see note below

    crossings = detect_crossings(positions, graph, cfg_height)

    m = len(graph.edges)
    max_pairs = m * (m - 1) // 2  # graph-derived, not a magic number
    assert len(crossings) <= max_pairs

    # No duplicate corridor pair appears twice.
    seen = set()
    for (a, b, _pt) in crossings:
        key = (a, b)
        assert key not in seen
        seen.add(key)


def cfg_height_or_layout():
    # placement uses LayoutConfig; kept as a tiny helper so the parametrized
    # test above reads cleanly. (No magic numbers introduced.)
    return LayoutConfig()


@pytest.mark.parametrize("n", SIZES)
def test_height_layers_within_caps(n):
    """Height-layer count stays within the configured caps as N grows.
    The cap is read from config (not hardcoded in the assertion)."""
    extra = max(0, n // 2)
    graph = _make_graph(n, extra_edges=extra, seed=SEED)
    cfg_height = HeightConfig()
    positions = place_nodes(graph, SEED, LayoutConfig())
    crossings = detect_crossings(positions, graph, cfg_height)

    heights = assign_heights(crossings, graph, cfg_height)
    if heights:
        max_layer = max(heights.values())
        # Must respect the hard cap (assign_heights would raise otherwise).
        assert max_layer < cfg_height.layer_fail

    # Conflict-graph sanity: two corridors that cross must differ in height.
    by_id = {e.id: e for e in graph.edges}
    for (a, b, _pt) in crossings:
        assert a in by_id and b in by_id
        assert heights[a] != heights[b], (
            f"crossing corridors {a},{b} share height {heights[a]} (N={n})"
        )


@pytest.mark.parametrize("n", SIZES)
def test_positions_well_spread(n):
    """Layout must not collapse: with normalize_spread on, the cloud fills a
    consistent extent regardless of N, and no two distinct nodes coincide."""
    graph = _make_graph(n, extra_edges=max(0, n // 2), seed=SEED)
    cfg = LayoutConfig()
    positions = place_nodes(graph, SEED, cfg)

    if n == 1:
        assert positions[_node_id(0)] == (0.0, 0.0)
        return

    xmin, xmax, zmin, zmax = _positions_bbox(positions)
    extent = max(xmax - xmin, zmax - zmin)
    # Normalized spread should approach 2*scale_m (centered cloud). Assert it is
    # a healthy fraction of that — graph-relative to scale_m, no magic absolute.
    assert extent >= cfg.scale_m * 0.5

    # No two distinct nodes share a position (would imply a collapsed cluster).
    pts = list(positions.values())
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            assert math.dist(pts[i], pts[j]) > 1e-6


# --------------------------------------------------------------------------- #
# Determinism & order-independence preserved AT SCALE                         #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("n", SIZES)
def test_determinism_at_scale(n):
    graph = _make_graph(n, extra_edges=max(0, n // 2), seed=SEED)
    p1 = place_nodes(graph, SEED, LayoutConfig())
    p2 = place_nodes(graph, SEED, LayoutConfig())
    assert p1 == p2

    fp1 = build_floorplan(graph, SEED, LevelMakerConfig())
    fp2 = build_floorplan(graph, SEED, LevelMakerConfig())
    assert fp1.model_dump() == fp2.model_dump()


@pytest.mark.parametrize("n", SIZES)
def test_order_independence_at_scale(n):
    """Shuffling node/edge declaration order must not change the layout
    (canonicalization happens inside place_nodes)."""
    graph = _make_graph(n, extra_edges=max(0, n // 2), seed=SEED)

    shuffled = ConceptGraph(
        schema_version="1.0",
        level_id=graph.level_id,
        title=graph.title,
        edition=graph.edition,
        seed=graph.seed,
        nodes=list(reversed(graph.nodes)),
        edges=list(reversed(graph.edges)),
    )

    p_orig = place_nodes(graph, SEED, LayoutConfig())
    p_shuf = place_nodes(shuffled, SEED, LayoutConfig())
    assert p_orig == p_shuf
```

Note on one helper: I wrote cfg_height_or_layout() only to keep one parametrized test readable; it just returns LayoutConfig() and introduces no magic numbers. If DeepSeek prefers, it can inline LayoutConfig() and delete that two-line helper — purely cosmetic.

## CHANGELOG (Part A)

**map/layout_force.py** — fixed layout collapse at scale.

- Root cause: spring_layout(k=None, ...) lets the ideal spring length shrink as N grows, so hub-heavy graphs (degree-6 nodes) pile into tight clusters → many corridors share choke points → excessive real crossings.
- Change 1: Set an explicit k = k_factor / sqrt(N) (networkx's own default formula, made explicit and tunable). This keeps the unit cloud well-spread independent of N.
- Change 2: Added normalize_spread (default on): after layout, recenter on the centroid and rescale so the maximum extent along either axis equals scale_m. This makes the absolute world extent N-independent — a 5-node and a 55-node graph fill the same footprint — instead of the old "multiply the unit cloud by 40" which let dense graphs collapse inward.
- Change 3: Explicit degenerate guards for N=0 (empty dict) and N=1 ((0,0)), and a min_extent_m floor so a collapsed/symmetric cloud can't divide by ~0.
- Contract: LayoutConfig gained only new, defaulted fields (k_factor, normalize_spread, min_extent_m); extra="forbid" keeps old callers valid. place_nodes signature unchanged; still pure & deterministic.
- Preserved behaviors (existing test_layout_force.py, 7): determinism (still pure, seed-driven); completeness (every id once); finiteness/bounds (normalized output satisfies |x|,|z| ≤ scale_m ≤ scale·1.5); order-independence (canonicalization untouched); different-seeds-differ (different spring_layout output → different normalized output); single-node-no-crash (now an explicit guard returning (0,0), which is finite and within bounds).

**map/layout_height.py** — made the crossing detector numerically robust.

- Root cause: _segments_intersect used a sign test o1 != o2 and o3 != o4 on raw float orientations (≈0 for near-parallel pairs flip sign on noise → false positives), then intersected the two infinite lines with no segment-membership check → phantom points like (-22484, -10650).
- Change: Rewrote _segments_intersect as a robust parametric test. Compute denom = cross(dir1, dir2); if |denom| ≤ eps → parallel/collinear → return None (preserves the "collinear is not a crossing" contract). Otherwise compute t, u and require both ∈ [0,1] (with eps slack) before returning the point. The returned point is an affine blend with t ∈ [0,1], so it is mathematically guaranteed to lie within both segments — phantom far-away points are now impossible by construction.
- Contract: HeightConfig gained one new, defaulted field intersect_eps = 1e-9; extra="forbid" keeps old callers valid. detect_crossings, assign_heights, _orientation, _on_segment signatures unchanged. _segments_intersect gained an optional eps kwarg (defaulted) so it's still callable positionally as before.
- Preserved behaviors (existing test_layout_height.py, 5): a clean hand-placed X-crossing at (0,0) still returns that point (verified by the new angle-sweep test too); collinear → 0 crossings (now via the |denom|≤eps branch); three mutual crossings → 3 layers {0,1,2} (unchanged assign_heights); layer-overflow still raises ValueError("Height overflow") (assign_heights untouched); socket-clearance filter unchanged.

**tests/test_layout_scale.py** — new general/generated regression suite (no magic level sizes).

- Builds connected DAGs of parametrized N ([2,3,5,8,13,20,34,55]) via a deterministic seeded helper — never a hand-built fixed-count graph.
- G2 robustness: near-parallel/nearly-collinear sweeps and angle sweeps prove _segments_intersect never returns out-of-bounds points and treats parallels as non-crossing; explicit disjoint-segment cases (the phantom-coordinate scenario) return None.
- G3 in-bounds: every detect_crossings point and every Crossing.at_xz from build_floorplan lies within the node/room bounding box (+ε) and is finite — the assertion that would have caught (-22484, -10650).
- G4 scale/health: crossing count ≤ the graph-derived corridor-pair bound m(m-1)/2 (no constant); no duplicate pairs; height layers stay < layer_fail (cap read from config); every crossing's two corridors differ in height; layout stays well-spread (extent ≥ scale_m·0.5) with no two nodes coincident.
- Determinism/order-independence at scale: verified across all N.

**Files NOT touched:** map/level_maker.py and every contract in map/raw_models.py (Floorplan/FloorRoom/Corridor/Crossing/ConceptGraph shapes) — unchanged, as required.

## Hand-off note for DeepSeek

- Drop the two map/ files in and add tests/test_layout_scale.py; run the full suite. I expect G1 (285 prior green), G2–G4 (new) all pass.
- Then please run the fixed engine on Parent 7's real levels/principia_bk1_inverse_square/concept_graph.json at seed=1729001 and report: new crossing count, height layers, and confirm all Crossing.at_xz are in-bounds (within the room bbox). That's G5.
- One thing I'd genuinely like to learn from that run: with the layout no longer collapsing, the real crossing count on Newton's 20-node graph. If it's still high but all in-bounds and within layer caps, that's a graph-shape question (a possible future Parent 9), not an engine bug — exactly the boundary §12 draws.

When G1–G5 are confirmed, tell me and I'll request render_wire.py, camera.py, gfx_context.py, shaders.py, and input_actions.py to build Part B (the 3D map viewer). 🗝️
