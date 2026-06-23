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
├── docs/                            # Website/platform planning docs (Fusion prompts, hero-art style prompt, redesign notes)
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
| **#J1** | T.16000M joystick wiring (true analog, additive) | ✅ COMPLETE (June 17-18, + #J1B buttons) |

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
| 3 | **T.16000M joystick** | ✅ DONE — fully wired June 17-18 (Briefs #J1 + #J1B). |

### Current state:
- Ship containment: walls + robots ✅
- Defeat plaques: baked PNG with white frame ✅
- Basel corridor: 7 robots playable ✅
- Joystick: ✅ FULLY WIRED (June 17-18, Briefs #J1 + #J1B)
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

## 🔴 SESSION LOG — June 21, 2026 EVENING (Corridor 2 built & flying! 🎉)

### FOREVER Prompt — 13+ fixes from comprehensive audit
Full audit of the corridor-creator prompt against baker/parser code. Fixed: stain `$...$` rule, thread double-dollar trap, `--out` flag, per-corridor `baked=` manifest, bare PRIMARY, SEGMENTS notation, portrait location, bake command, engineer value-arc system, physicist intermediate steps, `\text{}` allowed, baker NAME vs game NAME, PROBLEM example.

### Basel Corridor 2 — "Euler's Symmetric-Polynomial Ascent" ✅
Two child attempts. First child (OLD) had no value arcs + stain errors. Second child had thread double-dollar errors (8 failures) — fixed mechanically by DeepSeek (regex, 38 patterns). Final: **28/28 baked, 0 failures**. Nir confirmed: "it works great."

- Baker: `levels/mathematics/basel_problem/basel_symmetric_proof.txt`
- Game: `corridors/basel_symmetric.txt`
- Baked: `baked/basel/symmetric_polys/` (28 PNGs)
- 7 robots: Euler, Newton, Girard, Waring, Bernoulli, Lindemann, Apery
- 7 new portraits added this session

### Current state
| Item | Status |
|------|--------|
| Basel corridor 1 (Euler's 1734 approach) | ✅ Playable |
| Basel corridor 2 (Symmetric-Polynomial Ascent) | ✅ Playable, Nir confirmed |
| FOREVER prompt | ✅ All fixes applied |
| app.py points to | `levels/basel_c2.txt` (corridor 2) |
| Next | Corridors 3-10 for Basel (~10 total) |

### ON RESTART — Read these in order:
1. **WORKFLOW.md** (this file)
2. `PARENT_ESTATE/SESSION_2026-06-22_EVENING.md` — latest session context ⭐
3. `PARENT_ESTATE/PARENT_HANDOFF_V3.md` — THE LAW

## 🔴 SESSION LOG — June 22, 2026 MORNING (DeepSeek V4 Pro — arc baking + corridor 3 🎉)

### Value-Arc Baking Support — NEW FEATURE ✅
The engineer layer's `[[ $expr$ | value ]]` arcs were NOT visible in-game because baked PNGs are flat images — the game can't know where expressions are. Fixed by adding TikZ arc rendering directly to the baker:
- `bake_corridor.py`: `[[ expr | value ]]` → `\valuearc{}{}`  (TikZ parabola + value label)
- Added `\usepackage{lmodern}` to fix font scaling at 600 DPI
- Arcs only load TikZ when `[[ ]]` patterns are present (zero overhead otherwise)
- Corridor 2 re-baked with 21 arcs across all 7 engineer layers — 28/28, 0 failures
- Nir confirmed: "i like it a lot!"

### FOREVER Prompt Updated ✅
Changed 3 places: children now include `[[ ]]` arcs in BOTH the baker file AND the game file (previously was "game-file-only"). Added warning: do NOT use bare `|` (pipe) inside `[[ ]]` — use `\lvert`/`\rvert` for absolute values.

### Failed Child Leftovers Cleaned Up ✅
Removed 54 leftover files from previous failed child attempts:
- `corridors/basel_generalization.txt` + `baked/basel/generalization/`
- `corridors/OLD_basel_general.txt` + `baked/basel/OLD_euler_generalizations/`
- `corridors/OLD_euler_even_zeta.txt`
- Baker source OLD files
- Fixed manifest: was showing 3 corridors, now correctly shows 2 (before corridor 3)

### Basel Corridor 3 — "The Riemann Zeta Function" ✅
Child Opus produced all 3 files. DeepSeek fixed child's `$[[ ]]$` dollar-sign wrapping bug (arcs were inside outer `$...$` in both files — would break TikZ and render_rich). Also replaced bare `|` with `\lvert`/`\rvert`.
- Baker: `levels/mathematics/basel_problem/basel_zeta_function.txt`
- Game: `corridors/basel_zeta.txt` (7 robots, 42 fizzles)
- Baked: `baked/basel/zeta_function/` (28 PNGs, 0 failures)
- 7 robots: Riemann, Mengoli, Cauchy, Oresme, Torricelli, Weierstrass, J. Bernoulli
- 3 new portraits added: Augustin-Louis_Cauchy, Nicole_Oresme, Evangelista_Torricelli
- Nir confirmed: "it works great!"

### Current state
| Item | Status |
|------|--------|
| Basel corridor 1 (Euler's 1734 approach) | ✅ Playable |
| Basel corridor 2 (Symmetric-Polynomial Ascent) | ✅ Playable, arcs re-baked |
| Basel corridor 3 (Riemann Zeta Function) | ✅ Playable, Nir confirmed |
| Value-arc baking (TikZ) | ✅ Working |
| FOREVER prompt (arc in both files) | ✅ Updated |
| app.py points to | `levels/basel_c3.txt` (corridor 3) |
| Git | Clean, pushed |
| Next | Corridors 4-10 for Basel (~10 total) |

## 🔴 SESSION LOG — June 22, 2026 EVENING (DeepSeek V4 Pro — corridors 4, 5, 6 🎉)

### Corridor 4 — "Euler's Formula and L'Hopital's Rule" ✅
7 robots: Euler, Weierstrass, Cauchy, Cotes, Riccati, l'Hopital, Tannery. 28/28 baked, 0 failures. 4 new portraits (Cotes, Riccati, l'Hopital, Tannery). Fixed child's `$[[ ]]$` wrapping, added missing baker arcs, replaced `\coth` with plain text in game file.

### Corridor 5 — "A Proof Using Fourier Series" ✅
7 robots: Euler, Parseval, Fourier, Argand, Riemann, Hilbert, Bessel. 28/28 baked, 0 failures. 5 new portraits. Child's output was CUT OFF mid-Robot 7 — Nir got the rest from child. Fixed bare `|` inside `[[ ]]` arcs with `\lVert`/`\rVert`.

### Corridor 6 — "Parseval's Identity & the Recurrence" ✅
7 robots: Parseval, Pythagoras, Hilbert, Fourier, Taylor, Euler, Riemann. 28/28 baked, 0 failures. 1 new portrait (Pythagoras). Fixed thread double-dollar trap in Robot 2 baker. Child forgot ALL arcs in baker — got fix from child (7 EXPLAIN_ENGINEER lines). Fixed bare `|` in Robot 1 game arcs.

### Recurring child bugs documented:
1. `$[[ ]]$` wrapping — arcs inside outer `$...$` breaks rendering
2. Baker arcs forgotten — children include arcs in game but not baker
3. Bare `|` inside `[[ ]]` — breaks arc regex (use `\lvert`/`\rvert`)
4. Thread double-dollar trap — `$\thread{}{$...$}$` crashes LaTeX

### Current state
| Item | Status |
|------|--------|
| Basel corridor 1 (Euler's 1734 approach) | ✅ Playable |
| Basel corridor 2 (Symmetric-Polynomial Ascent) | ✅ Playable, arcs re-baked |
| Basel corridor 3 (Riemann Zeta Function) | ✅ Playable |
| Basel corridor 4 (Euler's Formula & L'Hopital) | ✅ Playable |
| Basel corridor 5 (Fourier Series) | ✅ Playable |
| Basel corridor 6 (Parseval's Identity) | ✅ Playable |
| Value-arc baking (TikZ) | ✅ Working |
| FOREVER prompt | ✅ Updated (arcs in both files + pipe warning) |
| app.py points to | `levels/basel_c6.txt` (corridor 6) |
| Git | Clean, pushed |
| Next | Corridors 7-10 for Basel (~10 total) |

## ✅ CORRECTION (June 23, 2026 — per Nir)

**The T.16000M joystick is FULLY WIRED and works in-game.** Nir confirmed this directly.
Some stale notes had crept into the latest session file and current-state tables saying
the joystick was "dispatched / pending / never completed" — these are WRONG and now corrected.

- Joystick was wired June 17-18 via **Brief #J1** (analog 6-DOF flight, additive to keyboard,
  proportional) + **Brief #J1B** (trigger = fire missile, back-center button = engineer reveal).
- See `SESSION_2026-06-18_EVENING.md` (`Joystick | FULLY WIRED`) and
  `PARENT_PROMPT_8/9` which both describe it as complete.
- Files: `render.py` (`Ship.update6dof`) + `app.py` + `understanding.py` + `gamepad.py`.

**Engine infrastructure status:** plain-text renderer ✅, ship containment ✅, joystick ✅ — ALL DONE.
Remaining real work = more Basel corridors (7-10) + multi-corridor play test + next subject.

## 🔴 SESSION LOG — June 23, 2026 (DeepSeek V4 Pro — corridors 7 & 8 + website)

### Basel Corridor 7 — "Differentiation Under the Integral Sign" ✅
7 robots: Euler, Leibniz, al-Khwarizmi, Gregory, Taylor, Fubini, Mengoli. 28/28 baked, 0 failures.
3 new portraits (Leibniz, Gregory, Fubini; Mengoli already existed). Wired: `levels/basel_c7.txt` + app.py.
Fixed child bug: R5 Taylor had bare math after `\text{}` inside a stain (`\stain{...}{\text{...}\sum 1/n^2}`) → re-wrapped math in `$...$`.

### Basel Corridor 8 — "Cauchy's Elementary Descent" ✅
7 robots: Cauchy, de Moivre, Newton, Viète, Pythagoras, Archimedes, Gauss. 28/28 baked, 0 failures.
3 new portraits (de Moivre, Archimedes, Carl Friedrich Gauss; Cauchy/Newton/Viète/Pythagoras existed). Wired: `levels/basel_c8.txt` + app.py.
Fixed child bug: R4 Viète had bare `\stain{roots}{\cot^2 x_r}` (no inner `$`) → `\stain{roots}{$\cot^2 x_r$}`.
Child also FORGOT all value-arcs → got a fix from the child (7 baker + 6 game `EXPLAIN_ENGINEER` lines with `[[ ]]` arcs), re-baked 28/28.
Verified `\binom`, `\operatorname{Im}`, `\rightarrow`, `\csc`, `\cot` all render in matplotlib mathtext on this machine.

### NEW recurring child bug (tell every future child)
5. **Bare math after `\text{}` inside a `\stain{}`** — any math chunk after a `\text{...}` in a stain body must be wrapped in its own `$...$` (e.g. `\stain{roots}{$\cot^2 x_r$}`, NOT `\stain{roots}{\cot^2 x_r}`). Bare math lands in colorbox text-mode → "Missing $ inserted". Hit corridor 7 R5 and corridor 8 R4.

### Website work (peaktogether.me) ✅
- Added **About page** (`about/index.html`, reuses `.page` style) — a verbatim tribute to Nir's girlfriend; `<3` → ❤️. Added "About" as the last header-menu item.
- Home page: swapped Last Frontier image to couple+AI version (`images/hall-of-fame-last-frontier2.png`); deleted old `hall-of-fame-last-frontier.png`.
- **Footer rebuilt**: 11 social icons (Call, Website, Gmail, Email, YouTube, Facebook, X, Instagram, LinkedIn, TikTok, GitHub) with real links, desktop hover tooltips, and `@media (hover:none)` labels for phones. Removed old emoji icons + Home/Riemann footer links. Icons live in `images/social-media/` (full folder copied; 21 icons, 11 used).

### Current state
Basel corridors 1-8 all playable. `app.py` → `levels/basel_c8.txt`. Git clean, pushed.

### 📋 TO-DO (open items)
- **Corridor 10 — "Geometric proof":** investigate including the Wikipedia illustration inside Understanding Mode for robot 1. Pre-baked PNGs are LaTeX-text only today; showing a real diagram/image needs new engine support. → **Make an Opus parent and consult on the best technical options** before building corridor 10.
- T.16000M joystick: ✅ already done (see correction above).
- Multi-corridor play test (all corridors in one `levels/basel.txt`) still untested.

### Next
Corridor 9 = **"Proof assuming Weil's conjecture on Tamagawa numbers."**

## 🔴 SESSION LOG — June 23, 2026 (LATER) — Corridor 9 + ALL-NINE COMPLETE GAME 🏆

### Basel Corridor 9 — "Geometry Meets Arithmetic" (Weil/Tamagawa) ✅
7 robots: Weil, Tamagawa, Chevalley, Hensel, Gauss, Euler, Riemann. 28/28 baked. 4 new portraits
(Weil, Tamagawa, Chevalley, Hensel). Fixed child bugs: 6 bare-pipe arcs (`|c|`, `|SL_2(F_p)|`,
`|z|`, `|Re z|` → `\lvert/\rvert`), `CORRIDOR: 1` → `9`, 2 bare-math-in-stain (`\tau`, `\prod`),
stray `;` artifacts. The yellow stain (`the_constant`) was orphaned → child repainted π²/6 yellow in
robot 7 (baker + game SEGMENTS) so green = blue + yellow is visible. Nir confirmed.

### THE COMPLETE ALL-NINE GAME (Parent #10) 🏆🎉
Goal: "make the game complete — auto-load ALL NINE corridors." Diagnosed & fixed with the architect
over several rounds (DeepSeek pasted real code each round; never guessed an API):
- **Combat scoping** (`combat.py`): `current_corridor`/`blocking_robot` are now ship-position-based
  via `c.inside(ship.pos)` (were hard-wired to `corridors[0]`). Threaded `ship.pos` through
  `_sync_arsenal`, `_fire`, `update`, `handle_input`, both `robot_in_view` fallbacks,
  `_face_hit_test` (a 2nd `_sync_arsenal` site DeepSeek caught via grep), and `game_state_demo`.
  Fire/HUD/arsenal now follow the corridor the ship is actually in.
- **Readable signs** (`hub_builder` + `corridor_builder`): door labels + corridor-mouth titles use
  `render.get_plain_text_tex` (plain prose) and strip the "The Basel Problem -- " prefix.
- **Plain-text texture bug** (`render.py`): `pygame.font.render` leaves transparent bg = `(fg,0)`,
  which the alpha-ignoring 3D billboard rendered as a SOLID COLOUR BAR (no text). FIX (empirically
  proven headless): zero RGB where `alpha==0` → bg `(0,0,0,0)` like `latex_to_surface`. (The
  architect's first idea, `surf.fill`, was a proven no-op; DeepSeek's "Candidate B" was the real fix.)
- **Progress + finale** (`game_state.py`): per-corridor "PROOF COMPLETE N/9" flash + a
  "QUOD ERAT DEMONSTRANDUM / All nine proofs solved." finale when all 9 are cleared.
- `app.py` `LEVEL_MANIFEST` → `"levels/basel.txt"` (ALL NINE).

### RESULT 🎉
Nir flew the **WHOLE all-nine game end-to-end** and reached the **QED finale**. The Basel Problem
game is **COMPLETE**.

### Current state
| Item | Status |
|------|--------|
| Basel corridors 1-9 | ✅ all playable |
| All-nine multi-corridor game | ✅ COMPLETE — auto-loads, ship-scoped combat, readable signs, PROOF COMPLETE flash + QED finale |
| `app.py` points to | `levels/basel.txt` (ALL NINE) |
| Git | clean, pushed |
| Next | Nir's call (next subject / new game / the geometric-proof game / polish) |

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

## 🔴 SESSION LOG — June 23, 2026 (LATER) — Website: footer + PLANNED nav redesign

### Footer tagline updated ✅
`footer.html` tagline → "💯 Always free · 🔓 Always open-source · ✋ No signup, no payment, no ads, no catch. Made with love for two minds at a time." (shared footer = every page). Committed `fa3e4ef`, pushed. (Nir uploads via FileZilla to go live on Dreamhost.)

### PLANNED navigation redesign (TALKED THROUGH, decided, NOT YET BUILT) 📋
Fusion's "lobby of an arcade" IA. Full spec written to `descent/docs/MENU_SYSTEM.md` → section "PLANNED NAVIGATION REDESIGN". Summary:
- Top bar: `Home · The Arcade · The Mountains ▾ · How It Works · About  [▶ Play Free] [GitHub]`
- **The Mountains** = dropdown ONLY (not a page) → sub-dropdowns **Mathematics / Physics / Chemistry / Biology** (more later).
- **Mathematics** = sub-dropdown (not a page) → leaf link **Riemann Hypothesis** → `https://www.peaktogether.me/mathematics/Riemann_hypothesis/` (NO further submenu; its 9 paths live on that page now).
- Only the DEEPEST level links to real pages. This is a NEW **3-level** menu (today it's 2-level).
- New pages: The Arcade (`/arcade/`), How It Works, ▶ Play Free. GitHub button → `https://github.com/strulovitz/peaktogether-website`.
- IMPLEMENTATION RULE: reuse — never replace — the proven mechanics (::after hover bridge, right+visibility mobile slide NEVER transform, span accordions, every `<a>` closes drawer, data-component injection, `components.js?v=N` bump).
- STATUS: ✅ BUILT June 23, 2026. `header.html` rewritten (3-level menu + Play Free/GitHub CTA), `style.css` got a "NAV v2" block, new pages `/arcade/ /how-it-works/ /play/` created, `components.js` UNCHANGED (handles nested toggles already), `style.css?v=13→v=14` bumped on all 48 HTML pages. See `descent/docs/MENU_SYSTEM.md` → "NAVIGATION REDESIGN — BUILT". Nir uploads via FileZilla to go live on Dreamhost (remember to upload the 3 new folders too).

## 🔴 SESSION LOG — June 23, 2026 (LATER) — Descent QED game page

### New dedicated game page: `/arcade/descent-qed/` ✅
Built from Fusion's 9-section "Reusable Game-Page Template", filled with rich detail from Claude Fable's
`descent/BIBLE/CLAUDE_FABLE_DESCENT_QED_DOCTRINE.md` (729 lines). Sections: title block (▶ Playable badge,
hook, hero placeholder, Download/GitHub buttons, setup line), nostalgia hook (Then→Now using original Descent
images + remake placeholder), the twist (robots = proof steps, weapons = mathematicians, gentle fizzle), the
mountain (Riemann Hypothesis / Basel Problem, $\sum 1/n^2=\pi^2/6$, the NINE corridors/proofs list),
Understanding Mode (4 glass road-signs graduate/undergrad/high-school/applied + kindergarten color-mixing law),
how-you-two-play (Pilot / Navigator roles + solo note), gallery (placeholders), download & setup
(`pip install pygame PyOpenGL numpy matplotlib`; `cd descent && python app.py`), footer strip.

### CTA buttons repointed (text/style UNCHANGED, only href) ✅
All "Play Descent"-style buttons now point to `/arcade/descent-qed/`:
- Home: 3 buttons ("Play the First Game Free", "Play Descent QED Free", "Start with Everest — Play Descent QED")
- Arcade page + Play page: "Enter Descent QED →"
- NOT touched: the menu "Riemann Hypothesis" leaf link and the in-page science link still point to
  `/mathematics/Riemann_hypothesis/` (that's the science hub, not the game).

### CSS + cache
Added a "GAME PAGE" block to `style.css` (`.gp-*`: badge, placeholders, then-now, gallery, signs, color chips,
roles, footer strip + mobile rules). Bumped `style.css?v=16 → v=17` on all pages.

### NEXT STEP (Nir's plan)
Ask Fusion (with DeepSeek's help) to refine this page — likely the hero art + Then→Now remake images
(currently placeholders) and any extra copy. Implement their answer INTO this same page.

### ⬆️ Upload reminder
FileZilla → Dreamhost: upload `style.css`, all changed HTML, and the new folder `arcade/descent-qed/`.

## 🔴 SESSION LOG — June 23, 2026 (LATER) — Game page images + Fusion packaging prompt

### Descent QED game-page images wired ✅
- Hero art: `images/descent-qed-hero-art.png` (square; GPT 5.4 Image 2; prompt saved verbatim in
  `docs/GAME_HERO_ART_STYLE_PROMPT.md` — reusable style template for all future game hero art).
- 4 screenshots placed: screenshot-1 = "Now" in Then→Now; screenshot-4 = corridor flight;
  screenshot-2 = robot lock-on; screenshot-3 = Q.E.D. finale.
- "Then" image swapped to `images/descent-2-water-elongated-14-over-9-screenshot.jpg`.
- Added a cross-browser **click-to-enlarge lightbox** (inline vanilla JS in the game page only — NO
  components.js change; targets all `.gp img`; close via backdrop/×/Esc; scroll-locked).
- Thumbnails: keep `width:100%`, use `height:auto` (dropped `object-fit:cover`) so images show uncropped.
- style.css bumped through v=20 during this work.

### NEXT BIG TOPIC — packaging & distribution (await Fusion) 📦
Wrote `docs/FUSION_PROMPT_PACKAGING_AND_DISTRIBUTION.md`. It asks Fusion how to ship the game so
non-technical 15–25-yr-olds can install/play WITHOUT `python app.py`: browser demo feasibility (pygbag vs our
PyOpenGL+matplotlib stack), one-click `.exe` (PyInstaller/Nuitka/etc.), a real `setup.exe` (Inno/NSIS) + Linux
(AppImage/Flatpak), FREE hosting (itch.io / GitHub Releases / etc.), no-system-collision strategy, multi-game
architecture, pinned requirements.txt, and a step-by-step pipeline for Nir's Dreamhost+FileZilla+GitHub reality.
Stack facts captured: Python 3.12.11, pygame 2.6.1 (SDL 2.28.4), PyOpenGL 3.1.10, numpy 2.4.6, matplotlib 3.10.9;
legacy fixed-function OpenGL; assets = pre-baked PNGs (~20 MB); LaTeX/TikZ baker is dev-only.
**STATUS:** Nir will restart DeepSeek, paste this prompt to Fusion, then we implement Fusion's answer.

## 🔴 SESSION LOG — June 23, 2026 (LATER) — Packaging & Distribution: Windows .exe BUILT 📦🎉

### Manual fusion received & saved VERBATIM
Nir gave the packaging question to GPT-5.5 + Gemini 3.1 Pro Preview (separate OpenRouter chats),
then had Claude Opus 4.8 judge + integrate. Opus's final combined answer saved **word-for-word** to
`docs/MANUAL_FUSION_PACKAGING_AND_DISTRIBUTION.md` (commit 558b397). Plan = PyInstaller one-folder →
zip → host on itch.io (primary) + GitHub Releases (mirror) → link from peaktogether.me. Never ship Python.

### Implemented Opus's DeepSeek steps 1-6 (then RELOCATED per Nir)
Files were first created in repo root (Opus said "repo root"), but **Nir's multi-game architecture rule
overrides that** — root is the platform/website, each game lives in its own folder. Moved everything into
`descent/` via `git mv` (commit 85e07be). Final locations:
- `descent/requirements-runtime.txt` (pygame==2.6.1, PyOpenGL==3.1.10, numpy==2.4.6 — what gets bundled)
- `descent/requirements-build.txt` (pyinstaller>=6.11,<7)
- `descent/requirements-dev.txt` (-r runtime + matplotlib==3.10.9 — dev-only baker)
- `descent/pt_runtime.py` (base-path + per-game AppData + crash-logger w/ MessageBox)
- `descent/packaging/descent_qed_windows.spec` (sweeps ALL non-.py assets; excludes matplotlib/tkinter)
- `descent/build_windows_release.ps1` (one-click: venv → pip → PyInstaller → zip → SHA-256)
- `descent/app.py` — bootstrap block inserted at top (before pygame/asset loading)
- `descent/render.py` — matplotlib **guarded** (try/except → HAS_MATPLOTLIB; `latex_to_surface`
  returns a tiny transparent surface if absent). NOT deleted. BIBLE/math_flyer.py left untouched.
- root `.gitignore` — added `build/ dist/ release/ .venv-build/`

### 🐛 THREE real bugs found in the plan/environment (flagged, not powered-through) + fixed
1. **`py -3.12` launcher not installed** on Nir's PC (only `python`=3.12.11). Build script's venv step
   would fail. Fix: try `py -3.12` if present, else fall back to `python`.
2. **`contents_directory="."` did NOT flatten** in PyInstaller 6.21 — data files landed in `_internal\`,
   but the bootstrap pointed the frozen base at the .exe folder → game would crash looking for
   `levels/basel.txt`. **Fix:** `pt_runtime.py` frozen branch now uses `sys._MEIPASS` (= `_internal`)
   as the asset base. Standard PyInstaller pattern.
3. **Sweep bundled internal dev folders** (BIBLE, PARENT_ESTATE, docs, packaging) into the player
   download — bloat + leaks private docs/Fable's code. **Fix:** added those to the spec's
   `excluded_dir_names`. Verified gone from the bundle.

### BUILD SUCCEEDED ✅ (Nir gave download permission)
`cd descent; .\build_windows_release.ps1` →
- venv `.venv-build` (python -m venv), pinned deps + pyinstaller 6.21.0 installed
- `dist\Descent QED\Descent QED.exe` + `_internal\` (260 baked PNGs, 44 holograms, levels, corridors) ✅
- `release\PeakTogether-DescentQED-Windows-2026.06.23.zip` (~103 MB) + `.sha256.txt`
- **SHA-256: 0C35E6D94E3C402DC23151F0A0924682946CC5E473A511C27BFE518E3948C970**
- Known harmless warnings: `MSVCR90.dll` missing for OpenGL's gle/freeglut .vc9 DLLs (we don't use
  GLE/GLUT — we use pygame for the window), and benign "conda-meta not found" notes.

### Automated smoke test PASSED
Launched the .exe headless-ish: ran 30s (game loop alive) with **NO crash-log** written to
`%LOCALAPPDATA%\PeakTogether\DescentQED\` → assets resolved, no unhandled exception. Visual eyeball
(images/text/controls) still pending Nir's double-click; true Python-free PC test in a few days.

### Current state / NEXT (steps 7-11 are Nir's, with DeepSeek's step-by-step help)
| Item | Status |
|------|--------|
| Steps 1-6 (code + spec + build script) | ✅ done, committed, pushed |
| Step 7 build | ✅ done (zip in `descent/release/`) |
| Step 8 test on Python-free PC | ⏳ Nir, in a few days |
| Step 9 upload to itch.io (primary) | ⏳ Nir (DeepSeek gave step-by-step) |
| Step 10 upload to GitHub Releases (mirror) | ⏳ Nir (DeepSeek gave step-by-step) |
| Step 11 update peaktogether.me (trailer + buttons + SmartScreen note) | 🔜 NEXT, with DeepSeek |

### NOTES for future games (reuse template)
Each game = its own folder with its own `requirements-*.txt`, `pt_runtime.py` (own slug),
`packaging/<game>_windows.spec`, `build_windows_release.ps1`. Writes to
`%LOCALAPPDATA%\PeakTogether\<GameSlug>\`. The spec must use `sys._MEIPASS` via pt_runtime (NOT the
exe folder) and exclude BIBLE/PARENT_ESTATE/docs/packaging. The `py -3.12`→`python` fallback is baked in.
The release zip/.sha256.txt are gitignored (uploaded to itch/GitHub Releases, never committed).

### 🐛 BUG #4 found during Nir's Step-8 test — Understanding Mode crash (missing Pillow)
Entering Understanding Mode on robot 1 crashed the packaged game:
`render.py:877 blur_surface -> ModuleNotFoundError: No module named 'PIL'`. `blur_surface` (the
glass-panel Gaussian blur) lazy-imports Pillow, which the dev machine had but the bundle did not.
**Fix:** added `Pillow==12.2.0` to `descent/requirements-runtime.txt` (now bundled — verified
`_internal\PIL` present) **and** guarded the import in `blur_surface` (returns the surface unblurred
if PIL is ever missing, instead of crashing). Proactively scanned ALL runtime imports — PIL was the
only extra third-party dep (the other PIL hit is the dev-only baker `deu/bake_corridor.py`, not shipped).
Rebuilt OK. **New zip ~108.8 MB. New SHA-256: 7A42613FCD9E831D8A68D52220DFA35EADED4E2C73FAC17A82B61586CCB069C8.**
Lesson for future games: any lazy/function-level `import` of a third-party lib must be in
requirements-runtime.txt; the dev machine hides missing deps that the frozen bundle exposes.

### ✅ STEP 8 PASSED — Nir confirmed "now everything works" (June 23, 2026)
Nir re-extracted the new (Pillow) zip and tested on his laptop: the packaged `Descent QED.exe`
launches, loads all assets, flies, AND **Understanding Mode works** (the crash is gone). The Windows
build is GOOD. (True Python-free PC test still planned in a few days as final confirmation.)
**NEXT:** Step 9 itch.io upload, Step 10 GitHub Releases upload, then Step 11 peaktogether.me
(trailer + buttons + SmartScreen note) — all with DeepSeek's step-by-step help.

### 🎉 STEP 9 DONE — Descent QED is LIVE on itch.io (June 23, 2026)
Nir uploaded the Windows zip + hero-art cover + 4 screenshots and confirmed "it worked".
**🔗 itch.io page (the "Play on Windows" target for Step 11): https://strulovitz.itch.io/descent-qed**
Remaining: Step 10 (GitHub Releases mirror + .sha256.txt), Step 11 (peaktogether.me — point the
"Play on Windows" button at the itch URL above, add a smaller "Mirror (GitHub)" link, trailer, and the
friendly SmartScreen "Unknown publisher" note; bump style.css?v=, FileZilla up to Dreamhost).
