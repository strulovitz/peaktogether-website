# Peak Together -- Workflow for DeepSeek V4 Pro (OpenCode)

## Who's Who

| Role | Who | What |
|------|-----|------|
| **Architect** | ~~Claude Fable~~ Claude Opus 4.8 | Claude Fable banned for non-USA (June 2026). Opus 4.8 is the new architect. |
| **Builder** | DeepSeek V4 Pro (OpenCode, this is YOU) | Copies Bible, fills in details, fixes bugs |
| **Boss** | Nir (strulovitz) | Decides everything, talks to Claude Opus 4.8, manages the website |

## The BIBLE System

- **BIBLE/math_flyer.py** = Claude Fable's original code. NEVER MODIFY IT. Only Claude Fable can authorize changes.
- **Working copy** = The actual downloadable `.py` file. You work on THIS.
- If you find a bug in the Bible, tell Nir. He asks Claude Fable. Claude Fable authorizes the fix. THEN you apply it to BOTH the Bible and the working copy.
- Document every Bible bug in `BIBLE/BUGS_FOUND_<bible_file>_<timestamp>.md` so Nir can show Claude Fable.

## Project Structure

```
peaktogether-website/                # GitHub repo root = website root
├── index.html                       # Website homepage
├── style.css                        # Website global styles
├── components.js                    # Website header/footer loader
├── header.html                      # Shared navigation menu (DO NOT BREAK)
├── footer.html                      # Shared footer
├── images/                          # Website images
├── mathematics/                     # Website content pages (Riemann Hypothesis, etc.)
├── .htaccess                        # Dreamhost Apache config
├── .gitignore                       # Ignores __pycache__, *.pyc, *.log
├── WEBSITE_REDESIGN_FUSION_2026-06-18.md
│
└── descent/                         # GAME 1: Descent QED (ALL game files here)
    ├── app.py                       # Game entry point: cd descent && python app.py
    ├── combat.py, cockpit.py, ...   # All engine modules (16 .py files)
    ├── *_demo.py                    # Demo scripts (8 files)
    ├── test_*.py                    # Test scripts (3 files)
    ├── *-hologram.png               # Portrait images (14 files)
    ├── corridors/                   # Corridor game files
    ├── levels/                      # Level manifests + baker source files
    │   ├── basel.txt                # Manifest with per-corridor baked= paths
    │   └── mathematics/             # Baker source files by subject
    ├── baked/                       # Per-corridor baked PNG images
    │   ├── basel/euler_approach/    # Corridor 1 baked images
    │   ├── basel/euler_generalizations/  # Corridor 2 baked images (NOT YET BAKED)
    │   └── maxwell/test/            # Maxwell corridor baked images
    ├── deu/                         # Baker tool (bake_corridor.py)
    ├── BIBLE/                       # Bible files (Claude Fable's original code)
    ├── PARENT_ESTATE/               # Development architecture docs, briefs, sessions
    ├── WORKFLOW.md                  # THIS FILE — read me first every session!
    └── docs/                        # Game documentation
```

## How to Prompt Claude Fable (for Nir's reference)

Claude Fable lives on OpenRouter and has NO MEMORY between sessions. Every time you must tell him:

1. **Who you are**: "I am Nir, building Peak Together"
2. **What we did so far**: Brief summary of the project status
3. **The reference**: Link to Wikipedia section or specific illustration
4. **The request**: "Please make an interactive demo page for [topic]"
5. **Constraints**: "Follow our mathtext-only rule (no \\tfrac, \\dfrac, AMSMath). Use the same engine. The output should be a new @register_page class."

## Conventions

### Mathtext-Only Rule
- ALLOWED: `\frac`, `\sum`, `\geq`, `\cdots`, `\left(`, `\right)`, `\to`, `\infty`, `\mathbf`
- FORBIDDEN: `\tfrac`, `\dfrac`, `\underbrace`, `\binom` and ALL other AMSMath commands
- Reason: matplotlib's built-in mathtext has no full LaTeX installation

### Coding Conventions
- Python file: single-file, extendable via `@register_page` classes
- Each new Wikipedia concept = one new `Page` subclass
- Tab cycles between pages
- Engine code (camera, UI, LaTeX textures) -- DO NOT TOUCH
- Gamepad code goes ONLY in `GamepadManager` class
- Keyboard/mouse/controllers are additive (work simultaneously)

### HTML Editing on Windows
- **NEVER use PowerShell's Set-Content for HTML files** -- it corrupts UTF-8 emojis/special chars to Windows-1252
- **ALWAYS use Python** for any HTML file modifications:
  ```python
  with open(path, 'r', encoding='utf-8') as f: content = f.read()
  # ... do replacements ...
  with open(path, 'w', encoding='utf-8') as f: f.write(content)
  ```

### Dreamhost Deployment
- The website is hosted on Dreamhost (NOT GitHub Pages)
- Nir uploads via FileZilla from the local repo
- After renaming directories, manually delete the OLD directory on Dreamhost (FileZilla doesn't auto-delete)
- After renaming files, manually delete the OLD file on Dreamhost

## What We've Built So Far

### Harmonic Series Roadmap — ALL 11 PAGES COMPLETE 🎉

| Page | Class | Topic | Status |
|------|-------|-------|--------|
| 1 | HarmonicSeriesPage | Definition & Divergence | ✅ |
| 2 | ComparisonTestPage | Oresme ~1350 | ✅ |
| 3 | IntegralTestPage | H_N trapped between integrals | ✅ |
| 4 | PartialSumsPage | Partial Sums & Growth Rate: ln n + γ | ✅ |
| 5 | DivisibilityPage | cube-towers n² proof (ORIGINAL) | ✅ |
| 6 | InterpolationPage | Digamma + Ramanujan Summation | ✅ |
| 7 | JeepProblemPage | Crossing a desert (Fraction arithmetic) | ✅ |
| 8 | BlockStackingPage | Stacking blocks — Overhang = H_n/2 | ✅ |
| 9 | PrimesDivisorsPage | Euler primes + Dirichlet hyperbola | ✅ |
| 10 | CouponCollectorPage | Collecting coupons — E[T] = n H_n | ✅ |
| 11 | QuicksortPage | ∑ 2H_i = O(n log n) — Lomuto partition | ✅ |

**All 11 pages Bible-synced, zero bugs, committed & pushed.** Clean streak: 11/11 pages with zero runtime bugs.

### Next: Basel Problem (New Wikipedia Section)
- **Topic:** Basel problem — ∑ 1/n² = π²/6 (Euler, 1734)
- **Goal:** A new interactive demo page (or pages) for the Basel problem section of the Harmonic Series Wikipedia article
- **Process:** Nir will get Wikipedia text + Claude Fable's design → paste to me → I build
- **File:** Same `harmonic_series_mathematics.py` (or a new file if the file gets too large — Claude Fable's Rule #8: past ~2000 lines, propose folder+zip)

### Features Implemented
- 6-DOF quaternion camera (no gimbal lock)
- LaTeX rendering via matplotlib mathtext
- Keyboard flight controls (Descent-style)
- Mouse slider controls (Manipulate-style)
- Gamepad support: T.16000M joystick (pilot) + Xbox 360 (manipulator)
- Startup joystick calibration (60 frames)
- Radial and scalar deadzones
- GL display list caching for performance
- Crash logging to .log file
- Tab to cycle between pages

## Session Checklist (Read Me Every Time!)

1. Read this WORKFLOW.md
2. Check C:\Users\nir_s\peaktogether-website is up to date (`git pull`)
3. NEVER run commands that create/download large files without asking Nir
4. NEVER modify BIBLE/ without explicit permission
5. ONLY use Python (not PowerShell) for HTML edits
6. Tell Nir about ANY typo you find (don't silently fix or ignore)
7. After every meaningful change, commit and push
8. Ask Nir before doing ANYTHING you're unsure about

## ⚠️ Known Bugs / Gotchas (June 11, 2026)

### Dreamhost 500 Error on .py Downloads
- **Symptom:** Clicking the download link for `harmonic_series_mathematics.py` gives 500 Internal Server Error
- **Cause:** Dreamhost Apache tries to EXECUTE `.py` files as CGI scripts. Our file is a desktop PyOpenGL app — it crashes the server.
- **Fix (in `.htaccess`):**
  ```apache
  <FilesMatch "\.py$">
      SetHandler default-handler
      Header set Content-Disposition "attachment"
  </FilesMatch>
  ```
- **If it happens again:** Check `.htaccess` is uploaded to Dreamhost. If missing, re-upload it.

### `import random` — CHECK BEFORE BUILDING
- The QuicksortPage (and potentially future pages) needs `import random` at the top of the file.
- Working copy and Bible both have it added as of June 11. Verify it's still there if pages stop working.

### HTML Editing: ALWAYS use Python, NEVER PowerShell Set-Content
- PowerShell corrupts UTF-8 emojis to Windows-1252. Use Python `open(path, 'r', encoding='utf-8')` for all HTML edits.

## 🔴 SESSION LOG — June 11, 2026

### Events
1. **OpenCode crashed** mid-session. Restored context from WORKFLOW.md and git history.
2. **Fixed AGENTS.md** — removed stale StrulovitzGhost references. Memory now points to PeakTogether WORKFLOW.md only.
3. **Fixed WORKFLOW.md** — updated "What We've Built" table to include Pages 3-6 (built before crash).
4. **Pages 7-11 built** from Claude Fable's designs:
   - Page 7 (JeepProblemPage): Exact Fraction arithmetic, no rounding
   - Page 8 (BlockStackingPage): True-3D wooden blocks with COM arrows
   - Page 9 (PrimesDivisorsPage): Sieve + display list caching (~3600 dots)
   - Page 10 (CouponCollectorPage): Deterministic seeded random, Wikipedia chart matching
   - Page 11 (QuicksortPage): Lomuto partition with trace precomputation
5. **`import random` added** — QuicksortPage needed it; was missing from both files.
6. **Claude Fable got stuck on Quicksort GIF** — couldn't see the animation. Started a fresh conversation with updated CLAUDE_FABLE_CONTEXT.md. Successfully built without the GIF.
7. **All 11 pages committed & pushed.** Zero bugs across the entire build.
8. **BIBLE folder now contains:** math_flyer.py (synced), CLAUDE_FABLE_CONTEXT.md (Fable's memory), CLAUDE_FABLE_PAGE{4-11}_RESPONSE.md (verbatim responses), BUGS_FOUND_math_flyer_py_10Jun2026_16_48.md.

### Files Modified Today
| File | Change |
|------|--------|
| `BIBLE/math_flyer.py` | Pages 7-11 added, `import random` added |
| `BIBLE/CLAUDE_FABLE_CONTEXT.md` | Addendum updated: all pages complete |
| `BIBLE/CLAUDE_FABLE_PAGE{7-11}_RESPONSE.md` | Created — verbatim Claude Fable responses |
| `mathematics/.../harmonic_series_mathematics.py` | Pages 7-11 added, `import random` added |
| `mathematics/.../index.html` | Demo callouts for Pages 7-11 added |
| `WORKFLOW.md` | Pages table updated, session log added |
| `C:\Users\nir_s\.config\opencode\AGENTS.md` | Removed StrulovitzGhost, points to PeakTogether only |

### Current State
| Item | Status |
|------|--------|
| Harmonic Series Roadmap (11 pages) | ✅ Complete |
| Bible synced | ✅ All 11 pages |
| Website demo callouts | ✅ All 11 pages |
| Git (PeakTogether) | Clean, pushed |
| Known bugs | 0 |
| Next | Basel Problem — new Wikipedia section |

## 🔴 SESSION LOG — June 15, 2026 (FULL DAY — 3rd & 4th parents)

### ALL BRIEFS COMPLETE — Game is playable end-to-end! 🎉

**3rd Parent (Opus 4.8):**
- Wrote `PARENT_HANDOFF_V3.md` + `docs/CONTENT_AUTHORING.md`
- Brief #10 (Arsenal): built, merged, working

**4th Parent (Opus 4.8):**
- Brief #12 (Hostages): TWO real 3D humanoid figures, standing on cavern floor
- Brief #13 (Game State): rescue trigger, HOSTAGES RESCUED, corridor/level complete, WIN-ONLY
- Brief #15 (Cockpit): Descent-style polygon HUD, flat bar, face row, canopy beams
- `draw_plain_text_2d`: real font rasterizer, killed all raw LaTeX text bugs

**DeepSeek (me):** Merged everything, wired all modules, fixed orientation/nav/text bugs, deleted dead grid code, pushed 30+ commits.

**Full session files (read in order):**
- `PARENT_ESTATE/SESSION_2026-06-15_MORNING.md`
- `PARENT_ESTATE/SESSION_2026-06-15_AFTERNOON.md`
- `PARENT_ESTATE/SESSION_2026-06-15_EVENING.md` ⭐ (read this for next session)

**Remaining:** Face panel needs normal photos (in Nir's Downloads), ship wall containment, joystick wiring.

## 🔴 SESSION LOG — June 16, 2026 (Parent #5 + DeepSeek Rollback)

### 🔥 MAJOR PIVOT: Live mathtext → Pre-baked LaTeX PNGs (Parent #5 / Opus 4.8)

Parent #5 replaced Understanding Mode's live matplotlib rendering with an offline baker (`deu/bake_corridor.py`). The baker compiles full LaTeX (stains+threads color system) into transparent colored PNGs. The game loads these instead of live-rendering.

**Baker works perfectly:** 0 failures on Maxwell (8/8) and Basel (28/28).

**Opus-authored files (PRESERVED):**
| File | Author | Description |
|------|--------|-------------|
| `deu/bake_corridor.py` | Parent #5 | Baker: corridor.txt → colored transparent PNGs |
| `understanding.py` | Parent #5 | Fog-and-glass flight, loads baked PNGs with render_rich fallback |
| `corridors/maxwell.txt` | Parent #5 | Baker-format Maxwell (stains+threads) |
| `levels/mathematics/basel_problem/basel_euler_proof.txt` | Parent #5 child | Baker-format Basel (6 stains, 7 robots, 28 layers) |
| `baked/maxwell/*.png` | Baker | 8 baked PNGs |
| `baked/basel/*.png` | Baker | 28 baked PNGs |
| `PARENT_ESTATE/UNDERSTANDING_MODE_PREBAKED_LATEX.md` | Parent #5 | Stain+thread design handoff |
| `PARENT_ESTATE/CORRIDOR_WRITER_PROMPT.md` | Parent #5 | Wikipedia → corridor file prompt |

### 🔴 DEEPSEEK ROLLBACK

DeepSeek attempted to wire the `baked:` manifest system (content_parser.py, level_parser.py, levels/maxwell.txt) and created Basel stubs (corridors/basel_stub_deepseek.txt, levels/basel_deepseek.txt). Robot 1 was invisible. **ALL DeepSeek changes rolled back via git revert.** Repo is now PURE OPUS CODE.

### ✅ DESIGN DECISION LOCKED: Fizzle is FINAL
Nir confirmed (June 16): wrong-mathematician shot → harmless fizzle for 6 seconds. NO penalty. The couple is learning together.

### ⚠️ THE GAP: Baked PNGs exist but are NOT wired to the game
- `understanding.py` expects `robot.understanding_dir` — but no module sets it
- `levels/maxwell.txt` has NO `baked:` line
- No game-format Basel corridor exists
- Understanding Mode always falls back to `render_rich`

### 📋 Parent #6 Prompt
Written: `PARENT_ESTATE/PARENT_PROMPT_6_POST_ROLLBACK.md` — full project-wide handoff for the next Opus 4.8 parent. Covers: wiring brief (#A), Basel game corridor brief (#B), engine gaps (#C).

### ⭐ ON RESTART — Read these in order:
1. **THIS FILE** (WORKFLOW.md)
2. `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — THE LAW
3. `PARENT_ESTATE/PARENT_PROMPT_6_POST_ROLLBACK.md` — Parent #6 handoff
4. `PARENT_ESTATE/SESSION_2026-06-15_EVENING.md` — last working session
5. `PARENT_ESTATE/SESSION_2026-06-16_NIGHT.md` — today's full session ⭐

## 🔴 SESSION LOG — June 16, 2026 NIGHT (end of day — HUGE PROGRESS 🎉)

### Brief #A — Baked PNG Wiring (+ Loud Fallback) — COMPLETE ✅
Parent #6 wrote the brief. Child Opus implemented 9 edits across 3 rounds:
- **Edits 1-6:** understanding_dir field on dataclasses, baked: manifest parsing, injection into data objects, Robot property, loud fallback prints
- **Edits 7-8:** robot_in_view(hub, ship) selector — U now opens the robot you're FACING, not the combat gate
- **Edit 9:** frame-1 auto-fire fix — changed abs(lt)→lt in gamepad trigger detection (Xbox triggers rest at -1.0, abs(-1.0)=1.0>0.5 → auto-fire on frame 1)

### 🔴 CRITICAL BUG FOUND & FIXED: Robot 1 invisible in all corridors
3 runtime probes narrowed it from "rendering mystery" to "input bug": data=5 stations=5 robots=5 (parser healthy) → all 5 positions spread cleanly (not co-located) → draw#1 defeated=True (caught auto-fire on frame 1). General fix — repairs robot 1 in Maxwell AND Basel.

### Design Decision Locked: fizzle is FINAL
Wrong missile → harmless 6s message, NO penalty. The couple is learning together.

### Brief #B — Basel Game Corridor — READY (not yet dispatched)
Parent #6 wrote the brief. Child will author corridors/basel.txt + levels/basel.txt (7 robots: Euler, al-Khwarizmi, Weierstrass, Taylor, Viete, Hipparchus, Riemann — 42 fizzles). Pending: Nir resolves NAME vs portrait-filename mismatch.

### Files modified today
combat.py (robot_in_view + abs fix), app.py (U key), content_parser.py, level_parser.py, robots.py, understanding.py, levels/maxwell.txt

### New files created today
CHILD_BRIEF_A_BAKED_PNG_WIRING.md, CHILD_BRIEF_B_BASEL_GAME_CORRIDOR.md, 3 Brief #A completion reports, SESSION_2026-06-16_NIGHT.md, PARENT_PROMPT_6_POST_ROLLBACK.md

## 🔴 SESSION LOG — June 17, 2026 (Parent #7 — Engine Gaps & Polish 🛠️)

### Parent #7 dispatched 3 briefs:

| Brief | Topic | Status |
|-------|-------|--------|
| **#C1** | Ship collision/containment (walls + robot blocking) | ✅ COMPLETE (8 versions, v8 works) |
| **#P1** | Defeat plaque — use baked PNG instead of live mathtext | ✅ COMPLETE (fixed cos45 sizing) |
| **#J1** | T.16000M joystick wiring (true analog, additive) | 📋 Dispatched, pending child |

### Brief #C1 journey (the hard one):
v1-v3: various wall/robot approaches, all leaked
v4: "oranges in a box" — robot blocking FIXED, walls still leaked
v5: iterative constraint solve — still leaked
v6: inner-tube axis (broken, rolled back by Nir)
v7: clean nearest-centerline (walls only, child deleted robot code)
**v8: v4 robots + v7 walls combined — WORKS** ✅

### Files created/modified today:
| File | Change |
|------|--------|
| `containment.py` | New — wall confinement + robot blocking |
| `app.py` | 2 lines: import containment + resolve() call |
| `corridor_builder.py` | Replaced _draw_plaques — baked PNG + white frame |
| `corridors/basel.txt` | Child Brief #B delivered (7 robots, 42 fizzles) |
| `levels/basel.txt` | Basel level manifest |
| `PARENT_ESTATE/PARENT_PROMPT_7_ENGINE_GAPS.md` | Parent #7 handoff |
| `PARENT_ESTATE/briefs/CHILD_BRIEF_C1_*.md` | Ship collision brief |
| `PARENT_ESTATE/briefs/CHILD_BRIEF_P1_*.md` | Defeat plaque brief |
| `PARENT_ESTATE/briefs/CHILD_BRIEF_J1_*.md` | Joystick wiring brief |
| `PARENT_ESTATE/reports/COMPLETION_REPORT_BRIEF_C1_*.md` | C1 completion report |

### 🔴 REMAINING ISSUES (Nir's list, June 17):

| # | Issue | Description |
|---|-------|-------------|
| 1 | **Understanding Mode "conveyor belt"** | The road-sign panels flip forward↔backward / drift like a conveyor — wrong feel. Must move/depth correctly. |
| 2 | **Multiple corridors** | Only ONE corridor exists. Game needs several (e.g. different proofs of the Basel problem, each a corridor). Multi-corridor is untested and may bleed holograms/text between robots. |
| 3 | **T.16000M joystick** | Brief #J1 dispatched, awaiting child. |

### Current state:
- Ship containment: walls + robots ✅
- Defeat plaques: baked PNG with white frame ✅
- Basel corridor: 7 robots playable ✅
- Joystick: brief dispatched 🟡
- Understanding Mode conveyor belt: ✅ FIXED (Brief #U1, signed-distance model)
- Multiple corridors: 🔴
- Unified corridor-creation prompt: 🔴 (first attempt failed, redo tomorrow)

## 🔴 SESSION LOG — June 18, 2026 EVENING

### Brief #U1 — Understanding Mode conveyor belt — FIXED ✅
Child Opus replaced abs() distance with signed distance in understanding.py.
Signs behind the car are now CULLED (never drawn). Entry starts at ENTRY_FOCUS=-1.0
so sign 0 fits on screen. ESC inert in U-mode. Exit by reversing 1/3 past sign 0.
Bug found: instant-close on entry (ENTRY_FOCUS already past EXIT_THRESHOLD). Fixed
by measuring exit from ENTRY_FOCUS, not zero: EXIT_FOCUS = -1.333.
Nir confirmed: "it works perfectly."

### New baker-format corridor — euler_even_zeta.txt
Corridor-writer child produced baker file for "Euler's Sine Product and the Even
Zeta Values" (2nd Basel corridor). 7 robots, 6 stains. Saved to
corridors/euler_even_zeta.txt. BUT: only the baker file was produced. The old
CORRIDOR_WRITER_PROMPT.md only produces baker files, not game files.

### Unified corridor prompt — ATTEMPTED AND FAILED
Parent #8 wrote CORRIDOR_CREATOR_PROMPT.md (a "forever" general prompt for all 3
files). When Nir pasted it to a fresh child, the child did NOT ask what topic to
work on — it immediately started writing content. Root cause: no fresh-chat gate,
and ~400 lines of inline Basel reference files confused the child. Prompt deleted.

### Tomorrow's #1 priority:
Write a new parent prompt asking a fresh Opus to create a PROPER unified
corridor-authoring prompt with: (1) fresh-chat gate that asks for the topic first,
(2) produces all 3 files (baker + game + manifest), (3) reference files NOT inline
(child asks for them), (4) general/forever, not Basel-specific.

## 🔴 SESSION LOG — June 20, 2026 NIGHT

### Website redesign committed & pushed
Fusion AI redesign (from June 18) was sitting uncommitted. Committed: new index.html, style.css, 7 new images. Commit aa6a785.

### CORRIDOR_CREATOR_PROMPT_FOREVER — unified corridor prompt
Parent #9 produced a "forever" prompt for creating ALL 3 corridor files (baker + game + manifest).
- v1: 54 lines — too compressed, Nir rejected
- v2: 274 lines — proper detail, accepted
- Saved as `PARENT_ESTATE/CORRIDOR_CREATOR_PROMPT_FOREVER.md`
- Old baker-only prompt `CORRIDOR_WRITER_PROMPT.md` UNTOUCHED

### Basel corridor 2 — "Every Even Zeta by Symmetric Polynomials"
Child Opus (using FOREVER prompt) produced all 3 files:
- Baker: `levels/mathematics/basel_problem/basel_general.txt` (7 robots)
- Game: `corridors/basel_general.txt` (42 fizzles)
- Manifest: `levels/basel.txt` updated with 2nd corridor
- Commit 4f4a321
- Old baker-only file renamed to `corridors/OLD_euler_even_zeta.txt`

### 🔴 CRITICAL: Baked image collision
Both corridors have robots 1-7. Manifest has ONE `baked:` path. Images named by robot number only. Baking corridor 2 would OVERWRITE corridor 1's images. Architecture needs per-corridor baked directories.

### Parent Prompt #10 — Generic Folder Architecture
Written: `PARENT_ESTATE/PARENT_PROMPT_10_GENERIC_FOLDERS_2026-06-20_NIGHT.md`
NOT YET DISPATCHED. Mission: design generic per-corridor baked image folders, manifest format change, level_parser.py changes.

### 4 new portraits needed
Jacob_Bernoulli, Isaac_Newton, Albert_Girard, Pietro_Mengoli (Nir will get them).

### Nir's multi-corridor strategy
Build corridors one at a time. Test each individually. After several real corridors work, THEN add multi-corridor engine support. Test with real Basel corridors, NOT the toy Maxwell placeholder.

### 🔴 REPO REORGANIZATION PLANNED (the big one)
Nir's vision: Peak Together is a MULTI-GAME platform (Descent, Doom, Pinball, fighting games, RTS, etc.). Right now ALL Descent files are dumped in the repo root mixed with website files. Plan: move ALL Descent files (all .py, corridors/, levels/, baked/, deu/, BIBLE/, PARENT_ESTATE/, portraits, WORKFLOW.md, docs/) into a `descent/` folder. Website files (index.html, style.css, components.js, header.html, footer.html, images/, mathematics/) stay in root. Future games get their own top-level folders (doom/, pinball/, etc.). Parent #10 prompt covers both this AND the per-corridor baked image fix.

### ON RESTART — Read these in order:
1. **WORKFLOW.md** (this file)
2. `PARENT_ESTATE/SESSION_2026-06-20_NIGHT.md` — tonight's full session context ⭐
3. `PARENT_ESTATE/PARENT_PROMPT_10_GENERIC_FOLDERS_2026-06-20_NIGHT.md` — Parent #10 (PASTE TO FRESH OPUS)
4. `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — THE LAW

## 🔴 SESSION LOG — June 21, 2026 MORNING (DeepSeek solo — Missions A + B 🏗️)

### MISSION A COMPLETE — Repo Reorganization ✅

ALL Descent QED files moved into `descent/` folder using `git mv` (preserves history). **ZERO code changes needed** — imports, manifest paths, portrait loading all work unchanged because everything moved together as a unit.

**50 items moved:**
- 16 Python modules (app.py, combat.py, cockpit.py, etc.)
- 8 demo scripts (*_demo.py)
- 3 test scripts (test_*.py)
- 7 data folders (corridors/, levels/, baked/, deu/, descent_qed/, BIBLE/, docs/)
- 14 portrait PNGs (*-hologram.png)
- PARENT_ESTATE/ and WORKFLOW.md

**Website files stayed in root:** index.html, style.css, components.js, header.html, footer.html, images/, mathematics/, .htaccess, .gitignore, WEBSITE_REDESIGN_FUSION_2026-06-18.md

**New game launch command:** `cd descent && python app.py`

### MISSION B COMPLETE — Per-Corridor Baked Image Isolation ✅

Each corridor now has its own isolated baked-image subfolder. Images can NEVER collide.

**New folder convention:**
```
descent/baked/<subject>/<corridor_slug>/robotN_layer.png
```

**Existing images moved:**
- `baked/basel/*.png` → `baked/basel/euler_approach/`
- `baked/maxwell/*.png` → `baked/maxwell/test/`

**New manifest format (per-corridor `baked=` annotation):**
```
title: The Basel Problem
corridors:
  ../corridors/basel.txt            baked=../baked/basel/euler_approach
  ../corridors/basel_general.txt    baked=../baked/basel/euler_generalizations
```

**Backward compatible:** old manifests with global `baked:` line still work (intro.txt). Per-corridor `baked=` overrides the global fallback.

**level_parser.py changes:**
- `_read_manifest` now detects `baked=<path>` on corridor lines
- Returns per-corridor baked dirs alongside corridor paths
- `load_level` uses per-corridor baked if available, falls back to global

**Parser tested:** All 3 manifests (Basel, Maxwell, Intro) parse correctly with proper per-corridor baked paths.

### Files modified
| File | Change |
|------|--------|
| `descent/level_parser.py` | Per-corridor `baked=` parsing support |
| `descent/levels/basel.txt` | Per-corridor baked paths (euler_approach, euler_generalizations) |
| `descent/levels/maxwell.txt` | Per-corridor baked path (test) |
| `AGENTS.md` | Updated paths to descent/PARENT_ESTATE/ and descent/WORKFLOW.md |
| `descent/WORKFLOW.md` | Updated project structure + this session log |

### Current state
| Item | Status |
|------|--------|
| Repo reorganization (descent/ folder) | ✅ Complete |
| Per-corridor baked image isolation | ✅ Complete |
| Basel corridor 1 (Euler approach) | ✅ Playable, baked in euler_approach/ |
| Basel corridor 2 (Euler generalizations) | 🟡 Files saved, NOT YET BAKED |
| Parser tested | ✅ All 3 manifests load correctly |
| 4 new portraits needed | ⏳ Nir |
| Git | Pending commit |

### Baker command for corridor 2 (when ready):
```
cd descent
python deu/bake_corridor.py levels/mathematics/basel_problem/basel_general.txt --out baked/basel/euler_generalizations
```

## 🔴 SESSION LOG — June 13, 2026

### MAJOR: Claude Fable Banned — New Architect & Architecture 🏗️
- **Claude Fable** is now banned for non-USA nationals (USA government regulation, June 2026)
- **Claude Opus 4.8** is the new software architect 🎉
- New **Parent/Child workflow**: Opus 4.8 writes interface briefs → DeepSeek V4 Pro (OpenCode) implements → Nir reviews
- New document: `/PARENT_ESTATE/INTERFACES_v0.1.md` — **Descent QED Engine** interface specification
- This defines 10 modules (content_parser, palette, hub_builder, corridor_builder, robots, reading_system, render, weapons, game_state, app) with strict contracts
- Engine is "mathematics-blind" — all math/content enters via corridor files only
- Key rules: mathtext-only, no humanoid robots, greyscale world with chroma for meaning only, legacy GL, one engine concept per build

### Files Created Today
| File | Description |
|------|-------------|
| `PARENT_ESTATE/INTERFACES_v0.1.md` | Descent QED Engine full interface spec — Parts 1 & 2 complete (verbatim from Opus 4.8) |
| `PARENT_ESTATE/INTERFACES_v0.1.md` (Part 2) | Corridor file format v0.2, Fibonacci-sphere hub geometry, rendering specs, dummy fixture |
| `PARENT_ESTATE/briefs/CHILD_BRIEF_01_content_parser.md` | Child brief #1 — content_parser module (verbatim from Opus 4.8) |
| `corridors/01_dummy.txt` | Dummy test fixture for content_parser |
| `WORKFLOW.md` | Updated Who's Who + session log |

## Nir's Preferences
- Nir LOVES emojis -- use them abundantly in chat
- Nir does NOT know Python -- explain things simply
- The target audience is couples (boyfriend + girlfriend) on a gaming PC
- Verbatin Claude Fable descriptions for website callouts
- Be concise but cheerful
- Nir is the boss -- always ask before taking initiative
