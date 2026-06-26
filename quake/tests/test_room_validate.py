import math

from build.room_validate import check_room
from map.raw_models import (
    AssetEntry,
    BuildConfig,
    DoorRT,
    EnemyRT,
    IncidentEdge,
    Manifest,
    PanelPairRT,
    PanelPlacementRT,
    RoomPortalSpec,
    RoomRuntime,
)


def make_config():
    return BuildConfig(
        door_nudge_tol_rad=0.20,
        door_min_separation_m=2.6,
        corner_clearance_m=0.5,
        room_min_w_m=6.0,
        room_min_d_m=6.0,
        room_min_h_m=3.2,
        door_width_m=2.0,
        room_headroom_m=1.2,
    )


def _asset_entry(asset_id="a.f1.off"):
    return AssetEntry(
        asset_id=asset_id,
        kind="figure_off",
        wall_path="a.png",
        master_path="a@master.png",
        px_w=100,
        px_h=80,
        content_bbox=(0, 0, 100, 80),
        dpi=220,
    )


def make_valid_room():
    W, H, D = 8.0, 3.5, 8.0
    doors = [
        DoorRT(
            edge_id="edge.a.to.b",
            neighbor_id="b",
            bearing_rad=0.0,
            wall="E",
            center_xyz=(W / 2, 1.3, 0.0),
            width_m=2.0,
            height_m=2.6,
            normal_yaw_rad=-math.pi / 2,
            spawn_xyz=(W / 2 - 0.5, 0.0, 0.0),
            spawn_heading_rad=math.pi,
        )
    ]
    panels = [
        PanelPairRT(
            pair_id="a.s1",
            step_index=1,
            drawing_off_asset="a.f1.off",
            drawing_on_asset="a.f1.on.1",
            text_off_asset="a.s1.txt.off",
            text_on_asset="a.s1.txt.on",
            drawing_placement=PanelPlacementRT(
                wall="N",
                slot_index=0,
                wall_slot="N-0",
                center_xyz=(0.0, 1.5, D / 2),
                width_m=1.5,
                height_m=1.0,
                yaw_rad=math.pi,
            ),
            text_placement=PanelPlacementRT(
                wall="N",
                slot_index=1,
                wall_slot="N-1",
                center_xyz=(2.0, 1.5, D / 2),
                width_m=1.2,
                height_m=1.0,
                yaw_rad=math.pi,
            ),
        )
    ]
    return RoomRuntime(
        schema_version="1.0",
        room_id="a",
        dimensions_m=(W, H, D),
        panel_pairs=panels,
        final_pair_id="a.s1",
        hidden_door_wall_slot="N-0",
        doors=doors,
        enemy=EnemyRT(enemy_id="a.demon", spawn_xyz=(3.0, 0.1, 3.0), health=5),
        ceiling_equations=[],
    )


def make_portals_for_room(room):
    return RoomPortalSpec(
        node_id=room.room_id,
        incident=[
            IncidentEdge(
                edge_id=d.edge_id,
                neighbor_id=d.neighbor_id,
                neighbor_importance=3,
                bearing_rad=d.bearing_rad,
            )
            for d in room.doors
        ],
    )


def make_manifest_for_room(room):
    assets = {}
    for p in room.panel_pairs:
        for aid in [
            p.drawing_off_asset,
            p.drawing_on_asset,
            p.text_off_asset,
            p.text_on_asset,
        ]:
            assets[aid] = _asset_entry(aid)
    return Manifest(schema_version="1.0", level_id="test", assets=assets)


def test_valid_room_passes():
    room = make_valid_room()
    portals = make_portals_for_room(room)
    manifest = make_manifest_for_room(room)
    violations = check_room(room, portals, manifest, make_config())
    assert violations == []


def test_wrong_door_count():
    room = make_valid_room()
    room.doors.append(room.doors[0].model_copy(deep=True))
    portals = make_portals_for_room(room)
    manifest = make_manifest_for_room(room)
    violations = check_room(room, portals, manifest, make_config())
    assert any(
        "door" in v.lower() or "degree" in v.lower() for v in violations
    )


def test_missing_asset():
    room = make_valid_room()
    portals = make_portals_for_room(room)
    manifest = make_manifest_for_room(room)
    manifest.assets.pop("a.f1.off", None)
    violations = check_room(room, portals, manifest, make_config())
    assert any("asset" in v.lower() for v in violations)


def test_dimensions_too_small():
    room = make_valid_room()
    room.dimensions_m = (5.0, 2.0, 5.0)
    portals = make_portals_for_room(room)
    manifest = make_manifest_for_room(room)
    violations = check_room(room, portals, manifest, make_config())
    assert any(
        "dimension" in v.lower() or "minimum" in v.lower() or "below" in v.lower()
        for v in violations
    )


def test_wrong_final_pair():
    room = make_valid_room()
    room.final_pair_id = "nonexistent"
    portals = make_portals_for_room(room)
    manifest = make_manifest_for_room(room)
    violations = check_room(room, portals, manifest, make_config())
    assert any("final" in v.lower() for v in violations)


def test_duplicate_slot():
    room = make_valid_room()
    room.panel_pairs[0].text_placement.slot_index = 0
    room.panel_pairs[0].text_placement.wall_slot = "N-0"
    portals = make_portals_for_room(room)
    manifest = make_manifest_for_room(room)
    violations = check_room(room, portals, manifest, make_config())
    assert any("slot" in v.lower() or "duplicate" in v.lower() for v in violations)
