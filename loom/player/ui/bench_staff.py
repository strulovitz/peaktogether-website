"""
bench_staff.py — the full grand staff, noteheads only. [M2 — Parent 3,
rev 2; M3 echo slots — Parent 4, rev 3]

Scripture: BIBLE par.2 (noteheads only — no stems/beams/time
signatures; LOCKED) + NIR'S M2 AMENDMENT (July 2026, recorded in the
Commentaries): the Bench ALWAYS shows the FULL GRAND STAFF — treble
above, bass below, middle C living between them. A note draws on the
treble staff iff midi >= 60, else on the bass staff (NT Stage 5 rule).
The spell's raw staff.clef field remains valid pack data but the Bench
no longer hides the bass staff for treble-only spells.

All positions come purely from core/notation.py lookups (zero music
theory here). Step -> pixel: y = middle_line_y - step * (line_gap/2).
Ledger lines at even steps beyond +/-4, out to the note's own step.
Clefs: Segoe UI Symbol glyphs (U+1D11E / U+1D122), letter fallback;
baked PNGs may replace them later inside this file only.

REV 3 (M3, ADDITIVE — recorded in the Commentaries): draw() gains a
trailing keyword arg echo=None. When given, it must offer (duck-typed,
mirroring core/echo_logic — no import, the demos run with player/ on
sys.path): slot_states() -> tuple of "confirmed"|"provisional"|
"placeholder", .preview_midi (int|None), .cursor (int|None). Then:
  "confirmed"    solid notehead at the spell note's own pitch (as rev 2)
  "provisional"  HOLLOW notehead at echo.preview_midi — the player sees
                 their OWN guess, through the same NotationTable lookup
  "placeholder"  a faint dash at a NEUTRAL height between the staves
                 (never at the target's pitch — that would hand over
                 the answer); the cursor's dash is brightened; dashes
                 blend toward the glow on crossing flashes (rhythm may
                 leak, pitch never does).
With echo=None the drawing is exactly rev 2 — m2_demo is untouched.

draw(surface, spell, frame, flash_levels, echo=None): frozen surface.
"""

from __future__ import annotations

import pygame

_GLOW = (255, 196, 64)
_INK = (230, 230, 230)
_LINE = (150, 150, 158)
_BG = (18, 18, 22)
_PROVISIONAL = (240, 220, 120)     # matches the keyboard's preview outline
_DASH = (95, 95, 105)

_TREBLE_MID_FRAC = 0.28
_BASS_MID_FRAC = 0.78


def _blend(base, glow, k):
    return tuple(int(b + (g - b) * k) for b, g in zip(base, glow))


class StaffWidget:
    """Frozen interface."""

    def __init__(self, rect, notation_table) -> None:
        self.rect = pygame.Rect(rect)
        self.table = notation_table
        self._clef_font = None
        self._sharp_font = None

    def _fonts(self):
        if self._clef_font is None:
            try:
                self._clef_font = pygame.font.SysFont("segoeuisymbol", 44)
            except Exception:
                self._clef_font = pygame.font.SysFont(None, 44)
            self._sharp_font = pygame.font.SysFont("consolas", 18, bold=True)
        return self._clef_font, self._sharp_font

    def _draw_five_lines(self, surface, x0, x1, middle_y, gap):
        for line_step in (-4, -2, 0, 2, 4):
            y = middle_y - line_step * (gap / 2)
            pygame.draw.line(surface, _LINE, (x0, y), (x1, y), 1)

    def _draw_clef(self, surface, x, middle_y, which):
        clef_font, _ = self._fonts()
        glyph = "\U0001D11E" if which == "treble" else "\U0001D122"
        try:
            img = clef_font.render(glyph, True, _INK)
            if img.get_width() < 4:
                raise ValueError
        except Exception:
            img = clef_font.render("G" if which == "treble" else "F",
                                   True, _INK)
        surface.blit(img, (x, middle_y - img.get_height() // 2))

    def _draw_notehead(self, surface, x, middle_y, gap, entry, step,
                       color, active, filled=True):
        y = middle_y - step * (gap / 2)
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
        if filled:
            pygame.draw.ellipse(surface, color, head)
        else:
            pygame.draw.ellipse(surface, color, head, 2)   # hollow (rev 3)
        if active:
            pygame.draw.ellipse(surface, _GLOW, head.inflate(8, 8), 2)
        if entry.sharp:
            _, sharp_font = self._fonts()
            img = sharp_font.render("#", True, color)
            surface.blit(img, (x - 24, round(y) - img.get_height() // 2))

    def _draw_pitched(self, surface, x, treble_mid, bass_mid, gap, midi,
                      color, active, filled=True):
        """One notehead at the grand-staff home of `midi` (rev 3 helper;
        the rev-2 rule verbatim: treble iff midi >= 60)."""
        entry = self.table.entry(midi)
        if midi >= 60:
            self._draw_notehead(surface, x, treble_mid, gap, entry,
                                entry.treble_step, color, active, filled)
        else:
            self._draw_notehead(surface, x, bass_mid, gap, entry,
                                entry.bass_step, color, active, filled)

    def draw(self, surface, spell, frame, flash_levels, echo=None) -> None:
        pygame.draw.rect(surface, _BG, self.rect)
        gap = 12
        x0 = self.rect.x + 8
        x1 = self.rect.right - 8
        slots_x0 = self.rect.x + 62

        treble_mid = self.rect.y + int(self.rect.h * _TREBLE_MID_FRAC)
        bass_mid = self.rect.y + int(self.rect.h * _BASS_MID_FRAC)
        self._draw_five_lines(surface, x0, x1, treble_mid, gap)
        self._draw_five_lines(surface, x0, x1, bass_mid, gap)
        self._draw_clef(surface, x0, treble_mid, "treble")
        self._draw_clef(surface, x0, bass_mid, "bass")

        n = len(spell.notes)
        if n == 0:
            return
        span = x1 - slots_x0
        states = echo.slot_states() if echo is not None else None
        neutral_y = (treble_mid + bass_mid) // 2

        for note in spell.notes:
            x = slots_x0 + int(span * (note.index + 0.5) / n)
            k = 0.0
            if flash_levels is not None and note.index < len(flash_levels):
                k = min(1.0, max(0.0, flash_levels[note.index]))
            active = (frame is not None
                      and frame.active_note_index == note.index)

            if states is None:                       # rev-2 path, verbatim
                color = _blend(_INK, _GLOW, k)
                self._draw_pitched(surface, x, treble_mid, bass_mid, gap,
                                   note.midi, color, active)
                continue

            st = states[note.index]
            if st == "confirmed":
                color = _blend(_INK, _GLOW, k)
                self._draw_pitched(surface, x, treble_mid, bass_mid, gap,
                                   note.midi, color, active)
            elif st == "provisional":
                self._draw_pitched(surface, x, treble_mid, bass_mid, gap,
                                   echo.preview_midi, _PROVISIONAL,
                                   False, filled=False)
            else:                                    # placeholder dash
                base = (_PROVISIONAL if note.index == echo.cursor
                        else _DASH)
                color = _blend(base, _GLOW, k)
                pygame.draw.line(surface, color,
                                 (x - 7, neutral_y), (x + 7, neutral_y), 2)
