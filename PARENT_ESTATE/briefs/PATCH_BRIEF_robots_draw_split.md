PATCH BRIEF — robots.py — split draw into opaque/emissive + holo floor
Project: DESCENT QED engine. You maintain ONE module: robots.

WHO GETS THIS:
- If you ARE the chat that built robots.py: proceed (you have the file).
- If FRESH: STOP. First ask Nir:
  "Please paste the COMPLETE current contents of robots.py, verbatim."
  Patch only the real file. Do not reconstruct from this brief.

ALREADY DONE — DO NOT RE-ADD: robot.position (public property) and
robot.base_pos already exist and are correct. Leave them untouched.

THE PRIME LAW: engine is mathematics-blind; robot's only meaning-color
is its eye via palette. This patch changes no behavior or appearance.

WHY (engine-wide invariant the parent just locked):
Canonical frame order is:
  opaque -> render.flush_walls(ship.pos) -> emissive -> billboards/labels
A robot's HULL is opaque (normal depth) and should draw in the OPAQUE
phase, BEFORE the wall flush. Its SCANNER + HOLOGRAM are additive,
depth-write-off, and must draw in the EMISSIVE phase, AFTER the flush —
otherwise the flushed translucent walls overpaint the hologram where it
floats in open air (observed bug). Currently draw() does both at once.

ADD (split the existing draw into two public methods):
  def draw_opaque(self, camera_right, camera_up, texcache):
      # the faceted hull + pods ONLY (opaque, normal depth test).
      # If defeated: draw nothing (or the existing fireball's opaque
      # part if any) — match current defeat behavior.

  def draw_emissive(self, camera_right, camera_up, texcache):
      # the Larson scanner glow + the always-on hologram billboard
      # (+ the fireball's additive flash/sparks if mid-defeat).
      # additive / depth-write-off, exactly as today.

KEEP a convenience wrapper so existing callers still work:
  def draw(self, camera_right, camera_up, texcache):
      self.draw_opaque(camera_right, camera_up, texcache)
      self.draw_emissive(camera_right, camera_up, texcache)
  (Behavior of draw() must look identical to today in a scene with no
   translucent walls; the split only MATTERS when an app interleaves
   the global frame order. Preserve all current visuals exactly.)

ALSO ADD — hologram scale floor (latent bug found by corridor_builder):
  The hologram is currently scaled by the robot's `size`, so a small
  robot loses its hologram. Add a module-level constant
    MIN_HOLO_SCALE = <pick a sane floor, e.g. 0.8>
  # TODO(DeepSeek): tune MIN_HOLO_SCALE after flight | ACCEPTANCE:
  #   a size=0.5 robot still shows a readable hologram.
  and clamp the effective hologram scale to at least MIN_HOLO_SCALE so
  shrinking the robot can never shrink the hologram below readable.

MUST NOT:
- Change hull/eye/hologram/explosion APPEARANCE or motion.
- Change update(), play_defeat(), is_defeated(), position, base_pos.
- Touch other modules.

TEST (Nir): in robots_demo.py, optionally call draw_opaque then
draw_emissive instead of draw() and confirm the scene looks identical;
and confirm a size=0.5 robot still shows a readable hologram.

COMPLETION REPORT (short):
  COMPLETION REPORT — robots patch (draw split + holo floor) — <date>
  FILE PATCHED: robots.py
  ADDED: draw_opaque(...), draw_emissive(...), draw(...) wrapper,
     MIN_HOLO_SCALE (value).
  CONFIRMED: identical appearance; position/base_pos/behavior unchanged.
  DEVIATIONS: none / list.
DeepSeek commits report to /PARENT_ESTATE/reports/.