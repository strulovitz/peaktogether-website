import math

from build.room_geometry import (
    WallSubSeg,
    bearing_to_wall_hit,
    nudge_doors,
    s_to_wall_along,
    subdivide_perimeter,
    wall_along_to_s,
)


# --- bearing_to_wall_hit ---


def test_bearing_east():
    hit = bearing_to_wall_hit(0.0, 10.0, 8.0)
    assert hit.wall == "E"
    assert abs(hit.along - 0.0) < 1e-9


def test_bearing_north():
    hit = bearing_to_wall_hit(math.pi / 2, 10.0, 8.0)
    assert hit.wall == "N"
    assert abs(hit.along - 0.0) < 1e-9


def test_bearing_west():
    hit = bearing_to_wall_hit(math.pi, 10.0, 8.0)
    assert hit.wall == "W"
    assert abs(hit.along - 0.0) < 1e-9


def test_bearing_south():
    hit = bearing_to_wall_hit(-math.pi / 2, 10.0, 8.0)
    assert hit.wall == "S"
    assert abs(hit.along - 0.0) < 1e-9


def test_central_direction_exact():
    theta = 0.7
    W, D = 10.0, 8.0
    hit = bearing_to_wall_hit(theta, W, D)
    if hit.wall in ("E", "W"):
        x = W / 2 if hit.wall == "E" else -W / 2
        z = hit.along
    else:
        x = hit.along
        z = D / 2 if hit.wall == "N" else -D / 2
    actual_theta = math.atan2(z, x)
    diff = abs(actual_theta - theta)
    diff = min(diff, 2 * math.pi - diff)
    assert diff < 1e-9


def test_corner_tie_resolved():
    theta = math.atan2(4.0, 5.0)
    W, D = 10.0, 8.0
    hit = bearing_to_wall_hit(theta, W, D)
    assert hit.wall == "E"


# --- wall_along_to_s / s_to_wall_along ---


def test_round_trip_n_wall():
    s = wall_along_to_s("N", 2.5, 10.0, 8.0)
    wall, along = s_to_wall_along(s, 10.0, 8.0)
    assert wall == "N"
    assert abs(along - 2.5) < 1e-9


def test_round_trip_e_wall():
    s = wall_along_to_s("E", -1.0, 10.0, 8.0)
    wall, along = s_to_wall_along(s, 10.0, 8.0)
    assert wall == "E"
    assert abs(along - (-1.0)) < 1e-9


def test_round_trip_s_wall():
    s = wall_along_to_s("S", -3.0, 10.0, 8.0)
    wall, along = s_to_wall_along(s, 10.0, 8.0)
    assert wall == "S"
    assert abs(along - (-3.0)) < 1e-9


def test_round_trip_w_wall():
    s = wall_along_to_s("W", 1.5, 10.0, 8.0)
    wall, along = s_to_wall_along(s, 10.0, 8.0)
    assert wall == "W"
    assert abs(along - 1.5) < 1e-9


# --- nudge_doors ---


def test_nudge_no_nudge_needed():
    P = 36.0
    doors_s = [5.0, 15.0, 25.0]
    widths = [2.0, 2.0, 2.0]
    corners = [0.0, 10.0, 18.0, 28.0]
    result = nudge_doors(doors_s, widths, P, corners, 0.5, 2.6)
    for r, o in zip(result, doors_s):
        assert abs(r - o) < 0.01


def test_nudge_separation():
    P = 36.0
    doors_s = [5.0, 5.5]
    widths = [2.0, 2.0]
    corners = [0.0, 10.0, 18.0, 28.0]
    result = nudge_doors(doors_s, widths, P, corners, 0.5, 2.6)
    assert result[1] - result[0] >= 2.6


def test_nudge_near_corner():
    P = 36.0
    doors_s = [9.7]
    widths = [2.0]
    corners = [0.0, 10.0, 18.0, 28.0]
    result = nudge_doors(doors_s, widths, P, corners, 0.5, 2.6)
    assert result[0] >= 11.5


def test_nudge_infeasible():
    P = 36.0
    doors_s = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    widths = [2.0] * 6
    corners = [0.0, 10.0, 18.0, 28.0]
    try:
        nudge_doors(doors_s, widths, P, corners, 0.5, 2.6)
        assert False, "should have raised"
    except ValueError as e:
        assert "NudgeInfeasible" in str(e)


# --- subdivide_perimeter ---


def test_subdivide_one_door():
    W, D = 10.0, 8.0
    doors_s = [5.0]
    widths = [2.0]
    result = subdivide_perimeter(doors_s, widths, W, D, 0.6)
    walls = {seg.wall for seg in result}
    assert "N" in walls
    assert "E" in walls
    assert "S" in walls
    assert "W" in walls
    for seg in result:
        assert seg.length_m > 0


def test_subdivide_no_doors():
    W, D = 10.0, 8.0
    result = subdivide_perimeter([], [], W, D, 0.6)
    assert len(result) == 4
    for seg in result:
        assert seg.length_m > 0


def test_subdivide_wall_margin():
    W, D = 10.0, 8.0
    result = subdivide_perimeter([], [], W, D, 0.6)
    for seg in result:
        if seg.wall in ("N", "S"):
            assert abs(seg.length_m - (W - 1.2)) < 1e-9
        else:
            assert abs(seg.length_m - (D - 1.2)) < 1e-9
