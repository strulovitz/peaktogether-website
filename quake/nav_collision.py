"""nav_collision.py — QUAKE runtime module #8.

PURE geometry: collision + ray queries for corridor (Mode A) and room
(Mode B) navigation. No GL, no window, no IO — fully unit-testable.

Coordinate law:
  floorplan XZ = map plane, Y up.
  Room-local axes parallel to map axes (no rotation).
  Walls: N at z=+D/2 (inward normal -Z), S at z=-D/2 (+Z),
         E at x=+W/2 (-X), W at x=-W/2 (+X), floor y=0.
"""

from __future__ import annotations

import math

from contracts import (Floorplan, FloorRoom, Corridor, RoomRuntime, DoorRT,
                       PanelPairRT, PanelPlacementRT, EnemyRT, CeilingEqRT,
                       Vec2, Vec3, NodeId, PairId, NavQuery, Ray, PanelHit)

# ----------------------------------------------------------------------------
# PINNED CONSTANTS
# ----------------------------------------------------------------------------
DOOR_TRIGGER_DEPTH_M = 0.25    # how close to the wall plane counts as "at the door"
CORRIDOR_SLIDE_SOFTNESS = 0.5  # rail-assist nudge factor (0=hard boundary, 1=full slide)

_EPS = 1e-9

_CORRIDOR_HEIGHT_M = 3.0
_RAMP_FRACTION = 0.30


# ----------------------------------------------------------------------------
# Small vector helpers (local, pure)
# ----------------------------------------------------------------------------
def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot3(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _len3(a: Vec3) -> float:
    return math.sqrt(_dot3(a, a))


def _norm3(a: Vec3) -> Vec3:
    n = _len3(a)
    if n < _EPS:
        return (0.0, 0.0, 0.0)
    return (a[0] / n, a[1] / n, a[2] / n)


# ----------------------------------------------------------------------------
# PURE HELPER: ray_rect_hit
# ----------------------------------------------------------------------------
def ray_rect_hit(
    ray: Ray, center: Vec3, width: float, height: float, yaw_rad: float
) -> float | None:
    """Intersect ray with a rectangular quad at `center`, size width×height,
    facing direction yaw_rad (the plane normal points along yaw_rad in the
    XZ plane). Return distance along ray to the hit, or None.

    The quad's normal is the horizontal direction:
        n = (cos(yaw), 0, sin(yaw))
    Its "horizontal" in-plane axis (spanning width) is perpendicular to n in
    the XZ plane:
        u = (-sin(yaw), 0, cos(yaw))
    Its vertical in-plane axis (spanning height) is world up:
        v = (0, 1, 0)
    """
    n = (math.cos(yaw_rad), 0.0, math.sin(yaw_rad))
    u = (-math.sin(yaw_rad), 0.0, math.cos(yaw_rad))
    v = (0.0, 1.0, 0.0)

    o = ray.origin
    d = ray.direction
    denom = _dot3(n, d)
    if abs(denom) < _EPS:
        return None  # ray parallel to plane

    t = _dot3(n, _sub(center, o)) / denom
    if t < 0.0:
        return None  # behind ray origin

    hit = (o[0] + d[0] * t, o[1] + d[1] * t, o[2] + d[2] * t)
    rel = _sub(hit, center)

    pu = _dot3(rel, u)
    pv = _dot3(rel, v)

    if abs(pu) <= width / 2.0 + _EPS and abs(pv) <= height / 2.0 + _EPS:
        return t
    return None


# ----------------------------------------------------------------------------
# PURE HELPER: point_in_door
# ----------------------------------------------------------------------------
def point_in_door(point: Vec3, door: DoorRT) -> bool:
    """True if `point` lies within the door opening on door.wall's plane.

    Opening centered at door.center_xyz, spanning door.width_m horizontally
    (along the wall) and door.height_m vertically, within DOOR_TRIGGER_DEPTH_M
    of the wall plane.
    """
    c = door.center_xyz
    px, py, pz = point
    cx, cy, cz = c

    half_w = door.width_m / 2.0
    # Vertical span: door rises from floor (cy - height/2 .. cy + height/2),
    # but accept anything from 0..height to be tolerant of socket_y conventions.
    # Use centered interval around door center for symmetry with width.
    half_h = door.height_m / 2.0

    wall = door.wall
    if wall in ("N", "S"):
        # wall plane is constant Z; opening runs along X (width), Y (height)
        depth = abs(pz - cz)
        along = abs(px - cx)
    elif wall in ("E", "W"):
        # wall plane is constant X; opening runs along Z (width), Y (height)
        depth = abs(px - cx)
        along = abs(pz - cz)
    else:
        return False

    if depth > DOOR_TRIGGER_DEPTH_M + _EPS:
        return False
    if along > half_w + _EPS:
        return False
    # vertical: accept within [cy-half_h, cy+half_h] OR within [0, height]
    if py < min(0.0, cy - half_h) - _EPS:
        return False
    if py > max(door.height_m, cy + half_h) + _EPS:
        return False
    return True


# ----------------------------------------------------------------------------
# CORRIDOR NAV
# ----------------------------------------------------------------------------
def _closest_on_segment_xz(
    p: Vec2, a: Vec2, b: Vec2
) -> tuple[Vec2, float]:
    """Return (closest_point_xz, t) where t in [0,1] is the parameter along a->b."""
    ax, az = a
    bx, bz = b
    px, pz = p
    dx, dz = bx - ax, bz - az
    seg_len2 = dx * dx + dz * dz
    if seg_len2 < _EPS:
        return (a, 0.0)
    t = ((px - ax) * dx + (pz - az) * dz) / seg_len2
    t = max(0.0, min(1.0, t))
    cx = ax + dx * t
    cz = az + dz * t
    return ((cx, cz), t)


def _corridor_vertex_heights_nav(cor: Corridor) -> list:
    """Y at each path_xz vertex — identical formula to render_wire._corridor_vertex_heights."""
    pts = cor.path_xz
    seg_lens = []
    for n in range(len(pts) - 1):
        dx = pts[n + 1][0] - pts[n][0]
        dz = pts[n + 1][1] - pts[n][1]
        seg_lens.append(math.hypot(dx, dz))
    total = sum(seg_lens)
    cum = [0.0]
    for sl in seg_lens:
        cum.append(cum[-1] + sl)
    ys = []
    cy = cor.cruise_y
    for i in range(len(pts)):
        u = (cum[i] / total) if total > _EPS else 0.0
        if u < 0.0:
            u = 0.0
        if u > 1.0:
            u = 1.0
        ramp = max(0.0, min(u / _RAMP_FRACTION, (1.0 - u) / _RAMP_FRACTION, 1.0))
        ys.append(cy * ramp)
    return ys


class _CorridorNav:
    def __init__(self, fp: Floorplan):
        self._corridors = list(fp.corridors)
        self._rooms = list(fp.rooms)
        self._segments = []
        for cor in self._corridors:
            pts = cor.path_xz
            if len(pts) < 2:
                continue
            seg_lens = []
            for n in range(len(pts) - 1):
                dx = pts[n + 1][0] - pts[n][0]
                dz = pts[n + 1][1] - pts[n][1]
                seg_lens.append(math.hypot(dx, dz))
            total = sum(seg_lens)
            cum = [0.0]
            for sl in seg_lens:
                cum.append(cum[-1] + sl)
            half_w = cor.width_m / 2.0
            for n in range(len(pts) - 1):
                ax, az = pts[n][0], pts[n][1]
                bx, bz = pts[n + 1][0], pts[n + 1][1]
                dx, dz = bx - ax, bz - az
                seg_len = math.hypot(dx, dz)
                if seg_len < _EPS:
                    continue
                fwd = (dx / seg_len, dz / seg_len)
                right = (-fwd[1], fwd[0])
                self._segments.append((
                    (ax, az), (bx, bz),
                    cor, cum[n], cum[n + 1], total,
                    right, half_w,
                ))

    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3:
        tx = start[0] + delta[0]
        ty = start[1] + delta[1]
        tz = start[2] + delta[2]

        if not self._segments:
            return (tx, ty, tz)

        best = None
        best_dist = float("inf")
        for seg in self._segments:
            s_xz, e_xz, cor, arc_s, arc_e, total, right, half_w = seg
            cpt, t = _closest_on_segment_xz((tx, tz), s_xz, e_xz)
            dist = math.hypot(tx - cpt[0], tz - cpt[1])
            if dist < best_dist:
                best_dist = dist
                best = (seg, cpt, t)

        seg, cpt, t = best
        s_xz, e_xz, cor, arc_s, arc_e, total, right, half_w = seg

        arc = arc_s + (arc_e - arc_s) * t
        u = (arc / total) if total > _EPS else 0.0
        if u < 0.0:
            u = 0.0
        if u > 1.0:
            u = 1.0
        ramp = max(0.0, min(u / _RAMP_FRACTION, (1.0 - u) / _RAMP_FRACTION, 1.0))
        floor_y = float(cor.cruise_y) * ramp

        lateral = (tx - cpt[0]) * right[0] + (tz - cpt[1]) * right[1]
        if lateral > half_w:
            lateral = half_w
        elif lateral < -half_w:
            lateral = -half_w
        fx = cpt[0] + lateral * right[0]
        fz = cpt[1] + lateral * right[1]

        cy = ty
        if cy < floor_y:
            cy = floor_y
        elif cy > floor_y + _CORRIDOR_HEIGHT_M:
            cy = floor_y + _CORRIDOR_HEIGHT_M

        return (fx, cy, fz)

    def nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None:
        return None

    def door_at(self, point: Vec3) -> str | None:
        return None


def build_corridor_nav(fp: Floorplan) -> NavQuery:
    """Build a NavQuery for corridor walkable space (Mode A)."""
    return _CorridorNav(fp)


# ----------------------------------------------------------------------------
# ROOM NAV
# ----------------------------------------------------------------------------
class _RoomNav:
    def __init__(self, room: RoomRuntime):
        self._room = room
        w, h, d = room.dimensions_m
        self._w = w
        self._h = h
        self._d = d
        self._doors = list(room.doors)
        self._pairs = list(room.panel_pairs)

    # --- motion ---------------------------------------------------------
    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3:
        w2 = self._w / 2.0
        d2 = self._d / 2.0

        sx, sy, sz = start
        tx = sx + delta[0]
        ty = sy + delta[1]
        tz = sz + delta[2]

        # Y clamp to box (floor..ceiling).
        if ty < 0.0:
            ty = 0.0
        if ty > self._h:
            ty = self._h

        # X axis: walls E (x=+w2) and W (x=-w2)
        if tx > w2:
            if not self._crosses_door_x(+w2, sy, sz, tz, ty):
                tx = w2
        elif tx < -w2:
            if not self._crosses_door_x(-w2, sy, sz, tz, ty):
                tx = -w2

        # Z axis: walls N (z=+d2) and S (z=-d2)
        if tz > d2:
            if not self._crosses_door_z(+d2, sy, sx, tx, ty):
                tz = d2
        elif tz < -d2:
            if not self._crosses_door_z(-d2, sy, sx, tx, ty):
                tz = -d2

        return (tx, ty, tz)

    def _crosses_door_x(self, plane_x: float, py: float,
                        pz_start: float, pz_end: float, ty: float) -> bool:
        """Is there a passable door opening on the X-plane (E/W wall) at the
        crossing location?"""
        wall = "E" if plane_x > 0 else "W"
        z = pz_end  # use destination z (and start z midpoint tolerant)
        for door in self._doors:
            if door.wall != wall:
                continue
            cz = door.center_xyz[2]
            if abs(z - cz) <= door.width_m / 2.0 + _EPS or \
               abs(pz_start - cz) <= door.width_m / 2.0 + _EPS:
                if 0.0 <= ty <= door.height_m + _EPS:
                    return True
        return False

    def _crosses_door_z(self, plane_z: float, py: float,
                        px_start: float, px_end: float, ty: float) -> bool:
        """Passable door opening on the Z-plane (N/S wall)?"""
        wall = "N" if plane_z > 0 else "S"
        x = px_end
        for door in self._doors:
            if door.wall != wall:
                continue
            cx = door.center_xyz[0]
            if abs(x - cx) <= door.width_m / 2.0 + _EPS or \
               abs(px_start - cx) <= door.width_m / 2.0 + _EPS:
                if 0.0 <= ty <= door.height_m + _EPS:
                    return True
        return False

    # --- panels ---------------------------------------------------------
    def nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None:
        best: PanelHit | None = None

        for pair in self._pairs:
            # Drawing panel
            dp = pair.drawing_placement
            d_dist = ray_rect_hit(ray, dp.center_xyz, dp.width_m,
                                  dp.height_m, dp.yaw_rad)
            # Text panel
            tp = pair.text_placement
            t_dist = ray_rect_hit(ray, tp.center_xyz, tp.width_m,
                                  tp.height_m, tp.yaw_rad)

            candidates = []
            if d_dist is not None and d_dist <= max_dist + _EPS:
                candidates.append((d_dist, True,
                                   pair.drawing_on_asset, pair.drawing_off_asset))
            if t_dist is not None and t_dist <= max_dist + _EPS:
                candidates.append((t_dist, False,
                                   pair.text_on_asset, pair.text_off_asset))

            for dist, is_drawing, on_asset, off_asset in candidates:
                if best is None or dist < best.distance:
                    best = PanelHit(
                        asset_on_id=on_asset,
                        asset_off_id=off_asset,
                        pair_id=pair.pair_id,
                        is_drawing=is_drawing,
                        distance=dist,
                    )
        return best

    # --- door_at --------------------------------------------------------
    def door_at(self, point: Vec3) -> str | None:
        for door in self._doors:
            if point_in_door(point, door):
                return door.edge_id
        return None


def build_room_nav(room: RoomRuntime) -> NavQuery:
    """Build a NavQuery for a room interior (Mode B)."""
    return _RoomNav(room)
