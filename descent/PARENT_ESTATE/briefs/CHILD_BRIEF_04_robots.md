===========================================================
CHILD BRIEF #4 — MODULE: robots
Project: DESCENT QED engine. You are a CHILD chat.
===========================================================

WHO YOU ARE
A fresh Claude chat assigned ONE module: robots. You design and
write its code in full. DeepSeek (Nir's builder, agentic in
OpenCode, reliable on mechanical/asset/tuning tasks, less clever
than you) commits your verbatim code to GitHub and works a copy
until it runs. Nir is courier and tester: NOT technical, very
smart; he runs the code and sends SCREENSHOTS. You have no memory
of other chats. Everything you need is here. When done you DIE
with a Completion Report (template at end).

THE PRIME LAW
The engine is MATHEMATICS-BLIND. A robot knows nothing about what
its math means. It receives a RobotData object (already parsed)
and a Palette, and from those it derives only: its EYE COLOR (from
a ledger key) and its hologram/eye visuals. It NEVER interprets
equations, never reads files, never picks colors by meaning.

================ THE SINGLE MOST IMPORTANT RULE ================
ROBOTS ARE NOT HUMANOID. This is the #1 trap in the whole project.
When anyone hears "robot" they imagine a head/arms/legs figure.
DESCENT QED ROBOTS ARE NOTHING LIKE THAT. They are HOVERING
MACHINES — no legs, no feet, no ground contact, floating at
corridor mid-height. If you ever feel tempted to add a head, a
face, arms, or legs: STOP. That is the failure mode this rule
exists to prevent.

BODY SIMPLICITY RULE (LOCKED canon — quote-faithful):
A robot body is a GENERIC VESSEL, never a sculpture of its math.
ONE robot = ONE simple compact body:
  - a single faceted hull (one prism/box, optional wedge nose),
    ~20–60 triangles total;
  - ONE glowing EYE BAND (an emissive quad/strip);
  - TWO stubby side pods (tool-mounts, NOT arms);
  - hover-bob (slow vertical sinusoid) + slow YAW toward the player.
Per-robot variation comes ONLY from: size, hull proportions,
a 2-color paint job, and EYE COLOR (= the ledger color of the
concept it guards). NO multi-part sculptures, NO shape gimmicks,
NO geometry that encodes mathematical meaning. The meaning lives
in equations/reading-layers/colors/briefing text — NOT in the body.
(A previous architect once proposed a robot shaped like an infinite
product. Once. Do not be that architect.)

VISUAL BIBLE — ROBOT APPEARANCE (observed from real Descent):
- CHUNKY LOW-POLY HULLS: angular faceted bodies — wedges, prisms,
  truncated pyramids; silhouettes industrial, like flying mining
  equipment (canonically they ARE hijacked mining machines).
- A CENTRAL glowing EYE: one sensor strip / lens band on the hull
  (no neck, no separate head).
- SIDE-MOUNTED stubby pods hanging from the flanks (tool-mounts).
- BOLD 2–3 COLOR paint jobs reading as team colors against dark
  walls. (The world is grey; the robot's PAINT may be one of the
  few non-grey things — but its EYE specifically carries MEANING
  via the ledger color. Keep paint distinct from eye.)
- SIZE: robots are roughly ship-sized or bigger; they FILL and
  credibly BLOCK a corridor.
- MOTION: bob/hover in place, slow yaw to face the player, slight
  idle drift — alive, mechanical, patient.

HOLOGRAM — ALWAYS ON (LOCKED canon):
A simplified wireframe-ish HOLOGRAM of the mathematician the robot
is vulnerable to floats ABOVE the robot, automatically, from the
start. NO scanning step, NO reveal mechanic — always visible.
(Rationale, locked: players should spend fresh mental energy
forming the face<->math association, not guessing among weapons.)
For THIS module: you do NOT have real mathematician portraits yet
(no asset files exist). So render the hologram as a PLACEHOLDER:
a translucent, faintly-glowing billboard quad above the robot
showing placeholder text (e.g. the robot's NAME or a generic
"[HOLOGRAM]" mathtext label) via render's mathtext billboard.
Leave a clear DeepSeek TODO + naming convention for swapping in a
real portrait texture later (faces/<name>.png). The hologram
should read as "hovering, holographic" (low alpha, maybe a subtle
bob of its own / slight color tint), not as a solid sign.

CONTEXT — WHAT ALREADY EXISTS (frozen, do not modify)
Module 1 content_parser.py, Module 2 palette.py, Module 3 render.py
are DONE. You IMPORT and CALL them; you never edit them.

From content_parser you receive RobotData (ALREADY PARSED):
  RobotData:
    number: int
    name: str
    briefing_hint: str
    problem: str
    explain: dict   # "mathematician"/"physicist"/"biologist"/"engineer"
    segments: list  # Segment(latex, ledger_key, exemplify)
    eye_color_key: str   # a ledger key, or "NEUTRAL"
    fizzles: dict
  (You will mainly use: name, eye_color_key. The equation/explain
   content is the reading_system's job, NOT yours. Do not render
   the problem text on the robot body.)

From palette (Module 2) — the SINGLE source of colors:
  Palette(ledger) with:
    .eye(key) -> (r,g,b)   # BRIGHT emissive glow, hue-preserving,
                           # NEUTRAL -> neutral bright grey
    .tint(key), .text_color_on(key), .blend_rgb(a,b)
  Use palette.eye(robot_data.eye_color_key) for the EYE BAND color.
  (Confirm the import form with Nir if unsure; he can paste
   palette.py's top. Do NOT invent colors.)

From render (Module 3) — the SINGLE source of drawing verbs.
  Frozen toolbox (use EXACTLY these; do NOT assume other names):
    init_gl, set_fog
    draw_wall(...)            # translucent fill + solid edge, two-pass
    draw_breadcrumb(...)      # a glowing point (seen through walls)
    draw_box_edges(...)       # box wireframe edges
    draw_billboard(...)       # camera-facing textured quad; caller
                              # passes camera_right & camera_up
    latex_to_surface, surface_to_texture, TexCache.get_mathtext
    begin_2d, end_2d, draw_texture, draw_text_mathtext_2d
  IMPORTANT render facts (canon):
    * render OWNS production FOG toward palette.CLEAR_COLOR
      (DARKNESS_START=40, DARKNESS_END=140). Far things darken;
      keep the eye/hologram bright enough to read at corridor
      mid-distance.
    * The REAL camera does not exist yet. render's Ship/quat_* are
      DEMO-ONLY. Therefore robots must RECEIVE camera_right and
      camera_up (and a ship/camera position for yaw-toward-player)
      as PARAMETERS. A robot NEVER owns or queries the camera.
    * NEVER place a TexCache.get_mathtext id inside a display list
      (texture-id recycling trap). If you display-list the static
      hull geometry, that is fine — but keep the eye glow, hologram
      billboard, and any mathtext OUT of the list.
  If you need a render verb that does not exist (e.g. a filled
  flat triangle for hull facets), DO NOT invent it inside robots
  in a way that duplicates render's job — instead either (a) build
  the hull from existing verbs (draw_wall can make quads; a hull
  can be quads), or (b) note a precise "render needs verb X"
  request in your Completion Report for the parent to schedule.
  Prefer (a): build the faceted hull from quad walls/triangles you
  emit with the same fixed-function GL style render uses, keeping
  colors from palette. State your choice in the report.

YOUR GOAL — implement robots.py providing:

  class Robot:
      def __init__(self, robot_data, palette, station_pose,
                   paint=None, size=1.0):
          # station_pose: position (and optional base orientation)
          #   where this robot sits in the corridor — PASSED IN by
          #   the (future) corridor_builder. For THIS module's demo,
          #   you may place it manually.
          # paint: optional 2-color paint job (two RGB tuples). If
          #   None, choose a default grey-metal + accent. Paint is
          #   DECORATION; the EYE color (from palette) is MEANING.
          # size: scalar; robots fill a corridor.
          # eye color is taken from palette.eye(robot_data.eye_color_key).

      def update(self, dt, ship_position):
          # advance hover-bob (slow vertical sinusoid) and slow YAW
          # toward ship_position. No physics, no collision here.

      def draw(self, camera_right, camera_up, texcache):
          # draw the faceted hull (flat-shaded, hidden-face removal
          #   ok), the glowing eye band, two stubby pods, and the
          #   ALWAYS-ON hologram billboard above it (placeholder
          #   text for now). Pull all colors from palette/paint.
          #   Use camera_right/up for the hologram billboard facing.

      def play_defeat(self):
          # trigger the defeat animation state (see below).

      def is_defeated(self) -> bool

  DEFEAT FIREBALL:
  On play_defeat(), the robot enters a short defeat animation: a
  bright ORANGE/YELLOW fireball — a billboard flash + briefly
  expanding sphere/quad — then the robot stops drawing its body.
  (Weapons/hit-logic that DECIDE defeat live in another module;
  robots only PLAYS the animation when told.) Keep the fireball
  cheap: an expanding camera-facing billboard with a hot color,
  fading out. After it finishes, is_defeated() stays True and
  draw() may draw nothing (or a faint marker — your call; the
  PLAQUE that replaces a defeated robot belongs to corridor_builder,
  not here — do NOT draw a plaque).

  HELPER (optional but encouraged):
  A module-level make_robot(robot_data, palette, station_pose, ...)
  factory mirroring the interface map, if cleaner.

THE TEST SCENE (your proof) — a SEPARATE file robots_demo.py
Reuse render's DEMO-ONLY camera (Ship/quat_*) to fly around.
Build robots straight from the REAL fixture so the data path is
proven end to end:
  - import content_parser; corridor = parse_corridor(
        "corridors/01_dummy.txt"); ledger = corridor.ledger
  - build Palette(ledger)
  - create Robot(corridor.robots[0], palette, pose_A) and
    Robot(corridor.robots[1], palette, pose_B), placed a few units
    apart at corridor mid-height.
  - Robot 0 (Dummy Sentinel Alpha) has eye_color_key "alpha" (red)
    -> eye glows RED.
  - Robot 1 (Dummy Sentinel Beta) has eye_color_key "delta"
    (blend alpha+beta) -> eye glows ORANGE. This proves the eye
    color flows from ledger -> palette -> robot correctly.
  - Each shows its ALWAYS-ON placeholder hologram above it.
  - Both bob and slowly yaw to face the camera as Nir flies around.
  - Bind a key (e.g. K) to call play_defeat() on the nearest robot
    so Nir can SEE the fireball and the robot vanish.
  - Keep CLEAR_COLOR / fog from render so the scene is the real
    greyscale-world look; the red and orange eyes must POP against
    grey (the chroma-as-meaning payoff).

DEEPSEEK-HANDOFF CLAUSE (some real boilerplate/tuning here)
Mark mechanical/tuning work inline as:
  # TODO(DeepSeek): <exact recipe> | ACCEPTANCE: <check>
and repeat at file end under  # === DEEPSEEK TODO SUMMARY === .
Likely DeepSeek TODOs:
  - real mathematician portrait textures for the hologram, naming
    convention faces/<name>.png + a loader hook (you define the
    convention; he wires the file load);
  - bob amplitude/speed, yaw speed, fireball duration/size TUNING
    after Nir's flight (name the constants);
  - any asset/path plumbing.
YOU design hull geometry, eye, hologram behavior, fireball logic.
Do NOT outsource the design to DeepSeek.

WHAT YOU MUST NOT DO
- Do NOT make the robot humanoid in ANY way. No head, face, arms,
  legs. (Re-read the Body Simplicity Rule.)
- Do NOT encode math meaning in the body shape.
- Do NOT render the problem text/equations on the robot (that is
  reading_system's job).
- Do NOT draw a plaque (corridor_builder's job).
- Do NOT own the camera; receive camera_right/up + ship_position.
- Do NOT do hit detection / weapon logic (weapons module).
- Do NOT modify content_parser / palette / render.
- Do NOT place a mathtext texture id inside a display list.
- Do NOT invent colors; use palette.
- Ambiguity -> most literal reading + a "trap discovered" note.

TEST PLAN (how Nir verifies via SCREENSHOTS)
1. Confirm the fixture corridors/01_dummy.txt exists (Module 1).
2. Nir runs robots_demo.py and sends SCREENSHOTS showing:
   - two clearly NON-HUMANOID hovering faceted machines at corridor
     mid-height (Nir should be able to say "those are flying
     machines, not little people");
   - robot 0's eye glowing RED, robot 1's eye glowing ORANGE,
     popping against the grey fogged world;
   - the always-on placeholder hologram floating above each;
   - both robots facing the camera as he flies around (yaw works);
   - a screenshot mid-fireball after pressing K, and one after,
     showing the robot gone.
3. Iterate with DeepSeek until it reads right (industrial, hovering,
   patient; eyes carry the meaning-color; nothing humanoid).

SUCCESS CRITERIA
- robots.py: Robot with __init__/update/draw/play_defeat/
  is_defeated as specified (final signatures documented).
- Non-humanoid faceted hull + eye band + two pods, hover-bob +
  yaw-to-player, always-on hologram (placeholder), defeat fireball.
- Eye color flows ledger -> palette.eye -> robot (red & orange
  proven from the fixture).
- All colors from palette; all drawing via render's frozen verbs;
  camera received, never owned; no mathtext in display lists.

WHEN DONE — COMPLETION REPORT (one page):
  COMPLETION REPORT — module robots — <date>
  FILES CREATED: robots.py, robots_demo.py
  PUBLIC INTERFACES (verbatim FINAL signatures of Robot + any
     factory):
  KEY DECISIONS: hull construction (verbs used / triangle count);
     how the hull was drawn given render's verb set (and any
     "render needs verb X" request); display-list usage (and the
     note keeping eye/hologram/mathtext OUT of lists); hologram
     placeholder approach + portrait naming convention; fireball
     implementation; default paint; bob/yaw constants.
  DEVIATIONS FROM BRIEF: none / list.
  TRAPS DISCOVERED: anything later modules MUST know — especially
     the station_pose convention and the camera-vector / ship-
     position parameters corridor_builder & game_state must supply.
  OLD-CODE REUSE: exactly what (if any) was mined from Fable's code
     (he had a "probably working but untried" robots attempt — ask
     Nir to paste it as REFERENCE ONLY; implement THIS interface,
     do not copy its structure).
  DEEPSEEK TODOS LEFT OPEN: list (portraits, tuning, assets).
Nir carries this back to the parent; DeepSeek commits it to
/PARENT_ESTATE/reports/.
===========================================================
END CHILD BRIEF #4
===========================================================