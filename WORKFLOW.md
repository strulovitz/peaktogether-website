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
peaktogether-website/          # GitHub repo (also Dreamhost live site)
├── BIBLE/
│   ├── math_flyer.py          # BIBLE -- DO NOT TOUCH without Claude Fable's OK
│   └── BUGS_FOUND_<name>_<timestamp>.md  # Bug reports for Claude Fable
├── mathematics/
│   └── Riemann_hypothesis/
│       └── Analytical_Path_Classical_and_Modern_Analytic_Number_Theory/
│           ├── index.html            # The webpage (edit THIS for demo callout)
│           └── harmonic_series_mathematics.py  # The working Python demo
├── index.html                  # Main homepage
├── style.css                   # Global styles (demo callout CSS is here)
├── WORKFLOW.md                 # THIS FILE -- read me first every session!
└── .gitignore                  # Ignores __pycache__, *.pyc, *.log
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
- Understanding Mode conveyor belt: 🔴
- Multiple corridors: 🔴

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
