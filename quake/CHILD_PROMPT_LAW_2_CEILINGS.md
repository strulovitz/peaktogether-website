# CHILD PROMPT — law_2: Write the FULL .room file from scratch

You are building content for a game where the player walks through Newton's Principia as a 3D dungeon. Each "room" is one idea. The player shoots panels on the walls to reveal colored text, kills a demon, and then the room's ceiling equations appear in blood-red above each station.

## The room: Law II (F = ma)

You are writing a complete `.room` text file. Here is Newton's actual text from the 1729 Motte translation:

---

**LAW II.**

*The alteration of motion is ever proportional to the motive force impress'd; and is made in the direction of the right line in which that force is impress'd.*

If any force generates a motion, a double force will generate double the motion, a triple force triple the motion, whether that force be impress'd altogether and at once, or gradually and successively. And this motion (being always directed the same way with the generating force) if the body moved before, is added to or subducted from the former motion, according as they directly conspire with or are directly contrary to each other; or obliquely joyned, when they are oblique, so as to produce a new motion compounded from the determination of both.

---

## The format — equation room

```
room <id>
kind equation
import <citation>
caption <one line — Newton's statement of the law>
final <step#>

station <n>
  ceiling <eq_id> :: <LaTeX>
  gloss <one sentence>
  color <name> <#hex>
  panel
    term <colorname> $<latex>$ [heart] [stabilo=#hex]
    layout $...$   (optional structured display with {name|$frag$} spans)
  text
    <explanation with {colorname|words} spans and $math$>
```

- `ceiling`: INSIDE each station. LaTeX formula capturing THAT step's key result. Displayed blood-red on ceiling when demon dies.
- `term`: a colored LaTeX fragment. `heart` marks the current step's key element (Stabilo highlight). `stabilo=#hex` sets the highlighter color.
- `layout`: optional — assembles the terms into a structured equation with `{colorname|$fragment$}` spans.
- Colors are local per station. Uncolored = black. Never grey. Text panels: 3–4+ sentences, explain, not repeat.

## Example ceiling equations

```
ceiling   eq0 :: \Delta(\text{motion}) \propto \mathbf{F}
ceiling   eq1 :: \Delta(\text{motion}) \parallel \mathbf{F}
```

## The 2 stations

**Station 1 — Proportionality:** Δ(motion) ∝ F. Newton explains: if any force generates a motion, double the force generates double the motion, triple generates triple — whether impressed all at once or gradually. The alteration of motion scales exactly with the impressed force. The heart is Δ(motion).

**Station 2 — Direction:** Δ(motion) ∥ F. The change of motion occurs along the right line of the generating force. If the body was moving before, the new motion is added to or subtracted from the former — or compounded obliquely — always directed the same way as the force. The heart is the parallel (∥) relation.

## What you produce

Complete `.room` file — header, 2 stations, each with its own `ceiling`. Room id: `law_2`. Kind: `equation`. Import: "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Axioms, or Laws of Motion, Law II."
