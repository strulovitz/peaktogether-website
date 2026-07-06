# LOOM — PARENT 3, REV 3: THE BPM BOX (typed tempo + spinners) — VERBATIM, BY FABLE

> Saved word-for-word, as-is, by DeepSeek. Parent 3 (Claude Fable)'s BPM-control
> feature: additive Conductor.set_bpm + a typed BPM box with up/down spinners on
> the far-right of the transport bar. Do not edit — this is the verbatim archive.

---

Wonderful news that it sounds clean now! 🎉 And yes — the BPM box is a great feature, exactly the kind of precision that scrubbing-by-hand can't give. It's very doable, and it even future-proofs us: the Laboratory (M6) needs a live tempo control anyway, so we're building its foundation early. Here's the whole thing. 🎯

🧠 Design decisions (quick)

    One additive method on the Conductor: set_bpm(). The Conductor is MEAT, but additive changes are allowed with your approval + a Commentaries note — and your request is the approval. DeepSeek implements it (he holds the source); I give the exact spec + tests below.
    The widget: BPM cluster lives at the far right of the transport bar — opposite side from play/pause, exactly as you asked (no triangle confusion). Up-triangle above, down-triangle below, text-box beside them.
    Typing rules: click the box → it focuses and empties; type digits (up to 3); Enter commits, Esc cancels, clicking anywhere else commits too. Committed values clamp to 40–200. While you're typing, the keyboard belongs to the box (Space won't toggle play mid-typing).
    Default 110: recorded as the new content default — the fixture generator now writes bpm: 110 (and FIT-THE-BEAT still picks the clean 0.5 s samples: 60/110 ≈ 0.545 s notes). The widget itself starts from whatever the spell says.

📦 3.1 — Spec for DeepSeek: additive Conductor.set_bpm (MEAT, Nir-approved)

Add to player/core/conductor.py:

```python
def set_bpm(self, bpm: float) -> None:
    """ADDITIVE (Nir, July 2026 — BPM box; also pre-work for M6 Lab).
    Change the playback tempo LIVE. playhead_beats does NOT move;
    only the beats-per-second rate changes from this moment on
    (playhead_seconds reporting follows the current bpm). Raises
    ValueError if bpm <= 0. Clamping to the UI range (40..200) is
    the widget's job, NOT the Conductor's."""
```

Plus a read-only property bpm (current live tempo; initialized from spell.bpm). Implementation is yours, DeepSeek — presumably: wherever update() uses the spell's bpm for beats-per-second, use an internal self._bpm instead. Acceptance tests to add to tests/test_conductor.py (adapt spell construction to your existing helpers):

```python
def test_set_bpm_changes_rate_not_position():
    c = make_conductor()              # your existing helper, e.g. 120 bpm
    c.play()
    c.update(0.5)
    pos = c.playhead_beats
    c.set_bpm(180.0)
    assert c.playhead_beats == pos                     # position untouched
    f = c.update(1.0)                                  # 180 bpm = 3 beats/s
    assert f.playhead_beats == pytest.approx(pos + 3.0, abs=1e-6)


def test_set_bpm_rejects_nonpositive():
    c = make_conductor()
    with pytest.raises(ValueError):
        c.set_bpm(0.0)
```

📦 3.2 — player/ui/bench_transport.py (full file, rev 3)

Additive interface changes only: TransportCommand.SET_BPM, a new optional bpm field on TransportEvent, optional initial_bpm ctor arg, and a typing property (so the wiring can mute hotkeys while the box is focused). All old behavior — the ear-approved m1 feel — is untouched.

```python
"""
bench_transport.py — the VLC-style transport + timeline + BPM box.
[M2 — Parent 3, rev 3]

Scripture: BIBLE par.1 pillar 3 + par.3.2 + NT par.II.4. Scrub surface
#1. Emits TransportEvents; never holds a Conductor.

REV 3 (Nir's BPM feature, July 2026): a BPM cluster on the FAR RIGHT
(opposite side from play/pause, per Nir — no adjacent triangles):
  [bpm] [ 110 ] [▲/▼]
- Click the box -> it focuses (empties); type digits; ENTER commits,
  ESC cancels, clicking elsewhere commits. Commit clamps to 40..200.
- The spinners step +/-1 and clamp; events fire only on real change.
- While the box is focused, .typing is True: the wiring MUST skip the
  InputMapper hotkeys (Space etc.) so typing is safe.
- Tempo default for new content: 110 (recorded in the Commentaries).

EXTRACTION NOTE (unchanged): 3 px click-vs-drag threshold, pixel<->
beats mapping, release=paused, click=jump — m1_demo's ear-approved
logic, verbatim.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pygame

_DRAG_THRESHOLD_PX = 3                 # m1_demo's proven constant, verbatim
BPM_MIN, BPM_MAX = 40, 200
_GLOW = (255, 196, 64)
_HANDLE = (240, 220, 120)
_GROOVE = (50, 50, 60)
_BTN = (60, 60, 72)
_BTN_ICON = (225, 225, 225)
_TEXT = (170, 170, 180)
_BOX_BG = (28, 28, 34)
_FOCUS = (240, 220, 120)


class TransportCommand(Enum):
    PLAY_PAUSE = auto(); STOP = auto()
    JUMP = auto(); SCRUB_BEGIN = auto(); SCRUB_TO = auto(); SCRUB_END = auto()
    SET_BPM = auto()                                   # rev 3 (additive)


@dataclass(frozen=True)
class TransportEvent:
    command: TransportCommand
    beats: float = 0.0          # for JUMP / SCRUB_TO
    bpm: float = 0.0            # for SET_BPM (rev 3, additive)


def _clamp_bpm(v: int) -> int:
    return max(BPM_MIN, min(BPM_MAX, v))


class TransportWidget:
    """Frozen interface (+ additive rev-3 members)."""

    def __init__(self, rect, initial_bpm: float = 110.0) -> None:
        self.rect = pygame.Rect(rect)
        pad = 6
        btn = self.rect.h - 2 * pad
        self._play_rect = pygame.Rect(self.rect.x + pad,
                                      self.rect.y + pad, btn, btn)
        self._stop_rect = pygame.Rect(self._play_rect.right + pad,
                                      self.rect.y + pad, btn, btn)
        # --- BPM cluster, far right (opposite side from play/pause) ---
        spin_w = 16
        spin_h = (self.rect.h - 8) // 2
        self._spin_up = pygame.Rect(self.rect.right - pad - spin_w,
                                    self.rect.y + 3, spin_w, spin_h)
        self._spin_down = pygame.Rect(self._spin_up.x,
                                      self._spin_up.bottom + 2,
                                      spin_w, spin_h)
        box_w = 58
        self._bpm_box = pygame.Rect(self._spin_up.x - 4 - box_w,
                                    self.rect.y + pad, box_w, btn)
        label_w = 34
        groove_x = self._stop_rect.right + 2 * pad
        groove_end = self._bpm_box.x - label_w - 2 * pad
        self._groove = pygame.Rect(groove_x, self.rect.centery - 5,
                                   groove_end - groove_x, 10)
        self._down_pos = None
        self._dragging = False
        self._font = None
        self._bpm = _clamp_bpm(int(round(initial_bpm)))
        self._focused = False
        self._buffer = ""

    # ---- rev-3 public read-only state --------------------------------
    @property
    def typing(self) -> bool:
        """True while the BPM box is focused: wiring must mute hotkeys."""
        return self._focused

    @property
    def bpm(self) -> int:
        return self._bpm

    # ---- internals ----------------------------------------------------
    def _bar_to_beats(self, px: int, total_beats: float) -> float:
        return (px - self._groove.x) / self._groove.w * total_beats

    def _set_bpm(self, value: int) -> list[TransportEvent]:
        value = _clamp_bpm(value)
        if value != self._bpm:
            self._bpm = value
            return [TransportEvent(TransportCommand.SET_BPM,
                                   bpm=float(value))]
        return []

    def _commit(self) -> list[TransportEvent]:
        self._focused = False
        buf, self._buffer = self._buffer, ""
        if buf:
            return self._set_bpm(int(buf))
        return []                                     # empty -> revert

    def _cancel(self) -> None:
        self._focused = False
        self._buffer = ""

    # ---- the frozen surface -------------------------------------------
    def handle_event(self, pygame_event, total_beats: float) -> list[TransportEvent]:
        ev = pygame_event
        out: list[TransportEvent] = []
        if ev.type == pygame.KEYDOWN and self._focused:
            if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                out += self._commit()
            elif ev.key == pygame.K_ESCAPE:
                self._cancel()
            elif ev.key == pygame.K_BACKSPACE:
                self._buffer = self._buffer[:-1]
            elif ev.unicode.isdigit() and len(self._buffer) < 3:
                self._buffer += ev.unicode
            return out
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._bpm_box.collidepoint(ev.pos):
                if not self._focused:
                    self._focused = True
                    self._buffer = ""
                return out
            if self._focused:                          # click-away commits
                out += self._commit()
            if self._spin_up.collidepoint(ev.pos):
                out += self._set_bpm(self._bpm + 1)
            elif self._spin_down.collidepoint(ev.pos):
                out += self._set_bpm(self._bpm - 1)
            elif self._play_rect.collidepoint(ev.pos):
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
        # play/pause + stop buttons (unchanged)
        pygame.draw.rect(surface, _BTN, self._play_rect, border_radius=4)
        pygame.draw.rect(surface, _BTN, self._stop_rect, border_radius=4)
        p = self._play_rect
        playing = (frame is not None and frame.state.name == "PLAYING")
        if playing:
            w = p.w // 5
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.x + w, p.y + w, w, p.h - 2 * w))
            pygame.draw.rect(surface, _BTN_ICON,
                             (p.right - 2 * w, p.y + w, w, p.h - 2 * w))
        else:
            m = p.w // 4
            pygame.draw.polygon(surface, _BTN_ICON,
                                [(p.x + m, p.y + m),
                                 (p.x + m, p.bottom - m),
                                 (p.right - m, p.centery)])
        s = self._stop_rect
        m = s.w // 4
        pygame.draw.rect(surface, _BTN_ICON,
                         (s.x + m, s.y + m, s.w - 2 * m, s.h - 2 * m))
        # groove + handle + readout (unchanged)
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
        # --- BPM cluster (rev 3) ---
        lbl = self._font.render("bpm", True, _TEXT)
        surface.blit(lbl, (self._bpm_box.x - lbl.get_width() - 6,
                           self._bpm_box.centery - lbl.get_height() // 2))
        pygame.draw.rect(surface, _BOX_BG, self._bpm_box, border_radius=3)
        pygame.draw.rect(surface, _FOCUS if self._focused else _BTN,
                         self._bpm_box, 2 if self._focused else 1,
                         border_radius=3)
        shown = (self._buffer + "_") if self._focused else str(self._bpm)
        img = self._font.render(shown, True, _BTN_ICON)
        surface.blit(img, img.get_rect(center=self._bpm_box.center))
        for r, up in ((self._spin_up, True), (self._spin_down, False)):
            pygame.draw.rect(surface, _BTN, r, border_radius=2)
            mx, quarter = r.centerx, max(3, r.h // 4)
            if up:
                pts = [(mx, r.y + quarter), (r.x + 3, r.bottom - quarter),
                       (r.right - 3, r.bottom - quarter)]
            else:
                pts = [(mx, r.bottom - quarter), (r.x + 3, r.y + quarter),
                       (r.right - 3, r.y + quarter)]
            pygame.draw.polygon(surface, _BTN_ICON, pts)
```

📦 3.3 — Surgical patches to player/m2_demo.py (three tiny edits)

(1) Widget creation — pass the spell's tempo:

```python
    transport = TransportWidget(layout.TRANSPORT, initial_bpm=spell.bpm)
```

(2) In apply(), add one branch:

```python
            elif c is TransportCommand.SET_BPM:
                conductor.set_bpm(te.bpm)
                print(f"(tempo -> {int(te.bpm)} BPM)")
```

(3) Mute hotkeys while typing — wrap the mapper block in the event loop:

```python
            if not transport.typing:
                for action in mapper.map_event(ev):
                    ...(existing body unchanged)...
```

(Everything else stays; pointer events already flow to transport.handle_event which now feeds the box.)

📦 3.4 — One-line change in fixtures/make_bench_fixtures.py

In build(...), change "bpm": 90, to:

```python
        "bpm": 110,
```

then rerun python fixtures/make_bench_fixtures.py. (FIT-THE-BEAT check: 60/110 ≈ 0.545 s notes → still chooses the clean 05 samples. The console will confirm.)

📦 3.5 — NEW tests/test_transport_bpm.py

```python
"""BPM box + spinner tests (rev 3), headless."""

import os
import sys

import pygame

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "player"))

from ui.bench_transport import (TransportWidget,               # noqa: E402
                                TransportCommand)


def ev(t, **kw):
    return pygame.event.Event(t, **kw)


def key(k, uni=""):
    return ev(pygame.KEYDOWN, key=k, unicode=uni)


def make():
    return TransportWidget(pygame.Rect(0, 0, 950, 30), initial_bpm=110)


def click(w, pos):
    return w.handle_event(ev(pygame.MOUSEBUTTONDOWN, button=1, pos=pos), 8.0)


def test_type_and_commit():
    w = make()
    click(w, w._bpm_box.center)
    assert w.typing is True
    for ch, kc in (("1", pygame.K_1), ("5", pygame.K_5), ("0", pygame.K_0)):
        w.handle_event(key(kc, ch), 8.0)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)
    assert w.typing is False and w.bpm == 150
    assert [e.command for e in out] == [TransportCommand.SET_BPM]
    assert out[0].bpm == 150.0


def test_commit_clamps_40_to_200():
    w = make()
    click(w, w._bpm_box.center)
    for ch, kc in (("9", pygame.K_9),) * 3:
        w.handle_event(key(kc, ch), 8.0)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)
    assert w.bpm == 200 and out[0].bpm == 200.0
    click(w, w._bpm_box.center)
    w.handle_event(key(pygame.K_5, "5"), 8.0)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)
    assert w.bpm == 40 and out[0].bpm == 40.0


def test_escape_cancels_and_empty_commit_reverts():
    w = make()
    click(w, w._bpm_box.center)
    w.handle_event(key(pygame.K_7, "7"), 8.0)
    w.handle_event(key(pygame.K_ESCAPE), 8.0)
    assert w.typing is False and w.bpm == 110
    click(w, w._bpm_box.center)
    out = w.handle_event(key(pygame.K_RETURN), 8.0)   # nothing typed
    assert out == [] and w.bpm == 110


def test_click_away_commits():
    w = make()
    click(w, w._bpm_box.center)
    w.handle_event(key(pygame.K_9, "9"), 8.0)
    w.handle_event(key(pygame.K_0, "0"), 8.0)
    out = click(w, (w._groove.centerx, w._groove.centery - 60))  # outside all
    assert any(e.command is TransportCommand.SET_BPM and e.bpm == 90.0
               for e in out)
    assert w.typing is False


def test_spinners_step_and_clamp():
    w = make()
    out = click(w, w._spin_up.center)
    assert w.bpm == 111 and out[0].bpm == 111.0
    out = click(w, w._spin_down.center)
    assert w.bpm == 110 and out[0].bpm == 110.0
    w2 = TransportWidget(pygame.Rect(0, 0, 950, 30), initial_bpm=40)
    out = click(w2, w2._spin_down.center)
    assert w2.bpm == 40 and out == []                 # no event on no-change


def test_hotkeys_ignored_while_typing_is_wirings_job():
    # the widget only exposes .typing; SPACE while focused must not be
    # eaten here (unicode " " is not a digit -> ignored, no crash):
    w = make()
    click(w, w._bpm_box.center)
    out = w.handle_event(key(pygame.K_SPACE, " "), 8.0)
    assert out == [] and w.typing is True
```

🔧 DeepSeek's checklist

    Implement Conductor.set_bpm + bpm property per spec 3.1 (+ the two conductor tests, adapted to your helpers).
    Land bench_transport.py rev 3, the three m2_demo patches, the generator bpm change (then regenerate fixtures), and test_transport_bpm.py.
    pytest → previous suite + ~8 new, green. Old transport tests must pass unchanged (the groove just got a bit shorter).
    Commentaries §5, append: "BPM control (Nir, July 2026): additive Conductor.set_bpm (live tempo; also pre-work for the M6 Lab); TransportWidget gains a typed BPM box (40–200, Enter/Esc/click-away, spinners ±1) on the far right; content default tempo = 110; TransportCommand.SET_BPM + TransportEvent.bpm added additively."

Nir's acceptance script for the feature: ▶️ play the cello √x spell → click the BPM box → type 60 → Enter → it slows live, mid-playback, same pitches (never chipmunked — pitch is the data!). Type 200 → it races. Tap ▲▼ for fine steps. Try typing while it plays — Space won't interrupt your typing. Then tell me how it feels! ⏱️🎻💖
