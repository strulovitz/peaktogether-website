from map.raw_models import (
    ConceptGraph,
    Node,
    Edge,
    Provenance,
    EdgeProvenance,
)
from map.sanity import check, render_preview


def make_graph(nodes_data, edges_data, prov_data=None):
    """Quickly build ConceptGraph + Provenance for tests."""
    nodes = [
        Node(id=nid, name=nid, kind=k, importance=imp, pages=[], summary="", tags=[])
        for nid, k, imp in nodes_data
    ]
    edges = [
        Edge(id=f"edge.{s}.to.{t}", source=s, target=t, kind="depends_on",
             weight=1.0, label="")
        for s, t in edges_data
    ]
    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=nodes, edges=edges,
    )

    if prov_data is None:
        prov_edges = [
            EdgeProvenance(edge_id=e.id, provenance="cited", snippet="",
                           page_seen="1", agreement="both", reason="", vague=False)
            for e in edges
        ]
    else:
        prov_edges = [
            EdgeProvenance(
                edge_id=pid, provenance=p, snippet="",
                page_seen="1" if p == "cited" else None,
                agreement=a, reason="", vague=False,
            )
            for pid, p, a in prov_data
        ]
    prov = Provenance(schema_version="1.0", level_id="test", edges=prov_edges, flags=[])
    return graph, prov


def test_cycle_detection():
    graph, prov = make_graph(
        [("lemma_3", "lemma", 3), ("prop_2", "proposition", 2)],
        [("lemma_3", "prop_2"), ("prop_2", "lemma_3")],
    )
    flags = check(graph, prov)
    assert any("CYCLE" in f for f in flags)
    assert any("lemma_3" in f for f in flags)


def test_missing_item():
    nodes = [(f"lemma_{i}", "lemma", 1) for i in [1, 2, 3, 4, 5, 6, 8]]
    edges = [
        ("lemma_1", "lemma_2"),
        ("lemma_2", "lemma_3"),
        ("lemma_3", "lemma_4"),
        ("lemma_4", "lemma_5"),
        ("lemma_5", "lemma_6"),
        ("lemma_6", "lemma_8"),
    ]
    graph, prov = make_graph(nodes, edges)
    flags = check(graph, prov)
    assert any("MISSING_ITEM" in f for f in flags)
    assert any("lemma_7" in f for f in flags)


def test_orphan():
    graph, prov = make_graph(
        [("lemma_1", "lemma", 1), ("lemma_2", "lemma", 1), ("def_5", "definition", 1)],
        [("lemma_1", "lemma_2")],
    )
    flags = check(graph, prov)
    assert any("ORPHAN" in f for f in flags)
    assert any("def_5" in f for f in flags)


def test_two_components():
    graph, prov = make_graph(
        [
            ("lemma_1", "lemma", 1),
            ("lemma_2", "lemma", 1),
            ("prop_1", "proposition", 1),
            ("prop_2", "proposition", 1),
        ],
        [("lemma_1", "lemma_2"), ("prop_1", "prop_2")],
    )
    flags = check(graph, prov)
    assert any("ISLANDS: 2 components" in f for f in flags)


def test_clean_graph():
    graph, prov = make_graph(
        [("lemma_1", "lemma", 1), ("lemma_2", "lemma", 1), ("lemma_3", "lemma", 1)],
        [("lemma_1", "lemma_2"), ("lemma_2", "lemma_3")],
    )
    flags = check(graph, prov)
    assert any("ISLANDS: 1 component (ok)" in f for f in flags)
    assert not any("CYCLE" in f for f in flags)
    assert not any("ORPHAN" in f for f in flags)
    assert not any("MISSING_ITEM" in f for f in flags)


def test_provenance_scrutiny():
    edges = [
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
        ("d", "e"),
    ]
    edge_ids = [f"edge.{s}.to.{t}" for s, t in edges]
    prov_data = [
        (edge_ids[0], "cited", "both"),
        (edge_ids[1], "cited", "citation_only"),
        (edge_ids[2], "cited", "citation_only"),
        (edge_ids[3], "inferred", "inference_only"),
    ]
    nodes = [(n, "node", 1) for n in ["a", "b", "c", "d", "e"]]
    graph, prov = make_graph(nodes, edges, prov_data=prov_data)
    flags = check(graph, prov)
    scrutiny = [f for f in flags if "SCRUTINY" in f]
    assert scrutiny
    assert "1 both" in scrutiny[0]
    assert "2 citation_only" in scrutiny[0]
    assert "1 inference_only" in scrutiny[0]
    assert "confirm against the page" in scrutiny[0]


def test_render_preview_smoke(tmp_path):
    graph, prov = make_graph(
        [("lemma_1", "lemma", 1), ("lemma_2", "lemma", 3), ("prop_1", "proposition", 5)],
        [("lemma_1", "lemma_2"), ("lemma_2", "prop_1")],
        prov_data=[
            ("edge.lemma_1.to.lemma_2", "cited", "both"),
            ("edge.lemma_2.to.prop_1", "inferred", "inference_only"),
        ],
    )
    out = tmp_path / "preview.png"
    render_preview(graph, prov, out)
    assert out.exists()
    assert out.stat().st_size > 0
