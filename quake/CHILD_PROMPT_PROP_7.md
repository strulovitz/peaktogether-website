# QUAKE CHILD PROMPT — prop_7.room

You are a Quake content child. Write ONE `.room` file for prop_7. Return ONLY the `.room` file text in a fenced code block.

## ⚠️ CRITICAL — YOU MUST FOLLOW THIS FORMAT EXACTLY ⚠️

The .room format is RIGID. Every station has this fixed structure:
```
station N
  gloss <one sentence>
  color <name> <#hex>
  panel
    <ops...>
  text
    <prose with {colorname|words} and $math$>
```

Every station re-defines all its own points. No "shared" geometry across stations.

## COMPLETE WORKING EXAMPLE (prop_6.room — THIS COMPILES!)

Study this EXACTLY. Your file must look like this:

```
room      prop_6
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition VI; Plate 3, Figure 2.
caption   In a space void of resistance, the centripetal force in the middle of a nascent arc is as the versed sine directly and the square of the time inversely.
final     4
ceiling   prop6 :: F \propto \dfrac{\text{versed sine}}{t^2} \qquad F \propto \dfrac{1}{SP^2\cdot QT^2/QR}

station 1
  gloss The centre S, the body at P, and the tiny nascent arc PQ pose the measurement problem.
  color centerorange #E8770A
  color arcblue #1E6FE0
  panel
    point S @(-2.6,-2.2) color=centerorange label=$S$ at=SW marker=dot
    point P @(2.4,1.9) label=$P$ at=NE marker=dot
    point Q @(1.55,2.55) label=$Q$ at=N marker=dot
    arc P Q S color=arcblue heart
    segment SP S P
  text
    Place the {centerorange|centre of force $S$} and let the body ride the curve at $P$. In the very next \
    instant it sweeps the {arcblue|nascent arc $PQ$ — the body's path in the least time}, and this arc is the \
    heart of everything that follows. Prop. I already told us that a central force makes the areas swept \
    proportional to the times — but it never told us HOW STRONG the force is.

station 2
  gloss The tangent ZPR is the forceless path; the versed sine measures how far the body falls from it.
  color tangreen #00A35A
  panel
    point S @(-2.6,-2.2) label=$S$ at=SW marker=dot
    point P @(2.4,1.9) label=$P$ at=E marker=dot
    point Q @(1.55,2.55) label=$Q$ at=N marker=dot
    point Z @(3.4,0.9) label=$Z$ at=SE
    point R @(1.35,0.75) label=$R$ at=S
    arc P Q S
    line ZPR Z R color=tangreen heart label=$\text{tangent }ZPR$ at=E
    segment SP S P
    segment QR Q R
  text
    Draw the {tangreen|tangent $ZPR$ at $P$} — the straight path the body WOULD take if the force suddenly \
    vanished. The versed sine $QR$ measures how far the curve pulls away from that tangent.

station 3
  gloss QR is drawn parallel to SP and QT perpendicular to SP.
  color parblue #1E6FE0
  color perpred #D81B60
  panel
    point S @(-2.6,-2.2) label=$S$ at=SW marker=dot
    point P @(2.4,1.9) label=$P$ at=E marker=dot
    point Q @(1.55,2.55) label=$Q$ at=N marker=dot
    point Z @(3.4,0.9) label=$Z$ at=SE
    point R @(1.9,1.05) label=$R$ at=SE
    foot T from Q to S P label=$T$ at=SW
    arc P Q S
    line ZPR Z R
    segment SP S P
    parallel QR through Q to S P color=parblue heart label=$QR\parallel SP$ at=NE
    perp QT through Q to S P color=perpred heart label=$QT\perp SP$ at=W
    angle QTP Q T P
  text
    Here is Newton's decisive stroke: draw {parblue|$QR$ PARALLEL to the radius $SP$}. Then drop \
    {perpred|$QT$ PERPENDICULAR to $SP$}, giving a right angle at $T$. The triangle $SQP$ has \
    area $\tfrac{1}{2}\,SP\cdot QT$ — proportional to the time by Prop. I.

station 4
  gloss The force-measure solid is the master formula.
  color measpurple #8E24AA
  panel
    point S @(-2.6,-2.2) label=$S$ at=SW marker=dot
    point P @(2.4,1.9) label=$P$ at=E marker=dot
    point Q @(1.55,2.55) label=$Q$ at=N marker=dot
    point R @(1.9,1.05) label=$R$ at=SE
    point Z @(3.4,0.9) label=$Z$ at=SE
    foot T from Q to S P label=$T$ at=SW
    arc P Q S
    line ZPR Z R
    segment SP S P
    parallel QR through Q to S P
    perp QT through Q to S P
    polygon quad S Q P color=measpurple heart label=$SP^2\!\cdot\!QT^2/QR$ at=center
  text
    Assemble the master key. The versed sine gives $F \propto QR/t^2$, while swept area sets \
    $t \propto SP\cdot QT$; substitute and $F \propto 1/(SP^2\cdot QT^2/QR)$. This single formula \
    unlocks EVERY later proposition. \textit{Q.E.D.}
```

## GEOMETRY OP KEYWORD SYNTAX (MEMORIZE THIS)

Every op has a NAME as the first token after the op keyword:

| Op | Syntax |
|-----|--------|
| `point` | `point <name> @(x,y) label=$L$ at=DIR marker=dot` |
| `segment` | `segment <name> <pt1> <pt2>` |
| `line` | `line <name> <pt1> <pt2>` |
| `ray` | `ray <name> <pt1> <pt2>` |
| `arc` | `arc <pt1> <pt2> <centre>` |
| `circle_cr` | `circle_cr <name> <centre> <radius>` |
| `circle_cp` | `circle_cp <name> <centre> <pt_on_circ>` |
| `circle_3` | `circle_3 <name> <pt1> <pt2> <pt3>` |
| `polygon` | `polygon <name> <pt1> <pt2> ...` |
| `polyline` | `polyline <name> <pt1> <pt2> ...` |
| `parallel` | `parallel <name> through <pt> to <ref_pt1> <ref_pt2>` |
| `perp` | `perp <name> through <pt> to <ref_pt1> <ref_pt2>` |
| `foot` | `foot <name> from <pt> to <line_pt1> <line_pt2>` |
| `tangent_at` | `tangent_at <name> on <curve_name> at <pt>` |
| `angle` | `angle <name> <a_pt> <vertex_pt> <b_pt>` |
| `intersect` | `intersect <name> of <obj1> and <obj2>` |
| `midpoint` | `midpoint <name> of <pt1> <pt2>` |
| `point_on` | `point_on <name> on <curve> at <DIR>` |

Attributes: `color=NAME heart label=$...$ at=DIR marker=dot`

## YOUR ROOM — prop_7

**prop_7 · DIAGRAM · 3 step-pairs · Pl.3 Fig.3 · importance 3**

Apply Prop. VI's QR/SP/QT construction to a CIRCLE with force toward ANY point S (not centre).

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition VII; Plate 3, Figure 3.
caption   If a body revolves in the circumference of a circle, find the law of centripetal force directed to any given point.
final     3
ceiling   prop7 :: F \propto \dfrac{1}{SP^2}\cdot\dfrac{1}{PV^3}

s1 — Circle VQPA → circblue(#1E6FE0); body P; force-point S → centerorange(#E8770A); SP → radgreen(#00A35A) ♥.
s2 — Tangent PRZ → tanteal(#00897B) ♥; chord PV + diameter VA + join AP → diampurple(#8E24AA).
s3 — QT ⟂ SP, LR ∥ SP → constred(#D81B60) ♥; circle geometry → QT²/QR ∝ PV³ → F ∝ 1/(SP²·PV³).

colors_used: circblue, centerorange, radgreen, tanteal, diampurple, constred
```

### Newton's text (verbatim):

> If a body revolves in the circumference of a circle; it is proposed to find the law of centripetal force directed to any given point. Pl. 3. Fig. 3.
>
> Let VQPA be the circumference of the circle; S the given point to which as to a centre the force tends; P the body moving in the circumference; Q the next place into which it is to move; and PRZ the tangent of the circle at the preceding place. Through the point S draw the chord PV, and the diameter VA of the circle, join AP, and draw QT perpendicular to SP, which produced, may meet the tangent PRZ in Z; and lastly, through the point Q draw LR parallel to SP, meeting the circle in L, and the tangent PZ in R. And, because of the similar triangles ZQR, ZTP, ZPA we shall have RP² (that is, QRL) to QT² as AV² to PV². And therefore QRL × PV² / AV² is equal to QT². Multiply those equals by SP²/QR, and the points P and Q coinciding, PV²/AV² becomes unity. Write PV for the chord; and the force (by cor. 1 and 5 prop. 6) will become reciprocally as SP² × PV³.

### Figure layout (Pl.3 Fig.3):
- A circle with centre O, radius ~5. Point S is inside (not centre), e.g. (1.0, -0.5)
- P on the right side of circumference (body's position)
- Q on the upper-left of circumference (next position, nearby)
- Tangent PRZ at P extending rightward
- Chord PV through S to far side V
- Diameter VA through V (through centre O)
- Join AP
- QT ⟂ SP (foot T on SP)
- LR ∥ SP through Q, meeting tangent at R

### GUIDANCE

**Station 1 — Circle and Force Centre:** Draw the circle (center O, radius ~5). Place S inside. P and Q on circumference. Draw circle, S, and SP. Heart: radgreen SP. Text: introduce the circle as simplest orbit, S not at centre — the challenge.

**Station 2 — Tangent, Chord, Diameter:** Add tangent PRZ at P, chord PV through S, diameter VA through V (through O), join AP. Heart: tanteal tangent. Text: tangent = forceless path, chord+diameter unlock circle geometry, VA is diameter so ∠VPA is right angle.

**Station 3 — Construction and Force Law:** Add QT ⟂ SP (foot T), LR ∥ SP through Q, point R on tangent. Heart: constred QT and LR. Text: similar triangles ZQR,ZTP,ZPA → QT²/QR ∝ PV³ → F ∝ 1/(SP²·PV³). When S=centre, PV=diameter → 1/SP². Q.E.D.

## ⛔ DO NOT
- Use `#` comments
- Invent your own format (no `s1`/`s2` section labels)
- Define points outside `station` blocks
- Skip `station N` / `gloss` / `color` / `panel` / `text` markers
- Forget the NAME on geometry ops
- Use `color=black` (black is default, omit)

Return ONLY the `.room` file text.
