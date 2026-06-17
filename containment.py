"""
containment.py -- Brief #C1: keep the ship inside the rock.

The world is a hollow atrium sphere plus straight corridor segments
(see hub_builder.py / corridor_builder.py). The drawn walls are square,
but the legal interior is round: a sphere for the atrium, a swept circle
(cylinder) around each corridor segment's centerline.

We confine the ship to a circle of radius CONFINE_RADIUS around the
nearest corridor centerline (smaller than the corridor's own collision
radius of 6, so the ship never reaches the square corners and so can
never see through them). Inside the atrium sphere the ship flies free.

Rock is not elastic: when the ship would cross the limit we do NOT push,
bounce, or stop it. We remove only the component of its motion that goes
INTO the wall and keep the component that runs ALONG the wall:

    v_allowed = v - (v . n_hat) * n_hat        (n_hat = outward radial)

so a dead-on hit stops, a glancing hit slides. The same projection is
applied to position so the ship is never left a hair outside the limit.
"""

import numpy as np


# Confinement radius around a corridor centerline. The corridor's round
# collision radius is 6 (TUBE_RADIUS) and its square wall corners reach
# ~8.5; we sit the ship well inside both at 4.0 -- forgiving enough to fly
# into a doorway, strict enough never to leak through a corner.
CONFINE_RADIUS = 4.0

# Small slack so floating-point jitter at the limit doesn't chatter.
_EPS = 1e-6


def _nearest_corridor_axis(hub, p):
    """Find the corridor segment whose centerline is nearest to point p.

    Returns (foot, n_hat, dist, radius):
        foot   : closest point ON the (clamped) segment centerline
        n_hat  : unit outward radial direction from centerline to p
        dist   : lateral distance from the centerline
        radius : that segment's own collision radius
    or None if there are no corridor segments at all.

    This mirrors corridor_builder.inside(): for each segment we project p
    onto the segment axis (clamped to the segment's extent) and measure the
    lateral offset. We keep the segment with the smallest lateral distance,
    so seams and bends are handled by "nearest", never by a gap.
    """
    best = None
    for c in hub.corridors:
        nodes = c._nodes
        for i in range(len(nodes) - 1):
            a_c = np.asarray(nodes[i]["center"], dtype=float)
            b_c = np.asarray(nodes[i + 1]["center"], dtype=float)
            axis = b_c - a_c
            L = float(np.linalg.norm(axis))
            if L < _EPS:
                continue
            ax = axis / L
            s = float(np.dot(p - a_c, ax))
            s = max(0.0, min(L, s))           # clamp onto the segment
            foot = a_c + ax * s
            lateral = p - foot
            dist = float(np.linalg.norm(lateral))
            seg_radius = max(nodes[i]["radius"], nodes[i + 1]["radius"])
            if best is None or dist < best[2]:
                if dist > _EPS:
                    n_hat = lateral / dist
                else:
                    n_hat = np.array([0.0, 1.0, 0.0])  # on the axis: any radial
                best = (foot, n_hat, dist, seg_radius)
    return best


def resolve(ship, hub, prev_pos):
    """Confine the ship after ship.update() set a tentative ship.pos.

    Strategy:
      * If the ship is comfortably inside the legal world, do nothing.
      * Otherwise confine it to CONFINE_RADIUS around the nearest corridor
        centerline, sliding along the wall (remove only the into-wall part
        of position and velocity).

    The atrium sphere (radius 34, center 0) is large and open; we let the
    ship fly free anywhere inside it. The tight confinement only matters in
    the corridors, where the square corners would otherwise leak.
    """
    p = np.asarray(ship.pos, dtype=float)
    center = hub.center
    R = hub.radius

    # --- inside the open atrium sphere: free flight, no correction --------
    if np.linalg.norm(p - center) <= R:
        return

    # --- otherwise we're in (or near) a corridor: confine to the tube -----
    near = _nearest_corridor_axis(hub, p)
    if near is None:
        return  # no corridors (degenerate level): nothing to confine to

    foot, n_hat, dist, _seg_radius = near

    # The limit is the SMALL confinement circle, but never larger than the
    # segment's own collision radius (so a flared cavern still uses 4.0).
    limit = CONFINE_RADIUS
    if dist <= limit:
        return  # already inside the tube: free flight

    # --- ship is outside the tube limit: slide along the rock -------------
    # 1) Position: clamp it back onto the limit circle along the radial.
    #    (Place it exactly ON the limit, sliding it inward only radially so
    #     its along-corridor position is preserved.)
    new_pos = foot + n_hat * limit
    ship.pos = new_pos

    # 2) Velocity: remove only the component heading INTO the wall (outward
    #    along n_hat). Keep everything running along the wall.
    v = np.asarray(ship.vel, dtype=float)
    into = float(np.dot(v, n_hat))
    if into > 0.0:                      # only kill outward-going motion
        v = v - into * n_hat
        ship.vel = v
