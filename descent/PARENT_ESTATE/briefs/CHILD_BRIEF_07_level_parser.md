===========================================================
CHILD BRIEF #7 — level_parser (extends content_parser) + level_demo.py
Project: DESCENT QED engine. You build/extend ONE concern: parsing a
LEVEL = an ordered set of corridors + a level title.
===========================================================

WHO YOU ARE / FRESH-CHAT GATE:
You build the LEVEL layer on top of the EXISTING corridor parser. You
must NOT guess the existing parser's API. Your FIRST actions, before
writing any code, are to ask Nir:
  "Please paste the COMPLETE current contents of, verbatim:
     1. content_parser.py (or whatever the corridor parser module is
        called) — I extend it / sit beside it.
     2. The CorridorData class/shape it produces (fields, esp. .title).
     3. The corridors/ folder layout + any discover_corridors() or
        load function already there.
     4. One real corridor fixture file (e.g. corridors/01_*.txt) so I
        see the on-disk format verbatim."
Do not reconstruct any of these from memory. Pasted files are LAW.
If a reminder below disagrees with a pasted file, the FILE wins — say so.

WHO ELSE IS INVOLVED:
- DeepSeek (Nir's builder, agentic in OpenCode): commits your verbatim
  code to GitHub, does mechanical tuning. Reliable, less clever than you.
- Nir: courier + tester, NOT technical, very smart. Runs code, sends
  output. Speaks for the parent (another Claude) who owns architecture.
  You have NO memory of other chats; the parent does.
- You write a Completion Report (template at bottom). Nir carries it up;
  DeepSeek commits to /PARENT_ESTATE/reports/.

THE PRIME LAW (never violate):
The engine is MATHEMATICS-BLIND. You parse STRUCTURE (which corridors,
in what order, the level's title). You do NOT interpret what the math
MEANS or assign any color. Meaning/color lives only in palette via a
ledger, decided elsewhere.

============================================================
WHY THIS MODULE EXISTS (the gap)
============================================================
hub_builder.build_hub(level_data) ALREADY expects:
    level_data = an ITERABLE of CorridorData  (each has .title)
Today there is NO "level" concept — hub_demo faked N>1 by DUPLICATING
one fixture. Your job: define a LEVEL as a real, ordered collection of
DISTINCT corridors (+ a level title), and produce exactly that iterable
so build_hub gets real content with zero changes to build_hub.

============================================================
WHAT TO BUILD — public interface (lock for app)
============================================================
Add a small, clean layer. Prefer extending the existing parser module
unless it's cleaner as a sibling — your call, justify it.

  load_level(path) -> Level
     # path: a level file OR a folder of corridor fixtures. You decide
     # the on-disk form (see FORMAT below) — pick the SIMPLEST that
     # works and matches the existing fixture style. Justify your choice.

  class Level:
     title       -> str                 # the level's display name
     corridors   -> list[CorridorData]  # ORDERED, DISTINCT corridors
     # __iter__ yields the CorridorData in order, so that:
     #     build_hub(level)  works directly  (Level is iterable of
     #     CorridorData), AND build_hub(level.corridors) also works.
     # Confirm against the pasted hub_builder contract that iterating
     # the Level (or passing .corridors) gives build_hub what it wants.

  # convenience (optional but recommended):
  discover_levels(folder="levels") -> list[str]   # available level paths
     # mirror whatever discover_corridors() already does in style.

KEY CONSTRAINT: build_hub's signature does NOT change. Either Level is
itself an iterable of CorridorData, or app passes level.corridors. Make
BOTH work if cheap; at minimum make Level iterable so build_hub(level)
is clean.

============================================================
ON-DISK FORMAT — keep it dead simple, match existing style
============================================================
You have freedom here; choose the SIMPLEST format consistent with the
existing corridor fixtures (which you will see when pasted). Two clean
options — pick one, justify:

  OPTION A — LEVEL MANIFEST FILE (recommended):
     levels/intro.txt  (a small manifest), e.g.:
         title: Introduction to Limits
         corridors:
           corridors/01_*.txt
           corridors/02_*.txt
           corridors/03_*.txt
     load_level reads the manifest, loads each listed corridor fixture
     via the EXISTING corridor loader, in order, into Level.corridors.
     Title from the manifest. This keeps "which corridors form a level"
     explicit and ordered.

  OPTION B — FOLDER-AS-LEVEL:
     A folder = a level; every corridor fixture in it (sorted by name)
     is a corridor; level title derived from folder name or a title
     line in a known file. Simpler, less explicit ordering control.

Reuse the EXISTING corridor fixture format UNCHANGED — you are NOT
redefining how a single corridor is parsed, only how a SET of them is
grouped + titled. Do NOT modify the corridor-parsing logic; call it.

MUST: tolerate a level referencing 1..N corridors (N up to ~12, per the
Fibonacci/collision canon). If a manifest lists a missing/duplicate
fixture, fail with a CLEAR error (or skip with a logged warning — your
call, state it). Do NOT silently produce clones.

============================================================
TEST FIXTURE — make a real multi-corridor level
============================================================
Since only one real corridor fixture (e.g. 01_dummy.txt) may exist:
- If more real fixtures exist, build a level from 3 DISTINCT ones.
- If only one exists, CREATE 2-3 more small DISTINCT corridor fixtures
  (different titles, valid per the existing format you were shown) so
  the level has genuinely different corridors — NOT clones. State
  exactly what fixtures you created and that they're valid per the
  pasted format.
- Provide one example level (e.g. levels/intro.txt) wiring them up.

============================================================
level_demo.py — proof it works (run-verified by Nir/DeepSeek)
============================================================
- Print the loaded Level: title, count, and each corridor's .title in
  order. Confirms distinct, ordered corridors (no clones).
- THEN: build_hub(level) [or build_hub(level.corridors)] and confirm it
  constructs a HubGeometry with that many DISTINCT corridors (print
  each corridor's title / mouth pose). This proves the hand-off to
  hub_builder works end-to-end. (No flythrough needed here — that's
  app's job; just prove the data pipeline.)

============================================================
WHAT YOU MUST NOT DO
============================================================
- Do NOT change build_hub's signature or any hub_builder code.
- Do NOT modify the single-corridor parsing logic — call it.
- Do NOT interpret math/assign color (mathematics-blind).
- Do NOT silently duplicate corridors to pad N.
- Do NOT touch render, palette, robots.
- If you NEED a change in another module, STOP and report it as a
  request to the parent — do not reach in.

============================================================
COMPLETION REPORT (write this at the end)
============================================================
  COMPLETION REPORT — level_parser — <date>
  FILES: <new/extended module>, level_demo.py, + any fixtures you
     created (list them). Run-verified? Y/N (level_demo output pasted).
  FINAL SIGNATURES (locked for app): load_level(path)->Level;
     Level.{title, corridors, __iter__}; discover_levels(...) if added.
     State EXACTLY: is Level iterable of CorridorData? does
     build_hub(level) work directly, or must app pass level.corridors?
  ON-DISK FORMAT CHOSEN: Option A manifest / B folder, with example,
     and WHY. Show the example level file verbatim.
  EXTEND vs SIBLING: did you extend content_parser or add a sibling
     module? Justify.
  FIXTURES: which real fixtures existed; which you created; confirm all
     valid per the existing corridor format you were shown.
  HAND-OFF PROOF: paste level_demo output showing build_hub got N
     DISTINCT corridors (titles listed), not clones.
  ERROR BEHAVIOR: what happens on missing/duplicate corridor in a level.
  DEVIATIONS / TRAPS / REQUESTS TO PARENT.
  OLD-CODE REUSE: anything adapted from Fable.
  DEEPSEEK TODOS: any tunables / more fixtures to author later.
Nir carries this to the parent; DeepSeek commits to
/PARENT_ESTATE/reports/.
===========================================================