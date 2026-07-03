"""Tests for the map viewer's PURE core.

We test FlyCamera math + floorplan stats + the scale-free initial vantage.
NO hardcoded level sizes: floorplans are generated at parametrized sizes, and
all assertions are graph-relative.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from contracts import Floorplan, FloorRoom, Corridor, Crossing
from tools.map_viewer import (
    FlyCamera,
    compute_stats,
    initial_camera,
    load_floorplan,
    PITCH_LIMIT_RAD,
)



# --------------------------------------------------------------------------- #
# Generated floorplans of arbitrary size — no magic counts.                   #
# --------------------------------------------------------------------------- #
def _make_floorplan(n_rooms: int, n_crossings: int = 0) -> Floorplan:
    rooms = []
    for i in range(n_rooms):
        rooms.append(
            FloorRoom(
                room_id=f"n{i}",
                map_xz=(float(i) * 10.0, float(-i) * 7.0),
                importance=1 + (i % 5),
                map_radius_m=2.0 + (i % 5),
                map_color="#4f6d7a",
                socket_y=0.0,
            )
        )
    corridors = []
    for i in range(max(0, n_rooms - 1)):
        layer = i % 3
        corridors.append(
            Corridor(
                corridor_id=f"edge.n{i}.to.n{i + 1}",
                source=f"n{i}",
                target=f"n{i + 1}",
                height_level=layer,
                cruise_y=float(layer) * 3.0,
                path_xz=[rooms[i].map_xz, rooms[i + 1].map_xz],
                width_m=3.0,
            )
        )
    crossings = []
    for j in range(n_crossings):
        crossings.append(
            Crossing(
                crossing_id=f"crossing_{j}",
                over_corridor=f"edge.n{j}.to.n{j + 1}",
                under_corridor=f"edge.n{j + 1}.to.n{j + 2}",
                at_xz=(float(j), float(-j)),
                over_y=6.0,
                under_y=3.0,
            )
        )
    return Floorplan(
        schema_version="1.0",
        level_id="gen_level",
        seed=1,
        rooms=rooms,
        corridors=corridors,
        crossings=crossings,
    )


SIZES = [1, 2, 3, 5, 8, 20, 55]


# --------------------------------------------------------------------------- #
# FlyCamera pure math                                                         #
# --------------------------------------------------------------------------- #
def test_view_matrix_shape_dtype_and_convention():
    """view_matrix must be the (4,4) float32 row-major matrix draw_graph wants,
    byte-identical in convention to camera.look_at."""
    from camera import look_at

    cam = FlyCamera()
    cam.pos = np.array([1.0, 2.0, 3.0])
    cam.yaw = 0.5
    cam.pitch = -0.2
    m = cam.view_matrix()

    assert m.shape == (4, 4)
    assert m.dtype == np.float32
    assert m.flags["C_CONTIGUOUS"]  # row-major memory

    # Same as look_at(eye, eye+forward, up) by construction.
    eye = cam.pos
    target = cam.pos + cam.forward()
    expected = look_at(eye, target, np.array([0.0, 1.0, 0.0]))
    assert np.allclose(m, expected)


def test_forward_uses_frozen_compass():
    """yaw=0, pitch=0 -> forward (1,0,0) = +X east. yaw=pi/2 -> +Z north."""
    cam = FlyCamera()
    cam.yaw = 0.0
    cam.pitch = 0.0
    assert np.allclose(cam.forward(), [1.0, 0.0, 0.0], atol=1e-6)

    cam.yaw = math.pi / 2.0
    assert np.allclose(cam.forward(), [0.0, 0.0, 1.0], atol=1e-6)


def test_move_forward_changes_position_along_look():
    cam = FlyCamera()
    cam.yaw = 0.0  # facing +X
    cam.pitch = 0.0
    start = cam.pos.copy()
    cam.move(forward_amt=5.0, right_amt=0.0, up_amt=0.0)
    delta = cam.pos - start
    assert np.allclose(delta, [5.0, 0.0, 0.0], atol=1e-6)


def test_strafe_is_horizontal_regardless_of_pitch():
    """right() ignores pitch -> strafing never changes Y even when looking up."""
    cam = FlyCamera()
    cam.yaw = 0.0
    cam.pitch = 1.0  # looking steeply up
    start = cam.pos.copy()
    cam.move(forward_amt=0.0, right_amt=3.0, up_amt=0.0)
    delta = cam.pos - start
    assert abs(delta[1]) < 1e-9  # no vertical drift from strafe


def test_up_is_pure_world_y():
    cam = FlyCamera()
    cam.yaw = 1.234
    cam.pitch = 0.7
    start = cam.pos.copy()
    cam.move(forward_amt=0.0, right_amt=0.0, up_amt=4.0)
    delta = cam.pos - start
    assert np.allclose(delta, [0.0, 4.0, 0.0], atol=1e-9)


def test_pitch_is_clamped_to_gimbal_guard():
    cam = FlyCamera()
    cam.add_look(0.0, 100.0)   # try to look way past straight up
    assert cam.pitch <= PITCH_LIMIT_RAD + 1e-12
    cam.add_look(0.0, -100.0)
    assert cam.pitch >= -PITCH_LIMIT_RAD - 1e-12


def test_yaw_wraps_and_stays_finite():
    cam = FlyCamera()
    for _ in range(1000):
        cam.add_look(0.1, 0.0)
    assert math.isfinite(cam.yaw)
    assert 0.0 <= cam.yaw < 2.0 * math.pi + 1e-9


# --------------------------------------------------------------------------- #
# Floorplan stats + scale-free initial vantage                                #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("n", SIZES)
def test_stats_counts_match_floorplan(n):
    fp = _make_floorplan(n)
    stats = compute_stats(fp)
    assert stats.n_rooms == len(fp.rooms)
    assert stats.n_corridors == len(fp.corridors)
    assert stats.n_crossings == len(fp.crossings)
    assert stats.extent >= 1.0
    assert np.all(np.isfinite(stats.center))


@pytest.mark.parametrize("n", SIZES)
def test_initial_camera_is_outside_bbox_and_finite(n):
    """The starting vantage scales with the layout (no magic size) and sits
    back from the content so the whole level is in frame."""
    fp = _make_floorplan(n)
    stats = compute_stats(fp)
    cam = initial_camera(stats)
    assert np.all(np.isfinite(cam.pos))
    assert math.isfinite(cam.yaw) and math.isfinite(cam.pitch)
    # Camera should be pulled back/up relative to extent (scale-relative check).
    assert cam.pos[1] >= stats.center[1]  # above center
    # Distance from center grows with extent (no fixed constant asserted).
    dist = float(np.linalg.norm(cam.pos - stats.center))
    assert dist >= stats.extent  # at least one extent away


def test_crossings_drive_flat_note_logic():
    """A 0-crossing layout is distinguishable from one with crossings via the
    same field the HUD reads — this is Nir's 'is it flat?' cue."""
    flat = compute_stats(_make_floorplan(5, n_crossings=0))
    bridged = compute_stats(_make_floorplan(5, n_crossings=2))
    assert flat.n_crossings == 0
    assert bridged.n_crossings == 2


def test_single_room_does_not_crash():
    fp = _make_floorplan(1)
    stats = compute_stats(fp)
    cam = initial_camera(stats)
    assert np.all(np.isfinite(cam.pos))



def test_load_floorplan_roundtrip(tmp_path):
    fp = _make_floorplan(8, n_crossings=1)
    p = tmp_path / "floorplan.json"
    p.write_text(fp.model_dump_json(), encoding="utf-8")
    loaded = load_floorplan(p)
    assert loaded.level_id == fp.level_id
    assert len(loaded.rooms) == len(fp.rooms)
    assert len(loaded.crossings) == len(fp.crossings)
