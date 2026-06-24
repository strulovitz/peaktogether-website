"""Loads/unloads the current cell so only one room/corridor exists at a time."""
from __future__ import annotations
from principia.schema import Floorplan
from principia.assets.manager import AssetManager


class RoomManager:
    def __init__(self, floorplan: Floorplan, assets: AssetManager) -> None:
        raise NotImplementedError("M4")

    def enter_cell(self, cell_id: str) -> None:
        raise NotImplementedError("M4")

    def current_cell(self) -> str:
        raise NotImplementedError("M4")

    def cell_entities(self):
        raise NotImplementedError("M4")
