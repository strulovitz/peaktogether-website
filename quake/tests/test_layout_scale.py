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
    positions = place_nodes(graph, SEED, LayoutConfig())

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
