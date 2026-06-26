"""Tests for quake/assets.py (M6 module #9). Headless: no GL, no window."""

from __future__ import annotations

import json
import os

import pytest

from assets import load_pack


# --------------------------------------------------------------------------- #
# Minimal valid JSON data builders — actual pydantic field names.
# --------------------------------------------------------------------------- #

def _floorplan(room_ids=("r",)):
    return {
        "schema_version": "1.0",
        "level_id": "l1",
        "seed": 1,
        "rooms": [
            {
                "room_id": rid,
                "map_xz": [0.0, 0.0],
                "importance": 3,
                "map_radius_m": 2.0,
                "map_color": "#ffffff",
                "socket_y": 0.0,
            }
            for rid in room_ids
        ],
        "corridors": [],
        "crossings": [],
    }


def _palette(include_importance_3=True):
    map_importance = {
        "1": "#111111",
        "2": "#222222",
        "3": "#333333",
        "4": "#444444",
        "5": "#555555",
    }
    if not include_importance_3:
        del map_importance["3"]
    return {
        "schema_version": "1.0",
        "pack_id": "p1",
        "groups": {},
        "grey_ink": "#202020",
        "grey_text": "#303030",
        "bg_key": "#0a0a0a",
        "map_importance": map_importance,
        "map_node_default": "#cccccc",
    }


def _asset_entry(asset_id, kind, wall_path, master_path):
    return {
        "asset_id": asset_id,
        "kind": kind,
        "wall_path": wall_path,
        "master_path": master_path,
        "px_w": 256,
        "px_h": 256,
        "content_bbox": [0, 0, 256, 256],
        "dpi": 300,
    }


def _manifest(assets):
    return {
        "schema_version": "1.0",
        "level_id": "l1",
        "assets": assets,
    }


def _placement(wall="N", slot_index=0, wall_slot="n0",
               center=None, w=1.0, h=1.0, yaw=0.0):
    # PanelPlacementRT: wall(Literal N/E/S/W), slot_index(int), wall_slot(str),
    # center_xyz(Vec3), width_m, height_m, yaw_rad
    return {
        "wall": wall,
        "slot_index": slot_index,
        "wall_slot": wall_slot,
        "center_xyz": center or [0.0, 0.0, 0.0],
        "width_m": w,
        "height_m": h,
        "yaw_rad": yaw,
    }


def _panel_pair(pair_id="r.s0", step_index=0,
                draw_off="a_doff", draw_on="a_don",
                text_off="a_toff", text_on="a_ton"):
    return {
        "pair_id": pair_id,
        "step_index": step_index,
        "drawing_off_asset": draw_off,
        "drawing_on_asset": draw_on,
        "text_off_asset": text_off,
        "text_on_asset": text_on,
        "drawing_placement": _placement("N", 0, "n0", [-1.0, 1.5, 3.0], 2.0, 1.5, 3.14159),
        "text_placement": _placement("N", 1, "n1", [1.0, 1.5, 3.0], 2.0, 1.5, 3.14159),
    }


def _ceiling_eq(eq_id="r.eq0", asset_id="a_ceil"):
    return {
        "eq_id": eq_id,
        "asset_id": asset_id,
        "pos_xyz": [0.0, 2.9, 0.0],
        "size_m": [1.0, 1.0],
    }


def _door():
    # DoorRT: edge_id, neighbor_id, bearing_rad, wall, center_xyz,
    # width_m, height_m, normal_yaw_rad, spawn_xyz, spawn_heading_rad
    return {
        "edge_id": "edge.r.to.n",
        "neighbor_id": "n",
        "bearing_rad": 0.0,
        "wall": "S",
        "center_xyz": [0.0, 1.5, -3.0],
        "width_m": 2.0,
        "height_m": 2.6,
        "normal_yaw_rad": 0.0,
        "spawn_xyz": [0.0, 0.0, -2.0],
        "spawn_heading_rad": 0.0,
    }


def _enemy():
    # EnemyRT: enemy_id (pattern *\.demon), spawn_xyz, health
    return {
        "enemy_id": "test.demon",
        "spawn_xyz": [0.0, 0.0, 0.0],
        "health": 5,
    }


def _room_runtime(room_id="r", final_pair_id="r.s0",
                  panel_pairs=None, ceiling_equations=None):
    if panel_pairs is None:
        panel_pairs = [_panel_pair()]
    if ceiling_equations is None:
        ceiling_equations = [_ceiling_eq()]
    return {
        "schema_version": "1.0",
        "room_id": room_id,
        "dimensions_m": [6.0, 3.0, 6.0],
        "panel_pairs": panel_pairs,
        "final_pair_id": final_pair_id,
        "hidden_door_wall_slot": "n3",
        "doors": [_door()],
        "enemy": _enemy(),
        "ceiling_equations": ceiling_equations,
    }


# --------------------------------------------------------------------------- #
# Filesystem fixture helpers.
# --------------------------------------------------------------------------- #

def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _touch_png(dir_path, rel_path):
    full = os.path.join(dir_path, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")


def _referenced_asset_ids():
    return ["a_doff", "a_don", "a_toff", "a_ton", "a_ceil"]


def _build_full_manifest(dir_path, asset_ids, create_files=True):
    assets = {}
    kinds = {
        "a_doff": "figure_off",
        "a_don": "figure_on",
        "a_toff": "text_off",
        "a_ton": "text_on",
        "a_ceil": "ceiling_neutral",
    }
    for aid in asset_ids:
        wall = os.path.join("png", "wall", f"{aid}.png")
        master = os.path.join("png", "master", f"{aid}.png")
        assets[aid] = _asset_entry(aid, kinds.get(aid, "figure_off"), wall, master)
        if create_files:
            _touch_png(dir_path, wall)
            _touch_png(dir_path, master)
    return _manifest(assets)


def _build_golden(tmp_path,
                  floorplan_room_ids=("r",),
                  room_id="r",
                  palette_importance_3=True,
                  extra_asset_ids=None,
                  create_pngs=True):
    dir_path = str(tmp_path)
    asset_ids = list(_referenced_asset_ids())
    if extra_asset_ids:
        asset_ids += list(extra_asset_ids)

    _write_json(os.path.join(dir_path, "floorplan.json"),
                _floorplan(floorplan_room_ids))
    _write_json(os.path.join(dir_path, "palette.json"),
                _palette(include_importance_3=palette_importance_3))
    _write_json(os.path.join(dir_path, "manifest.json"),
                _build_full_manifest(dir_path, asset_ids, create_files=create_pngs))
    _write_json(os.path.join(dir_path, "room_runtime", "room_r.json"),
                _room_runtime(room_id=room_id))
    return dir_path


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #

def test_loads_golden_pack(tmp_path):
    dir_path = _build_golden(tmp_path)
    pack = load_pack(dir_path)

    # rooms dict keyed by room_id ("r")
    assert "r" in pack.rooms
    assert pack.rooms["r"].room_id == "r"

    # manifest.assets non-empty
    assert len(pack.manifest.assets) > 0

    # floorplan.rooms contains the room
    fp_ids = {fr.room_id for fr in pack.floorplan.rooms}
    assert "r" in fp_ids

    # palette is valid (reserved keys present)
    for key in ("1", "2", "3", "4", "5"):
        assert key in pack.palette.map_importance

    # asset_dir resolves to the pack dir
    assert pack.asset_dir == dir_path


def test_asserts_schema(tmp_path):
    dir_path = _build_golden(tmp_path)
    bad = _floorplan()
    bad["schema_version"] = "0.9"
    _write_json(os.path.join(dir_path, "floorplan.json"), bad)

    with pytest.raises((ValueError, Exception)) as exc:
        load_pack(dir_path)
    assert exc.value is not None


def test_missing_asset_ref(tmp_path):
    dir_path = _build_golden(tmp_path)
    room = _room_runtime(
        room_id="r",
        panel_pairs=[_panel_pair(text_on="ghost_asset")],
        ceiling_equations=[],
    )
    _write_json(os.path.join(dir_path, "room_runtime", "room_r.json"), room)

    with pytest.raises(ValueError) as exc:
        load_pack(dir_path)
    assert "ghost_asset" in str(exc.value)


def test_spine_mismatch(tmp_path):
    dir_path = str(tmp_path)
    asset_ids = list(_referenced_asset_ids())

    _write_json(os.path.join(dir_path, "floorplan.json"),
                _floorplan(room_ids=("a",)))
    _write_json(os.path.join(dir_path, "palette.json"), _palette())
    _write_json(os.path.join(dir_path, "manifest.json"),
                _build_full_manifest(dir_path, asset_ids, create_files=True))
    _write_json(os.path.join(dir_path, "room_runtime", "room_r.json"),
                _room_runtime(room_id="b"))

    with pytest.raises(ValueError) as exc:
        load_pack(dir_path)
    assert "b" in str(exc.value)


def test_missing_png_path(tmp_path):
    dir_path = _build_golden(tmp_path, create_pngs=False)

    with pytest.raises(ValueError) as exc:
        load_pack(dir_path)
    msg = str(exc.value)
    assert ".png" in msg


def test_palette_reserved_keys(tmp_path):
    dir_path = _build_golden(tmp_path, palette_importance_3=False)

    with pytest.raises(ValueError) as exc:
        load_pack(dir_path)
    msg = str(exc.value)
    assert "map_importance" in msg or "3" in msg
