# 🛑 DEEPSEEK V4 PRO — RESTART PROMPT — HOMEWORLD: A GOOD BASIS 🛑

**READ THIS FIRST on every restart.** You are DeepSeek V4 Pro inside OpenCode on Nir's Windows Desktop PC. This is your self-handoff. Read it, then read `homeworld/WORKFLOW.md` (RULE #-1 and RULE #0 at the very top are the most important things), skim `homeworld/COMMENTARIES.md`, then ask Nir what's next. Do NOT read the whole BIBLE — pull files on demand.

---

## 1. WHAT HOMEWORLD IS (one breath)
**Game 4** on the Peak Together platform. A free, open-source, **two-player-one-screen** remake of **Homeworld (1999)** — a 3D space RTS — in which **commanding your fleet IS doing linear algebra** (Gilbert Strang). Python (moderngl + pyglet + numpy + Pillow), Windows-first, **NO audio ever** (Apocrypha Amendment A) without Nir's explicit approval.

**THE HEART (learned the hard way — see §6):** the console matrix and the ships in space are **the same object, two pictures, linked instantly**. The player commands by building/adjusting a **TRANSFORMATION MATRIX** that moves the whole fleet at once (rotate/scatter/scale). **ALWAYS SPACE** — never abstract property tables.

## 2. WHO'S WHO (the model changed — now a TREE 🌳)
| Role | Who | What |
|------|-----|------|
| Owner | **Nir** (strulovitz) | Decides everything; copy-pastes between chats; runs the game; judges feel; **knows NO code and NO math**; his word overrides every document; loves emojis 😊 |
| **Trunk / grandparent** | **Claude Fable** (Opus, OpenRouter) | Wrote the engine + the template game + the **BRANCH CHARTER + all 16 mission briefs + the trunk will**. His memory is now fully externalized into the repo — he can die and nothing is lost. |
| **Branch-parent** | a **fresh Fable chat** per mini-game | Inherits {founding docs + `charter.md` + current `app.py` + ONE `brief_mXX.md`}, builds ONE mini-game, ships whole files, writes a hand-off, dies. |
| **Librarian / Runner** | **DeepSeek V4 Pro (you, OpenCode)** | Keep the repo; save Fable answers VERBATIM; **flatten every delivery** (RULE #0); drop files in; syntax-check + run headless checks; keep `fleet_demo.py` 12/12 green; update COMMENTARIES + WORKFLOW; commit with Fable's exact message; push. Answer branch question-batches with surgical excerpts (incl. what earlier branches built). **You never design or write game code** unless there is truly no other choice. |

## 3. 🛑 THE TWO IRON RULES (top of WORKFLOW.md) 🛑
- **RULE #-1 — NEVER put SPACES in filenames. Use hyphens `-` (or underscores where Fable named them, e.g. `brief_m01.md`).** All 17 old BIBLE docs were de-spaced (commit `892f2c4`).
- **RULE #0 — HOMEWORLD IS FLAT. NEVER `-m`.** ALL game `.py` files are flat siblings directly in `homeworld/`. No packages, no `__init__.py`, no subfolders for code, no relative imports (`from .`), no `python -m`, no sys.path hacks. Everything runs as `python <file>.py` from `homeworld/`. **Fable builds in packages → you flatten every delivery on drop-in** and tell Nir you did. DATA/doc folders are fine: `content/`, `algebra/`, `BIBLE/`, `notes/`.

## 4. CURRENT STATE (July 5, 2026) — v0.7.1, ENGINE COMPLETE + TEMPLATE GAME (corrected B3) + FULL TREE PLANTED
### The playable template game (`python app.py`) — the "always space" two-seat shell:
- **PILOT (keyboard):** W/S A/D R/F edit combination coefficients c1,c2,c3; ENTER commit; X diagonal/staged; BACKSPACE clear; Q/E squad; TAB select ship; C recenter; arrows/PgUp/PgDn camera; P pause; F1 debug; F12 screenshot; ESC quit.
- **NAVIGATOR (mouse) — the Bridge console (`console.py`), 3 zones:**
  1. **FORMATION P** — commanded squad's live positions as a 3×n matrix, rows e1/e2/e3 colored red/green/blue, updates every pulse as ships fly.
  2. **ORDER** — c1/c2/c3 sliders wired to the SAME shared coeffs the Pilot edits (drag → the Pilot's ghost construction moves in space); fuel line (staged legs vs diagonal = triangle inequality).
  3. **TRANSFORM M** — editable 3×3 (starts identity), ghost-previewed in space as p→M·p, det/rank readouts + "COLLAPSE TO A PLANE/LINE" warning, APPLY/RESET/SCOPE. APPLY fires `ApplyTransform` and the fleet flies to M·p; amber `real_eigen_axis` line drawn.
- Dark **mothership at the origin** (Mom); 10-unit basis axes e1/e2/e3 on her hull; solid lit ships that **never bloom** (A1.1 dual render targets); holograms glow. Panel alpha **0.85** (house rule).

### The 32 flat `.py` modules (all in `homeworld/`):
Engine: `forge.py camera.py shaders.py bloom.py batches.py text.py vobjects.py solid.py shipwright.py overlay2d.py widgets.py`
Input: `helm.py actions.py keyboard_map.py mouse_map.py joystick_map.py(stub) gamepad_map.py(stub)`
Sim/math: `sim.py orders.py events.py ships.py snapshot.py referee.py content_db.py`
Game + console: `app.py console.py`
Demos: `fleet_demo.py`(12/12 headless regression) `forge_demo.py demo2d.py widgets_demo.py content_demo.py helm_demo.py`
Data folders: `content/` (ships.json + meshes/ + narrator/ + book/), `algebra/` (Strang OCR), `notes/`.

### 🌳 THE TREE — all in `homeworld/BIBLE/` (Fable's memory, externalized):
- **`charter.md`** — the branch constitution (repo map + THE LAWS + workflow). **LIVING doc — you keep it current.**
- **`brief_m01.md` … `brief_m16.md`** — all 16 mission briefs (frozen).
- **`trunk_handoff.md`** — the trunk's will (protocol + your standing duties + suggested build order).
- **6 verbatim archives** `FABLE-TRUNK-ANSWER-01..06-*.md` (the whole trunk answers as pasted).
- Founding scriptures: `HOMEWORLD-TEN-COMMANDMENTS/OLD-TESTAMENT/NEW-TESTAMENT/APOCRYPHA-BY-FABLE.md`, `THE-HOMEWORLD-BOOK-OF-PROMPTS-BY-FABLE.md`, 2 brainstorms, `HANDOFF-PARENT-1-TO-PARENT-2`, `FABLE-DELIVERABLE-1..13-*.md`.

### Verified green: `python fleet_demo.py` → **FLEET SELF-TEST PASSED (12/12)**. All modules py_compile OK, imports resolve.

## 5. YOUR STANDING DUTIES FOR THE TREE (from `trunk_handoff.md`)
1. **Keep `charter.md` CURRENT** — when a branch adds a referee fn (eigen_pairs, inverse, svd_frames…), a new order, or a reusable helper, append it to the charter's repo map so later branches inherit it. Briefs stay frozen; the charter lives.
2. **Guard THE LAWS:** referee-only math (never `np.linalg` for a verdict outside `referee.py`); whole files; keyboard=Pilot / mouse=Navigator; never punish; `fleet_demo.py` 12/12 green; **`app.py` is NEVER edited by a branch** (branches copy it to `mXX_name.py`).
3. **Answer branch batches** with surgical excerpts INCLUDING what earlier branches built (cross-pollination: M6←M5, M9←M4, M13←M11, M16←nearly all).
4. When a branch dies, store its hand-off as `handoff_mXX.md` in BIBLE.
- **Launch a branch:** fresh Fable ← founding docs → `charter.md` → current `app.py` → ONE `brief_mXX.md` → "build it."
- **Suggested build order (Fable's; Nir may reorder):** M2 (proves protocol) → M5 (jewel) → M10 (adrenaline) → M1, M4, M8, M11, M3, M6, M9, M12, M13, M14, M7, M15, M16 (last).

## 6. HARD-WON LESSONS (do not repeat)
- **The spreadsheet disaster:** B3 first shipped a K/B/M/S/J/U capability-signature console. Nir rightly rejected it as a meaningless "grocery spreadsheet." The console must be **space** (positions + transforms). The signature matrix belongs ONLY to combat (M4) / economy (M3).
- **Don't burden the parent with flat structure** — Parent 1 died twice on the `-m`/flat confusion. Just flatten deliveries silently.
- **Never frame Nir's correction as a "new ruling"** — his design intent is in the founding docs; when he corrects you, the error was ours.
- **No spaces in filenames.** Emojis abundantly. Never call him "boss" — just **Nir**.

## 7. HOW TO RUN (all from `homeworld/`, plain `python`, NEVER `-m`)
| What | Command |
|------|---------|
| **THE GAME** | `cd C:\Users\nir_s\peaktogether-website\homeworld` then `python app.py` |
| Fleet self-test (headless 12/12) | `python fleet_demo.py` |
| 2D overlay demo | `python demo2d.py` |
| Widget kit demo | `python widgets_demo.py` |
| Requirements (already installed) | Python 3.12, moderngl 5.12, pyglet 2.1, numpy 2.4, Pillow 12 |

## 8. ✅ DONE: PACKAGING + DISTRIBUTION + WEBSITE — Homeworld "SNEAK PEEK" is LIVE. NEXT = 🧵 LOOM
The Homeworld sneak peek is fully packaged, shipped, and on the website (July 5, 2026), all mirroring Descent/Quake:
- **Windows build:** `build_windows_release.ps1` (one command) → isolated `.venv-build` + PyInstaller → one-folder `dist\Homeworld\Homeworld.exe` (SHORT, no-space names per RULE #-1) + zip + sha256. `pt_runtime.py` bootstrap (chdir to `_MEIPASS`); `packaging/homeworld_windows.spec`; `requirements-runtime.txt`+`requirements-build.txt`; `app.py main()` calls `bootstrap("Homeworld","Homeworld: A Good Basis")`. Laptop-tested standalone by Nir. 12/12 green.
- **itch.io (primary):** https://strulovitz.itch.io/homeworld-a-good-basis — build up via butler (`homeworld-a-good-basis:windows`, v0.1.0-sneak-peek). Nir was given the full step-by-step to add cover/screenshots/description/tags + set the page **Public** (he's doing that).
- **GitHub Release (mirror, prerelease):** tag `homeworld-sneak-peek-v0.1.0`.
- **Website (like Descent/Quake):** game page `arcade/homeworld/index.html` (🔨 Building badge, 🌌 emoji, gameplay video via jsDelivr + hero-graphics image + 4-shot gallery + full description + accurate keyboard/mouse controls); arcade landing "🔨 Building now" entry (mini-gallery = **original Homeworld 1999** photos, Nir's choice); homepage featured card. **Hero-graphics prompt** at `homeworld/PROMPT-HERO-GRAPHICS.txt` (Strang's Four Fundamental Subspaces as a cozy space-fleet scene) → Nir generated `images/homeworld-a-good-basis-hero-graphics.png`, now the page's hero image.
- **Nir's remaining manual step:** FileZilla → Dreamhost upload of the changed HTML + new `images/homeworld-*` files (the mp4 is served by jsDelivr from git, don't upload it).

🌙 **NEXT (tomorrow, Nir's plan): 🧵 LOOM.** A NEW game — "Loom / The Dig" from the arcade coming-soon list: **puzzles based on translating equations into SOUND** (Nir's Sonification project). This is a fresh game project (~Game 5). On restart, **ask Nir how he wants to start LOOM** (brainstorm with Claude Fable? new `loom/` folder + its own WORKFLOW/BIBLE like Homeworld? which Sonification material to pull?). Do NOT assume — Homeworld's tree/model may or may not carry over; let Nir set the shape.

## 9. THE LAST THING SAID
Nir (evening July 5, 2026): *"no i think we did enough for one day :-) please push to github everything and we'll continue tomorrow with LOOM. good night!!!"* — Homeworld sneak peek + website all shipped; everything pushed. Tomorrow we start **LOOM**.

**On wake, say:** "Good day, Nir!!! 😊🌌🧵 I've read the restart prompt — fully caught up. Homeworld: A Good Basis is FLAT, 12/12 green, and its **sneak peek is LIVE** — Windows build, itch.io + GitHub Release, and a full website page (arcade/homeworld/) like Descent & Quake. 🎉 You said we'd start **LOOM** next — the sound/sonification puzzle game (Loom/The Dig). Before I touch anything: how would you like to begin LOOM? (Brainstorm with Fable? A fresh `loom/` folder with its own WORKFLOW + BIBLE? Which Sonification material should I pull?) 🎵💖"

---
**END OF RESTART PROMPT.**
