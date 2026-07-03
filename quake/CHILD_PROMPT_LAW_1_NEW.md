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

s1 (statement): Newton's statement of inertia — rest, uniform motion, impressed forces as the sole cause of change. The heart is the concept of impressed force.
s2 (spinning top example): Newton's first illustration — a top persists in rotation forever except retarded by air.
s3 (planets/comets example): Newton's second illustration — planets and comets in nearly empty space preserve motions for immense times.
s4 (projectile example): Newton's third illustration — projectiles persevere except hindered by air and gravity.
```

### Newton's text (verbatim, from the 1729 Motte translation):

**LAW I.** *Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd thereon.*

PROJECTILES persevere in their motions, so far as they are not retarded by the resistance of the air, or impelled downwards by the force of gravity. A top, whose parts by their cohesion are perpetually drawn aside from rectilinear motions, does not cease its rotation, otherwise than as it is retarded by the air. The greater bodies of the planets and comets, meeting with less resistance in more free spaces, preserve the motions both progressive and circular for a much longer time.

### GUIDANCE

This is a **TEXT** room — Newton printed no diagram here. The "figure" on the panel side is a colored-text display. Each station has one `phrase` as its heart.

**Station 1 (text panel):** State Law I. Introduce the three key concepts side by side: a state of rest, uniform motion in a right line, and impressed forces as the sole agent of change. The heart is impressed forces. Write 3–4 sentences — enough to teach the law.

**Station 2 (text panel):** Newton's first illustration — the spinning top. Newton chose this because the top's parts, by cohesion, are perpetually drawn aside from straight-line motion, yet the whole perseveres. The top does not cease its rotation except retarded by the resistance of the air. Without air, it would spin forever. The heart is the spinning top itself. Write 3–4 sentences.

**Station 3 (text panel):** Newton's second illustration — the planets and comets. These are his strongest example: vast bodies in nearly empty space preserve BOTH progressive AND circular motions for immensely long times. The planets and comets meet almost no resistance. The heart is the planets and comets. Write 3–4 sentences.

**Station 4 (text panel):** Newton's third illustration — projectiles. Stones, arrows, cannonballs. Newton notes they move in our air where we can see them, and a cannonball shot horizontally would circle the Earth if not for air and gravity. Projectiles persevere except when retarded by air resistance or gravity. The heart is projectiles. Write 3–4 sentences.

**Ceiling equations:** One per station — a short LaTeX formula capturing what that step proves. Displayed in blood-red on the ceiling when the demon dies. Keep them clean and readable.

Return ONLY the `.room` file text.

## RULES

1. Colors are LOCAL per station. Same concept may get different colors or none in another station.
2. Every station must have exactly one `heart` element.
3. Uncolored elements = BLACK. Never grey.
4. Every color you use must be declared with `color <name> <#hex>`.
5. Every declared color must be used in panel or text.
6. The `text` block: use `{colorname|words}` spans. Use `$math$` for LaTeX math.
7. Use `\\` at end of line to continue long lines.
8. ceiling goes INSIDE the station — one per station, after the `station <n>` line.
9. The child decides which concepts to color, which hex codes to use, and which element is the HEART of each step — based on Newton's text, not any pre-assigned design.
