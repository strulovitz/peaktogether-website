"""
corridor_builder.py — DESCENT QED world tier.

Builds ONE gently-bent octagonal "mine shaft" corridor from a parsed
corridor file: grey rock tube + dominant-color corner glow, chevron mouth
with title label, robot stations blocking the way, calm plaque where a
robot is defeated (museum effect), and a blue-hostage cavern at the far end.

Tier: world-builder (numpy OK). All colors/world constants come from palette.
Translucent rock walls are ENQUEUED via render.queue_wall; the app (or demo)
calls render.flush_walls(ship.pos) once per frame. We never sort walls here.

Ported bend machinery (centerline frames, ELBOW seam-overlap) is adapted from
Fable's deprecated descent_qed/corridor.py, driven with REAL turns.
"""

import math
import numpy as np

import palette as palette_mod
import render
from robots import Robot


# ----------------------------------------------------------------------
# TUNABLES  (iterate with DeepSeek via screenshots)
# ----------------------------------------------------------------------
TUBE_RADIUS      = 6.0     # circumradius of the octagon (world units)
SEGMENT_LENGTH   = 14.0    # nominal length of one centerline segment
STATION_SPACING  = 1       # robots per N segments are spaced out (see layout)
MAX_TURN_DEG     = 22.0    # |yaw|,|pitch| per segment cap (gentle mine shaft)
MIN_TURN_DEG     = 12.0    # avoid dead-straight; always a little curve
SEAM_OVERLAP     = 0.6     # BACK_EXTEND/TURN_EXTEND: walls overlap to hide gaps
N_SIDES          = 8       # octagonal tube
GLOW_SIDES       = 8       # corner-glow strips: one per edge
CHEVRON_ROWS     = 4       # mouth chevron stripes
CAVERN_RADIUS    = 11.0    # hostage cavern is a wider room at the far end
CAVERN_SEGMENTS  = 2       # how many trailing segments flare into the cavern

PLAQUE_SCALE     = 2.2     # billboard world-height for defeat plaques
TITLE_SCALE      = 3.0     # corridor title billboard height

_RNG_SALT        = 0x5EED  # deterministic per-corridor jitter


# ----------------------------------------------------------------------
# small math helpers (numpy)
# ----------------------------------------------------------------------
def _unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _frame(forward, up_hint=(0.0, 1.0, 0.0)):
    """Orthonormal (right, up, forward) basis from a forward dir.
    Ported in spirit from Fable's _frame; stabilized against the up_hint."""
    f = _unit(forward)
    up_hint = np.asarray(up_hint, dtype=float)
    if abs(np.dot(f, _unit(up_hint))) > 0.97:      # forward ~parallel to up
        up_hint = np.array([0.0, 0.0, 1.0])
    r = _unit(np.cross(up_hint, f))
    u = _unit(np.cross(f, r))
    return r, u, f


def _rotate_dir(forward, up, right, yaw, pitch):
    """Turn a forward vector by yaw (about local up) then pitch (about local right)."""
    f = _unit(forward)
    # yaw about up
    cy, sy = math.cos(yaw), math.sin(yaw)
    f = _unit(f * cy + right * sy)
    r = _unit(np.cross(up, f))
    # pitch about right
    cp, sp = math.cos(pitch), math.sin(pitch)
    f = _unit(f * cp + up * sp)
    u = _unit(np.cross(f, r))
    return f, u, r


# ----------------------------------------------------------------------
# Segment: one straight piece of the bent centerline with a local frame
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
        """N_SIDES polygon ring of vertices at param t in [0,1] along this seg."""
        rad = self.radius if radius is None else radius
        center = self.start + (self.end - self.start) * t
        verts = []
        for k in range(N_SIDES):
            a = 2.0 * math.pi * (k + 0.5) / N_SIDES  # +0.5 -> flat top/bottom
            offset = self.right * (math.cos(a) * rad) + self.up * (math.sin(a) * rad)
            verts.append(center + offset)
        return verts

    def local(self, point):
        """Express a world point in this segment's local (s along, lateral) coords.
        Returns (s, lateral_offset_vector_in_plane)."""
        p = np.asarray(point, dtype=float) - self.start
        axis = self.end - self.start
        L = np.linalg.norm(axis)
        if L < 1e-9:
            return 0.0, p
        s = float(np.dot(p, axis / L))                 # distance along (0..L)
        along = (axis / L) * s
        lateral = p - along
        return s, lateral, L


# ----------------------------------------------------------------------
# CorridorGeometry — the public product
# ----------------------------------------------------------------------
class CorridorGeometry:
    """A built corridor: bent octagonal tube + content hooks.

    Public interface (locked for hub_builder / game_state):
      .entrance_pose()           -> ((x,y,z), (nx,ny,nz))   mouth + outward normal
      .inside(point, margin=0.0) -> bool                    fly-through test
      .seg_bounds                -> list of dicts (see below)  raw per-seg bounds
      .hostage_positions()       -> list of (x,y,z)         cavern hostage anchors
      .get_robots()              -> list[Robot]
      .stations()                -> list of ((x,y,z), yaw)  robot station poses
      .update(dt, ship_position) -> None
      .draw(camera_right, camera_up, texcache) -> None      (enqueues walls)
    """

    def __init__(self, corridor_data, origin=(0, 0, 0), direction=(0, 0, -1)):
        self._data    = corridor_data
        self._origin  = np.asarray(origin, dtype=float)
        self._dir0    = _unit(direction)
        self._palette = palette_mod.Palette(corridor_data.ledger)

        # dominant color = first primary in the ledger
        self._dominant_key = corridor_data.ledger.primaries[0]
        self._dominant_rgb = self._palette.tint(self._dominant_key)

        self._ship_pos = np.asarray(origin, dtype=float)  # cached for sorting/LOD
        self._tube_list = None                            # display list id

        self._build_centerline()
        self._build_stations()
        self._build_robots()
        self._build_cavern_anchors()

    # ---- construction -------------------------------------------------
    def _build_centerline(self):
        robots_n = len(self._data.robots)
        # enough segments to space robots + leave a run-up + a cavern flare
        n_seg = max(6, robots_n * 2 + CAVERN_SEGMENTS + 2)

        rng = np.random.default_rng(
            (hash(self._data.title) ^ _RNG_SALT) & 0xFFFFFFFF
        )

        right, up, forward = _frame(self._dir0)
        pos = self._origin.copy()
        self._segments = []
        self._mouth_pos = pos.copy()
        self._mouth_normal = -forward  # outward = back toward the hub

        for i in range(n_seg):
            # gentle turn: first segment straight-ish so the mouth aligns cleanly
            if i == 0:
                yaw = pitch = 0.0
            else:
                yaw   = math.radians(rng.uniform(MIN_TURN_DEG, MAX_TURN_DEG)) * rng.choice([-1, 1])
                pitch = math.radians(rng.uniform(MIN_TURN_DEG, MAX_TURN_DEG)) * rng.choice([-1, 1])
                forward, up, right = _rotate_dir(forward, up, right, yaw, pitch)

            # cavern flare on the last CAVERN_SEGMENTS
            is_cavern = i >= (n_seg - CAVERN_SEGMENTS)
            radius = CAVERN_RADIUS if is_cavern else TUBE_RADIUS

            start = pos.copy()
            end   = pos + forward * SEGMENT_LENGTH
            self._segments.append(_Segment(start, end, right, up, forward, radius))
            pos = end

        self._far_center = pos.copy()

        # public raw bounds for game_state
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
        """One station per robot, spread along the non-cavern segments."""
        body = self._segments[1:len(self._segments) - CAVERN_SEGMENTS]
        n = len(self._data.robots)
        self._station_poses = []
        if not body or n == 0:
            return
        for j in range(n):
            t = (j + 1) / (n + 1)                       # spread 0..1 exclusive
            seg = body[int(t * (len(body) - 1) + 0.5)]
            center = (seg.start + seg.end) * 0.5
            # yaw so robot faces back down the corridor (toward incoming ship)
            f = -seg.forward
            yaw = math.atan2(f[0], -f[2])               # heading in XZ plane
            self._station_poses.append((tuple(center.tolist()), float(yaw)))

    def _build_robots(self):
        self._robots = []
        for rdata, pose in zip(self._data.robots, self._station_poses):
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
        # a small cluster of hostage anchors on the cavern floor
        for dx in (-3.0, 0.0, 3.0):
            anchor = c + last.right * dx - last.up * (last.radius * 0.5)
            self._hostage_anchors.append(tuple(anchor.tolist()))

    # ---- public interface --------------------------------------------
    def entrance_pose(self):
        """((x,y,z), (nx,ny,nz)) — mouth center + OUTWARD normal (toward hub)."""
        return (tuple(self._mouth_pos.tolist()),
                tuple(_unit(self._mouth_normal).tolist()))

    def stations(self):
        return list(self._station_poses)

    def get_robots(self):
        return list(self._robots)

    def hostage_positions(self):
        return list(self._hostage_anchors)

    def inside(self, point, margin=0.0):
        """True if point is within ANY segment's octagonal slab (+margin).
        Per-segment slab union — works for straight OR bent corridors."""
        p = np.asarray(point, dtype=float)
        for seg in self._segments:
            s, lateral, L = seg.local(p)
            if -margin <= s <= L + margin:
                # octagon ~ inscribed circle of radius*cos(pi/N); use circumradius
                if np.linalg.norm(lateral) <= seg.radius + margin:
                    return True
        return False

    # ---- per-frame ----------------------------------------------------
    def update(self, dt, ship_position):
        self._ship_pos = np.asarray(ship_position, dtype=float)
        for r in self._robots:
            r.update(dt, ship_position)

    def draw(self, camera_right, camera_up, texcache):
        """Enqueue translucent rock walls; draw opaque chevrons/glow; draw
        robots; draw labels/plaques. NOTE: caller must call
        render.flush_walls(ship.pos) after opaque+robots, before billboards."""
        self._draw_tube_walls()        # -> render.queue_wall (translucent)
        self._draw_corner_glow()       # opaque emissive-ish strips
        self._draw_chevrons()          # opaque mouth chevrons
        for r in self._robots:
            r.draw(camera_right, camera_up, texcache)
        # NOTE: app/demo flushes walls HERE (between robots and billboards)
        self._draw_title(camera_right, camera_up, texcache)
        self._draw_plaques(camera_right, camera_up, texcache)

    # ---- drawing internals -------------------------------------------
    def _quads_between(self, ring_a, ring_b):
        """Yield wall quads (4 verts each) between two N_SIDES rings."""
        for k in range(N_SIDES):
            k2 = (k + 1) % N_SIDES
            yield [ring_a[k], ring_a[k2], ring_b[k2], ring_b[k]]

    def _draw_tube_walls(self):
        fill = self._palette.WORLD_WALL_FILL if hasattr(self._palette, "WORLD_WALL_FILL") \
               else palette_mod.WORLD_WALL_FILL
        edge = palette_mod.WORLD_EDGE
        alpha = palette_mod.BACKDROP_BASE_ALPHA
        for i, seg in enumerate(self._segments):
            nxt = self._segments[i + 1] if i + 1 < len(self._segments) else None
            ring_a = seg.ring(0.0)
            # SEAM_OVERLAP: extend this segment's far ring slightly past its end
            # toward the next segment to hide the ELBOW gap (BACK_EXTEND style)
            t_end = 1.0 + (SEAM_OVERLAP / SEGMENT_LENGTH if nxt is not None else 0.0)
            ring_b = seg.ring(t_end)
            for quad in self._quads_between(ring_a, ring_b):
                render.queue_wall(quad, fill, edge, alpha)

    def _draw_corner_glow(self):
        """Thin dominant-color strips running along the 8 octagon edges.
        Opaque-ish accent so the corridor reads chromatically as its color."""
        glow = self._dominant_rgb
        glow_alpha = 0.85
        for seg in self._segments:
            ra = seg.ring(0.0)
            rb = seg.ring(1.0)
            for k in range(N_SIDES):
                # a slim quad along each edge line (k vertex of ring a -> ring b)
                inset = 0.12 * seg.radius
                ea = ra[k]
                eb = rb[k]
                # build a thin ribbon by nudging toward center
                ca = (seg.start + seg.end) * 0.5
                na = _unit(ca - ea) * inset
                strip = [ea, eb, eb + na, ea + na]
                render.queue_wall(strip, glow, glow, glow_alpha)

    def _draw_chevrons(self):
        """Dominant-color chevron stripes around the mouth ring (entry signage)."""
        seg = self._segments[0]
        glow = self._dominant_rgb
        for row in range(CHEVRON_ROWS):
            t0 = 0.04 + row * 0.06
            t1 = t0 + 0.03
            ra = seg.ring(t0, radius=seg.radius * 0.985)
            rb = seg.ring(t1, radius=seg.radius * 0.985)
            a = 1.0 - row * 0.18
            for quad in self._quads_between(ra, rb):
                render.queue_wall(quad, glow, glow, max(0.2, a))

    def _draw_title(self, cr, cu, texcache):
        title = getattr(self._data, "title", "CORRIDOR")
        tex = texcache.get_mathtext(
            r"\mathrm{%s}" % title.replace(" ", r"\ "),
            color=self._dominant_rgb, fontsize=18,
        )
        seg = self._segments[0]
        center = seg.start + seg.forward * (SEGMENT_LENGTH * 0.25) + seg.up * (seg.radius * 0.55)
        render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                              scale=TITLE_SCALE, alpha=0.95)

    def _draw_plaques(self, cr, cu, texcache):
        """Museum effect: where a robot is defeated, a calm plaque appears."""
        for r, (pose, _yaw) in zip(self._robots, self._station_poses):
            if not r.is_defeated():
                continue
            rdata = r._data if hasattr(r, "_data") else None
            text = getattr(rdata, "briefing_hint", "") if rdata else ""
            if not text:
                text = "—"
            tint = self._palette.eye(self._dominant_key) \
                   if False else self._palette.tint(self._dominant_key)
            tex = texcache.get_mathtext(
                r"\mathrm{%s}" % text.replace(" ", r"\ ")[:40],
                color=palette_mod.text_color_on(tint) if hasattr(palette_mod, "text_color_on")
                      else (0.95, 0.96, 0.98),
                fontsize=14,
            )
            center = np.asarray(pose, dtype=float)
            center = center + np.array([0.0, 1.2, 0.0])
            render.draw_billboard(tex, tuple(center.tolist()), cr, cu,
                                  scale=PLAQUE_SCALE, alpha=0.9)


# convenience factory ---------------------------------------------------
def build_corridor(corridor_data, origin=(0, 0, 0), direction=(0, 0, -1)):
    return CorridorGeometry(corridor_data, origin=origin, direction=direction)