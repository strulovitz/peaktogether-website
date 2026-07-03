# QUAKE CHILD PROMPT — law_1.room

You are a Quake content child. Write ONE `.room` file for law_1. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v2.0 — ceiling inside each station)

```
HEADER (before first station):
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#>

COLOR RULE: colors are local per station; matching words in text share them; uncolored
= plain BLACK (never grey); exactly the step's HEART element carries `heart`.

TEXT ops:      phrase <colorname> "<words>" [heart]

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

## YOUR ROOM — law_1

**law_1 · TEXT (colored, no drawn scene per Newton) · 4 step-pairs · importance 5 · Axioms p.19**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Axioms, or Laws of Motion, Law I.
caption   Law I — Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd thereon.

s1 (statement): ♥ = forceorange phrase. Colors:
  restblue(#1E6FE0) motiongreen(#00A35A) forceorange(#E8770A) ♥

s2 (spinning top example): ♥ = topblue phrase. Colors:
  topblue(#1E6FE0) dragred(#D81B60)

s3 (planets/comets example): ♥ = planetpurple phrase. Colors:
  planetpurple(#8E24AA) freeteal(#00897B)

s4 (projectile example): ♥ = projblue phrase. Colors:
  projblue(#1E6FE0) dragred(#D81B60) gravorange(#E8770A)
```

### Newton's text (verbatim, from the 1729 Motte translation):

**LAW I.** *Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd thereon.*

PROJECTILES persevere in their motions, so far as they are not retarded by the resistance of the air, or impelled downwards by the force of gravity. A top, whose parts by their cohesion are perpetually drawn aside from rectilinear motions, does not cease its rotation, otherwise than as it is retarded by the air. The greater bodies of the planets and comets, meeting with less resistance in more free spaces, preserve the motions both progressive and circular for a much longer time.

### GUIDANCE

This is a **TEXT** room — Newton printed no diagram here. The "figure" on the panel side is a colored-text display. Each station has one `phrase` as its heart.

**Station 1 (text panel):** State Law I. Introduce the three key concepts side by side: {restblue|a state of rest}, {motiongreen|uniform motion in a right line}, and {forceorange|forces impress'd} as the sole agent of change. The heart is {forceorange|forces impress'd}. Write 3–4 sentences — enough to teach the law.

**Station 2 (text panel):** Newton's first illustration — the spinning top. Newton chose this because the top's parts, by cohesion, are perpetually drawn aside from straight-line motion, yet the whole perseveres. {topblue|A top} does not cease its rotation except retarded by {dragred|the resistance of the air}. Without air, it would spin forever. The heart is {topblue|a top}. Write 3–4 sentences.

**Station 3 (text panel):** Newton's second illustration — the planets and comets. These are his strongest example: vast bodies in nearly empty space preserve BOTH progressive AND circular motions for immensely long times. {planetpurple|The planets and comets} meet almost no resistance. The heart is {planetpurple|the planets and comets}. Write 3–4 sentences.

**Station 4 (text panel):** Newton's third illustration — projectiles. Stones, arrows, cannonballs. Newton notes they move in our air where we can see them, and a cannonball shot horizontally would circle the Earth if not for air and gravity. {projblue|Projectiles} persevere except when retarded by {dragred|air resistance} or {gravorange|gravity}. The heart is {projblue|projectiles}. Write 3–4 sentences.

**Ceiling equations:** One per station — a short LaTeX formula capturing what that step proves. Displayed in blood-red on the ceiling when the demon dies. Keep them clean and readable.

## GOLD EXAMPLE — lemma_2.room (geometry room, for format reference)

```
room      lemma_2
kind      geometry
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section I, Lemma II; Plate 1, Fig. 6.
caption   Inscribed and circumscribed parallelograms on equal bases under the curve aE; as the bases shrink, the inscribed and circumscribed figures and the curvilinear figure become ultimately equal.
final     3

station 1
  ceiling   eq0 :: \lim_{AB \to 0}\; \bigl(\text{circumscribed} - \text{inscribed}\bigr) = ABla \;\longrightarrow\; 0
  gloss   The curvilinear figure AacE: the curve aE, the baseline AE on equal bases, and the side Aa.
  color   curveblue  #1E6FE0
  color   basegreen  #00A35A
  color   sideorange #E8770A
  panel
    point   A @(0,0)   marker=dot label=$A$ at=SW
    point   E @(8,0)   marker=dot label=$E$ at=SE
    point   ptA @(0,1.4)  color=curveblue label=$a$ at=NW
    point   ptb @(2,2.6)  color=curveblue label=$b$ at=N
    point   ptc @(4,3.4)  color=curveblue label=$c$ at=N
    point   ptd @(6,3.9)  color=curveblue label=$d$ at=N
    point   ptE @(8,4.2)  color=curveblue
    polyline curve ptA ptb ptc ptd ptE   color=curveblue heart
    segment baseAE A E   color=basegreen
    segment sideAa A ptA  color=sideorange
  text
    In the figure $AacE$, bounded by the right lines $\{sideorange|Aa}$ and $\{basegreen|AE}$ and by \{curveblue|the curve $acE$}, take any number of equal bases $AB$, $BC$, $CD$ along $\{basegreen|AE}$. This is the curvilinear figure whose area we measure.

station 2
  ceiling   eq1 :: \text{inscribed} \;=\; \text{circumscribed} \;=\; \text{curvilinear area} \quad (\text{ultimately})
  gloss   The inscribed parallelograms Ab, Bc, Cd, standing under the curve on the equal bases.
  color   inscpurple #8E24AA
  color   sideorange #E8770A
  color   curveblue  #1E6FE0
  panel
    series inscribed along baseAE to curve count 4 kind inscribed_rects color=inscpurple heart
  text
    On these equal bases erect \{inscpurple|the inscribed parallelograms $Ab$, $Bc$, $Cd$}, with sides parallel to $\{sideorange|Aa}$. \{inscpurple|The inscribed figure $AKbLcMdD$} lies wholly under \{curveblue|the curve}.

station 3
  ceiling   eq2 :: \text{insc}=\text{circ}=\text{area} \;(\text{ultimately},\;\text{Lem. I})
  gloss   The circumscribed parallelograms completed above the curve; their excess over the inscribed figure is the single rectangle ABla, which vanishes as AB shrinks.
  color   circred    #D81B60
  color   curveblue  #1E6FE0
  color   inscpurple #8E24AA
  color   basegreen  #00A35A
  panel
    series circumscribed along baseAE to curve count 4 kind circumscribed_rects color=circred heart
  text
    Complete \{circred|the circumscribed parallelograms} above the curve. Their excess is the rectangle $ABla$; as $\{basegreen|AB}$ shrinks, this vanishes. Hence by Lem.~I the inscribed and circumscribed figures — and the curvilinear area — become ultimately equal. Q.E.D.
```

## RULES

1. Colors are LOCAL per station. Same concept may get different colors or none in another station.
2. Every station must have exactly one `heart` element.
3. Uncolored elements = BLACK. Never grey.
4. Every color you use must be declared with `color <name> <#hex>`.
5. Every declared color must be used in panel or text.
6. The `text` block: use `{colorname|words}` spans. Use `$math$` for LaTeX math.
7. Use `\\` at end of line to continue long lines.
8. ceiling goes INSIDE the station — one per station, after the `station <n>` line.

Return ONLY the `.room` file text.
