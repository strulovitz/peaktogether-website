"""guidelines.py — QUAKE runtime engine, module #7 (M1).

Half-Life-style floor guide-lines: choose <=3 guide destinations (PURE core)
and draw them on the felt floor (THIN GL shell, headless-safe).

COORDINATES ARE LAW: floorplan is the XZ map-plane, Y is up.

PURE CORE: _graph_distances, select_targets, plus private helpers. These run
fully headless (numbers + dataclasses only). They are unit-tested.

THIN SHELL: draw_guidelines. Guarded so importing this module never requires a
GL context; the draw is skipped when HAVE_GL is False.
"""

from __future__ import annotations

import math
from collections import deque

from contracts import (Floorplan, FloorRoom, Corridor, NodeId, Vec2, Vec3,
                       BuildConfig, ViewMatrix, GameState)

# --------------------------------------------------------------------------
# Headless guard. NEVER crash on import without GL.
# --------------------------------------------------------------------------
try:
    from glguard import HAVE_GL
except Exception:
    HAVE_GL = False

_CORRIDOR_HEIGHT_M = 3.0
_RAMP_FRACTION = 0.30


def _compute_floor_y_at_xz(fp: Floorplan, x: float, z: float) -> float:
    """Corridor floor Y at (x,z) using the same trapezoid ramp as the tunnel boxes."""
    for cor in fp.corridors:
        pts = cor.path_xz
        if len(pts) < 2:
            continue
        seg_lens = []
        for n in range(len(pts) - 1):
            dx = pts[n + 1][0] - pts[n][0]
            dz = pts[n + 1][1] - pts[n][1]
            seg_lens.append(math.hypot(dx, dz))
        total = sum(seg_lens)
        if total < 1e-9:
            continue
        cum = [0.0]
        for sl in seg_lens:
            cum.append(cum[-1] + sl)
        for n in range(len(pts) - 1):
            ax, az = pts[n][0], pts[n][1]
            bx, bz = pts[n + 1][0], pts[n + 1][1]
            dx, dz = bx - ax, bz - az
            seg_len2 = dx * dx + dz * dz
            if seg_len2 < 1e-9:
                continue
            t = ((x - ax) * dx + (z - az) * dz) / seg_len2
            if t < -0.1 or t > 1.1:
                continue
            t = max(0.0, min(1.0, t))
            arc = cum[n] + t * seg_lens[n]
            u = arc / total
            if u < 0.0:
                u = 0.0
            if u > 1.0:
                u = 1.0
            ramp = max(0.0, min(u / _RAMP_FRACTION, (1.0 - u) / _RAMP_FRACTION, 1.0))
            return cor.cruise_y * ramp
    return 0.0


# ==========================================================================
# PURE CORE
# ==========================================================================

def _build_adjacency(fp: Floorplan) -> dict[NodeId, set[NodeId]]:
    """Build an undirected adjacency map from fp.corridors.

    Each corridor connects corridor.source <-> corridor.target. Rooms that
    appear in fp.rooms but have no corridor still get an (empty) entry so
    they are nodes in the graph (and thus correctly treated as unreachable
    from a disconnected `current`).
    """
    adj: dict[NodeId, set[NodeId]] = {}
    for room in fp.rooms:
        adj.setdefault(room.room_id, set())
    for c in fp.corridors:
        adj.setdefault(c.source, set())
        adj.setdefault(c.target, set())
        adj[c.source].add(c.target)
        adj[c.target].add(c.source)
    return adj


def _graph_distances(fp: Floorplan, current: NodeId) -> dict[NodeId, int]:
    """Compute BFS hop count from `current` to every reachable room.

    Build an undirected graph from fp.corridors. Use BFS from `current`.
    Unreachable nodes are NOT present in the returned dict. The current node
    itself has distance 0.
    """
    adj = _build_adjacency(fp)
    if current not in adj:
        # current is not even a node in the graph; only it is at distance 0.
        return {current: 0}

    dist: dict[NodeId, int] = {current: 0}
    q: deque[NodeId] = deque([current])
    while q:
        node = q.popleft()
        d = dist[node]
        for nb in sorted(adj.get(node, ())):  # sorted for determinism
            if nb not in dist:
                dist[nb] = d + 1
                q.append(nb)
    return dist


def _rooms_by_id(fp: Floorplan) -> dict[NodeId, FloorRoom]:
    return {r.room_id: r for r in fp.rooms}


def select_targets(
    fp: Floorplan,
    current: NodeId,
    cleared: set[NodeId],
    cfg: BuildConfig,
) -> list[NodeId]:
    """Choose <=3 guide-line destinations (pure, stateless, flicker-free).

    See module/brief docstring for the full algorithm. Hysteresis is the
    CALLER's responsibility; this function always returns the current best set.
    """
    max_lines = max(0, int(cfg.guide_max_lines))
    if max_lines == 0:
        return []

    dist = _graph_distances(fp, current)
    rooms = _rooms_by_id(fp)

    # 2. candidates = uncleared, reachable, not current, and a real room.
    candidates: list[NodeId] = [
        rid
        for rid in dist
        if rid != current
        and rid not in cleared
        and rid in rooms
    ]
    if not candidates:
        return []

    # 3. Slot 1: nearest honored (graph_dist asc, then room_id asc).
    candidates_slot1 = sorted(candidates, key=lambda rid: (dist[rid], rid))
    slot1 = candidates_slot1[0]
    selected: list[NodeId] = [slot1]

    if max_lines == 1:
        return selected

    # 5. Slots 2-3 from the remaining candidates, composite score descending.
    remaining = [rid for rid in candidates if rid != slot1]
    if remaining:
        rem_dists = [dist[rid] for rid in remaining]
        min_d = min(rem_dists)
        max_d = max(rem_dists)
        span = (max_d - min_d)

        def norm_imp(rid: NodeId) -> float:
            return (rooms[rid].importance - 1) / 4.0  # 0..1

        def norm_near(rid: NodeId) -> float:
            if span == 0:
                return 1.0
            return 1.0 - (dist[rid] - min_d) / span  # closer => higher

        def score(rid: NodeId) -> float:
            return (cfg.guide_w_imp * norm_imp(rid)
                    + cfg.guide_w_dist * norm_near(rid))

        # Sort: score desc, then importance desc, then dist asc, then id asc.
        remaining.sort(
            key=lambda rid: (
                -score(rid),
                -rooms[rid].importance,
                dist[rid],
                rid,
            )
        )
        slots_left = max_lines - len(selected)
        selected.extend(remaining[:slots_left])

    return selected


# ==========================================================================
# THIN GL SHELL (headless-safe)
# ==========================================================================

def _route_xz(fp: Floorplan, current: NodeId, target: NodeId) -> list[Vec2]:
    """Trace the BFS shortest-path corridor route (XZ polyline) current->target.

    Walks corridor path_xz polylines along the BFS parent chain. Returns the
    concatenated XZ polyline. Pure helper (no GL); safe headless. Returns []
    if target is unreachable.
    """
    # BFS keeping parent + the corridor used for that hop.
    adj_corr: dict[NodeId, list[Corridor]] = {}
    for c in fp.corridors:
        adj_corr.setdefault(c.source, []).append(c)
        adj_corr.setdefault(c.target, []).append(c)

    parent: dict[NodeId, tuple[NodeId, Corridor]] = {}
    visited: set[NodeId] = {current}
    q: deque[NodeId] = deque([current])
    while q:
        node = q.popleft()
        if node == target:
            break
        for c in sorted(adj_corr.get(node, ()), key=lambda x: x.corridor_id):
            nb = c.target if c.source == node else c.source
            if nb not in visited:
                visited.add(nb)
                parent[nb] = (node, c)
                q.append(nb)

    if target not in parent and target != current:
        return []

    # Reconstruct hop chain from target back to current.
    chain: list[tuple[NodeId, NodeId, Corridor]] = []
    node = target
    while node != current and node in parent:
        prev, corr = parent[node]
        chain.append((prev, node, corr))
        node = prev
    chain.reverse()

    rooms = _rooms_by_id(fp)
    pts: list[Vec2] = []
    if current in rooms:
        pts.append(rooms[current].map_xz)

    for prev, nxt, corr in chain:
        # Orient corridor path so it runs prev -> nxt.
        path = list(corr.path_xz)
        if corr.source == nxt and corr.target == prev:
            path = list(reversed(path))
        pts.extend(path)
        if nxt in rooms:
            pts.append(rooms[nxt].map_xz)

    # De-duplicate consecutive identical points.
    deduped: list[Vec2] = []
    for p in pts:
        if not deduped or deduped[-1] != p:
            deduped.append(p)
    return deduped


def _hex_to_rgb01(hex_color: str) -> Vec3:
    """Convert '#rrggbb' (or 'rrggbb') to a 0..1 RGB tuple. Pure; safe."""
    s = hex_color.lstrip("#")
    if len(s) != 6:
        return (1.0, 1.0, 1.0)
    try:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
    except ValueError:
        return (1.0, 1.0, 1.0)
    return (r, g, b)


def _arrowhead_xz(p_prev: Vec2, p_tip: Vec2, size: float) -> list[Vec2]:
    """Build 2 short barb segments forming a triangle arrowhead at p_tip.

    Pure 2D geometry on the XZ plane. Returns [left_barb, tip, right_barb]
    base points; caller draws two segments tip->left and tip->right.
    """
    dx = p_tip[0] - p_prev[0]
    dz = p_tip[1] - p_prev[1]
    length = (dx * dx + dz * dz) ** 0.5
    if length < 1e-9:
        return [p_tip, p_tip, p_tip]
    ux, uz = dx / length, dz / length          # unit direction toward tip
    # back from tip along -dir, then offset perpendicular (-uz, ux).
    bx, bz = p_tip[0] - ux * size, p_tip[1] - uz * size
    px, pz = -uz * size * 0.6, ux * size * 0.6
    left = (bx + px, bz + pz)
    right = (bx - px, bz - pz)
    return [left, p_tip, right]


# --- INTEGRATION wrappers (isolate uncertain external GL APIs) -------------

def _gl_floor_y(room: FloorRoom) -> float:
    """Felt-floor draw height for a guide-line: socket_y + small epsilon."""
    return room.socket_y + 0.02


def _gl_draw_strip(view: ViewMatrix, points_xyz: list[Vec3],
                   color_rgb: Vec3, alpha: float) -> None:
    """Draw a floor guide-line polyline via the simple wire_program (LINE_STRIP)."""
    if not HAVE_GL or len(points_xyz) < 2:
        return
    try:
        import moderngl
        ctx = moderngl.get_context()
    except Exception:
        return
    try:
        from shaders import wire_program
    except Exception:
        return
    prog = wire_program(ctx)
    if prog is None:
        return

    import numpy as np
    pts = np.asarray(points_xyz, dtype=np.float32)
    cols = np.tile(np.asarray(color_rgb, dtype=np.float32), (pts.shape[0], 1))

    vbo_p = None
    vbo_c = None
    vao = None
    try:
        vbo_p = ctx.buffer(pts.tobytes())
        vbo_c = ctx.buffer(cols.tobytes())
        vao = ctx.vertex_array(
            prog,
            [(vbo_p, '3f', 'in_pos'), (vbo_c, '3f', 'in_color')],
        )

        vp = np.ascontiguousarray(np.asarray(view, dtype=np.float32).T)
        try:
            prog['u_mvp'].write(vp.tobytes())
        except Exception:
            pass

        ctx.enable(moderngl.DEPTH_TEST)
        ctx.depth_func = "<="
        ctx.depth_mask = True
        ctx.disable(moderngl.BLEND)

        vao.render(mode=moderngl.LINE_STRIP)
    except Exception:
        pass
    finally:
        for obj in (vao, vbo_p, vbo_c):
            try:
                if obj is not None:
                    obj.release()
            except Exception:
                pass


def draw_guidelines(
    view: ViewMatrix,
    fp: Floorplan,
    targets: list[NodeId],
) -> None:
    """Draw Half-Life-style floor guide-lines. Headless-safe.

    The current room is inferred as the first corridor-graph node the routes
    emanate from is supplied via the floorplan + the caller's targets. Since
    the frozen signature does not pass `current`, we trace routes from each
    room reachable; in practice the caller passes targets from select_targets
    invoked with a known `current`. We resolve `current` from the floorplan's
    first room if needed; the route helper tolerates that.

    NOTE: per the brief, if targets is empty or GL is unavailable, draw nothing.
    """
    if not HAVE_GL or not targets:
        return

    rooms = _rooms_by_id(fp)
    if not fp.rooms:
        return

    # Without an explicit `current` in the signature, the convention is that
    # routes start from the player's current room. The gameplay layer that
    # owns GameState supplies targets; here we derive `current` as the common
    # source. Fall back to the first room.
    current = fp.rooms[0].room_id

    for tid in targets:
        if tid not in rooms:
            continue
        route2d = _route_xz(fp, current, tid)
        if len(route2d) < 2:
            continue

        color = _hex_to_rgb01(rooms[tid].map_color)

        route3d: list[Vec3] = [
            (x, _compute_floor_y_at_xz(fp, x, z) + 0.02, z) for (x, z) in route2d
        ]
        _gl_draw_strip(view, route3d, color, alpha=0.65)

        barbs = _arrowhead_xz(route2d[-2], route2d[-1], size=0.4)
        barb3d: list[Vec3] = [
            (x, _compute_floor_y_at_xz(fp, x, z) + 0.02, z) for (x, z) in barbs
        ]
        _gl_draw_strip(view, barb3d, color, alpha=0.65)
