from __future__ import annotations

from ursina import mouse, held_keys

import principia.config as config


def edge(prev: bool, cur: bool) -> bool:
    return bool(cur) and not bool(prev)


def scale_aim(vx: float, vy: float, sens: float) -> tuple[float, float]:
    return (vx * sens, vy * sens)


class InputManager:
    def __init__(self) -> None:
        # previous-state flags (must not touch Ursina here)
        self._prev_shoot = False
        self._prev_pause = False
        self._prev_map = False
        self._prev_read = False

        # edge flags computed in the last poll()
        self._shoot_edge = False
        self._pause_edge = False
        self._map_edge = False
        self._read_edge = False

    def poll(self) -> None:
        cur_shoot = bool(mouse.left)
        cur_pause = bool(held_keys["escape"])
        cur_map = bool(held_keys["m"])
        cur_read = bool(held_keys["r"])

        self._shoot_edge = edge(self._prev_shoot, cur_shoot)
        self._pause_edge = edge(self._prev_pause, cur_pause)
        self._map_edge = edge(self._prev_map, cur_map)
        self._read_edge = edge(self._prev_read, cur_read)

        self._prev_shoot = cur_shoot
        self._prev_pause = cur_pause
        self._prev_map = cur_map
        self._prev_read = cur_read

    def move_axis(self) -> tuple[float, float]:
        strafe = held_keys["d"] - held_keys["a"]
        forward = held_keys["w"] - held_keys["s"]
        return (strafe, forward)

    def body_yaw_delta(self) -> float:
        return 0.0

    def aim_delta(self) -> tuple[float, float]:
        return scale_aim(mouse.velocity[0], mouse.velocity[1], config.MOUSE_SENSITIVITY)

    def shoot_pressed(self) -> bool:
        return self._shoot_edge

    def toggle_map_pressed(self) -> bool:
        return self._map_edge

    def read_mode_pressed(self) -> bool:
        return self._read_edge

    def pause_pressed(self) -> bool:
        return self._pause_edge
