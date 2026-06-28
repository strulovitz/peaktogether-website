"""Tests for render_wire.py — 6 pure tests + 1 GPU smoke test."""
import numpy as np
import pytest

from render_wire import build_wire_mesh, hex_to_rgb, WireMesh, RING_SEGMENTS, WIRE_BASE
from contracts import Floorplan, FloorRoom, Corridor, Crossing
from conftest import skip_if_no_gl


# ---------------------------------------------------------------------------
# Builders for golden test data
# ---------------------------------------------------------------------------
def _room(room_id, xz, color="#ffffff", radius=3.0, socket_y=0.0, importance=3):
    return FloorRoom(
        room_id=room_id,
        map_xz=xz,
        importance=importance,
        map_radius_m=radius,
        map_color=color,
        socket_y=socket_y,
    )


def _corridor(cid, src, tgt, path, cruise_y=0.0, height_level=0, width=2.0):
    return Corridor(
        corridor_id=cid,
        source=src,
        target=tgt,
        height_level=height_level,
        cruise_y=cruise_y,
        path_xz=path,
        width_m=width,
    )


def _floorplan(rooms, corridors, crossings=None):
    return Floorplan(
        schema_version="1.0",
        level_id="lvl_test",
        seed=42,
        rooms=rooms,
        corridors=corridors,
        crossings=crossings or [],
    )


def _golden_fp():
    """2 rooms, 1 corridor of 3 points."""
    rooms = [
        _room("alpha", (0.0, 0.0)),
        _room("beta", (10.0, 0.0)),
    ]
    corridors = [
        _corridor("edge.c1.to.beta", "alpha", "beta",
                  [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)], cruise_y=0.0),
    ]
    return _floorplan(rooms, corridors)


# ---------------------------------------------------------------------------
# PURE TESTS
# ---------------------------------------------------------------------------
def test_mesh_segment_count():
    fp = _golden_fp()
    mesh = build_wire_mesh(fp)
    # 3-point polyline -> exactly 2 segments.
    assert mesh.line_segments.shape == (2, 2, 3)
    assert mesh.seg_colors.shape == (2, 3)


def test_ring_tessellation():
    fp = _floorplan([_room("solo", (0.0, 0.0))], [])
    mesh = build_wire_mesh(fp)
    assert mesh.ring_segments.shape[0] == RING_SEGMENTS
    assert mesh.ring_segments.shape == (RING_SEGMENTS, 2, 3)
    assert mesh.ring_colors.shape == (RING_SEGMENTS, 3)


def test_ring_radius():
    cx, cz, r, y = 7.0, -3.0, 4.25, 1.5
    fp = _floorplan([_room("solo", (cx, cz), radius=r, socket_y=y)], [])
    mesh = build_wire_mesh(fp)
    verts = mesh.ring_segments.reshape(-1, 3)  # all endpoints
    # Every vertex sits at radius r from center in XZ, at y=socket_y.
    dx = verts[:, 0] - cx
    dz = verts[:, 2] - cz
    dist = np.sqrt(dx * dx + dz * dz)
    assert np.allclose(dist, r, atol=1e-4)
    assert np.allclose(verts[:, 1], y, atol=1e-4)


def test_crossing_heights():
    rooms = [
        _room("a", (0.0, 0.0)),
        _room("b", (10.0, 0.0)),
        _room("c", (5.0, -5.0)),
        _room("d", (5.0, 5.0)),
    ]
    corridors = [
        _corridor("edge.over.to.b", "a", "b",
                  [(0.0, 0.0), (10.0, 0.0)], cruise_y=4.5),
        _corridor("edge.under.to.d", "c", "d",
                  [(5.0, -5.0), (5.0, 5.0)], cruise_y=0.0),
    ]
    fp = _floorplan(rooms, corridors)
    mesh = build_wire_mesh(fp)
    ys = mesh.line_segments[:, :, 1]  # all segment y values
    # over corridor (cruise_y=4.5) and under (0.0) must produce distinct y's.
    assert np.isclose(ys.max(), 4.5)
    assert np.isclose(ys.min(), 0.0)
    assert ys.max() > ys.min()


def test_hex_to_rgb():
    assert hex_to_rgb("#ffffff") == (1.0, 1.0, 1.0)
    assert hex_to_rgb("#000000") == (0.0, 0.0, 0.0)
    r, g, b = hex_to_rgb("#ff8000")
    assert abs(r - 1.0) < 1e-6
    assert abs(g - 0.5) < 0.01
    assert abs(b - 0.0) < 1e-6


def test_deterministic_mesh():
    fp = _golden_fp()
    m1 = build_wire_mesh(fp)
    m2 = build_wire_mesh(fp)
    assert np.array_equal(m1.line_segments, m2.line_segments)
    assert np.array_equal(m1.seg_colors, m2.seg_colors)
    assert np.array_equal(m1.ring_segments, m2.ring_segments)
    assert np.array_equal(m1.ring_colors, m2.ring_colors)


# ---------------------------------------------------------------------------
# GPU SMOKE TEST
# ---------------------------------------------------------------------------
@skip_if_no_gl
def test_draw_smoke():
    from render_wire import draw_graph
    from contracts import GameState, SaveGame, PlayerSave, LevelProgress

    fp = _golden_fp()
    view = np.eye(4, dtype=np.float32)

    # Construct a minimal valid GameState (data class from contracts).
    player = PlayerSave(
        level_id="lvl_test",
        mode="corridor",
        position_xyz=(0.0, 0.0, 0.0),
        heading_rad=0.0,
    )
    save = SaveGame(
        schema_version="1.0",
        profile_id="test",
        levels={"lvl_test": LevelProgress()},
        player=player,
    )
    state = GameState(
        save=save,
        mode="corridor",
        current_room_id=None,
        pos=(0.0, 0.0, 0.0),
        heading_rad=0.0,
        pitch_rad=0.0,
        lit=set(),
        cleared=set(),
    )

    # Must run without raising — the shell guards every GL call.
    # Parent 11 changed the signature to draw_graph(view, proj, aspect, fp, state).
    proj = np.eye(4, dtype=np.float32)
    draw_graph(view, proj, 1.0, fp, state)
