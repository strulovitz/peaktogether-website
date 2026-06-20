# PEAK TOGETHER — PARENT PROMPT #10: REPO REORGANIZATION + GENERIC FOLDER ARCHITECTURE (June 20, 2026)

> **TO:** Claude Opus 4.8 — You are PARENT #10 / ARCHITECT.
> **FROM:** Nir (strulovitz) — the human, the boss.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, tests, reports.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude Opus 4.8 conversation.
> **READ EVERY SECTION BEFORE WRITING ANYTHING.**

---

## 0. YOUR ROLE — TWO MISSIONS

You are the 10th PARENT / ARCHITECT. You write tightly-scoped BRIEFS for child Opus instances and design decisions for the builder (DeepSeek). You have TWO missions today, both about making the project scale cleanly to the future:

**MISSION A — REPO REORGANIZATION (the bigger one):** Peak Together is NOT just Descent QED. It is a platform for MANY games — Descent, Doom, Pinball, fighting games, RTS games, and more — each teaching science through a different classic game genre. Right now, ALL of Descent QED's files (Python modules, corridors, levels, baked images, portraits, BIBLE, docs) are dumped directly in the repo root, mixed in with the WEBSITE files (index.html, style.css, etc.). This must be separated: all Descent files move into a `descent/` folder, so that when Nir starts building a Doom clone tomorrow, it gets its own `doom/` folder and nothing gets mixed up.

**MISSION B — PER-CORRIDOR BAKED IMAGE ISOLATION:** Within Descent, the baked-image architecture uses one shared folder per level. Two corridors with the same robot numbers collide. Each corridor needs its own isolated baked-image folder. This is a SUBSET of Mission A — it's the internal folder structure within `descent/`.

---

## 1. THE GAME IN ONE PARAGRAPH

DESCENT QED is a 6-DOF flying game where a couple descends through corridors, each corridor being one mathematical proof/approach broken into robots. Each robot is a puzzle ("whose idea is this?"). The player fires mathematician-missiles to destroy robots. Wrong shots produce gentle teaching messages ("fizzles"). Understanding Mode lets the player read colored LaTeX explanations (baked as transparent PNGs). The engine is mathematics-blind — it never interprets math, only matches opaque IDs.

---

## 1b. THE BIGGER PICTURE — PEAK TOGETHER IS A MULTI-GAME PLATFORM

Peak Together's website (peaktogether.me) is the HOME of many games, not just Descent QED. Nir's roadmap includes:
- **Descent QED** — 6-DOF corridor flight (Descent 1995 tribute) — CURRENTLY BEING BUILT
- **A Doom/Quake clone** — graph-theory mazes
- **A fighting game** — trigonometry and integrals as moves/countermoves
- **A pinball game** — motion curves along function graphs
- **An RTS game** — biochemistry, building molecules
- **A roller coaster game** — topology
- And about 8 more game concepts

Each game is a separate codebase with its own engine, its own data files, its own assets. They all live under the same GitHub repo and the same website. The website's job is to present them all; each game's job is to be self-contained.

**RIGHT NOW, the repo is a mess.** Descent QED's Python files, corridor data, baked images, portrait PNGs, development docs (BIBLE/, PARENT_ESTATE/), and everything else are ALL dumped directly in the repo root alongside the website's HTML, CSS, and JS files. When Nir starts building the Doom clone, there would be nowhere clean to put it — Doom's Python files would mix with Descent's Python files in the same root folder.

**THE FIX:** All of Descent QED's files must move into a single `descent/` folder. The website files stay in the root. Future games get their own top-level folders (`doom/`, `pinball/`, etc.). Each game folder is fully self-contained.

### COMPLETE FILE INVENTORY — WHAT GOES WHERE

**STAYS IN REPO ROOT (website files):**

| File/Folder | What it is |
|-------------|-----------|
| `index.html` | Homepage |
| `style.css` | Global stylesheet |
| `components.js` | Header/footer loader + mobile menu |
| `header.html` | Shared header with navigation menu (CAREFUL — this took a long time to build, do not break it) |
| `footer.html` | Shared footer |
| `images/` | Website images (hero, doom screenshots, etc.) |
| `mathematics/` | Website content pages (Riemann Hypothesis paths, etc.) — includes the downloadable harmonic_series_mathematics.py demo |
| `.htaccess` | Dreamhost Apache config |
| `.gitignore` | Git ignore rules |
| `WEBSITE_REDESIGN_FUSION_2026-06-18.md` | Website design document |

**MOVES INTO `descent/` (Descent QED game — ALL of these):**

| File/Folder | What it is |
|-------------|-----------|
| `app.py` | Game entry point |
| `combat.py` | Combat system |
| `cockpit.py` | Cockpit HUD |
| `containment.py` | Ship wall/robot collision |
| `content_parser.py` | Corridor file parser |
| `corridor_builder.py` | Corridor geometry builder |
| `game_state.py` | Game state (win condition) |
| `gamepad.py` | Gamepad/joystick support |
| `hostages.py` | Hostage figures |
| `hub_builder.py` | Hub/atrium builder |
| `level_parser.py` | Level manifest parser |
| `palette.py` | Color ledger |
| `render.py` | Core GL rendering |
| `robots.py` | Robot class |
| `understanding.py` | Understanding Mode |
| `show_colors.py` | Color utility |
| `cockpit_demo.py` | Demo script |
| `corridor_demo.py` | Demo script |
| `game_state_demo.py` | Demo script |
| `hostages_demo.py` | Demo script |
| `hub_demo.py` | Demo script |
| `level_demo.py` | Demo script |
| `render_demo.py` | Demo script |
| `robots_demo.py` | Demo script |
| `test_palette.py` | Test script |
| `test_parser.py` | Test script |
| `test_quat.py` | Test script |
| `corridors/` | Corridor data files (baker + game format) |
| `levels/` | Level manifests and baker files |
| `baked/` | Baked PNG images for Understanding Mode |
| `deu/` | Baker tool (bake_corridor.py) |
| `descent_qed/` | Old early code (keep or clean up) |
| `BIBLE/` | Bible files (Claude Fable's original code) |
| `PARENT_ESTATE/` | Development architecture docs, briefs, sessions |
| `WORKFLOW.md` | Game development workflow/memory |
| `docs/` | Game documentation (CONTENT_AUTHORING.md, etc.) |
| `*-hologram.png` | 14 portrait images for robots |

**AFTER THE MOVE, the repo looks like:**

```
peaktogether-website/               # GitHub repo root = website root
├── index.html                      # Website
├── style.css                       # Website
├── components.js                   # Website
├── header.html                     # Website (DO NOT BREAK THE MENU)
├── footer.html                     # Website
├── images/                         # Website images
├── mathematics/                    # Website content pages
├── .htaccess                       # Dreamhost config
├── .gitignore                      # Git ignore
├── WEBSITE_REDESIGN_FUSION_2026-06-18.md
│
├── descent/                        # GAME 1: Descent QED
│   ├── app.py                      # Entry point: python descent/app.py
│   ├── combat.py, cockpit.py, ...  # All engine modules
│   ├── corridors/                  # Corridor data files
│   ├── levels/                     # Level manifests + baker files
│   ├── baked/                      # Per-corridor baked images (see Mission B)
│   ├── deu/                        # Baker tool
│   ├── BIBLE/                      # Bible
│   ├── PARENT_ESTATE/              # Dev docs
│   ├── WORKFLOW.md                 # Dev workflow
│   ├── docs/                       # Game docs
│   └── *-hologram.png              # Portrait images
│
├── doom/                           # GAME 2: (future) Doom/Quake clone
│   └── ...
│
├── pinball/                        # GAME 3: (future) Pinball
│   └── ...
│
└── (more games in the future)
```

### CRITICAL CONCERNS FOR THE MOVE:

1. **All Python imports within Descent are relative to each other** (e.g. `import render`, `from content_parser import ...`). After moving into `descent/`, these imports must still work. The game is run as `python descent/app.py` or from inside the `descent/` folder as `python app.py`. Design the move so imports don't break.

2. **The baker tool (`deu/bake_corridor.py`) references paths** relative to the repo root or to its own location. These paths must be updated or the baker must be told to run from inside `descent/`.

3. **The level manifests reference corridors and baked folders with relative paths** (e.g. `../corridors/basel.txt`, `../baked/basel`). After the move, these paths change because everything is inside `descent/`.

4. **The website's download links** on the mathematics pages point to the Python demo file. These links must still work after the move (or be updated).

5. **`git mv` must be used** for the move so git preserves file history. Do NOT delete-and-recreate.

6. **The header.html menu system took a VERY long time to get working.** Do NOT touch it. The website files are not moving — only the game files move.

---

## 2. THE FOUR-LEVEL HIERARCHY (critical — understand this first)

- **GAME** = DESCENT QED. The whole product. Covers ALL of mathematics, physics, chemistry, biology — every hard problem humanity faces.
- **LEVEL** = one mathematical SUBJECT (e.g. "The Basel Problem", "The Riemann Hypothesis", "Navier-Stokes Equations", "Protein Folding"). There will be MANY levels eventually, covering completely different branches of science. Each level is independent of every other level.
- **CORRIDOR** = one APPROACH or proof within a subject. A level can hold MANY corridors (e.g. the Basel Problem has Euler's 1734 approach, the Even Zeta generalization, and eventually more). Each corridor is independent and self-contained.
- **ROBOT** = one step inside a corridor. Each robot has baked PNG images for its 4 explanation layers.

---

## 3. THE CURRENT SYSTEM AND WHY IT'S BROKEN

### How baked images currently work:

1. A **baker file** (full LaTeX with color markup) is written for each corridor.
2. The builder runs `python deu/bake_corridor.py <baker-file> --out <output-folder>` which compiles the LaTeX into transparent colored PNGs. The output files are named `robot1_mathematician.png`, `robot1_physicist.png`, `robot1_biologist.png`, `robot1_engineer.png`, `robot2_mathematician.png`, ..., `robotN_engineer.png` — just robot NUMBER and layer name.
3. The **level manifest** has ONE `baked:` line that points to a SINGLE directory. Example from `levels/basel.txt`:

```
title: The Basel Problem
baked: ../baked/basel
corridors:
  ../corridors/basel.txt
  ../corridors/basel_general.txt
```

4. The **level_parser.py** reads this ONE `baked:` path and assigns it to EVERY corridor and EVERY robot in the level via `understanding_dir`. The Understanding Mode and defeat-plaque systems then load images from `<understanding_dir>/robot<N>_<layer>.png`.

### The collision problem:

We now have TWO corridors for the Basel Problem, each with 7 robots (robots 1-7). If both are baked into the same `baked/basel/` directory, corridor 2's images OVERWRITE corridor 1's images because both have `robot1_mathematician.png`, `robot2_physicist.png`, etc. The naming is by robot NUMBER only — there is no corridor identifier in the filename or path.

### The deeper problem — it's not just about Basel:

This is NOT a Basel-specific issue. Nir's vision for DESCENT QED is that it will eventually cover DOZENS of subjects across mathematics, physics, chemistry, and biology. Each subject will have MULTIPLE corridors. Every single one of those corridors has its own robots, its own baked images, and its own set of `robotN_layer.png` files. The folder architecture must be GENERIC from the start — it must work for any subject, any number of corridors, without anyone having to think about folder naming or image collision. Every corridor's baked images must live in their own isolated space.

---

## 4. WHAT NIR WANTS (his exact words, paraphrased)

"Each subject needs its own folder, and everything in that folder needs to work independently. I need something that works for many more subjects in the future that are not connected to Basel at all. Stop tailoring things specifically to Basel. Make the folder structure generic."

"I am building corridors one at a time. Each new corridor gets tested individually with the current single-corridor system before we move on. After we have several working corridors, THEN we will ask a fresh parent to make the big engine change to enable multi-corridor play. But right now, I need each corridor to be independently bakeable and independently testable, without breaking any other corridor's baked images."

---

## 5. WHAT EXISTS ON DISK RIGHT NOW

### Levels and corridors:

| Level | Corridor | Baker file | Game file | Baked to |
|-------|----------|-----------|-----------|----------|
| Basel Problem | Euler's 1734 approach (corridor 1) | `levels/mathematics/basel_problem/basel_euler_proof.txt` | `corridors/basel.txt` | `baked/basel/` (28 PNGs, robots 1-7) |
| Basel Problem | Even Zeta generalization (corridor 2) | `levels/mathematics/basel_problem/basel_general.txt` | `corridors/basel_general.txt` | **NOT YET BAKED** — would collide with corridor 1 |
| Maxwell (toy) | Maxwell equations (placeholder) | `corridors/maxwell.txt` | `corridors/maxwell_old.txt` | `baked/maxwell/` (8 PNGs, robots 3-4 only) |

### Key engine files involved:

| File | What it does with baked images |
|------|------|
| `deu/bake_corridor.py` | Takes a baker file + `--out` folder, produces `robotN_layer.png` files |
| `level_parser.py` | Reads manifest's single `baked:` line, assigns it to ALL corridors and ALL robots as `understanding_dir` |
| `understanding.py` | Loads `<understanding_dir>/robot<N>_<layer>.png` for the road-sign display |
| `corridor_builder.py` | Loads `<understanding_dir>/robot<N>_mathematician.png` for the defeat plaque |
| `content_parser.py` | Parses corridor game files; has `understanding_dir` field on `CorridorData` and `RobotData` |
| `robots.py` | Runtime `Robot` class exposes `understanding_dir` property |

### Current manifest format (`levels/basel.txt`):
```
title: The Basel Problem
baked: ../baked/basel
corridors:
  ../corridors/basel.txt
  ../corridors/basel_general.txt
```

---

## 6. THE CONSTRAINTS

1. **Each corridor's baked images must be isolated** — baking corridor 2 must NEVER overwrite corridor 1's images. This must be true regardless of how many corridors a level has, and regardless of what subject the level covers.

2. **The solution must be GENERIC** — it must work for "The Basel Problem" with 2 corridors, for "The Riemann Hypothesis" with 10 corridors, for "Protein Folding" with 3 corridors, for any future subject. No subject-specific naming or hardcoding anywhere.

3. **Single-corridor testing must still work** — Nir tests each corridor individually before combining. The builder must be able to point the game at one specific corridor, bake it, test it, confirm it works, move on to the next.

4. **The baker's `--out` flag already exists** — `deu/bake_corridor.py` accepts `--out <folder>`. The tool itself is not broken; the problem is that level_parser only supports ONE baked path per level, and the manifest format doesn't support per-corridor baked paths.

5. **Minimal engine changes** — the game engine is feature-complete and tested. Don't redesign the whole engine. The fix should be surgical: change the manifest format and level_parser to support per-corridor baked paths, and define a clean folder convention. The Understanding Mode and plaque systems already use `robot.understanding_dir` correctly — they just need that field to point to the RIGHT per-corridor folder instead of a shared level folder.

6. **The CORRIDOR CREATOR PROMPT must stay compatible** — there is a "forever" prompt (`PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT_FOREVER.md`) that tells child Opus instances how to produce the 3 files for a new corridor. Your design must be compatible with that workflow: a child produces 3 text files, Nir gives them to the builder, the builder bakes and wires them. The child never bakes or runs code.

---

## 7. YOUR MISSION — TWO PARTS

### MISSION A: REPO REORGANIZATION (game/website separation)

Design and produce a BRIEF for the builder to move ALL Descent QED files into a `descent/` folder, leaving only website files in the repo root. The complete file inventory is in section 1b above. Specifically:

1. **Design the exact `git mv` sequence** — list every file and folder that moves, in order, so the builder can execute it without guessing. Use `git mv` to preserve history.

2. **Design the import/path fix strategy** — after moving all .py files into `descent/`, every `import render`, `from content_parser import ...`, etc. must still work. Design how the game is launched (e.g. `cd descent && python app.py` or `python -m descent.app` or another approach). The simplest solution that doesn't require rewriting every import is best.

3. **Design the relative-path updates** — the level manifests reference corridors and baked folders with relative paths. The baker references paths relative to the repo root. All these paths must be updated after the move. List every file that needs path updates.

4. **Handle the website download links** — the `mathematics/` pages have download links to the Python demo. These may need updating if the demo file moves.

5. **Do NOT touch website files** — index.html, style.css, components.js, header.html, footer.html, images/ must NOT be modified. The header menu system took a long time to build; it must not be broken.

### MISSION B: PER-CORRIDOR BAKED IMAGE ISOLATION (within descent/)

Design the per-corridor baked image architecture WITHIN the new `descent/` folder. Specifically:

1. **Design a folder convention** for baked images that is generic, per-corridor, and collision-free. Think about: where do baked images for corridor 1 of the Basel Problem go? Where do baked images for corridor 3 of the Riemann Hypothesis go? Where do baked images for corridor 1 of Protein Folding go? The naming should be obvious, self-documenting, and never collide.

2. **Design the manifest format change** — the manifest currently has one `baked:` line for the whole level. It needs to support per-corridor baked paths. Design the new format. Keep it backward-compatible if possible (old manifests with one `baked:` line should still work for single-corridor levels).

3. **Design the level_parser.py changes** — what changes to `_read_manifest` and `load_level` are needed so that each corridor gets its own `understanding_dir` instead of sharing one?

4. **Design the baker workflow change** — when the builder bakes a new corridor, what `--out` path does it use? How does this connect to the manifest?

5. **Write the builder brief** — a tightly-scoped set of edits (numbered, one per edit) covering BOTH missions. The builder will execute these in order. Cover: the git mv sequence, import/path fixes, level_parser.py changes, manifest format changes, and the folder convention. Do NOT touch understanding.py or corridor_builder.py or robots.py unless absolutely necessary — they already use `robot.understanding_dir` correctly.

6. **Update guidance for the CORRIDOR CREATOR PROMPT** — what does the child need to know about the new folder structure and manifest format? (Nir will update the FOREVER prompt accordingly.)

---

## 8. WHAT TO PRODUCE

One document containing:
1. The repo reorganization plan: every file/folder that moves, the git mv commands, and the post-move structure
2. The import/path fix strategy for the Python modules
3. The per-corridor baked image folder convention (with examples for Basel, Riemann, and a hypothetical third subject)
4. The new manifest format (with example)
5. The numbered edits for the builder (git mv sequence + level_parser.py + manifest format + path updates)
6. The updated bake command for the builder (using new paths inside descent/)
7. A note on what the CORRIDOR CREATOR PROMPT needs to change

---

## 9. HOW TO BEGIN

Your first message to Nir should:
1. Confirm you understand BOTH missions (repo reorganization + per-corridor baked image isolation).
2. Ask Nir to paste `level_parser.py` so you can see exactly how the manifest is parsed today.
3. Ask any clarifying questions before writing the design.

Do NOT start writing until you have read the real files.

---

**END OF PROMPT — Nir will paste the requested files.**
