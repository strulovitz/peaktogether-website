"""Ceiling equation bands: hidden until the room's demon dies, then blood-red."""
from __future__ import annotations
from principia.schema import CeilingBand, Vec3
from principia.assets.manager import AssetManager


class CeilingManager:
    def __init__(self, assets: AssetManager) -> None:
        raise NotImplementedError("M3")

    def register_band(self, room_id: str, band: CeilingBand, entity) -> None:
        raise NotImplementedError("M3")

    def reveal(self, room_id: str) -> None:
        """Fade the room's equation bands in, tinted blood-red."""
        raise NotImplementedError("M3")

    def spray_from(self, origin: Vec3, glyph_texes: list) -> None:
        """Cosmetic: fling equation glyphs outward; they fade and vanish."""
        raise NotImplementedError("M3")
