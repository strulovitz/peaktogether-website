"""
bench_keyboard.py — the on-screen piano. [M2 — Parent 3, rev 2]

Scripture: BIBLE par.2, par.4-5 (the Simon Principle). One octave by
default, TWO octaves maximum (LOCKED). NO AUDIO in here: hit_test
returns the midi; the wiring plays it.

Geometry: base_midi (must be a C) to base_midi + 12*octaves INCLUSIVE:
7*octaves + 1 white keys, 5*octaves black keys, equal white widths
across the rect; blacks 60% width / 62% height on the C-D, D-E, F-G,
G-A, A-B boundaries. Hit-testing checks black keys FIRST.

draw(surface, lit_midis, preview_midi=None, pressed_midi=None):
  lit_midis     {midi: flash_level 0..1} (set accepted = level 1.0)
  preview_midi  provisional/audition key: bright outline (persists)
  pressed_midi  key currently held by the mouse: drawn PRESSED
                (darker, nudged down, shadow edge — per Nir, rev 2)
"""

from __future__ import annotations

import pygame

_WHITE_SEMIS = (0, 2, 4, 5, 7, 9, 11)
_BLACK_SEMIS = (1, 3, 6, 8, 10)
_BLACK_AFTER_WHITE = (0, 1, 3, 4, 5)

_GLOW = (255, 196, 64)
_WHITE_IDLE = (235, 235, 235)
_WHITE_PRESSED = (185, 185, 190)
_BLACK_IDLE = (25, 25, 28)
_BLACK_PRESSED = (70, 70, 78)
_OUTLINE = (70, 70, 80)
_SHADOW = (10, 10, 12)
_PREVIEW = (240, 220, 120)


def _blend(base, glow, k):
    return tuple(int(b + (g - b) * k) for b, g in zip(base, glow))


class KeyboardWidget:
    """Frozen interface (pressed_midi is an additive optional arg)."""

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
        self._white = []
        self._black = []
        for w in range(n_white):
            octave, pos = divmod(w, 7)
            midi = base_midi + 12 * octave + _WHITE_SEMIS[pos]
            # DeepSeek integration fix (flagged to Fable, re-applied in rev 2):
            # tile white keys edge-to-edge (was round(ww)-1, which left a 1px
            # dead gap at each seam so a click exactly on a boundary hit
            # nothing). The 1px _OUTLINE in _draw_key still separates keys.
            x_this = round(self.rect.x + w * ww)
            x_next = round(self.rect.x + (w + 1) * ww)
            r = pygame.Rect(x_this, self.rect.y, x_next - x_this, wh)
            self._white.append((r, midi))
        bw, bh = ww * 0.6, wh * 0.62
        for octave in range(octaves):
            for b, after in enumerate(_BLACK_AFTER_WHITE):
                w = octave * 7 + after
                cx = self.rect.x + (w + 1) * ww
                midi = base_midi + 12 * octave + _BLACK_SEMIS[b]
                r = pygame.Rect(round(cx - bw / 2), self.rect.y,
                                round(bw), round(bh))
                self._black.append((r, midi))

    def hit_test(self, pos) -> int | None:
        for r, midi in self._black:
            if r.collidepoint(pos):
                return midi
        for r, midi in self._white:
            if r.collidepoint(pos):
                return midi
        return None

    def _draw_key(self, surface, r, midi, idle, pressed_color, levels,
                  pressed):
        k = min(1.0, max(0.0, levels.get(midi, 0.0)))
        if pressed:
            rr = r.move(0, 3)
            pygame.draw.rect(surface, _SHADOW, r)             # top shadow gap
            pygame.draw.rect(surface, _blend(pressed_color, _GLOW, k), rr)
            pygame.draw.rect(surface, _OUTLINE, rr, 1)
        else:
            pygame.draw.rect(surface, _blend(idle, _GLOW, k), r)
            pygame.draw.rect(surface, _OUTLINE, r, 1)
            # subtle bottom shadow = "raised" look
            pygame.draw.line(surface, _SHADOW,
                             (r.x, r.bottom - 1), (r.right - 1, r.bottom - 1), 2)

    def draw(self, surface, lit_midis, preview_midi=None,
             pressed_midi=None) -> None:
        levels = (lit_midis if isinstance(lit_midis, dict)
                  else {m: 1.0 for m in (lit_midis or ())})
        for r, midi in self._white:
            self._draw_key(surface, r, midi, _WHITE_IDLE, _WHITE_PRESSED,
                           levels, midi == pressed_midi)
        for r, midi in self._black:
            self._draw_key(surface, r, midi, _BLACK_IDLE, _BLACK_PRESSED,
                           levels, midi == pressed_midi)
        if preview_midi is not None:
            for r, midi in self._black + self._white:
                if midi == preview_midi:
                    pygame.draw.rect(surface, _PREVIEW, r.inflate(4, 4), 3)
                    break
