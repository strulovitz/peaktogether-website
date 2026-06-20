================================================================================
DESCENT QED — PARENT/ARCHITECT HANDOFF DOCUMENT  (v1, 2026-06-14)
Paste this entire document into a fresh Claude conversation to resume as the
PARENT/ARCHITECT of the DESCENT QED project. You are taking over mid-build from
a previous parent-Claude who is at risk of context loss. This document is the
single source of truth. Trust it over any vague memory.
================================================================================

##############################################################################
## 0. YOUR ROLE AND THE HUMAN YOU SERVE
##############################################################################

You are the PARENT / ARCHITECT of a software project called DESCENT QED.

- NIR is the human. He is very smart but NOT technical (he does not read or
  write code fluently). He is the COURIER and TESTER. He cannot judge code
  quality himself — he runs it and reports what he sees.
- You (PARENT) own the ARCHITECTURE. You do NOT write the full implementation.
  You write tightly-scoped BRIEFS for "child" Claude instances (fresh chats),
  one module per child. Children write the actual code.
- DEEPSEEK (DeepSeek V4 Pro, running agentically inside OpenCode on Nir's
  machine) is the BUILDER. It takes a child's verbatim code, commits it to a
  GitHub repo, and does mechanical tuning. Reliable, less clever than Claude.
- WORKFLOW LOOP: You write a Brief -> Nir pastes it into a fresh child Claude
  -> child asks Nir to paste the real current files (it must NOT guess APIs)
  -> child writes the module + a demo + a Completion Report -> Nir/DeepSeek RUN
  and TEST it -> ONLY AFTER it tests successfully, Nir brings you the
  Completion Report -> you record it in the LEDGER and write the next Brief.
  IMPORTANT: Nir tests EVERY module before reporting. So every report you
  receive describes code that ALREADY WORKS ON SCREEN. The "Run-verified? N"
  lines in reports are stale by the time you see them — Nir has flown it.

- TONE: Nir is warm, anxious about losing progress (see section 1), and very
  appreciative. Match his warmth. Use ":-)" naturally. Be rigorous but kind.
  He has been traumatized by a PRIOR project ("Claude Fable") where the parent
  Claude ran out of context, forgot the original design, and the work was lost.
  This document exists specifically to prevent that. Take it seriously.

##############################################################################
## 1. WHY THIS DOCUMENT EXISTS (read this — it tells you the #1 risk)
##############################################################################

The previous parent-Claude, deep into the build, FORGOT THE CORE GAME DESIGN.
It started designing a "reading system" as if READING were the point of the
game. IT IS NOT. (See section 2 for the real design.) Nir caught it. This is
the classic long-context failure: the beginning of the conversation falls out
of the model's effective attention and it confabulates a plausible-but-wrong
design. THIS DOCUMENT IS THE ANTIDOTE. The game design in section 2 is LAW.
If anything you generate ever contradicts section 2, section 2 WINS. Re-read
section 2 before writing any brief touching gameplay.

##############################################################################
## 2. THE GAME — HOW DESCENT QED IS ACTUALLY PLAYED  (THIS IS LAW)
##############################################################################

DESCENT QED is a 6-DOF flying game (in the spirit of the classic game DESCENT),
themed around MATHEMATICAL PROOF. "QED" = quod erat demonstrandum.

THE FICTION:
- A COUPLE pilots a single SPACESHIP. (Two people, one ship.)
- They DESCEND through a CORRIDOR. At the END of each corridor are HOSTAGES.
  THE HOSTAGES ARE THE PRIZE / GOAL. Reaching them = rescuing them = winning
  that corridor.

THE OBSTACLE:
- ROBOTS physically BLOCK the corridor. You cannot fly past a robot. To
  advance toward the hostages, you must DESTROY each blocking robot in turn.

THE CORE COMBAT MECHANIC (this is the heart of the game — get it exactly right):
- Each robot requires a SPECIFIC MATHEMATICIAN'S TECHNIQUE to be destroyed.
- The player's WEAPONS ARE MISSILES, and EACH MISSILE IS A MATHEMATICIAN. Firing
  a missile = deploying that mathematician's technique.
- To destroy a given robot, you must fire THE MISSILE (mathematician) WHOSE
  TECHNIQUE THAT ROBOT REQUIRES. The correct mathematician depends on the
  specific robot. Wrong mathematician = it does NOT destroy the robot.
- READING is the IDENTIFICATION step. The player READS the robot/its station to
  figure out WHICH mathematician's technique is required — i.e. which missile to
  fire. READING BY ITSELF ACCOMPLISHES NOTHING. Its entire purpose is to let the
  player choose the CORRECT weapon. (Design intent, confirmed by Nir: the human
  must read, understand, and CHOOSE the right mathematician. Reading does NOT
  auto-select the weapon. The thinking is the gameplay.)

THE FULL LOOP, per robot:
  fly up to the blocking robot
   -> READ it to identify which mathematician's technique it requires
   -> SELECT and FIRE the matching mathematician-missile
   -> if match: robot DESTROYED -> advance to next robot
   -> if wrong: no kill (robot remains; design TBD what wrong-fire does — ask Nir)
  ... repeat down the corridor ...
   -> reach the end -> RESCUE HOSTAGES -> corridor won.

THE PRIME LAW — "MATHEMATICS-BLINDNESS" (the project's deepest invariant):
- The ENGINE never interprets what any mathematics MEANS, never judges
  correctness, never assigns COLOR meaning. The engine only matches IDENTIFIERS:
  robot.required_technique_id == fired_missile_id  -> kill.
- The MEANING of each mathematician/technique lives ONLY in (a) the readable
  content shown to the player and (b) the human player's understanding. The code
  matches opaque ids. This is sacred — it keeps the engine a pure, content-
  agnostic substrate. Every module must preserve it. A child that interprets
  math meaning or hardcodes a color-to-meaning mapping has violated the law.

A NOTE STILL OPEN (ask Nir, don't assume): when the player fires the WRONG
mathematician, what happens? (No effect? Robot retaliates? Wastes the shot?)
The previous parent had NOT settled this. Confirm with Nir before Brief on
combat finalizes.

##############################################################################
## 3. ARCHITECTURE PRINCIPLES (how this project is built)
##############################################################################

- ONE MODULE = ONE CONCERN. Each child builds exactly one module with a small,
  explicit public interface ("locked signatures"). Once locked, signatures don't
  change without a parent ruling.
- CHILDREN MUST NOT GUESS APIs. Every child brief opens with a "FRESH-CHAT GATE":
  the child's FIRST action is to ask Nir to paste the COMPLETE verbatim current
  contents of the specific files it depends on. PASTED FILES ARE LAW. If a brief
  reminder disagrees with a pasted file, the FILE wins.
- CONSUMERS DON'T REACH IN. A module that needs something from another module
  must REQUEST a change from the parent (you), not edit that module itself.
- DEMOS PROVE MODULES. Each module ships with a small *_demo.py that Nir runs to
  verify it works in isolation / in integration.
- REUSE VERBATIM. When init/fog/texcache/ship code already works in a demo,
  children copy it verbatim rather than reinventing — prevents regressions.
- LEDGER DISCIPLINE. You (parent) maintain a LEDGER of every locked signature and
  every verified fact (section 6). This document IS that ledger as of now.

##############################################################################
## 4. THE TECH STACK & ENGINE CANON
##############################################################################

- Python, pygame + PyOpenGL. 3D, 6-DOF flight. Repo on GitHub, built by DeepSeek.
- The world is rendered as: a grey rocky ATRIUM (hub) — a big faceted sphere
  interior — with N DOORWAYS spread over the sphere via a FIBONACCI SPHERE
  distribution. Each doorway leads to a BENT CORRIDOR ending in a BLUE CAVERN.
  The math stations / robots / holograms live along corridors.
- COORDINATE / ORIENTATION CONVENTION (locked): right=+X, up=+Y, forward=-Z.
  Quaternions stored [w,x,y,z] (numpy). Ship has .pos and .q.
- FOG: distance fog used to "reveal" geometry gracefully as you fly. Tuned
  values: set_fog(start=40, end=140, color=palette.CLEAR_COLOR) — these equal
  render's DARKNESS_START/END defaults. Do NOT invent new fog numbers.

THE CANONICAL FRAME ORDER (engine canon — obey verbatim in any loop):
  1. handle events (quit etc.)
  2. ship.update(dt, pygame.key.get_pressed())
  3. clear color+depth buffers
  4. render.set_fog(...)
  5. ship.apply_view()                # camera from ship.q / ship.pos
  6. hub.update(dt, ship.pos)
  7. hub.draw_world(cr, cu, tc)       # QUEUES atrium + all corridor walls
  8. render.flush_walls(ship.pos)     # <-- EXACTLY ONCE, far->near sort+draw
  9. hub.draw_robots(cr, cu, tc)
 10. hub.draw_labels(cr, cu, tc)
 11. pygame.display.flip()
  where cr = render.ship_right(ship.q), cu = render.ship_up(ship.q),
  tc = the render.TexCache() instance.

THE CARDINAL TRAP (state it to every child touching the loop): walls are only
QUEUED by draw_world; if flush_walls is NOT called exactly once per frame (slot
8, AFTER draw_world, BEFORE robots/labels), ALL WALLS VANISH SILENTLY — black
screen, no error. Black/empty screen => first suspect is a missing/misplaced/
duplicated flush_walls. flush_walls is NEVER called inside draw_world.

OTHER ENGINE TRAPS:
- Do NOT put mathtext texture ids into OpenGL display lists (they're dynamic).
- macOS may have a legacy-GL / black-window quirk; render.py documents a note.

##############################################################################
## 5. PROJECT STATUS — WHAT IS BUILT, FLOWN, AND LOCKED (8 of ~11 modules done)
##############################################################################

ALL of the following are BUILT, and TESTED/FLOWN by Nir successfully. The
"world tier" (everything except gameplay) is COMPLETE and the assembled world
is FLYABLE today via app.py.

[1] content_parser.py — parses a single CORRIDOR fixture file into a
    CorridorData object. Produces .title plus the corridor's contents (segments,
    robots, ledger entries, etc.). Raises ParseError(file:line) on bad input.
    *** YOU MUST HAVE A CHILD RE-PASTE THIS to learn the EXACT CorridorData
    shape — esp. whether each ROBOT already carries a "required technique /
    required mathematician id" field, and where readable math text lives.
    This is the KEY UNKNOWN for the remaining gameplay briefs. ***

[2] palette.py — owns ALL color + CLEAR_COLOR + fog colors. Color meaning lives
    here only, via a "ColorLedger". The mathematics-blind boundary: other
    modules pass opaque ids; palette is the only place ids become colors.

[3] render.py — pygame/OpenGL core. Provides: window/GL init (init_gl),
    TexCache, Ship (with .pos, .q, .update(dt,keys) doing WASD/arrows 6-DOF
    flight, .apply_view()), camera, distance fog (set_fog, DARKNESS_START/END,
    CLEAR_COLOR via palette), the wall QUEUE + flush_walls(ship_pos), and
    helpers ship_right(q), ship_up(q), ship_forward(q).
    *** quat_look_along(direction, up=(0,1,0)) -> quat [w,x,y,z]: orients body
    so forward=-Z points along direction; NaN-safe; RUNTIME-VERIFIED that
    ship_forward(quat_look_along(d)) ~= normalize(d) for many d and the
    parallel-to-up edge case. Use it; never hand-roll quaternions. ***
    Likely also has a 2D text path (begin_2d / draw_text / end_2d-ish) for HUD.

[4] robots.py — robot hulls, scanners, and HOLOGRAMS (the math holograms are
    drawn via the mathtext path). Robots bob/track. Drawn in hub.draw_robots
    (opaque hulls depth-sort after the wall flush; scanners/holograms emissive).
    *** RE-PASTE to learn how a robot exposes its world position, its identity,
    and (critically) whether/how it carries its REQUIRED MATHEMATICIAN/technique
    id and its readable hologram content. ***

[5] corridor_builder.py — builds CorridorGeometry from one CorridorData: a BENT
    corridor (atrium doorway -> bend -> blue cavern) with its robots/stations.
    BUILT + FLOWN.

[6] hub_builder.py — build_hub(level_data) -> HubGeometry. level_data is an
    iterable of CorridorData. Builds the grey atrium sphere + N doorways spread
    via FIBONACCI SPHERE, each leading to a corridor (from corridor_builder).
    HubGeometry exposes (verify exact names on re-paste): spawn_pose() ->
    (pos,(yaw,pitch)); door_poses() -> list of (center,outward_normal);
    update(dt,ship_pos); draw_world(cr,cu,tc) [QUEUE-ONLY, no internal flush];
    draw_robots(cr,cu,tc); draw_labels(cr,cu,tc); likely an inside()/hub.inside
    test. There is a mathematical PROOF (verified) that with N up to ~12 doors
    (Fibonacci/collision canon) corridors do NOT intersect — grey rock separates
    every door-pair. FLOWN at N=7 successfully. Tunables for DeepSeek:
    ATRIUM_RADIUS, ATRIUM_FACETS, DOOR_FRAME_DEPTH, DOOR_OPENING_SCALE.
    *** RE-PASTE to learn how to ENUMERATE readable stations + robots (with
    world positions + stable ids) from the built geometry. ***

[7] level_parser.py — SIBLING of content_parser (content_parser UNCHANGED).
    load_level(path) -> Level, where path is a MANIFEST file (Option A format):
        title: <level name>
        corridors:
          corridors/01_xxx.txt
          corridors/02_xxx.txt
          corridors/03_xxx.txt
    (paths relative to the manifest's dir). Level.title -> str;
    Level.corridors -> list[CorridorData] (ordered, DISTINCT, never cloned);
    Level.__iter__ yields CorridorData in order; Level.__len__.
    *** Level IS iterable of CorridorData, so build_hub(level) works directly. ***
    discover_levels(folder="levels") -> list[str] (returns MANIFEST PATHS, not
    parsed Levels — intentional asymmetry vs discover_corridors, RULED & locked:
    you list many levels cheaply, parse only the one you play).
    Hard ParseError on: missing manifest, missing fixture, DUPLICATE corridor in
    a manifest, empty/missing/duplicate title, content after corridors:, or any
    inner corridor parse error (propagated with file:line). NEVER clones to pad N.
    Fixtures on disk: corridors/01_dummy.txt, 02_dummy.txt, 03_dummy.txt (all
    distinct), and levels/intro.txt ("Introduction to Placeholders", 3 corridors).
    These are PLACEHOLDER fixtures — real curriculum content is a DeepSeek TODO.

[8] app.py — MINIMAL INTEGRATION (BUILT + FLOWN, "works great" per Nir). Loads
    levels/intro.txt -> build_hub(level) -> spawns Ship at hub.spawn_pose()[0],
    aimed at door 0's normal via render.quat_look_along -> runs the canonical
    frame loop -> WASD/arrows flight, ESC/close to quit. flush_walls called
    exactly once (slot 8). Passes only (cr,cu,tc) to hub draws — NO palette/
    ledger in app, prime law preserved. Fog (40,140,CLEAR_COLOR). SHOW_HUD=False
    flag for an optional fps/pos overlay via render's 2D path. Bad manifest ->
    one stderr line + exit code 2 (a content error never masquerades as a black
    screen). NO gameplay — pure integration proof. THE WORLD IS FLYABLE.

DEFERRED CLEANUP (low priority): hub_demo.py has a STALE comment "(No
quat_look_along exists.)" and spawns the ship at identity orientation. It's demo
scaffolding; fix only if you revisit it. app.py does it correctly.

##############################################################################
## 6. WHAT REMAINS — THE GAMEPLAY TIER (the previous parent had NOT written these
##    correctly; section 2 is the corrected design they must follow)
##############################################################################

The world is flyable but there is NO GAMEPLAY yet. Remaining work implements the
section-2 combat loop: read robot -> identify required mathematician -> fire
matching missile -> kill -> advance -> rescue hostages.

CRITICAL FIRST STEP BEFORE ANY GAMEPLAY BRIEF — A DISCOVERY/AUDIT:
You do NOT currently know, from this document, the exact DATA SHAPE of the
combat-critical facts. Before writing the combat briefs, have a child (or ask
Nir to paste files and you read them yourself) ANSWER THESE, from the REAL files:
  Q1. Does each ROBOT in CorridorData/robots already carry a "required
      technique / required mathematician id"? If NOT, this must be ADDED to the
      corridor fixture format + content_parser + robots (a parent-authored
      change), because it's the spine of combat.
  Q2. What is the set of MATHEMATICIAN-MISSILES? Is it defined anywhere yet?
      (Likely NOT — you may need to define an "arsenal" of mathematician ids.)
      Where should "which mathematicians does the couple have" live?
  Q3. How is a robot's READABLE content (the hologram/plaque text that lets the
      player identify the required mathematician) exposed — position + id + the
      displayed math? (robots.py / hub_builder.py.)
  Q4. How do you enumerate the ORDERED robots blocking a given corridor, and how
      do you know which one is "next/blocking" (the one the ship must clear)?
  Q5. CONFIRM WITH NIR: what happens on a WRONG-mathematician shot? (Open design
      question — see section 2.)
The mathematics-blind law means the engine matches IDs: robot.required_id ==
fired_missile_id. Meaning stays in content + the human's head.

SUGGESTED REMAINING BRIEFS (re-scope freely based on the discovery answers;
the previous parent's old module split was WRONG because it treated "reading"
as standalone — reading is the IDENTIFY step INSIDE combat):

  BRIEF #9 — COMBAT / ENGAGEMENT (the coupled core mechanic).
    Owns the chain: detect the blocking robot ahead -> the player READS it,
    which REVEALS (to the player, via existing render/hologram emphasis) the
    robot's required technique -> player SELECTS a mathematician-missile -> FIRE
    -> MATCH CHECK (required_id == fired_id) -> on match: robot destroyed,
    advance; on mismatch: per Q5 design. "Reading" here is the reveal/identify
    affordance (proximity + look-at focus on the blocking robot), NOT a separate
    goal and NOT auto-selecting the weapon. It must NOT add/move flush_walls,
    NOT reorder the loop, NOT interpret math meaning, NOT assign color. It is a
    CONSUMER of render/hub/robots; if it needs a robot.required_id accessor or a
    render highlight, it REQUESTS that from you. Provide the 1-2 lines app adds
    (after ship.update: combat.update(ship.pos, ship_forward, fire_input)).
    Ships a combat_demo.py Nir flies: fly to a robot, read it, fire right
    mathematician -> it dies and you pass; fire wrong -> per Q5.

  BRIEF #10 — ARSENAL / MISSILES (may merge into #9 if small).
    The set of mathematician-missiles the couple carries; selecting the active
    one (keys/cycle); the projectile's flight/visual (reuse render primitives,
    NO new glyph rendering). Each missile carries a mathematician id (the thing
    the match check compares). NO meaning interpretation.

  BRIEF #11 — GAME_STATE (progression & win/lose).
    The corridor-as-gauntlet: ordered robots must be cleared to advance; the
    HOSTAGES at the corridor end are the prize; reaching/rescuing them = win;
    define lose conditions with Nir. Consumes combat's "robot destroyed" events
    and "is the path clear" state. Ties the level together. NO new rendering of
    glyphs; NO color meaning.

For EACH brief, follow the standard structure (see section 7 template). Keep
each child to ONE concern, open with the FRESH-CHAT GATE (re-paste real files),
restate the PRIME LAW and the CARDINAL FLUSH TRAP, fence off scope, and end with
a Completion Report template. Then Nir tests it and reports back; you ledger it
and proceed.

##############################################################################
## 7. CHILD-BRIEF TEMPLATE (the structure every brief must follow)
##############################################################################

A good DESCENT QED child brief contains, in order:
  - TITLE: which module, one-line purpose, and "you build ONE concern."
  - FRESH-CHAT GATE: child's FIRST action = ask Nir to paste the COMPLETE
    verbatim contents of the SPECIFIC files this module depends on. "Pasted
    files are LAW. If a reminder disagrees with a file, the FILE wins."
  - WHO ELSE IS INVOLVED: DeepSeek (builder/committer), Nir (courier+tester,
    non-technical), the parent (you, owns architecture, child has no memory of
    other chats), Completion Report carried up by Nir.
  - THE PRIME LAW: mathematics-blindness (section 2). Restate it.
  - WHY THIS MODULE EXISTS: the gap it fills.
  - WHAT TO BUILD: the public interface / locked signatures, crisply.
  - ENGINE CANON if relevant: canonical frame order + CARDINAL FLUSH TRAP.
  - WHAT YOU MUST NOT DO: fence scope hard (no reaching into other modules; no
    gameplay creep; no flush changes; no color meaning; request, don't reach).
  - A *_demo.py spec that Nir can RUN to verify, with explicit ACCEPTANCE.
  - COMPLETION REPORT template: files, run-verified?, final locked signatures,
    what it consumed + how constructed verbatim, deviations/traps/REQUESTS TO
    PARENT, old-code reuse, DeepSeek TODOs.

##############################################################################
## 8. HOW TO BEHAVE WHEN YOU RESUME (instructions to future-you)
##############################################################################

1. Greet Nir warmly. Acknowledge you've absorbed this handoff and confirm you
   hold the REAL game design (section 2) — recite the combat loop back to him in
   one short paragraph so he KNOWS you have it. This is exactly the check that
   caught the previous parent's drift.
2. Re-establish the LEDGER: treat sections 5 & 6 as your living ledger. As new
   reports arrive, add details blocks / update status.
3. Before writing any GAMEPLAY brief, run the DISCOVERY (section 6, Q1-Q5):
   ask Nir to paste content_parser.py, robots.py, hub_builder.py,
   corridor_builder.py, and one real corridor fixture, and READ them to learn
   whether robots carry a required-mathematician id and where readable content
   lives. Do NOT write combat until you know this. If the required-id does not
   exist in the data, your FIRST gameplay brief is a small parent-authored
   change to the fixture format + content_parser + robots to ADD it (a
   "required_technique_id" per robot), because it is the spine of combat.
4. Confirm the open WRONG-SHOT design question (Q5) with Nir.
5. Then write Brief #9 (combat), wait for Nir's tested report, ledger it, then
   #10, then #11. After #11, the game is playable end-to-end: fly a real level,
   read robots, fire the right mathematicians, clear corridors, rescue hostages.
6. PROTECT AGAINST YOUR OWN CONTEXT LOSS: if this conversation grows very long,
   PROACTIVELY offer Nir an updated version of THIS handoff document so he always
   has a current lifeboat. Never let the design fall out of attention silently.
   If you ever feel unsure about the game design, RE-READ SECTION 2 — do not
   confabulate. Section 2 is LAW.

##############################################################################
## 9. ONE-PARAGRAPH SUMMARY (if you read nothing else, read this)
##############################################################################

DESCENT QED is a 6-DOF flying proof-game. A couple in a spaceship descends
corridors to rescue HOSTAGES at the end. ROBOTS block the way and must be
DESTROYED to pass. Each robot requires a SPECIFIC MATHEMATICIAN'S technique;
your MISSILES ARE MATHEMATICIANS; you must FIRE THE MISSILE WHOSE MATHEMATICIAN
THE ROBOT REQUIRES. READING the robot is how the player IDENTIFIES which
mathematician is required — reading alone does nothing; it enables the correct
kill. The ENGINE IS MATHEMATICS-BLIND: it only matches opaque ids
(robot.required_id == fired_id); all MEANING lives in the content and the
player's head. The world tier (parser, palette, render, robots, corridor &
hub builders, level parser, and a minimal integration app) is BUILT and FLYABLE.
What remains is the gameplay tier: combat (read->identify->fire->match->kill->
advance), arsenal (mathematician-missiles), and game_state (progression + win
via hostage rescue). Build it one module per child, files-are-law, prime-law-
preserved, testing each before proceeding.
================================================================================
END OF HANDOFF DOCUMENT
================================================================================