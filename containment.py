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

WALL_INSET = 1.8         # How far inside the rock wall the inner (flyable)
                         # tube sits. Tube radius ~6; inner radius = 6-1.8 =
                         # 4.2. Exceeds SHIP_RADIUS so the camera never
                         # reaches the wall. Correction always pulls TOWARD
                         # the axis, never outward -- no void-leak possible.


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
# WALL CONTAINMENT -- keep the ship inside a NARROWER inner prism/tube.
#
# Each corridor is straight prism sections (seg_bounds gives each section's
# centerline as start->end base-centers, plus its tube radius). We confine
# the ship to an INNER tube of radius INNER_RADIUS around the nearest
# section's axis: project the ship onto the axis; if it is farther than
# INNER_RADIUS from the axis, pull it straight back to that radius (the
# correction points TOWARD the axis, never outward, so the ship can never
# be pushed into the void). The atrium is handled by clamping to its sphere.
#
# The player still flies freely inside the inner tube -- it just can't reach
# the rock. Since the walls are untextured, the slightly smaller flyable
# volume is imperceptible.
# ----------------------------------------------------------------------

def _confine_to_axis(ship, center_a, center_b, tube_radius):
    """Confine the ship to an inner tube around the segment center_a->center_b.
    Returns True if this segment 'claims' the ship (its projection lands on
    the segment), so the caller knows the ship was handled."""
    a = np.asarray(center_a, dtype=float)
    b = np.asarray(center_b, dtype=float)
    ab = b - a
    L2 = float(np.dot(ab, ab))
    if L2 < 1e-12:
        return False
    t = float(np.dot(ship.pos - a, ab)) / L2
    if t < 0.0 or t > 1.0:
        return False                      # ship is not alongside this segment
    axis_point = a + ab * t               # nearest point on the centerline
    radial = ship.pos - axis_point        # vector from axis out to the ship
    r = _norm(radial)
    inner_radius = max(0.0, tube_radius - WALL_INSET)
    if r > inner_radius:
        # Pull the ship straight back toward the axis to the inner radius.
        if r > 1e-9:
            ship.pos = axis_point + radial * (inner_radius / r)
            # Kill the outward (toward-wall) velocity component.
            out = radial / r
            vdot = float(np.dot(ship.vel, out))
            if vdot > 0.0:
                ship.vel = ship.vel - out * vdot
    print("WALL r", round(r, 2), "inner", round(inner_radius, 2))
    return True


def _resolve_walls(ship, hub, prev_pos):
    # 1) If the ship is alongside any corridor section, confine it to that
    #    section's inner tube.
    handled = False
    for corridor in hub.corridors:
        for seg in getattr(corridor, "seg_bounds", []):
            if _confine_to_axis(ship, seg["start"], seg["end"],
                                 float(seg["radius"])):
                handled = True
                break
        if handled:
            break

    # 2) Otherwise the ship is in the atrium: clamp it inside the atrium
    #    sphere (radius minus the same inset / ship skin).
    if not handled:
        c = np.asarray(hub.center, dtype=float)
        radial = ship.pos - c
        r = _norm(radial)
        atrium_inner = max(0.0, float(hub.radius) - WALL_INSET)
        if r > atrium_inner and r > 1e-9:
            out = radial / r
            ship.pos = c + radial * (atrium_inner / r)
            vdot = float(np.dot(ship.vel, out))
            if vdot > 0.0:
                ship.vel = ship.vel - out * vdot


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
    """Hard containment. Mutates ship.pos / ship.vel in place. Call EXACTLY
    between ship.update(dt, keys) and ship.apply_view().

    Robots first (block sphere on the tube axis), then walls (confine to the
    inner tube). The wall step ALWAYS pulls the ship TOWARD the axis, never
    outward, so it can never push the ship into the void -- which is what
    broke the earlier slide-based version. If a robot push moved the ship
    radially, the wall step simply pulls it back onto the inner tube; the
    two no longer fight, because the wall correction has a fixed inward
    direction.
    """
    prev_pos = np.asarray(prev_pos, dtype=float)
    _resolve_robots(ship, hub, prev_pos)
    _resolve_walls(ship, hub, prev_pos)
