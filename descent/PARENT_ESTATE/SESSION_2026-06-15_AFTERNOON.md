# 🧠 SESSION CONTEXT — June 15, 2026 AFTERNOON (Brief #10 built, 3 bugs found)

> **Project:** DESCENT QED engine
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`

---

## 🚨 START HERE — READ THESE FIRST (4th parent)

**Before reading this file**, the 4th parent MUST read this document which
contains the FULL game design, architecture, data objects, corridor format,
canonical frame order, and list of all modules:

👉 **`PARENT_ESTATE/PARENT_HANDOFF_V3.md`** — THE LAW. Game design (section 1),
tech stack + frame order (section 2), all 11 built modules (section 3),
corridor file format (section 4), data objects (section 5). Read it first.

**This afternoon file** covers ONLY what happened TODAY: Brief #10 built,
3 bugs found by Nir, and what the 4th parent still needs to build. It
assumes you have already absorbed PARENT_HANDOFF_V3.md.

---

## 📦 WHAT WAS ALREADY BUILT BEFORE TODAY (summary)

### World Tier — 8 modules (all complete, tested, flown):
| # | Module | File | What |
|---|--------|------|------|
| 1 | content_parser | `content_parser.py` | Parses corridor `.txt` files → `CorridorData` |
| 2 | palette | `palette.py` | ColorLedger (opaque keys → colors) |
| 3 | render | `render.py` | Core GL: Ship, TexCache, quat helpers, wall queue, 2D text, fog |
| 4 | robots | `robots.py` | Robot class (hull, scanner, hologram, explosion) |
| 5 | corridor_builder | `corridor_builder.py` | Builds CorridorGeometry from CorridorData |
| 6 | hub_builder | `hub_builder.py` | Builds HubGeometry: atrium + doorways + corridors |
| 7 | level_parser | `level_parser.py` | Loads level manifest → Level (list of CorridorData) |
| 8 | app | `app.py` | Minimal integration, canonical frame loop, WASD/arrows flight |

### Gameplay Tier — built before today:
| Brief | File | What |
|-------|------|------|
| #9 COMBAT | `combat.py` | Fire/match/fizzle, auto-face, text HUD |
| #11 UNDERSTANDING | `understanding.py`, `gamepad.py` | 4-layer depth panels (U near robot) |

### Corridor fixtures on disk:
`corridors/01_dummy.txt`, `02_dummy.txt`, `03_dummy.txt`, `maxwell.txt`
Level manifests: `levels/intro.txt`, `levels/maxwell.txt`

---

## 📜 THE 3rd PARENT'S ONE REAL CONTRIBUTION — Content Authoring Architecture

Before writing Brief #10, Opus 4.8 produced one genuinely good design document:
**`docs/CONTENT_AUTHORING.md`** — the reusable "content-authoring child" brief.

This is how future Wikipedia pages (Basel Problem, etc.) get turned into game
corridors. Key ideas:
- A fresh child Claude interviews Nir page-by-page from Wikipedia, builds a
  mathematical concept hierarchy, picks ~7 concepts at the RIGHT ALTITUDE (no
  decomposing to elementary floor), chooses mathematicians + colors + faces
- The child does ALL the thinking and emits FINISHED corridor `.txt` files
- NO upfront cast list — each face/concept introduced AT ITS ROBOT, in context
- Kindergarten mixing law: primaries for ingredients, blends for combinations
- Corridor is a self-contained universe — same face can mean different things
  in different corridors
- Goal: correct large-resolution intuition (teen-driver standard), not mastery
- The brief template can be pasted into a fresh Claude anytime Nir wants a new
  Wikipedia subject turned into a game level

This document is durable — it survives parent context loss. The 4th parent
should read it before designing any future gameplay work, because it defines
how content gets authored.

---

## 🎮 WHAT WE BUILT TODAY — Brief #10 (Arsenal/Weapons)

The 3rd parent (Opus 4.8) wrote Brief #10, a child Claude built it, and I (DeepSeek)
merged it into the live code. Here's what landed:

### combat.py changes:
- **DELETED:** hardcoded module-level `ARSENAL` constant (the Maxwell-five list)
- **ADDED:** `build_arsenal(robots)` — derives weapons from the current corridor's
  robots. Returns `[{"id","name","png"}]`, de-duped by technique_id, first-seen,
  capped at 9. Mathematics-blind.
- **ADDED:** `current_corridor(hub)` — finds which corridor the blocking robot
  belongs to (multi-corridor support)
- **ADDED:** `_sync_arsenal(hub)` — rebuilds arsenal when corridor changes
- **REPLACED:** `handle_input` — new signature accepts `mouse_click_edge, mouse_x,
  mouse_y, gamepads`. Retires `[`/`]` (prev_edge/next_edge ignored). Xbox
  controller: Y/A/B/X = up/down/right/left grid nav, LB/RB = cycle, LT/RT = fire
  (all edge-detected). Mouse: click face to select. Keyboard SPACE still works.
- **MERGED:** `_fire` — adds projectile spawn at top, keeps existing match/mismatch
  resolve (correct id → defeat + auto-face, wrong id → 6s gentle fizzle)
- **MERGED:** `update` — adds projectile t-advance at top, keeps existing
  auto-face nlerp and fizzle timer
- **MERGED:** `draw_hud` — keeps existing text HUD (VULNERABLE TO / LOADED /
  fizzle panel) + adds 3x3 face panel grid (bottom-left, top-left origin).
  Uses `load_portrait(name)` for face textures, `draw_texture` for blit,
  `_draw_border` for selection highlight.
- **ADDED:** `draw_projectile_3d(cr, cu, texcache)` — world-space GL_LINES streak
  from ship to robot on fire. Yellow.
- **KEPT UNCHANGED:** `blocking_robot(hub)`, `_nlerp()`, `_mt()`, `_wrap()`

### app.py changes:
- Added mouse event capture (`MOUSEBUTTONDOWN`, button 1) in events loop (line 191)
- `mouse_click_edge` + `mouse_x/y` init before frame loop, reset after use
- `handle_input` call now passes `mouse_click_edge, mouse_x, mouse_y, gamepads`
- `draw_projectile_3d(cr, cu, texcache)` inserted between draw_labels and begin_2d

### Files committed:
- `combat.py`, `app.py`
- `PARENT_ESTATE/PARENT_HANDOFF_V3.md` (comprehensive handoff for 3rd parent)
- `docs/CONTENT_AUTHORING.md` (Opus 4.8's reusable content-authoring brief)
- `PARENT_ESTATE/briefs/CHILD_BRIEF_10_arsenal.md` (the brief the child built from)
- Hologram PNGs: `Ampere`, `Faraday`, `Gauss_Electric`, `Gauss_Magnetic`, `Maxwell`

### Test result:
`python app.py` launches and runs without errors. Face panel appears, weapons
auto-derive from the corridor's robots, controller + mouse + keyboard all work.

---

## 🔴 3 BUGS FOUND BY NIR AFTER TEST FLIGHT

### BUG 1 — Defeat plaque shows white rectangle instead of text

**Location:** `corridor_builder.py:324-336` (`_draw_plaques` method)

**What it does:** After a robot is defeated, a billboard "plaque" should appear
at the robot's position showing educational text — like a transparent "road sign"
the couple reads on the way back from the hostages. This is the EXPLAIN-level
text displayed in-world (NOT in Understanding Mode — simpler, just one layer).

**What's broken:** It renders as a SOLID WHITE RECTANGLE instead of readable text.

**Root cause (likely):** The code does:
```python
text = (getattr(rdata, "briefing_hint", "") or "—")[:36]
tex = texcache.get_mathtext(
    r"\mathrm{%s}" % text.replace(" ", r"\ "),
    color=text_rgb, fontsize=13,
)
```
Problems:
1. briefing_hint is truncated to 36 characters — may cut mid-word or mid-LaTeX
2. No special-character escaping (unlike `_mt()` in combat.py)
3. Uses `briefing_hint` (a short nudge), NOT the rich EXPLAIN text
4. The 36-char truncation before `\mathrm` wrapping means the closing `}` is
   always present, but the content may be garbled

**What Nir wants:** After a robot dies, display the EXPLAIN_MATHEMATICIAN text
(or similar educational content) as a semi-transparent billboard "road sign" at
the robot's position. Single layer only (no physicist/biologist/engineer depth —
that's Understanding Mode). Just a readable reinforcement on the way back.

**Key file:** `corridor_builder.py` — specifically `_draw_plaques()` at line 324.
The method already iterates defeated robots and draws billboards. It just needs
to use the correct text (EXPLAIN level, not brief hint), with proper escaping,
and without destructive truncation.

### BUG 2 — Face panel uses hologram images (blue-tinted), not normal photos

**Location:** `combat.py` — `draw_hud()` calls `load_portrait(weap["name"])`
which loads `*-hologram.png` (blue-tinted hologram versions).

**The problem:** Nir wants NORMAL face photos (not blue hologram versions) in the
weapons panel. The hologram PNGs are designed to look like glowing-blue holograms
(additive blending against black). The weapons panel needs the original portraits.

**The normal face images** are in Nir's Downloads folder (NOT in the repo yet):
- `gauss.png`, `faraday.png`, `ampere.png`, `maxwell.png`

**What needs to happen:**
1. Nir provides normal face PNGs → committed to repo under a clear naming scheme
   (e.g. `Gauss_Electric-portrait.png` or similar)
2. `combat.py` needs a SECOND portrait loader (or a parameter to `load_portrait`)
   that loads the NORMAL version instead of the hologram version
3. OR: the hologram PNGs are replaced with normal photos everywhere (including
   the robot hologram above the robot — but that might break the hologram look)

**Also: the panel layout.** Nir has uploaded reference images of how the spaceship
cockpit looks from the inside. The 3x3 grid should be styled to match that
interior design. Current layout is a bare grid in the bottom-left corner.

### BUG 3 — Ship flies through walls and robots (no containment)

**Location:** `hub_builder.py` has `HubGeometry.inside(point, margin) -> bool`
— it already WORKS. It checks whether a point is inside the atrium sphere or any
corridor segment. But nobody calls it to clamp the ship.

**What needs to happen:**
- After `ship.update(dt, keys)` in `app.py`, call `hub.inside(ship.pos, margin=1.0)`
- If outside: clamp ship back to last valid position
- Gentle behavior: teleport back (no bouncing, no damage, no punishment)
- Ship-to-robot collision also missing (fly through robots)

This was already listed as an engine infrastructure gap. Still not built.

---

## 📋 WHAT STILL NEEDS TO BE BUILT

| Task | Priority | Details |
|------|----------|---------|
| Fix defeat plaque (BUG 1) | 🔴 HIGH | `corridor_builder.py:_draw_plaques` — use EXPLAIN text, proper escaping, no truncation |
| Fix face panel images (BUG 2) | 🔴 HIGH | Load normal portraits (not holograms), match spaceship interior layout |
| Ship wall containment (BUG 3) | 🟡 MED | Call `hub.inside()` after `ship.update`, clamp if outside |
| Plain-text 2D renderer | 🟡 MED | `draw_plain_text_2d()` in render.py — stop reinventing `_mt()` |
| T.16000M joystick wiring | 🟡 MED | `gamepads.pilot_command()` exists, wire into ship.update in app.py |
| **Brief #11 (original) — GAME STATE** | 🔴 HIGH | Corridor progression, hostage rescue, win/lose, level transitions |
| Robot collision | 🟢 LOW | Ship should not pass through active (undefeated) robots |

---

## 🔑 ALL PROJECT FILES (for the 4th parent)

```
peaktogether-website/
├── app.py                    # main game loop (8 modules wired + Brief #9/#10/#11)
├── combat.py                 # Brief #9 + #10 merged (arsenal, face panel, projectiles)
├── render.py                 # core GL engine (Ship, TexCache, wall queue, 2D, fog)
├── gamepad.py                # GamepadManager (T.16000M pilot + Xbox manipulator)
├── understanding.py          # Brief #11: 4-layer depth panels (U near robot)
├── content_parser.py         # corridor .txt parser → CorridorData
├── palette.py                # ColorLedger
├── robots.py                 # Robot class + load_portrait(name)
├── corridor_builder.py       # CorridorGeometry builder (BUG 1: _draw_plaques)
├── hub_builder.py            # HubGeometry (atrium + doors + hub.inside())
├── level_parser.py           # level manifest loader
├── corridors/
│   ├── 01_dummy.txt          # 2 placeholder robots
│   ├── 02_dummy.txt          # 1 placeholder robot
│   ├── 03_dummy.txt          # 1 placeholder robot
│   └── maxwell.txt           # 5 Maxwell equation robots
├── levels/
│   ├── intro.txt             # 3 dummy corridors
│   └── maxwell.txt           # 1 Maxwell corridor
├── *.png                     # hologram portraits (blue-tinted)
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md  # ⭐ READ FIRST — full architecture + game design
│   ├── DESCENT_QED_PARENT_HANDOFF.md  # original v1 handoff (background)
│   ├── INTERFACES_v0.1.md    # original 10-module interface spec
│   ├── briefs/               # child briefs #1-#11 + patches
│   ├── reports/              # completion reports
│   ├── SESSION_2026-06-15_MORNING.md   # morning session (Brief #9/#11 context)
│   └── SESSION_2026-06-15_AFTERNOON.md # ⭐ THIS FILE
├── docs/
│   └── CONTENT_AUTHORING.md  # reusable Wikipedia→corridor child brief
├── index.html                # Peak Together website homepage
└── style.css                 # website styles
```

---

## 🚀 HOW TO RUN

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Controls: WASD/RF move, arrows rotate, Q/E roll, Shift boost, SPACE fire,
U = Understanding Mode near robot, ESC quit. Xbox: Y/A/B/X grid nav, LB/RB cycle,
LT/RT fire. Mouse: click face to select weapon.
