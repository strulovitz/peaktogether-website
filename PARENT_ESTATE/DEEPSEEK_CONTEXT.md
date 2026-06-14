# 🧠 DEEPSEEK CONTEXT — DESCENT QED Engine (June 14, 2026)

> **READ ME FIRST on every fresh OpenCode startup.** 
> This file is your memory. The parent (Claude Opus 4.8 on OpenRouter) designs architecture.
> Children (fresh Claude chats) write code. YOU commit it, tune it, run it. Nir tests everything.

---

## 🔥 CURRENT STATUS (as of June 14, 2026 ~2:40 AM)

**8 of 11 modules built, flown, and verified.** The world tier is COMPLETE. The game is flyable via `python app.py`.

### Modules Built ✅

| # | Module | File(s) | Status |
|---|--------|---------|--------|
| 1 | content_parser | content_parser.py, test_parser.py | ✅ DONE |
| 2 | palette | palette.py, test_palette.py, show_colors.py | ✅ DONE |
| 3 | render | render.py, render_demo.py | ✅ DONE (+ patches) |
| 4 | robots | robots.py, robots_demo.py | ✅ DONE (+ patches) |
| 5 | corridor_builder | corridor_builder.py, corridor_demo.py | ✅ DONE |
| 6 | hub_builder | hub_builder.py, hub_demo.py | ✅ DONE |
| 7 | level_parser | level_parser.py, level_demo.py | ✅ DONE |
| 8 | app | app.py | ✅ DONE (integration proof) |

### Patches Applied 🔧
- render: `queue_wall()` + `flush_walls()` — shared translucent-wall sorting
- render: `quat_look_along()` — spawn orientation helper
- robots: `robot.position` — public bobbed world-center property
- robots: `draw_opaque()` / `draw_emissive()` split + `MIN_HOLO_SCALE` floor

### Remaining 🔜
| 9 | combat (read→identify→fire→match→kill) |
| 10 | arsenal (mathematician-missiles) |
| 11 | game_state (progression + win/lose) |

---

## 📂 CRITICAL FILE LOCATIONS

### Repo root and key files
- **Repo:** `C:\Users\nir_s\peaktogether-website`
- **Main game:** `app.py` — runs the assembled world
- **Demos:** `render_demo.py`, `robots_demo.py`, `corridor_demo.py`, `hub_demo.py`, `level_demo.py`

### Architecture / planning
- `PARENT_ESTATE/DESCENT_QED_PARENT_HANDOFF.md` — **THE LIFEBOAT** for the parent. Contains game design (LAW), engine canon, all 8 module summaries, remaining briefs, child-brief template.
- `PARENT_ESTATE/INTERFACES_v0.1.md` — original interface document v0.1
- `PARENT_ESTATE/briefs/` — all child briefs (#1-#8) and patch briefs
- `PARENT_ESTATE/reports/` — all completion reports
- `WORKFLOW.md` — session history log

### Corridor fixtures
- `corridors/01_dummy.txt` — alpha=red, beta=yellow, gamma=blue, delta=orange; 2 robots
- `corridors/02_dummy.txt` — one=red, two=blue, three=purple; 1 robot
- `corridors/03_dummy.txt` — left=yellow, right=blue, mix=green; 1 robot

### Level manifest
- `levels/intro.txt` — "Introduction to Placeholders", 3 corridors

### Fable's old code (reference only)
- `BIBLE/descent_qed_*.py` — Fable's original attempt (deprecated, new engine replaces it)
- `BIBLE/math_flyer.py` — harmonic series demo (NOT descent_qed)

---

## 🎮 THE GAME DESIGN (LAW)

DESCENT QED = 6-DOF flying game themed around mathematical proof.
- Couple in a spaceship flies corridors to RESCUE HOSTAGES at the end.
- ROBOTS block corridors. Must be DESTROYED to pass.
- Each robot requires a SPECIFIC MATHEMATICIAN'S TECHNIQUE.
- MISSILES = MATHEMATICIANS. Fire the correct missile to kill.
- READING = identifying which mathematician (NOT auto-selecting weapon).
- ENGINE IS MATHEMATICS-BLIND: matches opaque ids only, never interprets meaning.

---

## ⚙️ ENGINE CANON

### Canonical Frame Order
```
1. handle events (quit etc.)
2. ship.update(dt, pygame.key.get_pressed())
3. clear color+depth buffers
4. render.set_fog(start=40, end=140, color=palette.CLEAR_COLOR)
5. ship.apply_view()
6. hub.update(dt, ship.pos)
7. hub.draw_world(cr, cu, tc)       # QUEUE walls only
8. render.flush_walls(ship.pos)      # EXACTLY ONCE, far->near sort+draw
9. hub.draw_robots(cr, cu, tc)
10. hub.draw_labels(cr, cu, tc)
11. pygame.display.flip()
```

### CARDINAL TRAP
Walls are only QUEUED by draw_world. If `flush_walls` is NOT called exactly once per frame (slot 8, AFTER draw_world, BEFORE robots/labels), ALL WALLS VANISH SILENTLY — black screen, no error.

### Other Traps
- NEVER put mathtext texture ids into OpenGL display lists (they're dynamic, ids recycle)
- macOS may show black window (legacy GL) — render.py has a comment at set_mode
- Conda commands HANG in PowerShell — use `python` (base conda) directly

---

## 🔑 KEY SIGNATURES (the ones I keep looking up)

### render.py
- `render.init_gl((w, h))` — INITIALIZATION TAKES ONE TUPLE
- `render.queue_wall(quad, fill_rgb, edge_rgb, fill_alpha)`
- `render.flush_walls(camera_pos)` — sort+draw all queued walls
- `render.Ship(home_pos)` — .pos, .q, .update(dt, keys), .apply_view()
- `render.ship_right(q)`, `render.ship_up(q)` — for cr, cu
- `render.quat_look_along(dir, up=(0,1,0))` — verified, forward=-Z
- `render.TexCache()` — no args
- `render.set_fog(start=40, end=140, color=palette.CLEAR_COLOR)`

### palette.py (module-level constants)
- `palette.CLEAR_COLOR = (0.045, 0.055, 0.10)`
- `palette.WORLD_WALL_FILL = (0.16, 0.17, 0.20, 0.85)` RGBA
- `palette.WORLD_EDGE = (0.88, 0.90, 0.94)` RGB
- `palette.HOSTAGE_BLUE = (0.30, 0.65, 1.00)`
- `palette.BACKDROP_BASE_ALPHA = 0.55`

### content_parser.py
- `parse_corridor(path) -> CorridorData` — single fixture
- `discover_corridors(dir) -> list[CorridorData]`
- `CorridorData.title` (str), `.ledger` (ColorLedger), `.robots` (list[RobotData])
- `RobotData.name`, `.eye_color_key`, `.briefing_hint`, `.explain` dict

### level_parser.py
- `load_level(manifest_path) -> Level`
- `Level.title`, `Level.corridors` (list[CorridorData])
- `Level.__iter__` yields CorridorData → `build_hub(level)` works directly
- `discover_levels(folder="levels") -> list[str]` — returns paths, not parsed

### hub_builder.py
- `build_hub(level_data, atrium_center=(0,0,0)) -> HubGeometry`
- `hub.spawn_pose() -> ((x,y,z),(yaw,pitch))`
- `hub.door_poses() -> list[((x,y,z),(nx,ny,nz))]`
- `hub.draw_world(cr, cu, tc)` — QUEUE only
- `hub.draw_robots(cr, cu, tc)`, `hub.draw_labels(cr, cu, tc)`
- `hub.update(dt, ship_position)`, `hub.inside(point, margin=0.0)`

### corridor_builder.py
- `build_corridor(corridor_data, origin, direction) -> CorridorGeometry`
- `CorridorGeometry.entrance_pose() -> ((x,y,z),(nx,ny,nz))` — normal points BACK toward hub
- `CorridorGeometry.draw_world()`, `draw_robots()`, `draw_labels()`
- `TUBE_RADIUS = 6.0`

### robots.py
- `Robot(rdata, palette, station_pose, paint=None, size=1.0)`
- `robot.position` (property) — bobbed world-center
- `robot.base_pos` — un-bobbed station anchor
- `robot.play_defeat()`, `robot.is_defeated()`
- `robot.draw()`, `robot.draw_opaque()`, `robot.draw_emissive()`

---

## 🤝 THE WORKFLOW

```
Parent (Opus 4.8) writes BRIEF → Nir pastes to CHILD Claude
→ Child asks Nir to paste real files → writes code + demo + report
→ Nir pastes code to DeepSeek → DeepSeek saves verbatim, commits, pushes
→ DeepSeek runs demo/tests → reports bugs to Nir → Nir tells child
→ Child fixes → cycle repeats → Nir flies final, reports to parent
→ Parent writes next brief
```

---

## 🧪 HOW TO TEST

```powershell
# Run the assembled game
cd C:\Users\nir_s\peaktogether-website
python app.py

# Individual demos
python render_demo.py
python robots_demo.py
python corridor_demo.py
python hub_demo.py
python level_demo.py
python test_parser.py
python test_palette.py
```

Controls: WASD/RF = translate, arrows = pitch/yaw, Q/E = roll, Shift = boost, ESC = quit

---

## ⚠️ WHEN A CHILD ASKS QUESTIONS

Children will ask about real file contents (they can't access the internet).
You have access to all files in `C:\Users\nir_s\peaktogether-website`.
Provide exact signatures, constants, and short answers. Give GitHub links for whole files.

---

## 📝 WHAT NIR WANTS

- Save ALL child code VERBATIM — never modify it (unless child explicitly asks for a fix)
- Commit and push EVERYTHING to GitHub
- Find bugs and FLAG them — don't silently fix
- Remind Nir to paste completion reports to the parent
- RUN demos/tests when asked
- WAIT for all parts before committing (don't jump ahead!)
- Nir is the BOSS — ask before initiative
