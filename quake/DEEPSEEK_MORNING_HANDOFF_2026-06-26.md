🌅 DEEPSEEK MORNING HANDOFF — June 26, 2026

## WHERE WE ARE (one-breath summary)

We are building **Quake** (Game 3) — a first-person true-3D game that turns Newton's Principia into a walkable concept-graph dungeon. Each idea = a room, each logical dependency = a corridor, crossings = bridges/underpasses. Walls carry step-by-step geometric proof panels you "read" by shooting them.

**186/186 tests green.** The entire content pipeline (Legs 1+2+3) is built. The runtime graphics engine is next (M0–M7).

---

## WHAT WE DID TODAY (June 26, 2026)

### 1. Woke up, re-oriented
- Read WORKFLOW.md and Commentaries. Found Leg 1+2 built (145 tests), Parent 2 done, §E flag open.
- Explained to Nir that the §E flag (figure_id vs block_id naming) was already settled by Parent 2 — figure_id-keying confirmed, zero rework.

### 2. Launched Parent 3 (Room Maker v3 architect)
- Nir pasted the Parent 3 handoff prompt + Commentaries + OT + NT to a fresh Opus chat.
- I fetched verbatim scriptures Parent 3 requested:
  - Batch 1: Apocrypha whole file
  - Batch 2: Second Canon §2.1 (ID-spine), §4.3 (room_source), §4.5 (room_runtime + commentary), §4.8 (BuildConfig + commentary), §5.2 (build signatures), §5.3 (runtime signatures + Read-Mode rule)
  - Batch 3: Leg-2 Frozen Child Briefs whole file + answer that golden fixture doesn't exist
- Renamed Leg-2 file to shorter name (QUAKE_LEG_2_WALLS_FROZEN_BY_OPUS_PARENT_2.md)
- Parent 3 delivered FROZEN Room Maker v3 child-brief package: 5 modules (portal_spec, room_geometry, room_pack, room_maker, room_validate) + worked degree-5 fixture + 5 pinned gaps + BuildConfig additions + §E settled.

### 3. Built Leg 3 — 5 children, one at a time
Each child: I crafted a self-contained prompt with exact signatures + models + golden tests. Nir pasted to fresh Opus chats. Child returned code. I adapted it to shared models (map.raw_models), wrote proper test files, ran tests, committed, pushed.

| # | Module | Tests | Key function |
|---|--------|-------|-------------|
| C1 | build/portal_spec.py | 4/4 | portal_spec(floorplan, graph, node_id) → RoomPortalSpec |
| C2 | build/room_geometry.py | 17/17 | bearing_to_wall_hit, wall_along_to_s, s_to_wall_along, nudge_doors, subdivide_perimeter |
| C3 | build/room_pack.py | 7/7 | size_and_pack(pair_blocks, doors_bearings, cfg) → PackResult |
| C4 | build/room_validate.py | 6/6 | check_room(room, portals, manifest, cfg) → list[str] |
| C5 | build/room_maker.py | 7/7 | build_room_runtime(room, portals, manifest, cfg) → RoomRuntime |

Pre-work: extended map/raw_models.py with BuildConfig, RoomSource, FigureDecl, DrawingBlock, StepPair, CeilingEq, RoomRuntime (amended with doors: list[DoorRT]), PanelPlacementRT, amended PanelPairRT, EnemyRT, CeilingEqRT, IncidentEdge, RoomPortalSpec, DoorRT.

### 4. Launched Parent 3's final mission — Parent 3→4 handoff
- Wrote detailed prompt asking Parent 3 to write a handoff for Parent 4 (runtime engine)
- Parent 3 delivered QUAKE_PARENT_3_TO_PARENT_4_HANDOFF.md — saved verbatim
- Comprehensive: engine M0-M7 mission, locked decisions, verbatim pull list, risk flags

### 5. Launched Parent 4 (runtime engine architect)
- Nir pasted Parent 3→4 handoff + Commentaries + OT + NT to fresh Opus chat
- I fetched verbatim scriptures Parent 4 requested:
  - Tier 1: §5.1 (Actions/Events/GameState/Pack/NavQuery), §5.3 (runtime signatures + Read-Mode lock), §5.4 (per-frame wiring)
  - Tier 2: §4.4 (Floorplan), §4.2 (ConceptGraph), §4.6+§2.3 (Manifest + pixel convention), §4.7 (savegame)
  - Tier 3: Apocrypha §7-§8 (downstream deltas), §4.5 panel-only + §4.8 (PanelPlacementRT/PanelPairRT/BuildConfig)
  - Tier 4: §2.4 (color rules)

### 6. Parent 4 answered — ANSWER RECEIVED BUT NOT YET PROCESSED
- Nir has the full answer from Parent 4.
- **This is where we stopped.** The answer needs to be integrated/saved, and children spun up.

---

## EXACT CURRENT STATE

### Files on disk
```
quake/
  map/                 # Leg 1 — MAP (9 modules, 94 tests)
    raw_models.py       # ALL shared pydantic models (Leg 1+2+3 models)
    citation_extract.py, citation_normalize.py, merge.py, sanity.py,
    layout_force.py, layout_height.py, level_maker.py, page_map_adapter.py
  bake/                # Leg 2 — WALLS (8 modules, 51 tests)
    palette_gen.py, recipe_validate.py, prooffig_check.py, asy_compile.py,
    _imageops.py, baker_figure.py, baker_text.py
  build/               # Leg 3 — ROOMS (5 modules, 41 tests) ← NEW TODAY
    __init__.py, portal_spec.py, room_geometry.py, room_pack.py,
    room_maker.py, room_validate.py
  tools/               # overlay_diff.py
  tests/               # 186 tests (all green)
    test_portal_spec.py (4), test_room_geometry.py (17),
    test_room_pack.py (7), test_room_validate.py (6),
    test_room_maker.py (7)  ← NEW TODAY
    + all Leg 1+2 tests
  BIBLE/               # All scriptures + handoffs
    QUAKE_PARENT_3_TO_PARENT_4_HANDOFF.md  ← NEW TODAY
  WORKFLOW.md          # Updated today
```

### Parent lineage
- Parent 1 (Claude Opus 4.8): DEAD (context cliff June 25). Delivered OT, NT, Second Canon, Apocrypha, remaining gaps.
- Parent 2 (Claude Opus 4.8): DONE. Delivered Leg 1+2 frozen briefs. Handed off to Parent 3.
- Parent 3 (Claude Opus 4.8): DONE. Delivered Room Maker v3 frozen briefs + Parent 3→4 handoff.
- Parent 4 (Claude Opus 4.8): ACTIVE. Just delivered engine frozen briefs (answer with Nir, NOT YET PROCESSED).

### Test count: 186/186 green
- Leg 1: 94 tests
- Leg 2: 51 tests  
- Leg 3: 41 tests (4+17+7+6+7)

---

## WHAT TO DO NEXT (on wake)

### Step 1 — Process Parent 4's answer
Nir has the full answer from Parent 4 (engine frozen child briefs). I need to:
1. Read it from Nir
2. Save as a BIBLE file: `QUAKE_LEG_4_ENGINE_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_4.md`
3. Update Commentaries catalog (item #12)
4. Identify the child modules and build order

### Step 2 — Build the engine children
Like Leg 3, spin children one at a time:
1. gfx_context.py (moderngl + pyglet window)
2. shaders.py (GLSL wire/solid/blit programs)
3. render_wire.py (Mode A wireframe)
4. camera.py (damped decoupled camera)
5. input_actions.py (semantic input layer)
6. ... and more per Parent 4's briefs

Each child: craft prompt → Nir pastes → receive code → adapt to shared models → test → commit → push.

### Step 3 — Update WORKFLOW.md and Commentaries
After each milestone, update tracking.

---

## CONVENTIONS (don't forget)
- Use `python` (base conda) — has pygame, PyOpenGL, numpy, matplotlib
- Work dir: `C:\Users\nir_s\peaktogether-website\quake`
- GitHub: `github.com/strulovitz/peaktogether-website` (branch: master)
- Push after every change
- Tables DON'T survive copy-paste → use fenced code blocks or lists
- Emojis are mandatory (Nir loves them) 😊🎉✨🔥💪🚀❤️
- Never download files/models without explicit permission
- Conda commands hang in PowerShell — use `python` directly
