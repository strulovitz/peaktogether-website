🗝️ QUAKE (Game 3) — SECOND CANON (Layer 3): THE FORMATS & INTERFACES STANDARD

Captured June 25, 2026, at Nir's request, VERBATIM / word-for-word, AS-IS. This is Parent 1 of Quake — Claude Opus 4.8, run ALONE (not Fusion), at "XHigh" reasoning effort — answering the prompt in `quake/BIBLE/PROMPT_TO_OPUS_FORMATS_AND_INTERFACES_STANDARD.md`. Nir named this the project's "Second Canon" (after the Old Testament `QUAKE_DOCTRINE_BY_FUSION.md` and the New Testament `QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`). Nothing below is edited.

⚠️ DEEPSEEK NOTE (not Opus's words): in §3.A.5 the "Op → Asymptote translation table" originally arrived BLANK in Nir's copy-paste. Opus re-sent it (June 25, 2026) and it is now RESTORED below as a LIST instead of a table (tables don't survive copy-paste) — the content is verbatim from Opus; only the table→list formatting was changed. Everything else in this document transmitted intact.

🛑 **SUPERSEDED — COLOR SYSTEM (2026-06-29).** The color/Stabilo design throughout this document (global fixed 5-group palette, "same group same color everywhere," grey off-state, cumulative `on_k` highlight) reflects the OLD misunderstanding — the same failure that froze the Wolfenstein box-room. Nir's true color system (authoritative, overrides this document AND the OT/NT): **(1)** per-station local matching colors, distinct within station, black/white uncolored (never grey); **(2)** current-step-only bright Stabilo on heart(s). See the **Commentaries §3 (Locked Decisions)** and the **Parent 13 + Parent 14 handoffs** for the full corrected spec. The verbiage below is kept unchanged as a fossil record.

--- BEGIN VERBATIM ---

Nir — I have the full doctrine and the two-legs document in context; nothing has dropped. This is the right next move, and you're right that only the holder of the whole system can set these. Below is Layer-3: The Formats & Interfaces Standard. Everything is verbatim, copy-paste-ready, and closed (no "child decides" anywhere).

Two honesty notes up front, then one non-blocking clarification:

    The only thing I still refuse to invent is Asymptote's real function names (e.g. whether it's intersectionpoint vs intersectionpoints, how a conic casts to a path). For those I define our wrapper convention (prooffig.asy) completely and verbatim, and mark the underlying Asymptote calls as ⟨confirm-from-docs⟩ — caught instantly by the compile loop you already approved. Everything that is ours is fully pinned.
    I am refining a few things the doctrine sketched loosely (the color_map indirection, the figure-per-step model). Where I refine, I say so. Treat this document as superseding the earlier sketches on those points.

Non-blocking clarification (does not stop you building): your Archive.org leaf→printed-page file almost certainly has its own shape. I define our canonical page_map.json below and a 10-line adapter brief to convert yours into it. If you paste me one line of your file later, I'll pin the adapter exactly. Until then, convert into the canonical form and proceed.

LAYER-3 · THE FORMATS & INTERFACES STANDARD

SCHEMA_VERSION = "1.0" — every JSON file carries "schema_version": "1.0". Loaders assert exact-string equality and fail loudly otherwise. Bumping it is an Architect-only event.

Organization (I reordered for sanity — invariants and the map first, so the formats read as one system):

    §1 — Data-Flow Map (who produces / who consumes each format)
    §2 — PART D: Shared Invariants (ID grammar, units, color rules, naming, correctness)
    §3 — PART A: AI-Emitted Formats (the formats with no external standard — most exhaustive)
    §4 — PART B: Generated Data Formats
    §5 — PART C: Module Interfaces (contracts.py made real)

§1 — DATA-FLOW MAP

```
                              PRODUCER                          → FORMAT (file)                → CONSUMER(S)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
CONTENT  Archive.org (you fetch)                                 source/*_djvu.txt, pages/*.png   citation_extract, READER AI
         adapter (you run)                                       page_map.json                    citation_extract, sanity
         STRUCTURE AI            ──────────────────────────────► nodes_raw.json                   merge
         citation_extract.py  (text) / CITATION AI (img fallback)► citations_raw.json              merge
         INFERENCE AI            ──────────────────────────────► inference_raw.json               merge
         READER AI               ──────────────────────────────► recipe.<figure_id>.json          EMITTER AI, prooffig_check
         EMITTER AI              ──────────────────────────────► figure.<figure_id>.asy           asy_compile, baker_figure, overlay_diff
         TEXT AI                 ──────────────────────────────► room_<node_id>.json (text blocks) baker_text, room_maker
         you + palette AI        ──────────────────────────────► palette.json                     palette_gen, validate
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
BUILD    merge.py                ──────────────────────────────► concept_graph.json               level_maker, sanity, validate
         merge.py                ──────────────────────────────► provenance.json (build-only)      sanity, you (audit)
         level_maker.py          ──────────────────────────────► floorplan.json                   assets→render_wire, guidelines
         palette_gen.py          ──────────────────────────────► palette.asy, palette.tex          baker_figure, baker_text
         baker_figure/baker_text ──────────────────────────────► assets/*.png + manifest.json      assets→render_room, readmode
         room_maker.py           ──────────────────────────────► room_runtime/room_<id>.json       assets→render_room, gameplay
─────────────────────────────────────────────────────────────────────────────────────────────────────────────
RUNTIME  assets.load_pack        ── reads floorplan/manifest/rooms_runtime/palette ──►  Pack       everything runtime
         gameplay.step           ──────────────────────────────► Event[] (in-memory)              app, render_*, audio
         state.save              ──────────────────────────────► savegame.json                    state.load (next run)
```

The single rule that makes this a system: every arrow is an id from the spine (§2.1). A node id minted by the STRUCTURE AI becomes the corridor id, the room-source filename, the figure-id prefix, the manifest asset keys, the savegame keys, and the runtime room id — unchanged.

§2 — PART D: SHARED INVARIANTS (authoritative, write-once)

2.1 The ID spine grammar

All ids are lowercase ASCII except geometric point-names inside a recipe (which may be uppercase letters, because they are the figure's letters). Validated by regex at build; any violation fails the build loudly.

| Entity | Grammar (regex) | Example |
|---|---|---|
| level_id | ^[a-z][a-z0-9_]*$ | principia_bk1_sec1 |
| node_id | ^[a-z][a-z0-9_]*$ | lemma_1, prop_11, cor_2_prop_4, law_2 |
| edge_id (derived) | ^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$ | edge.prop_1.to.law_2 |
| figure_id | ^<node_id>\.f[0-9]+$ | prop_1.f1 |
| pair_id | ^<node_id>\.s[0-9]+$ | prop_1.s3 |
| block_id (drawing) | ^<node_id>\.s[0-9]+\.fig$ | prop_1.s3.fig |
| block_id (text) | ^<node_id>\.s[0-9]+\.txt$ | prop_1.s3.txt |
| eq_id (ceiling) | ^<node_id>\.eq[0-9]+$ | prop_1.eq1 |
| enemy_id | ^<node_id>\.demon$ | prop_1.demon |
| group (color group) | ^[a-z][a-z0-9_]*$ | swept_area, tangent, radius |
| asset_id (manifest key) | see §4.6 | prop_1.f1.on.3, prop_1.s3.txt.off |
| recipe OpName / Ref | ^[A-Za-z][A-Za-z0-9_']*$ | A, S, Cc, arc1, tangent_at_P |

The hard equality (validated by validate.id_spine):

```
concept_graph.nodes[i].id
  == floorplan.rooms[j].room_id
  == room_<X>.json  where X == node_id   (filename stem)
  == room_runtime.room_id
  == savegame …rooms[X]
```

Mismatch, orphan room (room file with no node), dangling edge endpoint, or a block_id whose prefix ≠ its room's node_id → build fails with the offending id named.

2.2 schema_version handling

    Every JSON top-level object must contain "schema_version": "1.0".
    Every pydantic model uses model_config = ConfigDict(extra="forbid") — unknown fields are an error, not ignored. This is what stops a child from "improvising a field."
    Loaders call assert obj["schema_version"] == SCHEMA_VERSION before parsing; on mismatch raise SchemaVersionError(path, found, expected).

2.3 Coordinate system & units

    World (runtime & floorplan): right-handed, Y-up. Ground/map plane is XZ. Bridge/underpass height is +Y. Unit = meter (m). Angles in radians. Map points are written as [x, z] (2-tuples, ground plane); 3-D positions as [x, y, z].
    Recipe (figures): dimensionless "recipe units," y-up math convention, origin arbitrary. Absolute position/scale/rotation carry NO meaning — the overlay-diff tool fixes global placement. Only relative construction is authoritative. (This is locked amendment #2.)
    Baked images (pixels): origin top-left, +x right, +y down (standard image space). content_bbox = [x0, y0, x1, y1] in pixels, half-open.

2.4 Color-group naming rules

    Colors live in exactly one place: palette.json. Hex appears nowhere else, ever.
    A group name is a palette key. A figure element tagged group="tangent" and a text span \cg{tangent}{…} resolve to the same palette entry → same color in figure and prose, automatically. (This refines/removes the doctrine's per-figure color_map indirection: group names are the keys.)
    Every group referenced by any figure or text must exist in the pack's palette.json, else build fails.
    Reserved global keys (must always be present): grey_ink, grey_text, bg_key, and map_importance.1…map_importance.5.

2.5 File & directory naming (canonical layout)

```
pack_<pack_id>/
  pack.json
  palette.json
  build_config.json
  page_map.json
  source/
    <pack_id>_djvu.txt
    pages/leaf_0001.png …
  content/levels/<level_id>/
    nodes_raw.json
    citations_raw.json
    inference_raw.json
    concept_graph.json
    provenance.json                  ← build-world only; never shipped
    rooms/room_<node_id>.json
    figures/recipe.<figure_id>.json
    figures/figure.<figure_id>.asy
  build/                             ← generated, git-ignored, reproducible
    palette.asy
    palette.tex
    levels/<level_id>/
      floorplan.json
      rooms_runtime/room_<node_id>.json
      assets/<asset_id>.png
      assets/<asset_id>@master.png
      manifest.json
  dist/                              ← shipped bundle (build/ minus source & provenance)
```

2.6 The standing correctness rule (write-once, binds both legs)

    Correctness = fidelity to the printed page. We never claim mathematical truth. A figure is "correct" when your eyes, in the overlay-diff tool, judge the render to match the book's engraving "more or less." A graph edge is "correct" when it transcribes a citation phrase the book actually printed, with the verbatim snippet on record. Nothing in this project requires anyone to verify mathematics.

§3 — PART A: THE AI-EMITTED FORMATS

Shared scalar types used throughout (defined once; referenced everywhere):

```python
# contracts.py — shared scalars (Part C re-exports these)
from typing import Annotated, Literal, Any
from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.0"

Hex      = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]
NodeId   = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
LevelId  = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
GroupName= Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]
FigureId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.f[0-9]+$")]
PairId   = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+$")]
DrawBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.fig$")]
TextBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.txt$")]
EqId     = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.eq[0-9]+$")]
OpName   = Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9_']*$")]
Ref      = OpName
PageLabel= str   # printed label as a string, e.g. "41", "xii", "A-3"
Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]
```

3.A.1 — STRUCTURE pass output → nodes_raw.json

(a) Schema

```python
class RawNode(BaseModel):
    model_config = ConfigDict(extra="forbid")
    local_label: str          # exactly as printed, e.g. "Lemma I", "Prop. XI. Problem VI."
    proposed_id: NodeId       # the AI's normalized id; merge re-checks uniqueness
    kind: str                 # FREE TEXT: "lemma"|"proposition"|"corollary"|"law"|"definition"|…
    pages: list[PageLabel]    # printed page labels this item spans
    summary: str              # ONE plain-English sentence; no math literacy needed to read it
    importance_hint: int = Field(ge=1, le=5)   # AI's centrality guess; merge blends with in-degree

class NodesRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    edition: str              # free-text full citation sentence
    nodes: list[RawNode]
```

(b) Filled real example

```json
{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "edition": "Newton, Principia, trans. Andrew Motte, 1846 New York English ed.",
  "nodes": [
    {"local_label": "Law II", "proposed_id": "law_2", "kind": "law",
     "pages": ["19"], "summary": "Change of motion is proportional to the force impressed.",
     "importance_hint": 5},
    {"local_label": "Lemma I", "proposed_id": "lemma_1", "kind": "lemma",
     "pages": ["41"], "summary": "Quantities that tend to equality in a finite time become ultimately equal.",
     "importance_hint": 5},
    {"local_label": "Prop. I. Theorem I.", "proposed_id": "prop_1", "kind": "proposition",
     "pages": ["55","56"], "summary": "A body's radius to a fixed center sweeps equal areas in equal times.",
     "importance_hint": 5}
  ]
}
```

(c) Validation — proposed_id matches NodeId; proposed_id unique within file; importance_hint ∈ 1..5; pages non-empty; local_label non-empty. (Merge later enforces global uniqueness and numbering continuity.)

(d) Paste-to-AI snippet

> You are extracting the STRUCTURE of a classical mathematics text. From the material I paste (table of contents, section headers, and/or page text), output ONLY a JSON object exactly matching this shape: {"schema_version":"1.0","level_id":"<I give you this>","edition":"<I give you this>","nodes":[{"local_label":"<verbatim as printed>","proposed_id":"<lowercase id: 'Lemma VII'→lemma_7, 'Cor. 2. Prop. IV'→cor_2_prop_4, 'Law II'→law_2>","kind":"<free text>","pages":["<printed page label string>"],"summary":"<one plain-English sentence, no mathematics required to read it>","importance_hint":<1-5 guess of how central/foundational this result is>}]}. List every numbered or named result in printed order. Do not invent items you cannot see. Do not skip items. Output JSON only, no commentary.

3.A.2 — CITATION pass output → citations_raw.json (text-primary)

Since you now have the clean _djvu.txt, the preferred producer is the deterministic script citation_extract.py (regex over real text). The AI image-reading is the fallback for pages where OCR text is garbled. Both emit this identical format.

(a) Schema

```python
class RawCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phrase: str                 # VERBATIM as printed, e.g. "by the second Law"
    page_seen: PageLabel
    vague: bool = False         # True for "as shown above", "by what was demonstrated", etc.

class RawCiteItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    local_label: str            # the item doing the citing, matching a nodes_raw local_label
    citations: list[RawCitation]
    summary: str                # one plain sentence (redundant w/ nodes_raw; aids audit)

class CitationsRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    source: Literal["text", "image"]   # which producer made this
    items: list[RawCiteItem]
```

(b) Filled real example

```json
{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "source": "text",
  "items": [
    {"local_label": "Prop. I. Theorem I.",
     "summary": "Radii to a fixed center sweep equal areas in equal times.",
     "citations": [
        {"phrase": "by the first Law of Motion", "page_seen": "55", "vague": false},
        {"phrase": "by Cor. 1. of the Laws",     "page_seen": "55", "vague": false},
        {"phrase": "as was demonstrated above",   "page_seen": "56", "vague": true}
     ]}
  ]
}
```

(c) Validation — every local_label must match a nodes_raw label (merge cross-checks); phrase non-empty; page_seen matches PageLabel; if source=="text", each non-vague phrase must actually be a substring of the OCR text for page_seen (the script asserts this — a free hallucination guard).

(d) Paste-to-AI snippet (image fallback only)

> Here is a scanned page from a classical mathematics proof. For each numbered/named result whose statement or proof appears here, transcribe — VERBATIM, exactly as printed — every internal cross-reference it makes to another result (e.g. "by Lem. I", "per Cor. 2. Prop. IV", "by the second Law", "by Prop. XI of this Book"). Output ONLY this JSON: {"schema_version":"1.0","level_id":"<given>","source":"image","items":[{"local_label":"<the citing result, verbatim>","summary":"<one plain sentence>","citations":[{"phrase":"<verbatim phrase>","page_seen":"<printed page>","vague":<true if the reference names no specific result, e.g. 'as shown above'>}]}]}. Transcribe; never interpret the mathematics. If you see no citations for an item, give it an empty citations list.

Deterministic-script brief is in Part C (citation_extract.py). It scans the _djvu.txt (split into pages via page_map.json), runs the citation regex, and emits the same JSON with source="text".

3.A.3 — INFERENCE pass output → inference_raw.json

The understanding-based second opinion that powers the two-method disagreement check. It never directly creates shipped edges — it only corroborates or flags.

(a) Schema

```python
class RawInferEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_label: str          # the dependent result
    target_label: str          # the result it relies on
    reason: str                # one plain-English clause why (for your audit)

class InferenceRaw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    edges: list[RawInferEdge]
```

(b) Example

```json
{
  "schema_version": "1.0",
  "level_id": "principia_bk1_sec1",
  "edges": [
    {"source_label": "Prop. I. Theorem I.", "target_label": "Law II",
     "reason": "The equal-area proof builds each impulse from the change-of-motion law."},
    {"source_label": "Prop. I. Theorem I.", "target_label": "Lemma I",
     "reason": "The polygon-to-curve limit uses ultimate-equality of vanishing triangles."}
  ]
}
```

(c) Validation — labels must resolve to nodes; self-edges forbidden.

(d) Paste-to-AI snippet

> Here is the proof text of one result. Based ONLY on what the proof actually uses, list the earlier results it relies on. Output ONLY: {"schema_version":"1.0","level_id":"<given>","edges":[{"source_label":"<this result, verbatim>","target_label":"<a result it relies on, verbatim>","reason":"<one plain clause>"}]}. Prefer results the text explicitly names; include an unnamed reliance only if the proof clearly cannot proceed without it. Do not output anything else.

3.A.4 — READER AI output → recipe.<figure_id>.json (the construction recipe — the format I care most about)

This is the heart of Leg 2's authoring. It is a typed, ordered, coordinate-free construction op-list in JSON. No absolute coordinates are ever required — free points carry optional, recommended rough relative positions only (the overlay tool fixes everything global). Every drawn element is tagged (group, step). Steps segment the proof; the link to prose is by shared group names and shared step index.

(a) Schema — the op vocabulary (closed enum, discriminated on op)

```python
from typing import Union

# ---- attachments ----
class Label(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tex: str                                  # full LaTeX, e.g. "$A$", "$S$", "$c$"
    placement: Literal["N","S","E","W","NE","NW","SE","SW","center"] = "NE"
    offset: Vec2 | None = None                # optional fine nudge, recipe units

class Draw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group: GroupName                          # palette key → color
    step: int = Field(ge=1)                   # which proof step lights this element
    label: Label | None = None
    marker: Literal["none","dot","tick"] = "none"   # for points: usually "none" (letter only)

# ---- op base ----
class _Op(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: OpName
    draw: Draw | None = None                  # None ⇒ construction helper, computed but not drawn

# ---- POINTS ----
class FreePoint(_Op):     op: Literal["free_point"];  rough_xy: Vec2 | None = None   # recommended
class PointOn(_Op):       op: Literal["point_on"];    path: Ref; t: float | None = None; near: Vec2 | None = None
class Intersect(_Op):     op: Literal["intersect"];   a: Ref; b: Ref; near: Vec2 | None = None
class Midpoint(_Op):      op: Literal["midpoint"];    a: Ref; b: Ref
class Foot(_Op):          op: Literal["foot"];        point: Ref; line: Ref
class ReflectPoint(_Op):  op: Literal["reflect_point"]; point: Ref; over: Ref   # over a line

# ---- LINES / RAYS ----
class Line(_Op):          op: Literal["line"];        a: Ref; b: Ref
class Segment(_Op):       op: Literal["segment"];     a: Ref; b: Ref
class RayOp(_Op):         op: Literal["ray"];         a: Ref; b: Ref     # from a through b
class Parallel(_Op):      op: Literal["parallel"];    through: Ref; to: Ref
class Perpendicular(_Op): op: Literal["perpendicular"]; through: Ref; to: Ref
class TangentAt(_Op):     op: Literal["tangent_at"];  curve: Ref; at: Ref
class TangentFrom(_Op):   op: Literal["tangent_from"]; curve: Ref; frm: Ref; near: Vec2 | None = None
class Bisector(_Op):      op: Literal["bisector"];    a: Ref; vertex: Ref; b: Ref

# ---- CIRCLES / ARCS ----
class CircleCP(_Op):      op: Literal["circle_cp"];   center: Ref; through: Ref
class CircleCR(_Op):      op: Literal["circle_cr"];   center: Ref; radius_points: tuple[Ref,Ref] | None = None; radius_value: float | None = None
class Circle3(_Op):       op: Literal["circle_3"];    a: Ref; b: Ref; c: Ref
class Arc(_Op):           op: Literal["arc"];         center: Ref; frm: Ref; to: Ref; direction: Literal["ccw","cw"] = "ccw"

# ---- CONICS (Newton) ----
class EllipseFoci(_Op):   op: Literal["ellipse_foci"];   f1: Ref; f2: Ref; through: Ref
class EllipseAxes(_Op):   op: Literal["ellipse_axes"];   center: Ref; major_end: Ref; minor_end: Ref
class ParabolaFD(_Op):    op: Literal["parabola_fd"];    focus: Ref; directrix: Ref
class HyperbolaFoci(_Op): op: Literal["hyperbola_foci"]; f1: Ref; f2: Ref; through: Ref
class Conic5(_Op):        op: Literal["conic_5"];        p1: Ref; p2: Ref; p3: Ref; p4: Ref; p5: Ref

# ---- COMPOUND / SEQUENCES (ultimate-ratio figures) ----
class Polygon(_Op):       op: Literal["polygon"];   points: list[Ref] = Field(min_length=3)
class Polyline(_Op):      op: Literal["polyline"];  points: list[Ref] = Field(min_length=2)
class Series(_Op):
    op: Literal["series"]
    along: Ref                                  # a segment or arc to subdivide
    to_curve: Ref | None = None                 # curve the ordinates/rects reach to
    count: int = Field(ge=1, le=64)
    kind: Literal["inscribed_rects","circumscribed_rects","ordinates","chords","tangent_polygon"]

# ---- MARKS / STANDALONE LABELS ----
class AngleMark(_Op):     op: Literal["angle_mark"]; a: Ref; vertex: Ref; b: Ref; right: bool = False
class FloatLabel(_Op):    op: Literal["label"];      at: Union[Ref, Vec2]   # draw must be set; carries the text

RecipeOp = Annotated[
    Union[FreePoint,PointOn,Intersect,Midpoint,Foot,ReflectPoint,
          Line,Segment,RayOp,Parallel,Perpendicular,TangentAt,TangentFrom,Bisector,
          CircleCP,CircleCR,Circle3,Arc,
          EllipseFoci,EllipseAxes,ParabolaFD,HyperbolaFoci,Conic5,
          Polygon,Polyline,Series,AngleMark,FloatLabel],
    Field(discriminator="op")
]

class StepGloss(BaseModel):
    model_config = ConfigDict(extra="forbid")
    index: int = Field(ge=1)
    gloss: str                 # one plain-English line: what this step shows (also the hook for the text block)

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
```

(b) Filled real example — Newton Prop. I equal-areas figure (illustrative format example; the real construction comes from the scan + overlay-diff, per §2.6):

```json
{
  "schema_version": "1.0",
  "figure_id": "prop_1.f1",
  "node_id": "prop_1",
  "edition": "Newton, Principia, trans. Andrew Motte, 1846 New York English ed.",
  "caption": "Equal areas swept in equal times: the polygonal path and the parallel construction Cc.",
  "n_steps": 3,
  "steps": [
    {"index": 1, "gloss": "The body's straight-line path through points A, B, C."},
    {"index": 2, "gloss": "Radii drawn from the center of force S to A, B, C — the swept triangles."},
    {"index": 3, "gloss": "Through C draw Cc parallel to SB; triangle SBc equals SAB, proving equal areas."}
  ],
  "ops": [
    {"name": "S", "op": "free_point", "rough_xy": [0.0, -2.0], "draw": {"group": "radius", "step": 2, "label": {"tex": "$S$", "placement": "S"}}},
    {"name": "A", "op": "free_point", "rough_xy": [-3.0, 2.0], "draw": {"group": "path", "step": 1, "label": {"tex": "$A$", "placement": "NW"}}},
    {"name": "B", "op": "free_point", "rough_xy": [0.0, 2.6],  "draw": {"group": "path", "step": 1, "label": {"tex": "$B$", "placement": "N"}}},
    {"name": "C", "op": "free_point", "rough_xy": [3.0, 2.0],  "draw": {"group": "path", "step": 1, "label": {"tex": "$C$", "placement": "NE"}}},

    {"name": "AB", "op": "segment", "a": "A", "b": "B", "draw": {"group": "path", "step": 1}},
    {"name": "BC", "op": "segment", "a": "B", "b": "C", "draw": {"group": "path", "step": 1}},

    {"name": "SA", "op": "segment", "a": "S", "b": "A", "draw": {"group": "radius", "step": 2}},
    {"name": "SB", "op": "segment", "a": "S", "b": "B", "draw": {"group": "radius", "step": 2}},
    {"name": "SC", "op": "segment", "a": "S", "b": "C", "draw": {"group": "radius", "step": 2}},

    {"name": "lineAB", "op": "line", "a": "A", "b": "B"},
    {"name": "parC",   "op": "parallel", "through": "C", "to": "SB"},
    {"name": "c", "op": "intersect", "a": "parC", "b": "lineAB", "near": [-1.5, 2.3],
        "draw": {"group": "construction", "step": 3, "label": {"tex": "$c$", "placement": "NW"}}},
    {"name": "Cc", "op": "segment", "a": "C", "b": "c", "draw": {"group": "construction", "step": 3}},
    {"name": "Sc", "op": "segment", "a": "S", "b": "c", "draw": {"group": "construction", "step": 3}}
  ]
}
```

(c) Validation rules (enforced by validate.recipe + prooffig_check; build fails on any):

    figure_id startswith node_id + ".f"; node_id matches a real node.
    len(steps) == n_steps; step indices are exactly 1..n_steps, unique.
    All names unique; every Ref resolves to an earlier op (forward references forbidden → guarantees constructibility order).
    Type compatibility (the validator enforces): point-args must reference point-producing ops (free_point, point_on, intersect, midpoint, foot, reflect_point); line/parallel/perpendicular/tangent_* args needing a line must reference a line-producing op; tangent_*, point_on, intersect curve args must reference a path/circle/conic/arc producer; series.along must be a segment or arc.
    Every drawn op's draw.step ∈ 1..n_steps.
    Every step 1..n_steps has ≥1 drawn op (else its on_k would equal off).
    circle_cr has exactly one of radius_points / radius_value.
    FloatLabel must have draw set with a label.
    Every draw.group exists in the pack palette.json.
    No coordinate field is ever required; presence of rough_xy/near never affects validity, only the EMITTER's starting guess.

(d) Paste-to-AI snippet (READER)

> You are reading ONE figure from a classical geometry book. I paste the cropped figure image and its caption/surrounding text. Produce a CONSTRUCTION RECIPE as JSON exactly matching the schema I paste below. Rules you must obey: (1) Express the figure as an ORDERED list of construction ops — points, then the lines/circles/conics/arcs built from them — using ONLY the listed op kinds. (2) NEVER rely on absolute coordinates: every later object must be defined constructively (intersection, midpoint, parallel, perpendicular, tangent, foot, through-points). The only coordinates allowed are OPTIONAL rough rough_xy hints on free_points and OPTIONAL near disambiguators on intersect/tangent_from — these are rough relative placements only; global position/scale/rotation will be fixed later by a human tool, so do not try to match the page's exact scale or angle. (3) Name every object (you may use the figure's own letters: A, B, S, c…). (4) Tag every element that should be DRAWN with draw:{group,step,label?}; leave draw:null for helper objects. group is a lowercase semantic name (e.g. "radius","path","construction","tangent","swept_area") — reuse the SAME group name for the same concept so the prose can match its color. (5) Segment the proof into steps and set each drawn element's step to the step where it first appears/matters; fill steps[] with a one-line plain-English gloss per step. (6) Output JSON ONLY. [PASTE THE Recipe SCHEMA HERE.]

━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — BEGIN ✚ ━━━━━━━━━━━━━━━
**Added** 2026-06-25 by DeepSeek. **Decided by** Claude Opus 4.8 (Parent 1) in the "remaining gaps" answer. **Status:** LOCKED — was recorded only in chat; preserved here at its correct section. **What:** `Draw.marker` is narrowed.

In §3.A.4's `Draw` schema (above), `marker: Literal["none","dot","tick"]` is amended to **`marker: Literal["none","dot"]`** (the `"tick"` option is dropped). Reason: `prooffig.asy`'s `drawAll` only renders `none`/`dot`; `"tick"` was half-wired. Equal-length / tick marks, if ever needed, are expressed as explicit small segments or via the `angle_mark` op, and added properly in a later version.
━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — END ✚ ━━━━━━━━━━━━━━━

3.A.5 — EMITTER AI output → figure.<figure_id>.asy (the house convention)

The EMITTER turns the recipe into Asymptote against our frozen helper prooffig.asy. Two files are involved: our convention (verbatim, fixed) and the generated figure (a strict template).

prooffig.asy — OUR convention (verbatim; computes NO geometry — Asymptote's geometry module does)

```
// prooffig.asy — drawing/registration convention. v1.0. DO NOT add geometry here.
// Asymptote's `geometry` module computes all geometry; this only records & strokes.
import geometry;
access "palette.asy" as pal;     // generated: pen pal.hi(string g); pen pal.ink(string g); pen pal.greyInk;

struct Elem {
  path  p;          // the stroked path (for points: a tiny dot path, or nullpath if label-only)
  bool  isLabel;
  string tex; pair at; align a;   // label fields
  string group; int step;
  string marker;    // "none" | "dot" | "tick"
}
Elem[] ELEMS;

void elem(path p, string group, int step, string marker="none") {
  Elem e; e.p=p; e.isLabel=false; e.group=group; e.step=step; e.marker=marker; ELEMS.push(e);
}
void lbl(string tex, pair at, string group, int step, align a=NoAlign) {
  Elem e; e.isLabel=true; e.tex=tex; e.at=at; e.a=a; e.group=group; e.step=step; ELEMS.push(e);
}

// highlight = -1 → OFF (whole figure grey). highlight = k → ON_k (step k wears the Stabilo).
void drawAll(picture pic=currentpicture, int highlight) {
  // pass 1: Stabilo underlay for hot, non-label elements
  for (Elem e : ELEMS)
    if (!e.isLabel && e.step==highlight)
      draw(pic, e.p, pal.hi(e.group)+opacity(0.40)+linewidth(7pt)+squarecap);
  // pass 2: ink — hot saturated, others neutral grey
  for (Elem e : ELEMS)
    if (!e.isLabel) {
      pen ink = (e.step==highlight) ? pal.ink(e.group)+linewidth(1.4pt)
                                     : pal.greyInk+linewidth(1.0pt);
      draw(pic, e.p, ink);
      if (e.marker=="dot")  dot(pic, point(e.p,0), ink);
    }
  // pass 3: labels follow the same hot/grey rule
  for (Elem e : ELEMS)
    if (e.isLabel)
      label(pic, e.tex, e.at, e.a, (e.step==highlight) ? pal.ink(e.group) : pal.greyInk);
}
```

figure.<figure_id>.asy — the REQUIRED template the EMITTER must follow

```
// figure.prop_1.f1.asy  — generated by EMITTER from recipe.prop_1.f1.json
// MUST follow this 4-zone structure exactly.
import prooffig;

// ───────── ZONE 1: settings (fixed) ─────────
int highlight=-1;            // overridden at bake time:  asy -u "highlight=2" …
size(12cm);                  // size only; absolute placement is irrelevant (overlay tool aligns)

// ───────── ZONE 2: construction (Asymptote geometry; one line per recipe op, in order) ─────────
pair S=(0,-2), A=(-3,2), B=(0,2.6), C=(3,2);          // free_point rough_xy
// segments/lines are paths; points stay as pair/point
line SB = line(S,B);                                   // ⟨confirm `line(point,point)` in geometry docs⟩
line lineAB = line(A,B);
line parC = parallel(C, SB);                           // ⟨confirm `parallel(point,line)`⟩
pair c = intersectionpoint(parC, lineAB);              // ⟨confirm exact intersection fn name⟩

// ───────── ZONE 3: registration (one elem()/lbl() per DRAWN recipe element) ─────────
elem((path)(A--B), "path", 1);    elem((path)(B--C), "path", 1);
lbl("$A$", A, "path", 1, NW);     lbl("$B$", B, "path", 1, N);   lbl("$C$", C, "path", 1, NE);
elem((path)(S--A), "radius", 2);  elem((path)(S--B), "radius", 2);  elem((path)(S--C), "radius", 2);
lbl("$S$", S, "radius", 2, S);
elem((path)(C--c), "construction", 3);  elem((path)(S--c), "construction", 3);
lbl("$c$", c, "construction", 3, NW);

// ───────── ZONE 4: render (fixed) ─────────
drawAll(highlight);
```

(c) Validation (prooffig_check.lint, static/text-level — no math): file imports prooffig; declares int highlight=-1;; ends with drawAll(highlight);; every elem/lbl group exists in palette; steps used are contiguous 1..n and n == recipe.n_steps; zones present in order. Plus the compile gate: asy_compile must return ok=True. (The ⟨confirm-from-docs⟩ Asymptote names are validated by compiling, not by me asserting them.)

(d) Paste-to-AI snippet (EMITTER) — always pasted together with: the recipe JSON, prooffig.asy, the pinned asy_geometry_reference.txt, and 2 golden example figures.

> Translate this construction recipe into one Asymptote file following the REQUIRED 4-zone template I paste (settings; construction; registration; render). Rules: (1) Use ONLY Asymptote's geometry module for construction; use the function names from the reference doc I paste — do not guess names. (2) Emit construction lines in the recipe's op order, one Asymptote statement per op. (3) For every recipe element whose draw is not null, emit exactly one elem(...) (curves) or lbl(...) (points/labels) with the SAME group and step. (4) Do not invent elements not in the recipe. (5) Keep int highlight=-1; and end with drawAll(highlight);. (6) If a construction would be degenerate with the rough coordinates, adjust ONLY the free_point rough coordinates — never change the construction logic. Output the .asy file only. Here are the recipe, the prooffig.asy contract, the geometry reference, and two worked examples: […]

Op → Asymptote translation table (guidance pasted to the EMITTER; names marked ⟨…⟩ are confirmed from the reference doc, never from memory):

[DEEPSEEK NOTE — NOT OPUS'S WORDS: this was originally a table that came through blank; Opus re-sent it (June 25, 2026) and it is restored here as a LIST so it survives copy-paste. The content below is Opus's verbatim; only table→list formatting changed. Each entry: **op** — Asymptote construction — *result type* — *reg. (if drawn)* — *notes*. Lead-in from Opus: "Names in ⟨…⟩ are confirmed by the EMITTER against the pinned `asy_geometry_reference.txt` and proven by the compile loop — never asserted from memory. 'Result type' tells the EMITTER what the op produces (for later references); 'Reg.' tells it how the drawn version is registered through `prooffig.asy`."]

- **free_point** — `pair A=(x,y);` (rough_xy only as a starting guess) — *result:* point — *reg:* `lbl(...)`; `dot` if `marker=="dot"` — global placement is irrelevant (overlay tool aligns)
- **point_on** — `point P=⟨relpoint(path,t)⟩;` or pick nearest of `⟨intersectionpoints⟩` to `near` — *result:* point — *reg:* lbl — use `t` if given, else `near`
- **intersect** — `pair P=⟨intersectionpoint(a,b)⟩;` or `⟨intersectionpoints(a,b)⟩` then pick nearest to `near` — *result:* point — *reg:* lbl — `near` disambiguates multiple roots
- **midpoint** — `pair M=⟨midpoint(A--B)⟩;` — *result:* point — *reg:* lbl
- **foot** — `point F=⟨projection(line)*P⟩` / `⟨foot⟩`-equivalent — *result:* point — *reg:* lbl — perpendicular foot of point on line
- **reflect_point** — `point R=⟨reflect(line)*P⟩;` — *result:* point — *reg:* lbl — mirror point across `over` (a line)
- **line** — `line L=⟨line(A,B)⟩;` — *result:* line — *reg:* `elem((path)L,...)` — infinite line; for drawing, clip to the picture box
- **segment** — `path s=A--B;` — *result:* path — *reg:* `elem((path)s,...)`
- **ray** — `⟨halfline(A,B)⟩` or line clipped from A through B — *result:* line/path — *reg:* elem — from `a` through `b`
- **parallel** — `line L=⟨parallel(P,refline)⟩;` — *result:* line — *reg:* elem — through `through`, parallel to `to`
- **perpendicular** — `line L=⟨perpendicular(P,refline)⟩;` — *result:* line — *reg:* elem — through `through`, perpendicular to `to`
- **tangent_at** — `line t=⟨tangent of conic/circle at point⟩;` — *result:* line — *reg:* elem — `at` lies on the curve
- **tangent_from** — `line[] T=⟨tangents(conic/circle, externalpoint)⟩;` pick nearest to `near` — *result:* line — *reg:* elem — two tangents in general → `near` selects
- **bisector** — `line b=⟨bisector(A,vertex,B)⟩;` — *result:* line — *reg:* elem — interior angle bisector ray/line
- **circle_cp** — `circle c=⟨circle(center, abs(through-center))⟩;` — *result:* circle — *reg:* `elem((path)c,...)` — radius = |center→through|
- **circle_cr** — `circle c=⟨circle(center, R)⟩;` where `R=abs(P-Q)` (radius_points) or literal — *result:* circle — *reg:* elem — exactly one of points/value
- **circle_3** — `circle c=⟨circle(A,B,C)⟩;` — *result:* circle — *reg:* elem — through 3 points
- **arc** — `path a=⟨arc(center,from,to,dir)⟩;` — *result:* path — *reg:* elem — direction = ccw/cw
- **ellipse_foci** — `ellipse e=⟨ellipse(F1,F2,through)⟩;` — *result:* conic — *reg:* `elem((path)e,...)` — foci + one point on it
- **ellipse_axes** — `ellipse e=⟨ellipse(center, a, b, angle)⟩;` with `a=abs(major_end-center)`, `b=abs(minor_end-center)`, `angle=dir(major_end-center)` — *result:* conic — *reg:* elem — center + axis endpoints
- **parabola_fd** — `parabola p=⟨parabola(focus, directrix_line)⟩;` — *result:* conic — *reg:* elem — focus + directrix line
- **hyperbola_foci** — `hyperbola h=⟨hyperbola(F1,F2,through)⟩;` — *result:* conic — *reg:* elem — foci + one point
- **conic_5** — `conic k=⟨conic(p1,p2,p3,p4,p5)⟩;` — *result:* conic — *reg:* elem — general conic through 5 pts
- **polygon** — `path P=A--B--C--...--cycle;` — *result:* path — *reg:* elem — closed
- **polyline** — `path P=A--B--C--...;` — *result:* path — *reg:* elem — open
- **series** — a `for`-loop emitting the N sub-paths; register the whole family with ONE `elem(...)` per sub-path under the same group,step — *result:* path family — *reg:* elem ×N — see pattern below
- **angle_mark** — compute a small arc between rays vertex→a and vertex→b (or a right-angle square if `right`), as a path; register via elem — *result:* path — *reg:* elem — keeps it highlight-able (do not use a direct-draw `markangle` that bypasses prooffig)
- **label** — `lbl(tex, at, group, step, placement);` (`at` is a point ref or a literal pair) — *result:* — — *reg:* lbl — standalone floating label; `draw.label` required

series realization pattern (the EMITTER writes this; it's how the ultimate-ratio / inscribed-rectangle figures get drawn while staying highlight-able):

```
// kind == "inscribed_rects", along == segment AB on the base, to_curve == the curve
for (int i = 0; i < count; ++i) {
  real t0 = i/(real)count, t1 = (i+1)/(real)count;
  pair x0 = ⟨relpoint(along, t0)⟩, x1 = ⟨relpoint(along, t1)⟩;
  pair y0 = ⟨vertical drop from x0 up to to_curve⟩, y1 = ⟨...from x1...⟩;
  path rect = x0 -- ⟨inscribed corner⟩ -- ⟨...⟩ -- x1 -- cycle;
  elem(rect, "swept_area", 3);     // same group+step ⇒ the whole family lights as one step
}
```

(circumscribed_rects, ordinates, chords, tangent_polygon are the same loop with the corner rule swapped. The overlay-diff tool verifies the family matches the engraving; the count the book draws is what the READER reports.)

3.A.6 — The EXPLAINING-TEXT block (TEXT AI) — lives inside room_<node_id>.json

The text block is full LaTeX with color spans marked by our macro \cg{group}{words}. One source string; the baker compiles it twice (off ⇒ \cg greys everything; on ⇒ \cg colors by group). This is what couples prose color to figure color.

(a) Schema (the TextBlock portion of room source; full room source in §4.3)

```python
class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: TextBlockId
    latex: str                 # full LaTeX; color via \cg{group}{...}; math via $...$ / \[...\]
    groups_used: list[GroupName]   # every group name appearing in a \cg span (for validation)
```

(b) Example

```json
{
  "block_id": "prop_1.s3.txt",
  "latex": "Through $C$ draw \\cg{construction}{$Cc$} parallel to \\cg{radius}{$SB$}, meeting \\cg{path}{$AB$} produced in \\cg{construction}{$c$}. Then triangle $SBc$ equals triangle $SAB$, since they stand on the same base $SB$ and between the same parallels. Hence the area swept in each equal time is the same: $[\\,SAB\\,]=[\\,SBC\\,]$.",
  "groups_used": ["construction", "radius", "path"]
}
```

(c) Validation — block_id grammar + prefix == room node_id; every group inside a \cg{…}{…} span is listed in groups_used; every groups_used entry exists in palette.json; the LaTeX compiles under both the off and on preambles (baker gate).

(d) Paste-to-AI snippet (TEXT)

> Write the explaining text for ONE proof step. I paste the step's plain-English gloss, the figure's recipe (so you know the element letters and their group names), and the book's wording for this step. Output ONE JSON object: {"block_id":"<node_id>.s<k>.txt","latex":"<full LaTeX>","groups_used":[…]}. In the LaTeX, wrap each phrase that names a figure element in \cg{<group>}{<phrase>}, using the SAME group name that element has in the recipe (so the word is colored to match the drawing). Use normal LaTeX math (…). Keep faithful to the book's reasoning. Output JSON only.

3.A.7 — palette.json (authored per pack)

The single home of all hex. palette_gen.py compiles it into palette.asy and palette.tex.

(a) Schema

```python
class GroupColor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    hi:  Hex     # Stabilo / highlighter color (used under ink, at 40% opacity)
    ink: Hex     # saturated line color when hot; also the text color for \cg spans

class Palette(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    pack_id: str
    groups: dict[GroupName, GroupColor]
    grey_ink:  Hex                         # neutral ink for non-hot figure elements
    grey_text: Hex                         # neutral text for \cg in OFF bake
    bg_key:    Hex                         # flat background to render on then key out
    map_importance: dict[Literal["1","2","3","4","5"], Hex]   # node ring + guide-line colors
    map_node_default: Hex
```

(b) Example

```json
{
  "schema_version": "1.0",
  "pack_id": "principia",
  "groups": {
    "path":         {"hi": "#FFE08A", "ink": "#E8A200"},
    "radius":       {"hi": "#A8D8FF", "ink": "#1E6FE0"},
    "construction": {"hi": "#FFB3C7", "ink": "#D81B60"},
    "tangent":      {"hi": "#B9F6CA", "ink": "#00A35A"},
    "swept_area":   {"hi": "#E1BEE7", "ink": "#8E24AA"}
  },
  "grey_ink":  "#7A7A7A",
  "grey_text": "#8A8A8A",
  "bg_key":    "#FF00FF",
  "map_importance": {"1": "#4F6D7A", "2": "#3FA796", "3": "#E6B800", "4": "#E8743B", "5": "#F5F2E8"},
  "map_node_default": "#9AA0A6"
}
```

(c) Validation — all hex match Hex; reserved keys present; every group referenced by any recipe/text exists here (cross-checked at build); map_importance has exactly keys "1".."5".

(d) Snippet (optional, palette AI)

> Propose a beautiful, high-contrast color palette as JSON matching this schema: a hi/ink pair per concept group I list, plus grey_ink, grey_text, bg_key (a flat color that never appears in figures, e.g. magenta), and map_importance 1–5 graded cool→warm. Output JSON only.

Generated palette.tex (by palette_gen, verbatim form):

```
% palette.tex — generated. Baker prepends ONE of the two \cg definitions.
\usepackage{xcolor}
\definecolor{pathink}{HTML}{E8A200}
\definecolor{radiusink}{HTML}{1E6FE0}
\definecolor{constructionink}{HTML}{D81B60}
% … one \definecolor{<group>ink} per group …
\definecolor{greytext}{HTML}{8A8A8A}
% OFF bake prepends:  \newcommand{\cg}[2]{\textcolor{greytext}{#2}}
% ON  bake prepends:  \newcommand{\cg}[2]{\textcolor{#1ink}{#2}}
```

Generated palette.asy (verbatim form):

```
// palette.asy — generated.
pen rgbhex(string h){ return rgb(h); }   // ⟨confirm rgb("E8A200") hex form in asy docs⟩
pen greyInk = rgbhex("7A7A7A");
pen hi(string g){
  if(g=="path") return rgbhex("FFE08A");
  if(g=="radius") return rgbhex("A8D8FF");
  if(g=="construction") return rgbhex("FFB3C7");
  return greyInk;
}
pen ink(string g){
  if(g=="path") return rgbhex("E8A200");
  if(g=="radius") return rgbhex("1E6FE0");
  if(g=="construction") return rgbhex("D81B60");
  return greyInk;
}
```

§4 — PART B: GENERATED DATA FORMATS

4.1 page_map.json (our canonical page index)

```python
class PageEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page_label: PageLabel      # printed label, string
    leaf_index: int            # 0-based leaf in the scan/djvu
    image_path: str | None = None

class PageMap(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    pack_id: str
    pages: list[PageEntry]
```

```json
{"schema_version":"1.0","pack_id":"principia",
 "pages":[{"page_label":"55","leaf_index":74,"image_path":"source/pages/leaf_0075.png"}]}
```

Validation: page_label unique; leaf_index ≥ 0 and unique. Adapter brief: a 10-line script converting your Archive.org leaf→label file into this; paste one line of yours and I pin it.

━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — BEGIN ✚ ━━━━━━━━━━━━━━━
**Added** 2026-06-25 by DeepSeek. **Decided by** Claude Opus 4.8 (Parent 1) in the "remaining gaps" answer, after Nir supplied his Archive file's real shape. **Status:** LOCKED — was recorded only in chat; preserved here at its correct section. **What:** the §4.1 validation is finalized, plus the `page_map_adapter.py` child brief.

The §4.1 validation above is AMENDED (the "paste one line and I pin it" is now resolved). Final rule:
- `PageEntry.leaf_index` (`Field(ge=0)`, `== leafNum − 1`) is the **unique primary key**, present on every entry and **contiguous from 0** — this is what lets `citation_extract` slice the `_djvu.txt` form-feed chunks 1:1 by leaf.
- `page_label` uniqueness applies **only to non-empty labels**; empty `""` (unnumbered front-matter/plates) is allowed and may repeat freely.
- `image_path`, if present, must exist on disk.
- Downstream: `citation_extract.page_seen` uses the leaf's `page_label` if non-empty, else the synthetic string `"[leaf N]"` (N = leaf_index); the "phrase is a substring of the page OCR" guard keys on the leaf chunk, not the label.

New BUILD module — `page_map_adapter.py` (single file, one concern). Frozen contract:
```python
def adapt(hocr_pages: dict, pack_id: str, image_dir: str | None) -> PageMap: ...
```
Behavior: `hocr_pages` is the parsed archive-hocr-tools format-version "2" JSON (top-level `identifier`, `format-version`, `archive-hocr-tools-version`, `confidence`, `pages[]`; each page has `leafNum` (int, 1-based), `pageNumber` (string, may be ""), other fields ignored). Assert `hocr_pages["format-version"] == "2"` (raise `ValueError` with the found value otherwise). For each entry: `leaf_index = leafNum − 1`; `page_label = pageNumber` (verbatim, including ""); `image_path = f"{image_dir}/leaf_{leafNum:04d}.png"` if `image_dir` else `None`. Sort output pages by `leaf_index` ascending; assert contiguity from 0 (raise naming the missing index). Set `schema_version="1.0"`, `pack_id=pack_id`. Return a validated `PageMap`. Pure function; no IO, no network. Tests: (1) leafNum 1..5 / pageNumber `["","","","41","42"]` → leaf_index 0..4, two empty labels allowed, 41/42 unique, image_path `leaf_0004.png`/`leaf_0005.png`; (2) format-version "1" → raises; (3) gap in leafNum (1,2,4) → raises naming index 2; (4) duplicate non-empty pageNumber → raises; duplicate "" → passes.
━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — END ✚ ━━━━━━━━━━━━━━━

4.2 concept_graph.json (Layer 1 — feeds level_maker)

```python
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
```

```json
{"schema_version":"1.0","level_id":"principia_bk1_sec1",
 "title":"Book I, Section II — Centripetal Forces","edition":"… Motte 1846 …","seed":1729001,
 "nodes":[
   {"id":"law_2","name":"Law II","kind":"law","importance":5,"pages":["19"],"summary":"Change of motion ∝ impressed force.","tags":["axiom"]},
   {"id":"prop_1","name":"Prop. I, Theorem I","kind":"proposition","importance":5,"pages":["55","56"],"summary":"Radii sweep equal areas in equal times.","tags":["kepler-2"]}],
 "edges":[
   {"id":"edge.prop_1.to.law_2","source":"prop_1","target":"law_2","kind":"depends_on","weight":1.0,"label":"by the second Law"}]}
```

Validation: node ids unique & match NodeId; importance 1–5; edge.id == "edge."+source+".to."+target; endpoints exist; no self-loops; graph is a DAG (no cycles); every node has a room_<id>.json.

4.3 room_<node_id>.json (Layer 2 — feeds room_maker/baker)

```python
class FigureDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figure_id: FigureId
    asy_path: str
    recipe_path: str
    n_steps: int = Field(ge=1)
    caption: str
    groups_used: list[GroupName]

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
    text: TextBlock                 # from §3.A.6

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
```

```json
{"schema_version":"1.0","node_id":"prop_1","edition":"… Motte 1846 …",
 "figures":[{"figure_id":"prop_1.f1","asy_path":"figures/figure.prop_1.f1.asy",
             "recipe_path":"figures/recipe.prop_1.f1.json","n_steps":3,
             "caption":"Equal areas swept in equal times.","groups_used":["path","radius","construction"]}],
 "blocks":[
   {"pair_id":"prop_1.s1","step_index":1,
    "drawing":{"block_id":"prop_1.s1.fig","figure_id":"prop_1.f1","highlight_step":1},
    "text":{"block_id":"prop_1.s1.txt","latex":"The body moves uniformly along \\cg{path}{$AB$}, then \\cg{path}{$BC$} …","groups_used":["path"]}},
   {"pair_id":"prop_1.s3","step_index":3,
    "drawing":{"block_id":"prop_1.s3.fig","figure_id":"prop_1.f1","highlight_step":3},
    "text":{"block_id":"prop_1.s3.txt","latex":"Through $C$ draw \\cg{construction}{$Cc$} parallel to \\cg{radius}{$SB$} …","groups_used":["construction","radius"]}}],
 "final_pair_id":"prop_1.s3",
 "ceiling_equations":[{"eq_id":"prop_1.eq1","latex":"\\frac{dA}{dt}=\\tfrac12\\,r^2\\dot\\theta=\\text{const}"}]}
```

Validation: filename stem == node_id; all block_id/pair_id/eq_id prefixes == node_id; step_index contiguous 1..N, unique; each drawing.figure_id ∈ figures; highlight_step ∈ 1..figure.n_steps; figure.n_steps == recipe.n_steps; final_pair_id ∈ pairs; groups used ⊆ palette.

4.4 floorplan.json (feeds render_wire, guidelines)

```python
class FloorRoom(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_id: NodeId
    map_xz: Vec2
    importance: int = Field(ge=1, le=5)
    map_radius_m: float
    map_color: Hex            # resolved from palette.map_importance[importance]
    socket_y: float = 0.0

class Corridor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corridor_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    source: NodeId
    target: NodeId
    height_level: int
    cruise_y: float
    path_xz: list[Vec2]       # polyline incl. ramp knee points
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
```

Validation: room_ids == graph node ids (spine); corridor endpoints exist; crossing pairs have different *_y; over_y > under_y; height_level within cap (warn>7, fail>12).

4.5 room_runtime/room_<node_id>.json (feeds render_room, gameplay)

```python
class PanelPairRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId
    step_index: int
    drawing_off_asset: str    # asset_id in manifest
    drawing_on_asset: str
    text_off_asset: str
    text_on_asset: str
    wall_slot_drawing: str    # e.g. "N-0", "E-2"
    wall_slot_text: str

class EnemyRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enemy_id: str = Field(pattern=r"^[a-z][a-z0-9_]*\.demon$")
    spawn_xyz: Vec3
    health: int = 5

class CeilingEqRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eq_id: EqId
    asset_id: str             # the neutral baked PNG
    pos_xyz: Vec3
    size_m: Vec2

class RoomRuntime(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    room_id: NodeId
    dimensions_m: Vec3        # w, h, d — from content volume (TARDIS)
    panel_pairs: list[PanelPairRT]
    final_pair_id: PairId
    hidden_door_wall_slot: str
    enemy: EnemyRT
    ceiling_equations: list[CeilingEqRT]
```

Validation: asset_ids exist in manifest; final_pair_id ∈ pairs; hidden_door_wall_slot is the slot of the final pair's drawing OR text; enemy_id == room_id + ".demon"; no two pairs share a wall slot.

━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — BEGIN ✚ ━━━━━━━━━━━━━━━
**Added** 2026-06-25 by DeepSeek. **Decided by** Claude Opus 4.8 (Parent 1). **Status:** part SUPERSESSION pointer, part LOCKED schema (recorded only in chat; preserved here at its correct section). **What:** the room/door model in §4.5 above is superseded; the still-live panel schemas it keeps are pinned here.

⚠️ **SUPERSESSION:** the `RoomRuntime` door/entrance model in §4.5 above (and the Room-Maker that produced it) is **superseded** by the *Biblical Apocrypha* — `QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md` (Room System v3). For anything about rooms/doors, use the Apocrypha: it replaces the single-entrance model with a list of bearing-accurate `DoorRT` (door **count** = node degree; door **direction** = the corridor's true map bearing). The Apocrypha notes "panels & rest unchanged" — these are those unchanged panel schemas it relies on (they amend the v1 `PanelPairRT` shown above to carry explicit placement):
```python
class PanelPlacementRT(BaseModel):
    model_config = ConfigDict(extra="forbid")
    wall: Literal["N","E","S","W"]
    slot_index: int = Field(ge=0)
    wall_slot: str                 # the "<WALL>-<INDEX>" id (redundant, for debug/door ref)
    center_xyz: Vec3               # panel center in room-local space
    width_m: float
    height_m: float
    yaw_rad: float                 # facing rotation about Y (panel normal points inward)

class PanelPairRT(BaseModel):      # AMENDED: replaces wall_slot_drawing/wall_slot_text strings
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId
    step_index: int
    drawing_off_asset: str
    drawing_on_asset: str
    text_off_asset: str
    text_on_asset: str
    drawing_placement: PanelPlacementRT
    text_placement: PanelPlacementRT
```
Wall-slot grammar: `wall_slot = "<WALL>-<INDEX>"`, WALL ∈ {N,E,S,W}, INDEX 0-based along that wall in reading order; one panel per slot; a step-pair occupies two adjacent slots on the same wall (drawing then text), never split across a corner.
━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — END ✚ ━━━━━━━━━━━━━━━

4.6 manifest.json (baked assets — feeds assets.load_pack)

```python
class AssetEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asset_id: str
    kind: Literal["figure_off","figure_on","text_off","text_on","ceiling_neutral"]
    wall_path: str            # downscaled mip for the wall
    master_path: str          # high-res for Read Mode
    px_w: int; px_h: int
    content_bbox: tuple[int,int,int,int]
    dpi: int

class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    assets: dict[str, AssetEntry]   # keyed by asset_id
```

Asset-id grammar (fixed): figure_off→<figure_id>.off; figure_on→<figure_id>.on.<k>; text_off→<text_block_id>.off; text_on→<text_block_id>.on; ceiling_neutral→<eq_id>.neutral.

```json
{"schema_version":"1.0","level_id":"principia_bk1_sec1","assets":{
  "prop_1.f1.off":   {"asset_id":"prop_1.f1.off","kind":"figure_off","wall_path":"assets/prop_1.f1.off.png","master_path":"assets/prop_1.f1.off@master.png","px_w":1024,"px_h":760,"content_bbox":[12,8,1010,752],"dpi":220},
  "prop_1.f1.on.3":  {"asset_id":"prop_1.f1.on.3","kind":"figure_on","wall_path":"assets/prop_1.f1.on.3.png","master_path":"assets/prop_1.f1.on.3@master.png","px_w":1024,"px_h":760,"content_bbox":[12,8,1010,752],"dpi":220},
  "prop_1.s3.txt.off":{"asset_id":"prop_1.s3.txt.off","kind":"text_off","wall_path":"assets/prop_1.s3.txt.off.png","master_path":"assets/prop_1.s3.txt.off@master.png","px_w":1400,"px_h":420,"content_bbox":[4,4,1396,416],"dpi":220}
}}
```

Validation: every asset_id referenced by any room_runtime exists; figure_off shared across that figure's steps (deduped — one file); both wall_path and master_path exist on disk; content_bbox inside image.

4.7 savegame.json (written by state.save, atomic)

```python
class RoomProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pairs_on: list[PairId] = []
    hidden_door_open: bool = False
    enemy_defeated: bool = False
    room_cleared: bool = False

class LevelProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rooms: dict[NodeId, RoomProgress] = {}
    level_complete: bool = False

class PlayerSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level_id: LevelId
    mode: Literal["corridor","room"]
    current_room_id: NodeId | None
    position_xyz: Vec3
    heading_rad: float

class SaveGame(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    profile_id: str = "default"
    levels: dict[LevelId, LevelProgress] = {}
    player: PlayerSave
```

Validation: on load, unknown room/level ids vs. the pack are dropped with a logged warning (forward-compatible saves), but schema_version must match. Atomic write: temp file → flush/fsync → os.replace.

4.8 pack.json & build_config.json

```python
class Pack(BaseModel):                      # pack.json (authored)
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    pack_id: str
    title: str
    edition: str
    levels: list[LevelId]
    palette_path: str = "palette.json"

class BuildConfig(BaseModel):               # build_config.json (authored; bake & layout constants)
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    bake_dpi_wall: int = 220
    bake_dpi_master: int = 600
    bake_trim_alpha: int = 8
    bake_pad_px: int = 16
    layout_seed: int = 1729001
    layout_scale_m: float = 28.0
    height_delta_m: float = 4.5
    max_height_levels_warn: int = 7
    max_height_levels_fail: int = 12
    guide_w_imp: float = 0.6
    guide_w_dist: float = 0.4
    guide_max_lines: int = 3
```

━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — BEGIN ✚ ━━━━━━━━━━━━━━━
**Added** 2026-06-25 by DeepSeek. **Decided by** Claude Opus 4.8 (Parent 1) in the "remaining gaps" answer. **Status:** LOCKED — recorded only in chat; preserved here at its correct section. **What:** (A) additive `BuildConfig` fields the Room Maker + importance blend use; (B) the new **§4.9 `provenance.json` / `Provenance`** schema.

**(A) Additive `BuildConfig` fields** (amends §4.8; build_config.json):
```python
room_px_per_m: float = 360
panel_min_w_m: float = 0.6 ;  panel_max_w_m: float = 3.2
panel_min_h_m: float = 0.5 ;  panel_max_h_m: float = 2.4
panel_gap_m: float = 0.25         # between the two panels of a pair
pair_gap_m: float = 0.8           # between consecutive pairs
wall_margin_m: float = 0.6        # from corners
room_headroom_m: float = 1.2      # ceiling above tallest panel
room_min_w_m: float = 6.0 ; room_min_d_m: float = 6.0 ; room_min_h_m: float = 3.2
panel_center_y_pref_m: float = 1.55
importance_w_indeg: float = 0.6   # used by the importance blend (New Testament §1.4)
importance_w_hint:  float = 0.4
# NOTE: the door/room-v3 BuildConfig fields (door_width_m, door_height_m, door_min_separation_m,
# corner_clearance_m, room_target_aspect, room_pack_slack, room_grow_step_m, room_sizing_max_iters,
# aisle_depth_m, demon_offset_m) live in the Biblical Apocrypha §3.
```

**(B) §4.9 — `provenance.json` / `Provenance`** (BUILD-world only; emitted by `merge()`; never shipped):
```python
class EdgeProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    edge_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    provenance: Literal["cited", "inferred"]
    snippet: str                       # verbatim citation context; "" only when provenance=="inferred"
    page_seen: PageLabel | None        # the leaf's label (or "[leaf N]"); None for inferred-only
    agreement: Literal["both", "citation_only", "inference_only"]
    reason: str = ""                   # required (non-empty) when provenance=="inferred"
    vague: bool = False

class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    level_id: LevelId
    edges: list[EdgeProvenance]
    flags: list[str]                   # plain-English graph-level findings (cycles, missing items, orphans, islands)
```
Semantics: `cited` → edge from a resolved printed phrase (snippet verbatim, page_seen set). `inferred` → promoted from the INFERENCE pass with no matching citation (snippet="", reason non-empty). `agreement`: "both" (citation+inference agree — highest confidence) / "citation_only" / "inference_only" (the scrutiny pile — shown dashed in graph_preview.png). `flags` carries the math-free red-flags from `sanity.check`.
Validation (build fails on any): exactly one `EdgeProvenance` per `concept_graph` edge, matched by `edge_id` (no orphans, no missing); `cited` ⇒ `page_seen` not None and (snippet non-empty or `vague==True`); `inferred` ⇒ `snippet==""`, `page_seen is None`, `reason` non-empty; `agreement=="inference_only"` ⇒ `inferred`, `"citation_only"`/`"both"` ⇒ `cited`; `provenance.json` must NOT appear under `dist/` (a packaging check asserts this).
Example:
```json
{"schema_version":"1.0","level_id":"principia_bk1_sec1",
 "edges":[
   {"edge_id":"edge.prop_1.to.law_2","provenance":"cited","snippet":"…which is manifest by the second Law of Motion…","page_seen":"55","agreement":"both","reason":"","vague":false},
   {"edge_id":"edge.prop_1.to.lemma_1","provenance":"inferred","snippet":"","page_seen":null,"agreement":"inference_only","reason":"The polygon-to-curve limit relies on ultimate-equality of vanishing triangles.","vague":false}],
 "flags":["ISLANDS: 1 component (ok)"]}
```
━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — END ✚ ━━━━━━━━━━━━━━━

§5 — PART C: MODULE INTERFACES (contracts.py made real)

All data models are defined in §3–§4; contracts.py re-exports them plus the shared scalars (§3 top) and the runtime-only contracts below. Then every module's frozen public signature is listed. Children implement against these exactly; DeepSeek integrates.

5.1 Runtime-only contracts (not persisted)

```python
from dataclasses import dataclass
from typing import Protocol, Sequence
import numpy as np

# ---- co-op semantic actions (per frame; produced by input_actions.poll) ----
@dataclass(frozen=True)
class Actions:
    # MOVER (owns the body) -------------------------------------------------
    move_x: float           # [-1,1] strafe (right +)
    move_y: float           # [-1,1] forward (+) / back (-)
    heading_delta: float    # radians this frame (yaw). MOVER ONLY.
    pitch_delta: float      # radians this frame, pre-clamp. MOVER ONLY.
    # SHOOTER (owns the reticle) -------------------------------------------
    aim_x: float            # [-1,1] reticle x within cone
    aim_y: float            # [-1,1] reticle y within cone
    fire: bool              # edge: true only on the frame fire is pressed
    fire_held: bool
    # SHARED ---------------------------------------------------------------
    read_toggle: bool       # edge
    interact: bool          # edge
    pause: bool             # edge

# ---- events emitted by gameplay.step (in-memory, typed) ----
class _Ev(BaseModel):
    model_config = ConfigDict(extra="forbid")

class PanelLit(_Ev):          event: Literal["panel_lit"];      pair_id: PairId; block_id: str
class DoorOpened(_Ev):        event: Literal["door_opened"];    room_id: NodeId
class DemonSpawned(_Ev):      event: Literal["demon_spawned"];  enemy_id: str; room_id: NodeId
class DemonHit(_Ev):          event: Literal["demon_hit"];      enemy_id: str; hp: int
class DemonKilled(_Ev):       event: Literal["demon_killed"];   enemy_id: str; room_id: NodeId
class RoomCleared(_Ev):       event: Literal["room_cleared"];   room_id: NodeId
class LevelComplete(_Ev):     event: Literal["level_complete"]; level_id: LevelId
class ModeSwitch(_Ev):        event: Literal["mode_switch"];    to: Literal["corridor","room"]; room_id: NodeId | None
class ReadModeToggled(_Ev):   event: Literal["read_toggled"];   on: bool; asset_id: str | None
class GuidelinesRecomputed(_Ev): event: Literal["guides"];      targets: list[NodeId]

Event = Annotated[Union[PanelLit,DoorOpened,DemonSpawned,DemonHit,DemonKilled,
                        RoomCleared,LevelComplete,ModeSwitch,ReadModeToggled,
                        GuidelinesRecomputed], Field(discriminator="event")]

# ---- geometry/runtime helpers ----
@dataclass(frozen=True)
class Ray:    origin: Vec3; direction: Vec3
@dataclass(frozen=True)
class PanelHit: asset_on_id: str; asset_off_id: str; pair_id: PairId; is_drawing: bool; distance: float
ViewMatrix = "np.ndarray"   # shape (4,4), float32, row-major

class NavQuery(Protocol):
    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3: ...
    def nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None: ...

@dataclass
class GameState:
    save: SaveGame
    mode: Literal["corridor","room"]
    current_room_id: NodeId | None
    pos: Vec3
    heading_rad: float
    pitch_rad: float
    lit: set[str]            # block_ids turned on (mirrors save)
    cleared: set[NodeId]

@dataclass
class Pack:
    floorplan: Floorplan
    rooms: dict[NodeId, RoomRuntime]
    manifest: Manifest
    palette: Palette
    asset_dir: str

# ---- build result/report types ----
@dataclass(frozen=True)
class AsyResult: ok: bool; outputs: list[str]; stdout: str; stderr: str
@dataclass(frozen=True)
class Report:    ok: bool; errors: list[str]; warnings: list[str]
@dataclass(frozen=True)
class Flags:     missing: list[str]; cycles: list[str]; orphans: list[str]; components: int
@dataclass(frozen=True)
class BuildResult: ok: bool; manifest_path: str; report: Report
@dataclass(frozen=True)
class LabelIndex:  # for citation_normalize
    by_id: dict[str, str]        # node_id -> local_label
    aliases: dict[str, str]      # normalized phrase token -> node_id
```

5.2 Module signatures — CONTENT/BUILD world

```python
# citation_extract.py   (deterministic, text-primary)
def extract(djvu_text: str, page_map: PageMap, label_index: LabelIndex) -> CitationsRaw: ...

# citation_normalize.py
def build_label_index(nodes: NodesRaw) -> LabelIndex: ...
def normalize(phrase: str, idx: LabelIndex) -> NodeId | None: ...

# merge.py
def merge(nodes: NodesRaw, cites: CitationsRaw, infer: InferenceRaw,
          idx: LabelIndex) -> tuple[ConceptGraph, "Provenance"]: ...

# sanity.py
def check(graph: ConceptGraph, nodes: NodesRaw) -> Flags: ...
def render_preview(graph: ConceptGraph, out_png: str) -> None: ...

# layout_force.py
def place_nodes(graph: ConceptGraph, seed: int, scale_m: float) -> dict[NodeId, Vec2]: ...

# layout_height.py
def detect_crossings(pos: dict[NodeId, Vec2], graph: ConceptGraph) -> list[tuple[str,str,Vec2]]: ...
def assign_heights(graph: ConceptGraph, crossings: list[tuple[str,str,Vec2]],
                   cfg: BuildConfig) -> dict[str, int]: ...

# level_maker.py
def build_floorplan(graph: ConceptGraph, palette: Palette, cfg: BuildConfig) -> Floorplan: ...

# room_maker.py
def build_room_runtime(room: RoomSource, manifest: Manifest, cfg: BuildConfig) -> RoomRuntime: ...

# palette_gen.py
def gen(palette: Palette, out_asy: str, out_tex: str) -> None: ...

# prooffig_check.py
def lint(figure_asy_path: str, recipe: Recipe, palette: Palette) -> list[str]: ...

# asy_compile.py
def compile(src: str, out_stem: str, params: dict[str, str]) -> AsyResult: ...

# baker_figure.py
def bake(figure_asy: str, n_steps: int, palette: Palette,
         out_dir: str, cfg: BuildConfig) -> list[AssetEntry]: ...

# baker_text.py
def bake_text(block: TextBlock, palette: Palette, out_dir: str, cfg: BuildConfig) -> list[AssetEntry]: ...
def bake_ceiling(eq: CeilingEq, out_dir: str, cfg: BuildConfig) -> AssetEntry: ...

# validate.py
def validate_recipe(recipe: Recipe, palette: Palette) -> Report: ...
def validate_room(room: RoomSource, palette: Palette) -> Report: ...
def validate_id_spine(graph: ConceptGraph, rooms: list[RoomSource],
                      floorplan: Floorplan, manifest: Manifest) -> Report: ...

# buildpack.py  (the single CLI entry: runs validate→layout→bake→manifest)
def build_pack(content_dir: str, out_dir: str) -> BuildResult: ...
```

5.3 Module signatures — RUNTIME world

```python
# assets.py
def load_pack(dir: str) -> Pack: ...                      # asserts schema_version on every file

# state.py
def new_state(pack: Pack, profile_id: str = "default") -> GameState: ...
def load(path: str, pack: Pack) -> GameState: ...
def save(state: GameState, path: str) -> None: ...        # atomic

# input_actions.py
def poll(window, bindings) -> Actions: ...                # device-agnostic; two-player split

# camera.py
class Camera:
    def update(self, heading_rad: float, pitch_rad: float, pos: Vec3, dt: float) -> ViewMatrix: ...

# nav_collision.py
def build_corridor_nav(fp: Floorplan) -> NavQuery: ...
def build_room_nav(room: RoomRuntime) -> NavQuery: ...

# gameplay.py
def step(state: GameState, actions: Actions, pack: Pack, nav: NavQuery, dt: float) -> list[Event]: ...

# guidelines.py
def select_targets(fp: Floorplan, current: NodeId, cleared: set[NodeId], cfg: BuildConfig) -> list[NodeId]: ...
def draw_guidelines(view: ViewMatrix, fp: Floorplan, targets: list[NodeId]) -> None: ...

# gfx_context.py
def make_window(width: int, height: int, title: str): ...   # returns (window, gl_context)

# shaders.py
def wire_program(ctx): ...
def solid_program(ctx): ...
def blit_program(ctx): ...
def ceiling_tint_uniform(prog, red: float) -> None: ...

# render_wire.py
def draw_graph(view: ViewMatrix, fp: Floorplan, state: GameState) -> None: ...

# render_room.py
def draw_room(view: ViewMatrix, room: RoomRuntime, pack: Pack, state: GameState) -> None: ...

# readmode.py
def draw_read(asset_master_path: str, zoom: float, pan: Vec2) -> None: ...

# app.py
def main() -> int: ...

# tools/overlay_diff.py  (build-time utility)
def run(back_png: str, front_png: str) -> None: ...
```

━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — BEGIN ✚ ━━━━━━━━━━━━━━━
**Added** 2026-06-25 by DeepSeek. **Decided by** Claude Opus 4.8 (Parent 1) in the "remaining gaps" answer. **Status:** LOCKED — recorded only in chat; preserved here at its correct section. **What:** the Read-Mode target-selection rule (which panel `readmode` opens) + its constants.

`readmode` (above) opens the panel the reticle's ray hits (raycast, hit distance ≤ `READ_MAX_DIST`). If the ray hits nothing, it opens the panel whose center lies within `READ_CONE_HALF_ANGLE` of view-forward and is nearest by distance (≤ `READ_MAX_DIST`); if none qualify, Read is a no-op. Runtime config: **`READ_MAX_DIST = 6.0` m, `READ_CONE_HALF_ANGLE = 35°`**. (The raycast/cone helper is a child detail in `gameplay.py` / `nav_collision.py`.)
━━━━━━━━━━━━━━━ ✚ DEEPSEEK INLINE COMMENTARY — END ✚ ━━━━━━━━━━━━━━━

5.4 Per-frame wiring (authoritative order — restated so children align)

```
poll → Actions
gameplay.step(state, actions, pack, nav, dt) → [Event]
apply Events to state (+ debounced state.save)
camera.update(state.heading, clamp(state.pitch), state.pos, dt) → view
if state.mode == "corridor":
    if junction-or-clear event: targets = guidelines.select_targets(...)
    render_wire.draw_graph(view, fp, state); guidelines.draw_guidelines(view, fp, targets)
else:
    render_room.draw_room(view, room, pack, state)   # ceiling tint = red iff cleared
if read active: readmode.draw_read(master, zoom, pan)
bloom (corridor only); present
```

Closing notes

    What's fully pinned (no drift possible): every JSON schema, every id grammar, the recipe op-vocabulary, the \cg text-color mechanism, prooffig.asy, the figure template, the manifest asset-id grammar, all module signatures, the action/event contracts.
    The only ⟨confirm-from-docs⟩ items are Asymptote's real function names inside the generated .asy and the rgb("…") hex form — confirmed by the compile loop, never by guesswork, exactly as designed. Our convention around them is fully fixed.
    Refinements over earlier sketches (intentional): group names are palette keys (the old per-figure color_map is gone); figures are declared once per room with N highlight steps (drawing blocks reference figure_id + highlight_step); manifest is keyed by a fixed asset-id grammar.

One genuine open choice I'm flagging honestly, not deferring: figure background transparency. Preferred: Asymptote emits RGBA with a transparent background directly. If that proves unreliable in practice, the baker renders on palette.bg_key (#FF00FF) and keys it out with edge-despill. I've specified bg_key in the palette so both paths are ready; the baker child picks the one that actually produces clean edges and the overlay-diff tool will make any fringing visible to you immediately. This is a 30-minute empirical decision at bake time, not a design hole.

If your Archive.org page-label file shape would help me pin the page_map adapter precisely, paste one representative line and I'll write that one contract too. Otherwise this standard is complete and ready to hand, module by module, to memoryless children.

--- END VERBATIM ---
