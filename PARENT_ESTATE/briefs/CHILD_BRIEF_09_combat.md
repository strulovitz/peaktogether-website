================================================================
BRIEF #9 (CORRECTED) — COMBAT, flyable on its own.
Includes the data spine + the Maxwell test corridor so it stands
alone and Nir can fly it. The weapons/face PANEL is child #10.
Hostage RESCUE is child #11. Do NOT build those here.

EVERYTHING IN THIS BRIEF IS VERBATIM GROUND TRUTH from the live
engine. Where a format/signature is quoted, COPY IT EXACTLY. Do
NOT invent formats. Do NOT reinvent helpers that already exist.
================================================================

YOU ARE a fresh Opus child building ONE concern: COMBAT — flying up
to a robot, firing a mathematician-technique at it, and either
destroying it (right one) or a harmless gentle fizzle (wrong one).
You have NO memory of other chats. Everything you need is below,
quoted verbatim. Do NOT ask to see files. Write complete, runnable
code. Nir (human) flies it; DeepSeek commits it.

----------------------------------------------------------------
WHO IS INVOLVED
----------------------------------------------------------------
- Nir: human courier + tester, NON-TECHNICAL. Runs/flies it, reports
  what he SEES. Cannot judge code. Be warm, friendly, use ":-)".
- DeepSeek: builder. Commits your verbatim code; mechanical tuning only.
- Parent/Architect: owns design. You report up via the Completion
  Report Nir carries back. Stay inside this brief's scope.

----------------------------------------------------------------
THE GAME (the law you serve)
----------------------------------------------------------------
A couple pilots one ship down a corridor toward hostages. ROBOTS block
the way; you cannot fly past them. Each robot is destroyed by ONE
mathematician's technique. MISSILES ARE mathematicians. A BLUE HOLOGRAM
of the defeating mathematician already floats above each robot (drawn by
robots.py) as a deliberate GIVE-AWAY. The player matches that face to a
fired technique. Goal: build the intuition "this kind of problem <->
this technique's face".

GENTLE-DESIGN LAWS (sacred; add no challenge):
- NO losing, NO failure, NO time pressure, NO score.
- INFINITE ammo. Firing never depletes anything.
- Wrong missile -> HARMLESS FIZZLE + a warm panel saying WHY it doesn't
  fit and HINTING the correct one. Teaching, never punishment.
- Aiming MAXIMALLY FORGIVING: any distance/angle wins if the right
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
  (3) the keys of robot.fizzles (each FIZZLE's weapon-name == a tech id)
Wrong id X fired -> show robot.fizzles[X]. The correct id is NOT a
fizzle key. Arsenal ids for this build, exactly:
  gauss_e, gauss_m, faraday, ampere, maxwell

================================================================
PART A — DATA SPINE (content_parser.py + robots.py)
================================================================
GOAL: add one field to RobotData and surface it (+ .number + fizzles)
on the runtime Robot. The parser uses a TOKENIZER, not regex. Match it.

--- A1. content_parser.py ---
The VERBATIM current RobotData dataclass is:

    @dataclass
    class RobotData:
        number: int
        name: str
        briefing_hint: str
        problem: str
        explain: dict           # keys: mathematician, physicist, biologist, engineer
        segments: list          # list[Segment]
        eye_color_key: str      # a ledger key, or "NEUTRAL"
        fizzles: dict           # weapon_name -> why-not text

ADD exactly one field at the end:
        required_technique_id: str

The tokenizer yields these token shapes (VERBATIM):
    ("kv",    keyword, value, lineno)            # KEYWORD: value
    ("block", keyword, arg, body, lineno)        # KEYWORD { body }  (arg=None)
                                                 # FIZZLE <name> { body } (arg=name)
So  VULNERABLE_TO { gauss_e }  arrives as:
    ("block", "VULNERABLE_TO", None, " gauss_e ", lineno)

The VERBATIM current _parse_robot() dispatch loop is:

    for tok in toks[1:]:
        if tok[0] == "kv":
            raise ParseError(f"{fname}:{tok[3]}: unexpected single-value line {tok[1]}: inside robot")
        keyword, arg, body, ln = tok[1], tok[2], tok[3], tok[4]
        if keyword == "NAME":
            name = _clean_body(body)
        elif keyword == "BRIEFING_HINT":
            briefing_hint = _clean_body(body)
        elif keyword == "PROBLEM":
            problem = _clean_body(body)
        elif keyword in _explain_map:
            explain[_explain_map[keyword]] = _clean_body(body)
        elif keyword == "SEGMENTS":
            segments = _parse_segments(body, ledger, fname, ln)
        elif keyword == "EYE":
            key = _clean_body(body).strip()
            if not ledger.is_defined(key):
                raise ParseError(f"{fname}:{ln}: EYE key {key!r} not defined in ledger")
            eye = key
        elif keyword == "FIZZLE":
            if arg is None:
                raise ParseError(f"{fname}:{ln}: FIZZLE missing weapon name")
            fizzles[arg] = _clean_body(body)
        else:
            raise ParseError(f"{fname}:{ln}: unexpected robot block {keyword!r}")

MAKE THESE FOUR EDITS, matching the existing style exactly:
  (1) Where the per-robot accumulators are initialized (near `fizzles = {}`),
      add:   required_technique_id = None
  (2) Add a new dispatch branch (place it next to the EYE/FIZZLE branches),
      with validation matching the ParseError style:
        elif keyword == "VULNERABLE_TO":
            tok_id = _clean_body(body).strip()
            if not re.match(r'^[A-Za-z0-9_]+$', tok_id):
                raise ParseError(f"{fname}:{ln}: VULNERABLE_TO id must be [A-Za-z0-9_]+, got {tok_id!r}")
            required_technique_id = tok_id
      (Ensure `import re` exists; if not, add it.)
  (3) In the required-fields section (right after the `if eye is None:` check),
      add:
        if required_technique_id is None:
            raise ParseError(f"{fname}: robot {number} missing VULNERABLE_TO block")
  (4) In the `return RobotData(...)` call, add the kwarg:
        required_technique_id=required_technique_id,

_clean_body is VERBATIM:
    def _clean_body(body: str) -> str:
        """Trim a block body for prose fields..."""
        return _unescape_braces(body.strip())

ParseError raise style is always:  ParseError(f"{fname}:{lineno}: message")

--- A2. The 3 existing dummy fixtures will now fail to parse ---
Add to EACH robot in corridors/01_dummy.txt, 02_dummy.txt, 03_dummy.txt
exactly one line (place it near the robot's EYE line):
    VULNERABLE_TO { dummy_technique }
Change nothing else in those files.

--- A3. robots.py ---
The VERBATIM constructor signature is:
    def __init__(self, robot_data, palette, station_pose, paint=None, size=1.0):
CRITICAL FACT: today the constructor does NOT store robot_data; it only
extracts a couple of fields, e.g.:
    self.name = getattr(robot_data, "name", "[ROBOT]")
    self._eye_key = getattr(robot_data, "eye_color_key", "NEUTRAL")
So `fizzles`, `number`, `required_technique_id` are NOT reachable yet.

DO: in __init__, add one line storing the whole data object:
    self._robot_data = robot_data
Then add THREE read-only properties, mirroring the EXISTING property
style (here is the verbatim existing one to mirror):
    @property
    def position(self):
        """Public, read-only: the robot's CURRENT bobbed world-center..."""
        return self._world_center()
Add:
    @property
    def number(self):
        return self._robot_data.number
    @property
    def required_technique_id(self):
        return self._robot_data.required_technique_id
    @property
    def fizzles(self):
        return self._robot_data.fizzles
Do NOT touch drawing, bobbing, holograms, scanners, explosion, or
play_defeat/is_defeated.

================================================================
PART B — THE MAXWELL TEST CORRIDOR (new fixture content)
================================================================
Create corridors/maxwell.txt and levels/maxwell.txt. MATCH THE REAL
FORMAT BELOW EXACTLY. Below is a VERBATIM working robot block + header
from corridors/01_dummy.txt — copy its structure precisely:

    # ===========================================================
    # (comment lines start with #)
    # ===========================================================
    CORRIDOR: 1
    TITLE { Placeholder Corridor One }
    FLAVOR { A test tube where nothing means anything yet. }
    LEDGER {
      PRIMARY alpha = red
      PRIMARY beta  = yellow
      PRIMARY gamma = blue
      BLEND   delta = alpha + beta
    }
    BRIEFING_INTRO { This briefing page is placeholder text... }
    ENTRY_TEXT { You have entered the placeholder corridor. }
    EXIT_TEXT { You have cleared the placeholder corridor. Well done, tester. }

    ROBOT: 1
    NAME { Dummy Sentinel Alpha }
    BRIEFING_HINT { This robot is vulnerable to the placeholder technique FOO. }
    PROBLEM { Prove that the placeholder quantity $X$ equals the placeholder
              quantity $Y$ under the stated dummy conditions. }
    EXPLAIN_MATHEMATICIAN { Graduate-level placeholder... }
    EXPLAIN_PHYSICIST { Undergraduate placeholder... }
    EXPLAIN_BIOLOGIST { High-school placeholder... }
    EXPLAIN_ENGINEER { Plug in numbers: the quantity [[ $X$ | 3.000 ]] meets the
              quantity [[ $Y$ | 3.000 ]], so they match. }
    SEGMENTS {
      $X$       | alpha
      $=$       | NEUTRAL
      $Y$       | beta
    }
    EYE { alpha }
    VULNERABLE_TO { dummy_technique }
    FIZZLE BAR { The technique BAR does not apply here because... }
    FIZZLE BAZ { BAZ fizzles: it solves a different dummy problem. }

FORMAT RULES (do NOT deviate):
- Header blocks CORRIDOR:, TITLE, LEDGER, BRIEFING_INTRO, ENTRY_TEXT,
  EXIT_TEXT are ALL REQUIRED (parser raises if any missing). FLAVOR
  optional but include it.
- ROBOT: N  and  CORRIDOR: N  are single-value "kv" lines: a COLON,
  NO braces.
- The ONLY legal EXPLAIN names are EXPLAIN_MATHEMATICIAN,
  EXPLAIN_PHYSICIST, EXPLAIN_BIOLOGIST, EXPLAIN_ENGINEER. All four
  REQUIRED. Any other name raises ParseError.
- SEGMENTS lines are:  <mathtext-with-$...$> | <ledger_key or NEUTRAL>
  Math MUST be wrapped in $...$.
- Engineer value-arcs use:  [[ $expr$ | concrete_number ]]
- FIZZLE <id> { ... } : the <id> after FIZZLE is the technique id.

LEDGER GRAMMAR (verbatim rules):
    PRIMARY <key> = <color>          # color is one of: red, yellow, blue
    BLEND   <key> = <keyA> + <keyB>  # keyA,keyB distinct PRIMARY keys
- Max 3 PRIMARY entries. Palette decides blend color:
  red+blue = PURPLE, red+yellow = orange, yellow+blue = green.
- The parser does NOT assign blend colors; palette does.
For OUR corridor, use this exact ledger so red+blue -> purple:
    LEDGER {
      PRIMARY field_e = red
      PRIMARY field_b = blue
      BLEND   coupling = field_e + field_b
    }
KINDERGARTEN MIXING LAW: ledger key `coupling` (purple) appears ONLY on
robots 3 and 5, ONLY on the expression that genuinely couples E and B.
Single-field laws use pure field_e (red) or field_b (blue). Never use a
blend key as a standalone base.

SEGMENTS MATHTEXT — SAFE vs FORBIDDEN (matplotlib mathtext blacklist):
- SAFE (known-good): \frac \nabla \cdot \times \partial \mathbf{}
  \varepsilon \rho \mu subscripts _0 superscripts ^2 \sum \int \geq
  \leq \cdots \left( \right) \to \infty \approx \ln \log \pi \mathrm{}
  \Rightarrow
- FORBIDDEN (never use): \dfrac \tfrac \underbrace \color \text, and
  any AMSMath-only command.

Author FIVE robots IN THIS ORDER (robot 1 nearest the doorway). Each a
full ROBOT block with all required fields, EYE, VULNERABLE_TO, and a
FIZZLE entry for EACH WRONG technique id (warm why-it-doesn't-fit +
hint the right one). Fizzle ids are technique ids; never include the
robot's own id.

 #  NAME (clean, see hologram rule)  VULNERABLE_TO  EYE       physics
 1  Gauss Electric                   gauss_e        field_e   $\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}$
 2  Gauss Magnetic                   gauss_m        field_b   $\nabla \cdot \mathbf{B} = 0$
 3  Faraday                          faraday        coupling  $\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$   (couples E,B -> coupling/purple)
 4  Ampere                           ampere         field_b   $\nabla \times \mathbf{B} = \mu_0 \mathbf{J}$
 5  Maxwell                          maxwell        coupling  $\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}$   (couples E,B -> coupling/purple)

(EYE must be a ledger key defined above; `coupling` is fine for EYE.)

HOLOGRAM NAMING (verbatim formula in robots.py):
    def _portrait_filename(name):
        return name.strip().replace(" ", "_") + "-hologram.png"
ONLY spaces become underscores; apostrophes/parens pass through. So use
the CLEAN names above. Expected hologram files on disk (repo root or
next to robots.py):
    Gauss_Electric-hologram.png
    Gauss_Magnetic-hologram.png
    Faraday-hologram.png
    Ampere-hologram.png
    Maxwell-hologram.png
If a file is absent, robots.py falls back to mathtext text automatically
(no crash). List these exact filenames for Nir in your README.

LEVEL MANIFEST — create levels/maxwell.txt (verbatim format; paths
resolve relative to the levels/ dir):
    title: Maxwell Test Corridor
    corridors:
      ../corridors/maxwell.txt

================================================================
PART C — COMBAT (new module: combat.py)
================================================================
combat.py owns: finding the blocking robot, handling fire, matching
ids, defeat-or-fizzle, auto-facing the explosion, and drawing a MINIMAL
combat HUD (text only). The weapons/face PANEL is child #10 — do NOT
build it. Keep the "currently loaded technique" as a tiny local index
over this id list (id + display name only; NO images):
    ARSENAL = [("gauss_e","Gauss"), ("gauss_m","Gauss"),
               ("faraday","Faraday"), ("ampere","Ampere"),
               ("maxwell","Maxwell")]

VERBATIM signatures you will USE (do NOT reinvent any of these):

  # render.py 2D HUD (origin TOP-LEFT, y-down; must wrap text calls)
  render.begin_2d(w, h)
  render.end_2d()
  render.draw_text_mathtext_2d(cache, latex, x, y, color=(0.7,0.7,0.7),
                               fontsize=15, scale=1.0, alpha=1.0)
  # window size: app.py module constant WIN_SIZE = (1280, 800)
  #   -> w, h = WIN_SIZE

  # render.py quaternions ([w,x,y,z]; forward=-Z, right=+X, up=+Y)
  render.quat_mul(a, b)            -> [w,x,y,z]
  render.quat_normalize(q)         -> unit q
  render.quat_look_along(direction, up=(0,1,0)) -> unit [w,x,y,z]
      # orients ship FORWARD (-Z) along `direction`; roll minimized.
      # Guarantee: ship_forward(quat_look_along(d)) == normalize(d)
      # handles parallel/anti-parallel safely (no NaN)
  render.ship_forward(q) / ship_right(q) / ship_up(q) -> world vectors
  # NOTE: there is NO slerp helper. If you want smooth turning, build a
  # short nlerp yourself from quat_mul/quat_normalize (lerp the 4 comps
  # toward the target quat, then quat_normalize, fixing sign by checking
  # the dot product so you take the short way). Keep it small.

  # Ship public:  ship.pos (np.array xyz),  ship.q (np.array [w,x,y,z])

  # geometry:
  hub.corridors                         -> list[CorridorGeometry]
  CorridorGeometry.get_robots()         -> list[Robot] (path order; idx 0
                                           nearest the doorway)
  # Robot public (after Part A):
  robot.position  (property, bobbed world center np.array)
  robot.name, robot.number, robot.required_technique_id, robot.fizzles
  robot.is_defeated(), robot.play_defeat()  # explosion is AUTONOMOUS,
                                            # ~1.6s; caller does nothing else

C1. BLOCKING ROBOT: for the active corridor (use hub.corridors[0] for
    this single-corridor test), the blocking robot is the FIRST robot in
    get_robots() that is NOT is_defeated(). If all defeated -> path clear
    (this build just stops blocking; hostages are child #11).

C2. FIRE (rising edge of SPACE, not held). Compare the loaded id to the
    blocking robot's required_technique_id:
      - MATCH: call robot.play_defeat() (autonomous explosion). Start an
        "auto-face" state lasting ~1.0s: each frame nlerp ship.q toward
        render.quat_look_along(robot.position - ship.pos) so the couple
        watch the explosion. Match wins regardless of aim/range.
      - MISMATCH: HARMLESS. Do NOT defeat. Show the fizzle panel using
        robot.fizzles.get(loaded_id). No penalty. If that key is missing,
        show a generic gentle "that technique doesn't apply here" line.
      - If there is no blocking robot, SPACE does nothing.

C3. TEMPORARY SELECT (testing only; the real selector is child #10):
    keys '[' = prev, ']' = next, cycling the local index. Confirm in
    comments these don't collide with existing controls (WASD/RF move,
    arrow keys rotate, Q/E roll, Shift boost, SPACE fire).

C4. MINIMAL HUD (2D each frame, between begin_2d/end_2d, all via
    draw_text_mathtext_2d; NO images, NO face panel):
    - Top line: "VULNERABLE TO: <name>" where <name> is the display name
      of the blocking robot's required_technique_id looked up in ARSENAL.
      (id -> OUR label lookup; NOT math interpretation; allowed.) If no
      blocking robot: "PATH CLEAR".
    - A line: "LOADED: <name>" for the current selection so Nir sees what
      SPACE will fire.
    - On a mismatch, draw the fizzle text in a readable spot for a few
      seconds (wrap long text across lines yourself; the HUD text call
      does not wrap).

================================================================
PART D — WIRE INTO app.py (canonical frame order; do NOT break it)
================================================================
The level pipeline is VERBATIM:
    WIN_SIZE = (1280, 800)
    LEVEL_MANIFEST = "levels/intro.txt"
    level = _load_level_or_die(LEVEL_MANIFEST)        # -> Level
    hub = build_hub(level, atrium_center=(0, 0, 0))   # -> HubGeometry
    # hub.corridors[0].get_robots() -> list[Robot]
DO: change LEVEL_MANIFEST to "levels/maxwell.txt". Use the SAME pipeline
(load_level -> build_hub). Do NOT invent a new loader.

The current frame loop is, IN ORDER:
  1 clear; 2 ship.update; 3 ship.apply_view; 4 set_fog;
  5 cr=ship_right, cu=ship_up; 6 hub.update; 7 hub.draw_world;
  8 render.flush_walls(ship.pos)  <-- EXACTLY ONCE, never move/dup;
  9 hub.draw_robots; 10 hub.draw_labels; 11 pygame.display.flip()

THE FLUSH TRAP: flush_walls stays exactly once at slot 8, after
draw_world, before robots/labels. Moving/duplicating it makes the screen
silently BLACK. Do NOT touch it.

Insertions:
  - Read SPACE / '[' / ']' edges in the existing input handling; call
    combat.handle_input(...) and combat.update(dt, ship, hub) BETWEEN
    slot 6 (hub.update) and slot 7 (hub.draw_world). The auto-face nlerp
    of ship.q happens inside combat.update here (after ship.update ran
    this frame; new orientation applies next apply_view — acceptable).
  - Draw the combat HUD BETWEEN slot 10 (draw_labels) and slot 11 (flip),
    wrapped in render.begin_2d(*WIN_SIZE) / render.end_2d().

ENGINE CANON (guardrails):
  - Coords: right=+X, up=+Y, forward=-Z; quats [w,x,y,z].
  - Do NOT put mathtext texture ids into GL display lists.
  - Do NOT touch flush_walls placement (slot 8, once).

================================================================
HARD SCOPE FENCES (do NOT do)
================================================================
- Do NOT interpret math meaning; compare opaque ids only.
- Do NOT map meaning->color in code; you only WRITE ledger keys in the
  fixture; palette resolves colors.
- Do NOT build the weapons/face panel or load face images (child #10).
- Do NOT build hostages or rescue (child #11).
- Do NOT reinvent quaternion math — use render.quat_* as quoted.
- Do NOT invent fixture/parser formats — match the verbatim ones above.
- Do NOT redesign render/hub/corridor/palette internals. Consume the
  quoted public API. If one truly needs a change, STOP and list it under
  "REQUESTS TO PARENT" instead of editing it.
- Do NOT add scoring, lives, timers, or any fail state.

================================================================
ACCEPTANCE — what Nir should SEE flying levels/maxwell.txt
================================================================
1. Flying down the corridor, robot 1 blocks the way with a blue GAUSS
   hologram above it (if the PNG is on disk; else a text fallback). HUD
   top shows "VULNERABLE TO: Gauss".
2. HUD shows "LOADED: <name>"; ']' / '[' cycle it.
3. SPACE with the WRONG technique -> harmless; a gentle fizzle panel
   explains why it doesn't fit + hints the right one. Nothing lost.
4. Load Gauss, SPACE -> robot explodes; view gently turns to face the
   explosion; path opens; HUD advances to the next robot.
5. Works through all 5 (robots 3 and 5 show purple `coupling` in their
   segments; 1,2,4 stay pure red/blue). After the 5th: "PATH CLEAR".
6. No way to lose. No crashes. flush_walls untouched (no black screen).

In your README to Nir, list EXACTLY the 5 hologram filenames he must
place on disk (the Gauss_Electric / Gauss_Magnetic / Faraday / Ampere /
Maxwell ...-hologram.png names), and that absence just falls back to text.

================================================================
COMPLETION REPORT TEMPLATE (fill, give to Nir)
================================================================
BRIEF #9 COMPLETION REPORT
- Files created/modified:
- New module: combat.py
- FINAL LOCKED SIGNATURES (verbatim):
    RobotData new field:            required_technique_id: str
    Robot new properties:           .number / .required_technique_id / .fizzles
    Robot now stores:               self._robot_data = robot_data
    fixture directive added:        VULNERABLE_TO { <id> }
    combat public API:              handle_input(...) / update(dt, ship, hub) / draw_hud(...)
- Keys chosen (+ proof no collision with existing controls):
- Maxwell fixture: 5 robots, ids, ledger keys, segment latex used,
  value-arc examples, purple only on robots 3 & 5? (Y/N):
- Auto-face nlerp: how built from quat_mul/quat_normalize:
- Hologram filenames Nir must place on disk (exact):
- flush_walls confirmed untouched (slot 8, once)? (Y/N):
- Parser: VULNERABLE_TO added inside _parse_robot dispatch (not regex)? (Y/N):
- Run-verified in chat? (Y/N) (Nir tests on his machine):
- Deviations / traps hit / REQUESTS TO PARENT:
- Old code reused verbatim (what):
- DeepSeek TODOs (book-keeping only, exact recipe + acceptance):
================================================================
