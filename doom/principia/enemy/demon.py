from __future__ import annotations

from math import sin
import random

from ursina import Entity, color, destroy, Vec3 as _UVec3

from principia.schema import DemonSpec, Vec3


class _Health:
    def __init__(self, hp: int) -> None:
        self.hp = hp
        self.dead = False

    def hit(self) -> bool:
        if self.dead:
            return False
        self.hp -= 1
        if self.hp <= 0:
            self.dead = True
            return True
        return False


def add_offset(anchor, offset) -> tuple[float, float, float]:
    return (anchor[0] + offset[0], anchor[1] + offset[1], anchor[2] + offset[2])


def hex_to_rgb(hexstr: str) -> tuple[int, int, int]:
    s = hexstr.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


class Demon:
    def __init__(self, spec: DemonSpec, position: Vec3, parent=None) -> None:
        self._health = _Health(spec.hp)
        self._death_cb = None
        self._t = 0.0
        self._base_y = position[1]

        self.root = Entity(position=position)
        if parent is not None:
            self.root.parent = parent

        self._circles = []
        for circle in spec.circles:
            r, g, b = hex_to_rgb(circle.color)
            # Project Ursina expects normalized 0-1 floats (see builder._rgb01);
            # 0-255 ints render as white.
            c = Entity(
                model="sphere",
                parent=self.root,
                position=circle.offset,
                scale=circle.radius * 2,
                color=color.rgba(r / 255, g / 255, b / 255, 1),
                collider="sphere",
            )
            c.kind = "demon"
            c.demon = self
            self._circles.append(c)

    def update(self, dt: float) -> None:
        if self.is_dead():
            return
        self._t += dt
        self.root.y = self._base_y + sin(self._t * 2.0) * 0.1

    def hit(self, point) -> None:
        if self.is_dead():
            return
        if self._health.hit():
            self._die()

    def is_dead(self) -> bool:
        return self._health.dead

    def on_death(self, callback) -> None:
        self._death_cb = callback

    def _die(self) -> None:
        for c in self._circles:
            dvec = _UVec3(
                random.uniform(-1, 1),
                random.uniform(-0.3, 1.0),
                random.uniform(-1, 1),
            ).normalized() * 3
            c.animate_position(c.world_position + dvec, duration=0.6)
            c.animate_scale(0, duration=0.6)
            destroy(c, delay=0.7)

        if self._death_cb:
            self._death_cb()
