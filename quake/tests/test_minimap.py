"""Tests for the flat-pivot minimap HUD (pure core only — no GL)."""
from types import SimpleNamespace

import os

from minimap import (compute_box, project_rooms, marker_mood, hex_to_rgb,
                     MOOD_FILE, _EMOJI_DIR)


def test_hex_to_rgb():
    assert hex_to_rgb("#ffffff") == (1.0, 1.0, 1.0)
    assert hex_to_rgb("000000") == (0.0, 0.0, 0.0)
    r, g, b = hex_to_rgb("#804020")
    assert abs(r - 128 / 255) < 1e-6 and abs(g - 64 / 255) < 1e-6 and abs(b - 32 / 255) < 1e-6
    # malformed -> safe fallback
    assert hex_to_rgb("nope") == (0.8, 0.8, 0.85)


def test_compute_box_square_on_screen():
    aspect = 1280 / 720
    x0, y0, x1, y1 = compute_box(aspect, side_y=0.56, margin=0.04)
    assert x1 <= 1.0 and y1 <= 1.0
    assert x0 < x1 and y0 < y1
    # box must be square in PIXELS: ndc-x width * (w/2) == ndc-y height * (h/2)
    w, h = 1280, 720
    px_w = (x1 - x0) * (w / 2)
    px_h = (y1 - y0) * (h / 2)
    assert abs(px_w - px_h) < 1e-3


def test_project_rooms_inside_box_and_undistorted():
    aspect = 1280 / 720
    box = compute_box(aspect)
    x0, y0, x1, y1 = box
    rooms = {
        "c": (0.0, 0.0),
        "e": (10.0, 0.0), "w": (-10.0, 0.0),
        "s": (0.0, 10.0), "n": (0.0, -10.0),
    }
    pos = project_rooms(rooms, box, aspect)
    # every room maps inside the box
    for (mx, my) in pos.values():
        assert x0 - 1e-6 <= mx <= x1 + 1e-6
        assert y0 - 1e-6 <= my <= y1 + 1e-6
    # center room lands at the box center
    bcx, bcy = (x0 + x1) / 2, (y0 + y1) / 2
    assert abs(pos["c"][0] - bcx) < 1e-6
    assert abs(pos["c"][1] - bcy) < 1e-6
    # undistorted: equal world deltas -> equal SCREEN (pixel) deltas.
    dx = abs(pos["e"][0] - bcx)     # NDC-x for 10 world units in x
    dy = abs(pos["s"][1] - bcy)     # NDC-y for 10 world units in z
    assert abs(dy - aspect * dx) < 1e-6


def test_project_rooms_empty():
    assert project_rooms({}, compute_box(1.7), 1.7) == {}


def _state(cleared=(), rooms_prog=None, current="r1"):
    levels = {}
    if rooms_prog is not None:
        rooms = {rid: SimpleNamespace(**prog) for rid, prog in rooms_prog.items()}
        levels["lvl1"] = SimpleNamespace(rooms=rooms)
    save = SimpleNamespace(levels=levels)
    return SimpleNamespace(cleared=set(cleared), save=save, current_room_id=current)


def test_mood_cleared_beats_all():
    st = _state(cleared={"r1"})
    assert marker_mood(st, "lvl1", "r1", moved=True) == "cleared"


def test_mood_demon_when_door_open():
    st = _state(rooms_prog={"r1": {"hidden_door_open": True, "pairs_on": ["a"]}})
    assert marker_mood(st, "lvl1", "r1", moved=True) == "demon"


def test_mood_panels_when_lit():
    st = _state(rooms_prog={"r1": {"hidden_door_open": False, "pairs_on": ["a"]}})
    assert marker_mood(st, "lvl1", "r1", moved=True) == "panels"


def test_mood_arrived_vs_moving():
    st = _state(rooms_prog={"r1": {"hidden_door_open": False, "pairs_on": []}})
    assert marker_mood(st, "lvl1", "r1", moved=False) == "arrived"
    assert marker_mood(st, "lvl1", "r1", moved=True) == "moving"
    # fresh arrival with no progress at all
    assert marker_mood(_state(rooms_prog=None), "lvl1", "r1", moved=False) == "arrived"


def test_all_moods_have_existing_png():
    for mood in ("arrived", "moving", "panels", "demon", "cleared"):
        assert mood in MOOD_FILE
        assert os.path.exists(os.path.join(_EMOJI_DIR, MOOD_FILE[mood]))
