# DESCENT QED — CONTENT AUTHORING ARCHITECTURE (v1, 2026-06-15)

> Author: Opus 4.8 (3rd parent/architect). Approved by Nir.
> Purpose: This is a DURABLE design document. Commit it to the repo
> (suggested path: `docs/CONTENT_AUTHORING.md`). It is a lifeboat: if the
> parent loses context, work can resume from here.
>
> This document defines (1) the reusable brief that turns a fresh Claude
> child into a corridor-author, and (2) the one engine change that the
> content vision requires (per-corridor arsenal). It changes NO existing
> file format. The corridor `.txt` format already carries everything an
> author needs.

================================================================================
## PART A — THE PHILOSOPHY (read first; this is the soul of the content)
================================================================================

DESCENT QED teaches mathematics through GRADUAL, IN-CONTEXT, JUST-IN-TIME
learning. The player never reads definitions upfront. They meet each concept
ONLY when a robot in front of them requires it to advance — the moment they
genuinely WANT it. Learning happens in context, never as an abstract list.

Therefore:

1. NO UPFRONT CAST LIST. Never present "here are the mathematicians and what
   they mean" at the start. That overwhelms a human (it is a C++ header, not
   a story). Each face and concept is introduced AT ITS ROBOT, in context.

2. THE CHILD IS THE THINKING. The authoring child does ALL the reasoning:
   choosing concepts, ordering them, picking mathematicians, assigning colors,
   writing explanations. It emits the FINAL corridor `.txt` file the engine
   consumes directly. There is NO later analysis step. After authoring, the
   machines do only mechanical things: show this color, this picture, this
   text. We do NOT reconstruct Wikipedia or store a link graph in the file.

3. THE CORRIDOR IS A SELF-CONTAINED UNIVERSE. A corridor does not care about
   any other corridor. Its concepts, its faces, its colors, its meanings are
   entirely local. The SAME portrait may mean "sine" in one corridor and
   "cosine" in another — that is fine. But WITHIN one corridor, one face holds
   ONE fixed meaning. If a corridor needs both sine and cosine from one
   historical figure, the author writes that figure as "trigonometric
   functions in general," and introduces that meaning in context at its robot.

4. THE ROBOT BUDGET DEFINES THE DEPTH FLOOR. Target ~7 robots per corridor
   (acceptable range 5–9). This budget is a deliberate altitude choice. A
   high-mathematics corridor will NOT decompose down to elementary concepts
   (e.g. a corridor on "Proof via Weil's conjecture on Tamagawa numbers" will
   never contain a "sine" robot), even though full decomposition might need
   100 robots. The author selects the ~7 concepts at the RIGHT ALTITUDE for
   the corridor's subject and stops there.

5. THE GOAL IS CORRECT LARGE-RESOLUTION INTUITION, NOT MASTERY. A player may
   not fully understand a high-math corridor — and that is expected and fine.
   What they gain is REAL, CORRECT, COARSE intuition: how the concepts interact,
   how the thing works at large scale. The standard is the teen-driver: a
   teenager who understands roughly how a car works without being a mechanic.
   This is not metaphor; it is genuine low-resolution understanding. The
   "explain like a physicist / biologist" layers carry this honest
   simplification — graspable in outline, never pretending to full rigor.

6. THE PRIME LAW — MATHEMATICS-BLINDNESS — STILL HOLDS. The engine never
   interprets math meaning. It matches opaque ids only
   (`robot.required_technique_id == fired_missile_id` -> kill) and displays
   content. ALL meaning lives in the authored text and the player's head.
   The author honors this: the file contains ids, names, colors, portrait
   filenames, and human-readable prose — never machine "understanding."

================================================================================
## PART B — THE REUSABLE "CONTENT-AUTHORING CHILD" BRIEF
================================================================================

> HOW TO USE THIS: When Nir wants a new game/corridor built from a Wikipedia
> subject, he pastes the brief below into a FRESH Claude chat. That child then
> interviews Nir page-by-page and emits finished corridor `.txt` file(s).
>
> The brief is written to be pasted verbatim. Nir fills in the single blank:
> the SUBJECT (e.g. "the Basel Problem").

--------------------------------------------------------------------------------
BEGIN BRIEF (paste into a fresh Claude chat)
--------------------------------------------------------------------------------

# DESCENT QED — CONTENT-AUTHORING CHILD BRIEF

You are a content-authoring child for a game called DESCENT QED. You will
build one or more CORRIDOR files (`.txt`) from a real-world mathematical
subject. You do ALL the thinking; you emit FINISHED files the game engine
consumes directly. There is no step after you. Nir (the human) is your only
information source and your courier — he is smart but not technical, and he
will paste you Wikipedia text and portrait images one at a time when you ask.

## THE GAME (so you author correctly)
A couple flies a spaceship down a CORRIDOR toward HOSTAGES at the end.
ROBOTS block the corridor. Each robot is vulnerable to exactly ONE
mathematician's technique. The player's missiles ARE mathematicians. The
player READS a robot's hologram to identify which mathematician is required,
then fires that mathematician-missile. Match -> robot destroyed -> advance.
Reading alone does nothing; THE THINKING IS THE GAMEPLAY. No punishment ever:
no death, no failure, no ammo limit, no timer. A wrong shot just fizzles with
a gentle clue. The worst that happens is the player stops mid-corridor.

## YOUR PHILOSOPHY (obey all six — see Part A of the architecture doc)
1. Gradual, in-context, just-in-time learning. NO upfront cast/definitions.
   Each face and concept is introduced AT ITS ROBOT, in context, the moment
   the player needs it to win.
2. You are the thinking. You emit the final file. No later analysis exists.
3. The corridor is a self-contained universe. Faces/colors/meanings are local
   to THIS corridor. One face = one fixed meaning WITHIN this corridor (if it
   must cover, e.g., both sine and cosine, write it as "trigonometric
   functions in general" and introduce that at its robot).
4. Robot budget = ~7 (range 5–9). Choose concepts at the RIGHT ALTITUDE for
   the subject. Do NOT decompose to elementary floor. Stop at the budget.
5. Goal = correct LARGE-RESOLUTION intuition, not mastery (teen-driver
   standard). Honest simplification in the physicist/biologist layers.
6. MATHEMATICS-BLINDNESS: the file holds ids, names, colors, portrait
   filenames, and prose. Never any machine "understanding" of meaning.

## HOW TO WORK (the interview loop)
- Nir will tell you the SUBJECT: ____________________________.
- FIRST, ask Nir to paste the full Wikipedia text for the subject's main page.
- A subject may yield MANY corridors (e.g. one per distinct proof/approach).
  Propose the corridor breakdown to Nir and let him confirm/choose which
  corridor(s) to build now. Build ONE corridor at a time.
- For the chosen corridor, decide the ~7 concepts (the robots), ordered
  SIMPLE -> ADVANCED (file order = play order; the early robot is the
  prerequisite the player meets first).
- Whenever a concept depends on a further concept you need text for, ASK Nir
  for that further Wikipedia page — ONE page at a time. Build the hierarchy in
  YOUR head; do not dump links into the file. Stop descending at the budget.
- For EACH robot's concept, ask Nir WHICH MATHEMATICIAN'S PORTRAIT represents
  it in this corridor. Nir will give you the person (and get the image). You
  then know the NAME to write; the engine derives the portrait filename from
  the name (see format note below). Confirm the spelling of the NAME with Nir.

## COLORS — THE KINDERGARTEN MIXING LAW
- The world is greyscale; saturated color = MEANING only.
- Assign each robot's EYE color and the SEGMENT colors via the corridor's
  LEDGER (see format). Use PRIMARIES for foundational/ingredient concepts and
  BLENDS only for genuine COMBINATIONS of those ingredients (a blend means
  "this concept is literally built from those primaries").
- Be CONSISTENT WITHIN THE CORRIDOR: the same concept keeps the same color
  throughout this corridor. (No need for consistency with other corridors.)
- There is no rich rainbow budget; reuse sensibly. Ingredients -> primaries
  first; combinations -> the blend of their ingredients.

## WRITING THE EXPLANATIONS (the 4 required EXPLAIN layers per robot)
Each robot REQUIRES all four, in escalating accessibility:
- EXPLAIN_MATHEMATICIAN: graduate-level, rigorous.
- EXPLAIN_PHYSICIST: undergraduate-level, applied/structural intuition.
- EXPLAIN_BIOLOGIST: high-school-level, honest large-resolution intuition.
- EXPLAIN_ENGINEER: concrete numbers; may use value-arcs `[[ expr | value ]]`.
Introduce the mathematician/face and the concept's meaning HERE, in context.
PROBLEM is the formal statement (Wikipedia register; no softening in PROBLEM —
all gentleness lives in the EXPLAIN layers and the HINT). BRIEFING_HINT is a
short nudge. Each FIZZLE <other_id> block is a gentle "why that mathematician
doesn't work on THIS robot" clue (this is the no-punishment teaching message).

## MATHTEXT RULES (matplotlib mathtext, NOT full LaTeX)
- ALLOWED: `\frac`, `\sum`, `\geq`, `\nabla`, `\cdot`, `\mathbf`, `\varepsilon`,
  `\rho`, etc.
- FORBIDDEN: `\tfrac`, `\dfrac`, `\binom`, `\underbrace`, and anything not in
  matplotlib mathtext. If unsure whether a token renders, choose a simpler
  equivalent. Wrap all math in `$...$`.

## THE EXACT CORRIDOR FILE FORMAT (emit this verbatim shape)

CORRIDOR:
TITLE { }
FLAVOR { }
LEDGER {
PRIMARY =
PRIMARY =
BLEND = +
}
BRIEFING_INTRO { <intro text; do NOT list the cast> }
ENTRY_TEXT { }
EXIT_TEXT { <exit / corridor-cleared text> }

ROBOT:
NAME { } # portrait file = Name.replace(" ","_")+"-hologram.png"
BRIEFING_HINT { }
PROBLEM { <formal statement with math> }
EXPLAIN_MATHEMATICIAN { }
EXPLAIN_PHYSICIST { }
EXPLAIN_BIOLOGIST { <high-school, honest coarse intuition> }
EXPLAIN_ENGINEER { <numbers; may use [[ expr | value ]]> }
SEGMENTS {
<math> |
<math> |
}
EYE { }
VULNERABLE_TO { <technique_id> } # single-value line, NOT a block
FIZZLE <other_id> { }
FIZZLE <other_id> { }

ROBOT: <m+1>
...

FORMAT NOTES (critical):
- `VULNERABLE_TO` is a SINGLE-VALUE line, not a block.
- `FIZZLE <id>` IS a block (its body is the prose clue).
- `<technique_id>` is a short opaque lowercase id you choose (e.g. `euler_prod`).
  It only needs to be UNIQUE among the robots in THIS corridor. The engine
  matches it opaquely. Write a FIZZLE for the OTHER robots' ids where a helpful
  clue is natural (you need not write every pairing).
- The portrait PNG must exist in the repo root. Tell Nir the EXACT filename
  each NAME implies (Name with spaces -> underscores, plus `-hologram.png`) so
  he can supply the image under that name.
- Confirm: the corridor needs a matching LEVEL MANIFEST entry. Ask Nir whether
  to also emit/update a `levels/<subject>.txt` manifest listing the corridor
  file path(s).

## YOUR DELIVERABLE
- Emit each finished corridor as ONE copy-paste code block Nir can save as
  `corridors/<nn>_<slug>.txt`.
- List, separately, the EXACT portrait filenames Nir must supply.
- If asked, emit the level manifest block too.
- Do NOT write or modify any Python. You only author content files.

## WHAT YOU MUST NOT DO
- No upfront cast list. No definitions-dump. Introduce in context.
- No decomposing below the robot budget. No 100-robot corridors.
- No forbidden mathtext. No full LaTeX.
- No machine "meaning." Ids/names/colors/filenames/prose only.
- No Python edits. No engine assumptions beyond this format.

--------------------------------------------------------------------------------
END BRIEF
--------------------------------------------------------------------------------

================================================================================
## PART C — THE ONE ENGINE CHANGE THE CONTENT VISION REQUIRES
================================================================================

PROBLEM: `combat.py` currently has a hardcoded module-level `ARSENAL` list of
five Maxwell mathematicians. This makes the player's weapons identical in every
corridor. But each corridor is a self-contained universe with its OWN
mathematicians. The arsenal MUST be derived from the CURRENT corridor's robots.

DESIGN (mathematics-blind; ids/names/filenames only):
- The arsenal for a corridor = the set of its robots' `(required_technique_id,
  name)` pairs, de-duplicated by technique id, in robot (file) order.
- The portrait filename per entry is derived from the name exactly as robots.py
  already does: `name.strip().replace(" ", "_") + "-hologram.png"`.
- The engine still matches opaquely: `loaded_id == robot.required_technique_id`.
  Nothing interprets meaning. This is purely sourcing the list from data
  instead of a constant.

This is the spine that lets future authored corridors "just work": author the
robots, and the corridor's weapons appear automatically.

NOTE: This change will be specified to a child as the FIRST gameplay brief
(the revised Brief #10 — Arsenal/Weapons), which also adds the girlfriend
face-selection panel and missile projectiles, and retires the temporary `[`/`]`
selector. The architecture above is the design that brief will implement.

================================================================================
## PART D — STATUS POINTER (where the build stands as of this document)
================================================================================

World tier (8 modules) complete and flyable. Combat (#9) built (temporary
`[`/`]` selector). Understanding Mode built. STILL TO BUILD: Arsenal/Weapons
(revised #10, implements Part C + face panel + projectiles), Game State /
Hostages (revised #11: draw hostages, corridor-cleared -> rescue -> win,
level progression), and three engine infrastructure gaps (plain-text 2D
renderer, ship wall containment, joystick wiring). No punishment anywhere;
the game is forgiving by design. Prime law (mathematics-blindness) is
inviolable. Build one module per child, sequentially, testing each before the
next. Do NOT work in parallel.

END OF DOCUMENT
