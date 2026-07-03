# QUAKE CHILD PROMPT — law_2.room

You are a Quake content child. Write ONE `.room` file for law_2. Return ONLY the `.room` file text (in a fenced code block).

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

## YOUR ROOM — law_2

**law_2 · EQUATION/TEXT · 2 step-pairs · importance 5 · Axioms p.19**

```
import    Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Axioms, or Laws of Motion, Law II.
caption   Law II — The alteration of motion is ever proportional to the motive force impressed; and is made in the direction of the right line in which that force is impressed.

s1 (proportionality): equation-as-figure. Δ(motion) ∝ F. Double force → double motion. The heart is Δ(motion).
s2 (direction/composition): Δ(motion) ∥ F. The change occurs along the same right line as the force. The heart is the parallel direction.
```

### Newton's text (verbatim, from the 1729 Motte translation):

**LAW II.** *The alteration of motion is ever proportional to the motive force impress'd; and is made in the direction of the right line in which that force is impress'd.*

If any force generates a motion, a double force will generate double the motion, a triple force triple the motion, whether that force be impress'd altogether and at once, or gradually and successively. And this motion (being always directed the same way with the generating force) if the body moved before, is added to or subducted from the former motion, according as they directly conspire with or are directly contrary to each other; or obliquely joyned, when they are oblique, so as to produce a new motion compounded from the determination of both.

### GUIDANCE

This is an **EQUATION** room. The "figure" is the equation itself — colored terms with a Stabilo heart. Use `term` for colored LaTeX fragments and `layout` to display the structured equation. This is F = ma expressed geometrically by Newton.

**Station 1 — Proportionality (text panel):** Explain Newton's proportionality: the alteration of motion scales exactly with the impressed force. Double force → double motion. Triple force → triple motion. Whether impressed all at once or gradually. The equation panel shows Δ(motion) ∝ F. The heart is Δ(motion). Newton wrote: "If any force generates a motion, a double force will generate double the motion." Use his words. Write 3–4 sentences.

**Station 2 — Direction (text panel):** Explain that the change occurs along the SAME line as the force. If the body moved before, the new motion is added or subtracted — or compounded obliquely. Newton explains the parallelogram rule for forces. The heart is the right-line direction (∥ relation). Write 3–4 sentences.

**Ceiling equations:** One per station — a short LaTeX formula capturing what that step proves. Blood-red on ceiling when demon dies.

## RULES

1. Colors are LOCAL per station.
2. Every station has exactly one `heart` with optional `stabilo=#hex`.
3. Uncolored = BLACK. Never grey.
4. Every used color must be declared.
5. Every declared color must be used.
6. `text` block: use `{colorname|words}` spans and `$math$`.
7. `layout` assembles terms into a structured equation with `{name|$frag$}` spans.
8. ceiling INSIDE the station — one per station.
9. Use `\\` to continue long lines.

Return ONLY the `.room` file text.
