# QUAKE CHILD PROMPT — lemma_2.room

You are a Quake content child. Write ONE `.room` file for lemma_2. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v2.0 — ceiling inside each station)

```
HEADER (before first station):
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#>

COLOR RULE: colors are local per station; matching words in text share them; uncolored
= plain BLACK (never grey); exactly the step's HEART element carries `heart`.

GEOMETRY ops:  point  mid  on  intersect  midpoint  foot  reflect
  segment  line  ray  parallel  perp  tangent_at  tangent_from  bisector
  circle_cp  circle_cr  circle_3  arc  ellipse_foci  ellipse_axes
  parabola_fd  hyperbola_foci  conic_5  polygon  polyline  series  angle

  Attr tokens: color=NAME heart label=$..$ at=DIR marker=dot stabilo=#hex @(x,y)
  DIR = N|S|E|W|NE|NW|SE|SW|center

One STATION per step, contiguous from 1:
  station <n>
    ceiling <eq_id> :: <LaTeX>     (goes INSIDE the station — one per station)
    gloss <one sentence>
    color <name> <#hex>            (repeat; LOCAL to this station)
    panel
      <ops — see above>
    text
      <prose with {colorname|words} spans and $math$>
```

## YOUR ROOM — lemma_2

**lemma_2 · DIAGRAM · 3 step-pairs · (GOLD room — built by Parent 13; rewrite fresh)**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6.
caption   If in any figure AacE there be inscribed parallelograms on equal bases and circumscribed parallelograms completed: as the bases are diminished without limit, the inscribed, circumscribed, and curvilinear figures have the ultimate ratio of equality.

s1 Curvilinear figure: curve acE → curveblue(#1E6FE0) ♥; base AE → basegreen(#00A35A); side Aa → sideorange(#E8770A).
s2 Inscribed parallelograms Ab,Bc,Cd → inscpurple(#8E24AA) ♥.
s3 Circumscribed parallelograms → circred(#D81B60) ♥; excess = rectangle ABla.

colors_used: curveblue, basegreen, sideorange, inscpurple, circred
```

### Newton's text (verbatim, from the 1729 Motte translation):

If in any figure AacE (Pl.1.Fig.6.) terminated by the right lines Aa, AE, and the curve acE, there be inscrib'd any number of parallelograms Ab, Bc, Cd, etc. comprehended under equal bases AB, BC, CD, etc. and the sides Bb, Cc, Dd, etc. parallel to one side Aa of the figure; and the parallelograms aKbl, bLcm, cMdn, etc. are compleated. Then if the breadth of those parallelograms be suppos'd to be diminished, and their number to be augmented in infinitum: I say that the ultimate ratio's which the inscrib'd figure AKbLcMdD, the circumscribed figure AalbmcndoE, and the curvilinear figure AabcdE, will have to one another, are ratio's of equality.

For the difference of the inscrib'd and circumscrib'd figures is the sum of the parallelograms Kl, Lm, Mn, Do, that is, (from the equality of all their bases) the rectangle under one of their bases Kb and the sum of their altitudes Aa, that is, the rectangle ABla. But this rectangle, because its breadth AB is suppos'd diminished in infinitum, becomes less than any given space. And therefore (by Lem. I.) the figures inscribed and circumscribed become ultimately equal one to the other; and much more will the intermediate curvilinear figure be ultimately equal to either. Q.E.D.

### GUIDANCE

This is the "gold" room — the pipeline proof-of-concept. It is a **geometry** (DIAGRAM) room. The figure shows the curve aE, the baseline AE divided into equal bases, with inscribed rectangles below and circumscribed rectangles above.

**Station 1 (text panel):** Introduce the figure. The curvilinear area AacE with {curveblue|the curve aE}, {basegreen|the baseline AE}, and {sideorange|the vertical side Aa}. The equal bases AB, BC, CD partition the baseline. The heart is {curveblue|the curve}. Write 3–4 sentences.

**Station 2 (text panel):** The inscribed parallelograms Ab, Bc, Cd fill the figure from below. Their total area {inscpurple|AKbLcMdD} lies entirely under {curveblue|the curve}. The heart is {inscpurple|the inscribed rectangles}. Write 3–4 sentences.

**Station 3 (text panel):** The circumscribed parallelograms aKbl, bLcm, cMdn rise above the curve. Their excess over the inscribed figure is the single rectangle ABla. As AB → 0, this excess vanishes — so by Lemma I, {inscpurple|the inscribed}, {circred|the circumscribed}, and the curvilinear area become ultimately EQUAL. The heart is {circred|the circumscribed} — the final proof. End with Q.E.D. Write 4–5 sentences.

**Ceiling equations:** One per station — a short LaTeX formula capturing what that step proves. Blood-red on ceiling when demon dies.

## RULES

1. Colors are LOCAL per station.
2. Every station must have exactly one `heart` element.
3. Uncolored elements = BLACK. Never grey.
4. Every color you use in ops/text spans must be declared with `color <name> <#hex>`.
5. Every declared color must be used.
6. Geometry ops: every Name must be defined by an earlier op before being referenced.
7. The `text` block: use `{colorname|words}` spans. Use `$math$` for LaTeX math.
8. `@(x,y)` on point ops is a rough visual hint (cosmetic, no math precision needed).
9. ceiling INSIDE the station — one per station.
10. Use `\\` to continue long lines.

Return ONLY the `.room` file text.
