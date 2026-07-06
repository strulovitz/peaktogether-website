"""
lab_view.py — the Laboratory sliders. [BONE M6]

Scripture: BIBLE par.3/par.15 (Lab is IN for v1, LOCKED) + New Testament
par.I.4. Sliders: tempo, span, base note, scale, instrument, note count
— each bounded by the spell's lab_ranges (the Compiler's promise of
what samples shipped). On change: call core/lab_remap.remap(), build
the new note tuple, hand it to a fresh Conductor — then everything
(scrubbing included!) just works, because the Lab output IS a spell.

FATTEN ME LIKE THIS (M6 parent): slider widgets + one one debounce; the
heavy lifting is already frozen in lab_remap. Fun fact to preserve:
changing a slider mid-scrub should feel instant (remap is pure lookup).
"""

from __future__ import annotations


class LabView:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        raise NotImplementedError("M6")

    def handle_event(self, pygame_event, spell_raw) -> object | None:
        """Returns a new LabSettings when a slider commits, else None."""
        raise NotImplementedError("M6")

    def draw(self, surface, settings) -> None:
        raise NotImplementedError("M6")
