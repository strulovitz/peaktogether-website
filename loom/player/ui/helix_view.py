"""
helix_view.py — the demoscene pitch helix. [BONE M4]

Scripture: BIBLE par.7 (LOCKED normalization): angle = 30 degrees *
(semitone mod 12); z = semitone / 12 (one octave = 1.0 height).
Software 3D wireframe — NO OpenGL (LOCKED): project points yourself,
draw lines. Slow idle rotation; the active note's bead glows and
crossed notes flash, all driven by ConductorFrame like every renderer.

FATTEN ME LIKE THIS (M4 parent): pure projection math on the spell's
precompiled helix block (the Compiler ships per-note angle/z — this
file only rotates, projects, draws). Keep it under ~200 lines; it is
a jewel, not an engine.
"""

from __future__ import annotations


class HelixView:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        raise NotImplementedError("M4")

    def draw(self, surface, spell, frame, flash_levels, dt_s: float) -> None:
        raise NotImplementedError("M4")
