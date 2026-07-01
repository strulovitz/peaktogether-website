from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.0"

NodeId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
LevelId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
PageLabel = str  # printed label; may be ""
Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]
Hex  = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
GroupName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]  # ⚠️ DEPRECATED 2026-06-29 — replaced by LocalColor per-station. Kept for backward compat only.

# ── COLOR SYSTEM v2 (Nir's model, 2026-06-29) ─────────────────────────
class LocalColor(BaseModel):
    """A per-element local color assignment. NOT global — fresh per station.
    The ``name`` is what the matching text uses to reference it."""
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")   # "blue","red","green" — local within station
    hex: Hex                                            # e.g. "#1E6FE0"
FigureId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.f[0-9]+$")]
PairId   = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+$")]
DrawBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.fig$")]
TextBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.txt$")]
EqId     = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.eq[0-9]+$")]
OpName   = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_'\s]*$")]
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
    # ⚠️ 2026-06-29 — `group: GroupName` REMOVED (was global-palette mistake).
    # Replaced by local-per-station color:
    local_color: Optional[LocalColor] = None  # None = uncolored (black on light bg / white on dark bg)
    step: int = Field(ge=1)                   # which proof step this element belongs to
    is_heart: bool = False                    # True = this element gets the bright Stabilo marker (current step's highlight heart)
    label: Optional[Label] = None
    marker: Literal["none","dot"] = "none"    # LOCKED: "tick" dropped per amendment

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
    # ⚠️ 2026-06-29 — `groups_used: list[GroupName]` REMOVED (was global-palette mistake).
    # Replaced by local per-station colors:
    colors_used: list[LocalColor]  # which local colors appear in \color{name}{...} spans in this block

# ── LEG 2 — PALETTE ──────────────────────────────────────────────────
class GroupColor(BaseModel):
    """⚠️ DEPRECATED 2026-06-29 — was for global palette groups. Kept for backward compat only."""
    model_config = ConfigDict(extra="forbid")
    hi: Hex       # Stabilo / highlighter color (used under ink, at 40% opacity)
    ink: Hex      # saturated line color when hot; also the text color for \cg spans

class Palette(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    pack_id: str
    # ⚠️ 2026-06-29 — `groups`, `grey_ink`, `grey_text` are DEPRECATED (old global-palette mistake).
    # The corrected model uses per-element `LocalColor` assignments; uncolored = black/white (never grey).
    # These fields are kept as optional for backward compat only — they are NOT used by the corrected pipeline.
    groups: dict[GroupName, GroupColor] = {}
    grey_ink: Optional[Hex] = None
    grey_text: Optional[Hex] = None
    bg_key: Hex                    # flat background to render on then key out (magenta)
    map_importance: dict[str, Hex]  # keys "1".."5" → node ring + guide-line colors
    map_node_default: Hex


# ── LEG 2 — MANIFEST (baked assets) ────────────────────────────────────
class AssetEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str
    kind: Literal["figure_off","figure_on","text_off","text_on","ceiling_neutral"]
    wall_path: str
    master_path: str
    px_w: int
    px_h: int
    content_bbox: tuple[int,int,int,int]
    dpi: int


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    assets: dict[str, AssetEntry]


# ── LEG 2 — ROOM SOURCE (per-node input to room_maker) ──────────────────
class FigureDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figure_id: FigureId
    asy_path: str
    recipe_path: str
    n_steps: int = Field(ge=1)
    caption: str
    # ⚠️ 2026-06-29 — `groups_used: list[GroupName]` REMOVED.
    colors_used: list[LocalColor]

class DrawingBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: DrawBlockId
    figure_id: FigureId
    highlight_step: int = Field(ge=1)

class StepPair(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId
    step_index: int = Field(ge=1)
    drawing: DrawingBlock
    text: TextBlock

class CeilingEq(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eq_id: EqId
    latex: str

class RoomSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    node_id: NodeId
    edition: str
    figures: list[FigureDecl]
    blocks: list[StepPair]
    final_pair_id: PairId
    ceiling_equations: list[CeilingEq]


# ── LEG 3 — BUILDCONFIG (additive; bake & layout & room-v3 constants) ───
class BuildConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    # bake
    bake_dpi_wall: int = 220
    bake_dpi_master: int = 600
    bake_trim_alpha: int = 8
    bake_pad_px: int = 16
    # layout
    layout_seed: int = 1729001
    layout_scale_m: float = 28.0
    height_delta_m: float = 4.5
    max_height_levels_warn: int = 7
    max_height_levels_fail: int = 12
    guide_w_imp: float = 0.6
    guide_w_dist: float = 0.4
    guide_max_lines: int = 3
    # room / panel sizing (amendment §4(f))
    room_px_per_m: float = 360
    panel_min_w_m: float = 0.6
    panel_max_w_m: float = 3.2
    panel_min_h_m: float = 0.5
    panel_max_h_m: float = 2.4
    panel_gap_m: float = 0.25
    pair_gap_m: float = 0.8
    wall_margin_m: float = 0.6
    room_headroom_m: float = 1.2
    room_min_w_m: float = 6.0
    room_min_d_m: float = 6.0
    room_min_h_m: float = 3.2
    panel_center_y_pref_m: float = 1.55
    importance_w_indeg: float = 0.6
    importance_w_hint: float = 0.4
    # room v3 door/placement (Apocrypha §3 + Parent 3 additions)
    door_width_m: float = 2.0
    door_height_m: float = 2.6
    door_min_separation_m: float = 2.6
    corner_clearance_m: float = 0.5
    room_target_aspect: float = 1.30
    room_pack_slack: float = 1.20
    room_grow_step_m: float = 0.5
    room_sizing_max_iters: int = 240
    aisle_depth_m: float = 1.6
    demon_offset_m: float = 1.0
    door_nudge_tol_rad: float = 0.20


# ── LEG 3 — PANEL PLACEMENT (amended PanelPairRT with explicit placement) ─
class PanelPlacementRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wall: Literal["N", "E", "S", "W"]
    slot_index: int = Field(ge=0)
    wall_slot: str
    center_xyz: Vec3
    width_m: float
    height_m: float
    yaw_rad: float

class PanelPairRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId
    step_index: int
    drawing_off_asset: str
    drawing_on_asset: str
    text_off_asset: str
    text_on_asset: str
    drawing_placement: PanelPlacementRT
    text_placement: PanelPlacementRT


# ── LEG 3 — ENEMY / CEILING RT ──────────────────────────────────────────
class EnemyRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enemy_id: str = Field(pattern=r"^[a-z][a-z0-9_]*\.demon$")
    spawn_xyz: Vec3
    health: int = 5

class CeilingEqRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eq_id: EqId
    asset_id: str
    pos_xyz: Vec3
    size_m: Vec2


# ── LEG 3 — ROOM RUNTIME v3 (Apocrypha: doors replace entrance) ────────
class IncidentEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    neighbor_id: NodeId
    neighbor_importance: int = Field(ge=1, le=5)
    bearing_rad: float

class RoomPortalSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: NodeId
    incident: list[IncidentEdge]

class DoorRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str
    neighbor_id: NodeId
    bearing_rad: float
    wall: Literal["N", "E", "S", "W"]
    center_xyz: Vec3
    width_m: float
    height_m: float
    normal_yaw_rad: float
    spawn_xyz: Vec3
    spawn_heading_rad: float

class RoomRuntime(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    room_id: NodeId
    dimensions_m: Vec3
    panel_pairs: list[PanelPairRT]
    final_pair_id: PairId
    hidden_door_wall_slot: str
    doors: list[DoorRT]
    enemy: EnemyRT
    ceiling_equations: list[CeilingEqRT]


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
