# 🗝️ QUAKE PARENT 15 — FROZEN WAVE 1 DELIVERABLE (verbatim from Opus)

> Level: `principia_bk1_inverse_square` — Book I, Sections I–III, "First & Last Ratios → the Inverse-Square Law"
> Scope: Supersedes ONLY Parent 7's deficient parts (color model, the "9 figure-less rooms" shortcut, degree/citation/plate slips, the non-geometry-panel data shape). KEEPS Parent 7's concept_graph.json (20 nodes, 28 edges, DAG, validated GREEN), the 20-room set, and the build-order skeleton.

---

## §A — THE THREE LOCKED DECISIONS (data + foundations)

### A.1 — Non-geometry panels: the equation/colored-text IS the figure. ZERO contract change.

There are no "equation rooms" vs "figure rooms" at the data level — only figures. A FigureDecl is one of three flavors, all using the identical recipe → .asy → highlight=k → Stabilo pipeline:

- **DIAGRAM figure** — real geometry ops (segment, circle, ellipse_foci, series, …) + colored elements + per-step heart. [e.g. lemma_2]
- **EQUATION figure** — mostly `label` ops placing the equation's TERMS as separately-colored LaTeX labels, each tagged to a step; optional small geometry sketch as a 2nd station. [e.g. prop_4: F ∝ v²/r]
- **TEXT figure** — `label` ops placing colored phrases of a WORD-ONLY example (no physics sketch — Newton printed none). [e.g. law_1 top]

StepPair.drawing stays mandatory. DrawingBlock.figure_id → FigureDecl → .asy. colors_used is the union of local colors. DeepSeek contract action: NONE. The only build-order note (not a contract change): confirm an .asy made purely of colored label ops + a Stabilo underlay on the current heart bakes cleanly — it is a strict subset of what lemma_2.f1.asy already does, so it should pass prooffig_check and the baker unchanged. I flag it as Gate 0 below.

**Rationale, surfaced not buried:** forking the contract for equation/text panels would create a second code path through the most fragile stage (baker / room_maker / the Stabilo convention) for zero visual gain. The equation-as-figure and colored-text rules already say these are figures, so they are FigureDecls.

### A.2 — lemma_12: one-station DIAGRAM figure — ellipse + one pair of conjugate diameters + the circumscribed parallelogram (the Pl.4 Fig.1 picture, reused here). Newton gives no proof steps ("demonstrated by the writers on the conic sections"), so one station; the explanation notes in one sentence that this is Apollonius' result (also: stretching a circle to an ellipse preserves area ratios, constant area 4ab), so a curious player can chase it. Locked.

### A.3 — Foundation/word-only stations: colored TEXT figures, not drawn scenes (Nir's ruling). law_1 = 4 stations (statement + top + planets/comets + projectile), each a colored-phrase panel. law_2 = 2 stations (proportionality; direction/composition). The general rule multiple printed examples → multiple stations still holds; each example is a colored-text station, never an invented picture.

---

## §B — THE CORRECTED COLOR MODEL (replaces Parent 7's palette entirely)

**DEAD** (delete from palette.json): the `groups` block (path/radius/construction/tangent/swept_area), `grey_ink`, `grey_text`. There is no global station palette and no fixed group names.

**SURVIVES** in palette.json (map-side only, NOT station ink): `bg_key` (#FF00FF background keyout), `map_importance` (1→#4F6D7A … 5→#F5F2E8, the map-ring + guide-line colors), `map_node_default`. Parent 7's map-color logic stands: importance-5 rooms glow warm cream, biggest/brightest; guide-lines inherit target importance color.

**Per-station rules** (the live model):
- **Matching colors (word↔thing):** within one station, each important element gets its own distinct local color (`local_color {name, hex}`); the same words in the paired text carry it via `\textcolor{name}{...}`. Colors are local — the same concept may be a different color, or uncolored, in another station.
- **Uncolored ink = pure black** (light bg) — **never grey** (the .asy uses `rgb(0,0,0)` for off-elements, exactly as the gold lemma_2.f1.asy).
- **Stabilo heart:** only the current step's heart(s) get a bright translucent marker (yellow/green/orange/pink/cyan), laid under the ink, fresh per step, never cumulative (`is_heart: true` + `highlight=k`).

**House color vocabulary** (a suggestion pool for picking distinct local colors per station — NOT a global palette; reuse freely across stations since colors are local): blue #1E6FE0, green #00A35A, orange #E8770A, purple #8E24AA, red/magenta #D81B60, teal #00897B, indigo #3949AB, brown #6D4C41. Stabilo pool: yellow #FFE000, green #00E676, orange #FF6F00, pink #FF4081, cyan #00E5FF.

---

## §C — FACTUAL FIXES (§2.3)

**Degree corrections** (prose only — JSON edges already correct):
- `lemma_7` is **degree 6** (incoming: lemma_6, lemma_9, lemma_11, prop_4, prop_11, prop_13) — Parent 7 wrote 5. ⇒ 6 doors.
- `prop_11` is **degree 4** (incoming: prop_15; outgoing: prop_6, lemma_12, lemma_7) — Parent 7 wrote 5. ⇒ 4 doors.

**Citation labels — VERIFIED against the Motte page** (use these verbatim phrases as edge labels):
- `prop_1`   : "by law 1" · "by Cor. 1. of the laws" · "by cor. 4. lem. 5" · (Euclid: "prop. 40. book 1. elem.")
- `prop_2`   : "by law 1." · "by prop. 40. book 1. elem. and law 2."
- `prop_4`   : "by prop. 2." · "by cor. 2. prop. 1" · "by cor. 4. prop. 1." · "by lem. 7."
- `lemma_4`  : "by Lem. 3."
- `lemma_7`  : "by the preceding lemma" (= Lemma VI)
- `lemma_10` : "by Lem. 9."
- `lemma_11` : "by Lem. 1."
- `prop_6`   : "by cor. 4. prop. 1" · "by cor. 2 and 3. lem. 2" · "by corol. 4. lem. 10"
- `prop_7`   : "cor. 3. prop. 7" (self-corollary ref in proof; flag — may be a Motte typo)
- `prop_11`  : "(by lem. 12)" · "by cor. 3. prop. 7"
- `prop_13`  : "(by lem. 13.)" · "(by cor. 2 lem. 7.)" · (final force: "by cor. 1. prop. 6")
- `prop_15`  : "by cor. prop. 14"

`lemma_12` proof phrase (for the explanation panel, verbatim): "This is demonstrated by the writers on the conic sections."

Two items to flag for DeepSeek verification downstream: (1) prop_7's in-proof "cor. 3. prop. 7" looks self-referential — likely a Motte OCR/typo for another prop; confirm from a wider page range. (2) prop_13/prop_11 cite prop_14 ("cor. prop. 14") and lem. 13 — prop_14/lemma_13 are outside our 20-node set; the citations are real but their targets live in a later section. Keep them as labeled edges only if both endpoints are in-level; otherwise record as external_citation in the provenance sidecar (build-world only) and DO NOT add a dangling edge (the ID-spine build fails on dangling endpoints). This is a real topology question — surfaced, not buried; my recommendation is external_citation, Nir/DeepSeek confirm.

Plate/Fig numbers (Parent 7's were tentative; these match the page text where a label was printed — still confirmed downstream by overlay-diff):
- lemma_2 Pl.1 Fig.6 · lemma_3 (shares Pl.1 Fig.6 context) · lemma_4 Pl.1 Fig.7 · lemma_5 Pl.2 Fig.1 · lemma_6 Pl.2 Fig.1 · lemma_7 Pl.2 Fig.1 · lemma_9 Pl.2 (verify fig#) · lemma_10 (reuses Lem. IX area) · lemma_11 Pl.2 Fig.4 · lemma_12 (reuses Pl.4 Fig.1) · prop_1 Pl.2 Fig.5 · prop_2 (shares Prop. I figure family) · prop_4 (no printed fig — equation) · prop_6 Pl.3 Fig.2 · prop_7 Pl.3 Fig.3 · prop_11 Pl.4 Fig.2 · prop_13 Pl.5 Fig.3 · prop_15 (no printed fig — equation).

---

## 1 — Corrected `palette.json` (map-side only)

```json
{
  "schema_version": "1.0",
  "pack_id": "principia",
  "bg_key": "#FF00FF",
  "map_importance": {
    "1": "#4F6D7A",
    "2": "#3FA796",
    "3": "#E6B800",
    "4": "#E8743B",
    "5": "#F5F2E8"
  },
  "map_node_default": "#9AA0A6"
}
```

## 2 — Corrected `concept_graph.json` (same topology; verified labels; degree fixes are prose-level only — JSON was already correct)

```json
{
  "schema_version": "1.0",
  "level_id": "principia_bk1_inverse_square",
  "title": "Book I, Sections I–III — First & Last Ratios to the Inverse-Square Law",
  "edition": "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Sections I–III + Axioms (Laws).",
  "seed": 1729001,
  "nodes": [
    { "id": "law_1",    "name": "Law I — Inertia",                         "kind": "law",         "importance": 5, "pages": ["19"], "summary": "A body keeps rest or uniform straight motion unless a force changes it.", "tags": ["axiom","inertia"] },
    { "id": "law_2",    "name": "Law II — Force and Change of Motion",     "kind": "law",         "importance": 5, "pages": ["19"], "summary": "Change of motion is proportional to the impressed force and in its direction.", "tags": ["axiom","force"] },
    { "id": "lemma_2",  "name": "Lemma II — Inscribed/Circumscribed",      "kind": "lemma",       "importance": 4, "pages": ["29"], "summary": "Inscribed and circumscribed figures become ultimately equal as bases shrink.", "tags": ["limits"] },
    { "id": "lemma_3",  "name": "Lemma III — Unequal Breadths",            "kind": "lemma",       "importance": 3, "pages": ["30"], "summary": "Same ultimate equality holds for unequal diminishing breadths.", "tags": ["limits"] },
    { "id": "lemma_4",  "name": "Lemma IV — Ratio of Two Figures",         "kind": "lemma",       "importance": 4, "pages": ["31"], "summary": "Two figures whose parallelograms share an ultimate ratio are in that ratio.", "tags": ["limits"] },
    { "id": "lemma_5",  "name": "Lemma V — Similar Figures",               "kind": "lemma",       "importance": 3, "pages": ["32"], "summary": "Homologous sides of similar figures are proportional; areas in duplicate ratio.", "tags": ["similarity"] },
    { "id": "lemma_6",  "name": "Lemma VI — Vanishing Angle",              "kind": "lemma",       "importance": 4, "pages": ["32"], "summary": "The angle between chord and tangent vanishes as the points meet.", "tags": ["limits","tangent"] },
    { "id": "lemma_7",  "name": "Lemma VII — Arc, Chord, Tangent",         "kind": "lemma",       "importance": 5, "pages": ["33"], "summary": "Arc, chord and tangent are ultimately in a ratio of equality.", "tags": ["limits","tangent"] },
    { "id": "lemma_9",  "name": "Lemma IX — Triangles Duplicate Ratio",    "kind": "lemma",       "importance": 4, "pages": ["35"], "summary": "Areas of the limiting triangles are as the duplicate ratio of the sides.", "tags": ["limits"] },
    { "id": "lemma_10", "name": "Lemma X — Spaces as Square of Times",     "kind": "lemma",       "importance": 5, "pages": ["36"], "summary": "Spaces from any finite force are initially as the square of the times.", "tags": ["limits","dynamics"] },
    { "id": "lemma_11", "name": "Lemma XI — Evanescent Subtense",          "kind": "lemma",       "importance": 5, "pages": ["37"], "summary": "The subtense of the contact angle is ultimately as the square of the arc's subtense.", "tags": ["limits","curvature"] },
    { "id": "lemma_12", "name": "Lemma XII — Conjugate Parallelograms",    "kind": "lemma",       "importance": 3, "pages": ["55"], "summary": "Parallelograms about conjugate diameters of an ellipse/hyperbola are all equal.", "tags": ["conics"] },
    { "id": "prop_1",   "name": "Prop. I — Areas Proportional to Times",   "kind": "proposition","importance": 5, "pages": ["40"], "summary": "A central force makes radii sweep areas proportional to the times.", "tags": ["dynamics","areas"] },
    { "id": "prop_2",   "name": "Prop. II — Converse of Areas",            "kind": "proposition","importance": 4, "pages": ["42"], "summary": "Equal areas in equal times imply a centripetal force to that point.", "tags": ["dynamics","areas"] },
    { "id": "prop_4",   "name": "Prop. IV — Circular Centripetal Force",   "kind": "proposition","importance": 5, "pages": ["45"], "summary": "For circular motion the centripetal force is as v squared over the radius.", "tags": ["dynamics","circle"] },
    { "id": "prop_6",   "name": "Prop. VI — Force Measure",                "kind": "proposition","importance": 5, "pages": ["48"], "summary": "Centripetal force is as the versed sine directly and the square of the time inversely.", "tags": ["dynamics","force"] },
    { "id": "prop_7",   "name": "Prop. VII — Force to a Point on a Circle","kind": "proposition","importance": 3, "pages": ["50"], "summary": "Finds the law of force for a body on a circle directed to any given point.", "tags": ["dynamics","circle"] },
    { "id": "prop_11",  "name": "Prop. XI — Ellipse, Force to Focus",      "kind": "proposition","importance": 5, "pages": ["56"], "summary": "For an ellipse the force to the focus is reciprocally as the square of the distance.", "tags": ["dynamics","conics","inverse-square"] },
    { "id": "prop_13",  "name": "Prop. XIII — Parabola, Force to Focus",   "kind": "proposition","importance": 4, "pages": ["61"], "summary": "For a parabola the force to the focus is also as the inverse square of the distance.", "tags": ["dynamics","conics"] },
    { "id": "prop_15",  "name": "Prop. XV — Kepler's Third Law",           "kind": "proposition","importance": 5, "pages": ["63"], "summary": "Periodic times in ellipses are as the 3/2 power of the greater axes.", "tags": ["dynamics","kepler"] }
  ],
  "edges": [
    { "id": "edge.lemma_3.to.lemma_2",   "source": "lemma_3",  "target": "lemma_2",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 2" },
    { "id": "edge.lemma_4.to.lemma_3",   "source": "lemma_4",  "target": "lemma_3",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 3." },
    { "id": "edge.lemma_7.to.lemma_6",   "source": "lemma_7",  "target": "lemma_6",  "kind": "depends_on", "weight": 1.0, "label": "by the preceding lemma" },
    { "id": "edge.lemma_9.to.lemma_5",   "source": "lemma_9",  "target": "lemma_5",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 5" },
    { "id": "edge.lemma_10.to.lemma_9",  "source": "lemma_10", "target": "lemma_9",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 9." },
    { "id": "edge.lemma_11.to.lemma_6",  "source": "lemma_11", "target": "lemma_6",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 1" },
    { "id": "edge.lemma_11.to.lemma_7",  "source": "lemma_11", "target": "lemma_7",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 7" },
    { "id": "edge.prop_1.to.law_1",      "source": "prop_1",   "target": "law_1",    "kind": "depends_on", "weight": 1.0, "label": "by law 1" },
    { "id": "edge.prop_1.to.law_2",      "source": "prop_1",   "target": "law_2",    "kind": "depends_on", "weight": 1.0, "label": "by Cor. 1. of the laws" },
    { "id": "edge.prop_1.to.lemma_5",    "source": "prop_1",   "target": "lemma_5",  "kind": "depends_on", "weight": 1.0, "label": "by cor. 4. lem. 5" },
    { "id": "edge.prop_2.to.law_1",      "source": "prop_2",   "target": "law_1",    "kind": "depends_on", "weight": 1.0, "label": "by law 1." },
    { "id": "edge.prop_2.to.law_2",      "source": "prop_2",   "target": "law_2",    "kind": "depends_on", "weight": 1.0, "label": "by prop. 40. book 1. elem. and law 2." },
    { "id": "edge.prop_2.to.prop_1",     "source": "prop_2",   "target": "prop_1",   "kind": "depends_on", "weight": 1.0, "label": "converse of Prop. I" },
    { "id": "edge.prop_4.to.prop_2",     "source": "prop_4",   "target": "prop_2",   "kind": "depends_on", "weight": 1.0, "label": "by prop. 2." },
    { "id": "edge.prop_4.to.prop_1",     "source": "prop_4",   "target": "prop_1",   "kind": "depends_on", "weight": 1.0, "label": "by cor. 4. prop. 1." },
    { "id": "edge.prop_4.to.lemma_7",    "source": "prop_4",   "target": "lemma_7",  "kind": "depends_on", "weight": 1.0, "label": "by lem. 7." },
    { "id": "edge.prop_6.to.prop_1",     "source": "prop_6",   "target": "prop_1",   "kind": "depends_on", "weight": 1.0, "label": "by cor. 4. prop. 1" },
    { "id": "edge.prop_6.to.lemma_2",    "source": "prop_6",   "target": "lemma_2",  "kind": "depends_on", "weight": 1.0, "label": "by cor. 2 and 3. lem. 2" },
    { "id": "edge.prop_6.to.lemma_10",   "source": "prop_6",   "target": "lemma_10", "kind": "depends_on", "weight": 1.0, "label": "by corol. 4. lem. 10" },
    { "id": "edge.prop_7.to.prop_6",     "source": "prop_7",   "target": "prop_6",   "kind": "depends_on", "weight": 1.0, "label": "by Prop. VI construction" },
    { "id": "edge.prop_11.to.prop_6",    "source": "prop_11",  "target": "prop_6",   "kind": "depends_on", "weight": 1.0, "label": "by cor. 3. prop. 7 / prop. 6" },
    { "id": "edge.prop_11.to.lemma_7",   "source": "prop_11",  "target": "lemma_7",  "kind": "depends_on", "weight": 1.0, "label": "by Lem. 7" },
    { "id": "edge.prop_11.to.lemma_12",  "source": "prop_11",  "target": "lemma_12", "kind": "depends_on", "weight": 1.0, "label": "by lem. 12" },
    { "id": "edge.prop_13.to.lemma_7",   "source": "prop_13",  "target": "lemma_7",  "kind": "depends_on", "weight": 1.0, "label": "by cor. 2 lem. 7." },
    { "id": "edge.prop_13.to.prop_6",    "source": "prop_13",  "target": "prop_6",   "kind": "depends_on", "weight": 1.0, "label": "by cor. 1. prop. 6" },
    { "id": "edge.prop_15.to.prop_11",   "source": "prop_15",  "target": "prop_11",  "kind": "depends_on", "weight": 1.0, "label": "by cor. prop. 14 (via Prop. XI)" },
    { "id": "edge.prop_15.to.prop_4",    "source": "prop_15",  "target": "prop_4",   "kind": "depends_on", "weight": 1.0, "label": "sesquiplicate ratio result" },
    { "id": "edge.prop_13.to.prop_11",   "source": "prop_13",  "target": "prop_11",  "kind": "depends_on", "label": "retaining the preceding construction" }
  ]
}
```

Note (surfaced): I kept exactly Parent 7's 28-edge topology and all endpoints in-level. The two genuinely-external citations (prop. 14, lem. 13) are not added as edges (they'd dangle and fail the ID-spine build); record them as external_citation in the build-world provenance sidecar. Degree truths after this graph: lemma_7 = 6 incoming, prop_11 = 4 (3 out + 1 in). Use these for door counts.

---

## 3 — STATION MAP, ROOMS 1–10

Notation per step: gloss — element → colorname(#hex); ♥ = Stabilo heart of that step.

### lemma_2 · DIAGRAM · 3 step-pairs · (GOLD — already built by Parent 13; listed for completeness)

- **s1** Curvilinear figure: curve acE → curveblue(#1E6FE0) ♥; base AE → basegreen(#00A35A); side Aa → sideorange(#E8770A).
- **s2** Inscribed parallelograms Ab,Bc,Cd → inscpurple(#8E24AA) ♥.
- **s3** Circumscribed parallelograms → circred(#D81B60) ♥; excess = rectangle ABla.
- **colors_used:** curveblue, basegreen, sideorange, inscpurple, circred
- **ceiling:** \lim_{AB\to0}(\text{circ}-\text{insc})=ABla\to0 · \text{insc}=\text{circ}=\text{area}
- **final_pair_id:** lemma_2.s3

### lemma_3 · DIAGRAM · 2 step-pairs

- **s1** Unequal-breadth rectangles under the curve: the stepped rectangles → stepblue(#1E6FE0) ♥; baseline AF..AE → basegreen(#00A35A).
- **s2** Bounding parallelogram FAaf → boundred(#D81B60) ♥ shrinking as breadth AF → 0; greatest breadth AF → widthorange(#E8770A).
- **colors_used:** stepblue, basegreen, boundred, widthorange
- **ceiling:** FAaf > (\text{circ}-\text{insc}) · AF\to0 \Rightarrow FAaf\to0
- **final_pair_id:** lemma_3.s2

### lemma_4 · DIAGRAM · 3 step-pairs · Pl.1 Fig.7

- **s1** First figure AacE with its rectangle rank → figaviolet(#8E24AA) ♥.
- **s2** Second figure PprT with its rectangle rank → figbteal(#00897B) ♥.
- **s3** Correspondence lines pairing rank-to-rank → corrorange(#E8770A) ♥; the shared ultimate ratio.
- **colors_used:** figaviolet, figbteal, corrorange
- **ceiling:** \frac{\Box_i^{A}}{\Box_i^{P}}\to k \;\Rightarrow\; \frac{AacE}{PprT}=k (by Lem. 3)
- **final_pair_id:** lemma_4.s3

### lemma_5 · DIAGRAM · 2 step-pairs · Pl.2 Fig.1

- **s1** Two similar figures side by side; figure 1 → simblue(#1E6FE0), figure 2 → simgreen(#00A35A); homologous boundary ♥ (the pair together).
- **s2** Marked homologous sides → sideorange(#E8770A) ♥; areas in duplicate ratio.
- **colors_used:** simblue, simgreen, sideorange
- **ceiling:** \text{sides} \propto \text{homologous} · \text{areas} \propto (\text{side})^2
- **final_pair_id:** lemma_5.s2

### lemma_6 · DIAGRAM · 3 step-pairs · Pl.2 Fig.1

- **s1** Arc ACB → arcblue(#1E6FE0) ♥.
- **s2** Chord AB → chordgreen(#00A35A) ♥.
- **s3** Tangent AD → tanorange(#E8770A); contact angle BAD → anglered(#D81B60) ♥ vanishing as B→A.
- **colors_used:** arcblue, chordgreen, tanorange, anglered
- **ceiling:** B\to A \;\Rightarrow\; \angle BAD \to 0
- **final_pair_id:** lemma_6.s3

### lemma_7 · DIAGRAM · 3 step-pairs · Pl.2 Fig.1 · 6 doors (degree 6)

- **s1** Arc ACB → arcblue(#1E6FE0) ♥; chord AB, tangent AD.
- **s2** Auxiliary similar arc Acb via produced points b,d; secant BD & parallel bd → auxpurple(#8E24AA) ♥.
- **s3** Coincidence at A: arc, chord, tangent → equalteal(#00897B) ♥ acquire ratio of equality.
- **colors_used:** arcblue, auxpurple, equalteal
- **ceiling:** \text{arc}:\text{chord}:\text{tangent}\to 1:1:1
- **final_pair_id:** lemma_7.s3

### lemma_9 · DIAGRAM · 3 step-pairs · Pl.2 (verify fig#)

- **s1** Line AE → lineblue(#1E6FE0), curve ABC → curvegreen(#00A35A); ordinates BD, CE → ordorange(#E8770A) ♥; triangles ABD, ACE.
- **s2** Auxiliary: produced Ad,Ae ∝ AD,AE; similar curve Abc; tangent Ag → auxpurple(#8E24AA) ♥; points F,G,f,g.
- **s3** Vanishing cAg: rectilinear areas Afd, Age → arearred(#D81B60) ♥; duplicate ratio of sides.
- **colors_used:** lineblue, curvegreen, ordorange, auxpurple, arearred
- **ceiling:** \triangle ABD : \triangle ACE \to AD^2 : AE^2
- **final_pair_id:** lemma_9.s3

### lemma_10 · DIAGRAM · 2 step-pairs · (reuses Lem. IX area picture) · importance 5

- **s1** Time axis AD,AE → timeblue(#1E6FE0); velocity ordinates DB,EC → velgreen(#00A35A) ♥.
- **s2** Areas ABD,ACE → spacered(#D81B60) ♥ = the spaces; ultimately as the square of the times (by Lem. 9).
- **colors_used:** timeblue, velgreen, spacered
- **ceiling:** s \propto t^2 · F \propto \dfrac{s}{t^2} (Cor. 4)
- **final_pair_id:** lemma_10.s2

### law_1 · TEXT (colored, no drawn scene per Nir) · 4 step-pairs · importance 5 · Axioms p.19

- **s1** (statement) "Every body perseveres in its state of rest→restblue(#1E6FE0), or of uniform motion in a right line→motiongreen(#00A35A), unless compelled to change that state by forces impress'd→forceorange(#E8770A)" ♥ = forceorange phrase.
- **s2** (top) "A top→topblue(#1E6FE0) does not cease its rotation, otherwise than as it is retarded by the air→dragred(#D81B60)" ♥ = topblue.
- **s3** (planets/comets) "The greater bodies of the planets and comets→planetpurple(#8E24AA), meeting less resistance in more free spaces→freeteal(#00897B), preserve their motions for a much longer time" ♥ = planetpurple.
- **s4** (projectile) "Projectiles→projblue(#1E6FE0) persevere, so far as not retarded by the resistance of the air→dragred(#D81B60), or impell'd downwards by gravity→gravorange(#E8770A)" ♥ = projblue.
- **colors_used:** restblue, motiongreen, forceorange, topblue, dragred, planetpurple, freeteal, projblue, gravorange
- **ceiling:** \text{no force} \Rightarrow \text{no change of motion} (surfaced: if this is still too modern, use the word-form; DeepSeek's call with Nir)
- **final_pair_id:** law_1.s4

### law_2 · EQUATION/TEXT · 2 step-pairs · importance 5 · Axioms p.19

- **s1** (proportionality) equation-as-figure: \text{(alteration of motion)}→motionblue(#1E6FE0) \;\propto\; \text{(motive force)}→forceorange(#E8770A) ♥ = whole proportion (heart on the ∝-bearing motionblue term). Explanation: "a double force→forceorange will generate double the motion→motionblue."
- **s2** (direction/composition) "made in the direction of the right line→dirgreen(#00A35A) in which the force is impress'd"; added to or subducted from former motion→motionblue ♥ = dirgreen.
- **colors_used:** motionblue, forceorange, dirgreen
- **ceiling:** \Delta(\text{motion}) \propto F · \Delta(\text{motion}) \parallel F
- **final_pair_id:** law_2.s2

---

End Wave 1. Wave 2 (rooms 11–20: lemma_11, lemma_12, prop_1, prop_2, prop_4, prop_6, prop_7, prop_11, prop_13, prop_15) is ready — sending it next message so context survives.
