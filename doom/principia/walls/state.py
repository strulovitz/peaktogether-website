"""Off/On state per wall block (sticky). Tracks reading progress; saves/loads."""
from __future__ import annotations
from principia.assets.manager import AssetManager


class WallStateManager:
    def __init__(self, assets: AssetManager) -> None:
        raise NotImplementedError("M2")

    def register(self, block_id: str, entity, off_tex, on_tex) -> None:
        raise NotImplementedError("M2")

    def toggle(self, block_id: str) -> bool:
        """Return new state (True = on/colored)."""
        raise NotImplementedError("M2")

    def state(self, block_id: str) -> bool:
        raise NotImplementedError("M2")

    def progress(self, room_id: str) -> float:
        """Fraction of this room's blocks that are 'on' (0..1)."""
        raise NotImplementedError("M2")

    def save(self, path: str) -> None:
        raise NotImplementedError("M2")

    def load(self, path: str) -> None:
        raise NotImplementedError("M2")
