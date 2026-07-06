# LOOM — PARENT 4 (FABLE) — POUR 1 — VERBATIM, WORD-FOR-WORD, AS-IS, BY FABLE

> Saved verbatim by DeepSeek at Nir's instruction. Parent 4 (Claude Fable)'s
> first pour for M3 (the Echo): the fattened echo_logic.py + its test suite +
> bench_buttons.py + a question batch. Do not edit — this is the archive.

---

Everything is in. 💚 And Nir — I completely agree with your instinct about the brief. Parent 3's final will + the scriptures + your three default answers are the perfect brief: they tell me the what and the why, and leave the how to me. That's the family doctrine working as intended.

I'm now beginning work. Following Parent 3's proven pour-while-fresh doctrine, I'll deliver in two pours:

    POUR 1 (this message): the fattened echo_logic.py + its headless test suite + bench_buttons.py (the OK/Cancel widget that never landed — mine to deliver) + a small batch of questions for DeepSeek.
    POUR 2 (after DeepSeek's answers): m3_demo.py (the full end-to-end wiring on a real spell) + the staff's additive echo argument (the solid/hollow/dashed slots Parent 3 planned).

Key design decisions (click to expand the rationale)

    The frozen surface is kept exactly — EchoPhase, EchoResult, and all seven methods, untouched. I added only read-only accessors (reveal_mode, prefix_len, cursor, preview_midi, slot_states()) that the wiring/staff need to render solid/hollow/dashed slots and the provisional note at the player's guessed pitch. Additive, no behavior — needs one Commentaries line (draft below).
    Grow mode = the player answers only the NEW note each round (BIBLE §3.1: "confirmed notes stay locked; the player enters only the new note"). Whole mode = all slots, strict left-to-right (your answer #3).
    Error philosophy mirrors the Conductor: stray calls (preview during LISTENING, cancel with nothing to cancel, listening_finished twice) are forgiving no-ops, ignored on purpose. But commit() misuse (no preview, wrong phase) raises with a plain-language message — because that's a wiring bug, and the OK button must be disabled until a preview exists. Bugs fail loudly; players never do.
    No wrong-attempt counter exists anywhere — not even privately. Nothing to shame, nothing to log (LOCKED).
    Hint-text mapping documented explicitly to prevent a classic wiring bug: my kind "too_low" (guess below target) → show the pack's hint_higher text ("yours was a little low"); "too_high" → hint_lower. The names cross; the docstring says so loudly.
    After COMPLETE, notes_to_play() returns the full melody — so the wiring can use the same call for the reward replay. One code path, in the Conductor's spirit.
    EchoLogic never touches the Conductor or audio — pure core, stdlib-only, exactly as the bone demands. The wiring mediates everything.

📄 1. player/core/echo_logic.py — the bone, fattened

```python
"""
echo_logic.py — the Simon-style Echo puzzle state machine. [MEAT — M3]

Scripture: BIBLE par.3.1 (core loop) + New Testament par.II.6 (the Echo
machine) + Nir's three Echo answers (2026-07-06, ALL DEFAULTS):
  (1) wrong commit -> gentle higher/lower hint (kinds "too_high"/"too_low")
  (2) auto-sound on correct commit (the wiring plays the target note's
      OWN sample at low gain — never a foreign sound)
  (3) strict left-to-right slot order (the cursor never skips)

Hear the melody -> repeat it on the piano, note by note, with per-note
OK/Cancel commit, unlimited retries, gentle higher/lower hints, and two
reveal modes: "grow" (default: the melody replays one note longer each
round; notes confirmed in earlier rounds stay locked — the player only
answers the NEW note) and "whole" (full melody each time; the player
answers every slot left to right). Wrong is NEVER punished (LOCKED):
no counter of wrong attempts exists anywhere in this module.

PURE LOGIC: no rendering, no audio, no pygame, no Conductor. The wiring
plays sounds (from the spell's OWN palette) and shows texts (which come
from pack.json: intro_text, hint_higher, hint_lower, success_text —
this module returns KINDS, the pack provides the words).

HOW THE WIRING DRIVES ONE ROUND:
  LISTENING  auto-play the notes in notes_to_play() through the
             Conductor (beat 0 .. the prefix's last end_beat), then call
             listening_finished(). The transport and BOTH scrub surfaces
             stay live in EVERY phase (Forgiving Forever); free
             re-listens do NOT re-enter LISTENING and never move the
             cursor.
  ECHOING    key click -> preview(midi) (the wiring also sounds that
             key — audition, Simon Principle). OK -> commit(), but ONLY
             when preview_midi is not None (keep the OK button disabled
             otherwise). Cancel -> cancel().
  on result  "correct":  wiring plays the confirm sound (target note's
             own sample, low gain). If phase() flipped to LISTENING
             (grow), auto-play the new prefix. If .puzzle_done, phase()
             is COMPLETE: full reward replay (notes_to_play() now
             returns the whole melody) + success_text.
             "too_low":  the guess was BELOW the target -> show the
             pack's hint_higher text ("yours was a little low...").
             "too_high": the guess was ABOVE the target -> show the
             pack's hint_lower text. NOTE THE CROSSED NAMES — the
             pack's fields are named for the direction the player must
             GO, this module's kinds for what the guess WAS.

ERROR PHILOSOPHY (mirrors the Conductor): stray calls in the wrong
phase — preview() while LISTENING/COMPLETE, cancel() with nothing to
cancel, listening_finished() twice — are forgiving no-ops, ignored on
purpose. commit() misuse (no preview, or outside ECHOING) raises
ValueError with a plain-language message: that is a WIRING bug, and
bugs fail loudly while players never do.

ADDITIVE read-only accessors (beyond the frozen bone surface, for the
wiring and the staff's solid/hollow/dashed slots — recorded in the
Commentaries): reveal_mode, prefix_len, cursor, preview_midi,
slot_states().

Imports: standard library ONLY (see tests/test_purity.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from .spell_model import SpellData


class EchoPhase(Enum):
    LISTENING = auto()   # the melody (or its grown prefix) is being played
    ECHOING = auto()     # the player is answering, one note at a time
    COMPLETE = auto()    # celebration; wiring shows success_text


@dataclass(frozen=True)
class EchoResult:
    kind: str            # "correct" | "too_high" | "too_low"
    target_index: int    # which note of the melody was being answered
    puzzle_done: bool    # True when the last note lands


_REVEAL_MODES = ("grow", "whole")

# Slot state names (the staff will draw: solid / hollow / dashed).
SLOT_CONFIRMED = "confirmed"       # answered correctly; locked solid
SLOT_PROVISIONAL = "provisional"   # the cursor slot, holding a preview
SLOT_PLACEHOLDER = "placeholder"   # everything else (faint dashes)


class EchoLogic:
    """Frozen interface. reveal_mode: "grow" | "whole" (pack.json)."""

    def __init__(self, spell: SpellData, reveal_mode: str = "grow") -> None:
        if reveal_mode not in _REVEAL_MODES:
            raise ValueError(
                f"reveal_mode must be one of {_REVEAL_MODES}, got "
                f"{reveal_mode!r}. Check the puzzle's 'reveal_mode' field "
                f"in pack.json.")
        self._spell = spell
        self._mode = reveal_mode
        self._n = len(spell.notes)
        self._confirmed = 0          # notes 0.._confirmed-1 are locked solid
        self._prefix = self._n if reveal_mode == "whole" else 1
        self._phase = EchoPhase.LISTENING
        self._preview: Optional[int] = None

    # ---------------- the frozen bone surface ----------------

    def phase(self) -> EchoPhase:
        return self._phase

    def notes_to_play(self) -> tuple[int, ...]:
        """Note indices the wiring should replay this LISTENING round
        (a growing prefix in grow mode; everything in whole mode).
        After COMPLETE this is the whole melody — use it verbatim for
        the reward replay."""
        return tuple(range(self._prefix))

    def listening_finished(self) -> None:
        """Wiring reports the auto-play of the prefix has ended.
        Only meaningful while LISTENING; a stray call is ignored."""
        if self._phase is EchoPhase.LISTENING:
            self._phase = EchoPhase.ECHOING
            self._preview = None

    def preview(self, midi: int) -> None:
        """Player pressed a key but has not committed (no judgment yet).
        Overwrites any earlier preview. Ignored outside ECHOING (the
        wiring may still SOUND the key — audition is always allowed —
        but there is nothing to judge yet)."""
        if self._phase is EchoPhase.ECHOING:
            self._preview = int(midi)

    def commit(self) -> EchoResult:
        """OK pressed: judge the previewed note against the target.
        Simple integer comparison on precompiled midi numbers
        (BIBLE par.10 — the dumb-runtime doctrine)."""
        if self._phase is not EchoPhase.ECHOING:
            raise ValueError(
                "commit() called outside the ECHOING phase — the wiring "
                "must only enable OK while the player is answering.")
        if self._preview is None:
            raise ValueError(
                "commit() called with no previewed note — the wiring must "
                "keep the OK button disabled until a key is chosen.")
        target = self._spell.notes[self._confirmed]
        guess = self._preview
        self._preview = None          # committed or faded — either way, gone
        if guess == target.midi:
            self._confirmed += 1
            done = self._confirmed == self._n
            if done:
                self._phase = EchoPhase.COMPLETE
            elif self._mode == "grow" and self._confirmed == self._prefix:
                self._prefix += 1
                self._phase = EchoPhase.LISTENING
            return EchoResult("correct", target.index, done)
        kind = "too_high" if guess > target.midi else "too_low"
        return EchoResult(kind, target.index, False)

    def cancel(self) -> None:
        """Cancel pressed: forget the preview. Never a penalty; harmless
        in any phase."""
        self._preview = None

    # ------- ADDITIVE read-only accessors (Commentaries note) -------

    @property
    def reveal_mode(self) -> str:
        return self._mode

    @property
    def prefix_len(self) -> int:
        """How many notes the current round covers."""
        return self._prefix

    @property
    def cursor(self) -> Optional[int]:
        """Index of the slot being answered (strict left-to-right),
        or None once the puzzle is COMPLETE."""
        return None if self._phase is EchoPhase.COMPLETE else self._confirmed

    @property
    def preview_midi(self) -> Optional[int]:
        """The un-committed guess, or None. The staff draws the hollow
        provisional notehead at THIS pitch (the player sees their own
        guess, not the answer)."""
        return self._preview

    def slot_states(self) -> tuple[str, ...]:
        """One state per melody slot, length == number of notes, valid
        in every phase: SLOT_CONFIRMED (solid) / SLOT_PROVISIONAL
        (hollow, at preview_midi) / SLOT_PLACEHOLDER (faint dashes —
        players always see how many notes remain, NT par.II.5)."""
        states = []
        for i in range(self._n):
            if i < self._confirmed:
                states.append(SLOT_CONFIRMED)
            elif (i == self._confirmed
                  and self._phase is EchoPhase.ECHOING
                  and self._preview is not None):
                states.append(SLOT_PROVISIONAL)
            else:
                states.append(SLOT_PLACEHOLDER)
        return tuple(states)
```

📄 2. player/ui/bench_buttons.py — OK/Cancel, born in M3

Parent 3 wrote a version that never landed and I don't have his text, so per the honesty rule I wrote it fresh, matching the M2 widget family's style (pressed visual like the keyboard keys, palette from the transport).

```python
"""
bench_buttons.py — the OK / Cancel bench buttons. [M3 — Parent 4]

Scripture: BIBLE par.2 (OK/Cancel in fixed positions on the Bench) +
par.3.1 (OK commits the current note; Cancel clears the selection).
Parent 3 wrote a version that was never landed; this is Parent 4's,
matching the M2 widget family (pressed visual per bench_keyboard,
palette per bench_transport).

NO logic and NO audio in here: handle_event returns True exactly when
the button is activated (left-mouse released inside after pressing
inside — the standard forgiving button contract: dragging off before
release aborts). The wiring routes OK -> EchoLogic.commit() and
Cancel -> EchoLogic.cancel().

The wiring MUST keep OK disabled (.enabled = False) while EchoLogic
.preview_midi is None or the phase is not ECHOING — commit() raises on
misuse by design (wiring bugs fail loudly; players never do).

Keyboard mirrors (Enter = OK, Backspace = Cancel) belong to the
input-action layer in the wiring, NOT here — and must respect the
transport's .typing guard so the BPM box owns Enter while focused.
"""

from __future__ import annotations

import pygame

_BTN = (60, 60, 72)
_BTN_DISABLED = (42, 42, 50)
_TEXT = (225, 225, 225)
_TEXT_DISABLED = (110, 110, 120)
_OUTLINE = (70, 70, 80)
_SHADOW = (10, 10, 12)
_OK_ACCENT = (255, 196, 64)      # the family glow, on OK's outline only


class BenchButton:
    """Frozen interface. One fixed-position bench button."""

    def __init__(self, rect, label: str, accent: bool = False) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.accent = accent          # OK gets the warm outline
        self.enabled = True
        self._down = False
        self._font = None

    def handle_event(self, pygame_event) -> bool:
        """Returns True exactly once per activation."""
        ev = pygame_event
        if not self.enabled:
            self._down = False
            return False
        if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1
                and self.rect.collidepoint(ev.pos)):
            self._down = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            was_down = self._down
            self._down = False
            if was_down and self.rect.collidepoint(ev.pos):
                return True
        return False

    def draw(self, surface) -> None:
        if self._font is None:
            self._font = pygame.font.SysFont("consolas", 16, bold=True)
        pressed = self._down and self.enabled
        body = self.rect.move(0, 3) if pressed else self.rect
        if pressed:
            pygame.draw.rect(surface, _SHADOW, self.rect, border_radius=4)
        color = _BTN if self.enabled else _BTN_DISABLED
        pygame.draw.rect(surface, color, body, border_radius=4)
        outline = (_OK_ACCENT if (self.accent and self.enabled)
                   else _OUTLINE)
        pygame.draw.rect(surface, outline, body, 1, border_radius=4)
        if not pressed and self.enabled:
            pygame.draw.line(surface, _SHADOW,
                             (body.x + 2, body.bottom - 1),
                             (body.right - 3, body.bottom - 1), 2)
        text_color = _TEXT if self.enabled else _TEXT_DISABLED
        img = self._font.render(self.label, True, text_color)
        surface.blit(img, img.get_rect(center=body.center))
```

📄 3. tests/test_echo_logic.py — headless suite

```python
"""Headless tests for core/echo_logic.py (M3). Style: test_conductor.py —
pure logic, no pygame, no audio, spells built directly in memory."""

import pytest

from player.core.spell_model import SpellData, SpellNote
from player.core.echo_logic import (
    EchoLogic, EchoPhase, SLOT_CONFIRMED, SLOT_PROVISIONAL,
    SLOT_PLACEHOLDER,
)


def make_spell(midis):
    notes = tuple(
        SpellNote(index=i, midi=m, start_beat=float(i), duration_beats=1.0,
                  sample=f"audio/fake_{i}.mp3", gain=1.0)
        for i, m in enumerate(midis))
    return SpellData(spell_id="test", bpm=110.0, notes=notes,
                     total_beats=float(len(midis)), raw={})


MELODY = (60, 64, 67, 72)   # C4 E4 G4 C5


# ---------------- construction ----------------

def test_bad_reveal_mode_raises():
    with pytest.raises(ValueError):
        EchoLogic(make_spell(MELODY), reveal_mode="banana")


def test_initial_grow():
    e = EchoLogic(make_spell(MELODY), "grow")
    assert e.phase() is EchoPhase.LISTENING
    assert e.notes_to_play() == (0,)
    assert e.prefix_len == 1
    assert e.cursor == 0
    assert e.preview_midi is None
    assert e.slot_states() == (SLOT_PLACEHOLDER,) * 4


def test_initial_whole():
    e = EchoLogic(make_spell(MELODY), "whole")
    assert e.notes_to_play() == (0, 1, 2, 3)
    assert e.prefix_len == 4


# ---------------- phase transitions ----------------

def test_listening_finished_and_stray_calls():
    e = EchoLogic(make_spell(MELODY))
    e.preview(60)                     # stray during LISTENING: ignored
    assert e.preview_midi is None
    e.listening_finished()
    assert e.phase() is EchoPhase.ECHOING
    e.listening_finished()            # idempotent no-op
    assert e.phase() is EchoPhase.ECHOING


def test_cancel_is_always_harmless():
    e = EchoLogic(make_spell(MELODY))
    e.cancel()                        # LISTENING: no-op
    e.listening_finished()
    e.cancel()                        # ECHOING, nothing to cancel: no-op
    e.preview(64)
    e.cancel()
    assert e.preview_midi is None


# ---------------- preview ----------------

def test_preview_overwrites_and_shows_in_slots():
    e = EchoLogic(make_spell(MELODY))
    e.listening_finished()
    e.preview(62)
    e.preview(64)                     # overwrite is fine (re-audition)
    assert e.preview_midi == 64
    assert e.slot_states()[0] == SLOT_PROVISIONAL
    assert e.slot_states()[1:] == (SLOT_PLACEHOLDER,) * 3


# ---------------- commit: guards ----------------

def test_commit_without_preview_raises():
    e = EchoLogic(make_spell(MELODY))
    e.listening_finished()
    with pytest.raises(ValueError):
        e.commit()


def test_commit_outside_echoing_raises():
    e = EchoLogic(make_spell(MELODY))
    with pytest.raises(ValueError):
        e.commit()


# ---------------- commit: judgment ----------------

def test_wrong_commits_gentle_and_unlimited():
    e = EchoLogic(make_spell(MELODY))
    e.listening_finished()
    for guess, kind in ((72, "too_high"), (50, "too_low"), (61, "too_high")):
        e.preview(guess)
        r = e.commit()
        assert (r.kind, r.target_index, r.puzzle_done) == (kind, 0, False)
        assert e.phase() is EchoPhase.ECHOING       # never thrown out
        assert e.preview_midi is None               # the note gently fades
        assert e.cursor == 0                        # strict order holds
    e.preview(60)                                   # still welcome to win
    assert e.commit().kind == "correct"


def test_grow_full_walkthrough():
    e = EchoLogic(make_spell(MELODY), "grow")
    for round_no in range(4):
        assert e.phase() is EchoPhase.LISTENING
        assert e.notes_to_play() == tuple(range(round_no + 1))
        e.listening_finished()
        assert e.cursor == round_no                 # only the NEW note
        e.preview(MELODY[round_no])
        r = e.commit()
        assert r.kind == "correct"
        assert r.target_index == round_no
    assert r.puzzle_done is True
    assert e.phase() is EchoPhase.COMPLETE
    assert e.slot_states() == (SLOT_CONFIRMED,) * 4
    assert e.notes_to_play() == (0, 1, 2, 3)        # the reward replay
    assert e.cursor is None


def test_whole_full_walkthrough_no_relisten():
    e = EchoLogic(make_spell(MELODY), "whole")
    e.listening_finished()
    for i, midi in enumerate(MELODY):
        assert e.phase() is EchoPhase.ECHOING       # never back to LISTENING
        assert e.cursor == i
        e.preview(midi)
        r = e.commit()
        assert r.kind == "correct"
    assert r.puzzle_done is True
    assert e.phase() is EchoPhase.COMPLETE


def test_single_note_spell_completes_immediately():
    e = EchoLogic(make_spell((60,)), "grow")
    e.listening_finished()
    e.preview(60)
    r = e.commit()
    assert r.puzzle_done is True
    assert e.phase() is EchoPhase.COMPLETE


def test_complete_is_final():
    e = EchoLogic(make_spell((60,)), "whole")
    e.listening_finished()
    e.preview(60)
    e.commit()
    e.preview(64)                     # stray after COMPLETE: ignored
    assert e.preview_midi is None
    with pytest.raises(ValueError):
        e.commit()


def test_confirmed_slots_survive_grow_relisten():
    e = EchoLogic(make_spell(MELODY), "grow")
    e.listening_finished()
    e.preview(60)
    e.commit()
    assert e.phase() is EchoPhase.LISTENING         # round 2 replay
    assert e.slot_states()[0] == SLOT_CONFIRMED     # stays locked
    assert e.slot_states()[1] == SLOT_PLACEHOLDER
```

📬 4. Batch of questions for DeepSeek (please copy-paste, Nir 🙏)

PARENT 4 (Fable, M3) — QUESTION BATCH 1 for DeepSeek:

1. Please paste m2_demo.py (and m1_demo.py if it differs in wiring
   style) — POUR 2 (m3_demo.py) must reuse the ear-approved wiring +
   the keyboard-click -> sample resolver verbatim, and I will not
   guess their signatures from memory (Iron Rule 2).
2. layout.py is FROZEN — does it already reserve rects for OK/Cancel
   (BIBLE par.2 says they have fixed positions)? If not, please tell
   me what free pixels exist on the Bench so I can propose rects for
   Nir's eye (additive only; nothing moves).
3. Does test_purity.py auto-discover ALL core/ modules, or is it an
   explicit list needing one line for echo_logic? (Its docstring said
   "add to test_purity.py", suggesting a list.)
4. Confirm my POUR 1 files land cleanly against the current 65-test
   suite, and please append the MAP status line + this Commentaries
   par.5 draft:
   "M3 POUR 1 (Parent 4): core/echo_logic.py fattened -> MEAT with
   ADDITIVE read-only accessors (reveal_mode, prefix_len, cursor,
   preview_midi, slot_states) for the staff's solid/hollow/dashed
   slots; ui/bench_buttons.py born (BenchButton; OK must be disabled
   unless a preview exists — commit() raises on wiring misuse).
   Hint-name mapping: kind too_low -> pack hint_higher text, kind
   too_high -> pack hint_lower text (crossed names, documented)."
5. For POUR 2 I will propose the staff's ADDITIVE optional echo arg
   (draw(surface, spell, frame, flash_levels, echo=None)) exactly as
   Parent 3 planned — flag now if you foresee integration trouble.

🔜 What POUR 2 will contain (once the answers arrive)

    m3_demo.py: the full Echo experience on fixture_bench8 (grow) and fixture_bench20 (whole) — LISTENING auto-play through the Conductor (pause at the prefix's last end_beat → listening_finished()), key audition, OK/Cancel, the confirm sound (target's own sample at low gain), gentle hint texts, the COMPLETE reward replay, transport + both scrub surfaces live in every phase, and Enter/Backspace mirrors respecting transport.typing.
    The staff's additive echo arg: solid confirmed noteheads, hollow provisional at preview_midi, dashed placeholders.
    A small player/data/echo_tuning.json for the feel constants (confirm gain factor, replay gap) — constants in data, never code.

Nir — POUR 1 is ready for DeepSeek to land. May the Echo feel like the game finally answering back. 🌀🎹💚
