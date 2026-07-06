"""Validates the generated M2 fixtures (design-time generator output)."""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(HERE), "fixtures", "make_bench_fixtures.py")

spec = importlib.util.spec_from_file_location("make_bench_fixtures", GEN)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def built():
    import math
    line = gen.build("t8", "t", "f(x)=x", lambda x: x, 8, 65,
                     60, 12, gen.MAJOR, "violin", "arco-normal", 60, 72)
    root = gen.build("t20", "t", "f(x)=sqrt(x)", math.sqrt, 20, 200,
                     48, 24, gen.CHROMATIC, "cello", "arco-normal", 48, 72)
    return line, root


def test_segments_tile_zero_to_one():
    for s in built():
        segs = [n["graph_segment"] for n in s["notes"]]
        assert segs[0]["x_from"] == 0.0
        assert segs[-1]["x_to"] == 1.0
        for a, b in zip(segs, segs[1:]):
            assert abs(a["x_to"] - b["x_from"]) < 1e-9


def test_midis_inside_keyboard_window():
    line, root = built()
    for n in line["notes"]:
        assert 60 <= n["midi"] <= 72
    for n in root["notes"]:
        assert 48 <= n["midi"] <= 72
    # the sqrt fixture must actually exercise black keys + bass staff
    assert any(n["midi"] % 12 in (1, 3, 6, 8, 10) for n in root["notes"])
    assert any(n["midi"] < 60 for n in root["notes"])


def test_key_index_consistency():
    for s in built():
        base = {"t8": 60, "t20": 48}[s["spell_id"]]
        for n in s["notes"]:
            assert n["key_index"] == n["midi"] - base


def test_graph_points_normalized_and_monotone_x():
    for s in built():
        pts = s["graph"]["points"]
        assert pts[0][0] == 0.0 and pts[-1][0] == 1.0
        assert all(0.0 <= y <= 1.0 for _, y in pts)
        assert all(a[0] < b[0] for a, b in zip(pts, pts[1:]))
