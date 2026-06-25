import re
from pathlib import Path

import networkx as nx

from map.raw_models import (
    ConceptGraph,
    Node,
    Edge,
    Provenance,
    EdgeProvenance,
    NodeId,
)


_IMPORTANCE_COLORS = {
    1: "#4F6D7A",
    2: "#3FA796",
    3: "#E6B800",
    4: "#E8743B",
    5: "#D81B60",
}

_ID_PATTERN = re.compile(r"^(?P<kind>[A-Za-z]+)_(?P<num>\d+)$")


def _parse_simple_id(node_id: str):
    """Return (kind, n) for ids of the form <kind>_<N>, else None."""
    m = _ID_PATTERN.match(node_id)
    if not m:
        return None
    return m.group("kind"), int(m.group("num"))


def _build_nx(graph: ConceptGraph) -> nx.DiGraph:
    g = nx.DiGraph()
    for node in graph.nodes:
        g.add_node(node.id)
    for edge in graph.edges:
        g.add_edge(edge.source, edge.target)
    return g


def check(
    graph: ConceptGraph,
    provenance: Provenance,
    expected_runs: dict[str, list[int]] | None = None,
) -> list[str]:
    """Return plain-English flag strings. These get written into Provenance.flags."""
    flags: list[str] = []

    # ---- 1. NUMBERING-CONTINUITY ----
    by_kind: dict[str, set[int]] = {}
    for node in graph.nodes:
        parsed = _parse_simple_id(node.id)
        if parsed is None:
            continue
        kind, n = parsed
        by_kind.setdefault(kind, set()).add(n)

    for kind in sorted(by_kind):
        observed = by_kind[kind]
        if expected_runs is not None and kind in expected_runs:
            expected = set(expected_runs[kind])
        else:
            if not observed:
                continue
            expected = set(range(1, max(observed) + 1))
        missing = sorted(expected - observed)
        for n in missing:
            flags.append(
                f"MISSING_ITEM: {kind}_{n} expected — not found in nodes"
            )

    # ---- 2. CYCLE DETECTION ----
    g = _build_nx(graph)
    cycles = list(nx.simple_cycles(g))
    reported = 0
    for cycle in cycles:
        if reported >= 10:
            break
        path = cycle + [cycle[0]]
        flags.append(
            f"CYCLE: {' -> '.join(path)} — likely a misread citation; "
            f"check these pages"
        )
        reported += 1
    if len(cycles) > 10:
        flags.append(f"…and {len(cycles) - 10} more cycles")

    # ---- 3. ORPHANS ----
    for node in graph.nodes:
        if g.degree(node.id) == 0:
            flags.append(f"ORPHAN: {node.id} has no edges")

    # ---- 4. CONNECTIVITY / ISLANDS ----
    if g.number_of_nodes() == 0:
        n_components = 0
    else:
        n_components = nx.number_weakly_connected_components(g)
    if n_components == 1:
        flags.append("ISLANDS: 1 component (ok)")
    else:
        flags.append(
            f"ISLANDS: {n_components} components — a section-bridging "
            f"citation may be missing"
        )

    # ---- 5. PROVENANCE SCRUTINY ----
    n_both = 0
    n_cit_only = 0
    n_inf_only = 0
    for ep in provenance.edges:
        if ep.agreement == "both":
            n_both += 1
        elif ep.agreement == "citation_only":
            n_cit_only += 1
        elif ep.agreement == "inference_only":
            n_inf_only += 1
    scrutiny = (
        f"SCRUTINY: {n_both} both, {n_cit_only} citation_only, "
        f"{n_inf_only} inference_only edges"
    )
    if n_inf_only > 0:
        scrutiny += " — confirm against the page"
    flags.append(scrutiny)

    return flags


def render_preview(graph: ConceptGraph, provenance: Provenance, out_png: Path) -> None:
    """Draw the graph with networkx + matplotlib. Build-only; smoke-tested only."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    g = nx.DiGraph()
    name_by_id: dict[str, str] = {}
    size_by_id: dict[str, float] = {}
    color_by_id: dict[str, str] = {}
    for node in graph.nodes:
        g.add_node(node.id)
        name_by_id[node.id] = node.name
        size_by_id[node.id] = 200 + node.importance * 150
        color_by_id[node.id] = _IMPORTANCE_COLORS.get(node.importance, "#4F6D7A")

    for edge in graph.edges:
        g.add_edge(edge.source, edge.target, edge_id=edge.id)

    inferred_ids = {
        ep.edge_id for ep in provenance.edges if ep.provenance == "inferred"
    }

    pos = nx.spring_layout(g, seed=42)

    node_list = list(g.nodes())
    node_sizes = [size_by_id.get(n, 200) for n in node_list]
    node_colors = [color_by_id.get(n, "#4F6D7A") for n in node_list]

    inferred_edges = []
    cited_edges = []
    for u, v, data in g.edges(data=True):
        if data.get("edge_id") in inferred_ids:
            inferred_edges.append((u, v))
        else:
            cited_edges.append((u, v))

    fig, ax = plt.subplots(figsize=(10, 8))

    nx.draw_networkx_nodes(
        g, pos, nodelist=node_list, node_size=node_sizes,
        node_color=node_colors, ax=ax,
    )
    if cited_edges:
        nx.draw_networkx_edges(
            g, pos, edgelist=cited_edges, style="solid",
            edge_color="#222222", ax=ax,
        )
    if inferred_edges:
        nx.draw_networkx_edges(
            g, pos, edgelist=inferred_edges, style="dashed",
            edge_color="#999999", ax=ax,
        )
    nx.draw_networkx_labels(g, pos, labels=name_by_id, font_size=8, ax=ax)

    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(str(out_png), dpi=150)
    plt.close(fig)
