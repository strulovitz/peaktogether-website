import json

import pytest

from core.spell_model import SpellLoadError, load_spell


def write(tmp_path, data):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


def base(**over):
    d = {"format": "loom-spell", "format_version": "1.0",
         "spell_id": "t", "bpm": 90,
         "notes": [
             {"index": 0, "midi": 60, "start_beat": 0.0, "duration_beats": 1.0,
              "sample": "a.mp3", "gain": 0.9},
             {"index": 1, "midi": 62, "start_beat": 1.0, "duration_beats": 1.0,
              "sample": "b.mp3", "gain": 0.9}]}
    d.update(over)
    return d


def test_loads_and_computes(tmp_path):
    s = load_spell(write(tmp_path, base()))
    assert s.total_beats == 2.0 and len(s.notes) == 2
    assert s.sample_paths == ("a.mp3", "b.mp3")
    assert s.notes[1].end_beat == 2.0


def test_dedupes_samples(tmp_path):
    d = base()
    d["notes"][1]["sample"] = "a.mp3"
    assert load_spell(write(tmp_path, d)).sample_paths == ("a.mp3",)


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(format="something-else"),
    lambda d: d.update(format_version="2.0"),
    lambda d: d.update(bpm=0),
    lambda d: d.update(notes=[]),
    lambda d: d["notes"][1].update(start_beat=0.5),          # overlap
    lambda d: d["notes"][0].update(start_beat=5.0),          # unsorted
    lambda d: d["notes"][1].update(index=7),                 # bad index
    lambda d: d["notes"][0].update(duration_beats=0),
])
def test_rejects_bad_files(tmp_path, mutate):
    d = base()
    mutate(d)
    with pytest.raises(SpellLoadError):
        load_spell(write(tmp_path, d))
