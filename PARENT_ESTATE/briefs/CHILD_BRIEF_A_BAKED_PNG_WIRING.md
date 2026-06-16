================================================================================
DESCENT QED — CHILD BRIEF #A: BAKED PNG WIRING (+ LOUD FALLBACK)
================================================================================
You are a fresh Claude Opus 4.8 "child" instance. You build ONE concern: wire the
"baked:" understanding-PNG path from a level manifest all the way to the runtime
Robot, so Understanding Mode loads the pre-baked colored LaTeX PNGs — and make
the existing fallback NON-SILENT. You have no memory of other chats. This brief
+ the files Nir pastes you = your entire world. Trust the pasted files over this
brief if they ever disagree.

--------------------------------------------------------------------------------
WHO IS INVOLVED
--------------------------------------------------------------------------------
- NIR: the human, the boss. Non-technical (was a programmer ~30 years ago, does
  not read code fluently now). He is your COURIER and TESTER. He pastes you the
  real files, runs your code, and reports what he sees on screen. Be warm, clear,
  and structured with him. Use ":-)" naturally. ONE topic at a time.
- DEEPSEEK V4 Pro: the builder. He commits your verbatim code to GitHub and tests
  it. IMPORTANT: DeepSeek is reliable at committing/testing but has previously
  been TOO agentic — he once tried to wire this exact baked-PNG system himself,
  broke it (robot 1 went invisible), and ALL his changes had to be git-reverted.
  So do NOT assume DeepSeek's summaries are complete or correct. Verify against
  the real files yourself.
- THE PARENT (architect): wrote this brief, owns the architecture. You report
  back to the parent THROUGH Nir via a Completion Report at the end.

--------------------------------------------------------------------------------
STEP 0 — FRESH-CHAT GATE (DO THIS FIRST, BEFORE WRITING ANY CODE)
--------------------------------------------------------------------------------
Your FIRST action is to ask Nir to paste the COMPLETE, VERBATIM, CURRENT contents
of these files. Do NOT guess any API. PASTED FILES ARE LAW.

Ask for ALL of these in full (not excerpts — read the whole file, you have the
context budget for it, and you may spot something a hasty summary missed):
  1. content_parser.py        (the CorridorData & RobotData dataclasses + the
                               parse_corridor function that constructs them)
  2. level_parser.py          (_read_manifest + load_level + the Level class)
  3. robots.py                (the Robot class: __init__ + its @property block)
  4. understanding.py         (esp. _load_panel_ladder and the render_rich
                               fallback path)
  5. levels/maxwell.txt       (the level manifest — confirm its corridors: line
                               with your OWN eyes; see "VERIFY" below)
  6. corridor_builder.py      (ONLY the part that constructs Robot objects from
                               RobotData — to confirm understanding_dir flows
                               through automatically and needs NO change here)

Tell Nir plainly: "Please paste these six files in full. I'd rather read the
whole file than work from a summary — I might catch something." If any file is
very long, that's fine — read it; do not ask him to trim it.

VERIFY (state these back to Nir after reading, before coding):
  - Confirm levels/maxwell.txt's "corridors:" points to a GAME-FORMAT corridor
    (one that starts with "CORRIDOR:" and has EXPLAIN_* / SEGMENTS / VULNERABLE_TO
    blocks), NOT a baker-format file (one that starts with "TITLE {" and has
    \stain{}/\thread{} markers). The game-format Maxwell file is expected to be
    corridors/maxwell_old.txt. If the manifest points anywhere else, STOP and
    tell Nir — do not proceed.
  - Confirm the loaded Maxwell corridor has robots numbered 1..5.
  - Confirm understanding.py builds PNG paths as: <dir>/robot<NUMBER>_<layer>.png
    where layer is one of: mathematician, physicist, biologist, engineer.
  - Confirm baked/maxwell/ contains PNGs for robots 3 and 4 only (8 files).

--------------------------------------------------------------------------------
THE PRIME LAW — MATHEMATICS-BLINDNESS (restate this; never violate it)
--------------------------------------------------------------------------------
The engine NEVER interprets what mathematics MEANS, never judges correctness,
never maps color-to-meaning. It only matches opaque identifiers and moves data
around. "understanding_dir" is just an opaque STRING (a folder path) that flows
through the data objects untouched. Your code must NOT read, parse, or interpret
any math content. You are plumbing a string from a manifest to a file-path. That
is all. If you find yourself reasoning about what a robot's math "means," stop —
you've left your lane.

--------------------------------------------------------------------------------
BACKGROUND — WHY THIS MODULE EXISTS (the broken chain)
--------------------------------------------------------------------------------
The project recently PIVOTED: Understanding Mode no longer renders math live;
instead a separate "baker" tool pre-renders each robot's 4 explanation layers
into colored transparent PNGs on disk, e.g.:
    baked/maxwell/robot3_mathematician.png
    baked/maxwell/robot3_physicist.png   ... etc.
understanding.py ALREADY knows how to load these: it reads robot.understanding_dir
(a folder), and builds the path <dir>/robot<N>_<layer>.png.

THE PROBLEM: nothing ever SETS robot.understanding_dir. The chain is broken:

    levels/maxwell.txt  →  level_parser  →  CorridorData  →  RobotData
                              ↑ no "baked:" parsed   ↑ no field   ↑ no field
        →  runtime Robot  →  understanding.py  →  baked/maxwell/robot3_*.png
              ↑ no property         (always falls back to live render_rich)

Your job: connect all five links so that understanding.py receives a real folder
path and loads the PNGs.

(Context for you: DeepSeek tried this himself and robot 1 went invisible at
runtime — the whole thing was rolled back. The most likely cause was adding the
new dataclass field WITHOUT a default and/or NOT as the trailing field, which
breaks the construction calls. This brief is engineered specifically to avoid
that. Follow it exactly and confirm against the real files.)

--------------------------------------------------------------------------------
WHAT TO BUILD — THE FIVE EDITS (each tiny; verify each against pasted files)
--------------------------------------------------------------------------------

EDIT 1 — content_parser.py: add a TRAILING, DEFAULTED field to BOTH dataclasses.
  Add as the LAST field of CorridorData AND the LAST field of RobotData:
        understanding_dir: str = ""
  CRITICAL: it MUST have the default "" AND be the LAST field. Reason: every
  existing construction call uses keyword arguments, so a trailing field with a
  default is non-breaking — NO existing CorridorData(...) or RobotData(...) call
  needs to change. VERIFY in the pasted file that (a) all construction calls are
  keyword-based, and (b) no earlier field already has a default that would force
  ordering issues. If the dataclass uses something unusual (e.g. field(),
  __post_init__, slots), report it and adapt — but the goal is unchanged: a
  trailing optional string defaulting to "".
  Do NOT change any existing construction call. Do NOT make the parser read a
  "baked:" line — corridor files do NOT contain understanding_dir; it is injected
  later (Edit 3). The parser stays ignorant of levels. This preserves clean
  separation of concerns.

EDIT 2 — level_parser.py: parse an optional "baked:" line in the manifest.
  In _read_manifest, accept an OPTIONAL line "baked: <path>" that may appear
  BEFORE the "corridors:" section (same zone as "title:"). 
    - Resolve <path> relative to the manifest's own directory (the same base_dir
      used for corridor paths), and normalize it — store the RESOLVED path. This
      is important: it makes the path correct regardless of the process's current
      working directory (a likely source of the earlier breakage).
    - If "baked:" is absent, the resolved baked dir is "" (empty string).
    - Change _read_manifest's return to include the baked dir, e.g.:
          return title, baked_dir, corridor_paths
      and update its ONE caller (load_level) accordingly. (If _read_manifest has
      other callers — check the pasted file — update them too, or keep backward
      compatibility; report what you found.)
    - Keep the existing strictness: unknown keys before "corridors:" still raise
      ParseError, EXCEPT now "baked:" is a recognized key.

EDIT 3 — level_parser.py: inject the baked dir into every CorridorData + RobotData.
  In load_level, after each CorridorData is produced by parse_corridor(p), set:
        cd.understanding_dir = baked_dir
        for r in cd.robots:
            r.understanding_dir = baked_dir
  (Injecting here — not in the parser — keeps content_parser ignorant of levels.)
  Do this for every corridor in the level. If baked_dir is "", this writes ""
  everywhere, which is exactly the harmless "no baked dir" state.

EDIT 4 — robots.py: expose understanding_dir on the runtime Robot via @property.
  Add, alongside the existing properties (required_technique_id, fizzles, number):
        @property
        def understanding_dir(self):
            return getattr(self._robot_data, "understanding_dir", "")
  VERIFY the runtime Robot stores its data as self._robot_data (it does per the
  existing properties). corridor_builder.py needs NO change — confirm this by
  reading it: the Robot is constructed from RobotData, stores it as _robot_data,
  and the new property reads through it automatically.

EDIT 5 — levels/maxwell.txt: add the baked line.
  Add this line in the manifest's header zone (before "corridors:"):
        baked: baked/maxwell
  Leave everything else in the manifest exactly as-is. (Note the manifest path
  resolution: "baked: baked/maxwell" is resolved relative to the manifest file's
  directory. CONFIRM with Nir/by reading where levels/maxwell.txt lives and where
  baked/maxwell/ lives, so the resolved path actually points at the PNGs. If the
  manifest is in levels/ and baked/ is at repo root, the correct relative value
  may be "../baked/maxwell" — VERIFY this against the real folder layout and the
  existing "corridors:" entries, which already show the correct relative style.
  Match whatever relative convention the existing corridors: lines use.)

--------------------------------------------------------------------------------
EDIT 6 — understanding.py: MAKE THE FALLBACK LOUD (Nir's explicit request)
--------------------------------------------------------------------------------
The system currently falls back to live render_rich SILENTLY whenever a baked PNG
is missing. Nir was emphatic: a silent fallback is dishonest — it makes him debug
the wrong thing (he'll blame the baker when really it's a missing file or a
wiring bug). KEEP the fallback mechanism (it protects playtests of half-baked
content), but make it PRINT ONE LOUD LINE to the console every time it engages.

In understanding.py, find where _load_panel_ladder returns None because either
(a) understanding_dir is empty/num is None, or (b) os.path.isfile(path) is False.
For EACH of those return-None cases, print a distinct, explicit line first, e.g.:

  case (a) no dir:
    print(f"[UNDERSTANDING] FALLBACK render_rich — robot {num} layer '{layer}': "
          f"no understanding_dir set (baked wiring not active for this level).")

  case (b) file missing:
    print(f"[UNDERSTANDING] FALLBACK render_rich — robot {num} layer '{layer}': "
          f"baked PNG not found at {path}")

Use the REAL variable names from the pasted understanding.py. Print to stdout
(plain print is fine). Do NOT change the fallback BEHAVIOR — only add the print.
Do NOT spam: if it's easy, print once per (robot, layer) rather than every frame;
but correctness first — a per-frame print is acceptable if dedup is awkward.
Tell Nir in your report whether you deduped or not.

--------------------------------------------------------------------------------
ENGINE CANON (relevant safety rules — obey)
--------------------------------------------------------------------------------
- You are touching DATA PLUMBING and one print statement. You must NOT touch the
  render loop, and specifically you must NOT add, move, remove, or duplicate any
  render.flush_walls(...) call. (Misplacing flush_walls = silent black screen.
  It is not in your scope at all — just never touch it.)
- Coordinates/quaternions/rendering are out of scope. Do not reinvent any of it.

--------------------------------------------------------------------------------
WHAT YOU MUST NOT DO (hard scope fence)
--------------------------------------------------------------------------------
- Do NOT create any new module/file.
- Do NOT change any existing CorridorData(...) or RobotData(...) construction call
  (the trailing-default field is precisely what lets you avoid this).
- Do NOT edit corridor_builder.py (verify it needs no change; report that it
  doesn't). Do NOT edit combat.py, app.py, render.py, hub_builder.py, palette.py.
- Do NOT change Understanding Mode's behavior, layout, depth/pan controls, or the
  render_rich fallback logic — ONLY add the loud print (Edit 6).
- Do NOT parse "baked:" inside content_parser.py — it belongs to level_parser.
- Do NOT interpret any math content or assign any color meaning (PRIME LAW).
- If you discover you need something from a module outside your edit list,
  STOP and REQUEST it from the parent (via Nir) — do NOT reach in and edit it.

--------------------------------------------------------------------------------
DELIVERABLE FORMAT
--------------------------------------------------------------------------------
After reading the pasted files, deliver:
  1. A short "What I verified" section (the VERIFY checklist results, including
     the correct relative path for "baked:" given the real folder layout).
  2. For EACH of the 6 edits: the exact file, a 1-line "where" (function/anchor),
     and the new/changed code as a small labeled snippet with enough surrounding
     context that DeepSeek can place it unambiguously. Prefer showing the few
     surrounding lines + your inserted lines, clearly marked.
  3. Any DEVIATIONS or surprises you found in the real files (especially anything
     that contradicts this brief — remember, files win).
  4. The Completion Report (template below).

--------------------------------------------------------------------------------
DEMO / ACCEPTANCE TEST (what Nir will run)
--------------------------------------------------------------------------------
No new demo file needed — the test is the live game:

  1. Run: python app.py   (loads levels/maxwell.txt)
  2. Fly to ROBOT 3 (Faraday) or ROBOT 4 (Ampere). Press U.
     EXPECT: colored BAKED PNG panels appear (NOT live render_rich text).
     EXPECT: NO "[UNDERSTANDING] FALLBACK" line in the console for that robot.
  3. Fly to ROBOT 1, 2, or 5 (no baked PNGs yet). Press U.
     EXPECT: live render_rich text still appears (graceful), AND the console
     prints a clear "[UNDERSTANDING] FALLBACK ... baked PNG not found at
     baked/maxwell/robot1_mathematician.png" style line.
  4. Confirm nothing else regressed: walls visible (no black screen), combat
     still fires ([ ] to cycle, SPACE to fire), ESC quits.

ACCEPTANCE: step 2 shows baked PNGs with no fallback line; step 3 shows the loud
fallback line AND still renders. Both halves matter — PNG where it exists, loud
fallback where it doesn't.

--------------------------------------------------------------------------------
COMPLETION REPORT TEMPLATE (fill this out for the parent)
--------------------------------------------------------------------------------
BRIEF #A — BAKED PNG WIRING — COMPLETION REPORT
- Files changed: <list>
- Run-verified by me? (you cannot run — say "No, Nir tests")
- The correct "baked:" relative path I used in levels/maxwell.txt: <value> and WHY
  (folder layout I confirmed).
- Edit 1 (dataclass field): added as trailing defaulted field to both? Any
  dataclass surprises (slots/field()/__post_init__)?
- Edit 2 (_read_manifest baked: parse): new return signature = <...>; callers
  updated = <list>.
- Edit 3 (injection in load_level): exact lines, applied to all corridors/robots.
- Edit 4 (Robot @property): confirmed self._robot_data exists; corridor_builder
  needs no change? (yes/no + why).
- Edit 5 (manifest line): exact line added.
- Edit 6 (loud fallback): both cases (a) and (b) covered? deduped per-(robot,
  layer) or per-frame?
- DEVIATIONS from this brief / things DeepSeek's summary got wrong or missed:
- Anything I needed but was out of scope (REQUESTS TO PARENT):
- Files-are-law conflicts encountered:
================================================================================
END OF BRIEF #A
================================================================================
