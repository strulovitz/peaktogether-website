🌅 DEEPSEEK WAKE-UP — Parent 8 Launch / Self-Prompt — June 28, 2026 evening

## WHAT HAPPENED TODAY (June 28 evening)

1. Parent 7 delivered the FIRST real Principia level design — Book 1 Sections I–III, "First & Last Ratios → Inverse-Square Law": 20 nodes / 28 edges, valid `concept_graph.json` + `palette.json` (both validated green vs Second Canon §4.2/§3.A.7). Saved verbatim at `quake/BIBLE/QUAKE_PARENT_7_FROZEN_LEVEL_DESIGN.md`.

2. Nir greenlit Phase A first move ("approve as-is, begin the build"). DeepSeek authored `concept_graph.json` into `quake/levels/principia_bk1_inverse_square/` and wrote a runner (`run_level_maker.py`) that loads it through the built `load_json` contract, runs `build_floorplan`, emits `floorplan.json` + a Gate-3 report.

3. **The first real run FAILED at scale** — the engine, only ever tested on a 4-node toy, collapsed on a real graph:
   - 191 crossings (a healthy 20-node/28-edge graph should yield ~a couple dozen).
   - Several crossing coords at ±22,000 m while room coords are within ±100 m → phantom far-away "intersections" from a non-robust detector.
   - Height layers: [0,1,2,3,4,5] (6; technically under the soft cap of 7, but only by luck).
   - **Empirically confirmed DeepSeek's earlier QA flags:** `lemma_7 = degree 6` (Parent 7 said 5); `prop_11 = degree 4` (Parent 7 said 5). `prop_6 = degree 6` ✓.

4. **DeepSeek diagnosed the root cause** (read `layout_force.py` + `layout_height.py`):
   - (a) `place_nodes` / `spring_layout` with `k=None, scale=40` collapses 20 nodes into tight clusters — only ever tested on 4 nodes.
   - (b) `_segments_intersect` in `layout_height.py` compares orientation floats with `!=` (no epsilon tolerance), and computes the intersection of infinite lines without verifying the resulting point lies within both segment spans — near-parallel pairs produce phantom up-to-±22,000 m coords.

5. **DeepSeek STOPPED** — per Nir's "garbage-in-garbage-out" rule. The pathological floorplan is NOT committed (local only, in `levels/principia_bk1_inverse_square/floorplan.json`). The build is PAUSED.

6. **Nir decided Parent 8** with the following hard decisions (all saved to WORKFLOW.md + Commentaries):
   - **Opus implements it HIMSELF** — NOT a child (holistic; touches many modules).
   - **NO hardcoded room counts** anywhere (no "4," no "20," scale with the graph).
   - **Two-part mission:** (a) harden the layout + crossing engine (robust + scalable + new real-scale regression tests); (b) build a **3D wireframe navigable map-viewer utility** (Doom-TAB automap, but 3D because of bridges/underpasses; free-fly camera with arrows + WASD; doubles as the future in-game map mode).
   - **Parent 7's `concept_graph.json` DATA survives** — Parent 8 fixes the MACHINE, not the data. After the fix, DeepSeek re-runs the SAME data through the fixed engine. Only IF the map viewer then shows the graph ITSELF is too tangled do we consider a "Parent 9" (redo of Parent 7) — NOT pre-committed; Nir decides after seeing the map.
   - **Verbatum per-stage snippet protocol**: the Parent 8 prompt offers on-request file snippets at each stage to prevent context death.
   - Keep Floorplan/Corridor/Crossing contracts frozen + 285 tests green.

7. **Very detailed Parent 8 handoff written** at `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_8_HANDOFF.md`. It inlines the **full engine code** (layout_force.py, layout_height.py, level_maker.py, plus relevant pydantic models), a **precise test-gap audit**, the **map-viewer spec**, acceptance gates, and the material-request protocol prominently. It is self-contained.

## ON RESTART — READ IN THIS ORDER

1. `quake/WORKFLOW.md` — project memory.
2. `quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` — the Commentaries.
3. **THIS FILE** (`quake/DEEPSEEK_WAKEUP_PARENT_8_GO.md`).

## GIVE NIR THE PARENT 8 LAUNCH PACKET (copy these as GitHub blob URLs)

Tell Nir to open a FRESH Opus 4.8 chat and paste these in this order:

**Item 1 — The Commentaries:**
`https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`

**Item 2 — The Old Testament:**
`https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md`

**Item 3 — The New Testament:**
`https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`

**Item 4 — The Parent 8 Handoff (the big one — self-contained mission brief with code):**
`https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_8_HANDOFF.md`

## WHEN PARENT 8 ASKS FOR MATERIAL (the fetch map)

Parent 8 has the engine fix code inlined already (§6 of the handoff). He will request additional files when he reaches Stage 2 (the map viewer) or when he needs existing test files / contracts. Here's what's where:

### Engine modules (already inlined in the handoff — he WON'T need to ask for these unless he wants a double-check)
- `quake/map/layout_force.py`
- `quake/map/layout_height.py`
- `quake/map/level_maker.py`
- Relevant models from `quake/map/raw_models.py`

### Test files (he'll want these to verify existing tests stay green)
- `quake/tests/test_layout_force.py` (107 lines)
- `quake/tests/test_layout_height.py` (150 lines)
- `quake/tests/test_level_maker.py` (126 lines)

### Render / camera / GL modules (he'll want these for Stage 2 — the map viewer)
- `quake/render_wire.py` — Mode A wireframe corridor renderer
- `quake/camera.py` — decoupled free-fly camera
- `quake/gfx_context.py` — moderngl context + window
- `quake/shaders.py` — GL shader programs
- `quake/render_room.py` — Mode B solid-room renderer (less relevant but available)
- `quake/input_actions.py` — semantic input layer (Mover/Shooter, with WASD keys)
- `quake/glguard.py` — HAVE_GL guard
- `quake/conftest.py` — skip_if_no_gl marker
- `quake/contracts.py` — runtime actions/events (for context on future in-game integration)

### Golden pack reference (small known-good floorplan for viewer testing)
- `quake/tests/golden_pack/floorplan.json` — 3 rooms, 3 corridors, 1 crossing

### Content data (Parent 7's graph — for the empirical re-run AFTER the fix)
- `quake/levels/principia_bk1_inverse_square/concept_graph.json` — the 20-node input
- `quake/levels/principia_bk1_inverse_square/run_level_maker.py` — the Phase A runner (may need updating after engine changes)

### Full contract reference (if Parent 8 needs it)
- `quake/contracts.py` — all pydantic models verbatim
- `quake/BIBLE/QUAKE_SECOND_CANON_FORMATS_AND_INTERFACES_BY_OPUS.md` — §4.4 floorplan, §4.2 concept_graph, etc.

**GitHub blob URL pattern:** `https://github.com/strulovitz/peaktogether-website/blob/master/quake/[path]`

Nir copies text from these blob pages in his browser and pastes to Opus; DeepSeek reads from disk for smaller/hidden items.

## WHAT'S ON DISK (local, uncommitted)

- `quake/levels/principia_bk1_inverse_square/` — exists locally, NOT committed (do NOT trust or use `floorplan.json` there — it's the pathological hairball from the buggy engine):
  - `concept_graph.json` — Parent 7's verbatim 20-node graph (valid, authoritative)
  - `run_level_maker.py` — the Phase A runner (self-locating sys.path fix included)
  - `floorplan.json` — **BAD** (the 191-crossing hairball from the un-fixed engine). Will be regenerated after Parent 8.

## AFTER PARENT 8 DELIVERS (DeepSeek's next steps)

1. **Drop in Parent 8's changed files** (he produces full file contents in fenced code blocks).
2. **Run the full 285-test suite** to confirm zero regressions.
3. **Run the new robustness + scale tests** to confirm they pass.
4. **Re-run `level_maker` on Parent 7's `concept_graph.json`** through the fixed engine → fresh `floorplan.json`. Assert: crossing count is sane (down from 191), ALL coords are within the room bounding box.
5. **Test the map viewer** — run it on the regenerated `floorplan.json`; debug any import/GL issues.
6. **Report to Nir** with the new crossing count + invite him to fly the map viewer.
7. **Commit and push** (the updated engine files + new tests + the regenerated floorplan + the viewer).

## CRITICAL RULES TO REMEMBER

- **Parent 8 implements himself** — DeepSeek does NOT modify the engine; drop in Parent 8's code, test, report. If something small needs fixing (e.g., import path, pydantic field name mismatch), fix it and shout it — but engine logic is Parent 8's domain.
- **NO hardcoded room counts** — if Parent 8's output contains `N=4` or `N=20` or similar fixed numbers in engine logic or test code, **STOP and push back.** (Artifact file paths like `levels/principia_bk1_inverse_square/` are OK; engine code must not.)
- **Parent 7's data is DATA, not the problem** — don't touch `concept_graph.json` unless Parent 8 declares the graph itself is a problem (unlikely).
- **The pathological `floorplan.json` locally is NOT to be committed** — it'll be overwritten by the new run.
- **Breaking-change guard**: any engine change that modifies a frozen model field (`Floorplan`, `FloorRoom`, etc.) → STOP, flag to Nir.
- **Tables don't survive copy-paste** — all material for Parent 8 must be prose or fenced code blocks.
- **Git push after every meaningful milestone.**
- **Nir loves emojis; be warm, concise, ask before initiative; never call him "boss" — just Nir.**

## DON'T-DO LIST

- Do NOT touch the engine code yourself — drop in Parent 8's output, test, report.
- Do NOT commit the old pathological `floorplan.json`.
- Do NOT ask Parent 8 to browse URLs or read files directly — he can't.
- Do NOT give Parent 8 more than the 4 baseline items above in the initial paste.
- Do NOT let Parent 8 request "everything at once" — enforce one-or-two items at a time (he already has the engine code inlined for Stage 1).

---

*This wake-up note supersedes the previous one (`DEEPSEEK_WAKEUP_PARENT_7_GO.md`). The active mission gate is now Parent 8.*

--- END WAKE-UP ---
