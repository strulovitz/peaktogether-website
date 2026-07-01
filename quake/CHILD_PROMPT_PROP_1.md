# QUAKE CHILD PROMPT — prop_1.room

You are a Quake content child. Write ONE `.room` file for prop_1. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — prop_1

**prop_1 · DIAGRAM · 4 step-pairs · Pl.2 Fig.5 · ★★★ IMPORTANCE 5 ★★★**

THE FOUNDATION. Proposition I proves the single most important result in Newtonian dynamics: equal areas are swept in equal times by any body moving under ANY central force. This is Kepler's Second Law, generalized from ellipses to all central-force motion. The proof uses Newton's brilliant "impulse approximation" — break time into tiny equal steps, let inertia carry the body forward, then apply a single centripetal thump toward S, and prove the swept triangles are equal. Take the limit and you get a smooth orbit with dA/dt = constant.

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition I; Plate 2, Fig. 5.
caption   The areas which revolving bodies describe by radii drawn to an immoveable centre of force are proportional to the times in which they are described.
final     4
ceiling   prop1 :: \dfrac{dA}{dt} = \text{const}\;( \text{areas} \propto \text{times})

s1 — Centre S → centerorange(#E8770A); polygonal path ABCDE → pathblue(#1E6FE0) ♥.
s2 — Radii SA,SB,SC,SD,SE → radigreen(#00A35A) ♥.
s3 — Swept triangles SAB, SBc, SBC → arearpurple(#8E24AA) ♥ shown equal (innate motion Bc=AB, centripetal Cc∥SB).
s4 — Centripetal impulse at B: Cc ∥ SB → impulsered(#D81B60) ♥; in the limit the polygon → curve, areas ∝ times.

colors_used: centerorange, pathblue, radigreen, arearpurple, impulsered
```

### Newton's text (verbatim, 1729 Motte, Book I, Section II, Proposition I):

> The areas, which revolving bodies describe by radii drawn to an immoveable centre of force, do lie in the same immovable planes, and are proportional to the times in which they are described. Pl. 2. Fig. 5.
>
> For suppose the time to be divided into equal parts, and in the first part of that time, let the body by its innate force describe the right line AB. In the second part of that time, the same would, (by law 1.) if not hinder'd, proceed directly to c, along the line Bc equal to AB; so that by the radii AS, BS, cS drawn to the centre, the equal areas ASB, BSc, would be described. But when the body is arrived at B, suppose that a centripetal force act at once with a great impulse, and turning aside the body from the right line Bc, compells it afterwards to continue its motion along the right line BC. Draw cC parallel to BS meeting BC in C; and at the end of the second part of the time, the body (by Cor. 1. of the laws) will be found in C, in the same plane with the triangle ASB. Joyn SC, and, because SB and Cc are parallel, the triangle SBC will be equal to the triangle SBc, and therefore also to the triangle SAB. By the like argument, if the centripetal force acts successively in C, D, E, &c. and makes the body in each single particle of time, to describe the right lines CD, DE, EF, &c. they will all lye in the same plane; and the triangle SCD will be equal to the triangle SBC, and SDE to SCD, and SEF to SDE. And therefore in equal times, equal areas are describ'd in one immovable plane: and, by composition, any sums SADS, SAFS, of those areas, are one to the other, as the times in which they are describ'd. Now let the number of those triangles be augmented, and their breadth diminished in infinitum; and (by cor. 4. lem. 5.) their ultimate perimeter ADF will be a curve line: and therefore the centripetal force, by which the body is perpetually drawn back from the tangent of this curve, will act continually; and any describ'd areas SADS, SAFS, which are always proportional to the times of description, will, in this case also, be proportional to those times. Q. E. D.

### GUIDANCE

This is THE most important proof in all of Newtonian orbital mechanics — Kepler's Second Law, generalized. The proof works by a beautiful "impulse" trick:

1. Divide time into equal tiny intervals Δt
2. In the first interval, inertia (Law 1) carries the body along AB
3. In the next interval, inertia WOULD carry it to c (with Bc = AB, same speed)
4. BUT at B, a single centripetal impulse toward S thumps the body, deflecting it to C instead
5. Cc is parallel to BS (the impulse is purely toward the centre)
6. Therefore triangle SBC = triangle SBc (same base BS, same height — since Cc ∥ BS)
7. And triangle SBc = triangle SAB (since Bc = AB, same base BS)
8. So SBC = SAB — equal areas swept in equal times!
9. Repeat at C, D, E... all triangles are equal
10. Take the limit Δt → 0, polygon → smooth curve → dA/dt = constant for ANY central force!

**Step 1 — The Stage:** Place the centre S somewhere (not on the path). Draw the polygonal path ABCDEF — the body's discrete-jump trajectory. The {centerorange|centre of force S} is fixed, and the {pathblue|polygonal path ABCDEF} is the heart. In the text: introduce the idea — "imagine time chopped into equal tiny slices. In each slice, the body flies straight by pure inertia... unless a force intervenes." This is the method of first and last ratios applied to MOTION.

**Step 2 — The Radii:** Draw the radii from S to each vertex: SA, SB, SC, SD, SE, SF. These are the "sweeping lines" that trace out the triangles. The {radigreen|radii SA, SB, SC, SD, SE} are the heart. In the text explain: "the radius from S to the body sweeps out an area — if we can show all those little triangles are equal, then area ÷ time is constant." Connect to Kepler: this is exactly what Kepler observed for Mars, but Newton will prove it's true for ANY central force.

**Step 3 — The Triangles are Equal:** Focus on the first three vertices A, B, C. Show the point c (where the body WOULD have gone if left alone, with Bc = AB). Draw the little lines: AB (first motion), Bc (inertial continuation = AB), and the actual path BC. Draw Cc parallel to BS — this is the centripetal deflection. The three key triangles: SAB (first step's area), SBc (would-be area), SBC (actual area). Color them all {arearpurple|areapurple} and make them the heart. Explain the equality chain: SAB = SBc (Bc = AB, same base), SBc = SBC (Cc ∥ BS, same base/height). Text: "Newton's genius — by making the impulse purely toward S, the triangle area is PRESERVED. The force changes the DIRECTION of motion but not the area swept per time."

**Step 4 — The Limit:** Show the full polygonal arc with its alternating inertia + impulse pattern at each vertex. At B: the segment Bc (inertia dashed) and the impulse arrow Cc ∥ BS. The {impulsered|centripetal impulse Cc, always parallel to the radius BS} is the heart. In the text: "repeat at C, D, E... every triangle equals every other. Now let the time-slices shrink to zero — the polygon becomes a smooth curve, and the area swept per unit time becomes the constant dA/dt. This holds for ANY central force, whether it varies with distance or not — the force changes the shape of the orbit but never the equal-area law." End with Q.E.D.

**Figure layout (Pl.2 Fig.5):**
- Centre S placed somewhere (e.g., above-left of the path)
- Polygonal path: A → B → C → D → E → F (several segments, gently curving around)
- Point c near B: show Bc continuing straight from AB (dashed/lightly), with Cc connecting c to C (parallel to BS)
- Radii from S to each vertex (SA, SB, SC...)
- At least the first few triangles (SAB, SBC) clearly visible
- The figure should suggest: the polygon is an approximation; in the limit it becomes a smooth orbit

**Key visual elements:**
- Centre S (centerorange dot)
- Polygonal path ABCDEF (pathblue segments)
- Radii (radigreen lines)
- Point c near B (Bc = AB continuation) and Cc parallel to BS
- Triangles SAB, SBc, SBC (arearpurple fill or outline)
- The impulse arrow at B (impulsered Cc)

### GOLD EXAMPLE — lemma_5.room (geometry with ratio reasoning)

Prop_1 is the first genuine dynamics room — it combines geometry (triangles, parallels, equal areas) with physics (inertia, impulse). The construction style is similar to other diagram rooms. Study lemma_5 for the pattern of declaring colors, building a geometric figure step by step, and writing rich text panels:

```
room      lemma_5
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma V; Plate 1.
caption   In similar figures, all corresponding sides, whether curvilinear or rectilinear, are proportional; and the areas are in the duplicate ratio of the sides.
final     2
ceiling   lem5 :: \frac{AB}{ab} = \frac{BC}{bc} = \cdots \;;\; \frac{\text{area}}{\text{area}'} = \left(\frac{AB}{ab}\right)^2

station 1
  gloss   Two similar rectilinear figures with the same number of sides, paired vertex to vertex.
  color   simblue  #1E6FE0
  color   simgreen #00A35A
  panel
    point    A  @(0,0)    marker=dot label=$A$ at=SW
    point    B  @(2.0,1.5) marker=dot label=$B$ at=NE
    point    C  @(4.0,0.5) marker=dot label=$C$ at=SE
    point    a  @(0.8,3.2) marker=dot label=$a$ at=W
    point    b  @(2.4,4.2) marker=dot label=$b$ at=NE
    point    c  @(3.8,3.5) marker=dot label=$c$ at=E
    polygon  figABC A B C color=simblue heart label=$ABC$ at=NE
    polygon  figabc a b c color=simgreen heart label=$abc$ at=NE
  text
    We place two rectilinear figures {\simblue|$ABC$} and {\simgreen|$abc$} side by side ...

station 2
  gloss   The homologous boundary shares the same ratio as all other pairs of corresponding sides.
  color   sideorange #E8770A
  color   simblue    #1E6FE0
  color   simgreen   #00A35A
  panel
    point    A  @(0,0)
    point    B  @(2.0,1.5)
    point    a  @(0.8,3.2)
    point    b  @(2.4,4.2)
    segment  AB  A B color=sideorange heart label=$AB$ at=SE
    segment  ab  a b color=sideorange heart label=$ab$ at=NW
  text
    The {\sideorange|homologous sides $AB$ and $ab$} ... \textit{Q.E.D.}
```

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey. Never use `color=black` (black is default — omit the color attr).
2. At least one `heart` per station (with the color explicitly set in the panel).
3. Every used color declared with `color <name> #<hex>`; every declared color used somewhere in that station.
4. Define point geometry ops BEFORE segments/polygons that reference them.
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences per panel, EDUCATIONAL — this is the foundation of orbital dynamics! Explain WHY it matters (Kepler's Law generalized, conservation of angular momentum in disguise) and HOW the proof works (impulse approximation).
6. `@(x,y)` on point ops = cosmetic layout hint only.
7. Prop. I depends on Law I, Law II (Cor. 1), and Lemma V (Cor. 4) — mention these in the text.
8. End final station with `\textit{Q.E.D.}`
9. `\` at end of line to continue long lines.
10. This is the single most important Proposition in Book I. Make the text panels SHINE — teach the reader what "equal areas in equal times" means and why it's so profound.

Return ONLY the `.room` file text.
