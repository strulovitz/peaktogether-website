# QUAKE CHILD PROMPT — prop_4.room

You are a Quake content child. Write ONE `.room` file for prop_4. Return ONLY the `.room` file text (in a fenced code block).

## THE .room FORMAT (v2.0 — ceiling inside each station)

```
HEADER (before first station):
  room <node_id> | kind geometry|equation|text | import <citation> | caption <line>
  final <step#>

COLOR RULE: colors are local per station; matching words in text share them; uncolored
= plain BLACK (never grey); exactly the step's HEART element carries `heart`.

EQUATION ops:  term <colorname> $<latex>$ [heart] [stabilo=#hex]
All kinds: optional `layout $...$` with {name|$frag$} spans for structured eq display.

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

## YOUR ROOM — prop_4

**prop_4 · EQUATION-AS-FIGURE · 2 step-pairs · importance 5 · THE locked-doctrine example of equation-as-figure**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition IV.
caption   The centripetal forces of bodies, which by equoble motions describe different circles, tend to the centres of the same circles; and are one to the other, as the squares of the arcs described in equal times applied to the radii of the circles.

s1 (equation): equation-as-figure — F ∝ v² / r. The centripetal force grows with the square of the speed and inversely with the radius. The heart is v² (the square of the speed).
s2 (sketch/derivation): small circle, equal-time arc, versed sine gives force (by Cor. 4 Prop. 1, Lem. 7). Combined: F ∝ v²/r. The heart is v².
```

### Newton's text (verbatim, from the 1729 Motte translation):

**Proposition IV. Theorem IV.** *The centripetal forces of bodies, which by equoble motions describe different circles, tend to the centres of the same circles; and are one to the other, as the squares of the arcs described in equal times applied to the radii of the circles.*

These forces tend to the centres of the circles (by prop. 2. and cor. 2. prop. 1) and are one to another as the versed sines of the least arcs described in equal times (by cor. 4. prop. 1.) that is, as the squares of the same arcs applied to the diameters of the circles, (by lem. 7.) and therefore since those arcs are as arcs described in any equal times, and the diameters are as the radii; the forces will be as the squares of any arcs described in the same time applied to the radii of the circles. Q. E. D.

**Cor. 1.** Therefore, since those arcs are as the velocities of the bodies, the centripetal forces are in a ratio compounded of the duplicate ratio of the velocities directly, and of the simple ratio of the radii inversely.

### GUIDANCE

This is THE canonical example of an "equation-as-figure" room in Quake doctrine. The equation IS the figure — color its important terms, match explanatory words in the same colors.

**Station 1 — The equation (text panel):** The centripetal force grows with the square of the speed and inversely with the distance. The equation panel displays v² (the square of the speed) divided by r (the radius), scaling F (the centripetal pull toward the centre). The heart is v². Use Newton's own phrase "the pull toward the centre." Write 3–4 sentences.

**Station 2 — The derivation (text panel):** By Prop. I and Cor. 4, the centripetal force in a small arc is as the versed sine ÷ time². By Lemma VII, the versed sine ∝ arc²/diameter. Combined with arc ∝ speed × time, this yields F ∝ v²/r. The heart is v². Explain the proof chain in plain words. Write 3–4 sentences.

**Ceiling equations:** One per station — a short LaTeX formula. Blood-red on ceiling when demon dies.

## RULES

1. Colors are LOCAL per station.
2. Every station has exactly one `heart` with optional `stabilo=#hex`.
3. Uncolored = BLACK. Never grey.
4. Every used color must be declared.
5. Every declared color must be used.
6. `text`: use `{colorname|words}` spans and `$math$`.
7. `layout` assembles terms with `{name|$frag$}` spans.
8. ceiling INSIDE the station — one per station.
9. Use `\\` to continue long lines.

Return ONLY the `.room` file text.
