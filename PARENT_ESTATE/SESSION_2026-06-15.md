# 🧠 SESSION CONTEXT — June 15-16, 2026 (late night → tomorrow morning)

> **Project:** DESCENT QED engine (in `peaktogether-website` repo)
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`

---

## 🎮 WHERE WE ARE RIGHT NOW

**Brief #9 (COMBAT) — BUILT & FLOWN**
- Fire missiles at robots, match IDs, defeat or fizzle
- Temporary `[`/`]` selector, SPACE to fire
- Auto-face explosion on correct hit
- Maxwell corridor (5 robots, Gauss→Faraday→Ampere→Maxwell)
- HUD shows "VULNERABLE TO:" and "LOADED:"
- Bug: HUD text escapes too aggressively (known, parent needs to fix)

**Brief #10 (render_rich) — BUILT**
- `render_rich()` — mixed prose+math, multi-line, value-arcs, Gaussian blur
- Lives in `render.py`, nothing else touched
- Foundation for Understanding Mode

**Brief #11 (Understanding Mode) — BUILT & FLOWN**
- Press U near a robot → 4-layer depth panels (mathematician/physicist/biologist/engineer)
- Mouse wheel = depth, mouse = pan, CTRL = jump to engineer + unlock arcs
- Xbox right-stick pans (confirmed: axis 2=left/right, axis 3=forward/back)
- All bugs fixed: scroll direction, arc shape, CTRL behavior, axis mapping, arc position
- Files: `gamepad.py` (verbatim Bible GamepadManager), `understanding.py`, `app.py`

---

## 🔴 WHAT IS NOT YET BUILT (from original PARENT HANDOFF)

| Original Brief | What | Status |
|---------------|------|--------|
| #9 COMBAT | Fire/match/fizzle | ✅ DONE |
| #10 ARSENAL / WEAPONS | Girlfriend face-selection panel, missile projectiles, weapon cycling with images | ❌ Parent replaced with `render_rich` |
| #11 GAME_STATE | Corridor progression, HOSTAGES at corridor end, win/lose/"corridor cleared" | ❌ Parent replaced with Understanding Mode |

**Also missing:**
- T.16000M joystick NOT wired to ship flight (code exists in gamepad.py, never connected in app.py)
- Ship flies through walls (hub.inside() exists but no containment)
- No plain-text renderer (every child reinvents `_mt()`)

---

## 📋 NEXT STEPS FOR THE PARENT

1. **Write Brief #10 (original): WEAPONS / ARSENAL**
   - Girlfriend face-selection panel with face images (gauss.png, faraday.png, ampere.png, maxwell.png)
   - Missile projectiles that fly from ship to robot
   - Retire temporary `[`/`]` selector, replace with proper panel
   - Face images are in Downloads: gauss.png, faraday.png, ampere.png, maxwell.png
   - The robot hologram loads `<Name>-hologram.png` — same faces but blue tint

2. **Write Brief #11 (original): GAME_STATE / HOSTAGES**
   - After all robots in a corridor are defeated, hostages appear/rescued
   - Corridor cleared → win condition
   - Hostage positions: `CorridorGeometry.hostage_positions()` returns 3 world-space points
   - Hostages are NOT drawn anywhere yet (only data exists)

3. **Wire T.16000M joystick** — `gamepads.pilot_command()` already returns pitch/yaw/roll/thrust. Just needs to be added to ship.update in app.py.

4. **Engine infrastructure** (parent patches, not child briefs):
   - Ship wall containment (hub.inside exists, just call it)
   - Plain-text 2D renderer (stop reinventing _mt())

---

## 🔑 KEY FILES FOR THE PARENT (verbatim truth)

| File | Purpose |
|------|---------|
| `PARENT_ESTATE/DESCENT_QED_PARENT_HANDOFF.md` | Section 2 (game design), Section 6 (remaining briefs #9-#10-#11) |
| `PARENT_ESTATE/INTERFACES_v0.1.md` | Original 10-module plan, data objects, corridor format |
| `app.py` | Frame loop (where weapons/game_state get wired) |
| `combat.py` | Combat class, blocking_robot, fire/match |
| `robots.py` | Robot class, position, is_defeated/play_defeat |
| `corridor_builder.py` | hostage_positions(), get_robots(), stations() |
| `render.py` | render_rich, draw_texture, begin_2d/end_2d, quat helpers |
| `gamepad.py` | GamepadManager (verbatim Bible), pilot_command(), manipulator_right_stick() |
| `understanding.py` | UnderstandingMode (what Brief #11 became) |

---

## 📂 REPO LAYOUT

```
peaktogether-website/
├── app.py                    ← main game loop
├── combat.py                 ← Brief #9
├── render.py                 ← Brief #10 (render_rich) + core engine
├── gamepad.py                ← Brief #11 (Bible GamepadManager)
├── understanding.py          ← Brief #11 (4-layer panels)
├── content_parser.py         ← corridor file parser
├── palette.py                ← color ledger
├── robots.py                 ← robot hulls/holograms
├── corridor_builder.py       ← one corridor's geometry
├── hub_builder.py            ← central atrium + all corridors
├── level_parser.py           ← level manifest loading
├── corridors/
│   ├── 01_dummy.txt          ← 2 placeholder robots
│   ├── 02_dummy.txt          ← 1 placeholder robot
│   ├── 03_dummy.txt          ← 1 placeholder robot
│   └── maxwell.txt           ← 5 Maxwell equation robots
├── levels/
│   ├── intro.txt             ← 3 dummy corridors
│   └── maxwell.txt           ← 1 Maxwell corridor
├── PARENT_ESTATE/
│   ├── DESCENT_QED_PARENT_HANDOFF.md    ← THE LAW
│   ├── INTERFACES_v0.1.md
│   ├── briefs/             ← all child briefs
│   ├── reports/            ← completion reports
│   ├── PARENT_REPORT_BRIEF_11_POST_FLIGHT.md
│   └── PARENT_NOTE_BRIEF_10_11_SPLIT.md
└── WORKFLOW.md
```

---

## 🧪 HOW TO RUN

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, `[`/`]` cycle weapon, SPACE fire, U = Understanding Mode.

Hologram PNGs for Maxwell corridor are in repo root (Gauss_Electric-hologram.png, etc.)
