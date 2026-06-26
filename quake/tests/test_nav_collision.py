"""Pure-geometry tests for nav_collision.py — no GL, no window context."""

import math

from nav_collision import (build_corridor_nav, build_room_nav,
                           ray_rect_hit, point_in_door,
                           DOOR_TRIGGER_DEPTH_M, CORRIDOR_SLIDE_SOFTNESS)
from contracts import (Floorplan, FloorRoom, Corridor, RoomRuntime, DoorRT,
                       PanelPairRT, PanelPlacementRT, EnemyRT, CeilingEqRT,
                       Vec3, Ray, PanelHit)


# ----------------------------------------------------------------------------
# Builders for test fixtures
# ----------------------------------------------------------------------------
def _room_a(room_id="a", socket_y=0.0):
    return FloorRoom(
        room_id=room_id, map_xz=(0.0, 0.0), importance=3,
        map_radius_m=2.0, map_color="#ffffff", socket_y=socket_y,
    )


def _room_b(room_id="b", socket_y=4.0):
    return FloorRoom(
        room_id=room_id, map_xz=(10.0, 0.0), importance=3,
        map_radius_m=2.0, map_color="#ffffff", socket_y=socket_y,
    )


def _ramp_floorplan():
    # Corridor from a (socket_y=0) to b (socket_y=4): a ramp.
    cor = Corridor(
        corridor_id="edge.a.to.b", source="a", target="b", height_level=0,
        cruise_y=2.0, path_xz=[(0.0, 0.0), (10.0, 0.0)], width_m=4.0,
    )
    return Floorplan(
        schema_version="1.0",
        level_id="l1", seed=1,
        rooms=[_room_a("a", 0.0), _room_b("b", 4.0)],
        corridors=[cor], crossings=[],
    )


def _placement(wall, slot_index, wall_slot, center, w, h, yaw):
    return PanelPlacementRT(
        wall=wall, slot_index=slot_index, wall_slot=wall_slot,
        center_xyz=center, width_m=w, height_m=h, yaw_rad=yaw,
    )


def _pair(pair_id, step, draw_center, draw_yaw, text_center, text_yaw,
          dw=1.0, dh=1.0):
    return PanelPairRT(
        pair_id=pair_id, step_index=step,
        drawing_off_asset=f"{pair_id}_d_off",
        drawing_on_asset=f"{pair_id}_d_on",
        text_off_asset=f"{pair_id}_t_off",
        text_on_asset=f"{pair_id}_t_on",
        drawing_placement=_placement("N", 0, "N0", draw_center, dw, dh, draw_yaw),
        text_placement=_placement("N", 1, "N1", text_center, dw, dh, text_yaw),
    )


def _door(edge_id, wall, center, w=1.0, h=2.0, bearing=0.0, normal_yaw=0.0):
    return DoorRT(
        edge_id=edge_id, neighbor_id="nbor", bearing_rad=bearing, wall=wall,
        center_xyz=center, width_m=w, height_m=h, normal_yaw_rad=normal_yaw,
        spawn_xyz=center, spawn_heading_rad=0.0,
    )


def _enemy():
    return EnemyRT(
        enemy_id="test.demon",
        spawn_xyz=(0.0, 0.0, 0.0),
        health=5,
    )


def _room_runtime(dimensions=(10.0, 3.0, 10.0), pairs=None, doors=None):
    return RoomRuntime(
        schema_version="1.0",
        room_id="r",
        dimensions_m=dimensions,
        panel_pairs=pairs or [],
        final_pair_id="r.s0",
        hidden_door_wall_slot="N0",
        doors=doors or [],
        enemy=_enemy(),
        ceiling_equations=[],
    )


# ----------------------------------------------------------------------------
# CORRIDOR TESTS
# ----------------------------------------------------------------------------
def test_corridor_keeps_on_floor():
    fp = _ramp_floorplan()
    nav = build_corridor_nav(fp)
    # Walk to the midpoint of the ramp; y should interpolate between 0 and 4.
    start = (0.0, 0.0, 0.0)
    delta = (5.0, 0.0, 0.0)
    pos = nav.resolve_player_motion(start, delta)
    assert math.isclose(pos[0], 5.0, abs_tol=1e-6)
    assert math.isclose(pos[2], 0.0, abs_tol=1e-6)
    # midpoint between socket_y 0 and 4 -> 2.0
    assert math.isclose(pos[1], 2.0, abs_tol=1e-6)


def test_corridor_soft_boundary():
    fp = _ramp_floorplan()
    nav = build_corridor_nav(fp)
    half_w = 4.0 / 2.0
    # Attempt to walk far off the centerline (z direction) at x=5.
    start = (5.0, 2.0, 0.0)
    delta = (0.0, 0.0, 100.0)  # way past half-width
    pos = nav.resolve_player_motion(start, delta)
    # Must stay within half-width of centerline (z=0 line).
    dist = abs(pos[2])
    assert dist <= half_w + 1e-6


def test_corridor_nearest_panel_none():
    fp = _ramp_floorplan()
    nav = build_corridor_nav(fp)
    ray = Ray(origin=(0.0, 1.0, 0.0), direction=(1.0, 0.0, 0.0))
    assert nav.nearest_panel(ray, 100.0) is None


def test_corridor_door_at_none():
    fp = _ramp_floorplan()
    nav = build_corridor_nav(fp)
    assert nav.door_at((5.0, 2.0, 0.0)) is None


# ----------------------------------------------------------------------------
# ROOM MOTION TESTS
# ----------------------------------------------------------------------------
def test_room_wall_blocks():
    room = _room_runtime(dimensions=(10.0, 3.0, 10.0), doors=[])
    nav = build_room_nav(room)
    # Walk straight into the E wall (x=+5) with no door.
    start = (4.0, 1.0, 0.0)
    delta = (5.0, 0.0, 0.0)  # would reach x=9, past +5
    pos = nav.resolve_player_motion(start, delta)
    assert pos[0] <= 5.0 + 1e-6
    # Should be clamped at the wall plane.
    assert math.isclose(pos[0], 5.0, abs_tol=1e-6)


def test_room_door_passable():
    # Door on E wall (x=+5), centered at z=0, width 2, height 2.
    door = _door("edge.r.to.nbor", "E", center=(5.0, 1.0, 0.0), w=2.0, h=2.0)
    room = _room_runtime(dimensions=(10.0, 3.0, 10.0), doors=[door])
    nav = build_room_nav(room)
    start = (4.0, 1.0, 0.0)
    delta = (3.0, 0.0, 0.0)  # would reach x=7, crossing the door opening
    pos = nav.resolve_player_motion(start, delta)
    # Passing through the door is allowed -> x crosses the wall plane.
    assert pos[0] > 5.0 + 1e-6


# ----------------------------------------------------------------------------
# RAY / PANEL TESTS
# ----------------------------------------------------------------------------
def test_ray_hits_drawing_panel():
    # Drawing panel centered at (0,1,5) on N wall, normal facing -Z (inward).
    # yaw for normal -Z: cos(yaw)=0, sin(yaw)=-1 => yaw = -pi/2.
    yaw = -math.pi / 2.0
    pair = _pair("r.s1", 0,
                 draw_center=(0.0, 1.0, 5.0), draw_yaw=yaw,
                 text_center=(0.0, 1.0, -5.0), text_yaw=math.pi / 2.0,
                 dw=2.0, dh=2.0)
    room = _room_runtime(dimensions=(10.0, 3.0, 10.0), pairs=[pair])
    nav = build_room_nav(room)
    # Ray from center of room aimed at +Z toward the drawing panel.
    ray = Ray(origin=(0.0, 1.0, 0.0), direction=(0.0, 0.0, 1.0))
    hit = nav.nearest_panel(ray, 100.0)
    assert hit is not None
    assert hit.is_drawing is True
    assert hit.asset_on_id == "r.s1_d_on"
    assert hit.asset_off_id == "r.s1_d_off"
    assert hit.pair_id == "r.s1"
    assert math.isclose(hit.distance, 5.0, abs_tol=1e-6)


def test_ray_misses():
    yaw = -math.pi / 2.0
    pair = _pair("r.s1", 0,
                 draw_center=(0.0, 1.0, 5.0), draw_yaw=yaw,
                 text_center=(0.0, 1.0, -5.0), text_yaw=math.pi / 2.0,
                 dw=2.0, dh=2.0)
    room = _room_runtime(dimensions=(10.0, 3.0, 10.0), pairs=[pair])
    nav = build_room_nav(room)
    # Ray pointing in +X, away from both panels (which are on N/S walls).
    ray = Ray(origin=(0.0, 1.0, 0.0), direction=(1.0, 0.0, 0.0))
    assert nav.nearest_panel(ray, 100.0) is None


def test_nearest_of_two():
    # Two panels both facing -Z, both in front along +Z. Drawing at z=3,
    # text at z=6. Ray along +Z hits both -> nearer (drawing, z=3) returned.
    yaw = -math.pi / 2.0
    pair = _pair("r.s1", 0,
                 draw_center=(0.0, 1.0, 3.0), draw_yaw=yaw,
                 text_center=(0.0, 1.0, 6.0), text_yaw=yaw,
                 dw=2.0, dh=2.0)
    room = _room_runtime(dimensions=(20.0, 3.0, 20.0), pairs=[pair])
    nav = build_room_nav(room)
    ray = Ray(origin=(0.0, 1.0, 0.0), direction=(0.0, 0.0, 1.0))
    hit = nav.nearest_panel(ray, 100.0)
    assert hit is not None
    assert hit.is_drawing is True
    assert math.isclose(hit.distance, 3.0, abs_tol=1e-6)


# ----------------------------------------------------------------------------
# DOOR_AT TESTS
# ----------------------------------------------------------------------------
def test_door_at_inside():
    door = _door("edge.r.to.nbor", "N", center=(0.0, 1.0, 5.0), w=2.0, h=2.0)
    room = _room_runtime(dimensions=(10.0, 3.0, 10.0), doors=[door])
    nav = build_room_nav(room)
    # Point right at the wall plane, within the opening width.
    point = (0.5, 1.0, 5.0 - 0.1)  # within DOOR_TRIGGER_DEPTH_M
    assert nav.door_at(point) == "edge.r.to.nbor"
    # Direct helper check.
    assert point_in_door(point, door) is True


def test_door_at_solid():
    door = _door("edge.r.to.nbor", "N", center=(0.0, 1.0, 5.0), w=2.0, h=2.0)
    room = _room_runtime(dimensions=(10.0, 3.0, 10.0), doors=[door])
    nav = build_room_nav(room)
    # Point on the N wall but far along X (outside the door opening width).
    point = (4.0, 1.0, 5.0 - 0.1)
    assert nav.door_at(point) is None
    assert point_in_door(point, door) is False


def test_door_at_uses_bearing_placed_door():
    # Door placed on N wall but offset along +X (non-center), at a non-cardinal
    # bearing. door_at must find it at its actual center_xyz, not wall center.
    bearing = math.radians(37.0)
    door = _door("edge.r.to.nbor", "N", center=(3.0, 1.0, 5.0),
                 w=1.5, h=2.0, bearing=bearing, normal_yaw=bearing)
    room = _room_runtime(dimensions=(12.0, 3.0, 10.0), doors=[door])
    nav = build_room_nav(room)

    # Wall center (x=0) should NOT register as the door.
    wall_center_point = (0.0, 1.0, 5.0 - 0.1)
    assert nav.door_at(wall_center_point) is None

    # The actual door center offset should register.
    at_door_point = (3.0, 1.0, 5.0 - 0.1)
    assert nav.door_at(at_door_point) == "edge.r.to.nbor"
    assert point_in_door(at_door_point, door) is True
