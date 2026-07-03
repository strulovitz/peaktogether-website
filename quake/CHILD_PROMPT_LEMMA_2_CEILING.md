# CHILD PROMPT — lemma_2: Add missing ceiling equation

Your only task: the room has 3 stations but only 2 ceiling lines. Write the missing third ceiling equation for station 3, capturing its key mathematical idea in LaTeX. Do NOT change the existing eq0 and eq1 lines, and do NOT change any other part of the file.

Here is the current file:

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
  color   insblue   #1E6FE0
  color   circred   #D81B60
  color   curvpurp  #8E24AA
  panel
    point   A @(0,0)       label=$A$ at=SW
    point   a @(0,2.5)     label=$a$ at=NW
    point   E @(7,0)       label=$E$ at=SE
    polygon aE  a E
    segment AE A E
    segment Aa A a
    polyline baseline A E
    series  inscribed_rects  along AE to aE count 4 kind inscribed_rects  color=insblue  heart
    series  circumscribed_rects along AE to aE count 4 kind circumscribed_rects  color=circred
  text
    The {insblue|inscribed rectangles} fill the curvilinear figure from below; the {circred|circumscribed rectangles} enclose it from above. The curve {curvpurp|aE} forms the upper boundary along the baseline $AE$. As the number of rectangles grows, the difference between the sum of the {insblue|inscribed} and the sum of the {circred|circumscribed} tends to nothing.

station 2
  gloss   The base AB is diminished to nothing (AB → 0), and the difference of the inscribed and circumscribed figures shrinks.
  color   baseblue  #1E6FE0
  panel
    point   A @(0,0)     label=$A$ at=SW
    point   B @(1.4,0)   label=$B$ at=S
    point   a @(0,2.5)   label=$a$ at=NW
    point   b @(1.4,2.5) label=$b$ at=N
    segment AB A B
    segment Aa A a
    segment Bb B b
    segment ab a b
    segment aE a E
  text
    As the subtense {baseblue|AB} becomes infinitely small, the difference between the {insblue|inscribed} and {circred|circumscribed} rectangles goes to zero. The gap $Abla$ collapses, and in the limit the two constructions become indistinguishable.

station 3
  gloss   The ultimate equality: the inscribed figure, circumscribed figure, and curvilinear area are all ultimately equal.
  color   insblue  #1E6FE0
  color   circred  #D81B60
  color   curvpurp #8E24AA
  panel
    point  A @(0,0)    label=$A$ at=SW
    point  E @(7,0)    label=$E$ at=SE
    segment AE A E
    polygon aE a E
  text
    In the limit as $AB \to 0$, the {insblue|inscribed} figure, the {circred|circumscribed} figure, and the {curvpurp|curvilinear area $AacE$} are ultimately equal. Newton states "if you deny their ultimate ratios to be ratios of equality, you deny the foundations of geometry." The method of exhaustion yields the exact area under the curve.
```

Give me ONLY the new `ceiling eq2` line. Format: `ceiling   eq2 :: <LaTeX>`.
