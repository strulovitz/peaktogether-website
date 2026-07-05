# COMMENTARIES — repository memory. Updated: July 5, 2026 (helm complete)

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
Doctrine), Book of Prompts (birth-prompt templates), Ten Commandments (the ORIGINAL
founding document v1.0 — even more foundational than the OT v2.1), Parent 1→2
Handoff (Fable's honest goodbye letter), 2 brainstorms, and 9 Fable deliverable files.

**Current state (July 5, 2026):** forge ✅, helm ✅, fleet ✅ (12/12), app.py wiring ✅,
content data layer ✅, **AMENDMENT A1 ✅**, and **AMENDMENT A1.1 ✅** (Fable deliverable 9).
**A1.1 — ships never bloom (architectural fix):** Dual render targets — location 0 = SOLID
buffer (ships, untouched by bloom or tone mapping), location 1 = GLOW buffer (holograms only,
feeds bloom). Mothership at (0,0,0) with dark slate hull; 10-unit overlay basis axes e1/e2/e3
drawn ON TOP of hulls (depth test OFF for overlay objects). Engine nozzles/lamps use dim
emissive values ≤1 (no HDR). COMPOSITE_FRAG reads 3 textures (solid + glow + blurred glow)
and tone-maps ONLY the hologram layer. Ships stay crisp like real Homeworld hulls. settings
v0.7.1. 12/12 fleet green. Python CODE all FLAT. NOTE: run.bat deleted (Nir) — run with
`python app.py`.

**Next packages (NT/Apocrypha):** (1) ✅ forge → (2) ✅ helm → (3) ✅ fleet → (4) ✅ app
wiring → (5) ✅ content → (6) ✅ **A1 solid ships** → iterate art per Nir → then **bridge**
(forge 2D overlay + widget kit + FLEET ZONE console — Navigator's mouse, 2nd player joins) →
**campaign + Mission 1** → Missions 2–16. In parallel: fill PLACEHOLDER book excerpts.

**Books filed so far (`homeworld/algebra/`):** Linear Algebra for Everyone preface
iii–xii (+ combined `preface.txt`); Introduction to Linear Algebra preface iii–x
(+ combined `preface.txt`). Chapter 1 folders exist, empty, awaiting pages.

**Run (Quake-style, NEVER `-m`):** `cd C:\Users\nir_s\peaktogether-website\homeworld` then
`python forge\demo.py` (forge) or `python helm\demo.py` (helm), or double-click `run.bat`.
**Import convention LOCKED:** flat absolute imports only (`from camera import Camera`); NO
relative imports (`from .`) anywhere — they force `-m`, which Nir never agreed to. Every Fable
file that arrives with `from .` / `-m` is converted to flat absolute imports on drop-in.

## FILE INDEX
homeworld/WORKFLOW.md — DeepSeek's project memory (what we did, current state, road ahead, standing rules) — WORKING
homeworld/COMMENTARIES.md — this file: the living repository memory (Fable's Part-5 format) — WORKING
homeworld/BIBLE/ — verbatim scriptures (OT/NT/Apocrypha/Book of Prompts/Ten Commandments/Parent 1→2 Handoff) + 2 brainstorms + Fable deliverables 1-9 — WORKING
homeworld/notes/amendment_a1_art_direction.md — AMENDMENT A1: ships = solid opaque lit meshes; math layer = glowing holograms over them; "looks like a game a gamer would choose" outranks aesthetic theory (owner is arbiter) — WORKING
homeworld/shaders.py — GLSL: line ribbon + MESH (Blinn-Phong key/fill/rim/spec, two-sided) + bloom pipeline + textured-quad shaders (Amendment A1) — WORKING
homeworld/solid.py — SolidMesh (opaque lit triangle vobject, per-vertex color+emissive, set_transform/set_highlight) + SolidRenderer (batched, depth test, no blend) (Amendment A1) — WORKING
homeworld/shipwright.py — procedural solid-ship generator: lofted hulls + wings/fins/masts/towers + emissive nozzles, per-class deterministic; build_ship(klass, spec) -> verts/tris/colors/emissive (264-396 tris/class) (Amendment A1) — WORKING
homeworld/forge.py — Forge class (window, GL, 10 Hz loop): render pipeline SOLID pass (depth write) -> GLOW pass (depth test, no write) -> bloom -> overlay (Amendment A1) — WORKING
homeworld/bloom.py — Bloom: scene FBO now RGBA16F + DEPTH (solids need depth); downsample/Gaussian/composite+tonemap (Amendment A1) — WORKING
homeworld/app.py — THE GAME SHELL (root): wires forge+helm+fleet+content; shakedown scenario (7 ships in 2 squads: mothership + 3 fighters squad 1, corvette+collector+frigate squad 2; keyboard combination-order console; Q/E switch commanded squad). Runs `python app.py` — FLAT, no `-m`, no hacks. (NT step 9 / Apocrypha 1) — WORKING (awaiting Nir play-test)
homeworld/content_db.py — ContentDB (was content/db.py): loads + LOUDLY validates the content/ data tree (ships, meshes, narrator, book, missions) (Apocrypha 1.1-1.4) — WORKING
homeworld/content_demo.py — content check (was content/demo.py): prints CONTENT CHECK PASSED + placeholder ledger; run `python content_demo.py` (NEVER `-m`) — WORKING (verified)
homeworld/content/ — DATA folder (like Quake's levels/): ships.json + meshes/{mothership,fighter,corvette,collector,frigate}.json + narrator/core.json + book/ch1_excerpts.json (2 PLACEHOLDER excerpts awaiting Strang paste) — WORKING
homeworld/algebra/ — Strang book OCR: everyone/ (preface iii-xii + preface.txt) + introduction/ (preface iii-x + preface.txt), each with an empty chapter 1/ — WORKING
homeworld/requirements.txt — Python dependencies (numpy, moderngl, pyglet, Pillow) — WORKING
run.bat — DELETED (Nir's choice — always runs with `python app.py` directly) — GONE
homeworld/settings.json — human-editable config (v0.5.0; title, size, vsync, bloom_strength, exposure, seed, input) — WORKING
—— STRUCTURE: ALL modules are FLAT siblings in homeworld/ (no forge/helm/fleet subfolders, no __init__.py, no packages — Quake-style). ——
homeworld/forge.py — Forge class (was forge/app.py): window, GL, 10 Hz loop, scene FBO -> panels -> labels -> bloom -> screen overlay (fps, F1), PULSE_DT (NT 1) — WORKING
homeworld/camera.py — Camera: ORBIT mode + look_at/perspective math (NT 1.3) — WORKING
homeworld/shaders.py — GLSL: line ribbon + bloom pipeline + textured-quad (text/image) shaders (NT 1.5/1.6/1.7) — WORKING
homeworld/bloom.py — Bloom: 3-FBO classic bloom (RGBA16F scene, downsample, Gaussian, composite + tone map) (NT 1.6) — WORKING
homeworld/text.py — GlyphAtlas + TextRenderer (3D labels + screen overlay) + PanelRenderer (ImagePanels) (NT 1.7) — WORKING
homeworld/vobjects.py — FULL primitives: Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel (NT 1.4) — WORKING
homeworld/overlay2d.py — 2D screen-space UI layer (INTERFACES v1.1, B1): Rect2D/Line2D/Label2D/Image2D items + Overlay2D renderer (own shader OVERLAY2D_VERT/FRAG, standard alpha blend, painter's algorithm, text_width helper). Wired into Forge (.overlay2d, drawn after bloom, before HUD) — WORKING
homeworld/demo2d.py — 2D overlay acceptance demo (was forge/demo2d.py): console mock-up (panel, slider, clock, 2 images) over a 3D world; run `python demo2d.py` — WORKING
homeworld/widgets.py — Navigator's mouse-only widget kit (B2, APOCRYPHA 3.3): Widget base + WidgetManager (hit-test topmost-first, drag capture, wheel-to-hovered) + Button/Slider/MatrixGrid/ValueReadout/HintCard, built on overlay2d, retained-mode — WORKING
homeworld/widgets_demo.py — widget-kit acceptance demo: 3x3 MatrixGrid with live rank via referee.rank (edit bottom row: 2→3), slider, buttons (one disabled), hint card; mouse-only; run `python widgets_demo.py` — WORKING
homeworld/batches.py — CPU segment->camera-facing-ribbon expansion (+ per-segment color for Trail), vectorized numpy (NT 1.5) — WORKING
homeworld/forge_demo.py — FULL forge acceptance demo: trail, floating text, flattening det box, live SVD image panel, ellipsoid, F1 overlay (NT Part 6) — WORKING (confirmed by Nir)
homeworld/helm.py — Helm orchestrator (was helm/__init__.py): pilot+navigator device factory (settings-driven), .attach/.poll/.poll_axes_only, graceful fallback to keyboard/mouse (NT 2.3) — WORKING
homeworld/actions.py — THE FROZEN ACTION LIST (v1): PILOT_AXES, PILOT_BUTTONS, SYSTEM_BUTTONS, ActionEvent, PointerState (NT 2.2) — WORKING
homeworld/keyboard_map.py — KeyboardMapper (Pilot baseline): frozen default bindings + settings overrides, held-key axes, press/release events, TAB/SHIFT+TAB select (NT 2.4) — WORKING
homeworld/mouse_map.py — MouseMapper (Navigator baseline): PointerState (x/y/primary/secondary/wheel), pyglet-native bottom-left origin (NT 2.2) — WORKING
homeworld/joystick_map.py — JoystickMapper STUB (NotImplementedError + full T16000M impl instructions; sanctioned DeepSeek future work, NT 2.5) — STUB
homeworld/gamepad_map.py — GamepadMapper STUB (NotImplementedError + full Xbox impl instructions; sanctioned DeepSeek future work, NT 2.5) — STUB
homeworld/helm_demo.py — helm acceptance demo: 10 Hz poll loop printing actions/axes/pointer/wheel to console (NT Part 6) — WORKING (confirmed by Nir)
homeworld/referee.py — THE REFEREE: canonical NumPy verdict fns (rank, is_solvable, residual, least_squares, nullspace_basis, in_nullspace, spanned_volume, real_eigen_axis, weak_axis, gram_penalty, cr_factor, svd_partial) — the game's math conscience (NT 3.6) — WORKING
homeworld/orders.py — THE FROZEN ORDER TYPES v1: MoveCombination, Trim, SetIntake, FireSolution, LeastSquaresFire, GramSchmidtDrill, RowOperation, BackSubstitute, BuildShip, JamStation, AssignSquad (NT 3.3) — WORKING
homeworld/events.py — THE FROZEN EVENT TYPES v1: Event(kind, data) + the frozen kind list (NT 3.4) — WORKING
homeworld/ships.py — Ship dataclass + BUILTIN_CLASSES placeholder table (mothership/fighter/corvette/collector/frigate) + get_class (NT 3.2) — WORKING
homeworld/snapshot.py — FleetSnapshot (frozen, copied arrays) + copy_context; the read-only view forge/bridge read (NT 3.5) — WORKING
homeworld/sim.py — FleetSim: the 9-phase fixed-order 10 Hz pulse (prev_pos, orders, movement, drills, harvest, combat, sensors, structure, events) + snapshot/save/load; deterministic (own RNG) (NT 3.5) — WORKING
homeworld/fleet_demo.py — fleet headless self-test: re-proves 12 Bible worked examples through referee+sim, prints FLEET SELF-TEST PASSED (12/12) (NT Part 6) — WORKING (12/12, confirmed by Nir)

## INTERFACES
INTERFACES.md not yet committed as a standalone file. Frozen contracts in force
come from NEW_TESTAMENT.md Part 5 (v1.0). forge is FEATURE-COMPLETE:
Forge(settings), .window, .camera, .add/.remove, .set_debug_lines (F1 overlay
live), .screenshot, .run(tick_cb, frame_cb); Camera .set_orbit, .orbit_input,
.eye, .view, .proj; the FULL VObject vocabulary (Line, Arrow, DashedLine, Grid,
WireSphere, WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel); bloom;
glyph-atlas text (3D labels + screen overlay).
INTERFACES v1.1 (owner-approved via APOCRYPHA 3.1): forge/overlay2d.py adds the entire 2D UI vocabulary — Rect2D(x,y,w,h,color,filled=False), Line2D(x0,y0,x1,y1,color), Label2D(text,x,y,px=16,color), Image2D(image,x,y,w,h) — all with .visible/.color/.set_color, window-pixel coords, origin bottom-left; setters set_rect/set_points/set_text/set_pos/set_image; Rect2D/Line2D have .thickness (px). Renderer Overlay2D(ctx, atlas): add/remove/clear/text_width(text,px)/draw(w,h). Forge gains .overlay2d, drawn after bloom composite, before HUD text, standard alpha blending, insertion-order painter's algorithm. No further UI primitives without amendment. (Delivered flat per RULE #0: overlay2d.py + demo2d.py, run `python demo2d.py`.)
B2 shipped: widgets.py (Button, Slider, MatrixGrid, ValueReadout, HintCard + WidgetManager with drag capture, per APOCRYPHA 3.3) and widgets_demo.py. Widget constructors match the frozen APOCRYPHA signatures; positions set via set_rect after construction. MatrixGrid: wheel = step, click-drag vertical = step per 8 px, .step attr default 1.0. Mouse-only (keyboard belongs to the Pilot). WidgetManager.on_pointer(ps) once per PULSE, .draw() once per FRAME; rank verdict via the real referee.rank, never a numpy re-implementation. (Flat per RULE #0: run `python widgets_demo.py`.)
helm is COMPLETE (NT 2.2/2.3, ACTIONS_VERSION 1): Helm(settings), .attach(window),
.poll() -> (events, axes, pointer) once per PULSE, .poll_axes_only() once per FRAME;
ActionEvent(action, value), PointerState(x, y, primary, secondary, wheel); the frozen
action list PILOT_AXES (CAM_YAW/PITCH/ZOOM, TRIM_X/Y/Z) + PILOT_BUTTONS + SYSTEM_BUTTONS.
Keyboard (Pilot) + mouse (Navigator) live; joystick/gamepad are stubs (NT 2.5).
fleet is COMPLETE (NT Part 3): FleetSim(seed, content=None) with .submit(order), .tick(dt)
-> [events], .snapshot() -> FleetSnapshot, .spawn/.install_context/.set_engine_vectors,
.save(path)/.load(path); referee module (frozen verdict fns, TOL_RANK/TOL_RESIDUAL/TOL_IMAG);
12 frozen order types; Event(kind, data); Ship + BUILTIN_CLASSES. Deterministic 9-phase pulse.
Not yet implemented (later packages): FOLLOW/POV camera modes; joystick/gamepad
mappers. Next: app.py root wiring (forge + helm + fleet).

## DEMO STATUS
forge.demo — CONFIRMED on owner's machine — WORKING (Nir's eyes: text readable in
Consolas; determinant box flat when vol 0.00). Requirements already installed:
numpy 2.4.6, moderngl 5.12.0, pyglet 2.1.14, Pillow 12.2.0; run via run.bat.
helm.demo — CONFIRMED on owner's machine (Nir tried every key: mapped-key press/release
actions; held-axis W with W+S cancel; TAB / SHIFT+TAB select; mouse pointer/buttons; wheel;
unmapped key = no crash — all as designed). helm is DONE.
fleet.demo — DeepSeek verified **FLEET SELF-TEST PASSED (12/12)** via `python fleet\demo.py`
(headless, no window); Nir confirmed 12/12. Each PASS line re-proves a Bible worked
example through the real referee (shield solve, jamming/nullspace, gate determinant, weak-axis
targeting, SVD energy, determinism, performance floor).
app.py (game) — the playable build: wiring imports verified; awaiting Nir's play-test (now
7 ships in 2 squads, Q/E switches commanded squad, meshes from content/, fleet rank 5).
content_demo.py — DeepSeek verified **CONTENT CHECK PASSED** (5 classes, 5 meshes 16-24 edges,
7 narrator lines, 2 PLACEHOLDER book excerpts); awaiting Nir's run.
bridge.demo / campaign.demo / intel.demo — not built yet.

## CHANGE LOG (newest first, keep the last ~30 entries)
July 5, 2026 — House rule: console/panel backgrounds use alpha 0.85 (owner-standardized). demo2d.py panel_bg 0.75→0.85; widgets.py already complies — by DeepSeek (Fable maintenance task, B3 prep)
July 5, 2026 — bridge: add widget kit (B2) — Button/Slider/MatrixGrid/ValueReadout/HintCard + WidgetManager (mouse-only per APOCRYPHA 3.3, drag capture, wheel-to-hovered) + widgets_demo (live rank via referee.rank) — by Parent Fable (via DeepSeek; both files NEW, already flat, imports house-correct, DEEPSEEK fix-me notes removed; no shared files touched; fleet 12/12 still green)
July 5, 2026 — forge: add 2D overlay layer (INTERFACES v1.1, bridge B1) — Rect2D/Line2D/Label2D/Image2D + Overlay2D renderer + demo2d acceptance demo — by Parent Fable (via DeepSeek; flattened per RULE #0: forge/overlay2d.py→overlay2d.py, forge/demo2d.py→demo2d.py, demo imports→flat, run `python demo2d.py`; two wiring insertions into forge.py: import + self.overlay2d in __init__ + self.overlay2d.draw(w,h) after bloom composite/before HUD; fleet 12/12 still green)
July 5, 2026 — Amendment A1.1: ships never bloom (dual render targets — solid buffer untouched + glow buffer feeds bloom only), dark mothership at origin (0,0,0), overlay axes (10-unit long e1/e2/e3 drawn on top of hulls with depth test off), engine nozzles = dim lamps (<1 emissive, no HDR), mothership color steel-blue [0.45,0.55,0.7] — by Parent Fable (via DeepSeek; flattened per RULE #0: forge/*→flat; settings v0.7.1; 12/12 still green)
July 5, 2026 — Amendment A1 recorded into the SCRIPTURES: add-only "⚖️ OWNER AMENDMENTS (READ FIRST)" banner at the top of the Old Testament + New Testament + Apocrypha (solid ships override the wireframe/holographic aesthetic; Fable's text kept verbatim below) — by DeepSeek (Nir's instruction: owner amendments belong in the Bible, not only notes/COMMENTARIES)
July 5, 2026 — AMENDMENT A1: solid shaded ships — mesh shader, depth pipeline, procedural shipwright — by Parent Fable (via DeepSeek; flattened per RULE #0: forge/*.py→root, content/shipwright.py→shipwright.py, forge/__init__ dropped; all 5 ships build headlessly)
July 5, 2026 — Apocrypha step 1: content data layer (ContentDB, ships.json, 5 meshes, narrator core, book placeholders) + app wiring — by Parent Fable (via DeepSeek; flattened per RULE #0: content/db.py→content_db.py, content/demo.py→content_demo.py, __init__ dropped; content/ kept as DATA folder; CONTENT CHECK PASSED)
July 5, 2026 — FLATTENED to Quake structure: all 23 modules moved out of forge/helm/fleet subfolders into homeworld/ root as flat siblings (forge.py, helm.py, sim.py, …); removed the app.py sys.path bootstrap; plain absolute imports; `python app.py` runs like Quake (no -m, no hacks); 12/12 still green — by DeepSeek (Nir's order; RULE #0 now mandates flat + flatten every Fable delivery)
July 5, 2026 — NT step 9: app.py wiring — forge+helm+fleet, shakedown scenario with combination orders — by Parent Fable (via DeepSeek; RULE #0 sys.path bootstrap so `python app.py` works with the flat packages, no -m; wiring imports verified)
July 5, 2026 — NT steps 6-7: fleet core (referee, orders, events, sim, snapshot) + 12-line self-test — by Parent Fable (via DeepSeek; dropped in Quake-style flat absolute imports; 12/12 verified)
July 5, 2026 — Converted Homeworld to Quake-style: flat absolute imports everywhere, run `python <file>.py` (NEVER `-m`); fixed run.bat + all docstrings + WORKFLOW/COMMENTARIES — by DeepSeek (Nir's order; Nir never agreed to `-m`)
July 5, 2026 — NT step 5: helm complete (actions, keyboard+mouse mappers, joystick/gamepad stubs, demo) — by Parent Fable (via DeepSeek)
July 4, 2026 — NT step 4: text (glyph atlas) + remaining primitives — forge feature-complete — by Parent Fable (via DeepSeek)
July 4, 2026 — NT step 3: bloom (RGBA16F scene FBO, gaussian blur, composite + tone map) — by Parent Fable (via DeepSeek)
July 4, 2026 — NT steps 1-2: forge walking skeleton (window, camera, ribbons, grid, first arrow) — by Parent Fable (via DeepSeek)

## PLACEHOLDER LEDGER
(none yet — content/ book-excerpt files not created until the campaign packages begin)
