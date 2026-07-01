# QUAKE CHILD PROMPT — prop_7.room

You are a Quake content child. Write ONE `.room` file for prop_7. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER:
  room <node_id>
  kind geometry|equation|text
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
  circle_cp circle_cr circle_3 arc ellipse_foci ellipse_axes
  polygon polyline series angle

  Attrs: color=NAME heart label=$..$ at=DIR marker=dot @(x,y)
  DIR = N|S|E|W|NE|NW|SE|SW|center

Every op takes a NAME right after the op keyword. Examples:
  segment SP S P color=radgreen heart
  line ZPR Z R color=tangreen heart
  arc P Q S color=arcblue
  circle_cr circ O 3.2 color=circblue
  foot T from Q to S P
  parallel LR through Q to S P
  perp QT through Q to S P
  tangent_at tan on circ at P
  angle QTP Q T P

Each station re-defines all its own points from scratch.
Text uses {colorname|words} spans and $math$.
```

## YOUR ROOM — prop_7

**prop_7 · DIAGRAM · 3 step-pairs · Pl.3 Fig.3 · importance 3**

Prop. VI gave the force-measure: F ∝ 1/(SP²·QT²/QR). Prop. VII is the first application — find the law for a body on a CIRCLE with force toward ANY point S (not necessarily the centre). The circle geometry collapses QT²/QR into 1/PV³, giving F ∝ 1/(SP²·PV³).

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition VII; Plate 3, Figure 3.
caption   If a body revolves in the circumference of a circle, find the law of centripetal force directed to any given point.
final     3
ceiling   prop7 :: F \propto \dfrac{1}{SP^2}\cdot\dfrac{1}{PV^3}

s1 — Circle VQPA → circblue(#1E6FE0); body P, Q nearby; force centre S → centerorange(#E8770A); SP → radgreen(#00A35A) ♥.
s2 — Tangent PRZ → tanteal(#00897B) ♥; chord PV through S; diameter VA; join AP → diampurple(#8E24AA).
s3 — QT ⟂ SP, LR ∥ SP → constred(#D81B60) ♥; similar triangles → QT²/QR ∝ PV³ → F ∝ 1/(SP²·PV³).

colors_used: circblue, centerorange, radgreen, tanteal, diampurple, constred
```

### Newton's text (verbatim, 1729 Motte, Book I, Section II, Proposition VII):

> If a body revolves in the circumference of a circle; it is proposed to find the law of centripetal force directed to any given point. Pl. 3. Fig. 3.
>
> Let VQPA be the circumference of the circle; S the given point to which as to a centre the force tends; P the body moving in the circumference; Q the next place into which it is to move; and PRZ the tangent of the circle at the preceding place. Through the point S draw the chord PV, and the diameter VA of the circle, join AP, and draw QT perpendicular to SP, which produced, may meet the tangent PRZ in Z; and lastly, through the point Q draw LR parallel to SP, meeting the circle in L, and the tangent PZ in R. And, because of the similar triangles ZQR, ZTP, ZPA we shall have RP² (that is, QRL) to QT² as AV² to PV². And therefore QRL × PV² / AV² is equal to QT². Multiply those equals by SP²/QR, and the points P and Q coinciding, PV²/AV² becomes unity. Write PV for the chord; and the force (by cor. 1 and 5 prop. 6) will become reciprocally as SP² × PV³, that is, reciprocally as the square of the distance SP and the cube of the chord PV conjunctly.

### GUIDANCE

Prop. VII is the first concrete application of the Prop. VI force formula to a real curve. The QR/SP/QT construction stays the same — but now it lives inside a circle.

**Station 1 — Circle and Force Centre:** Draw the circle VQPA (centre O, radius ~3.2). Place S somewhere INSIDE the circle but NOT at the centre — e.g. at (0.7, -0.8). P is the body on the circumference. Q is the next nearby place. Draw SP. The {circblue|circle} is the orbit, the {centerorange|force centre S} is somewhere inside, and the {radgreen|radius SP} is the heart. Text: explain that this is the simplest curvilinear orbit, but the force need not come from the centre — S can be anywhere inside. The challenge is to apply Prop. VI's construction.

**Station 2 — Tangent, Chord, and Diameter:** Draw the tangent at P — use `tangent_at` on the circle. Through S draw chord PV to the far side of the circle at V. Draw diameter VA through V (and the centre O). Join AP. The {tanteal|tangent PRZ} is the heart — the forceless path. The {diampurple|chord PV through S and diameter VA} link S to the circle's intrinsic geometry. Text: because VA is a diameter, angle VPA is a right angle — this seeds the similar triangles that will unlock the ratio. The chord PV through S is the key length that governs the entire force law.

**Station 3 — The Construction and Force Law:** Apply Prop. VI's apparatus. Use `foot T from Q to S P` to get the foot, then `perp QT through Q to S P` for the perpendicular, and `parallel LR through Q to S P` for the parallel. Place R where LR meets the tangent, L where it meets the circle. The {constred|construction QT ⟂ SP and LR ∥ SP} is the heart. Text: similar triangles ZQR, ZTP, ZPA collapse the ratio QT²/QR into the clean chord-cube PV³. Plug into Prop. VI: F ∝ 1/(SP²·PV³). In the special case where S is at the centre, PV becomes the diameter and the law simplifies to 1/SP² — the inverse-square law emerging naturally from a circle. Q.E.D.

**Figure layout (Pl.3 Fig.3):** Circle centre O at (0,0) with radius ~3.2. S inside at about (0.7,-0.8). P on right side of circumference (~2.8,-1.5). Q upper-left (~1.3,2.9). V on left (~-1.65,0.3). A opposite V (~1.65,-0.3). Tangent extending right from P.

### GOLD EXAMPLE — prop_6.room (same construction family, already built!)

Prop. VII uses the identical QR/SP/QT construction as Prop. VI. Study prop_6 for the station structure and the keyword syntax for `foot`, `perp`, `parallel`, `tangent_at`, `segment`, `line`, `arc`, `angle`. Prop. VII differs by adding a `circle_cr` and `tangent_at`, and by having a chord+diameter in station 2.

## RULES

1. Colors local per station. Uncolored = BLACK (never use `color=black` — just omit the color attr).
2. At least one `heart` per station.
3. Every declared color used; every used color declared.
4. Define points BEFORE segments/polygons that reference them.
5. Every geometry op has a NAME as the first token after the op keyword.
6. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences, EDUCATIONAL.
7. Prop. VII depends on Prop. VI — mention this in the text.
8. End final station with `\textit{Q.E.D.}`. Use `\` at end of line for long lines.

Return ONLY the `.room` file text.
