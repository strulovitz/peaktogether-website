"""
echo_logic.py — the Simon-style Echo puzzle state machine. [BONE M3]

Scripture: BIBLE par.5 (core loop) + New Testament Part II (Echo machine).
Hear the melody -> repeat it on the piano, note by note, with per-note
OK/Cancel commit, unlimited retries, gentle higher/lower hints, and two
reveal modes: "grow" (default: melody replays one note longer each round)
and "whole" (full melody each time). Wrong is NEVER punished (LOCKED).

PURE LOGIC: no rendering, no audio, no pygame. The wiring plays sounds
(from the spell's OWN palette — target note at low gain; never foreign
sounds) and shows texts (which come from pack.json: intro_text,
hint_higher, hint_lower, success_text — this module returns KINDS, the
pack provides the words).

FATTEN ME LIKE THIS (M3 parent): implement against Conductor+SpellData
exactly as m1_demo wires them; drive melody playback by telling the
wiring WHICH prefix of notes to play (grow mode). Add to test_purity.py
and write a headless pytest suite in the style of test_conductor.py.
Simple arithmetic on precompiled midi numbers is allowed (BIBLE par.10).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

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


class EchoLogic:
    """Frozen interface. reveal_mode: "grow" | "whole" (pack.json)."""

    def __init__(self, spell: SpellData, reveal_mode: str = "grow") -> None:
        raise NotImplementedError("M3")

    def phase(self) -> EchoPhase:
        raise NotImplementedError("M3")

    def notes_to_play(self) -> tuple[int, ...]:
        """Note indices the wiring should replay this LISTENING round
        (a growing prefix in grow mode; everything in whole mode)."""
        raise NotImplementedError("M3")

    def listening_finished(self) -> None:
        raise NotImplementedError("M3: -> ECHOING")

    def preview(self, midi: int) -> None:
        """Player pressed a key but has not committed (no judgment yet)."""
        raise NotImplementedError("M3")

    def commit(self) -> EchoResult:
        """OK pressed: judge the previewed note against the target."""
        raise NotImplementedError("M3")

    def cancel(self) -> None:
        """Cancel pressed: forget the preview. Never a penalty."""
        raise NotImplementedError("M3")
