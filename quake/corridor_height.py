"""corridor_height.py — QUAKE single source of truth for corridor floor height.

A corridor is LOW at its two room ends (room socket_y) and HIGH along its
cruising middle (cruise_y). The ramp is the transition. This module is the ONE
place that rule lives; render_wire, nav_collision, and guidelines all call it,
so the wire you see, the floor you walk, and the guide-line you follow are
byte-identical.

PURE: numbers + dataclasses only. No GL, no IO. Fully unit-testable.
Coordinate law: floorplan XZ = map plane, Y up.
"""

from __future__ import annotations

from contracts import Corridor, FloorRoom, NodeId


def _socket_y(node_id: NodeId, rooms: list[FloorRoom]) -> float | None:
    for r in rooms:
        if r.room_id == node_id:
            return r.socket_y
    return None


def height_at_vertex(cor: Corridor, idx: int, rooms: list[FloorRoom]) -> float:
    """Y of corridor vertex `idx`. Endpoints sit at their room socket_y;
    every interior vertex sits at cruise_y. This is the ramp shape:
    socket -> (ramp) -> cruise ... cruise -> (ramp) -> socket."""
    path = cor.path_xz
    last = len(path) - 1
    if idx <= 0:
        sy = _socket_y(cor.source, rooms)
        return sy if sy is not None else cor.cruise_y
    if idx >= last:
        sy = _socket_y(cor.target, rooms)
        return sy if sy is not None else cor.cruise_y
    return cor.cruise_y


def floor_height(cor: Corridor, seg_i: int, t: float, rooms: list[FloorRoom]) -> float:
    """Interpolated walkable floor Y at parameter t in [0,1] along segment seg_i
    (vertex seg_i -> vertex seg_i+1)."""
    y_start = height_at_vertex(cor, seg_i, rooms)
    y_end = height_at_vertex(cor, seg_i + 1, rooms)
    return y_start + (y_end - y_start) * t
