"""
pack_model.py — loads a Problem Pack (pack.json) into dataclasses. [BONE M7]

Scripture: Apocrypha par.2 (the pack.json schema — follow it EXACTLY).
Validation duties (plain-language errors, like spell_model's): every
dialogue path reaches "END"; every puzzle_after names a defined puzzle
or null; every spell path exists on disk; up to 4 options per node;
choice puzzles have exactly one correct answer.

FATTEN ME LIKE THIS (M7 parent): mirror spell_model.py's style — frozen
dataclasses, one load_pack(path), SpellLoadError-like error class,
unknown fields ignored, semantic version check (refuse newer major).
Headless tests with tiny hand-written packs. Add to test_purity.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DialogueOption:
    text: str
    goto: str                    # node id or "END"


@dataclass(frozen=True)
class DialogueNode:
    speaker: str
    text: str
    options: tuple[DialogueOption, ...]


@dataclass(frozen=True)
class SceneData:
    scene_id: str
    image: str                   # relative path to the baked PNG
    caption: str
    dialogue_start: str
    dialogue_nodes: dict         # node_id -> DialogueNode
    puzzle_after: str | None


@dataclass(frozen=True)
class PackData:
    pack_id: str
    title: str
    scenes: tuple[SceneData, ...]
    puzzles: dict                # puzzle_id -> EchoPuzzle | ChoicePuzzle (define in M7)
    raw: dict


def load_pack(path: str) -> PackData:
    raise NotImplementedError("M7")
