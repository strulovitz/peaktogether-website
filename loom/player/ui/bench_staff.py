"""
bench_staff.py — the real musical staff, noteheads only. [M2 — Parent 3]

Scripture: BIBLE par.2 (LOCKED): treble or grand clef, NOTEHEADS ONLY —
no stems, no beams, no time signatures. Every drawing position comes
purely from core/notation.py lookups. ZERO music theory in this file:
it draws ellipses at looked-up steps, a '#' glyph when the table says
sharp, and ledger lines when the step leaves the five lines.

Clef selection: spell.raw["staff"]["clef"] — "treble" (default) or
"grand". On a grand staff a note draws on the bass staff iff midi < 60
(NT Stage 5 rule), else on the treble staff.

Step -> pixel: y = middle_line_y - step * (line_gap / 2). Ledger lines
are drawn at even steps beyond +/-4, out to the note's own step.

Clef glyphs: drawn from the "Segoe UI Symbol" font (present on Nir's
Windows) — U+1D11E treble / U+1D122 bass — with a plain G/F letter
fallback. Baked clef PNGs may replace this later purely inside this
file (an asset swap, no interface change).

M3 NOTE (documented, not implemented): the Echo controller will add
solid-confirmed / hollow-provisional / dashed-placeholder slot states
via the frozen draw() args it controls (BIBLE par.3). M2 draws the
spell's own notes: solid heads, active glow, crossed-flash decay.

draw(surface, spell, frame, flash_levels):
  spell         SpellData (uses .notes midi order + raw["staff"])
  frame         ConductorFrame (active_note_index)
  flash_levels  sequence of 0..1 per note index (wiring-computed)
"""

from __future__ import annotations

import pygame

_GLOW = (255, 196, 64)
_INK = (230, 230, 230)
_LINE = (150, 150, 158)
_BG = (18, 18, 22)


def _blend(base, glow, k):
    return tuple(int(b + (g - b) * k) for b, g in zip(base, glow))


class StaffWidget:
    """Frozen interface."""

    def __init__(self, rect, notation_table) -> None:
        self.rect = pygame.Rect(rect)
        self.table = notation_table
        self._clef_font = None
        self._sharp_font = None

    # ---- internal helpers -------------------------------------------
    def _fonts(self):
        if self._clef_font is None:
            try:
                self._clef_font = pygame.font.SysFont("segoeuisymbol", 46)
            except Exception:
                self._clef_font = pygame.font.SysFont(None, 46)
            self._sharp_font = pygame.font.SysFont("consolas", 18, bold=True)
        return self._clef_font, self._sharp_font

    def _draw_five_lines(self, surface, x0, x1, middle_y, gap):
        for line_step in (-4, -2, 0, 2, 4):
            y = middle_y - line_step * (gap / 2)
            pygame.draw.line(surface, _LINE, (x0, y), (x1, y), 1)

    def _draw_clef(self, surface, x, middle_y, gap, which):
        clef_font, _ = self._fonts()
        glyph = "\U0001D11E" if which == "treble" else "\U0001D122"
        try:
            img = clef_font.render(glyph, True, _INK)
            if img.get_width() < 4:          # font lacked the glyph
                raise ValueError
        except Exception:
            img = clef_font.render("G" if which == "treble" else "F",
                                   True, _INK)
        surface.blit(img, (x, middle_y - img.get_height() // 2))

    def _draw_notehead(self, surface, x, middle_y, gap, entry, step,
                       color, active):
        y = middle_y - step * (gap / 2)
        # ledger lines at even steps beyond the five lines
        if step > 4:
            for ls in range(6, (step // 2) * 2 + 1, 2):
                ly = middle_y - ls * (gap / 2)
                pygame.draw.line(surface, _LINE, (x - 12, ly), (x + 12, ly), 1)
        elif step < -4:
            for ls in range(-6, (step // 2) * 2 - 1, -2):
                ly = middle_y - ls * (gap / 2)
                pygame.draw.line(surface, _LINE, (x - 12, ly), (x + 12, ly), 1)
        head = pygame.Rect(0, 0, 14, 10)
        head.center = (x, round(y))
        pygame.draw.ellipse(surface, color, head)
        if active:
            pygame.draw.ellipse(surface, _GLOW, head.inflate(8, 8), 2)
        if entry.sharp:
            _, sharp_font = self._fonts()
            img = sharp_font.render("#", True, color)
            surface.blit(img, (x - 24, round(y) - img.get_height() // 2))

    # ---- the frozen surface -----------------------------------------
    def draw(self, surface, spell, frame, flash_levels) -> None:
        pygame.draw.rect(surface, _BG, self.rect)
        clef = spell.raw.get("staff", {}).get("clef", "treble")
        gap = 12
        clef_margin = 46
        x0 = self.rect.x + 8
        x1 = self.rect.right - 8
        slots_x0 = self.rect.x + clef_margin + 16

        if clef == "grand":
            treble_mid = self.rect.y + int(self.rect.h * 0.30)
            bass_mid = self.rect.y + int(self.rect.h * 0.72)
            self._draw_five_lines(surface, x0, x1, treble_mid, gap)
            self._draw_five_lines(surface, x0, x1, bass_mid, gap)
            self._draw_clef(surface, x0, treble_mid, gap, "treble")
            self._draw_clef(surface, x0, bass_mid, gap, "bass")
        else:
            treble_mid = self.rect.y + self.rect.h // 2
            bass_mid = None
            self._draw_five_lines(surface, x0, x1, treble_mid, gap)
            self._draw_clef(surface, x0, treble_mid, gap, "treble")

        n = len(spell.notes)
        if n == 0:
            return
        span = x1 - slots_x0
        for note in spell.notes:
            entry = self.table.entry(note.midi)
            x = slots_x0 + int(span * (note.index + 0.5) / n)
            k = 0.0
            if flash_levels is not None and note.index < len(flash_levels):
                k = min(1.0, max(0.0, flash_levels[note.index]))
            color = _blend(_INK, _GLOW, k)
            active = (frame is not None
                      and frame.active_note_index == note.index)
            if clef == "grand" and note.midi < 60:
                self._draw_notehead(surface, x, bass_mid, gap, entry,
                                    entry.bass_step, color, active)
            else:
                self._draw_notehead(surface, x, treble_mid, gap, entry,
                                    entry.treble_step, color, active)
