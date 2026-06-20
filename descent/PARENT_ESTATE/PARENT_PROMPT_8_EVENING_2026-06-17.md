# 🚀 DESCENT QED — PARENT PROMPT #8: POLISH & MULTI-CORRIDOR (June 17, 2026 EVENING)

> **TO:** Claude Opus 4.8 — You are PARENT #8 / ARCHITECT.
> **FROM:** Nir (strulovitz) — the human, the boss. He pastes this to you.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, tests, reports.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude Opus 4.8 conversation.
> **READ EVERY SECTION BEFORE WRITING ANY BRIEF.**

---

## 0. YOUR ROLE & THE BACKSTORY (READ FIRST)

You are the 8th **PARENT / ARCHITECT** of DESCENT QED. You write tightly-scoped **BRIEFS** for child Opus instances (fresh chats, no memory). Children write the actual code. DeepSeek (running on Nir's machine) commits it, tests it, and reports back. DeepSeek does NOT design or write code unless explicitly told — your children write ALL new code.

**WHAT HAPPENED BEFORE YOU — THE 7 PARENTS:**

| Parent | Who | What They Did |
|--------|-----|---------------|
| **#1** | Claude Fable (banned June 2026) | Original math_flyer.py engine, 11 harmonic series pages, mathtext-only rule |
| **#2** | Opus 4.8 (DIED — context lost) | Wrote Briefs #1-#9 (world tier + combat), got confused and wrote Understanding Mode as Brief #10 instead of Weapons |
| **#3** | Opus 4.8 | PARENT_HANDOFF_V3.md (THE LAW), Brief #10 (Arsenal/Weapons), Brief #11 (Understanding Mode — live-mathtext) |
| **#4** | Opus 4.8 | Brief #12 (Hostages — 3D humanoids), Brief #13 (Game State — WIN-ONLY), Brief #15 (Cockpit — Descent HUD), `draw_plain_text_2d` engine function |
| **#5** | Opus 4.8 | THE BIG PIVOT: live mathtext → pre-baked LaTeX PNGs. Built `deu/bake_corridor.py` baker, new `understanding.py` (fog-and-glass flight), 36 baked PNGs |
| **#6** | Opus 4.8 | Brief #A: Baked PNG wiring (baked: manifest → runtime). Brief #B: Basel game corridor (7 robots, 42 fizzles). Fixed frame-1 auto-fire bug. Added robot_in_view selector. |
| **#7** | Opus 4.8 (TODAY) | Brief #C1: Ship collision/containment (walls + robot blocking). Brief #P1: Defeat plaques using baked PNGs. Brief #J1: T.16000M joystick wiring (true analog, additive). Brief #J1B: Joystick button wiring (trigger = fire, back-center = engineer reveal). |

**THE GAME IS NOW FEATURE-COMPLETE AT THE ENGINE LEVEL.** Two playable corridors (Maxwell + Basel), combat, hostages, Understanding Mode with baked PNGs, Descent cockpit, ship containment, defeat plaques, full joystick support.

---

## 1. THE GAME — THIS IS LAW (re-read before writing any brief)

DESCENT QED is a **6-DOF flying game** themed around MATHEMATICAL PROOF. "QED" = quod erat demonstrandum.

**THE FICTION:**
- A **COUPLE** pilots a single SPACESHIP (two people, one ship).
- They DESCEND through CORRIDORS. At the END of each corridor are **HOSTAGES** — the prize/goal. Reaching them = WINNING.

**THE OBSTACLE:**
- **ROBOTS** physically BLOCK the corridor. You cannot fly past a robot until it's destroyed.

**THE CORE COMBAT MECHANIC:**
- Each robot requires a **SPECIFIC MATHEMATICIAN'S TECHNIQUE** to be destroyed.
- The player's **WEAPONS ARE MISSILES**, and **EACH MISSILE = A MATHEMATICIAN**.
- To destroy a robot, fire the missile whose mathematician the robot is VULNERABLE TO.
- **READING** is the IDENTIFICATION step — then THINKING is the gameplay.

**THE FULL LOOP PER ROBOT:**
```
Fly up to blocking robot → READ its hologram → IDENTIFY required mathematician
→ SELECT that mathematician-missile → FIRE → MATCH CHECK → robot DESTROYED
→ Advance to next robot → ... → Reach corridor end → RESCUE HOSTAGES → WIN
```

**THE PRIME LAW — MATHEMATICS-BLINDNESS:**
- The engine NEVER interprets what math MEANS. It only matches IDENTIFIERS:
  `robot.required_technique_id == fired_missile_id` → kill.
- All MEANING lives in the corridor fixture files and the player's head.
- No module hardcodes color-to-meaning. Color passes through `palette.py` via opaque keys.

**RESOLVED DESIGN DECISIONS:**
- Wrong-mathematician shot → harmless fizzle message for 6 seconds. NO penalty. FINAL.
- Game is WIN-ONLY. No death, no timer, no punishment.
- Fizzle is FINAL: the couple is learning together.
- Joystick: true analog, proportional, additive to keyboard.

---

## 2. TECH STACK & ENGINE CANON

- **Python 3.12**, pygame + PyOpenGL. Legacy fixed-function OpenGL (no shaders).
- **Repo:** `https://github.com/strulovitz/peaktogether-website` (local: `C:\Users\nir_s\peaktogether-website`)
- **World:** Grey rocky ATRIUM (hollow faceted sphere, radius 34) → N doorways via FIBONACCI SPHERE distribution → each doorway leads to a BENT CORRIDOR → ends in a BLUE CAVERN (hostage room).
- **Corridors:** Square box tunnel (N_SIDES=4, visual corners), but `inside()` collision is ROUND (cylindrical lateral-distance test from centerline). Tube radius = 6. Straight prism segments joined at bends (random turns 12°-22°, segment length 14).
- **Coordinates:** right=+X, up=+Y, forward=-Z. Quaternions [w,x,y,z] numpy.
- **Ship:** `.pos` (vec3), `.vel` (vec3), `.q` (quaternion). `ship.update6dof(dt, keys, cmd)`.
- **Fog:** `set_fog(start=40, end=140, color=palette.CLEAR_COLOR)`

**THE CANONICAL FRAME ORDER (verbatim, obey in every loop):**
```
 1. glClear(color + depth)
 2. ship.update6dof(dt, keys, cmd)  # keyboard + analog joystick, additive
 3. containment.resolve(ship, hub, prev_pos)  # walls + robots
 4. ship.apply_view()
 5. render.set_fog(...)
 6. cr = render.ship_right(ship.q); cu = render.ship_up(ship.q)
 7. hub.update(dt, ship.pos)
 8. hub.draw_world(cr, cu, tc)       # QUEUES walls only — NO flush inside
 9. render.flush_walls(ship.pos)     # ← EXACTLY ONCE, here. Omit = BLACK SCREEN.
10. hub.draw_robots(cr, cu, tc)
11. hub.draw_labels(cr, cu, tc)
12. combat HUD and overlays (begin_2d/end_2d)
13. pygame.display.flip()
```

**THE CARDINAL FLUSH TRAP:** walls are only QUEUED by `draw_world`. If `flush_walls` is NOT called exactly once per frame (step 9), ALL WALLS VANISH SILENTLY — black screen, no error. This is the #1 cause of "black screen" bugs.

---

## 3. WHAT IS FULLY BUILT & WORKING (complete inventory)

### WORLD TIER (8 modules — all complete):
| Module | File | What it does |
|--------|------|-------------|
| **content_parser** | `content_parser.py` | Parses corridor `.txt` files → `CorridorData` + `RobotData` objects with `understanding_dir`, `explain`, `fizzles`, `segments`, etc. |
| **palette** | `palette.py` | ColorLedger. Maps opaque keys → RGBA colors. |
| **render** | `render.py` | Core GL. `Ship` class (pos, vel, q, `update6dof`), quaternion math, `set_fog`, wall queue + `flush_walls`, `begin_2d`/`end_2d`, `draw_plain_text_2d`, `render_rich`, `draw_billboard`, `draw_texture`. |
| **robots** | `robots.py` | `Robot` class (faceted hull, Larson scanner eye, hologram portrait, explosion). `is_defeated()`, `play_defeat()`, `understanding_dir`, `base_pos`, `position`. |
| **corridor_builder** | `corridor_builder.py` | Builds `CorridorGeometry`: bent tube, stations, robot positions, blue cavern, defeat plaques (baked PNGs with white frame). `seg_bounds`, `inside()`, `hostage_positions()`. |
| **hub_builder** | `hub_builder.py` | Builds `HubGeometry`: grey atrium sphere + Fibonacci doorways → corridors. `spawn_pose()`, `inside(point, margin)`, `corridors` list. |
| **level_parser** | `level_parser.py` | Loads level manifest → `Level`. Parses `baked:` line → `understanding_dir`. |
| **app** | `app.py` | Minimal integration. Canonical frame loop. Joystick + keyboard input. `LEVEL_MANIFEST = "levels/basel.txt"`. |

### GAMEPLAY TIER (all complete):
| Brief | File | What it does |
|-------|------|-------------|
| **#9 COMBAT** | `combat.py` | Fire missiles. ID matching. Fizzle (6s). `robot_in_view()` selector. `blocking_robot()`. |
| **#10 ARSENAL** | `combat.py` + `gamepad.py` | Per-corridor weapons from VULNERABLE_TO. Face-selection panel. Xbox/mouse/keyboard selection. |
| **#11 UNDERSTANDING** | `understanding.py` | Fog-and-glass flight. Pre-baked PNG panels. Mouse wheel depth, mouse pan, CTRL/joystick-button engineer unlock. |
| **#12 HOSTAGES** | `hostages.py` | TWO 3D humanoid figures on cavern floor. Gentle idle bob+sway. |
| **#13 GAME STATE** | `game_state.py` | Rescue trigger, "HOSTAGES RESCUED" flash, corridor/level complete, WIN-ONLY. |
| **#15 COCKPIT** | `cockpit.py` | Descent-style polygon HUD: flat bar, face row, canopy beams. |

### NEW ENGINE MODULES (Parent #7 — today):
| Brief | File | What it does |
|-------|------|-------------|
| **#C1 CONTAINMENT** | `containment.py` | Wall confinement (nearest-centerline, CONFINE_RADIUS=4.0) + robot blocking ("oranges in a box" sphere on tube axis). Hard stop + slide. |
| **#P1 PLAQUES** | `corridor_builder.py` | Defeat plaques load baked PNG (`robotN_mathematician.png`), sized to 90% of tube cross-section, thin white frame. |
| **#J1 JOYSTICK** | `render.py` + `app.py` | `Ship.update6dof` — keyboard + T.16000M analog, additive, proportional, combined single-ease. |
| **#J1B BUTTONS** | `app.py` + `understanding.py` | T.16000M trigger (index 0) = fire missile. T.16000M back-center (index 1) = engineer reveal. |

### CORRIDORS & LEVELS:
| File | Description |
|------|-------------|
| `corridors/maxwell_old.txt` | 5 Maxwell robots, game-format |
| `corridors/basel.txt` | 7 Basel robots, 42 fizzles, game-format |
| `levels/maxwell.txt` | Maxwell manifest (baked: ../baked/maxwell) |
| `levels/basel.txt` | Basel manifest (baked: ../baked/basel) — **CURRENTLY ACTIVE** |
| `levels/intro.txt` | 3 dummy corridors |
| `levels/mathematics/basel_problem/basel_euler_proof.txt` | Baker-format Basel (SOURCE OF TRUTH) |

### BAKED PNGs:
| Directory | Files | Description |
|-----------|-------|-------------|
| `baked/maxwell/` | 8 PNGs | Robots 3-4, 4 layers each |
| `baked/basel/` | 28 PNGs | Robots 1-7, 4 layers each |

### HARDWARE:
- T.16000M FCS flight stick: fully wired (6-DOF analog flight + fire trigger + engineer reveal button)
- Xbox 360 controller: weapon selection + fire (manipulator role)

---

## 4. KEY DATA OBJECTS (current state)

```python
# === content_parser.py ===
CorridorData:
    .number, .title, .flavor, .briefing_intro, .entry_text, .exit_text
    .robots: list[RobotData]
    .ledger: ColorLedger
    .understanding_dir: str = ""

RobotData:
    .number, .name, .briefing_hint, .problem
    .explain: dict[str,str]  # keys: "mathematician","physicist","biologist","engineer"
    .segments: list[Segment]
    .eye_color_key, .fizzles: dict[str,str]
    .required_technique_id: str  # from VULNERABLE_TO
    .understanding_dir: str = ""

# === robots.py ===
Robot (runtime):
    .name, .position (vec3, bobbed), .base_pos (vec3, un-bobbed)
    .required_technique_id, .understanding_dir, .number, .size
    ._hull_verts, ._HULL_R = 1.6
    .is_defeated() -> bool
    .play_defeat()

# === corridor_builder.py ===
CorridorGeometry:
    .seg_bounds: list[dict]  # {"start":(x,y,z), "end":(x,y,z), "right":(x,y,z),
                             #  "up":(x,y,z), "radius":float}
    .get_robots() -> list[Robot]
    .inside(point, margin=0.0) -> bool  # cylindrical swept-tube test
    .stations() -> list[((x,y,z), yaw)]
    .hostage_positions() -> list[(x,y,z)]
    .cavern_floor_normal() -> tuple

# === hub_builder.py ===
HubGeometry:
    .center: vec3, .radius: float (=34)
    .corridors: list[CorridorGeometry]
    .inside(point, margin=0.0) -> bool  # atrium sphere OR any corridor
    .spawn_pose() -> ((x,y,z),(yaw,pitch))
    .door_poses() -> list[((x,y,z),(nx,ny,nz))]

# === render.py ===
Ship:
    .pos: vec3, .vel: vec3, .q: quaternion, .home: vec3
    .update(dt, keys)            # keyboard-only (digital, preserved for tests)
    .update6dof(dt, keys, cmd)   # keyboard + joystick, combined single-ease
    .apply_view()
    MAX_SPEED=18, ACCEL=5, BOOST=3, PITCH_YAW=radians(95), ROLL_SPEED=radians(140)

# === containment.py ===
resolve(ship, hub, prev_pos) -> None  # mutates ship.pos/.vel
# Walls: confine to CONFINE_RADIUS=4.0 around nearest centerline, slide
# Robots: "oranges in a box" sphere on tube axis, sized to plug tube
```

---

## 5. WHAT REMAINS TO BUILD — THE 2 KNOWN ISSUES

### 🔴 Issue 1 — Understanding Mode "Conveyor Belt"

**The symptom:** When flying through the explanation panels (mathematician → physicist → biologist → engineer), the road-sign panels flip forward↔backward or drift like a conveyor belt. The feel is wrong — they don't move/depth correctly.

**What needs investigation:** How `focus`/`target` interact with the panel ordering, whether the FAR→NEAR draw order is correct, whether pan/focus compose as intended. This is a UX/feel bug in `understanding.py`.

**Design context:** Understanding Mode uses a "fog-and-glass" physical model:
- Each sign is a glass panel with baked PNG transparency
- Focus (depth) is a continuous float 0..3
- Distance = |focus - layer_index|
- Size grows with nearness, blur decreases, fog veil sits between signs
- CTRL (keyboard or joystick button 1) = engineer unlock (fly to layer 3)
- Mouse wheel changes target depth, smooth glide toward it

**Nir's desired feel:** Flying forward/backward through the signs should feel like approaching glass road-signs — they grow in size as you get near, stay in their fixed positions in space, and you pass through them. Not a conveyor belt that drifts or flips.

### 🔴 Issue 2 — Multiple Corridors

**The symptom:** Only ONE corridor exists in the level. The hub supports multiple corridors (Fibonacci sphere doorways → `hub.corridors` list), and `build_hub` can attach any number. But only one corridor has ever been tested at a time (`levels/basel.txt` has one `corridors:` entry).

**What needs investigation and building:**
- Create a level manifest with MULTIPLE corridor entries (e.g. Maxwell + Basel, or multiple Basel proof-variants)
- Test that multiple corridors work end-to-end: enter corridor 1, fight robots, rescue hostages, exit back to atrium, enter corridor 2
- Verify no cross-corridor bleed: holograms from one corridor don't appear in another, weapons/arsenal reset per corridor, understanding mode loads the right baked PNGs per corridor
- Verify game state resets per corridor (hostages, robot defeat state)
- Verify the atrium door selection works visually (doorway labels, ship navigation between doors)

**Design context:**
- The hub already allocates doorways via Fibonacci sphere
- `hub.corridors` is a list of `CorridorGeometry` objects
- `_sync_arsenal` in `combat.py` already detects corridor changes and rebuilds the weapon panel
- `hub.inside()` returns True for the atrium OR any corridor — multi-corridor containment should work

---

## 6. HOW THE PARENT SHOULD PROCEED

### STEP 1 — Confirm with Nir:
- Ask Nir: "Should I write the conveyor-belt fix and multi-corridor as two separate briefs, or combine them?"
- Ask Nir: "For multi-corridor, do you have specific corridor files ready, or should I design a test manifest with the existing Maxwell + Basel together?"
- Ask Nir: "Are there any other polish items you want before calling the engine done?"

### STEP 2 — Write the briefs:

**Brief #U1 — Understanding Mode Conveyor Belt Fix:**
Investigate and fix the panel drift/flip. This is an `understanding.py`-only change. The child must understand the fog-and-glass physical model, the focus/target easing, the FAR→NEAR draw order, and identify what causes the conveyor-belt feel. Pure UX fix.

**Brief #M1 — Multi-Corridor Level:**
Build a level manifest that loads multiple corridor files. Test end-to-end: enter corridor 1, complete it (all robots + hostages), return to atrium, enter corridor 2. Verify no bleed between corridors (arsenal, robots, hostages, understanding mode, plaques). Fix any bleed bugs discovered. May need small changes to `game_state.py`, `combat.py`, `app.py`, and a new level manifest file.

### Brief writing principles (same as always):
- **Paste verbatim code** the child needs — NEVER let a child hallucinate APIs
- **Fence scope hard** — "You build ONE concern."
- **No flush changes** — A child must NOT add, move, or remove `flush_walls` calls
- **Test with BOTH corridors** — any change must work for Maxwell AND Basel

---

## 7. HOW TO RUN (for Nir)

```powershell
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Currently loads Basel corridor (`levels/basel.txt`).

Controls:
- **Keyboard:** WASD/RF move, arrows rotate, Q/E roll, Shift boost, SPACE fire, `[`/`]` cycle weapon, U = Understanding Mode, CTRL = engineer unlock, ESC = quit
- **T.16000M Joystick:** stick = pitch/roll, twist = yaw, throttle = forward thrust, hat = strafe, trigger = fire, back-center = engineer unlock
- **Xbox:** Y/A/B/X cycle weapons, LB/RB cycle, LT/RT fire
- **Mouse:** click face to select weapon, wheel = depth in Understanding Mode, move = pan

---

## 8. FILE INVENTORY (complete, current)

```
peaktogether-website/
├── app.py                           # Main loop (LEVEL_MANIFEST = levels/basel.txt)
├── understanding.py                 # Fog-and-glass PNG loading + joystick engineer button
├── combat.py                        # Combat + arsenal + fizzle
├── containment.py                   # Wall confinement + robot blocking (Brief #C1)
├── cockpit.py                       # Descent HUD
├── gamepad.py                       # T.16000M + Xbox (pilot_command, deadzones, calibration)
├── game_state.py                    # Win/lose conditions
├── hostages.py                      # 3D humanoid hostages
├── robots.py                        # Robot class + understanding_dir
├── render.py                        # Core GL + Ship + update6dof + draw_billboard + draw_plain_text_2d
├── content_parser.py                # Corridor file parser
├── palette.py                       # Color ledger
├── corridor_builder.py              # Corridor geometry + defeat plaques (baked PNG)
├── hub_builder.py                   # Atrium + Fibonacci doorways + inside()
├── level_parser.py                  # Level manifest + baked: parsing
├── deu/
│   └── bake_corridor.py             # Baker
├── corridors/
│   ├── basel.txt                    # Basel game corridor (7 robots, 42 fizzles)
│   ├── maxwell_old.txt              # Maxwell game corridor (5 robots)
│   ├── maxwell.txt                  # Baker-format Maxwell
│   └── 01-03_dummy.txt
├── levels/
│   ├── basel.txt                    # Basel manifest (ACTIVE)
│   ├── maxwell.txt                  # Maxwell manifest
│   ├── intro.txt
│   └── mathematics/basel_problem/
│       └── basel_euler_proof.txt    # Baker-format Basel
├── baked/
│   ├── maxwell/                     # 8 PNGs
│   └── basel/                       # 28 PNGs
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md         # ⭐ THE LAW
│   ├── PARENT_PROMPT_7_ENGINE_GAPS.md
│   ├── PARENT_PROMPT_8_EVENING_2026-06-17.md  # ⭐ THIS FILE
│   ├── SESSION_2026-06-16_NIGHT.md
│   ├── briefs/                      # Briefs #C1, #P1, #J1, #J1B
│   └── reports/                     # Completion reports
└── *.png                             # 15 hologram portraits
```

---

## 9. ONE-PARAGRAPH SUMMARY FOR PARENT

You are Parent #8. Seven parents before you built a complete 6-DOF Descent-style game: grey rock mine with atrium + radiating corridors, 7-module world tier, full combat system (missiles are mathematicians, wrong shot = harmless 6s fizzle), hostages to rescue, Understanding Mode with pre-baked colored LaTeX PNGs, Descent-style cockpit HUD, ship containment (walls + robot blocking), defeat plaques showing baked mathematician signs, and full T.16000M joystick support (analog flight + fire trigger + engineer button). Two complete corridors exist (Maxwell: 5 robots, Basel: 7 robots). The engine is feature-complete. Your job: fix two remaining polish issues — (1) Understanding Mode panels drift/flip like a conveyor belt instead of staying in fixed space positions, and (2) the game needs multiple corridors per level instead of one, with no cross-corridor bleed. These are the last items before the game is fully polished.

---

**END OF PROMPT — Nir will tell you what to build first.**
