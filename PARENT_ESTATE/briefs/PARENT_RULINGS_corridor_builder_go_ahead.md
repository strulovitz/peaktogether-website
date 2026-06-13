===========================================================
PARENT RULINGS + GO-AHEAD — corridor_builder
Project: DESCENT QED engine. This is for the child who wrote the
Parent Package and asked Decisions A–E. (If, and ONLY if, that chat is
lost: a fresh chat must FIRST ask Nir to paste back your own Parent
Package AND any corridor_builder.py draft you already wrote, verbatim,
before doing anything — do not rebuild from this brief alone.)
===========================================================

The parent has ruled on all five questions. Build corridor_builder.py
+ corridor_demo.py correctly the first time against these. DeepSeek
commits; Nir tests by SCREENSHOT.

DECISION A — Translucency sorting: APPROVED, lives in render. ✅
  render is gaining (in parallel, via its own patch):
    queue_wall(quad, fill_color, edge_color, fill_alpha)
    flush_walls(camera_pos)   # render stays stateless; cam passed in
  => In your CorridorGeometry.draw(), enqueue every rock-wall via
     render.queue_wall(...) instead of calling draw_wall directly.
     Do NOT sort walls yourself. The app's frame loop will call
     render.flush_walls(ship.pos) ONCE per frame, after opaque+robots,
     before billboards. For YOUR corridor_demo.py, you call
     render.flush_walls(ship.pos) yourself at that point in the loop.
  TRAP to respect: if walls are enqueued but flush_walls is never
     called, they vanish silently — so make sure your demo's loop
     flushes.

DECISION B — Gentle mine-shaft BENDS: LIVE NOW. Make it gorgeous. ✅
  Earlier the parent hesitated over a feared collision between bent
  corridors once many radiate from the hub. Nir DISPROVED that fear,
  and the parent fully accepts the proof. Record it as canon:
    All corridors radiate from the shared hub center along
    Fibonacci-sphere directions. For N<=12 the minimum angular
    separation between any two corridor directions is large
    (>= ~40 deg, and near the icosahedral ~63 deg for 12). Two
    corridors EACH bending up to ~20 deg, even aimed straight at
    each other, close the gap by at most 20+20 = 40 deg — still
    within the separation, so centerlines never meet. A sphere
    spreads directions in TWO angular dimensions (poles, equator,
    and between), giving MORE separation than a circle, not less.
  => Therefore: bends are purely YOUR aesthetic concern. There is NO
     collision constraint and NO "wander budget." hub_builder will
     care only about your entrance mouth (position + outward normal),
     never the far end.
  IMPLEMENT: a segmented centerline with gentle random ~15-25 deg
     yaw/pitch per segment. Port Fable's bend machinery — _frame(yaw,
     pitch) basis builder, the per-segment turn/pitch segment table,
     the ELBOW rule, and BACK_EXTEND/TURN_EXTEND seam-overlap that
     hides gaps at turns — and drive it with REAL turns so the one
     corridor curves like a true Descent mine shaft. Fog (render-owned,
     40->140 toward CLEAR_COLOR) will reveal it gradually and hide
     far seams — lean into that.
  (Keep the centerline as a list of segments — it already must be, for
   bends. This also makes inside() and entrance_pose() segment-based.)

DECISION C — Expose collision query: APPROVED. ✅
  CorridorGeometry exposes:
    inside(point, margin=0.0) -> bool   # Fable's per-segment slab
                                        # union; works straight OR bent
    and the raw segment-bounds list (e.g. self.seg_bounds) publicly.
  This gives the future game_state child fly-through + "reached hostage
  room" detection for free. State the exact return shapes in your report.

DECISION D — Robot position: APPROVED. ✅
  robots is gaining a public robot.position (bobbed world center) via
  its own patch. For YOUR demo NOW, use the already-public robot.base_pos
  (un-bobbed station anchor) so you never touch a private method. (When
  game_state later needs the live bobbed center it will use
  robot.position; you don't need it for placement.)

DECISION E — numpy: APPROVED. ✅
  You are a world-builder (render tier). Use numpy freely. Canon: the
  pure-data leaves (content_parser, palette) stay numpy-free; the
  render/world tier (render, robots, corridor_builder, hub_builder) may
  use it.

NOW BUILD per your original Child Brief #5, with these rulings applied.
Reminders of the frozen facts you gathered (use EXACTLY these):
  render.draw_wall(quad, fill_rgb, edge_rgb, fill_alpha)  [via queue_wall now]
  render.draw_billboard(tex, center, cam_right, cam_up, scale=1.0, alpha=1.0)
     tex = (tid,w,h) from TexCache.get_mathtext(latex, color, fontsize)
  render.draw_box_edges(lo, hi, color)        # axis-aligned
  render.draw_breadcrumb(pos, color, size=0.15)
  render.set_fog(start=40, end=140, color=CLEAR_COLOR)
  Camera (DEMO-ONLY): ship.pos, ship.q; render.ship_right/up/forward(q);
     ship.update(dt, pygame.key.get_pressed()); ship.apply_view()
  palette: Palette(ledger).tint/text_color_on/eye/blend_rgb; world
     constants CLEAR_COLOR, WORLD_WALL_FILL, WORLD_EDGE, HOSTAGE_BLUE,
     HAZARD_YELLOW, HAZARD_BLACK, BACKDROP_BASE_ALPHA live ONLY in palette.
  robots: Robot(robot_data, palette, station_pose, paint=None, size=1.0);
     station_pose = (x,y,z) OR ((x,y,z), base_yaw_radians);
     update(dt, ship_position); draw(camera_right, camera_up, texcache);
     play_defeat(); is_defeated(); robot.base_pos public.
  Fixture corridors/01_dummy.txt: 2 robots (Alpha eye=alpha=RED,
     Beta eye=delta=ORANGE); ledger primaries alpha=red, beta=yellow,
     gamma=blue; corridor DOMINANT color = first primary = RED.
  Plaque placeholder text source: RobotData.briefing_hint.
  NEVER place a TexCache.get_mathtext id in a display list (recycling
     trap). Static tube geometry MAY be display-listed; keep labels/
     holograms/mathtext OUT of lists.

DELIVER: corridor_builder.py + corridor_demo.py, screenshots to Nir,
iterate with DeepSeek on tuning (TUBE_RADIUS, STATION_SPACING, segment
count/turn angles, chevron stripes, plaque size/fade) until it reads as
a real bent Descent shaft: octagonal grey tube with dominant-RED corner
glow, chevron mouth + title label, two non-humanoid robots (red eye /
orange eye) blocking the way, a calm plaque appearing where one is
defeated (museum effect on the way back), and a blue-hostage cavern at
the far end. Greyscale world; chroma only where it means something.

WHEN DONE — write the Completion Report exactly as your Child Brief #5
specified (FILES, final signatures incl. entrance_pose() return shape +
inside()/seg_bounds shapes + hostage_positions(), KEY DECISIONS,
DEVIATIONS, TRAPS for hub_builder/game_state, OLD-CODE REUSE, DEEPSEEK
TODOS). Nir carries it to the parent; DeepSeek commits to
/PARENT_ESTATE/reports/.
===========================================================