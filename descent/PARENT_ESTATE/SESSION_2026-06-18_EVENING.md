# SESSION CONTEXT — June 18, 2026 EVENING

> **Project:** DESCENT QED engine
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`
> **Builder:** DeepSeek V4 Pro (OpenCode)
> **Time:** ~10 PM Israel time. Nir is going to sleep.

---

## WHAT HAPPENED TODAY

### 1. Understanding Mode conveyor belt — FIXED (Brief #U1)

Parent #8 (Opus 4.8) wrote Brief #U1 for a child to fix the "conveyor belt" bug
in Understanding Mode. The child replaced absolute-distance with signed-distance
in understanding.py. Key changes:

- `abs(self.focus - i)` replaced with signed `s_i = i - f` (s < 0 = behind = CULLED)
- Entry focus starts at ENTRY_FOCUS = -1.0 (sign 0 at fits-on-screen framing)
- ESC is now INERT inside Understanding Mode (app.py already blocked ESC-quit)
- Exit only by reversing past sign 0 by 1/3 of a spacing
- Pan resets when nearest sign changes

**Bug found and fixed:** The child's initial code instantly closed Understanding
Mode because ENTRY_FOCUS (-1.0) was already past EXIT_THRESHOLD (-0.333). Fixed
by adding EXIT_FOCUS = ENTRY_FOCUS - EXIT_THRESHOLD = -1.333.

**Status:** WORKING. Nir confirmed "it works perfectly."

Files changed: understanding.py only.
Commits: 233cf7c (initial), b7fb588 (exit fix)

### 2. New corridor baker file created — euler_even_zeta.txt

A corridor-writer child (using the old CORRIDOR_WRITER_PROMPT.md) produced a
baker-format corridor file for "Euler's Sine Product and the Even Zeta Values"
— the 2nd corridor of the Basel Problem level. 7 robots, 6 stains.

Saved to: corridors/euler_even_zeta.txt
Commit: 3983749

**PROBLEM DISCOVERED:** This child only produced the baker-format file (1 of 3
needed files). The game-format file (with FIZZLE, VULNERABLE_TO, SEGMENTS, etc.)
and the level manifest update were NOT produced. The old CORRIDOR_WRITER_PROMPT.md
only knows about baker-format files.

### 3. Attempted to create unified corridor-creation prompt — FAILED

Parent #8 wrote a new prompt (CORRIDOR_CREATOR_PROMPT.md) that was supposed to
be a "forever" general-purpose prompt making a child produce all 3 files. But
when Nir pasted it to a fresh child on OpenRouter:

- The child did NOT ask Nir what topic to work on
- The child immediately started writing content (probably because the prompt
  included full Basel reference files inline, confusing the child)
- Nir deleted the prompt in frustration

Commit: 5c20e55 (deleted)

**ROOT CAUSE:** The prompt lacked a clear "STEP 1: your first message must ONLY
ask Nir what Wikipedia topic to work on" instruction. The inline Basel reference
files (~400 lines) likely made the child think the subject was already decided.

---

## WHAT TO DO TOMORROW — THE #1 PRIORITY

### Create a NEW parent prompt and ask a fresh Opus 4.8 to write a general-purpose corridor-authoring prompt.

**The goal:** A single prompt that Nir can paste to a fresh child, the child asks
for a Wikipedia page, gathers material, and produces ALL 3 files:
1. Baker file (STAINS, full LaTeX, \stain{}/\thread{} — for baking PNGs)
2. Game file (LEDGER, SEGMENTS, EYE, VULNERABLE_TO, all FIZZLEs — for the engine)
3. Level manifest (title, baked path, corridor list)

**What worked well (KEEP):**
- CORRIDOR_WRITER_PROMPT.md's recursive Wikipedia-gathering protocol (section 6)
- CORRIDOR_WRITER_PROMPT.md's fresh-chat gate ("greet Nir and ask for the topic")
- CORRIDOR_WRITER_PROMPT.md's STAIN color system (backwards reasoning)
- CHILD_BRIEF_B's game-format requirements (fizzles, LEDGER, SEGMENTS, etc.)
- The parent's CORRIDOR_CREATOR_PROMPT sections 0-11 had good explanations of
  the dual-register system, the colour logic, naming conventions, etc.

**What failed (FIX):**
- NO fresh-chat gate telling the child to ask for the topic FIRST
- Inline reference files (~400 lines) confused the child into thinking the
  subject was already decided
- The prompt was too large (680 lines / 50KB) — hard to paste

**Key design decisions for the new prompt:**
- The prompt MUST start with a clear instruction: "Your first message to Nir
  must ONLY ask what Wikipedia topic to work on. Do not write any content yet."
- Reference files should NOT be inline. Instead, the child should ask Nir to
  paste existing files as examples (the fresh-chat gate pattern that works).
- The prompt should be general — NOT hardcoded to Basel or Maxwell.
- The prompt should explain both file formats clearly (baker vs game) and the
  relationship between them (game EXPLAIN = baker EXPLAIN stripped of LaTeX).
- The fizzle formula: R robots = R*(R-1) fizzles.
- The portrait filename rule: NAME.strip().replace(" ", "_") + "-hologram.png"
- The mathtext-only rule for game files.

**Files to reference when writing the parent prompt:**
- `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` — the GOOD old baker-only prompt
- `PARENT_ESTATE/briefs/CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md` — game-format brief
- `corridors/maxwell_old.txt` — game-format example (5 robots)
- `corridors/basel.txt` — game-format example (7 robots, 42 fizzles)
- `levels/mathematics/basel_problem/basel_euler_proof.txt` — baker-format example
- `levels/basel.txt` — manifest example
- `content_parser.py` — the authoritative parser

**The parent prompt file should be saved as:**
`PARENT_ESTATE/PARENT_PROMPT_9_CORRIDOR_PIPELINE_2026-06-19.md` (or similar)

---

## CURRENT STATE OF THE REPO

| Item | Status |
|------|--------|
| Understanding Mode conveyor belt | FIXED |
| Basel corridor (Euler's approach) | PLAYABLE (baker + game + manifest) |
| Even Zeta corridor | BAKER FILE ONLY (corridors/euler_even_zeta.txt) — needs game file + manifest update |
| Unified corridor prompt | DELETED — needs redo tomorrow with new parent |
| Ship containment | WORKING |
| Joystick | FULLY WIRED |
| Cockpit/Combat/Hostages | ALL WORKING |
| Git | Clean, pushed |

---

## GIT LOG (today)

```
5c20e55 Delete CORRIDOR_CREATOR_PROMPT.md -- child ignores topic, useless
f2cdb56 Fix CORRIDOR_CREATOR_PROMPT: restore em-dashes and accents
6e69bba CORRIDOR_CREATOR_PROMPT: unified forever-prompt for corridor authoring
155e1c8 Fix Parent Prompt: Parent #8 (not #9), add manifest importance
dad324d Parent Prompt #9: fix corridor-creation pipeline
3983749 New baker-format corridor: Euler's Sine Product and the Even Zeta Values
b7fb588 Brief #U1 fix: exit threshold measured from ENTRY_FOCUS, not zero
233cf7c Child Brief #U1 applied: signed-distance road-sign model kills conveyor belt
493d5e2 Child Brief #U1: Understanding Mode conveyor belt fix (road-signs in fog)
```

---

## REMINDERS FOR TOMORROW

- Nir is the human. He is NOT a programmer. Be clear, warm, use emojis.
- Do NOT start building or fixing on your own — do exactly what Nir/child says.
- The old CORRIDOR_WRITER_PROMPT.md is GOOD but incomplete (baker only).
- The game needs TWO format files per corridor (baker + game), NOT one.
- The manifest groups corridors into levels (multi-corridor support).
- corridors/euler_even_zeta.txt exists but is ONLY the baker half — the new
  unified child should eventually produce all 3 files for this corridor.

Good night Nir! Sleep well! Tomorrow we make the pipeline right! :-)
