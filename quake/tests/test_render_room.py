"""Tests for render_room.py — M6 module #10."""

import math

import numpy as np
import pytest

from contracts import (
    RoomRuntime, DoorRT, PanelPairRT, PanelPlacementRT, EnemyRT,
    Pack, GameState, Manifest, Palette, Floorplan, SaveGame,
    PlayerSave, LevelProgress,
)

import render_room
from render_room import (
    build_room_mesh, panel_is_on, draw_room,
    PanelQuad, RoomMesh, WALL_RGB, ALCOVE_DEPTH_M,
)


# ----------------------------------------------------------------------
# Fixture builders (valid pydantic objects)
# ----------------------------------------------------------------------
def _enemy():
    return EnemyRT(
        enemy_id="boss.demon",
        spawn_xyz=(0.0, 0.0, 0.0),
        health=5,
    )


def _placement(wall, slot_idx, wall_slot, center, w=1.0, h=1.0, yaw=0.0):
    return PanelPlacementRT(
        wall=wall,
        slot_index=slot_idx,
        wall_slot=wall_slot,
        center_xyz=center,
        width_m=w,
        height_m=h,
        yaw_rad=yaw,
    )


def _pair(pid, step, wall, d_center, t_center, yaw=0.0):
    return PanelPairRT(
        pair_id=pid,
        step_index=step,
        drawing_off_asset=f"{pid}_draw_off",
        drawing_on_asset=f"{pid}_draw_on",
        text_off_asset=f"{pid}_text_off",
        text_on_asset=f"{pid}_text_on",
        drawing_placement=_placement(wall, 0, f"{wall}_d", d_center, yaw=yaw),
        text_placement=_placement(wall, 1, f"{wall}_t", t_center, yaw=yaw),
    )


def _room(dimensions=(8.0, 4.0, 6.0), doors=None, pairs=None,
          final_pair_id="a.s0", ceilings=None):
    if doors is None:
        doors = []
    if pairs is None:
        pairs = []
    if ceilings is None:
        ceilings = []
    return RoomRuntime(
        schema_version="1.0",
        room_id="alpha",
        dimensions_m=dimensions,
        panel_pairs=pairs,
        final_pair_id=final_pair_id,
        hidden_door_wall_slot="N_slot0",
        doors=doors,
        enemy=_enemy(),
        ceiling_equations=ceilings,
    )


def _door(wall, center, w=1.2, h=2.5, yaw=0.0):
    return DoorRT(
        edge_id=f"edge.{wall.lower()}room.to.next",
        neighbor_id="next",
        bearing_rad=0.0,
        wall=wall,
        center_xyz=center,
        width_m=w,
        height_m=h,
        normal_yaw_rad=yaw,
        spawn_xyz=center,
        spawn_heading_rad=0.0,
    )


# ----------------------------------------------------------------------
# Geometry helper for assertions
# ----------------------------------------------------------------------
def _tri_covers_point_xy_on_plane(tris, axis_fixed, fixed_val,
                                  along_idx, along_val, y_val, tol=1e-4):
    """Return True if any triangle lying on plane axis_fixed==fixed_val
    contains the (along, y) point."""
    for tri in tris:
        coords = tri[:, axis_fixed]
        if not np.all(np.abs(coords - fixed_val) < tol):
            continue
        along = tri[:, along_idx]
        ys = tri[:, 1]
        if (along.min() - tol <= along_val <= along.max() + tol and
                ys.min() - tol <= y_val <= ys.max() + tol):
            if _point_in_tri(
                (along_val, y_val),
                (tri[0, along_idx], tri[0, 1]),
                (tri[1, along_idx], tri[1, 1]),
                (tri[2, along_idx], tri[2, 1]),
            ):
                return True
    return False


def _point_in_tri(p, a, b, c):
    def sign(p1, p2, p3):
        return ((p1[0] - p3[0]) * (p2[1] - p3[1]) -
                (p2[0] - p3[0]) * (p1[1] - p3[1]))
    d1 = sign(p, a, b)
    d2 = sign(p, b, c)
    d3 = sign(p, c, a)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (has_neg and has_pos)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
def test_box_dimensions():
    W, H, D = 8.0, 4.0, 6.0
    room = _room((W, H, D))
    mesh = build_room_mesh(room)
    tris = mesh.wall_tris

    zs = tris[:, :, 2].reshape(-1)
    assert np.any(np.abs(zs - D / 2) < 1e-4), "N wall at +D/2 missing"
    assert np.any(np.abs(zs - (-D / 2)) < 1e-4), "S wall at -D/2 missing"

    xs = tris[:, :, 0].reshape(-1)
    assert np.any(np.abs(xs - W / 2) < 1e-4), "E wall at +W/2 missing"
    assert np.any(np.abs(xs - (-W / 2)) < 1e-4), "W wall at -W/2 missing"

    ys = tris[:, :, 1].reshape(-1)
    assert abs(ys.min()) < 1e-4
    assert abs(ys.max() - H) < 1e-4


def test_door_hole_present():
    W, H, D = 8.0, 4.0, 6.0
    door = _door("E", (W / 2, 1.25, 0.0), w=1.2, h=2.5)
    room = _room((W, H, D), doors=[door])
    mesh = build_room_mesh(room)
    tris = mesh.wall_tris

    # E wall at x=+W/2; door spans z in [-0.6, 0.6], y in [0, 2.5].
    # No wall triangle on the E plane should cover the center of the hole.
    covered = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=0, fixed_val=W / 2,
        along_idx=2, along_val=0.0, y_val=1.0,
    )
    assert not covered, "E wall should have a hole at the door"

    # Other walls solid.
    n_covered = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=2, fixed_val=D / 2,
        along_idx=0, along_val=0.0, y_val=2.0,
    )
    assert n_covered, "N wall should be solid"
    s_covered = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=2, fixed_val=-D / 2,
        along_idx=0, along_val=0.0, y_val=2.0,
    )
    assert s_covered, "S wall should be solid"
    w_covered = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=0, fixed_val=-W / 2,
        along_idx=2, along_val=0.0, y_val=2.0,
    )
    assert w_covered, "W wall should be solid"


def test_door_hole_at_bearing():
    W, H, D = 8.0, 4.0, 6.0
    offset = 2.0
    door = _door("N", (offset, 1.25, D / 2), w=1.0, h=2.5)
    room = _room((W, H, D), doors=[door])
    mesh = build_room_mesh(room)
    tris = mesh.wall_tris

    hole_covered = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=2, fixed_val=D / 2,
        along_idx=0, along_val=offset, y_val=1.0,
    )
    assert not hole_covered, "hole should be at x=+2.0"

    center_covered = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=2, fixed_val=D / 2,
        along_idx=0, along_val=0.0, y_val=1.0,
    )
    assert center_covered, "N wall center should remain solid"

    left_solid = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=2, fixed_val=D / 2,
        along_idx=0, along_val=1.0, y_val=1.0,
    )
    assert left_solid, "left of hole solid"
    right_solid = _tri_covers_point_xy_on_plane(
        tris, axis_fixed=2, fixed_val=D / 2,
        along_idx=0, along_val=3.0, y_val=1.0,
    )
    assert right_solid, "right of hole solid"


def test_panel_count():
    W, H, D = 8.0, 4.0, 6.0
    pairs = [
        _pair("a.s0", 0, "N", (0.0, 2.0, D / 2), (1.5, 2.0, D / 2), yaw=math.pi),
        _pair("a.s1", 1, "S", (0.0, 2.0, -D / 2), (1.5, 2.0, -D / 2), yaw=0.0),
        _pair("a.s2", 2, "W", (-W / 2, 2.0, 0.0), (-W / 2, 2.0, 1.5),
              yaw=math.pi / 2),
    ]
    room = _room((W, H, D), pairs=pairs, final_pair_id="a.s0")
    mesh = build_room_mesh(room)
    assert len(mesh.panel_quads) == 2 * len(pairs)


def test_panel_corners():
    W, H, D = 8.0, 4.0, 6.0
    cx, cy, cz = 0.0, 2.0, D / 2
    w, h = 2.0, 1.5
    pair = PanelPairRT(
        pair_id="a.s0",
        step_index=0,
        drawing_off_asset="a.s0_d_off",
        drawing_on_asset="a.s0_d_on",
        text_off_asset="a.s0_t_off",
        text_on_asset="a.s0_t_on",
        drawing_placement=_placement("N", 0, "N_d", (cx, cy, cz), w=w, h=h,
                                     yaw=math.pi),
        text_placement=_placement("N", 1, "N_t", (1.0, cy, cz), w=0.5, h=0.5,
                                   yaw=math.pi),
    )
    room = _room((W, H, D), pairs=[pair], final_pair_id="a.s0")
    mesh = build_room_mesh(room)

    drawing = [q for q in mesh.panel_quads if q.is_drawing][0]
    c = drawing.corners
    assert c.shape == (4, 3)

    x_span = c[:, 0].max() - c[:, 0].min()
    assert abs(x_span - w) < 1e-4
    y_span = c[:, 1].max() - c[:, 1].min()
    assert abs(y_span - h) < 1e-4
    assert abs(c[:, 0].mean() - cx) < 1e-4
    assert abs(c[:, 1].mean() - cy) < 1e-4

    # N wall inward = -Z, so corners should be slightly in negative Z
    assert np.all(c[:, 2] < cz)
    assert np.all(c[:, 2] > cz - 0.05)


def test_panel_on_off_select():
    W, H, D = 8.0, 4.0, 6.0
    pair = _pair("a.s0", 0, "N", (0.0, 2.0, D / 2), (1.5, 2.0, D / 2),
                 yaw=math.pi)
    room = _room((W, H, D), pairs=[pair], final_pair_id="a.s0")

    assert panel_is_on("a.s0", set(), room) is False
    assert panel_is_on("a.s0", {"a.s0_draw_on"}, room) is True
    assert panel_is_on("a.s0", {"a.s0_text_on"}, room) is True
    assert panel_is_on("a.s0", {"something.else"}, room) is False
    assert panel_is_on("zzz.s9", {"a.s0_draw_on"}, room) is False


def test_alcove_is_recess():
    W, H, D = 8.0, 4.0, 6.0
    final = _pair("a.s0", 0, "W", (-W / 2, 2.0, 0.0), (-W / 2, 2.0, 1.5),
                  yaw=math.pi / 2)
    other = _pair("a.s1", 1, "N", (0.0, 2.0, D / 2), (1.5, 2.0, D / 2),
                  yaw=math.pi)
    room = _room((W, H, D), pairs=[final, other], final_pair_id="a.s0")
    mesh = build_room_mesh(room)

    assert mesh.alcove_tris.shape[0] > 0, "alcove should exist"

    xs = mesh.alcove_tris[:, :, 0].reshape(-1)
    assert xs.max() > -W / 2 + 1e-4, "alcove must be pushed inward"
    assert abs(xs.min() - (-W / 2)) < 1e-3, "front rim on wall plane"
    assert xs.max() <= -W / 2 + ALCOVE_DEPTH_M + 1e-4

    # W wall must remain SOLID at the alcove location (no through-hole)
    covered = _tri_covers_point_xy_on_plane(
        mesh.wall_tris, axis_fixed=0, fixed_val=-W / 2,
        along_idx=2, along_val=0.0, y_val=2.0,
    )
    assert covered, "W wall must remain solid at alcove (not a hole)"


# ----------------------------------------------------------------------
# GL smoke test
# ----------------------------------------------------------------------
skip_if_no_gl = pytest.mark.skipif(
    not getattr(render_room, "HAVE_GL", False),
    reason="no GL context available (headless)",
)


def _stub_pack():
    fp = Floorplan(
        schema_version="1.0", level_id="l1", seed=1,
        rooms=[], corridors=[], crossings=[],
    )
    manifest = Manifest(
        schema_version="1.0", level_id="l1", assets={},
    )
    palette = Palette(
        schema_version="1.0", pack_id="p1", groups={},
        grey_ink="#202020", grey_text="#303030", bg_key="#0a0a0a",
        map_importance={"1": "#111111", "2": "#222222", "3": "#333333", "4": "#444444", "5": "#555555"},
        map_node_default="#cccccc",
    )
    return Pack(
        floorplan=fp, rooms={}, manifest=manifest, palette=palette, asset_dir=".",
    )


def _stub_state():
    player = PlayerSave(
        level_id="l1", mode="room", position_xyz=(0.0, 0.0, 0.0), heading_rad=0.0,
    )
    save = SaveGame(
        schema_version="1.0", profile_id="test",
        levels={"l1": LevelProgress()}, player=player,
    )
    return GameState(
        save=save, mode="room", current_room_id="alpha",
        pos=(0.0, 1.6, 0.0), heading_rad=0.0, pitch_rad=0.0,
        lit=set(), cleared=set(),
    )


@skip_if_no_gl
def test_draw_smoke():
    W, H, D = 8.0, 4.0, 6.0
    pair = _pair("a.s0", 0, "N", (0.0, 2.0, D / 2), (1.5, 2.0, D / 2),
                 yaw=math.pi)
    room = _room((W, H, D), pairs=[pair], final_pair_id="a.s0",
                 doors=[_door("E", (W / 2, 1.25, 0.0))])
    pack = _stub_pack()
    state = _stub_state()
    view = np.eye(4, dtype=np.float32)

    draw_room(view, room, pack, state)
