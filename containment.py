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

SHIP_RADIUS = 0.6        # ship "skin": clamp margin for hub.inside()
NORMAL_EPS  = 0.25       # finite-difference probe step for the wall normal
                         # (units): small vs TUBE_RADIUS 6, large enough to
                         # cross the inside/outside boundary reliably given
                         # ~<=0.9 max per-frame motion.


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
# ROBOT BLOCKING -- hard stop + slide around an undefeated robot's hull.
#
# Treat each UNDEFEATED robot as a sphere at robot.position with radius
# (robot_hull_radius + SHIP_RADIUS). If the ship center is inside that
# sphere, push it out to the surface along the line from the robot to the
# ship, and kill the inward velocity component (same slide math as walls,
# with n = normalize(ship.pos - robot.position)).
#
# Defeated robots are skipped (pass-through). Hostages are never consulted
# here (they are not obstacles).
# ----------------------------------------------------------------------
def _robot_hull_radius(robot):
    # World-space hull radius: robots.py draws the hull with glScalef(size)
    # and exposes Robot._HULL_R ("approx hull radius"). size * _HULL_R is the
    # live world radius, honoring any future size change automatically.
    hull_r = getattr(type(robot), "_HULL_R", 1.6)
    size = float(getattr(robot, "size", 1.0))
    return size * hull_r


def _resolve_robots(ship, hub, prev_pos):
    for corridor in hub.corridors:
        for robot in corridor.get_robots():
            if robot.is_defeated():
                continue   # pass-through once destroyed
            rc = np.asarray(robot.position, dtype=float)
            solid_r = _robot_hull_radius(robot) + SHIP_RADIUS
            to_ship = ship.pos - rc
            dist = _norm(to_ship)
            print("ROBOT", robot.is_defeated(), "dist", round(dist, 2),
                  "solid_r", round(solid_r, 2))
            if dist >= solid_r:
                continue   # not overlapping this robot

            n = _normalize(to_ship)
            if n is None:
                # ship center is exactly on the robot center: pick the
                # direction we came from as the safe push-out.
                n = _normalize(prev_pos - rc)
                if n is None:
                    n = np.array([0.0, 1.0, 0.0])  # arbitrary but valid

            # Push the ship center out to the sphere surface (hard stop).
            ship.pos = rc + n * solid_r

            # Kill inward velocity so it slides around the hull, not into it.
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
