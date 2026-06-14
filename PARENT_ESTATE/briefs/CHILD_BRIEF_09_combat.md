================================================================
BRIEF #9 — COMBAT (flyable on its own)
Includes the data spine + the Maxwell test corridor so it stands
alone and you can fly it. Arsenal panel (#10) and hostage rescue
(#11) come in later children — NOT here.
================================================================

YOU ARE a fresh Opus child building ONE concern: COMBAT — flying up
to a robot, firing a mathematician-technique at it, and either
destroying it (right one) or a harmless gentle fizzle (wrong one).
You have NO memory of other chats. Everything you need is in THIS
brief; all exact signatures are quoted verbatim. Do NOT ask to see
files. Write complete, runnable code. Nir (human) flies it; DeepSeek
commits it.

----------------------------------------------------------------
WHO IS INVOLVED
----------------------------------------------------------------
- Nir: human courier + tester. NON-TECHNICAL. He runs and flies the
  program and reports what he SEES. He cannot judge code quality.
  Be warm, friendly, use ":-)", explain plainly.
- DeepSeek: builder. Takes your verbatim code, commits to GitHub,
  mechanical tuning only.
- The Parent/Architect: owns design; you report up via a Completion
  Report Nir carries back. Stay inside this brief's scope.

----------------------------------------------------------------
THE GAME (the law you serve)
----------------------------------------------------------------
A couple pilots one ship down a corridor toward hostages. ROBOTS
block the way; you cannot fly past them. Each robot is destroyed by
ONE specific mathematician's technique. MISSILES ARE mathematicians.
A BLUE HOLOGRAM of the defeating mathematician already floats above
each robot (drawn by robots.py) as a deliberate GIVE-AWAY. The player
matches that face to a fired technique. Goal: build intuition
"this kind of problem <-> this technique's face".

GENTLE-DESIGN LAWS (sacred; add no challenge):
- NO losing, NO failure, NO time pressure, NO score.
- INFINITE ammo. Firing never depletes anything.
- Wrong missile -> HARMLESS FIZZLE + warm panel saying WHY it doesn't
  fit and HINTING the correct one. Teaching, never punishment.
- Aiming is MAXIMALLY FORGIVING: any distance/angle wins if the right
  missile is fired at the blocking robot. On a correct hit, smoothly
  turn the view to face the exploding robot so the payoff is seen.

PRIME LAW — MATHEMATICS-BLINDNESS (never break):
The engine NEVER interprets math meaning, never judges correctness,
never maps meaning->color. Combat compares OPAQUE STRING IDS only:
    robot.required_technique_id == fired_missile_id
All meaning lives in readable content + the human's head.

SHARED ID SPACE (critical):
ONE opaque id per technique, used identically in 3 places:
  (1) robot.required_technique_id
  (2) the fired missile's id
  (3) the keys of robot.fizzles
So fizzles is keyed by technique ids. Wrong id X fired -> show
robot.fizzles[X]. The correct id is NOT a fizzle key.
Arsenal ids for this build, exactly:
  gauss_e, gauss_m, faraday, ampere, maxwell

----------------------------------------------------------------
PART A — DATA SPINE (content_parser.py + robots.py)
----------------------------------------------------------------
RobotData currently has NO field naming which technique defeats it.
Add it; surface two accessors on the runtime Robot.

A1. content_parser.py — current verbatim RobotData:
        @dataclass
        class RobotData:
            number: int
            name: str
            briefing_hint: str
            problem: str
            explain: dict
            segments: list
            eye_color_key: str
            fizzles: dict
    ADD one field:  required_technique_id: str
    Parse it from a new per-robot fixture directive written as:
        VULNERABLE_TO { gauss_e }
    (single token: letters/digits/underscores). REQUIRED on every
    robot; if missing, raise the parser's existing ParseError style
    with file:line. Match the file's existing directive parsing
    (it already parses NAME { ... }, EYE { ... }, etc.).

A2. The 3 dummy fixtures will now fail to parse. Add to EACH robot in
    corridors/01_dummy.txt, 02_dummy.txt, 03_dummy.txt exactly one
    line:  VULNERABLE_TO { dummy_technique }
    Change nothing else in those files.

A3. robots.py — the Robot constructor is:
        def __init__(self, robot_data, palette, station_pose,
                     paint=None, size=1.0):
    Add two read-only public accessors (match the file's property
    style):
        Robot.number                -> robot_data.number
        Robot.required_technique_id  -> robot_data.required_technique_id
    No behavior change. Do NOT touch drawing, bobbing, holograms,
    scanners, explosion, or play_defeat/is_defeated.

----------------------------------------------------------------
PART B — THE MAXWELL TEST CORRIDOR (new fixture content)
----------------------------------------------------------------
Create corridors/maxwell.txt and a manifest levels/maxwell.txt.

Manifest format (verbatim style of the existing one):
    title: <name>
    corridors:
      ../corridors/maxwell.txt
(Paths resolve relative to the levels/ directory.)

SEGMENTS syntax:  <mathtext> | <ledger_key>  ; NEUTRAL = no color.
EXPLAIN blocks + value-arc syntax [[ $expr$ | value ]] already work.
Define the corridor LEDGER (mirror the dummy fixtures' LEDGER syntax
exactly) with these keys:
    red    = electric field E   (ingredient primary)
    blue   = magnetic field B   (ingredient primary)
    purple = a genuine E+B combination (red+blue)

KINDERGARTEN MIXING LAW (obey): purple ONLY on robots 3 and 5, ONLY on
the expression that genuinely couples E and B. Single-field laws stay
pure red or blue. Never purple as a standalone base.

Author FIVE robots IN THIS ORDER (robot 1 nearest the doorway). Each a
full ROBOT block: number, NAME, BRIEFING_HINT, PROBLEM (formal
Wikipedia register), all four EXPLAIN_* (engineer uses
[[ $expr$ | value ]] arcs with plausible numbers), SEGMENTS with the
ledger keys, EYE { <key> }, VULNERABLE_TO, and a FIZZLE entry for EACH
WRONG technique id (warm, clear, why-it-doesn't-fit + hint the right
one). Fizzle keys are technique ids; never include the robot's own id.

 1  Gauss's Law (Electric) | gauss_e | red    | div E = rho/eps0
 2  Gauss's Law (Magnetic) | gauss_m | blue   | div B = 0
 3  Faraday's Law          | faraday | purple | curl E = -dB/dt (couples E,B -> purple)
 4  Ampere's Law           | ampere  | blue   | curl B = mu0 J
 5  Maxwell's Correction   | maxwell | purple | add mu0 eps0 dE/dt (couples E,B -> purple)

At the TOP of maxwell.txt put these comment lines (asset manifest):
 # faces:     faces/gauss.png faces/faraday.png faces/ampere.png faces/maxwell.png  (natural color, 512x512)
 # holograms: holograms/gauss.png holograms/faraday.png holograms/ampere.png holograms/maxwell.png (blue, 512x512)
 # gauss_e AND gauss_m both use the Gauss face/hologram (one image, two robots)

----------------------------------------------------------------
PART C — COMBAT (new module: combat.py)
----------------------------------------------------------------
combat.py owns: finding the blocking robot, handling fire, matching
ids, defeat or fizzle, auto-facing the explosion, and drawing the
minimal combat HUD (lock-on label + fizzle panel).

NOTE: the full weapons panel + girlfriend face-selection is a LATER
child (#10). For THIS build, the player switches the loaded technique
with a TEMPORARY keypress (see C3) so firing is testable now. Keep the
"currently loaded technique id" in a tiny local state inside combat.py
(a simple index over the arsenal id list below). Do NOT build a panel.

Arsenal id list for selection (id + display name only; no images yet):
    [("gauss_e","Gauss"), ("gauss_m","Gauss"), ("faraday","Faraday"),
     ("ampere","Ampere"), ("maxwell","Maxwell")]

Verbatim signatures you will use:
  render.begin_2d(w, h) / render.end_2d()
  render.draw_text_mathtext_2d(cache, latex, x, y,
       color=(0.7,0.7,0.7), fontsize=15, scale=1.0, alpha=1.0)
  render.ship_forward(q) / ship_right(q) / ship_up(q)
  Ship public: ship.pos (np.array xyz), ship.q (np.array [w,x,y,z])
  CorridorGeometry.get_robots() -> list[Robot]  (path order; index 0
       nearest the doorway)
  HubGeometry.corridors -> list[CorridorGeometry]
  Robot.position (property, bobbed world center), Robot.name,
       Robot.number, Robot.required_technique_id,
       Robot.play_defeat(), Robot.is_defeated()

C1. BLOCKING ROBOT: For the active corridor (you may use
    hub.corridors[0] for this single-corridor test), the blocking
    robot is the FIRST robot in get_robots() that is NOT
    is_defeated(). If all are defeated, the path is clear (this build
    just stops blocking; hostages come in #11).

C2. FIRE (rising edge of SPACE, not held). Compare the loaded id to
    the blocking robot's required_technique_id:
      - MATCH: call robot.play_defeat() (explosion is autonomous,
        ~1.6s). Set an "auto-face" state: over ~1s smoothly slerp
        ship.q so ship_forward points at robot.position, so the couple
        watch it. Match wins regardless of aim/range.
      - MISMATCH: HARMLESS. Do NOT defeat. Show the fizzle panel with
        the blocking robot's fizzles[loaded_id]. No penalty. If that
        key is missing for any reason, show a generic gentle line.
      - If there is no blocking robot (all defeated), SPACE does
        nothing.

C3. TEMPORARY SELECT (testing only, removed/replaced in #10): keys
    '[' = prev technique, ']' = next technique, cycling the local
    index. Confirm in comments these don't collide with existing
    controls (WASD/RF move, arrows rotate, Q/E roll, Shift boost,
    SPACE fire).

C4. MINIMAL HUD (2D, each frame, via begin_2d/end_2d):
    - Top: lock-on label "VULNERABLE TO: <name>" where <name> is the
      display name of the blocking robot's required_technique_id,
      looked up in the arsenal list above. (This is an id->OUR-label
      lookup, NOT math interpretation — allowed.) If no blocking
      robot: "PATH CLEAR".
    - Also show "LOADED: <name>" for the currently selected technique
      so Nir can see what SPACE will fire.
    - On a mismatch, draw the fizzle text in a readable panel
      (wrap long text) for a few seconds.
    Use draw_text_mathtext_2d for all text. Do NOT build a face panel.

----------------------------------------------------------------
PART D — WIRE INTO app.py (canonical frame order; do NOT break it)
----------------------------------------------------------------
Current loop, in order:
  1 clear; 2 ship.update; 3 ship.apply_view; 4 set_fog;
  5 cr=ship_right, cu=ship_up; 6 hub.update; 7 hub.draw_world;
  8 render.flush_walls(ship.pos)  <-- EXACTLY ONCE, never move/dup;
  9 hub.draw_robots; 10 hub.draw_labels; 11 pygame.display.flip()

THE FLUSH TRAP: flush_walls must stay exactly once, at slot 8, after
draw_world and before robots/labels. Moving or duplicating it makes
the screen silently BLACK. Do NOT touch it.

Insertions:
  - Read SPACE / '[' / ']' edges in the existing input handling and
    call combat.handle_input(...) and combat.update(dt, ship)
    BETWEEN slot 6 (hub.update) and slot 7 (hub.draw_world). The
    auto-face slerp of ship.q happens in combat.update here (after
    ship.update ran this frame; new orientation applies next
    apply_view — acceptable).
  - Draw the combat HUD (lock-on + loaded + fizzle panel) BETWEEN slot
    10 (draw_labels) and slot 11 (flip), wrapped in begin_2d/end_2d.
  - Load the MAXWELL level (levels/maxwell.txt) for this test instead
    of intro.txt, so the flown corridor is the Maxwell one. Build it
    through the SAME pipeline the existing app uses to build the
    hub/corridor from a level manifest — mirror existing code; do not
    invent a new pipeline.

ENGINE CANON (guardrails):
  - Coords: right=+X, up=+Y, forward=-Z; quats [w,x,y,z].
  - Do NOT put mathtext texture ids into GL display lists.
  - Do NOT touch flush_walls placement (slot 8, once).

----------------------------------------------------------------
HARD SCOPE FENCES (do NOT do)
----------------------------------------------------------------
- Do NOT interpret math meaning anywhere; compare opaque ids only.
- Do NOT map meaning->color in code; ledger keys are author labels
  resolved by palette. You only WRITE keys in the fixture.
- Do NOT build the weapons/face panel or load face images — that is
  child #10. Do NOT build hostages or rescue — that is child #11.
- Do NOT redesign render/hub/corridor/palette internals. Consume their
  public API as quoted. If one needs a change, STOP and list it under
  "REQUESTS TO PARENT" instead of editing it.
- Do NOT add scoring, lives, timers, or any fail state.

----------------------------------------------------------------
ACCEPTANCE — what Nir should SEE flying levels/maxwell.txt
----------------------------------------------------------------
1. Flying down the Maxwell corridor, robot 1 blocks the way with a
   blue GAUSS hologram floating above it; HUD top shows
   "VULNERABLE TO: Gauss".
2. HUD shows "LOADED: <name>"; pressing ']' / '[' cycles it.
3. SPACE with the WRONG technique loaded -> harmless; a gentle fizzle
   panel explains why it doesn't fit and hints the right one. Nothing
   is lost.
4. Load Gauss, press SPACE -> robot explodes; view gently turns to
   face the explosion; the path opens; HUD updates to the next robot.
5. Works through all 5 robots (3 and 5 show purple coupling in their
   segments; 1,2,4 stay pure red/blue). After the 5th: "PATH CLEAR".
6. No way to lose. No crashes. flush_walls untouched (no black screen).

Provide a short README note to Nir listing EXACTLY which hologram image
files he must place on disk and their filenames, derived from the
robot NAME fields you wrote (robots.py loads <Name>-hologram.png). If
the existing hologram lookup is by robot NAME, state the exact names.

----------------------------------------------------------------
COMPLETION REPORT TEMPLATE (fill, give to Nir)
----------------------------------------------------------------
BRIEF #9 COMPLETION REPORT
- Files created/modified:
- New module: combat.py
- FINAL LOCKED SIGNATURES (verbatim):
    RobotData new field:           required_technique_id: str
    Robot.number / .required_technique_id:
    combat public API (handle_input / update / draw_hud):
    fixture directive added:       VULNERABLE_TO { <id> }
- Keys chosen (and proof they don't collide with existing controls):
- Maxwell fixture: 5 robots, ids, ledger keys, value-arc examples:
- Auto-face implementation (how the slerp works):
- Hologram filenames Nir must place on disk (exact, NAME-derived):
- flush_walls confirmed untouched (slot 8, once)? (Y/N):
- Run-verified in chat? (Y/N) (Nir tests on his machine):
- Deviations / traps hit / REQUESTS TO PARENT:
- Old code reused verbatim (what):
- DeepSeek TODOs (book-keeping only, exact recipe + acceptance):
================================================================

This is **combat only** — flyable on its own (fold-in data spine + Maxwell corridor), with a temporary `[ ]` selector so you can test firing now. The real weapons panel (#10) and hostage rescue (#11) stay as their own children, exactly as the previous parent planned. 🙂
