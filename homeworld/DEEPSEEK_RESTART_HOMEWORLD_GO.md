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

## 3. WHAT WE DID TODAY (July 5, 2026 — A1.1 + salvaged documents from dying Parent 1)

### Morning: Amendment A1.1 (Fable Deliverable 9)
- Nir saw the A1 solid ships — they were too shiny (bloom on ships, bright HDR nozzles)
- Fable delivered the architectural fix: **dual render targets** — SOLID buffer (ships, untouched by bloom/tone-map) + GLOW buffer (holograms only, feeds bloom)
- **Dark mothership at (0,0,0)** — dark slate hull (0.155, 0.165, 0.195), steel-blue accent [0.45, 0.55, 0.7]
- **Overlay axes** — 10-unit bright e1/e2/e3 with `.overlay = True` → depth test OFF pass on top of mothership hull. "She is the coordinate system made flesh."
- **Dim lamp nozzles** — emissive values ≤1, no HDR. Ships can NEVER bloom, by construction.
- **COMPOSITE_FRAG** reads 3 textures (u_scene pass-through + u_glow full-res + u_bloom blurred) and tone-maps ONLY the hologram layer.
- **7 files modified** (shaders.py, bloom.py, forge.py, shipwright.py, content/ships.json, app.py, settings.json → v0.7.1)
- **ALL FLAT** per RULE #0. Verified: 5/5 py_compile OK, fleet_demo 12/12 GREEN.
- **Nir confirmed: "now it looks great!!! :-)"**
- Saved verbatim: `BIBLE/FABLE DELIVERABLE 9 - A1.1 dual render targets no bloom ships.md`
- Amendment banners updated in OT + NT + Apocrypha to include A1.1.
- Commit `2c8cac9`: "A1.1: ships never bloom (dual render targets), dark mothership at origin, overlay axes — update COMMENTARIES.md."

### Afternoon: Salvaging from dying Parent 1
- Parent 1's OpenRouter context filled. Before launching Parent 2, Nir salvaged 2 critical documents:
  1. **`HOMEWORLD TEN COMMANDMENTS BY FABLE.md`** — the ORIGINAL founding document (v1.0), even more foundational than the OT v2.1. Math typos fixed by DeepSeek (zero-width joiners, broken subscripts/superscripts — cross-referenced with OT v2.1 where needed, only fixing things 90%+ clear).
  2. **`HANDOFF PARENT 1 TO PARENT 2 BY FABLE.md`** — Fable's honest goodbye letter from chat #1. Records exact handoff state: v0.7.1, all modules confirmed, A1+A1.1, 12/12 green, bridge next.
- Parent 1 already wrote the Parent 2 launch handoff himself (not DeepSeek's job).
- Updated WORKFLOW.md, COMMENTARIES.md, wrote this fresh restart prompt.
- Commit `ccf344d` (Ten Commandments), `7861e4b` (Handoff).

---

## 4. CURRENT SITUATION — EXACTLY WHERE WE ARE NOW (July 5, 2026)

### v0.7.1 — Everything is FLAT and WORKING

| Module | Status | Nir's Eyes? |
|--------|--------|-------------|
| forge (render engine) | ✅ COMPLETE (A1.1 dual targets) | ✅ Yes — "looks great!!!" |
| helm (input) | ✅ COMPLETE | ✅ Yes (tested every key) |
| fleet (simulation) | ✅ COMPLETE | ✅ Yes (12/12 confirmed) |
| app.py (game wiring) | ✅ COMPLETE (A1.1 mothership+axes) | ✅ Yes |
| content (data layer) | ✅ COMPLETE | ✅ CONTENT CHECK PASSED |

### Render pipeline (A1.1 — the current truth):
- SOLID pass (location 0, depth write, no blend) → ships, crisp, never bloom/tone-mapped
- GLOW pass (location 1, depth test ON, write OFF, additive) → holograms, feed bloom
- OVERLAY pass (depth test OFF) → `.overlay = True` objects (origin axes on mothership)
- Bloom blurs ONLY the GLOW buffer → composite adds tone-mapped glow over untouched solid
- HUD overlay (crisp text, always on top)

### Structure: COMPLETELY FLAT (Quake-style)
All 26+ Python modules are flat siblings in `homeworld/`. No packages, no __init__.py, no -m, no sys.path hacks. `python app.py` runs exactly like Quake — a plain file in a flat folder.

### BIBLE folder contents:
- 2 brainstorms
- OT v2.1 + NT v1.0 + Apocrypha v1.0 + Book of Prompts
- **Ten Commandments v1.0** (original founding doc — more foundational than the Bible)
- **Parent 1→2 Handoff** (Fable's goodbye letter)
- 9 Fable deliverable files (#1 through #9)
- All with A1+A1.1 amendment banners

### Settings: v0.7.1
1280×720, vsync true, bloom_strength 0.85, exposure 2.5, seed 1234.

---

## 5. HOW TO RUN EVERYTHING (all from homeworld/, full paths, NO `-m`)

| What | Command |
|------|---------|
| **THE GAME** | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python app.py` |
| Fleet self-test (headless) | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python fleet_demo.py` |
| Content check (headless) | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python content_demo.py` |
| Helm demo (keyboard test) | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python helm_demo.py` |
| Forge demo (old wireframe) | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python forge_demo.py` |

---

## 6. WHAT STILL NEEDS TO BE DONE (the road ahead — Parent 1's agreed plan)

1. ⏳ **NEXT: Parent 2 — bridge/** — the Navigator's mouse console. Needs forge 2D overlay API, a widget kit, and the FLEET ZONE console (the fleet matrix A live, ships as columns). This makes it two-player. **Parent 1 already wrote the Parent 2 launch handoff himself.**
2. **intel/** — narrator/event feed consuming content/narrator/*.json (rules already enforced by ContentDB: ≤140 chars, teach⇒cite).
3. **campaign/** — mission runner + Mission m01 ("A Single Voice", Chapter-1: combinations/span; the finale rescues a freighter at 2e1 + 3e3), chapter gates, saves. Then title flow, packaging (DeepSeek+PyInstaller), soak test.
4. **Missions 2–16** — the full 16-mission journey.
5. **Book excerpts** — Nir pastes Strang text into the PLACEHOLDER slots in content/book/ch1_excerpts.json (2 placeholder entries waiting).
6. **Joystick + Xbox mappers** — stubs exist (joystick_map.py, gamepad_map.py) with complete implementation instructions.
7. **FOLLOW/POV camera modes** — deferred.
8. **Audio** — FORBIDDEN without Nir's explicit approval.

---

## 7. THE SCRIPTURES (what to read if you need detail)

All verbatim in `homeworld/BIBLE/`. The most important:

- **Ten Commandments v1.0** — the ORIGINAL founding document. More foundational than the OT.
- **Old Testament v2.1** (HOMEWORLD OLD TESTAMENT BY FABLE.md) — vision, mechanics, 16-mission campaign, engineering doctrine. Has A1+A1.1 banner. **Top precedence.**
- **New Testament v1.0** — forge/fleet/helm module design + INTERFACES v1.0. Has A1+A1.1 banner.
- **Apocrypha v1.0** — content/campaign/bridge/intel/guidestone. Has A1+A1.1 banner.
- **Parent 1→2 Handoff** — Fable's exact state at handoff. Essential reading for understanding where we are.
- **Fable Deliverables 1–9** — each a verbatim code drop from Fable.

**On restart, read WORKFLOW.md first** (especially RULE #0), then this file. Do NOT read the whole Bible — it's huge; pull sections on demand.

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
- **Python command for internal checks:** `python -m py_compile` is fine for your own syntax checks. But `python app.py` / `python fleet_demo.py` / etc. is what you give Nir. No -m in Nir-facing commands.
- **Current working directory for operations:** `C:\Users\nir_s\peaktogether-website\homeworld`

---

## 9. THE LAST THING THAT WAS SAID

Nir said: *"ok please write in your memory (workflow file) and in the apocrypha and wherever needed what we did, what is the current situation and what still needs to be done, also make a very detailed prompt for yourself (replace the old prompt for yourself that you made like 1 hour ago) , and then i will restart OpenCode, because you are now filled-up to 17% of your context-window and i want you to be fresh when we talk to the next Fable parent, please. thank you so much!!! :-)"*

This file is that prompt. When you wake up and Nir asks you to read it — you already have. Say:

**"Good morning, Nir!!! 😊🌌 I've read the restart prompt and I'm ALL caught up! Homeworld v0.7.1 is FLAT and beautiful — dark mothership at the origin, overlay axes, ships never bloom, 12/12 green, Nir confirmed 'looks great!!!' 😍🚀 Parent 1 died but we salvaged the Ten Commandments and his handoff to Parent 2. Parent 1 already wrote the Parent 2 launch handoff himself — ready when you are! What's next? 🎯💖"**

---

**END OF RESTART PROMPT.**
