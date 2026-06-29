import math

import pytest

from build.room_maker import build_room_runtime
from map.raw_models import (
    AssetEntry,
    BuildConfig,
    CeilingEq,
    DrawingBlock,
    FigureDecl,
    IncidentEdge,
    LocalColor,
    Manifest,
    RoomPortalSpec,
    RoomRuntime,
    RoomSource,
    StepPair,
    TextBlock,
)


def _make_asset(asset_id, px_w=200, px_h=300):
    return AssetEntry(
        asset_id=asset_id,
        kind="figure_off" if "off" in asset_id else "figure_on",
        wall_path=f"{asset_id}.png",
        master_path=f"{asset_id}@master.png",
        px_w=px_w,
        px_h=px_h,
        content_bbox=(0, 0, px_w, px_h),
        dpi=220,
    )


def make_fixture():
    figure = FigureDecl(
        figure_id="a.f1",
        asy_path="figures/figure.a.f1.asy",
        recipe_path="figures/recipe.a.f1.json",
        n_steps=3,
        caption="Test figure",
        colors_used=[LocalColor(name="path", hex="#E8A200")],
    )
    drawing = DrawingBlock(
        block_id="a.s1.fig",
        figure_id="a.f1",
        highlight_step=3,
    )
    text = TextBlock(
        block_id="a.s1.txt",
        latex="Test $x$",
        colors_used=[LocalColor(name="path", hex="#E8A200")],
    )
    pair = StepPair(
        pair_id="a.s1",
        step_index=1,
        drawing=drawing,
        text=text,
    )
    room = RoomSource(
        schema_version="1.0",
        node_id="a",
        edition="Test",
        figures=[figure],
        blocks=[pair],
        final_pair_id="a.s1",
        ceiling_equations=[],
    )

    portals = RoomPortalSpec(
        node_id="a",
        incident=[
            IncidentEdge(
                edge_id="edge.a.to.b",
                neighbor_id="b",
                neighbor_importance=3,
                bearing_rad=0.0,
            )
        ],
    )

    manifest = Manifest(
        schema_version="1.0",
        level_id="test",
        assets={
            "a.f1.off": _make_asset("a.f1.off"),
            "a.f1.on.3": _make_asset("a.f1.on.3"),
            "a.s1.txt.off": _make_asset("a.s1.txt.off", 300, 200),
            "a.s1.txt.on": _make_asset("a.s1.txt.on", 300, 200),
        },
    )

    cfg = BuildConfig()
    return room, portals, manifest, cfg


def test_returns_runtime_with_room_id():
    room, portals, manifest, cfg = make_fixture()
    rt = build_room_runtime(room, portals, manifest, cfg)
    assert isinstance(rt, RoomRuntime)
    assert rt.room_id == "a"


def test_doors_match_incident_count():
    room, portals, manifest, cfg = make_fixture()
    rt = build_room_runtime(room, portals, manifest, cfg)
    assert len(rt.doors) == len(portals.incident)


def test_panel_pair_asset_ids():
    room, portals, manifest, cfg = make_fixture()
    rt = build_room_runtime(room, portals, manifest, cfg)
    pp = rt.panel_pairs[0]
    assert pp.drawing_off_asset == "a.f1.off"
    assert pp.drawing_on_asset == "a.f1.on.3"
    assert pp.text_off_asset == "a.s1.txt.off"
    assert pp.text_on_asset == "a.s1.txt.on"


def test_spawn_heading_is_bearing_plus_pi():
    room, portals, manifest, cfg = make_fixture()
    rt = build_room_runtime(room, portals, manifest, cfg)
    for door, edge in zip(rt.doors, portals.incident):
        diff = abs(door.spawn_heading_rad - (edge.bearing_rad + math.pi))
        diff = min(diff, 2 * math.pi - diff)
        assert diff < 1e-9


def test_hidden_door_wall_slot_set():
    room, portals, manifest, cfg = make_fixture()
    rt = build_room_runtime(room, portals, manifest, cfg)
    assert rt.hidden_door_wall_slot
    assert rt.hidden_door_wall_slot == rt.panel_pairs[0].drawing_placement.wall_slot


def test_deterministic_rerun():
    room, portals, manifest, cfg = make_fixture()
    rt1 = build_room_runtime(room, portals, manifest, cfg)
    rt2 = build_room_runtime(room, portals, manifest, cfg)
    assert rt1.model_dump() == rt2.model_dump()


def test_missing_asset_raises():
    room, portals, manifest, cfg = make_fixture()
    del manifest.assets["a.f1.on.3"]
    with pytest.raises(ValueError) as exc:
        build_room_runtime(room, portals, manifest, cfg)
    assert "a.f1.on.3" in str(exc.value)
