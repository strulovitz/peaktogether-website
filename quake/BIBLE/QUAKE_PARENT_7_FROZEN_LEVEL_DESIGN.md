# QUAKE — PARENT 7 FROZEN LEVEL DESIGN (VERBATIM)

> **HOLY / VERBATIM.** This is Parent 7's (Claude Opus 4.8) complete deliverable, saved word-for-word as-is at Nir's instruction. The only non-Opus text is this header block.
>
> **DeepSeek provenance + QA note (not Opus's words):** Saved June 28, 2026. DeepSeek validated the buildable artifacts against the real Second Canon contracts before saving: the **concept_graph.json** below passes §4.2 (20 nodes — unique ids, importance 1–5; 28 edges — every `edge.id == "edge."+source+".to."+target`, all endpoints exist, no self-loops; valid DAG, connected, `extra="forbid"`-clean), and the **palette.json** passes §3.A.7 (reserved keys, `map_importance` keys "1".."5", valid hex). Three honest blemishes, none build-breaking: (a) two cosmetic degree miscounts in the prose of PART 6 — *"lemma_7 (degree 5)"* is actually **degree 6**, *"prop_11 (degree 5)"* is actually **degree 4** (the pipeline derives door-count from the correct edges, so the build is unaffected); (b) the verbatim citation `label` phrases in PART 2 are Parent 7's reconstructions, to be confirmed by the CITATION-AI pass + Nir's eyeball (Parent 7 flagged this himself); (c) figure plate/fig numbers are tentative, confirmed downstream via overlay-diff. The build (Phase A onward) was deliberately NOT started — Parent 7 deferred the go/no-go to Nir.

---

Wonderful — 18–20 rooms it is. A brutal, real crossing-test with the full arc of Newton's foundational mechanics. Let's build something serious. 🔥📖

I'll design 20 rooms spanning the true spine of Book 1:

- 8 toolbox lemmas — Section I (limits)
- → 6 props, Kepler's 2nd — Section II (centripetal force)
- → 6 props/lemmas, the famous result — Section III (inverse-square)

The many-to-many citation pattern (Section II & III props each reaching back into multiple Section I lemmas) is what guarantees a richly non-planar graph → real bridges and underpasses. Here is the complete design.

## 🗝️ QUAKE — FIRST REAL PRINCIPIA LEVEL (Parent 7 Deliverable)

Level: "First and Last Ratios → The Inverse-Square Law" — Book 1, Sections I–III. 20 rooms. Designed against the real Second Canon §4.2 / §3.A.4 / §3.A.7 contracts.

## PART 1 — LEVEL PLAN

```
level_id:  principia_bk1_inverse_square
edition:   "Isaac Newton, The Mathematical Principles of Natural Philosophy, trans. Andrew Motte (1729); Wikisource transcription."
seed:      1729001
book:      Book I — The Motion of Bodies
sections:  Section I (Lemmas), Section II (Centripetal Forces), Section III (Eccentric Conic Sections)
rooms:     20
```

The 20 nodes (the dependency climb), with page labels from the DIGEST/Motte:

```
TOOLBOX (Section I) — simple, compile-safe figures, baked first:
  lemma_2   Lemma II    p.30   imp 5  (inscribed/circumscribed rects → exhaustion)   FIG
  lemma_3   Lemma III   p.30   imp 3  (unequal breadths, same limit)                 no fig
  lemma_4   Lemma IV    p.31   imp 4  (whole figures share the ultimate ratio)       FIG
  lemma_5   Lemma V     p.32   imp 3  (similar figures: areas as square of sides)    FIG
  lemma_6   Lemma VI    p.32   imp 4  (chord-tangent angle vanishes)                 FIG
  lemma_7   Lemma VII   p.33   imp 5  (arc ≈ chord ≈ tangent at the limit)           FIG
  lemma_9   Lemma IX    p.35   imp 3  (triangle areas ~ duplicate ratio of sides)    no fig
  lemma_10  Lemma X     p.36   imp 5  (spaces as square of times, s ∝ t²)            no fig
  lemma_11  Lemma XI    p.37   imp 5  (evanescent subtense ~ duplicate ratio of arc) FIG

LAW (Axioms) — the dynamical input:
  law_1     Law I       p.19   imp 4  (inertia)                                      no fig
  law_2     Law II      p.19   imp 5  (change of motion ∝ impressed force)           no fig

CENTRIPETAL FORCE (Section II):
  prop_1    Prop. I     p.40   imp 5  (radii sweep equal areas in equal times)       FIG
  prop_2    Prop. II    p.42   imp 4  (converse: equal areas ⟹ centripetal force)   no fig
  prop_4    Prop. IV    p.45   imp 5  (uniform circular: force as v²/r)              no fig
  prop_6    Prop. VI    p.48   imp 5  (force as versed-sine / time², the key tool)   FIG
  prop_7    Prop. VII   p.50   imp 3  (circle, force to any point: 1/dist⁵)          FIG

INVERSE-SQUARE (Section III):
  lemma_12  Lemma XII   p.55   imp 3  (circumscribed parallelograms of conic equal)  no fig
  prop_11   Prop. XI    p.56   imp 5  (ELLIPSE, force to focus: 1/dist²) ★ THE RESULT FIG (conic)
  prop_13   Prop. XIII  p.61   imp 4  (PARABOLA, force to focus: 1/dist²)            FIG (conic)
  prop_15   Prop. XV    p.63   imp 5  (Kepler's 3rd: T ∝ a^(3/2))                    no fig
```

Why this shape gives crossings: Section II/III props each cite several Section I lemmas (e.g. prop_6 cites Lemmas VII, X, XI; prop_11 cites Lemma XII + Prop VI). These long back-edges fan across the force-directed layout and must cross each other — that is the bridge/underpass test. 11 rooms have figures (front-loaded simple → back-loaded conic); 9 are figure-less (text-only proof panels — also a real test of the room maker with no-figure rooms).

## PART 2 — CONCEPT GRAPH SPECIFICATION

Here is the complete concept_graph.json, valid against §4.2 (unique ids, DAG, edge.id == "edge."+source+".to."+target, no self-loops). Edge direction = depends_on: source depends on target. Verbatim citation phrases go in label.

```json
{
  "schema_version": "1.0",
  "level_id": "principia_bk1_inverse_square",
  "title": "Book I, Sections I–III — From First and Last Ratios to the Inverse-Square Law",
  "edition": "Isaac Newton, The Mathematical Principles of Natural Philosophy, trans. Andrew Motte (1729); Wikisource transcription.",
  "seed": 1729001,
  "nodes": [
    {"id":"lemma_2","name":"Lemma II","kind":"lemma","importance":5,"pages":["30"],"summary":"Inscribed and circumscribed rectangles under a curve have an ultimate ratio of equality.","tags":["limits","exhaustion"]},
    {"id":"lemma_3","name":"Lemma III","kind":"lemma","importance":3,"pages":["30"],"summary":"The same ultimate equality holds even when the rectangle breadths are unequal.","tags":["limits"]},
    {"id":"lemma_4","name":"Lemma IV","kind":"lemma","importance":4,"pages":["31"],"summary":"If corresponding parts share an ultimate ratio, the whole figures share it too.","tags":["limits"]},
    {"id":"lemma_5","name":"Lemma V","kind":"lemma","importance":3,"pages":["32"],"summary":"In similar figures, areas are as the squares of homologous sides.","tags":["similarity"]},
    {"id":"lemma_6","name":"Lemma VI","kind":"lemma","importance":4,"pages":["32"],"summary":"The angle between chord and tangent vanishes as the arc shrinks.","tags":["limits","tangent"]},
    {"id":"lemma_7","name":"Lemma VII","kind":"lemma","importance":5,"pages":["33"],"summary":"Arc, chord, and tangent become ultimately equal as the arc vanishes.","tags":["limits","tangent"]},
    {"id":"lemma_9","name":"Lemma IX","kind":"lemma","importance":3,"pages":["35"],"summary":"Areas of the limiting triangles are in the duplicate ratio of their sides.","tags":["limits"]},
    {"id":"lemma_10","name":"Lemma X","kind":"lemma","importance":5,"pages":["36"],"summary":"Spaces described from rest under a finite force are as the squares of the times.","tags":["dynamics","s-t-squared"]},
    {"id":"lemma_11","name":"Lemma XI","kind":"lemma","importance":5,"pages":["37"],"summary":"The evanescent subtense of contact is as the square of the subtense of the arc.","tags":["limits","curvature"]},
    {"id":"law_1","name":"Law I","kind":"law","importance":4,"pages":["19"],"summary":"A body perseveres in rest or uniform straight motion unless compelled to change.","tags":["axiom","inertia"]},
    {"id":"law_2","name":"Law II","kind":"law","importance":5,"pages":["19"],"summary":"Change of motion is proportional to the impressed force and in its direction.","tags":["axiom","force"]},
    {"id":"prop_1","name":"Prop. I, Theorem I","kind":"proposition","importance":5,"pages":["40","41"],"summary":"Radii to an immovable centre sweep equal areas in equal times (Kepler's 2nd law).","tags":["kepler-2","centripetal"]},
    {"id":"prop_2","name":"Prop. II, Theorem II","kind":"proposition","importance":4,"pages":["42"],"summary":"Conversely, a body sweeping equal areas is urged by a centripetal force to that centre.","tags":["centripetal","converse"]},
    {"id":"prop_4","name":"Prop. IV, Theorem IV","kind":"proposition","importance":5,"pages":["45"],"summary":"In uniform circular motion the centripetal force is as the square of the velocity over the radius.","tags":["circular","v-squared"]},
    {"id":"prop_6","name":"Prop. VI, Theorem V","kind":"proposition","importance":5,"pages":["48"],"summary":"Centripetal force is as the versed sine of the nascent arc directly and the square of the time inversely.","tags":["centripetal","force-measure"]},
    {"id":"prop_7","name":"Prop. VII, Problem II","kind":"proposition","importance":3,"pages":["50"],"summary":"For a body in a circle with force to any given point, the force is reciprocally as the fifth power of the distance.","tags":["circular","force-law"]},
    {"id":"lemma_12","name":"Lemma XII","kind":"lemma","importance":3,"pages":["55"],"summary":"All parallelograms circumscribed about conjugate diameters of an ellipse are equal.","tags":["conic","ellipse"]},
    {"id":"prop_11","name":"Prop. XI, Problem VI","kind":"proposition","importance":5,"pages":["56","57"],"summary":"A body in an ellipse with force to the focus is urged by a force reciprocally as the square of the distance.","tags":["inverse-square","ellipse","headline"]},
    {"id":"prop_13","name":"Prop. XIII, Problem VIII","kind":"proposition","importance":4,"pages":["61"],"summary":"A body in a parabola with force to the focus obeys the same inverse-square law.","tags":["inverse-square","parabola"]},
    {"id":"prop_15","name":"Prop. XV, Theorem VII","kind":"proposition","importance":5,"pages":["63"],"summary":"Periodic times in ellipses are as the 3/2 power of the major axes (Kepler's 3rd law).","tags":["kepler-3","period"]}
  ],
  "edges": [
    {"id":"edge.lemma_3.to.lemma_2","source":"lemma_3","target":"lemma_2","kind":"depends_on","weight":1.0,"label":"as in the foregoing Lemma"},
    {"id":"edge.lemma_4.to.lemma_2","source":"lemma_4","target":"lemma_2","kind":"depends_on","weight":1.0,"label":"by Lem. II"},
    {"id":"edge.lemma_4.to.lemma_3","source":"lemma_4","target":"lemma_3","kind":"depends_on","weight":1.0,"label":"by Lem. III"},
    {"id":"edge.lemma_7.to.lemma_6","source":"lemma_7","target":"lemma_6","kind":"depends_on","weight":1.0,"label":"by Lem. VI"},
    {"id":"edge.lemma_9.to.lemma_7","source":"lemma_9","target":"lemma_7","kind":"depends_on","weight":1.0,"label":"by Lem. VII"},
    {"id":"edge.lemma_9.to.lemma_5","source":"lemma_9","target":"lemma_5","kind":"depends_on","weight":1.0,"label":"by Lem. V"},
    {"id":"edge.lemma_11.to.lemma_6","source":"lemma_11","target":"lemma_6","kind":"depends_on","weight":1.0,"label":"by Lem. VI"},
    {"id":"edge.lemma_11.to.lemma_7","source":"lemma_11","target":"lemma_7","kind":"depends_on","weight":1.0,"label":"by Lem. VII"},
    {"id":"edge.lemma_10.to.law_2","source":"lemma_10","target":"law_2","kind":"depends_on","weight":1.0,"label":"by the second Law of Motion"},
    {"id":"edge.lemma_10.to.lemma_9","source":"lemma_10","target":"lemma_9","kind":"depends_on","weight":1.0,"label":"by Lem. IX"},
    {"id":"edge.prop_1.to.law_1","source":"prop_1","target":"law_1","kind":"depends_on","weight":1.0,"label":"by the first Law"},
    {"id":"edge.prop_1.to.law_2","source":"prop_1","target":"law_2","kind":"depends_on","weight":1.0,"label":"by the second Law"},
    {"id":"edge.prop_1.to.lemma_3","source":"prop_1","target":"lemma_3","kind":"depends_on","weight":1.0,"label":"by Cor. of Lem. III"},
    {"id":"edge.prop_2.to.prop_1","source":"prop_2","target":"prop_1","kind":"depends_on","weight":1.0,"label":"converse of Prop. I"},
    {"id":"edge.prop_2.to.law_1","source":"prop_2","target":"law_1","kind":"depends_on","weight":1.0,"label":"by the first Law"},
    {"id":"edge.prop_4.to.lemma_7","source":"prop_4","target":"lemma_7","kind":"depends_on","weight":1.0,"label":"by Lem. VII"},
    {"id":"edge.prop_4.to.lemma_11","source":"prop_4","target":"lemma_11","kind":"depends_on","weight":1.0,"label":"by Lem. XI"},
    {"id":"edge.prop_6.to.prop_1","source":"prop_6","target":"prop_1","kind":"depends_on","weight":1.0,"label":"by Prop. I"},
    {"id":"edge.prop_6.to.lemma_10","source":"prop_6","target":"lemma_10","kind":"depends_on","weight":1.0,"label":"by Lem. X"},
    {"id":"edge.prop_6.to.lemma_11","source":"prop_6","target":"lemma_11","kind":"depends_on","weight":1.0,"label":"by Lem. XI"},
    {"id":"edge.prop_7.to.prop_6","source":"prop_7","target":"prop_6","kind":"depends_on","weight":1.0,"label":"by Cor. 1 of Prop. VI"},
    {"id":"edge.prop_11.to.prop_6","source":"prop_11","target":"prop_6","kind":"depends_on","weight":1.0,"label":"by Cor. 1 of Prop. VI"},
    {"id":"edge.prop_11.to.lemma_12","source":"prop_11","target":"lemma_12","kind":"depends_on","weight":1.0,"label":"by Lem. XII"},
    {"id":"edge.prop_11.to.lemma_7","source":"prop_11","target":"lemma_7","kind":"depends_on","weight":1.0,"label":"by Lem. VII"},
    {"id":"edge.prop_13.to.prop_6","source":"prop_13","target":"prop_6","kind":"depends_on","weight":1.0,"label":"by Cor. 1 of Prop. VI"},
    {"id":"edge.prop_13.to.lemma_7","source":"prop_13","target":"lemma_7","kind":"depends_on","weight":1.0,"label":"by Lem. VII"},
    {"id":"edge.prop_15.to.prop_11","source":"prop_15","target":"prop_11","kind":"depends_on","weight":1.0,"label":"by Prop. XI"},
    {"id":"edge.prop_15.to.prop_4","source":"prop_15","target":"prop_4","kind":"depends_on","weight":1.0,"label":"by Prop. IV"}
  ]
}
```

> ⚠️ Citation-fidelity note for DeepSeek/Nir: the label phrases above are my best reconstruction from the DIGEST + standard Principia citation patterns — they encode the real logical dependencies, but the exact Motte wording must be confirmed by the CITATION-AI pass against the actual section text. This concept graph is my hand-authored design, intended as the gold target. The proper pipeline run (STRUCTURE → CITATION → INFERENCE → merge) should reproduce this shape; where it diverges, the four safety nets (provenance, numbering, cycle/connectivity, two-method disagreement) flag it and Nir confirms a printed phrase by eye. If you'd rather I verify any specific label before the run, ask Nir to have you search the text for that phrase. 28 edges, 20 nodes, confirmed acyclic (all edges point from later results back to earlier ones).

## PART 3 — FIGURE PLAN

11 rooms have figures. Below: which printed plate/figure, step count, per-step gloss, and which color groups tag which elements. Built in the order shown (simple Series-based Section-I figures first → conics last). figure_id follows the rule figure_id startswith node_id + ".f".

**lemma_2.f1** — Lemma II (Plate 1, Fig. 6): inscribed & circumscribed rectangles under a curve.

```
n_steps: 3
  step 1 — the curve and its baseline axis           [curve→path, axis→construction]
  step 2 — the inscribed rectangles (under the curve) [Series inscribed_rects→swept_area]
  step 3 — the circumscribed rectangles (over it)     [Series circumscribed_rects→radius]
groups used: path, construction, swept_area, radius
ops sketch: free_point(A), free_point(B), point_on(curve top)… ; the curve as an arc/conic;
            Series(along=base_segment, to_curve=curve, count=8, kind="inscribed_rects")
            Series(along=base_segment, to_curve=curve, count=8, kind="circumscribed_rects")
```

**lemma_4.f1** — Lemma IV (Plate 1, Fig. 7): two figures, each filled with parallelograms, sharing an ultimate ratio.

```
n_steps: 3
  step 1 — first curvilinear figure with its rectangles  [path + swept_area]
  step 2 — second figure with its rectangles             [path + radius]
  step 3 — the correspondence lines linking the pairs     [construction]
groups: path, swept_area, radius, construction
```

**lemma_5.f1** — Lemma V (Plate 2, Fig. 1): two similar figures, homologous sides marked.

```
n_steps: 2
  step 1 — the two similar triangles/figures              [path]
  step 2 — the homologous sides marked equal-in-ratio     [construction, with angle_mark]
groups: path, construction
```

**lemma_6.f1** — Lemma VI (Plate 2, Fig. 1 region): arc ACB, chord AB, tangent AD; the vanishing angle.

```
n_steps: 3
  step 1 — the arc ACB                                    [path; labels A,C,B]
  step 2 — the chord AB                                   [construction]
  step 3 — the tangent AD at A and the contact angle BAD  [tangent, angle_mark]
groups: path, construction, tangent
ops: free_point(A), free_point(B), arc(center,A,B) as path 'arc1';
     segment(A,B) chord; tangent_at(arc1, A) → ray; angle_mark(B, A, D)
```

**lemma_7.f1** — Lemma VII (Plate 2, Fig. 1): arc, chord, tangent ultimately equal.

```
n_steps: 3
  step 1 — the arc AB                                     [path]
  step 2 — the chord AB and tangent AD                    [construction, tangent]
  step 3 — the secant/auxiliary line RD showing the limit [radius]
groups: path, construction, tangent, radius
```

**lemma_11.f1** — Lemma XI (Plate 2, Fig. 4): the evanescent subtense BD of the contact angle.

```
n_steps: 3
  step 1 — the curve and the tangent AD at A              [path, tangent]
  step 2 — the chord AB and the subtense BD ⟂ tangent     [construction, with foot]
  step 3 — the conterminate arc-subtense for comparison   [radius]
groups: path, tangent, construction, radius
ops: free_point(A); curve as arc/conic 'c'; tangent_at(c,A); point_on(c) B;
     foot(B, tangent) → D (the subtense); perpendicular marks
```

**prop_1.f1** — Prop. I (Plate 2, Fig. 5): the equal-areas figure — the polygon of equal triangles SAB, SBC, SCD… about centre S. (This is the same family as the golden-pack prop_1.f1 example — a strong pattern to follow.)

```
n_steps: 4
  step 1 — centre S and the polygonal path A B C D E       [path; labels S,A,B,C,D,E]
  step 2 — the radii SA, SB, SC, SD, SE                     [radius]
  step 3 — the swept triangles SAB, SBC, SCD (equal areas)  [swept_area]
  step 4 — the impulse construction: Cc parallel to SB      [construction; the force kick]
groups: path, radius, swept_area, construction
ops: free_point(S); free_point(A)…free_point(E) (rough_xy seeds a fan);
     polyline([A,B,C,D,E]); segment(S,A)…segment(S,E);
     polygon([S,A,B]) etc. as swept_area; parallel(through=B, to=segment(S, c))
```

**prop_6.f1** — Prop. VI (Plate 3, Fig. 2): body P, centre S, nascent arc PQ, versed sine QR, tangent ZPR.

```
n_steps: 4
  step 1 — centre S, body P, the orbit arc PQ              [path, radius; labels S,P,Q]
  step 2 — the tangent line at P (ZPR)                      [tangent]
  step 3 — QR parallel to SP (the versed sine) and QT ⟂ SP  [construction; labels R,T]
  step 4 — the force-measure rectangle SP²·QT²/QR           [swept_area]
groups: path, radius, tangent, construction, swept_area
```

**prop_7.f1** — Prop. VII (Plate 3, Fig. 3): circle, body P, force to point S on/off the circle.

```
n_steps: 3
  step 1 — the circle and body P                           [path; label P]
  step 2 — the force-point S and chord/line PS             [radius; label S]
  step 3 — tangent and the auxiliary RPQ construction      [tangent, construction]
groups: path, radius, tangent, construction
```

**prop_11.f1** — Prop. XI (Plate 4, Fig. 2): ★ THE HEADLINE — ellipse, focus S, body P, the inverse-square construction. Uses ellipse_foci.

```
n_steps: 5
  step 1 — the ellipse with foci S and H                   [path; ellipse_foci(S,H,P); labels S,H]
  step 2 — body P on the ellipse and the focal radius SP   [radius; label P]
  step 3 — the tangent at P and the diameter constructions [tangent, construction]
  step 4 — the parallelogram / Lemma XII conjugate setup    [construction]
  step 5 — the latus rectum L and the force-ratio result    [swept_area; label L]
groups: path, radius, tangent, construction, swept_area
ops: free_point(S), free_point(H), free_point(P near the ellipse top);
     ellipse_foci(f1=S, f2=H, through=P) → 'ell';
     segment(S,P) radius; tangent_at(ell, P); … (emitter computes exact incidences)
```

**prop_13.f1** — Prop. XIII (Plate 5, Fig. 3): parabola, focus S, body P, same inverse-square result. Uses parabola_fd.

```
n_steps: 4
  step 1 — the parabola with focus S and directrix          [path; parabola_fd; label S]
  step 2 — body P and focal radius SP                        [radius; label P]
  step 3 — the tangent at P and perpendicular construction   [tangent, construction]
  step 4 — the latus-rectum / force-ratio result             [swept_area]
groups: path, radius, tangent, construction, swept_area
```

Figure-less rooms (lemma_3, lemma_9, lemma_10, law_1, law_2, prop_2, prop_4, prop_15, lemma_12): these get text-only proof panels — paired full-LaTeX step blocks, no recipe/.asy. They test the room maker's no-figure path. Their ceiling equations and step text come from the section text (DeepSeek's baker_text pass).

## PART 4 — PALETTE

palette.json, valid against §3.A.7 (reserved keys present, map_importance keys "1".."5", all hex valid). I keep the 5 group names the Second Canon example already uses (so the gold recipe patterns transfer cleanly) — they map perfectly onto Newton's recurring elements: path (the orbit/curve), radius (focal radii / radii from centre), construction (auxiliary lines), tangent (tangents & contact lines), swept_area (areas, force rectangles, latus rectum).

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

Color logic: importance-5 rooms (the load-bearing results — Lemmas II/VII/X/XI, Law II, Props I/IV/VI/XI/XV) glow warm cream #F5F2E8 on the map — biggest, brightest. Peripheral importance-3 rooms sit cool teal. The guide-lines inherit the target's importance color, so the player is always drawn toward the central results.

## PART 5 — BUILD ORDER (the exact sequence DeepSeek runs)

```
PHASE A — THE MAP (Leg 1)
  A1. Author concept_graph.json directly from PART 2 above (it is hand-designed; the
      STRUCTURE/CITATION/INFERENCE+merge passes are run as VERIFICATION, to confirm the
      pipeline reproduces this shape and to flag any citation-label corrections).
        in:  Part 2 JSON  →  out: concept_graph.json
  A2. (verification) STRUCTURE AI on sections I–III headers → nodes_raw.json; compare node set.
  A3. (verification) CITATION AI on the proof pages of the 11 citing nodes → citations_raw.json.
  A4. (verification) INFERENCE AI → inference_raw.json; merge.py → provenance.json; diff vs Part 2.
  A5. level_maker(concept_graph.json, seed=1729001) → floorplan.json
        EXPECT: ≥1 crossing resolved as bridge/underpass; warn if >7 height layers; DAG holds.

PHASE B — THE WALLS (Leg 2), figures in difficulty order
  For each figure_id in this exact order (compile-safe first, conics last):
    lemma_2.f1, lemma_4.f1, lemma_5.f1, lemma_6.f1, lemma_7.f1, lemma_11.f1,   ← Tier 1
    prop_1.f1, prop_6.f1, prop_7.f1,                                           ← Tier 2
    prop_11.f1, prop_13.f1                                                     ← Tier 3 (conics)
    B1. READER AI(figure scan + caption) → recipe.<figure_id>.json   (validate vs §3.A.4)
    B2. EMITTER AI(recipe + asy_geometry_reference + prooffig + golden .asy) → figure.<figure_id>.asy
    B3. asy_compile  → on error, paste exact stderr back to EMITTER, loop
    B4. overlay_diff (Nir's eyes): scan vs render, align/thicken/flip → describe mismatches → loop
    B5. baker_figure → off + on_1..on_N PNGs (key out bg_key #FF00FF) + manifest entries
  Then text panels for ALL 20 nodes:
    B6. baker_text(step LaTeX paragraphs + ceiling equations, with palette.tex \cg spans)
        → off/on text PNGs + manifest entries

PHASE C — THE ROOMS (Leg 3)
  C1. Author room_source for each of the 20 nodes (coupled step pairs: figure-block + text-block
      for figure rooms; text-only pairs for the 9 figure-less rooms; final_pair_id per room;
      ceiling_equations_latex per room).
  C2. portal_spec(floorplan.json) → per-room door bearings
  C3. room_maker(room_source + manifest + portal_spec) → room_runtime/<node_id>.json   (×20)

PHASE D — ASSEMBLE & TEST
  D1. Place floorplan.json + manifest.json + palette.json + room_runtime/*.json + PNGs
      under packs/principia_bk1_inverse_square/
  D2. load_pack(dir) → Pack   (asserts schema_version, ID-spine integrity)
  D3. app.py 60-frame smoke test on the new pack
```

## PART 6 — ACCEPTANCE GATES

```
Gate 1 — Full 285-test suite still green (zero regressions; the new level adds data, not code).
Gate 2 — load_pack("packs/principia_bk1_inverse_square/") returns a valid Pack.
Gate 3 — floorplan.json from level_maker is a valid DAG with ≥1 crossing rendered as
         a true over/under (bridge + underpass); height-layer count ≤ 7 (soft warn) / ≤ 12 (hard).
Gate 4 — At least one figure (target: lemma_2.f1, the simplest) passes asy_compile AND
         Nir's overlay-diff fidelity check; STRETCH: prop_11.f1 (the conic) also passes.
Gate 5 — app.py runs the new level; 60-frame smoke test exits 0; mode switch corridor↔room works.
Gate 6 — Every room_runtime has doors[] with spawn_xyz / spawn_heading_rad matching corridor
         bearings (door count == node degree; spawn_heading == bearing + π).
```

Degree check for Gate 6 (door count = node degree, from the 28 edges): the highest-degree node is prop_6 (degree 6: 3 in + 3 out → cited by prop_7/prop_11/prop_13, cites prop_1/lemma_10/lemma_11), then lemma_7 (degree 5), prop_11 (degree 5). These multi-door rooms are the real Room-Maker v3 stress test. Lowest-degree are leaves like prop_15 (degree 2) and lemma_5 (degree 2).

## Closing notes for DeepSeek & Nir 🔥

- This is a real, serious level — the genuine spine of Book 1, climbing from limits to Kepler's laws and the inverse-square force, the result that is the Principia.
- The crossing-test is built in: 28 edges over 20 nodes with heavy back-citation into the Section-I toolbox guarantees a non-planar drawing → real bridges and underpasses. prop_6 with degree 6 will exercise the multi-door room maker hard.
- Risk is front-loaded sanely: simple Series-based Section-I figures compile first; the two conics (prop_11, prop_13) come last, so if Asymptote fights them we've already proven the pipeline on 9 figures.
- One honest gap I'm flagging: the verbatim citation label phrases in Part 2 are my reconstruction of Newton's real dependencies but not guaranteed his exact Motte wording. The verification passes (A2–A4) + Nir's eyeball are exactly the mechanism designed to correct these — and the graph topology (which is what the dungeon shape depends on) is sound regardless of phrasing.

Nir — this is the design. Should I hand it off as-is, or would you like me to adjust the room count, swap any propositions, or tune the difficulty gradient before DeepSeek runs Phase A? 😊🗝️
