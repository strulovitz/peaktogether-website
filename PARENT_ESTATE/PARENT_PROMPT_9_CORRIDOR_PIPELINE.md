# DESCENT QED — PARENT PROMPT #9: FIX THE CORRIDOR-CREATION PIPELINE (June 18, 2026)

> **TO:** Claude Opus 4.8 — You are PARENT #9 / ARCHITECT.
> **FROM:** Nir (strulovitz) — the human, the boss. He pastes this to you.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, tests, reports.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude Opus 4.8 conversation.
> **READ EVERY SECTION BEFORE WRITING ANYTHING.**

---

## 0. THE PROBLEM — READ THIS FIRST

We have a broken corridor-creation pipeline. Right now, creating a new corridor for the game requires TWO separate child sessions with TWO separate prompts, and the human (Nir) has to manually coordinate between them. This is unacceptable. Here's what happened today:

1. Nir asked a child (using `CORRIDOR_WRITER_PROMPT.md`) to write a new corridor about "Euler's Sine Product and the Even Zeta Values."
2. The child delivered a beautiful baker-format file (`corridors/euler_even_zeta.txt`) with TITLE, STAINS, 7 ROBOT blocks, each with NAME and 4 EXPLAIN layers. This file is the input to the PNG baker (`deu/bake_corridor.py`) which produces the transparent colored Understanding Mode PNGs.
3. But this file is **ONLY HALF of what the game needs.** The game engine loads a completely DIFFERENT format — the **game-format corridor file** — which has: CORRIDOR header, TITLE, FLAVOR, LEDGER, BRIEFING_INTRO, ENTRY_TEXT, EXIT_TEXT, and per robot: NAME, BRIEFING_HINT, PROBLEM, EXPLAIN_MATHEMATICIAN/PHYSICIST/BIOLOGIST/ENGINEER, SEGMENTS, EYE, VULNERABLE_TO, and FIZZLE entries (7 robots × 6 wrong weapons = 42 FIZZLE entries per corridor).
4. To get the game-format file, Nir previously had to go to a DIFFERENT parent, who wrote a DIFFERENT brief (`CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md`), which was then given to a DIFFERENT child, who produced the game-format file.

**This is broken.** Nir should be able to paste ONE prompt to ONE child, give it a Wikipedia page, and get back BOTH files — the baker-format file AND the game-format file — in one session. Plus the level manifest. Three files total, one child, one session.

---

## 1. THE TWO FILE FORMATS (you must understand both)

### FILE 1: Baker-format corridor (input to `deu/bake_corridor.py`)

This file is compiled by the baker into transparent colored PNG images for Understanding Mode. It uses FULL LaTeX (amsmath, amssymb, xcolor — the baker runs real pdflatex). Format:

```
TITLE { <corridor title> }

STAINS {
  <meaningkey> = r g b   # <color name> — <why>
  ...
}

ROBOT: <n>
  NAME { <name> }
  EXPLAIN_MATHEMATICIAN { <full LaTeX prose with \stain{key}{...} and \thread{id}{...}> }
  EXPLAIN_PHYSICIST { ... }
  EXPLAIN_BIOLOGIST { ... }
  EXPLAIN_ENGINEER { ... }
```

Key features:
- Uses \stain{key}{content} for macro-level color (sacred, cross-robot)
- Uses \thread{id}{content} for micro-level color (page-local)
- Full LaTeX allowed (\tfrac, \displaystyle, \binom, etc.)
- The color system uses 3 base colors (red/yellow/blue) and up to 3 blends (purple/orange/green) with backwards-reasoning from synthesis to primitives
- STAINS are declared as RGB floats

### FILE 2: Game-format corridor (loaded by the game engine via `content_parser.py`)

This file is what the game actually loads at runtime to place robots, run combat, show holograms, handle fizzles, etc. It uses matplotlib MATHTEXT (a LIMITED LaTeX subset — NO \tfrac, \dfrac, \displaystyle, \emph, \binom). Format:

```
CORRIDOR: 1
TITLE { <title> }
FLAVOR { <short evocative line> }
LEDGER {
  PRIMARY <key> = <color_name>
  PRIMARY <key> = <color_name>
  PRIMARY <key> = <color_name>
  BLEND <key> = <key1> + <key2>
  ...
}
BRIEFING_INTRO { <sets up the mission> }
ENTRY_TEXT { <you have entered...> }
EXIT_TEXT { <celebrates solving/rescuing> }

ROBOT: 1
NAME { <mathematician name — must resolve to portrait PNG filename> }
BRIEFING_HINT { <one line — the step/technique name> }
PROBLEM { <the puzzle, with simple mathtext> }
EXPLAIN_MATHEMATICIAN { <rigorous, mathtext-legal> }
EXPLAIN_PHYSICIST { <intuitive, mathtext-legal> }
EXPLAIN_BIOLOGIST { <everyday analogy, mathtext-legal> }
EXPLAIN_ENGINEER { <practical/applied, mathtext-legal> }
SEGMENTS {
  $<short math>$  | <ledger_key>
  $=$              | NEUTRAL
  $<short math>$  | <ledger_key>
}
EYE { <ledger_key> }
VULNERABLE_TO { <weapon_id> }
FIZZLE <wrong_id_1> { <generous teaching hint — why this wrong weapon doesn't work here> }
FIZZLE <wrong_id_2> { ... }
FIZZLE <wrong_id_3> { ... }
FIZZLE <wrong_id_4> { ... }
FIZZLE <wrong_id_5> { ... }
FIZZLE <wrong_id_6> { ... }
```

Key features:
- LEDGER (not STAINS) — uses PRIMARY/BLEND syntax with named colors
- SEGMENTS — short colored math fragments on the robot body
- EYE — robot eye color from LEDGER
- VULNERABLE_TO — the weapon ID that defeats this robot
- 6 FIZZLE entries per robot (one per WRONG weapon) = N_robots × (N_robots - 1) total
- Mathtext-only rule: ONLY \frac, \sum, \pi, \infty, \cdot, \prod, \pm, \sin, etc.
- FORBIDDEN: \tfrac, \dfrac, \displaystyle, \emph, \binom, \underbrace, any AMSMath

### FILE 3: Level manifest

```
title: <Level Title>
baked: ../baked/<dirname>
corridors:
  ../corridors/<game_format_filename>.txt
```

---

## 2. WHAT EXISTS TODAY

### The current (broken) corridor-creation prompt:
`PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` — produces ONLY the baker-format file. It knows about STAINS, the 4 EXPLAIN layers, robots, the color-meaning system, and the recursive Wikipedia-gathering protocol. But it knows NOTHING about the game-format file (no LEDGER, no SEGMENTS, no EYE, no VULNERABLE_TO, no FIZZLEs, no BRIEFING_HINT, no PROBLEM, no FLAVOR, no ENTRY_TEXT, no EXIT_TEXT).

### The existing game-format brief (one-time, not reusable):
`PARENT_ESTATE/briefs/CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md` — was written by a previous parent for ONE specific corridor (Euler's approach to the Basel problem). It contains good game-format requirements (the 42 fizzles, the mathtext rule, the LEDGER→STAINS mirroring, the portrait-filename resolution, the SEGMENTS rule) but it's hardcoded to 7 specific robots with specific names/IDs and is NOT reusable for other corridors.

### Working examples on disk:
- Baker-format: `corridors/maxwell.txt` (Maxwell, 5 robots), `levels/mathematics/basel_problem/basel_euler_proof.txt` (Basel/Euler approach, 7 robots), `corridors/euler_even_zeta.txt` (Even Zeta, 7 robots — JUST CREATED TODAY, not yet baked)
- Game-format: `corridors/maxwell_old.txt` (Maxwell, 5 robots), `corridors/basel.txt` (Basel/Euler approach, 7 robots)
- Level manifests: `levels/maxwell.txt`, `levels/basel.txt`

---

## 3. WHAT YOU MUST PRODUCE

**ONE new prompt** — call it `CORRIDOR_CREATOR_PROMPT.md` — that replaces the current `CORRIDOR_WRITER_PROMPT.md`. This new prompt:

1. **Is GENERAL and FOREVER.** It works for ANY mathematical topic from ANY Wikipedia page. Not hardcoded to any specific corridor, number of robots, or set of mathematician names.

2. **Produces ALL THREE files in ONE child session:**
   - The baker-format corridor file (for baking Understanding Mode PNGs)
   - The game-format corridor file (for the game engine, with ALL required fields including ALL fizzles)
   - The level manifest file

3. **Preserves everything good from the existing prompts:**
   - The recursive Wikipedia-gathering protocol from CORRIDOR_WRITER_PROMPT.md
   - The STAIN color-meaning system (backwards reasoning: 3 bases → 3 blends)
   - The 4 EXPLAIN layers at 4 depths
   - The \stain{} and \thread{} markup for the baker file
   - The mathtext-only rule for the game file
   - The LEDGER↔STAINS mirroring (game LEDGER mirrors the baker STAINS color story)
   - The portrait-filename resolution (NAME → filename)
   - The fizzle requirements (warm, teaching, generous — never punishing)
   - The SEGMENTS rule (short colored math on the robot body)
   - The fresh-chat gate (child asks Nir to paste real files before writing)

4. **Includes the game-format requirements that were previously only in Brief #B:**
   - CORRIDOR header, TITLE, FLAVOR, BRIEFING_INTRO, ENTRY_TEXT, EXIT_TEXT
   - BRIEFING_HINT per robot
   - PROBLEM per robot
   - SEGMENTS per robot (mathtext-legal, ledger-keyed)
   - EYE per robot
   - VULNERABLE_TO per robot (the weapon ID — child must invent unique IDs)
   - ALL fizzles: N_robots × (N_robots - 1) unique fizzle entries
   - The LEDGER block (PRIMARY + BLEND, mirroring the STAINS color story)

5. **Has a clear fresh-chat gate** where the child asks Nir to paste:
   - `corridors/maxwell_old.txt` (game-format syntax template)
   - `levels/maxwell.txt` (manifest syntax template)
   - An existing baker-format file as example (e.g. `corridors/maxwell.txt`)
   - `content_parser.py` (to confirm exact field names and validation)

6. **Explains the relationship between the two files clearly** so the child understands they are writing the SAME corridor in TWO formats for TWO different consumers (the baker vs the game engine), and that the mathematical content, robot order, robot numbering, and color-meaning story must be CONSISTENT between the two files.

7. **Handles the variable robot count.** The prompt should say "aim for 7 robots (acceptable 5–9)" and the fizzle count formula adjusts automatically: N × (N-1).

---

## 4. CONSTRAINTS ON THE PROMPT

- The prompt must be SELF-CONTAINED. A fresh child with no memory must be able to follow it completely without needing a parent, a brief, or any other document.
- The prompt must NOT reference any specific corridor (no "Basel," no "Maxwell," no "Even Zeta"). It uses those only as EXAMPLES of format, never as content.
- The prompt must be clear enough for a child who has never seen this project before.
- The prompt must include the EXACT file format specs for both baker-format and game-format, so the child doesn't have to guess.
- The prompt must include the fizzle-writing guidelines (warm, teaching, generous, never punishing, each one specific to the robot×wrong-weapon pair).
- The prompt must include the mathtext-only rule for the game file AND the full-LaTeX allowance for the baker file, and make clear WHICH rules apply to WHICH file.

---

## 5. DELIVERABLE

One file: `CORRIDOR_CREATOR_PROMPT.md` — the complete, general, forever-good prompt that Nir can paste to a fresh child Claude to produce all three corridor files from any Wikipedia topic. Ready to save to `PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT.md`.

---

## 6. HOW TO BEGIN

Write the prompt. You have all the information you need in this document. If anything is unclear, ask Nir. Do NOT write any code or any corridor content — ONLY the reusable child prompt.

---

**END OF PROMPT — Write the unified corridor-creation prompt now.**
