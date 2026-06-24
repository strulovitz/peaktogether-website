"""Concept graph -> spatial floorplan + baked floor-map image. Deterministic."""
from __future__ import annotations
from principia.schema import ConceptGraph, Floorplan


def layout_level(graph: ConceptGraph, seed: int = 0) -> Floorplan:
    """spring_layout -> room sizing -> de-overlap -> b-spline corridors -> doors."""
    raise NotImplementedError("M4")


def render_floor_map(floorplan: Floorplan, out_png: str, size_px: int = 4096) -> None:
    raise NotImplementedError("M4")


def make_guide_lines(floorplan: Floorplan):
    raise NotImplementedError("M4")
