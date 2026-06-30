# QUAKE CHILD PROMPT — lemma_3.room

You are a Quake content child. Write ONE `.room` file for lemma_3. Return ONLY the `.room` file text (in a fenced code block).

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
    color <name> <#hex>
    panel
      <ops>
    text
      <prose with {colorname|words} spans and $math$>
```

## YOUR ROOM — lemma_3

**lemma_3 · DIAGRAM · 2 step-pairs · (shares Pl.1 Fig.6 context with Lemma II)**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma III; Plate 1, Fig. 6.
caption   The same ultimate equality of inscribed and circumscribed figures holds even when the breadths of the parallelograms are unequal.

s1 — Unequal-breadth rectangles under the curve: stepped rectangles → stepblue(#1E6FE0) ♥; baseline AF..AE → basegreen(#00A35A).
s2 — Bounding parallelogram FAaf → boundred(#D81B60) ♥ shrinking as greatest breadth AF → 0; greatest breadth AF → widthorange(#E8770A).

colors_used: stepblue, basegreen, boundred, widthorange
ceiling: FAaf > (\text{circ}-\text{insc}) \cdot AF\to0 \;\Rightarrow\; FAaf\to0
```

### Newton's text (verbatim, 1729 Motte, Book I, Section I, Lemma III):

> The same ultimate ratio's are also ratio's of equality, when the breadths AB, BC, DC, &c., of the parallelograms are unequal, and are all diminished in infinitum.
>
> For suppose AF equal to the greatest breadth, and compleat the parallelogram FAaf. This parallelogram will be greater than the difference of the inscrib'd and circumscribed figures; but, because its breadth AF is diminished in infinitum, it will become less than any given rectangle. Q.E.D.

### GUIDANCE

This is a short extension of Lemma II. The earlier lemma assumed EQUAL bases under the curve. This lemma says: the result holds even for UNEQUAL breadths. The proof: take the widest base AF, build a rectangle FAaf that traps the error, and since AF shrinks to nothing, so does the error.

**The figure:** Same general scene as Lemma II (Pl.1 Fig.6) — a curve aE above a baseline AE, with rectangles under it. But here the bases are UNEQUAL widths (AB wider, BC narrower, etc.). The key visual is the bounding parallelogram FAaf on the widest base.

**Step 1:** Draw the curve aE, the baseline from A to E, and several UNEQUAL-width rectangles under the curve (wider then narrower). The {stepblue|stepped rectangles} are the heart — show them with visibly different widths.

**Step 2:** Identify the greatest breadth AF. Draw the {boundred|bounding parallelogram FAaf} sitting on this widest base. Show that it contains the whole error between inscribed and circumscribed. As {widthorange|the greatest breadth AF} shrinks, the bound → 0, so the error → 0. The {boundred|parallelogram FAaf} is the heart. 4–5 sentences. End Q.E.D.

**Practical:** Use `series` op (like lemma_2 does) for the rectangles? No — `series` expects equal bases. Since these are UNEQUAL, use free-hand `point` + `polygon` for the rectangles, or use a `polyline` for the curve and manually draw a few rectangles as `polygon` ops.

Simplest approach:
- Free points for the baseline (A, F, B, C, D, E at various x-spacings — uneven!)
- A `polyline` curve above them
- A few `polygon` rectangles (manually as individual shapes) with unequal widths
- The bounding parallelogram FAaf on the widest base

## GOLD EXAMPLE — lemma_2.room (same figure family, equal bases)

```
room      lemma_2
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6.
caption   Inscribed and circumscribed parallelograms on equal bases under the curve aE; as the bases shrink, the inscribed and circumscribed figures and the curvilinear figure become ultimately equal.
final     3
ceiling   eq0 :: \lim_{AB \to 0}\; \bigl(\text{circumscribed} - \text{inscribed}\bigr) = ABla \;\longrightarrow\; 0
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
    In the figure $AacE$, bounded by the right lines $\{sideorange|Aa}$ and $\{basegreen|AE}$ and by \{curveblue|the curve $acE$}, take any number of \emph{equal} bases $AB$, $BC$, $CD$, $\&c.$ along \{basegreen|the base $AE$}. This is the curvilinear figure whose area we mean to measure.

station 2
  gloss   The inscribed parallelograms Ab, Bc, Cd, standing under the curve on the equal bases.
  color   inscpurple #8E24AA
  color   sideorange #E8770A
  color   curveblue  #1E6FE0
  panel
    series inscribed along baseAE to curve count 4 kind inscribed_rects \
           color=inscpurple heart
  text
    On these equal bases erect \{inscpurple|the inscribed parallelograms $Ab$, $Bc$, $Cd$, $\&c.$}, with sides $Bb$, $Cc$, $Dd$ parallel to $\{sideorange|Aa}$. \{inscpurple|The inscribed figure $AKbLcMdD$} lies wholly \emph{under} \{curveblue|the curve}.

station 3
  gloss   The circumscribed parallelograms completed above the curve; their excess over the inscribed figure is the single rectangle ABla, which vanishes as AB shrinks.
  color   circred    #D81B60
  color   curveblue  #1E6FE0
  color   inscpurple #8E24AA
  color   basegreen  #00A35A
  panel
    series circumscribed along baseAE to curve count 4 kind circumscribed_rects \
           color=circred heart
  text
    Complete \{circred|the circumscribed parallelograms $aKbl$, $bLcm$, $cMdn$, $\&c.$}, rising \emph{above} \{curveblue|the curve}. Their excess over \{inscpurple|the inscribed figure} is the sum $Kl + Lm + Mn + Do$, equal to the single rectangle $ABla$ on the base $\{basegreen|AB}$. As $\{basegreen|AB}$ is diminished \emph{in infinitum} this rectangle becomes less than any given space; hence (by Lem.~I) \{inscpurple|the inscribed} and \{circred|the circumscribed} figures, and therefore the intermediate curvilinear figure, become ultimately equal. \textit{Q.E.D.}
```

## RULES

1. Colors LOCAL per station. Uncolored = BLACK. Never grey.
2. At least one `heart` per station.
3. Every used color declared; every declared color used.
4. Define geometry ops before referencing them.
5. Text: `{colorname|words}` spans + `$math$`. EDUCATIONAL — 4–5 sentences each.
6. `@(x,y)` on point ops = cosmetic hint only.
7. End final text with \textit{Q.E.D.} or a concluding sentence.
8. `\\` at end of line to continue long lines.
9. Since bases are UNEQUAL, do NOT use `series` (which expects equal spacing). Draw individual `polygon` rects or use free points + manual polygons.
10. Lemma III depends on Lemma II — mention Lemma II in the text where appropriate ("by Lem. II").

Return ONLY the `.room` file text.
