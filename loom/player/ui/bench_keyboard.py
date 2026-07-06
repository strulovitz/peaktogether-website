"""
bench_keyboard.py — the on-screen piano. [BONE M2]

Scripture: BIBLE par.4-5 (the Simon Principle). One octave by default,
TWO octaves maximum (LOCKED). Keys light up in sync with the melody
(fed by ConductorFrame + the spell's key_index data) and are clickable
by Player M. Clicking makes a sound — always from the spell's OWN
sample palette (never foreign tones), which the wiring provides.

FATTEN ME LIKE THIS (M2 parent): draw from layout.KEYBOARD; expose
hit_test(pos)->midi|None and draw(surface, lit_midis, preview_midi).
No audio in here — return what was pressed; the wiring plays it.
"""

from __future__ import annotations


class KeyboardWidget:
    """Frozen interface."""

    def __init__(self, rect, base_midi: int, octaves: int = 1) -> None:
        raise NotImplementedError("M2")

    def hit_test(self, pos) -> int | None:
        raise NotImplementedError("M2: pixel -> midi (or None)")

    def draw(self, surface, lit_midis, preview_midi=None) -> None:
        raise NotImplementedError("M2")
