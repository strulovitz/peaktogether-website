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
