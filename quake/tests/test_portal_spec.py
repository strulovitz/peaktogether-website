import math

from build.portal_spec import portal_spec
from map.raw_models import (
    ConceptGraph,
    Corridor,
    Edge,
    Floorplan,
    FloorRoom,
    IncidentEdge,
    Node,
    RoomPortalSpec,
)


def make_floorplan():
    return Floorplan(
        schema_version="1.0",
        level_id="test",
        seed=1,
        rooms=[
            FloorRoom(
                room_id="a",
                map_xz=(0.0, 0.0),
                importance=3,
                map_radius_m=2.0,
                map_color="#FFFFFF",
            ),
            FloorRoom(
                room_id="b",
                map_xz=(3.0, 4.0),
                importance=5,
                map_radius_m=2.0,
                map_color="#FFFFFF",
            ),
            FloorRoom(
                room_id="c",
                map_xz=(-2.0, 5.0),
                importance=1,
                map_radius_m=2.0,
                map_color="#FFFFFF",
            ),
        ],
        corridors=[
            Corridor(
                corridor_id="edge.a.to.b",
                source="a",
                target="b",
                height_level=1,
                cruise_y=0.0,
                path_xz=[],
                width_m=1.0,
            ),
            Corridor(
                corridor_id="edge.c.to.a",
                source="c",
                target="a",
                height_level=1,
                cruise_y=0.0,
                path_xz=[],
                width_m=1.0,
            ),
        ],
        crossings=[],
    )


def make_graph():
    return ConceptGraph(
        schema_version="1.0",
        level_id="test",
        title="t",
        edition="e",
        seed=1,
        nodes=[
            Node(
                id="a",
                name="A",
                kind="prop",
                importance=3,
                pages=[],
                summary="",
            ),
            Node(
                id="b",
                name="B",
                kind="prop",
                importance=5,
                pages=[],
                summary="",
            ),
            Node(
                id="c",
                name="C",
                kind="lemma",
                importance=1,
                pages=[],
                summary="",
            ),
        ],
        edges=[
            Edge(id="edge.a.to.b", source="a", target="b"),
            Edge(id="edge.c.to.a", source="c", target="a"),
        ],
    )


def test_collects_both_directions():
    fp = make_floorplan()
    g = make_graph()
    result = portal_spec(fp, g, "a")
    assert result.node_id == "a"
    assert len(result.incident) == 2


def test_bearings_exact():
    fp = make_floorplan()
    g = make_graph()
    result = portal_spec(fp, g, "a")
    for inc in result.incident:
        node = next(r for r in fp.rooms if r.room_id == "a")
        nb_room = next(r for r in fp.rooms if r.room_id == inc.neighbor_id)
        expected_bearing = math.atan2(
            nb_room.map_xz[1] - node.map_xz[1],
            nb_room.map_xz[0] - node.map_xz[0],
        )
        assert abs(inc.bearing_rad - expected_bearing) < 1e-9


def test_ordering_importance_desc():
    fp = make_floorplan()
    g = make_graph()
    result = portal_spec(fp, g, "a")
    assert result.incident[0].neighbor_id == "b"
    assert result.incident[1].neighbor_id == "c"


def test_degree_zero():
    fp = Floorplan(
        schema_version="1.0",
        level_id="t",
        seed=1,
        rooms=[
            FloorRoom(
                room_id="orphan",
                map_xz=(0.0, 0.0),
                importance=1,
                map_radius_m=1.0,
                map_color="#FFFFFF",
            )
        ],
        corridors=[],
        crossings=[],
    )
    g = ConceptGraph(
        schema_version="1.0",
        level_id="t",
        title="t",
        edition="e",
        seed=1,
        nodes=[
            Node(
                id="orphan",
                name="O",
                kind="prop",
                importance=1,
                pages=[],
                summary="",
            )
        ],
        edges=[],
    )
    result = portal_spec(fp, g, "orphan")
    assert result.incident == []
    assert result.node_id == "orphan"
