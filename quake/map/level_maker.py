from __future__ import annotations

import math
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

import math

from map.raw_models import (
    ConceptGraph,
    Floorplan,
    FloorRoom,
    Corridor,
    Crossing,
    Hex,
    NodeId,
    Vec2,
)
from map.layout_force import place_nodes, LayoutConfig
from map.layout_height import detect_crossings, assign_heights, HeightConfig


_DEV_PALETTE: dict[int, Hex] = {
    1: "#4F6D7A",
    2: "#3FA796",
    3: "#E6B800",
    4: "#E8743B",
    5: "#D81B60",
}


class LevelMakerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layout: LayoutConfig = LayoutConfig()
    height: HeightConfig = HeightConfig()
    map_radius_base_m: float = 2.0
    map_radius_per_importance_m: float = 1.0
    corridor_width_m: float = 3.0
    corridor_ramp_run_m: float = 6.0
    palette_map_importance: dict[int, Hex] = {}


def _insert_ramp_waypoints(
    path_xz: list[Vec2], ramp_run_m: float
) -> list[Vec2]:
    """Insert a ramp-top waypoint a short run in from each end, so the corridor
    has interior vertices that can hold cruise_y. Ramp run is clamped so a short
    corridor never over-ramps (<= 1/3 of the end segment length)."""
    if len(path_xz) < 2:
        return list(path_xz)

    pts = list(path_xz)

    def _lerp_in(a: Vec2, b: Vec2) -> Vec2:
        dx = b[0] - a[0]
        dz = b[1] - a[1]
        seg_len = math.hypot(dx, dz)
        if seg_len < 1e-9:
            return a
        run = min(ramp_run_m, seg_len / 3.0)
        f = run / seg_len
        return (a[0] + dx * f, a[1] + dz * f)

    start = pts[0]
    end = pts[-1]
    ramp_a = _lerp_in(start, pts[1])
    ramp_b = _lerp_in(end, pts[-2])

    return [start, ramp_a] + pts[1:-1] + [ramp_b, end]


def build_floorplan(graph: ConceptGraph, seed: int, cfg: "LevelMakerConfig") -> Floorplan:
    # STEP 1 — POSITIONS
    positions = place_nodes(graph, seed, cfg.layout)

    # STEP 2 — CROSSINGS
    crossings_raw = detect_crossings(positions, graph, cfg.height)

    # STEP 3 — HEIGHTS
    heights = assign_heights(crossings_raw, graph, cfg.height)

    # STEP 4 — BUILD ROOMS
    rooms: list[FloorRoom] = []
    for node in graph.nodes:
        importance = node.importance
        map_radius_m = cfg.map_radius_base_m + (importance - 1) * cfg.map_radius_per_importance_m
        map_color = cfg.palette_map_importance.get(
            importance, _DEV_PALETTE.get(importance, "#999999")
        )
        rooms.append(
            FloorRoom(
                room_id=node.id,
                map_xz=positions[node.id],
                importance=importance,
                map_radius_m=map_radius_m,
                map_color=map_color,
                socket_y=0.0,
            )
        )

    # Map corridor_id -> list of crossing points involving it
    crossings_by_corridor: dict[str, list[Vec2]] = {}
    for (corr_a, corr_b, at_xz) in crossings_raw:
        crossings_by_corridor.setdefault(corr_a, []).append(at_xz)
        crossings_by_corridor.setdefault(corr_b, []).append(at_xz)

    # STEP 5 — BUILD CORRIDORS
    corridors: list[Corridor] = []
    for edge in graph.edges:
        corridor_id = edge.id
        src_pos = positions[edge.source]
        tgt_pos = positions[edge.target]
        height_level = heights[edge.id]

        if height_level == 0:
            base_path: list[Vec2] = [src_pos, tgt_pos]
        else:
            pts = crossings_by_corridor.get(corridor_id, [])
            sorted_pts = sorted(
                pts,
                key=lambda p: (p[0] - src_pos[0]) ** 2 + (p[1] - src_pos[1]) ** 2,
            )
            base_path = [src_pos] + list(sorted_pts) + [tgt_pos]

        path_xz = _insert_ramp_waypoints(base_path, cfg.corridor_ramp_run_m)

        cruise_y = cfg.height.base_y + height_level * cfg.height.delta_y

        corridors.append(
            Corridor(
                corridor_id=corridor_id,
                source=edge.source,
                target=edge.target,
                height_level=height_level,
                width_m=cfg.corridor_width_m,
                path_xz=path_xz,
                cruise_y=cruise_y,
            )
        )

    # STEP 6 — BUILD CROSSINGS
    crossings: list[Crossing] = []
    for i, (corr_a, corr_b, at_xz) in enumerate(crossings_raw):
        h_a = heights[corr_a]
        h_b = heights[corr_b]

        if h_a > h_b:
            over_corridor, under_corridor = corr_a, corr_b
        elif h_b > h_a:
            over_corridor, under_corridor = corr_b, corr_a
        else:
            # tie -> alphabetically first is over
            if corr_a <= corr_b:
                over_corridor, under_corridor = corr_a, corr_b
            else:
                over_corridor, under_corridor = corr_b, corr_a

        over_y = cfg.height.base_y + heights[over_corridor] * cfg.height.delta_y
        under_y = cfg.height.base_y + heights[under_corridor] * cfg.height.delta_y
        assert over_y > under_y

        crossings.append(
            Crossing(
                crossing_id=f"crossing_{i}",
                over_corridor=over_corridor,
                under_corridor=under_corridor,
                at_xz=at_xz,
                over_y=over_y,
                under_y=under_y,
            )
        )

    # STEP 7 — EMIT
    rooms.sort(key=lambda r: r.room_id)
    corridors.sort(key=lambda c: c.corridor_id)

    return Floorplan(
        schema_version="1.0",
        level_id=graph.level_id,
        seed=seed,
        rooms=rooms,
        corridors=corridors,
        crossings=crossings,
    )
