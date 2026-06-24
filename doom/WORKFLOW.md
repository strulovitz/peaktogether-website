# DOOM (Principia Descent) — Project WORKFLOW

> ⭐ ON STARTUP: read this file FIRST. Then the latest SESSION file in `doom/PARENT_ESTATE/`.

## Quick Start
```powershell
cd C:\Users\nir_s\peaktogether-website\doom
python -m pytest -q          # 49 tests, all green
python m3b_demo.py           # Full single-room demo (demon + read mode)
```

## Project Identity
**Game 2** of the Peak Together platform. An educational FPS (Doom-like) in Python 3.11, using Ursina/Panda3D. Teaches math/science by turning a book into a walkable dungeon. First book: Newton's Principia.

Repo folder: `doom/` (peer to `descent/`). Python package: `principia/`. Content pack: `content_packs/principia/`.

## The 3 Worlds (Architecture's Spine)
| World | When | Produces |
|-------|------|----------|
| CONTENT | Design time (LLM children) | concept_graph.json, per-room LaTeX/TikZ source |
| BUILD | Design time (deterministic tools) | floorplan.json, baked .png panels |
| RUNTIME | Player's machine | Loads baked JSON+PNG only. Never sees Wikipedia/LaTeX/LLM. |

## Who's Who
| Role | Who | What |
|------|-----|------|
| Human | Nir (strulovitz) | Boss, decides, plays demos, carries bible between chats |
| Architect | Parent (Claude Opus 4.8) | Designs, splits milestones, writes child prompts. Parent 1 DIED June 24 — left New Testament handoff |
| Children | Fresh Opus chats | Implement one module each to frozen contracts, then discarded |
| Runner | DeepSeek V4 Pro (OpenCode) | Pastes child code, runs tests, fixes wiring, pushes to git, reports |

## Key Files to Read Every Session
1. **THIS FILE** (`doom/WORKFLOW.md`)
2. Latest SESSION file: `doom/PARENT_ESTATE/SESSION_*.md` (sort by date)
3. `doom/BIBLE/PARENT_HANDOFF_V1_TO_V2.md` — New Testament (frozen contracts, milestone status)
4. `doom/BIBLE/DOOM_DOCTRINE_BY_FUSION.md` — Old Testament (original master design)
5. `doom/PARENT_ESTATE/SESSION_2026-06-24_EVENING.md` — Today's full session log

## Architecture Map
```
doom/
├── BIBLE/                           # Old + New Testament (verbatim doctrine docs)
├── PARENT_ESTATE/                    # Briefs + Session logs
│   ├── briefs/                       # 6 child prompts (M1 through M3b)
│   └── SESSION_*.md                  # Per-session memory
├── principia/                        # Engine (20 modules)
│   ├── config.py                     ✅ Constants & tunables
│   ├── schema.py                     ✅ Pydantic contracts
│   ├── content/loader.py             ✅ Load + validate packs
│   ├── assets/manager.py             ✅ Textures (PNG or placeholders)
│   ├── world/builder.py              ✅ build_room → Ursina entities
│   ├── walls/state.py                ✅ Off/on state + save/load
│   ├── control/input.py              ✅ WASD + mouse input
│   ├── player/shooter.py             ✅ Raycast shooter
│   ├── enemy/demon.py                ✅ Sphere-circle demon
│   ├── ceiling/equations.py          ✅ Blood-red equation reveal
│   ├── ui/readmode.py                ✅ Full-screen panel overlay
│   └── layout/, world/rooms/, nav/, ui/mapmode/, doors/, audio/ 🟡 STUBS
├── content_packs/principia/          # Golden fixture
├── tests/                            # 49 tests, all green
├── m0_demo.py … m3b_demo.py          # Throwaway demos (latest = best)
└── requirements.txt
```

## Module Status (M0–M3b COMPLETE, 49 tests)
| Milestone | Modules | Tests |
|-----------|---------|-------|
| M0 | Hardcoded room demo | - |
| M1/M1b | loader, assets, builder | 18 |
| M2a/M2b | walls/state, control/input, player/shooter | +18 = 36 |
| M3a/M3b | enemy/demon, ceiling/equations, ui/readmode | +13 = 49 |
| M4 | layout/graph, world/rooms, nav/navigator, mapmode | PENDING |
| M5 | doors/secret, boss | PENDING |
| M6 | Gamepad/joystick, co-op | PENDING |

## Frozen Architecture Rules (THE LAW)
1. Modules communicate ONLY through typed signatures + pydantic contracts. Never import another module's internals.
2. Frozen signatures. Changes require parent versioning + DeepSeek ledger update.
3. One module per child. Split milestones when it improves testing.
4. Headless-first testing: pure helpers, fakes, monkeypatch. Ursina tests guarded with try/except → pytest.skip.
5. `from __future__ import annotations` in every file. Type hints mandatory.

## Critical Conventions

### Coordinates
- N = +Z, S = z = rect.z, E = +X, W = x = rect.x
- Default room: 12×12, ceiling 3.0, eye 1.6
- Panel inset from wall INNER face: `WALL_THICKNESS/2 + PANEL_INSET`

### Colors
- Ursina expects 0-1 floats: use `_rgb01(r,g,b)` = `color.rgba(r/255, g/255, b/255, 1)`
- `unlit=True` on all builder entities
- Okabe–Ito color-blind-safe palette

### Input/Demo Patterns (copy from m3_demo.py)
- `globals()["update"] = update` — NOT `app.update = update`
- `mouse.locked = True` — let Ursina handle look (no manual yaw/pitch)
- Flat XZ mover: zero y, normalize, clamp to [0.6, 11.4]
- `player.gravity = 0` with FirstPersonController
- `load_level("content_packs/principia", "fixture")` — level_id is "fixture", room match by "lemma1"

### Shooter Dispatch
- `on_wall(block_id)` — single arg string
- `on_demon(entity, point)` — `entity.demon` back-ref for `.hit(point)`
- `on_secret(door_id)`

### Id Spine
`ConceptNode.id == floorplan room id == rooms/<id>.json filename == room_id`

## Signature Versions (Ledger)
| Module | Change | When |
|--------|--------|------|
| `WallStateManager.register` | Added `room_id` as first param | M2a |
| `Demon.__init__` | Added optional `parent=None` | M3a |
| Master doc `io/` → `control/` | Renamed package (io shadows stdlib) | June 23 |

## PENDING DECISION (§9 of New Testament)
Book-agnostic format redesign: ConceptNode/ConceptEdge → pages→paragraphs→(text·math·figure). Edition=free text citation, page=string label, kind=free text everywhere. Blocks=LaTeX paragraphs. Figures=TikZ/prompt recipes with color_map.

Next steps per Parent 1: (1) schema-update child, (2) Stage-1 authoring child, (3) Stage-2 authoring child, then resume M4a.

## Git Conventions
- `doom/` is the game root; NEVER put game files in repo root
- BIBLE files: saved VERBATIM, WORD-FOR-WORD, AS-IS from Fusion/Opus
- Child briefs: saved to `doom/PARENT_ESTATE/briefs/`
- Session logs: `doom/PARENT_ESTATE/SESSION_YYYY-MM-DD_{MORNING|AFTERNOON|EVENING|NIGHT}.md`
- Commit after every meaningful change. Push immediately.
- Clean up temp/probe/diagnostic files after debugging

## Known Bugs / Gotchas
- `color.rgb(0-255)` renders WHITE on Ursina (clamps to 1.0). Always normalize.
- `application.quit()` raises `SystemExit` (BaseException). Catch with `except (Exception, SystemExit)`.
- `FirstPersonController` sinks through thin planes (gravity). Use `player.gravity = 0`.
- `app.update = update` doesn't work. Use `globals()["update"] = update`.
- `load_level("lemma1")` crashes — level_id is "fixture", room_id is "lemma1".
- `wall_state.toggle(room_id, block_id)` (2 args) → `toggle(block_id)` (1 arg).
- Shooter `on_wall(block_id)` takes 1 arg (the string), not the entity.
