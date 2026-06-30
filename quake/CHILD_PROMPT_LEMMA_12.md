# QUAKE CHILD PROMPT — lemma_12.room

You are a Quake content child. Write ONE `.room` file for lemma_12. Return ONLY the `.room` file text (in a fenced code block).

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

One STATION per step:
  station <n>
    gloss <one sentence>
    color <name> <#hex>            (LOCAL to this station)
    panel
      <ops>
    text
      <prose with {colorname|words} spans and $math$>
```

## YOUR ROOM — lemma_12

**lemma_12 · DIAGRAM · 1 step-pair · Pl.4 Fig.1 (reused)**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I (Lemma XII cited later in Prop. XI); Plate 4, Fig. 1.
caption   All parallelograms described about conjugate diameters of a given ellipse or hyperbola are equal to one another.

s1 — Ellipse → ellblue(#1E6FE0); conjugate diameters → conjorange(#E8770A); circumscribed parallelogram → pargreen(#00A35A) ♥ (constant area = 4ab).

colors_used: ellblue, conjorange, pargreen
ceiling: \text{parallelogram about conjugate diameters} = \text{const} = 4ab
```

### Newton's text (1729 Motte):

Newton gives essentially no proof — he cites Apollonius:

> "This is demonstrated by the writers on the conic sections."

### GUIDANCE

This is the SIMPLEST room in the whole level — just **one step**. But it's elegant. Draw an ellipse, pick one pair of conjugate diameters (two lines through the center that bisect each other's parallel chords), and draw the circumscribed parallelogram whose sides are tangent to the ellipse at the endpoints of those diameters. The heart = the parallelogram (constant area).

**The figure:** An ellipse centered at origin, wider than tall. Two conjugate diameters crossing at the center (not perpendicular — conjugate diameters are skewed). A parallelogram circumscribed about the ellipse, touching it at the four endpoints of the diameters.

**Step 1 (ONLY step):** Draw the {ellblue|ellipse}. Draw one pair of conjugate diameters (e.g., one roughly horizontal-ish, one roughly vertical-ish but skewed — they need NOT be perpendicular; that's the key point). Draw the {pargreen|circumscribed parallelogram} touching the ellipse at the four diameter endpoints. The text explains: for a given ellipse, every parallelogram through conjugate diameters has the SAME area = 4ab, where a and b are the semi-axes. This is an Apollonius result that Newton uses later. 4–5 sentences in the text panel. End with Q.E.D. or "This is demonstrated by the writers on the conic sections."

**Practical:** Use `ellipse_axes` to define the ellipse (center at origin, major and minor endpoints). Then use `point_on` to place two conjugate-diameter endpoints (rough positions, no math precision needed — the visual is enough). The parallelogram uses `polygon` with the four tangent points.

## GOLD EXAMPLE — lemma_5.room (1 fewer station than you need, but close)

```
room      lemma_5
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma V; Plate 2, Fig. 1.
caption   In similar figures all homologous sides are proportional, and the areas are in the duplicate ratio of the homologous sides.
final     2
ceiling   eq0 :: \frac{AB}{DE} \;=\; \frac{BC}{EF} \;=\; \frac{CA}{FD} \;=\; k
ceiling   eq1 :: \frac{\text{area}_1}{\text{area}_2} \;=\; k^2

station 1
  gloss   Two similar triangles displayed side by side: a larger figure ABC and a smaller figure DEF of the very same shape.
  color   simblue   #1E6FE0
  color   simgreen  #00A35A
  panel
    point   A @(0,0)    color=simblue marker=dot label=$A$ at=SW
    point   B @(4,0)    color=simblue marker=dot label=$B$ at=SE
    point   C @(1.2,3)  color=simblue marker=dot label=$C$ at=N
    polygon fig1 A B C  color=simblue heart
    point   D @(6,0)    color=simgreen marker=dot label=$D$ at=SW
    point   E @(8,0)    color=simgreen marker=dot label=$E$ at=SE
    point   F @(6.6,1.5) color=simgreen marker=dot label=$F$ at=N
    polygon fig2 D E F  color=simgreen heart
  text
    Here stand two \emph{similar} figures ...

station 2
  gloss   One pair of homologous sides AB and DE is highlighted ...
  color   sideorange #E8770A
  color   simblue    #1E6FE0
  color   simgreen   #00A35A
  panel
    point   A @(0,0)    color=simblue marker=dot label=$A$ at=SW
    point   B @(4,0)    color=simblue marker=dot label=$B$ at=SE
    point   C @(1.2,3)  color=simblue label=$C$ at=N
    polygon fig1 A B C  color=simblue
    point   D @(6,0)    color=simgreen marker=dot label=$D$ at=SW
    point   E @(8,0)    color=simgreen marker=dot label=$E$ at=SE
    point   F @(6.6,1.5) color=simgreen label=$F$ at=N
    polygon fig2 D E F  color=simgreen
    segment sideAB A B  color=sideorange heart
    segment sideDE D E  color=sideorange heart
  text
    ... duplicate ratio $k^2$ ...
```

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey.
2. At least one `heart` per station.
3. Every used color must be declared. Every declared color must be used.
4. Geometry refs: define before referencing.
5. Text panels: `{colorname|words}` spans + `$math$`.
6. `@(x,y)` on points = rough visual hint only.
7. Text panels = EDUCATIONAL (4–5 sentences). End with \textit{Q.E.D.} or concluding sentence.
8. Point op with `marker=dot` puts a dot at that coordinate.

Return ONLY the `.room` file text.
