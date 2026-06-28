def test_four_node_one_crossing_floorplan():
    """End-to-end floorplan for a 4-node 2-edge graph. Verifies schema,
    room/corridor invariants. Crossing count is not asserted (layout-dependent);
    if crossings exist, their invariants are checked. The correct detection of
    genuine crossings and non-detection of phantom points is tested in
    test_layout_height.py (hand-placed) and test_layout_scale.py (generated)."""
    from map.level_maker import build_floorplan, LevelMakerConfig
    from map.raw_models import ConceptGraph, Node, Edge, Floorplan

    graph = ConceptGraph(
        schema_version="1.0", level_id="test", title="", edition="", seed=1,
        nodes=[
            Node(id="a", name="a", kind="node", importance=3, pages=[], summary="", tags=[]),
            Node(id="b", name="b", kind="node", importance=1, pages=[], summary="", tags=[]),
            Node(id="c", name="c", kind="node", importance=5, pages=[], summary="", tags=[]),
            Node(id="d", name="d", kind="node", importance=1, pages=[], summary="", tags=[]),
        ],
        edges=[
            Edge(id="edge.a.to.c", source="a", target="c", kind="depends_on", weight=1.0, label=""),
            Edge(id="edge.b.to.d", source="b", target="d", kind="depends_on", weight=1.0, label=""),
        ]
    )
    cfg = LevelMakerConfig()

    fp = build_floorplan(graph, 1729001, cfg)

    assert fp.schema_version == "1.0"
    assert fp.level_id == "test"
    assert fp.seed == 1729001

    room_ids = {r.room_id for r in fp.rooms}
    assert room_ids == {"a", "b", "c", "d"}

    for room in fp.rooms:
        assert room.map_color.startswith("#")
        assert room.map_radius_m >= cfg.map_radius_base_m
        assert room.socket_y == 0.0

    corridor_ids = {c.corridor_id for c in fp.corridors}
    assert corridor_ids == {"edge.a.to.c", "edge.b.to.d"}

    for corr in fp.corridors:
        assert corr.height_level >= 0
        assert corr.width_m == cfg.corridor_width_m

    # Crossing invariants: if the layout happens to produce crossings, verify
    # they are well-formed. The correct crossing-detection logic (no phantom
    # points, genuine crossings only) is tested in test_layout_height.py and
    # test_layout_scale.py.
    for x in fp.crossings:
        assert x.over_y > x.under_y
        assert x.over_corridor in corridor_ids
        assert x.under_corridor in corridor_ids
        assert x.over_corridor != x.under_corridor
        # Parent 8 guarantee: crossing coords must be finite (no phantom points).
        import math
        assert math.isfinite(x.at_xz[0]) and math.isfinite(x.at_xz[1])


def test_spine_equality():
    from map.level_maker import build_floorplan, LevelMakerConfig
    from map.raw_models import ConceptGraph, Node, Edge

    nodes = [Node(id=f"n{i}", name=f"n{i}", kind="node", importance=1, pages=[], summary="", tags=[]) for i in range(5)]
    edges = [Edge(id=f"edge.n{i}.to.n{i+1}", source=f"n{i}", target=f"n{i+1}", kind="depends_on", weight=1.0, label="") for i in range(4)]
    graph = ConceptGraph(schema_version="1.0", level_id="test", title="", edition="", seed=1, nodes=nodes, edges=edges)

    fp = build_floorplan(graph, 1, LevelMakerConfig())

    node_ids = {n.id for n in graph.nodes}
    room_ids = {r.room_id for r in fp.rooms}
    assert node_ids == room_ids


def test_determinism():
    from map.level_maker import build_floorplan, LevelMakerConfig
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
    cfg = LevelMakerConfig()
    fp1 = build_floorplan(graph, 42, cfg)
    fp2 = build_floorplan(graph, 42, cfg)
    assert fp1.model_dump() == fp2.model_dump()


def test_no_crossing_floorplan():
    from map.level_maker import build_floorplan, LevelMakerConfig
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
    fp = build_floorplan(graph, 1, LevelMakerConfig())
    assert len(fp.crossings) == 0
    for corr in fp.corridors:
        assert corr.height_level == 0


def test_importance_affects_radius():
    from map.level_maker import build_floorplan, LevelMakerConfig
    from map.raw_models import ConceptGraph, Node, Edge

    nodes = [
        Node(id="a", name="a", kind="node", importance=1, pages=[], summary="", tags=[]),
        Node(id="b", name="b", kind="node", importance=5, pages=[], summary="", tags=[]),
    ]
    graph = ConceptGraph(schema_version="1.0", level_id="test", title="", edition="", seed=1,
                         nodes=nodes, edges=[])
    cfg = LevelMakerConfig(map_radius_base_m=2.0, map_radius_per_importance_m=1.0)
    fp = build_floorplan(graph, 1, cfg)
    r1 = next(r for r in fp.rooms if r.room_id == "a").map_radius_m
    r5 = next(r for r in fp.rooms if r.room_id == "b").map_radius_m
    assert r1 == 2.0
    assert r5 == 6.0
