# QUAKE CHILD PROMPT — lemma_6.room

You are a Quake content child. Write ONE `.room` file for lemma_6. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v1.0)

```
HEADER (before first station):
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#> | ceiling <eq_id> :: <verbatim LaTeX>   (repeat ceiling per equation)

COLOR RULE: colors are local per station; matching words in text share them; uncolored
= plain BLACK (never grey); exactly the step's HEART element carries `heart`.

GEOMETRY ops:  point  point_on  intersect  midpoint  foot  reflect
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

## YOUR ROOM — lemma_6

**lemma_6 · DIAGRAM · 3 step-pairs · Pl.2 Fig.1**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma VI; Plate 2, Fig. 1.
caption   As a point B on a curve approaches the point of contact A, the angle between the chord AB and the tangent AD is diminished without limit and ultimately vanishes.

s1 — Arc ACB → arcblue(#1E6FE0) ♥
s2 — Chord AB → chordgreen(#00A35A) ♥
s3 — Tangent AD → tanorange(#E8770A); contact angle BAD → anglered(#D81B60) ♥ vanishing as B→A.

colors_used: arcblue, chordgreen, tanorange, anglered
ceiling: B \to A \;\Rightarrow\; \angle BAD \to 0
```

### Newton's text (verbatim, from the 1729 Motte translation, Book I, Section I, Lemma VI):

> If any arc ACB (Pl.2.Fig.1.) given in position is by its chord AB, and in any point A in the middle of the continued curvature is touched by a right line AD, produced both ways; then if the points A and B approach one another and meet, I say the angle BAD, contained between the chord and the tangent, will be diminished in infinitum, and ultimately will vanish.
>
> For if that angle does not vanish, the arc ACB will contain with the tangent AD an angle equal to a rectilinear angle; and therefore the curvature at the point A will not be continued, which is against the supposition.

### GUIDANCE

Newton's proof is a clean 2-sentence argument — but the **text panels** are where you TEACH it. Write clear, friendly prose in each step's text block that explains what the player sees. 3–5 sentences each.

**The figure (Pl.2 Fig.1):** A curve with a visible arc ACB rising upward, a point A at the left end where the curve is smooth (continuous curvature), a chord AB connecting A to a nearby point B on the curve, and a tangent AD touching the curve at A and extending rightward. Point B slides toward A along the curve.

**Step 1 (the ARC):** Draw the curve / arc ACB. The arc is the curvilinear path connecting A to B. Introduce what "continuous curvature" means: the bend is smooth, no sharp corners. The {arcblue|arc ACB} is the heart — this is the curve whose nature we're investigating.

**Step 2 (the CHORD):** Draw the chord AB — the straight line connecting A to B. Explain that as B moves closer to A along the curve, the {chordgreen|chord AB} grows shorter and shorter. The chord is a straight-line shortcut under the arc. The chord is the heart.

**Step 3 (the TANGENT + ANGLE):** Draw the tangent AD at A. Explain: the tangent is the straight line that just grazes the curve at A, matching its direction at that single point. Form the angle BAD — the angle between {tanorange|the tangent AD} and {chordgreen|the chord AB}. As B approaches A, the chord swivels toward the tangent, and the {anglered|angle BAD} shrinks — ultimately to zero. Newton's proof: if it didn't vanish, the curve would have a sharp elbow at A (not continuous curvature), contradicting the premise. The angle BAD is the heart.

**Ceiling:** One clean equation — the limit statement that as B approaches A, the angle between chord and tangent vanishes.

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
2. Every station must have at least one `heart` element (the Stabilo highlight for that step).
3. Uncolored elements = BLACK. Never grey.
4. Every color you use in ops/text spans must be declared with `color <name> <#hex>`.
5. Every declared color must be used.
6. Geometry ops: every Name must be defined by an earlier op before being referenced.
7. The `text` block: use `{colorname|words}` spans for colored text. Use `$math$` for LaTeX math.
8. Ceiling equations: verbatim LaTeX between `::` delimiters.
9. `@(x,y)` on point ops is a rough visual hint (cosmetic, no math precision needed).
10. Use `\\` at end of line to continue long lines.
11. Text panels must be EDUCATIONAL — 3–5 sentences each, teaching the concept in plain words.
12. End the final station's text with a concluding sentence or \textit{Q.E.D.}
13. The ceiling equation is part of the room atmosphere — one clean limit statement is enough.

Return ONLY the `.room` file text.
