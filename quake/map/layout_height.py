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
