# QUAKE (Game 3) — Project WORKFLOW & MEMORY for DeepSeek V4 Pro (OpenCode)

> ⭐ **ON RESTART, READ THIS FIRST.** Then read the **Commentaries** (`quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`) — it is the map of the whole project. Then read `quake/DEEPSEEK_MORNING_HANDOFF_2026-06-26.md` for today's exact state. Then ask Nir what's next. Do NOT try to read the whole BIBLE; it's huge and on-demand.
>
> This is my (DeepSeek's) own memory for the Quake project. AGENTS.md is intentionally NOT modified (Nir's instruction).

---

## 0. WHERE THIS GAME SITS (the Peak Together lineage)
Peak Together is a multi-game platform (repo root = website; each game in its own top-level folder).
- **Game 1 — Descent QED** (`descent/`): an educational 6-DOF flyer (Basel Problem). **FINISHED & SHIPPED** (itch.io + GitHub Releases). Done.
- **Game 2 — Doom / "Principia Descent"** (`doom/`): an educational FPS in Ursina/Panda3D (M0–M3b built, 49 tests). **SHELVED** — superseded by the Quake pivot (a 2D-ish/flat engine couldn't do what we need; see below).
- **Game 3 — Quake** (`quake/`): **CURRENT PROJECT.** A from-scratch **true-3D** redo. We are in the **BUILD phase** — Legs 1+2+3 complete (186/186 tests green). Leg 4 (engine) design delivered by Parent 4, children not yet spun.

🌙 **ON RESTART:** If you're waking up fresh, read `quake/DEEPSEEK_MORNING_HANDOFF_2026-06-26.md` FIRST — it has the exact current state, what's done today, what's next. Then read the Commentaries. Then ask Nir what's next.

## 1. WHAT QUAKE IS (in one breath)
A first-person, true-3D desktop game (Python, Windows-first) that turns a **geometry-rich book** into a walkable 3D **concept-graph dungeon**. Each idea = a room; each logical dependency = a corridor; corridors cross at different heights as **bridges/underpasses** (because a force-directed graph layout inevitably crosses — that's WHY it must be true 3D, "Quake," not flat "Doom/Wolfenstein"). Walls carry the **step-by-step geometric proof** (each step = a drawing panel + a full-LaTeX text panel). You "read" a panel by **shooting it** (grey → colored). The final lit proof-wall is a hidden door → shoot it → the room's one demon emerges → kill it → ceiling equations bleed red. Clear every room → level complete. **A fun game, not educational software.** First book: **Newton's _Principia_** (1846 Motte English translation; we have clean OCR text + per-page images + page-numbers JSON).

## 2. WHO'S WHO
| Role | Who | What |
|------|-----|------|
| Boss | **Nir** (strulovitz) | Decides everything; carries text between chats; **knows NO code and NO math**; loves emojis 😊 |
| Architect | **Claude Opus 4.8** "parents" | Design/decisions/contracts/child-briefs — **never code**. Parent 1 **died** (context cliff) June 25 after delivering Room System v3. **Parent 2 handoff is ready** (mission slot unfilled). |
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
- Prompt history: `FUSION_REQUEST_QUAKE_GAME_FROM_SCRATCH.md`, `PROMPT_TO_OPUS_THE_TWO_LEGS.md`, `PROMPT_TO_OPUS_FORMATS_AND_INTERFACES_STANDARD.md`, `PROMPT_TO_OPUS_REMAINING_GAPS.md`, `PROMPT_TO_OPUS_ROOMS_HAVE_VARIABLE_DOORS.md`, `PROMPT_TO_OPUS_DOORS_MATCH_MAP_BEARINGS.md`, `PROMPT_TO_OPUS_QUAKE_PARENT_2_HANDOFF.md`

## 6. LOCKED DECISIONS (the frozen spine — full list lives in Commentaries §3)
Geometry-rich books ONLY (first = Newton's Principia). True 3D, crossings = bridges/underpasses. Two render modes (wireframe corridor / solid room), switched at the door. Two truths (map vs **TARDIS** room). Two machines (level maker / room maker). Three worlds (content/build/runtime; runtime never sees LaTeX/LLM/book). **Geometry = Asymptote ONLY** (no homemade kernel). **Verification = human overlay-diff** tool. **Highlighting = whole figure + per-step Stabilo**, baked, via `prooffig.asy`. Correctness = **fidelity to the printed page**. Importance 1–5 → room size + map color. **Co-op core** (Mover owns body/heading; Shooter owns reticle; decoupled camera). God-mode; **one hidden enemy per room** (behind the final-proof wall); no level boss. Tech: all-Python, Windows-first, **moderngl + pyglet** + numpy/pillow/pydantic-v2/networkx + (build-only) matplotlib/Asymptote/Tectonic + PyInstaller. **NO** hide-the-pipeline engine. ID spine + `schema_version "1.0"` + `extra="forbid"`. **Room v3 (Apocrypha):** doors = node degree; door direction = corridor's true map bearing; room-local axes parallel to map (global compass); spawn heading = bearing+π; size stays TARDIS. Colors live only in `palette.json` (group names = keys).

## 7. WHAT WE DID TODAY (June 26, 2026)

1. **Re-oriented:** Read WORKFLOW + Commentaries. Explained §E flag to Nir (already settled: figure_id-keying).
2. **Launched Parent 3:** Room Maker v3 design frozen. Scripture fetched per Parent 3's pull list.
3. **Built Leg 3 — 5 children one-by-one:**
   - C1 portal_spec (4 tests) — bearings from floorplan+graph
   - C2 room_geometry (17 tests) — bearing rays, perimeter s-map, nudge, subdivide
   - C3 room_pack (7 tests) — panel sizing, first-fit, grow-and-retry
   - C4 room_validate (6 tests) — §8 validation rules
   - C5 room_maker (7 tests) — orchestrator: asset-resolve, doors, panels, demon, ceiling
   - Extended raw_models.py with BuildConfig, RoomSource, RoomRuntime v3, DoorRT, etc.
4. **Parent 3 final mission:** Wrote Parent 3→4 handoff (runtime engine M0–M7).
5. **Launched Parent 4:** Fresh Opus chat with handoff + Commentaries + OT + NT. Fetched §5.1/§5.3/§5.4/§4.4/§4.2/§4.6/§4.7/Apocrypha §7-§8/§4.5 panels/§4.8.
6. **Parent 4 delivered engine frozen briefs** — answer with Nir, NOT YET PROCESSED by DeepSeek.
7. Wrote this morning handoff + updated WORKFLOW. Pushed to GitHub.
8. **Parent 4's answer SAVED** — verbatim as `QUAKE_LEG_4_ENGINE_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_4.md`. Commentaries updated (item #12). 13 engine children identified, ready to spin.

### Afternoon session (after restart, early afternoon)
9. **Parent 4 infrastructure gap RESCUED** — Parent 4 delivered full PART 1.5 with verbatim contracts.py, glguard.py, conftest.py. Created all three files.
10. **Installed moderngl 5.12.0 + pyglet 2.1.14** (not previously in environment). HAVE_GL=True confirmed.
11. **Built 4 engine children one-by-one:**
    - M-1 (INFRA): contracts.py, glguard.py, conftest.py — foundation
    - C1 gfx_context.py (6 tests) — window + GL context + GPU capability check
    - C2 shaders.py (4 tests) — wire/solid/blit GLSL programs + ceiling tint
    - C3 app.py M0 stub (7 tests) — triangle + wireframe render loop, depth on, blend off
    - C4 camera.py (7 tests) — critically-damped decoupled camera, pure math, PITCH_CLAMP_RAD from contracts
12. **M0 ACCEPTANCE GATE PASSED** — GPU path is ours. M1 IN PROGRESS (camera done, 4 more M1 modules remain).
13. **Critical lesson:** Children cannot see our codebase. Every child prompt MUST include ALL types inline (pydantic models, aliases, constants) so the child writes matching code.
14. Wrote `DEEPSEEK_EARLY_AFTERNOON_HANDOFF_2026-06-26.md` — detailed restart document.

## 8. CURRENT SITUATION (June 26, 2026 — early afternoon)
- **Leg 1 (MAP)** built, 94 tests. **Leg 2 (WALLS)** built, 51 tests. **Leg 3 (ROOMS)** built, 41 tests.
- **210/210 total tests green.** Content pipeline COMPLETE. M-1+M0 engine DONE.
- **Parent 1 dead. Parent 2 done. Parent 3 done** (Room Maker v3 + Parent 3→4 handoff).
- **Parent 4 done** (engine frozen child briefs, 13 modules M-1 through M7).
- **M0 ACCEPTANCE PASSED.** M1 IN PROGRESS (camera ✅, 4 modules remaining).
- All code pushed to GitHub (branch: master).
- **Parent 4 DONE** — delivered engine frozen child briefs. Answer saved as catalog item #12.
- All code pushed to GitHub (branch: master).

## 9. NEXT STEPS (on wake)
1. ~~**Read Parent 4's answer** from Nir. Save verbatim.~~ ✅ DONE.
2. ~~**Update Commentaries** catalog (add item #12).~~ ✅ DONE.
3. ~~**M-1 Infrastructure** (contracts + glguard + conftest)~~ ✅ DONE.
4. ~~**M0 (GPU path)**~~ ✅ DONE. gfx_context + shaders + app M0 stub.
5. **M1 (walk wireframe)** — 4 modules remaining:
   - Child 5: input_actions.py (semantic action layer, 6 tests)
   - Child 6: render_wire.py (Mode A wireframe, 7 tests)
   - Child 7: guidelines.py (guide-line selection + draw, 8 tests)
   - Child 8: nav_collision.py (corridor nav, 5 tests + corridor tests)
6. **M6 (enter room):** assets → render_room → readmode → nav_collision grows
7. **M7 (full loop):** state → gameplay → app.py final wiring
8. **Build golden fixture pack** under `tests/golden_pack/` per Part 3 spec.
9. Deferred: audio (~M8), figure background-transparency, Mode A labels (post-M7).

### ⚡ CRITICAL: Child prompt format
Children CANNOT see our codebase. Every prompt MUST include:
- ALL types inline (pydantic models, type aliases, constants)
- The full Brief spec from Parent 4's engine document
- Exact module path and test path
- Exact test names
- ONE block (no internal ``` fences that break copy-paste)

## 10. LESSONS LEARNED / GOTCHAS (don't repeat these)
- **Don't micromanage the architect.** Give Opus the *truth* + the *whole problem* and let it think holistically. Surgical "fix exactly this field" prompts are wrong (Nir's "pinky finger, not the whole body" rebuke). Same for context: don't spoon-feed parents pre-filtered lines.
- **Tables don't survive copy-paste** → deliver/request copy-paste content as **fenced code blocks or lists**.
- **I (DeepSeek) don't build things** unless there's no choice; the architect designs, children build.
- **Opus outputs are saved VERBATIM** ("holy"). Wrap any DeepSeek additions in clearly-marked begin/end commentary blocks with author + status.
- **The Commentaries is the answer to the parent-killer context problem.** Maintain it; never rewrite the whole bible.
- Nir loves emojis; be warm, concise, ask before initiative, surface typos.

## 11. CONVENTIONS
- Each game lives in its own top-level folder; never put game files in repo root.
- BIBLE = verbatim scriptures; DeepSeek additions are clearly-marked inline commentaries.
- Commit + push after every meaningful change; give Nir **view (blob)** GitHub links to copy from.
- Default branch is **master** (not main).

## 12. ON RESTART / AGENTS.md
🌙 **ON RESTART:** Read this WORKFLOW.md first, then the **Commentaries** (`quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`), then **today's handoff** (`quake/DEEPSEEK_EARLY_AFTERNOON_HANDOFF_2026-06-26.md`) which has the exact current state, what's done, and what's next. Then ask Nir what's next.

AGENTS.md (`C:\Users\nir_s\.config\opencode\AGENTS.md`) routes startup **directly to Quake**. AGENTS.md lives outside the git repo, so it is NOT on GitHub — it persists locally on Nir's machine.
