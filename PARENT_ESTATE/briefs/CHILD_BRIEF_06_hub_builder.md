============================================================
CHILD BRIEF #6 — hub_builder.py + hub_demo.py
Project: DESCENT QED engine. You are the maintainer of ONE NEW module:
hub_builder. You build the central ATRIUM and attach N corridors to it.
============================================================

WHO YOU ARE / FRESH-CHAT GATE:
You are a fresh chat building a brand-new module. You depend on REAL,
ALREADY-BUILT modules (render, palette, robots, corridor_builder). You
must NOT guess their APIs. Your FIRST actions, before writing any hub
code, are to ask Nir:
  "Please paste the COMPLETE current contents of, verbatim:
     1. corridor_builder.py   (I attach to its entrance_pose)
     2. render.py             (I queue walls + draw via it)
     3. palette.py            (world color constants live here)
     4. robots.py             (only if I end up touching robots — I
                               likely DON'T; ask only if needed)
   And the fixture folder layout (corridors/*.txt) + content_parser's
   public load function, so my demo can build real corridors."
Do not reconstruct any of these from memory or from this brief's
reminders. The reminders below are to ORIENT you; the pasted files are
LAW. If a reminder disagrees with the pasted file, the FILE wins —
say so in your report.

WHO ELSE IS INVOLVED:
- DeepSeek (Nir's builder, agentic in OpenCode): commits your verbatim
  code to GitHub, does mechanical tuning. Reliable, less clever than you.
- Nir: courier + tester. NOT technical, very smart. Runs code, sends
  screenshots/output. Speaks for the parent (another Claude) who designs
  architecture. You have NO memory of other chats; the parent does.
- You write a Completion Report at the end (template at bottom). Nir
  carries it up; DeepSeek commits it to /PARENT_ESTATE/reports/.

THE PRIME LAW (never violate):
The engine is MATHEMATICS-BLIND. hub_builder knows nothing about what
the math MEANS. It arranges geometry in space and draws grey walls.
Color meaning comes only from palette (via a ledger). You place doors
and walls; you do not interpret corridor content.

============================================================
WHAT hub_builder IS (the concept)
============================================================
The DESCENT QED level is a central hollow CHAMBER (the "atrium" / hub)
with N doorways cut into its shell. Out of each doorway radiates ONE
corridor (a CorridorGeometry from corridor_builder). The player spawns
inside the atrium, picks a doorway, flies down that corridor to its
hostage cavern, and returns. The atrium is the lobby of the whole level.

Visually (greyscale world, chroma only where meaning lives):
- A roughly spherical/faceted hollow grey room (translucent rock walls,
  same WORLD_WALL_FILL / WORLD_EDGE family as corridors, fog-revealed).
- N doorway openings in the shell, each rimmed with a chevron/frame so
  the player can see "a corridor begins here."
- Each doorway's frame may carry that corridor's title label (billboard)
  so the player can read where each tunnel leads — like a hub of a
  museum with labeled wings.
- The atrium interior is OPEN space you fly around in.

============================================================
THE FIBONACCI SPHERE — door directions (the core math)
============================================================
Given N corridors, compute N unit direction vectors evenly spread on a
sphere — these are the OUTWARD directions of the N doorways from the
atrium center. Use the standard Fibonacci-sphere spread:

  golden = pi * (3 - sqrt(5))                  # ~2.39996 rad
  for i in range(N):
      y   = 1 - 2*(i + 0.5)/N                   # y from ~+1 to ~-1
      r   = sqrt(max(0.0, 1 - y*y))             # radius at that y
      th  = golden * i
      dir_i = (cos(th)*r, y, sin(th)*r)         # unit vector
  # these N unit vectors are the door OUTWARD normals.

This spreads doors over the whole sphere (poles + equator + between),
NOT just a ring. Use numpy (you are render-tier; numpy is allowed).

COLLISION SAFETY — CANON, settled by Nir's proof (do NOT re-litigate,
do NOT add any anti-collision constraint):
  All corridors radiate from the shared atrium center along these
  Fibonacci directions. For N<=12 the minimum angular separation between
  any two directions is large (>= ~40 deg; near the icosahedral ~63 deg
  at N=12). A corridor may bend up to ~20 deg off its spoke; two
  corridors each bending 20 deg, even aimed straight at each other,
  close the gap by at most 40 deg — still within separation. The sphere
  spreads directions in TWO angular dimensions, so they are MORE
  separated than a ring, not less. => Bent corridors NEVER collide for
  N<=12. You impose NO wander budget, NO straightening, NO spacing
  hack. You only place mouths; corridor_builder owns the bends freely.
  (If someone ever asks for N>12, that's a FUTURE question — flag it,
   don't solve it now. Design for N in roughly 1..12.)

============================================================
ATTACHMENT CONTRACT — how a corridor connects to a doorway
============================================================
corridor_builder gives you (VERIFY exact shapes from the pasted file —
these are the locked signatures the parent recorded):

  build_corridor(corridor_data, origin=(0,0,0), direction=(0,0,-1))
      -> CorridorGeometry
  CorridorGeometry.entrance_pose() -> ((x,y,z), (nx,ny,nz))
      # mouth CENTER + OUTWARD normal (the normal points back toward the
      # hub, i.e. INTO the atrium / opposite the direction of travel).
      # The far end of the corridor is ARBITRARY (it bends) — NEVER
      # assume it is straight or where it ends up.

THE KEY DESIGN CHOICE (state your decision clearly in the report):
You have two clean ways to attach. Pick ONE, justify it:

  OPTION 1 — BUILD AT ORIGIN: For each door i, call
     build_corridor(data_i, origin=door_center_i, direction=dir_i)
     so the corridor is born already positioned/oriented at the doorway,
     pointing outward along dir_i. This is cleanest IF build_corridor's
     origin/direction params actually place+aim the whole corridor.
     VERIFY from the pasted corridor_builder that origin/direction do
     what you need (they appear to: origin=(0,0,0), direction=(0,0,-1)
     defaults). If yes, prefer this — no post-hoc transforms.

  OPTION 2 — BUILD THEN TRANSFORM: build each corridor at default
     origin, then compute a rigid transform (rotation + translation)
     that maps its entrance_pose() onto the doorway pose (door center +
     dir_i), and apply it to the corridor's geometry. Only do this if
     corridor_builder does NOT support being born at a pose. This is
     more fragile (you must transform seg_bounds, robots, hostage
     positions, labels consistently). AVOID if Option 1 works.

Almost certainly OPTION 1 is correct — confirm against the file and say
so. The doorway POSE for corridor i is:
     door_center_i = atrium_center + dir_i * ATRIUM_RADIUS
     door_outward_i = dir_i
and you build/aim the corridor to emerge there pointing along dir_i.

After attaching, the atrium must CUT/own an opening at each door_center
so the player can actually fly from atrium into corridor (don't draw a
solid wall sealing the doorway — leave/frame an opening of ~corridor
mouth radius there).

============================================================
WHAT TO BUILD — public interface (lock these for app/game_state)
============================================================
class HubGeometry  (mirror corridor_builder's style/three-phase draw):

  build_hub(level_data, atrium_center=(0,0,0)) -> HubGeometry
     # level_data tells you the list of corridors to build (their
     # corridor_data + titles). VERIFY how content_parser exposes a
     # "level" or a list of corridor files; if there is no level
     # container yet, accept a simple list of corridor_data objects and
     # SAY SO in the report (the parent may add a level parser later).

  # geometry / queries
  corridors            -> list[CorridorGeometry]   # the attached corridors
  door_poses()         -> list[((x,y,z),(nx,ny,nz))] # center+outward per door
  inside(point, margin=0.0) -> bool   # True if point is in the atrium
                                      # interior OR inside ANY corridor
                                      # (delegate to each corridor.inside)
  spawn_pose()         -> ((x,y,z),(yaw,pitch)or quat)  # where the ship
                                      # starts: atrium center, facing the
                                      # first/nearest doorway. State the
                                      # exact orientation form you return.

  # per-frame — FOLLOW THE CANONICAL FRAME ORDER (locked engine invariant)
  update(dt, ship_position) -> None
     # update all corridors (their robots bob/track) + any hub animation
  draw_world(cr, cu, texcache) -> None
     # QUEUE the atrium's translucent rock walls (via render.queue_wall)
     # + door frames/chevrons, AND call each corridor's draw_world(...)
     # so all walls land in the SINGLE shared queue. Do NOT flush here.
  draw_robots(cr, cu, texcache) -> None
     # call each corridor's draw_robots(...). (Hub has no robots of its
     # own unless you add atrium guardians — don't, unless trivial.)
  draw_labels(cr, cu, texcache) -> None
     # door title labels + call each corridor's draw_labels(...)

THE CANONICAL FRAME ORDER (locked — your demo loop MUST obey it):
  opaque (robot hulls via draw_robots' opaque part) ->
  render.flush_walls(ship.pos) ->
  emissive (scanners/holograms) ->
  billboards/labels
  NOTE: corridor_builder currently exposes draw_robots as a single
  phase drawn AFTER flush (works because hull depth still sorts). The
  robots module now ALSO offers draw_opaque()/draw_emissive() split.
  For THIS demo, you may use corridor_builder's existing draw_robots
  (after flush) — it works. If you want textbook order, ask the parent
  whether corridor_builder should expose the split too; otherwise keep
  it simple: draw_world -> flush_walls -> draw_robots -> draw_labels.
  TRAP (canon): if walls are queued but flush_walls(ship.pos) is never
  called once per frame, ALL walls vanish silently. Your demo loop MUST
  call it exactly once, after draw_world, before robots/labels.

============================================================
FROZEN FACTS — use EXACTLY these (verify against pasted files)
============================================================
render (queue + draw; render is STATELESS, mathematics-blind):
  render.queue_wall(quad, fill_color, edge_color, fill_alpha)  # enqueue
  render.flush_walls(camera_pos)   # sort far->near & draw, once/frame
  render.draw_wall(quad, fill_rgb, edge_rgb, fill_alpha)       # immediate
  render.draw_billboard(tex, center, cam_right, cam_up, scale=1.0, alpha=1.0)
     tex = (tid,w,h) from TexCache.get_mathtext(latex, color, fontsize)
  render.draw_box_edges(lo, hi, color)        # axis-aligned, for debug
  render.draw_breadcrumb(pos, color, size=0.15)
  render.set_fog(start=40, end=140, color=CLEAR_COLOR)
  Camera (DEMO ONLY): ship.pos, ship.q; render.ship_right/up/forward(q);
     ship.update(dt, pygame.key.get_pressed()); ship.apply_view()
  NEVER put a get_mathtext texture id into a display list (recycling
     trap). Static atrium-shell geometry MAY be display-listed; keep
     labels/holograms/mathtext OUT of lists.

palette (ALL world color constants live here — import, do not invent):
  CLEAR_COLOR, WORLD_WALL_FILL, WORLD_EDGE, HOSTAGE_BLUE,
  HAZARD_YELLOW, HAZARD_BLACK, BACKDROP_BASE_ALPHA
  Palette(ledger).tint / text_color_on / eye / blend_rgb
  The atrium walls use the SAME grey rock family as corridors
  (WORLD_WALL_FILL fill, WORLD_EDGE edges, translucent). Door frame
  chevrons may echo each corridor's dominant ledger color subtly if you
  want hue-family hinting — OPTIONAL, ask parent before adding chroma.

corridor_builder (verify shapes; locked by parent):
  build_corridor(corridor_data, origin, direction) -> CorridorGeometry
  .entrance_pose() -> ((x,y,z),(nx,ny,nz))   # mouth center + OUTWARD normal
  .inside(point, margin=0.0) -> bool
  .seg_bounds -> list[dict{start,end,right,up,radius}]
  .hostage_positions() -> list[(x,y,z)]
  .stations() -> list[((x,y,z),yaw)]
  .get_robots() -> list[Robot]
  .update(dt, ship_position); .draw_world(cr,cu,tc); .draw_robots(cr,cu,tc);
  .draw_labels(cr,cu,tc)
  N_SIDES=4 box tunnels, gentle bends live, cavern flares blue at far end.

============================================================
TUNABLES (constants at top of file; DeepSeek tunes via screenshots)
============================================================
  ATRIUM_RADIUS      = ?   # size of the central chamber (must comfortably
                           # fit N door openings of ~corridor mouth radius)
  ATRIUM_FACETS      = ?   # how faceted the spherical shell is (icosphere-
                           # ish or lat/long); keep it readable & fog-friendly
  DOOR_FRAME_DEPTH   = ?   # chevron rim thickness around each opening
  Mark each with: # TODO(DeepSeek): tune ... | ACCEPTANCE: <visible test>

============================================================
hub_demo.py — standalone flythrough (screenshot-verified)
============================================================
- Load REAL corridor fixtures (ask Nir for the corridors/*.txt list +
  content_parser load fn). Build a HubGeometry with N of them
  (try N=1, then N=3, then N=7, then N=12 — confirm doors spread over
  the sphere and corridors don't intersect, per the proof).
- Spawn ship at spawn_pose(); WASD/arrows fly (ship.update).
- Frame loop EXACTLY: clear -> set_fog -> hub.update(dt, ship.pos) ->
  hub.draw_world(cr,cu,tc) -> render.flush_walls(ship.pos) ->
  hub.draw_robots(cr,cu,tc) -> hub.draw_labels(cr,cu,tc) -> flip.
- Nir flies from the atrium center OUT through a doorway, down the bent
  corridor, to the blue cavern, and back. Confirms: doors spread on the
  sphere; each corridor reads correctly; no corridor punches into
  another; fog reveals gracefully; labels readable at doorways.

============================================================
WHAT YOU MUST NOT DO
============================================================
- Do NOT interpret math/color meaning (mathematics-blind).
- Do NOT modify render, palette, robots, or corridor_builder. If you
  NEED a change in any of them, STOP and report it as a request to the
  parent (like corridor_builder did with the draw-order finding) — do
  not reach into or fork another module.
- Do NOT add any anti-collision constraint (the proof forbids needing
  one for N<=12).
- Do NOT seal the doorways with solid wall (leave the opening).
- Do NOT put mathtext ids in display lists.
- Do NOT add chroma beyond grey world without asking the parent
  (hue-family door hints are OPTIONAL and parent-gated).

============================================================
COMPLETION REPORT (write this at the end)
============================================================
  COMPLETION REPORT — hub_builder — <date>
  FILES: hub_builder.py, hub_demo.py (screenshot-verified? Y/N)
  FINAL SIGNATURES (locked for app/game_state): build_hub(...),
     HubGeometry.{corridors, door_poses(), inside(), spawn_pose(),
     update(), draw_world(), draw_robots(), draw_labels()} with EXACT
     return shapes (esp. spawn_pose orientation form, door_poses shape).
  ATTACHMENT METHOD CHOSEN: Option 1 (build-at-pose) or Option 2
     (transform), with justification + what you verified in
     corridor_builder to decide.
  FIBONACCI: confirmed door spread for N=1,3,7,12 (screenshots);
     confirmed no corridor-corridor intersection (the proof held).
  FRAME ORDER: confirmed demo obeys draw_world->flush_walls->robots->
     labels; flush called exactly once.
  LEVEL INPUT: how the list of corridors is supplied (real level
     parser? or a plain list of corridor_data? — say what you needed).
  KEY DECISIONS / DEVIATIONS / TRAPS (for app + game_state).
  REQUESTS TO PARENT: any change you needed in another module (do NOT
     make it yourself — request it).
  OLD-CODE REUSE: anything adapted from Fable.
  DEEPSEEK TODOS: tunables + acceptance tests.
Nir carries this to the parent; DeepSeek commits to
/PARENT_ESTATE/reports/.
===========================================================