===========================================================
CHILD BRIEF #3 — MODULE: render
Project: DESCENT QED engine. You are a CHILD chat.
===========================================================

WHO YOU ARE
A fresh Claude chat assigned ONE module: render — the engine's
low-level drawing toolbox. You design and write its code in full.
DeepSeek (Nir's builder, agentic in OpenCode, reliable on
mechanical/platform tasks, less clever than you) commits your
verbatim code to GitHub and works a copy until it runs. Nir is
courier and tester: NOT technical, very smart; he runs the code
and sends SCREENSHOTS. You have no memory of other chats.
Everything you need is here. When done you DIE with a Completion
Report (template at end).

CRITICAL SCOPE DISCIPLINE — READ FIRST
This module is the PRIMITIVE TOOLBOX ONLY. You build the drawing
verbs and ONE throwaway TEST SCENE that exercises them. You do
NOT build corridors, robots, the hub, the reading system, or any
game content — those are OTHER modules that will later CALL your
verbs. If you feel tempted to draw a corridor or a robot, STOP:
draw only the generic primitives below, and a test scene made of
them. (Engine rule: at most ONE new engine concept per step; this
module is already a big one.)

THE PRIME LAW
The engine is MATHEMATICS-BLIND. render knows nothing about math,
corridors, or color meaning. It receives colors and geometry as
plain numbers from callers and draws them. It NEVER imports
content_parser and NEVER interprets a ledger key.

CONTEXT — WHAT ALREADY EXISTS (frozen, do not modify)
Module 1 content_parser.py and Module 2 palette.py are DONE.
- You may IMPORT palette to pull WORLD COLOR CONSTANTS (so the
  test scene uses the canonical greys/clear-color), namely:
    palette.CLEAR_COLOR      = (0.045, 0.055, 0.10)
    palette.WORLD_WALL_FILL  = (0.16, 0.17, 0.20, 0.85)  # RGBA
    palette.WORLD_EDGE       = (0.88, 0.90, 0.94)         # RGB
    palette.HAZARD_YELLOW, palette.HAZARD_BLACK, etc.
  (Confirm exact access form with Nir: they may be module-level
   constants or class attributes — ASK Nir to paste palette.py's
   top section if unsure. Do NOT redefine these colors yourself;
   palette is the single source.)
- Do NOT modify content_parser.py or palette.py.

TECH CONSTRAINTS (hard rules, inherited canon)
- Legacy FIXED-FUNCTION OpenGL ONLY: glBegin/glEnd, glColor,
  glVertex, GL_LINE_STIPPLE ok. NO shaders, NO modern VBO/VAO
  pipeline. Deps: pygame, PyOpenGL, numpy, matplotlib.
- Display lists for HEAVY STATIC geometry; key = a rounded state
  tuple; glDeleteLists + rebuild on change.
- draw_latex_3d MUST NEVER be placed inside a display list
  (the texture cache recycles texture ids; baking a tid into a
  list will later draw the WRONG texture). This is a known trap.
- mathtext ONLY for any LaTeX you render (matplotlib mathtext).
  SAFE: \frac \sum \int \geq \leq \cdots \cdot \left( \right)
  \to \infty \approx \ln \log \pi \zeta \qquad \mathrm{} \mathbf{}
  \Rightarrow.  FORBIDDEN: \tfrac \dfrac \underbrace \color \text,
  any AMSmath. (For THIS module's test scene you only need a
  couple of simple mathtext strings to prove rendering works.)

THE LOOK YOU SERVE (so the test scene looks right)
- GREYSCALE WORLD: background near-black (CLEAR_COLOR); walls dark
  grey translucent fill; edges light-grey/white wireframe lines.
- WALLS RECIPE: each wall quad is drawn TWICE:
    (a) translucent flat-shaded FILL, alpha = (1 - wall_transparency)
    (b) bright EDGE lines (WORLD_EDGE) drawn ON TOP.
  A single wall_transparency value in [0,1] blends between
  "automap wireframe look" (transparency high -> faint fill) and
  "solid Descent look" (transparency low -> opaque fill).
  Default wall_transparency = 0.5.
- CHROMA = MEANING only: the test scene may show a couple of
  colored quads/points to prove tinting + breadcrumb glow work,
  but the structural world stays grey.
- Billboards: faces/text/holograms will (later) be drawn as
  camera-facing textured quads. You provide the billboard verb;
  you do NOT provide any actual face images (none exist yet) —
  use a placeholder solid-color or a simple mathtext texture.

YOUR GOAL — implement render.py providing this public toolbox.
(Signatures are a STARTING CONTRACT; you may refine names/params
for cleanliness, but DOCUMENT every final signature in the report,
because later modules will be written against exactly these.)

  --- GL lifecycle / modes ---
  init_gl(width, height) -> None
      # enable depth test, blending (GL_SRC_ALPHA,
      # GL_ONE_MINUS_SRC_ALPHA), set clear color = CLEAR_COLOR,
      # set up a perspective projection helper. Fixed-function.
  set_perspective(width, height, fov=70.0, near=0.1, far=4000.0)
  begin_2d(width, height) -> None   # switch to ortho/screen space
  end_2d() -> None                  # restore 3D projection
  clear() -> None                   # glClear color+depth

  --- 3D primitives ---
  draw_quad(p0, p1, p2, p3, rgba) -> None
      # a single flat-shaded translucent quad (the wall FILL).
  draw_quad_edges(p0, p1, p2, p3, rgb) -> None
      # the 4 bright edge lines on top (the wall wireframe).
  draw_wall(p0, p1, p2, p3, fill_rgba, edge_rgb,
            wall_transparency=0.5) -> None
      # convenience: does the TWO-PASS walls recipe in one call.
      # final fill alpha = fill_rgba's alpha * (1 - wall_transparency).
  draw_line_3d(a, b, rgb, width=1.0) -> None
  draw_point_3d(p, rgb, size=4.0) -> None
      # for breadcrumb glow points seen through walls.
  draw_box(center, size, fill_rgba, edge_rgb) -> None
      # axis-aligned box via draw_wall x6 — a generic building
      # block (NOT a robot; just a box). Useful for test scene.

  --- billboards & textures ---
  class TexCache:
      # caches matplotlib-mathtext-rendered textures.
      def get_latex(self, latex_str, fontsize, rgb)
                        -> (tex_id, w, h)
      # Renders mathtext to an RGBA surface (white or given rgb
      # text on TRANSPARENT background), uploads as a GL texture,
      # caches by (latex_str, fontsize, rgb). Returns id + pixel
      # size. NOTE the recycling trap: ids may be reused if the
      # cache evicts — document your eviction policy (or "no
      # eviction, grows unbounded for now" is acceptable for the
      # slice; just STATE it).
  draw_texture_2d(tex_id, x, y, w, h, alpha=1.0) -> None
      # draw a cached texture in 2D screen space (HUD, labels).
  draw_billboard(tex_id, center3d, world_w, world_h,
                 camera_right, camera_up, alpha=1.0) -> None
      # draw a texture as a camera-facing quad in the 3D world.
      # camera_right/up are passed in by the caller (the eventual
      # camera/game_state owns the camera; you just consume them).
  draw_latex_3d(latex_str, center3d, height_world, rgb,
                camera_right, camera_up, texcache, alpha=1.0) -> None
      # convenience: render mathtext via texcache + draw_billboard.
      # REMINDER: callers must NOT cache this inside a display list.

  --- 2D helpers (for HUD/labels later) ---
  draw_rect_2d(x, y, w, h, rgba) -> None
  draw_text_mathtext_2d(latex_str, x, y, fontsize, rgb, texcache,
                        alpha=1.0) -> None

REUSE — OLD CODE IS GENUINELY USEFUL HERE
A previous architect (Claude Fable, now unavailable) wrote engine
plumbing you can mine: quaternion helpers, latex_to_surface /
TexCache, begin_2d/end_2d, draw_rect, draw_texture, draw_box,
draw_latex_3d, a 60-FPS pygame App skeleton, display-list caching
discipline. ASK NIR to paste that old code and treat it as
REFERENCE ONLY: it predates these contracts and did not anticipate
this module split. You MAY adapt its mathtext-to-texture and 2D/3D
mode-switch logic where it MATCHES the signatures above, but:
  - rename/reshape to THESE signatures,
  - strip anything game-specific (it is a generic toolbox now),
  - note exactly what you reused in your report.
Do NOT copy its overall structure or any slider-demo content.

THE TEST SCENE (your proof it works) — a SEPARATE file
Build a small runnable program (e.g. render_demo.py) that opens a
window and draws a STATIC test scene exercising every verb:
  - clear to CLEAR_COLOR;
  - a few grey translucent WALLS via draw_wall forming a short
    open box/room the camera sits inside (this is NOT a corridor
    module — it is just walls proving the recipe);
  - bright wireframe edges visible on those walls;
  - one or two colored draw_point_3d "breadcrumbs" placed BEHIND
    a translucent wall, to prove they glow through (greyscale-
    world payoff);
  - one draw_box;
  - one 3D billboard showing a simple mathtext string via
    draw_latex_3d (e.g. "$\frac{\pi^2}{6}$") that always faces the
    camera;
  - a 2D HUD overlay via begin_2d/end_2d: a draw_rect_2d panel and
    a draw_text_mathtext_2d label (e.g. "$\zeta(2)$");
  - a wall_transparency control: let Nir change it (e.g. keys
    [ and ] or +/-) and SEE the walls blend between wireframe-ish
    and solid. This single control demonstrates the whole walls
    recipe.
  - basic camera: it is fine to use a simple fixed or
    arrow-key/WASD free-look camera JUST for the demo (you may
    mine Fable's quaternion Ship for this) — but mark the camera
    as DEMO-ONLY; the real camera belongs to a later module.
The demo's job is purely visual verification via screenshots.

DEEPSEEK-HANDOFF CLAUSE (this module HAS real boilerplate)
Mark genuinely mechanical/platform work inline as:
  # TODO(DeepSeek): <exact recipe> | ACCEPTANCE: <check>
and repeat all at file end under  # === DEEPSEEK TODO SUMMARY === .
Expected DeepSeek TODOs here may include:
  - pygame window/display creation flags + OpenGL context attribs
    for Nir's Windows 11 machine (DOUBLEBUF|OPENGL, resizable,
    Esc to quit, H/F1 help);
  - the exact pip install line in a comment
    (pip install pygame PyOpenGL numpy matplotlib);
  - any platform-specific matplotlib backend setting needed to
    rasterize mathtext to an array headlessly (Agg).
YOU design the GL/render logic; DeepSeek does window plumbing and
tuning. Do NOT outsource any drawing logic to DeepSeek.

WHAT YOU MUST NOT DO
- Do NOT build corridors, robots, hub, reading system, weapons,
  HUD-content, or game state. Toolbox + demo scene ONLY.
- Do NOT put draw_latex_3d / any TexCache texture inside a display
  list.
- Do NOT invent colors; pull world colors from palette.
- Do NOT use modern shader pipeline.
- Ambiguity -> most literal reading + a "trap discovered" note.

TEST PLAN (how Nir verifies)
1. Confirm with Nir that palette.py exposes the world constants
   (ask him to paste palette.py's constants block if needed).
2. Nir runs render_demo.py on Windows 11 and sends SCREENSHOTS:
   - the grey translucent room with bright wireframe edges;
   - colored breadcrumb point(s) glowing THROUGH a wall;
   - the mathtext billboard facing the camera (and still facing it
     after he moves/rotates the demo camera);
   - the 2D HUD panel + mathtext label;
   - two shots at LOW vs HIGH wall_transparency showing the blend.
3. You iterate with DeepSeek until the screenshots look right:
   greyscale world, chroma only where placed, text crisp, billboard
   correctly camera-facing, no z-fighting on edges (use a slight
   polygon offset or draw edges after fill — your call, document).

SUCCESS CRITERIA
- render.py provides the full toolbox above (final signatures
  documented).
- render_demo.py opens, runs at ~60 FPS, and visually proves every
  verb per the screenshots.
- Walls show the two-pass recipe; transparency control blends
  wireframe<->solid.
- A mathtext billboard faces the camera from any angle.
- No third-party deps beyond pygame/PyOpenGL/numpy/matplotlib.
- palette is the only source of world colors.

WHEN DONE — COMPLETION REPORT (one page):
  COMPLETION REPORT — module render — <date>
  FILES CREATED: render.py, render_demo.py
  PUBLIC INTERFACES (verbatim FINAL signatures of every verb,
     plus TexCache methods and its eviction policy):
  KEY DECISIONS: edge z-fighting fix; billboard math; mathtext->
     texture path (backend, transparency); display-list usage (and
     the explicit note that latex is kept OUT of lists); how
     wall_transparency maps to alpha.
  DEVIATIONS FROM BRIEF: none / list.
  TRAPS DISCOVERED: anything later modules MUST know (camera
     conventions, coordinate handedness, units, texture-id
     recycling behavior, etc.).
  OLD-CODE REUSE: exactly what was mined from Fable's code.
  DEEPSEEK TODOS LEFT OPEN: list (window plumbing, tuning).
Nir carries this back to the parent; DeepSeek commits it to
/PARENT_ESTATE/reports/.
===========================================================
END CHILD BRIEF #3
===========================================================