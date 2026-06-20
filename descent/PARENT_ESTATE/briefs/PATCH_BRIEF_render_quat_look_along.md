PATCH BRIEF — render.py — add quat_look_along helper
Project: DESCENT QED engine. You maintain ONE module: render.

WHO GETS THIS:
- If you ARE the render chat: proceed (you have the file).
- If FRESH: STOP. First ask Nir: "Please paste the COMPLETE current
  contents of render.py, verbatim." Patch only the real file.

PRIME LAW: render is mathematics-blind (knows no game meaning) but it
DOES own all camera/quaternion math — Ship's q, ship_right/up/forward(q),
apply_view(). This helper belongs here because the orientation
CONVENTION lives here and must not be duplicated elsewhere.

WHY: hub_builder.spawn_pose() returns a look direction; app/Ship needs
to turn a direction into an orientation in render's EXACT convention
(forward = -Z, yaw about +Y, pitch about +X) without re-deriving it.

ADD (one function, matching the convention render's q already uses):
  def quat_look_along(direction, up=(0.0, 1.0, 0.0)):
      # Return a unit quaternion orienting the ship so its FORWARD
      # (-Z in render's convention) points along `direction`, with
      # roll minimized using `up`. Must match the SAME quaternion
      # convention as ship.q / ship_right/up/forward(q) / apply_view()
      # already in this file. Verify against those and say so.
      # Handle direction parallel to up gracefully (no NaN).
      ...
  Use the quaternion representation already used by Ship in this file
  (same component order, same handedness). If render builds the view
  from q via a known formula, INVERT that consistently so that
  ship_forward(quat_look_along(d)) == normalize(d).

VERIFY (state in report): ship_forward(quat_look_along((0,0,-1))) is
(0,0,-1); a few other directions point correctly; no NaN when
direction == up.

MUST NOT: change Ship, apply_view, fog, walls, billboards, or any
existing function. Only ADD quat_look_along. Touch no other module.

COMPLETION REPORT (short):
  COMPLETION REPORT — render patch (quat_look_along) — <date>
  FILE PATCHED: render.py
  ADDED: quat_look_along(direction, up=(0,1,0)) -> quat
  CONVENTION CONFIRMED: matches ship.q / ship_forward(q) (forward=-Z);
     ship_forward(quat_look_along(d)) == normalize(d) verified.
  EDGE: direction parallel to up handled (no NaN).
  DEVIATIONS: none / list.
DeepSeek commits report to /PARENT_ESTATE/reports/.