import os
import json
import tempfile

import pytest

from state import new_state, load, save, state_to_save, save_to_state
from contracts import (
    GameState,
    SaveGame,
    PlayerSave,
    LevelProgress,
    RoomProgress,
    Pack,
    Floorplan,
    FloorRoom,
)


def _stub_pack():
    rooms = [
        FloorRoom(room_id="alpha", map_xz=(10.0, 20.0), importance=3,
                  map_radius_m=2.0, map_color="#ffffff", socket_y=0.5),
        FloorRoom(room_id="beta", map_xz=(30.0, 40.0), importance=1,
                  map_radius_m=2.0, map_color="#ffffff", socket_y=1.0),
    ]
    fp = Floorplan(schema_version="1.0", level_id="l1", seed=1,
                   rooms=rooms, corridors=[], crossings=[])
    return Pack(floorplan=fp, rooms={}, manifest=None, palette=None, asset_dir=".")


def test_new_state_starts_in_room():
    pack = _stub_pack()
    state = new_state(pack)

    assert state.mode == "room"
    assert state.current_room_id == "alpha"   # lexicographically first room
    assert state.lit == set()
    assert state.cleared == set()
    # pack.rooms is empty in stub, so pos defaults to origin
    assert state.pos == (0.0, 0.0, 0.0)
    assert state.heading_rad == 0.0
    assert state.pitch_rad == 0.0
    assert state.save.profile_id == "default"
    assert "l1" in state.save.levels


def test_roundtrip():
    pack = _stub_pack()
    state = new_state(pack)

    state.pos = (1.0, 2.0, 3.0)
    state.heading_rad = 1.5
    state.lit = {"r.s0"}
    state.cleared = {"alpha"}
    state.mode = "room"
    state.current_room_id = "alpha"
    # gameplay keeps player block + levels current; mirror that here.
    state.save.player.mode = "room"
    state.save.player.current_room_id = "alpha"
    state.save.levels["l1"].rooms["alpha"] = RoomProgress(
        pairs_on=["r.s0"], room_cleared=True
    )

    s = state_to_save(state)
    state2 = save_to_state(s, pack)

    assert state2.pos == (1.0, 2.0, 3.0)
    assert state2.heading_rad == 1.5
    assert state2.mode == "room"
    assert state2.current_room_id == "alpha"
    assert state2.lit == {"r.s0"}
    assert state2.cleared == {"alpha"}


def test_pitch_not_persisted():
    pack = _stub_pack()
    state = new_state(pack)
    state.pitch_rad = 0.5

    s = state_to_save(state)
    state2 = save_to_state(s, pack)

    assert state2.pitch_rad == 0.0


def test_atomic_write(monkeypatch):
    pack = _stub_pack()
    state = new_state(pack)

    calls = []
    real_replace = os.replace

    def fake_replace(src, dst):
        calls.append((src, dst))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", fake_replace)

    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, "save.json")
        save(state, target)

        assert len(calls) == 1
        src, dst = calls[0]
        assert src.endswith(".atomic_tmp")
        assert dst == target
        assert os.path.exists(target)
        # The target should be valid JSON we can reload.
        with open(target, encoding="utf-8") as f:
            data = json.load(f)
        assert data["schema_version"] == "1.0"


def test_schema_assert():
    pack = _stub_pack()
    with tempfile.TemporaryDirectory() as d:
        bad_path = os.path.join(d, "bad.json")
        with open(bad_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "schema_version": "0.9",
                    "profile_id": "default",
                    "levels": {},
                    "player": {
                        "level_id": "l1",
                        "mode": "corridor",
                        "current_room_id": None,
                        "position_xyz": [0.0, 0.0, 0.0],
                        "heading_rad": 0.0,
                    },
                },
                f,
            )
        with pytest.raises(Exception):
            load(bad_path, pack)


def test_forward_compat_drop():
    pack = _stub_pack()  # pack.rooms is empty -> any room_id is "unknown"

    bad_save = SaveGame(
        schema_version="1.0",
        profile_id="default",
        levels={
            "l1": LevelProgress(
                rooms={"ghost": RoomProgress(pairs_on=[], room_cleared=False)}
            )
        },
        player=PlayerSave(
            level_id="l1",
            mode="corridor",
            current_room_id=None,
            position_xyz=(0.0, 0.0, 0.0),
            heading_rad=0.0,
        ),
    )

    with tempfile.TemporaryDirectory() as d:
        target = os.path.join(d, "save.json")
        with open(target, "w", encoding="utf-8") as f:
            f.write(bad_save.model_dump_json(indent=2))

        with pytest.warns(UserWarning):
            state = load(target, pack)

        assert "ghost" not in state.save.levels["l1"].rooms
