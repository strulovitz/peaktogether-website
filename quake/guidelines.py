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
    return [(p[0], p[2]) for p in _route_xyz(fp, current, target)]


def _route_xyz(fp: Floorplan, current: NodeId, target: NodeId) -> list[Vec3]:
    """Route from `current` to `target` as 3D points that ride the walkable
    corridor floor (up ramps, across bridges), sitting +0.02 m above it."""
    from corridor_height import floor_height, height_at_vertex

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

    chain: list[tuple[NodeId, NodeId, Corridor]] = []
    node = target
    while node != current and node in parent:
        prev, corr = parent[node]
        chain.append((prev, node, corr))
        node = prev
    chain.reverse()

    rooms = _rooms_by_id(fp)
    rooms_list = list(fp.rooms)
    lift = 0.02
    pts: list[Vec3] = []

    def _push(x: float, z: float, y: float) -> None:
        p = (x, y + lift, z)
        if not pts or (pts[-1][0] != p[0] or pts[-1][2] != p[2]):
            pts.append(p)

    if current in rooms:
        r0 = rooms[current]
        _push(r0.map_xz[0], r0.map_xz[1], r0.socket_y)

    for prev, nxt, corr in chain:
        path = list(corr.path_xz)
        forward = not (corr.source == nxt and corr.target == prev)
        n = len(path)
        for j in range(n):
            idx = j if forward else (n - 1 - j)
            x, z = float(path[idx][0]), float(path[idx][1])
            y = height_at_vertex(corr, idx, rooms_list)
            _push(x, z, y)
        if nxt in rooms:
            rn = rooms[nxt]
            _push(rn.map_xz[0], rn.map_xz[1], rn.socket_y)

    return pts


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

_GUIDE_PROG = [None]  # cached simple wire program


def _gl_draw_strip(vp_bytes: bytes, points_xyz: list[Vec3],
                   color_rgb: Vec3, mode) -> None:
    """Draw a bright polyline (LINE_STRIP) or barb set (LINES) into the
    currently-bound framebuffer. Bright, no distance-dim, depth-tested against
    the wire (inherits the scene's GL_LESS depth state)."""
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

    if _GUIDE_PROG[0] is None:
        try:
            _GUIDE_PROG[0] = wire_program(ctx)
        except Exception:
            return
    prog = _GUIDE_PROG[0]

    import numpy as np
    pos = np.asarray(points_xyz, dtype=np.float32).reshape(-1, 3)
    col = np.tile(np.asarray(color_rgb, dtype=np.float32), (pos.shape[0], 1))

    try:
        prog['u_mvp'].write(vp_bytes)
    except Exception:
        pass

    vbo_p = ctx.buffer(pos.tobytes())
    vbo_c = ctx.buffer(col.tobytes())
    vao = ctx.vertex_array(
        prog,
        [(vbo_p, '3f', 'in_pos'), (vbo_c, '3f', 'in_color')],
        mode=mode,
    )
    vao.render()
    try:
        vao.release(); vbo_p.release(); vbo_c.release()
    except Exception:
        pass


def draw_guidelines(
    view: ViewMatrix,          # NOTE: app passes vp = proj @ view here
    fp: Floorplan,
    targets: list[NodeId],
    current: NodeId | None = None,
) -> None:
    """Draw Half-Life-style floor guide-lines. Headless-safe."""
    if not HAVE_GL or not targets:
        return
    if not fp.rooms:
        return

    import numpy as np
    import moderngl

    # app hands us the combined view-projection; upload transposed (row-major GL)
    vp = np.asarray(view, dtype=np.float32)
    vp_bytes = np.ascontiguousarray(vp.T, dtype=np.float32).tobytes()

    rooms = _rooms_by_id(fp)
    cur = current if (current is not None and current in rooms) else fp.rooms[0].room_id

    for tid in targets:
        if tid not in rooms:
            continue
        route3d = _route_xyz(fp, cur, tid)
        if len(route3d) < 2:
            continue

        color = _hex_to_rgb01(rooms[tid].map_color)

        _gl_draw_strip(vp_bytes, route3d, color, mode=moderngl.LINE_STRIP)

        # Arrowhead at the tip, on the floor plane at the tip's Y.
        tip = route3d[-1]
        prev = route3d[-2]
        barbs2d = _arrowhead_xz((prev[0], prev[2]), (tip[0], tip[2]), size=0.4)
        y = tip[1]
        barb3d: list[Vec3] = [(x, y, z) for (x, z) in barbs2d]
        _gl_draw_strip(vp_bytes, barb3d, color, mode=moderngl.LINES)
