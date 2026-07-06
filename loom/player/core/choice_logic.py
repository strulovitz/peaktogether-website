"""
choice_logic.py — the Choice puzzle (comparative sonification). [BONE M5]

Scripture: BIBLE par.5 + Apocrypha pack.json schema. Two or three spells
sit behind labels A/B/C; the players listen (full transport + scrubbing
on each!), then answer a menu question. Wrong answers get the pack's
kind "explain" text and another try — forever (LOCKED).

PURE LOGIC: holds which spell is selected for listening and judges
answers against the pack data. Wiring owns Conductors and rendering.

FATTEN ME LIKE THIS (M5 parent): implement against pack_model's
ChoicePuzzle dataclass; headless tests. Add to test_purity.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnswerResult:
    correct: bool
    text: str            # the pack's explain text (kind, always)
    puzzle_done: bool    # True only when correct


class ChoiceLogic:
    """Frozen interface."""

    def __init__(self, puzzle) -> None:      # puzzle: pack_model.ChoicePuzzle
        raise NotImplementedError("M5")

    def labels(self) -> tuple[str, ...]:     # e.g. ("A", "B")
        raise NotImplementedError("M5")

    def spell_path_for(self, label: str) -> str:
        raise NotImplementedError("M5")

    def answer(self, option_index: int) -> AnswerResult:
        raise NotImplementedError("M5")
