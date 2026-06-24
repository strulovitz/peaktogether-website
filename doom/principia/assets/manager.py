"""Turns manifest entries + png paths into engine textures (lazy, cached)."""
from __future__ import annotations


class AssetManager:
    def __init__(self, pack_dir: str) -> None:
        raise NotImplementedError("M1")

    def wall_textures(self, block_id: str):
        """Return (off_texture, on_texture) for a wall block."""
        raise NotImplementedError("M1")

    def equation_texture(self, eq_id: str):
        raise NotImplementedError("M3")

    def floor_map_texture(self, level_id: str):
        raise NotImplementedError("M4")

    def name_tile_texture(self, room_id: str):
        raise NotImplementedError("M4")
