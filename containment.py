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

import math
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

# (ROBOT_RADIUS_PAD, ROBOT_RADIUS_MIN, PLUG_RIM_GAP removed --
#  no longer used by the oranges-in-a-box block sphere.)


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
    if hub.inside(ship.pos, margin=SHIP_RADIUS):
        return  # legal: the whole attempted move stayed in the world

    # The move pushed (part of) the ship into rock. Find the slide normal.
    n = _wall_normal(hub, ship.pos)

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
# ROBOT BLOCKING -- "oranges in a box."
#
# The ship is an invisible sphere; each undefeated robot is an invisible
# sphere CENTERED ON THE TUBE AXIS (not on the robot's low drawn position,
# which left a gap to fly over -- that was the earlier bug). The robot
# sphere is sized so that ship_radius + robot_radius is LARGER than the
# tube's clear half-width, so the ship cannot fit beside it -- no lane on
# the floor, in a corner, or overhead. Wall containment keeps the ship in
# the tube; this keeps it from passing the robot. Hard stop + slide.
# ----------------------------------------------------------------------

def _robot_block_sphere(corridor, robot):
    """Return (center_on_axis, robot_radius) for an undefeated robot.

    center_on_axis: the point on the corridor centerline nearest the robot,
                    using the corridor's public seg_bounds (so the sphere
                    sits in the MIDDLE of the tube, not on the floor).
    robot_radius:   sized from the local tube radius so that
                    robot_radius + SHIP_RADIUS > tube_radius, i.e. the ship
                    cannot fit beside it. Returns None if not near this
                    corridor's centerline.
    """
    p = np.asarray(robot.position, dtype=float)
    best = None  # (dist2, center, tube_radius)
    for seg in getattr(corridor, "seg_bounds", []):
        a = np.asarray(seg["start"], dtype=float)
        b = np.asarray(seg["end"], dtype=float)
        ab = b - a
        L2 = float(np.dot(ab, ab))
        if L2 < 1e-12:
            continue
        t = max(0.0, min(1.0, float(np.dot(p - a, ab)) / L2))
        c = a + ab * t
        d2 = float(np.dot(p - c, p - c))
        if best is None or d2 < best[0]:
            best = (d2, c, float(seg["radius"]))
    if best is None:
        return None
    _d2, center, tube_radius = best

    # Size the robot sphere to reach the FARTHEST the ship center can get
    # from the axis, so there is no corner/diagonal lane to slip through.
    # Round tube -> max wall distance is tube_radius. Square tube -> it's
    # tube_radius * sqrt(2) (the corner). We use sqrt(2) unconditionally so a
    # square cross-section is also fully blocked; for the actual round tube
    # this is just safely conservative (the wall still keeps the ship inside,
    # so an oversized robot sphere is harmless). A tiny extra ensures the
    # ship+robot spheres always overlap rather than exactly touch.
    DIAGONAL_SAFETY = math.sqrt(2.0)
    max_wall_dist = tube_radius * DIAGONAL_SAFETY
    robot_radius = max_wall_dist - SHIP_RADIUS + 0.3
    return center, robot_radius


def _resolve_robots(ship, hub, prev_pos):
    for corridor in hub.corridors:
        for robot in corridor.get_robots():
            if robot.is_defeated():
                continue   # destroyed -> sphere gone, ship passes freely

            sphere = _robot_block_sphere(corridor, robot)
            if sphere is None:
                continue
            center, robot_radius = sphere

            solid_r = robot_radius + SHIP_RADIUS   # ship sphere + robot sphere
            to_ship = ship.pos - center
            dist = _norm(to_ship)
            print("ORANGE solid_r", round(solid_r, 2), "dist", round(dist, 2))
            if dist >= solid_r:
                continue   # not touching this robot

            n = _normalize(to_ship)
            if n is None:
                n = _normalize(prev_pos - center)
                if n is None:
                    n = np.array([0.0, 1.0, 0.0])

            # Hard stop at the surface; slide along it (tangential motion kept).
            ship.pos = center + n * solid_r
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
