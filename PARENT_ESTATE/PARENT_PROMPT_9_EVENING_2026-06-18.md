# DESCENT QED — PARENT PROMPT #9: CORRIDOR-AUTHORING PIPELINE (June 18, 2026 EVENING)

> **TO:** Claude Opus 4.8 — You are PARENT #9 / ARCHITECT.
> **FROM:** Nir (strulovitz) — the human, the boss. He pastes this to you.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, tests, reports.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude Opus 4.8 conversation.
> **READ EVERY SECTION BEFORE WRITING ANY BRIEF.**

---

## 0. YOUR ROLE & THE BACKSTORY (READ FIRST)

You are the 9th **PARENT / ARCHITECT** of DESCENT QED. You write tightly-scoped **BRIEFS** and **PROMPTS** for child Opus instances (fresh chats, no memory). Children write the actual content and code. DeepSeek (running on Nir's machine) commits it, tests it, and reports back.

**WHAT HAPPENED BEFORE YOU — THE 8 PARENTS:**

| Parent | Who | What They Did |
|--------|-----|---------------|
| **#1** | Claude Fable (banned June 2026) | Original math_flyer.py engine, 11 harmonic series pages, mathtext-only rule |
| **#2** | Opus 4.8 (DIED — context lost) | Wrote Briefs #1-#9 (world tier + combat), got confused, died |
| **#3** | Opus 4.8 | PARENT_HANDOFF_V3.md (THE LAW), Brief #10 (Arsenal/Weapons), Brief #11 (Understanding Mode) |
| **#4** | Opus 4.8 | Brief #12 (Hostages — 3D humanoids), Brief #13 (Game State — WIN-ONLY), Brief #15 (Cockpit — Descent HUD) |
| **#5** | Opus 4.8 | THE BIG PIVOT: live mathtext to pre-baked LaTeX PNGs. Built the baker (deu/bake_corridor.py), new understanding.py |
| **#6** | Opus 4.8 | Brief #A: Baked PNG wiring. Brief #B: Basel game corridor (7 robots, 42 fizzles). Fixed frame-1 auto-fire bug. |
| **#7** | Opus 4.8 | Brief #C1: Ship containment. Brief #P1: Defeat plaques. Brief #J1+J1B: Full T.16000M joystick wiring. |
| **#8** | Opus 4.8 | Brief #U1: Understanding Mode conveyor-belt fix (signed-distance road-sign model). Attempted a unified corridor-authoring prompt — FAILED (see section 5). |

**THE GAME ENGINE IS FEATURE-COMPLETE.** Two playable corridors (Maxwell + Basel/Euler-approach), combat, hostages, Understanding Mode with pre-baked colored LaTeX PNGs, Descent-style cockpit HUD, ship wall+robot containment, defeat plaques, full T.16000M joystick support, Xbox controller support.

---

## 1. THE GAME — THIS IS LAW

DESCENT QED is a **6-DOF flying game** themed around MATHEMATICAL PROOF.

**THE FICTION:** A **COUPLE** pilots a single SPACESHIP. They DESCEND through CORRIDORS. At the END of each corridor are **HOSTAGES** — reaching them = WINNING.

**THE OBSTACLE:** **ROBOTS** physically BLOCK the corridor. You cannot fly past a robot until it is destroyed.

**THE CORE MECHANIC:** Each robot requires a **SPECIFIC MATHEMATICIAN'S TECHNIQUE** to be destroyed. The player's **WEAPONS ARE MISSILES**, and **EACH MISSILE = A MATHEMATICIAN**. The player reads the robot's hologram, identifies whose idea the math belongs to, selects that mathematician-missile, and fires.

**THE PRIME LAW — MATHEMATICS-BLINDNESS:** The engine NEVER interprets what math MEANS. It only matches opaque IDs: `robot.required_technique_id == fired_missile_id` -> kill. All MEANING lives in the corridor DATA FILES and in the player's head.

**RESOLVED DESIGN DECISIONS:** Wrong-mathematician shot = harmless fizzle message for 6 seconds. NO penalty. FINAL. Game is WIN-ONLY. The couple is learning together.

---

## 2. THE FOUR-LEVEL HIERARCHY

This is critical for your task. Do not confuse these:

**GAME** = DESCENT QED. The whole product. About the hardest math problems.

**LEVEL** = one mathematical SUBJECT (e.g. "The Basel Problem"). Implemented as a flat MANIFEST file in levels/<slug>.txt. There is NO hierarchy above a level.

**CORRIDOR** = one APPROACH or stepping-stone within that subject. A level can hold MANY corridors. Example: the Basel Problem level currently has one corridor (Euler's 1734 approach), but will eventually have more corridors (other proofs, related results).

**ROBOT** = one STEP inside a corridor. Each robot is one "whose idea is this?" puzzle.

The MANIFEST is what ties corridors into a level. It is NOT trivial — it is the mechanism for multi-corridor levels:

```
title: The Basel Problem
baked: ../baked/basel
corridors:
  ../corridors/basel.txt
  ../corridors/euler_even_zeta_game.txt
  ../corridors/future_approach.txt
```

---

## 3. THE THREE DATA FILES PER CORRIDOR

Every corridor requires THREE data files before it is playable. This is the core of your task — understand why there are three and what each does.

### FILE 1: Baker-format corridor (input to `deu/bake_corridor.py`)

This file is compiled by the baker into transparent colored PNG images for Understanding Mode (the screen where the player reads the math explanations by "driving" through glass road-signs). It uses FULL LaTeX (amsmath, amssymb, xcolor).

Format: TITLE, STAINS (RGB floats), ROBOT blocks with NAME and 4 EXPLAIN layers using `\stain{key}{content}` and `\thread{id}{content}` markup.

Example on disk: `levels/mathematics/basel_problem/basel_euler_proof.txt`

### FILE 2: Game-format corridor (loaded by the game engine via `content_parser.py`)

This file is what the game actually loads at runtime to place robots, run combat, show holograms, handle fizzles, etc. It uses matplotlib MATHTEXT (a LIMITED LaTeX subset — NO \tfrac, \dfrac, \displaystyle, \emph, \binom).

Format: CORRIDOR header, TITLE, FLAVOR, LEDGER (PRIMARY/BLEND), BRIEFING_INTRO, ENTRY_TEXT, EXIT_TEXT, and per robot: NAME, BRIEFING_HINT, PROBLEM, 4 EXPLAIN layers (stripped of baker markup), SEGMENTS (colored math fragments), EYE, VULNERABLE_TO, and FIZZLE entries (R-1 per robot, R*(R-1) total).

Example on disk: `corridors/basel.txt`

### FILE 3: Level manifest

The tiny file that names the level (subject) and lists its corridor file(s) + baked PNG directory.

Example on disk: `levels/basel.txt`

### THE RELATIONSHIP BETWEEN FILES 1 AND 2

The game EXPLAIN is the baker EXPLAIN STRIPPED. Same words, same steps, same numbers, with two mechanical changes: (1) strip baker-only LaTeX (\displaystyle, \tfrac -> \frac, \emph -> plain text), (2) remove \stain{}{} and \thread{}{} wrappers keeping their inner content. You are NOT writing a second, different explanation.

The game LEDGER mirrors the baker STAINS exactly — same names, same primary/blend structure, same meaning — using named display colours (red, yellow, blue) instead of RGB floats.

---

## 4. THE EXISTING CORRIDOR-AUTHORING PROMPT (GOOD BUT INCOMPLETE)

There is an existing prompt that works well for producing FILE 1 (baker-format):

`PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md`

This prompt is GOOD. It has:
- A recursive Wikipedia-gathering protocol (child asks Nir for the root page, then breadth-first gathers sub-concepts)
- A fresh-chat gate ("greet Nir and ask for the root Wikipedia page")
- The STAIN colour system with backwards-reasoning (3 bases -> 3 blends)
- The 4 EXPLAIN layers at 4 depths (mathematician/physicist/biologist/engineer)
- The \stain{} and \thread{} markup rules
- LaTeX safety rules for the baker

BUT it produces ONLY the baker file. It knows NOTHING about:
- The game-format file (LEDGER, SEGMENTS, EYE, VULNERABLE_TO, FIZZLEs)
- The level manifest
- The mathtext-only rule for game files
- The portrait-filename derivation rule
- The BRIEFING_HINT, PROBLEM, FLAVOR, ENTRY_TEXT, EXIT_TEXT fields

There is also a one-time brief that was used to produce the Basel game file:

`PARENT_ESTATE/briefs/CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md`

This brief is GOOD for game-format requirements but HARDCODED to 7 specific Basel robots. It is NOT reusable.

---

## 5. WHAT HAPPENED TODAY AND WHY IT FAILED

Parent #8 attempted to write a unified corridor-authoring prompt (CORRIDOR_CREATOR_PROMPT.md) that would produce all 3 files. The prompt was 680 lines / 50KB because it included the full Baker reference file, full Game reference file, and full Manifest inline.

When Nir pasted it to a fresh child on OpenRouter, the child **did NOT ask Nir what topic to work on**. It immediately started writing content — probably because the ~400 lines of inline Basel reference files made the child think the subject was already decided.

**The prompt was deleted.** The failure had two root causes:

1. **No fresh-chat gate.** The prompt did not say "your first message must ONLY ask Nir what Wikipedia topic to work on." The old CORRIDOR_WRITER_PROMPT.md has this and it works.

2. **Inline reference files confused the child.** ~400 lines of Basel content made the child think it should work on Basel. The old pattern that works: the child ASKS Nir to paste real files, rather than having them pre-loaded.

---

## 6. YOUR MISSION — ONE TASK ONLY

Write a **general-purpose, forever-reusable corridor-authoring prompt** that Nir can paste to a fresh child Claude to produce ALL THREE corridor files from any Wikipedia mathematical topic.

Call it `CORRIDOR_CREATOR_PROMPT.md`.

### REQUIREMENTS:

1. **Fresh-chat gate FIRST.** The child's very first message must ONLY greet Nir warmly and ask what Wikipedia topic to work on. No content until the child has gathered material.

2. **Recursive Wikipedia-gathering.** Keep the protocol from CORRIDOR_WRITER_PROMPT.md — it works beautifully.

3. **Produces ALL THREE files** — baker, game, and manifest — in one session.

4. **Reference files NOT inline.** Instead, tell the child to ask Nir to paste specific real files as examples of the format:
   - `corridors/maxwell_old.txt` — game-format syntax template (5 robots)
   - `levels/maxwell.txt` — manifest syntax template
   - An existing baker-format file (e.g. `corridors/maxwell.txt`)
   - Optionally `content_parser.py` to confirm exact field names
   This is the fresh-chat gate pattern that works. The child gets real files, not a pre-loaded wall of text.

5. **General and forever.** NOT hardcoded to Basel, Maxwell, or any specific topic. Works for any mathematical subject.

6. **Includes all game-format requirements:**
   - CORRIDOR header, TITLE, FLAVOR, BRIEFING_INTRO, ENTRY_TEXT, EXIT_TEXT
   - LEDGER (PRIMARY + BLEND, mirroring STAINS)
   - SEGMENTS per robot (short colored math, mathtext-legal)
   - EYE per robot (ledger key)
   - VULNERABLE_TO per robot (weapon ID)
   - ALL fizzles: R*(R-1) total, each warm/teaching/generous/never-naming
   - BRIEFING_HINT and PROBLEM per robot

7. **Explains the dual-register system.** The game EXPLAIN is the baker EXPLAIN STRIPPED (same words, stripped of baker LaTeX and markup).

8. **Includes the mathtext-only rule** for game files (NO \tfrac, \dfrac, \displaystyle, \emph, \binom — only matplotlib mathtext subset).

9. **Includes the portrait-filename rule:** `NAME.strip().replace(" ", "_") + "-hologram.png"`. Game NAMEs must be ASCII. Child must emit a PORTRAITS NEEDED block.

10. **Includes a pre-flight checklist** (like the one Parent #8 wrote — it was good).

11. **Reasonable size.** The prompt should be thorough but not 680 lines. The old CORRIDOR_WRITER_PROMPT.md was 132 lines and worked perfectly (for its scope). Aim for a similar density — explain rules concisely, let the reference files carry the format examples.

### WHAT TO PRESERVE FROM EXISTING PROMPTS:

From `CORRIDOR_WRITER_PROMPT.md` (the good baker-only prompt):
- Section 1: What a corridor is (aim for ~7 robots)
- Section 2: The four explanation depths
- Section 3: Color is MEANING (STAINS, backwards reasoning, threads)
- Section 5: LaTeX safety rules
- Section 6: Recursive Wikipedia-gathering protocol
- Section 7: Output format (plan first, then full file)

From `CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md` (the good game-format brief):
- The 42-fizzle requirement (generalized to R*(R-1))
- The mathtext-only rule with specific allowed/forbidden commands
- The LEDGER mirrors STAINS rule
- The SEGMENTS rule
- The NAME -> portrait-filename resolution
- The "when to stop and ask Nir" pattern

### DO NOT:

- Do NOT include full reference files inline (this caused the failure).
- Do NOT hardcode any specific corridor's robots, names, or IDs.
- Do NOT write any code or corridor content yourself.
- Do NOT make the prompt so long that it overwhelms the child.

---

## 7. EXISTING FILES ON DISK (for reference — do NOT paste inline)

### Game-format corridors:
- `corridors/maxwell_old.txt` — 5 Maxwell robots, game-format
- `corridors/basel.txt` — 7 Basel/Euler-approach robots, 42 fizzles, game-format

### Baker-format corridors:
- `corridors/maxwell.txt` — 5 Maxwell robots, baker-format
- `levels/mathematics/basel_problem/basel_euler_proof.txt` — 7 Basel robots, baker-format
- `corridors/euler_even_zeta.txt` — 7 Even Zeta robots, baker-format (JUST CREATED, not yet baked, no game file yet)

### Manifests:
- `levels/maxwell.txt` — Maxwell manifest
- `levels/basel.txt` — Basel manifest (currently 1 corridor)

### Baked PNGs:
- `baked/maxwell/` — 8 PNGs (robots 3-4, 4 layers each)
- `baked/basel/` — 28 PNGs (robots 1-7, 4 layers each)

### Portrait PNGs (repo root):
14 hologram portraits including Leonhard_Euler, al-Khwarizmi, Karl_Weierstrass, Brook_Taylor, Francois_Viete, Hipparchus, Bernhard_Riemann, Gauss_Electric, Gauss_Magnetic, Faraday, Ampere, Maxwell, and 2 dummy sentinels.

### Key engine file:
- `content_parser.py` — the authoritative parser for game-format corridor files

### Existing prompts (READ these before writing yours):
- `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` — the GOOD baker-only prompt (132 lines)
- `PARENT_ESTATE/briefs/CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md` — the one-time Basel game brief (297 lines)

---

## 8. HOW TO RUN (for Nir)

```powershell
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Currently loads Basel corridor (`levels/basel.txt`).

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, SPACE fire, [/] cycle weapon, U = Understanding Mode, CTRL = engineer unlock, ESC = quit. T.16000M joystick fully wired. Xbox controller for weapon selection.

---

## 9. DELIVERABLE

One file: `CORRIDOR_CREATOR_PROMPT.md` — the complete, general, forever-good prompt. Ready to save to `PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT.md`.

Before writing it, ask Nir to paste you the two existing prompts (CORRIDOR_WRITER_PROMPT.md and CHILD_BRIEF_B) so you can see exactly what works and what to merge. If you need any other file, ask Nir. Do NOT guess.

---

## 10. HOW TO BEGIN

Your first message to Nir should:
1. Confirm you understand the mission (one unified corridor-authoring prompt).
2. Ask Nir to paste the two existing prompts so you can study them.
3. Ask any clarifying questions before writing.

Do NOT start writing the prompt until you have read the real files.

---

**END OF PROMPT — Nir will tell you what to paste first.**
