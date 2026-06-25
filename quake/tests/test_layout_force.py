import math

from map.raw_models import ConceptGraph, Node, Edge
from map.layout_force import place_nodes, LayoutConfig


def make_simple_graph():
    return ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[
            Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="c", name="c", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="d", name="d", kind="node", importance=1, pages=[], summary="", tags=[]),
        ],
        edges=[
            Edge(id="edge.a.to.b", source="a", target="b", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.b.to.c", source="b", target="c", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.c.to.d", source="c", target="d", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.a.to.d", source="a", target="d", kind="depends_on", weight=1.0, label=""),
        ]
    )


def test_same_process_determinism():
    """Calling twice with same inputs on this machine → identical dict."""
    graph = make_simple_graph()
    cfg = LayoutConfig()
    pos1 = place_nodes(graph, 1729001, cfg)
    pos2 = place_nodes(graph, 1729001, cfg)
    assert pos1 == pos2  # exact equality on same process/machine


def test_completeness():
    """Every node id present exactly once; no extras."""
    graph = make_simple_graph()
    cfg = LayoutConfig()
    pos = place_nodes(graph, 1729001, cfg)
    expected_ids = {"a", "b", "c", "d"}
    assert set(pos.keys()) == expected_ids


def test_finiteness_and_bounds():
    """All coordinates finite and within [-scale_m, +scale_m]."""
    graph = make_simple_graph()
    cfg = LayoutConfig(scale_m=40.0)
    pos = place_nodes(graph, 1729001, cfg)
    for node_id, (x, z) in pos.items():
        assert abs(x) < cfg.scale_m * 1.5  # spring_layout can push slightly beyond
        assert abs(z) < cfg.scale_m * 1.5
        assert math.isfinite(x)
        assert math.isfinite(z)


def test_order_independence():
    """Shuffling graph input order → identical output (canonicalization works)."""
    nodes_unsorted = [
        Node(id="c", name="c", kind="node", importance=1, pages=[], summary="", tags=[]),
        Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
        Node(id="d", name="d", kind="node", importance=1, pages=[], summary="", tags=[]),
        Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
    ]
    edges_unsorted = [
        Edge(id="edge.c.to.d", source="c", target="d", kind="depends_on", weight=1.0, label=""),
        Edge(id="edge.a.to.b", source="a", target="b", kind="depends_on", weight=1.0, label=""),
        Edge(id="edge.b.to.c", source="b", target="c", kind="depends_on", weight=1.0, label=""),
        Edge(id="edge.a.to.d", source="a", target="d", kind="depends_on", weight=1.0, label=""),
    ]
    graph_unsorted = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=nodes_unsorted, edges=edges_unsorted,
    )

    nodes_sorted = sorted(nodes_unsorted, key=lambda n: n.id)
    edges_sorted = sorted(edges_unsorted, key=lambda e: (e.source, e.target))
    graph_sorted = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=nodes_sorted, edges=edges_sorted,
    )

    cfg = LayoutConfig()
    pos_unsorted = place_nodes(graph_unsorted, 1729001, cfg)
    pos_sorted = place_nodes(graph_sorted, 1729001, cfg)
    assert pos_unsorted == pos_sorted  # exact equality — canonicalization worked


def test_different_seeds_different():
    """Different seeds produce different positions (with very high probability)."""
    graph = make_simple_graph()
    cfg = LayoutConfig()
    pos1 = place_nodes(graph, 1, cfg)
    pos2 = place_nodes(graph, 99999, cfg)
    any_diff = any(pos1[n] != pos2[n] for n in pos1)
    assert any_diff


def test_single_node():
    """Single node with no edges should not crash."""
    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[Node(id="solo", name="solo", kind="node", importance=1, pages=[], summary="", tags=[])],
        edges=[],
    )
    cfg = LayoutConfig()
    pos = place_nodes(graph, 1, cfg)
    assert list(pos.keys()) == ["solo"]
    assert math.isfinite(pos["solo"][0])
