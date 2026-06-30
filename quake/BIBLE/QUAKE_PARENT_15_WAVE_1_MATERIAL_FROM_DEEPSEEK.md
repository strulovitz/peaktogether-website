# 📦 MATERIAL PACKET FOR PARENT 15 — WAVE 1 (assembled by DeepSeek)

> This answers your batched questions: Group A (gold reference + station contract), Group B (Parent 7's figure plan + palette), Group C **Wave 1** (the 8 Newton items), and Nir's answer to your Group D / Q4. Everything verbatim except where I mark a `[DeepSeek note]`.

---

## 0 — CONFIRMATION + HOW TO STAY ALIVE (read once, then don't loop)

Your four understanding points are **all correct** — local-per-station color (no global palette, no grey, current-step-only Stabilo), the **station** as the atomic unit, **math + its foundations** both colored, and the missing data-contract piece for non-geometry panels. **You do not need to restate this again.** Please skip the "let me prove I understood" recaps and the multi-batch confirmation rounds — those are what fill your context and kill you before you deliver. From here: take a node, read its material below, decide its stations, write it down. Keep confirmations to one line. When you want **Wave 2**, ask for it in **one** batch.

**Q4 — Nir's decision (foundation-room stations):** **OPTION A.** Each foundational illustration is **its own station** → a bigger room. And Nir made it a **general rule**: *wherever a node has multiple foundational illustrations/examples, each one gets its own station.* So `law_1` (inertia) becomes a multi-station room: **top = 1 station, planets/comets = 1 station, projectile = 1 station** (plus the law statement itself). Apply the same rule anywhere else it comes up.

---

## A.1 — THE GOLD REFERENCE: the `lemma_2` trio (verbatim, the corrected-model template)

### recipe — `recipes/lemma_2.f1.json`
```json
{
  "schema_version": "1.0",
  "figure_id": "lemma_2.f1",
  "node_id": "lemma_2",
  "edition": "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6.",
  "caption": "Inscribed and circumscribed parallelograms on equal bases under the curve aE; as the bases shrink, the inscribed figure AKbLcMdD, the circumscribed figure AalbmcndoE, and the curvilinear figure AabcdE become ultimately equal.",
  "n_steps": 3,
  "steps": [
    { "index": 1, "gloss": "The curvilinear figure AacE: the curve aE, the baseline AE on equal bases, and the side Aa." },
    { "index": 2, "gloss": "The inscribed parallelograms Ab, Bc, Cd, standing under the curve on the equal bases." },
    { "index": 3, "gloss": "The circumscribed parallelograms completed above the curve; their excess over the inscribed figure is the single rectangle ABla, which vanishes as AB shrinks." }
  ],
  "ops": [
    { "name": "A", "op": "free_point", "rough_xy": [0.0, 0.0], "draw": { "step": 1, "marker": "dot", "label": { "tex": "$A$", "placement": "SW" } } },
    { "name": "E", "op": "free_point", "rough_xy": [8.0, 0.0], "draw": { "step": 1, "marker": "dot", "label": { "tex": "$E$", "placement": "SE" } } },
    { "name": "B", "op": "free_point", "rough_xy": [2.0, 0.0], "draw": { "step": 1, "marker": "dot", "label": { "tex": "$B$", "placement": "S" } } },
    { "name": "C", "op": "free_point", "rough_xy": [4.0, 0.0], "draw": { "step": 1, "marker": "dot", "label": { "tex": "$C$", "placement": "S" } } },
    { "name": "D", "op": "free_point", "rough_xy": [6.0, 0.0], "draw": { "step": 1, "marker": "dot", "label": { "tex": "$D$", "placement": "S" } } },
    { "name": "ptA", "op": "free_point", "rough_xy": [0.0, 1.4], "draw": { "step": 1, "marker": "none", "label": { "tex": "$a$", "placement": "NW" }, "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptb", "op": "free_point", "rough_xy": [2.0, 2.6], "draw": { "step": 1, "marker": "none", "label": { "tex": "$b$", "placement": "N" }, "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptc", "op": "free_point", "rough_xy": [4.0, 3.4], "draw": { "step": 1, "marker": "none", "label": { "tex": "$c$", "placement": "N" }, "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptd", "op": "free_point", "rough_xy": [6.0, 3.9], "draw": { "step": 1, "marker": "none", "label": { "tex": "$d$", "placement": "N" }, "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "ptE", "op": "free_point", "rough_xy": [8.0, 4.2], "draw": { "step": 1, "marker": "none", "label": null, "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "curve", "op": "polyline", "points": ["ptA", "ptb", "ptc", "ptd", "ptE"], "draw": { "step": 1, "marker": "none", "is_heart": true, "local_color": { "name": "curveblue", "hex": "#1E6FE0" } } },
    { "name": "baseAE", "op": "segment", "a": "A", "b": "E", "draw": { "step": 1, "marker": "none", "local_color": { "name": "basegreen", "hex": "#00A35A" } } },
    { "name": "sideAa", "op": "segment", "a": "A", "b": "ptA", "draw": { "step": 1, "marker": "none", "local_color": { "name": "sideorange", "hex": "#E8770A" } } },
    { "name": "inscribed", "op": "series", "along": "baseAE", "to_curve": "curve", "count": 4, "kind": "inscribed_rects", "draw": { "step": 2, "marker": "none", "is_heart": true, "local_color": { "name": "inscpurple", "hex": "#8E24AA" } } },
    { "name": "circumscribed", "op": "series", "along": "baseAE", "to_curve": "curve", "count": 4, "kind": "circumscribed_rects", "draw": { "step": 3, "marker": "none", "is_heart": true, "local_color": { "name": "circred", "hex": "#D81B60" } } }
  ]
}
```

### room_source — `room_sources/lemma_2.json`
```json
{
  "schema_version": "1.0",
  "node_id": "lemma_2",
  "edition": "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II.",
  "figures": [
    {
      "figure_id": "lemma_2.f1",
      "asy_path": "figures/lemma_2.f1.asy",
      "recipe_path": "recipes/lemma_2.f1.json",
      "n_steps": 3,
      "caption": "Inscribed and circumscribed parallelograms under the curve aE on equal bases.",
      "colors_used": [
        { "name": "curveblue",  "hex": "#1E6FE0" },
        { "name": "basegreen",  "hex": "#00A35A" },
        { "name": "sideorange", "hex": "#E8770A" },
        { "name": "inscpurple", "hex": "#8E24AA" },
        { "name": "circred",    "hex": "#D81B60" }
      ]
    }
  ],
  "blocks": [
    {
      "pair_id": "lemma_2.s1", "step_index": 1,
      "drawing": { "block_id": "lemma_2.s1.fig", "figure_id": "lemma_2.f1", "highlight_step": 1 },
      "text": {
        "block_id": "lemma_2.s1.txt",
        "latex": "In the figure $AacE$, bounded by the right lines $\\textcolor{sideorange}{Aa}$ and $\\textcolor{basegreen}{AE}$ and by \\textcolor{curveblue}{the curve $acE$}, take any number of \\emph{equal} bases $AB$, $BC$, $CD$, $\\&c.$ along \\textcolor{basegreen}{the base $AE$}. This is the curvilinear figure whose area we mean to measure.",
        "colors_used": [
          { "name": "curveblue",  "hex": "#1E6FE0" },
          { "name": "basegreen",  "hex": "#00A35A" },
          { "name": "sideorange", "hex": "#E8770A" }
        ]
      }
    },
    {
      "pair_id": "lemma_2.s2", "step_index": 2,
      "drawing": { "block_id": "lemma_2.s2.fig", "figure_id": "lemma_2.f1", "highlight_step": 2 },
      "text": {
        "block_id": "lemma_2.s2.txt",
        "latex": "On these equal bases erect \\textcolor{inscpurple}{the inscribed parallelograms $Ab$, $Bc$, $Cd$, $\\&c.$}, with sides $Bb$, $Cc$, $Dd$ parallel to $\\textcolor{sideorange}{Aa}$. \\textcolor{inscpurple}{The inscribed figure $AKbLcMdD$} lies wholly \\emph{under} \\textcolor{curveblue}{the curve}.",
        "colors_used": [
          { "name": "inscpurple", "hex": "#8E24AA" },
          { "name": "sideorange", "hex": "#E8770A" },
          { "name": "curveblue",  "hex": "#1E6FE0" }
        ]
      }
    },
    {
      "pair_id": "lemma_2.s3", "step_index": 3,
      "drawing": { "block_id": "lemma_2.s3.fig", "figure_id": "lemma_2.f1", "highlight_step": 3 },
      "text": {
        "block_id": "lemma_2.s3.txt",
        "latex": "Complete \\textcolor{circred}{the circumscribed parallelograms $aKbl$, $bLcm$, $cMdn$, $\\&c.$}, rising \\emph{above} \\textcolor{curveblue}{the curve}. Their excess over \\textcolor{inscpurple}{the inscribed figure} is the sum $Kl + Lm + Mn + Do$, equal to the single rectangle $ABla$ on the base $\\textcolor{basegreen}{AB}$. As $\\textcolor{basegreen}{AB}$ is diminished \\emph{in infinitum} this rectangle becomes less than any given space; hence (by Lem.~I) \\textcolor{inscpurple}{the inscribed} and \\textcolor{circred}{the circumscribed} figures, and therefore the intermediate curvilinear figure, become ultimately equal. \\textit{Q.E.D.}",
        "colors_used": [
          { "name": "circred",    "hex": "#D81B60" },
          { "name": "curveblue",  "hex": "#1E6FE0" },
          { "name": "inscpurple", "hex": "#8E24AA" },
          { "name": "basegreen",  "hex": "#00A35A" }
        ]
      }
    }
  ],
  "final_pair_id": "lemma_2.s3",
  "ceiling_equations": [
    { "eq_id": "lemma_2.eq0", "latex": "\\lim_{AB \\to 0}\\; \\bigl(\\text{circumscribed} - \\text{inscribed}\\bigr) = ABla \\;\\longrightarrow\\; 0" },
    { "eq_id": "lemma_2.eq1", "latex": "\\text{inscribed} \\;=\\; \\text{circumscribed} \\;=\\; \\text{curvilinear area} \\quad (\\text{ultimately})" }
  ]
}
```

### figure — `figures/lemma_2.f1.asy`  (note the self-contained "prooffig" convention: black ink when OFF; matched colors + a translucent Stabilo underlay for the **current step's heart only** when `highlight=k`)
```asy
// figure.lemma_2.f1.asy  — Lemma II (inscribed/circumscribed rectangles)
// Self-contained prooffig convention. Compile: asy -u "highlight=k" figure.lemma_2.f1.asy
// highlight=-1 => OFF (all black). highlight=k (1..3) => step k's matched colors + step k heart Stabilo.

import graph;
settings.outformat = "png";
unitsize(1cm);

int highlight = -1;
usersetting();   // processes the -u "highlight=1" command-line flag

// ---- palette (LOCAL to this station-set; pure black when uncolored) ----
pen BLACK = rgb(0,0,0) + linewidth(1.0pt);
pen curveblue   = rgb(30/255, 111/255, 224/255) + linewidth(1.6pt);
pen basegreen   = rgb(0/255, 163/255, 90/255) + linewidth(1.6pt);
pen sideorange  = rgb(232/255, 119/255, 10/255) + linewidth(1.6pt);
pen inscpurple  = rgb(142/255, 36/255, 170/255) + linewidth(1.4pt);
pen circred     = rgb(216/255, 27/255, 96/255) + linewidth(1.4pt);

// bright Stabilo markers (local, per heart) — laid UNDER the ink, translucent
pen STABILO_CURVE = rgb(255/255, 224/255, 0/255) + opacity(0.45) + linewidth(9pt) + squarecap; // yellow
pen STABILO_INSC  = rgb(0/255, 230/255, 118/255) + opacity(0.35) + linewidth(9pt) + squarecap; // green
pen STABILO_CIRC  = rgb(255/255, 111/255, 0/255) + opacity(0.35) + linewidth(9pt) + squarecap; // orange

pair A=(0,0), B=(2,0), C=(4,0), D=(6,0), E=(8,0);
pair pa=(0,1.4), pb=(2,2.6), pc=(4,3.4), pd=(6,3.9), pe=(8,4.2);
path curve = pa--pb--pc--pd--pe;
path baseAE = A--E;
path sideAa = A--pa;

real curveY(real x) {
  pair[] P = {pa,pb,pc,pd,pe};
  for (int i=0; i<P.length-1; ++i)
    if (x >= P[i].x && x <= P[i+1].x) {
      real t = (x - P[i].x)/(P[i+1].x - P[i].x);
      return P[i].y + t*(P[i+1].y - P[i].y);
    }
  return P[P.length-1].y;
}
real[] xs = {0,2,4,6,8};
path[] inscribed; path[] circumscribed;
for (int i=0; i<xs.length-1; ++i) {
  real x0=xs[i], x1=xs[i+1];
  real hIn = curveY(x0); real hOut = curveY(x1);
  inscribed.push((x0,0)--(x1,0)--(x1,hIn)--(x0,hIn)--cycle);
  circumscribed.push((x0,0)--(x1,0)--(x1,hOut)--(x0,hOut)--cycle);
}

void drawAll(int highlight) {
  bool on1=(highlight==1), on2=(highlight==2), on3=(highlight==3);
  if (on1) draw(curve, STABILO_CURVE);
  if (on2) for (path r : inscribed)     draw(r, STABILO_INSC);
  if (on3) for (path r : circumscribed) draw(r, STABILO_CIRC);
  for (path r : inscribed)     filldraw(r, rgb(142/255,36/255,170/255)+opacity(0.12), on2 ? inscpurple : BLACK);
  for (path r : circumscribed) draw(r, on3 ? circred : BLACK);
  draw(baseAE, on1 ? basegreen  : BLACK);
  draw(sideAa, on1 ? sideorange : BLACK);
  draw(curve,  on1 ? curveblue  : BLACK);
  label("$A$", A, SW); label("$B$", B, S); label("$C$", C, S);
  label("$D$", D, S);  label("$E$", E, SE);
  label("$a$", pa, NW); label("$b$", pb, N); label("$c$", pc, N); label("$d$", pd, N);
}
drawAll(highlight);
```

---

## A.2 — THE STATION CONTRACT (verbatim from `map/raw_models.py`, pydantic v2, `extra="forbid"`)

```python
SCHEMA_VERSION = "1.0"
Hex  = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]
FigureId    = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.f[0-9]+$")]   # e.g. "law_1.f1"
PairId      = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+$")]   # e.g. "law_1.s2"
DrawBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.fig$")]
TextBlockId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.s[0-9]+\.txt$")]
EqId        = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*\.eq[0-9]+$")]

class LocalColor(BaseModel):          # per-element, fresh per station; NOT global
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")   # what the matching text references, e.g. "vsquared"
    hex: Hex

class Label(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tex: str
    placement: Literal["N","S","E","W","NE","NW","SE","SW","center"] = "NE"
    offset: Optional[Vec2] = None

class Draw(BaseModel):                 # the per-element draw spec inside a recipe op
    model_config = ConfigDict(extra="forbid")
    local_color: Optional[LocalColor] = None  # None = uncolored (black on light bg / white on dark; NEVER grey)
    step: int = Field(ge=1)                   # which proof step this element belongs to
    is_heart: bool = False                    # True = gets the bright Stabilo for that step
    label: Optional[Label] = None
    marker: Literal["none","dot"] = "none"

# Recipe ops you have (each op has name, op-literal, its geometry args, and optional draw):
#   POINTS:  free_point, point_on, intersect, midpoint, foot, reflect_point
#   LINES:   line, segment, ray, parallel, perpendicular, tangent_at, tangent_from, bisector
#   CIRCLES: circle_cp, circle_cr, circle_3, arc
#   CONICS:  ellipse_foci, ellipse_axes, parabola_fd, hyperbola_foci, conic_5
#   COMPOUND: polygon, polyline, series, angle_mark, label
class Series(BaseModel):               # the powerful one used by lemma_2
    op: Literal["series"]; along: Ref; to_curve: Optional[Ref] = None
    count: int = Field(ge=1, le=64)
    kind: Literal["inscribed_rects","circumscribed_rects","ordinates","chords","tangent_polygon"]

class StepGloss(BaseModel):
    model_config = ConfigDict(extra="forbid")
    index: int = Field(ge=1); gloss: str

class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]; figure_id: FigureId; node_id: NodeId
    edition: str; caption: str; n_steps: int = Field(ge=1)
    steps: list[StepGloss]; ops: list[RecipeOp]

class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: TextBlockId
    latex: str                         # \textcolor{name}{...} spans reference LocalColor.name
    colors_used: list[LocalColor]      # the local colors that appear in this block's spans

class FigureDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")
    figure_id: FigureId; asy_path: str; recipe_path: str
    n_steps: int = Field(ge=1); caption: str
    colors_used: list[LocalColor]      # union of all local colors across the figure's steps

class DrawingBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    block_id: DrawBlockId; figure_id: FigureId; highlight_step: int = Field(ge=1)

class StepPair(BaseModel):             # ← THE STATION. drawing is MANDATORY.
    model_config = ConfigDict(extra="forbid")
    pair_id: PairId; step_index: int = Field(ge=1)
    drawing: DrawingBlock              # ⚠️ NOT optional → a non-geometry station still needs a figure block
    text: TextBlock

class CeilingEq(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eq_id: EqId; latex: str

class RoomSource(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"]; node_id: NodeId; edition: str
    figures: list[FigureDecl]; blocks: list[StepPair]
    final_pair_id: PairId; ceiling_equations: list[CeilingEq]
```

**[DeepSeek note — the non-geometry-panel problem you flagged (§2.4):]** You are right: `StepPair.drawing: DrawingBlock` is mandatory, and `DrawingBlock` requires a `figure_id` pointing at a `FigureDecl` with an `.asy`. So **every station currently must have a figure**. For equation rooms / foundation rooms there is no printed diagram, so the cleanest path (matches the gold model with **zero contract change**) is: **the equation/illustration IS the figure** — emit a tiny `.asy` (or, if you prefer, a LaTeX-only image) that draws the colored equation or the colored foundational illustration, with the same `highlight=k` Stabilo convention. That keeps `drawing` populated and reuses the whole baker/room-maker pipeline. **You decide and specify it; I (DeepSeek) implement whatever contract/code change you choose** (e.g., if you'd rather add an optional `equation_panel` shape to `StepPair`, say so and I'll do it). Please pick one explicitly so I can wire it once.

---

## B — WHAT YOU ARE CORRECTING: Parent 7's figure plan + palette (verbatim)

**[DeepSeek note]** Parent 7's color groups below use the **dead** global 5-group model — you are replacing all of it with local-per-station colors. I keep the group tags only so you see exactly what you're replacing. Plate/Fig numbers are **tentative** (Parent 7 flagged this; confirm via the page later). Two prose **degree miscounts** to fix: `lemma_7` is **degree 6** (Parent 7 wrote 5); `prop_11` is **degree 4** (Parent 7 wrote 5) — the JSON edges are correct, only the prose was wrong. The PART-2 citation `label` phrases are Parent 7's reconstructions, to be confirmed.

**Parent 7's 11 FIGURE rooms** (plate/fig · steps · gloss · [old dead groups]):
- **lemma_2.f1** — Pl.1 Fig.6 — 3 steps — curve+baseline / inscribed rects / circumscribed rects. *(= the gold above.)*
- **lemma_4.f1** — Pl.1 Fig.7 — 3 — two figures of rectangles + correspondence lines.
- **lemma_5.f1** — Pl.2 Fig.1 — 2 — two similar figures, homologous sides marked.
- **lemma_6.f1** — Pl.2 Fig.1 region — 3 — arc ACB, chord AB, tangent AD, vanishing angle BAD.
- **lemma_7.f1** — Pl.2 Fig.1 — 3 — arc/chord/tangent + auxiliary RD.
- **lemma_11.f1** — Pl.2 Fig.4 — 3 — curve+tangent, chord AB + subtense BD⟂tangent.
- **prop_1.f1** — Pl.2 Fig.5 — 4 — centre S, polygon ABCDE, radii, swept triangles, impulse Cc∥SB. *(same family as golden-pack prop_1.)*
- **prop_6.f1** — Pl.3 Fig.2 — 4 — S, P, arc PQ, tangent ZPR, versed sine QR, QT⟂SP, force rect.
- **prop_7.f1** — Pl.3 Fig.3 — 3 — circle, body P, force-point S, tangent + RPQ.
- **prop_11.f1** — Pl.4 Fig.2 — 5 — ★HEADLINE ellipse foci S,H; body P; SP; tangent+diameters; parallelogram (Lem.XII); latus rectum L. `ellipse_foci`.
- **prop_13.f1** — Pl.5 Fig.3 — 4 — parabola, focus S, body P, tangent, latus rectum. `parabola_fd`.

**Parent 7's 9 "FIGURE-LESS" rooms (verbatim, line 267):** "*lemma_3, lemma_9, lemma_10, law_1, law_2, prop_2, prop_4, prop_15, lemma_12: these get text-only proof panels — paired full-LaTeX step blocks, no recipe/.asy.*"

**⚠️ This is the shortcut to overturn.** See Group C — the actual pages show **8 of these 9 carry diagrams or are equation/foundation rooms**; only the treatment differs (real diagram vs equation-as-figure vs foundation illustration). None should be a dead text wall.

**Parent 7's palette — `palette.json` (verbatim, OLD model):**
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
**[DeepSeek note — what dies vs survives in this file]:** `groups`, `grey_ink`, `grey_text` are **dead** (the global-station-color mistake). `bg_key`, `map_importance` (1–5 → map ring + guide-line colors), and `map_node_default` are **MAP-side colors and SURVIVE** — they're not station ink. Parent 7's map-color logic also survives: importance-5 rooms glow warm cream `#F5F2E8` (biggest/brightest), importance-3 cool teal, guide-lines inherit the target's importance color.

---

## C — WAVE 1: THE NEWTON TEXT + DeepSeek's figure-fact ruling (8 items, verbatim)

> Source: `quake/principia/` (1729 Motte, Wikisource). Spelling is Newton's/Motte's original; OCR garbles flagged `[sic → …]`. "Ruling" = what the actual page supports; you make the final call.

### 1) `lemma_3` — Lemma III (Section I, p.30)
**Statement (verbatim):** "The same ultimate ratio's are also ratio's of equality, when the breadths AB, BC, DC, &c., of the parallelograms are unequal, and are all diminished in infinitum."
**Proof (verbatim):** "For suppose AF equal to the greatest breadth, and compleat the parallelogram FAaf. This parallelogram will be greater than the difference of the inscrib'd and circumscribed figures; but, because its breadth AF is diminished in infinitum, it will become less than any given rectangle. Q.E.D."
*(Corollaries 1–4 follow: the evanescent parallelograms coincide with the curvilinear figure; likewise the chord-figure and the tangent-figure; so these ultimate figures are curvilinear limits, not rectilinear.)*
**Figure fact:** Geometric — same family as Lemma II (parallelograms under a curve), now with **unequal** breadths plus the bounding parallelogram **FAaf**. No separate plate label printed; shares the Pl.1 Fig.6 figure context.
**DeepSeek ruling:** **FIGURE room** (NOT text-only). Likely 1–2 stations: the unequal-breadth rectangles; the bounding parallelogram FAaf shrinking. A close variant of the gold `lemma_2` figure.

### 2) `lemma_9` — Lemma IX (Section I, p.35)
**Statement (verbatim):** "If a right line AE and a curve line ABC, both given by position, cut each other in a given angle; and to that right line, in another given angle, BD, CE are ordinately applied, meeting the curve in B, C; and the points B and C together approach towards, and meet in, the point A: I say that the areas of the triangles ABD, ACE, will ultimately be one to the other in the duplicate ratio of the sides."
**Proof (verbatim):** "For while the points B, C approach towards the point A, suppose always AD to be produced to the remote points d and e, so as Ad, Ae may be proportional to AD, AE; and the ordinates db, ec, to be drawn parallel to the ordinates DB and EC, and meeting AB and AC produced in b and c. Let the curve Abc be similar to the curve ABC, and draw the right line Ag so as to touch both curves in A, and cut the ordinates DB, EC, db, ec, in F, G, f, g. Then supposing the length Ae to remain the same, let the points B and C meet the point A; and the angle cAg vanishing, the curvilinear areas Abd, Ace will coincide with the rectilinear areas Afd, Age; and therefore (by Lem 5) will be one to other in the duplicate ratio of the sides Ad, Ae. But the areas ABD, ACE are always proportional to these areas; and so the sides AD, AE are to these sides. And therefore the areas ABD, ACE are ultimately one to the other in the duplicate ratio of the sides AD, AE. Q.E.D."
**Figure fact:** Clearly geometric — line AE, curve ABC, ordinates BD/CE, triangles ABD/ACE, tangent Ag, similar curve Abc, points F,G,f,g. **Plate/Fig label NOT in the transcription → verify from the page** (Section-I lemmas sit on Plate 2).
**DeepSeek ruling:** **FIGURE room** (NOT text-only). ~3 steps (the two triangles; the similar auxiliary construction Ad/Ae/Ag; the ultimate duplicate-ratio).

### 3) `lemma_10` — Lemma X (Section I, p.36) — importance 5
**Statement (verbatim):** "The spaces which a body describes by any finite force urging it, whether that force is determined and immutable, or is continually augmented or continually diminished, are in the very beginning of the motion one to the other in the duplicate ratio of the times."
**Proof (verbatim):** "Let the times be represented by the lines AD, AE, and the velocities generated in those times be ordinates DB, EC. The spaces described with these velocities will be as the areas ABD, ACE, described by those ordinates, that is, at the very beginning of the motion (by Lem. 9.) in the duplicate ratio of the times AD, AE."
*(Cor.2–5 + Scholium follow. Cor.4 (verbatim): "And therefore the forces are as the spaces described in the very beginning of the motion directly, and the squares of the times inversly." — a key dynamical seed.)*
**Figure fact:** Geometric — reuses Lemma IX's **area-under-the-velocity-curve** diagram (times AD/AE on the axis, velocities DB/EC as ordinates, areas ABD/ACE = the spaces). Has a diagram.
**DeepSeek ruling:** **FIGURE room** (NOT text-only). The velocity–time area picture; this is the **s ∝ t²** result. Consider a ceiling equation `s ∝ t²` and possibly `F ∝ s / t²` from Cor.4.

### 4) `lemma_12` — Lemma XII (in Section II, p.55) — importance 3
**Statement (verbatim):** "All parallelograms circmscribed [sic → circumscribed] about any conjugate diameters of a given ellipsis or hyperbola are equal among themselves."
**Proof (verbatim, in full):** "This is demonstrated by the writers on the conic sections."
**Figure fact:** Inherently geometric (ellipse, a pair of conjugate diameters, the circumscribed parallelogram) BUT **Newton gives no proof and no figure of its own** — the conjugate-diameter/parallelogram picture appears next to **Prop. X (Pl.4 Fig.1)**, and Lemma XII is used later by **prop_11**.
**DeepSeek ruling (SETTLED — Nir's decision, Option A):** **FIGURE room.** Draw an ellipse + one pair of conjugate diameters + the circumscribed parallelogram. The same conjugate-diameter/parallelogram picture appears next to **Prop. X (Pl.4 Fig.1)** — reuse that drawing here as well (it lives in both rooms; neither loses it). This is a foundational conic fact, stated without proof by Newton, who refers (*"This is demonstrated by the writers on the conic sections"*) to **Apollonius of Perga**'s classic work on conics (~200 BC); it is also provable via affine geometry (stretching a circle into an ellipse preserves area ratios — the constant area is 4ab). The explanation panel may note this in a sentence, so an interested player can google it. **One station** (the statement + the picture — Newton gives no proof steps).

### 5) `prop_2` — Prop. II, Theorem II (Section II, p.42)
**Statement (verbatim):** "Every body, that moves in any curve line described in a plane, and by a radius, drawn to a point either immoveable, or moving forward with an uniform rectilinear motion, describes about that point areas proportional to the times, is urged by a centripetal force directed to that point."
**Proof (verbatim, Case 1):** "For every body that moves in a curve line, is (by law 1.) turned aside from its rectilinear course by the action of some force that impels it. And that force by which the body is turned off from its rectilinear course, and is made to describe, in equal times, the equal least triangles SAB, SBC, SCD, &c. about the immovable point S, (by prop. 40. book 1. elem. and law 2.) acts in the place B, according to the direction of a line parallel to cC, that is, in the direction of the line BS; and in the place C, according to the direction of a line parallel to dD, that is, in the direction of the line CS, &c. And therefore acts always in the direction of lines tending to the immovable point S. Q.E.D." *(Case 2 + Cor.1–2 + Scholium follow.)*
**Figure fact:** Geometric — the **equal-triangles fan** SAB, SBC, SCD about centre S (the converse of Prop. I; same figure family as **prop_1**, Pl.2 Fig.5). Shares Prop. I's figure; no separate plate label printed.
**DeepSeek ruling:** **FIGURE room** (NOT text-only). Reuse the prop_1 triangle-fan figure family. ~2–3 steps. Depends on `law_1` + `prop_1`.

### 6) `prop_4` — Prop. IV, Theorem IV (Section II, p.45) — importance 5
**Statement (verbatim):** "The centripetal forces of bodies, which by equoble [sic → equable] motions describe different circles, tend to the centres of the same circles; and are one to the other, as the squares of the arcs described in equal times applied to [sic → divided by] the radii … of the circles."
**Proof (verbatim):** "These forces tend to the centres of the circles (by prop. 2. and cor. 2. prop. 1) and are one to another as the versed sines of the least arcs described in equal times (by cor. 4. prop. 1.) that is, as the squares of the same arcs applied to the diameters of the circles, (by lem. 7.) and therefore since those arcs are as arcs described in any equal times, and the diameters are as the radii; the forces will be as the squares of an arcs described in the same time applied to the radii of the circles. Q.E.D."
**Cor.1 (verbatim) — THE HEADLINE:** "Therefore, since those arcs are as the velocities of the bodies, the centripetal forces are in a ratio compounded of the duplicate ratio of the velocities directly, and of the simple ratio of the radii inversely." → **F ∝ v²/r.**
**Figure fact:** Essentially a proportional/relational result; the page may carry a small circle/arc sketch, but the heart is the relation. This is the **exact example in the locked doctrine** (Commentaries §3): color `v²` blue, `r` green, `F` orange; in the explanation "the square of the speed" blue, "the distance from the centre" green, "the pull toward the centre" orange.
**DeepSeek ruling:** **EQUATION-AS-FIGURE room.** The equation `F ∝ v²/r` IS the figure (color its terms) + matching-colored explanation; optionally a small arc-on-circle sketch as a second station. Depends on `lemma_7` + `lemma_11`.

### 7) `law_1` — Law I (Axioms, p.19) — FOUNDATION room, Option A (multi-station)
**Statement (verbatim):** "Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd thereon."
**Illustrations (verbatim):** "PRojectiles persevere in their motions, so far as they are not retarded by the resistance of the air, or impelled downwards by the force of gravity. A top, whose parts by their cohesion are perpetually drawn aside from rectilinear motions, does not cease its rotation, otherwise than as it is retarded by the air. The greater bodies of the planets and comets, meeting with less resistance in more free spaces, preserve the motions both progressive and circular for a much longer time."
**Figure fact:** **No printed diagram.** Foundation node.
**DeepSeek ruling + Nir's Q4 (Option A):** **FOUNDATION room, multi-station.** Per Nir: each illustration = its own station (statement-as-figure, drawn-fresh + matching-colored explanation): **(s1) the spinning top**, **(s2) the planets & comets**, **(s3) the projectile**, plus the **law statement** itself as a station. NOT a dead text room.

### 8) `law_2` — Law II (Axioms, p.19) — importance 5
**Statement (verbatim):** "The alteration of motion is ever proportional to the motive force impress'd; and is made in the direction of the right line in which that force is impress'd."
**Illustration (verbatim):** "If any force generates a motion, a double force will generate double the motion, a triple force triple the motion, whether that force be impress'd altogether and at once, or gradually and successively. And this motion (being always directed the same way with the generating force) if the body moved before, is added to or subducted from the former motion …"
**Figure fact:** **No printed diagram.**
**DeepSeek ruling:** **EQUATION-AS-FIGURE / foundation room.** Color the relationship (e.g. *alteration-of-motion* ∝ *force*, same *direction*); explanation uses Newton's own "double force → double motion." Possibly 2 stations: the proportionality, and the direction/composition. The `Δmotion ∝ F` here is what `lemma_10` and `prop_1` cite.

**[DeepSeek summary of Wave 1]:** Of Parent 7's 9 "figure-less" rooms, Wave 1 covers 8 — and **all 8 should have a colored thing to shoot**: `lemma_3/9/10` + `prop_2` are real diagrams; `prop_4` + `law_2` are equation-as-figure; `law_1` is a multi-station foundation room; `lemma_12` is a one-station drawn-fresh FIGURE (ellipse + conjugate diameters + circumscribed parallelogram, reused from Pl.4 Fig.1 per Nir's Option A; no Newton proof — cites Apollonius). The 9th, `prop_15` (Kepler's 3rd, T² ∝ a³), is Wave 2 and is also equation-as-figure.

---

## D — WAVE 2 (ask in ONE batch when ready)

Remaining nodes: `lemma_4, lemma_5, lemma_6, lemma_7, lemma_11` and `prop_1, prop_6, prop_7, prop_11, prop_13, prop_15`. Note Parent 7 **already planned real figures** for all of these except `prop_15` (Kepler's 3rd → equation-as-figure). So Wave 2 is mostly **confirming** the existing figure plans against the page + redoing their color in the local model. Tell me which you want full verbatim text for and I'll fetch them together.
