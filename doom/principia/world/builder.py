"""Builds the Ursina entities for ONE cell (room or corridor)."""
from __future__ import annotations
from principia.schema import RoomCell, Corridor
from principia.assets.manager import AssetManager


def build_room(room: RoomCell, content, assets: AssetManager):
    """Return a CellEntities handle (has .destroy()) for one room."""
    raise NotImplementedError("M1")


def build_corridor(corr: Corridor, assets: AssetManager):
    raise NotImplementedError("M4")
