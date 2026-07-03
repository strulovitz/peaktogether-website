# CHILD PROMPT — law_1: Write the FULL .room file from scratch

Build the complete Quake `.room` file for Law I.

## The format

```
room <id>
kind text
import <citation>
caption <one line>
final <step#>

station <n>
  ceiling <eq_id> :: <LaTeX>
  gloss <one sentence>
  color <name> <#hex>
  panel
    phrase <colorname> "<book words>" [heart]
  text
    <prose with {colorname|words} spans and $math$>
```

The `ceiling` line goes INSIDE the station block, just after `station <n>`. Each station has exactly one `ceiling` equation. Colors are local per station. The `heart` marks the current step's key element. Uncolored = black. Never grey.

## The room: law_1

Newton, Principia, Axioms or Laws of Motion, Law I:
**Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd.**

This is the principle of inertia. Newton gives three physical illustrations.

## The 4 stations

**Station 1:** The statement of Law I itself. Three key concepts: rest (a state of staying still), uniform straight-line motion, and impressed forces (which alone can change either state). The heart is "forces impress'd" — the cause of change.

**Station 2:** Newton's first illustration. A spinning top does not cease its rotation except as retarded by the resistance of the air. Without air resistance, it would spin forever. The heart is "a spinning top."

**Station 3:** Newton's second illustration. The planets and comets — vast bodies moving in spaces with very little resistance — preserve both their progressive and circular motions for immensely long times. The heart is "the planets and comets."

**Station 4:** Newton's third illustration. Projectiles — stones, arrows, cannonballs — keep moving except as hindered by air resistance and pulled downward by gravity. The heart is "projectiles."

## What you produce

The complete `.room` file — header, 4 stations, everything from scratch. Each station MUST contain its own `ceiling` line. Use the name `law_1` as the room id.
