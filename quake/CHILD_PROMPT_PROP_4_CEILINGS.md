# CHILD PROMPT — prop_4: Write the FULL .room file from scratch

You are building content for a game where the player walks through Newton's Principia as a 3D dungeon. Each "room" is one idea. The player shoots panels on the walls to reveal colored text/equations, kills a demon, and then the room's ceiling equations appear in blood-red above each station.

## The room: Prop. IV, Theorem IV (F ∝ v²/r)

Here is Newton's actual text from the 1729 Motte translation:

---

**Proposition IV. Theorem IV.**

*The centripetal forces of bodies, which by equoble motions describe different circles, tend to the centres of the same circles; and are one to the other, as the squares of the arcs described in equal times applied to the radii of the circles.*

These forces tend to the centres of the circles (by prop. 2. and cor. 2. prop. 1) and are one to another as the versed sines of the least arcs described in equal times (by cor. 4. prop. 1.) that is, as the squares of the same arcs applied to the diameters of the circles, (by lem. 7.) and therefore since those arcs are as arcs described in any equal times, and the diameters are as the radii; the forces will be as the squares of any arcs described in the same time applied to the radii of the circles. Q. E. D.

**Cor. 1.** Therefore, since those arcs are as the velocities of the bodies, the centripetal forces are in a ratio compounded of the duplicate ratio of the velocities directly, and of the simple ratio of the radii inversely.

---

## The format — equation room

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
    layout $...$   (optional structured display)
  text
    <explanation with {colorname|words} spans and $math$>
```

- `ceiling`: INSIDE each station. LaTeX formula capturing THAT step's key result. Displayed blood-red on ceiling when demon dies.
- `term`: colored LaTeX fragment. `heart` marks the current step's key element.
- Colors are local per station. Uncolored = black. Never grey. Text: 3–4+ sentences.

## The 2 stations

**Station 1 — The proportionality:** F ∝ v²/r. Newton's core result: the centripetal force grows with the square of the speed (v²) and is inversely as the distance from the centre (r). The heart is v² (the square of the speed). Key concepts: v² (speed squared), F (centripetal force), r (radius/distance from centre).

**Station 2 — The proof chain:** Newton proves this via the versed sine. By Prop. I and Cor. 4, the versed sine of a nascent arc ∝ force × time². By Lemma VII, the versed sine ∝ arc² / diameter. Combined: F ∝ arc² / (time² × radius) = v²/r. The heart is v².

## What you produce

Complete `.room` file — header, 2 stations, each with its own `ceiling`. Room id: `prop_4`. Kind: `equation`. Import: "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Book I, Section II, Proposition IV."
