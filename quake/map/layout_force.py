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
