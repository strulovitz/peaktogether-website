# HOMEWORLD: A GOOD BASIS (Game 4) — Project WORKFLOW & MEMORY for DeepSeek V4 Pro (OpenCode)

> 🛑🛑🛑 **RULE #0 — HOMEWORLD IS FLAT. NEVER `-m`. FLATTEN EVERY FABLE DELIVERY. SAY THIS AT THE START OF EVERY SESSION.** 🛑🛑🛑
> **Nir NEVER agreed to `-m` and hates it. Nir wants Homeworld exactly like our previous games (Quake/Descent): FLAT.**
> 1. **FLAT STRUCTURE — no subfolders, no packages, ever.** ALL game `.py` files live **directly in `homeworld/`** as plain siblings
>    (like Quake: app.py, camera.py, sim.py, forge.py, helm.py all next to each other). There are **NO `forge/`, `helm/`, `fleet/`
>    subfolders** and **no `__init__.py`**. (BIBLE/ and algebra/ are docs/text folders — those stay.)
> 2. **Fable builds in subfolders/packages. I MUST FLATTEN every delivery on drop-in:** move his files into `homeworld/` root,
>    convert package imports to flat absolute imports (`from camera import Camera`), rename collisions (a package's `__init__.py`
>    holding a class → `<name>.py`; a module `app.py` inside a package → `<pkgname>.py`; each `demo.py` → `<pkg>_demo.py`),
>    and delete the empty folders. Then TELL NIR at the very start that I flattened it.
> 3. **NEVER `python -m`, NEVER relative imports (`from .`), NEVER a sys.path bootstrap/hack.** Flat + plain absolute imports
>    is the ONLY allowed way. Everything runs with plain `python <file>.py` from `homeworld/`.
> 3b. **DATA folders are FINE** (exactly like Quake's `levels/`/`hud/`): JSON/text/image data may live in a folder (e.g. `content/`
>    with ships.json + meshes/ + narrator/ + book/, plus `algebra/` and `BIBLE/`). The FLAT rule is about **Python CODE only** —
>    no code packages, no `__init__.py`, no `-m`. A flat loader module (e.g. `content_db.py`) reads the data folder by path.
> 4. **The 2-line command I give Nir EVERY time (full paths, consistent):**
>    `cd C:\Users\nir_s\peaktogether-website\homeworld`
>    then `python app.py` (the game) — or `python fleet_demo.py` / `python helm_demo.py` / `python forge_demo.py` for a module test.
> - I failed Nir repeatedly on July 5, 2026 (passed a raw `-m` command; then added a sys.path bootstrap hack instead of truly
>   flattening). The bootstrap is GONE; the whole game is now flat. Never reintroduce folders, packages, `-m`, or hacks.
>
> ⭐ **ON RESTART, READ THIS FIRST.** Then read `homeworld/COMMENTARIES.md` (the repo memory, Fable's format). Then read the latest `homeworld/BIBLE/FABLE DELIVERABLE N ...md` if a package is mid-flight. Then ask Nir what's next.
>
> This is my (DeepSeek's) own memory for the Homeworld project. NOTE: `AGENTS.md` still routes startup to **Quake** — until Nir says otherwise, when he restarts he should tell me "read homeworld/WORKFLOW.md" (or ask me to update AGENTS.md to point here).

---

## 0. WHAT HOMEWORLD IS (in one breath)
**Game 4** on the Peak Together platform. A free, open-source, **two-player-one-screen** remake of **Homeworld (1999)** — a 3D space RTS — in which **commanding your fleet IS doing linear algebra**. Every ship is a column vector, the fleet is a matrix, and the 16-mission journey home to Hiigara is "the search for a good basis" (Strang §8.3), ending in the mission "The Victory of Orthogonality" (Strang §7.4). It teaches linear algebra from **Gilbert Strang's** books. Built in **Python** (moderngl + pyglet + numpy + Pillow), Windows-first.

## 1. WHO'S WHO (the working model — different from Quake!)
| Role | Who | What |
|------|-----|------|
| Owner | **Nir** (strulovitz) | Decides everything; copy-pastes text between chats; **knows NO code and NO math**; runs the game and describes what he sees; loves emojis 😊 |
| Architect / Parent | **Claude Fable** (Opus, in OpenRouter) | Designs everything AND writes the actual code, package by package. Nir pastes Fable's answers to me. |
| Librarian / Runner | **DeepSeek V4 Pro (me, OpenCode)** | Save Fable's answers VERBATIM to the BIBLE; drop Fable's code files into the repo EXACTLY as given; update COMMENTARIES.md; commit with Fable's EXACT message; push. I do **mechanical** work only — I never design or redesign. |

**⚠️ KEY DIFFERENCE FROM QUAKE:** Here Fable (the Parent) writes the code himself and hands it over as complete files. My job is NOT to write game code — it's to save verbatim, drop files in exactly, verify (syntax check only), commit, push. (See the DeepSeek Standing Orders in `THE HOMEWORLD BOOK OF PROMPTS BY FABLE.md` Part 3.)

## 2. THE BOOK SOURCE (Strang) — `homeworld/algebra/`
Two Gilbert Strang books, each getting OCR'd page-by-page (Nir pastes text+LaTeX blocks from Claude Sonnet; I file them):
- `homeworld/algebra/everyone/` — **Linear Algebra for Everyone**. Preface pages **iii–xii** DONE (10 files) + combined `preface.txt`. Subfolders: `preface/`, `chapter 1/`.
- `homeworld/algebra/introduction/` — **Introduction to Linear Algebra** (6th ed.). Preface pages **iii–x** DONE (8 files) + combined `preface.txt`. Subfolders: `preface/`, `chapter 1/`.
- Files named by printed page number: `page_iii.txt`, `page_iv.txt`, ... Figures captured as detailed `% FIGURE DESCRIPTION` comment blocks (I can't see images).
- **NEXT for the books:** Chapter 1 pages, when Nir starts pasting them → `chapter 1/` folders. (Also: build combined chapter files like we did for preface, when a chapter is complete.)

## 3. THE BIBLE (`homeworld/BIBLE/`) — the scriptures, all VERBATIM
Everything Fable produces is saved here word-for-word. Current contents:
- `brainstorming 1 with Fable.md` — HomeWorld × Linear Algebra for Everyone
- `brainstorming 2 with Fable.md` — HomeWorld × Introduction to Linear Algebra
- `HOMEWORLD OLD TESTAMENT BY FABLE.md` — **the Bible** (vision + every mechanic to implementation depth + 16-mission campaign + engineering doctrine). Precedence: Bible wins over all.
- `HOMEWORLD NEW TESTAMENT BY FABLE.md` — module design of **forge / fleet / helm** (the 3 hardest modules). Includes INTERFACES v1.0, the Referee, acceptance demos, the 12-line fleet self-test.
- `HOMEWORLD APOCRYPHA BY FABLE.md` — module design of **content / campaign / bridge / intel / guidestone**. Two binding amendments: **A = NO AUDIO EVER**; **B = Guidestone is a garnish (~50 lines)**. First-Five-Minutes Doctrine.
- `THE HOMEWORLD BOOK OF PROMPTS BY FABLE.md` — birth-prompt templates (Parent/Child/DeepSeek standing orders/succession/commentaries format/bug report). "I highly doubt we'll use this" (Nir) but saved for the record.
- `FABLE DELIVERABLE 1 - forge walking skeleton (NT steps 1-2).md`
- `FABLE DELIVERABLE 2 - bloom (NT step 3).md`
- `FABLE DELIVERABLE 3 - text + remaining primitives (NT step 4).md`

## 4. THE GAME CODE (`homeworld/`) — what's built
Game root = `homeworld/`. **FLAT like Quake — all `.py` files live directly in `homeworld/`, no subfolders. Run with plain `python <file>.py`, NEVER `-m`:**
- The game: `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python app.py` (or double-click `run.bat`).
- Module self-tests (optional): `python fleet_demo.py` (headless 12/12) · `python forge_demo.py` (window) · `python helm_demo.py` (window) — all from the same `homeworld/` folder.

**Structure convention (LOCKED, Quake-style):** ALL modules are flat siblings in `homeworld/` (app.py, forge.py, helm.py, sim.py, referee.py, camera.py, vobjects.py, …). Every module uses **flat absolute imports** (`from camera import Camera`, `from sim import FleetSim`). **NO subfolders, NO packages, NO `__init__.py`, NO relative imports (`from .`), NO `-m`, NO sys.path hacks.** Fable delivers in subfolders → **I flatten every delivery on drop-in** (see RULE #0).

**Requirements already installed on Nir's machine** (verified): numpy 2.4.6, moderngl 5.12.0, pyglet 2.1.14, Pillow 12.2.0. **Do NOT install anything without asking.**

### `forge/` — the render engine ("a real-time Manim") — FEATURE-COMPLETE ✅
Built across NT build steps 1–4 (Fable's deliverables 1–3):
- `forge/camera.py` — Camera: ORBIT mode + look_at/perspective (numpy). (FOLLOW/POV stubs to come.)
- `forge/shaders.py` — GLSL: line-ribbon shader + bloom pipeline (fullscreen tri, blit, Gaussian blur, composite+tone-map) + textured-quad shader (text/images).
- `forge/batches.py` — CPU segment → camera-facing glowing ribbons (vectorized numpy); per-segment color for Trail.
- `forge/bloom.py` — 3-FBO classic bloom (RGBA16F scene → downsample → separable Gaussian → composite + soft exposure tone map).
- `forge/text.py` — GlyphAtlas (Pillow → Consolas fallback) + TextRenderer (3D billboard Labels + screen overlay) + PanelRenderer (grayscale ImagePanels).
- `forge/vobjects.py` — the FULL frozen primitive vocabulary: Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel.
- `forge/app.py` — the Forge class: window, GL context, 10 Hz fixed-timestep accumulator loop, scene FBO → panels → labels → bloom → screen overlay (fps corner + F1 debug overlay), F12 screenshot, ESC quit, resize-safe.
- `forge/demo.py` — the full acceptance demo (grid, origin axes, sweeping white arrow + comet trail, floating text, flattening determinant box counting to `vol 0.00`, live SVD image panel rank 1→32, magenta ellipsoid, F1 overlay).
- `forge/__init__.py` — exports.
- `requirements.txt`, `run.bat`, `settings.json` (v0.3.0: bloom_strength 0.85, exposure 2.5, seed 1234).

## 5. CURRENT SITUATION (July 5, 2026, end of day — ~31% DeepSeek context)

### The game state (verified — every module below has its code dropped in, compiles, and its imports resolve):
| Module | Fable Deliverable | Status | Notes |
|--------|-------------------|--------|-------|
| **forge** | #1, #2, #3 (NT 1-4) | ✅ Nir confirmed | Camera, GLSL line-ribbon + bloom + textured-quad shaders, batches, Bloom, GlyphAtlas+TextRenderer+PanelRenderer, FULL vobjects vocabulary (Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel, SolidMesh — A1), **SolidRenderer (A1)**. Render pipeline: SOLID pass (depth write, no blend) → GLOW pass (depth test, no write, additive) → bloom → crisp overlay. F12 screenshot, F1 debug. |
| **helm** | #4 (NT step 5) | ✅ Nir confirmed | actions.py (frozen list v1), keyboard_map.py (Pilot), mouse_map.py (Navigator), joystick_map.py + gamepad_map.py (stubs w/ full impl), helm.py (Helm orchestrator), helm_demo.py. Every key tested. |
| **fleet** | #5 (NT 6-7) | ✅ Nir confirmed | referee.py (12 canonical NumPy fns — the math conscience), orders.py (12 types), events.py, ships.py (Ship + BUILTIN_CLASSES), snapshot.py (FleetSnapshot), sim.py (FleetSim — deterministic 9-phase 10 Hz pulse), fleet_demo.py. FLEET SELF-TEST PASSED (12/12). |
| **app.py wiring** | #6 (NT step 9) | ✅ Wiring verified | Root game shell: wires forge+helm+fleet. Shakedown: mothership + 3 fighters (squad 1) + corvette+collector+frigate (squad 2). Keyboard combination-order console (ghost legs/arrow, ENTER commit, X diagonal/staged, Q/E squad switch, TAB select, C recenter, camera, P pause). |
| **content** | #7 (Apocrypha 1) | ✅ Content check verified | content_db.py (ContentDB: loads + LOUDLY validates), content_demo.py (CONTENT CHECK PASSED), content/ DATA folder: ships.json, 5 mesh JSONs, narrator/core.json (7 lines), book/ch1_excerpts.json (2 PLACEHOLDERS awaiting Nir's Strang paste). |
| **SOLID SHIPS** | #8 (A1) | ✅ Built, NOT SEEN BY NIR | **Amendment A1**: ships now solid opaque lit meshes (Blinn-Phong, 264–396 tris/class) from shipwright.py. shaders.py MESH shader, solid.py SolidMesh+SolidRenderer, bloom.py depth buffer, forge.py new pipeline. **Nir has NOT yet seen/played this — the context-window restart is happening now so he can run it with fresh context.** |
| **BIBLE** | — | ✅ A1 in scriptures | Amendment A1 banner at top of OT+NT+Apocrypha. 8 deliverable files saved verbatim. |
| **Structure** | — | ✅ FLATTENED | All 26+ modules are flat siblings in homeworld/. No packages, no __init__.py, no -m, no hacks. content/ is a DATA folder (like Quake's levels/). RULE #0 permanent. run.bat deleted (Nir's choice). |

### Runs
| What | Command | Status |
|------|---------|--------|
| The full game | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python app.py` | ⏳ **AWAITING Nir's art-director play-test** (solid ships!) |
| Fleet self-test | `python fleet_demo.py` (from homeworld/) | ✅ 12/12 PASS |
| Content check | `python content_demo.py` (from homeworld/) | ✅ CONTENT CHECK PASSED |
| Helm demo | `python helm_demo.py` (from homeworld/) | ✅ Nir confirmed |
| Forge demo | `python forge_demo.py` (from homeworld/) | ✅ Nir confirmed (but shows old wireframe test — low priority) |

### Data folders (not code — fine per RULE #0 clause 3b)
- `content/` — ships.json, meshes/ (5 .json), narrator/ (core.json, 7 lines), book/ (ch1_excerpts.json, 2 PLACEHOLDERS), missions/ (empty)
- `algebra/` — Strang book OCR: everyone/ + introduction/ (prefaces done, Chapter 1 empty awaiting pages)
- `BIBLE/` — verbatim scriptures (OT+NT+Apocrypha+Book of Prompts) + 2 brainstorms + 8 Fable deliverable files
- `notes/` — amendment_a1_art_direction.md

### What's NOT yet built (next after Nir's A1 art review)
1. **Bridge** (NT/Apocrypha) — forge 2D overlay + widget kit + FLEET ZONE console. The Navigator picks up the mouse. 2nd player joins.
2. **Campaign + Mission 1** (Apocrypha) — minute-by-minute mission script. First real playable mission.
3. **Missions 2–16** — the full 16-mission journey home to Hiigara.
4. **Content book excerpts** — Nir pastes Strang text into the PLACEHOLDER slots in content/book/ch1_excerpts.json.
5. **Joystick + Xbox mappers** — stubs exist with complete implementation instructions.
6. **FOLLOW/POV camera modes** — deferred.
- ⏳ **AWAITING Nir's play-test** of `run.bat`: compose W (blue leg) + D (red leg) → ghost arrow → ENTER → fighters fly the diagonal; then X + compose + ENTER → they fly staged (two sides of the parallelogram). Fable also wants Nir's gamer feel on compose-then-commit (feel-knobs COEFF_RATE=2.0, COEFF_SNAP=0.5 are one-line changes).
- ⏳ **NEXT (after Nir plays):** content loader + real ship meshes → bridge (Navigator's mouse console, 2nd player) → campaign + Mission 1.
- The last thing before Nir restarts OpenCode: WORKFLOW.md + COMMENTARIES written; everything pushed.

## 6. WHAT STILL NEEDS TO BE DONE (the road ahead)
Per the New Testament build order + Fable's stated plan:
1. ⏳ **Nir confirms helm demo** (`python helm\demo.py`, report to Fable).
2. ✅ **helm** (NT Part 2) — DONE. (joystick/Xbox mappers deferred — Fable's Book of Prompts + the stub docstrings flag these as my one sanctioned future coding task, ONLY when Nir explicitly invokes it.)
3. ✅ **fleet** (NT Part 3) — DONE. Ships as matrix columns, the 10 Hz pulse, orders, events, and **referee.py** (the canonical NumPy verdict functions). `python fleet\demo.py` prints **FLEET SELF-TEST PASSED (12/12)** (DeepSeek-verified; Nir confirming).
4. **app.py wiring** (NT Part 4) — bind forge + helm + fleet → three ships flying combination orders live on screen (Bible Mission 1 becomes buildable).
5. Then the APOCRYPHA modules: **content** loader, **campaign** runner + Mission 1, **bridge** console + Big Picture, **intel** narrator. Then Missions 2–16.
6. Ongoing in parallel: keep filing Strang book pages (Chapter 1 next) into `homeworld/algebra/`.

## 7. STANDING RULES / LESSONS (how I work on Homeworld)
- **SAVE VERBATIM.** Fable's answers → BIBLE, word-for-word, LaTeX untouched. Strip only chat UI chrome (timestamps, "Reasoning", model labels) and Nir's own instructions.
- **OWNER AMENDMENTS GO INTO THE SCRIPTURES.** When Nir makes a binding decision that changes/overrides an earlier design (e.g. Amendment A1 = solid ships, not wireframe), record it as an **add-only, clearly-marked "⚖️ OWNER AMENDMENTS (READ FIRST)" banner at the TOP of the relevant scripture** — Old Testament + New Testament + Apocrypha (whichever carry the superseded design) — NOT only in notes/ or COMMENTARIES. Fable's original text stays verbatim below; the banner says the amendment overrides anything below that conflicts. The OT is the top precedence ("Bible wins over all"), so the correction MUST be visible there. Append future amendments to the same banner. (Nir's instruction, July 5, 2026 — I had put A1 only in notes/COMMENTARIES and he corrected me.)
- **DROP CODE IN EXACTLY.** Fable's code files go to the paths he names, byte-for-byte. He writes complete files (never diffs). Full path stated before each fence.
- **COMMIT WITH FABLE'S EXACT MESSAGE** (e.g. "NT step 4: text (glyph atlas) + remaining primitives — forge feature-complete"). Update COMMENTARIES.md every change. Push. Report done.
- **I DON'T DESIGN.** No redesigning, no "improving." Mechanical fixes only, and only when exact old/new text is specified. Anything needing judgment → back to Fable (via Nir).
- **NEVER install/download without asking.** Requirements are already present.
- **Syntax-check only** (`python -m py_compile`) — safe, no deps needed. Do NOT run the GUI demo myself; Nir is the visual judge. (Note: `py_compile` is an internal check I run; the RULE against `-m` is about the RUN COMMANDS I hand to Nir — those are always plain `python <file>.py`.)
- **Give Nir the FULL run command every time:** `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python app.py` (the game), or `python fleet_demo.py` / `python forge_demo.py` / `python helm_demo.py` for a module test (PowerShell). NEVER `-m`, never a half `cd`, never "type cmd in the address bar." He has Python — no install lectures.
- **CONVERT every Fable file that uses `from .` / `-m` to flat absolute imports on drop-in**, and tell Nir at the start that I did so.
- **Emojis abundantly**, warm, concise. Never call him "boss" — just **Nir**.
- **Game code lives under `homeworld/`** (the game root in the monorepo). `__pycache__`, `*.pyc`, `build/` are gitignored (fine).
- Give Nir **view (blob)** GitHub links when he asks, plain text, no fancy formatting that 404s.

## 8. CONVENTIONS
- Repo: `github.com/strulovitz/peaktogether-website`, branch **master**. Local: `C:\Users\nir_s\peaktogether-website`.
- Each game = its own top-level folder. Homeworld = `homeworld/`.
- BIBLE = verbatim scriptures. COMMENTARIES.md = the living repo memory (Fable's Part-5 format). This WORKFLOW.md = my DeepSeek memory.
- Commit + push after every meaningful change.

## 9. SESSION LOG
## 9. SESSION LOG

### TODAY (July 5, 2026) — THE ENTIRE DAY — from helm through solid ships (8 Fable deliverables!)
This was the biggest single-day session in Homeworld history. DeepSeek's context is now ~31% full. Here's every beat, in order, for the restart:

#### FABLE DELIVERABLE 4 — helm complete (NT step 5)
- Nir pasted Fable's helm answer. I saved it verbatim to `BIBLE/FABLE DELIVERABLE 4 - helm complete (NT step 5).md`.
- Created the `helm/` package: actions.py, keyboard_map.py, mouse_map.py, joystick_map.py (stub), gamepad_map.py (stub), __init__.py, demo.py. Updated `settings.json` → v0.4.0.
- Fable passed `python -m helm.demo` to Nir. **Nir HATED `-m` and was FURIOUS.** This started the whole flattening saga.
- I tried several bad things: inconsistent cd/path commands, a sys.path bootstrap hack, a run.bat Nir hated. Nir kept correcting me.
- **Nir confirmed helm works** (every key tested). Pushed. See RULE #0 below for what I learned.

**CRITICAL LESSON — the `-m` saga:** Fable built Homeworld as PACKAGES (forge/, helm/, fleet/) with relative imports (`from .`), which force `-m` to run. Nir never agreed to `-m`; every previous Peak Together game (Quake, Descent) was BORN FLAT and ran `python app.py`. I kept trying workarounds (sys.path bootstrap) instead of properly flattening. Nir called me out repeatedly until I finally understood: the whole game must be FLAT — all .py files as siblings in homeworld/ — like Quake. This led to the big flatten operation.

#### FABLE DELIVERABLE 5 — fleet core (NT steps 6-7)
- Saved verbatim to `BIBLE/FABLE DELIVERABLE 5 - fleet core (NT steps 6-7).md`.
- Created `fleet/` package: referee.py, orders.py, events.py, ships.py, snapshot.py, sim.py, __init__.py, demo.py. Dropped in Quake-style (flat absolute imports).
- `python fleet_demo.py` → FLEET SELF-TEST PASSED (12/12). Pushed.

#### FABLE DELIVERABLE 6 — app.py wiring (NT step 9) — FIRST PLAYABLE BUILD
- Nir confirmed 12/12 to Fable. Fable sent the wiring.
- Saved verbatim → `BIBLE/FABLE DELIVERABLE 6 - app.py wiring (NT step 9).md`.
- Created root `app.py` (game shell: forge+helm+fleet), updated `run.bat` (`python app.py` — Fable got it right!), `settings.json` → v0.5.0.
- **RULE #0 failure (again):** I added a sys.path bootstrap to app.py instead of truly flattening. Nir caught this and was furious.

#### THE BIG FLATTENING (Nir's order)
- **Nir told me to make it like Quake. I FINALLY did it right:** moved ALL 23 module files out of forge/, helm/, fleet/ into homeworld/ root as flat siblings.
- Renamed collisions: forge/app.py→forge.py, helm/__init__.py→helm.py, forge/demo→forge_demo.py, helm/demo→helm_demo.py, fleet/demo→fleet_demo.py.
- Deleted forge/__init__.py, fleet/__init__.py, and the empty subfolders.
- Removed the sys.path bootstrap from app.py; all imports now plain flat absolute.
- Verified: all 23 files compile; fleet_demo 12/12; app imports resolve; zero `-m`/`from .`/packages anywhere.
- **Wrote RULE #0** — the permanent iron rule against `-m`, packages, and sys.path hacks. Also mandates flattening every future Fable delivery on drop-in.
- Added RULE #0 clause 3b: DATA folders (content/, algebra/, BIBLE/) are fine — only Python CODE must be flat.
- Nir told me to delete run.bat (he runs `python app.py` directly). Deleted it.

#### FABLE DELIVERABLE 7 — content data layer (Apocrypha step 1)
- Saved verbatim → `BIBLE/FABLE DELIVERABLE 7 - content data layer (Apocrypha step 1).md`.
- Flattened per RULE #0: content/db.py→content_db.py, content/demo.py→content_demo.py (`from content_db import`), dropped content/__init__.py. Kept content/ as a pure DATA folder.
- Created the content/ data tree: ships.json + 5 mesh JSONs + narrator/core.json + book/ch1_excerpts.json (2 PLACEHOLDER excerpts awaiting Nir's Strang paste).
- app.py now spawns 7 ships in 2 squads (Q/E switches commands), meshes from content/, fleet rank 5.
- Verified: `python content_demo.py` → CONTENT CHECK PASSED. Pushed.
- **Nir never got to run this** (we moved straight to Amendment A1 after he saw the wireframe ships).

#### FABLE DELIVERABLE 8 — AMENDMENT A1: solid shaded ships
- Nir judged the glowing-wireframe ships as ugly — they FAIL Bible Law 1 ("gaming first — would a gamer choose to play this?"). Fable agreed and amended the art direction.
- Saved verbatim → `BIBLE/FABLE DELIVERABLE 8 - solid shaded ships (Amendment A1).md`.
- Ships are now SOLID, OPAQUE, LIT triangle meshes: per-pixel Blinn-Phong (key+fill+rim+specular), paneled hulls with per-face color variation, emissive engine nozzles/windows feeding bloom. The math layer stays glowing holographic over them.
- Flattened per RULE #0: forge/shaders.py→shaders.py (updated with MESH shader), forge/solid.py→solid.py (new), forge/bloom.py→bloom.py (updated with depth buffer), forge/app.py→forge.py (updated render pipeline), content/shipwright.py→shipwright.py (new procedural ship builder). Dropped forge/__init__.py.
- Render pipeline: SOLID pass (depth write) → GLOW pass (depth test, no write) → bloom → overlay.
- Art-direction note saved at `notes/amendment_a1_art_direction.md`.
- Verified: all files compile; ALL 5 SHIPS build headlessly (264–396 tris each); shipwright generates real geometry; app imports resolve. Pushed.
- **Nir has NOT yet play-tested this** (context-window restart happens now). The solid ships await his eyes as art director.

#### Amendment A1 recorded into the SCRIPTURES (Nir's catch)
- Nir asked why A1 wasn't put into the Old Testament. I had put it only in notes/COMMENTARIES. He was right: the Bible is the top-precedence source of truth.
- Added an **add-only "⚖️ OWNER AMENDMENTS (READ FIRST)" banner** to the top of the Old Testament + New Testament + Apocrypha (all three). Each banner records A1 (solid ships) and says it overrides anything below that conflicts. Fable's original words preserved verbatim below.
- Made it a standing rule: all future owner amendments go into the scripture banners. Pushed.

### Earlier sessions (condensed backup — see previous session log for detail)
2. Filed **Linear Algebra for Everyone** preface pages iii–xii + combined `preface.txt`.
3. Filed **Introduction to Linear Algebra** preface pages iii–x + combined `preface.txt`.
4. Created `homeworld/BIBLE/`; saved (verbatim) the 2 brainstorms + Old Testament + New Testament + Apocrypha + Book of Prompts.
5. Applied Fable's forge deliverables 1–3 (NT steps 1–4): walking skeleton → bloom → text + remaining primitives. **forge feature-complete.** Each saved verbatim to BIBLE + committed with Fable's exact message + pushed.
6. Verified Nir has all requirements installed (numpy/moderngl/pyglet/Pillow).
7. Wrote this WORKFLOW.md + expanded COMMENTARIES.md. Pushed. (Nir about to restart OpenCode at ~29% context.)

### July 5, 2026 — forge confirmed by Nir; helm built (NT step 5)
1. Nir ran the forge demo and confirmed (a) text readable (Consolas) + (b) determinant box flat at `vol 0.00`. **forge officially DONE.**
2. Applied Fable's **deliverable 4 = helm complete** (NT step 5). Saved verbatim to `BIBLE/FABLE DELIVERABLE 4 - helm complete (NT step 5).md`.
3. Created the `homeworld/helm/` package — 7 files exactly as Fable gave them: `actions.py`, `keyboard_map.py`, `mouse_map.py`, `joystick_map.py` (stub), `gamepad_map.py` (stub), `__init__.py`, `demo.py`. Updated `settings.json` → v0.4.0 (adds `input` section).
4. Syntax-checked all 7 .py files (py_compile OK) + validated settings.json.
5. Updated COMMENTARIES.md (state, file index, interfaces, demo status, change log) + this WORKFLOW.md.
6. Committed with Fable's exact message: `NT step 5: helm complete (actions, keyboard+mouse mappers, joystick/gamepad stubs, demo)`. Pushed.
7. ⏳ Nir to run `python helm\demo.py` (console visible) and report the six input behaviors to Fable.

### July 5, 2026 — CONVERTED HOMEWORLD TO QUAKE-STYLE (no more `-m`) — Nir's order
Nir was (rightly) furious: I passed Fable's raw `python -m helm.demo` straight to him. He NEVER agreed to `-m` and hates it; every previous game (Quake) runs with plain `python app.py`. Root cause: Fable built Homeworld as packages with **relative imports** (`from .`), which force `-m`; Quake uses **flat absolute imports** (`from camera import`), which run with `python app.py`.
1. **Converted ALL forge + helm files** from relative imports (`from .x import`) to flat absolute imports (`from x import`). Files: forge/{app,bloom,text,demo,__init__}.py + helm/{keyboard_map,mouse_map,__init__,demo}.py. (helm/demo.py `from . import Helm` → `from __init__ import Helm`.)
2. **Fixed `run.bat`**: `python -m forge.demo` → `python forge\demo.py`.
3. **Fixed every `-m` mention in docstrings/comments** of Fable's files (forge/demo, helm/demo, helm/joystick_map, helm/gamepad_map) → `python forge/demo.py` / `python helm/demo.py`.
4. **Deleted** the `helm_demo.bat` I'd created unprompted (it had `-m`).
5. **Verified**: both demos import-resolve as plain scripts (`python forge\demo.py`, `python helm\demo.py`); all 16 files py_compile OK; zero `from .` and zero `python -m` remain in any code/bat.
6. **Added RULE #0** at the top of this file + updated §4/§7 standing rules: never `-m`, always flat absolute imports, always the full `cd` command, always convert Fable's future files on drop-in and tell Nir at the start.
7. Updated COMMENTARIES.md + the BIBLE deliverable note accordingly. Committed + pushed.

### July 5, 2026 — fleet built + 12/12 (NT steps 6-7)
1. Applied Fable's **deliverable 5 = fleet core**. Saved verbatim to `BIBLE/FABLE DELIVERABLE 5 - fleet core (NT steps 6-7).md`.
2. Created the `homeworld/fleet/` package — 8 files: referee.py, orders.py, events.py, ships.py, snapshot.py, sim.py, __init__.py, demo.py.
3. **Dropped in Quake-style per RULE #0** — converted the 3 files with relative imports (sim.py, __init__.py, demo.py) to flat absolute imports (`import referee`, `from sim import FleetSim`, etc.). referee/orders/events/ships/snapshot had no relative imports.
4. **Verified**: all 8 files py_compile OK; zero `from .` and zero `-m`; ran `python fleet\demo.py` → **FLEET SELF-TEST PASSED (12/12)**.
5. Updated COMMENTARIES.md (state, file index, interfaces, demo status, change log) + this WORKFLOW.md. Committed with Fable's exact message + pushed.
6. ⏳ Nir to run `python fleet\demo.py` and report "12/12" to Fable → then Fable wires app.py (forge+helm+fleet, Mission 1 buildable).

### July 5, 2026 — app.py wiring built — FIRST PLAYABLE BUILD (NT step 9)
1. Nir reported fleet **12/12** to Fable. Applied Fable's **deliverable 6 = app.py wiring**. Saved verbatim to `BIBLE/FABLE DELIVERABLE 6 - app.py wiring (NT step 9).md`.
2. Created root **`app.py`** (game shell wiring forge+helm+fleet + shakedown scenario), updated **`run.bat`** (`python app.py`), **`settings.json`** → v0.5.0.
3. **RULE #0 conversion:** Fable's app.py imports the packages via `from forge import ...` / `from helm import ...` / `from fleet import ...`. Because our packages use flat absolute imports (no `-m`), I added a small **sys.path bootstrap** at the top of app.py (inserts forge/, helm/, fleet/ on the path) so `python app.py` resolves everything AND `from app import Forge` inside forge finds forge/app.py, not the root app.py. This is the ONLY change from Fable's verbatim file. run.bat already used `python app.py` (Fable got the root right — no `-m`).
4. **Verified:** app.py py_compile OK; replicated the bootstrap + all wiring imports (`Forge, Grid, Arrow, DashedLine, Label, Trail, WireMesh, Helm, FleetSim, MoveCombination`) resolve cleanly (no window). Full sweep: zero `-m`, zero `from .` in the whole tree.
5. Could NOT run the actual game (opens a window → Nir is the visual judge). Any forge-API mismatch inside App.__init__ would surface as a crash on Nir's run (normal loop) — not my job to change (that's Fable's design).
6. Updated COMMENTARIES.md + this WORKFLOW.md. Committed with Fable's exact message + pushed.
7. ⏳ Nir to double-click run.bat, fly a combination order, and report back (+ gamer feel on compose-then-commit).

### July 5, 2026 — FLATTENED to Quake structure (Nir's order; ends the -m/hack pain for good)
Nir was right and furious: I kept hacking around the fact that Fable builds in subfolders (forge/, helm/, fleet/) while our previous games (Quake/Descent) were **born flat**. A root app.py reaching into subfolders is the only thing that forces `-m` or a sys.path hack. Fix = make Homeworld look like Quake: FLAT.
1. **Moved all 23 modules** out of forge/, helm/, fleet/ into `homeworld/` root as plain siblings (via `git mv`, preserving history). Renamed collisions: `forge/app.py`→`forge.py` (the Forge class), `helm/__init__.py`→`helm.py` (the Helm class), `forge/demo.py`→`forge_demo.py`, `helm/demo.py`→`helm_demo.py`, `fleet/demo.py`→`fleet_demo.py`. Deleted `forge/__init__.py` + `fleet/__init__.py` (re-export-only). Deleted the subfolders.
2. **Removed the sys.path bootstrap from app.py** and fixed its imports to flat siblings: `from forge import Forge`, `from vobjects import Grid, Arrow, DashedLine, Label, Trail, WireMesh`, `from helm import Helm`, `from sim import FleetSim`, `from orders import MoveCombination`.
3. Fixed demo imports: forge_demo `from forge import Forge`; helm_demo `from helm import Helm`; docstrings updated to the new `python <file>.py` names.
4. **Verified:** all 23 flat files py_compile OK; app.py wiring imports resolve (no window, no bootstrap); `python fleet_demo.py` → **FLEET SELF-TEST PASSED (12/12)**. Zero `-m`, zero `from .`, zero `import fleet` anywhere. (One empty `fleet/` folder is locked on disk by a stray handle — harmless, untracked by git, won't be pushed; clears on reboot.)
5. **Updated RULE #0** to mandate the FLAT structure + flattening every future Fable delivery on drop-in. Updated §4 + docs. Committed + pushed.
6. ⏳ Nir to double-click run.bat (or `python app.py`) and play-test the shakedown scenario.

### July 5, 2026 — content data layer (Apocrypha step 1) — flattened + verified
Applied Fable's **deliverable 7 = content data layer**. Saved verbatim to `BIBLE/FABLE DELIVERABLE 7 - content data layer (Apocrypha step 1).md`.
1. **Flattened per RULE #0:** Fable delivered a `content/` package (content/__init__.py + db.py + demo.py, relative import, `python -m content.demo`). I moved the CODE flat: `content_db.py` (from db.py, no changes), `content_demo.py` (from demo.py; `from .db import` → `from content_db import`; docstring/run → `python content_demo.py`), dropped `content/__init__.py`. Kept the `content/` folder as a pure DATA directory (ships.json + meshes/ + narrator/ + book/) — like Quake's levels/. Added RULE #0 clause 3b: data folders are fine, only code must be flat.
2. **app.py** replaced (Fable's File 12) with flattened imports (`from forge import Forge` + `from vobjects import …` + `from sim import FleetSim` + `from orders import MoveCombination` + `from content_db import ContentDB`). Now 7 ships / 2 squads, Q/E switches commanded squad. settings.json → v0.6.0.
3. **Verified:** content_db/content_demo/app py_compile OK; `python content_demo.py` → **CONTENT CHECK PASSED** (5 classes, 5 meshes 16-24 edges, 7 narrator lines, 2 PLACEHOLDER); app wiring imports resolve; zero `-m`/relative/package imports.
4. Updated COMMENTARIES.md + this WORKFLOW.md. Committed with Fable's exact message + pushed.
5. ⏳ Nir to run `python content_demo.py` + play-test the 7-ship scene, report back (+ any ugly mesh).

### July 5, 2026 — AMENDMENT A1: solid shaded ships — flattened + verified
Nir judged the glowing wireframe ships ugly (they FAIL Bible Law 1: "gaming first"). Fable amended the art direction: ships become **solid opaque lit meshes**; the math layer stays glowing holographic. Applied Fable's **deliverable 8**. Saved verbatim to `BIBLE/FABLE DELIVERABLE 8 - solid shaded ships (Amendment A1).md`.
1. **Flattened per RULE #0:** forge/shaders.py→shaders.py, forge/solid.py→solid.py (`from .shaders/.vobjects`→flat), forge/bloom.py→bloom.py, forge/app.py→forge.py (all `from .x`→flat), content/shipwright.py→shipwright.py; dropped forge/__init__.py. The art note → `notes/amendment_a1_art_direction.md` (docs folder, fine).
2. **app.py** replaced with flattened imports (`from forge import Forge` + `from vobjects import …, Line` + `from solid import SolidMesh` + `from sim import FleetSim` + `from orders import MoveCombination` + `from content_db import ContentDB` + `from shipwright import build_ship`). Ships now SolidMesh + glowing selection ring. settings.json → v0.7.0.
3. **New forge render pipeline:** scene FBO (RGBA16F + depth) → SOLID pass (depth write, no blend) → GLOW pass (depth test, no write, additive) → bloom → crisp overlay. New MESH shader = per-pixel Blinn-Phong (key/fill/rim/spec), two-sided. `shipwright.py` builds each class from lofted hull rings + wings/fins/masts/towers + emissive nozzles.
4. **Verified:** all files py_compile OK; **all 5 ships build headlessly** (264–396 tris each); app wiring imports resolve; zero `-m`/relative/package imports. Could not run the window (Nir is the visual judge — this is an art-director review).
5. Updated COMMENTARIES.md + this WORKFLOW.md. Committed with Fable's exact message + pushed.
6. ⏳ Nir to `python app.py` and review AS ART DIRECTOR: best/worst ship, too dark/bright, panel variation, engine glow (all one-number knobs).
