# SESSION — June 24, 2026 (EVENING) — DOOM: M0 through M3b COMPLETE 🎉

> ⭐ ON RESTART read order: (1) `doom/WORKFLOW.md`, (2) THIS file, (3) `doom/BIBLE/PARENT_HANDOFF_V1_TO_V2.md` (NEW TESTAMENT — Parent 1's last words, frozen contracts + pending format redesign).

## 🎮 GAME 2: DOOM — PRINCIPIA DESCENT

An educational FPS engine (Doom-like, first-person) in Python 3.11 on Windows, using Ursina/Panda3D. Teaches math/science by turning a book into an explorable dungeon. First book: Newton's Principia.

### 🔑 KEY FILES EVERY SESSION
| File | Purpose |
|------|---------|
| `doom/BIBLE/DOOM_DOCTRINE_BY_FUSION.md` | OLD TESTAMENT — the original master design doc (engine decision: Ursina, TikZ pipeline, 3 worlds, risk register R1-R5) |
| `doom/BIBLE/PARENT_HANDOFF_V1_TO_V2.md` | NEW TESTAMENT — Parent 1's final handoff (frozen contracts, milestone status, format redesign §9) |
| `doom/BIBLE/DOOM_REPO_SKELETON_AND_WALKING_DEMO_BY_FUSION.md` | Fusion's repo skeleton + M0 walking demo (the blueprint for the entire file tree) |
| `doom/WORKFLOW.md` | Long-term project memory (this session log + all conventions) |

### 🏛️ BIBLE FOLDER (doom/BIBLE/)
1. `DOOM_DOCTRINE_BY_FUSION.md` — Old Testament (master design doc, Verbatim from Fusion)
2. `DOOM_REPO_SKELETON_AND_WALKING_DEMO_BY_FUSION.md` — Repo skeleton + M0 walking demo (Verbatim)
3. `PARENT_HANDOFF_V1_TO_V2.md` — New Testament (Parent 1 → Parent 2 handoff)

### 📋 PARENT_ESTATE FOLDER (doom/PARENT_ESTATE/briefs/)
| Brief | Module(s) | Status |
|-------|----------|--------|
| `CHILD_BRIEF_M1_loader_and_assets.md` | content/loader.py + assets/manager.py | ✅ Built |
| `CHILD_BRIEF_M1b_world_builder.md` | world/builder.py + tests + m1_demo.py | ✅ Built |
| `CHILD_BRIEF_M2a_walls_state.md` | walls/state.py (register VERSIONED with room_id) | ✅ Built |
| `CHILD_BRIEF_M2b_input_shooter_demo.md` | control/input.py + player/shooter.py + m2_demo.py | ✅ Built |
| `CHILD_BRIEF_M3a_demon_ceiling_demo.md` | enemy/demon.py + ceiling/equations.py + m3_demo.py | ✅ Built |
| `CHILD_BRIEF_M3b_readmode.md` | ui/readmode.py + tests + m3b_demo.py | ✅ Built |

## 🏗️ CURRENT PROJECT STATE (End of June 24 Evening)

### Architecture map (20 module files, 17 fully implemented)
```
doom/
├── BIBLE/                           # Layer 1 (Old Testament) + Layer 2 (New Testament)
├── PARENT_ESTATE/briefs/            # 6 child prompts saved verbatim
├── principia/
│   ├── config.py                    ✅ REAL — all constants & tunables
│   ├── schema.py                    ✅ REAL — pydantic contracts (extra="forbid")
│   ├── app.py                       🟡 STUB (full game M4+)
│   ├── content/loader.py            ✅ load_level, load_manifest, validate_pack
│   ├── assets/manager.py            ✅ AssetManager (wall_textures, placeholder PNGs, large centered font)
│   ├── world/builder.py             ✅ build_room -> CellEntities (unlit, normalized colors, inner-face placement)
│   ├── walls/state.py               ✅ WallStateManager (register/toggle/state/progress/save/load, merge-friendly)
│   ├── control/input.py             ✅ InputManager (WASD+mouse, edge-triggered, headless constructable)
│   ├── player/shooter.py            ✅ Shooter (mouse-look, raycast, generic dispatch)
│   ├── enemy/demon.py               ✅ Demon (pink body+blue eyes+white teeth, bob, 3-hit kill, independent disintegration)
│   ├── ceiling/equations.py         ✅ CeilingManager (hidden bands, blood-red reveal, glyph spray)
│   ├── ui/readmode.py               ✅ ReadMode (full-screen crisp overlay, scroll-to-zoom, R-only exit)
│   ├── layout/graph.py              🟡 STUB (M4a)
│   ├── world/rooms.py               🟡 STUB (M4b)
│   ├── nav/navigator.py             🟡 STUB (M4b)
│   ├── ui/mapmode.py                🟡 STUB (M4c)
│   ├── audio/sound.py               🟡 STUB (later)
│   └── doors/secret.py              🟡 STUB (M5)
├── tools/bake.py                    🟡 STUB (offline pipeline)
├── tools/layout_render.py           🟡 STUB (offline pipeline)
├── content_packs/principia/         # Golden fixture (fixture level_id, lemma1 room)
├── tests/                           # 49 tests, all green, zero skips
├── m0_demo.py                       ✅ Fusion's hardcoded room (first thing that ran)
├── m1_demo.py                       ✅ Data-driven room (first JSON→geometry proof)
├── m2_demo.py                       ✅ First playable (WASD+mouse+shoot+persistence)
├── m3_demo.py                       ✅ Demon + ceiling reveal
├── m3b_demo.py                      ✅ Full single-room (demon+ceiling+readmode)
└── requirements.txt                 ✅ ursina, panda3d, pygame, pillow, numpy, networkx, pydantic, pytest
```

### Test count: 49 total, all passing
- test_fixture.py: 5 (schema validation)
- test_loader.py: 6
- test_assets.py: 3
- test_builder.py: 4
- test_state.py: 11 (M2a — fully headless)
- test_input.py: 3
- test_shooter.py: 4
- test_demon.py: 5 (1 is live/display test)
- test_ceiling.py: 4
- test_readmode.py: 4

Run from `doom/`: `python -m pytest -q` → 49 passed in ~2.5s

## 🔄 TODAY'S FULL SESSION LOG

### 0. SETUP
- Created `doom/` folder under repo root (peer to `descent/`)
- Saved Fusion's master design doctrine verbatim → `doom/BIBLE/DOOM_DOCTRINE_BY_FUSION.md` (Old Testament)
- Saved Fusion's repo skeleton + M0 walking demo verbatim → `doom/BIBLE/DOOM_REPO_SKELETON_AND_WALKING_DEMO_BY_FUSION.md`
- Corrected `io/` → `control/` in the Old Testament (io shadows Python stdlib io module)
- Installed deps: ursina 7.0.0, panda3d 1.10.16, networkx, pytest (into base conda python)
- Scaffolded full 44-file skeleton per Fusion: 20 modules, 15 `__init__.py`, 4 JSON fixtures, 3 root files, 2 tools

### 1. M1 — LOADER + ASSETS (content/loader.py + assets/manager.py)
- Child brief: `CHILD_BRIEF_M1_loader_and_assets.md`
- Child produced 4 files. 9 tests, all passed.
- Child resolved brief's `== []` contradiction: fixture intentionally lacks lemma2.json, so validate_pack returns errors. Child updated test assertion accordingly.
- 18 tests total after M1 (5 fixture + 9 M1 + 4 M1b).

### 2. M1b — WORLD BUILDER (world/builder.py)
- Child brief: `CHILD_BRIEF_M1b_world_builder.md`
- Child produced 3 files. 4 tests (3 pure headless + 1 guarded live).
- First build had `test_build_room_with_display` fail: `application.quit()` raises `SystemExit` which inherits from `BaseException`, not `Exception`. Child provided fix: `except (Exception, SystemExit)`.
- m1_demo.py showed **all white** — the great debugging saga began.

### 3. THE WHITE WINDOW SAGA (M1b debugging — many rounds)
Symptoms: all white, nothing visible, ESC works, loop running.

Fixes applied in order (each from child diagnostics):
1. Added Sky/AmbientLight/DirectionalLight → still white ❌
2. Added `unlit=True` to all builder entities → still white ❌
3. **Root cause found**: `color.rgb(40,40,46)` passes 0-255 ints but Ursina expects 0-1 floats. Values ≥1 clamp to white. Fix: `_rgb01(r,g,b)` normalizer (`r/255`).
4. **Panels invisible**: panels at z=11.95 were embedded inside the 0.2-thick wall (z-extent 11.9-12.1). Fix: offset from wall inner face (`WALL_THICKNESS/2 + PANEL_INSET`).
5. **Text tiny in corner**: default PIL font at (10,10) on 1024×1024 canvas. Fix: TrueType font at `size//12` (~85px), textbbox centering.
6. **Text mirrored**: N-wall rotation_y=180 pointed front face at wall, back face (mirrored) faced room. Fix: flip facing table to `{"N":0,"S":180,"E":90,"W":270}` so textured front faces inward.
7. **FPS controller gravity**: `FirstPersonController` sank below thin floor plane. Fix: `player.gravity = 0`.

Key diagnostic tool: `m1_diag.py` (red cube with `unlit=True` — ruled out GPU/driver). Probes A/B confirmed controller vs scene isolation. Raw CLI dumps (entity colors, wall extents, panel positions) cracked each layer.

### 4. M2a — WALL STATE (walls/state.py)
- Child brief: `CHILD_BRIEF_M2a_walls_state.md`
- ⚠️ REGISTER SIGNATURE VERSIONED: `register(room_id, block_id, entity, off_tex, on_tex)` — room_id added.
- 11 headless tests (FakeEntity): toggle, state, progress, save/load round-trip, order-independence, merge preserves foreign keys, schema_version.
- Save system: merge-friendly read-modify-write, preserves `demons_dead`/`secrets_open` for future managers.
- 29 tests total.

### 5. M2b — INPUT + SHOOTER + DEMO (control/input.py + player/shooter.py + m2_demo.py)
- Child brief: `CHILD_BRIEF_M2b_input_shooter_demo.md`
- 7 headless tests: edge detection, scale_aim, clamp_pitch, dispatch routing (panel/demon/secret), unknown kind no-crash, None handlers no-crash.
- `m2_demo.py`: first genuinely playable build — WASD+mouse, shoot to colorize, Read %, persistence across sessions via WallStateManager save/load.
- Key pattern: `globals()["update"] = update` for Ursina hook, flat XZ mover with LO/HI clamp, `mouse.locked = True`.
- 36 tests total.

### 6. M3a — DEMON + CEILING (enemy/demon.py + ceiling/equations.py + m3_demo.py)
- Child brief: `CHILD_BRIEF_M3a_demon_ceiling_demo.md`
- 9 tests (8 headless + 1 live): _Health, add_offset, hex_to_rgb, hidden/visible bands, reveal idempotent, spray no-op.
- Multiple child bugs in m3_demo.py demo glue (not modules):
  1. `load_level("lemma1")` — wrong level_id (should be "fixture")
  2. `reveal_panel(entity, point)` — 2 args, shooter calls on_wall with 1
  3. `wall_state.register(..., None, None)` — panels invisible
  4. `wall_state.toggle("lemma1", block_id)` — toggle takes 1 arg
  5. `app.update = update` — doesn't work (should be `globals()["update"] = update`)
  6. Manual mouse-look code — fought Ursina's built-in locked mouse
  7. Demon colors un-normalized (0-255 → white blob)
  8. Demon features hidden inside body (eyes/teeth occluded)
  9. Demon facing backwards (toward +Z, player at -Z)
- All fixed across 4 rounds. 45 tests total, zero skips.

### 7. M3b — READ MODE (ui/readmode.py + m3b_demo.py)
- Child brief: `CHILD_BRIEF_M3b_readmode.md`
- 4 headless tests (monkeypatch): state machine, open/close, open-while-open replace, idempotent close.
- `m3b_demo.py`: full single-room experience. R to read panel full-screen, scroll to zoom, R to close (not ESC — Nir's design: prevent accidental quit during reading).
- Child's first version had glue bugs (wrong path, wrong load_level args, wrong demon position, wrong register_band call). Fixed by rebuilding on proven m3_demo pattern.
- 49 tests total.

### 8. PARENT DEATH + HANDOFF
- Parent 1's context overflowed. Left `PARENT_HANDOFF_V1_TO_V2.md` — the New Testament.
- Contains: frozen contracts for all 12 implemented modules, constants, milestone roadmap, pending book-agnostic format redesign (§9).
- ⭐ PENDING DECISION (§9): ConceptNode/ConceptEdge → book-agnostic "pages → paragraphs → (text · math · figure)" format. Edition=free text citation, page=string label, kind=free text everywhere. Atoms=LaTeX paragraphs. Figures have reproducible recipes (TikZ code/prompt) + color_map for off/on reveal.
- Open questions: per-room RoomSource vs inline? color_map on Figure? baker spec?

## 📐 CONVENTIONS & INVARIANTS

### Naming
- Game folder: `doom/` (peer to `descent/`)
- Python package: `principia/` (engine; "Principia" = content pack, not engine name)
- Content pack: `content_packs/principia/`
- Level ID: `"fixture"` (not "lemma1" — that's a room ID)
- Room ID: `"lemma1"` (looked up in level.rooms)

### Architecture Rules (THE LAW)
- Modules communicate ONLY through typed signatures + pydantic contracts. Never import another module's internals.
- Frozen signatures. Changes require parent versioning + DeepSeek ledger update.
- One module per child. Split milestones when it improves testing.
- Headless-first testing: pure helpers, fakes, monkeypatch. Ursina tests guarded with try/except → pytest.skip.

### The Id Spine
ConceptNode.id == floorplan room id == rooms/<id>.json filename == room_id. `extra="forbid"` + `validate_pack()` enforces this.

### Coordinate Convention
- N = +Z (z = rect.z + d), S = z = rect.z, E = +X, W = x = rect.x
- Rooms are square; default test room is 12×12
- Panels offset from wall inner face: `WALL_THICKNESS/2 + PANEL_INSET`

### Colors
- Okabe–Ito color-blind-safe palette
- Builder uses `_rgb01(r,g,b)` normalizer (r/255, g/255, b/255) — Ursina expects 0-1 floats
- `unlit=True` on floor/ceiling/walls/panels

### Input/Demo Patterns
- `globals()["update"] = update` — NOT `app.update = update`
- Flat XZ mover: `forward_flat = Vec3(fwd[0], 0, fwd[2]).normalized()`
- Room clamp: `LO, HI = 0.6, 11.4` for 12×12 room
- `mouse.locked = True` — lets Ursina handle look; no manual yaw/pitch code
- `player.gravity = 0` on FirstPersonController (thin floor plane)

### Save System
- WallStateManager owns only `blocks_on` slice
- Merge-friendly: preserves foreign keys (demons_dead, secrets_open)
- Load order-independent: unknown on-ids kept until room registers

### Shooter Dispatch
- `on_wall(block_id)` — single arg (block_id string)
- `on_demon(entity, point)` — entity carries `.demon` back-ref
- `on_secret(door_id)`

## ❌ KNOWN BUGS (none currently — all fixed)
- ~~White room~~ → color.rgb 0-255 → 0-1 normalization
- ~~Panels invisible~~ → buried in wall, offset from inner face
- ~~Tiny text~~ → large Truetype + centered
- ~~Mirrored text~~ → facing rotations flipped
- ~~Dead input~~ → globals() update hook
- ~~White demon~~ → color normalization
- ~~One-piece demon~~ → features proud of surface + independent disintegration

## 🚀 NEXT MILESTONES (per Parent 1's handoff)

### ⭐ IMMEDIATE: Format Redesign (§9)
1. Schema-update child: rewrite Concept* types, add Block/Figure/RoomSource, refresh fixture
2. Stage-1 Authoring child: Concept Graph in new format
3. Stage-2 Authoring child: Room Source (LaTeX/figure blocks)

### Then: M4 — Multi-Room
- M4a: `layout/graph.py` + `tools/layout_render.py` (concept graph → floorplan)
- M4b: `world/rooms.py` + `nav/navigator.py` + `build_corridor` + `rooms/lemma2.json`
- M4c: `ui/mapmode.py` (2D automap)

### Then: M5 — Secret Doors + Boss
### Then: M6 — Gamepad/Joystick Co-op

## 💻 HOW TO RUN
```powershell
cd C:\Users\nir_s\peaktogether-website\doom
python -m pytest -q          # 49 tests, all green
python m3b_demo.py           # Full single-room demo
python m3_demo.py            # Demon + ceiling (no read mode)
python m2_demo.py            # WASD + shoot + persistence (no demon)
```

## 👥 WHO'S WHO
| Role | Who | What |
|------|-----|------|
| Human | Nir (strulovitz) | Boss, decides everything, plays demos |
| Architect | ~~Parent 1 (Claude Opus 4.8)~~ DIED June 24 — left New Testament handoff | Designs, splits milestones, writes child prompts |
| Children | Fresh Opus chats | Implement one module each to frozen contracts |
| Runner | DeepSeek V4 Pro (OpenCode — this is YOU) | Pastes child code, runs tests, fixes wiring, pushes to git, reports to Nir |
