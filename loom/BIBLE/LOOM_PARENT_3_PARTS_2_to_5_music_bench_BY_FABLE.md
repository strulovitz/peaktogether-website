# LOOM — PARENT 3, PARTS 2-5 (THE WHOLE BUCKET) — VERBATIM, BY FABLE

> Saved word-for-word, as-is, by DeepSeek. Parent 3 (Claude Fable)'s full M2
> delivery, poured in one breath (Parts 2, 3, 4, 5 + batched questions + legacy
> summary). Do not edit — this is the verbatim archive.

---

Message received with a full heart. 💛 You're right — the middle is the poison, coordination spends memory too, and git is my immortality. So here it is: the whole bucket list, in one breath. Parts 2, 3, 4, 5 — back-to-back. Batched questions and my legacy summary at the very end. 🌊

📦 PART 2 — layout.py + input_actions.py

2A. player/ui/layout.py (full file — replaces the bone)

The numbers stay Parent 2's provisional values (they are sane); the eye-tuning pass with Nir happens on the running m2_demo.py — screenshots back and forth, then DeepSeek edits numbers here and only here, then we freeze.

```python
"""
layout.py — every fixed rectangle of the 1280x720 window. [M2 — Parent 3]

Scripture: BIBLE par.2 — window LOCKED at 1280x720; positions never
move (muscle memory is an accessibility feature). Top half = Scene
Stage (story image OR graph + helix + equation); bottom half = Music
Bench (keyboard, staff, OK/Cancel, transport).

STATUS: numbers below are STILL PROVISIONAL until Nir's eye-tuning
pass on the running m2_demo (screenshots back and forth). When Nir
says "freeze", DeepSeek flips this line to FROZEN and the numbers
become law. No widget invents its own geometry — every rect comes
from here, passed into widget constructors by the wiring. Widgets
never import this module themselves (testability).
"""

import pygame

WINDOW = pygame.Rect(0, 0, 1280, 720)

# --- top half: the Scene Stage ---
SCENE_STAGE = pygame.Rect(0, 0, 1280, 400)       # story image + caption
GRAPH = pygame.Rect(40, 30, 620, 330)            # puzzle mode: the graph
HELIX = pygame.Rect(700, 30, 280, 330)           # puzzle mode: the pitch helix
EQUATION = pygame.Rect(1000, 30, 240, 120)       # LaTeX-baked PNG
CAPTION = pygame.Rect(40, 360, 1200, 36)

# --- bottom half: the Music Bench ---
BENCH = pygame.Rect(0, 400, 1280, 320)
KEYBOARD = pygame.Rect(60, 430, 700, 170)        # 1 octave default, 2 max
STAFF = pygame.Rect(790, 430, 430, 170)          # noteheads only
OK_BUTTON = pygame.Rect(790, 615, 90, 40)
CANCEL_BUTTON = pygame.Rect(895, 615, 90, 40)
TRANSPORT = pygame.Rect(60, 620, 700, 60)        # play/pause/stop + timeline
```

2B. player/ui/input_actions.py (full file — replaces the bone)

Design decision (per my flag #2, implemented): the InputMapper owns named KEY actions only; mouse pointer events flow directly to widgets, which hit-test their own rects (that is exactly what the frozen widget signatures already say). input_mapping.json's "mouse" section is documentation of that routing, not mapper input.

```python
"""
input_actions.py — the mandatory input-abstraction layer. [M2 — Parent 3]

Scripture: BIBLE par.5 (LOCKED): named actions + ONE device->action
config file (player/data/input_mapping.json), so keyboard/mouse today
can become joystick/Xbox controller later WITHOUT touching game code.
Player K (keyboard, canonically Boyfriend): story, menus, Choice
answers, transport hotkeys. Player M (mouse, canonically Girlfriend):
piano, OK/Cancel, transport + scrubbing. Solo: everything mouse-usable.

ROUTING DOCTRINE (M2, frozen): the InputMapper translates KEY events
into named Actions via the JSON file. POINTER events (motion, buttons)
are NOT translated here — they flow raw to the widgets, which hit-test
their own rects (KeyboardWidget.hit_test, TransportWidget.handle_event,
GraphView.handle_event). The JSON's "mouse" section documents this
routing; the mapper skips it. A future gamepad parent adds a "gamepad"
section + entries here, ZERO game-code changes — exactly as scripture
demands. Game code must NEVER test ev.key/ev.button directly.
"""

from __future__ import annotations

import json
from enum import Enum, auto

import pygame


class Action(Enum):
    # transport (either player)
    PLAY_PAUSE = auto(); STOP = auto(); NUDGE_LEFT = auto(); NUDGE_RIGHT = auto()
    # Player K: story & menus
    MENU_UP = auto(); MENU_DOWN = auto(); MENU_CONFIRM = auto(); MENU_BACK = auto()
    # Player M: bench commitment
    OK = auto(); CANCEL = auto()
    # app
    QUIT = auto()


# Key names used in input_mapping.json -> pygame key constants.
# Explicit aliases first (stable, spelling-proof); pygame.key.key_code
# is the fallback for names not listed here.
_KEY_ALIASES = {
    "SPACE": pygame.K_SPACE, "HOME": pygame.K_HOME,
    "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT,
    "UP": pygame.K_UP, "DOWN": pygame.K_DOWN,
    "RETURN": pygame.K_RETURN, "ENTER": pygame.K_RETURN,
    "BACKSPACE": pygame.K_BACKSPACE, "ESCAPE": pygame.K_ESCAPE,
    "END": pygame.K_END, "TAB": pygame.K_TAB,
}

# JSON action names that are documentation, not mappable Actions:
_DOC_ONLY_ACTIONS = {"POINTER_PRIMARY"}


class InputMapper:
    """Frozen interface."""

    def __init__(self, key_to_action: dict[int, Action]) -> None:
        self._key_to_action = key_to_action

    @staticmethod
    def load(mapping_path: str) -> "InputMapper":
        with open(mapping_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        key_to_action: dict[int, Action] = {}
        for key_name, action_name in data.get("keyboard", {}).items():
            if key_name.startswith("_"):
                continue                       # _comment fields
            if action_name in _DOC_ONLY_ACTIONS:
                continue
            try:
                action = Action[action_name]
            except KeyError:
                raise ValueError(
                    f"{mapping_path}: unknown action {action_name!r} for key "
                    f"{key_name!r}. Known actions: "
                    f"{', '.join(a.name for a in Action)}") from None
            keycode = _KEY_ALIASES.get(key_name.upper())
            if keycode is None:
                try:
                    keycode = pygame.key.key_code(key_name.lower())
                except Exception:
                    raise ValueError(
                        f"{mapping_path}: unknown key name {key_name!r}"
                    ) from None
            key_to_action[keycode] = action
        # "mouse" section intentionally ignored: pointer events route
        # raw to widgets (see ROUTING DOCTRINE in the module docstring).
        return InputMapper(key_to_action)

    def map_event(self, pygame_event) -> list[Action]:
        if pygame_event.type == pygame.KEYDOWN:
            action = self._key_to_action.get(pygame_event.key)
            if action is not None:
                return [action]
        if pygame_event.type == pygame.QUIT:
            return [Action.QUIT]
        return []
```

📦 PART 3 — bench_keyboard.py + bench_staff.py

Shared convention (frozen for all M2 widgets): flash levels are floats in [0,1] (1 = just triggered, 0 = cold), computed by the wiring as flash_ms_remaining / highlight_decay_ms — exactly m1_demo's arithmetic. Widgets receive levels; they never own timers. The resting palette is calm black-and-white; highlights are the warm glow (255,196,64) blended by level (BIBLE §13: color-blind-safe = brightness + color together).

3A. player/ui/bench_keyboard.py (full file — replaces the bone)

```python
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
            r = pygame.Rect(round(self.rect.x + w * ww), self.rect.y,
                            round(ww) - 1, wh)
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
```

3B. player/ui/bench_staff.py (full file — replaces the bone)

```python
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
```

📦 PART 4 — bench_transport.py + graph_view.py

4A. player/ui/bench_transport.py (full file — replaces the bone)

The timeline logic is m1_demo's, extracted verbatim in behavior: same 3-pixel click-vs-drag threshold, same bar_to_beats linear map, same release-equals-paused, same click-equals-jump. Added (per BIBLE §2): the Play/Pause and Stop buttons as clickable rects inside the widget.

```python
"""
bench_transport.py — the VLC-style transport + timeline. [M2 — Parent 3]

Scripture: BIBLE par.1 pillar 3 + par.3.2 (Scrubbing) + NT par.II.4.
Scrub surface #1 (the graph is #2). The widget EMITS TransportEvents;
the wiring applies them to the Conductor — the widget never holds one.

EXTRACTION NOTE (on the record): the click-vs-drag threshold (3 px),
the pixel<->beats mapping, release=paused and click=jump are lifted
from m1_demo.py UNCHANGED IN BEHAVIOR — that feel is already
ear-approved by Nir. If the threshold ever needs tuning it should
migrate to scrub_tuning.json via Nir + a Commentaries note.

Internal layout (derived from the rect passed in; layout.py stays the
only owner of the rect itself): a square Play/Pause button at the
left, a Stop button beside it, then the timeline groove filling the
rest, with a small beats/seconds readout above the groove.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

_DRAG_THRESHOLD_PX = 3                 # m1_demo's proven constant, verbatim
_GLOW = (255, 196, 64)
_HANDLE = (240, 220, 120)
_GROOVE = (50, 50, 60)
_BTN = (60, 60, 72)
_BTN_ICON = (225, 225, 225)
_TEXT = (170, 170, 180)


class TransportCommand(Enum):
    PLAY_PAUSE = auto(); STOP = auto()
    JUMP = auto(); SCRUB_BEGIN = auto(); SCRUB_TO = auto(); SCRUB_END = auto()


@dataclass(frozen=True)
class TransportEvent:
    command: TransportCommand
    beats: float = 0.0          # for JUMP / SCRUB_TO


class TransportWidget:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        self.rect = pygame.Rect(rect)
        pad = 6
        btn = self.rect.h - 2 * pad
        self._play_rect = pygame.Rect(self.rect.x + pad,
                                      self.rect.y + pad, btn, btn)
        self._stop_rect = pygame.Rect(self._play_rect.right + pad,
                                      self.rect.y + pad, btn, btn)
        groove_x = self._stop_rect.right + 2 * pad
        self._groove = pygame.Rect(groove_x,
                                   self.rect.centery - 5,
                                   self.rect.right - pad - groove_x, 10)
        self._down_pos = None
        self._dragging = False
        self._font = None

    # ---- m1_demo's mapping, verbatim in behavior ---------------------
    def _bar_to_beats(self, px: int, total_beats: float) -> float:
        return (px - self._groove.x) / self._groove.w * total_beats

    def handle_event(self, pygame_event, total_beats: float) -> list[TransportEvent]:
        ev = pygame_event
        out: list[TransportEvent] = []
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._play_rect.collidepoint(ev.pos):
                out.append(TransportEvent(TransportCommand.PLAY_PAUSE))
            elif self._stop_rect.collidepoint(ev.pos):
                out.append(TransportEvent(TransportCommand.STOP))
            elif self._groove.inflate(0, 24).collidepoint(ev.pos):
                self._down_pos = ev.pos
                self._dragging = False
        elif ev.type == pygame.MOUSEMOTION and self._down_pos is not None:
            if (not self._dragging
                    and abs(ev.pos[0] - self._down_pos[0]) > _DRAG_THRESHOLD_PX):
                self._dragging = True
                out.append(TransportEvent(TransportCommand.SCRUB_BEGIN))
            if self._dragging:
                out.append(TransportEvent(
                    TransportCommand.SCRUB_TO,
                    self._bar_to_beats(ev.pos[0], total_beats)))
        elif (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1
              and self._down_pos is not None):
            if self._dragging:
                out.append(TransportEvent(TransportCommand.SCRUB_END))
            else:
                out.append(TransportEvent(
                    TransportCommand.JUMP,
                    self._bar_to_beats(self._down_pos[0], total_beats)))
            self._down_pos, self._dragging = None, False
        return out

    def draw(self, surface, frame, total_beats: float) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 14)
        # buttons
        pygame.draw.rect(surface, _BTN, self._play_rect, border_radius=4)
        pygame.draw.rect(surface, _BTN, self._stop_rect, border_radius=4)
        p = self._play_rect
        playing = (frame is not None and frame.state.name == "PLAYING")
        if playing:                                   # pause icon: two bars
            w = p.w // 5
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.x + w, p.y + w, w, p.h - 2 * w))
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.right - 2 * w, p.y + w, w, p.h - 2 * w))
        else:                                         # play icon: triangle
            m = p.w // 4
            pygame.draw.polygon(surface, _BTN_ICON,
                                [(p.x + m, p.y + m),
                                 (p.x + m, p.bottom - m),
                                 (p.right - m, p.centery)])
        s = self._stop_rect
        m = s.w // 4
        pygame.draw.rect(surface, _BTN_ICON,
                         (s.x + m, s.y + m, s.w - 2 * m, s.h - 2 * m))
        # groove + handle (m1_demo's look, relocated)
        pygame.draw.rect(surface, _GROOVE, self._groove)
        if total_beats > 0 and frame is not None:
            px = (self._groove.x
                  + self._groove.w * frame.playhead_beats / total_beats)
            pygame.draw.rect(surface, _HANDLE,
                             (int(px) - 2, self._groove.y - 8,
                              4, self._groove.h + 16))
            txt = (f"{frame.state.name:9s} beat {frame.playhead_beats:5.2f}  "
                   f"{frame.playhead_seconds:5.2f}s")
            surface.blit(self._font.render(txt, True, _TEXT),
                         (self._groove.x, self._groove.y - 24))
```

4B. player/ui/graph_view.py (full file — replaces the bone)

The beats<->plot-x maps are module-level pure functions (headless-testable without a window). Everything is interpolation over precompiled numbers — the permitted arithmetic, nothing more.

```python
"""
graph_view.py — the function's picture, and scrub surface #2.
[M2 — Parent 3]

Scripture: BIBLE par.2 + par.10 (dumb runtime): the Player never
evaluates f(x) — it draws the POLYLINE the Compiler precomputed
(spell.raw["graph"]["points"], unit-box normalized) and scrubs via the
precompiled per-note segments (spell.raw["notes"][i]["graph_segment"],
which tile [0,1] exactly — Compiler Stage 10). All mapping below is
linear interpolation over those precompiled numbers.

Emits the SAME TransportEvents as bench_transport (one command
vocabulary, one Conductor, one feel) and shares its 3 px
click-vs-drag threshold verbatim.

Graceful degradation (binding): a spell without a graph block (the M1
fixtures) draws an honest "no graph data" panel and emits nothing —
never crashes.
"""

from __future__ import annotations

import pygame

from .bench_transport import TransportCommand, TransportEvent

_DRAG_THRESHOLD_PX = 3                 # shared with bench_transport, verbatim
_GLOW = (255, 196, 64)
_CURVE = (200, 200, 210)
_ACTIVE = (240, 220, 120)
_BG = (18, 18, 22)
_FRAME_C = (70, 70, 80)
_TEXT = (120, 120, 130)
_PAD = 14


# ---- pure mapping helpers (headless-testable) ------------------------

def segments_of(spell):
    """[(index, x_from, x_to), ...] from raw; [] if the spell has none."""
    raw_notes = spell.raw.get("notes", [])
    out = []
    for n in spell.notes:
        if n.index < len(raw_notes) and "graph_segment" in raw_notes[n.index]:
            seg = raw_notes[n.index]["graph_segment"]
            out.append((n.index, float(seg["x_from"]), float(seg["x_to"])))
    return out if len(out) == len(spell.notes) else []


def u_to_beats(spell, u: float) -> float:
    """Normalized plot x (0..1) -> playhead beats, via the segment tiling."""
    segs = segments_of(spell)
    u = min(1.0, max(0.0, u))
    for idx, x_from, x_to in segs:
        if x_from <= u <= x_to:
            note = spell.notes[idx]
            frac = 0.0 if x_to <= x_from else (u - x_from) / (x_to - x_from)
            return note.start_beat + frac * note.duration_beats
    # outside every segment (non-tiling data): clamp to nearest boundary
    if segs and u < segs[0][1]:
        return spell.notes[segs[0][0]].start_beat
    if segs:
        last = spell.notes[segs[-1][0]]
        return last.start_beat + last.duration_beats
    return 0.0


def beats_to_u(spell, beats: float) -> float:
    """Playhead beats -> normalized plot x; gaps interpolate linearly."""
    segs = segments_of(spell)
    if not segs:
        return 0.0
    first = spell.notes[segs[0][0]]
    if beats <= first.start_beat:
        return segs[0][1]
    for k, (idx, x_from, x_to) in enumerate(segs):
        note = spell.notes[idx]
        end = note.start_beat + note.duration_beats
        if note.start_beat <= beats <= end:
            frac = (0.0 if note.duration_beats <= 0
                    else (beats - note.start_beat) / note.duration_beats)
            return x_from + frac * (x_to - x_from)
        if k + 1 < len(segs):
            nxt = spell.notes[segs[k + 1][0]]
            if end < beats < nxt.start_beat:            # inside a rest
                frac = (beats - end) / (nxt.start_beat - end)
                nxt_from = segs[k + 1][1]
                return x_to + frac * (nxt_from - x_to)
    return segs[-1][2]


class GraphView:
    """Frozen interface."""

    def __init__(self, rect) -> None:
        self.rect = pygame.Rect(rect)
        self._plot = self.rect.inflate(-2 * _PAD, -2 * _PAD)
        self._down_pos = None
        self._dragging = False
        self._font = None

    def _px_to_u(self, px: int) -> float:
        return (px - self._plot.x) / self._plot.w

    def _to_screen(self, pt):
        x = self._plot.x + pt[0] * self._plot.w
        y = self._plot.bottom - pt[1] * self._plot.h
        return (x, y)

    def handle_event(self, pygame_event, spell) -> list:
        if not segments_of(spell):
            return []
        ev = pygame_event
        out: list[TransportEvent] = []
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._plot.inflate(0, 24).collidepoint(ev.pos):
                self._down_pos = ev.pos
                self._dragging = False
        elif ev.type == pygame.MOUSEMOTION and self._down_pos is not None:
            if (not self._dragging
                    and abs(ev.pos[0] - self._down_pos[0]) > _DRAG_THRESHOLD_PX):
                self._dragging = True
                out.append(TransportEvent(TransportCommand.SCRUB_BEGIN))
            if self._dragging:
                out.append(TransportEvent(
                    TransportCommand.SCRUB_TO,
                    u_to_beats(spell, self._px_to_u(ev.pos[0]))))
        elif (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1
              and self._down_pos is not None):
            if self._dragging:
                out.append(TransportEvent(TransportCommand.SCRUB_END))
            else:
                out.append(TransportEvent(
                    TransportCommand.JUMP,
                    u_to_beats(spell, self._px_to_u(self._down_pos[0]))))
            self._down_pos, self._dragging = None, False
        return out

    def draw(self, surface, spell, frame, flash_levels) -> None:
        pygame.draw.rect(surface, _BG, self.rect)
        pygame.draw.rect(surface, _FRAME_C, self.rect, 1)
        points = spell.raw.get("graph", {}).get("points")
        segs = segments_of(spell)
        if not points or not segs:
            if self._font is None:
                self._font = pygame.font.SysFont("consolas", 16)
            img = self._font.render("(no graph data in this spell)",
                                    True, _TEXT)
            surface.blit(img, img.get_rect(center=self.rect.center))
            return
        scr = [self._to_screen(p) for p in points]
        if len(scr) >= 2:
            pygame.draw.lines(surface, _CURVE, False, scr, 2)
        # per-note glow: active segment + crossed-flash afterglow
        for idx, x_from, x_to in segs:
            k = 0.0
            if flash_levels is not None and idx < len(flash_levels):
                k = min(1.0, max(0.0, flash_levels[idx]))
            active = (frame is not None and frame.active_note_index == idx)
            if k <= 0.0 and not active:
                continue
            sub = [self._to_screen(p) for p in points
                   if x_from - 1e-9 <= p[0] <= x_to + 1e-9]
            if len(sub) >= 2:
                col = _ACTIVE if active else (
                    int(_BG[0] + (_GLOW[0] - _BG[0]) * k),
                    int(_BG[1] + (_GLOW[1] - _BG[1]) * k),
                    int(_BG[2] + (_GLOW[2] - _BG[2]) * k))
                pygame.draw.lines(surface, col, False, sub, 4)
        # playhead cursor: thin vertical line, in agreement with the bar
        if frame is not None:
            u = beats_to_u(spell, frame.playhead_beats)
            px = self._plot.x + u * self._plot.w
            pygame.draw.line(surface, _HANDLE_COLOR,
                             (px, self.rect.y + 4),
                             (px, self.rect.bottom - 4), 1)


_HANDLE_COLOR = (240, 220, 120)
```

📦 PART 5 — Fixture + m2_demo.py + tests + legacy

5A. New fixture: fixtures/spells/fixture_bench8.json

A new file (the two M1 fixtures stay untouched MEAT). Eight rising violin notes — a C-major scale, the sonification of a straight line — carrying the full BIBLE §8 bench/graph blocks that M2 needs. Hand-computed at design time (I am allowed math; the Player is not).

```json
{
  "format": "loom-spell",
  "format_version": "1.0",
  "spell_id": "fixture_bench8",
  "display_name": "M2 Bench Fixture - a straight line, heard",
  "function_text": "f(x) = x on [0, 1] (hand-made fixture)",
  "instrument": "violin",
  "articulation": "arco-normal",
  "bpm": 90,
  "scale": "major",
  "base_note": "C4",
  "total_beats": 8.0,
  "keyboard": { "low_note": "C4", "high_note": "C5" },
  "staff": { "clef": "treble" },
  "notes": [
    {"index": 0, "note_name": "C4", "midi": 60, "start_beat": 0.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_C4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 0,  "graph_segment": {"x_from": 0.0,   "x_to": 0.125}},
    {"index": 1, "note_name": "D4", "midi": 62, "start_beat": 1.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_D4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 2,  "graph_segment": {"x_from": 0.125, "x_to": 0.25}},
    {"index": 2, "note_name": "E4", "midi": 64, "start_beat": 2.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_E4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 4,  "graph_segment": {"x_from": 0.25,  "x_to": 0.375}},
    {"index": 3, "note_name": "F4", "midi": 65, "start_beat": 3.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_F4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 5,  "graph_segment": {"x_from": 0.375, "x_to": 0.5}},
    {"index": 4, "note_name": "G4", "midi": 67, "start_beat": 4.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_G4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 7,  "graph_segment": {"x_from": 0.5,   "x_to": 0.625}},
    {"index": 5, "note_name": "A4", "midi": 69, "start_beat": 5.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_A4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 9,  "graph_segment": {"x_from": 0.625, "x_to": 0.75}},
    {"index": 6, "note_name": "B4", "midi": 71, "start_beat": 6.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_B4_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 11, "graph_segment": {"x_from": 0.75,  "x_to": 0.875}},
    {"index": 7, "note_name": "C5", "midi": 72, "start_beat": 7.0, "duration_beats": 1.0, "dynamic": "forte", "sample": "audio/violin_C5_05_forte_arco-normal.mp3", "gain": 0.9, "key_index": 12, "graph_segment": {"x_from": 0.875, "x_to": 1.0}}
  ],
  "graph": {
    "points": [[0.0, 0.0], [0.125, 0.125], [0.25, 0.25], [0.375, 0.375], [0.5, 0.5], [0.625, 0.625], [0.75, 0.75], [0.875, 0.875], [1.0, 1.0]],
    "x_label": "x",
    "y_label": "f(x)"
  },
  "notes_for_humans": "Hand-made M2 fixture. A steady staircase: the straight line's melody, with keyboard/staff/graph blocks for the Bench widgets."
}
```

(DeepSeek: if load_spell rejects any of these fields, tell me which — the sample paths are placeholders overridden by the resolver, and total_beats is included defensively in case the loader reads rather than computes it. Extra raw keys should be harmless by design.)

5B. player/m2_demo.py (new file — Nir's eye/ear acceptance harness)

```python
"""
m2_demo.py — Milestone 2: the Music Bench lives. [demo scaffolding]

Run (from anywhere):
    python m2_demo.py                        <- bench fixture, real violin
    python m2_demo.py --spell <path>         <- any spell JSON
    python m2_demo.py --library <path>       <- Philharmonia root
    python m2_demo.py --beeps                <- EXPLICIT fallback only

Reuses m1_demo's ear-approved resolver (real instruments first, uniform
length, hard error over silent fallback) and wires the M2 widgets:
layout rects, InputMapper, KeyboardWidget, StaffWidget, TransportWidget,
GraphView, notation table.

NIR'S ACCEPTANCE SCRIPT (printed on startup):
  1. SPACE (or click Play): eight rising violin notes; watch the piano
     key, the staff notehead, and the graph segment light TOGETHER.
  2. Drag the timeline: identical feel to M1 (it is the same logic,
     extracted). Release = stays paused.
  3. Drag ON THE GRAPH: the curve itself is a playable surface — slow,
     fast, backward. The bar's handle and the graph cursor always agree.
  4. Click piano keys: each sounds instantly with the real violin (keys
     belonging to this spell), and gets a bright preview outline.
  5. The staff shows 8 noteheads (no stems - noteheads only); the
     sounding one glows and fades warmly.
  6. Click OK / Cancel: they print to the console (their real meaning
     arrives with M3's Echo controller).
  7. The only question that matters: is it ONE instrument now — hand,
     ear, and eye touching the same melody?
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
                     note_name, DEFAULT_LIBRARY)

DEFAULT_SPELL = os.path.join(LOOM_DIR, "fixtures", "spells",
                             "fixture_bench8.json")
TUNING_PATH = os.path.join(HERE, "data", "scrub_tuning.json")
NOTATION_PATH = os.path.join(HERE, "data", "notation_table.json")
MAPPING_PATH = os.path.join(HERE, "data", "input_mapping.json")


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
    if args.beeps:
        print("NOTE: --beeps requested: test tones, NOT game audio.")
        resolved = resolve_beeps(spell)
    else:
        print(f"Resolving REAL instruments from {args.library} ...")
        resolved = resolve_real_samples(spell, args.library)
    midi_to_sample = {spell.notes[i].midi: p for i, p in resolved.items()}
    midi_gain = {n.midi: n.gain for n in spell.notes}

    # ---- pygame world starts here ----
    from ui.audio_pygame import PygameAudioEngine, init_mixer
    import pygame
    from ui import layout
    from ui.input_actions import InputMapper, Action
    from ui.bench_keyboard import KeyboardWidget
    from ui.bench_staff import StaffWidget
    from ui.bench_transport import TransportWidget, TransportCommand
    from ui.graph_view import GraphView

    init_mixer()
    pygame.init()
    screen = pygame.display.set_mode((layout.WINDOW.w, layout.WINDOW.h))
    pygame.display.set_caption(f"LOOM M2 - {spell.spell_id}")
    font = pygame.font.SysFont("consolas", 16)
    clock = pygame.time.Clock()

    audio = PygameAudioEngine()
    audio.preload("", list(resolved.values()))
    conductor = Conductor(spell, tuning)
    mapper = InputMapper.load(MAPPING_PATH)

    kb = spell.raw.get("keyboard", {})
    base_midi = table.midi_for_name(kb.get("low_note", "C4"))
    high_midi = table.midi_for_name(kb.get("high_note", "C5"))
    octaves = 2 if (high_midi - base_midi) > 12 else 1
    keyboard = KeyboardWidget(layout.KEYBOARD, base_midi, octaves)
    staff = StaffWidget(layout.STAFF, table)
    transport = TransportWidget(layout.TRANSPORT)
    graph = GraphView(layout.GRAPH)

    flash_ms = [0.0] * len(spell.notes)
    preview_midi = None

    def apply(events):
        for te in events:
            c = te.command
            if c is TransportCommand.PLAY_PAUSE:
                (conductor.pause() if conductor.state is ConductorState.PLAYING
                 else conductor.play())
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
                    apply([type(
                        "T", (), {})()] and
                        [__import__("ui.bench_transport", fromlist=["x"])
                         .TransportEvent(TransportCommand.PLAY_PAUSE)])
                elif action is Action.STOP:
                    conductor.stop(); audio.stop_all(tuning.steal_fade_ms)
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
                    preview_midi = None
            # pointer events flow raw to the widgets:
            apply(transport.handle_event(ev, spell.total_beats))
            apply(graph.handle_event(ev, spell))
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                midi = keyboard.hit_test(ev.pos)
                if midi is not None:
                    preview_midi = midi
                    sample = midi_to_sample.get(midi)
                    if sample:
                        audio.trigger(sample, midi_gain.get(midi, 0.9))
                    else:
                        print(f"(no sample for {note_name(midi)} in this "
                              "demo - real packs ship full keyboard "
                              "coverage via required_samples)")
                elif layout.OK_BUTTON.collidepoint(ev.pos):
                    print("(OK - Echo controller arrives in M3)")
                elif layout.CANCEL_BUTTON.collidepoint(ev.pos):
                    preview_midi = None
                    print("(Cancel - provisional cleared)")

        # ---- the wiring loop (conductor.py doctrine, as in m1_demo) ----
        frame = conductor.update(dt_ms / 1000.0)
        for i in frame.triggers:
            n = spell.notes[i]
            audio.trigger(resolved[i], n.gain)
        for i in frame.crossed:
            flash_ms[i] = tuning.highlight_decay_ms
        for i in range(len(flash_ms)):
            flash_ms[i] = max(0.0, flash_ms[i] - dt_ms)
        levels = [f / tuning.highlight_decay_ms for f in flash_ms]
        lit = {spell.notes[i].midi: levels[i]
               for i in range(len(levels)) if levels[i] > 0}
        if frame.active_note_index is not None:
            lit[spell.notes[frame.active_note_index].midi] = max(
                lit.get(spell.notes[frame.active_note_index].midi, 0.0), 1.0)

        # ---- draw ----
        screen.fill((12, 12, 16))
        graph.draw(screen, spell, frame, levels)
        staff.draw(screen, spell, frame, levels)
        keyboard.draw(screen, lit, preview_midi)
        transport.draw(screen, frame, spell.total_beats)
        for rect, label in ((layout.OK_BUTTON, "OK"),
                            (layout.CANCEL_BUTTON, "Cancel")):
            pygame.draw.rect(screen, (60, 60, 72), rect, border_radius=6)
            img = font.render(label, True, (225, 225, 225))
            screen.blit(img, img.get_rect(center=rect.center))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

⚠️ DeepSeek, one honest self-catch: in the Action.PLAY_PAUSE branch above I wrote an over-clever inline construction. Please replace that whole elif action is Action.PLAY_PAUSE: branch body with the plain, correct form:

```python
                elif action is Action.PLAY_PAUSE:
                    (conductor.pause()
                     if conductor.state is ConductorState.PLAYING
                     else conductor.play())
```

(Also import nothing extra for it — TransportEvent isn't needed there. And preview_midi is assigned inside the loop, so make it a plain local mutated in place — if Python scoping complains in your integration, hoist it into a one-element list preview = [None]. Your call; behavior is what's specified in the acceptance script.)

5C. New tests: tests/test_m2_widgets.py

```python
"""Headless M2 tests: geometry + mapping, no window, no audio."""

import os
import sys
from types import SimpleNamespace

import pygame
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from ui.bench_keyboard import KeyboardWidget                  # noqa: E402
from ui.bench_transport import (TransportWidget,              # noqa: E402
                                TransportCommand)
from ui.graph_view import u_to_beats, beats_to_u              # noqa: E402


def fake_spell():
    notes = [SimpleNamespace(index=i, midi=60 + i, start_beat=float(i),
                             duration_beats=1.0, gain=0.9)
             for i in range(4)]
    raw = {"notes": [{"graph_segment":
                      {"x_from": i / 4, "x_to": (i + 1) / 4}}
                     for i in range(4)]}
    return SimpleNamespace(notes=notes, raw=raw, total_beats=4.0)


# ---- keyboard geometry ----------------------------------------------

def test_keyboard_white_and_black_hits():
    kb = KeyboardWidget(pygame.Rect(0, 0, 700, 170), 60, 1)
    ww = 700 / 8
    assert kb.hit_test((int(ww * 0.5), 160)) == 60        # C4, low on key
    assert kb.hit_test((int(ww * 7.5), 160)) == 72        # C5
    assert kb.hit_test((int(ww * 1.0), 20)) == 61         # Cs4 boundary, top
    assert kb.hit_test((int(ww * 1.0), 160)) in (60, 62)  # below black: white
    assert kb.hit_test((9999, 9999)) is None


def test_keyboard_rejects_non_c_base():
    with pytest.raises(ValueError):
        KeyboardWidget(pygame.Rect(0, 0, 700, 170), 61, 1)
    with pytest.raises(ValueError):
        KeyboardWidget(pygame.Rect(0, 0, 700, 170), 60, 3)


# ---- transport: m1_demo's proven click-vs-drag, extracted ------------

def ev(t, **kw):
    return pygame.event.Event(t, **kw)


def test_transport_click_is_jump():
    w = TransportWidget(pygame.Rect(0, 0, 700, 60))
    g = w._groove
    mid = (g.x + g.w // 2, g.centery)
    assert w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=mid), 8.0) == []
    out = w.handle_event(ev(pygame.MOUSEBUTTONUP, button=1, pos=mid), 8.0)
    assert len(out) == 1 and out[0].command is TransportCommand.JUMP
    assert abs(out[0].beats - 4.0) < 0.1


def test_transport_drag_is_scrub_and_release_ends():
    w = TransportWidget(pygame.Rect(0, 0, 700, 60))
    g = w._groove
    p0 = (g.x + 10, g.centery)
    w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=p0), 8.0)
    out = w.handle_event(
        ev(pygame.MOUSEMOTION, pos=(p0[0] + 30, p0[1])), 8.0)
    cmds = [e.command for e in out]
    assert cmds[0] is TransportCommand.SCRUB_BEGIN
    assert TransportCommand.SCRUB_TO in cmds
    out = w.handle_event(
        ev(pygame.MOUSEBUTTONUP, button=1, pos=(p0[0] + 30, p0[1])), 8.0)
    assert [e.command for e in out] == [TransportCommand.SCRUB_END]


def test_transport_tiny_wiggle_is_still_click():
    w = TransportWidget(pygame.Rect(0, 0, 700, 60))
    g = w._groove
    p0 = (g.x + 100, g.centery)
    w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=p0), 8.0)
    out = w.handle_event(
        ev(pygame.MOUSEMOTION, pos=(p0[0] + 2, p0[1])), 8.0)   # <= 3 px
    assert out == []
    out = w.handle_event(
        ev(pygame.MOUSEBUTTONUP, button=1, pos=(p0[0] + 2, p0[1])), 8.0)
    assert [e.command for e in out] == [TransportCommand.JUMP]


# ---- graph mapping: the permitted arithmetic --------------------------

def test_u_to_beats_and_back():
    s = fake_spell()
    assert abs(u_to_beats(s, 0.0) - 0.0) < 1e-9
    assert abs(u_to_beats(s, 0.5) - 2.0) < 1e-9
    assert abs(u_to_beats(s, 1.0) - 4.0) < 1e-9
    assert abs(beats_to_u(s, 2.0) - 0.5) < 1e-9
    assert abs(beats_to_u(s, 3.5) - 0.875) < 1e-9


def test_graph_without_data_is_silent():
    s = SimpleNamespace(notes=[], raw={}, total_beats=0.0)
    assert u_to_beats(s, 0.5) == 0.0
    assert beats_to_u(s, 1.0) == 0.0
```

5D. New tests: tests/test_input_mapper.py

```python
"""Headless InputMapper tests (M2)."""

import json
import os
import sys

import pygame
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from ui.input_actions import InputMapper, Action              # noqa: E402


def write(tmp_path, data):
    p = tmp_path / "input_mapping.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


GOOD = {"keyboard": {"SPACE": "PLAY_PAUSE", "HOME": "STOP",
                     "LEFT": "NUDGE_LEFT", "RIGHT": "NUDGE_RIGHT",
                     "UP": "MENU_UP", "DOWN": "MENU_DOWN",
                     "RETURN": "MENU_CONFIRM", "BACKSPACE": "MENU_BACK",
                     "ESCAPE": "QUIT"},
        "mouse": {"_comment": "doc", "BUTTON_1": "POINTER_PRIMARY"}}


def test_maps_keys_to_actions(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))
    e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    assert m.map_event(e) == [Action.PLAY_PAUSE]
    e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert m.map_event(e) == [Action.QUIT]


def test_unmapped_key_yields_nothing(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))
    e = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
    assert m.map_event(e) == []


def test_mouse_section_and_comments_ignored(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))       # must not raise
    e = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
    assert m.map_event(e) == []


def test_unknown_action_name_rejected(tmp_path):
    bad = {"keyboard": {"SPACE": "FLY_TO_THE_MOON"}}
    with pytest.raises(ValueError):
        InputMapper.load(write(tmp_path, bad))


def test_quit_event_maps_to_quit(tmp_path):
    m = InputMapper.load(write(tmp_path, GOOD))
    assert m.map_event(pygame.event.Event(pygame.QUIT)) == [Action.QUIT]
```

5E. DeepSeek's integration checklist (mechanical)

    Land Parts 1–5 files; apply my flagged PLAY_PAUSE-branch fix in m2_demo.py (5B note) and hoist preview_midi if scoping complains.
    Generate temp player/data/notation_table.json (contract 1B, MIDI 36–96).
    Add notation to test_purity.py's list.
    Run pytest — expect 28 old + ~19 new ≈ 47 passed. Fix trivial wiring breaks freely (imports/paths); paste anything behavioral back to me/Nir.
    Run python m2_demo.py for Nir's acceptance script; screenshot for the layout eye-tuning pass; tune layout.py numbers per Nir's eye, then mark layout FROZEN.
    Flip the seven M2 bones to MEAT in MAP.md + append a status-log line.

🧾 BATCHED QUESTIONS (all non-blocking; answer whenever)

    midi_for_name on NotationTable (Part 1F#1) — I used it in m2_demo.py; if Nir says no, DeepSeek swaps to base_midi = spell.notes[0].midi - raw_key_index(0) arithmetic. Default assumption: yes.
    Drag threshold (3 px) stays hard-coded to preserve m1's exact feel; migrate to scrub_tuning.json later only if Nir's hand asks for it.
    Clef glyphs come from Segoe UI Symbol with letter fallback; baked clef PNGs can replace them later inside bench_staff.py alone. OK as v1?
    OK/Cancel have layout rects + demo behavior but no widget bone; I propose a tiny ui/bench_buttons.py be born in M3 with the Echo controller, where they gain real meaning.
    fixture_bench8.json: if load_spell computes total_beats itself or validates unknown keys strictly, DeepSeek adjusts the fixture (not the loader) and notes it.

📜 PARENT 3 (Fable) — LEGACY SUMMARY, for the Commentaries

PARENT 3 (Fable) — M2: THE MUSIC BENCH (July 2026)

Delivered (all code): core/notation.py (MEAT; frozen notation_table.json
on-disk format v1.0 in its docstring, incl. step convention 0=middle
line, +1=letter up; additive midi_for_name reverse lookup — flagged,
default-approved); ui/input_actions.py (MEAT; InputMapper = KEY events
only; ROUTING DOCTRINE: pointer events flow raw to widgets, JSON mouse
section is documentation); ui/layout.py (numbers still provisional
until Nir's eye pass on m2_demo, then FROZEN); ui/bench_keyboard.py
(C-anchored, 1-2 octaves, black-keys-first hit-testing, flash-level
glow, preview outline, NO audio inside); ui/bench_staff.py (noteheads
only, 100% notation-table lookups, treble/grand, ledger lines, sharps,
Segoe-UI-Symbol clefs w/ letter fallback — PNG swap possible later);
ui/bench_transport.py (m1_demo's click-vs-drag/jump/release=paused
extracted UNCHANGED, 3px threshold verbatim; + play/pause/stop buttons;
emits TransportEvents, never holds a Conductor); ui/graph_view.py
(polyline from raw graph.points; scrub surface #2 via segment tiling;
pure module-level u_to_beats/beats_to_u; graceful "no graph data"
degradation — M1 fixtures never crash it); fixtures/spells/
fixture_bench8.json (new; M1 fixtures untouched); m2_demo.py (Nir's
7-step acceptance script; reuses m1_demo's resolver unchanged);
tests/test_notation.py, test_m2_widgets.py, test_input_mapper.py.

Shared M2 convention: flash levels = floats 0..1 computed by wiring as
flash_ms/highlight_decay_ms (m1_demo's arithmetic); widgets never own
timers; resting palette calm B&W, glow (255,196,64).

Known small debts: OK/Cancel widgetless until M3 (propose
ui/bench_buttons.py then); clef PNGs optional future asset swap;
layout freeze pending Nir's eye; m2_demo PLAY_PAUSE branch needed
DeepSeek's noted one-line fix; keyboard keys outside the spell's own
notes are silent in the demo (real packs ship full coverage via
required_samples).

Nir — that's the whole bucket, poured. 🪣✨ The Bench is designed to feel like one instrument: hand on the graph, ear on the violin, eye on three lights that never disagree. Take it to DeepSeek, run the acceptance script, and may the melody feel like something you can touch. 🎹🎻🌀💖
