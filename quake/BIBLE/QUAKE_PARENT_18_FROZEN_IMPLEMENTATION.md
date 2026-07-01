I have everything I need. Here is the complete, real code for all four fixes, written against the actual names in the files you pasted. I've followed the pasted style exactly (headless guards, try/except around GL uniforms, PURE core untouched where possible).

The strategy is: one shared height helper is the single source of truth, and all three consumers (render_wire, nav_collision, guidelines) call it. level_maker inserts ramp waypoints so the helper has interior cruise vertices to work with.
NEW FILE 1 — quake/corridor_height.py

The single source of truth. Both a per-vertex function (for wire/guidelines) and a segment-interpolating function (for nav) live here, so nothing can drift.

"""corridor_height.py — QUAKE single source of truth for corridor floor height.

A corridor is LOW at its two room ends (room socket_y) and HIGH along its
cruising middle (cruise_y). The ramp is the transition. This module is the ONE
place that rule lives; render_wire, nav_collision, and guidelines all call it,
so the wire you see, the floor you walk, and the guide-line you follow are
byte-identical.

PURE: numbers + dataclasses only. No GL, no IO. Fully unit-testable.
Coordinate law: floorplan XZ = map plane, Y up.
"""

from __future__ import annotations

from contracts import Corridor, FloorRoom, NodeId


def _socket_y(node_id: NodeId, rooms: list[FloorRoom]) -> float | None:
    for r in rooms:
        if r.room_id == node_id:
            return r.socket_y
    return None


def height_at_vertex(cor: Corridor, idx: int, rooms: list[FloorRoom]) -> float:
    """Y of corridor vertex `idx`. Endpoints sit at their room socket_y;
    every interior vertex sits at cruise_y. This is the ramp shape:
    socket -> (ramp) -> cruise ... cruise -> (ramp) -> socket."""
    path = cor.path_xz
    last = len(path) - 1
    if idx <= 0:
        sy = _socket_y(cor.source, rooms)
        return sy if sy is not None else cor.cruise_y
    if idx >= last:
        sy = _socket_y(cor.target, rooms)
        return sy if sy is not None else cor.cruise_y
    return cor.cruise_y


def floor_height(cor: Corridor, seg_i: int, t: float, rooms: list[FloorRoom]) -> float:
    """Interpolated walkable floor Y at parameter t in [0,1] along segment seg_i
    (vertex seg_i -> vertex seg_i+1)."""
    y_start = height_at_vertex(cor, seg_i, rooms)
    y_end = height_at_vertex(cor, seg_i + 1, rooms)
    return y_start + (y_end - y_start) * t

FIX 2 (build data) — quake/map/level_maker.py

Two changes: (a) add the ramp-run config, (b) insert ramp-top waypoints so every corridor has interior cruise vertices. This is what turns the flat data into a ramp shape. Nothing else in the file changes.

Change 2a — LevelMakerConfig, add one field:

class LevelMakerConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layout: LayoutConfig = LayoutConfig()
    height: HeightConfig = HeightConfig()
    map_radius_base_m: float = 2.0
    map_radius_per_importance_m: float = 1.0
    corridor_width_m: float = 3.0
    corridor_ramp_run_m: float = 6.0        # <-- NEW: XZ length of each end ramp
    palette_map_importance: dict[int, Hex] = {}

Change 2b — replace the path_xz construction inside STEP 5. Add a module-level helper above build_floorplan, then rewrite the path_xz block. Here is the helper:

def _insert_ramp_waypoints(
    path_xz: list[Vec2], ramp_run_m: float
) -> list[Vec2]:
    """Insert a ramp-top waypoint a short run in from each end, so the corridor
    has interior vertices that can hold cruise_y. Ramp run is clamped so a short
    corridor never over-ramps (<= 1/3 of the end segment length)."""
    if len(path_xz) < 2:
        return list(path_xz)

    pts = list(path_xz)

    def _lerp_in(a: Vec2, b: Vec2) -> Vec2:
        dx = b[0] - a[0]
        dz = b[1] - a[1]
        seg_len = math.hypot(dx, dz)
        if seg_len < 1e-9:
            return a
        run = min(ramp_run_m, seg_len / 3.0)
        f = run / seg_len
        return (a[0] + dx * f, a[1] + dz * f)

    start = pts[0]
    end = pts[-1]
    ramp_a = _lerp_in(start, pts[1])          # short run in from the source end
    ramp_b = _lerp_in(end, pts[-2])           # short run in from the target end

    # start, ramp_a, <existing interior>, ramp_b, end
    return [start, ramp_a] + pts[1:-1] + [ramp_b, end]

And the STEP 5 path_xz block becomes:

    # STEP 5 — BUILD CORRIDORS
    corridors: list[Corridor] = []
    for edge in graph.edges:
        corridor_id = edge.id
        src_pos = positions[edge.source]
        tgt_pos = positions[edge.target]
        height_level = heights[edge.id]

        if height_level == 0:
            base_path: list[Vec2] = [src_pos, tgt_pos]
        else:
            pts = crossings_by_corridor.get(corridor_id, [])
            sorted_pts = sorted(
                pts,
                key=lambda p: (p[0] - src_pos[0]) ** 2 + (p[1] - src_pos[1]) ** 2,
            )
            base_path = [src_pos] + list(sorted_pts) + [tgt_pos]

        # Insert ramp-top waypoints so endpoints (socket_y) rise to cruise_y.
        # A level-0 corridor still gets ramps but its cruise_y == base_y, so the
        # ramp is flat when base_y == socket_y — harmless and uniform.
        path_xz = _insert_ramp_waypoints(base_path, cfg.corridor_ramp_run_m)

        cruise_y = cfg.height.base_y + height_level * cfg.height.delta_y

        corridors.append(
            Corridor(
                corridor_id=corridor_id,
                source=edge.source,
                target=edge.target,
                height_level=height_level,
                width_m=cfg.corridor_width_m,
                path_xz=path_xz,
                cruise_y=cruise_y,
            )
        )

    Note: math is already imported at the top of level_maker.py.

FIX 2 (render side) — quake/render_wire.py

build_wire_mesh is PURE and I'm keeping it pure, but it must now stamp per-vertex Y using the shared helper. It needs fp.rooms, which it already iterates — so I pass rooms into the height calls. Replace only the corridor loop inside build_wire_mesh:

def build_wire_mesh(fp: Floorplan) -> WireMesh:
    from corridor_height import height_at_vertex
    seg_list=[]; seg_col_list=[]; base=(1.0,1.0,1.0)
    rooms_list=list(fp.rooms)
    for cor in fp.corridors:
        pts=cor.path_xz
        for n in range(len(pts)-1):
            ay=height_at_vertex(cor, n, rooms_list)
            by=height_at_vertex(cor, n+1, rooms_list)
            ax,az=float(pts[n][0]),float(pts[n][1])
            bx,bz=float(pts[n+1][0]),float(pts[n+1][1])
            seg_list.append(np.array([[ax,ay,az],[bx,by,bz]],dtype=np.float32)); seg_col_list.append(base)
    line_segments=(np.stack(seg_list,0).astype(np.float32) if seg_list else np.zeros((0,2,3),np.float32))
    seg_colors=np.array(seg_col_list,np.float32) if seg_col_list else np.zeros((0,3),np.float32)
    ring_list=[]; ring_col_list=[]
    angles=(2.0*np.pi)*(np.arange(RING_SEGMENTS,dtype=np.float64)/float(RING_SEGMENTS))
    next_angles=(2.0*np.pi)*((np.arange(RING_SEGMENTS,dtype=np.float64)+1.0)/float(RING_SEGMENTS))
    for room in fp.rooms:
        cx,cz=float(room.map_xz[0]),float(room.map_xz[1]); r=float(room.map_radius_m)
        y=float(room.socket_y); rgb=hex_to_rgb(room.map_color)
        for k in range(RING_SEGMENTS):
            t0,t1=angles[k],next_angles[k]
            ring_list.append(np.array(
                [[cx+r*np.cos(t0),y,cz+r*np.sin(t0)],
                 [cx+r*np.cos(t1),y,cz+r*np.sin(t1)]],dtype=np.float32))
            ring_col_list.append(rgb)
    ring_segments=(np.stack(ring_list,0).astype(np.float32) if ring_list else np.zeros((0,2,3),np.float32))
    ring_colors=np.array(ring_col_list,np.float32) if ring_col_list else np.zeros((0,3),np.float32)
    return WireMesh(line_segments,seg_colors,ring_segments,ring_colors)

Everything else in render_wire.py is unchanged — the thick-quad GS path and CPU billboard fallback already handle arbitrary 3D endpoints, so ramps and bridges render for free.
FIX 4 (nav side) — quake/nav_collision.py

Two changes to _CorridorNav: (a) delegate height to the shared helper (delete the local duplicates), and (b) disambiguate the nearest segment by Y at crossings so the player stays on the bridge they're on.

Change 4a & 4b — replace _nearest_segment, _floor_height, _height_at_vertex, _socket_y and resolve_player_motion. The rest of _CorridorNav and the whole _RoomNav are untouched.

class _CorridorNav:
    def __init__(self, fp: Floorplan):
        self._corridors = list(fp.corridors)
        self._rooms = list(fp.rooms)

    def _nearest_segment(self, p_xz: Vec2, p_y: float | None = None):
        """Nearest corridor segment. When two corridors overlap in XZ (a
        crossing), prefer the one whose interpolated floor Y is closest to the
        player's current Y — so walking a bridge never snaps you to the
        corridor passing underneath."""
        from corridor_height import floor_height
        best = None
        for cor in self._corridors:
            path = cor.path_xz
            if len(path) < 2:
                continue
            for i in range(len(path) - 1):
                a = path[i]
                b = path[i + 1]
                cpt, t = _closest_on_segment_xz(p_xz, a, b)
                dx = p_xz[0] - cpt[0]
                dz = p_xz[1] - cpt[1]
                dist_xz = math.hypot(dx, dz)
                if p_y is None:
                    key = (dist_xz, 0.0)
                else:
                    seg_y = floor_height(cor, i, t, self._rooms)
                    # XZ is primary; Y breaks ties at overlaps (crossings).
                    key = (dist_xz, abs(seg_y - p_y))
                if best is None or key < best[5]:
                    best = (cor, i, cpt, t, dist_xz, key)
        return best

    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3:
        from corridor_height import floor_height
        tx = start[0] + delta[0]
        tz = start[2] + delta[2]
        target_xz = (tx, tz)

        best = self._nearest_segment(target_xz, p_y=start[1])
        if best is None:
            return (tx, start[1] + delta[1], tz)

        cor, seg_i, cpt, t, dist, _key = best
        half_w = cor.width_m / 2.0

        if dist > half_w:
            ox = tx - cpt[0]
            oz = tz - cpt[1]
            n = math.hypot(ox, oz)
            if n > _EPS:
                ux, uz = ox / n, oz / n
            else:
                ux, uz = 0.0, 0.0
            clamp_x = cpt[0] + ux * half_w
            clamp_z = cpt[1] + uz * half_w
            rx = clamp_x + (cpt[0] - clamp_x) * CORRIDOR_SLIDE_SOFTNESS
            rz = clamp_z + (cpt[1] - clamp_z) * CORRIDOR_SLIDE_SOFTNESS
            fx, fz = rx, rz
            path = cor.path_xz
            _, t = _closest_on_segment_xz((fx, fz), path[seg_i], path[seg_i + 1])
        else:
            fx, fz = tx, tz

        y = floor_height(cor, seg_i, t, self._rooms)
        return (fx, y, fz)

Delete the now-unused _floor_height, _height_at_vertex, and _socket_y methods from _CorridorNav (they're replaced by the shared module). Keep nearest_panel and door_at.

    Import note: I use a local from corridor_height import floor_height inside the two methods (mirroring how render_wire does lazy imports) to be maximally safe against import ordering. If DeepSeek prefers, hoist it to the top of nav_collision.py — no circular risk (corridor_height imports only from contracts).

FIX 3 + FIX 4 (guidelines) — quake/guidelines.py

Three changes: (a) make routing 3D-aware (Y follows the walkable floor via the shared helper), (b) un-stub _gl_draw_strip with the real wire_program API, (c) feed per-vertex Y through draw_guidelines.

Change 3a — replace _route_xz with a Y-aware _route_xyz. It reuses the existing BFS but records which corridor each hop uses, so it can compute floor Y per vertex. Replace _route_xz entirely with:

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

Change 3b — replace _gl_floor_y (no longer needed for routes) and _gl_draw_strip. The real draw uses the simple wire_program (bright 1-px lines, no dimming), depth-tested by inheriting the scene state:

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

Change 3c — rewrite draw_guidelines to use the Y-aware route, the real current node, and pass the MVP bytes through. Note the app already computes vp = proj @ view and passes it as view — so draw_guidelines's view arg is the combined view-projection matrix; I convert it to transposed bytes here (matching render_wire._mvp_bytes):

def draw_guidelines(
    view: ViewMatrix,          # NOTE: app passes vp = proj @ view here
    fp: Floorplan,
    targets: list[NodeId],
    current: NodeId | None = None,
) -> None:
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

    _gl_floor_y is now dead; DeepSeek may delete it. _route_xz is replaced by _route_xyz; if anything else imports _route_xz, keep a thin alias def _route_xz(fp, c, t): return [(p[0], p[2]) for p in _route_xyz(fp, c, t)]. The PURE core (select_targets, _graph_distances, etc.) is untouched — all existing guideline tests stay green.

FIX 1 (de-amputate) — quake/app.py

Stop slicing the floorplan to 2 rooms. Render the full graph in corridor mode, and pass the real current node to the guidelines.

Change 1a — the render dispatch block (app.py ~470):

            # (10) render by mode
            try:
                if state.mode == "corridor":
                    render_fp = pack.floorplan          # FULL graph, not the 2-room stub
                    guide_cur = _corridor_current_node(state, outcome, pack)
                    def _gl(v, p, aspect):
                        # v is view, p is proj; guidelines wants combined vp
                        vp = np.ascontiguousarray(p @ v, dtype=np.float32)
                        draw_guidelines(vp, render_fp, targets, current=guide_cur)
                    render_mode_a(ctx, window, view, proj, render_fp, state,
                                  guidelines_fn=_gl, targets=targets)
                else:
                    # room rendering ... (unchanged)

Change 1b — the follow-ups block (app.py ~420): remove the stub construction. Corridor nav must now be built over the full floorplan (so the player can walk any corridor and traverse crossings), and it only needs building once:

            if outcome.mode_switched_to == "room" and outcome.switched_room_id is not None:
                if outcome.switched_room_id not in room_navs:
                    room_navs[outcome.switched_room_id] = \
                        build_room_nav(pack.rooms[outcome.switched_room_id])
                # (corridor nav persists; nothing to tear down)

            if outcome.mode_switched_to == "corridor":
                if _active_corridor[1] is None:
                    _active_corridor[0] = pack.floorplan
                    _active_corridor[1] = build_corridor_nav(pack.floorplan)

Change 1c — add the small helper (near _single_corridor_floorplan, which is now dead and may be deleted):

def _corridor_current_node(state, outcome, pack):
    """The node the guide-lines should originate from while in corridor mode.
    Prefer the room just left (carried on the ModeSwitch as room_id); fall back
    to nearest room ring to the player."""
    rid = getattr(outcome, "switched_room_id", None)
    if rid:
        return rid
    best = None
    px, pz = state.pos[0], state.pos[2]
    for fr in pack.floorplan.rooms:
        dx = px - fr.map_xz[0]; dz = pz - fr.map_xz[1]
        d2 = dx * dx + dz * dz
        if best is None or d2 < best[1]:
            best = (fr.room_id, d2)
    return best[0] if best else None

    Wherever the loop uses _active_corridor[1] as the corridor nav for movement, it now holds the full-floorplan corridor nav — correct, because Fix 4's Y-disambiguation lets it handle crossings. The _active_corridor clearing on room-entry is removed so the full-graph nav persists across trips (rebuilding every door-exit is wasteful and pointless now that it's the whole graph).

What DeepSeek must verify (acceptance + honest gaps)

Render + show Nir a PNG after this drops in — "tests pass" is not success for anything visual (the standing lesson). Specifically look for:

    Full glowing graph around the player on door-exit (not 2 rings). Fix 1.
    Visible bridges/underpasses — a corridor ramping up over another. Fix 2. If everything still looks flat, check that cfg.height.delta_y / base_y are non-trivial and heights[edge.id] actually varies (the hierarchical layout gives ~5 crossings on the Principia graph — those are your bridges).
    <=3 colored guide-lines with arrowheads, riding the floor up ramps. Fix 3+4.
    Walk a bridge without falling to the corridor below. Fix 4b.

Honest gaps / risks:

    G1 — wire_program vs the thick-quad program. I used wire_program(ctx) per your C1 note (simple 1-px lines, correct for floor lines). If it renders too thin to see against the felt, the fallback is to route guide-lines through wire_quad_program with a distinct color — but try the simple program first as specified.
    G2 — MVP handedness for guidelines. render_wire._mvp_bytes computes proj @ view then transposes on upload. In draw_guidelines the app already passes vp = proj @ view as the view arg, so I transpose once. If lines appear mirrored/offset from the wire, the transpose is the first suspect — align it byte-for-byte with _mvp_bytes.
    G3 — Ramp-run vs. short corridors. _insert_ramp_waypoints clamps the run to <=1/3 of the end segment, so short corridors get gentle ramps, not overshoots. Confirm on the real Principia floorplan that no corridor ends up with a zero-length or reversed ramp segment (the clamp should prevent it; a scale test on the 20-node graph will confirm).
    G4 — Nav segment search cost. _nearest_segment is now O(all corridors * segments) per frame with a floor_height call each. For the 28-edge Principia graph this is trivial; if a future 200-node pack stutters, spatially index it. Not a concern now.
    G5 — Existing tests. PURE cores (build_wire_mesh shape, select_targets, _graph_distances, ray/room nav) are unchanged in contract. build_wire_mesh now emits ramped Y — any golden test asserting flat cruise_y on wire vertices will need its expected values updated (this is a correct change, not a regression; update the golden). _CorridorNav height tests that assumed flat Y should now assert the ramped Y from corridor_height.floor_height — port them to the shared helper.
    G6 — Bloom ordering. Guide-lines are drawn inside the scene FBO before bright-extract (your render_mode_a calls guidelines_fn right after _draw_wire, before step 2). So bright guide-lines will bloom slightly. That's probably desirable (they glow). If Nir wants them crisp, move the guideline draw to after the composite (step 5) — a one-line reorder in render_mode_a. Flag for Nir's eyes.

That's the complete implementation — one new file, four edited files, all against real names. Order to drop in: corridor_height.py -> level_maker.py -> render_wire.py -> nav_collision.py -> guidelines.py -> app.py, then render and show Nir.
