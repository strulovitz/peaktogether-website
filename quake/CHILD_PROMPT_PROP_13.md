# QUAKE CHILD PROMPT — prop_13.room

You are a Quake content child. Write ONE `.room` file for prop_13. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER:
  room <node_id>
  kind geometry
  import <citation>
  caption <line>
  final <step#>
  ceiling <eq_id> :: <verbatim LaTeX>

STATION:
  station <n>
    gloss <one sentence>
    color <name> <#hex>
    panel
      <ops>
    text
      <prose with {colorname|words} spans and $math$>
```

GEOMETRY ops: point point_on intersect midpoint foot from to reflect
  segment line ray parallel through to perp through to tangent_at on at
  circle_cp circle_cr radiusval circle_3 arc ellipse_foci ellipse_axes center major minor
  polygon polyline series angle

Attrs: color=NAME heart label=$..$ at=DIR marker=dot @(x,y)

Each op has a NAME right after the op keyword. Examples:
  segment SP S P color=radgreen heart
  foot T from Q to S P
  parallel QR through Q to S P
  perp QT through Q to S P
  tangent_at tan on par at P
  circle_cr circ O radiusval 3.2

Each station re-defines all its own points from scratch.
Text uses {colorname|words} spans and $math$.
```

## YOUR ROOM — prop_13

**prop_13 · DIAGRAM · 4 step-pairs · Pl.5 Fig.3 · importance 4**

After the ellipse (Prop. XI), Newton proves the SAME inverse-square law holds for the parabola. A body on a parabola with force to the focus also feels F ∝ 1/SP². The proof uses the parabola's conic property Qv² = 4PS·Pv (from Lemma XIII) and the Prop. VI force-measure construction.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section III, Proposition XIII; Plate 5, Figure 3.
caption   If a body moves in the perimeter of a parabola, find the law of the centripetal force tending to the focus.
final     4
ceiling   prop13 :: Qv^2 = 4PS\cdot Pv \qquad F \propto \dfrac{1}{SP^2}

s1 — Parabola → parabblue(#1E6FE0); focus S → fociorange(#E8770A) ♥; body P; SP → radgreen(#00A35A).
s2 — From Q: QR ∥ SP, QT ⟂ SP, Qv ∥ tangent → constpurple(#8E24AA) ♥; meets diameter PG at v.
s3 — Similar triangles ⇒ QR = Pv → relgreen(#00A35A) ♥; conic property Qv² = L·Pv = 4PS·QR.
s4 — Coincidence P,Q: Qv:Qx → 1 (by Lemma VII); force → resultred(#D81B60) ♥ ∝ 1/SP².

colors_used: parabblue, fociorange, radgreen, constpurple, relgreen, resultred
```

### Newton's text (verbatim, 1729 Motte, Book I, Section III, Proposition XIII):

> If a body moves in the perimeter of a parabola: it is required to find the law of the centripetal force tending to the focus of that figure. Pl. 5. Fig. 3.
>
> Retaining the construction of the preceding lemma, let P be the body in the perimeter of the parabola; and from the place Q into which it is next to succeed draw QR parallel and QT perpendicular to SP, as also Qv parallel to the tangent, and meeting the diameter PG in v, and the distance SP in x. Now, because of the similar triangles Pxv, SPM, and of the equal sides SP, SM of the one, the sides Px or QR and Pv of the other will be also equal. But (by the conic sections) the square of the ordinate Qv is equal to the rectangle under the latus rectum and the segment Pv of the diameter, that is, (by lem. 13.) to the rectangle 4PS × Pv, or 4PS × QR; and the points P and Q coinciding, the ratio of Qv to Qx (by cor. 2 lem. 7.) becomes a ratio of equality. And therefore Qx² in this case becomes equal to the rectangle 4PS × QR. But (because of the similar triangles QxT, SPN) Qx² is to QT² as PS² to SN², that is, as PS to SA; and therefore QT² is proportional to SP × QR. Whence by cor. 1. prop. 6 the centripetal force is reciprocally as SP².

### GUIDANCE

Prop. XIII is the parabola counterpart to the ellipse's Prop. XI — both prove the inverse-square law, but the parabola proof is simpler because the conic property Qv² = 4PS·Pv is more direct.

**Station 1 — Parabola and Focus:** Draw a parabola with focus S. P is the body. Draw SP. The {parabblue|parabola} is the orbit, the {fociorange|focus S} is the heart, and {radgreen|SP} connects them. Text: Newton has proven inverse-square for ellipses. Now the parabola — the limiting case where the orbit opens to infinity. Does it still give 1/SP²? Yes.

**Station 2 — The Construction:** From the nearby point Q, draw QR ∥ SP, QT ⟂ SP, and Qv parallel to the tangent at P, meeting the diameter PG at v. The {constpurple|construction QR ∥ SP, QT ⟂ SP, Qv ∥ tangent} is the heart. Text: the standard Prop. VI apparatus, plus the parabola-specific ordinate Qv along the diameter PG.

**Station 3 — QR = Pv and the Conic Property:** Show the similar triangles Pxv and SPM. Because SP = SM (the parabola's focal property), and the triangles are similar, we get QR = Pv. Then by the parabola's conic property (Lemma XIII): Qv² = L·Pv = 4PS·QR. The {relgreen|equality QR = Pv and Qv² = 4PS·QR} is the heart. Text: the parabola's geometry collapses Qv² into 4PS·QR — the latus rectum of the parabola is 4PS (four times the focal distance).

**Station 4 — The Limit and the Law:** As Q→P, Qv:Qx→1 (by Lemma VII Cor. 2). Then Qx² → 4PS·QR. But by similar triangles QxT, SPN, we have Qx²:QT² = PS²:SN² = PS:SA. Therefore QT² ∝ SP·QR, and force by Prop. VI ∝ 1/(SP²·QT²/QR) = 1/SP². The {resultred|inverse-square law F ∝ 1/SP²} is the heart. Q.E.D.

**Figure layout (Pl.5 Fig.3):** Parabola with vertex A, focus S. Body P near the right side. Nearby Q. Diameter PG through P. Tangent at P. QR ∥ SP, QT ⟂ SP, Qv parallel to tangent meeting PG at v. Point M on the axis such that SP = SM.

### GOLD EXAMPLE — prop_7.room (same Prop. VI construction!)

Prop. XIII uses the QR/SP/QT construction with the parabola-specific additions Qv and the diameter PG. Study prop_7 for the station structure. Key difference: replace the circle with a parabola, and add Qv ∥ tangent meeting the diameter.

## RULES

1. Colors local per station. Uncolored = BLACK (never `color=black`).
2. At least one `heart` per station.
3. Every declared color used; every used color declared.
4. Define points BEFORE referencing them. Each station defines its own points.
5. Every geometry op has a NAME right after the op keyword.
6. Text: `{colorname|words}` + `$math$`. 4–5 sentences, EDUCATIONAL.
7. Prop. XIII depends on Lemma VII (Cor. 2), Lemma XIII, and Prop. VI (Cor. 1).
8. End final station with `\textit{Q.E.D.}`. `\` for line continuation.

Return ONLY the `.room` file text.
