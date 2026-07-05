# HOMEWORLD: A GOOD BASIS (Game 4) — Project WORKFLOW & MEMORY for DeepSeek V4 Pro (OpenCode)

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
Game root = `homeworld/`. Run with: `cd C:\Users\nir_s\peaktogether-website\homeworld` then `.\run.bat` (which runs `python -m forge.demo`).

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

## 5. CURRENT SITUATION (July 5, 2026)
- ✅ **forge is FEATURE-COMPLETE + CONFIRMED by Nir** — deliverables 1–3 applied; Nir's eyes confirmed: text readable (Consolas), det box flat at `vol 0.00`.
- ✅ **helm is COMPLETE** — NT step 5 (Fable deliverable 4): `helm/` package = actions.py (frozen action list v1), keyboard_map.py (Pilot), mouse_map.py (Navigator), joystick_map.py + gamepad_map.py (stubs w/ full impl instructions), __init__.py (Helm orchestrator), demo.py. settings.json bumped v0.3.0 → v0.4.0 (adds `input` section). All syntax-checked, committed with Fable's exact message, pushed.
- ⏳ **AWAITING Nir's console confirmation** of `python -m helm.demo` (NOT run.bat — run.bat still launches forge). Six behaviors to verify: mapped-key actions, held-axis W (W+S cancel), TAB/SHIFT+TAB select, mouse pointer/buttons, wheel, unmapped key = no crash.
- The last thing before Nir restarts OpenCode: WORKFLOW.md + COMMENTARIES written; everything pushed.

## 6. WHAT STILL NEEDS TO BE DONE (the road ahead)
Per the New Testament build order + Fable's stated plan:
1. ⏳ **Nir confirms helm demo** (`python -m helm.demo`, report to Fable).
2. ✅ **helm** (NT Part 2) — DONE. (joystick/Xbox mappers deferred — Fable's Book of Prompts + the stub docstrings flag these as my one sanctioned future coding task, ONLY when Nir explicitly invokes it.)
3. **fleet** (NT Part 3) — the simulation core: ships as matrix columns, the 10 Hz pulse, orders, events, and **referee.py** (the canonical NumPy verdict functions). Target: `python -m fleet.demo` prints **12/12** self-test PASS.
4. **app.py wiring** (NT Part 4) — bind forge + helm + fleet → three ships flying combination orders live on screen (Bible Mission 1 becomes buildable).
5. Then the APOCRYPHA modules: **content** loader, **campaign** runner + Mission 1, **bridge** console + Big Picture, **intel** narrator. Then Missions 2–16.
6. Ongoing in parallel: keep filing Strang book pages (Chapter 1 next) into `homeworld/algebra/`.

## 7. STANDING RULES / LESSONS (how I work on Homeworld)
- **SAVE VERBATIM.** Fable's answers → BIBLE, word-for-word, LaTeX untouched. Strip only chat UI chrome (timestamps, "Reasoning", model labels) and Nir's own instructions.
- **DROP CODE IN EXACTLY.** Fable's code files go to the paths he names, byte-for-byte. He writes complete files (never diffs). Full path stated before each fence.
- **COMMIT WITH FABLE'S EXACT MESSAGE** (e.g. "NT step 4: text (glyph atlas) + remaining primitives — forge feature-complete"). Update COMMENTARIES.md every change. Push. Report done.
- **I DON'T DESIGN.** No redesigning, no "improving." Mechanical fixes only, and only when exact old/new text is specified. Anything needing judgment → back to Fable (via Nir).
- **NEVER install/download without asking.** Requirements are already present.
- **Syntax-check only** (`python -m py_compile`) — safe, no deps needed. Do NOT run the GUI demo myself; Nir is the visual judge.
- **Give Nir normal run commands** with `cd <full path>` then `.\run.bat` (PowerShell) — no "install Python" lectures (he has it).
- **Emojis abundantly**, warm, concise. Never call him "boss" — just **Nir**.
- **Game code lives under `homeworld/`** (the game root in the monorepo). `__pycache__`, `*.pyc`, `build/` are gitignored (fine).
- Give Nir **view (blob)** GitHub links when he asks, plain text, no fancy formatting that 404s.

## 8. CONVENTIONS
- Repo: `github.com/strulovitz/peaktogether-website`, branch **master**. Local: `C:\Users\nir_s\peaktogether-website`.
- Each game = its own top-level folder. Homeworld = `homeworld/`.
- BIBLE = verbatim scriptures. COMMENTARIES.md = the living repo memory (Fable's Part-5 format). This WORKFLOW.md = my DeepSeek memory.
- Commit + push after every meaningful change.

## 9. SESSION LOG
### July 4, 2026 — Homeworld born; books filed; scriptures saved; forge built to feature-complete
1. Created `homeworld/algebra/{everyone,introduction}/{preface,chapter 1}/` structure.
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
7. ⏳ Nir to run `python -m helm.demo` (console visible) and report the six input behaviors to Fable.
