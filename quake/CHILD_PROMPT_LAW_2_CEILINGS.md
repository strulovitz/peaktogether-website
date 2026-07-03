# CHILD PROMPT — law_2: Write the FULL .room file from scratch

Build the complete Quake `.room` file for Law II.

## The format

```
room <id>
kind equation
import <citation>
caption <one line>
final <step#>

station <n>
  ceiling <eq_id> :: <LaTeX>
  gloss <one sentence>
  color <name> <#hex>
  panel
    term <colorname> $<latex>$ [heart] [stabilo=#hex]
    layout $...$   (optional; with {name|$frag$} spans)
  text
    <prose with {colorname|words} spans and $math$>
```

The `ceiling` line goes INSIDE the station block, just after `station <n>`. Each station has exactly one `ceiling` equation. Colors are local per station. The `heart` marks the current step's key element. Uncolored = black. Never grey.

## The room: law_2

Newton, Principia, Axioms or Laws of Motion, Law II:
**The alteration of motion is ever proportional to the motive force impressed; and is made in the direction of the right line in which that force is impressed.**

This is F = ma, expressed geometrically. Newton splits it into two parts.

## The 2 stations

**Station 1: Proportionality — Δ(motion) ∝ F.** If a force generates a motion, double the force generates double the motion, triple generates triple — whether impressed all at once or gradually. The alteration of motion scales exactly with the impressed force. The heart is Δ(motion).

**Station 2: Direction — Δ(motion) ∥ F.** The change of motion occurs along the right line of the generating force. If the body was already moving, the new motion is added to or subtracted from the former — or compounded obliquely — always directed the same way as the force. The heart is the parallel/direction (∥).

## What you produce

The complete `.room` file — header, 2 stations, everything from scratch. Each station MUST contain its own `ceiling` line. Use the name `law_2` as the room id.
