"""
corridor_builder.py — DESCENT QED world tier.

Builds ONE gently-bent octagonal "mine shaft" corridor: grey rock tube +
dominant-color corner glow, chevron mouth + title, robot stations blocking
the way, calm plaque where a robot is defeated (museum effect), blue-hostage
cavern at the far end.

Tier: world-builder (numpy OK). Colors/world constants live in palette
(module-level). Translucent rock walls are ENQUEUED via render.queue_wall;
the app/demo calls render.flush_walls(ship.pos) ONCE per frame. We never sort.

DRAW IS TWO-PHASE (contract: flush walls BEFORE billboards):
  corridor.draw_world(cr, cu, texcache)   # walls (queued) + opaque robots
  render.flush_walls(ship.pos)            # caller does this between phases
  corridor.draw_labels(cr, cu, texcache)  # title + defeat plaques (billboards)

Bend machinery (centerline frames, ELBOW seam-overlap) adapted from Fable's
deprecated descent_qed/corridor.py, driven with REAL turns.
"""

import math
import numpy as np

import palette
from palette import Palette
import render
from robots import Robot


# ----------------------------------------------------------------------
# TUNABLES  (iterate with DeepSeek via screenshots)
# ----------------------------------------------------------------------
TUBE_RADIUS      = 6.0
SEGMENT_LENGTH   = 14.0
MAX_TURN_DEG     = 22.0
MIN_TURN_DEG     = 12.0
SEAM_OVERLAP     = 0.6
N_SIDES          = 8
CHEVRON_ROWS     = 4
CAVERN_RADIUS    = 11.0
CAVERN_SEGMENTS  = 2

PLAQUE_SCALE     = 2.2
TITLE_SCALE      = 3.0
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


# ----------------------------------------------------------------------
# Segment
# ----------------------------------------------------------------------
class _Segment:
    __slots__ = ("start", "end", "right", "up", "forward", "radius")

    def __init__(self, start, end, right, up, forward, radius):
        self.start   = np.asarray(start, dtype=float)
        self.end     = np.asarray(end, dtype=float)
        self.right   = np.asarray(right, dtype=float)
        self.up      = np.asarray(up, dtype=float)
        self.forward = np.asarray(forward, dtype=float)
        self.radius  = float(radius)

    def ring(self, t, radius=None):
        rad = self.radius if radius is None else radius
        center = self.start + (self.end - self.start) * t
        verts = []
        for k in range(N_SIDES):
            a = 2.0 * math.pi * (k + 0.5) / N_SIDES
            offset = self.right * (math.cos(a) * rad) + self.up * (math.sin(a) * rad)
            verts.append(center + offset)
        return verts

    def local(self, point):
        p = np.asarray(point, dtype=float) - self.start
        axis = self.end - self.start
        L = np.linalg.norm(axis)
        if L < 1e-9:
            return 0.0, p, 0.0
        s = float(np.dot(p, axis / L))
        lateral = p - (axis / L) * s
        return s, lateral, L


# ----------------------------------------------------------------------
# CorridorGeometry
# ----------------------------------------------------------------------
class CorridorGeometry:
    """Bent octagonal tube + content hooks. Public interface:
        entrance_pose()            -> ((x,y,z),(nx,ny,nz))  mouth + OUTWARD normal
        inside(point, margin=0.0)  -> bool
        seg_bounds                 -> list[dict]  (start,end,right,up,radius)
        hostage_positions()        -> list[(x,y,z)]
        get_robots()               -> list[Robot]
        stations()                 -> list[((x,y,z), yaw)]
        update(dt, ship_position)  -> None
        draw_world(cr, cu, texcache)  -> None   (queue walls + opaque robots)
        draw_labels(cr, cu, texcache) -> None   (billboards; AFTER flush_walls)
    """

    def __init__(self, corridor_data, origin=(0, 0, 0), direction=(0, 0, -1)):
        self._data    = corridor_data
        self._robots_data = list(corridor_data.robots)     # keep our own (Bug 2)
        self._origin  = np.asarray(origin, dtype=float)
        self._dir0    = _unit(direction)
        self._palette = Palette(corridor_data.ledger)

        # dominant key = FIRST primary; primaries is a dict (Bug 4)
        self._dominant_key = next(iter(corridor_data.ledger.primaries))
        self._dominant_rgb = self._palette.tint(self._dominant_key)[:3]  # RGBA->RGB (Bug 5)

        self._ship_pos = self._origin.copy()

        self._build_centerline()
        self._build_stations()
        self._build_robots()
        self._build_cavern_anchors()

    # ---- construction -------------------------------------------------
    def _build_centerline(self):
        robots_n = len(self._robots_data)
        n_seg = max(6, robots_n * 2 + CAVERN_SEGMENTS + 2)

        rng = np.random.default_rng(
            (hash(self._data.title) ^ _RNG_SALT) & 0xFFFFFFFF
        )

        right, up, forward = _frame(self._dir0)
        pos = self._origin.copy()
        self._segments = []
        self._mouth_pos = pos.copy()
        self._mouth_normal = -forward

        for i in range(n_seg):
            if i == 0:
                pass  # first segment straight so the mouth aligns cleanly
            else:
                yaw   = math.radians(rng.uniform(MIN_TURN_DEG, MAX_TURN_DEG)) * rng.choice([-1, 1])
                pitch = math.radians(rng.uniform(MIN_TURN_DEG, MAX_TURN_DEG)) * rng.choice([-1, 1])
                forward, up, right = _rotate_dir(forward, up, right, yaw, pitch)

            is_cavern = i >= (n_seg - CAVERN_SEGMENTS)
            radius = CAVERN_RADIUS if is_cavern else TUBE_RADIUS

            start = pos.copy()
            end   = pos + forward * SEGMENT_LENGTH
            self._segments.append(_Segment(start, end, right, up, forward, radius))
            pos = end

        self._far_center = pos.copy()

        self.seg_bounds = [
            {
                "start":  seg.start.tolist(),
                "end":    seg.end.tolist(),
                "right":  seg.right.tolist(),
                "up":     seg.up.tolist(),
                "radius": seg.radius,
            }
            for seg in self._segments
        ]

    def _build_stations(self):
        body = self._segments[1:len(self._segments) - CAVERN_SEGMENTS]
        n = len(self._robots_data)
        self._station_poses = []
        if not body or n == 0:
            return
        for j in range(n):
            t = (j + 1) / (n + 1)
            seg = body[int(t * (len(body) - 1) + 0.5)]
            center = (seg.start + seg.end) * 0.5
            f = -seg.forward
            yaw = math.atan2(f[0], -f[2])
            self._station_poses.append((tuple(center.tolist()), float(yaw)))

    def _build_robots(self):
        self._robots = []
        for rdata, pose in zip(self._robots_data, self._station_poses):
            paint = self._palette.eye(rdata.eye_color_key)
            self._robots.append(
                Robot(rdata, self._palette, station_pose=pose, paint=paint, size=1.0)
            )

    def _build_cavern_anchors(self):
        cav = self._segments[len(self._segments) - CAVERN_SEGMENTS:]
        self._hostage_anchors = []
        if not cav:
            self._hostage_anchors = [tuple(self._far_center.tolist())]
            return
        last = cav[-1]
        c = (last.start + last.end) * 0.5
        for dx in (-3.0, 0.0, 3.0):
            anchor = c + last.right * dx - last.up * (last.radius * 0.5)
            self._hostage_anchors.append(tuple(anchor.tolist()))

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
        for seg in self._segments:
            s, lateral, L = seg.local(p)
            if -margin <= s <= L + margin:
                if np.linalg.norm(lateral) <= seg.radius + margin:
                    return True
        return False

    # ---- per-frame ----------------------------------------------------
    def update(self, dt, ship_position):
        self._ship_pos = np.asarray(ship_position, dtype=float)
        for r in self._robots:
            r.update(dt, ship_position)

    def draw_world(self, camera_right, camera_up, texcache):
        """Phase 1: enqueue translucent walls + draw OPAQUE robots.
        Caller MUST call render.flush_walls(ship.pos) after this,
        then call draw_labels()."""
        self._draw_tube_walls()
        self._draw_corner_glow()
        self._draw_chevrons()
        for r in self._robots:
            r.draw(camera_right, camera_up, texcache)

    def draw_labels(self, camera_right, camera_up, texcache):
        """Phase 2: billboards (title + defeat plaques). Call AFTER flush_walls."""
        self._draw_title(camera_right, camera_up, texcache)
        self._draw_plaques(camera_right, camera_up, texcache)

    # ---- drawing internals -------------------------------------------
    def _quads_between(self, ring_a, ring_b):
        for k in range(N_SIDES):
            k2 = (k + 1) % N_SIDES
            yield [ring_a[k], ring_a[k2], ring_b[k2], ring_b[k]]

    def _draw_tube_walls(self):
        fill  = palette.WORLD_WALL_FILL[:3]              # module-level (Bug 1)
        edge  = palette.WORLD_EDGE
        alpha = palette.WORLD_WALL_FILL[3] if len(palette.WORLD_WALL_FILL) > 3 \
                else palette.BACKDROP_BASE_ALPHA
        for i, seg in enumerate(self._segments):
            nxt = self._segments[i + 1] if i + 1 < len(self._segments) else None
            ring_a = seg.ring(0.0)
            t_end = 1.0 + (SEAM_OVERLAP / SEGMENT_LENGTH if nxt is not None else 0.0)
            ring_b = seg.ring(t_end)
            for quad in self._quads_between(ring_a, ring_b):
                render.queue_wall(quad, fill, edge, alpha)

    def _draw_corner_glow(self):
        glow = self._dominant_rgb
        glow_alpha = 0.85
        for seg in self._segments:
            ra = seg.ring(0.0)
            rb = seg.ring(1.0)
            ca = (seg.start + seg.end) * 0.5
            inset = 0.12 * seg.radius
            for k in range(N_SIDES):
                ea, eb = ra[k], rb[k]
                na = _unit(ca - ea) * inset
                strip = [ea, eb, eb + na, ea + na]
                render.queue_wall(strip, glow, glow, glow_alpha)

    def _draw_chevrons(self):
        seg = self._segments[0]
        glow = self._dominant_rgb
        for row in range(CHEVRON_ROWS):
            t0 = 0.04 + row * 0.06
            t1 = t0 + 0.03
            ra = seg.ring(t0, radius=seg.radius * 0.985)
            rb = seg.ring(t1, radius=seg.radius * 0.985)
            a = max(0.2, 1.0 - row * 0.18)
            for quad in self._quads_between(ra, rb):
                render.queue_wall(quad, glow, glow, a)

    def _draw_title(self, cr, cu, texcache):
        title = self._data.title
        tex = texcache.get_mathtext(
            r"\mathrm{%s}" % title.replace(" ", r"\ "),
            color=self._dominant_rgb, fontsize=18,
        )
        seg = self._segments[0]
        center = seg.start + seg.forward * (SEGMENT_LENGTH * 0.25) + seg.up * (seg.radius * 0.55)
        render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                              scale=TITLE_SCALE, alpha=0.95)

    def _draw_plaques(self, cr, cu, texcache):
        text_rgb = self._palette.text_color_on(self._dominant_key)   # instance (Bug 3)
        for r, rdata, (pose, _yaw) in zip(self._robots, self._robots_data, self._station_poses):
            if not r.is_defeated():
                continue
            text = (getattr(rdata, "briefing_hint", "") or "—")[:40]   # own data (Bug 2)
            tex = texcache.get_mathtext(
                r"\mathrm{%s}" % text.replace(" ", r"\ "),
                color=text_rgb, fontsize=14,
            )
            center = np.asarray(pose, dtype=float) + np.array([0.0, 1.2, 0.0])
            render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                                  scale=PLAQUE_SCALE, alpha=0.9)


def build_corridor(corridor_data, origin=(0, 0, 0), direction=(0, 0, -1)):
    return CorridorGeometry(corridor_data, origin=origin, direction=direction)