"""
schema.py — the single source of truth for all data that crosses module
boundaries. Every JSON file in a content pack validates against these
pydantic models. If it isn't defined here, modules must not pass it around.

Children: depend on these types. Never invent a parallel data shape.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

from principia.config import SCHEMA_VERSION

Vec3 = tuple[float, float, float]
Facing = Literal["N", "E", "S", "W"]
EdgeKind = Literal["depends_on", "generalizes", "example_of", "related"]
BlockType = Literal["diagram", "text"]


class _Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


# ============================================================ concept graph
class ConceptNode(_Base):
    id: str
    name: str
    importance: int = Field(ge=1, le=5)
    summary: str = ""


class ConceptEdge(_Base):
    source: str
    target: str
    weight: float = 1.0
    kind: EdgeKind = "related"
    label: str = ""


class ConceptGraph(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    title: str = ""
    nodes: list[ConceptNode]
    edges: list[ConceptEdge] = Field(default_factory=list)


# ============================================================ floorplan
class Rect(_Base):
    x: float
    z: float
    w: float
    d: float


class Door(_Base):
    id: str
    room: str
    corridor: str
    position: Vec3
    facing: Facing
    width: float


class RoomCell(_Base):
    id: str
    rect: Rect
    center: Vec3
    name_tile: str = ""
    doors: list[str] = Field(default_factory=list)


class Corridor(_Base):
    id: str
    from_room: str = Field(alias="from")
    to_room: str = Field(alias="to")
    spline: list[Vec3]
    width: float
    guide_color: str = "#ffcc00"


class Floorplan(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    ceiling_h: float
    rooms: list[RoomCell]
    corridors: list[Corridor] = Field(default_factory=list)
    doors: list[Door] = Field(default_factory=list)


# ============================================================ room content
class WallBlock(_Base):
    block_id: str
    type: BlockType
    off_png: str
    on_png: str
    colors: dict[str, str] = Field(default_factory=dict)  # group -> hex
    order: int = 0
    caption: str = ""


class Wall(_Base):
    wall_id: str
    facing: Facing
    blocks: list[WallBlock] = Field(default_factory=list)


class CeilingBand(_Base):
    band_id: str
    above_wall: str
    equation_png: str
    hidden_until_demon_dead: bool = True


class DemonCircle(_Base):
    offset: Vec3
    radius: float
    color: str
    role: str = "body"


class DemonSpec(_Base):
    demon_id: str
    position: Vec3
    hp: int = 3
    circles: list[DemonCircle] = Field(default_factory=list)
    spray_glyphs: list[str] = Field(default_factory=list)


class SecretDoorSpec(_Base):
    door_id: str
    wall_id: str
    tile_png: str
    position: Vec3
    boss: DemonSpec | None = None


class RoomContent(_Base):
    schema_version: str = SCHEMA_VERSION
    room_id: str
    walls: list[Wall] = Field(default_factory=list)
    ceiling_bands: list[CeilingBand] = Field(default_factory=list)
    demon: DemonSpec | None = None
    secret_door: SecretDoorSpec | None = None


# ============================================================ assets / save
class AssetEntry(_Base):
    off_png: str
    on_png: str
    w_px: int
    h_px: int


class Level(_Base):
    """Everything the runtime needs for one level, after loading."""
    schema_version: str = SCHEMA_VERSION
    level_id: str
    floorplan: Floorplan
    rooms: dict[str, RoomContent]


class SaveGame(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    blocks_on: list[str] = Field(default_factory=list)
    demons_dead: list[str] = Field(default_factory=list)
    secrets_open: list[str] = Field(default_factory=list)
