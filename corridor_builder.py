"""
corridor_builder.py — DESCENT QED world tier.

Builds ONE gently-bent FOUR-WALL "mine shaft" corridor (the common Descent
box tunnel — no gravity, fly any orientation): grey rock tube, chevron mouth +
small title, robot stations blocking the way, calm plaque where a robot is
defeated (museum effect), blue hostage cavern at the far end.

Walls are ENQUEUED via render.queue_wall; caller calls render.flush_walls
ONCE per frame BEFORE billboards. We never sort walls here.

Two-phase draw:
  corridor.draw_world(cr, cu, texcache)   # walls queued + opaque robots
  render.flush_walls(ship.pos)
  corridor.draw_labels(cr, cu, texcache)  # small billboards (title + plaques)
"""

import math
import numpy as np

import palette
from palette import Palette
import render
from robots import Robot


# ----------------------------------------------------------------------
# TUNABLES
# ----------------------------------------------------------------------
TUBE_RADIUS      = 6.0       # half-width of the square tunnel
SEGMENT_LENGTH   = 14.0
MAX_TURN_DEG     = 22.0
MIN_TURN_DEG     = 12.0
N_SIDES          = 4         # FOUR-WALL box tunnel (common Descent section)
CHEVRON_ROWS     = 3
CAVERN_RADIUS    = 11.0
CAVERN_SEGMENTS  = 3         # flare over a few segments (smooth, no gap)

ROBOT_SIZE       = 1.0       # was 0.6 — shrinking it shrank the hologram too
TITLE_SCALE      = 0.9       # << tube width
PLAQUE_SCALE     = 0.7       # smaller than the robot
LABEL_LIFT       = 2.2       # how far above station to float a plaque
_RNG_SALT        = 0x5EED


# ----------------------------------------------------------------------
# math helpers
# ----------------------------------------------------------------------
def _unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _frame(forward, up_hint=(0.0, 1.0, 0.0)):
    f = _unit(forward)
    up_hint = np.asarray(up_hint, dtype=float)
    if abs(np.dot(f, _unit(up_hint))) > 0.97:
        up_hint = np.array([0.0, 0.0, 1.0])
    r = _unit(np.cross(up_hint, f))
    u = _unit(np.cross(f, r))
    return r, u, f


def _rotate_dir(forward, up, right, yaw, pitch):
    f = _unit(forward)
    cy, sy = math.cos(yaw), math.sin(yaw)
    f = _unit(f * cy + right * sy)
    r = _unit(np.cross(up, f))
    cp, sp = math.cos(pitch), math.sin(pitch)
    f = _unit(f * cp + up * sp)
    u = _unit(np.cross(f, r))
    return f, u, r


def _square_ring(center, right, up, radius):
    """N_SIDES=4 ring oriented as a box (flat floor/ceiling/walls)."""
    verts = []
    for k in range(N_SIDES):
        a = 2.0 * math.pi * (k + 0.5) / N_SIDES   # +0.5 -> flat top/bottom/sides
        verts.append(center + right * (math.cos(a) * radius) + up * (math.sin(a) * radius))
    return verts


# ----------------------------------------------------------------------
# CorridorGeometry
# ----------------------------------------------------------------------
class CorridorGeometry:
    """Public interface unchanged:
        entrance_pose() -> ((x,y,z),(nx,ny,nz))   mouth + OUTWARD normal
        inside(point, margin=0.0) -> bool
        seg_bounds -> list[dict] (center,right,up,radius)
        hostage_positions() -> list[(x,y,z)]
        get_robots() -> list[Robot]
        stations() -> list[((x,y,z), yaw)]
        update(dt, ship_position)
        draw_world(cr, cu, texcache)   # queue walls + opaque robots
        draw_labels(cr, cu, texcache)  # billboards, AFTER flush_walls
    """

    def __init__(self, corridor_data, origin=(0, 0, 0), direction=(0, 0, -1)):
        self._data    = corridor_data
        self._robots_data = list(corridor_data.robots)
        self._origin  = np.asarray(origin, dtype=float)
        self._dir0    = _unit(direction)
        self._palette = Palette(corridor_data.ledger)

        self._dominant_key = next(iter(corridor_data.ledger.primaries))
        self._dominant_rgb = self._palette.tint(self._dominant_key)[:3]

        self._ship_pos = self._origin.copy()

        self._build_rings()        # builds shared joint rings (NO gaps)
        self._build_stations()
        self._build_robots()
        self._build_cavern_anchors()

    # ---- construction -------------------------------------------------
    def _build_rings(self):
        """Build a chain of JOINT rings. Each ring is shared by the segment
        before and after it -> adjacent walls use identical vertices -> no gaps.
        At a bend, the joint ring is oriented to the AVERAGE of the two
        incoming/outgoing directions, so the corner closes cleanly."""
        robots_n = len(self._robots_data)
        n_seg = max(6, robots_n * 2 + CAVERN_SEGMENTS + 2)

        rng = np.random.default_rng((hash(self._data.title) ^ _RNG_SALT) & 0xFFFFFFFF)

        right, up, forward = _frame(self._dir0)
        pos = self._origin.copy()

        # collect node frames (centers + local axes + radius) along the path
        nodes = []  # each: dict(center, right, up, forward, radius)
        for i in range(n_seg + 1):  # n_seg+1 joints for n_seg segments
            if i == 0:
                pass
            elif i == 1:
                pass  # keep first segment straight so the mouth aligns
            else:
                yaw   = math.radians(rng.uniform(MIN_TURN_DEG, MAX_TURN_DEG)) * rng.choice([-1, 1])
                pitch = math.radians(rng.uniform(MIN_TURN_DEG, MAX_TURN_DEG)) * rng.choice([-1, 1])
                forward, up, right = _rotate_dir(forward, up, right, yaw, pitch)

            # smooth radius flare into the cavern over the last CAVERN_SEGMENTS
            segs_from_end = n_seg - i
            if segs_from_end < CAVERN_SEGMENTS:
                f = 1.0 - (segs_from_end / CAVERN_SEGMENTS)   # 0..1
                radius = TUBE_RADIUS + (CAVERN_RADIUS - TUBE_RADIUS) * f
            else:
                radius = TUBE_RADIUS

            nodes.append(dict(center=pos.copy(), right=right.copy(),
                              up=up.copy(), forward=forward.copy(), radius=radius))
            if i < n_seg:
                pos = pos + forward * SEGMENT_LENGTH

        self._nodes = nodes
        self._rings = [_square_ring(n["center"], n["right"], n["up"], n["radius"])
                       for n in nodes]

        self._mouth_pos    = nodes[0]["center"].copy()
        self._mouth_normal = -nodes[0]["forward"]
        self._far_center   = nodes[-1]["center"].copy()

        # public per-segment bounds for game_state
        self.seg_bounds = []
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            self.seg_bounds.append({
                "start":  a["center"].tolist(),
                "end":    b["center"].tolist(),
                "right":  a["right"].tolist(),
                "up":     a["up"].tolist(),
                "radius": max(a["radius"], b["radius"]),
            })

    def _seg_mid(self, i):
        a, b = self._nodes[i]["center"], self._nodes[i + 1]["center"]
        return (a + b) * 0.5

    def _build_stations(self):
        n = len(self._robots_data)
        self._station_poses = []
        if n == 0:
            return
        first = 1
        last = len(self._nodes) - 1 - CAVERN_SEGMENTS
        body = list(range(first, max(first + 1, last)))
        for j in range(n):
            t = (j + 1) / (n + 1)
            seg_i = body[int(t * (len(body) - 1) + 0.5)] if body else 1
            node = self._nodes[seg_i]
            center = self._seg_mid(seg_i)
            # seat the robot toward the FLOOR so its hologram rises into open
            # space toward the ceiling instead of clipping it
            center = center - node["up"] * (node["radius"] * 0.45)
            fwd = -node["forward"]
            yaw = math.atan2(fwd[0], -fwd[2])
            self._station_poses.append((tuple(center.tolist()), float(yaw)))

    def _build_robots(self):
        self._robots = []
        for rdata, pose in zip(self._robots_data, self._station_poses):
            # paint=None -> grey-metal hull. Eye color is applied INSIDE robots.py
            # from rdata.eye_color_key (the scanner glow). Do NOT paint the hull.
            self._robots.append(
                Robot(rdata, self._palette, station_pose=pose, paint=None, size=ROBOT_SIZE)
            )

    def _build_cavern_anchors(self):
        last = self._nodes[-1]
        c = last["center"]
        floor = -last["up"] * (last["radius"] * 0.55)
        self._hostage_anchors = [
            tuple((c + last["right"] * dx + floor).tolist())
            for dx in (-3.5, 0.0, 3.5)
        ]

    # ---- public interface --------------------------------------------
    def entrance_pose(self):
        return (tuple(self._mouth_pos.tolist()),
                tuple(_unit(self._mouth_normal).tolist()))

    def stations(self):
        return list(self._station_poses)

    def get_robots(self):
        return list(self._robots)

    def hostage_positions(self):
        return list(self._hostage_anchors)

    def inside(self, point, margin=0.0):
        p = np.asarray(point, dtype=float)
        for i in range(len(self._nodes) - 1):
            a, b = self._nodes[i], self._nodes[i + 1]
            axis = b["center"] - a["center"]
            L = np.linalg.norm(axis)
            if L < 1e-9:
                continue
            ax = axis / L
            s = float(np.dot(p - a["center"], ax))
            if -margin <= s <= L + margin:
                lateral = (p - a["center"]) - ax * s
                rad = max(a["radius"], b["radius"])
                if np.linalg.norm(lateral) <= rad + margin:
                    return True
        return False

    # ---- per-frame ----------------------------------------------------
    def update(self, dt, ship_position):
        self._ship_pos = np.asarray(ship_position, dtype=float)
        for r in self._robots:
            r.update(dt, ship_position)

    def draw_world(self, camera_right, camera_up, texcache):
        """Phase 1: ONLY queue translucent walls + mouth chevrons.
        Robots are NOT drawn here anymore — see draw_robots()."""
        self._draw_tube_walls()
        self._draw_chevrons()

    def draw_robots(self, camera_right, camera_up, texcache):
        """Phase 2b: draw robots (opaque hull + additive scanner/hologram).
        MUST be called AFTER render.flush_walls() so the additive hologram
        is not overpainted by the translucent walls."""
        for r in self._robots:
            r.draw(camera_right, camera_up, texcache)

    def draw_labels(self, camera_right, camera_up, texcache):
        """Phase 3: title + defeat plaques. After robots."""
        self._draw_title(camera_right, camera_up, texcache)
        self._draw_plaques(camera_right, camera_up, texcache)

    # ---- drawing internals -------------------------------------------
    def _quads_between(self, ring_a, ring_b):
        for k in range(N_SIDES):
            k2 = (k + 1) % N_SIDES
            yield [ring_a[k], ring_a[k2], ring_b[k2], ring_b[k]]

    def _draw_tube_walls(self):
        fill  = palette.WORLD_WALL_FILL[:3]
        edge  = palette.WORLD_EDGE
        base_alpha = palette.WORLD_WALL_FILL[3] if len(palette.WORLD_WALL_FILL) > 3 \
                     else palette.BACKDROP_BASE_ALPHA
        # blend wall color toward HOSTAGE_BLUE in the cavern so the far room reads blue
        for i in range(len(self._rings) - 1):
            ra, rb = self._rings[i], self._rings[i + 1]
            segs_from_end = (len(self._rings) - 1) - i
            if segs_from_end <= CAVERN_SEGMENTS:
                blue = palette.HOSTAGE_BLUE
                t = 1.0 - (segs_from_end / max(1, CAVERN_SEGMENTS))
                wall = tuple(fill[c] * (1 - 0.5 * t) + blue[c] * (0.5 * t) for c in range(3))
            else:
                wall = fill
            for quad in self._quads_between(ra, rb):
                render.queue_wall(quad, wall, edge, base_alpha)

    def _draw_chevrons(self):
        """Subtle dominant-color band just inside the mouth (entry signage).
        Far fewer / dimmer than the old corner glow."""
        glow = self._dominant_rgb
        c0 = self._nodes[0]
        for row in range(CHEVRON_ROWS):
            along = c0["forward"] * (2.0 + row * 1.5)
            r = c0["radius"] * 0.98
            ra = _square_ring(c0["center"] + along, c0["right"], c0["up"], r)
            rb = _square_ring(c0["center"] + along + c0["forward"] * 0.5,
                              c0["right"], c0["up"], r)
            a = max(0.15, 0.55 - row * 0.15)
            for quad in self._quads_between(ra, rb):
                render.queue_wall(quad, glow, glow, a)

    def _draw_title(self, cr, cu, texcache):
        title = self._data.title
        tex = texcache.get_mathtext(
            r"\mathrm{%s}" % title.replace(" ", r"\ "),
            color=self._dominant_rgb, fontsize=16,
        )
        n0 = self._nodes[0]
        center = n0["center"] + n0["forward"] * 4.0 + n0["up"] * (n0["radius"] * 0.6)
        render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                              scale=TITLE_SCALE, alpha=0.95)

    def _draw_plaques(self, cr, cu, texcache):
        text_rgb = self._palette.text_color_on(self._dominant_key)
        for r, rdata, (pose, _yaw) in zip(self._robots, self._robots_data, self._station_poses):
            if not r.is_defeated():
                continue
            text = (getattr(rdata, "briefing_hint", "") or "—")[:36]
            tex = texcache.get_mathtext(
                r"\mathrm{%s}" % text.replace(" ", r"\ "),
                color=text_rgb, fontsize=13,
            )
            center = np.asarray(pose, dtype=float) + np.array([0.0, LABEL_LIFT, 0.0])
            render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                                  scale=PLAQUE_SCALE, alpha=0.9)


def build_corridor(corridor_data, origin=(0, 0, 0), direction=(0, 0, -1)):
    return CorridorGeometry(corridor_data, origin=origin, direction=direction)