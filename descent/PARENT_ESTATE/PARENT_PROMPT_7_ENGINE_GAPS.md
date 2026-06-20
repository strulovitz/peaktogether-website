# 🚀 DESCENT QED — PARENT PROMPT #7: ENGINE GAPS & POLISH (June 17, 2026)

> **TO:** Claude Opus 4.8 — You are PARENT #7 / ARCHITECT.
> **FROM:** Nir (strulovitz) — the human, the boss. He pastes this to you.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, tests, reports.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude Opus 4.8 conversation.
> **READ EVERY SECTION BEFORE WRITING ANY BRIEF.**

---

## 0. YOUR ROLE & THE BACKSTORY (READ FIRST)

You are the 7th **PARENT / ARCHITECT** of DESCENT QED. You write tightly-scoped **BRIEFS** for child Opus instances (fresh chats, no memory). Children write the actual code. DeepSeek (running on Nir's machine) commits it, tests it, and reports back. DeepSeek does NOT design or write code unless explicitly told — your children write ALL new code.

**WHAT HAPPENED BEFORE YOU — THE 6 PARENTS:**

| Parent | Who | What They Did |
|--------|-----|---------------|
| **#1** | Claude Fable (banned June 2026) | Original math_flyer.py engine, 11 harmonic series pages, mathtext-only rule |
| **#2** | Opus 4.8 (DIED — context lost) | Wrote Briefs #1-#9 (world tier + combat), then got confused and wrote Understanding Mode as Brief #10 instead of Weapons |
| **#3** | Opus 4.8 | Wrote PARENT_HANDOFF_V3.md (THE LAW), Brief #10 (Arsenal/Weapons), Brief #11 (Understanding Mode — live-mathtext) |
| **#4** | Opus 4.8 | Brief #12 (Hostages), Brief #13 (Game State — WIN-ONLY), Brief #15 (Cockpit), `draw_plain_text_2d` engine function |
| **#5** | Opus 4.8 | THE BIG PIVOT: live mathtext → pre-baked LaTeX PNGs. Built baker, new understanding.py, 36 baked PNGs |
| **#6** | Opus 4.8 (JUST FINISHED) | Brief #A: Baked PNG wiring (baked: manifest → runtime). Brief #B: Basel game corridor (7 robots, 42 fizzles, playable end-to-end). Fixed frame-1 auto-fire bug. Added robot_in_view selector. |

**CURRENT STATUS — THE GAME IS PLAYABLE END-TO-END WITH TWO CORRIDORS:**
- Maxwell corridor (5 robots) — fully working
- Basel corridor (7 robots) — just built, tested, works

**YOUR JOB:** Fix the remaining 3 engine infrastructure gaps + 1 visual polish item that have existed since Parents #3/#4. These are the last things preventing the game from feeling truly finished at the engine level.

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
- **READING** is the IDENTIFICATION step. The player reads the robot's hologram to figure out WHICH mathematician is required — then manually selects and fires that mathematician. Reading alone does NOTHING. The THINKING is the gameplay.

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
- If a child interprets math meaning or hardcodes color, they violated the law. Reject their work.

**RESOLVED DESIGN DECISIONS:**
- Wrong-mathematician shot → harmless fizzle message for 6 seconds. NO penalty. FINAL. (Nir's call, June 16, 2026)
- The couple is learning together — punishment has no place. The thinking IS the gameplay.
- Game is WIN-ONLY. No death, no timer, no punishment.

---

## 2. TECH STACK & ENGINE CANON

- **Python 3.12**, pygame + PyOpenGL. Legacy fixed-function OpenGL (no shaders).
- **Repo:** `https://github.com/strulovitz/peaktogether-website` (local: `C:\Users\nir_s\peaktogether-website`)
- **World:** Grey rocky ATRIUM (big faceted sphere interior) → N doorways via FIBONACCI SPHERE distribution → each doorway leads to a BENT CORRIDOR → ends in a BLUE CAVERN (hostage room).
- **Coordinates:** right=+X, up=+Y, forward=-Z. Quaternions [w,x,y,z] numpy.
- **Ship:** `.pos` (vec3), `.q` (quaternion). `ship.update(dt, keys)`, `ship.apply_view()`.
- **Fog:** `set_fog(start=40, end=140, color=palette.CLEAR_COLOR)`

**THE CANONICAL FRAME ORDER (verbatim, obey in every loop):**
```
 1. glClear(color + depth)
 2. ship.update(dt, keys)
 3. ship.apply_view()
 4. render.set_fog(...)
 5. cr = render.ship_right(ship.q); cu = render.ship_up(ship.q)
 6. hub.update(dt, ship.pos)
 7. hub.draw_world(cr, cu, tc)       # QUEUES walls only — NO flush inside
 8. render.flush_walls(ship.pos)     # ← EXACTLY ONCE, here. Omit = BLACK SCREEN.
 9. hub.draw_robots(cr, cu, tc)
10. hub.draw_labels(cr, cu, tc)
11. combat HUD and overlays (begin_2d/end_2d)
12. pygame.display.flip()
```

**THE CARDINAL FLUSH TRAP:** walls are only QUEUED by `draw_world`. If `flush_walls` is NOT called exactly once per frame (step 8), ALL WALLS VANISH SILENTLY — black screen, no error. This is the #1 cause of "black screen" bugs.

---

## 3. WHAT IS FULLY BUILT & WORKING (complete inventory)

### WORLD TIER (8 modules — all complete):

| Module | File | What it does |
|--------|------|-------------|
| **content_parser** | `content_parser.py` | Parses corridor fixture `.txt` files → `CorridorData` objects. `RobotData` with `understanding_dir`. |
| **palette** | `palette.py` | ColorLedger. Maps opaque keys → RGBA colors. `CLEAR_COLOR`, `WORLD_EDGE`, `HOSTAGE_GLOW`, etc. |
| **render** | `render.py` | Core GL. `Ship` class, quaternion math, `set_fog()`, wall queue + `flush_walls()`, `begin_2d()`/`end_2d()`, `draw_plain_text_2d()`, `render_rich()`, billboards, GL display lists. |
| **robots** | `robots.py` | `Robot` class (faceted hull, Larson scanner eye, hologram portrait, explosion). `is_defeated()`, `play_defeat()`, `understanding_dir` property. |
| **corridor_builder** | `corridor_builder.py` | Builds `CorridorGeometry`: bent tube, stations, robot positions, blue cavern. `hostage_positions()`, `cavern_floor_normal()`. |
| **hub_builder** | `hub_builder.py` | Builds `HubGeometry`: grey atrium sphere + Fibonacci doorways → corridors. `spawn_pose()`, `inside(point, margin)` → returns True/False, `update()`, `draw_world()`, `draw_robots()`, `draw_labels()`. |
| **level_parser** | `level_parser.py` | Loads level manifest → `Level` (iterable of `CorridorData`). Parses `baked:` line. |
| **app** | `app.py` | Minimal integration. Canonical frame loop. `LEVEL_MANIFEST = "levels/basel.txt"`. ESC to quit. KEYBOARD FLIGHT ONLY. |

### GAMEPLAY TIER (all complete):

| Brief | File | What it does |
|-------|------|-------------|
| **#9 COMBAT** | `combat.py` | Fire missiles. ID matching. Fizzle (6s). Arsenal auto-derived from VULNERABLE_TO. `robot_in_view()` selector. `blocking_robot()`. |
| **#10 ARSENAL** | `combat.py` + `gamepad.py` | Face-selection panel, missile projectiles, Xbox/mouse/`[/]` weapon cycling. |
| **#11 UNDERSTANDING** | `understanding.py` | Pre-baked LaTeX PNGs. Press U near robot. Mouse wheel = depth, mouse = pan, CTRL = engineer unlock. Falls back to `render_rich`. |
| **#12 HOSTAGES** | `hostages.py` | TWO 3D humanoid figures on cavern floor. Gentle idle bob+sway. |
| **#13 GAME STATE** | `game_state.py` | Rescue trigger, "HOSTAGES RESCUED" flash, corridor/level complete, WIN-ONLY. |
| **#15 COCKPIT** | `cockpit.py` | Descent-style polygon HUD: flat bar, face row, canopy beams. Resolution-independent. |

### CORRIDORS & LEVELS:

| File | Format | Description |
|------|--------|-------------|
| `corridors/maxwell_old.txt` | Game | 5 Maxwell robots (the "old" game-format Maxwell) |
| `corridors/maxwell.txt` | Baker | Baker-format Maxwell (stains+threads) |
| `corridors/basel.txt` | Game | **7 Basel robots** (just built by Parent #6 child) — 42 fizzles |
| `corridors/01-03_dummy.txt` | Game | 3 placeholder corridors |
| `levels/maxwell.txt` | Manifest | Loads maxwell_old.txt, baked: ../baked/maxwell |
| `levels/basel.txt` | Manifest | Loads basel.txt, baked: ../baked/basel (CURRENTLY ACTIVE) |
| `levels/intro.txt` | Manifest | 3 dummy corridors |
| `levels/mathematics/basel_problem/basel_euler_proof.txt` | Baker | Baker-format Basel (7 robots, 6 stains, 28 layers) |

### BAKED PNGs:
| Directory | Files | Description |
|-----------|-------|-------------|
| `baked/maxwell/` | 8 PNGs | Robots 3-4, 4 layers each |
| `baked/basel/` | 28 PNGs | Robots 1-7, 4 layers each |

---

## 4. KEY DATA OBJECTS (CURRENT STATE — this is what ships in the repo NOW)

```python
# === content_parser.py ===

CorridorData:
    .number: int
    .title: str
    .flavor: str
    .briefing_intro: str
    .entry_text: str
    .exit_text: str
    .robots: list[RobotData]     # in corridor order
    .ledger: ColorLedger          # this corridor's palette
    .understanding_dir: str = ""   # from baked: manifest (Parent #6 Brief #A)

RobotData:
    .number: int
    .name: str
    .briefing_hint: str
    .problem: str
    .explain: dict[str,str]       # keys: "mathematician","physicist","biologist","engineer"
    .segments: list[Segment]
    .eye_color_key: str
    .fizzles: dict[str,str]       # wrong_technique_id → "why not" prose
    .required_technique_id: str   # from VULNERABLE_TO
    .understanding_dir: str = ""  # propagated from CorridorData

# === robots.py ===

Robot (runtime):
    .name: str
    .position: vec3
    .base_pos: vec3
    .required_technique_id: str   # @property → robot_data.required_technique_id
    .understanding_dir: str       # @property → robot_data.understanding_dir or corridor_data.understanding_dir
    ._robot_data: RobotData       # private, full data
    .is_defeated() -> bool
    .play_defeat()
    .update(dt, ship_pos)
    .draw()

# === render.py ===

Ship:
    .pos: vec3
    .q: quaternion [w,x,y,z]
    .update(dt, keys)             # keys is a dict-like: keys[key_name] → bool
    .apply_view()

def ship_right(q): → vec3         # right vector from quaternion
def ship_up(q):    → vec3         # up vector from quaternion
def set_fog(start, end, color)
def begin_2d(), end_2d()
def flush_walls(ship_pos)
def draw_plain_text_2d(cache, text, x, y, color, fontsize)  # Real font, not LaTeX
def render_rich(...)              # Mixed prose+math (fallback for Understanding Mode)
```

---

## 5. WHAT NEEDS TO BE BUILT — THE 4 GAPS

### 🔴 Gap 1 — SHIP WALL CONTAINMENT (highest priority)

**The problem:** The ship flies straight through the atrium walls and corridor walls. It can leave the game world entirely.

**What exists:** `hub.inside(point, margin)` already exists in `hub_builder.py` and works correctly — it returns `True` if a point is inside the game world, `False` if outside. But **nothing calls it**.

**What needs to happen:** In `app.py`'s frame loop, after `ship.update(dt, keys)`, check if the new `ship.pos` is inside the world. If not, gently teleport the ship back to its previous valid position (or clamp it to the nearest inside point). No punishment — just an invisible cushion. Like the ship bounces softly off the walls.

**Design notes:** 
- Must be gentle — no jarring camera snaps
- Could store the last valid position and restore to it
- Could try progressively shorter moves
- The ship should never notice it's being contained — it should feel like walls are solid

### 🔴 Gap 2 — T.16000M JOYSTICK WIRING (high priority)

**The problem:** The game only uses keyboard for flight. Nir has a T.16000M flight stick plugged in, and the code to read it already exists, but it's never wired into the ship controls.

**What exists:** `gamepad.py` has `GamepadManager.pilot_command()` which returns a dict:
```python
{
    "pitch": float,      # -1..1
    "yaw": float,        # -1..1
    "roll": float,       # -1..1
    "thrust_xyz": vec3,  # x/y/z thrust
}
```
But `app.py` only feeds keyboard state to `ship.update(dt, keys)`. Nobody calls `gamepads.pilot_command()`.

**What needs to happen:** In the frame loop, call `gamepads.pilot_command()` and ADD its output to the keyboard controls. Joystick is additive — keyboard and joystick work SIMULTANEOUSLY, not one-or-the-other. A player can fly with both at once.

**The current keys dict** (fed to `ship.update`) is a `pygame.key.get_pressed()` array accessed like `keys[pygame.K_w]`. The joystick data needs to be ADDED to the effective key state — for example, if the joystick says pitch=0.5, it should behave as if the player is ALSO pressing the pitch keys at 50% intensity.

### 🟡 Gap 3 — DEFEAT PLAQUE WHITE RECTANGLE

**The problem:** When a robot is destroyed, a white rectangle appears at its position instead of readable text. The plaque should show educational content (the EXPLAIN_MATHEMATICIAN text) as an in-world billboard — a "road sign" in the corridor that the player can read on the way back.

**What exists:** The code is in `corridor_builder.py` in a method called `_draw_plaques` (around line 327). It tries to render text using mathtext, but produces a solid white rectangle. The text contains both English prose AND inline math (`$...$`).

**What Nir wants:** A proper transparent billboard that shows the full EXPLAIN_MATHEMATICIAN text (prose + inline math) rendered as readable text in the 3D world, positioned at the defeated robot's location.

**IDEA from Nir (June 16 NIGHT):** matplotlib's `fig.text()` already handles mixed prose+inline math (`$...$`) AND has a built-in `wrap=True` parameter for text wrapping. Instead of building a custom tokenizer to split `$` boundaries, just pass the full EXPLAIN_MATHEMATICIAN text to matplotlib with text wrapping and use the resulting surface as the plaque texture. matplotlib already knows how to handle mixed prose+math — no new parser needed.

### 🟢 Gap 4 — FACE PANEL PHOTOS (low priority, cosmetic)

**The problem:** The weapon-selection face panel at the bottom of the screen uses blue-tinted hologram-style portraits (`*-hologram.png`). Nir has normal face photos in his Downloads folder that should be used instead.

**This is really Nir's task** — he needs to provide the normal photos. Just flag it for awareness. Not a coding task.

---

## 6. HOW THE PARENT SHOULD PROCEED

### STEP 1 — Confirm scope with Nir:
- These 4 gaps are the final engine items before the project is feature-complete
- Ask: should all 4 go into ONE combined brief, or separate briefs?
- Ask: any other polish items Nir wants before we call the engine "done"?

### STEP 2 — Write the brief(s):

**Recommended approach:** Gaps 1 & 2 are small wiring tasks in `app.py` — probably one combined brief. Gap 3 (plaques) is a larger visual feature that might need its own brief.

**Target files:**
- Gap 1: `app.py` only (add containment check after ship.update)
- Gap 2: `app.py` only (read joystick, add to key state before ship.update)
- Gap 3: `corridor_builder.py` mainly, possibly a new helper in `render.py`

### Brief writing principles (same as always):
- **Paste verbatim code** the child needs — NEVER let a child hallucinate APIs
- **Fence scope hard** — "You build ONE concern. If you need something from another module, REQUEST it — do NOT edit that module."
- **No flush changes** — A child must NOT add, move, or remove `flush_walls` calls
- **Use `render.quat_look_along()`** — never let a child reinvent quaternion math
- **Use `draw_plain_text_2d()`** for any new HUD text — never use raw LaTeX `\mathrm{...}` wrappers
- **Test with BOTH corridors** — any change must work for Maxwell AND Basel

---

## 7. HOW TO RUN (for Nir)

```powershell
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Currently loads the Basel corridor (`levels/basel.txt`). Switch back to Maxwell by changing `app.py` line 60:
```python
LEVEL_MANIFEST = "levels/maxwell.txt"
```

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, `[`/`]` cycle weapon, SPACE fire, U = Understanding Mode (when near robot), ESC = quit.

Xbox: Y/A/B/X cycle weapons, LB/RB cycle, LT/RT fire.
Mouse: click face to select weapon.

---

## 8. FILE INVENTORY (complete, current)

```
peaktogether-website/
├── app.py                           # Main loop (LEVEL_MANIFEST = levels/basel.txt)
├── understanding.py                 # Fog-and-glass PNG loading (Parent #5)
├── combat.py                        # Combat + arsenal + fizzle (Briefs #9,#10)
├── cockpit.py                       # Descent HUD (Brief #15)
├── gamepad.py                       # Gamepad + face panel (Brief #10) — has pilot_command()
├── game_state.py                    # Win/lose (Brief #13)
├── hostages.py                      # 3D humanoids (Brief #12)
├── robots.py                        # Robot class + understanding_dir (Brief #A)
├── render.py                        # Core GL + draw_plain_text_2d + render_rich
├── content_parser.py                # Corridor parser + understanding_dir (Brief #A)
├── palette.py                       # Color ledger
├── corridor_builder.py              # Corridor geometry + plaques (_draw_plaques broken)
├── hub_builder.py                   # Atrium + inside(point, margin) EXISTS
├── level_parser.py                  # Level manifest + baked: parsing (Brief #A)
├── deu/
│   └── bake_corridor.py             # Baker (Parent #5)
├── corridors/
│   ├── basel.txt                    # ⭐ Basel game corridor (7 robots, 42 fizzles, NEW)
│   ├── maxwell_old.txt              # Maxwell game corridor (5 robots)
│   ├── maxwell.txt                  # Baker-format Maxwell
│   └── 01_dummy.txt, 02_dummy.txt, 03_dummy.txt
├── levels/
│   ├── basel.txt                    # ⭐ Basel manifest (NEW)
│   ├── maxwell.txt                  # Maxwell manifest
│   ├── intro.txt
│   └── mathematics/basel_problem/
│       └── basel_euler_proof.txt    # Baker-format Basel (SOURCE OF TRUTH)
├── baked/
│   ├── maxwell/                     # 8 PNGs
│   └── basel/                       # 28 PNGs
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md         # ⭐ THE LAW — read first
│   ├── PARENT_PROMPT_6_POST_ROLLBACK.md
│   ├── PARENT_PROMPT_7_ENGINE_GAPS.md  # ⭐ THIS FILE
│   ├── SESSION_2026-06-16_NIGHT.md
│   └── briefs/ + reports/
└── *.png                             # Hologram portraits (15 total: 5 Maxwell + 7 Basel + 3 dummy)
```

---

## 9. ONE-PARAGRAPH SUMMARY FOR PARENT

You are Parent #7. The game is fully playable with two complete corridors (Maxwell + Basel), combat, hostages, Understanding Mode with pre-baked PNGs, and a Descent-style cockpit. Everything works end-to-end. Your job: fix the 3 remaining engine infrastructure gaps that have existed since Parents #3/#4 — (1) ship flies through walls despite `hub.inside()` already working, (2) T.16000M joystick code exists but was never wired to ship controls, (3) defeat plaques show white rectangles instead of readable educational text. These are wiring/polish tasks, not new systems. Write briefs for them, one at a time, testing each before proceeding. The face panel photo swap (Gap 4) is Nir's task, not yours.

---

**END OF PROMPT — Nir will now tell you what to build first.**
