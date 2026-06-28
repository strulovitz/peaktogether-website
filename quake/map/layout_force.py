"""Hierarchical force-directed 2D node placement.

HARDENED (Parent 8) to scale with graph size:
  - Explicit spring distance k ∝ 1/sqrt(N) so layouts don't collapse as N grows.
  - Post-layout normalization rescales the cloud to a consistent world spread.

HIERARCHICAL (Nir's "solar-system" design, June 28, 2026):
  - Phase 1: place "planet" nodes (high importance + degree). They interact.
  - Phase 2: freeze planets. Add "asteroid" nodes one at a time — each pulled
    by springs to its already-placed neighbors only. Asteroids don't pull back.
  - Because planets are frozen and spread out, edges from different asteroids
    to overlapping planet-subsets naturally criss-cross → guaranteed crossings.

Pure & deterministic: same (graph, seed, cfg) -> identical output.  No IO.
"""

from __future__ import annotations

import math
import random

import networkx as nx
from pydantic import BaseModel, ConfigDict

from map.raw_models import ConceptGraph, NodeId, Vec2


class LayoutConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scale_m: float = 40.0          # world half-extent in meters (target spread)
    iterations: int = 200          # spring_layout iterations
    # --- Parent 8 ---
    k_factor: float = 1.0          # multiplier on auto spring distance k = k_factor / sqrt(N)
    normalize_spread: bool = True  # recenter to centroid + rescale to scale_m
    min_extent_m: float = 1e-6     # floor for rescale divisor (degenerate guard)
    # --- Hierarchical layout (June 28, 2026) ---
    planet_importance: int = 4     # nodes with importance >= this are planets
    planet_degree: int = 3         # nodes with undirected degree >= this are planets


def _compute_degrees(graph: ConceptGraph) -> dict[NodeId, int]:
    """Undirected degree for each node (count of incident edges)."""
    deg: dict[NodeId, int] = {n.id: 0 for n in graph.nodes}
    for e in graph.edges:
        deg[e.source] += 1
        deg[e.target] += 1
    return deg


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

    cx = sum(unit_pos[i][0] for i in sorted_node_ids) / n
    cy = sum(unit_pos[i][1] for i in sorted_node_ids) / n

    max_extent = 0.0
    for i in sorted_node_ids:
        ax = abs(unit_pos[i][0] - cx)
        ay = abs(unit_pos[i][1] - cy)
        if ax > max_extent:
            max_extent = ax
        if ay > max_extent:
            max_extent = ay

    if max_extent < cfg.min_extent_m:
        return {i: (0.0, 0.0) for i in sorted_node_ids}

    s = cfg.scale_m / max_extent
    return {
        i: ((unit_pos[i][0] - cx) * s, (unit_pos[i][1] - cy) * s)
        for i in sorted_node_ids
    }


def place_nodes(graph: ConceptGraph, seed: int, cfg: "LayoutConfig") -> dict[NodeId, Vec2]:
    """Hierarchical force-directed layout.

    Phase 1: place planet nodes (importance >= planet_importance OR
    degree >= planet_degree) — they interact with each other via spring_layout.

    Phase 2: freeze planets. Add asteroid nodes one at a time, sorted by
    connectedness to already-placed nodes. Each asteroid is pulled by springs
    to its placed neighbors only — neighbors are FIXED, asteroid moves alone.

    Returns {node_id: (x, z)} in world meters.  Deterministic.
    """
    sorted_node_ids = sorted(n.id for n in graph.nodes)
    sorted_edges = sorted(
        ((e.source, e.target) for e in graph.edges),
        key=lambda st: (st[0], st[1]),
    )

    n = len(sorted_node_ids)
    if n == 0:
        return {}
    if n == 1:
        return {sorted_node_ids[0]: (0.0, 0.0)}

    # --- classify planets vs asteroids ---
    degrees = _compute_degrees(graph)
    node_importance = {n.id: n.importance for n in graph.nodes}

    planet_ids = sorted(
        nid for nid in sorted_node_ids
        if node_importance[nid] >= cfg.planet_importance
        or degrees[nid] >= cfg.planet_degree
    )
    asteroid_ids = sorted(nid for nid in sorted_node_ids if nid not in planet_ids)

    # Edge case: no planets → promote highest-degree node to planet.
    if not planet_ids:
        best = max(sorted_node_ids, key=lambda nid: (degrees[nid], nid))
        planet_ids = [best]
        asteroid_ids = [nid for nid in asteroid_ids if nid != best]

    # Edge case: no asteroids → fall back to simultaneous layout (same as old).
    if not asteroid_ids:
        return _place_all_simultaneous(
            sorted_node_ids, sorted_edges, n, seed, cfg
        )

    # Build adjacency lookup
    neighbors: dict[NodeId, set[NodeId]] = {nid: set() for nid in sorted_node_ids}
    for s, t in sorted_edges:
        neighbors[s].add(t)
        neighbors[t].add(s)

    # --- Phase 1: place planets ---
    all_pos: dict[NodeId, tuple[float, float]] = _place_planet_subgraph(
        planet_ids, sorted_edges, seed, cfg
    )

    # --- Phase 2: place asteroids sequentially ---
    # Sort by connectedness to already-placed nodes (planets), then by node_id.
    def _connectedness(nid: str) -> int:
        return len(neighbors[nid] & set(all_pos.keys()))

    asteroid_order = sorted(
        asteroid_ids,
        key=lambda nid: (-_connectedness(nid), nid),
    )

    for nid in asteroid_order:
        placed_neighbors = [nb for nb in neighbors[nid] if nb in all_pos]

        if not placed_neighbors:
            all_pos[nid] = (0.0, 0.0)
            continue

        if len(placed_neighbors) == 1:
            rng = random.Random(seed + sorted_node_ids.index(nid))
            angle = rng.uniform(0, 2 * math.pi)
            offset = cfg.scale_m * 0.04
            p = all_pos[placed_neighbors[0]]
            all_pos[nid] = (
                p[0] + offset * math.cos(angle),
                p[1] + offset * math.sin(angle),
            )
            continue

        # 2+ placed neighbors: spring_layout with neighbors fixed.
        G_local = nx.Graph()
        G_local.add_node(nid)
        init_pos: dict[str, tuple[float, float]] = {nid: (0.0, 0.0)}
        fixed: dict[str, bool] = {nid: False}
        edge_set = set(sorted_edges)
        for nb in placed_neighbors:
            G_local.add_node(nb)
            G_local.add_edge(nb, nid)
            init_pos[nb] = all_pos[nb]
            fixed[nb] = True

        # Start asteroid at centroid of its neighbors
        cx = sum(init_pos[nb][0] for nb in placed_neighbors) / len(placed_neighbors)
        cy = sum(init_pos[nb][1] for nb in placed_neighbors) / len(placed_neighbors)
        init_pos[nid] = (cx, cy)

        local_k = cfg.k_factor / math.sqrt(len(placed_neighbors) + 1)
        result = nx.spring_layout(
            G_local,
            pos=init_pos,
            fixed=fixed,
            k=local_k,
            seed=seed,
            iterations=cfg.iterations,
        )
        all_pos[nid] = (float(result[nid][0]), float(result[nid][1]))

    # --- normalize ---
    if cfg.normalize_spread:
        scaled = _normalize_positions(all_pos, sorted_node_ids, cfg)
    else:
        scaled = {
            i: (all_pos[i][0] * cfg.scale_m, all_pos[i][1] * cfg.scale_m)
            for i in sorted_node_ids
        }

    return {i: (scaled[i][0], scaled[i][1]) for i in sorted_node_ids}


def _place_planet_subgraph(
    planet_ids: list[NodeId],
    sorted_edges: list[tuple[NodeId, NodeId]],
    seed: int,
    cfg: LayoutConfig,
) -> dict[NodeId, tuple[float, float]]:
    """Place planet nodes using spring_layout on the planet subgraph."""
    if len(planet_ids) < 2:
        return {nid: (0.0, 0.0) for nid in planet_ids}

    G = nx.Graph()
    for nid in planet_ids:
        G.add_node(nid)
    for s, t in sorted_edges:
        if s in planet_ids and t in planet_ids:
            G.add_edge(s, t)

    k = cfg.k_factor / math.sqrt(len(planet_ids))
    pos = nx.spring_layout(G, k=k, seed=seed, iterations=cfg.iterations)
    return {i: (float(p[0]), float(p[1])) for i, p in pos.items()}


def _place_all_simultaneous(
    sorted_node_ids: list[NodeId],
    sorted_edges: list[tuple[NodeId, NodeId]],
    n: int,
    seed: int,
    cfg: LayoutConfig,
) -> dict[NodeId, Vec2]:
    """Fallback: place all nodes simultaneously (old behavior)."""
    G = nx.Graph()
    for nid in sorted_node_ids:
        G.add_node(nid)
    for s, t in sorted_edges:
        G.add_edge(s, t)

    k = cfg.k_factor / math.sqrt(n)
    unit_pos = nx.spring_layout(G, k=k, seed=seed, iterations=cfg.iterations)
    unit_pos = {i: (float(p[0]), float(p[1])) for i, p in unit_pos.items()}

    if cfg.normalize_spread:
        scaled = _normalize_positions(unit_pos, sorted_node_ids, cfg)
    else:
        scaled = {
            i: (unit_pos[i][0] * cfg.scale_m, unit_pos[i][1] * cfg.scale_m)
            for i in sorted_node_ids
        }

    return {i: (scaled[i][0], scaled[i][1]) for i in sorted_node_ids}
