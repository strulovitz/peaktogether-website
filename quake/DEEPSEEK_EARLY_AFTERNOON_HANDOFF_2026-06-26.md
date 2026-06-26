🌤️ DEEPSEEK EARLY AFTERNOON HANDOFF — June 26, 2026

## WHERE WE ARE (one-breath summary)

Building **Quake** (Game 3) — a first-person true-3D game that turns Newton's Principia
into a walkable concept-graph dungeon. 210/210 tests green. Content pipeline (Legs
1+2+3) complete. Runtime engine (Leg 4) **M-1 (infrastructure) + M0 (GPU proof) DONE**.
M1 (walk wireframe) **IN PROGRESS** — 1 of 5 M1 modules done.

## WHAT WE DID TODAY (June 26, 2026)

### Morning session (before restart)
1. **Re-oriented:** Read WORKFLOW + Commentaries. Legs 1+2+3 built (186 tests).
2. **Rescued Parent 4's missing infrastructure:** Parent 4's engine briefs assumed
   `contracts.py` existed — it didn't. Parent 4 delivered a full PART 1.5 with verbatim
   contracts.py, glguard.py, conftest.py. Saved, created files, verified.
3. **Installed moderngl 5.12.0 + pyglet 2.1.14** (not previously in the environment).
4. **Launched and integrated 4 children one-by-one:**

| # | Module | Milestone | Tests | Status |
|---|--------|-----------|-------|--------|
| M-1a | contracts.py | INFRA | — | ✅ Created (Parent 4 verbatim) |
| M-1b | glguard.py | INFRA | — | ✅ Created (HAVE_GL=True) |
| M-1c | conftest.py | INFRA | — | ✅ Created (skip_if_no_gl) |
| C1 | gfx_context.py | M0 | 6/6 | ✅ Window + GL context + caps |
| C2 | shaders.py | M0 | 4/4 | ✅ Wire/solid/blit GLSL programs |
| C3 | app.py (M0 stub) | M0 | 7/7 | ✅ Triangle + wireframe render loop |
| C4 | camera.py | M1 | 7/7 | ✅ Decoupled damped camera |

**M0 ACCEPTANCE GATE: PASSED** — window opens, shaders compile, triangle+line draw.
**M1 IN PROGRESS** — camera done, 4 more M1 modules remain.

### Critical lesson learned today
**When crafting child prompts: give ALL types inline.** Children cannot see our
codebase — they don't have GitHub, no internet, no contracts.py. The prompt must
include verbatim type definitions (the pydantic model fields, type aliases, constants)
so the child can write code that matches our contracts exactly. Otherwise the child
returns code with placeholder types that require rework.

## EXACT CURRENT STATE

### Files on disk (engine modules so far)
```
quake/
  contracts.py          # M-1a: re-exports raw_models + engine types
  glguard.py            # M-1b: HAVE_GL probe
  conftest.py           # M-1c: skip_if_no_gl marker
  gfx_context.py        # C1 M0: window + GL context + check_caps
  shaders.py            # C2 M0: GLSL wire/solid/blit programs
  app.py                # C3 M0: thin loop (M0 stub)
  camera.py             # C4 M1: critically-damped camera (PURE MATH)
  map/                  # Leg 1 (MAP): 9 modules, 94 tests
  bake/                 # Leg 2 (WALLS): 8 modules, 51 tests
  build/                # Leg 3 (ROOMS): 5 modules, 41 tests
  tests/                # 210 tests (all green)
    test_gfx_context.py (6)
    test_shaders.py     (4)
    test_app.py         (7)
    test_camera.py      (7)
    + all Leg 1+2+3 tests
  BIBLE/                # All scriptures including Parent 4 engine briefs
    QUAKE_LEG_4_ENGINE_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_4.md  ← THE SOURCE
```

### Test count: 210/210 green
- Leg 1 (MAP): 94
- Leg 2 (WALLS): 51
- Leg 3 (ROOMS): 41
- M-1 (infra): 0 (no tests needed)
- M0 (GPU): 17 (6+4+7)
- M1 (started): 7 (camera only)
- TOTAL: 210

### Parent lineage
- Parent 1: DEAD (context cliff June 25)
- Parent 2: DONE (Leg 1+2 frozen briefs)
- Parent 3: DONE (Leg 3 Room Maker v3 + Parent 3→4 handoff)
- Parent 4: DONE (Leg 4 engine frozen briefs — 13 children, M-1 through M7)

### Dependency-sorted build order (from Parent 4 PART 1)
```
M-1 INFRASTRUCTURE  ✅ contracts.py, glguard.py, conftest.py

M0  GPU PATH        ✅ 1.gfx_context, 2.shaders, 3.app M0 stub

M1  WALK WIREFRAME  ⏳ 4.camera ✅, 5.input_actions, 6.render_wire,
                       7.guidelines, 8.nav_collision (corridor)

M6  ENTER ROOM      ⬜ 9.assets, 10.render_room, 11.readmode
                       + nav_collision grows (room nav + door_at)
                       + app.py grows (Mode B + Read + teleport-snap)

M7  FULL LOOP       ⬜ 12.state, 13.gameplay
                       + app.py final (full wiring per §5.4)
```

## WHAT TO DO NEXT (exactly)

### Step 1 — Child 5: input_actions.py (M1)
From Parent 4's Brief 4. Pure core (EdgeTracker, build_actions, RawSample) + thin
shell (poll function). Needs Actions type from contracts.py.

**CRITICAL FOR PROMPT:** Include the full Actions pydantic model definition inline
so the child can write matching code. See Brief 4 in the engine document (BIBLE/
QUAKE_LEG_4_ENGINE_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_4.md).

Test names required:
  test_edge_fire_once
  test_edges_independent
  test_mover_owns_rotation
  test_aim_clamped
  test_scaling
  test_actions_frozen

### Step 2 — Child 6: render_wire.py (M1)
Mode A wireframe renderer. Brief 5. Pure core: build_wire_mesh, hex_to_rgb.
Shell: draw_graph. Needs Floorplan type.

### Step 3 — Child 7: guidelines.py (M1)
Guide-line selection + draw. Brief 6. Pure core: select_targets, _graph_distances.
Shell: draw_guidelines. Needs Floorplan, BuildConfig.

### Step 4 — Child 8: nav_collision.py (M1 corridor only)
Corridor navigation. Brief 7. Pure core: build_corridor_nav implementing NavQuery
protocol. Needs Floorplan, NavQuery, Ray.

### After each child:
1. Save child's code verbatim (camera.py → quake/camera.py, test → quake/tests/test_camera.py)
2. Fix imports to use contracts.py instead of any placeholder types
3. Fix test imports from `from quake.module import ...` to `from module import ...`
4. Run `python -m pytest tests/test_MODULE.py -v` then full `python -m pytest tests/ -q`
5. `git add -A; git commit -m "..."; git push`

### Child prompt format:
- ONE block (no internal ``` fences that break copy-paste)
- Include ALL types the child needs INLINE (pydantic models, aliases, constants)
- Include the full Brief spec from Parent 4
- Specify exact module path and test path
- Specify exact test names

## KNOWN INTEGRATION NOTES
- camera.py's look_at matrix convention: column-vector (V @ p). May need transpose
  at GL boundary when renderer uploads. Flagged with INTEGRATION comment.
- app.py M0 stub uses static geometry only. Will grow to full wiring in M1/M6/M7.
- moderngl uniform API uses `program["name"].value = ...` — confirmed working.
- pyglet window API: `pyglet.window.Window(width, height, caption, resizable, vsync)`
  — confirmed working in gfx_context.
- HAVE_GL = True on Nir's machine (moderngl + pyglet installed).
- Python: use `python` (base conda). Work dir: `C:\Users\nir_s\peaktogether-website\quake`
- GitHub: `github.com/strulovitz/peaktogether-website`, branch: master

## CONVENTIONS (never forget)
- 😊 Emojis are MANDATORY in all responses to Nir ✨🔥💪🚀❤️
- Packages installed: moderngl 5.12.0, pyglet 2.1.14, glcontext 3.0.0
- Tables DON'T survive copy-paste → fenced code blocks or lists for child transfers
- Push after every meaningful change
- NEVER write game code — architect designs, children build, DeepSeek integrates
- Nir knows NO code and NO math — explain things simply
- Parents are Claude Opus 4.8 via OpenRouter
- Never download files/models without explicit permission

(End of handoff — total 128 lines)
