# CHILD PROMPT — law_1: Write the FULL .room file from scratch

You are building content for a game where the player walks through Newton's Principia as a 3D dungeon. Each "room" is one idea from the book. The player shoots panels on the walls to reveal colored text/figures, kills a demon, and then the room's ceiling equations appear in blood-red.

## The room: Law I (Inertia)

You are writing a complete `.room` text file. Here is Newton's actual text from the 1729 Motte translation:

---

**LAW I.**

*Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impress'd thereon.*

PROJECTILES persevere in their motions, so far as they are not retarded by the resistance of the air, or impelled downwards by the force of gravity. A top, whose parts by their cohesion are perpetually drawn aside from rectilinear motions, does not cease its rotation, otherwise than as it is retarded by the air. The greater bodies of the planets and comets, meeting with less resistance in more free spaces, preserve the motions both progressive and circular for a much longer time.

---

## The format

```
room <id>
kind text
import <citation>
caption <one line — Newton's own statement of the law>
final <step#>

station <n>
  ceiling <eq_id> :: <LaTeX>
  gloss <one sentence — what this station teaches>
  color <name> <#hex>
  panel
    phrase <colorname> "<Newton's exact words>" [heart]
  text
    <explanation with {colorname|words} spans and $math$>
```

- `ceiling`: goes INSIDE each station. A LaTeX formula capturing the key result of THAT step, displayed in blood-red on the ceiling when the demon dies.
- `color`: declared per station. Each important concept gets a distinct color. Matching words in the text use `{colorname|words}`.
- `heart`: marks the CURRENT step's key element — it gets a bright Stabilo highlighter. One `heart` per station.
- Uncolored elements are black. Never grey.
- Text panels should be 3–4+ sentences. Explain, don't just repeat.

## Example ceiling equation (from a different room)

```
ceiling   eq0 :: \frac{p_i}{q_i} \to k \;\Longrightarrow\; \frac{\sum p_i}{\sum q_i} = k
```

## The 4 stations

**Station 1 — The law itself:** Newton's statement of inertia. Three concepts: rest, uniform straight-line motion, and impressed forces as the only cause of change. The heart is "forces impress'd."

**Station 2 — The spinning top:** Newton's first illustration — a top persists in rotation perpetually, retarded only by air. Without air it would spin forever. The heart is "a spinning top."

**Station 3 — Planets and comets:** Newton's second illustration — the vast bodies of planets and comets move in nearly empty space, preserving both progressive and circular motions for immense times with almost no resistance. The heart is "the planets and comets."

**Station 4 — Projectiles:** Newton's third illustration — stones, arrows, cannonballs keep moving except as hindered by air resistance and gravity. The heart is "projectiles."

## What you produce

The complete `.room` file. 4 stations, each with its own `ceiling` line. Room id: `law_1`. Kind: `text`. Import: "Newton, Principia, Andrew Motte trans., 1729 (Wikisource); Axioms, or Laws of Motion, Law I."
