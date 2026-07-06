# LOOM — PARENT 3, POUR 2 (rev 2: wide bench, grand staff, black keys, curves) — VERBATIM, BY FABLE

> Saved word-for-word, as-is, by DeepSeek. Parent 3 (Claude Fable)'s rev-2 M2
> delivery answering Nir's 8 points. Do not edit — this is the verbatim archive.
>
> NOTE (DeepSeek): after landing this, per Nir's decision the num_notes cap was
> AMENDED from 16 to 20 and the curved fixture is fixture_bench20 (20 notes).
> See Commentaries §5. This archive preserves Fable's original text (16) verbatim.

---

Approved-times-five received, and the feedback is gold — every point makes the Bench better. Answers first (short and honest), then the poured bucket: updated files, a fixture generator that produces real curves, and a rewritten demo. 🪣💖

🗣️ Answers to your 8 points

    🌀 The helix is not missing — it's M4. The New Testament's build order (II.8) deliberately sequences: M2 = Bench + graph, M4 = helix renderer. Its home is reserved: layout.HELIX + the helix_view.py bone. What I can do now: the demo draws a clearly-labeled placeholder panel in its exact spot, so you see the composition today. The spiral itself belongs to the M4 parent (or me, if I'm still alive after this).
    📈 Real curves — yes, always were. GraphView draws any precompiled polyline; the straight line was just the simplest hand-typed fixture. Real spells ship a 200-point dense polyline (BIBLE §7.2 dense_points), so the curve is smooth no matter how few notes the melody has. Below: a generator script that builds a real curved fixture — f(x) = √x — so you'll see a genuine curve today.
    🎹 Keyboard now spans almost the full width — new layout.py below: 1240 px wide, gorgeous at 1 octave, exactly right at 2.
    🎼 Staff also full width, above the piano — and it's N-agnostic: it divides its width into N slots, so 8, 16, or 20 notes all fit.
    🎵 Full grand staff — done, and recorded as your amendment. The staff now always draws both staves (treble above, bass below; middle C sits between them, as on a real grand staff). Notes at C4-and-above draw on the treble, below C4 on the bass. (DeepSeek: record in Commentaries §5 — "M2 amendment by Nir: the Bench staff always shows the full grand staff", superseding BIBLE §2's "grand only when required".)
    📊 About ~20 notes — one honest flag: the widgets don't care (they take any N), and the curve's resolution comes from the 200-point polyline, not the note count — your "7 pixels" fear can't happen. But BIBLE §7.2 locks num_notes at 4–16. Raising the cap to 20 is a one-line amendment that only you can make; nothing in my code needs to change. The new fixture uses 16 — the current legal maximum — so you can judge by eye whether you still want 20.
    ⚫ Black keys were silent only because the demo had just the spell's own 8 samples. Fixed two ways: the demo now resolves every key on the keyboard from the library (mirroring the required_samples superset doctrine), and the new √x fixture is quantized chromatically — its melody itself lands on Fs, Ds, Gs, As. Black keys sing. 🎶
    🖱️ Pressed/released key visuals — done. Keys now have a true pressed state (darker, nudged down, shadow edge — the Windows-button feel), separate from the lit-glow and the preview outline.

📦 POUR 2.1 — updated player/ui/layout.py (full file)

```python
"""
layout.py — every fixed rectangle of the 1280x720 window. [M2 — Parent 3]

Scripture: BIBLE par.2 — window LOCKED at 1280x720; positions never
move. Top half = Scene Stage; bottom half = Music Bench.

REVISED per Nir's eye feedback (July 2026): keyboard + staff span
almost the full width; staff sits directly above the piano and is a
FULL GRAND STAFF always (Nir's amendment); transport + OK/Cancel share
the bottom strip. HELIX keeps its reserved home for M4.

STATUS: still PROVISIONAL until Nir's final eye pass on m2_demo,
then FROZEN. Every widget takes its rect from here via the wiring;
widgets never import this module (testability).
"""

import pygame

WINDOW = pygame.Rect(0, 0, 1280, 720)

# --- top half: the Scene Stage ---
SCENE_STAGE = pygame.Rect(0, 0, 1280, 400)       # story image + caption
GRAPH = pygame.Rect(30, 14, 640, 356)            # puzzle mode: the graph
HELIX = pygame.Rect(700, 14, 310, 356)           # reserved: M4 pitch helix
EQUATION = pygame.Rect(1030, 14, 230, 140)       # LaTeX-baked PNG
CAPTION = pygame.Rect(40, 374, 1200, 24)         # story mode text strip

# --- bottom half: the Music Bench ---
BENCH = pygame.Rect(0, 400, 1280, 320)
STAFF = pygame.Rect(20, 404, 1240, 150)          # full grand staff, full width
KEYBOARD = pygame.Rect(20, 562, 1240, 118)       # 1 octave default, 2 max
TRANSPORT = pygame.Rect(20, 686, 950, 30)        # play/pause/stop + timeline
OK_BUTTON = pygame.Rect(1000, 684, 120, 34)
CANCEL_BUTTON = pygame.Rect(1140, 684, 120, 34)
```

📦 POUR 2.2 — updated player/ui/bench_keyboard.py (full file)

Additive change only: pressed_midi optional arg (frozen surface preserved).

```python
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
            r = pygame.Rect(round(self.rect.x + w * ww), self.rect.y,
                            round(ww) - 1, wh)
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
```

📦 POUR 2.3 — updated player/ui/bench_staff.py (full file)

```python
"""
bench_staff.py — the full grand staff, noteheads only. [M2 — Parent 3, rev 2]

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

M3 NOTE (documented, not implemented): the Echo controller will add
solid-confirmed / hollow-provisional / dashed-placeholder slot states.

draw(surface, spell, frame, flash_levels): frozen surface.
"""

from __future__ import annotations

import pygame

_GLOW = (255, 196, 64)
_INK = (230, 230, 230)
_LINE = (150, 150, 158)
_BG = (18, 18, 22)

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
                       color, active):
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
        pygame.draw.ellipse(surface, color, head)
        if active:
            pygame.draw.ellipse(surface, _GLOW, head.inflate(8, 8), 2)
        if entry.sharp:
            _, sharp_font = self._fonts()
            img = sharp_font.render("#", True, color)
            surface.blit(img, (x - 24, round(y) - img.get_height() // 2))

    def draw(self, surface, spell, frame, flash_levels) -> None:
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
        for note in spell.notes:
            entry = self.table.entry(note.midi)
            x = slots_x0 + int(span * (note.index + 0.5) / n)
            k = 0.0
            if flash_levels is not None and note.index < len(flash_levels):
                k = min(1.0, max(0.0, flash_levels[note.index]))
            color = _blend(_INK, _GLOW, k)
            active = (frame is not None
                      and frame.active_note_index == note.index)
            if note.midi >= 60:
                self._draw_notehead(surface, x, treble_mid, gap, entry,
                                    entry.treble_step, color, active)
            else:
                self._draw_notehead(surface, x, bass_mid, gap, entry,
                                    entry.bass_step, color, active)
```

📦 POUR 2.4 — NEW fixtures/make_bench_fixtures.py

A design-time generator (math allowed here — this is the Compiler's little cousin, stdlib only). It writes both bench fixtures, with canonical midpoint segment tiling (Compiler Stage 10):

    fixture_bench8.json — the line, violin, 1 octave (regenerated; overwrites my hand-typed one).
    fixture_bench16.json — f(x) = √x, 16 notes, chromatic, cello, TWO octaves C3–C5: a real curve, black keys in the melody, bass-clef notes on the grand staff. This becomes the demo default.

```python
"""
make_bench_fixtures.py — design-time generator for the M2 bench
fixtures. [demo/design scaffolding — stdlib only]

Math is allowed HERE (author's machine, like the Compiler); the Player
never evaluates anything. Writes into fixtures/spells/:

  fixture_bench8.json   f(x)=x   violin, 8 notes, major, C4..C5
  fixture_bench16.json  f(x)=sqrt(x) cello, 16 notes, CHROMATIC,
                        span 24, C3..C5 (grand staff + black keys)

Segments use the canonical midpoint tiling of Compiler Stage 10:
boundaries at midpoints between consecutive x_i; first=0, last=1.

Run:  python fixtures/make_bench_fixtures.py
"""

from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "spells")

NOTE_NAMES = ["C", "Cs", "D", "Ds", "E", "F", "Fs", "G", "Gs", "A", "As", "B"]


def note_name(midi: int) -> str:
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def midpoint_segments(xs):
    bounds = [0.0]
    for a, b in zip(xs, xs[1:]):
        bounds.append((a + b) / 2.0)
    bounds.append(1.0)
    return [(bounds[i], bounds[i + 1]) for i in range(len(xs))]


def build(spell_id, display, func_text, f, n_notes, dense, base_midi,
          span, scale_semis, instrument, articulation, low, high):
    xs = [i / (n_notes - 1) for i in range(n_notes)]
    ys = [f(x) for x in xs]
    y_min, y_max = min(ys), max(ys)

    def norm(y):
        return 0.0 if y_max == y_min else (y - y_min) / (y_max - y_min)

    scale_set = sorted({12 * q + d for q in range(3) for d in scale_semis
                        if 12 * q + d <= span} | {0})
    segs = midpoint_segments(xs)
    notes = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        theta = span * norm(y)
        snapped = min(scale_set,
                      key=lambda s: (abs(theta - s), s))   # ties downward
        midi = base_midi + snapped
        notes.append({
            "index": i, "note_name": note_name(midi), "midi": midi,
            "start_beat": float(i), "duration_beats": 1.0,
            "dynamic": "forte",
            "sample": (f"audio/{instrument}_{note_name(midi)}"
                       f"_05_forte_{articulation}.mp3"),
            "gain": 0.9, "key_index": midi - base_midi,
            "graph_segment": {"x_from": round(segs[i][0], 6),
                              "x_to": round(segs[i][1], 6)},
        })
    points = [[round(i / (dense - 1), 6), round(norm(f(i / (dense - 1))), 6)]
              for i in range(dense)]
    return {
        "format": "loom-spell", "format_version": "1.0",
        "spell_id": spell_id, "display_name": display,
        "function_text": func_text,
        "instrument": instrument, "articulation": articulation,
        "bpm": 90, "base_note": note_name(base_midi),
        "total_beats": float(n_notes),
        "keyboard": {"low_note": note_name(low), "high_note": note_name(high)},
        "staff": {"clef": "grand" if any(n["midi"] < 60 for n in notes)
                  else "treble"},
        "notes": notes,
        "graph": {"points": points, "x_label": "x", "y_label": "f(x)"},
        "notes_for_humans": f"Generated M2 fixture: {func_text}.",
    }


MAJOR = (0, 2, 4, 5, 7, 9, 11)
CHROMATIC = tuple(range(12))


def main():
    os.makedirs(OUT, exist_ok=True)
    specs = [
        build("fixture_bench8", "M2 Bench Fixture - a straight line, heard",
              "f(x) = x on [0, 1]", lambda x: x, 8, 65,
              60, 12, MAJOR, "violin", "arco-normal", 60, 72),
        build("fixture_bench16", "M2 Bench Fixture - the square root's curve",
              "f(x) = sqrt(x) on [0, 1]", math.sqrt, 16, 129,
              48, 24, CHROMATIC, "cello", "arco-normal", 48, 72),
    ]
    for s in specs:
        path = os.path.join(OUT, s["spell_id"] + ".json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(s, fh, indent=2)
        print(f"wrote {path}  ({len(s['notes'])} notes)")


if __name__ == "__main__":
    main()
```

📦 POUR 2.5 — rewritten player/m2_demo.py (full file, replaces the previous — cleanly this time)

```python
"""
m2_demo.py — Milestone 2: the Music Bench lives. [demo scaffolding, rev 2]

Run (from anywhere):
    python m2_demo.py                     <- sqrt fixture, real cello, 2 octaves
    python m2_demo.py --spell fixtures/spells/fixture_bench8.json
    python m2_demo.py --library <path>    <- Philharmonia root
    python m2_demo.py --beeps             <- EXPLICIT fallback only

NIR'S ACCEPTANCE SCRIPT (printed on startup):
  1. SPACE or Play: sixteen cello notes climb the SQUARE ROOT's curve -
     steep steps first, ever-gentler steps after. Watch key + notehead +
     graph segment light TOGETHER. Several notes are BLACK KEYS.
  2. Drag the timeline: M1's exact feel. Release = stays paused.
  3. Drag ON THE GRAPH: the curve is a playable surface - slow, fast,
     backward. Bar handle and graph cursor always agree.
  4. Click ANY piano key, black or white: it sounds with the real
     instrument and looks physically PRESSED while held.
  5. The GRAND STAFF spans the full width: low notes on the bass staff,
     high notes on the treble staff, noteheads only, sharps marked #.
  6. The helix panel shows its reserved home (the spiral itself is M4).
  7. OK / Cancel click and print (their real meaning arrives in M3).
  8. The only question: is it ONE instrument - hand, ear, eye?
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOOM_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from core.spell_model import load_spell                      # noqa: E402
from core.tuning import load_tuning                          # noqa: E402
from core.conductor import Conductor, ConductorState         # noqa: E402
from core.notation import NotationTable                      # noqa: E402
from m1_demo import (resolve_real_samples, resolve_beeps,    # noqa: E402
                     note_name, DEFAULT_LIBRARY, DYNAMIC_PREFERENCE)

DEFAULT_SPELL = os.path.join(LOOM_DIR, "fixtures", "spells",
                             "fixture_bench16.json")
TUNING_PATH = os.path.join(HERE, "data", "scrub_tuning.json")
NOTATION_PATH = os.path.join(HERE, "data", "notation_table.json")
MAPPING_PATH = os.path.join(HERE, "data", "input_mapping.json")


def resolve_keyboard_coverage(resolved_spell_paths, keyboard_midis):
    """Every key should sound (Nir, rev 2). Mirrors the required_samples
    superset doctrine using the SAME uniform length token the spell's
    resolver already chose (the Selection Law). Missing keys are
    reported and stay silent - never a beep, never a crash."""
    sample0 = next(iter(resolved_spell_paths.values()))
    folder = os.path.dirname(sample0)
    parts = os.path.basename(sample0)[:-4].split("_")
    instrument, token, articulation = parts[0], parts[2], parts[4]
    coverage, missing = {}, []
    for midi in keyboard_midis:
        for dyn in DYNAMIC_PREFERENCE:
            cand = os.path.join(
                folder,
                f"{instrument}_{note_name(midi)}_{token}_{dyn}_"
                f"{articulation}.mp3")
            if os.path.isfile(cand):
                coverage[midi] = cand
                break
        else:
            missing.append(note_name(midi))
    if missing:
        print(f"  (keyboard keys without a recording, silent: {missing})")
    return coverage


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spell", default=DEFAULT_SPELL)
    ap.add_argument("--library", default=DEFAULT_LIBRARY)
    ap.add_argument("--beeps", action="store_true")
    args = ap.parse_args()

    spell = load_spell(args.spell)
    tuning = load_tuning(TUNING_PATH)
    table = NotationTable.load(NOTATION_PATH)
    print(f"Loaded spell {spell.spell_id!r}: {len(spell.notes)} notes.")

    kb = spell.raw.get("keyboard", {})
    base_midi = table.midi_for_name(kb.get("low_note", "C4"))
    high_midi = table.midi_for_name(kb.get("high_note", "C5"))
    octaves = 2 if (high_midi - base_midi) > 12 else 1
    keyboard_midis = list(range(base_midi, base_midi + 12 * octaves + 1))

    if args.beeps:
        print("NOTE: --beeps requested: test tones, NOT game audio.")
        resolved = resolve_beeps(spell)
        coverage = {spell.notes[i].midi: p for i, p in resolved.items()}
    else:
        print(f"Resolving REAL instruments from {args.library} ...")
        resolved = resolve_real_samples(spell, args.library)
        coverage = resolve_keyboard_coverage(resolved, keyboard_midis)
    midi_gain = {n.midi: n.gain for n in spell.notes}

    # ---- pygame world starts here ----
    from ui.audio_pygame import PygameAudioEngine, init_mixer
    import pygame
    from ui import layout
    from ui.input_actions import InputMapper, Action
    from ui.bench_keyboard import KeyboardWidget
    from ui.bench_staff import StaffWidget
    from ui.bench_transport import (TransportWidget, TransportCommand,
                                    TransportEvent)
    from ui.graph_view import GraphView

    init_mixer()
    pygame.init()
    screen = pygame.display.set_mode((layout.WINDOW.w, layout.WINDOW.h))
    pygame.display.set_caption(f"LOOM M2 - {spell.spell_id}")
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    audio = PygameAudioEngine()
    audio.preload("", sorted(set(resolved.values()) | set(coverage.values())))
    conductor = Conductor(spell, tuning)
    mapper = InputMapper.load(MAPPING_PATH)

    keyboard = KeyboardWidget(layout.KEYBOARD, base_midi, octaves)
    staff = StaffWidget(layout.STAFF, table)
    transport = TransportWidget(layout.TRANSPORT)
    graph = GraphView(layout.GRAPH)

    flash_ms = [0.0] * len(spell.notes)
    ui = {"preview": None, "pressed": None}

    def apply(events):
        for te in events:
            c = te.command
            if c is TransportCommand.PLAY_PAUSE:
                if conductor.state is ConductorState.PLAYING:
                    conductor.pause()
                else:
                    conductor.play()
            elif c is TransportCommand.STOP:
                conductor.stop()
                audio.stop_all(tuning.steal_fade_ms)
            elif c is TransportCommand.JUMP:
                conductor.jump_to_beats(te.beats)
            elif c is TransportCommand.SCRUB_BEGIN:
                conductor.begin_scrub()
            elif c is TransportCommand.SCRUB_TO:
                conductor.scrub_to_beats(te.beats)
            elif c is TransportCommand.SCRUB_END:
                conductor.end_scrub()

    print(__doc__.split("printed on startup):")[-1])
    running = True
    while running:
        dt_ms = clock.tick(60)
        for ev in pygame.event.get():
            for action in mapper.map_event(ev):
                if action is Action.QUIT:
                    running = False
                elif action is Action.PLAY_PAUSE:
                    apply([TransportEvent(TransportCommand.PLAY_PAUSE)])
                elif action is Action.STOP:
                    apply([TransportEvent(TransportCommand.STOP)])
                elif action in (Action.NUDGE_LEFT, Action.NUDGE_RIGHT):
                    ph = conductor.playhead_beats
                    if action is Action.NUDGE_RIGHT:
                        nxt = [n.start_beat for n in spell.notes
                               if n.start_beat > ph + 1e-9]
                        if nxt:
                            conductor.jump_to_beats(nxt[0])
                    else:
                        prv = [n.start_beat for n in spell.notes
                               if n.start_beat < ph - 1e-9]
                        if prv:
                            conductor.jump_to_beats(prv[-1])
                elif action is Action.OK:
                    print("(OK - Echo controller arrives in M3)")
                elif action is Action.CANCEL:
                    ui["preview"] = None
            # pointer events flow raw to the widgets:
            apply(transport.handle_event(ev, spell.total_beats))
            apply(graph.handle_event(ev, spell))
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                midi = keyboard.hit_test(ev.pos)
                if midi is not None:
                    ui["preview"] = midi
                    ui["pressed"] = midi
                    if midi in coverage:
                        audio.trigger(coverage[midi],
                                      midi_gain.get(midi, 0.9))
                    else:
                        print(f"(no recording for {note_name(midi)})")
                elif layout.OK_BUTTON.collidepoint(ev.pos):
                    print("(OK - Echo controller arrives in M3)")
                elif layout.CANCEL_BUTTON.collidepoint(ev.pos):
                    ui["preview"] = None
                    print("(Cancel - provisional cleared)")
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                ui["pressed"] = None

        # ---- the wiring loop (conductor.py doctrine) ----
        frame = conductor.update(dt_ms / 1000.0)
        for i in frame.triggers:
            audio.trigger(resolved[i], spell.notes[i].gain)
        for i in frame.crossed:
            flash_ms[i] = tuning.highlight_decay_ms
        for i in range(len(flash_ms)):
            flash_ms[i] = max(0.0, flash_ms[i] - dt_ms)
        levels = [f / tuning.highlight_decay_ms for f in flash_ms]
        lit = {spell.notes[i].midi: levels[i]
               for i in range(len(levels)) if levels[i] > 0}
        if frame.active_note_index is not None:
            am = spell.notes[frame.active_note_index].midi
            lit[am] = max(lit.get(am, 0.0), 1.0)

        # ---- draw ----
        screen.fill((12, 12, 16))
        graph.draw(screen, spell, frame, levels)
        pygame.draw.rect(screen, (18, 18, 22), layout.HELIX)
        pygame.draw.rect(screen, (70, 70, 80), layout.HELIX, 1)
        img = font.render("pitch helix - reserved (M4)", True, (120, 120, 130))
        screen.blit(img, img.get_rect(center=layout.HELIX.center))
        staff.draw(screen, spell, frame, levels)
        keyboard.draw(screen, lit, ui["preview"], ui["pressed"])
        transport.draw(screen, frame, spell.total_beats)
        for rect, label in ((layout.OK_BUTTON, "OK"),
                            (layout.CANCEL_BUTTON, "Cancel")):
            pygame.draw.rect(screen, (60, 60, 72), rect, border_radius=6)
            t = font.render(label, True, (225, 225, 225))
            screen.blit(t, t.get_rect(center=rect.center))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

📦 POUR 2.6 — NEW tests/test_bench_fixtures.py

```python
"""Validates the generated M2 fixtures (design-time generator output)."""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(os.path.dirname(HERE), "fixtures", "make_bench_fixtures.py")

spec = importlib.util.spec_from_file_location("make_bench_fixtures", GEN)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)


def built():
    import math
    line = gen.build("t8", "t", "f(x)=x", lambda x: x, 8, 65,
                     60, 12, gen.MAJOR, "violin", "arco-normal", 60, 72)
    root = gen.build("t16", "t", "f(x)=sqrt(x)", math.sqrt, 16, 129,
                     48, 24, gen.CHROMATIC, "cello", "arco-normal", 48, 72)
    return line, root


def test_segments_tile_zero_to_one():
    for s in built():
        segs = [n["graph_segment"] for n in s["notes"]]
        assert segs[0]["x_from"] == 0.0
        assert segs[-1]["x_to"] == 1.0
        for a, b in zip(segs, segs[1:]):
            assert abs(a["x_to"] - b["x_from"]) < 1e-9


def test_midis_inside_keyboard_window():
    line, root = built()
    for n in line["notes"]:
        assert 60 <= n["midi"] <= 72
    for n in root["notes"]:
        assert 48 <= n["midi"] <= 72
    # the sqrt fixture must actually exercise black keys + bass staff
    assert any(n["midi"] % 12 in (1, 3, 6, 8, 10) for n in root["notes"])
    assert any(n["midi"] < 60 for n in root["notes"])


def test_key_index_consistency():
    for s in built():
        base = {"t8": 60, "t16": 48}[s["spell_id"]]
        for n in s["notes"]:
            assert n["key_index"] == n["midi"] - base


def test_graph_points_normalized_and_monotone_x():
    for s in built():
        pts = s["graph"]["points"]
        assert pts[0][0] == 0.0 and pts[-1][0] == 1.0
        assert all(0.0 <= y <= 1.0 for _, y in pts)
        assert all(a[0] < b[0] for a, b in zip(pts, pts[1:]))
```

🔧 DeepSeek's integration checklist (rev 2)

    Land all rev-2 files (layout, keyboard, staff, generator, m2_demo, new test). The rev-1 m2_demo.py is fully replaced (its noted bug is gone in this version — TransportEvent is now properly imported and used).
    Run python fixtures/make_bench_fixtures.py → writes/overwrites fixture_bench8.json + fixture_bench16.json. (Overwriting bench8 is intended: the generator is now its canonical source; note it in the Commentaries.)
    Confirm the cello folder covers C3–C5 at some common length for arco-normal (the resolver hard-errors with the fix-message if not — if cello lacks a common token, try --spell fixture_bench8.json and tell me; the Forge is the designed remedy).
    pytest — expect the previous suite + these new tests green.
    Run python m2_demo.py for Nir's rev-2 acceptance script; screenshots for the layout eye pass.
    Commentaries §5, add: "M2 amendment (Nir, July 2026): the Bench staff always shows the full grand staff." And record: OPEN QUESTION for Nir — raise BIBLE §7.2 num_notes max from 16 to 20? (widgets already N-agnostic; it's purely a doctrine number).

Nir — pour received, pour returned. 🪣 Now the Bench is wide, the staff is whole, the black keys sing, the keys press like real buttons, the curve truly curves, and the helix's chair is visibly waiting for M4. Run it, look, listen — and tell me what your eye and ear say. 🎻🎹🌀💖
