"""
hub_builder.py — DESCENT QED central ATRIUM + N radiating corridors.

MATHEMATICS-BLIND. This module arranges geometry in space and draws grey
rock walls. It places doorways on a Fibonacci sphere and attaches one
CorridorGeometry per doorway, born already positioned/aimed (Option 1).
It interprets NO math/color meaning. Color comes only from palette.

Public interface (locked for app/game_state):
    build_hub(level_data, atrium_center=(0,0,0)) -> HubGeometry
    HubGeometry.corridors            -> list[CorridorGeometry]
    HubGeometry.door_poses()         -> list[((x,y,z),(nx,ny,nz))]
    HubGeometry.inside(point, margin=0.0) -> bool
    HubGeometry.spawn_pose()         -> ((x,y,z),(yaw,pitch))   # radians
    HubGeometry.update(dt, ship_position) -> None
    HubGeometry.draw_world(cr, cu, texcache) -> None   # QUEUE only; no flush
    HubGeometry.draw_robots(cr, cu, texcache) -> None
    HubGeometry.draw_labels(cr, cu, texcache) -> None
"""

import math
import numpy as np

import render
import palette
from corridor_builder import build_corridor, TUBE_RADIUS


def _door_label_text(title):
    """Turn a verbose corridor TITLE into a short, readable door sign.

    Strips the shared 'The Basel Problem -- ' prefix (redundant on every door)
    and normalizes the ASCII double-hyphen to an en-dash. Pure string cleanup;
    no math meaning is interpreted (PRIME LAW preserved).
    """
    s = title.strip()
    prefix = "The Basel Problem -- "
    if s.startswith(prefix):
        s = s[len(prefix):].strip()
    return s.replace(" -- ", " - ").replace("--", "-")


# ============================================================
# TUNABLES  (DeepSeek tunes via screenshots)
# ============================================================

# Radius of the central hollow chamber. Must comfortably seat N door
# openings of radius ~TUBE_RADIUS (=6) on the shell without the openings
# overlapping. Larger N -> the doors get angularly closer, so a larger
# ATRIUM_RADIUS spreads the door footprints apart on the surface.
ATRIUM_RADIUS = 34.0
# TODO(DeepSeek): tune ATRIUM_RADIUS.
# ACCEPTANCE: at N=12 the 12 door rings on the shell are visibly
#   separated (grey rock between each pair of openings, no two rims
#   touching/overlapping). At N=1 the single door is comfortably framed,
#   not swallowing the whole shell.

# Faceting of the spherical shell. We build a lat/long grid; this is the
# number of latitude bands. Longitude segments = 2 * ATRIUM_FACETS.
# Keep readable & fog-friendly (not too dense, not too coarse).
ATRIUM_FACETS = 10
# TODO(DeepSeek): tune ATRIUM_FACETS.
# ACCEPTANCE: shell reads as a faceted hollow rock dome (clearly curved,
#   facets visible but not noisy); fog reveals it gracefully as you fly.

# Thickness/length of each doorway chevron rim that frames an opening,
# measured radially outward from the shell along the door normal.
DOOR_FRAME_DEPTH = 5.0
# TODO(DeepSeek): tune DOOR_FRAME_DEPTH.
# ACCEPTANCE: each doorway has a visible raised rim/collar you can read
#   as "a tunnel begins here" before you enter; not so deep it occludes
#   the corridor mouth.

# Angular half-size (in shell-surface terms) of the hole we punch for a
# door, as a multiple of the mouth radius. The door opening on the shell
# has world radius DOOR_OPENING_SCALE * TUBE_RADIUS.
DOOR_OPENING_SCALE = 1.10
# TODO(DeepSeek): tune DOOR_OPENING_SCALE.
# ACCEPTANCE: the shell opening is slightly larger than the corridor
#   mouth so the player flies cleanly from atrium into corridor with no
#   wall lip clipping; not so large the shell looks shredded.

# Number of segments around each circular door opening / frame ring.
DOOR_RING_SEGMENTS = 12

GOLDEN = math.pi * (3.0 - math.sqrt(5.0))   # ~2.39996 rad


# ============================================================
# Fibonacci sphere — door OUTWARD directions
# ============================================================

def fibonacci_directions(n):
    """N unit vectors evenly spread over the sphere (door outward normals)."""
    dirs = []
    for i in range(n):
        y = 1.0 - 2.0 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1.0 - y * y))
        th = GOLDEN * i
        dirs.append(np.array([math.cos(th) * r, y, math.sin(th) * r],
                             dtype=np.float64))
    return dirs


# ============================================================
# Small geometry helpers (mathematics-blind: pure space arrangement)
# ============================================================

def _basis_for(normal):
    """Return (right, up) unit vectors spanning the plane perpendicular to
    `normal`. Stable: picks a reference axis least parallel to normal."""
    n = normal / (np.linalg.norm(normal) + 1e-12)
    ref = np.array([0.0, 1.0, 0.0]) if abs(n[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    right = np.cross(ref, n)
    right /= (np.linalg.norm(right) + 1e-12)
    up = np.cross(n, right)
    up /= (np.linalg.norm(up) + 1e-12)
    return right, up


def _ring_points(center, normal, radius, segments):
    """Points of a circle of `radius` centered at `center` in the plane
    perpendicular to `normal`."""
    right, up = _basis_for(normal)
    pts = []
    for k in range(segments):
        a = 2.0 * math.pi * k / segments
        pts.append(center + right * (math.cos(a) * radius)
                          + up * (math.sin(a) * radius))
    return pts


# ============================================================
# HubGeometry
# ============================================================

class HubGeometry:
    def __init__(self, atrium_center, corridors, door_dirs, door_centers, titles):
        self.center = np.asarray(atrium_center, dtype=np.float64)
        self.radius = ATRIUM_RADIUS
        self.corridors = corridors                 # list[CorridorGeometry]
        self._door_dirs = door_dirs                 # list[np.array unit]
        self._door_centers = door_centers           # list[np.array world pos]
        self._titles = titles                       # list[str]
        self._t = 0.0                               # animation clock
        self._shell_quads = self._build_shell()     # static grey rock facets
        self._frame_quads = self._build_frames()    # door chevron rims

    # ---- queries -------------------------------------------------------

    def door_poses(self):
        """list[((x,y,z),(nx,ny,nz))] — door CENTER + OUTWARD normal."""
        return [(tuple(c), tuple(d))
                for c, d in zip(self._door_centers, self._door_dirs)]

    def inside(self, point, margin=0.0):
        """True if point is inside the atrium interior OR inside ANY
        corridor. Mathematics-blind containment for ship clamping."""
        p = np.asarray(point, dtype=np.float64)
        if np.linalg.norm(p - self.center) <= self.radius + margin:
            return True
        for c in self.corridors:
            if c.inside(tuple(p), margin=margin):
                return True
        return False

    def spawn_pose(self):
        """((x,y,z),(yaw,pitch)) in RADIANS. Ship starts at the atrium
        center, facing the FIRST doorway (along door_dirs[0]).

        Orientation convention (matches a forward = -Z look with yaw about
        +Y and pitch about +X): yaw = atan2(dx, -dz), pitch = asin(dy).
        If there are no doors, face -Z (yaw=0, pitch=0).
        """
        pos = tuple(self.center)
        if not self._door_dirs:
            return (pos, (0.0, 0.0))
        d = self._door_dirs[0]
        d = d / (np.linalg.norm(d) + 1e-12)
        yaw = math.atan2(d[0], -d[2])
        pitch = math.asin(max(-1.0, min(1.0, d[1])))
        return (pos, (yaw, pitch))

    # ---- per-frame -----------------------------------------------------

    def update(self, dt, ship_position):
        self._t += dt
        for c in self.corridors:
            c.update(dt, ship_position)

    def draw_world(self, cr, cu, texcache):
        """QUEUE the atrium shell + door frames, then let each corridor
        QUEUE its own walls. NO flush here (canonical frame order: the
        demo/app calls render.flush_walls(ship.pos) exactly once after)."""
        fill = palette.WORLD_WALL_FILL
        edge = palette.WORLD_EDGE
        # RGBA fill -> (rgb, alpha) for queue_wall(quad, fill, edge, alpha)
        fill_rgb = fill[:3]
        fill_a = fill[3] if len(fill) > 3 else palette.BACKDROP_BASE_ALPHA

        for quad in self._shell_quads:
            render.queue_wall(quad, fill_rgb, edge, fill_a)
        for quad in self._frame_quads:
            render.queue_wall(quad, fill_rgb, edge, min(1.0, fill_a + 0.10))

        for c in self.corridors:
            c.draw_world(cr, cu, texcache)

    def draw_robots(self, cr, cu, texcache):
        # Hub has no robots of its own. Delegate to corridors.
        for c in self.corridors:
            c.draw_robots(cr, cu, texcache)

    def draw_labels(self, cr, cu, texcache):
        # Door title billboards (kept OUT of any display list — mathtext).
        for center, normal, title in zip(self._door_centers,
                                          self._door_dirs, self._titles):
            if not title:
                continue
            label = _door_label_text(title)
            tex = render.get_plain_text_tex(label, color=palette.WORLD_EDGE)
            # Place the label just outside the door, on the frame rim.
            lbl_pos = center + normal * (DOOR_FRAME_DEPTH + 2.0)
            render.draw_billboard(tex, tuple(lbl_pos), cr, cu, scale=1.0, alpha=1.0)
        for c in self.corridors:
            c.draw_labels(cr, cu, texcache)

    # ---- shell construction (static grey rock) -------------------------

    def _is_in_doorway(self, surf_point):
        """True if a point on the shell surface lies within an opening.
        We compare angular distance from each door direction against the
        angular radius subtended by the door opening."""
        v = surf_point - self.center
        vn = v / (np.linalg.norm(v) + 1e-12)
        open_r = DOOR_OPENING_SCALE * TUBE_RADIUS
        # angular radius of the opening on a sphere of self.radius
        ang_r = math.asin(min(1.0, open_r / self.radius))
        for d in self._door_dirs:
            cosang = float(np.dot(vn, d))
            cosang = max(-1.0, min(1.0, cosang))
            if math.acos(cosang) < ang_r:
                return True
        return False

    def _build_shell(self):
        """Lat/long faceted hollow sphere. Quads that fall inside any
        doorway opening are OMITTED (we do NOT seal the doorways)."""
        quads = []
        bands = ATRIUM_FACETS
        segs = ATRIUM_FACETS * 2
        R = self.radius
        C = self.center

        def vert(ib, iseg):
            phi = math.pi * ib / bands            # 0..pi  (pole to pole)
            theta = 2.0 * math.pi * iseg / segs   # 0..2pi
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)
            return C + np.array([x, y, z]) * R

        for ib in range(bands):
            for iseg in range(segs):
                a = vert(ib,     iseg)
                b = vert(ib + 1, iseg)
                cc = vert(ib + 1, iseg + 1)
                d = vert(ib,     iseg + 1)
                quad = [a, b, cc, d]
                # Omit this facet if its center sits in a doorway hole.
                fc = (a + b + cc + d) * 0.25
                if self._is_in_doorway(fc):
                    continue
                quads.append([tuple(p) for p in quad])
        return quads

    def _build_frames(self):
        """Chevron/collar rim around each door opening: a short cylinder
        band extruded outward along the door normal from the shell."""
        frames = []
        open_r = DOOR_OPENING_SCALE * TUBE_RADIUS
        for center, normal in zip(self._door_centers, self._door_dirs):
            inner = _ring_points(center, normal, open_r, DOOR_RING_SEGMENTS)
            outer_center = center + normal * DOOR_FRAME_DEPTH
            outer = _ring_points(outer_center, normal, open_r * 0.92,
                                 DOOR_RING_SEGMENTS)
            n = len(inner)
            for k in range(n):
                k2 = (k + 1) % n
                quad = [tuple(inner[k]), tuple(inner[k2]),
                        tuple(outer[k2]), tuple(outer[k])]
                frames.append(quad)
        return frames


# ============================================================
# build_hub
# ============================================================

def build_hub(level_data, atrium_center=(0, 0, 0)):
    """Build the central atrium and attach one corridor per entry.

    level_data: a plain iterable of CorridorData (NO level container
    exists yet — per content_parser, we accept list[CorridorData]).
    Each CorridorData carries .title (used for the door label).

    Attachment = OPTION 1 (build-at-pose): each corridor is built with
    origin=door_center, direction=door_outward, so it is born positioned
    and aimed; no post-hoc transforms.
    """
    corridor_data_list = list(level_data)
    n = len(corridor_data_list)
    center = np.asarray(atrium_center, dtype=np.float64)

    door_dirs = fibonacci_directions(n)
    door_centers = [center + d * ATRIUM_RADIUS for d in door_dirs]
    titles = [getattr(cd, "title", "") for cd in corridor_data_list]

    corridors = []
    for cd, dctr, ddir in zip(corridor_data_list, door_centers, door_dirs):
        # direction points OUTWARD from hub (into the corridor / direction
        # of travel). entrance_pose()'s normal will point back inward.
        corr = build_corridor(cd, origin=tuple(dctr), direction=tuple(ddir))
        corridors.append(corr)

    return HubGeometry(center, corridors, door_dirs, door_centers, titles)