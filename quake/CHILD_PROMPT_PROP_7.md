# QUAKE CHILD PROMPT — prop_7.room

You are a Quake content child. Write ONE `.room` file for prop_7. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER:
  room <node_id>
  kind geometry
  import <citation>
  caption <line>
  final <step#>
  ceiling <eq_id> :: <verbatim LaTeX>

GEOMETRY ops: point point_on intersect midpoint foot from to reflect
  segment line ray parallel through to perp through to tangent_at on at
  circle_cp circle_cr circle_3 arc ellipse_foci ellipse_axes
  polygon polyline series angle

  Attrs: color=NAME heart label=$..$ at=DIR marker=dot @(x,y)
  DIR = N|S|E|W|NE|NW|SE|SW|center
```

## YOUR ROOM — prop_7

**prop_7 · DIAGRAM · 3 step-pairs · Pl.3 Fig.3 · importance 3**

Prop. VI gave us the force-measure formula F ∝ 1/(SP²·QT²/QR). Prop. VII is the FIRST application: find the centripetal force for a body moving in a CIRCLE, with the force directed to ANY point S (not necessarily the centre). Construction: through S draw chord PV and diameter VA, draw QT ⟂ SP, and LR ∥ SP. The circle geometry collapses the ratio QT²/QR into a simple expression involving PV and AV.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition VII; Plate 3, Figure 3.
caption   If a body revolves in the circumference of a circle, find the law of centripetal force directed to any given point.
final     3
ceiling   prop7 :: F \propto \dfrac{1}{SP^2}\cdot\dfrac{1}{PV^3}

s1 — Circle VQPA → circblue(#1E6FE0); body P; force-point S → centerorange(#E8770A); SP → radgreen(#00A35A) ♥.
s2 — Tangent PRZ → tanteal(#00897B) ♥; chord PV + diameter VA → diampurple(#8E24AA).
s3 — Construction QT ⟂ SP, LR ∥ SP → constred(#D81B60) ♥; proportion QT²/QR ∝ 1/PV³ ⇒ the force law.

colors_used: circblue, centerorange, radgreen, tanteal, diampurple, constred
```

### Newton's text (verbatim, 1729 Motte, Book I, Section II, Proposition VII):

> If a body revolves in the circumference of a circle; it is proposed to find the law of centripetal force directed to any given point. Pl. 3. Fig. 3.
>
> Let VQPA be the circumference of the circle; S the given point to which as to a centre the force tends; P the body moving in the circumference; Q the next place into which it is to move; and PRZ the tangent of the circle at the preceding place. Through the point S draw the chord PV, and the diameter VA of the circle, join AP, and draw QT perpendicular to SP, which produced, may meet the tangent PRZ in Z; and lastly, through the point Q draw LR parallel to SP, meeting the circle in L, and the tangent PZ in R. And, because of the similar triangles ZQR, ZTP, ZPA we shall have RP² (that is, QRL) to QT² as AV² to PV². And therefore QRL × PV² / AV² is equal to QT². Multiply those equals by SP²/QR, and the points P and Q coinciding, PV²/AV² becomes unity. Write PV for the chord; and the force (by cor. 1 and 5 prop. 6) will become reciprocally as SP² × PV³, that is (because SP² × PV³ was given), reciprocally as the square of the distance or altitude SP, and the cube of the chord PV conjunctly.

### GUIDANCE

Prop. VII is the first concrete application of the Prop. VI force-measure construction to a specific curve — the circle. The key insight: applying the QR/SP/QT construction from Prop. VI to a circle, with S NOT necessarily at the centre, yields a force that varies as 1/(SP²·PV³) where PV is the chord through S.

**Step 1 — Circle and Force Centre:** Draw the circle VQPA. Place S somewhere INSIDE the circle (not at centre). P is the body's current position on the circle. Draw the radius SP (from force centre to body). The {circblue|circle VQPA} is the orbit, the {centerorange|force centre S} is inside it, and the {radgreen|radius SP} is the heart — this line connects the body to the attracting point. In the text: "the circle is the simplest curvilinear orbit. But the force need not come from the circle's centre — S can be anywhere inside. The challenge: apply Prop. VI's QR/SP/QT construction to extract the force law."

**Step 2 — Tangent, Chord, and Diameter:** Draw the tangent PRZ at P (touching the circle). Through S draw chord PV (cutting the circle at V on the far side). Draw the diameter VA through V. The {tanteal|tangent PRZ} is the heart — the forceless path. The {diampurple|chord PV through S and diameter VA} link S to the circle's geometry. In the text: "the chord PV is the line through S that connects to the far side of the circle. The diameter VA through V gives us the circle's radius — and with it, the similar triangles that will unlock the ratio we need."

**Step 3 — The Construction and Force Law:** Draw QT perpendicular to SP, and LR through Q parallel to SP (Prop. VI's standard construction, adapted for the circle). The {constred|construction QT ⟂ SP and LR ∥ SP} is the heart. The circle's geometry gives the proportion QT²/QR ∝ 1/PV³ through similar triangles ZQR, ZTP, ZPA. Plug into Prop. VI's formula: F ∝ 1/(SP²·PV³). In the text: "the circle collapses the messy QT²/QR ratio into the clean chord-cube law. In the special case where S is at the centre, PV becomes the diameter and the force simplifies to 1/SP² — the inverse-square law emerges naturally from the circle. This is the first glimpse of the 1/r² force that governs the solar system." End with Q.E.D.

**Figure layout (Pl.3 Fig.3):**
- A large circle VQPA
- Point S somewhere inside (not centre), e.g., below and right of centre
- Point P on the circumference, body's current position
- Nearby point Q on the circle (to the left of P)
- Tangent PRZ at P (horizontal-ish line)
- Chord PV through S, cutting circle at V (far side)
- Diameter VA through V (through circle centre)
- QT perpendicular from Q to line SP
- LR through Q parallel to SP, meeting tangent at R

### GOLD EXAMPLE — prop_6.room (same construction pattern!)

Prop. VII uses the identical QR/SP/QT construction as Prop. VI, but applies it to a specific curve (circle). Study prop_6 for the construction pattern. Key differences: s1 adds the circle, s2 adds chord+diameter specific to the circle, s3 derives the circle-specific force law.

## RULES

1. Colors LOCAL per station. Uncolored = BLACK (omit `color=black`).
2. At least one `heart` per station.
3. Every declared color used; every used color declared.
4. Define points BEFORE referencing them.
5. `segment <name> <pt1> <pt2>`, `line <name> <pt1> <pt2>` — always include a name!
6. `angle <name> <a> <vertex> <b>` — 4 positional tokens.
7. `parallel <name> through <pt> to <pt1> <pt2>` — use `through`+`to` keywords.
8. `perp <name> through <pt> to <pt1> <pt2>` — use `through`+`to` keywords.
9. `foot <name> from <pt> to <pt1> <pt2>` — use `from`+`to` keywords.
10. `tangent_at <name> on <curve> at <pt>` — use `on`+`at` keywords.
11. Text: `{colorname|words}` + `$math$`. 4–5 sentences, EDUCATIONAL.
12. End final station with `\textit{Q.E.D.}`. `\` for line continuation.

Return ONLY the `.room` file text.
