"""Headless tests for player/core/notation.py (M2, Parent 3)."""

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from core.notation import NotationTable  # noqa: E402


def make_table(tmp_path, midi_min=59, midi_max=62, mutate=None):
    entries = [
        {"midi": 59, "name": "B3",  "treble_step": -7, "bass_step": 5, "sharp": False},
        {"midi": 60, "name": "C4",  "treble_step": -6, "bass_step": 6, "sharp": False},
        {"midi": 61, "name": "Cs4", "treble_step": -6, "bass_step": 6, "sharp": True},
        {"midi": 62, "name": "D4",  "treble_step": -5, "bass_step": 7, "sharp": False},
    ]
    data = {"format": "loom-notation-table", "format_version": "1.0",
            "midi_min": midi_min, "midi_max": midi_max, "entries": entries}
    if mutate:
        mutate(data)
    p = tmp_path / "notation_table.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def test_load_and_entry(tmp_path):
    t = NotationTable.load(make_table(tmp_path))
    e = t.entry(60)
    assert e.name == "C4" and e.treble_step == -6 and e.bass_step == 6
    assert e.sharp is False
    assert t.entry(61).sharp is True
    assert t.entry(61).treble_step == t.entry(60).treble_step  # sharp shares step


def test_reverse_lookup(tmp_path):
    t = NotationTable.load(make_table(tmp_path))
    assert t.midi_for_name("C4") == 60
    assert t.midi_for_name("Cs4") == 61
    with pytest.raises(KeyError):
        t.midi_for_name("H9")


def test_out_of_range_is_plain_error(tmp_path):
    t = NotationTable.load(make_table(tmp_path))
    with pytest.raises(KeyError):
        t.entry(20)


def test_missing_midi_rejected(tmp_path):
    def drop_one(data):
        data["entries"] = [e for e in data["entries"] if e["midi"] != 61]
    with pytest.raises(ValueError):
        NotationTable.load(make_table(tmp_path, mutate=drop_one))


def test_duplicate_midi_rejected(tmp_path):
    def dup(data):
        data["entries"].append(dict(data["entries"][0]))
    with pytest.raises(ValueError):
        NotationTable.load(make_table(tmp_path, mutate=dup))


def test_wrong_format_rejected(tmp_path):
    def bad(data):
        data["format"] = "something-else"
    with pytest.raises(ValueError):
        NotationTable.load(make_table(tmp_path, mutate=bad))


def test_newer_major_version_refused(tmp_path):
    def newer(data):
        data["format_version"] = "2.0"
    with pytest.raises(ValueError):
        NotationTable.load(make_table(tmp_path, mutate=newer))
