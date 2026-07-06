"""
lab_remap.py — the Laboratory's frozen arithmetic. [BONE M6]

Scripture: New Testament par.I.4 — THE LAB REMAP CONTRACT, frozen so the
Compiler and Player agree forever. The Lab does multiplication, snapping,
and lookup ONLY — never function evaluation (BIBLE par.10):

  1. resample the spell's precompiled dense_values at num_notes points;
  2. normalize each value with the PLANNED range (the dense pass min/max
     stored by the Compiler — so sliders can never escape the range);
  3. map to the new span/base: semitone offset = normalized * span;
  4. snap to the chosen scale's table (ties break DOWNWARD — determinism);
  5. look up the sample for (instrument, midi) in the shipped superset —
     the Lab always uses FORTE (that bounds what packs bundle).

FATTEN ME LIKE THIS (M6 parent): implement remap() returning SpellNote
tuples so a plain Conductor can play the result unchanged — the Lab is
just another spell source. Headless tests: goldens for snapping ties,
span edges, num_notes extremes from lab_ranges. Add to test_purity.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from .spell_model import SpellNote


@dataclass(frozen=True)
class LabSettings:
    span_semitones: int
    bpm: float
    base_midi: int       # base_note as midi (C3/C4/C5 -> 48/60/72)
    scale: str           # "pentatonic_major" | "major" | "natural_minor" | "chromatic"
    num_notes: int
    instrument: str


def remap(spell_raw: dict, settings: LabSettings) -> tuple[SpellNote, ...]:
    """spell_raw = SpellData.raw (has dense_values, planned min/max, lab
    block with sample superset). Returns playable notes. Pure, deterministic."""
    raise NotImplementedError("M6: implement the 5 steps above, exactly")
