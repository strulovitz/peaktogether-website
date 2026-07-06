"""
bench_keyboard.py — the on-screen piano. [M2 — Parent 3]

Scripture: BIBLE par.2, par.4-5 (the Simon Principle). One octave by
default, TWO octaves maximum (LOCKED). Keys light in sync with the
melody (fed by ConductorFrame flash levels via the wiring) and are
clickable by Player M. NO AUDIO in here: hit_test returns the midi;
the wiring plays it (always from the spell's OWN sample palette).

Geometry: the keyboard runs from base_midi (must be a C) to
base_midi + 12*octaves INCLUSIVE (C to C, like a real short keyboard):
7*octaves + 1 white keys, 5*octaves black keys. White keys are equal
rectangles across the widget rect; black keys are narrower (60%) and
shorter (62%), overlaid on the C-D, D-E, F-G, G-A, A-B boundaries.
Hit-testing checks black keys FIRST (they sit on top).

draw(surface, lit_midis, preview_midi):
  lit_midis     mapping {midi: flash_level 0..1} (a set is accepted and
                treated as level 1.0) — playback/scrub highlights.
  preview_midi  the key Player M is currently auditioning (pressed /
                provisional), drawn with a bright outline.
"""

from __future__ import annotations

import pygame

_WHITE_SEMIS = (0, 2, 4, 5, 7, 9, 11)          # C D E F G A B offsets
_BLACK_SEMIS = (1, 3, 6, 8, 10)                # Cs Ds Fs Gs As offsets
# black key sits on the boundary AFTER white index: C-D, D-E, F-G, G-A, A-B
_BLACK_AFTER_WHITE = (0, 1, 3, 4, 5)

_GLOW = (255, 196, 64)
_WHITE_IDLE = (235, 235, 235)
_BLACK_IDLE = (25, 25, 28)
_OUTLINE = (70, 70, 80)
_PREVIEW = (240, 220, 120)


def _blend(base, glow, k):
    return tuple(int(b + (g - b) * k) for b, g in zip(base, glow))


class KeyboardWidget:
    """Frozen interface."""

    def __init__(self, rect, base_midi: int, octaves: int = 1) -> None:
        if octaves not in (1, 2):
            raise ValueError(f"octaves must be 1 or 2 (LOCKED), got {octaves}")
        if base_midi % 12 != 0:
            raise ValueError(
                f"base_midi {base_midi} is not a C — the keyboard window "
                "must start on a C (Compiler Stage 5 rule)")
        self.rect = pygame.Rect(rect)
        self.base_midi = base_midi
        self.octaves = octaves

        n_white = 7 * octaves + 1
        ww = self.rect.w / n_white
        wh = self.rect.h
        self._white = []            # list of (pygame.Rect, midi)
        self._black = []
        for w in range(n_white):
            octave, pos = divmod(w, 7)
            midi = base_midi + 12 * octave + _WHITE_SEMIS[pos]
            # DeepSeek integration fix (flagged to Fable): tile white keys
            # edge-to-edge (was round(ww)-1, which left a 1px dead gap at
            # each seam so a click exactly on a boundary hit nothing). The
            # 1px _OUTLINE drawn in draw() still separates keys visually.
            x_this = round(self.rect.x + w * ww)
            x_next = round(self.rect.x + (w + 1) * ww)
            r = pygame.Rect(x_this, self.rect.y, x_next - x_this, wh)
            self._white.append((r, midi))
        bw, bh = ww * 0.6, wh * 0.62
        for octave in range(octaves):
            for b, after in enumerate(_BLACK_AFTER_WHITE):
                w = octave * 7 + after
                cx = self.rect.x + (w + 1) * ww          # boundary after white w
                midi = base_midi + 12 * octave + _BLACK_SEMIS[b]
                r = pygame.Rect(round(cx - bw / 2), self.rect.y,
                                round(bw), round(bh))
                self._black.append((r, midi))

    def hit_test(self, pos) -> int | None:
        for r, midi in self._black:                       # black first: on top
            if r.collidepoint(pos):
                return midi
        for r, midi in self._white:
            if r.collidepoint(pos):
                return midi
        return None

    def draw(self, surface, lit_midis, preview_midi=None) -> None:
        levels = (lit_midis if isinstance(lit_midis, dict)
                  else {m: 1.0 for m in (lit_midis or ())})
        for r, midi in self._white:
            k = min(1.0, max(0.0, levels.get(midi, 0.0)))
            pygame.draw.rect(surface, _blend(_WHITE_IDLE, _GLOW, k), r)
            pygame.draw.rect(surface, _OUTLINE, r, 1)
        for r, midi in self._black:
            k = min(1.0, max(0.0, levels.get(midi, 0.0)))
            pygame.draw.rect(surface, _blend(_BLACK_IDLE, _GLOW, k), r)
            pygame.draw.rect(surface, _OUTLINE, r, 1)
        if preview_midi is not None:
            for r, midi in self._black + self._white:
                if midi == preview_midi:
                    pygame.draw.rect(surface, _PREVIEW, r.inflate(4, 4), 3)
                    break
