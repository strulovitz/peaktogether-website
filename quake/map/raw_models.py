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
FigureId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.f[0-9]+$")]
PairId   = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+$")]
DrawBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.fig$")]
TextBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.txt$")]
EqId     = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.eq[0-9]+$")]
OpName   = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_']*$")]
Ref      = OpName


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


# ── LEG 2 — RECIPE (coordinate-free construction op-list) ──────────────
class _Op(BaseModel):
    """Base for all construction ops."""
    model_config = ConfigDict(extra="forbid")
    name: OpName
    draw: Optional["Draw"] = None  # None = construction helper, computed but not drawn

# ---- attachments ----
class Label(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tex: str                            # full LaTeX, e.g. "$A$"
    placement: Literal["N","S","E","W","NE","NW","SE","SW","center"] = "NE"
    offset: Optional[Vec2] = None

class Draw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group: GroupName                    # palette key → color
    step: int = Field(ge=1)             # which proof step lights this element
    label: Optional[Label] = None
    marker: Literal["none","dot"] = "none"  # LOCKED: "tick" dropped per amendment

# ---- POINTS ----
class FreePoint(_Op):     op: Literal["free_point"];  rough_xy: Optional[Vec2] = None
class PointOn(_Op):       op: Literal["point_on"];    path: Ref; t: Optional[float] = None; near: Optional[Vec2] = None
class Intersect(_Op):     op: Literal["intersect"];   a: Ref; b: Ref; near: Optional[Vec2] = None
class Midpoint(_Op):      op: Literal["midpoint"];    a: Ref; b: Ref
class Foot(_Op):          op: Literal["foot"];        point: Ref; line: Ref
class ReflectPoint(_Op):  op: Literal["reflect_point"]; point: Ref; over: Ref

# ---- LINES / RAYS ----
class LineOp(_Op):        op: Literal["line"];        a: Ref; b: Ref
class Segment(_Op):       op: Literal["segment"];     a: Ref; b: Ref
class RayOp(_Op):         op: Literal["ray"];         a: Ref; b: Ref
class Parallel(_Op):      op: Literal["parallel"];    through: Ref; to: Ref
class Perpendicular(_Op): op: Literal["perpendicular"]; through: Ref; to: Ref
class TangentAt(_Op):     op: Literal["tangent_at"];  curve: Ref; at: Ref
class TangentFrom(_Op):   op: Literal["tangent_from"]; curve: Ref; frm: Ref; near: Optional[Vec2] = None
class Bisector(_Op):      op: Literal["bisector"];    a: Ref; vertex: Ref; b: Ref

# ---- CIRCLES / ARCS ----
class CircleCP(_Op):      op: Literal["circle_cp"];   center: Ref; through: Ref
class CircleCR(_Op):      op: Literal["circle_cr"];   center: Ref; radius_points: Optional[tuple[Ref, Ref]] = None; radius_value: Optional[float] = None
class Circle3(_Op):       op: Literal["circle_3"];    a: Ref; b: Ref; c: Ref
class Arc(_Op):           op: Literal["arc"];         center: Ref; frm: Ref; to: Ref; direction: Literal["ccw","cw"] = "ccw"

# ---- CONICS (Newton) ----
class EllipseFoci(_Op):   op: Literal["ellipse_foci"];   f1: Ref; f2: Ref; through: Ref
class EllipseAxes(_Op):   op: Literal["ellipse_axes"];   center: Ref; major_end: Ref; minor_end: Ref
class ParabolaFD(_Op):    op: Literal["parabola_fd"];    focus: Ref; directrix: Ref
class HyperbolaFoci(_Op): op: Literal["hyperbola_foci"]; f1: Ref; f2: Ref; through: Ref
class Conic5(_Op):        op: Literal["conic_5"];        p1: Ref; p2: Ref; p3: Ref; p4: Ref; p5: Ref

# ---- COMPOUND / SEQUENCES ----
class Polygon(_Op):       op: Literal["polygon"];   points: list[Ref] = Field(min_length=3)
class Polyline(_Op):      op: Literal["polyline"];  points: list[Ref] = Field(min_length=2)
class Series(_Op):
    op: Literal["series"]
    along: Ref
    to_curve: Optional[Ref] = None
    count: int = Field(ge=1, le=64)
    kind: Literal["inscribed_rects","circumscribed_rects","ordinates","chords","tangent_polygon"]

# ---- MARKS / STANDALONE LABELS ----
class AngleMark(_Op):     op: Literal["angle_mark"]; a: Ref; vertex: Ref; b: Ref; right: bool = False
class FloatLabel(_Op):    op: Literal["label"];      at: Ref  # draw must be set; carries the text

RecipeOp = Annotated[
    "FreePoint | PointOn | Intersect | Midpoint | Foot | ReflectPoint | "
    "LineOp | Segment | RayOp | Parallel | Perpendicular | TangentAt | TangentFrom | Bisector | "
    "CircleCP | CircleCR | Circle3 | Arc | "
    "EllipseFoci | EllipseAxes | ParabolaFD | HyperbolaFoci | Conic5 | "
    "Polygon | Polyline | Series | AngleMark | FloatLabel",
    Field(discriminator="op"),
]

class StepGloss(BaseModel):
    model_config = ConfigDict(extra="forbid")
    index: int = Field(ge=1)
    gloss: str

class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    figure_id: FigureId
    node_id: NodeId
    edition: str
    caption: str
    n_steps: int = Field(ge=1)
    steps: list[StepGloss]
    ops: list[RecipeOp]

# ── LEG 2 — TEXT BLOCK ─────────────────────────────────────────────────
class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: TextBlockId
    latex: str
    groups_used: list[GroupName]

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
