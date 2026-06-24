"""Detects which cell the players occupy and triggers door transitions."""
from __future__ import annotations
from principia.schema import Floorplan, Vec3


class Navigator:
    def __init__(self, floorplan: Floorplan, rooms) -> None:
        raise NotImplementedError("M4")

    def update(self, player_pos: Vec3) -> None:
        raise NotImplementedError("M4")

    def cell_at(self, pos: Vec3) -> str:
        raise NotImplementedError("M4")
