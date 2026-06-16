# 🧠 SESSION CONTEXT — June 16, 2026 EVENING

> **Project:** DESCENT QED engine
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`
> **Parent:** You are PARENT #6 (Opus 4.8). Read PARENT_HANDOFF_V3.md first.

---

## 🚨 READ THESE FIRST

1. **`PARENT_ESTATE/PARENT_HANDOFF_V3.md`** — THE LAW: game design, all modules, frame order, data objects
2. **THIS FILE** — today's session: what changed, what's broken, what remains

---

## 📦 WHAT EXISTED AT START OF DAY

**World Tier** — 8 modules: content_parser, palette, render, robots, corridor_builder, hub_builder, level_parser, app

**Gameplay Tier** — Briefs #9 (Combat), #10 (Arsenal), #11 (Understanding Mode - live mathtext), #12 (Hostages), #13 (Game State), #15 (Cockpit)

All built and flown. Game playable end-to-end (WIN-ONLY).

**Known issues:** defeat plaque white rectangle, ship wall containment not wired, T.16000M joystick not wired, face panel uses hologram images. Understanding Mode rendered everything in one flat white color — kindergarten mixing existed in data but was never rendered.

---

## 🎮 WHAT CHANGED TODAY

### THE BIG PIVOT: From live mathtext to pre-baked LaTeX PNGs

The original Understanding Mode used matplotlib's crippled mathtext (no per-symbol color, no advanced LaTeX). Parent #5 (Opus 4.8) designed a new architecture:

1. **Baker** (`deu/bake_corridor.py`) — offline tool. Reads a corridor `.txt` file with `\stain{}` and `\thread{}` markers, compiles via pdflatex → pdftocairo, emits transparent colored PNGs. Zero game dependencies. Standalone.

2. **Two color systems** (stains + threads):
   - **STAINS** — MACRO, sacred, span whole corridor. Background color washes behind concepts. Kindergarten mixing: red+blue=purple, yellow+red=orange, yellow+blue=green.
   - **THREADS** — MICRO, page-local. Foreground letter colors linking compact→expanded expressions. Auto-colored by baker.

3. **Corridor Writer** prompt — reusable child-Opus prompt for turning Wikipedia pages into corridor files in the new format.

### Files created/changed today:

| File | What | Author |
|------|------|--------|
| `deu/bake_corridor.py` | Baker tool (full stain+thread, `\colorbox` not `soul`) | Parent #5 + child |
| `corridors/maxwell.txt` | Baker-format Maxwell corridor (replaced old game format) | Parent #5 |
| `corridors/maxwell_old.txt` | Old game-format Maxwell (backup) | DeepSeek |
| `levels/mathematics/basel_problem/basel_euler_proof.txt` | Baker-format Basel corridor (6 stains, 7 robots, 28 layers) | Child Opus writer |
| `baked/maxwell/*.png` | 8 baked PNGs (robots 3-4, 4 layers each) | Baker |
| `baked/basel/*.png` | 28 baked PNGs (robots 1-7, 4 layers each) | Baker |
| `understanding.py` | Fog-and-glass flight: loads baked PNGs, fog+blur depth, minimap, fallback to render_rich | Parent #5 |
| `content_parser.py` | Added `understanding_dir: str = ""` to `RobotData` and `CorridorData` | DeepSeek |
| `level_parser.py` | Added `baked:` support to level manifests, propagates to all robots | DeepSeek |
| `levels/maxwell.txt` (manifest) | Updated: points to `maxwell_old.txt`, adds `baked: baked/maxwell` | DeepSeek |
| `corridors/basel_stub_deepseek.txt` | Game-playable stub for Basel (7 robots, placeholder combat) | DeepSeek |
| `levels/basel_deepseek.txt` | Level manifest for Basel stub with `baked: baked/basel` | DeepSeek |
| `app.py` | `LEVEL_MANIFEST` changed to `levels/basel_deepseek.txt` for testing | DeepSeek |
| `PARENT_ESTATE/UNDERSTANDING_MODE_PREBAKED_LATEX.md` | Full design handoff: stains+threads, baker spec, corridor format | Parent #5 |
| `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` | Reusable child-Opus prompt: Wikipedia → corridor files | Parent #5 |
| `PARENT_ESTATE/PARENT_PROMPT_5B_UNDERSTANDING_GAME_SIDE.md` | Game-side integration prompt (continuation of Parent #5) | DeepSeek |

### Key design decisions (Parent #5):
- **`\colorbox` not `soul`** — soul's `\hl` crashes on `\displaystyle` math. `\colorbox` handles it.
- **`pdftocairo` not `dvisvgm --png`** — MiKTeX's dvisvgm lacks PNG output. pdftocairo is cleaner.
- **Stains sacred, threads auto-colored** — stain colors never altered. Thread hues auto-assigned per page.
- **Nesting works** — `\stain{coupling}{ \thread{t1}{...} }` — stain contains thread.

---

## ✅ WHAT IS FULLY WORKING

- Baker: 0 failures on both Maxwell (8/8) and Basel (28/28)
- `baked:` manifest wiring: flows through `load_level` → `CorridorData` → `RobotData.understanding_dir`
- Understanding Mode: new `understanding.py` loads baked PNGs with fog+blur+pan+minimap+fallback
- All old game mechanics: flying, shooting, cockpit, game state, hostages — unchanged

---

## 🔴 WHAT IS BROKEN

### Bug 1 — Robot 1 (Leonhard Euler) not visible in Basel corridor

**Symptoms (description only, no diagnosis):**
- Ran `python app.py` with `LEVEL_MANIFEST = "levels/basel_deepseek.txt"`
- Flew into the Basel corridor
- Only 6 robots are visible in the corridor
- The visible robots show these names (in order): "Coefficient Matching", "The Product Over Roots", "The Series From Derivatives", "François Viète", "The Zeros of Sine", "Bernhard Riemann"
- These correspond to robots 2-7 in the corridor data file
- Robot 1 ("Leonhard Euler") is NOT visible anywhere in the corridor — not at the entrance, not further in, not when flying backward
- When pressing U near any robot, Understanding Mode opens and shows the baked PNG for that robot
- Pressing U near the first visible robot ("Coefficient Matching") shows robot 2's baked content ("If a function equals both...")

**Verified (code is correct at data level):**
- `corridors/basel_stub_deepseek.txt` has 7 ROBOT blocks (1-7), all correctly formatted
- `level_parser.load_level()` creates 7 `RobotData` objects with correct names, numbers, and `understanding_dir`
- `corridor_builder` creates 7 `Robot` runtime objects
- All 7 have valid positions (verified via Python — robot 1 at ~(80.8, 5.9, -8.3))
- `self._robots_data` count = 7, `self._robots` count = 7, `self._station_poses` count = 7
- Robot 0 in `_robots` list is "Leonhard Euler", number=1, `_defeated=False`
- `blocking_robot` should return robot 0 (first undefeated)
- Baked PNGs exist: `baked/basel/robot1_mathematician.png` (77KB, different from other robot PNGs)
- `app.py` correctly points to `levels/basel_deepseek.txt`

The bug is **runtime rendering only** — manifests as robot 1 invisible in the 3D corridor view despite existing in all data structures.

### Bug 2 — Defeat plaque still white rectangle
`corridor_builder.py:_draw_plaques` — unchanged since before today.

### Bug 3 — Ship wall containment
`hub.inside()` exists but is never called. Ship flies through walls.

### Bug 4 — T.16000M joystick not wired
`gamepads.pilot_command()` exists but never fed to `ship.update()`.

### Bug 5 — Face panel uses hologram images (blue-tinted)
Normal photos in Nir's Downloads folder, not in repo.

---

## 📂 CURRENT FILE INVENTORY

```
peaktogether-website/
├── app.py                           # Main loop (LEVEL_MANIFEST=basel_deepseek for testing)
├── understanding.py                  # NEW: fog-and-glass PNG loading with fallback
├── combat.py, cockpit.py, gamepad.py, game_state.py, hostages.py, robots.py
├── render.py, content_parser.py, palette.py
├── corridor_builder.py, hub_builder.py, level_parser.py
├── deu/
│   └── bake_corridor.py             # Baker: corridor.txt -> colored transparent PNGs
├── corridors/
│   ├── basel_stub_deepseek.txt       # DeepSeek game stub for Basel (DELETE when Opus builds real one)
│   ├── maxwell_old.txt               # Old game-format Maxwell (backup)
│   ├── maxwell.txt                   # Baker-format Maxwell (stains+threads)
│   └── 01_dummy.txt, 02_dummy.txt, 03_dummy.txt
├── levels/
│   ├── basel_deepseek.txt            # DeepSeek: manifest for Basel testing (DELETE later)
│   ├── maxwell.txt                   # Maxwell manifest (points to maxwell_old.txt, baked: baked/maxwell)
│   ├── intro.txt
│   └── mathematics/basel_problem/
│       └── basel_euler_proof.txt     # Baker-format Basel (6 stains, 7 robots, 28 layers)
├── baked/
│   ├── maxwell/                      # 8 PNGs (robots 3-4)
│   └── basel/                        # 28 PNGs (robots 1-7)
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md          # ⭐ THE LAW
│   ├── UNDERSTANDING_MODE_PREBAKED_LATEX.md  # Stain+thread design handoff
│   ├── CORRIDOR_WRITER_PROMPT.md     # Wikipedia → corridor file prompt
│   ├── PARENT_PROMPT_5B_UNDERSTANDING_GAME_SIDE.md
│   ├── SESSION_2026-06-16_EVENING.md # ⭐ THIS FILE
│   └── ... (previous sessions, briefs, reports)
└── *.png                             # Hologram portraits
```

---

## 🔧 GAME FILE NAMING CONVENTIONS

- **DeepSeek files** (temporary, DELETE when Opus builds real versions): marked with "DeepSeek" in filename and comments. Files: `corridors/basel_stub_deepseek.txt`, `levels/basel_deepseek.txt`
- **Old game format files** (backups): `corridors/maxwell_old.txt`
- **Baker-format files** (stain+thread, for `bake_corridor.py`): `corridors/maxwell.txt`, `levels/mathematics/basel_problem/basel_euler_proof.txt`
- **Level manifests**: `levels/*.txt`, format: `title:`, optional `baked:`, `corridors:` with indented paths

---

## 🚀 HOW TO RUN

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Currently loads Basel stub level. To switch back to Maxwell, change `LEVEL_MANIFEST` in `app.py:60` to `"levels/maxwell.txt"`.

**Baker:**
```
python deu\bake_corridor.py <corridor.txt> --out baked/<name> --dpi 600
```

Requires: pdflatex, pdftocairo (both in MiKTeX/TeX Live), Pillow (`pip install pillow`).

---

## 📋 WHAT PARENT #6 SHOULD DO

### Priority 1 — Fix robot 1 visibility bug (🔴)
The first robot in the Basel corridor is invisible at runtime despite correct data. See Bug 1 above for full symptoms.

### Priority 2 — Build the REAL Basel game corridor (🔴)
Replace DeepSeek's stub (`corridors/basel_stub_deepseek.txt`) with a proper game-format corridor. It must:
- Have 7 robots with the same names and numbers as the baker-format file (so Understanding Mode PNGs map correctly)
- Use the game's existing corridor format (CORRIDOR:, LEDGER:, SEGMENTS:, EXPLAIN_*, etc.)
- Be placed in `corridors/` with a proper name
- Have a corresponding level manifest in `levels/` with `baked: baked/basel`

### Priority 3 — Remaining engine gaps (🟡)
- Defeat plaque (corridor_builder.py:_draw_plaques — white rectangle)
- Ship wall containment (call hub.inside() after ship.update)
- T.16000M joystick wiring (gamepads.pilot_command() → ship.update)

### Priority 4 — Face panel images (🟢)
Replace blue-tinted hologram PNGs with normal photos (in Nir's Downloads).

---

**END OF SESSION — Nir will now tell Parent #6 what to build first.**
