# QUAKE CHILD PROMPT — lemma_4.room

You are a Quake content child. Write ONE `.room` file for lemma_4. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — lemma_4

**lemma_4 · DIAGRAM · 3 step-pairs · Pl.1 Fig.7**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma IV; Plate 1, Fig. 7.
caption   If corresponding parallelograms in two figures share one ultimate ratio each-to-each, then the whole figures are in that same ratio.

s1 — First figure AacE with its rectangle rank → figaviolet(#8E24AA) ♥
s2 — Second figure PprT with its rectangle rank → figbteal(#00897B) ♥
s3 — Correspondence lines pairing rank-to-rank → corrorange(#E8770A) ♥; the shared ultimate ratio k.

colors_used: figaviolet, figbteal, corrorange
ceiling: pairs in constant ratio k → whole figures in ratio k (by Lem. 3)
```

### Newton's text (verbatim, 1729 Motte, Book I, Section I, Lemma IV):

> If in two figures AacE, PprT, (Pl.i.Fig.7.) you inscribe (as before) two ranks of parallelograms, an equal number in each rank, and when their breadths are diminished in infinitum, the ultimate ratio's of the parallelograms in one figure to those in the other each to each respectively, are the same; I say that those two figures AacE, PprT, are to one another in that same ratio.
>
> For as the parallelograms in the one are severally to the parallelograms in the other, so (by composition) is the sum of all in the one to the sum of all in the other; and so is the one figure to the other, because (by Lem. 3.) the former figure to the former sum, and the latter figure to the latter sum are both in the ratio of equality. Q. E. D.

### GUIDANCE

This lemma compares TWO figures. Each has its own inscribed rectangle rank (same number of rectangles per figure). If the corresponding rectangle pairs share a constant ratio k (1st rectangle in figure A : 1st rectangle in figure B = k, and so on), then the whole figures also share that ratio k.

**The figure (Pl.1 Fig.7):** Two curves, one labeled AacE (like Lemma II's figure) and another PprT (different shape, curving differently). Both have equal-count rectangle ranks inscribed under them.

**Step 1:** Draw the FIRST figure — curve aE over baseline AE, with inscribed rectangles (say 3 rectangles). Use `series` (like lemma_2) if you want uniform bases, or free points + individual polygons. The {figaviolet|first figure AacE with its inscribed rectangles} is the heart.

**Step 2:** Draw the SECOND figure — a DIFFERENT curve PrT over baseline PT, same count of rectangles (3). The shape should look different from step 1 (e.g. leans differently, different height). The {figbteal|second figure PprT with its own rectangle rank} is the heart.

**Step 3:** Draw correspondence — thin lines connecting each 1st-figure rectangle to its paired 2nd-figure rectangle (e.g. arrow-like connecting segments). The text explains: each rectangle pair has the same ratio k, so by composition the sums have ratio k, and by Lem. III each sum equals its figure → the figures are in ratio k. The {corrorange|correspondence lines} are the heart. 4–5 sentences. End Q.E.D.

**Layout:** Stack the two figures vertically (first figure above, second below) with space for correspondence lines between them.

## GOLD EXAMPLE — lemma_2.room (single figure with series)

```
room      lemma_2
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6.
caption   Inscribed and circumscribed parallelograms on equal bases under the curve aE; as bases shrink, inscribed and circumscribed figures and the curvilinear figure become ultimately equal.
final     3
ceiling   eq0 :: \lim_{AB \to 0}\; \bigl(\text{circ}-\text{insc}\bigr) = ABla \;\longrightarrow\; 0
ceiling   eq1 :: \text{inscribed} \;=\; \text{circumscribed} \;=\; \text{curvilinear area} \quad (\text{ultimately})

station 1
  gloss   The curvilinear figure AacE: the curve aE, the baseline AE on equal bases, and the side Aa.
  color   curveblue  #1E6FE0
  color   basegreen  #00A35A
  color   sideorange #E8770A
  panel
    point   A @(0,0)   marker=dot label=$A$ at=SW
    point   E @(8,0)   marker=dot label=$E$ at=SE
    point   B @(2,0)   marker=dot label=$B$ at=S
    point   C @(4,0)   marker=dot label=$C$ at=S
    point   D @(6,0)   marker=dot label=$D$ at=S
    point   ptA @(0,1.4)  color=curveblue label=$a$ at=NW
    point   ptb @(2,2.6)  color=curveblue label=$b$ at=N
    point   ptc @(4,3.4)  color=curveblue label=$c$ at=N
    point   ptd @(6,3.9)  color=curveblue label=$d$ at=N
    point   ptE @(8,4.2)  color=curveblue
    polyline curve ptA ptb ptc ptd ptE   color=curveblue heart
    segment baseAE A E   color=basegreen
    segment sideAa A ptA  color=sideorange
  text
    In the figure $AacE$, bounded by ... $\&c.$ along \{basegreen|the base $AE$}.

station 2
  gloss   The inscribed parallelograms under the curve.
  color   inscpurple #8E24AA
  color   sideorange #E8770A
  color   curveblue  #1E6FE0
  panel
    series inscribed along baseAE to curve count 4 kind inscribed_rects \
           color=inscpurple heart
  text
    On these equal bases erect \{inscpurple|the inscribed parallelograms $Ab$, $Bc$, $Cd$, $\&c.$}...

station 3
  gloss   The circumscribed parallelograms above the curve.
  color   circred    #D81B60
  color   curveblue  #1E6FE0
  color   inscpurple #8E24AA
  color   basegreen  #00A35A
  panel
    series circumscribed along baseAE to curve count 4 kind circumscribed_rects \
           color=circred heart
  text
    Complete \{circred|the circumscribed parallelograms}... \textit{Q.E.D.}
```

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey.
2. At least one `heart` per station.
3. Every used color declared; every declared color used.
4. Define geometry ops BEFORE referencing them.
5. Text: `{colorname|words}` spans + `$math$`. 4–5 sentences each, EDUCATIONAL.
6. `@(x,y)` on point ops = cosmetic hint only.
7. Points must be defined BEFORE polygons/segments that reference them.
8. `\\` at end of line to continue long lines.
9. End final station with \textit{Q.E.D.}
10. Lemma IV depends on Lem. III — mention it in the text.

Return ONLY the `.room` file text.
