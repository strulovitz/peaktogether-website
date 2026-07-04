# COMMENTARIES — repository memory. Updated: July 4, 2026 (forge feature-complete)

Note: "repository" here means the Homeworld game root at `homeworld/` inside the
Peak Together monorepo (github.com/strulovitz/peaktogether-website). Game code
lives under `homeworld/`; the design scriptures live under `homeworld/BIBLE/`;
the Strang book excerpts live under `homeworld/algebra/`.

## PROJECT OVERVIEW & STATE
**Homeworld: A Good Basis** — a free, open-source, two-player-one-screen remake of
Homeworld (1999) where commanding the fleet IS doing linear algebra (every ship is
a column vector; the fleet is a matrix; the 16-mission journey home to Hiigara is
"the search for a good basis"). Teaches Gilbert Strang's linear algebra. Python +
moderngl + pyglet + numpy + Pillow, Windows-first. NO audio, ever (Apocrypha
Amendment A).

**Team model:** Nir (owner — pastes text between chats, runs the game, can't code
or do math) → Claude Fable (the Parent/architect in OpenRouter — designs AND writes
all code, delivered as complete files) → DeepSeek (librarian/runner in OpenCode —
saves Fable verbatim to BIBLE, drops code files in exactly, updates this file,
commits with Fable's exact message, pushes; never designs or writes game code).

**Scriptures (all verbatim in `homeworld/BIBLE/`):** Old Testament (vision + every
mechanic + 16-mission campaign + engineering doctrine — wins over all), New
Testament (forge/fleet/helm module design + INTERFACES v1.0 + the Referee + the
12-line fleet self-test), Apocrypha (content/campaign/bridge/intel/guidestone +
Amendment A "no audio" + Amendment B "Guidestone ≈50 lines" + First-Five-Minutes
Doctrine), Book of Prompts (birth-prompt templates), 2 brainstorms, and one
"FABLE DELIVERABLE N" file per code package.

**Current state (July 4, 2026):** **forge is FEATURE-COMPLETE** (NT build steps 1–4
= Fable deliverables 1–3: walking skeleton → bloom → text + all remaining
primitives). All syntax-checked (py_compile), committed with Fable's exact
messages, pushed. AWAITING Nir's visual confirmation of `run.bat` (the forge
acceptance demo). Requirements already installed on Nir's machine: numpy 2.4.6,
moderngl 5.12.0, pyglet 2.1.14, Pillow 12.2.0 (never install without asking).

**Next packages (NT build order):** (1) Nir confirms forge demo → (2) **helm**
(keyboard=Pilot + mouse=Navigator action layer + demo) → (3) **fleet** (ships as
matrix columns + 10 Hz pulse + orders/events + **referee.py**; target
`fleet.demo` = 12/12) → (4) **app.py wiring** = three ships flying combination
orders (Mission 1 buildable) → then Apocrypha modules (content, campaign+Mission 1,
bridge+Big Picture, intel) → Missions 2–16. In parallel: keep filing Strang book
pages (Chapter 1 next) into `homeworld/algebra/`.

**Books filed so far (`homeworld/algebra/`):** Linear Algebra for Everyone preface
iii–xii (+ combined `preface.txt`); Introduction to Linear Algebra preface iii–x
(+ combined `preface.txt`). Chapter 1 folders exist, empty, awaiting pages.

**Run:** `cd C:\Users\nir_s\peaktogether-website\homeworld` then `.\run.bat`.

## FILE INDEX
homeworld/WORKFLOW.md — DeepSeek's project memory (what we did, current state, road ahead, standing rules) — WORKING
homeworld/COMMENTARIES.md — this file: the living repository memory (Fable's Part-5 format) — WORKING
homeworld/BIBLE/ — verbatim scriptures (OT/NT/Apocrypha/Book of Prompts) + 2 brainstorms + Fable deliverables 1-3 — WORKING
homeworld/algebra/ — Strang book OCR: everyone/ (preface iii-xii + preface.txt) + introduction/ (preface iii-x + preface.txt), each with an empty chapter 1/ — WORKING
homeworld/requirements.txt — Python dependencies (numpy, moderngl, pyglet, Pillow) — WORKING
homeworld/run.bat — double-click launcher (runs `python -m forge.demo`) — WORKING
homeworld/settings.json — human-editable config (v0.3.0; title, size, vsync, bloom_strength, exposure, seed) — WORKING
homeworld/forge/__init__.py — forge package exports (Forge, PULSE_DT, Camera, full VObject vocabulary) — WORKING
homeworld/forge/app.py — Forge class: window, GL, 10 Hz loop, scene FBO -> panels -> labels -> bloom -> screen overlay (fps, F1) — WORKING
homeworld/forge/camera.py — Camera: ORBIT mode + look_at/perspective math (NT 1.3) — WORKING
homeworld/forge/shaders.py — GLSL: line ribbon + bloom pipeline + textured-quad (text/image) shaders (NT 1.5/1.6/1.7) — WORKING
homeworld/forge/bloom.py — Bloom: 3-FBO classic bloom (RGBA16F scene, downsample, Gaussian, composite + tone map) (NT 1.6) — WORKING
homeworld/forge/text.py — GlyphAtlas + TextRenderer (3D labels + screen overlay) + PanelRenderer (ImagePanels) (NT 1.7) — WORKING
homeworld/forge/vobjects.py — FULL primitives: Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel (NT 1.4) — WORKING
homeworld/forge/batches.py — CPU segment->camera-facing-ribbon expansion (+ per-segment color for Trail), vectorized numpy (NT 1.5) — WORKING
homeworld/forge/demo.py — FULL forge acceptance demo: trail, floating text, flattening det box, live SVD image panel, ellipsoid, F1 overlay (NT Part 6) — WORKING (awaiting owner's eyes)

## INTERFACES
INTERFACES.md not yet committed as a standalone file. Frozen contracts in force
come from NEW_TESTAMENT.md Part 5 (v1.0). forge is now FEATURE-COMPLETE:
Forge(settings), .window, .camera, .add/.remove, .set_debug_lines (F1 overlay
live), .screenshot, .run(tick_cb, frame_cb); Camera .set_orbit, .orbit_input,
.eye, .view, .proj; the FULL VObject vocabulary (Line, Arrow, DashedLine, Grid,
WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel); bloom;
glyph-atlas text (3D labels + screen overlay).
Not yet implemented (later packages): FOLLOW/POV camera modes; forge is
otherwise done. Next modules: helm, then fleet.

## DEMO STATUS
forge.demo — not yet confirmed on owner's machine — PENDING (requirements already
installed: numpy 2.4.6, moderngl 5.12.0, pyglet 2.1.14, Pillow 12.2.0; run via
run.bat). Now the FULL acceptance demo (trail, floating text, flattening
determinant box counting to vol 0.00, live SVD image panel rank 1->32, ellipsoid,
fps corner, F1 debug overlay).
helm.demo — not built yet.
fleet.demo — not built yet (self-test target: 12/12).
bridge.demo / campaign.demo / intel.demo — not built yet.

## CHANGE LOG (newest first, keep the last ~30 entries)
July 4, 2026 — NT step 4: text (glyph atlas) + remaining primitives — forge feature-complete — by Parent Fable (via DeepSeek)
July 4, 2026 — NT step 3: bloom (RGBA16F scene FBO, gaussian blur, composite + tone map) — by Parent Fable (via DeepSeek)
July 4, 2026 — NT steps 1-2: forge walking skeleton (window, camera, ribbons, grid, first arrow) — by Parent Fable (via DeepSeek)

## PLACEHOLDER LEDGER
(none yet — content/ book-excerpt files not created until the campaign packages begin)
