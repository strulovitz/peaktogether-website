from __future__ import annotations

from math import sin
import random

from ursina import Entity, color, destroy, scene, Vec3 as _UVec3

from principia.schema import DemonSpec, DemonCircle, Vec3


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


def _to_color(hexstr: str):
    r, g, b = hex_to_rgb(hexstr)
    # Project convention: normalized 0-1 floats (see world/builder._rgb01).
    return color.rgba(r / 255, g / 255, b / 255, 1)


class Demon:
    def __init__(self, spec: DemonSpec, position: Vec3, parent=None) -> None:
        self._health = _Health(spec.hp)
        self._death_cb = None
        self._t = 0.0
        self._base_y = position[1]

        self.root = Entity(position=position, parent=parent or scene)

        self._circles: list[Entity] = []
        # Sort so the big body is drawn first; eyes/teeth (smaller) drawn after
        # and pushed slightly outward so the opaque body doesn't occlude them.
        circles = sorted(spec.circles, key=lambda c: c.radius, reverse=True)
        body_radius = circles[0].radius if circles else 0.0

        for circle in circles:
            off = _UVec3(*circle.offset)
            # Features (smaller than body) get nudged outward along their
            # offset direction so they sit proud of the body surface.
            if circle.role != "body" and off.length() > 0:
                off = off.normalized() * (body_radius + circle.radius * 0.5)

            c = Entity(
                model="sphere",
                parent=self.root,
                position=off,
                scale=circle.radius * 2,
                color=_to_color(circle.color),
                collider="sphere",
                double_sided=True,
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
        # Reparent each piece to the scene at its current WORLD transform so it
        # flies independently instead of being dragged by the shared root.
        for c in self._circles:
            wp = c.world_position
            c.world_parent = scene
            c.world_position = wp

            direction = _UVec3(
                random.uniform(-1, 1),
                random.uniform(-0.3, 1.0),
                random.uniform(-1, 1),
            )
            if direction.length() == 0:
                direction = _UVec3(0, 1, 0)
            direction = direction.normalized() * random.uniform(2.5, 4.0)

            c.animate_position(c.world_position + direction, duration=0.6)
            c.animate_scale(0, duration=0.6)
            c.collider = None
            destroy(c, delay=0.7)

        destroy(self.root, delay=0.7)

        if self._death_cb:
            self._death_cb()
