from __future__ import annotations

import json

import pytest

import principia.config as config
from principia.walls.state import WallStateManager


OFF = "OFF_TEX"
ON = "ON_TEX"


class FakeEntity:
    def __init__(self):
        self.texture = None
        self.is_on = False


def test_init_accepts_none():
    mgr = WallStateManager(None)
    assert mgr.state.__self__ is mgr  # sanity: object built fine


def test_toggle_flips_and_updates_visuals():
    mgr = WallStateManager(None)
    e = FakeEntity()
    mgr.register("room1", "b1", e, OFF, ON)
    assert e.texture == OFF
    assert e.is_on is False

    assert mgr.toggle("b1") is True
    assert e.texture == ON
    assert e.is_on is True

    assert mgr.toggle("b1") is False
    assert e.texture == OFF
    assert e.is_on is False


def test_state_reflects_value():
    mgr = WallStateManager(None)
    e = FakeEntity()
    mgr.register("room1", "b1", e, OFF, ON)
    assert mgr.state("b1") is False
    mgr.toggle("b1")
    assert mgr.state("b1") is True


def test_unknown_block_raises_keyerror():
    mgr = WallStateManager(None)
    with pytest.raises(KeyError):
        mgr.state("nope")
    with pytest.raises(KeyError):
        mgr.toggle("nope")


def test_progress():
    mgr = WallStateManager(None)
    e1, e2 = FakeEntity(), FakeEntity()
    mgr.register("room1", "b1", e1, OFF, ON)
    mgr.register("room1", "b2", e2, OFF, ON)
    assert mgr.progress("room1") == 0.0

    mgr.toggle("b1")
    assert mgr.progress("room1") == 0.5

    mgr.toggle("b2")
    assert mgr.progress("room1") == 1.0

    assert mgr.progress("nonexistent") == 0.0


def test_save_load_round_trip(tmp_path):
    path = str(tmp_path / "s.json")
    mgr = WallStateManager(None)
    e1, e2, e3 = FakeEntity(), FakeEntity(), FakeEntity()
    mgr.register("room1", "b1", e1, OFF, ON)
    mgr.register("room1", "b2", e2, OFF, ON)
    mgr.register("room1", "b3", e3, OFF, ON)
    mgr.toggle("b1")
    mgr.toggle("b3")
    mgr.save(path)

    mgr2 = WallStateManager(None)
    n1, n2, n3 = FakeEntity(), FakeEntity(), FakeEntity()
    mgr2.register("room1", "b1", n1, OFF, ON)
    mgr2.register("room1", "b2", n2, OFF, ON)
    mgr2.register("room1", "b3", n3, OFF, ON)
    mgr2.load(path)

    assert mgr2.state("b1") is True
    assert n1.texture == ON
    assert mgr2.state("b2") is False
    assert n2.texture == OFF
    assert mgr2.state("b3") is True
    assert n3.texture == ON


def test_order_independence_load_before_register(tmp_path):
    path = str(tmp_path / "s.json")
    src = WallStateManager(None)
    e = FakeEntity()
    src.register("room1", "b1", e, OFF, ON)
    src.toggle("b1")
    src.save(path)

    mgr = WallStateManager(None)
    mgr.load(path)  # load BEFORE registering
    new_e = FakeEntity()
    mgr.register("room1", "b1", new_e, OFF, ON)

    assert mgr.state("b1") is True
    assert new_e.texture == ON
    assert new_e.is_on is True


def test_merge_preserves_foreign_keys(tmp_path):
    path = tmp_path / "s.json"
    path.write_text(json.dumps({"demons_dead": ["d1"]}), encoding="utf-8")

    mgr = WallStateManager(None)
    e = FakeEntity()
    mgr.register("room1", "b1", e, OFF, ON)
    mgr.toggle("b1")
    mgr.save(str(path))

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["demons_dead"] == ["d1"]
    assert "blocks_on" in data
    assert data["blocks_on"] == ["b1"]


def test_schema_version_written(tmp_path):
    path = tmp_path / "s.json"
    mgr = WallStateManager(None)
    mgr.save(str(path))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == config.SCHEMA_VERSION


def test_save_handles_unreadable_existing_file(tmp_path):
    path = tmp_path / "s.json"
    path.write_text("{ this is not valid json", encoding="utf-8")
    mgr = WallStateManager(None)
    e = FakeEntity()
    mgr.register("room1", "b1", e, OFF, ON)
    mgr.toggle("b1")
    mgr.save(str(path))  # should not raise; starts from {}
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["blocks_on"] == ["b1"]
    assert data["schema_version"] == config.SCHEMA_VERSION


def test_load_missing_file_is_noop(tmp_path):
    path = str(tmp_path / "does_not_exist.json")
    mgr = WallStateManager(None)
    e = FakeEntity()
    mgr.register("room1", "b1", e, OFF, ON)
    mgr.load(path)  # no file -> do nothing
    assert mgr.state("b1") is False
