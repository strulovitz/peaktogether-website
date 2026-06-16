# 🚀 DESCENT QED — PARENT PROMPT #6: POST-ROLLBACK REBUILD (June 16, 2026 EVENING)

> **TO:** Claude Opus 4.8 — You are PARENT #6 / ARCHITECT.
> **FROM:** Nir (strulovitz) — the human, the boss. He pastes this to you.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, fixes bugs, tests, reports.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude Opus 4.8 conversation.
> **READ EVERY SECTION BEFORE WRITING ANY BRIEF.**

---

## 0. YOUR ROLE & THE BACKSTORY (READ FIRST)

You are the 6th **PARENT / ARCHITECT** of DESCENT QED. You write tightly-scoped **BRIEFS** for child Opus instances (fresh chats, no memory). Children write the actual code. DeepSeek (running on Nir's machine) commits it, wires it all together, tests it, and reports back.

**WHAT HAPPENED BEFORE YOU — THE 5 PARENTS:**

| Parent | Who | What They Did |
|--------|-----|---------------|
| **#1** | Claude Fable (banned June 2026) | Original math_flyer.py engine, 11 harmonic series pages, mathtext-only rule |
| **#2** | Opus 4.8 (DIED — context lost) | Wrote Briefs #1-#9 (world tier + combat), then got confused and wrote Understanding Mode as Brief #10 instead of Weapons, wrote render_rich as Brief #11 instead of Game State |
| **#3** | Opus 4.8 | Wrote PARENT_HANDOFF_V3.md (THE LAW), Brief #10 (Arsenal/Weapons — face panel + missiles), Brief #11 (Understanding Mode — original live-mathtext version) |
| **#4** | Opus 4.8 | Brief #12 (Hostages — 3D humanoids), Brief #13 (Game State — rescue, WIN-ONLY), Brief #15 (Cockpit — Descent HUD), `draw_plain_text_2d` engine function |
| **#5** | Opus 4.8 (TODAY) | THE BIG PIVOT: replaced live mathtext Understanding Mode with PRE-BAKED COLORED LATEX PNGs. Built `deu/bake_corridor.py` baker, new `understanding.py` (fog-and-glass flight), baker-format Maxwell & Basel corridors, 36 baked PNGs. |

**DEEPSEEK'S FAILED ATTEMPT (rolled back — DO NOT REPEAT):**
After Parent #5 finished, DeepSeek (the builder) attempted to wire the baked: system himself:
- Added `understanding_dir` field to `RobotData` and `CorridorData` in `content_parser.py`
- Added `baked:` parsing to `level_parser.py` level manifests
- Added `baked: baked/maxwell` line to `levels/maxwell.txt` manifest
- Created a DeepSeek-authored game stub corridor (`corridors/basel_stub_deepseek.txt`) 
- Created a DeepSeek-authored level manifest (`levels/basel_deepseek.txt`)
- Changed `app.py` `LEVEL_MANIFEST` to the DeepSeek stub

**RESULT:** Robot 1 invisible at runtime, system broken. ALL DeepSeek changes have been **rolled back** via git revert. The repo is now PURE OPUS CODE ONLY. DeepSeek is forbidden from designing or wiring new systems — he only commits, tests, fixes bugs in Opus-authored code, and merges.

**YOUR JOB:** Write the briefs that DeepSeek SHOULD have asked for. Wire the baked system properly, build the real Basel game corridor, and fix remaining engine gaps. One brief at a time.

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

**UNRESOLVED DESIGN QUESTION (ask Nir!):** What happens when the player fires the WRONG mathematician? Currently: harmless fizzle message appears for 6 seconds. Is that final, or should there be a penalty?

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

## 3. WHAT IS BUILT & FLOWN (complete inventory)

### WORLD TIER (all complete, tested, committed):

| Module | File | What it does |
|--------|------|-------------|
| **content_parser** | `content_parser.py` | Parses corridor fixture `.txt` files → `CorridorData` objects. `RobotData` dataclass. Understands CORRIDOR:, ROBOT:, LEDGER:, SEGMENTS:, EXPLAIN_*, VULNERABLE_TO, FIZZLE, etc. |
| **palette** | `palette.py` | ColorLedger. Maps opaque keys → RGBA colors. `CLEAR_COLOR`, `WORLD_EDGE`, `ATRIUM_SHELL`, etc. |
| **render** | `render.py` | Core GL. `Ship` class, quaternion math, set_fog, wall queue + `flush_walls()`, `begin_2d()`/`end_2d()`, `draw_plain_text_2d()`, `render_rich()`, billboards, GL display lists. |
| **robots** | `robots.py` | `Robot` class (faceted hull, Larson scanner eye, hologram portrait, explosion). `RobotData` dataclass. `Robot.is_defeated()`, `Robot.play_defeat()`. |
| **corridor_builder** | `corridor_builder.py` | Builds `CorridorGeometry` from `CorridorData`: bent tube, stations, robot positions, blue cavern. `hostage_positions()`. |
| **hub_builder** | `hub_builder.py` | Builds `HubGeometry`: grey atrium sphere + Fibonacci-sphere doorways → corridors. `spawn_pose()`, `inside(point, margin)`, `update()`, `draw_world()`, `draw_robots()`, `draw_labels()`. |
| **level_parser** | `level_parser.py` | Loads level manifest → `Level` (iterable of `CorridorData`). `discover_levels()`. |
| **app** | `app.py` | Minimal integration. Canonical frame loop. KEYBOARD FLIGHT ONLY (no joystick wired). `LEVEL_MANIFEST = "levels/maxwell.txt"`. ESC to quit. |

### GAMEPLAY TIER (all complete, tested, committed):

| Brief | File | What it does |
|-------|------|-------------|
| **#9 COMBAT** | `combat.py` | Fire missiles at robots. ID matching. Auto-face explosion on hit. Fizzle on wrong hit (6s). `[`/`]` cycle, SPACE to fire. `Combat.blocking_robot(hub)`. |
| **#10 ARSENAL** | `gamepad.py` (face panel) + `combat.py` | Girlfriend face-selection 2D panel (mathematician face images). Missile projectiles. Still uses `[`/`]` as fallback. |
| **#11 UNDERSTANDING** | `understanding.py` (NEW — fog-and-glass) | Pre-baked LaTeX PNGs. Press U near robot. Mouse wheel = depth, mouse = pan, CTRL = engineer unlock. Xbox right-stick pans. Falls back to `render_rich` if PNG missing. |
| **#12 HOSTAGES** | `hostages.py` | TWO 3D humanoid figures, standing on cavern floor. |
| **#13 GAME STATE** | `game_state.py` | Rescue trigger, HOSTAGES RESCUED, corridor/level complete, WIN-ONLY. |
| **#15 COCKPIT** | `cockpit.py` | Descent-style polygon HUD, flat bar, face row, canopy beams. |

### CORRIDOR FIXTURES ON DISK:

| File | Format | Description |
|------|--------|-------------|
| `corridors/01_dummy.txt` | Game | 2 placeholder robots |
| `corridors/02_dummy.txt` | Game | 1 placeholder robot |
| `corridors/03_dummy.txt` | Game | 1 placeholder robot |
| `corridors/maxwell.txt` | **Baker** (stains+threads) | 5 Maxwell equation robots with full stain/thread coloring |
| `corridors/maxwell_old.txt` | Game (backup) | Old game-format Maxwell corridor — THIS is what `levels/maxwell.txt` currently loads |
| `levels/mathematics/basel_problem/basel_euler_proof.txt` | **Baker** (stains+threads) | 7 robots, 6 stains, 28 layers — FULL Basel corridor in baker format |

### LEVEL MANIFESTS:

| File | Points to | baked: line? | Status |
|------|-----------|-------------|--------|
| `levels/intro.txt` | 3 dummy corridors | No | Works |
| `levels/maxwell.txt` | `corridors/maxwell.txt` | **NO** (rolled back) | Works — loads game-format Maxwell |

### BAKED PNGs (exist on disk, NOT wired to game yet):

| Directory | Files | Robots | Status |
|-----------|-------|--------|--------|
| `baked/maxwell/` | 8 PNGs | Robots 3-4, 4 layers each | ✅ Baked, NOT wired |
| `baked/basel/` | 28 PNGs | Robots 1-7, 4 layers each | ✅ Baked, NOT wired |

### PARENT #5 FILES (Opus-authored, preserved):

| File | Description |
|------|-------------|
| `deu/bake_corridor.py` | Baker tool — corridor.txt → colored transparent PNGs. Standalone. |
| `understanding.py` | NEW understanding mode — fog-and-glass flight, loads baked PNGs with `render_rich` fallback. Scope: "this is the ONLY file changed." |
| `PARENT_ESTATE/UNDERSTANDING_MODE_PREBAKED_LATEX.md` | Stain+thread design handoff (156 lines, authoritative) |
| `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` | Child-Opus prompt: Wikipedia → stain+thread corridor files |

---

## 4. KEY DATA OBJECTS (current state — what ships in the repo NOW)

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
    # NOTE: NO understanding_dir field — this was DeepSeek's addition, rolled back.

RobotData:
    .number: int
    .name: str
    .briefing_hint: str
    .problem: str                 # formal statement, Wikipedia register
    .explain: dict[str,str]       # keys: "mathematician","physicist","biologist","engineer"
    .segments: list[Segment]
    .eye_color_key: str           # ledger key → palette.eye(key) → color
    .fizzles: dict[str,str]       # wrong_technique_id → "why not" prose
    .required_technique_id: str   # what VULNERABLE_TO parsed to
    # NOTE: NO understanding_dir field — rolled back.

# === robots.py ===

Robot (runtime):
    .name: str
    .position: vec3
    .base_pos: vec3
    .required_technique_id: str   # @property → robot_data.required_technique_id
    ._robot_data: RobotData       # private, full data
    .is_defeated() -> bool
    .play_defeat()
    .update(dt, ship_pos)
    .draw()                       # opaque + emissive

# === corridor_builder.py ===

CorridorGeometry:
    .stations: list[vec3]
    .robot_positions: list[vec3]
    .hostage_positions() -> list[vec3]    # 3 world-space points
    // etc.
```

---

## 5. CORRIDOR FILE FORMATS — THE TWO FORMATS

### FORMAT A: Game Corridor (used by content_parser.py, loaded by level manifests)

```
CORRIDOR: 1
TITLE { Maxwell Test Corridor }
FLAVOR { Four field laws and the synthesis that binds them. }
LEDGER {
  PRIMARY field_e = red
  PRIMARY field_b = blue
  BLEND   coupling = field_e + field_b
}
BRIEFING_INTRO { Briefing text... }
ENTRY_TEXT { You have entered the corridor. }
EXIT_TEXT { You have cleared the corridor. }

ROBOT: 1
NAME { Gauss Electric }
BRIEFING_HINT { Hint text... }
PROBLEM { Formal problem statement with $math$... }
EXPLAIN_MATHEMATICIAN { Graduate-level explanation... }
EXPLAIN_PHYSICIST { Undergraduate explanation... }
EXPLAIN_BIOLOGIST { High-school explanation... }
EXPLAIN_ENGINEER { Plug in numbers: [[ $\nabla \cdot \mathbf{E}$ | 3.000 ]] ... }
SEGMENTS {
  $\nabla \cdot \mathbf{E}$       | field_e
  $=$                             | NEUTRAL
  $\frac{\rho}{\varepsilon_0}$    | field_e
}
EYE { field_e }
VULNERABLE_TO { gauss_e }
FIZZLE gauss_m { Why Gauss Magnetic doesn't work... }
FIZZLE faraday { Why Faraday doesn't work... }
```

- `VULNERABLE_TO` is a single-value line, NOT a block.
- `FIZZLE <id>` IS a block — body is "why this doesn't work" prose.
- `[[ expr | value ]]` = value-arc for engineer layer. Only in EXPLAIN_ENGINEER.
- The 4 EXPLAIN fields are REQUIRED with EXACT names: `EXPLAIN_MATHEMATICIAN`, `EXPLAIN_PHYSICIST`, `EXPLAIN_BIOLOGIST`, `EXPLAIN_ENGINEER`.

### FORMAT B: Baker Corridor (for deu/bake_corridor.py — DIFFERENT FORMAT)

This is the input to the baker. It has stains (`\stain{name}{...}`) and threads (`\thread{id}{...}`) markers. It is NOT the same as the game corridor format. Example fragment:

```
\stain{field_e}{\thread{t1}{$\nabla \cdot \mathbf{E}$} $=$ \thread{t2}{$\frac{\rho}{\varepsilon_0}$}}
```

Full spec in `PARENT_ESTATE/UNDERSTANDING_MODE_PREBAKED_LATEX.md` §5-§7.

**These two formats are SEPARATE.** A game corridor has EXPLAIN_* blocks with plain text/$math$. A baker corridor has \stain{} and \thread{} markers. The baker produces PNGs from baker-format files. The game loads game-format files for combat/gameplay. They must be CONSISTENT (same robot names, same ordering) so Understanding Mode PNGs map to the correct robots.

---

## 6. THE WIRING PROBLEM — WHAT NEEDS TO BE BUILT

### The Gap:

The baker works. The baked PNGs exist on disk (36 files). The new `understanding.py` can load them. But there is NO PATH from the level manifest to the PNG directory. The chain is broken:

```
Level manifest → CorridorData → Robot → Understanding Mode → PNG files
                   ^^^              ^^^
              NO baked: dir      NO understanding_dir
```

### What understanding.py expects:

Look at `understanding.py` line ~105:
```python
d = getattr(self.robot, "understanding_dir", "") or ""
```
It looks for `robot.understanding_dir`. If empty string → falls back to `render_rich`. If set → loads PNGs from `baked/<dir>/robot<N>_<layer>.png`.

### What needs to exist:

1. **`level_parser.py`**: Parse an optional `baked:` line in level manifests:
   ```
   title: Maxwell Test Corridor
   baked: baked/maxwell
   corridors:
     ../corridors/maxwell.txt
   ```
   The `baked:` value should flow to every `CorridorData` loaded by this manifest.

2. **`content_parser.py`**: Add `understanding_dir: str = ""` to `CorridorData` and `RobotData`. When a `CorridorData` is created with an `understanding_dir`, it should propagate to all its `RobotData` children.

3. **`robots.py`**: Expose `understanding_dir` on the runtime `Robot` class so `understanding.py` can access it via `self.robot.understanding_dir`.

4. **`levels/maxwell.txt`**: Add `baked: baked/maxwell` line.

### The flow:

```
levels/maxwell.txt:
  baked: baked/maxwell
  corridors: ../corridors/maxwell.txt

→ level_parser sees baked: → passes to CorridorData(dir="baked/maxwell")
→ CorridorData propagates to each RobotData
→ corridor_builder creates Robot objects, each with .understanding_dir = "baked/maxwell"
→ understanding.py: robot.understanding_dir → "baked/maxwell" → loads baked/maxwell/robot3_mathematician.png etc.
```

---

## 7. THE BASEL PROBLEM — WHAT NEEDS TO BE BUILT

### Current state:

- **Baker-format Basel exists:** `levels/mathematics/basel_problem/basel_euler_proof.txt` — 7 robots (Leonhard Euler, Coefficient Matching, The Product Over Roots, The Series From Derivatives, François Viète, The Zeros of Sine, Bernhard Riemann), 6 stains, 28 layers.
- **Baked PNGs exist:** `baked/basel/` — 28 PNGs.
- **NO game-format Basel corridor exists** — cannot play the Basel level in-game.
- **NO Basel level manifest exists.**

### What needs to be built:

A proper **game-format** Basel corridor file (`corridors/basel.txt`) that:
- Has 7 ROBOT blocks with the SAME names and numbers as the baker-format file (so Understanding Mode PNGs map correctly)
- Uses the game corridor format (CORRIDOR:, LEDGER:, SEGMENTS:, EXPLAIN_*, VULNERABLE_TO, FIZZLE, etc.)
- Has proper `VULNERABLE_TO` and `FIZZLE` entries for each robot (so combat works)
- Uses `Euler_Goldbach-hologram.png` and other hologram PNGs from repo root

And a level manifest (`levels/basel.txt`) that:
```
title: Basel Problem — Euler's Proof
baked: baked/basel
corridors:
  ../corridors/basel.txt
```

The baker-format Basel file (`levels/mathematics/basel_problem/basel_euler_proof.txt`) is the SOURCE OF TRUTH for robot names, ordering, and layer content. The game-format corridor MUST match it.

---

## 8. EXISTING ENGINE GAPS (from PARENT_HANDOFF_V3 §6)

These are known issues that predate Parent #5:

### Gap 1 — Ship wall containment (NOT WIRED)
- `hub.inside(point, margin)` exists and works (returns True/False). But **nothing calls it**.
- Ship flies through walls. Need to add containment in `app.py` frame loop (after `ship.update`).
- Desired behavior: gentle teleport back inside (invisible cushion). No punishment.

### Gap 2 — T.16000M joystick not wired
- `gamepad.py` has `GamepadManager.pilot_command()` → returns `{pitch, yaw, roll, thrust_xyz}`.
- But `app.py` only feeds KEYBOARD to `ship.update`. Nobody calls `gamepads.pilot_command()`.
- Wire joystick output into ship controls in the frame loop. Joystick ADDS to keyboard (simultaneous, not replacement).

### Gap 3 — Defeat plaque white rectangle
- `corridor_builder.py:_draw_plaques` draws white rectangles instead of proper defeat plaques.
- Low priority but visible.

### Gap 4 — Face panel uses hologram images
- The face-selection panel uses blue-tinted hologram PNGs.
- Normal face photos exist in Nir's Downloads folder (not yet in repo).

---

## 9. WHAT PARENT #6 SHOULD DO

### STEP 1 — Confirm with Nir:
- Ask Nir: "Should I write the wiring brief (#A) and Basel corridor brief (#B) as separate child briefs, or handle the wiring myself as a small parent patch?"
- Ask Nir: "For the Basel game corridor, should I write it myself or dispatch a child Opus with the corridor writer prompt?"
- Ask Nir: "What happens on WRONG-mathematician shot? Currently harmless fizzle for 6 seconds. Is that final?"

### STEP 2 — Write the briefs (one at a time, test each before next):

**Brief #A — BAKED PNG WIRING:**
Wire `baked:` from level manifests → `CorridorData` → `RobotData` → runtime `Robot` → `understanding.py`. Three small changes to `level_parser.py`, `content_parser.py`, `robots.py`. One line addition to `levels/maxwell.txt`. No new modules. Test by running Maxwell corridor and pressing U near a robot — should show colored PNGs instead of render_rich fallback.

**Brief #B — BASEL GAME CORRIDOR:**
Build a proper game-format Basel corridor (`corridors/basel.txt`) matching the baker-format file's 7 robots. Create level manifest (`levels/basel.txt`) with `baked: baked/basel`. Must be playable end-to-end: fly through corridor, destroy all 7 robots, rescue hostages.

**Brief #C — ENGINE GAPS (optional, lower priority):**
- Ship wall containment
- T.16000M joystick wiring

### Brief writing principles:
- **Paste verbatim code** the child needs — NEVER let a child hallucinate APIs.
- **Fence scope hard.** "You build ONE concern. If you need something from another module, REQUEST it — do NOT edit that module."
- **No flush changes.** A child must NOT add, move, or remove `flush_walls` calls.
- **Use `render.quat_look_along()`** — never let a child reinvent quaternion math.

---

## 10. HOW TO RUN (for Nir)

```powershell
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, `[`/`]` cycle weapon, SPACE fire, U = Understanding Mode (when near robot), ESC = quit.

**Baker:**
```powershell
python deu\bake_corridor.py <corridor.txt> --out baked/<name> --dpi 600
```
Requires: pdflatex, pdftocairo (in MiKTeX/TeX Live), Pillow (`pip install pillow`).

---

## 11. FILE INVENTORY (complete, post-rollback)

```
peaktogether-website/
├── app.py                           # Main loop (LEVEL_MANIFEST = levels/maxwell.txt)
├── understanding.py                 # NEW: fog-and-glass PNG loading with fallback (Parent #5)
├── combat.py                        # Combat system (Brief #9)
├── cockpit.py                       # Descent HUD (Brief #15)
├── gamepad.py                       # Gamepad + face selection panel (Brief #10)
├── game_state.py                    # Win/lose conditions (Brief #13)
├── hostages.py                      # 3D humanoid hostages (Brief #12)
├── robots.py                        # Robot class + RobotData dataclass
├── render.py                        # Core GL engine + Ship + quaternions
├── content_parser.py                # Corridor file parser
├── palette.py                       # Color ledger
├── corridor_builder.py              # Corridor geometry builder
├── hub_builder.py                   # Atrium hub + Fibonacci doorways
├── level_parser.py                  # Level manifest loader
├── deu/
│   └── bake_corridor.py             # Baker: corridor.txt → colored PNGs (Parent #5)
├── corridors/
│   ├── maxwell.txt                  # Baker-format Maxwell (Parent #5 — stains+threads)
│   ├── maxwell_old.txt              # Game-format Maxwell (WHAT THE GAME CURRENTLY LOADS)
│   └── 01_dummy.txt, 02_dummy.txt, 03_dummy.txt
├── levels/
│   ├── maxwell.txt                  # Manifest: loads maxwell_old.txt (NO baked: line — ROLLED BACK)
│   ├── intro.txt
│   └── mathematics/basel_problem/
│       └── basel_euler_proof.txt    # Baker-format Basel (Parent #5 child — 7 robots, 6 stains)
├── baked/
│   ├── maxwell/                     # 8 PNGs (robots 3-4, 4 layers each)
│   └── basel/                       # 28 PNGs (robots 1-7, 4 layers each)
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md         # ⭐ THE LAW — read first
│   ├── UNDERSTANDING_MODE_PREBAKED_LATEX.md  # Stain+thread design handoff
│   ├── CORRIDOR_WRITER_PROMPT.md    # Wikipedia → corridor file prompt
│   ├── SESSION_2026-06-15_EVENING.md # Last working session before today
│   └── ... (previous sessions, briefs, reports)
└── *.png                             # Hologram portraits (Gauss_Electric-hologram.png, etc.)
```

---

## 12. ONE-PARAGRAPH SUMMARY FOR PARENT

You are Parent #6. Parent #5 just completed a massive pivot: live mathtext → pre-baked colored LaTeX PNGs. The baker works (36 PNGs baked, zero failures), the new understanding.py works, the baker-format corridors exist for Maxwell and Basel. What's missing: the `baked:` wiring from level manifests to runtime robots (DeepSeek tried it, failed, got rolled back — all code is now pure Opus). Also missing: a game-format Basel corridor so the Basel level is playable in-game. Three engine gaps remain from earlier parents (ship containment, joystick wiring, defeat plaques). Write the wiring brief and Basel corridor brief, one at a time. Do not let context loss corrupt the design — re-read section 1 before EVERY brief.

---

**END OF PROMPT — Nir will now tell you what to build first.**
