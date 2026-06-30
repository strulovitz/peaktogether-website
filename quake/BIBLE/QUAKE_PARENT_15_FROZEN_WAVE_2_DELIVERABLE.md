# QUAKE PARENT 15 — FROZEN WAVE 2 DELIVERABLE (verbatim from Opus)

> Rooms 11–20 of the station map. Wave 1 (rooms 1–10 + palette + concept_graph) at `QUAKE_PARENT_15_FROZEN_WAVE_1_DELIVERABLE.md`.

law_1 ceiling → word-form, locked: \text{no force} \Rightarrow \text{no change of motion}.

---

## STATION MAP, ROOMS 11–20

Notation per step: gloss — element → colorname(#hex); ♥ = Stabilo heart of that step.

### lemma_11 · DIAGRAM · 3 step-pairs · Pl.2 Fig.4 · importance 5

- **s1** Curve at A with tangent AD → tanblue(#1E6FE0) ♥; chord/arc AB → arcgreen(#00A35A).
- **s2** Subtense BD ⟂ AD → subred(#D81B60) ♥; foot on tangent; auxiliaries BG ⟂ AB, AG → auxpurple(#8E24AA), ultimate intersection J.
- **s3** Conterminate-arc subtense; the relation AB² = AG·BD → relorange(#E8770A) ♥ ⇒ subtense as duplicate ratio of arc-subtense.
- **colors_used:** tanblue, arcgreen, subred, auxpurple, relorange
- **ceiling:** BD \propto AB^2 \;(\text{ultimately})
- **final_pair_id:** lemma_11.s3

### lemma_12 · DIAGRAM · 1 step-pair · Pl.4 Fig.1 (reused) · importance 3

- **s1** Ellipse → ellblue(#1E6FE0); one pair of conjugate diameters → conjorange(#E8770A); circumscribed parallelogram → pargreen(#00A35A) ♥ (the constant-area parallelogram). Explanation notes (one line) this is Apollonius' conic result; area constant =4ab.
- **colors_used:** ellblue, conjorange, pargreen
- **ceiling:** \text{parallelogram about conjugate diameters} = \text{const} = 4ab
- **final_pair_id:** lemma_12.s1

### prop_1 · DIAGRAM · 4 step-pairs · Pl.2 Fig.5 · importance 5

- **s1** Centre S → centerorange(#E8770A); polygonal path ABCDE → pathblue(#1E6FE0) ♥.
- **s2** Radii SA,SB,SC,SD,SE → radigreen(#00A35A) ♥.
- **s3** Swept triangles SAB, SBc, SBC → arearpurple(#8E24AA) ♥ shown equal (innate motion Bc=AB).
- **s4** Centripetal impulse at B: Cc ∥ SB → impulsered(#D81B60) ♥; in the limit the polygon → curve, areas ∝ times.
- **colors_used:** centerorange, pathblue, radigreen, arearpurple, impulsered
- **ceiling:** \dfrac{dA}{dt} = \text{const} (areas ∝ times)
- **final_pair_id:** prop_1.s4

### prop_2 · DIAGRAM · 3 step-pairs · (reuses Prop. I triangle-fan) · importance 4

- **s1** Curve + centre S → centerorange(#E8770A); equal triangles SAB,SBC,SCD → fanpurple(#8E24AA) ♥ in equal times.
- **s2** At B, deflection from rectilinear course (by Law 1): line parallel to cC → deflectblue(#1E6FE0) ♥, i.e. directed along BS.
- **s3** Force always directed to S: radial lines BS, CS → radialred(#D81B60) ♥ ⇒ centripetal.
- **colors_used:** centerorange, fanpurple, deflectblue, radialred
- **ceiling:** \text{areas} \propto \text{times} \;\Rightarrow\; F \to S
- **final_pair_id:** prop_2.s3

### prop_4 · EQUATION-AS-FIGURE (+ optional sketch) · 2 step-pairs · importance 5 · the locked-doctrine example

- **s1** (equation) equation-as-figure: F→forceorange(#E8770A) \;\propto\; \dfrac{v^2→velblue(#1E6FE0)}{\,r→radgreen(#00A35A)\,} ♥ = v² velblue. Explanation: "the pull toward the centre→forceorange is as the square of the speed→velblue divided by the distance from the centre→radgreen."
- **s2** (sketch) small circle, equal-time arc → velblue(#1E6FE0), radius to centre → radgreen(#00A35A) ♥; versed sine ↔ force (by Cor. 4 Prop. 1, Lem. 7).
- **colors_used:** forceorange, velblue, radgreen
- **ceiling:** F \propto \dfrac{v^2}{r}
- **final_pair_id:** prop_4.s2

### prop_6 · DIAGRAM · 4 step-pairs · Pl.3 Fig.2 · importance 5

- **s1** Centre S → centerorange(#E8770A), body P, nascent arc PQ → arcblue(#1E6FE0) ♥.
- **s2** Tangent ZPR → tangreen(#00A35A) ♥; versed sine bisecting the chord through S.
- **s3** QR ∥ SP → parblue(#1E6FE0); QT ⟂ SP → perpred(#D81B60) ♥.
- **s4** Force-measure solid \dfrac{SP^2\cdot QT^2}{QR} → measpurple(#8E24AA) ♥; force as versed sine ÷ time².
- **colors_used:** centerorange, arcblue, tangreen, parblue, perpred, measpurple
- **ceiling:** F \propto \dfrac{\text{versed sine}}{t^2} · F \propto \dfrac{1}{SP^2\cdot QT^2/QR}
- **final_pair_id:** prop_6.s4

### prop_7 · DIAGRAM · 3 step-pairs · Pl.3 Fig.3 · importance 3

- **s1** Circle VQPA → circblue(#1E6FE0); body P; force-point S → centerorange(#E8770A); SP → radgreen(#00A35A) ♥.
- **s2** Tangent PRZ → tanteal(#00897B) ♥; chord PV + diameter VA → diampurple(#8E24AA).
- **s3** Construction QT ⟂ SP, LR ∥ SP → constred(#D81B60) ♥; proportion QT²/QR ∝ PV²/AV² ⇒ the force law.
- **colors_used:** circblue, centerorange, radgreen, tanteal, diampurple, constred
- **ceiling:** F \propto \dfrac{1}{SP^2}\cdot\dfrac{\,\cdots\,}{PV^2}
- **final_pair_id:** prop_7.s3

### prop_11 · DIAGRAM · 5 step-pairs · Pl.4 Fig.2 · ★HEADLINE · importance 5 · 4 doors (degree 4)

- **s1** Ellipse → ellblue(#1E6FE0); foci S, H → fociorange(#E8770A) ♥; body P; radius SP → radgreen(#00A35A).
- **s2** Construction: HI ∥ EC, show EP = AC (semi-major) → equalpurple(#8E24AA) ♥; the ½(PS+PH)=AC relation.
- **s3** Tangent + conjugate diameters DK, PG; ordinate Qv; parallelogram QxPR → parteal(#00897B) ♥.
- **s4** Invoke Lem. XII: CD² ↔ CB²; latus rectum L = 2BC²/AC → latusred(#D81B60) ♥; ratio chain L·QR : QT².
- **s5** Compound reduction ⇒ L·QR / QT² = SP² reciprocally → resultblue(#1E6FE0) ♥; force ∝ 1/SP². Q.E.I.
- **colors_used:** ellblue, fociorange, radgreen, equalpurple, parteal, latusred, resultblue
- **ceiling:** F \propto \dfrac{1}{SP^2} (inverse-square — the payoff)
- **final_pair_id:** prop_11.s5

### prop_13 · DIAGRAM · 4 step-pairs · Pl.5 Fig.3 · importance 4

- **s1** Parabola → parabblue(#1E6FE0); focus S → fociorange(#E8770A) ♥; body P; SP → radgreen(#00A35A).
- **s2** From next place Q: QR ∥ SP, QT ⟂ SP, Qv ∥ tangent → constpurple(#8E24AA) ♥; meets diameter PG at v.
- **s3** Similar triangles Pxv, SPM ⇒ QR = Pv → relgreen(#00A35A) ♥; conic property Qv² = L·Pv = 4PS·QR (by Lem. 13).
- **s4** Coincidence P,Q: Qv:Qx → 1 (by Cor. 2 Lem. 7); force → resultred(#D81B60) ♥ ∝ 1/SP² (by Cor. 1 Prop. 6).
- **colors_used:** parabblue, fociorange, radgreen, constpurple, relgreen, resultred
- **ceiling:** Qv^2 = 4PS\cdot Pv · F \propto \dfrac{1}{SP^2}
- **final_pair_id:** prop_13.s4

### prop_15 · EQUATION-AS-FIGURE · 2 step-pairs · importance 5 · Kepler's 3rd · no printed figure

- **s1** (the relationship) equation-as-figure: \text{(periodic time)}^2→timeblue(#1E6FE0) \;\propto\; \text{(greater axis)}^3→axisorange(#E8770A) ♥ = axisorange. Explanation (Newton's language): "the periodic times→timeblue in ellipses are in the sesquiplicate ratio→ratiopurple(#8E24AA) of their greater axes→axisorange."
- **s2** (derivation) the lesser axis is mean proportional between greater axis and latus rectum → meangreen(#00A35A) ♥; subducting the subduplicate ratio of the latus rectum leaves the sesquiplicate ratio (by Cor. Prop. 14).
- **colors_used:** timeblue, axisorange, ratiopurple, meangreen
- **ceiling:** T^2 \propto a^3 (Kepler III)
- **final_pair_id:** prop_15.s2

---

## DELIVERABLE SUMMARY

- **Station map complete** — all 20 rooms delivered (Wave 1: rooms 1–10 + palette + graph; Wave 2: rooms 11–20 above).
- **20 rooms, 56 stations total** — every room has a colored thing to look at and shoot (16 DIAGRAM rooms, 2 EQUATION rooms prop_4/prop_15, 1 TEXT room law_1, 1 EQUATION/TEXT law_2).
- **No dead text-only rooms** — Parent 7's "9 figure-less" shortcut fully overturned and justified per page.
- **Degree fixes:** lemma_7 = 6 doors, prop_11 = 4 doors.
- **Citations verified** against the Motte text; two genuinely-external refs (prop_14, lem_13) kept out of the edge set as external_citation provenance to protect the ID-spine build.
- **Color:** fully local-per-station, no global palette, no grey, current-step-only Stabilo hearts.
- **Contract:** zero change — equation/text panels are FigureDecls via colored-label .asy (Gate 0 = confirm a label-only .asy bakes; strict subset of lemma_2.f1.asy).

Two items still flagged for DeepSeek (not blocking): (1) confirm prop_7's self-referential "cor. 3. prop. 7" against a wider page range; (2) confirm external_citation handling for prop_14/lem_13. Both are downstream verification, not design.

Parent 15 deliverable done. Over to Parent 16 for the format + build/room_from_spec.py tool.
