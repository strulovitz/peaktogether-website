# CHILD PROMPT — prop_4: Write the FULL .room file from scratch

Build the complete Quake `.room` file for Prop. IV, Theorem IV.

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
    <ops>
  text
    <prose with {colorname|words} spans and $math$>
```

For equation rooms: panel uses `term <colorname> $<latex>$ [heart]` and optionally `layout $...$` with `{name|$frag$}` spans.
Colors are local per station. The `heart` marks the current step's key element. Uncolored = black. Never grey.

## The room: prop_4

Newton, Principia, Book I, Section II, Proposition IV, Theorem IV:
**The centripetal force of a body moving uniformly in a circle is as the square of the speed divided by the radius.**

Newton's proof: in a circle, a body moves from P to Q in a small time. The centripetal force pulls it inward by the versed sine of the arc PQ. By Galileo's law, the versed sine ∝ force × time². The arc ∝ speed × time. Combining: force ∝ (arc²/time²)/radius ∝ v²/r.

## The 2 stations

**Station 1:** The centripetal pull grows with the square of the speed (v²) and inversely with the distance from the centre (r). The key elements are: v² — the square of the speed; F — the centripetal pull toward the centre; r — the distance from the centre (radius). The heart is v² (speed squared).

**Station 2:** Geometry of a small circular arc swept in equal time. By Prop. I, areas are proportional to times. The versed sine (the inward sagitta) gives the force — by Corollary 4 of Prop. I and Lemma VII, the versed sine in the nascent arc is ultimately as the square of the arc, confirming F ∝ v²/r. The heart is v² (speed squared).

## What you produce

The complete `.room` file text — header, 2 stations, everything. One `ceiling` equation per station. Use the name `prop_4` as the room id. Kind is `equation`.
