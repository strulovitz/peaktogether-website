"""
spell_model.py — loads a compiled spell JSON into frozen dataclasses. [MEAT]

Scripture: BIBLE v1.1 par.8 (the spell format). The Player is a "dumb
runtime" (BIBLE par.10): this module does NO mathematics — it only reads
numbers the Spell Compiler precomputed, validates their shape, and hands
them to the rest of the game.

M1 consumes only the fields needed by the Conductor and the audio engine
(bpm + per-note timing/midi/sample/gain). Unknown fields are preserved in
SpellData.raw so future modules (graph M2, helix M4, lab M6) can read the
SAME loaded object without touching this file's interface.

Imports: standard library ONLY (see tests/test_purity.py).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


class SpellLoadError(Exception):
    """Raised with a plain-language message Nir can paste to DeepSeek."""


@dataclass(frozen=True)
class SpellNote:
    """One note of the melody. All numbers precomputed by the Compiler."""
    index: int              # position in the melody, 0-based
    midi: int               # unambiguous pitch (comparisons for hints, M3)
    start_beat: float       # region start, in beats
    duration_beats: float   # region length, in beats (region is half-open)
    sample: str             # relative audio path, e.g. "audio/flute_C4_1_forte_normal.mp3"
    gain: float             # compile-time volume multiplier (files ship verbatim)

    @property
    def end_beat(self) -> float:
        return self.start_beat + self.duration_beats


@dataclass(frozen=True)
class SpellData:
    """A loaded spell. seconds = beats * 60 / bpm, and nothing more."""
    spell_id: str
    bpm: float
    notes: tuple[SpellNote, ...]
    total_beats: float
    raw: dict = field(repr=False, compare=False, default_factory=dict)

    @property
    def sample_paths(self) -> tuple[str, ...]:
        """Every sample the audio engine must preload (order preserved,
        duplicates removed)."""
        seen: dict[str, None] = {}
        for n in self.notes:
            seen.setdefault(n.sample, None)
        return tuple(seen.keys())


def load_spell(path: str) -> SpellData:
    """Read and validate a spell JSON file.

    Refuses (with plain-language errors): wrong format tag, a newer major
    format_version, missing/empty notes, unsorted notes, overlapping note
    regions, non-positive bpm or durations. Gaps between regions (rests)
    are legal. Unknown fields are ignored here and kept in .raw.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SpellLoadError(f"Spell file not found: {path}")
    except json.JSONDecodeError as e:
        raise SpellLoadError(f"Spell file {path} is not valid JSON: {e}")

    if data.get("format") != "loom-spell":
        raise SpellLoadError(
            f"{path}: 'format' must be 'loom-spell', got {data.get('format')!r}.")

    version = str(data.get("format_version", ""))
    major = version.split(".", 1)[0]
    if major != "1":
        raise SpellLoadError(
            f"{path}: this Player understands format 1.x spells, "
            f"but the file says {version!r}. Please recompile the spell "
            f"or update the Player.")

    bpm = float(data.get("bpm", 0))
    if bpm <= 0:
        raise SpellLoadError(f"{path}: bpm must be a positive number, got {bpm}.")

    raw_notes = data.get("notes")
    if not raw_notes:
        raise SpellLoadError(f"{path}: the spell has no notes.")

    notes: list[SpellNote] = []
    for pos, rn in enumerate(raw_notes):
        try:
            note = SpellNote(
                index=int(rn["index"]),
                midi=int(rn["midi"]),
                start_beat=float(rn["start_beat"]),
                duration_beats=float(rn["duration_beats"]),
                sample=str(rn["sample"]),
                gain=float(rn.get("gain", 1.0)),
            )
        except (KeyError, TypeError, ValueError) as e:
            raise SpellLoadError(
                f"{path}: note at position {pos} is malformed ({e}).")
        if note.index != pos:
            raise SpellLoadError(
                f"{path}: note at position {pos} has index {note.index}; "
                f"indices must be 0,1,2,... in order.")
        if note.duration_beats <= 0:
            raise SpellLoadError(
                f"{path}: note {pos} has non-positive duration "
                f"{note.duration_beats}.")
        notes.append(note)

    for a, b in zip(notes, notes[1:]):
        if b.start_beat < a.start_beat:
            raise SpellLoadError(
                f"{path}: notes {a.index} and {b.index} are not sorted by "
                f"start_beat.")
        if b.start_beat < a.end_beat - 1e-9:
            raise SpellLoadError(
                f"{path}: notes {a.index} and {b.index} overlap in time; "
                f"note regions must never overlap (gaps are fine).")

    total_beats = max(n.end_beat for n in notes)
    return SpellData(
        spell_id=str(data.get("spell_id", "unknown")),
        bpm=bpm,
        notes=tuple(notes),
        total_beats=total_beats,
        raw=data,
    )
