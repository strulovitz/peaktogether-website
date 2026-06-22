# 🚀 DESCENT QED — PARENT HANDOFF v3 (June 15, 2026)

> **TO:** Claude Opus 4.8 — You are the 3rd PARENT/ARCHITECT of this project.
> **FROM:** Nir (strulovitz) — the human, the boss. He pastes this to you.
> **BUILDER:** DeepSeek V4 Pro (OpenCode) — commits code, fixes bugs, wires hardware.
> **PASTE THIS ENTIRE DOCUMENT** into a fresh Claude conversation.

---

## 0. YOUR ROLE & THE BACKSTORY (READ FIRST)

You are the **PARENT / ARCHITECT**. You do NOT write full implementations. You write tightly-scoped **BRIEFS** for child Claude instances (fresh chats, no memory). Children write the actual code. DeepSeek (running on Nir's machine) commits it, tests it, fixes bugs, and reports back to Nir.

**THE 2nd PARENT DIED.** The previous Opus session ran out of context, forgot the core game design, and annoyed Nir. He did not produce an updated handoff before dying. This document replaces him. You are the **3rd parent**. Do not repeat his mistakes.

**WHAT HAPPENED WITH THE 2nd PARENT:**
- He wrote Briefs #1-#8 (world tier) — all built and flown successfully.
- Then he wrote Brief #9 (Combat) — built, tested, flown. Works.
- For Brief #10, instead of writing the ARSENAL/WEAPONS brief, he wrote `render_rich` (a mixed prose+math text renderer).
- For Brief #11, instead of writing the GAME_STATE/HOSTAGES brief, he wrote Understanding Mode (4-layer depth panels for reading robot explanations).
- **The ORIGINAL Brief #10 (Weapons/Arsenal) and ORIGINAL Brief #11 (Game State/Hostages) were NEVER written and NEVER built.**

**WORKFLOW LOOP:** You write a Brief → Nir pastes it into a fresh child Claude → child writes the module → Nir/DeepSeek test it → they report back → you write the next Brief. Nir tests EVERY module before reporting to you. Reports describe code that ALREADY WORKS ON SCREEN.

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

**RESOLVED DESIGN QUESTION (June 16, 2026 — Nir's decision):** What happens when the player fires the WRONG mathematician? **Harmless fizzle message appears for 6 seconds. FINAL. No penalty.** The player is a couple learning together — punishment has no place here. The thinking IS the gameplay.

---

## 2. TECH STACK & ENGINE CANON

- **Python 3.12**, pygame + PyOpenGL. Legacy fixed-function OpenGL (no shaders).
- **Repo:** `https://github.com/strulovitz/peaktogether-website` (local: `C:\Users\nir_s\peaktogether-website`)
- **World:** Grey rocky ATRIUM (big faceted sphere interior) → N doorways via FIBONACCI SPHERE distribution → each doorway leads to a BENT CORRIDOR → ends in a BLUE CAVERN (hostage room).
- **Coordinates:** right=+X, up=+Y, forward=-Z. Quaternions [w,x,y,z] numpy.
- **Ship:** `.pos` (vec3), `.q` (quaternion). `ship.update(dt, keys)`, `ship.apply_view()`.
- **Fog:** `set_fog(start=40, end=140, color=palette.CLEAR_COLOR)`
- **Mathtext-only rule:** `\frac`, `\sum`, `\geq` ALLOWED. `\tfrac`, `\dfrac`, `\binom`, `\underbrace` FORBIDDEN. (matplotlib's built-in mathtext, no full LaTeX)

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

## 3. WHAT IS BUILT & FLOWN (Modules 1-8 + Briefs #9, #10, #11)

### WORLD TIER (all complete, tested, committed):

| Module | File | What it does |
|--------|------|-------------|
| **content_parser** | `content_parser.py` | Parses corridor fixture `.txt` files → `CorridorData` objects. Raises `ParseError` on bad input. Uses a tokenizer (`_tokenize()`) producing `(type, keyword, arg, body, lineno)` tuples. |
| **palette** | `palette.py` | ColorLedger. Maps opaque keys → RGBA colors. `CLEAR_COLOR`, `WORLD_EDGE`, `ATRIUM_SHELL`, etc. |
| **render** | `render.py` | Core GL. `init_gl()`, `TexCache`, `Ship` class, `quat_look_along()`, `quat_normalize()`, `quat_mul()`, `set_fog()`, wall queue + `flush_walls()`, `begin_2d()`/`end_2d()`, `draw_text_mathtext_2d()`, `render_rich()`, `ship_right()`, `ship_up()`, billboards, GL display lists. |
| **robots** | `robots.py` | `Robot` class (non-humanoid faceted hull, Larson scanner eye, hologram portrait, explosion). `RobotData` dataclass. `Robot.is_defeated()`, `Robot.play_defeat()`, `Robot.position`, `Robot.required_technique_id`. |
| **corridor_builder** | `corridor_builder.py` | Builds `CorridorGeometry` from `CorridorData`: bent tube with stations, robot positions, blue cavern at end. `hostage_positions()` returns 3 world-space points (NOT drawn yet). |
| **hub_builder** | `hub_builder.py` | Builds `HubGeometry`: grey atrium sphere + Fibonacci-sphere doorways → corridors. `spawn_pose()`, `door_poses()`, `inside(point, margin)`, `update()`, `draw_world()`, `draw_robots()`, `draw_labels()`. `hub.corridors` list. |
| **level_parser** | `level_parser.py` | Loads level manifest → `Level` (iterable of `CorridorData`). `discover_levels()`. |
| **app** | `app.py` | Minimal integration. Canonical frame loop. Loads `levels/maxwell.txt`. Spawns ship. WASD/arrows flight. ESC to quit. **T.16000M joystick FULLY WIRED for flight ✅ (Briefs #J1 + #J1B, June 17-18 — analog 6-DOF + fire trigger + engineer button).** |

### GAMEPLAY TIER (Briefs #9, #10, #11 — BUILT):

| Brief | File | What it does |
|-------|------|-------------|
| **#9 COMBAT** | `combat.py` | Fire missiles at robots. ID matching (opaque string IDs). Auto-face explosion on correct hit. Fizzle message on wrong hit (6s). Temporary `[`/`]` cycle, SPACE to fire. `Combat.blocking_robot(hub)` static method. |
| **#10 RENDER_RICH** | `render.py` | `render_rich()` — mixed prose+math, multi-line text with value-arcs. Gaussian blur. Built to power Understanding Mode. |
| **#11 UNDERSTANDING** | `understanding.py`, `gamepad.py` | 4-layer depth panels (mathematician/physicist/biologist/engineer). Press U near a robot. Mouse wheel = depth, mouse = pan, CTRL = engineer unlock. Xbox right-stick pans. |

### CORRIDOR FIXTURES ON DISK:

| File | Description |
|------|-------------|
| `corridors/01_dummy.txt` | 2 placeholder robots |
| `corridors/02_dummy.txt` | 1 placeholder robot |
| `corridors/03_dummy.txt` | 1 placeholder robot |
| `corridors/maxwell.txt` | 5 Maxwell equation robots (Gauss Electric, Gauss Magnetic, Faraday, Ampere, Maxwell) |
| `levels/intro.txt` | 3 dummy corridors (manifest) |
| `levels/maxwell.txt` | 1 Maxwell corridor (manifest) |

---

## 4. CORRIDOR FILE FORMAT (verbatim — children MUST match this)

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
FIZZLE gauss_m { Why Gauss Magnetic doesn't work on this robot... }
FIZZLE faraday { Why Faraday doesn't work... }
```

**The 4 EXPLAIN fields are REQUIRED.** The child that built Brief #9 invented wrong names (EXPLAIN_WHAT/WHY/HOW/SO) — was rejected. The correct names are above exactly.

**`VULNERABLE_TO` is a single-value line**, NOT a block. It's handled inside the tokenizer dispatch, alongside NAME, EYE, FIZZLE, etc.

**`FIZZLE <id>` is a BLOCK** — the body is the "why this doesn't work" prose.

**`[[ expr | value ]]`** syntax = value-arc for engineer layer. Only in EXPLAIN_ENGINEER.

---

## 5. KEY DATA OBJECTS (verbatim)

```python
CorridorData:
    .number: int
    .title: str
    .flavor: str
    .briefing_intro: str
    .entry_text: str
    .exit_text: str
    .robots: list[RobotData]     # in corridor order
    .ledger: ColorLedger          # this corridor's palette

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

Robot (runtime):
    .name: str
    .position: vec3
    .base_pos: vec3
    .required_technique_id: str   # @property → robot_data.required_technique_id
    ._robot_data: RobotData       # private, full data
    .is_defeated() -> bool
    .play_defeat()                # triggers explosion animation
    .update(dt, ship_pos)
    .draw()                       # opaque + emissive
```

---

## 6. WHAT REMAINS TO BUILD (the actual gaps)

### 🔴 ORIGINAL BRIEF #10 — WEAPONS / ARSENAL (NOT BUILT)
The couple needs a proper weapon system:
- **Girlfriend face-selection panel** — a 2D overlay showing mathematician FACE IMAGES (Gauss, Faraday, Ampere, Maxwell). The girlfriend player selects which mathematician-missile is loaded.
- **Missile projectiles** — visual effects (fly from ship to robot, reuse render primitives, NO new glyph rendering).
- **Retire the temporary `[`/`]` selector** — replace with the proper face panel.
- **Face PNGs exist** at repo root: `Gauss_Electric-hologram.png`, `Faraday-hologram.png`, `Ampere-hologram.png`, `Maxwell-hologram.png`, `Gauss_Magnetic-hologram.png`, `Dummy_Sentinel_Alpha-hologram.png`, `Dummy_Sentinel_Beta-hologram.png`

### 🔴 ORIGINAL BRIEF #11 — GAME STATE / HOSTAGES (NOT BUILT)
The corridor-as-gauntlet progression:
- After ALL robots in a corridor are defeated → path is clear → hostages appear/rescued
- Reaching/rescuing hostages = WIN condition for that corridor
- Hostage positions: `CorridorGeometry.hostage_positions()` already returns 3 world-space points (but no hostages are drawn anywhere yet)
- Win/lose conditions, corridor-cleared messaging
- Level progression (beat corridor 1 → corridor 2 → etc. opens)

### 🟡 ENGINE INFRASTRUCTURE GAPS (3 things needed)

#### 1. Plain-text 2D renderer
Every child reinvents a hacky `_mt()` function to wrap English words in `\mathrm{...}`. The engine needs ONE function:
```python
# In render.py — add:
def draw_plain_text_2d(cache, text, x, y, color=(1,1,1), fontsize=18):
    """Accepts normal English strings. Handles escaping internally."""
```
After this exists, remove `_mt()` from `combat.py` and call the engine function.

#### 2. Ship wall containment
`hub.inside(point, margin)` already exists and works (returns True/False for any point). But nothing calls it. The ship flies through walls.
- Add containment call in `app.py` frame loop (after `ship.update`).
- Desired behavior: gentle teleport back inside (like invisible cushion). No punishment.

#### 3. T.16000M joystick wiring — ✅ DONE (June 17-18, Briefs #J1 + #J1B)
`gamepad.py`'s `GamepadManager.pilot_command()` is now wired into ship controls in the frame loop. Joystick is additive to keyboard (simultaneous use). Analog 6-DOF flight + fire trigger + engineer-reveal button all working. Nir confirmed in-game.

---

## 7. KNOWN BUGS

| Bug | Severity | Details |
|-----|----------|---------|
| HUD text escapes too aggressively | Low | `_mt()` in combat.py strips apostrophes, hyphens. Known, will be fixed by plain-text renderer (gap #1). |
| Ship flies through walls | Medium | Containment not enforced (gap #2). |
| ~~Joystick not wired~~ | ✅ FIXED | Wired June 17-18 (Briefs #J1 + #J1B). Analog flight + trigger + button. |
| Black screen on macOS | Info | Legacy GL profile issue. Documented in render.py. |

---

## 8. HOW THE PARENT SHOULD PROCEED

### STEP 1 — Confirm design decisions with Nir:
- Ask Nir: what happens on WRONG-mathematician shot? (Currently: harmless fizzle for 6 seconds. Is that final?)
- Ask Nir: should the 3 engine infrastructure gaps be separate child tasks, or parent-authored quick patches?

### STEP 2 — Write the missing briefs:
1. **Brief #10 (ORIGINAL) — WEAPONS/ARSENAL**: Face-selection panel, missile projectiles, replace `[`/`]` with proper UI
2. **Brief #11 (ORIGINAL) — GAME STATE/HOSTAGES**: Corridor progression, hostage rescue, win/lose conditions

### STEP 3 — Handle engine infrastructure:
Either write small parent patches, or dispatch as tiny child briefs.

### BRIEF TEMPLATE (every brief follows this):
1. TITLE + one-line purpose
2. FRESH-CHAT GATE: child's first action = ask Nir to paste SPECIFIC real files
3. PRIME LAW (mathematics-blindness) restated
4. WHAT TO BUILD: public interface / locked signatures
5. ENGINE CANON: canonical frame order + CARDINAL FLUSH TRAP
6. WHAT YOU MUST NOT DO: scope fence
7. A `*_demo.py` spec for Nir to test
8. COMPLETION REPORT template

### BRIEF WRITING PRINCIPLES:
- **Paste verbatim code** the child needs — NEVER let a child hallucinate APIs. If a brief says "the robot has a `fizzles` field", paste the actual Python definition of `fizzles`.
- **Fence scope hard.** "You build ONE concern. If you need something from another module, REQUEST it from the parent — do NOT edit that module."
- **Use `render.quat_look_along()`** — never let a child reinvent quaternion math.
- **No flush changes.** A child must NOT add, move, or remove `flush_walls` calls.

---

## 9. HOW TO RUN (for Nir)

```powershell
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, `[`/`]` cycle weapon, SPACE fire, U = Understanding Mode (when near robot), ESC = quit.

---

## 10. ONE-PARAGRAPH SUMMARY FOR PARENT

You are building a 6-DOF Descent-style game where a couple flies through mathematics corridors to rescue hostages at the end. Robots block the way and must be destroyed by firing the correct mathematician-missile at them. Reading the robot's hologram tells the player which mathematician is required — reading alone does nothing; the player must think and choose. The engine is mathematics-blind (matches opaque IDs only). The world tier (8 modules) is complete and flyable. The gameplay tier started: combat (#9) and Understanding Mode (#11) are built. The original weapons/arsenal (#10) and game state/hostages (#11) briefs were never written by the 2nd parent. The three earlier engine infrastructure gaps (plain-text renderer, ship containment, joystick wiring) are now ALL FIXED. Write the remaining briefs, one per child, testing each before proceeding. Do not let context loss corrupt the design — re-read section 1 before EVERY brief.

---
**END OF HANDOFF — Nir will now tell you what to build first.**
