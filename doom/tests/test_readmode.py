from __future__ import annotations

from principia.ui.readmode import ReadMode


def test_constructs_closed():
    rm = ReadMode()
    assert rm.is_open() is False


def test_open_close_state_machine():
    rm = ReadMode()
    destroyed = []
    rm._build = lambda texture: ["bg", "img", "hint"]
    rm._destroy = lambda entities: destroyed.extend(entities)

    rm.open("l1_step1", "TEX")
    assert rm.is_open() is True
    assert rm._block_id == "l1_step1"

    rm.close()
    assert rm.is_open() is False
    assert rm._block_id is None
    assert destroyed == ["bg", "img", "hint"]


def test_open_while_open_replaces():
    rm = ReadMode()
    destroyed = []
    builds = iter([["a"], ["b"]])
    rm._build = lambda texture: next(builds)
    rm._destroy = lambda entities: destroyed.extend(entities)

    rm.open("b1", "T")
    rm.open("b2", "T")

    assert rm._block_id == "b2"
    assert rm.is_open() is True
    assert "a" in destroyed  # old overlay torn down before new built


def test_close_is_idempotent():
    rm = ReadMode()
    rm.close()
    rm.close()
    assert rm.is_open() is False
