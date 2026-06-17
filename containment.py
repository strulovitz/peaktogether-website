"""
containment.py -- DESCENT QED, CHILD MODULE #C1: ship collision / containment.

PURE GEOMETRY + PHYSICS. MATHEMATICS-BLIND: this module reads no equations,
picks no colors, knows no "meaning." It asks only two questions:
    "is the ship center inside the rock-bounded world?"  (hub.inside)
    "is the ship center inside an undefeated robot's hull?"
and, when the answer is "no longer legal," it HARD-STOPS the ship at the
solid surface and lets it SLIDE along it (tangential motion preserved,
into-surface motion killed). Like a real rock mine: never a spring, never a
cushion, never a bounce.

NO RENDERING. NO GLOBAL STATE. The single public entry point is a pure
function of (ship, hub, prev_pos):

    resolve(ship, hub, prev_pos) -> None      # mutates ship.pos / ship.vel

It is called by app.py EXACTLY between ship.update(dt, keys) and
ship.apply_view(), so the camera matrix is built from the corrected position.

--------------------------------------------------------------------------
WHY THESE NUMBERS (geometry-derived; DeepSeek may tune):

  SHIP_RADIUS = 0.6
     The corridor tube has TUBE_RADIUS = 6.0 (corridor_builder), and
     hub.inside() treats the tube as a swept cylinder of that radius. A
     containment margin eats into the flyable width: usable half-width
     becomes (6.0 - SHIP_RADIUS). 0.6 keeps ~5.4 of clear half-width
     (10.8-wide flyable tube) -- the wall feels solid without choking the
     6-DOF flying. The atrium (radius 34) is barely affected. 0.6 is also
     comfortably larger than the max single-frame step (MAX_SPEED 18 * 3
     boost * 1/60 ~= 0.9... see note) so it is a real skin, not a sliver.

  ROBOT_RADIUS source = robot.size * Robot._HULL_R
     robots.py defines Robot._HULL_R = 1.6 ("approx hull radius") and the
     hull is drawn with glScalef(size,...). The corridor seats robots at
     size = ROBOT_SIZE = 1.0, so the world-space hull radius is ~1.6. We
     read it straight off the live robot, so any future size change is
     honored automatically. No magic constant, no parent change needed.
--------------------------------------------------------------------------
"""

import numpy as np

# --- containment constants (geometry-derived; see module docstring) ---

SHIP_RADIUS = 1.5        # ship "skin" / eye standoff: how far the camera
                         # (which sits AT ship.pos) must stay off any solid
                         # surface. TUBE_RADIUS=6, so flyable half-width is
                         # 6-1.5 = 4.5 (9-wide tube) -- solid wall, the eye
                         # never reaches the rock, flight still roomy.
                         # (Was 0.6: too small -> camera peered through.)

NORMAL_EPS  = 0.35       # finite-difference probe step for the wall normal.
                         # Scaled up with SHIP_RADIUS so the +/-EPS samples
                         # straddle the (now thicker) clamp boundary cleanly.

ROBOT_RADIUS_PAD  = 0.6  # extra skin added around a robot's true hull reach
                         # so the ship cannot graze the snout/pods.
ROBOT_RADIUS_MIN  = 2.6  # floor on the blocking radius. With SHIP_RADIUS the
                         # plug is >= ROBOT_RADIUS_MIN + SHIP_RADIUS ~= 4.1
                         # against a tube of half-width 6 -> the robot truly
                         # blocks the corridor; no clean lane around it.

PLUG_RIM_GAP = 0.8       # How much smaller than the full tube the plug is,
                         # so the ship can SLIDE around the plug's rim against
                         # the wall instead of wedging dead. With TUBE_RADIUS=6
                         # and SHIP_RADIUS=1.5, plug radius (6-0.8)=5.2 leaves
                         # only a 0.8 sliver at the wall -- too thin for the
                         # 1.5-radius ship to squeeze through, so corridor is
                         # genuinely blocked, but ship can still graze-slide.


# ----------------------------------------------------------------------
# small vector helpers (local; no dependency on other modules' helpers)
# ----------------------------------------------------------------------
def _norm(v):
    return float(np.linalg.norm(v))


def _normalize(v):
    n = _norm(v)
    if n < 1e-12:
        return None
    return v / n


# ----------------------------------------------------------------------
# WALL NORMAL by finite differences of the boolean inside() test.
#
# hub.inside() is boolean-only, so we approximate the OUTWARD-from-rock
# (i.e. INTO-open-space) normal by sampling inside() around the blocked
# point. For each axis we test +EPS and -EPS: if stepping +X lands inside
# the world and -X does not, "more open space lies toward +X," so the
# normal gains a +X component. Summing over all axes yields a vector that
# points back toward open space. We normalize it.
#
# This is the crux of "slide, not stick." It is robust at the doorway seam
# because hub.inside() is the UNION (atrium sphere OR any corridor): the
# union is continuous through the doorway, so the sampled gradient does not
# flip wildly where the two surfaces overlap.
# ----------------------------------------------------------------------
def _wall_normal(hub, point, eps=NORMAL_EPS):
    p = np.asarray(point, dtype=float)
    n = np.zeros(3)
    for axis in range(3):
        d = np.zeros(3)
        d[axis] = eps
        plus  = hub.inside(p + d, margin=SHIP_RADIUS)
        minus = hub.inside(p - d, margin=SHIP_RADIUS)
        if plus and not minus:
            n[axis] += 1.0
        elif minus and not plus:
            n[axis] -= 1.0
        # both inside or both outside -> this axis gives no clear direction
    return _normalize(n)   # may be None if degenerate


# ----------------------------------------------------------------------
# WALL CONTAINMENT -- hard stop + slide.
# ----------------------------------------------------------------------
def _resolve_walls(ship, hub, prev_pos):
    print("INSIDE?", hub.inside(ship.pos, margin=SHIP_RADIUS),
          "pos", np.round(ship.pos, 2))
    if hub.inside(ship.pos, margin=SHIP_RADIUS):
        return  # legal: the whole attempted move stayed in the world

    # The move pushed (part of) the ship into rock. Find the slide normal.
    n = _wall_normal(hub, ship.pos)
    print("WALL NORMAL", None if n is None else np.round(n, 2),
          "into atrium?", float(np.dot(n, hub.center - ship.pos)) if n is not None else None)

    if n is None:
        # Degenerate finite-difference (e.g. a sharp corner). Fall back to
        # the direction from the blocked point back toward known-open space:
        # prev_pos was inside the world (it was legal last frame), so the
        # vector prev_pos - pos points back into open space. If prev_pos is
        # somehow coincident, use atrium center (always inside).
        n = _normalize(prev_pos - ship.pos)
        if n is None:
            n = _normalize(hub.center - ship.pos)
        if n is None:
            ship.pos = prev_pos.copy()
            ship.vel = np.zeros(3)
            return

    # Keep only the tangential part of the attempted delta (slide along the
    # surface); discard the component that drove into the rock.
    delta = ship.pos - prev_pos
    delta_slide = delta - n * float(np.dot(delta, n))
    ship.pos = prev_pos + delta_slide

    # Kill the inward velocity component so the ship does not keep grinding
    # into the wall next frame (vel is inertial in render.Ship -> it must be
    # corrected, or the slide will not feel solid).
    vdot = float(np.dot(ship.vel, n))
    if vdot < 0.0:
        ship.vel = ship.vel - n * vdot

    # Corner case: the slid position is STILL outside (e.g. sliding along one
    # wall pushed us through another). Stop dead rather than leak through.
    if not hub.inside(ship.pos, margin=SHIP_RADIUS):
        ship.pos = prev_pos.copy()
        # kill only the inward component again (prev_pos was legal)
        vdot = float(np.dot(ship.vel, n))
        if vdot < 0.0:
            ship.vel = ship.vel - n * vdot


# ----------------------------------------------------------------------
# ROBOT BLOCKING -- a PLUG across the corridor tube, not a ball at the hull.
#
# WHY A PLUG: the robot is seated LOW in the tube (corridor_builder seats it
# at center - up*radius*0.45). A sphere centered on the robot's visual hull
# leaves a clear gap between the top of that sphere and the tube ceiling --
# the ship simply flies OVER the robot (probe: nearest dist 9.36 >> solid_r
# 4.43, ship passed freely). The robot's PURPOSE is to block the corridor,
# so the blocking volume must sit on the TUBE AXIS at the robot's depth and
# SPAN the tube. We find the nearest point on the corridor centerline (from
# the corridor's public seg_bounds) to the robot, center the plug there, and
# size it to (segment tube radius - small gap). That leaves no over/under/
# around lane while preserving HARD-STOP + SLIDE (you slide on the plug face
# until you give up and kill the robot).
# ----------------------------------------------------------------------


def _hull_min_radius(robot):
    """Lower bound for the plug: the robot's true geometric reach (so the
    plug never sits INSIDE the visible hull). See SYMPTOM #2 notes: _HULL_R
    is a decoration constant; we measure actual hull vertices instead."""
    size = float(getattr(robot, "size", 1.0))
    verts = getattr(robot, "_hull_verts", None)
    if verts is not None and len(verts):
        reach = float(np.max(np.linalg.norm(np.asarray(verts, dtype=float),
                                            axis=1)))
    else:
        reach = float(getattr(type(robot), "_HULL_R", 1.6))
    return reach * size + ROBOT_RADIUS_PAD


def _nearest_centerline_plug(corridor, robot_pos):
    """Return (plug_center, plug_radius) on this corridor's centerline,
    nearest to robot_pos, using the corridor's PUBLIC seg_bounds. The plug
    is centered on the tube AXIS (not the low-seated hull) and sized to the
    local tube radius so it spans the corridor. Returns None if the robot is
    not near this corridor's centerline (defensive)."""
    best = None  # (dist2, center, tube_radius)
    p = np.asarray(robot_pos, dtype=float)
    for seg in getattr(corridor, "seg_bounds", []):
        a = np.asarray(seg["start"], dtype=float)
        b = np.asarray(seg["end"], dtype=float)
        ab = b - a
        L2 = float(np.dot(ab, ab))
        if L2 < 1e-12:
            continue
        t = float(np.dot(p - a, ab)) / L2
        t = max(0.0, min(1.0, t))
        c = a + ab * t
        d2 = float(np.dot(p - c, p - c))
        if best is None or d2 < best[0]:
            best = (d2, c, float(seg["radius"]))
    if best is None:
        return None
    _d2, center, tube_radius = best
    return center, tube_radius


def _resolve_robots(ship, hub, prev_pos):
    for corridor in hub.corridors:
        for robot in corridor.get_robots():
            if robot.is_defeated():
                continue   # pass-through once destroyed

            plug = _nearest_centerline_plug(corridor, robot.position)
            if plug is None:
                continue
            plug_center, tube_radius = plug

            # Plug spans the tube (minus a thin rim) but never smaller than
            # the visible hull; then add the ship skin.
            tube_span = max(0.0, tube_radius - PLUG_RIM_GAP)
            plug_r = max(tube_span, _hull_min_radius(robot)) + SHIP_RADIUS
            print("PLUG r", round(plug_r, 2), "center", np.round(plug_center, 1),
                  "dist", round(_norm(ship.pos - plug_center), 2))

            to_ship = ship.pos - plug_center
            dist = _norm(to_ship)
            if dist >= plug_r:
                continue   # not inside this plug

            n = _normalize(to_ship)
            if n is None:
                n = _normalize(prev_pos - plug_center)
                if n is None:
                    n = np.array([0.0, 1.0, 0.0])

            # Hard stop at the plug surface; slide on its face.
            ship.pos = plug_center + n * plug_r
            vdot = float(np.dot(ship.vel, n))
            if vdot < 0.0:
                ship.vel = ship.vel - n * vdot


# ----------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ----------------------------------------------------------------------
def resolve(ship, hub, prev_pos):
    """Hard-stop-with-slide containment. Mutates ship.pos / ship.vel in
    place. Call EXACTLY between ship.update(dt, keys) and ship.apply_view().

    prev_pos: a COPY of ship.pos taken BEFORE ship.update() ran (the last
    known-legal position). Pass np.asarray(prev_pos, float).

    Order: WALLS first, then ROBOTS, then ONE more wall pass -- a robot push
    in a tight tube could nudge the ship toward a wall; the second wall pass
    catches that. Correct-and-simple over clever. If constraints truly fight,
    the wall pass's "still outside -> prev_pos" fallback stops the ship dead
    rather than leaking it through either surface.
    """
    prev_pos = np.asarray(prev_pos, dtype=float)

    _resolve_walls(ship, hub, prev_pos)
    _resolve_robots(ship, hub, prev_pos)
    _resolve_walls(ship, hub, prev_pos)   # re-settle if a robot push hit rock
