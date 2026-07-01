# QUAKE CHILD PROMPT — prop_6.room

You are a Quake content child. Write ONE `.room` file for prop_6. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER:
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#> | ceiling <eq_id> :: <verbatim LaTeX>

GEOMETRY ops: point point_on intersect midpoint foot reflect
  segment line ray parallel perp tangent_at tangent_from bisector
  circle_cp circle_cr circle_3 arc ellipse_foci ellipse_axes
  parabola_fd hyperbola_foci conic_5 polygon polyline series angle

  Attrs: color=NAME heart label=$..$ at=DIR marker=dot @(x,y)
  DIR = N|S|E|W|NE|NW|SE|SW|center

STATION:
  station <n>
    gloss <one sentence>
    color <name> <#hex>
    panel
      <ops>
    text
      <prose with {colorname|words} spans and $math$>
```

## YOUR ROOM — prop_6

**prop_6 · DIAGRAM · 4 step-pairs · Pl.3 Fig.2 · ★★★ IMPORTANCE 5 ★★★**

THE FORCE MEASURE. This is the practical workhorse of all celestial mechanics in the Principia. Prop. I proved areas ∝ times. Prop. VI now gives the FORMULA: what is the actual centripetal force, expressed in terms of the orbit's geometry? The answer: construct the tangent ZPR at P, draw QR ∥ SP to a nearby point Q on the curve, drop QT ⟂ SP — then F ∝ SP²·QT² / QR in the limit as Q → P. Every later proposition (7, 11, 13) applies this construction to specific curves.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition VI; Plate 3, Figure 2.
caption   In a space void of resistance, the centripetal force in the middle of a nascent arc is as the versed sine directly and the square of the time inversely.
final     4
ceiling   prop6 :: F \propto \dfrac{\text{versed sine}}{t^2} \qquad F \propto \dfrac{1}{SP^2\cdot QT^2/QR}

s1 — Centre S → centerorange(#E8770A), body P, nascent arc PQ → arcblue(#1E6FE0) ♥.
s2 — Tangent ZPR → tangreen(#00A35A) ♥; versed sine bisecting the chord through S.
s3 — QR ∥ SP → parblue(#1E6FE0); QT ⟂ SP → perpred(#D81B60) ♥.
s4 — Force-measure solid SP²·QT²/QR → measpurple(#8E24AA) ♥; force as versed sine ÷ time².

colors_used: centerorange, arcblue, tangreen, parblue, perpred, measpurple
```

### Newton's text (verbatim, 1729 Motte, Book I, Section II, Proposition VI):

> In a space void of resistance, if a body revolves in any orbit about an immoveable centre, and in the least time describes any arc just then nascent; and the versed sine of that arc is supposed to be drawn, bisecting the chord, and produced passing through the centre of force: the centripetal force in the middle of the arc, will be as the versed sine directly and the square of the time inversely.
>
> For the versed sine in a given time is as the force (by cor. 4. prop. 1.) and augmenting the time in any ratio, because the arc will be augmented in the same ratio, the versed sine will be augmented in the duplicate of that ratio, (by cor. 2 and 3. lem. 2.) and therefore is as the force and the square of the time. Subduct on both sides the duplicate ratio of the time, and the force will be as the versed line directly and the square of the time inversely. Q. E. D.
>
> Cor. 1. If a body P revolving about the centre S describes a curve line APQ which a right line ZPR touches in any point P; and from any other point Q of the curve, QR is drawn parallel to the distance SP, meeting the tangent in R; and QT is drawn perpendicular to the distance SP: the centripetal force will be reciprocally as the solid SP² × QT² / QR, if the solid be taken of that magnitude which it ultimately acquires when the points P and Q coincide. For QR is equal to the versed sine of double the arc QP, whose middle is P: and double the triangle SQP, or SP × QT is proportional to the time, in which that double arc is described; and therefore may be used for the exponent of the time.

### GUIDANCE

Prop. VI is the PRACTICAL heart of the Principia's dynamics. It answers: given an orbit, how do you actually COMPUTE the force? The answer involves a specific geometric construction at any point P of the orbit:

1. Choose a point P on the orbit. Draw the tangent ZPR.
2. Pick a nearby point Q (infinitesimally close to P). Draw QR parallel to SP (the radius), meeting the tangent at R.
3. Drop QT perpendicular to SP.
4. In the limit Q→P, the centripetal force F ∝ 1 / (SP²·QT²/QR).

This construction (QR ∥ SP, QT ⟂ SP) is the key that unlocks every later proposition.

**Step 1 — The Setting:** Place the centre S and the body at P on a curve. Show the nascent arc PQ — the tiny piece of orbit. The {centerorange|centre S} and the {arcblue|nascent arc PQ — the body's path in the very next instant} is the heart. In the text: introduce the question — "we know from Prop. I that a central force makes areas ∝ times. But HOW STRONG is the force? How do we measure it from the shape of the orbit alone?" This is the measurement problem.

**Step 2 — Tangent and Versed Sine:** Draw the tangent ZPR at P (the direction the body WOULD go if the force vanished). The versed sine is the line QR — from a nearby point Q on the curve, drawn to the tangent, bisecting the chord. The {tangreen|tangent ZPR — the forceless path} is the heart. In the text: "if no force acted, the body would fly off along the tangent. The distance it falls away from the tangent — the versed sine QR — measures the pull. By Cor. 4 of Prop. I, in a given time this fall is proportional to the force."

**Step 3 — The Auxiliary Construction:** The clever part: draw QR NOT directly to the tangent, but PARALLEL to SP (the radius). This makes QR ∥ SP. Then drop QT from Q perpendicular to SP. Now we have a right triangle involving the force direction. The {parblue|parallel QR ∥ SP} and the {perpred|perpendicular QT ⟂ SP} is the heart. In the text: "Newton makes QR parallel to the radius SP — this makes QR bypass the tangent, and connects the geometry of the orbit directly to the direction of the force. QT is perpendicular to SP, so the triangle SQP has area ½·SP·QT — and by Prop. I, this area is proportional to the time."

**Step 4 — The Force Formula:** The payoff: QR is the versed sine → F ∝ QR/t² (by the main proof). But t ∝ SP·QT (the area of the triangle swept in that time). Substitute and rearrange: F ∝ 1 / (SP²·QT²/QR). The {measpurple|force-measure solid SP²·QT²/QR} is the heart. In the text: "this formula is the master key. For any curve, pick P and nearby Q, draw QR ∥ SP and QT ⟂ SP, compute the limit of SP²·QT²/QR as Q→P, and you have the force. Props. 7, 11, and 13 will apply this construction to circles, ellipses, and parabolas respectively — it is the single most used formula in all of Book I."

**Figure layout (Pl.3 Fig.2):**
- Centre S, body P on a curve (the orbit arcs up or around)
- Tangent ZPR at P — a straight line touching the curve
- Nearby point Q on the curve, very close to P
- QR drawn PARALLEL to SP, meeting the tangent at R
- QT drawn PERPENDICULAR to SP from Q
- The construction should clearly show the right angle at T, the parallel QR ∥ SP, and the tiny arc PQ

### GOLD EXAMPLE — prop_1.room (centre + orbiting body figure family)

Prop. VI extends the Prop. I figure with a tangent, a parallel, and a perpendicular. Study prop_1 for the centre + orbit layout pattern. The key addition in prop_6 is the specific QR-T construction.

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey. Never use `color=black` (omit — black is default).
2. At least one `heart` per station (with color explicitly set in panel).
3. Every used color declared with `color <name> #<hex>`; every declared color used.
4. Define point ops BEFORE segments/polygons/polyline referencing them.
5. `polyline name A B C` — only points after name, labels via `label=` attr.
6. Header: each keyword (`room`, `kind`, `import`, `caption`, `final`, `ceiling`) on its OWN line — NEVER pipe-separated.
7. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences, EDUCATIONAL.
8. Prop. VI depends on Prop. I (Cor. 4), Lemma II (Cor. 2,3), and Lemma X (Cor. 4) — mention these.
9. End final station with `\textit{Q.E.D.}`
10. `\` at end of line to continue long lines.

Return ONLY the `.room` file text.
