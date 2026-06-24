from __future__ import annotations

import random

from ursina import Entity, color, destroy, Vec3 as _UVec3

from principia.schema import CeilingBand, Vec3
from principia.assets.manager import AssetManager


class CeilingManager:
    def __init__(self, assets: AssetManager) -> None:
        self._assets = assets  # reserved/unused in M3
        self._bands: dict[str, list[tuple]] = {}
        self._revealed: set[str] = set()
        self._red = color.rgb(178, 0, 0)

    def register_band(self, room_id: str, band: CeilingBand, entity) -> None:
        self._bands.setdefault(room_id, []).append((band, entity))
        if getattr(band, "hidden_until_demon_dead", False):
            entity.enabled = False
        else:
            entity.enabled = True
        entity.color = self._red

    def reveal(self, room_id: str) -> None:
        if room_id in self._revealed:
            return
        self._revealed.add(room_id)
        for _band, entity in self._bands.get(room_id, []):
            entity.enabled = True
            entity.color = self._red
            if hasattr(entity, "fade_in"):
                entity.fade_in(duration=0.8)

    def spray_from(self, origin, glyph_texes: list) -> None:
        if not glyph_texes:
            return
        for tex in glyph_texes:
            q = Entity(
                model="quad",
                texture=tex,
                position=origin,
                scale=0.6,
                double_sided=True,
                billboard=True,
            )
            dvec = _UVec3(
                random.uniform(-1, 1),
                random.uniform(0.0, 1.0),
                random.uniform(-1, 1),
            ).normalized() * 2.5
            target = _UVec3(origin[0], origin[1], origin[2]) + dvec
            q.animate_position(target, duration=0.8)
            q.fade_out(duration=0.8)
            destroy(q, delay=0.9)
