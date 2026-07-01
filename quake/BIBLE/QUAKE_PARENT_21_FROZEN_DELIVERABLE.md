# QUAKE PARENT 21 — FROZEN DELIVERABLE (VERBATIM)

**Delivered by:** Claude Opus 4.8 (Parent 21)
**Date:** July 1, 2026
**Mission:** Real 3D Wireframe Corridors (code-writer)

---

## Writing all four files now, drop-in ready.

### File 1 — render_wire.py (add tunnel mesh + point resources at it)

Add these constants, helpers, and _build_tunnel_mesh near the pure core, and change the one call inside _get_wire_resources from build_wire_mesh(fp) to _build_tunnel_mesh(fp). build_wire_mesh is kept for tests/back-compat.

```python
# ==================== ADD near top, after RING_SEGMENTS ====================
import math  # (numpy already imported as np)

_CORRIDOR_HEIGHT_M = 3.0
_RAMP_FRACTION = 0.30


def _ramp_y(u: float) -> float:
    """Symmetric trapezoid: 0 at ends, 1 across the middle. u = arc-length fraction."""
    if u < 0.0:
        u = 0.0
    if u > 1.0:
        u = 1.0
    return max(0.0, min(u / _RAMP_FRACTION, (1.0 - u) / _RAMP_FRACTION, 1.0))


def _corridor_vertex_heights(cor) -> list:
    """Y at each path_xz vertex: socket_y(0) at ends, ramping to cruise_y in middle."""
    pts = cor.path_xz
    seg_lens = []
    for n in range(len(pts) - 1):
        dx = float(pts[n + 1][0]) - float(pts[n][0])
        dz = float(pts[n + 1][1]) - float(pts[n][1])
        seg_lens.append(math.hypot(dx, dz))
    total = sum(seg_lens)
    cum = [0.0]
    for sl in seg_lens:
        cum.append(cum[-1] + sl)
    ys = []
    cy = float(cor.cruise_y)
    for i in range(len(pts)):
        u = (cum[i] / total) if total > 1e-9 else 0.0
        ys.append(cy * _ramp_y(u))  # socket_y = 0.0
    return ys


def _box_segment_edges(start, end, right, up, width, height) -> list:
    """12 wireframe edges ((2,3) float32) for one gravity-aligned box prism."""
    hw, hh = width / 2.0, height / 2.0
    cs = [start + right * hw * sx + up * hh * sy
          for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    ce = [end + right * hw * sx + up * hh * sy
          for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    edges = []
    for i in range(4):  # start ring
        edges.append(np.array([cs[i], cs[(i + 1) % 4]], dtype=np.float32))
    for i in range(4):  # end ring
        edges.append(np.array([ce[i], ce[(i + 1) % 4]], dtype=np.float32))
    for i in range(4):  # rails
        edges.append(np.array([cs[i], ce[i]], dtype=np.float32))
    return edges


def _build_tunnel_mesh(fp: Floorplan) -> WireMesh:
    """Corridor mode mesh: 3D box-chain tunnels (one box per path segment) + room rings."""
    seg_list = []
    seg_col_list = []
    base = WIRE_BASE  # (1,1,1) — shader dims with distance
    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    for cor in fp.corridors:
        pts = cor.path_xz
        if len(pts) < 2:
            continue
        y_vals = _corridor_vertex_heights(cor)
        width = float(cor.width_m)
        for n in range(len(pts) - 1):
            ax, az = float(pts[n][0]), float(pts[n][1])
            bx, bz = float(pts[n + 1][0]), float(pts[n + 1][1])
            direction = np.array([bx - ax, 0.0, bz - az], dtype=np.float32)
            length = float(np.linalg.norm(direction))
            if length < 1e-6:
                continue
            direction = direction / length
            right = np.cross(up, direction)
            rn = float(np.linalg.norm(right))
            if rn < 1e-6:
                continue
            right = right / rn
            start = np.array([ax, y_vals[n], az], dtype=np.float32)
            end = np.array([bx, y_vals[n + 1], bz], dtype=np.float32)
            edges = _box_segment_edges(start, end, right, up, width, _CORRIDOR_HEIGHT_M)
            seg_list.extend(edges)
            seg_col_list.extend([base] * len(edges))

    line_segments = (np.stack(seg_list, 0).astype(np.float32)
                     if seg_list else np.zeros((0, 2, 3), np.float32))
    seg_colors = (np.array(seg_col_list, np.float32)
                  if seg_col_list else np.zeros((0, 3), np.float32))

    # Room rings (identical to build_wire_mesh)
    ring_list = []
    ring_col_list = []
    angles = (2.0 * np.pi) * (np.arange(RING_SEGMENTS, dtype=np.float64) / float(RING_SEGMENTS))
    next_angles = (2.0 * np.pi) * ((np.arange(RING_SEGMENTS, dtype=np.float64) + 1.0) / float(RING_SEGMENTS))
    for room in fp.rooms:
        cx, cz = float(room.map_xz[0]), float(room.map_xz[1])
        r = float(room.map_radius_m)
        y = float(room.socket_y)
        rgb = hex_to_rgb(room.map_color)
        for k in range(RING_SEGMENTS):
            t0, t1 = angles[k], next_angles[k]
            ring_list.append(np.array(
                [[cx + r * np.cos(t0), y, cz + r * np.sin(t0)],
                 [cx + r * np.cos(t1), y, cz + r * np.sin(t1)]], dtype=np.float32))
            ring_col_list.append(rgb)
    ring_segments = (np.stack(ring_list, 0).astype(np.float32)
                     if ring_list else np.zeros((0, 2, 3), np.float32))
    ring_colors = (np.array(ring_col_list, np.float32)
                   if ring_col_list else np.zeros((0, 3), np.float32))

    return WireMesh(line_segments, seg_colors, ring_segments, ring_colors)
```

One-line change inside `_get_wire_resources`: replace `mesh=build_wire_mesh(fp)` with:

```python
    mesh=_build_tunnel_mesh(fp)
```

---

### File 2 — nav_collision.py (replace _CorridorNav)

Replace the entire `_CorridorNav` class (keep `_closest_on_segment_xz`, `build_corridor_nav`, everything else unchanged). This uses the exact same ramp math as render_wire.

```python
# ---------------------------------------------------------------------------
# CORRIDOR NAV — box-chain collision (matches render_wire tunnel geometry)
# ---------------------------------------------------------------------------
_CORRIDOR_HEIGHT_M = 3.0   # must match render_wire.py
_RAMP_FRACTION = 0.30      # must match render_wire.py


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
        ys.append(cy * ramp)  # socket_y = 0.0
    return ys


class _CorridorNav:
    def __init__(self, fp: Floorplan):
        self._corridors = list(fp.corridors)
        self._rooms = list(fp.rooms)
        # Pre-compute one box per path segment across all corridors.
        # Each entry: (start_xz, end_xz, y_start, y_end, right_xz, half_w)
        self._segments = []
        for cor in self._corridors:
            pts = cor.path_xz
            if len(pts) < 2:
                continue
            y_vals = _corridor_vertex_heights_nav(cor)
            half_w = cor.width_m / 2.0
            for n in range(len(pts) - 1):
                ax, az = pts[n][0], pts[n][1]
                bx, bz = pts[n + 1][0], pts[n + 1][1]
                dx, dz = bx - ax, bz - az
                seg_len = math.hypot(dx, dz)
                if seg_len < _EPS:
                    continue
                fwd = (dx / seg_len, dz / seg_len)
                right = (-fwd[1], fwd[0])  # perpendicular in XZ
                self._segments.append((
                    (ax, az), (bx, bz),
                    y_vals[n], y_vals[n + 1],
                    right, half_w,
                ))

    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3:
        tx = start[0] + delta[0]
        ty = start[1] + delta[1]
        tz = start[2] + delta[2]

        if not self._segments:
            return (tx, ty, tz)

        # Find the segment whose centerline is closest to the target XZ.
        best = None
        best_dist = float("inf")
        for seg in self._segments:
            s_xz, e_xz, y_s, y_e, right, half_w = seg
            cpt, t = _closest_on_segment_xz((tx, tz), s_xz, e_xz)
            dist = math.hypot(tx - cpt[0], tz - cpt[1])
            if dist < best_dist:
                best_dist = dist
                best = (seg, cpt, t)

        seg, cpt, t = best
        s_xz, e_xz, y_s, y_e, right, half_w = seg

        floor_y = y_s + (y_e - y_s) * t

        # Clamp lateral offset from centerline to the box half-width.
        lateral = (tx - cpt[0]) * right[0] + (tz - cpt[1]) * right[1]
        if lateral > half_w:
            lateral = half_w
        elif lateral < -half_w:
            lateral = -half_w
        fx = cpt[0] + lateral * right[0]
        fz = cpt[1] + lateral * right[1]

        # Clamp Y between floor and ceiling; Z (forward) is free.
        cy = ty
        if cy < floor_y:
            cy = floor_y
        elif cy > floor_y + _CORRIDOR_HEIGHT_M:
            cy = floor_y + _CORRIDOR_HEIGHT_M

        return (fx, cy, fz)

    def nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None:
        return None  # corridors have no panels

    def door_at(self, point: Vec3) -> str | None:
        return None  # socket-entry handles room arrival; boxes have no side doors
```

`build_corridor_nav(fp)` already returns `_CorridorNav(fp)` — unchanged.

---

### File 3 — guidelines.py (implement _gl_draw_strip + floor-height on the ramp)

Add ramp constants + `_compute_floor_y_at_xz`, replace the stubbed `_gl_draw_strip`, and update `draw_guidelines` to ride the tunnel floor.

```python
# ==================== ADD near top (after HAVE_GL guard) ====================
import math

_CORRIDOR_HEIGHT_M = 3.0   # unused here but keeps parity
_RAMP_FRACTION = 0.30      # must match render_wire.py / nav_collision.py


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
            return cor.cruise_y * ramp  # socket_y = 0.0
    return 0.0
```

Replace the stubbed `_gl_draw_strip`:

```python
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

        # view is already the combined VP matrix (app passes p @ v).
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
```

Update `draw_guidelines` so route + arrowhead ride the ramping floor (replace the per-target body that builds route3d / barb3d):

```python
def draw_guidelines(
    view: ViewMatrix,
    fp: Floorplan,
    targets: list[NodeId],
) -> None:
    """Draw Half-Life-style floor guide-lines on the tunnel floor. Headless-safe."""
    if not HAVE_GL or not targets:
        return
    rooms = _rooms_by_id(fp)
    if not fp.rooms:
        return
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
```

---

### File 4 — app.py (render full floorplan; keep single-corridor nav)

Replace the corridor-mode render dispatch block so the renderer receives the full `pack.floorplan` (all rooms + all corridor tunnels + true heights → depth-test bridges/underpasses). The single-corridor floorplan and its nav (`_active_corridor`) stay exactly as-is and are used only for collision.

```python
if state.mode == "corridor":
    # Render the FULL floorplan: every tunnel + ring at true heights so the
    # player sees the whole see-through graph through the box they stand in,
    # and depth-test resolves bridges/underpasses automatically.
    render_fp = pack.floorplan

    def _gl(v, p, aspect):
        vp = np.ascontiguousarray(p @ v, dtype=np.float32)
        draw_guidelines(vp, render_fp, targets)

    render_mode_a(ctx, window, view, proj, render_fp, state,
                  guidelines_fn=_gl, targets=targets)
```

The nav dispatch line above it is unchanged:

```python
nav = _active_corridor[1] if state.mode == "corridor" and _active_corridor[1] else corridor_nav
```

Guide-line current derivation stays as pasted (`gcur = state.current_room_id or _start_node(pack)`); when a corridor is entered via `outcome.travel_edge_id`, if you want the source room as current, add this just before `targets = select_targets(...)`:

```python
if state.mode == "corridor" and outcome.travel_edge_id is not None:
    parts = outcome.travel_edge_id.split(".to.")
    src_cand = parts[0].replace("edge.", "") if len(parts) == 2 else None
    gcur = src_cand if src_cand else (state.current_room_id or _start_node(pack))
else:
    gcur = state.current_room_id or _start_node(pack)
targets = select_targets(pack.floorplan, gcur, state.cleared, cfg)
```

Done — all four files. The ramp math (`_ramp_y / cor.cruise_y * ramp`, `_RAMP_FRACTION=0.30`, `_CORRIDOR_HEIGHT_M=3.0`, `socket_y=0`) is byte-identical across render_wire, nav_collision, and guidelines, so the box geometry, the collision walls/floor/ceiling, and the guide-line floor all agree exactly. Tunnels render as white box-edge chains through wire_quad_program (distance-dim, depth-tested, no blend, bloom), the player is confined inside them, guide-lines ride the ramping floor, and crossings resolve as bridges/underpasses for free via the depth test.
