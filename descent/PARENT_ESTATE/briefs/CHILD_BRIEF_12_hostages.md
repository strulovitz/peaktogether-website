================================================================================
DESCENT QED — CHILD BRIEF #12: HOSTAGES (TWO real 3D figures — the couple)
You build ONE concern: a new module `hostages.py` containing a `Hostage` class
that constructs a REAL 3D HUMANOID FIGURE from GL geometry — built and animated
the SAME WAY the 1st parent built the Robot class in `robots.py`. TWO hostages
per corridor (a couple), standing together at the end. NOT a sprite. NOT a
billboard. NOT a flat image. NOT a blob. A real 3D object with a body.
================================================================================

THE STANDARD YOU ARE HELD TO:
`robots.py` (the 1st parent's work) builds a Robot as a REAL 3D object out of GL
primitives — a hull, a scanner, etc., assembled in code, lit, animated. THAT is
the bar. You build the hostages to the SAME standard: real 3D humanoid figures
assembled from GL primitives in code. If a robot deserves a real 3D body, the
TWO PEOPLE WE CROSSED THE WHOLE CORRIDOR TO RESCUE deserve real 3D bodies more.
The hostages are the entire heart of this game (Peak Together — a couple). Do a
good job worthy of the 1st parent's Robot class.

------------------------------------------------------------------------------
FRESH-CHAT GATE — DO THIS FIRST, BEFORE WRITING ANY CODE
------------------------------------------------------------------------------
You are a fresh child Claude with no memory of other chats. Your FIRST action is
to ask Nir (the human courier, non-technical) to paste the COMPLETE, VERBATIM,
CURRENT contents of these files. PASTED FILES ARE LAW. If anything here disagrees
with a pasted file, THE FILE WINS — and you flag it to the parent.

  1. robots.py        ⭐ MOST IMPORTANT — study HOW the Robot class builds a real
                       3D object: how it assembles primitives, stores geometry,
                       takes a world position + orientation, lights itself,
                       animates (bob/spin), and exposes a draw(cr,cu,texcache)
                       method. YOUR Hostage class MIRRORS THIS PATTERN EXACTLY.
  2. render.py        (GL primitive helpers, quaternion/camera helpers, lighting,
                       fog, draw conventions, ship_right/up, color usage)
  3. corridor_builder.py  (hostage anchor computation in _build_cavern_anchors;
                       hostage_positions(); _far_center; draw_robots() slot;
                       how robots are instantiated & stored per corridor)
  4. hub_builder.py   (how hub iterates corridors and calls draw_robots /
                       draw_labels; hub.corridors list)
  5. palette.py       (how to request an OPAQUE color id; existing keys;
                       whether a hostage color exists)
  6. app.py           (the canonical frame loop — to see EXACTLY where draw_robots
                       is called; you ADD NOTHING to app, you give the parent the
                       exact 1 line to add)

Do NOT guess any signature. Mirror the REAL Robot class you are shown.

------------------------------------------------------------------------------
WHO ELSE IS INVOLVED
------------------------------------------------------------------------------
- NIR: the human. Smart but NOT technical. The courier + tester. He runs your
  demo and reports what he sees. He has asked for this MANY times — get it right.
- DEEPSEEK (V4 Pro): the builder who commits your code. DO NOT defer design to
  DeepSeek. DeepSeek's earlier "just use primitives / do nothing fancy" steer was
  WRONG and rejected by Nir. You DESIGN the real 3D figures. DeepSeek only does
  mechanical tuning (scale, bob speed) AFTER.
- PARENT/ARCHITECT (separate Claude): owns architecture. Your Completion Report
  is carried back by Nir.

------------------------------------------------------------------------------
THE PRIME LAW — MATHEMATICS-BLINDNESS
------------------------------------------------------------------------------
The engine NEVER interprets what mathematics MEANS, never assigns color MEANING.
Hostages carry NO mathematics and NO meaning — pure prize geometry. If you need a
color, request an OPAQUE color id from palette; never map color→meaning.

------------------------------------------------------------------------------
WHAT TO BUILD — `hostages.py`
------------------------------------------------------------------------------
A `Hostage` class that mirrors the Robot class structure from robots.py. Proposed
shape (adjust ONLY to match the REAL Robot pattern you are shown):

  class Hostage:
      def __init__(self, world_pos, facing, color_id, variant):
          # build a REAL 3D HUMANOID from GL primitives, assembled in code:
          #   - head (sphere/cube), torso, two arms, two legs — a recognizable
          #     standing PERSON, like the blue figures in Descent 1995.
          #   - stored as geometry the same way Robot stores its hull, so draw()
          #     just transforms + emits it.
          #   - `variant` lets the TWO hostages differ slightly (the couple is
          #     two distinct people, not clones — e.g. slight build/height/pose
          #     difference). Keep it tasteful and simple.
          ...
      def update(self, dt):
          # gentle idle life — slow bob / subtle sway, MIRROR how Robot animates.
          # NO combat, NO death, NO timer. They just wait to be rescued.
      def draw(self, cr, cu, texcache):
          # transform to world_pos + facing, emit the 3D figure, lit/emissive so
          # they GLOW and POP against the blue cavern, like the Descent sprites
          # glowed — but as REAL 3D geometry.

  # module-level helper the corridor/hub will use:
  def build_hostages(corridor_geom):
      """Return exactly TWO Hostage objects for this corridor, positioned as a
      couple standing TOGETHER at the corridor's end. Use the corridor's existing
      cavern anchors / far-center for placement (see CONSTRAINTS below)."""

  def near_hostages(hostage_list, ship_pos, radius):
      """True if ship_pos is within `radius` of the couple. Pure geometry, no
      side effects. The ONLY query Brief #13 (GAME STATE) will consume."""

CONSTRAINTS ON COUNT & PLACEMENT (CRITICAL — read twice):
  - EXACTLY TWO hostages. TWO. A couple. Not three. Not one. TWO.
  - The existing `hostage_positions()` returns THREE floor anchors at offsets
    (-3.5, 0.0, 3.5). DO NOT use three. Place the TWO hostages standing side by
    side near the cavern floor/center — e.g. at two of the anchors, or compute
    two positions around `_far_center` (a small left/right offset so they stand
    TOGETHER as a couple). They should be clearly TWO PEOPLE STANDING TOGETHER,
    facing back up the corridor toward the arriving ship.
  - If you think the corridor should store its own two Hostage objects (so each
    corridor owns its couple, like it owns its robots), that's the right design —
    but DO NOT edit corridor_builder yourself. Instead, REQUEST in your report
    that the parent add `self._hostages = build_hostages(self)` in
    CorridorGeometry and a `draw_hostages(cr,cu,tc)` call in the draw_robots slot.
    Build hostages.py so that wiring is trivial.

VISUAL TARGET (from the real Descent 1995 reference Nir provided):
  - Two glowing humanoid figures standing in the cavern, clearly visible,
    clearly PEOPLE, clearly the prize. Warm/bright and emissive so they POP
    against the blue cavern walls. Friendly and inviting — NOT scary, NOT robotic.
  - Built as REAL 3D geometry (the Descent original was a sprite; Nir explicitly
    wants 3D, like the robots). Recognizable body: head, torso, arms, legs.

------------------------------------------------------------------------------
ENGINE CANON — OBEY VERBATIM
------------------------------------------------------------------------------
Canonical frame order (already in app.py — you ADD NOTHING to app):
  events → ship.update → clear → set_fog → apply_view → hub.update →
  hub.draw_world (QUEUE walls) → render.flush_walls (EXACTLY ONCE) →
  hub.draw_robots → hub.draw_labels → flip

THE CARDINAL FLUSH TRAP: walls are only QUEUED by draw_world. flush_walls runs
EXACTLY ONCE, AFTER draw_world, BEFORE robots. If you add/move/remove/duplicate
flush_walls, ALL WALLS VANISH SILENTLY (black screen, no error). DO NOT TOUCH
flush_walls. Hostages are SOLID 3D geometry like robots, so they draw in the
draw_robots slot (AFTER flush) — exactly where robots draw. Mirror the robot
draw path; never call flush yourself.

------------------------------------------------------------------------------
WHAT YOU MUST NOT DO
------------------------------------------------------------------------------
- Do NOT make sprites, billboards, flat quads, or blobs. REAL 3D figures only.
- Do NOT make three. Make TWO.
- Do NOT defer the design to DeepSeek or "keep it minimal to avoid burden." BUILD
  the figures properly, to the Robot-class standard.
- Do NOT add/move/remove/duplicate flush_walls. Do NOT reorder the loop.
- Do NOT build win/lose logic, rescue logic, or game state (Brief #13). THERE IS
  NO LOSING IN THIS GAME — never add damage, death, timer, or fail state.
- Do NOT change the corridor .txt format / content_parser / CorridorData.
  Placement comes from existing cavern geometry. Zero new fixture fields.
- Do NOT interpret math/technique/color MEANING. Request opaque color ids only.
- Do NOT edit app.py or corridor_builder.py yourself. REQUEST the exact wiring
  lines in your report; build hostages.py so wiring is one trivial line each.
- Do NOT add PNG assets. The figures are BUILT in code from GL primitives, like
  the Robot hull.

------------------------------------------------------------------------------
DEMO — `hostages_demo.py` (Nir RUNS this)
------------------------------------------------------------------------------
Reuse the real init/fog/ship/hub setup VERBATIM from app.py. It must:
  - Load a real level (levels/intro.txt or levels/maxwell.txt) → build_hub.
  - Spawn ship at hub.spawn_pose() aimed at a door.
  - Run the canonical loop, flush_walls EXACTLY ONCE in slot 8.
  - For each corridor, build_hostages(corridor) and draw them + update them in
    the draw_robots slot (since corridor_builder isn't wired yet, the DEMO does
    this directly so Nir can SEE them now).
  - Print a one-line console status via near_hostages when the ship comes close.

ACCEPTANCE (what Nir must SEE):
  1. Fly to the blue cavern → TWO glowing 3D PEOPLE standing together, facing the
     ship. Recognizable bodies (head/torso/arms/legs). They POP against the blue.
  2. Exactly TWO, in every corridor's cavern. Never three.
  3. They have gentle idle life (subtle bob/sway), like the robots are alive.
  4. No black screen / vanished walls (flush trap respected).
  5. Console prints a NEAR line when the ship gets close; stops when flying away.

------------------------------------------------------------------------------
COMPLETION REPORT TEMPLATE (Nir carries to parent)
------------------------------------------------------------------------------
- FILES ADDED/CHANGED: (hostages.py, hostages_demo.py; app.py & corridor_builder
  UNCHANGED)
- RUN-VERIFIED? (Y/N)
- FINAL LOCKED SIGNATURES: (Hostage.__init__/update/draw, build_hostages,
  near_hostages — exact as built)
- HOW I MIRRORED THE ROBOT CLASS (verbatim): (quote the Robot pattern you copied:
  geometry assembly, draw, animate, lighting)
- WHAT I CONSUMED + HOW: (hostage_positions/_far_center, render primitive helpers,
  palette color key, quat/camera helpers — quote real signatures)
- THE EXACT WIRING LINES THE PARENT MUST ADD (and WHERE): (e.g. in CorridorGeometry
  __init__: self._hostages = build_hostages(self); and in draw_robots slot:
  for h in self._hostages: h.update(dt); h.draw(cr,cu,tc))
- DEVIATIONS / REQUESTS TO PARENT: (e.g. palette had no hostage color — I REQUEST
  key 'hostage_glow'; placement decision I made; etc.)
- DEEPSEEK TODOs (mechanical tuning only): (figure scale, bob speed/amplitude,
  the two world positions / spacing, rescue radius, glow color/intensity, variant
  difference between the two people — list constants + current values)
================================================================================
END OF BRIEF #12
================================================================================
