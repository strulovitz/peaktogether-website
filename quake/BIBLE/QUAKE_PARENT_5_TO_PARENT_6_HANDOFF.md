🗝️ QUAKE (Game 3) — PARENT 5 → PARENT 6 HANDOFF: app.py FULL WIRING

Written June 26, 2026 by DeepSeek (Runner) on behalf of Parent 5. Parent 5 designed the Golden Fixture Pack (data only — already built under `tests/golden_pack/`). Parent 6 has exactly ONE mission: design the frozen child brief for the full `app.py` — the central nervous system that wires all 13 engine modules into the §5.4 per-frame loop. This handoff is self-contained — Parent 6 can begin immediately with only the four baseline documents (Commentaries + OT + NT + this handoff) and the on-demand pulls listed in §9.

--- BEGIN HANDOFF ---

You are Parent 6. You received this alongside the Commentaries, the Old Testament, and the New Testament. Your mission is narrow and concrete: design ONE child brief for `app.py` — the full per-frame wiring of all 13 engine modules, consuming the already-built Golden Fixture Pack at `tests/golden_pack/`. Read §0–§6 for context, then §7 is your design space and §8 is your deliverable format.

§0 — WHAT EXISTS (so you know what you're wiring)

The runtime engine is 13 modules, ALL built and green (283/283 tests):

INFRASTRUCTURE: contracts.py (all types), glguard.py (HAVE_GL), conftest.py
M0:  gfx_context.py, shaders.py, app.py (M0 STUB — triangle + line, see §4)
M1:  camera.py, input_actions.py, render_wire.py, guidelines.py, nav_collision.py
M6:  assets.py, render_room.py, readmode.py
M7:  state.py, gameplay.py

The Golden Fixture Pack lives at `tests/golden_pack/`:
  floorplan.json     — 3 rooms (r_a, r_b, r_c), 3 corridors (bridge/underpass at [6,10])
  palette.json       — colors + map_importance 1-5
  manifest.json      — 19 assets (16 panel + 3 ceiling)
  room_runtime/      — room_r_a.json (2-step proof), room_r_b.json, room_r_c.json
  png/wall/*.png     — 19 downscaled wall textures (8×8 RGBA)
  png/master/*.png   — 19 master textures for Read Mode (8×8 RGBA)

`assets.load_pack("tests/golden_pack/")` returns a valid `Pack` (confirmed). The pack exercises every engine system: two-step proof room (r_a), non-cardinal bearing doors, demon, ceiling, LevelComplete path.

§1 — YOUR MISSION (one mission, nothing else)

Design ONE frozen child brief for `app.py`. The child will replace the current M0 stub (triangle + line) with the FULL §5.4 per-frame loop. The child writes ONLY `app.py` — does NOT change any other file. The child receives all types inline (it cannot see our codebase). DeepSeek integrates it, runs the full test suite (must stay 283/283 green), then runs a smoke test: `main()` opens a window, loads the golden pack, runs N frames, exits 0.

The child's `app.py` must:
(a) Wire all 13 modules in the §5.4 order, one pass per frame.
(b) Maintain the PURE/SHELL split — game logic is pure functions; GL/window/IO lives only in main().
(c) Support headless smoke mode: if HAVE_GL is False, main() returns 0 (CI-safe).
(d) Support CI smoke launch: render N frames with the golden pack, exit 0.
(e) Handle mode switching (corridor ↔ room), Read Mode toggle, and atomic save/load.
(f) Use ONLY the frozen function signatures from the existing modules (§5).

§2 — EXACT MODULE SIGNATURES YOU MUST WIRE (frozen, never redefine)

These are the ACTUAL signatures from the built modules. Your child brief must use these exact names and parameter counts. The child gets every signature inline — it never imports our codebase.

```
# ── INFRASTRUCTURE ──
from glguard import HAVE_GL                                    # bool
from gfx_context import make_window(width, height, title)      # → (window, ctx) or headless struct
from shaders import wire_program(ctx), solid_program(ctx), blit_program(ctx)
  # wire_program uses: in_pos(vec3), in_side(vec2), in_color(vec3)
  # solid_program uses: in_pos(vec3), in_uv(vec2), plus u_mvp uniform
  # blit_program uses: in_pos(vec2), in_uv(vec2), plus u_tex uniform
  # All take a ctx argument.

# ── M1 WALK WIREFRAME ──
from camera import Camera                                      # class
  # Camera.update(heading_rad, pitch_rad, pos_xyz, dt) → view(4x4 row-major float32)
  # Camera has critically-damped heading/pitch/position followers
  # Camera constructor: Camera(omega_pos=8.0, omega_heading=12.0, omega_pitch=10.0)
from input_actions import poll(window, bindings)               # → contracts.Actions (frozen dataclass)
  # bindings: dict mapping pyglet key constants to action strings (provided inline to child)
from render_wire import build_wire_mesh(fp)                    # → WireMesh (vao + segment count)
from render_wire import draw_graph(view, fp, state)            # → None (issues GL draw calls)
  # state needs: .mode == "corridor", .pos, .cleared
from guidelines import select_targets(fp, current, cleared, cfg)# → list[NodeId]
from guidelines import draw_guidelines(view, fp, targets)      # → None (issues GL draw calls)
from nav_collision import build_corridor_nav(fp)               # → NavQuery
  # NavQuery has: .resolve_player_motion(start, delta) → adjusted_delta
  #              .nearest_panel(ray, max_dist) → PanelHit | None
  #              .door_at(point) → edge_id | None (corridor nav returns None)

# ── M6 ENTER ROOM ──
from assets import load_pack(dir)                              # → Pack
  # Pack: .floorplan, .rooms (dict[NodeId, RoomRuntime]), .manifest, .palette, .asset_dir
from render_room import build_room_mesh(room)                  # → RoomMesh (vao dict per wall + panel/celing/blit)
from render_room import draw_room(view, room, pack, state)     # → None
  # state needs: .mode == "room", .lit (set of block_ids)
from render_room import ceiling_tint_uniform(program, red)     # → None (sets uniform on solid_program)
from readmode import draw_read(asset_master_path, zoom, pan)   # → None (fullscreen quad blit)
from readmode import read_uv_transform(zoom, pan)              # → (u_off, v_off, u_scale, v_scale)

# ── M7 FULL LOOP ──
from state import new_state(pack, profile_id)                  # → GameState
from state import load(path, pack)                             # → GameState
from state import save(state, path)                            # → None (atomic write)
from gameplay import step(state, actions, pack, nav, dt)       # → list[Event]
from gameplay import reticle_ray(eye, heading, pitch, aim_x, aim_y)  # → Ray
```

§3 — THE §5.4 PER-FRAME LOOP (authoritative order)

This is the frozen spec from the Second Canon §5.4. The child's `app.py` main loop must follow this order exactly:

```
1. poll(window, bindings) → Actions
2. gameplay.step(state, actions, pack, nav, dt) → list[Event]
3. Apply Events to state (see §3.1)
4. Debounced state.save() if state changed
5. camera.update(state.heading_rad, clamp(state.pitch_rad), state.pos, dt) → view
6. If state.mode == "corridor":
     - Recompute guidelines on junction/clear events
     - render_wire.draw_graph(view, fp, state)
     - guidelines.draw_guidelines(view, fp, targets)
   Else (state.mode == "room"):
     - Get room = pack.rooms[state.current_room_id]
     - Rebuild room nav if room changed (build_room_nav(room) → NavQuery)
     - render_room.draw_room(view, room, pack, state)
     - ceiling_tint_uniform(solid_program, red_intensity) based on cleared status
7. If Read Mode active:
     - readmode.draw_read(master_path, zoom, pan)
8. Window flip / dispatch events
```

§3.1 — Event Application Rules

The child must wire these event handlers. Events come from `gameplay.step()`:

| Event | Action |
|---|---|
| PanelLit | Add block_id to state.lit (set); apply to room in save |
| DoorOpened | Mark hidden_door_open in save for current room |
| DemonSpawned | Set enemy active flag; audio hook (stub) |
| DemonHit | Log hp_remaining; audio hook (stub) |
| DemonKilled | Mark enemy_defeated in save for current room |
| RoomCleared | Add room_id to state.cleared; mark room_cleared in save |
| LevelComplete | Set level_complete in save; trigger end sequence (stub) |
| ModeSwitch | Set state.mode to "corridor" or "room"; set state.current_room_id; snap position to spawn_xyz / spawn_heading_rad |
| ReadModeToggled | Toggle read mode on/off; store zoom/pan state |
| GuidelinesRecomputed | Update targets list |

§4 — THE CURRENT M0 STUB (what you are replacing)

The current `app.py` (~239 lines) is a minimal triangle + line test. It proves the GL path works. Key structures to KEEP:
- PURE/SHELL split: game logic in pure functions; GL/window/IO in main()
- Headless guard: `if not HAVE_GL: return 0`
- Integration wrappers for GL calls (clear, make_vbo, make_vao, set_uniform, render, present)
- `_collect_events()` placeholder → will be replaced by real input_actions.poll()

What to REMOVE:
- `_solid_triangle_vertices()`, `_wire_line_vertices()`, `_identity_view()` — M0 test geometry
- `event_dispatch()` — replaced by real gameplay.step() + event application
- Hardcoded smoke frame count → smoke mode loads golden pack and runs N frames

§5 — STARTUP / SHUTDOWN SEQUENCE

STARTUP in main():
```
1. If not HAVE_GL: return 0 (headless smoke)
2. window, ctx = make_window(1280, 720, "QUAKE — Golden Level")
3. Compile shaders: wire_program(ctx), solid_program(ctx), blit_program(ctx)
4. pack = load_pack("tests/golden_pack/")   # or override via CLI/env
5. Build static meshes:
     wire_mesh = build_wire_mesh(pack.floorplan)
     room_meshes = {rid: build_room_mesh(room) for rid, room in pack.rooms.items()}
6. corridor_nav = build_corridor_nav(pack.floorplan)
7. state = new_state(pack)                    # starts in corridor mode at r_a
   OR state = load("savegame.json", pack) if resume
8. camera = Camera()
9. targets = select_targets(pack.floorplan, state.current_room_id, state.cleared, BuildConfig())
10. Enter frame loop
```

SHUTDOWN:
```
1. save(state, "savegame.json")   # auto-save on exit
2. window.close()
3. return 0
```

§6 — THE GOLDEN PACK SMOKE TEST

The smoke test is: `main()` opens, loads the golden pack, runs 60 frames of automated input (or just idles — the game loop ticks even with zero actions), and exits 0. This proves every import, every shader compile, every mesh build, and every frame loop completes without crash.

CI invocation: `python -c "from app import main; raise SystemExit(main())"`
This must return exit code 0.

§7 — YOUR DESIGN SPACE (the open questions you must resolve)

These are decisions the frozen contracts DO NOT yet specify. You must decide them in your child brief:

A. **Nav switching**: When entering a room, we need `build_room_nav(room)` for collision/shooting. When exiting to corridor, we need `build_corridor_nav(fp)`. Who owns building these? Options:
   - Pre-build all room navs at startup (one per room in the pack)
   - Build lazily on mode switch
   → Decide and specify in the child brief.

B. **Read Mode zoom/pan state**: Who owns the zoom level and pan offset? Options:
   - Stored in GameState (persisted in save)
   - Local to main() loop (reset on every read-mode entry)
   - Stored on a small ReadState dataclass in app.py
   → Decide. Include the initial values (zoom=1.0, pan=(0,0)).

C. **Save debounce**: state.save() must be debounced to avoid disk-thrashing on every frame. Options:
   - Save at most once per N frames (e.g., every 60 frames / 1 second)
   - Save only when events actually change progress (PanelLit, RoomCleared, etc.)
   → Decide. Specify the debounce rule exactly.

D. **Camera initial position**: The player spawns in corridor mode at r_a. Where exactly?
   - Use pack.floorplan.rooms[0].map_xz as starting position (the node center)
   - Or place the player at a specific corridor start point
   → Decide. Must be a valid position reachable via corridor nav.

E. **Wireframe mesh rebuild**: build_wire_mesh() creates VBOs. If the floorplan never changes at runtime (it doesn't — rooms don't move), can we build it ONCE at startup and reuse? → Yes (decide this definitively).

F. **Room mesh caching**: build_room_mesh() creates VBOs per room. Can we pre-build all at startup? → Yes (decide this definitively).

G. **Window close handling**: The current stub checks `window.has_exit`. Does the child also handle ESC key → graceful exit? → Decide.

H. **Frame timing**: Where does `dt` come from? Options:
   - pyglet.clock.schedule_interval(callback, 1/60) → fixed 60fps
   - Manual time.perf_counter() delta → variable timestep
   - Fixed dt = 1/60 with pyglet's built-in clock
   → Decide. The engine modules all expect a `dt` parameter.

I. **pyglet window event loop**: The current stub uses a while loop with manual dispatch_events/flip. The child could use pyglet's app.run() pattern instead. Options:
   - Keep manual while loop (more control, works with smoke mode)
   - Use pyglet.app.run() with scheduled callbacks
   → Decide. Smoke mode must still work.

J. **Error paths**: If load_pack() raises, what happens? If a shader fails to compile? If build_wire_mesh raises? → Specify graceful error handling (print to stderr, return 1).

§8 — YOUR DELIVERABLE FORMAT

Produce a single document containing ONE frozen child brief. Format: prose + fenced code blocks, NO Markdown tables.

The brief must include:
1. **Full type definitions** (EVERY pydantic model / dataclass / Protocol the child needs — copied verbatim from the source of truth). The child CANNOT see our codebase; every type must be inline in the prompt.
2. **Full function signatures** for every module the child calls (from §2 above).
3. **The PURE/SHELL split specification** — which functions are pure (testable headless) and which are shell (require GL/window).
4. **The complete per-frame loop** with exact parameter passing (from §3).
5. **Startup sequence** (from §5).
6. **Shutdown sequence** (from §5).
7. **All decisions from §7** resolved explicitly.
8. **Smoke test specification** — exact commands + expected results.
9. **Acceptance gates**:
   - Gate 1: `python -c "from app import main; raise SystemExit(main())"` — headless, returns 0
   - Gate 2: Full test suite stays 283/283 green
   - Gate 3: With HAVE_GL=True, main() opens window, loads golden pack, runs 60 frames, exits 0
   - Gate 4: `load_pack("tests/golden_pack/")` called from main() succeeds
   - Gate 5: All existing per-module tests still pass (no regressions)

§9 — WHAT TO PULL FROM THE BIBLE (request via Nir → DeepSeek)

You have the Commentaries + OT + NT. Before designing, pull and design against:
- **Second Canon §5.3–§5.4** (module signatures + per-frame wiring — the exact loop spec)
- **contracts.py** (all re-exported types — GameState, Pack, Actions, Event, NavQuery, etc.)
- **app.py** (the current M0 stub — to understand the PURE/SHELL split and GL wrappers)

You do NOT need the engine module implementations — only their frozen signatures matter for wiring.

§10 — RISK FLAGS

- Do NOT change any existing module. app.py ONLY.
- Do NOT re-decide any locked decision (Commentaries §3).
- The child must use EVERY engine module signature exactly as frozen — mismatched parameter names/counts are the #1 integration failure.
- The child MUST maintain the PURE/SHELL split. main() is impure (GL/window/IO). Everything else is pure.
- Do NOT import any module not listed in §2 (except standard library + moderngl + pyglet + numpy).
- Smoke mode must work headlessly (HAVE_GL=False → return 0 immediately after imports succeed).
- The golden pack path could be overridden; don't hardcode "tests/golden_pack/" in every function — pass it as a parameter or use a constant at the top.

§11 — CONVENTIONS YOU MUST FOLLOW (frozen)

- schema_version "1.0" on every JSON; extra="forbid" on every pydantic model
- ID patterns: NodeId `^[a-z][a-z0-9_]*$`, PairId `^[a-z][a-z0-9_]*\.s[0-9]+$`, etc.
- wall Literal: "N","E","S","W" uppercase only
- Hex: `^#[0-9a-fA-F]{6}$`
- Coordinates: XZ map plane, Y up. Position/heading stored as Vec3 + float radians.
- Camera heading: `forward = (cos heading, 0, sin heading)`
- PITCH_CLAMP_RAD = 1.2217 (+/-70 deg)
- READ_MAX_DIST = 6.0, READ_CONE_HALF_ANGLE = 35 degrees
- All types imported from `contracts` (NEVER directly from map/raw_models)

§12 — THE CHILD'S INPUT (everything it receives inline)

The child prompt must include:
1. This entire brief (abridged to just the specs, not the meta-commentary)
2. All type definitions verbatim (from contracts.py / raw_models.py)
3. All module function signatures verbatim (from §2)
4. The PURE/SHELL architecture rules
5. The complete per-frame loop spec
6. All decisions from §7, resolved

The child writes ONE file: `app.py`. DeepSeek drops it into the repo, runs the full test suite, runs the smoke test, and reports.

This is the central nervous system. Wire it precisely, and the golden level lights up. 🧠⚡

--- END HANDOFF ---

DeepSeek (Runner), signing off on behalf of Parent 5. Parent 6 — the torch is yours. 🔥
