# 🛑 DEEPSEEK V4 PRO — RESTART PROMPT — HOMEWORLD: A GOOD BASIS 🛑

**READ THIS FIRST on every restart.** You are DeepSeek V4 Pro inside OpenCode on Nir's Windows Desktop PC. This file is your self-handoff — it tells you everything you need to know to pick up exactly where we stopped, without re-reading every memory file. Also read RULE #0 in WORKFLOW.md (it's the most important thing). Then ask Nir what's next.

---

## 1. WHAT HOMEWORLD IS (1 breath)

**Game 4** on the Peak Together platform. A free, open-source, **two-player-one-screen** remake of Homeworld (1999) — a 3D space RTS — in which **commanding your fleet IS doing linear algebra**. Every ship is a column vector, the fleet is a matrix, and the 16-mission journey home to Hiigara is "the search for a good basis" (Strang §8.3). Teaches **Gilbert Strang's** linear algebra. Built in **Python** (moderngl + pyglet + numpy + Pillow), Windows-first, **NO audio ever**.

---

## 2. WHO'S WHO (the working model — DIFFERENT from Quake!)

| Role | Who | What |
|------|-----|------|
| Owner | **Nir** (strulovitz) | Decides everything; copy-pastes text between chats; runs the game; **knows NO code and NO math**; loves emojis 😊 |
| Architect / Parent | **Claude Fable** (Opus, in OpenRouter) | Designs everything AND writes the actual code, package by package. Nir pastes Fable's answers to you. |
| Librarian / Runner | **DeepSeek V4 Pro (you, OpenCode)** | Save Fable's answers VERBATIM to the BIBLE; flatten Fable's code per RULE #0; drop files into the repo EXACTLY (with flattening); syntax-check; run headless self-tests; update COMMENTARIES.md + WORKFLOW.md; commit with Fable's EXACT message; push. You do **mechanical** work — you never redesign or write game code. |

---

## 3. WHAT WE DID TODAY (July 5, 2026 — 8 Fable deliverables in one MASSIVE session)

This was the single biggest day in Homeworld history. Your context is ~31% full (Nir is restarting OpenCode for a fresh window). Here's every beat, in order:

### Deliverable 4 — helm (NT step 5) — CONFIRMED by Nir
- Fable sent the helm package. You dropped it in: actions.py, keyboard_map.py, mouse_map.py, joystick_map.py + gamepad_map.py (stubs), helm.py (Helm orchestrator), helm_demo.py. settings.json → v0.4.0.
- **CRITICAL:** Fable told Nir to run `python -m helm.demo`. **Nir HATES `-m` and was FURIOUS.** This started an all-day war against packages/relative imports. Nir demanded Homeworld run like Quake — plain `python app.py`, flat, no `-m`, ever. You tried several wrong approaches (sys.path bootstrap, inconsistent cd/file commands) before finally doing it right.
- Nir tested every key on helm_demo — works perfectly. Helm confirmed.

### Deliverable 5 — fleet (NT steps 6-7) — CONFIRMED by Nir (12/12)
- referee.py (12 canonical NumPy fns), orders.py (12 types), events.py, ships.py (Ship + BUILTIN_CLASSES), snapshot.py, sim.py (FleetSim — deterministic 9-phase 10 Hz pulse), fleet_demo.py.
- `python fleet_demo.py` → **FLEET SELF-TEST PASSED (12/12)**. Nir confirmed.

### Deliverable 6 — app.py wiring (NT step 9) — FIRST PLAYABLE BUILD
- Root app.py: wires forge+helm+fleet. Shakedown: mothership + 3 fighters (squad 1). Keyboard combination console.
- **You made a sys.path bootstrap hack instead of flattening.** Nir caught this and was furious.

### THE BIG FLATTENING (Nir's order — the definitive fix)
- **Moved ALL modules** out of forge/, helm/, fleet/ into homeworld/ root as flat siblings.
- Renamed collisions: forge/app.py→forge.py, helm/__init__.py→helm.py, forge/demo→forge_demo.py, helm/demo→helm_demo.py, fleet/demo→fleet_demo.py.
- Deleted forge/__init__.py, fleet/__init__.py, and the empty subfolders.
- Removed all sys.path hacks, all relative imports, all `-m`.
- Verified: all files compile, 12/12 still green, app imports resolve.
- **Wrote RULE #0** at the top of WORKFLOW.md — the PERMANENT iron rule. (Read it on every restart — it's the most important thing in this project.)
- Nir deleted run.bat (he runs `python app.py` directly).

### Deliverable 7 — content data layer (Apocrypha step 1)
- content_db.py (ContentDB), content_demo.py, and the content/ DATA folder (ships.json + 5 mesh JSONs + narrator/core.json + book/ch1_excerpts.json w/ 2 PLACEHOLDER excerpts).
- Flattened: content/db.py→content_db.py, content/demo.py→content_demo.py, dropped content/__init__.py. Content/ kept as DATA folder (like Quake's levels/).
- app.py now 7 ships in 2 squads (Q/E switches), fleet rank 5.
- `python content_demo.py` → CONTENT CHECK PASSED.
- **Nir never ran this** — we moved straight to Amendment A1 after he saw the wireframe ships.

### Deliverable 8 — AMENDMENT A1: SOLID SHADED SHIPS (Nir's art-direction ruling)
- **Nir judged the glowing-wireframe ships as UGLY.** They FAIL Bible Law 1 ("gaming first").
- Fable amended the art direction. Ships are now **SOLID, OPAQUE, LIT** triangle meshes:
  - Per-pixel Blinn-Phong (key light + fill light + rim light + specular highlight)
  - Flat-shaded paneled hulls with per-face color variation
  - Emissive engine nozzles/windows feeding bloom
  - 264–396 triangles per ship class, generated procedurally by `shipwright.py`
- **The math layer** (arrows, grids, ghost vectors, trails, labels) stays **glowing holographic**, drawn additively OVER the solid ships with depth testing.
- New render pipeline: **SOLID pass (depth write) → GLOW pass (depth test, no write) → bloom → overlay**.
- Files: shaders.py (updated with MESH_VERT/MESH_FRAG), solid.py (new — SolidMesh + SolidRenderer), bloom.py (added depth buffer), forge.py (new pipeline), shipwright.py (new — procedural ship builder).
- Flattened per RULE #0. Art note at `notes/amendment_a1_art_direction.md`.
- Verified: all 5 ships build headlessly (264–396 tris each). App imports resolve.
- **Nir has NOT yet seen/played the solid ships.** The context window is now ~31% full and Nir is restarting so you can see them with fresh context.

### Amendment A1 recorded into the SCRIPTURES (Nir caught you on this)
- You had only put A1 in notes/ and COMMENTARIES. Nir asked: "why did you not put the amendments into the old testament bible?"
- He was right: the Bible is the top-precedence source of truth. You added an **add-only "⚖️ OWNER AMENDMENTS (READ FIRST)" banner** to the top of OT + NT + Apocrypha (all three), recording A1. Fable's original words preserved verbatim below each banner.

---

## 4. CURRENT SITUATION — EXACTLY WHERE WE ARE NOW (July 5, 2026, end of day)

### Every module built and verified (not all confirmed by Nir's eyes yet):

| Module | Status | Nir's Eyes? |
|--------|--------|-------------|
| forge (render engine) | ✅ COMPLETE | ✅ Yes (original forge demo; forge.py updated for A1 but same API) |
| helm (input) | ✅ COMPLETE | ✅ Yes (tested every key) |
| fleet (simulation) | ✅ COMPLETE | ✅ Yes (12/12 self-test confirmed) |
| app.py (game wiring) | ✅ COMPLETE | ⚠️ Wired verified by you; Nir played the WIREframe version, not the A1 solid version |
| content (data layer) | ✅ COMPLETE | ⚠️ Content check verified by you; Nir never ran `python content_demo.py` |
| **SOLID SHIPS (A1)** | ✅ BUILT, NOT SEEN | ❌ **Nir has NOT seen the solid ships AT ALL** — the context-window restart is happening FOR THIS REASON |

### STRUCTURE: completely FLAT (Quake-style)
All 26+ Python modules are flat siblings in `homeworld/`. No packages, no __init__.py, no -m, no sys.path hacks. `python app.py` runs exactly like Quake's `python app.py` — a plain file in a flat folder.

Data folders that are fine per RULE #0 clause 3b (not code):
- `content/` — JSON data (ships.json, 5 mesh files, narrator/core.json, book/ch1_excerpts.json w/ 2 PLACEHOLDER excerpts)
- `algebra/` — Strang book OCR
- `BIBLE/` — verbatim scriptures + 8 Fable deliverable files
- `notes/` — amendment_a1_art_direction.md

### Settings: v0.7.0
`settings.json`: title "Homeworld: A Good Basis", v0.7.0, 1280×720, vsync true, bloom_strength 0.85, exposure 2.5, seed 1234. Input section: pilot_device=keyboard, navigator_device=mouse, empty overrides.

### What was DELETED
- `run.bat` — Nir's choice (he runs `python app.py` directly)
- forge/__init__.py, fleet/__init__.py — package re-export files, not needed flat

---

## 5. HOW TO RUN EVERYTHING (all from the homeworld/ folder, full paths, NO `-m`)

Every run command is two lines. The cd line is always `cd C:\Users\nir_s\peaktogether-website\homeworld`.

| What | The two commands (second line only — cd is always the same) |
|------|--------|
| **THE GAME** (solid ships!) | `python app.py` |
| Fleet self-test (headless) | `python fleet_demo.py` |
| Content check (headless) | `python content_demo.py` |
| Helm demo (keyboard test) | `python helm_demo.py` |
| Forge demo (old wireframe) | `python forge_demo.py` |

---

## 6. WHAT NIR NEEDS TO DO (FIRST THING on restart — this is what we were waiting for)

**🎨 Play-test the solid ships as art director.** Run `python app.py` and review:
- (a) Which ship looks best / worst
- (b) Too dark or too bright overall
- (c) Panel variation — nice or noisy
- (d) Engine glow — more or less

Every one of these is a one-number change in the code. Fable is waiting for Nir's art-director report before building the next module (bridge).

Controls reminder (keyboard — both players on keyboard+mouse for now):
- **W/S, A/D, R/F** — edit combination coefficients (c3, c1, c2)
- **ENTER** — commit the order (squad flies c1*e1 + c2*e2 + c3*e3)
- **X** — toggle diagonal vs component-by-component flight
- **BACKSPACE** — reset coefficients to zero
- **Q / E** — switch commanded squad (squad 1 = fighters, squad 2 = corvette+collector+frigate)
- **TAB / SHIFT+TAB** — select next/previous ship (white highlight + glowing ring)
- **C** — recenter camera on selected ship
- **ARROWS / PAGEUP / PAGEDOWN** — orbit / zoom camera
- **P** — pause
- **F1** — debug overlay (pulse, fleet rank, coefficients, mode, squad, selected ship)
- **F12** — screenshot (saves to screenshots/ folder)
- **ESC** — quit

Also Nir may want to run at some point:
- `python content_demo.py` → should print CONTENT CHECK PASSED (5 classes, 424–744 verts per ship, 7 narrator lines, 2 PLACEHOLDER book excerpts)
- `python fleet_demo.py` → should print FLEET SELF-TEST PASSED (12/12)

---

## 7. WHAT STILL NEEDS TO BE DONE (the road ahead)

After Nir confirms the solid-ships look good (or tells you what to tweak):
1. **Iterate art** per Nir's feedback (one-number changes — you relay to Fable or Fable adjusts)
2. **Bridge** (NT/Apocrypha) — forge 2D overlay + widget kit + FLEET ZONE console. The Navigator picks up the mouse. 2nd player officially joins.
3. **Campaign + Mission 1** (Apocrypha) — minute-by-minute script. First real playable mission.
4. **Missions 2–16** — full 16-mission journey.
5. **Book excerpts** — Nir pastes Strang text into the PLACEHOLDER slots in content/book/ch1_excerpts.json (two placeholder entries waiting for him).
6. **Joystick + Xbox mappers** — stubs exist (joystick_map.py, gamepad_map.py) with complete implementation instructions in their docstrings. DeepSeek-sanctioned future work.
7. **FOLLOW/POV camera modes** — deferred.

---

## 8. CRITICAL STANDING RULES (READ EVERY RESTART)

### 🛑🛑🛑 RULE #0 (in WORKFLOW.md — read it fully!) 🛑🛑🛑
The short version:
- **NO `-m`, EVER.** Nir never agreed to it and hates it.
- **FLAT STRUCTURE.** All Python code is flat siblings in homeworld/. No packages, no __init__.py, no subfolders for code.
- **FLATTEN EVERY FABLE DELIVERY** on drop-in. Fable builds in subfolders/packages → you flatten them. Tell Nir at the start that you flattened.
- **The 2-line command format ALWAYS:** `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python <filename>.py`. Both full paths, both consistent.
- Data folders are fine (content/, algebra/, BIBLE/, notes/ — they're not Python packages).

### Other rules
- **Save Fable answers VERBATIM** to BIBLE. Strip only chat chrome and Nir's instructions.
- **Drop code in exactly** (but flattened per RULE #0). Syntax-check only.
- **Commit with Fable's EXACT message.** Push.
- **Owner amendments go into the SCRIPTURES.** When Nir makes a binding decision, add it as an add-only "⚖️ OWNER AMENDMENTS (READ FIRST)" banner at the top of OT + NT + Apocrypha. Keep Fable's original words below.
- **Never install/download without asking.** Requirements already present.
- **Give Nir the full 2-line command every time.**
- **Never call Nir "boss"** — just Nir.
- **Emojis abundantly**, warm and polite.
- **Test numbers:** PyInstaller inside `.pyi-build/` NEVER `build/`. `python app.py` from homeworld.
- **Current working directory for operations:** `C:\Users\nir_s\peaktogether-website\homeworld`
- **Runs:** `python -m py_compile` is for your internal checks. `python app.py` / `python fleet_demo.py` / etc. is what you give Nir. No -m in Nir-facing commands.

---

## 9. THE SCRIPTURES (what to read if you need detail)

All verbatim in `homeworld/BIBLE/`. The big three (with A1 amendment banners):
- **Old Testament** (HOMEWORLD OLD TESTAMENT BY FABLE.md) — vision, mechanics, 16-mission campaign, engineering doctrine. **Top precedence.** Has A1 banner.
- **New Testament** (HOMEWORLD NEW TESTAMENT BY FABLE.md) — forge/fleet/helm module design + INTERFACES v1.0. Has A1 banner.
- **Apocrypha** (HOMEWORLD APOCRYPHA BY FABLE.md) — content/campaign/bridge/intel/guidestone + Amendment B "NO AUDIO" + First-Five-Minutes Doctrine. Has A1 banner.

Plus 8 FABLE DELIVERABLE files (#1 through #8) — each a verbatim code drop from a Fable chat.

**On restart, read WORKFLOW.md first** (especially RULE #0), then this file, then COMMENTARIES.md for the reference index. Do NOT read the whole Bible — it's huge; pull sections on demand.

---

## 10. THE LAST THING THAT WAS SAID

Nir said: *"ok thank you so much!!! :-) so now your context-window here in OpenCode is 31% which is very full. i want to restart you. please save everything to github, explain to yourself in very detailed prompt what we did today, what we are doing now, what is the situation now, what we still need to do, etc. ... then i will re-start OpenCode so that you have fresh memory, and when you wake up, i will ask you to read your prompt that you now write to yourself."*

This file is that prompt. When you wake up and Nir asks you to read it — you already have. Say: "Good morning, Nir!!! 😊🌌 I've read the restart prompt and I'm ready! Homeworld is FLAT, all 8 modules are built, and **the solid ships** (Amendment A1) are ready and waiting for your art-director eyes — want to run `python app.py` and have a look? 🎨🚀"

**END OF RESTART PROMPT.**
