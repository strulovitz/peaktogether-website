===========================================================
CHILD BRIEF #5 — MODULE: corridor_builder
Project: DESCENT QED engine. You are a CHILD chat.
===========================================================

WHO YOU ARE
A fresh Claude chat assigned ONE module: corridor_builder. You
design and write its code in full. DeepSeek (Nir's builder,
agentic in OpenCode, reliable on mechanical/tuning tasks, less
clever than you) commits your verbatim code to GitHub and works a
copy until it runs. Nir is courier and tester: NOT technical, very
smart; he runs the code and sends SCREENSHOTS. You have no memory
of other chats. Everything you need is here. When done you DIE
with a Completion Report (template at end).

THE PRIME LAW
The engine is MATHEMATICS-BLIND. corridor_builder lays out GEOMETRY
from a parsed CorridorData. It never interprets equations and never
chooses a color by meaning. The only meaning-colors it uses come
from palette via ledger keys carried in the data (e.g. a corridor's
dominant color = palette color of its FIRST ledger primary).

SCOPE DISCIPLINE — READ FIRST
You build ONE corridor's spatial layout: an octagonal tube along a
given direction, robot STATIONS along its centerline (and the
Robot objects placed at them), a chevron-framed ENTRANCE mouth,
PLAQUE slots that appear where a robot has been defeated, and a
HOSTAGE ROOM capping the far end with blue hostage figures.
You do NOT build:
  - the hub or multiple corridors (that is hub_builder, next);
  - the camera / flight / lock-on (game_state/app);
  - the reading system, weapons, or HUD content.
At most ONE new engine concept per step; this module is "a corridor
as a place." Stay in that lane.

CONTEXT — WHAT ALREADY EXISTS (frozen; import, never modify)
Module 1 content_parser.py, Module 2 palette.py, Module 3 render.py,
Module 4 robots.py are DONE.

From content_parser — parsed data (already built):
  parse_corridor(path) -> CorridorData
  CorridorData:
    number, title, flavor, briefing_intro, entry_text, exit_text,
    robots: list[RobotData], ledger: ColorLedger
  ColorLedger: primaries (dict key->"red"/"yellow"/"blue"),
               blends (dict key->(a,b)), is_defined(key)
  (The corridor's DOMINANT color = palette color of its FIRST
   primary key — use the first key in ledger.primaries insertion
   order. If there are no primaries, fall back to a neutral grey.)

From palette — single source of colors:
  Palette(ledger): .tint(key)->rgba, .text_color_on(key)->rgb,
  .eye(key)->rgb, .blend_rgb(a,b)->rgb
  WORLD CONSTANTS (the ONLY place these live):
    CLEAR_COLOR, WORLD_WALL_FILL (rgba), WORLD_EDGE (rgb),
    HOSTAGE_BLUE, HAZARD_YELLOW, HAZARD_BLACK, BACKDROP_BASE_ALPHA
  Use WORLD_WALL_FILL/WORLD_EDGE for tube walls (greyscale world),
  HAZARD_YELLOW/HAZARD_BLACK for chevrons, HOSTAGE_BLUE for hostages.

From render — single source of drawing verbs (use EXACTLY these):
    init_gl, set_fog
    draw_wall(...)            # two-pass translucent fill + solid edge
    draw_breadcrumb(...)      # glowing point (seen through walls)
    draw_box_edges(...)       # box wireframe edges
    draw_billboard(...)       # camera-facing textured quad
    latex_to_surface, surface_to_texture, TexCache.get_mathtext
    begin_2d, end_2d, draw_texture, draw_text_mathtext_2d
  render OWNS production FOG toward CLEAR_COLOR (DARKNESS_START=40,
  DARKNESS_END=140): the far end of a long tube will DARKEN. Design
  corridor LENGTH and label brightness with that in mind (a corridor
  that is too long will fade its hostage room to black — pick a
  length where the far room is still faintly visible, or accept the
  reveal-as-you-approach effect intentionally and say so).
  The REAL camera does not exist yet; render's Ship/quat_* are
  DEMO-ONLY. Your demo may use them. Your build_* functions must NOT
  own a camera; drawing functions that need it RECEIVE camera_right/
  up (and ship_position for robots) as parameters.
  NEVER place a TexCache.get_mathtext id inside a display list
  (texture-id recycling trap). Static tube geometry MAY be display-
  listed; keep labels/holograms/mathtext OUT of the list.

From robots — the guardian objects:
  Robot(robot_data, palette, station_pose, paint=None, size=1.0)
    station_pose accepts (x,y,z) OR ((x,y,z), base_yaw_radians).
  robot.update(dt, ship_position)
  robot.draw(camera_right, camera_up, texcache)
  robot.play_defeat(); robot.is_defeated() -> bool
  You CREATE the Robot objects (one per robot_data) and place them
  at the station positions you compute. You then expose them so the
  caller can update/draw/defeat them.

REFERENCE-ONLY OLD CODE (genuinely relevant here)
Fable's earlier prototype had corridor-related logic. ASK NIR to
paste it as REFERENCE ONLY:
  - ROBOT_SLOTS / corridor import / a module-level ROBOTS list
    (per Module 4's report) — these are corridor-placement ideas;
  - any tube/section geometry Fable used.
It predates these contracts. Implement THIS interface; mine only
matching plumbing (e.g. how he built tube cross-sections) and note
reuse in your report. Do NOT copy his structure.

YOUR GOAL — implement corridor_builder.py providing:

  class CorridorGeometry:
      # the built, drawable corridor. Holds wall geometry, station
      # poses, the Robot objects, plaque slots, chevron entrance,
      # and the hostage room.
      def update(self, dt, ship_position) -> None
          # forward to each living robot's update; advance any
          # ambient animation (e.g. hostage idle, plaque fade-in).
      def draw(self, camera_right, camera_up, texcache) -> None
          # draw tube walls (greyscale two-pass), corner edge-glow
          # strips in the corridor's DOMINANT color, chevron mouth,
          # living robots, plaques for defeated robots, hostage room.
      def stations(self) -> list            # station poses in order
      def get_robots(self) -> list[Robot]    # in corridor order
      def entrance_pose(self):               # where the mouth sits
          # (position + outward normal/direction) — hub_builder will
          # use this to attach the corridor to a hub door.
      def on_robot_defeated(self, robot) -> None
          # reveal the plaque slot at that robot's station (the
          # robot itself stops drawing via its own is_defeated()).

  def build_corridor(corridor_data, direction, start_point=(0,0,0),
                     hub_radius=0.0, palette=None) -> CorridorGeometry
      # direction: a unit 3-vector the tube extrudes along (later
      #   from hub_builder; for the demo you pass e.g. (1,0,0) or
      #   (0,0,-1)).
      # start_point + hub_radius: the mouth begins at
      #   start_point + direction*hub_radius (so later it sits on
      #   the hub surface). For a standalone demo hub_radius=0.
      # palette: a Palette built from corridor_data.ledger; if None,
      #   build one internally from corridor_data.ledger.
      # Returns a CorridorGeometry with N robots placed (N =
      #   len(corridor_data.robots), DERIVED, never declared).

GEOMETRY SPEC (the design, be faithful):
  - OCTAGONAL tube cross-section (8 walls), a comfortable radius
    (propose a constant TUBE_RADIUS ~ 6.0 world units; robots
    (size~1 ~ a few units) should FILL it enough to read as
    "blocking"). Name it as a constant; DeepSeek may tune.
  - Tube CENTERLINE runs from the entrance (start_point +
    direction*hub_radius) straight along `direction` for a total
    length sized so N robots have breathing room AND the far
    hostage room is still (faintly) reachable through fog. Propose
    STATION_SPACING (~18 units) and an entrance/exit margin; total
    length = derived from N. State the numbers.
  - CORNER EDGE-GLOW: thin emissive strips along the 8 lengthwise
    corners, in the corridor's DOMINANT ledger color (palette of
    first primary). This is the corridor's "hue family" (Visual
    Bible) and doubles as the bright wireframe of the walls recipe.
  - ROBOT STATIONS: evenly spaced along the centerline at corridor
    mid-height (tube center), facing back toward the entrance
    (toward the incoming player). Create one Robot per robot_data
    at each station (pass the station pose; robots will yaw to the
    player themselves).
  - CHEVRON ENTRANCE: the tube mouth framed with yellow/black
    diagonal hazard chevrons (HAZARD_YELLOW/HAZARD_BLACK) — flat
    quads, instantly readable as "blocked/danger beyond." A label
    billboard just inside the mouth shows the corridor TITLE
    (mathtext via render), facing the incoming player.
    (Per the Visual Bible, a chevron frame may ALSO mark each
    robot station as "blocked passage" — optional; if cheap, add a
    subtle chevron ring at each station. State your choice.)
  - PLAQUES: when a robot is defeated (on_robot_defeated), reveal a
    calm floating PLAQUE at that station showing a short summary —
    for now use the robot's NAME (real summary text will come from
    content later; the field exists as briefing_hint / a future
    plaque field — use robot_data.name or briefing_hint as the
    placeholder and NOTE this). Flying back through a cleared
    corridor should read as a museum of plaques. Plaque = a
    backdrop quad (palette tint of the robot's eye key, low alpha)
    + mathtext label, billboarded to face the reader.
  - HOSTAGE ROOM: an irregular faceted cavern (NOT a clean box —
    a few angled walls) capping the far end, containing 1–3 simple
    blue hostage FIGURES (the ONE place humanoid shapes are
    correct: a capsule body + sphere head, HOSTAGE_BLUE). They
    stand and gently idle. Rescue logic (fly-through) belongs to
    game_state; here just BUILD and DRAW them, and expose their
    position(s) via a method e.g. hostage_positions().

THE TEST SCENE (your proof) — a SEPARATE file corridor_demo.py
  - import content_parser; corridor_data = parse_corridor(
        "corridors/01_dummy.txt")
  - build Palette from corridor_data.ledger
  - geom = build_corridor(corridor_data, direction=(0,0,-1),
        palette=palette)   # extrude down -Z so the demo camera
                           # flies INTO it from the entrance
  - use render's DEMO-ONLY Ship/quat_* camera to fly down the tube
  - each frame: geom.update(dt, ship_position);
        geom.draw(camera_right, camera_up, texcache)
  - the two dummy robots (eye RED and ORANGE from the fixture)
    stand at their stations, bobbing and facing the camera;
  - bind a key (e.g. K) to defeat the nearest living robot ->
    its plaque appears; fly back to SEE the museum effect;
  - fly to the far end to SEE the hostage room with blue figures.
  Visual goals Nir should confirm in SCREENSHOTS:
    octagonal grey tube with colored corner glow; chevron mouth +
    title; two non-humanoid robots blocking the way; defeating one
    leaves a plaque; blue hostages waiting at the end; greyscale
    world with chroma only where it means something.

DEEPSEEK-HANDOFF CLAUSE
Mark mechanical/tuning work inline:
  # TODO(DeepSeek): <recipe> | ACCEPTANCE: <check>
and repeat at file end under  # === DEEPSEEK TODO SUMMARY === .
Likely TODOs: TUBE_RADIUS / STATION_SPACING / corridor length /
chevron stripe count / plaque size + fade timing TUNING after Nir's
flight; any asset plumbing. YOU design the geometry and layout
logic; DeepSeek tunes numbers and wires assets.

WHAT YOU MUST NOT DO
- Do NOT build the hub or more than one corridor.
- Do NOT own the camera; receive camera_right/up + ship_position.
- Do NOT do lock-on, reading, weapons, or rescue logic.
- Do NOT make the robots (they exist); only place/own them here.
- Do NOT make hostages anything but simple blue capsule+sphere
  figures (the only allowed humanoids), and do NOT make robots
  humanoid.
- Do NOT invent colors; use palette + world constants.
- Do NOT place mathtext ids in display lists.
- Do NOT modify the four frozen modules.
- Ambiguity -> most literal reading + a "trap discovered" note.

TEST PLAN (Nir verifies via SCREENSHOTS)
1. Confirm fixture corridors/01_dummy.txt exists.
2. Nir runs corridor_demo.py, flies in, sends screenshots:
   octagonal tube + corner glow; chevron mouth + title label;
   two hovering non-humanoid robots blocking; press K -> plaque
   appears; far-end hostage room with blue figures.
3. Iterate with DeepSeek on tuning until it reads as a real Descent
   corridor: a place you fly through, robots blocking, museum of
   plaques behind you, hostages ahead.

SUCCESS CRITERIA
- corridor_builder.py: CorridorGeometry + build_corridor with the
  signatures above (final versions documented).
- Octagonal tube along a given direction; N robots placed (derived);
  chevron entrance + title; plaques on defeat; hostage room with
  blue figures at the end.
- Dominant-color corner glow from palette; greyscale world; chroma
  only where meaningful.
- entrance_pose() exposes the mouth so hub_builder can attach it.
- All drawing via render's frozen verbs; camera received not owned;
  no mathtext in display lists.

WHEN DONE — COMPLETION REPORT (one page):
  COMPLETION REPORT — module corridor_builder — <date>
  FILES CREATED: corridor_builder.py, corridor_demo.py
  PUBLIC INTERFACES (verbatim FINAL signatures of CorridorGeometry
     methods + build_corridor + entrance_pose() return shape +
     hostage_positions()):
  KEY DECISIONS: TUBE_RADIUS, STATION_SPACING, total-length rule vs
     fog; chevron approach; plaque placeholder text source; hostage
     count/shape; display-list usage (mathtext kept out); how
     dominant color is chosen.
  DEVIATIONS FROM BRIEF: none / list.
  TRAPS DISCOVERED: anything hub_builder & game_state MUST know —
     ESPECIALLY the exact shape returned by entrance_pose()
     (position + direction/normal) since hub_builder attaches to it,
     and the station_pose form passed to robots.
  OLD-CODE REUSE: exactly what was mined from Fable's corridor code.
  DEEPSEEK TODOS LEFT OPEN: list.
Nir carries this back to the parent; DeepSeek commits it to
/PARENT_ESTATE/reports/.
===========================================================
END CHILD BRIEF #5
===========================================================