from __future__ import annotations

from ursina import raycast

import principia.config as config
from principia.control.input import InputManager


def clamp_pitch(p: float, limit: float) -> float:
    return max(-limit, min(limit, p))


class Shooter:
    def __init__(self, camera, input_mgr: InputManager) -> None:
        self.camera = camera
        self.input_mgr = input_mgr
        self.on_wall = None
        self.on_demon = None
        self.on_secret = None
        self._pitch = 0.0

    def register_hit_handlers(self, on_wall, on_demon, on_secret) -> None:
        self.on_wall = on_wall
        self.on_demon = on_demon
        self.on_secret = on_secret

    def update(self, dt: float) -> None:
        # Look (assumes input_mgr.poll() already called this frame)
        yaw, pitch = self.input_mgr.aim_delta()
        self.camera.rotation_y += yaw
        self._pitch = clamp_pitch(self._pitch - pitch, config.PITCH_CLAMP_DEG)
        self.camera.rotation_x = self._pitch

        # Shoot
        if self.input_mgr.shoot_pressed():
            hit = raycast(
                self.camera.world_position,
                self.camera.forward,
                distance=config.SHOOT_RANGE,
                ignore=(),
            )
            if hit.hit:
                self._dispatch_hit(hit.entity, hit.point)

    def _dispatch_hit(self, entity, point) -> None:
        kind = getattr(entity, "kind", None)
        if kind == "panel":
            if self.on_wall:
                self.on_wall(entity.block_id)
        elif kind == "demon":
            if self.on_demon:
                self.on_demon(entity, point)
        elif kind == "secret":
            if self.on_secret:
                self.on_secret(entity.door_id)
        # anything else / handler None → do nothing
