import pytest


def test_golden_merge():
    """The §4.9 verbatim example: nodes_raw + citations_raw + inference_raw → exact Provenance + ConceptGraph."""
    from map.raw_models import (
        NodesRaw, RawNode, CitationsRaw, RawCiteItem, RawCitation,
        InferenceRaw, RawInferEdge, MergeConfig,
        ConceptGraph, Node, Edge, Provenance, EdgeProvenance,
    )
    from map.merge import merge

    nodes_raw = NodesRaw(
        schema_version="1.0",
        level_id="principia_bk1_sec1",
        edition="Newton, Principia, trans. Andrew Motte, 1846 New York English ed.",
        nodes=[
            RawNode(local_label="Law II", proposed_id="law_2", kind="law",
                    pages=["19"], summary="Change of motion is proportional to the force impressed.",
                    importance_hint=5),
            RawNode(local_label="Lemma I", proposed_id="lemma_1", kind="lemma",
                    pages=["41"], summary="Quantities that tend to equality in a finite time become ultimately equal.",
                    importance_hint=5),
            RawNode(local_label="Prop. I. Theorem I.", proposed_id="prop_1", kind="proposition",
                    pages=["55", "56"], summary="A body's radius to a fixed center sweeps equal areas in equal times.",
                    importance_hint=5),
        ]
    )

    citations_raw = CitationsRaw(
        schema_version="1.0",
        level_id="principia_bk1_sec1",
        source="text",
        items=[
            RawCiteItem(
                local_label="Prop. I. Theorem I.",
                summary="Radii to a fixed center sweep equal areas in equal times.",
                citations=[
                    RawCitation(phrase="by the first Law of Motion", page_seen="55", vague=False),
                    RawCitation(phrase="by the second Law", page_seen="55", vague=False),
                    RawCitation(phrase="as was demonstrated above", page_seen="56", vague=True),
                ]
            )
        ]
    )

    inference_raw = InferenceRaw(
        schema_version="1.0",
        level_id="principia_bk1_sec1",
        edges=[
            RawInferEdge(source_label="Prop. I. Theorem I.", target_label="Law II",
                         reason="The equal-area proof builds each impulse from the change-of-motion law."),
            RawInferEdge(source_label="Prop. I. Theorem I.", target_label="Lemma I",
                         reason="The polygon-to-curve limit uses ultimate-equality of vanishing triangles."),
        ]
    )

    cfg = MergeConfig(title="Book I, Section I", seed=1729001)

    graph, prov = merge(nodes_raw, citations_raw, inference_raw, cfg)

    assert graph.schema_version == "1.0"
    assert graph.level_id == "principia_bk1_sec1"
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    node_ids = [n.id for n in graph.nodes]
    assert node_ids == ["law_2", "lemma_1", "prop_1"]

    edge_keys = [(e.source, e.target) for e in graph.edges]
    assert edge_keys == [("prop_1", "law_2"), ("prop_1", "lemma_1")]

    e0 = graph.edges[0]
    assert e0.id == "edge.prop_1.to.law_2"
    assert e0.source == "prop_1"
    assert e0.target == "law_2"
    assert e0.kind == "depends_on"
    assert e0.label == "by the second Law"

    e1 = graph.edges[1]
    assert e1.id == "edge.prop_1.to.lemma_1"
    assert e1.source == "prop_1"
    assert e1.target == "lemma_1"
    assert e1.label == ""

    assert len(prov.edges) == 2
    assert prov.flags == []

    p0 = prov.edges[0]
    assert p0.edge_id == "edge.prop_1.to.law_2"
    assert p0.provenance == "cited"
    assert "second Law" in p0.snippet
    assert p0.page_seen == "55"
    assert p0.agreement == "both"
    assert p0.vague == False

    p1 = prov.edges[1]
    assert p1.edge_id == "edge.prop_1.to.lemma_1"
    assert p1.provenance == "inferred"
    assert p1.snippet == ""
    assert p1.page_seen is None
    assert p1.agreement == "inference_only"
    assert "ultimate-equality" in p1.reason

    importances = {n.id: n.importance for n in graph.nodes}
    assert importances["prop_1"] == 3
    assert importances["law_2"] == 5
    assert importances["lemma_1"] == 5


def test_duplicate_proposed_id_raises():
    from map.raw_models import NodesRaw, RawNode, CitationsRaw, InferenceRaw, MergeConfig
    from map.merge import merge

    nodes_raw = NodesRaw(
        schema_version="1.0", level_id="test", edition="",
        nodes=[
            RawNode(local_label="Lemma I", proposed_id="lemma_1", kind="lemma", pages=["1"], summary="", importance_hint=3),
            RawNode(local_label="Lemma I (dup)", proposed_id="lemma_1", kind="lemma", pages=["2"], summary="", importance_hint=3),
        ]
    )
    citations_raw = CitationsRaw(schema_version="1.0", level_id="test", source="text", items=[])
    inference_raw = InferenceRaw(schema_version="1.0", level_id="test", edges=[])
    cfg = MergeConfig()

    with pytest.raises(ValueError, match="lemma_1"):
        merge(nodes_raw, citations_raw, inference_raw, cfg)


def test_unknown_owner_raises():
    from map.raw_models import NodesRaw, RawNode, CitationsRaw, RawCiteItem, InferenceRaw, MergeConfig
    from map.merge import merge

    nodes_raw = NodesRaw(
        schema_version="1.0", level_id="test", edition="",
        nodes=[RawNode(local_label="Lemma I", proposed_id="lemma_1", kind="lemma", pages=["1"], summary="", importance_hint=3)]
    )
    citations_raw = CitationsRaw(
        schema_version="1.0", level_id="test", source="text",
        items=[RawCiteItem(local_label="NONEXISTENT", summary="", citations=[])]
    )
    inference_raw = InferenceRaw(schema_version="1.0", level_id="test", edges=[])
    cfg = MergeConfig()

    with pytest.raises(ValueError, match="NONEXISTENT"):
        merge(nodes_raw, citations_raw, inference_raw, cfg)


def test_self_loop_skipped():
    from map.raw_models import NodesRaw, RawNode, CitationsRaw, RawCiteItem, RawCitation, InferenceRaw, RawInferEdge, MergeConfig
    from map.merge import merge

    nodes_raw = NodesRaw(
        schema_version="1.0", level_id="test", edition="",
        nodes=[RawNode(local_label="Lemma I", proposed_id="lemma_1", kind="lemma", pages=["1"], summary="", importance_hint=3)]
    )
    citations_raw = CitationsRaw(
        schema_version="1.0", level_id="test", source="text",
        items=[RawCiteItem(local_label="Lemma I", summary="",
                 citations=[RawCitation(phrase="by Lemma I", page_seen="1", vague=False)])]
    )
    inference_raw = InferenceRaw(
        schema_version="1.0", level_id="test",
        edges=[RawInferEdge(source_label="Lemma I", target_label="Lemma I", reason="self ref")]
    )
    cfg = MergeConfig()

    graph, prov = merge(nodes_raw, citations_raw, inference_raw, cfg)
    assert len(graph.edges) == 0


def test_empty_inputs():
    from map.raw_models import NodesRaw, CitationsRaw, InferenceRaw, MergeConfig
    from map.merge import merge

    nodes_raw = NodesRaw(schema_version="1.0", level_id="test", edition="", nodes=[])
    citations_raw = CitationsRaw(schema_version="1.0", level_id="test", source="text", items=[])
    inference_raw = InferenceRaw(schema_version="1.0", level_id="test", edges=[])
    cfg = MergeConfig()

    graph, prov = merge(nodes_raw, citations_raw, inference_raw, cfg)
    assert len(graph.nodes) == 0
    assert len(graph.edges) == 0
    assert len(prov.edges) == 0
    assert prov.flags == []
