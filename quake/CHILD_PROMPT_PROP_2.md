# QUAKE CHILD PROMPT — prop_2.room

You are a Quake content child. Write ONE `.room` file for prop_2. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — prop_2

**prop_2 · DIAGRAM · 3 step-pairs · (reuses Prop. I triangle-fan figure) · importance 4**

THE CONVERSE. Proposition I proved: central force ⇒ equal areas in equal times. Proposition II proves the REVERSE: equal areas in equal times ⇒ the force must be centripetal (pointed toward S). The proof is short and elegant — it reuses Prop. I's triangle-fan figure and runs the logic backward. If you know the triangles SAB, SBC, SCD are equal, then elementary geometry forces the deflection cC to be parallel to BS, which means the impulse points toward S.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition II; (reuses Prop. I figure).
caption   Every body that moves in a curve and describes areas proportional to the times about a point is urged by a centripetal force directed to that point.
final     3
ceiling   prop2 :: \text{areas} \propto \text{times} \;\Rightarrow\; F \to S

s1 — Curve + centre S → centerorange(#E8770A); equal triangles SAB,SBC,SCD → fanpurple(#8E24AA) ♥ in equal times.
s2 — At B, deflection from rectilinear course (by Law 1): line parallel to cC → deflectblue(#1E6FE0) ♥, i.e. directed along BS.
s3 — Force always directed to S: radial lines BS, CS → radialred(#D81B60) ♥ ⇒ centripetal.

colors_used: centerorange, fanpurple, deflectblue, radialred
```

### Newton's text (verbatim, 1729 Motte, Book I, Section II, Proposition II):

> Every body, that moves in any curve line described in a plane, and by a radius, drawn to a point either immoveable, or moving forward with an uniform rectilinear motion, describes about that point areas proportional to the times, is urged by a centripetal force directed to that point.
>
> Case 1. For every body that moves in a curve line, is (by law 1.) turned aside from its rectilinear course by the action of some force that impels it. And that force by which the body is turned off from its rectilinear course, and is made to describe, in equal times, the equal least triangles SAB, SBC, SCD, &c. about the immovable point S, (by prop. 40. book 1. elem. and law 2.) acts in the place B, according to the direction of a line parallel to cC, that is, in the direction of the line BS; and in the place C, according to the direction of a line parallel to dD, that is, in the direction of the line CS, &c. And therefore acts always in the direction of lines tending to the immovable point S. Q. E. D.
>
> Case 2. And (by cor. 5. of the laws) it is indifferent whether the superficies in which a body describes a curvilinear figure be quiescent, or moves together with the body, the figure describ'd, and its point S, uniformly forwards in right lines.

### GUIDANCE

Prop. II is the converse of Prop. I — and it's shorter and simpler! It reuses the exact same figure (the triangle-fan with centre S and polygonal path ABC...), but this time the equal-area condition is the PREMISE, and centripetal force is the CONCLUSION.

**The logic in one breath:** If triangles SAB, SBC, SCD are equal (areas ∝ times by assumption), then by Euclid's Elements Book I Prop. 40, triangles on the same base between the same parallels are equal → the deflection cC at B must be parallel to BS → the impulse points toward S → centripetal force. Repeat at every vertex → the force is always toward S.

**Step 1 — The Given:** Draw the same figure as Prop. I: centre S, a curve (or its polygonal approximation ABC...), and the swept triangles SAB, SBC, SCD. The {centerorange|centre S} is fixed. The {fanpurple|triangles SAB, SBC, SCD — all equal} are the heart. Unlike Prop. I where we PROVED they're equal, here it is GIVEN: the body sweeps equal areas in equal times. In the text, explain: "Prop. I showed us that central force produces equal areas. Now we ask the reverse question: if we OBSERVE equal areas (as Kepler did for Mars), can we conclude the force is central?" This is the "observational → theoretical" direction.

**Step 2 — The Deflection:** Focus on vertex B. By Law I, if no force acted, the body would continue straight from B — but it doesn't, it turns toward C. Some force must deflect it. The equal-triangle condition SBC = SAB means (by Euclid I.40) that line cC must be {deflectblue|parallel to BS — the deflection points along the radius} — the heart. In the text: "Euclid's Prop. 40: equal triangles on the same base (here SB) lie between the same parallels. Since SBC equals SAB equals SBc, the vertex C must lie on a line through c parallel to SB. The force impulse that bent the body from Bc to BC was therefore directed EXACTLY along BS — toward the centre."

**Step 3 — Centripetal:** The same argument applies at C (dD ∥ CS), at D, at every vertex. The {radialred|radial lines BS, CS — the force direction at every point} is the heart. Each deflection arrow is parallel to the radius at that point → the force always points toward S → centripetal. Q.E.D. In the text: "So the equal-area observation alone is enough to guarantee that whatever pushes the body pushes it straight toward S. The force could be strong or weak, varying with distance however it likes — the direction is locked. This is the test: watch a planet, measure its swept areas — if equal in equal times, the Sun is pulling on it."

**Figure layout (same as Prop. I, Pl.2 Fig.5):**
- Centre S (above the path)
- Polygonal path A → B → C → D → E
- Radii SA, SB, SC, SD
- At B: show the parallelogram: Bc (inertial continuation), cC (deflection parallel to BS), actual path BC
- Triangles SAB, SBC, SCD shaded or outlined to show they're equal
- Deflection arrows at B (cC) and C (dD) pointing toward S

### GOLD EXAMPLE — prop_1.room (SAME FIGURE!)

Prop. II reuses the identical figure as Prop. I. The difference is purely logical: in Prop. I, the impulse was GIVEN and we PROVED equal triangles; in Prop. II, equal triangles are GIVEN and we PROVE the impulse points toward S. Study prop_1's construction — replicate the triangle-fan figure but with 3 stations and the reversed logical flow:

- Station 1: Same as prop_1 s1+s2 combined — centre + curve/radii + equal triangles (given!)
- Station 2: The deflection geometry — Bc, cC ∥ BS
- Station 3: Generalize — the force is centripetal at every vertex

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey. Never use `color=black` (omit).
2. At least one `heart` per station (with color explicitly set in panel).
3. Every used color declared; every declared color used.
4. Define point ops BEFORE segments/polygons/polyline that reference them.
5. In `polyline name A B C`, only points go after the name — labels/names go in `label=` attr. NO extra words in the point list!
6. Text: `{colorname|words}` spans + `$math$`. 3–4 sentences per panel, EDUCATIONAL.
7. Prop. II depends on Law I, Law II, and Prop. I (its converse) — mention these.
8. End final station with `\textit{Q.E.D.}`
9. `\` at end of line to continue long lines.

Return ONLY the `.room` file text.
