# 🧠 SESSION CONTEXT — June 15, 2026 EVENING (end of day, 3rd & 4th parents, Briefs #10-#15)

> **Project:** DESCENT QED engine
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`

---

## 🚨 READ THESE FIRST (4th/5th parent)

1. **`PARENT_ESTATE/PARENT_HANDOFF_V3.md`** — THE LAW. Full game design, all modules, data objects, corridor format, frame order.
2. **`PARENT_ESTATE/SESSION_2026-06-15_MORNING.md`** — morning session (3rd parent start, initial state)
3. **`PARENT_ESTATE/SESSION_2026-06-15_AFTERNOON.md`** — afternoon session (Briefs #10-#13, hostages, game state)
4. **THIS FILE** — evening session (Brief #15 cockpit, bug fixes, final state)

---

## 📦 WHAT EXISTED AT START OF DAY (morning)

**World Tier** — 8 modules built and flown:
content_parser, palette, render, robots, corridor_builder, hub_builder, level_parser, app

**Gameplay Tier** — Briefs #9 (Combat) and #11 (Understanding Mode) built.
Hardcoded ARSENAL, `[`/`]` weapon cycling, no hostages, no game state, no cockpit.

---

## 🎮 WHAT WE BUILT TODAY (chronological)

### 3rd PARENT (Opus 4.8) — Morning/Early Afternoon

**Documents created:**
- `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — comprehensive handoff for 3rd parent
- `docs/CONTENT_AUTHORING.md` — reusable content-authoring child brief (Wikipedia→corridors)

**Brief #10 — ARSENAL/WEAPONS** (built by child, merged by DeepSeek)
- Deleted hardcoded `ARSENAL` constant
- `build_arsenal(robots)` — per-corridor arsenal from corridor robots
- 3x3 face panel in HUD (later replaced by cockpit)
- Xbox controller selection + mouse click-to-select
- Cosmetic projectile streaks (`draw_projectile_3d`)
- Files: `combat.py` (merged), `app.py` (wired), `PARENT_ESTATE/briefs/CHILD_BRIEF_10_arsenal.md`

**3 bugs found by Nir after Brief #10:**
1. Defeat plaque white rectangle (corridor_builder.py:324)
2. Face panel uses blue-tinted hologram PNGs instead of normal photos
3. Ship flies through walls (hub.inside() exists, never called)

### 4th PARENT (Opus 4.8) — Afternoon

**Brief #12 — HOSTAGES** (built by child, wired by DeepSeek)
- `hostages.py` — Hostage class: TWO real 3D humanoid figures from GL primitives
- Mirrors Robot class structure (geometry assembly, fake lighting, split opaque/emissive draw)
- Two variants (distinct builds/colors), gentle idle bob+sway
- `build_hostages(corridor_geom)` → exactly 2 Hostage objects
- `near_hostages(hostage_list, ship_pos)` → bool
- Wired into `corridor_builder.py` (build, update, draw)
- `hostages_demo.py` — flyable demo
- Added `palette.HOSTAGE_GLOW`
- Files: `hostages.py`, `hostages_demo.py`, `palette.py`, `corridor_builder.py`

**Orientation fix (BUG from Brief #12):**
- Hostages were tilted at 30° — corridors bend in 6-DOF
- Fix: `Hostage` now accepts `up_normal` (cavern floor normal)
- `cavern_floor_normal()` accessor added to `CorridorGeometry`
- `glMultMatrixf` replaces old `glRotatef(yaw)`
- Files: `hostages.py` (rewritten), `corridor_builder.py`

**Brief #13 — GAME STATE** (built by child, wired by DeepSeek)
- `game_state.py` — GameState class (WIN-ONLY, no lose)
- Rescue trigger: fly near couple → `corridor.hostages_rescued = True` → couple disappears
- "HOSTAGES RESCUED" flash + "RESCUED N/M" status + "LEVEL COMPLETE" banner
- Corridor complete = rescued AND all robots defeated
- Level complete = all corridors complete
- `game_state_demo.py` — flyable demo
- Wired into `app.py` (4 lines) + `corridor_builder.py` (1-line guard)
- Files: `game_state.py`, `game_state_demo.py`, `app.py`, `corridor_builder.py`

**draw_plain_text_2d — text rendering fix**
- All HUD/title/plaque text showed raw LaTeX code (`\mathrm{HOSTAGES\ RESCUED}`)
- Added `draw_plain_text_2d()` + `get_plain_text_tex()` using `pygame.font` rasterizer
- Deleted broken `_mt()` wrappers from `combat.py` and `game_state.py`
- Corridor titles + defeat plaques stay on mathtext (they contain actual math)
- HUD labels (VULNERABLE TO, LOADED, RESCUED, fizzle) use real font
- Files: `render.py`, `combat.py`, `game_state.py`, `corridor_builder.py`

**Minor fixes during afternoon:**
- Arsenal name labels fixed (were showing raw `\text{}` — switched to plain text)
- Rescue count shows PEOPLE (x2 per corridor): "RESCUED 0/2" not "RESCUED 0/1"

### 4th PARENT (Opus 4.8) — Evening

**Brief #15 — COCKPIT** (built by child, wired by DeepSeek)
- `cockpit.py` — `CockpitHUD` class: polygon-built Descent-1995-style HUD
- Resolution-independent (fractions of W,H — re-layouts on resize)
- Final design (after Nir's feedback):
  - ONE flat black horizontal bar across the bottom (no peak, no boxes, no gauge)
  - Faces in ONE ROW, big, evenly spaced with names below
  - Two grey canopy beams (slanted quads) framing the top corners, feet on bar
  - Beam toggle: `STRUTS_ON` constant
- Replaced `combat.py` draw_hud and _face_hit_test (now delegates to cockpit)
- `cockpit_demo.py` — standalone demo with resize presets
- Files: `cockpit.py`, `cockpit_demo.py`, `combat.py`

**Cockpit iterations today:**
1. V1: Two black boxes + glowing gauge + peaked dashboard → REJECTED (ugly)
2. V2: Flat bar, single row, big faces, names below, optional struts → KEPT
3. V3: Canopy beams added (grey slanted quads from screen edges to bar)
4. V4: Beams flush to screen top (`_BEAM_TOP_DROP=0`)
5. V5: Xbox nav fixed — deleted grid logic, all directions cycle ±1

---

## 📂 CURRENT FILE INVENTORY (every source file)

```
peaktogether-website/
├── app.py                    # main loop (all briefs wired)
├── combat.py                 # Brief #9+#10: combat + arsenal + cockpit delegation
├── cockpit.py                # Brief #15: Descent-style polygon HUD
├── cockpit_demo.py           # Brief #15: standalone cockpit demo (resizable)
├── render.py                 # core GL engine + draw_plain_text_2d
├── gamepad.py                # GamepadManager (T.16000M + Xbox)
├── understanding.py          # Brief #11: 4-layer depth panels
├── game_state.py             # Brief #13: rescue, progress, WIN-ONLY
├── game_state_demo.py        # Brief #13: flyable demo
├── hostages.py               # Brief #12: TWO 3D humanoid figures
├── hostages_demo.py          # Brief #12: flyable demo
├── content_parser.py         # corridor .txt parser → CorridorData
├── palette.py                # ColorLedger + HOSTAGE_GLOW
├── robots.py                 # Robot class + load_portrait()
├── corridor_builder.py       # CorridorGeometry (hostages wired, plaque guard)
├── hub_builder.py            # HubGeometry (atrium + doors + hub.inside())
├── level_parser.py           # level manifest loader
├── corridors/
│   ├── 01_dummy.txt, 02_dummy.txt, 03_dummy.txt
│   └── maxwell.txt           # 5 Maxwell equation robots
├── levels/
│   ├── intro.txt             # 3 dummy corridors
│   └── maxwell.txt           # 1 Maxwell corridor
├── *.png                     # hologram portraits (blue-tinted)
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md          # ⭐ THE LAW — read first
│   ├── DESCENT_QED_PARENT_HANDOFF.md # original v1 handoff
│   ├── INTERFACES_v0.1.md            # 10-module interface spec
│   ├── SESSION_2026-06-14.md         # previous day
│   ├── SESSION_2026-06-15_MORNING.md  # ☀️ morning session
│   ├── SESSION_2026-06-15_AFTERNOON.md # 🌤️ afternoon session
│   ├── SESSION_2026-06-15_EVENING.md  # 🌙 THIS FILE
│   ├── briefs/                        # child briefs #1-#15
│   │   ├── CHILD_BRIEF_10_arsenal.md
│   │   ├── CHILD_BRIEF_12_hostages.md
│   │   ├── CHILD_BRIEF_13_game_state.md
│   │   └── CHILD_BRIEF_15_cockpit.md
│   └── reports/                       # completion reports
│       ├── COMPLETION_REPORT_12_hostages.md
│       └── COMPLETION_REPORT_13_game_state.md
└── docs/
    └── CONTENT_AUTHORING.md   # reusable Wikipedia→corridor child brief
```

---

## 🔴 WHAT STILL NEEDS TO BE DONE

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1 | **Face panel images** — replace blue-tinted `*-hologram.png` with normal photos | 🔴 HIGH | Normal PNGs in Nir's Downloads, not in repo |
| 2 | **Ship wall containment** — call `hub.inside()` after `ship.update`, clamp if outside | 🟡 MED | `hub.inside()` exists, unwired |
| 3 | **T.16000M joystick** — wire `gamepads.pilot_command()` into ship controls | 🟡 MED | Code exists in `gamepad.py`, unwired |
| 4 | **Defeat plaque STILL SHOWS WHITE RECTANGLE** — after robot dies, a billboard should appear at the robot's position showing EXPLAIN_MATHEMATICIAN text as a transparent "road sign" in the corridor (NOT in Understanding Mode — directly in-world, single layer, educational reinforcement on the way back). Currently: white rectangle. Code in `corridor_builder.py:_draw_plaques` (line 327). Was partially changed from `briefing_hint[:36]` to `explain["mathematician"]` but mathtext rendering is still broken. | 🔴 HIGH |
| 5 | **Spaceship interior reference** — Nir uploaded reference images of cockpit interior that haven't been matched | 🟢 LOW | Current cockpit is functional but might need styling tweaks |

---

## ✅ WHAT IS FULLY COMPLETE

- All 8 world-tier modules (content_parser through app)
- Combat (#9): fire, match/fizzle, auto-face, projectiles
- Arsenal (#10): per-corridor weapons, face panel, Xbox/mouse/keyboard selection
- Understanding Mode (#11): 4-layer depth panels
- Hostages (#12): TWO real 3D humanoid figures, standing on cavern floor
- Game State (#13): rescue trigger, HOSTAGES RESCUED, corridor/level complete, WIN-ONLY
- Cockpit (#15): flat bar, face row, canopy beams, Xbox nav
- Plain text renderer: `draw_plain_text_2d()` using pygame.font
- All text HUD labels: clean readable English (no raw LaTeX)
- All _mt() wrappers: deleted from combat.py and game_state.py

---

## 🚀 HOW TO RUN

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, SPACE fire,
U = Understanding Mode near robot, ESC quit.
Xbox: Y/A/B/X cycle weapons, LB/RB cycle, LT/RT fire.
Mouse: click face to select weapon.

Demos available:
- `python cockpit_demo.py` — cockpit with resize presets (1-4 keys)
- `python hostages_demo.py` — fly to see the couple
- `python game_state_demo.py` — full game with game state

---

## 📋 GAME FLOW (what the player does)

1. Spawn in atrium, fly into a corridor doorway
2. Fly down the corridor, approach the first robot
3. Read the robot's hologram → identify required mathematician
4. Select that mathematician's face on the bottom bar (Xbox or mouse)
5. Fire (SPACE or LT/RT) → match = robot destroyed, mismatch = gentle fizzle clue
6. Repeat for all robots in the corridor
7. Fly to the blue cavern at the end → see TWO glowing 3D people
8. Fly near them → "HOSTAGES RESCUED" flash, couple disappears, status updates
9. Kill remaining robots → corridor complete
10. Do all corridors → "LEVEL COMPLETE" banner

NO losing. NO death. NO timer. NO punishment. WIN ONLY.

---

## 🔑 GAME DESIGN (THE LAW — from PARENT_HANDOFF_V3.md §1)

DESCENT QED is a 6-DOF flying game themed around MATHEMATICAL PROOF.
A COUPLE pilots a single SPACESHIP. They DESCEND through CORRIDORS to
rescue HOSTAGES at the end. ROBOTS block the way and must be DESTROYED.
Each robot requires a SPECIFIC MATHEMATICIAN'S TECHNIQUE. The player's
MISSILES ARE MATHEMATICIANS. READING identifies which one to fire.

PRIME LAW — MATHEMATICS-BLINDNESS: the engine matches opaque IDs only
(`loaded_id == robot.required_technique_id` → kill). NEVER interprets meaning.

CARDINAL FLUSH TRAP: `render.flush_walls()` called EXACTLY ONCE per frame,
after `draw_world`, before robots. Omit/duplicate → BLACK SCREEN.
