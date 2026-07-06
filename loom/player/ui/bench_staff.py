"""
bench_staff.py — the real musical staff, noteheads only. [BONE M2]

Scripture: BIBLE par.4 (LOCKED): treble or grand clef, NOTEHEADS ONLY —
no stems, no beams, no time signatures. Drawing positions come purely
from core/notation.py lookups (which come from notation_table.json).
Zero music theory in this file: it draws circles at looked-up steps.

FATTEN ME LIKE THIS (M2 parent): draw(surface, spell, frame) placing
one notehead per note, highlighting frame.active_note_index and
flash-decaying frame.crossed (use scrub_tuning highlight_decay_ms).
"""

from __future__ import annotations


class StaffWidget:
    """Frozen interface."""

    def __init__(self, rect, notation_table) -> None:
        raise NotImplementedError("M2")

    def draw(self, surface, spell, frame, flash_levels) -> None:
        raise NotImplementedError("M2")
