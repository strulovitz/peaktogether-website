# QUAKE CHILD PROMPT — lemma_5.room

You are a Quake content child. Write ONE `.room` file for lemma_5. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER (before first station):
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#> | ceiling <eq_id> :: <verbatim LaTeX>   (repeat ceiling per equation)

COLOR RULE: colors are local per station; matching words in text share them; uncolored
= plain BLACK (never grey); exactly the step's HEART element carries `heart`.

GEOMETRY ops:  point  mid  on  intersect  midpoint  foot  reflect
  segment  line  ray  parallel  perp  tangent_at  tangent_from  bisector
  circle_cp  circle_cr  circle_3  arc  ellipse_foci  ellipse_axes
  parabola_fd  hyperbola_foci  conic_5  polygon  polyline  series  angle

  Attr tokens: color=NAME heart label=$..$ at=DIR marker=dot stabilo=#hex @(x,y)
  DIR = N|S|E|W|NE|NW|SE|SW|center

EQUATION ops:  term <colorname> $<latex>$ [heart]
TEXT ops:      phrase <colorname> "<words>" [heart]
All kinds: optional `layout $...$` with {name|$frag$} spans for structured eq.

One STATION per step, contiguous from 1:
  station <n>
    gloss <one sentence>
    color <name> <#hex>            (repeat; LOCAL to this station)
    panel
      <ops — see above>
    text
      <prose with {colorname|words} spans and $math$>
```

## YOUR ROOM — lemma_5

**lemma_5 · DIAGRAM · 2 step-pairs · Pl.2 Fig.1**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma V; Plate 2, Fig. 1.
caption   In similar figures all homologous sides are proportional, and the areas are in the duplicate ratio of the homologous sides.

s1 — Two similar figures side by side; figure 1 → simblue(#1E6FE0), figure 2 → simgreen(#00A35A); homologous boundary ♥ (the pair together).
s2 — Marked homologous sides → sideorange(#E8770A) ♥; areas in duplicate ratio.

colors_used: simblue, simgreen, sideorange
ceiling: \text{sides} \propto \text{homologous} \cdot \text{areas} \propto (\text{side})^2
```

### Newton's text (verbatim, from the 1729 Motte translation):

"In similar figures, all sorts of homologous sides, whether curvilinear or rectilinear, are proportional; and the area's are in the duplicate ratio of the homologous sides."

### GUIDANCE

Newton's text is just one sentence — don't worry. The **text panels** are where you teach the player. Write clear, friendly prose that EXPLAINS what the figure shows. Each station's text panel should stand on its own as a mini-lesson.

This is a **geometry** (DIAGRAM) room. On the panel: draw TWO similar figures side-by-side (e.g. two similar triangles, one larger and one smaller — simple and clear). Label their vertices. Mark their homologous sides in step 2.

**Step 1 (text panel):** Introduce the two similar figures. Explain what "similar" means in plain words: same shape, different size, all angles equal, corresponding sides in the same proportion. The {simblue|first figure} and {simgreen|second figure} are displayed — their shared shape (the homologous boundary) is the heart. Write at least 3–4 sentences — enough to teach the concept.

**Step 2 (text panel):** Pick one pair of homologous sides (e.g. AB in figure 1 ↔ DE in figure 2). Explain that ALL homologous sides share the same ratio, call it k. Then explain that the AREAS are in the duplicate ratio k² — if the big figure's sides are 2× the small one's, its area is 4×. The {sideorange|homologous sides} are the heart. Write at least 4–5 sentences — this is THE payoff of the lemma. End with "Q.E.D." or a concluding sentence.

**Ceiling:** Two short equations restating the result. Keep them clean and readable.

## GOLD EXAMPLE — lemma_2.room (geometry, for reference)

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

1. Colors are LOCAL per station. Same concept may get different colors or none in another station.
2. Every station must have exactly one `heart` element (the Stabilo highlight for that step).
3. Uncolored elements = BLACK. Never grey.
4. Every color you use in ops/text spans must be declared with `color <name> <#hex>`.
5. Every declared color must be used.
6. Geometry ops: every Name must be defined by an earlier op before being referenced.
7. The `text` block: use `{colorname|words}` spans for colored text. Use `$math$` for LaTeX math.
8. Ceiling equations: verbatim LaTeX between `::` delimiters.
9. `@(x,y)` on point ops is a rough visual hint (cosmetic, no math precision needed).
10. Use `\\` at end of line to continue long lines.

Return ONLY the `.room` file text.
