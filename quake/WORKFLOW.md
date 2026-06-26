# QUAKE (Game 3) — Project WORKFLOW & MEMORY for DeepSeek V4 Pro (OpenCode)

> ⭐ **ON RESTART, READ THIS FIRST.** Then read the **Commentaries** (`quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) — it is the map of the whole project. Then read `quake/DEEPSEEK_LATE_AFTERNOON_HANDOFF_2026-06-26.md` for today's exact state. Then ask Nir what's next. Do NOT try to read the whole BIBLE; it's huge and on-demand.
>
> This is my (DeepSeek's) own memory for the Quake project. AGENTS.md is intentionally NOT modified (Nir's instruction).

---

## 0. WHERE THIS GAME SITS (the Peak Together lineage)
Peak Together is a multi-game platform (repo root = website; each game in its own top-level folder).
- **Game 1 — Descent QED** (`descent/`): an educational 6-DOF flyer (Basel Problem). **FINISHED & SHIPPED** (itch.io + GitHub Releases). Done.
- **Game 2 — Doom / "Principia Descent"** (`doom/`): an educational FPS in Ursina/Panda3D (M0–M3b built, 49 tests). **SHELVED** — superseded by the Quake pivot (a 2D-ish/flat engine couldn't do what we need; see below).
- **Game 3 — Quake** (`quake/`): **CURRENT PROJECT.** A from-scratch **true-3D** redo. We are in the **BUILD phase** — Legs 1+2+3 complete (186/186 tests green). Leg 4 (engine) **ALL 13 MODULES BUILT + GREEN (283/283 tests).** Engine is COMPLETE. Parent 4→5 handoff for Golden Fixture Pack requested; awaiting Parent 4's answer.

🌙 **ON RESTART:** Read `quake/DEEPSEEK_LATE_AFTERNOON_HANDOFF_2026-06-26.md` FIRST — it has the exact current state, what's done today, what's next. Then read the Commentaries. Then ask Nir what's next.

## 1. WHAT QUAKE IS (in one breath)
A first-person, true-3D desktop game (Python, Windows-first) that turns a **geometry-rich book** into a walkable 3D **concept-graph dungeon**. Each idea = a room; each logical dependency = a corridor; corridors cross at different heights as **bridges/underpasses** (because a force-directed graph layout inevitably crosses — that's WHY it must be true 3D, "Quake," not flat "Doom/Wolfenstein"). Walls carry the **step-by-step geometric proof** (each step = a drawing panel + a full-LaTeX text panel). You "read" a panel by **shooting it** (grey → colored). The final lit proof-wall is a hidden door → shoot it → the room's one demon emerges → kill it → ceiling equations bleed red. Clear every room → level complete. **A fun game, not educational software.** First book: **Newton's _Principia_** (1846 Motte English translation; we have clean OCR text + per-page images + page-numbers JSON).

## 2. WHO'S WHO
| Role | Who | What |
|------|-----|------|
| Boss | **Nir** (strulovitz) | Decides everything; carries text between chats; **knows NO code and NO math**; loves emojis 😊 |
| Architect | **Claude Opus 4.8** "parents" | Design/decisions/contracts/child-briefs — **never code**. Parent 1 **died** (context cliff) June 25. Parent 2 DONE (Legs 1+2). Parent 3 DONE (Leg 3 + Parent 3→4 handoff). Parent 4 DONE (Leg 4 engine briefs + parent 4→5 handoff REQUESTED). |
| Children | fresh Opus chats | each implements ONE module to a frozen contract + tests, then discarded |
| Runner | **DeepSeek V4 Pro (me, OpenCode)** | integrate child code, run tests, fix wiring, push to git, **fetch scripture for parents**, and **write the prompts/handoffs** (a dying parent can't). I do NOT write game code unless there is truly no other choice. |
| Fusion | OpenRouter multi-model (GPT-5.5 + Gemini 3.1 + Opus judge) | produced the master doctrine only |

## 3. THE WORKING MODEL & IRON RULES
1. Architect writes **documents**; children write **code**; DeepSeek **integrates/tests/pushes**.
2. **Never re-decide or contradict a frozen format/contract.** Before touching anything formatted/contracted, request that exact section verbatim and design *with* it.
3. **Honesty:** invent nothing; mark gaps; few load-bearing questions; never assert external-API names from memory (Asymptote etc.) — define our own conventions and let the compile loop confirm.
4. **Copy-paste transfers must be prose or fenced code blocks, NEVER Markdown tables** (tables lose their cells on copy — this bit us with the Op→Asymptote table).
5. **Nir's hard constraint:** Nir can't code or do math. ALL *understanding* (scans, math, figures, dependencies) is done by **AI in OpenRouter**. Nir's role is mechanical (fetch, paste, run, eyeball). Never design anything needing Nir to understand a proof or hand-draw a figure.
6. **Budget:** Opus runs at **normal/medium effort** now (XHigh too expensive — Descent was built fine in medium). Expect shorter parent answers; keep prompts focused.

## 4. THE BIBLE + THE COMMENTARIES PROTOCOL (how parents get context)
- The BIBLE (`quake/BIBLE/`) holds verbatim "scriptures" + the prompts. It's **large** — giving it all to a parent is a context-killer.
- **The Commentaries** (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) is the small, **DeepSeek-maintained** digest: catalog + locked decisions + amendment trail. **Every parent gets this in full** + the **Old Testament** + **New Testament** (baseline).
- **Everything else is need-to-know, PARENT-DRIVEN.** The parent decides what to request from the catalog. **Do NOT spoon-feed** a pre-filtered subset — we want Opus's full holistic thinking. Whole files → Nir pastes; snippets/sections → DeepSeek fetches verbatim, Nir pastes.
- **The bible is NEVER rewritten** (always in flux, too huge). The Commentaries is the living, accurate digest; I keep its §4 (amendments) and §5 (frontier) current.

## 5. THE BIBLE CATALOG (`quake/BIBLE/`)
- `QUAKE_DOCTRINE_BY_FUSION.md` — **Old Testament** (Fusion's master doctrine, ~459 lines)
- `QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md` — **New Testament** (the two hard legs: MAP + WALLS, ~385 lines)
- `QUAKE_SECOND_CANON_FORMATS_AND_INTERFACES_BY_OPUS.md` — **Second Canon** (Formats & Interfaces Standard, ~1300+ lines, the big reference)
- `QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md` — **Apocrypha** (Room System v3, bearing-accurate doors; supersedes Room-Maker v2 in the Second Canon)
- `QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` — **the Commentaries** (the digest)
- Prompt history: `FUSION_REQUEST_QUAKE_GAME_FROM_SCRATCH.md`, `PROMPT_TO_OPUS_THE_TWO_LEGS.md`, `PROMPT_TO_OPUS_FORMATS_AND_INTERFACES_STANDARD.md`, `PROMPT_TO_OPUS_REMAINING_GAPS.md`, `PROMPT_TO_OPUS_ROOMS_HAVE_VARIABLE_DOORS.md`, `PROMPT_TO_OPUS_DOORS_MATCH_MAP_BEARINGS.md`, `PROMPT_TO_OPUS_QUAKE_PARENT_2_HANDOFF.md`, `PROMPT_TO_OPUS_QUAKE_PARENT_3_HANDOFF.md`

## 6. LOCKED DECISIONS (the frozen spine — full list lives in Commentaries §3)
Geometry-rich books ONLY (first = Newton's Principia). True 3D, crossings = bridges/underpasses. Two render modes (wireframe corridor / solid room), switched at the door. Two truths (map vs **TARDIS** room). Two machines (level maker / room maker). Three worlds (content/build/runtime; runtime never sees LaTeX/LLM/book). **Geometry = Asymptote ONLY** (no homemade kernel). **Verification = human overlay-diff** tool. **Highlighting = whole figure + per-step Stabilo**, baked, via `prooffig.asy`. Correctness = **fidelity to the printed page**. Importance 1–5 → room size + map color. **Co-op core** (Mover owns body/heading; Shooter owns reticle; decoupled camera). God-mode; **one hidden enemy per room** (behind the final-proof wall); no level boss. Tech: all-Python, Windows-first, **moderngl + pyglet** + numpy/pillow/pydantic-v2/networkx + (build-only) matplotlib/Asymptote/Tectonic + PyInstaller. **NO** hide-the-pipeline engine. ID spine + `schema_version "1.0"` + `extra="forbid"`. **Room v3 (Apocrypha):** doors = node degree; door direction = corridor's true map bearing; room-local axes parallel to map (global compass); spawn heading = bearing+π; size stays TARDIS. Colors live only in `palette.json` (group names = keys).

## 7. WHAT WE DID TODAY (June 26, 2026)

### Morning session
1. **Re-oriented:** Read WORKFLOW + Commentaries. Explained §E flag to Nir (already settled: figure_id-keying).
2. **Launched Parent 3:** Room Maker v3 design frozen. Scripture fetched per Parent 3's pull list.
3. **Built Leg 3 — 5 children one-by-one.**
4. **Parent 3 final mission:** Wrote Parent 3→4 handoff (runtime engine M0–M7).
5. **Launched Parent 4:** Fresh Opus chat with handoff + Commentaries + OT + NT.
6. **Parent 4 delivered engine frozen briefs.**

### Early afternoon session (after restart)
7. **Parent 4 infrastructure gap RESCUED** — contracts.py, glguard.py, conftest.py created.
8. **Installed moderngl 5.12.0 + pyglet 2.1.14.**
9. **Built 4 engine children:** gfx_context, shaders, app M0 stub, camera. M0 ACCEPTANCE PASSED.

### Late afternoon session (Children 5 through 13 — the engine build marathon)
10. **M1 Walk Wireframe COMPLETED:**
    - Child 5: input_actions.py (6/6 tests) — semantic action layer, edge detection, Mover/Shooter split
    - Child 6: render_wire.py (7/7 tests) — Mode A wireframe, line-quads, bloom stub
    - Child 7: guidelines.py (8/8 tests) — guide-line selection + draw
    - Child 8: nav_collision.py (12/12 tests) — corridor nav + room nav + raycasting
11. **M6 Enter Room COMPLETED:**
    - Child 9: assets.py (6/6 tests) — load baked JSON+PNG into Pack with full validation
    - Child 10: render_room.py (8/8 tests) — Mode B solid rooms, walls-with-holes, jambs, alcove, ceiling tint
    - Child 11: readmode.py (5/5 tests) — pin-sharp fullscreen Read Mode, zoom/pan clamp
12. **M7 Full Loop COMPLETED:**
    - Child 12: state.py (6/6 tests) — GameState persistence, atomic save/load, forward-compat
    - Child 13: gameplay.py (15/15 tests) — THE BRAIN: motion, mode-switch, shooting, resolve_shot, LevelComplete

### Total: 283/283 tests green. Engine COMPLETE.
13. **Wrote Parent 4→5 handoff prompt** — detailed mission brief for Golden Fixture Pack.
14. **Wrote DeepSeek late-afternoon handoff** (this file's companion).
15. **Updated WORKFLOW.md** (this file).

## 8. CURRENT SITUATION (June 26, 2026 — late afternoon)

### What's built
- **Leg 1 (MAP):** 9 modules, 94 tests. ✅
- **Leg 2 (WALLS):** 8 modules, 51 tests. ✅
- **Leg 3 (ROOMS):** 5 modules, 41 tests. ✅
- **Leg 4 Engine M-1:** 3 files (contracts, glguard, conftest). ✅
- **Leg 4 Engine M0:** 3 modules, 17 tests. ✅
- **Leg 4 Engine M1:** 5 modules, 40 tests. ✅
- **Leg 4 Engine M6:** 3 modules, 19 tests. ✅
- **Leg 4 Engine M7:** 2 modules, 21 tests. ✅

### Test totals
- Content pipeline (Legs 1+2+3): 186
- Engine (Leg 4, 13 modules): 97
- **GRAND TOTAL: 283/283 green** 🟢

### Git
- All code pushed to GitHub (branch: master).
- Repo: `github.com/strulovitz/peaktogether-website`

### Parent lineage
- Parent 1: DEAD (context cliff June 25)
- Parent 2: DONE (Leg 1+2 frozen briefs)
- Parent 3: DONE (Room Maker v3 + Parent 3→4 handoff)
- **Parent 4: DONE** (engine frozen briefs, 13 modules built and green)
- **Parent 5: PENDING** — handoff request sent to Parent 4, awaiting answer

### What app.py looks like now
- `app.py` is still the M0 stub (triangle + line test). It has NOT been grown to the full §5.4 wiring.

## 9. NEXT STEPS (the 3-parent roadmap)

Nir has decided the next 3 big things will each be done by a separate parent:

**Parent 5 — Golden Fixture Pack** (NEXT, awaiting Parent 4's handoff)
- Hand-author baked JSON+PNG files under `tests/golden_pack/`
- 3 rooms (r_a, r_b, r_c), 3 corridors with 1 crossing (bridge/underpass)
- Exercises every engine system: two-step proof room, non-cardinal bearing doors, demon, ceiling, LevelComplete
- Parent 4→5 handoff prompt sent; answer pending from Nir

**Parent 6 — app.py Full Wiring** (AFTER Golden Pack)
- Grow M0 stub into the full §5.4 loop
- Wire all 13 modules together per-frame
- Mode switching, Read Mode pause, atomic save
- CI smoke launch: main() opens, runs N frames against golden pack, exits 0

**Parent 7 — M8 First Principia Level** (AFTER app.py)
- Choose real Newton propositions
- Define concept graph
- Run full Leg 1+2+3 build pipeline on real Principia data
- Audio SFX
- Turn Quake from tech demo into an actual game

### Deferred
- Audio (~M8) — will be designed by Parent 7
- Figure background-transparency
- Mode A labels (post-M7 polish)

## 10. LESSONS LEARNED / GOTCHAS (don't repeat these)
- **Don't micromanage the architect.** Give Opus the *truth* + the *whole problem* and let it think holistically.
- **Tables don't survive copy-paste** → deliver/request copy-paste content as **fenced code blocks or lists**.
- **I (DeepSeek) don't build things** unless there's no choice; the architect designs, children build.
- **Opus outputs are saved VERBATIM** ("holy").
- **The Commentaries is the answer to the parent-killer context problem.**
- **Children cannot see our codebase.** Every child prompt MUST include ALL types inline.
- **Pydantic pattern mismatches are the #1 integration fix.** Children often get IDs wrong (uppercase wall literals, missing pattern matches, missing schema_version). Always check pydantic validation before running tests.
- **GL integration:** shader attribute names must match (in_pos vs in_position). moderngl.create_context() vs get_context(). solid_program/blit_program take a ctx argument.
- **One parent per mission.** Don't give a parent multiple large missions.
- Nir hates short prompts when he asked for "very detailed." Be thorough.
- Nir loves emojis; be warm, concise, ask before initiative, surface typos.

## 11. CONVENTIONS
- Each game lives in its own top-level folder; never put game files in repo root.
- BIBLE = verbatim scriptures; DeepSeek additions are clearly-marked inline commentaries.
- Commit + push after every meaningful change; give Nir **view (blob)** GitHub links to copy from.
- Default branch is **master** (not main).

## 12. ON RESTART / AGENTS.md
🌙 **ON RESTART:** Read this WORKFLOW.md first, then the **Commentaries**, then **today's handoff** (`quake/DEEPSEEK_LATE_AFTERNOON_HANDOFF_2026-06-26.md`) which has the exact current state. Then ask Nir what's next.

AGENTS.md (`C:\Users\nir_s\.config\opencode\AGENTS.md`) routes startup **directly to Quake**. AGENTS.md lives outside the git repo, so it is NOT on GitHub — it persists locally on Nir's machine.
