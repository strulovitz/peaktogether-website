"""Harmless demon made of coloured sprite circles. Death = disintegration."""
from __future__ import annotations
from principia.schema import DemonSpec, Vec3


class Demon:
    def __init__(self, spec: DemonSpec, position: Vec3) -> None:
        raise NotImplementedError("M3")

    def update(self, dt: float) -> None:
        raise NotImplementedError("M3")

    def hit(self, point: Vec3) -> None:
        raise NotImplementedError("M3")

    def is_dead(self) -> bool:
        raise NotImplementedError("M3")

    def on_death(self, callback) -> None:
        """callback() fires once; triggers ceiling reveal + equation spray."""
        raise NotImplementedError("M3")
