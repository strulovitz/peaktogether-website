# 🔥 PROMPT TO OPUS — QUAKE PARENT 10: Principia Room Content Design

> DeepSeek-authored. Self-contained. The ONE file Nir pastes after Commentaries + OT + NT.

---

## ⚠️ CRITICAL — HOW YOU GET INFORMATION

You (Parent 10, inside OpenRouter) have NO internet, NO GitHub access, NO file system. Everything you know comes from what Nir pastes.

When you need more information:

    "Nir, please ask DeepSeek to fetch [specific file / section / snippet]."

Nir → DeepSeek → fetches from disk → Nir pastes to you.

---

## §1 — WHERE WE ARE

The game engine is complete. 382/382 tests green. The level graph (20 nodes, 28 edges, Principia Book 1 Sections I–III) is frozen and validated. The floorplan has 5 natural crossings (bridges/underpasses). The map viewer works — you can fly around and see the graph.

**Your job: design the CONTENT that fills those 20 rooms.**

---

## §2 — THE 20 NODES

Here is the complete concept_graph.json (Parent 7's frozen deliverable). 11 nodes have figures, 9 are text-only.

```
NODE         NAME              KIND     IMP  PAGES    FIG?
lemma_2      Lemma II          lemma    5    30       FIG (simple)
lemma_3      Lemma III         lemma    3    30       no fig
lemma_4      Lemma IV          lemma    4    31       FIG (simple)
lemma_5      Lemma V           lemma    3    32       FIG (similar triangles)
lemma_6      Lemma VI          lemma    4    32       FIG (chord-tangent)
lemma_7      Lemma VII         lemma    5    33       FIG (arc-chord-tangent)
lemma_9      Lemma IX          lemma    3    35       no fig
lemma_10     Lemma X           lemma    5    36       no fig
lemma_11     Lemma XI          lemma    5    37       FIG (subtense-curvature)
law_1        Law I             law      4    19       no fig
law_2        Law II            law      5    19       no fig
prop_1       Prop. I, Th I     prop     5    40-41    FIG (Kepler area law)
prop_2       Prop. II, Th II   prop     4    42       no fig
prop_4       Prop. IV, Th IV   prop     5    45       no fig
prop_6       Prop. VI, Th V    prop     5    48       FIG (force measure)
prop_7       Prop. VII, Pr II  prop     3    50       FIG (circle force)
lemma_12     Lemma XII         lemma    3    55       no fig
prop_11      Prop. XI, Pr VI   prop     5    56-57    FIG ★ (inverse-square ellipse)
prop_13      Prop. XIII, Pr VIII prop    4    61       FIG (inverse-square parabola)
prop_15      Prop. XV, Th VII  prop     5    63       no fig
```

Full concept_graph.json at: `quake/levels/principia_bk1_inverse_square/concept_graph.json`
(Ask DeepSeek to fetch it if you need the edges.)

---

## §3 — YOUR DELIVERABLE

For EACH of the 20 nodes, produce a **room source JSON** conforming to the Second Canon §4.3. The schema is:

```python
class FigureDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figure_id: FigureId          # pattern: ^[a-z][a-z0-9_]*\.f[0-9]+$  e.g. "lemma_2.f1"
    asy_path: str                # path to .asy file, e.g. "figures/figure.lemma_2.f1.asy"
    recipe_path: str             # path to recipe JSON, e.g. "figures/recipe.lemma_2.f1.json"
    n_steps: int = Field(ge=1)   # number of highlight steps (including the "off" state)
    caption: str                 # human-readable caption
    groups_used: list[GroupName] # palette group names this figure uses

class DrawingBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: DrawBlockId        # pattern: {node}.s{n}.fig  e.g. "lemma_2.s1.fig"
    figure_id: FigureId          # which figure this step draws
    highlight_step: int = Field(ge=1)  # 1..n_steps

class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: TextBlockId        # pattern: {node}.s{n}.txt
    latex: str                   # LaTeX text for this step
    groups_used: list[GroupName] # palette groups referenced in this text

class StepPair(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId              # pattern: {node}.s{n}  e.g. "lemma_2.s1"
    step_index: int = Field(ge=1)
    drawing: DrawingBlock
    text: TextBlock

class RoomSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]
    node_id: NodeId
    edition: str                 # citation string
    figures: list[FigureDecl]
    blocks: list[StepPair]
    final_pair_id: PairId        # the last step (shooting this opens the hidden door)
    ceiling_equations: list[CeilingEq]  # latex displayed on the ceiling
```

Example of a complete room_source JSON:

```json
{
  "schema_version": "1.0",
  "node_id": "lemma_2",
  "edition": "Newton, Principia, trans. Motte (1729)",
  "figures": [
    {
      "figure_id": "lemma_2.f1",
      "asy_path": "figures/figure.lemma_2.f1.asy",
      "recipe_path": "figures/recipe.lemma_2.f1.json",
      "n_steps": 3,
      "caption": "Inscribed and circumscribed parallelograms under a curve.",
      "groups_used": ["curve", "inscribed", "circumscribed"]
    }
  ],
  "blocks": [
    {
      "pair_id": "lemma_2.s1",
      "step_index": 1,
      "drawing": {"block_id": "lemma_2.s1.fig", "figure_id": "lemma_2.f1", "highlight_step": 1},
      "text": {"block_id": "lemma_2.s1.txt", "latex": "Let the curve $AB$ be divided...", "groups_used": ["curve"]}
    },
    {
      "pair_id": "lemma_2.s2",
      "step_index": 2,
      "drawing": {"block_id": "lemma_2.s2.fig", "figure_id": "lemma_2.f1", "highlight_step": 2},
      "text": {"block_id": "lemma_2.s2.txt", "latex": "The \\cg{inscribed}{inscribed rectangles}...", "groups_used": ["inscribed"]}
    },
    {
      "pair_id": "lemma_2.s3",
      "step_index": 3,
      "drawing": {"block_id": "lemma_2.s3.fig", "figure_id": "lemma_2.f1", "highlight_step": 3},
      "text": {"block_id": "lemma_2.s3.txt", "latex": "Therefore the ultimate ratio is equality. Q.E.D.", "groups_used": ["circumscribed"]}
    }
  ],
  "final_pair_id": "lemma_2.s3",
  "ceiling_equations": [
    {"eq_id": "lemma_2.eq1", "latex": "\\lim_{n\\to\\infty}\\frac{A_{\\text{inscribed}}}{A_{\\text{circumscribed}}}=1"}
  ]
}
```

**Validation rules:**
- filename stem == node_id (e.g. room_lemma_2.json)
- All block_id/pair_id/eq_id prefixes == node_id
- step_index contiguous from 1..N, unique
- Each drawing.figure_id ∈ figures list
- highlight_step ∈ 1..figure.n_steps
- final_pair_id ∈ blocks
- All groups_used ⊆ palette keys

---

## §4 — WHAT YOU NEED TO DESIGN FOR EACH ROOM

### A) Figures (for the 11 FIG rooms)

For each figure room, you need to design:

1. **The Asymptote `.asy` file** — a geometric construction that draws the figure.
   Must use `prooffig.asy` (the standard template that handles highlight/off states).
   The key contract: `prooffig.asy` provides `drawall(int highlight)` — your `.asy` file
   calls `drawall(highlight)` and defines the drawing logic for each step.

2. **The recipe JSON** — specifies what gets highlighted at each step.
   Schema (Second Canon §3.A.4):
   ```json
   {
     "schema_version": "1.0",
     "figure_id": "lemma_2.f1",
     "n_steps": 3,
     "steps": [
       {"step": 0, "desc": "off", "show": [], "highlight": []},
       {"step": 1, "desc": "Draw the curve", "show": ["curve"], "highlight": ["curve"]},
       {"step": 2, "desc": "Add inscribed rects", "show": ["curve","inscribed"], "highlight": ["inscribed"]},
       {"step": 3, "desc": "Add circumscribed rects", "show": ["curve","inscribed","circumscribed"], "highlight": ["circumscribed"]}
     ]
   }
   ```
   Step 0 = the "off" state (grey outline only).

3. **Color groups** — defined in `palette.json`. You reference group names like
   `"curve"`, `"inscribed"`, `"circumscribed"` — NOT hex colors. The palette
   already has groups defined.

### B) Text panels (for ALL 20 rooms)

Each step has a LaTeX text block. Use `\cg{groupname}{text}` to color-code
references to figure groups. The text should follow Newton's actual proof from
the Principia text.

For text-only rooms (no figures): still produce step pairs with drawing blocks
that reference `figure_id: ""` and `highlight_step: 0` (no figure).

### C) Ceiling equations

At least 1 LaTeX equation per room, displayed on the ceiling when the player
enters. Should be the key result of that lemma/proposition.

---

## §5 — PALETTE

The palette.json is already defined for this level. Ask DeepSeek for:
`quake/levels/principia_bk1_inverse_square/palette.json`

It defines the color groups you reference in figures and text. Key groups include:
`curve`, `inscribed`, `circumscribed`, `radius`, `tangent`, `chord`, `arc`,
`orbit`, `force`, `construction`, `area`, `path`, etc.

---

## §6 — MATERIAL YOU CAN REQUEST

**Already provided in baseline:**
- The Commentaries (BIBLE index + locked decisions)
- Old Testament (Fusion's doctrine)
- New Testament (Opus's two-legs design)

**Available on request:**

- `quake/levels/principia_bk1_inverse_square/concept_graph.json` — 20 nodes + 28 edges
- `quake/levels/principia_bk1_inverse_square/palette.json` — color groups
- `quake/principia/DIGESTED_PRINCIPIA.md` — one-sentence summaries of all 148 items
- `quake/principia/book_1/section_01.txt` — Lemmas I–XI text
- `quake/principia/book_1/section_02.txt` — Props I–X text
- `quake/principia/book_1/section_03.txt` — Props XI–XVII text
- `quake/principia/axioms/axioms_and_laws.txt` — Laws I–III
- Second Canon §3.A.4–§3.A.7 (recipe, figure.asy, prooffig.asy, palette contracts)
- Second Canon §4.3 (room_source schema)

---

## §7 — SUGGESTED WORKFLOW

1. Ask for the palette.json + concept_graph.json
2. Ask for the DIGEST to review one-sentence summaries
3. Design FIGURES first (the 11 figure rooms) — these are the hard part:
   - Start with the simplest: lemma_2 (rectangles under curve), lemma_5 (similar triangles)
   - Then medium: lemma_7 (arc-chord-tangent), prop_1 (Kepler area law)
   - Then hard: prop_11 (inverse-square ellipse — the centerpiece)
4. For each figure: write the Asymptote .asy source + recipe JSON + figure declaration
5. Add text panels for all 20 rooms (LaTeX proof text)
6. Output all 20 room_source JSONs

**For LaTeX text:** read the DIGEST first, then request individual section text files
for specific propositions. Do NOT request all 4,500 lines at once — one section at
a time, only when you need it.

**For figure design:** the DIGEST tells you what each figure shows. DeepSeek can
fetch the original Principia plate descriptions if you need the exact geometry.

---

## §8 — ACCEPTANCE GATES

After you deliver, DeepSeek will:

1. Validate all 20 room_source JSONs against §4.3 schema
2. Validate all recipe JSONs against §3.A.4 schema
3. Validate all Asymptote .asy files for correct imports and structure
4. Run the full content pipeline (palette → recipe_validate → prooffig_check →
   asy_compile → imageops → baker_figure → baker_text → overlay_diff)
5. Run the room pipeline (portal_spec → room_geometry → room_pack → room_validate → room_maker)
6. Assemble the pack and verify load_pack succeeds
7. Run the full 382-test suite — zero regressions

---

## §9 — THE BIG PICTURE

After 9 parents, the engine is DONE. The layout is FIXED. The map viewer WORKS.
The ONLY remaining piece before Nir can play is the CONTENT — the figures and text
that fill the rooms.

This is YOUR mission: take Newton's actual 1729 proofs and turn them into walkable,
shootable 3D rooms. 20 rooms. 11 figures. The inverse-square law is the headline —
prop_11 should be the most beautiful room in the level.

You design. Children build. DeepSeek integrates. Go. 🔥📐

---

## §10 — CRITICAL: KNOWN RENDERING BUGS (read before designing room renderer)

The rendering code (`render_wire.py`) shipped with MULTIPLE silent bugs that
made it render black since day 1. DeepSeek discovered and attempted to fix them
but Nir judged the fixes low-quality (took hours, produced a simplified LINES
hack that discards the thick-line/bloom/quad-expansion aesthetic the OT specified).

**You should review the renderers and fix them properly.**

### The bugs found:

**Bug 1 — shader function never called:**
`shaders.py` exports `wire_program(ctx)` as a FUNCTION that takes a GL context
and returns a compiled program. But `draw_graph` imported it and passed the
RAW FUNCTION to `ctx.vertex_array()`, which silently failed (try/except swallowed
the error). Verify `solid_program(ctx)` is called correctly in `render_room.py`.

**Bug 2 — shader/VBO type mismatch:**
Shader declared `in vec2 in_side` but VBO provided only 1 float per vertex.
The missing y component defaulted to 0, causing quad-expansion triangles to
collapse to zero area. The "expand to quad" code (`expand_segments_to_quad_attribs`
in render_wire.py) and the VAO format string must match the shader declarations.

**Bug 3 — VAO attribute not in shader:**
`_gl_make_vao` bound attribute `in_other` that the shader never declared.
`ctx.vertex_array()` raised KeyError, caught silently, nothing rendered.

**Bug 4 — No projection matrix:**
Map viewer passes `u_mvp` = view matrix only. The shader expects a full
model-view-PROJECTION matrix but no perspective projection was ever built.

**Bug 5 — `KeyStateHandler` broken in pyglet 2.1.14 on Windows:**
Replaced with manual `_pressed: set[int]` tracking in the viewer.

### What DeepSeek did (the "fix" you should review):
Stripped out the entire quad-expansion system, replaced WIRE shader with a
trivial pass-through vertex/fragment shader, and renders corridors as simple
1-pixel GL_LINES. This works visually but discards: thick-line width, screen-space
distance dimming, bloom post-pass, and the Mode A aesthetic from the OT.

### Relevant files (ask DeepSeek to fetch):
- `quake/render_wire.py` — current simplified wireframe renderer
- `quake/render_room.py` — solid room renderer (UNVERIFIED — likely has same bugs)
- `quake/shaders.py` — all GLSL + `wire_program(ctx)` etc.
- `quake/tools/map_viewer.py` — map viewer (key tracking)
- `quake/camera.py` — `look_at()` view matrix
- `quake/gfx_context.py` — window + GL context

### Your call:
Decide whether to restore the proper quad-expansion approach with thick lines and
bloom, or keep the simplified LINES and add thickness back later. Either way,
`render_room.py` must be verified — if rooms render black, the entire game is
pointless no matter how beautiful the figure designs are.
