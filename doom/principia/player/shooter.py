"""Aims the reticle and fires a raycast; dispatches hits to registered handlers."""
from __future__ import annotations
from principia.control.input import InputManager


class Shooter:
    def __init__(self, camera, input_mgr: InputManager) -> None:
        raise NotImplementedError("M2")

    def update(self, dt: float) -> None:
        raise NotImplementedError("M2")

    def register_hit_handlers(self, on_wall, on_demon, on_secret) -> None:
        """on_wall(block_id), on_demon(demon, point), on_secret(door_id)."""
        raise NotImplementedError("M2")
