# PARENT 14 HANDOFF — DESIGN THE ROOM-CONTENT FORMAT + BUILDER TOOL

> **Your mission, single sentence:** Design a text format for room content (like Descent's corridor format) and build a Python tool (`build/room_from_spec.py`) that converts that format into `recipe.json` + `figure.asy` + `room_source.json` — one reusable tool, run 20+ times by DeepSeek, fed by 20+ children who each produce one room spec.

---

## ⚠️ CORRECTION FROM NIR — READ THIS FIRST (it overrides everything) ⚠️

**This block comes directly from Nir, the author and owner of this project. It OVERRIDES any description of color or highlighting anywhere else in this prompt (especially §0.5, §2, §3, §5, §6) AND anywhere in the Bible (Old Testament, New Testament, Second Canon, Apocrypha, Commentaries). Wherever they conflict, THIS wins. Your format and tool must embody THIS, not the old model.**

### Why this overrides the Bible (please internalize it; do not argue it back)

- The "frozen" / "Bible" system exists for ONE reason: to stop the AI assembly-line (many fresh chats) from drifting and silently contradicting each other. It was **never** meant to bind Nir. Nir is the author. To him nothing is set in stone — the project is still "water and void," and he shapes the world as he sees fit. When Nir's stated intent and a frozen text conflict, **Nir wins, every time.**
- This is **not Nir changing his mind.** Nir described this exact color behavior from the very beginning; earlier AIs misunderstood it and froze the misread — the same failure that froze the rejected Wolfenstein box-room. So the Bible's color model is a **recorded mistake**, not Nir's intent. We are correcting a misunderstanding, not amending a decision.
- **Why we are NOT editing the Bible to fix it:** purely mechanical safety — editing those large verbatim scripture files has repeatedly caused collateral damage (adjacent paragraphs altered or deleted). So we leave the scriptures untouched as a historical record and carry the LIVE truth here in the handoff. The handoff is the authority; the old scripture is the fossil.
- Your job is to **serve Nir's goal.** Be the angel that builds what the author wants — not the one who quotes scripture back at him.

### The color system Nir actually wants (your format + tool MUST capture exactly this)

A **"station"** = one step-pair = a geometry **drawing panel** + its paired **text-explanation panel**. EVERY station obeys the SAME two rules:

**Rule 1 — Matching colors (the words ↔ the picture). LOCAL to each station.**
- Whatever the explanation text calls out as important is given a color in the drawing, and the SAME words in the text get that SAME color. Text says "angle ABC" in blue → angle ABC is drawn blue.
- Within ONE station, each important element gets its OWN DISTINCT color (angle ABC = blue, so triangle DEF = red, line XY = green, …). No two important elements in the same station share a color.
- Colors are chosen FRESH per station — they are LOCAL, never global. The same angle ABC may be blue in one station, red in another, and have NO color in a third (if it isn't important there). All fine.
- Anything NOT important in a station is NOT colored. It is drawn in plain **BLACK** (on a light background) or plain **WHITE** (on a dark background). **NEVER grey. There are no shades of grey.**

**Rule 2 — The Stabilo bright highlighter. CURRENT STEP ONLY.**
- On TOP of the matched colors, ONLY the current step gets a bright highlighter swipe over its "heart" — the single most important piece of that step.
- If the current step has several hearts, each heart gets its OWN bright marker color: bright yellow, bright green, bright orange, bright pink, bright cyan.
- These bright marker colors are also LOCAL — picked fresh, not fixed. The same piece highlighted elsewhere can get a different bright color next time.
- This is NOT cumulative. We do NOT light steps 1..k. We light ONLY the current step's heart(s).

### What this explicitly KILLS from the old (mistaken) model

1. ❌ **No single global fixed palette** ("path is always orange everywhere"). Colors are local, per station, distinct-within-station, and only on important elements.
2. ❌ **No cumulative reveal** (steps 1..k). The Stabilo lights ONLY the current step's heart(s).
3. ❌ **No grey.** Uncolored = pure black (light background) or pure white (dark background).

### What this means for YOUR format + tool

- The child's spec must let them, **per station**, mark which elements are important and assign each a **distinct local color**, and write the matching text so the same words carry the same color. (No global 5-group enum; the child picks colors locally. A small set of named, easily-distinguished colors is fine, but the assignment is per station, not a fixed global meaning.)
- The child's spec must let them mark, **per step**, the **heart(s)** of that step and a **bright marker color** for each — used by the Stabilo, current-step-only.
- The tool must emit drawings where uncolored ink is black (light bg) / white (dark bg), important elements carry their local color, and only the current step's heart(s) carry the bright Stabilo.
- The schemas quoted later (the 5 fixed groups, the global `palette.json`, "grey", `highlight >= step`) reflect the OLD mistake. Reconciling them to THIS model is part of your first task; DeepSeek will then update `raw_models.py` and the bake tools. Surface your proposed data shape to Nir.

---

## §0 — THE PATTERN (why you're doing this)

We have 20 Principia rooms (11 with figures, 9 text-only). Parent 13 is building ONE room as a pipeline proof-of-concept. After that succeeds, we need to build the other 19 — and then more levels after that.

The **Descent QED pattern** that WORKS (from our first shipped game):

1. **A text format** (keyword blocks) — simple enough for a child AI to fill in
2. **A Python tool** (written once) — parses the format → generates all game asset files
3. **Children** (one per room) — each gets the format + their room's source text, produces one spec
4. **DeepSeek** — runs the same tool 20 times on 20 children's specs

No parent designs 42 files. No context death. One format, one tool, many children.

**Your job:** design the format and build the tool. Then children will use them for all rooms beyond the first.

---

## §0.5 — THE COLOR SYSTEM (the heart of Quake — your format + tool MUST embody this)

> 🛑 **SUPERSEDED — DISREGARD THE REST OF THIS SECTION.** Everything below in §0.5 (the "Layer 1/2/3/4" model, cumulative `on_k`, the 5 fixed groups, the global palette, `\cg{group}{}`, "grey") describes the OLD misunderstanding. The **authoritative, correct color system is the "⚠️ CORRECTION FROM NIR" block at the top of this prompt** — read it and design your format + tool to it. In one breath: **(1) Matching colors** are local per station, distinct within a station, only on important elements; uncolored ink is **black/white, never grey**; the same words in the text share the color of their shape in the picture. **(2) Stabilo** is a bright marker (yellow/green/orange/pink/cyan) on ONLY the current step's heart(s), never cumulative, also local. The stale text that follows is kept only so you can see what was wrong.

This is NOT optional. Every child spec, every tool output, every generated file for ALL future rooms must carry the (corrected) color system. Design your format and tool AROUND it.

### Layer 1: Stabilo — cumulative step highlighting on figures

The figure is always shown in FULL. "Off" = everything grey. "On_k" = steps 1..k in their group colors, steps k+1..n_steps remain grey. This is cumulative reveal.

```
OFF:   everything grey (unread room)
ON_1:  step 1 elements in color, rest grey
ON_2:  steps 1+2 elements in color, rest grey
ON_3:  all elements in color (fully read)
```

The child's spec must assign each geometric element to a step (1..n_steps). The tool generates Asymptote with `highlight` conditionals: `if(highlight >= step) { draw(color) } else { draw(grey) }`.

### Layer 2: Color-matched figure↔text (permanent, per-panel)

Every geometric concept has a **group name** (one of the 5 palette keys: `path`, `radius`, `construction`, `tangent`, `swept_area`). That group has an **ink color** (hex from palette.json). 

In the FIGURE: each element tagged with its group → drawn in that group's ink color.
In the TEXT: `\cg{group}{phrase}` renders that phrase in the SAME ink color.

Example: `\cg{path}{the curve AB} meets \cg{radius}{the focal radius SP} at \cg{construction}{point Q}` — three colors in one sentence, each matching the same-colored element in the figure.

**The child's spec MUST:**
- Tag every geometric element with its group name
- Use `\cg{group}{text}` spans in ALL LaTeX text blocks for ANY reference to a figure element
- List `groups_used` per text block (validation hook)

**The tool MUST:**
- Generate RecipeOps with `Draw.group` set per element
- Generate Asymptote with each element drawn in its group's color variable
- Generate TextBlocks with `\cg` spans preserved and `groups_used` populated
- Validate: every `\cg` group exists in palette; every `groups_used` entry exists in palette

### Layer 3: Multiple colors per panel (per-panel independent)

A single text panel can use ANY subset of the 5 groups. One panel might use `path`+`radius`+`construction`. Another might use only `swept_area`. The child chooses per panel. The format must support this.

### Layer 4: OFF vs ON bake (how \cg becomes grey or colored)

The baker compiles the same LaTeX TWICE:
- OFF: `\newcommand{\cg}[2]{\textcolor{greytext}{#2}}` — everything grey
- ON:  `\newcommand{\cg}[2]{\textcolor{#1ink}{#2}}` — group-colored

The tool doesn't bake — it just generates the LaTeX source with `\cg` spans. The existing `baker_text` handles the double-compile. But the tool must ensure `groups_used` is populated so the baker's validator can cross-check.

### The difference (mandatory in your format design)

| Mechanism | What it does | When it changes | Who sets it |
|-----------|-------------|-----------------|-------------|
| **Stabilo** (step) | Which figure elements are grey vs colored | Cumulative per proof STEP | Child: `step` field per element |
| **Color-matching** (\cg) | Which text words match which figure elements | FIXED per panel | Child: `\cg{group}{...}` in LaTeX text |

**Both use the same 5 palette groups. The format must capture BOTH. The tool must emit BOTH. Every child must produce BOTH.**

---

## §1 — WHAT THE TOOL MUST PRODUCE

For each room, the tool takes ONE input (a child-produced spec text file) and outputs up to 3 files:

### For a figure room:
1. `recipe.<figure_id>.json` — construction operations + step glosses
2. `figure.<figure_id>.asy` — Asymptote source with `highlight=k` support
3. `room_source.<node_id>.json` — RoomSource with StepPairs, DrawingBlocks, TextBlocks, CeilingEqs

### For a text-only room:
1. `room_source.<node_id>.json` — RoomSource with TextBlocks only, no figures

The tool does NOT run Asymptote or bake PNGs — that's a separate pipeline step. The tool just generates the source files.

---

## §2 — THE FROZEN OUTPUT FORMATS (your tool writes THESE)

> 🛑 **CORRECTION (read before trusting the schemas below).** These formats currently encode the OLD color mistake — a fixed `GroupName` enum of 5 globally-fixed groups, one shared `palette.json`, "grey" for the off-state, `groups_used`, and a per-step "group" tag built for cumulative reveal. Under Nir's corrected model (top of this prompt) colors are **local per station, distinct within a station, only on important elements**, uncolored ink is **black/white (never grey)**, and the Stabilo lights **only the current step's heart(s)** in bright marker colors. So `GroupName`, the global `palette.json`, `Draw.group`, and `groups_used` will need to CHANGE. Treat the schemas below as the *current* shape, not as law — proposing the corrected shape that expresses Nir's model is part of your first task, and DeepSeek will update `raw_models.py` + the bake tools to match. Surface your proposed shape to Nir.

### Recipe (Section 3.A.4)

```python
class StepGloss(BaseModel):
    model_config = ConfigDict(extra="forbid")
    index: int = Field(ge=1)
    gloss: str

class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    figure_id: FigureId               # pattern r"^[a-z][a-z0-9_]*\.f[0-9]+$"
    node_id: NodeId                   # pattern r"^[a-z][a-z0-9_]*$"
    edition: str
    caption: str
    n_steps: int = Field(ge=1)
    steps: list[StepGloss]
    ops: list[RecipeOp]
```

### RecipeOp — the full construction vocabulary

Every op has `name: OpName` (unique id, pattern `r"^[A-Za-z][A-Za-z0-9_']*$"`) and optional `draw: Draw | None`. The `op` literal discriminates type:

**Points:** `FreePoint` (free_point, optional rough_xy: Vec2), `PointOn` (point_on, path: Ref, optional t: float, near: Vec2), `Intersect` (intersect, a: Ref, b: Ref, optional near: Vec2), `Midpoint` (midpoint, a: Ref, b: Ref), `Foot` (foot, point: Ref, line: Ref), `ReflectPoint` (reflect_point, point: Ref, over: Ref)

**Lines:** `LineOp` (line, a: Ref, b: Ref), `Segment` (segment, a: Ref, b: Ref), `RayOp` (ray, a: Ref, b: Ref), `Parallel` (parallel, through: Ref, to: Ref), `Perpendicular` (perpendicular, through: Ref, to: Ref), `TangentAt` (tangent_at, curve: Ref, at: Ref), `TangentFrom` (tangent_from, curve: Ref, frm: Ref, optional near: Vec2), `Bisector` (bisector, a: Ref, vertex: Ref, b: Ref)

**Circles:** `CircleCP` (circle_cp, center: Ref, through: Ref), `CircleCR` (circle_cr, center: Ref, optional radius_points: tuple[Ref,Ref], radius_value: float), `Circle3` (circle_3, a: Ref, b: Ref, c: Ref), `Arc` (arc, center: Ref, frm: Ref, to: Ref, optional direction: "ccw"|"cw" default "ccw")

**Conics:** `EllipseFoci` (ellipse_foci, f1: Ref, f2: Ref, through: Ref), `EllipseAxes` (ellipse_axes, center: Ref, major_end: Ref, minor_end: Ref), `ParabolaFD` (parabola_fd, focus: Ref, directrix: Ref), `HyperbolaFoci` (hyperbola_foci, f1: Ref, f2: Ref, through: Ref), `Conic5` (conic_5, p1..p5: Ref)

**Compounds:** `Polygon` (polygon, points: list[Ref] min 3), `Polyline` (polyline, points: list[Ref] min 2), `Series` (series, along: Ref, optional to_curve: Ref, count: int 1..64, kind: "inscribed_rects"|"circumscribed_rects"|"ordinates"|"chords"|"tangent_polygon")

**Marks:** `AngleMark` (angle_mark, a: Ref, vertex: Ref, b: Ref, optional right: bool), `FloatLabel` (label, at: Ref — draw MUST be set)

### Draw

```python
class Draw(BaseModel):
    model_config = ConfigDict(extra="forbid")
    group: GroupName          # "path"|"radius"|"construction"|"tangent"|"swept_area"
    step: int = Field(ge=1)
    label: Optional[Label] = None
    marker: Literal["none","dot"] = "none"

class Label(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tex: str                  # "$A$"
    placement: Literal["N","S","E","W","NE","NW","SE","SW","center"] = "NE"
    offset: Optional[Vec2] = None
```

### TextBlock

```python
class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: TextBlockId       # pattern r"^[a-z][a-z0-9_]*\.s[0-9]+\.txt$"
    latex: str
    groups_used: list[GroupName]
```

### RoomSource

```python
class DrawingBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: DrawBlockId       # pattern r"^[a-z][a-z0-9_]*\.s[0-9]+\.fig$"
    figure_id: FigureId
    highlight_step: int = Field(ge=1)

class StepPair(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId             # pattern r"^[a-z][a-z0-9_]*\.s[0-9]+$"
    step_index: int = Field(ge=1)
    drawing: DrawingBlock
    text: TextBlock

class CeilingEq(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eq_id: EqId                 # pattern r"^[a-z][a-z0-9_]*\.eq[0-9]+$"
    latex: str

class FigureDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figure_id: FigureId
    asy_path: str
    recipe_path: str
    n_steps: int = Field(ge=1)
    caption: str
    groups_used: list[GroupName]

class RoomSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    node_id: NodeId
    edition: str
    figures: list[FigureDecl]    # empty for text-only rooms
    blocks: list[StepPair]
    final_pair_id: PairId
    ceiling_equations: list[CeilingEq]
```

**For text-only rooms:** StepPairs have NO DrawingBlock (or drawing=None). `figures` is empty list.

---

## §3 — THE 20 ROOMS (what children will fill in)

### 11 figure rooms (Parent 7's plan, step counts LOCKED)

lemma_2.f1 (n=3, groups: path/construction/swept_area/radius), lemma_4.f1 (n=3, path/swept_area/radius/construction), lemma_5.f1 (n=2, path/construction), lemma_6.f1 (n=3, path/construction/tangent), lemma_7.f1 (n=3, path/construction/tangent/radius), lemma_11.f1 (n=3, path/tangent/construction/radius), prop_1.f1 (n=4, path/radius/swept_area/construction), prop_6.f1 (n=4, path/radius/tangent/construction/swept_area), prop_7.f1 (n=3, path/radius/tangent/construction), prop_11.f1 (n=5, path/radius/tangent/construction/swept_area), prop_13.f1 (n=4, path/radius/tangent/construction/swept_area)

### 9 text-only rooms

lemma_3, lemma_9, lemma_10, law_1, law_2, prop_2, prop_4, lemma_12, prop_15

### Palette (locked)

```json
{"path":{"hi":"#FFE08A","ink":"#E8A200"},"radius":{"hi":"#A8D8FF","ink":"#1E6FE0"},"construction":{"hi":"#FFB3C7","ink":"#D81B60"},"tangent":{"hi":"#B9F6CA","ink":"#00A35A"},"swept_area":{"hi":"#E1BEE7","ink":"#8E24AA"}}
```

### Concept graph

20 nodes, 28 edges. Full graph lives at `levels/principia_bk1_inverse_square/concept_graph.json`. Every room's node degree = its door count (1–6).

---

## §4 — THE CHILD INTERACTION PROTOCOL (design your format AROUND this)

Children have NO internet, NO file access. They only know what Nir copy-pastes. Protocol:

1. Child gets: format spec + their room's figure plan
2. Child asks Nir for Principia text: "Please paste Lemma II from Section I"
3. Nir asks DeepSeek → DeepSeek reads from `quake/principia/book_1/section_01.txt` → Nir pastes
4. Child may ask follow-ups based on what they read
5. Child fills in the format and outputs the completed spec

**Your format must make this natural.** The format's fields should be things like "describe this step" and "list geometric elements" — which the child CAN'T fill in without source text, forcing them to ask for it.

---

## §5 — FORMAT DESIGN CONSTRAINTS

1. **Text-based, keyword blocks.** Children write text better than JSON. See Descent's `CORRIDOR:`, `ROBOT:`, `SEGMENTS:` pattern.
2. **Machine-parseable.** Your Python tool reads it deterministically.
3. **Complete.** Contains ALL info for the 3 output files. Child never needs to know Asymptote or pydantic.
4. **Figure + text-only support.** Different keyword blocks for each.
5. **LaTeX-safe.** Panels contain `$...$` math. Format must not corrupt it.
6. **Step-structured.** Content organized by step (1..n_steps).
7. **Local-color-aware (matching colors, per station).** Per station, the child marks which elements are *important* and gives each its own **distinct local color**; the matching words in the paired text carry that SAME color. Unimportant elements get NO color (drawn black on light bg / white on dark bg). The format must ENFORCE that every important element has a local color and that the colored words in the text match their shapes — a child cannot submit a spec without these color annotations. This is NOT optional. (No global 5-group enum; colors are chosen locally per station and may differ between stations.)
8. **Stabilo-aware (current step ONLY).** Per step, the child marks the **heart(s)** of that step and a **bright marker color** for each (bright yellow/green/orange/pink/cyan). The Stabilo lights ONLY the current step's heart(s) — never cumulatively. A step with no heart marked is REJECTED.
9. **Geometry-expressible.** Child specifies geometric elements with construction relationships; tool maps to RecipeOps + Asymptote. Tool generates proper `Draw` objects with both `group` AND `step` populated from the spec.

---

## §6 — THE TOOL SPEC

> 🛑 **CORRECTION (overrides the generation/validation rules in this section).** The specifics below (`highlight >= step` cumulative conditionals, per-group color variables, "`\cg` group exists in palette", `groups_used`) reflect the OLD color mistake. Keep the tool's *shape* (parse → validate → emit the 3 source files), but change WHAT it validates and emits to Nir's model: local per-station colors where the text's colored words match their shapes, uncolored ink **black/white (never grey)**, and a Stabilo that lights **only the current step's heart(s)** in bright marker colors. The validation rules must enforce *that* model (every important element has a local color; matching text words carry it; each step has at least one heart + bright color), not the old global-palette/cumulative one.

Single Python file: `build/room_from_spec.py`

```python
def build_room(spec_path: str, out_dir: str) -> dict:
    """Parse spec, write recipe.json + figure.asy + room_source.json to out_dir.
    Returns dict of written paths."""
```

Dependencies: stdlib + pydantic v2 (for validating output against raw_models schemas). No GL, no moderngl, no pyglet.

What it does:
1. Parse spec → structured data
2. Validate: correct IDs, step counts match, every element has BOTH `group` AND `step`, every `\cg` group exists in palette, every `groups_used` entry exists in palette, no duplicate element names, all `\cg{group}{...}` groups are listed in `groups_used`
3. Figure rooms: generate Recipe (map elements → RecipeOps with `Draw.group` and `Draw.step` populated), generate .asy (map elements → Asymptote with `highlight >= step` conditionals AND per-group color variables), generate RoomSource (TextBlocks with `\cg` spans intact + `groups_used` populated)
4. Text-only rooms: generate RoomSource (TextBlocks with `\cg` spans + `groups_used`; NO DrawingBlocks)
5. All output valid against `schema_version: "1.0"`, pydantic `extra="forbid"`
6. **MANDATORY validation failures** (reject spec, do not generate): missing group on any drawn element, missing step on any drawn element, `\cg` group not in palette, `\cg` group not in `groups_used`, `groups_used` entry not in palette

---

## §8 — DELIVERABLES

1. **Format specification doc** — markdown with every keyword block defined, grammar rules, complete example for figure room + text-only room. Both examples MUST show: color groups per element, step assignments per element, `\cg` spans in all LaTeX text, `groups_used` lists. The spec MUST make colors + Stabilo MANDATORY, not optional.
2. **`build/room_from_spec.py`** — the tool (with all validation rules from §7)
3. **Child prompt template** — reusable text DeepSeek pastes to each child. MUST include: the full format spec, the palette (5 group names + their meanings), the color-system rules (child MUST assign group+step to every element, child MUST use \cg for all figure-element references in text, child MUST populate groups_used), and a placeholder for the room-specific Principia text.

---

## §8 — PRINCIPIA TEXT LOCATIONS

```
quake/principia/axioms/axioms_and_laws.txt     — Laws I-III
quake/principia/book_1/section_01.txt           — Section I (Lemmas I-XI)
quake/principia/book_1/section_02.txt           — Section II (Props I-X)
quake/principia/book_1/section_03.txt           — Section III (Props XI-XVII)
```

DeepSeek also has DIGESTED PRINCIPIA (343-line summary).

---

## §9 — CONTEXT SURVIVAL RULES

1. **Minimal batches.** Target 2-3 total messages. Don't go back-and-forth.
2. **One batch of questions.** Ask everything in your first response.
3. **Don't ask for entire files.** Formats are in §2. Figure plan in §3. Palette in §3.
4. **One mission. One deliverable.** Format + tool only.
5. **Tables die on copy-paste.** Use fenced code blocks.

---

## §10 — START

State your format design approach, your tool architecture, and all your questions. Then build. 🚀
