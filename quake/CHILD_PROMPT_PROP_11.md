# QUAKE CHILD PROMPT — prop_11.room

You are a Quake content child. Write ONE `.room` file for prop_11. Return ONLY the `.room` file text (in a fenced code block).

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
  parallel LR through Q to S P
  perp QT through Q to S P
  tangent_at tan on circ at P
  circle_cr circ O radiusval 3.2
  ellipse_foci ell S H radiusval 5.0
  point P @(2.8,-1.5) label=$P$ at=SE marker=dot

Each station re-defines all its own points from scratch.
Text uses {colorname|words} spans and $math$.
```

## YOUR ROOM — prop_11

**prop_11 · DIAGRAM · 5 step-pairs · Pl.4 Fig.2 · ★★★ HEADLINE ★★★ · importance 5**

THE PAYOFF. This is the Proposition the whole Principia was building toward. Newton proves: for a body revolving in an ELLIPSE with the force directed to a FOCUS, the centripetal force varies as 1/SP² — the INVERSE-SQUARE LAW. This is the mathematical proof that Kepler's elliptical orbits imply gravity falls off as the square of the distance. The construction uses the conjugate-diameter geometry of Lemma XII and the force-measure apparatus of Prop. VI.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section III, Proposition XI; Plate 4, Figure 2.
caption   If a body revolves in an ellipse, find the law of the centripetal force tending to the focus of the ellipse.
final     5
ceiling   prop11 :: F \propto \dfrac{1}{SP^2}

s1 — Ellipse → ellblue(#1E6FE0); foci S (force), H → fociorange(#E8770A) ♥; body P; radius SP → radgreen(#00A35A).
s2 — Construction: HI ∥ EC, show EP = AC (semi-major) → equalpurple(#8E24AA) ♥; the ½(PS+PH)=AC relation.
s3 — Tangent + conjugate diameters DK, PG; ordinate Qv; parallelogram QxPR → parteal(#00897B) ♥.
s4 — Lemma XII: CD² ↔ CB²; latus rectum L = 2BC²/AC → latusred(#D81B60) ♥; ratio chain L·QR : QT².
s5 — Compound reduction ⇒ L·QR / QT² = SP² → resultblue(#1E6FE0) ♥; force ∝ 1/SP². Q.E.I.

colors_used: ellblue, fociorange, radgreen, equalpurple, parteal, latusred, resultblue
```

### Newton's text (verbatim, 1729 Motte, Book I, Section III, Proposition XI):

> If a body revolves in an ellipse: it is required to find the law of the centripetal force tending to the focus of the ellipse.
>
> Let CA, CB be semi-axes of the ellipse; GP, DK other conjugate diameters; PF, QT perpendiculars to those diameters; Qv an ordinate to the diameter GP; and if the parallelogram QxPR be completed, the rectangle PvG will be to Qv² as PC² to CD²; and (because of the similar triangles QxT, PEF) Qx² or QT² is to EP² as PF² to CA²; and (by Lem. XII) the rectangle 2BC × CA is equal to the latus rectum. Putting these together, the centripetal force comes out reciprocally as SP², that is, reciprocally in the duplicate ratio of the distance SP. Q.E.I.

### GUIDANCE

This is the CROWN JEWEL of Book I. Newton assembles everything — the Prop. VI force formula, the ellipse's conjugate-diameter property from Lemma XII, and the latus rectum — to prove the inverse-square law.

**Station 1 — The Ellipse and its Foci:** Draw an ellipse with semi-axes. Mark the two foci S and H. P is the body on the ellipse. Draw the radius SP from the force-focus to the body. The {ellblue|ellipse} is the orbit, the {fociorange|foci S (force centre) and H (empty focus)} are the heart, and the {radgreen|radius SP} connects body to force. Text: introduce the ellipse as Kepler's great discovery — planets move in ellipses with the Sun at one focus. Newton now asks: what force law PRODUCES this orbit? The answer, proven here, is the inverse-square.

**Station 2 — The EP = AC Relation:** Draw the construction: HI parallel to the tangent at P, meeting the diameter EC. Show that EP equals AC (the semi-major axis). The {equalpurple|equality EP = AC — the semi-major axis} is the heart. Text: this is the step that ties the ellipse's focal property (PS+PH = 2AC) to the geometry needed for the force calculation. The sum of distances to the foci is constant = the major axis.

**Station 3 — Conjugate Diameters and the Parallelogram:** Draw the tangent at P. Draw conjugate diameters DK and PG. Draw the ordinate Qv (parallel to the tangent, meeting the diameter PG at v). Complete the parallelogram QxPR. The {parteal|conjugate diameters DK, PG and the parallelogram QxPR} is the heart. Text: conjugate diameters are pairs of lines through the centre where each is parallel to the tangent at the endpoint of the other. The parallelogram QxPR is the ellipse's version of the QR construction from Prop. VI — adapted for the ellipse's specific geometry.

**Station 4 — Lemma XII and the Latus Rectum:** Invoke Lemma XII: the parallelogram about conjugate diameters has constant area. This gives the relation CD² ↔ CB². The latus rectum L = 2BC²/AC enters — a fundamental constant of the ellipse. The {latusred|latus rectum L = 2BC²/AC} is the heart. Text: Lemma XII (all parallelograms about conjugate diameters are equal) gives the bridge from the ellipse's shape constants to the force. The latus rectum is the chord through a focus perpendicular to the major axis — it encodes the ellipse's "width" at the focus.

**Station 5 — The Inverse-Square Law:** Compound the ratio chain: L·QR / QT² = SP², so the force from Prop. VI (∝ 1/(SP²·QT²/QR)) becomes 1/(SP²·SP²) = 1/SP². The {resultblue|inverse-square law F ∝ 1/SP²} is the heart. Text: after five steps of reduction, the messy ellipse geometry collapses into the clean inverse-square — the force that holds planets in their elliptical orbits is exactly the same force that Newton would later identify as universal gravitation. Q.E.I. (Quod Erat Inveniendum — "which was to be found," the closing of a Problem).

**Figure layout (Pl.4 Fig.2):** Ellipse with centre C, major axis AA', minor axis BB'. Foci S and H on the major axis. Body P on the circumference. Conjugate diameters PG and DK. Tangent at P. Ordinate Qv from nearby point Q. Parallelogram QxPR. Various perpendiculars PF, QT.

### GOLD EXAMPLE — prop_7.room (same Prop. VI construction family!)

Prop. XI is the most complex room yet — 5 stations, 7 colors. But the fundamental structure is the same as prop_7 and prop_6: set up the curve, draw auxiliary lines, apply the QR/SP/QT construction, reduce the ratio. Study prop_7 for the station structure pattern; prop_11 just has more steps because the ellipse has richer geometry.

## RULES

1. Colors local per station. Uncolored = BLACK (never `color=black`).
2. At least one `heart` per station.
3. Every declared color used; every used color declared.
4. Define points BEFORE segments/polygons that reference them.
5. Every geometry op has a NAME right after the op keyword.
6. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences, EDUCATIONAL.
7. Prop. XI depends on Prop. VI, Lemma VII, Lemma XII — mention these.
8. End final station with `\textit{Q.E.I.}` (Problem = Inveniendum, not Demonstradum).
9. `\` at end of line for long text lines.

Return ONLY the `.room` file text.
