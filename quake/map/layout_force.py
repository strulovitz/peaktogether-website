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
