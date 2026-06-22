# PARENT PROMPT #10 — Complete the game: auto-load ALL NINE corridors
### Written 2026-06-23, EVENING (Israel time) · for a fresh Claude Opus 4.8 architect

> **TO:** Claude Opus 4.8 — you are being asked to act as the **ARCHITECT / PARENT** (Parent #10)
> of the DESCENT QED game.
> **FROM:** Nir (strulovitz) — the human, the boss. He will paste this whole document to you.
> **BUILDER:** DeepSeek V4 Pro (running in OpenCode on Nir's Windows PC) — commits code, runs the
> baker, fixes bugs, wires hardware, pushes to GitHub.
>
> **IMPORTANT — your role here:** We are deliberately NOT telling you what to do or how to do it.
> We describe the project, the current situation, and **what we want**. You are the doctor; we only
> describe the symptoms and the wish. Please diagnose the best technical path yourself, ask for any
> real files you need to see, and propose the approach. Nir decides and DeepSeek builds.

---

## 0. THE BIG PICTURE — Peak Together & DESCENT QED

**Peak Together** (website: peaktogether.me, repo: `https://github.com/strulovitz/peaktogether-website`)
is a free, open-source platform of cooperative games that turn the hardest unsolved problems in
science and mathematics into adventures a **couple** can play together on one computer. The vibe:
a nostalgic-90s-DOS-games arcade on the surface, a science museum underneath. Built for two players
side by side (solo works too).

**DESCENT QED** is the first game — a **6-DOF flying game** (inspired by Descent, 1995) themed on
**mathematical proof**. "QED" = quod erat demonstrandum.

**The fiction & core loop:**
- A couple pilots a single spaceship and **descends through CORRIDORS**.
- **ROBOTS physically block** the corridor; you cannot pass until one is destroyed.
- Each robot is one **step of a mathematical proof**, and is vulnerable to exactly **one
  mathematician's technique**. The player's weapons are **missiles, and each missile is a
  mathematician**. To destroy a robot you fire the missile whose mathematician that proof-step
  belongs to.
- **READING is the identification step:** the player reads the robot's hologram to figure out which
  mathematician is required, then selects and fires that mathematician. The *thinking* is the
  gameplay. Reading alone does nothing.
- **Wrong mathematician → harmless "fizzle" message for ~6 seconds. No penalty. FINAL.** (The couple
  is learning together; punishment has no place here.)
- At the end of each corridor are **HOSTAGES** — reaching/rescuing them = winning that corridor.

**THE PRIME LAW — mathematics-blindness:** the engine never interprets what the math *means*. It
only matches opaque identifiers: `robot.required_technique_id == fired_missile_id` → kill. All
meaning lives in the corridor content files and in the players' heads. No module hardcodes
color-to-meaning.

**Tech:** Python 3.12, pygame + PyOpenGL, legacy fixed-function OpenGL (no shaders). Hardware:
keyboard + mouse, plus a Thrustmaster T.16000M flight stick (pilot) and an Xbox controller
(manipulator), all wired and working.

---

## 1. THE WORLD STRUCTURE (relevant to this task)

- The player spawns in a grey rocky **ATRIUM** — the interior of a big faceted sphere.
- The atrium wall has **N doorways**, distributed by a **Fibonacci sphere**. Each doorway leads to
  one **bent CORRIDOR**.
- Each corridor is a tube with the proof's robots stationed along it, ending in a **blue CAVERN**
  (the hostage room).
- The hub builder (`hub_builder.py`) creates the atrium and one doorway per corridor in the loaded
  level; `corridor_builder.py` builds each corridor's geometry, robot positions, and cavern.
- The Fibonacci-sphere placement and the hub contract are **already designed and built — do NOT
  re-improvise them.** For the record (verify exact names by reading the files): the hub exposes
  `spawn_pose() -> ((x,y,z),(yaw,pitch))` (radians, forward = −Z; yaw = atan2(dx,−dz), pitch =
  asin(dy)), `door_poses() -> list[((x,y,z),(nx,ny,nz))]` (door centre + outward Fibonacci normal),
  `direction(i) -> unit vec3`, a `hub.corridors` list, `inside(point, margin) -> bool`, and
  `update()/draw_world()/draw_robots()/draw_labels()`. The Fibonacci spacing is guaranteed
  non-intersecting for N up to ~12 at the hub radius (the hub asserts a minimum pairwise angle), so
  **nine corridors → nine doorways is well within the safe range.** The precise Fibonacci-sphere
  maths and design rationale are written up in `INTERFACES_v0.1.md` **Part 2** (see §7, Reference
  Documents) — and in Claude Fable's original doctrine. Read them; don't reinvent them.
- Canonical per-frame render order is strict (clear → ship.update → apply_view → fog → queue walls
  → flush_walls EXACTLY once → robots → labels → HUD → flip). Forgetting the single `flush_walls`
  call = silent black screen. (DeepSeek knows this trap.)

---

## 2. THE CONTENT PIPELINE (how a corridor is made)

Each corridor is described by THREE hand-authored text files:

1. **A baker file** — `descent/levels/mathematics/basel_problem/<name>_proof.txt`. Per robot: a
   `NAME` and four reading-screen layers (`EXPLAIN_MATHEMATICIAN/PHYSICIST/BIOLOGIST/ENGINEER`),
   written in full LaTeX with custom colour macros `\stain{key}{...}` (sacred background wash) and
   `\thread{id}{...}` (page-local foreground), plus engineer value-arcs `[[ expr | value ]]`.
2. **A game file** — `descent/corridors/NN_<name>.txt`. Holds `CORRIDOR`, `TITLE`, `FLAVOR`,
   `LEDGER` (colour palette: PRIMARY/BLEND keys), `BRIEFING_INTRO/ENTRY_TEXT/EXIT_TEXT`, and per
   robot: `NAME`, `BRIEFING_HINT`, `PROBLEM`, the four `EXPLAIN_*` (mathtext fallbacks), `SEGMENTS`
   (floating coloured equation pieces on the robot in 3D), `EYE`, `VULNERABLE_TO <id>`, and one
   `FIZZLE <id> { ... }` per other mathematician.
3. **A manifest line** — in a level manifest under `descent/levels/`, pointing a corridor file to
   its baked-image folder.

**The baker** (`descent/deu/bake_corridor.py`) compiles each robot×layer into a transparent coloured
PNG via `pdflatex` → `pdftocairo`, into `descent/baked/basel/<corridor>/robotN_<layer>.png`
(28 PNGs per corridor). **Understanding Mode** (`descent/understanding.py`): press **U** near a
robot to enter a fog-and-glass space and "drive" (mouse wheel / joystick) through floating glass
road-sign panels — the four baked depth layers (engineer is deepest, unlocked with CTRL / a joystick
button).

---

## 3. WHAT IS BUILT & WORKING RIGHT NOW

**Engine (all complete, tested, flown):** world tier (atrium, doorways, corridors, caverns); combat
(missiles = mathematicians, ID-matching, fizzles); arsenal / weapon selection; game state + hostage
rescue + win; Descent-style cockpit HUD; ship wall+robot containment; Understanding Mode (pre-baked
PNG road-signs, signed-distance model); full T.16000M joystick + Xbox controller; the offline baker
with stain/thread colours and TikZ value-arcs.

**The Basel Problem level — NINE corridors complete & playable** (each: 7 robots, 28 baked layers,
value-arcs, portraits, 42 fizzles):
1. Euler's 1734 approach (sine product)
2. Symmetric-Polynomial Ascent (Newton/Girard → all even zeta)
3. The Riemann Zeta Function
4. Euler's Formula & L'Hôpital's Rule
5. A Proof Using Fourier Series
6. Parseval's Identity & the Recurrence
7. Differentiation Under the Integral Sign (Feynman trick)
8. Cauchy's Elementary Descent (cotangent sum + squeeze)
9. Geometry Meets Arithmetic (assuming Weil's conjecture on Tamagawa numbers)

Each corridor was authored by a fresh Opus *child* using a reusable "**FOREVER prompt**"
(`descent/PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT_FOREVER.md`); DeepSeek baked, fixed bugs, wired, and
pushed. **We are now PAUSING corridor creation — nine is enough for this game.** (Other proofs,
including a geometric one that needs diagrams, will go into a DIFFERENT future game.)

**Repo layout:** all game files under `descent/`. Project memory: `descent/WORKFLOW.md`. Design LAW:
`descent/PARENT_ESTATE/PARENT_HANDOFF_V3.md`. Launch: `cd descent && python app.py`.

---

## 4. THE CURRENT SITUATION (the symptom)

**Today the game loads ONE corridor at a time.** In `descent/app.py` there is a line
`LEVEL_MANIFEST = "levels/basel_c9.txt"`, and `basel_c9.txt` is a tiny "single-corridor test
manifest" that loads only corridor 9. There is one such test manifest per corridor
(`levels/basel_c2.txt` … `levels/basel_c9.txt`). To try a different corridor, we currently
hand-edit that one line in `app.py`. That is fine for testing one proof, but it is NOT a finished
game.

There is ALSO a **full nine-corridor manifest**, `descent/levels/basel.txt`, which lists all nine
corridor files together with their baked-image folders (one `baked=` path per corridor). **But
loading all nine corridors together has never actually been tested**, and our own notes flag
possible problems, for example:
- holograms or floating SEGMENT text potentially **bleeding between robots or between corridors**;
- open questions about **how the player should travel from one corridor to the next** (the atrium
  already supports one doorway per corridor — so nine corridors would mean nine doorways — but this
  has not been exercised with real content);
- how **winning / progression** should work across nine corridors (is the game "won" when all nine
  are cleared? does each corridor's hostage-rescue feed a larger completion? etc.).

So: the nine proofs all exist and each plays correctly in isolation, but the game has never been
assembled into a single, complete, all-nine experience.

---

## 5. WHAT WE WANT — a COMPLETE game

We want to make this Basel-Problem game feel **COMPLETE**, by which we mean: **the game should
automatically load and present ALL NINE corridors as one finished experience**, so a couple can fly
the entire Basel Problem — all nine proofs — without anyone hand-editing a manifest line.

That is the whole wish. We are intentionally NOT prescribing the structure or the method. As the
architect, please decide:
- how the nine corridors should be assembled into one game (e.g. all reachable from the atrium's
  doorways, or some progression, or whatever feels best — your call);
- how the player travels among the nine corridors;
- what, if anything, needs to be fixed or added in the engine to make multi-corridor play **clean**
  (no hologram/text bleed between robots or corridors, correct per-corridor baked images, stable
  navigation);
- how progression and the overall win condition should work across nine corridors;
- how to verify it (what Nir should SEE on screen when it works).

We're describing the symptoms and the goal; the diagnosis and the cure are yours. Please get
oriented first — ask Nir to paste any real files you want to study (good candidates: `app.py`,
`level_parser.py`, `levels/basel.txt`, one single-corridor manifest like `levels/basel_c9.txt`,
`hub_builder.py`, `corridor_builder.py`, `understanding.py`, `game_state.py` if it exists) — and
then propose how you'd like to proceed. Break it into as many or as few briefs as you judge best;
DeepSeek implements, tests on Nir's machine, and reports back.

---

## 6. PRACTICAL FACTS YOU MAY WANT

- Repo: `https://github.com/strulovitz/peaktogether-website` · local: `C:\Users\nir_s\peaktogether-website`
- Game root: `descent/` · launch: `cd descent && python app.py`
- The full nine-corridor manifest: `descent/levels/basel.txt` (lists all 9 corridor files +
  per-corridor `baked=` folders).
- Single-corridor test manifests: `descent/levels/basel_c2.txt` … `basel_c9.txt`.
- `app.py` currently has `LEVEL_MANIFEST = "levels/basel_c9.txt"`.
- Baked reading-screens live per corridor in `descent/baked/basel/<corridor>/robotN_<layer>.png`.
- Each corridor has 7 robots; mathematician portrait holograms live at
  `descent/<Name_With_Underscores>-hologram.png`.
- DeepSeek is reliable on mechanical work (committing your verbatim files, editing app.py, running
  the game/baker, fixing bugs, pushing). Write briefs for him concretely; paste the exact code/API
  he needs so he never has to guess. He cannot show you the game running, but he can run it, read
  any file, and report precisely what happens / any error.

---

## 7. REFERENCE DOCUMENTS & ENGINE SOURCE (read these / ask Nir to paste them)

Everything previous parents — and the project's original designer **"Claude Fable"** — wrote about
the engine, the world, the **Fibonacci-sphere hub**, and the multi-corridor question already lives
in the repo. Please READ (or ask Nir to paste) whatever you need **before** proposing a plan. Never
invent an API — read the real signatures (a hard rule the project learned from past mistakes). The
most relevant material (paths under `descent/` unless noted):

**Design / architecture (in `PARENT_ESTATE/`):**
- `INTERFACES_v0.1.md` — the engine interface spec. **Part 2 is "THE HUB & FIBONACCI-SPHERE GEOMETRY
  (the core engine novelty)"**: exact Fibonacci-sphere placement, the non-intersection / collision
  canon, and the full `HubGeometry` API. This is THE place for the geometry details.
- `PARENT_HANDOFF_V3.md` — the current design **LAW** (game rules, module list, data objects, the
  corridor file format, the canonical frame order + the flush trap).
- `DESCENT_QED_PARENT_HANDOFF.md` — an earlier full architect handoff (world + Fibonacci + module
  contracts).
- `reports/COMPLETION_REPORT_06_hub_builder.md` — the **exact hub API as actually built**
  (`spawn_pose`/`door_poses` shapes, the Fibonacci yaw/pitch convention, the collision assertion).
- `reports/COMPLETION_REPORT_07_level_parser.md` — how a level manifest becomes a `Level` of
  corridors (the parser already asserts unique titles + unique `CORRIDOR` numbers and
  `len(hub.corridors) == len(level.corridors) == len(door_poses())`).

**The original designer's doctrine (in `BIBLE/`):**
- `CLAUDE_FABLE_DESCENT_QED_DOCTRINE.md`, `CLAUDE_FABLE_CONTEXT.md`,
  `CLAUDE_FABLE_CONTEXT_V2_BASEL.md` — "Claude Fable"'s original design doctrine and context (the
  deeper *why* behind the hub, the colours, the reading system, the two-player roles).

**Prior parents already scoped MULTI-CORRIDOR — worth reading:**
- `PARENT_PROMPT_9_EVENING_2026-06-18.md` — already spells out the exact multi-corridor test: "enter
  corridor 1, complete, return to atrium, enter corridor 2; verify no cross-corridor bleed of
  holograms / weapons / hostages / Understanding Mode."
- `PARENT_PROMPT_8_EVENING_2026-06-17.md` — earlier notes that the hub already supports
  `hub.corridors`, but only one corridor had ever been attached.

**Engine source files (in `descent/`):** `app.py`, `level_parser.py`, `content_parser.py`,
`hub_builder.py`, `corridor_builder.py`, `render.py`, `robots.py`, `combat.py`, `game_state.py`,
`understanding.py`, `palette.py`, `cockpit.py`, `containment.py`, `gamepad.py`. Manifests:
`levels/basel.txt` (all nine) and `levels/basel_cN.txt` (single-corridor). Baker:
`deu/bake_corridor.py`. Project memory: `WORKFLOW.md`.

DeepSeek can paste any of these to you verbatim on request.

## 8. ONE-LINE SUMMARY

DESCENT QED is a 6-DOF couples' game where you fly through mathematical-proof corridors and destroy
each robot by firing the mathematician whose idea that proof-step belongs to. **Nine Basel-Problem
corridors are fully built and each plays correctly on its own, but the game still loads only one
corridor at a time via a hand-edited manifest line.** We want the finished game to **automatically
load all nine corridors as one complete experience**, with clean navigation between them and no
cross-corridor bleed. You are the architect — please diagnose the best way to assemble and complete
the game, ask for any files you need, and propose the plan. 🩺

**END OF PROMPT — Nir will now tell you to begin.**
