from __future__ import annotations

from math import sin
import random

from ursina import Entity, color, destroy

from principia.schema import DemonSpec, Vec3


# ---------------------------------------------------------------------------
# Pure, headless-testable helpers
# ---------------------------------------------------------------------------
class _Health:
    def __init__(self, hp: int) -> None:
        self.hp = hp
        self.dead = False

    def hit(self) -> bool:  # returns True ONLY on the lethal hit
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


# ---------------------------------------------------------------------------
# Demon
# ---------------------------------------------------------------------------
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
            c = Entity(
                model="sphere",
                parent=self.root,
                position=circle.offset,
                scale=circle.radius * 2,
                color=color.rgb(r, g, b),
                collider="sphere",
            )
            c.kind = "demon"
            c.demon = self  # back-reference for generic shooter handler
            self._circles.append(c)

    def update(self, dt: float) -> None:
        if self.is_dead():
            return
        self._t += dt
        self.root.y = self._base_y + sin(self._t * 2.0) * 0.1

    def hit(self, point) -> None:
        if self.is_dead():
            return
        if self._health.hit():  # lethal
            self._die()

    def is_dead(self) -> bool:
        return self._health.dead

    def on_death(self, callback) -> None:
        self._death_cb = callback

    def _die(self) -> None:
        for c in self._circles:
            ang = random.uniform(0, 6.283185)
            elev = random.uniform(-0.5, 1.0)
            direction = type(c.world_position)(
                sin(ang), elev, sin(ang + 1.5708)
            ) if False else None
            # build a simple outward direction tuple-compatible offset
            from ursina import Vec3 as _UVec3
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
