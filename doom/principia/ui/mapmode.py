"""2D wireframe automap overlay (Doom-style)."""
from __future__ import annotations
from principia.schema import Floorplan, Vec3


class MapMode:
    def __init__(self, floorplan: Floorplan, wall_state) -> None:
        raise NotImplementedError("M4")

    def toggle(self) -> None:
        raise NotImplementedError("M4")

    def update(self, player_pos: Vec3) -> None:
        raise NotImplementedError("M4")
