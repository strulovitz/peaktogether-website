"""
progress.py — the forgiving little save file. [BONE M7]

Scripture: BIBLE (no punishment, replay anything). Saves ONLY comfort:
per pack — last scene reached, puzzles completed, lab unlocked. Never
scores, never timers, never failure counts (LOCKED: nothing shaming
exists, so nothing shaming can be saved).

FATTEN ME LIKE THIS (M7 parent): one JSON file in the user's home
(e.g. ~/.loom_progress.json). Corrupt/missing file = fresh start with a
gentle console note, never a crash. Headless tests via tmp_path.
Imports: standard library ONLY. Add to test_purity.py.
"""

from __future__ import annotations


class Progress:
    """Frozen interface."""

    @staticmethod
    def load(path: str | None = None) -> "Progress":
        raise NotImplementedError("M7")

    def save(self) -> None:
        raise NotImplementedError("M7")

    def last_scene(self, pack_id: str) -> str | None:
        raise NotImplementedError("M7")

    def set_last_scene(self, pack_id: str, scene_id: str) -> None:
        raise NotImplementedError("M7")

    def mark_puzzle_complete(self, pack_id: str, puzzle_id: str) -> None:
        raise NotImplementedError("M7")

    def is_puzzle_complete(self, pack_id: str, puzzle_id: str) -> bool:
        raise NotImplementedError("M7")
