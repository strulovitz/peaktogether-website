from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.0"

NodeId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
LevelId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
PageLabel = str  # printed label; may be ""
Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]
Hex  = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
GroupName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]


# ── SCHEMA 1 ──────────────────────────────────────────────────────────
class RawNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    local_label: str
    proposed_id: NodeId
    kind: str
    pages: list[PageLabel]
    summary: str
    importance_hint: int = Field(ge=1, le=5)


class NodesRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    edition: str
    nodes: list[RawNode]


# ── SCHEMA 2 ──────────────────────────────────────────────────────────
class RawCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phrase: str
    page_seen: PageLabel
    vague: bool = False


class RawCiteItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    local_label: str
    citations: list[RawCitation]
    summary: str


class CitationsRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    source: Literal["text", "image"]
    items: list[RawCiteItem]


# ── SCHEMA 3 ──────────────────────────────────────────────────────────
class RawInferEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_label: str
    target_label: str
    reason: str


class InferenceRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    edges: list[RawInferEdge]


# ── SCHEMA 4 ──────────────────────────────────────────────────────────
class PageEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page_label: PageLabel
    leaf_index: int = Field(ge=0)
    image_path: Optional[str] = None


class PageMap(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    pack_id: str
    pages: list[PageEntry]


# ── SCHEMA 5 ──────────────────────────────────────────────────────────
class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: NodeId
    name: str
    kind: str
    importance: int = Field(ge=1, le=5)
    pages: list[PageLabel]
    summary: str
    tags: list[str] = []


class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    source: NodeId
    target: NodeId
    kind: str = "depends_on"
    weight: float = 1.0
    label: str = ""


class ConceptGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    title: str
    edition: str
    seed: int
    nodes: list[Node]
    edges: list[Edge]


# ── SCHEMA 6 ──────────────────────────────────────────────────────────
class FloorRoom(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_id: NodeId
    map_xz: Vec2
    importance: int = Field(ge=1, le=5)
    map_radius_m: float
    map_color: Hex
    socket_y: float = 0.0


class Corridor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corridor_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    source: NodeId
    target: NodeId
    height_level: int
    cruise_y: float
    path_xz: list[Vec2]
    width_m: float


class Crossing(BaseModel):
    model_config = ConfigDict(extra="forbid")
    crossing_id: str
    over_corridor: str
    under_corridor: str
    at_xz: Vec2
    over_y: float
    under_y: float


class Floorplan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    seed: int
    rooms: list[FloorRoom]
    corridors: list[Corridor]
    crossings: list[Crossing]


# ── SCHEMA 7 ──────────────────────────────────────────────────────────
class EdgeProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    provenance: Literal["cited", "inferred"]
    snippet: str
    page_seen: Optional[PageLabel] = None
    agreement: Literal["both", "citation_only", "inference_only"]
    reason: str = ""
    vague: bool = False


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    edges: list[EdgeProvenance]
    flags: list[str]


# ── SCHEMA 8 ──────────────────────────────────────────────────────────
class MergeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = ""
    seed: int = 1729001
    importance_w_indeg: float = 0.6
    importance_w_hint: float = 0.4


# ── LEG 2 — PALETTE ──────────────────────────────────────────────────
class GroupColor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hi: Hex       # Stabilo / highlighter color (used under ink, at 40% opacity)
    ink: Hex      # saturated line color when hot; also the text color for \cg spans

class Palette(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    pack_id: str
    groups: dict[GroupName, GroupColor]
    grey_ink: Hex
    grey_text: Hex
    bg_key: Hex                    # flat background to render on then key out (magenta)
    map_importance: dict[str, Hex]  # keys "1".."5" → node ring + guide-line colors
    map_node_default: Hex


# ── LOADER HELPER ─────────────────────────────────────────────────────
class SchemaVersionError(ValueError):
    def __init__(self, path: str, found: str, expected: str):
        super().__init__(
            f"{path}: expected schema_version {expected!r}, found {found!r}"
        )


def load_json(path: str, model_cls: type) -> object:
    """Read a JSON file, assert schema_version=="1.0", parse and return the model instance."""
    import json

    with open(path, "r", encoding="utf-8") as fh:
        obj = json.load(fh)
    found = obj.get("schema_version")
    if found != SCHEMA_VERSION:
        raise SchemaVersionError(path, found, SCHEMA_VERSION)
    return model_cls.model_validate(obj)
