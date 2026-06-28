"""Phase A runner — author -> level_maker -> floorplan.json + Gate-3 report.

Run from the quake/ package root:
    python levels/principia_bk1_inverse_square/run_level_maker.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QUAKE_ROOT = os.path.dirname(os.path.dirname(HERE))  # levels/<lvl> -> quake/
if QUAKE_ROOT not in sys.path:
    sys.path.insert(0, QUAKE_ROOT)

import networkx as nx

from map.raw_models import ConceptGraph, load_json
from map.level_maker import build_floorplan, LevelMakerConfig

CG_PATH = os.path.join(HERE, "concept_graph.json")
FP_PATH = os.path.join(HERE, "floorplan.json")


def main() -> None:
    graph: ConceptGraph = load_json(CG_PATH, ConceptGraph)  # validates schema_version + model

    # Independent DAG / connectivity check (Gate 3) via networkx
    G = nx.DiGraph()
    for n in graph.nodes:
        G.add_node(n.id)
    for e in graph.edges:
        G.add_edge(e.source, e.target)
    is_dag = nx.is_directed_acyclic_graph(G)
    weakly_connected = nx.is_weakly_connected(G)

    fp = build_floorplan(graph, graph.seed, LevelMakerConfig())

    with open(FP_PATH, "w", encoding="utf-8") as fh:
        json.dump(fp.model_dump(mode="json"), fh, ensure_ascii=False, indent=2)

    height_levels = sorted({c.height_level for c in fp.corridors})
    deg = {n.id: G.in_degree(n.id) + G.out_degree(n.id) for n in graph.nodes}

    print("=== PHASE A — level_maker report ===")
    print(f"level_id:        {fp.level_id}")
    print(f"seed:            {fp.seed}")
    print(f"nodes / rooms:   {len(graph.nodes)} / {len(fp.rooms)}")
    print(f"edges / corridors: {len(graph.edges)} / {len(fp.corridors)}")
    print(f"crossings:       {len(fp.crossings)}")
    print(f"height levels:   {height_levels}  (count={len(height_levels)})")
    print(f"DAG:             {is_dag}")
    print(f"weakly connected: {weakly_connected}")

    print("--- crossings (bridge / underpass) ---")
    for c in fp.crossings:
        print(
            f"  {c.crossing_id}: OVER {c.over_corridor} (y={c.over_y:.2f})  "
            f"UNDER {c.under_corridor} (y={c.under_y:.2f})  "
            f"at=({c.at_xz[0]:.2f}, {c.at_xz[1]:.2f})"
        )

    print("--- node degree = door count (high -> low) ---")
    for nid, d in sorted(deg.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {nid}: {d}")

    print(f"wrote: {FP_PATH}")


if __name__ == "__main__":
    main()
