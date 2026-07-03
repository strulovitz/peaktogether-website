# CHILD PROMPT — law_1: Write the FULL .room file from scratch

Build the complete Quake `.room` file for Law I.

## The format

You write in the ROOMSPEC format. Header:

```
room <id>
kind <geometry|equation|text>
import <citation>
caption <one line>
final <step#>
ceiling <eq_id> :: <LaTeX>     (one per station)

station <n>
  gloss <one sentence>
  color <name> <#hex>          (repeat; local to this station)
  panel
    phrase <colorname> "<book words>" [heart]
  text
    <prose with {colorname|words} spans and $math$>
```

For text rooms: panel uses `phrase <colorname> "<words>" [heart]`. Colors are local per station. The `heart` marks the current step's key element. Uncolored = black. Never grey.

## The room: law_1

Newton, Principia, Axioms or Laws of Motion, Law I:
**Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd.**

This is the principle of inertia. Newton gives three physical illustrations: the spinning top, the planets, and projectiles.

## The 4 stations

**Station 1:** The statement of Law I itself. Three key concepts: rest (a state of staying still), uniform straight-line motion, and impressed forces (which alone can change either state). The heart is "forces impress'd" — the cause of change.

**Station 2:** Newton's first illustration. A spinning top does not cease its rotation except as retarded by the resistance of the air. Without air resistance, it would spin forever — the larger the top, the longer it persists. The heart is "a spinning top."

**Station 3:** Newton's second illustration. The planets and comets — vast bodies moving in spaces with very little resistance — preserve both their progressive (forward) and circular motions for immensely long times. The heart is "the planets and comets."

**Station 4:** Newton's third illustration. Projectiles — stones, arrows, cannonballs — keep moving except as hindered by air resistance and pulled downward by gravity. A cannonball shot horizontally would circle the Earth if not for these forces. The heart is "projectiles."

## What you produce

The complete `.room` file text — header, 4 stations, everything. One `ceiling` equation per station. Use the name `law_1` as the room id. Kind is `text`.
