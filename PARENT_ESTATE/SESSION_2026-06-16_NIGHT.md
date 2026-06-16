# 🧠 SESSION CONTEXT — June 16, 2026 NIGHT (end of day)

> **Project:** DESCENT QED engine
> **Repo:** `C:\Users\nir_s\peaktogether-website`
> **GitHub:** `https://github.com/strulovitz/peaktogether-website`
> **Today's Parents:** Parent #5 (Opus 4.8) + Parent #6 (Opus 4.8)
> **Builder:** DeepSeek V4 Pro (OpenCode)

---

## 🚨 READ THESE FIRST (on next wake-up)

1. **THIS FILE** — today's full session: what happened, what's done, what remains
2. `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — THE LAW: game design, all modules, frame order, data objects
3. `PARENT_ESTATE/PARENT_PROMPT_6_POST_ROLLBACK.md` — Parent #6 post-rollback handoff (still relevant for engine gaps)
4. `WORKFLOW.md` — updated session log

---

## 📦 WHAT EXISTED AT START OF DAY

**World Tier** — 8 modules: content_parser, palette, render, robots, corridor_builder, hub_builder, level_parser, app

**Gameplay Tier** — Briefs #9 (Combat), #10 (Arsenal), #11 (Understanding Mode - old live mathtext), #12 (Hostages), #13 (Game State), #15 (Cockpit). All built and flown. Game playable end-to-end (WIN-ONLY).

**Known issues:** defeat plaque white rectangle, ship wall containment not wired, T.16000M joystick not wired, face panel uses hologram images.

---

## 🔥 MAJOR PIVOT — PARENT #5: Live mathtext → Pre-baked LaTeX PNGs

Parent #5 (Opus 4.8) replaced Understanding Mode's live matplotlib rendering with an offline baker. The baker (`deu/bake_corridor.py`) compiles full LaTeX into transparent colored PNGs with a stain+thread color system. The game loads these PNGs instead of live-rendering.

**Baker works perfectly:** 0 failures on Maxwell (8/8) and Basel (28/28).

**Opus-authored files (PRESERVED):**

| File | Author | Description |
|------|--------|-------------|
| `deu/bake_corridor.py` | Parent #5 | Baker: corridor.txt → colored transparent PNGs |
| `understanding.py` | Parent #5 | Fog-and-glass flight, loads baked PNGs with render_rich fallback |
| `corridors/maxwell.txt` | Parent #5 | Baker-format Maxwell (stains+threads) |
| `levels/mathematics/basel_problem/basel_euler_proof.txt` | Parent #5 child | Baker-format Basel (6 stains, 7 robots, 28 layers) |
| `baked/maxwell/*.png` | Baker | 8 baked PNGs (robots 3-4) |
| `baked/basel/*.png` | Baker | 28 baked PNGs (robots 1-7) |
| `PARENT_ESTATE/UNDERSTANDING_MODE_PREBAKED_LATEX.md` | Parent #5 | Stain+thread design handoff |
| `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` | Parent #5 | Wikipedia → corridor file prompt |

---

## 🔴 DEEPSEEK ROLLBACK (beginning of session)

DeepSeek had previously attempted to wire the `baked:` manifest system himself (content_parser.py, level_parser.py, levels/maxwell.txt) and created Basel stubs. Robot 1 was invisible. **ALL DeepSeek changes were rolled back via git revert.** Repo restored to PURE OPUS CODE.

**Rollback commits:** 8764115, 1d45e36, 2bf7944, 0701d08 (4 reverts + restore)

---

## ✅ BRIEF #A — BAKED PNG WIRING (+ LOUD FALLBACK) — COMPLETE

Parent #6 wrote Child Brief #A. A child Opus 4.8 implemented 9 edits across 3 rounds:

### Round 1 — Edits 1-6 (wiring):
| Edit | File | What |
|------|------|------|
| 1 | `content_parser.py` | `understanding_dir: str = ""` added as trailing field to RobotData and CorridorData |
| 2 | `level_parser.py` | `_read_manifest` parses optional `baked:` line, resolves path, returns 3-tuple |
| 3 | `level_parser.py` | `load_level` injects `baked_dir` into every CorridorData and RobotData |
| 4 | `robots.py` | `@property understanding_dir` on runtime Robot |
| 5 | `levels/maxwell.txt` | Added `baked: ../baked/maxwell` |
| 6 | `understanding.py` | Loud fallback prints for both silent cases (no dir + file missing) |

### Round 2 — Edits 7-8 (robot_in_view selector):
| Edit | File | What |
|------|------|------|
| 7 | `combat.py` | New `robot_in_view(hub, ship)` — picks the robot the player is LOOKING AT for Understanding Mode |
| 8 | `app.py` | U key calls `robot_in_view` instead of `blocking_robot` |

**Bug found:** All robots showed robot 2's text. Root cause: `blocking_robot` always returned first undefeated — not the robot you're facing. Fixed by `robot_in_view`.

### Round 3 — Edit 9 (frame-1 auto-fire fix):
| Edit | File | What |
|------|------|------|
| 9 | `combat.py` | Changed `abs(lt) > FIRE_TH` to `lt > FIRE_TH` (signed comparison) |

**🔴 CRITICAL BUG FOUND & FIXED:** Robot 1 (Gauss Electric) was invisible in Maxwell, and robot 1 (Leonhard Euler) would have been invisible in Basel. Root cause: Xbox/XInput analog triggers rest at -1.0. `abs(-1.0) = 1.0 > 0.5` → frame-1 auto-fire → kills robot 1 before first frame drawn. One-operator fix: `abs(lt)` → `lt` (signed, not abs). **General fix — repairs robot 1 in all corridors, present and future.**

**Investigation methodology (3 runtime probes):**
1. data=5 stations=5 robots=5 → parser/placement healthy
2. All 5 positions spread cleanly → not co-location/mouth-clip
3. draw#1 defeated=True → caught the auto-fire on frame 1

**All Brief #A completion reports archived:**
- `PARENT_ESTATE/reports/COMPLETION_REPORT_BRIEF_A_EDITS_1_6.md`
- `PARENT_ESTATE/reports/COMPLETION_REPORT_BRIEF_A_EDITS_7_8.md`
- `PARENT_ESTATE/reports/COMPLETION_REPORT_BRIEF_A_ROBOT_1_FIX.md`

---

## 📋 BRIEF #B — BASEL GAME CORRIDOR — READY (not yet built)

Parent #6 wrote Child Brief #B (saved as `PARENT_ESTATE/briefs/CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md`). A child Opus will author:
- `corridors/basel.txt` — game-format Basel corridor (7 robots, 42 fizzles, LEDGER with stains-mirroring colors)
- `levels/basel.txt` — level manifest with `baked: ../baked/basel`

**Key facts for the child:**
- 7 robots, fixed order (matches baker spine for PNG mapping): Leonhard Euler, al-Khwarizmi, Karl Weierstrass, Brook Taylor, Francois Viete, Hipparchus, Bernhard Riemann
- 7 VULNERABLE_TO ids: euler, al_khwarizmi, weierstrass, taylor, viete, hipparchus, riemann
- 42 unique FIZZLE entries (7 robots × 6 wrong)
- Mathtext-only rule: NO \tfrac, \dfrac, \displaystyle, \emph
- NAME → portrait filename: NAME.replace(" ", "_") + "-hologram.png"
- **Open issue:** NAME vs portrait-filename mismatch (case/accents) — Nir must resolve. Currently no Basel portraits exist on disk.

---

## 📂 CURRENT FILE INVENTORY (end of day)

```
peaktogether-website/
├── app.py                           # LEVEL_MANIFEST = "levels/maxwell.txt"
├── understanding.py                 # Fog-and-glass PNG loading (Parent #5)
├── combat.py                        # Edit 9: abs(lt)→lt fix + robot_in_view (Edits 7,9)
├── content_parser.py                # understanding_dir field (Edit 1)
├── level_parser.py                  # baked: parsing + injection (Edits 2-3)
├── robots.py                        # understanding_dir property (Edit 4)
├── cockpit.py, gamepad.py, game_state.py, hostages.py, render.py
├── corridor_builder.py, hub_builder.py, palette.py
├── deu/
│   └── bake_corridor.py             # Baker (Parent #5)
├── corridors/
│   ├── maxwell_old.txt              # Game-format Maxwell (what the game loads)
│   ├── maxwell.txt                  # Baker-format Maxwell (stains+threads)
│   └── 01_dummy.txt, 02_dummy.txt, 03_dummy.txt
├── levels/
│   ├── maxwell.txt                  # Manifest: loads maxwell_old.txt, baked: ../baked/maxwell
│   ├── intro.txt
│   └── mathematics/basel_problem/
│       └── basel_euler_proof.txt    # Baker-format Basel (7 robots, 6 stains)
├── baked/
│   ├── maxwell/                     # 8 PNGs (robots 3-4)
│   └── basel/                       # 28 PNGs (robots 1-7)
├── PARENT_ESTATE/
│   ├── PARENT_HANDOFF_V3.md         # ⭐ THE LAW
│   ├── PARENT_PROMPT_6_POST_ROLLBACK.md
│   ├── PARENT_PROMPT_5B_UNDERSTANDING_GAME_SIDE.md
│   ├── UNDERSTANDING_MODE_PREBAKED_LATEX.md
│   ├── CORRIDOR_WRITER_PROMPT.md
│   ├── SESSION_2026-06-16_NIGHT.md  # ⭐ THIS FILE
│   ├── briefs/
│   │   ├── CHILD_BRIEF_A_BAKED_PNG_WIRING.md
│   │   └── CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md
│   └── reports/
│       ├── COMPLETION_REPORT_BRIEF_A_EDITS_1_6.md
│       ├── COMPLETION_REPORT_BRIEF_A_EDITS_7_8.md
│       └── COMPLETION_REPORT_BRIEF_A_ROBOT_1_FIX.md
└── *.png                             # Hologram portraits (Maxwell/dummy only)
```

---

## 🟢 WHAT IS FULLY WORKING

- Baker: 0 failures on Maxwell (8/8) and Basel (28/28)
- Baked PNG wiring: `baked:` manifest → CorridorData → RobotData → runtime Robot → understanding.py
- Understanding Mode: colored baked PNGs for robots 3 & 4 in Maxwell, render_rich fallback for others
- `robot_in_view`: U opens the robot you're LOOKING AT, not the combat gate
- Frame-1 auto-fire bug: FIXED (general fix for all corridors)
- All 5 Maxwell robots visible and working
- Combat, cockpit, game state, hostages — all working
- Git: clean, everything pushed

---

## 🟡 WHAT REMAINS TO DO

### Priority 1 — Brief #B: Basel game corridor (🔴)
- Child Opus needs to author `corridors/basel.txt` and `levels/basel.txt`
- Nir needs to resolve NAME vs portrait-filename mismatch (case/accents)
- Nir needs to create/provide 7 Basel hologram PNGs
- DeepSeek needs to wire `app.py` LEVEL_MANIFEST to `levels/basel.txt` for testing

### Priority 2 — Engine gaps (🟡, from PARENT_HANDOFF_V3)
- Ship wall containment (`hub.inside()` exists but never called)
- T.16000M joystick wiring (`gamepads.pilot_command()` exists but never fed to `ship.update()`)
- Defeat plaque white rectangle (`corridor_builder.py:_draw_plaques`)
- Face panel: replace hologram images with normal photos (Nir's Downloads)

### Priority 3 — Arsenal source question (🟡)
- Confirm how the 7 Basel weapons appear in the arsenal: auto-derived from VULNERABLE_TO ids, or manually declared? (Child Brief #B asks Nir this)

---

## 🚀 HOW TO RUN

```
cd C:\Users\nir_s\peaktogether-website
python app.py
```

Currently loads Maxwell (`LEVEL_MANIFEST = "levels/maxwell.txt"`). To test Basel later, change to `"levels/basel.txt"` after the child delivers.

---

## 🎯 DESIGN DECISIONS LOCKED TODAY

- Fizzle is FINAL: wrong missile → harmless 6s message, NO penalty (Nir's call, June 16)
- `abs(lt)` → `lt` fix is general: affects all corridors
- `robot_in_view` is additive/read-only: `blocking_robot` untouched for combat
- All names for Basel robots decided by Parent #6 (pending Nir's portrait-filename resolution)

---

## 📋 GIT LOG (end of day)

```
548549c Child Brief #B: Basel Problem Game Corridor
dafb4d4 Archive: Brief #A child completion reports (Edits 1-6, 7-8)
1c211c2 Completion Report — Brief #A: Robot 1 fix saga
183dbc3 Edit 9: Fix frame-1 auto-fire bug
3cfdf46 Child Brief #A Edits 7+8: robot_in_view selector
357d5fb Child Brief #A applied: Baked PNG Wiring (+ Loud Fallback)
9378405 Child Brief #A verbatim
7f1655d Fix: levels/maxwell.txt → maxwell_old.txt
d376b5a Design decision locked: fizzle is FINAL
e3a518c Session + Parent #6 post-rollback prompt
0701d08 Rollback: restore 3 files to pre-DeepSeek state
2bf7944 Revert DeepSeek Basel stub
1d45e36 Revert SESSION file
8764115 Revert WORKFLOW update
```

---

## ⭐ ON RESTART — Read these in order:

1. **THIS FILE** (`PARENT_ESTATE/SESSION_2026-06-16_NIGHT.md`)
2. `WORKFLOW.md` — updated session log
3. `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — THE LAW
4. `PARENT_ESTATE/briefs/CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md` — next brief to dispatch

---

**END OF SESSION — Good night, Nir! 🌙😴 Today was incredible! 🎉✨🚀**
