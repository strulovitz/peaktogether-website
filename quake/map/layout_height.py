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
