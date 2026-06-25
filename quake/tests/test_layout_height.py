def test_four_node_one_crossing():
    from map.layout_height import detect_crossings, assign_heights, HeightConfig
    from map.raw_models import ConceptGraph, Node, Edge

    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[
            Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="c", name="c", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="d", name="d", kind="node", importance=1, pages=[], summary="", tags=[]),
        ],
        edges=[
            Edge(id="edge.a.to.c", source="a", target="c", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.b.to.d", source="b", target="d", kind="depends_on", weight=1.0, label=""),
        ]
    )
    positions = {"a": (0.0, 2.0), "b": (2.0, 0.0), "c": (0.0, -2.0), "d": (-2.0, 0.0)}
    cfg = HeightConfig(socket_clearance_m=0.5)

    crossings = detect_crossings(positions, graph, cfg)
    assert len(crossings) == 1
    assert crossings[0][0] == "edge.a.to.c" or crossings[0][0] == "edge.b.to.d"
    assert crossings[0][1] == "edge.b.to.d" or crossings[0][1] == "edge.a.to.c"
    ix, iz = crossings[0][2]
    assert abs(ix) < 0.01
    assert abs(iz) < 0.01

    heights = assign_heights(crossings, graph, cfg)
    assert heights["edge.a.to.c"] != heights["edge.b.to.d"]
    assert heights["edge.a.to.c"] in (0, 1)
    assert heights["edge.b.to.d"] in (0, 1)


def test_no_crossings():
    from map.layout_height import detect_crossings, assign_heights, HeightConfig
    from map.raw_models import ConceptGraph, Node, Edge

    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[
            Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="c", name="c", kind="node", importance=1, pages=[], summary="", tags=[]),
        ],
        edges=[
            Edge(id="edge.a.to.b", source="a", target="b", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.b.to.c", source="b", target="c", kind="depends_on", weight=1.0, label=""),
        ]
    )
    positions = {"a": (0.0, 0.0), "b": (2.0, 0.0), "c": (4.0, 0.0)}
    cfg = HeightConfig()

    crossings = detect_crossings(positions, graph, cfg)
    assert len(crossings) == 0

    heights = assign_heights(crossings, graph, cfg)
    assert heights["edge.a.to.b"] == 0
    assert heights["edge.b.to.c"] == 0


def test_three_mutual_crossings():
    from map.layout_height import detect_crossings, assign_heights, HeightConfig
    from map.raw_models import ConceptGraph, Node, Edge

    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[
            Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="c", name="c", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="d", name="d", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="e", name="e", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="f", name="f", kind="node", importance=1, pages=[], summary="", tags=[]),
        ],
        edges=[
            Edge(id="edge.a.to.d", source="a", target="d", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.b.to.e", source="b", target="e", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.c.to.f", source="c", target="f", kind="depends_on", weight=1.0, label=""),
        ]
    )
    positions = {
        "a": (-2.0, 2.0), "d": (2.0, -2.0),
        "b": (2.0, 2.0),  "e": (-2.0, -2.0),
        "c": (-2.0, 0.0), "f": (2.0, 0.0),
    }
    cfg = HeightConfig(socket_clearance_m=0.5)

    crossings = detect_crossings(positions, graph, cfg)
    assert len(crossings) == 3

    heights = assign_heights(crossings, graph, cfg)
    assert len(set(heights.values())) == 3
    assert set(heights.values()) == {0, 1, 2}


def test_layer_overflow_raises():
    from map.layout_height import assign_heights, HeightConfig
    from map.raw_models import ConceptGraph, Node, Edge
    import pytest

    edges = []
    crossings = []
    for i in range(13):
        eid = f"edge.n{i}.to.n{i+13}"
        edges.append(Edge(id=eid, source=f"n{i}", target=f"n{i+13}", kind="depends_on", weight=1.0, label=""))

    nodes = []
    for i in range(26):
        nodes.append(Node(id=f"n{i}", name=f"n{i}", kind="node", importance=1, pages=[], summary="", tags=[]))

    graph = ConceptGraph(schema_version="1.0", level_id="test", title="", edition="", seed=1,
                         nodes=nodes, edges=edges)

    for i in range(13):
        for j in range(i+1, 13):
            crossings.append((edges[i].id, edges[j].id, (0.0, 0.0)))

    cfg = HeightConfig(layer_fail=12)
    with pytest.raises(ValueError, match="Height overflow"):
        assign_heights(crossings, graph, cfg)


def test_socket_clearance():
    from map.layout_height import detect_crossings, HeightConfig
    from map.raw_models import ConceptGraph, Node, Edge

    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[
            Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="c", name="c", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="d", name="d", kind="node", importance=1, pages=[], summary="", tags=[]),
        ],
        edges=[
            Edge(id="edge.a.to.c", source="a", target="c", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.b.to.d", source="b", target="d", kind="depends_on", weight=1.0, label=""),
        ]
    )
    positions = {
        "a": (0.0, 0.5),
        "b": (2.0, -1.0),
        "c": (0.0, -3.0),
        "d": (-2.0, -1.0),
    }
    cfg = HeightConfig(socket_clearance_m=2.0)

    crossings = detect_crossings(positions, graph, cfg)
    assert len(crossings) == 0
