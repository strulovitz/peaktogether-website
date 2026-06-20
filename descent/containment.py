"""
containment.py -- DESCENT QED, CHILD MODULE #C1: ship collision / containment.

PURE GEOMETRY + PHYSICS. MATHEMATICS-BLIND: this module reads no equations,
picks no colors, knows no "meaning." It asks only two questions:
    "is the ship center inside the rock-bounded world?"
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

This file combines:
  * ROBOT BLOCKING  -- the v4 "oranges in a box" code, KEPT VERBATIM.
  * WALL CONFINEMENT -- new nearest-centerline confinement (replaces the
    v4 wall code that leaked through the square corners into the void).
"""

import math
import numpy as np


SHIP_RADIUS = 1.5

# Confinement radius around a corridor centerline. The corridor's round
# collision radius is 6 and its drawn square corners reach ~8.5; we hold the
# ship's CENTER at 4.0 from the axis -- forgiving enough to fly into a
# doorway, strict enough that the ship never reaches a corner and so can
# never see through one into the void.
CONFINE_RADIUS = 4.0

_EPS = 1e-12


# ----------------------------------------------------------------------
# small vector helpers
# ----------------------------------------------------------------------
def _norm(v):
    return float(np.linalg.norm(v))


def _normalize(v):
    n = _norm(v)
    if n < 1e-12:
        return None
    return v / n


# ======================================================================
# ROBOT BLOCKING -- "oranges in a box."   *** v4 CODE, KEPT VERBATIM ***
#
# The ship is an invisible sphere; each undefeated robot is an invisible
# sphere CENTERED ON THE TUBE AXIS (not on the robot's low drawn position).
# The robot sphere is sized so that ship_radius + robot_radius is LARGER
# than the tube's clear half-width, so the ship cannot fit beside it.
# Defeated robots are pass-through.
# ======================================================================

def _robot_block_sphere(corridor, robot):
    """Return (center_on_axis, robot_radius) for an undefeated robot."""
    p = np.asarray(robot.position, dtype=float)
    best = None
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
    DIAGONAL_SAFETY = math.sqrt(2.0)
    max_wall_dist = tube_radius * DIAGONAL_SAFETY
    robot_radius = max_wall_dist - SHIP_RADIUS + 0.3
    return center, robot_radius


def _resolve_robots(ship, hub, prev_pos):
    for corridor in hub.corridors:
        for robot in corridor.get_robots():
            if robot.is_defeated():
                continue
            sphere = _robot_block_sphere(corridor, robot)
            if sphere is None:
                continue
            center, robot_radius = sphere
            solid_r = robot_radius + SHIP_RADIUS
            to_ship = ship.pos - center
            dist = _norm(to_ship)
            if dist >= solid_r:
                continue
            n = _normalize(to_ship)
            if n is None:
                n = _normalize(prev_pos - center)
                if n is None:
                    n = np.array([0.0, 1.0, 0.0])
            ship.pos = center + n * solid_r
            vdot = float(np.dot(ship.vel, n))
            if vdot < 0.0:
                ship.vel = ship.vel - n * vdot

# *** end of v4 robot code -- untouched ***


# ======================================================================
# WALL CONFINEMENT -- new nearest-centerline confinement.
#
# Confine the ship's center to a circle of CONFINE_RADIUS around the nearest
# corridor centerline. Rock is not elastic: when the ship would cross the
# limit we remove only the INTO-wall component of motion and keep the
# ALONG-wall component (slide), and clamp position radially back onto the
# limit. Inside the open atrium sphere the ship flies completely free.
# ======================================================================

def _nearest_corridor_axis(hub, p):
    """Nearest corridor centerline to point p.

    Returns (foot, n_hat, dist, seg_radius) or None.
        foot       : closest point on the clamped segment centerline
        n_hat      : unit outward radial from centerline to p
        dist       : lateral distance from the centerline
        seg_radius : that segment's tube radius

    Uses the SAME per-segment data the robot code reads (corridor.seg_bounds
    with "start"/"end"/"radius"), so walls and robots agree on the geometry.
    """
    best = None
    for corridor in hub.corridors:
        for seg in getattr(corridor, "seg_bounds", []):
            a = np.asarray(seg["start"], dtype=float)
            b = np.asarray(seg["end"], dtype=float)
            ab = b - a
            L2 = float(np.dot(ab, ab))
            if L2 < _EPS:
                continue
            t = max(0.0, min(1.0, float(np.dot(p - a, ab)) / L2))
            foot = a + ab * t
            lateral = p - foot
            dist = _norm(lateral)
            if best is None or dist < best[2]:
                if dist > 1e-9:
                    n_hat = lateral / dist
                else:
                    n_hat = np.array([0.0, 1.0, 0.0])  # on axis: any radial
                best = (foot, n_hat, dist, float(seg["radius"]))
    return best


def _resolve_walls(ship, hub, prev_pos):
    p = np.asarray(ship.pos, dtype=float)

    # Inside the open atrium sphere: free flight, no correction.
    if _norm(p - hub.center) <= hub.radius:
        return

    near = _nearest_corridor_axis(hub, p)
    if near is None:
        return  # no corridors (degenerate level)

    foot, n_hat, dist, seg_radius = near

    # Hold the ship's center at CONFINE_RADIUS, never wider than the
    # segment's own tube radius (a flared cavern still uses 4.0).
    limit = min(CONFINE_RADIUS, seg_radius)
    if dist <= limit:
        return  # already inside the tube: free flight

    # Outside the limit: clamp position radially back onto the limit circle
    # (along-corridor progress preserved), then kill only outward velocity.
    ship.pos = foot + n_hat * limit
    vdot = float(np.dot(ship.vel, n_hat))
    if vdot > 0.0:
        ship.vel = ship.vel - n_hat * vdot


# ----------------------------------------------------------------------
# PUBLIC ENTRY POINT -- walls AND robots, together.
# ----------------------------------------------------------------------
def resolve(ship, hub, prev_pos):
    prev_pos = np.asarray(prev_pos, dtype=float)
    # 1) Confine to the rock walls first (slide along the tube).
    _resolve_walls(ship, hub, prev_pos)
    # 2) Block at undefeated robots (the v4 "oranges in a box").
    _resolve_robots(ship, hub, prev_pos)
    # 3) Re-settle the walls after the robot push, so a robot can never
    #    shove the ship out through a wall.
    _resolve_walls(ship, hub, prev_pos)
