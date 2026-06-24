"""Translates the shared body. Movement is relative to body heading (R2)."""
from __future__ import annotations
from principia.control.input import InputManager


class Mover:
    def __init__(self, camera, input_mgr: InputManager, nav) -> None:
        raise NotImplementedError("M2")

    def update(self, dt: float) -> None:
        raise NotImplementedError("M2")
