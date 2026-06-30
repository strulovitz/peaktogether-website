# PARENT 14 HANDOFF — ROOM-CONTENT FORMAT + BUILDER TOOL

> **Your mission, in one sentence:** Design a keyword-block text format for room content (like Descent's `CORRIDOR:` / `ROBOT:` / `SEGMENTS:` pattern) and build a Python tool (`build/room_from_spec.py`) that parses that format and outputs `recipe.<figure_id>.json` + `figure.<figure_id>.asy` + `room_source.<node_id>.json`. One reusable tool, run 20+ times by DeepSeek, fed by 20 parallel children who each write one room spec using your format.

---

## §0 — THE DESCENT PATTERN (what works)

Our first game, **Descent QED**, shipped successfully with this pipeline:

1. **A keyword-block text format** — children write text, not JSON. `CORRIDOR: 1`, `TITLE { ... }`, `ROBOT: 1`, `SEGMENTS { ... }`. Children have NO internet, NO file access — they only know what Nir pastes in.
2. **A Python tool** — `content_parser.py` parses the format and generates game data. Written ONCE.
3. **Children** — one per room/corridor. Each gets: the format spec + their room's source text. Each produces: one filled-in spec file.
4. **DeepSeek** — runs the same tool 20 times on 20 children's output files.

**Your job:** replicate this pattern for Quake rooms. Design the format. Build the tool. The format must be simple enough for a child AI to fill in, and complete enough for the tool to generate all 3 output files without the child ever touching JSON or Asymptote.

---

## §1 — THE COLOR SYSTEM (the heart of Quake — your format must capture this)

This section is the SINGLE source of truth. There are no contradictions, no old models, no "CORRECTION" blocks. This is Nir's color system as it actually works in the current codebase.

### A "station" = one step-pair

Each step of the proof is a **station**: a geometry **drawing panel** + its paired **text panel** on the wall.

### Rule 1 — Matching colors (word ⟷ shape), LOCAL per station

- Within ONE station, each important geometric element gets its own **distinct local color** (e.g. "curveblue", "basegreen", "sideorange"). No two important elements in the same station share a color.
- The matching words in the text panel use that SAME color. Example: `\textcolor{sideorange}{Aa}` in the LaTeX text matches the orange `Aa` line in the figure.
- Colors are chosen FRESH per station — they are LOCAL, never global. The same concept may be blue in one station, red in another, and uncolored in a third.
- Unimportant elements are drawn in **plain black** (light background) or **plain white** (dark background). **NEVER grey.**

### Rule 2 — Stabilo bright highlighter (current step ONLY)

- ONLY the current step's **heart(s)** — the single most important piece(s) — get a bright marker swipe over their colored form.
- Bright colors: yellow, green, orange, pink, cyan. Picked fresh per step, not fixed.
- This is **NOT cumulative** (we do NOT highlight steps 1..k). Only the CURRENT step's heart(s) light up.

### How this works in the actual data model

The codebase (as of June 29, 2026) uses this corrected model everywhere. Here is what YOUR format and tool must produce:

**In a recipe JSON:**
```json
{
  "name": "curve",
  "op": "polyline", "points": ["ptA", "ptb", "ptc", "ptd", "ptE"],
  "draw": {
    "step": 1,
    "is_heart": true,
    "local_color": { "name": "curveblue", "hex": "#1E6FE0" }
  }
}
```
- `local_color` = `LocalColor | null`. `null` means uncolored (black ink).
- `is_heart: true` = this element gets the bright Stabilo marker on its step.
- `step` = which proof step this element belongs to (1-based).

**In a TextBlock:**
```json
{
  "block_id": "lemma_2.s1.txt",
  "latex": "In the figure $AacE$, bounded by $\\textcolor{sideorange}{Aa}$ and $\\textcolor{basegreen}{AE}$ and by \\textcolor{curveblue}{the curve $acE$}...",
  "colors_used": [
    { "name": "curveblue",  "hex": "#1E6FE0" },
    { "name": "basegreen",  "hex": "#00A35A" },
    { "name": "sideorange", "hex": "#E8770A" }
  ]
}
```
- The LaTeX uses standard `\textcolor{name}{text}` — no custom macros.
- `colors_used` lists every local color that appears in `\textcolor` spans in this text block.
- The OFF baker redefines each `\textcolor{name}` to render as black (000000), so the OFF panel is pure black text.

**Important:** The child NEVER writes `colors_used` — the TOOL populates it by scanning the LaTeX for `\textcolor{name}{...}` spans. The child only writes `\textcolor{name}{text}` in their LaTeX and declares which colors they're using per station in the format.

---

## §2 — THE FROZEN OUTPUT FORMATS (your tool MUST write these exactly)

These are the ACTUAL pydantic schemas in `map/raw_models.py` as of June 29, 2026. Your tool's output must validate against them with `extra="forbid"`.

### Recipe (`recipe.<figure_id>.json`)

```python
class Recipe(BaseModel):
    schema_version: Literal["1.0"]
    figure_id: FigureId               # pattern: ^[a-z][a-z0-9_]*\.f[0-9]+$   e.g. "lemma_2.f1"
    node_id: NodeId                   # pattern: ^[a-z][a-z0-9_]*$            e.g. "lemma_2"
    edition: str                      # free-text citation
    caption: str                      # one-sentence figure description
    n_steps: int = Field(ge=1)
    steps: list[StepGloss]            # per-step human glosses
    ops: list[RecipeOp]               # construction operations

class StepGloss(BaseModel):
    index: int = Field(ge=1)
    gloss: str                        # one-sentence English description of this step

class LocalColor(BaseModel):
    name: str   # pattern: ^[a-z][a-z0-9_]*$   lowercase_underscore, e.g. "curveblue"
    hex: str    # "#RRGGBB"

class Draw(BaseModel):
    local_color: Optional[LocalColor] = None  # None = uncolored (black/white)
    step: int = Field(ge=1)
    is_heart: bool = False
    label: Optional[Label] = None
    marker: Literal["none","dot"] = "none"
```

Every `RecipeOp` has a `name: OpName` (unique id) and optional `draw: Draw | None`. The full construction vocabulary:

**Points:** `free_point` (optional rough_xy), `point_on` (path, optional t, near), `intersect` (a, b, optional near), `midpoint` (a, b), `foot` (point, line), `reflect_point` (point, over)
**Lines:** `line` (a, b), `segment` (a, b), `ray` (a, b), `parallel` (through, to), `perpendicular` (through, to), `tangent_at` (curve, at), `tangent_from` (curve, frm, optional near), `bisector` (a, vertex, b)
**Circles:** `circle_cp` (center, through), `circle_cr` (center, optional radius_points, radius_value), `circle_3` (a, b, c), `arc` (center, frm, to, optional direction ccw/cw)
**Conics:** `ellipse_foci` (f1, f2, through), `ellipse_axes` (center, major_end, minor_end), `parabola_fd` (focus, directrix), `hyperbola_foci` (f1, f2, through), `conic_5` (p1..p5)
**Compounds:** `polygon` (points, min 3), `polyline` (points, min 2), `series` (along, optional to_curve, count 1..64, kind: inscribed_rects | circumscribed_rects | ordinates | chords | tangent_polygon)
**Labels:** `label` (at — must set Draw)

### RoomSource (`room_source.<node_id>.json`)

```python
class TextBlock(BaseModel):
    block_id: TextBlockId   # pattern: ^[a-z][a-z0-9_]*\.s[0-9]+\.txt$   e.g. "lemma_2.s1.txt"
    latex: str              # LaTeX body with \textcolor{name}{...} spans
    colors_used: list[LocalColor]  # POPULATED BY TOOL from scanning \textcolor spans

class DrawingBlock(BaseModel):
    block_id: DrawBlockId   # pattern: ^[a-z][a-z0-9_]*\.s[0-9]+\.fig$   e.g. "lemma_2.s1.fig"
    figure_id: FigureId
    highlight_step: int = Field(ge=1)

class StepPair(BaseModel):
    pair_id: PairId         # pattern: ^[a-z][a-z0-9_]*\.s[0-9]+$         e.g. "lemma_2.s1"
    step_index: int = Field(ge=1)
    drawing: DrawingBlock
    text: TextBlock

class FigureDecl(BaseModel):
    figure_id: FigureId
    asy_path: str           # e.g. "figures/lemma_2.f1.asy"
    recipe_path: str        # e.g. "recipes/lemma_2.f1.json"
    n_steps: int = Field(ge=1)
    caption: str
    colors_used: list[LocalColor]  # POPULATED BY TOOL: union of all TextBlock colors_used

class CeilingEq(BaseModel):
    eq_id: EqId             # pattern: ^[a-z][a-z0-9_]*\.eq[0-9]+$       e.g. "lemma_2.eq0"
    latex: str              # a mathematical expression, e.g. "\lim_{AB \to 0} ..."

class RoomSource(BaseModel):
    schema_version: Literal["1.0"]
    node_id: NodeId
    edition: str
    figures: list[FigureDecl]    # empty list for text-only rooms
    blocks: list[StepPair]
    final_pair_id: PairId
    ceiling_equations: list[CeilingEq]
```

**Text-only rooms:** `figures = []`, `blocks` have NO DrawingBlock (or drawing=None).

### Figure .asy (Asymptote source)

Your tool generates self-contained Asymptote code that uses a `highlight` variable (default -1 = all off, 1..n_steps = that step's heart lit) and per-local-color `pen` variables. The Asymptote does NOT use `\cg`, `prooffig.asy`, or any global palette — it's self-contained.

See the real lemma_2 example at `quake/levels/principia_bk1_inverse_square/figures/lemma_2.f1.asy` for the exact pattern.

---

## §3 — THE FORMAT DESIGN (what children write)

### Inspiration: Descent's keyword-block format

```
CORRIDOR: 1
TITLE { ... }
BRIEFING_INTRO { ... }

ROBOT: 1
NAME { ... }
PROBLEM { ... }
SEGMENTS { ... }
EYE { <ledger_key> }
```

Blocks use `KEYWORD { ... }` with braces spanning multiple lines. Single values use `KEYWORD: value`. Lines starting `#` are comments. Order is fixed.

### Your Quake room format (your design)

You design the exact keywords. It must support TWO room types:

**Figure room:** has steps with geometry + text. Tool outputs: recipe.json + figure.asy + room_source.json.
**Text-only room:** has steps with text only (no geometry, no figure). Tool outputs: room_source.json only.

Minimum information the format must capture for EACH station (step):

| What | Where it goes |
|------|---------------|
| Step description (English gloss) | Recipe.steps[i].gloss |
| Geometric elements: name, construction op, params | Recipe.ops |
| Per element: `local_color` (name+hex) or null, `step`, `is_heart` | Recipe.ops[i].draw |
| Labels on points/lines | Recipe.ops[i].draw.label |
| LaTeX text for the text panel (with `\textcolor{name}{text}`) | TextBlock.latex |
| Ceiling equation LaTeX | CeilingEq.latex |

The format must also capture:
- `edition` (citation string)
- `caption` (one-sentence figure description)
- `n_steps` (number of steps)
- `final_pair_id` (which step-pair is the last one)

### Example: what a lemma_2 format file might look like

This is illustrative — YOU design the final keyword names and structure:

```
ROOM: lemma_2
EDITION: Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II.
FIGURE: lemma_2.f1
  CAPTION: Inscribed and circumscribed parallelograms on equal bases...
  N_STEPS: 3

STEP: 1
  GLOSS: The curvilinear figure AacE: the curve aE, the baseline AE, and side Aa.
  HEART: curve        # which element(s) get the Stabilo bright marker
  COLORS {
    curveblue  = #1E6FE0
    basegreen  = #00A35A
    sideorange = #E8770A
  }
  ELEMENTS {
    point A   at (0, 0)     label "$A$" SW
    point E   at (8, 0)     label "$E$" SE
    point B   at (2, 0)     label "$B$" S
    ...
    segment baseAE  from A to E              color basegreen
    polyline curve  through ptA ptb ptc ptE  color curveblue
    segment sideAa  from A to ptA            color sideorange
  }
  TEXT {
    In the figure $AacE$, bounded by the right lines $\textcolor{sideorange}{Aa}$
    and $\textcolor{basegreen}{AE}$ and by \textcolor{curveblue}{the curve $acE$},
    take any number of \emph{equal} bases $AB$, $BC$, $CD$, $\&c.$ along
    \textcolor{basegreen}{the base $AE$}.
  }

STEP: 2
  GLOSS: The inscribed parallelograms standing under the curve.
  HEART: inscribed
  COLORS { inscpurple = #8E24AA }
  ELEMENTS {
    series inscribed  along baseAE to_curve curve  count 4  kind inscribed_rects  color inscpurple
  }
  TEXT {
    On these equal bases erect \textcolor{inscpurple}{the inscribed parallelograms
    $Ab$, $Bc$, $Cd$, $\&c.$}, with sides $Bb$, $Cc$, $Dd$ parallel to
    $\textcolor{sideorange}{Aa}$.
  }

STEP: 3
  GLOSS: The circumscribed parallelograms completed above the curve.
  HEART: circumscribed
  COLORS { circred = #D81B60 }
  ELEMENTS {
    series circumscribed  along baseAE to_curve curve  count 4  kind circumscribed_rects  color circred
  }
  TEXT {
    Complete \textcolor{circred}{the circumscribed parallelograms $aKbl$, $bLcm$, ...
    rising \emph{above} \textcolor{curveblue}{the curve}. ... \textit{Q.E.D.}
  }

CEILING {
  eq0: \lim_{AB \to 0}\; \bigl(\text{circumscribed} - \text{inscribed}\bigr) = 0
  eq1: \text{inscribed} = \text{circumscribed} = \text{curvilinear area}
}
```

The child writes THIS. Your tool reads it and generates valid JSON + Asymptote.

**Key rules the format must enforce:**
1. Every geometric element in a step MUST have a `color` or be explicitly marked `nocolor`
2. Every step MUST have at least one `HEART` element
3. Every `\textcolor{name}{...}` in the LaTeX text MUST use a color declared in that step's `COLORS` block
4. `COLORS` names must be lowercase_underscore matching the `LocalColor.name` pattern
5. Ceiling equations are optional but at least one per room is recommended

---

## §4 — THE TOOL SPEC

Single Python file: `build/room_from_spec.py`

```python
def build_room(spec_path: str, out_dir: str) -> dict:
    """Parse spec, write recipe.json + figure.asy + room_source.json to out_dir.
    Returns dict of written paths."""
```

Dependencies: stdlib + pydantic v2 (for validating output). No GL, no moderngl, no pyglet.

What it does, step by step:
1. **Parse** the spec file → structured data
2. **Validate:**
   - Every element has `local_color` or explicit `nocolor`
   - Every step has >=1 heart
   - Every `\textcolor{name}` uses a declared color
   - IDs match patterns, step counts match, no duplicates
   - All `\textcolor{name}` names appear in that step's COLORS block
3. **For figure rooms:** generate Recipe.ops with `Draw` populated (local_color, step, is_heart, label, marker) + generate .asy (Asymptote with per-color pens and `highlight` conditionals) + generate RoomSource (TextBlocks with `\textcolor` spans intact, `colors_used` populated by scanning)
4. **For text-only rooms:** generate RoomSource only (no recipe, no .asy)
5. **All output valid** against `raw_models.py` schemas with `extra="forbid"`

**What the tool does NOT do:** run Asymptote, bake PNGs, compile LaTeX. Those are separate pipeline steps.

---

## §5 — THE 20 ROOMS (what children will fill in)

From Parent 7's frozen level design (Book 1 Sections I–III):

### 11 figure rooms (step counts LOCKED):

| Room | Figure | Steps |
|------|--------|-------|
| lemma_2 | lemma_2.f1 | 3 |
| lemma_4 | lemma_4.f1 | 3 |
| lemma_5 | lemma_5.f1 | 2 |
| lemma_6 | lemma_6.f1 | 3 |
| lemma_7 | lemma_7.f1 | 3 |
| lemma_11 | lemma_11.f1 | 3 |
| prop_1 | prop_1.f1 | 4 |
| prop_6 | prop_6.f1 | 4 |
| prop_7 | prop_7.f1 | 3 |
| prop_11 | prop_11.f1 | 5 |
| prop_13 | prop_13.f1 | 4 |

### 9 text-only rooms:

lemma_3, lemma_9, lemma_10, law_1, law_2, prop_2, prop_4, lemma_12, prop_15

---

## §6 — PRINCIPIA TEXT LOCATIONS (for children's material requests)

```
quake/principia/axioms/axioms_and_laws.txt     — Laws I-III
quake/principia/book_1/section_01.txt           — Section I (Lemmas I-XI)
quake/principia/book_1/section_02.txt           — Section II (Props I-X)
quake/principia/book_1/section_03.txt           — Section III (Props XI-XVII)
```

DeepSeek also has `quake/principia/DIGESTED_PRINCIPIA.md` — a 340-line summary of all 148 items.

---

## §7 — CONCRETE REFERENCE FILES (ask Nir to paste any you need)

These are the working, validated files from Parent 13's lemma_2 proof-of-concept:

```
quake/levels/principia_bk1_inverse_square/recipes/lemma_2.f1.json      — full recipe
quake/levels/principia_bk1_inverse_square/figures/lemma_2.f1.asy       — full .asy
quake/levels/principia_bk1_inverse_square/room_sources/lemma_2.json     — full room_source
quake/map/raw_models.py                                                — all pydantic schemas
quake/bake/baker_text.py                                               — how \textcolor baking works
```

If you need exact field names, pattern regexes, or the Asymptote highlight convention, ask Nir to paste the relevant file. Do NOT ask for the whole Bible — ask for specific sections.

---

## §8 — CONTEXT SURVIVAL RULES

1. **One batch of questions.** Ask everything in your first response. Then build.
2. **Minimal messages.** Target 2-3 round-trips total.
3. **Ask for specific files,** not "the Bible" or "everything."
4. **One mission, one deliverable:** format spec + `build/room_from_spec.py`.
5. **Tables die on copy-paste.** Use fenced code blocks.
6. **Talk first, then build.** Do NOT sprint to implementation — state your approach and questions first, wait for answers.

---

## §9 — START

State your format design approach (keyword names, block structure, how you'll handle figure vs text-only rooms), your tool architecture (parse → validate → emit), and ALL your questions. Then, after answers, build. 🚀
