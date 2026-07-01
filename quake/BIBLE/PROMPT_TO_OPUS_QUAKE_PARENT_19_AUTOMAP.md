# PARENT 19 — MISSION: DESCENT-STYLE 3D WIREFRAME AUTOMAP

> **Role:** You are a fresh Opus 4.8 architect. **You write code.** Not a document. Not a design spec that DeepSeek implements. Actual Python code, drop-in ready. You are the implementer.

> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**

---

## §0 — WHAT CURRENTLY EXISTS (the problem)

There is no automap. When the player presses Tab, nothing happens. The corridor mode renders a flat 2D top-down map of circles and lines on the XZ plane — what Nir calls "the ugly map." This map is not an automap. It is the wrong thing drawn the wrong way from the wrong perspective.

What Nir wants is a Descent-style 3D wireframe automap. Toggle it with Tab. Fly freely through the entire level as a 3D wireframe. See every room as a 3D box, every corridor as a 3D box chain. Colored by importance. Depth-tested. Distance-dimmed. Nothing flat, nothing 2D, nothing like the current "ugly map."

The Old Testament §3.1 defines the wireframe world. The automap is the same visual language as the corridor tunnel — 3D wireframe boxes — used in a different context: free-flight above the graph instead of walking inside one tunnel.

---

## §1 — THE SPEC (verbatim from the Old Testament §3.1)

> *"Wireframe only. Lines and node rings; no shaded polygons. 'Transparent' here means empty faces with visible edges, not alpha translucency."*

> *"Depth-tested, NO alpha blending. Depth test on, depth write on, blend off, depthFunc = LEQUAL. Near geometry occludes far."*

> *"Distance-dimming in the line shader: the current section renders near pure white, fading with view-space distance toward dark grey — never pure black (so far structure stays a faint felt presence; vanishing into black is what disorients)."*

> *"Crossings visible as true 3D over/under passes."*

### §1.1 — What the automap IS

- Every room = a 3D wireframe box (12 edges — 4 bottom, 4 top, 4 vertical). Box positioned at the room's `map_xz` in floorplan space, at the room's `socket_y` (0.0).
- Every corridor = a chain of 3D wireframe boxes placed end-to-end along `path_xz` (one box per path segment). Box edges drawn at their true ramp-interpolated heights (0 at room ends → `cruise_y` in the middle → back to 0).
- All edges drawn via the existing `wire_quad_program` (thick camera-facing quads, distance-dimming white→grey, depth-tested, no blend).
- Depth test handles bridges and underpasses automatically (boxes at higher `cruise_y` occlude boxes at lower `cruise_y` where they cross).
- Free-fly camera: the player flies through the wireframe graph with full 6-DOF movement (WASD + mouse look). NOT walking on the ground. NOT constrained to a tunnel. NOT attached to the player body. The automap camera is its own thing.

### §1.2 — What the automap is NOT

- NOT a 2D flat top-down map of circles and lines on XZ plane.
- NOT the corridor mode (no collision, no guide-lines, no floor, no arrowheads, no walking inside a tunnel).
- NOT filled solid surfaces.
- NOT alpha-blended.

---

## §2 — BOX GEOMETRY FOR ROOMS AND CORRIDORS

### §2.1 — Room boxes

Each room in `Floorplan.rooms` becomes a 3D wireframe box. Room box dimensions:

**Width and depth:** The room's `map_radius_m` is the radius of its circle on the map. For the automap box, the room spans 2×map_radius_m in both X and Z (a square floor of side 2×map_radius_m, centered at map_xz). This keeps the room box proportional to its map footprint.

**Height:** Use `RoomRuntime.dimensions_m[1]` (the room's TARDIS interior height) if the room data is available at automap construction time. If the automap mesh is built independently of the Pack, use a fixed height: `_AUTOMAP_ROOM_HEIGHT_M = 3.0`.

```python
# Room box: 12 edges at (map_xz.x, socket_y, map_xz.z) with floor at socket_y
# Box spans: X in [cx-r, cx+r], Z in [cz-r, cz+r], Y in [socket_y, socket_y+height]
# where cx,cz = map_xz, r = map_radius_m
```

The 12 edges of a room box:
- 4 bottom edges: form a square at Y = socket_y
- 4 top edges: form a square at Y = socket_y + height
- 4 vertical edges: connect bottom corners to top corners

Edge color: the room's `map_color` (hex → RGB). This is the importance color — rooms with high importance get their designated color on the automap.

### §2.2 — Corridor box chains (the Descent QED pattern)

Same pattern as the corridor tunnel — one box per `path_xz` segment, multiple boxes end-to-end per corridor:

```python
def _box(start, end, right, up, width, height):
    """One rectangular box prism between start and end. Returns 4 start corners, 4 end corners."""
    hw, hh = width / 2.0, height / 2.0
    cs = [start + right * hw * s + up * hh * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    ce = [end   + right * hw * s + up * hh * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    return cs, ce
```

Take the 8 corner vertices and produce 12 edge segments:
- 4 start-ring edges: `cs[i] → cs[(i+1)%4]`
- 4 end-ring edges: `ce[i] → ce[(i+1)%4]`
- 4 rail edges: `cs[i] → ce[i]`

Height interpolation (the ramp):
- `path_xz[0]` = source room's `map_xz` (floor at socket_y=0)
- `path_xz[-1]` = target room's `map_xz` (floor at socket_y=0)
- Middle vertices: floor Y rises to `cruise_y` and falls back
- Symmetric trapezoid ramp: `ramp(u) = clamp(min(u, 1-u) / ramp_fraction, 0, 1)` where u is normalized arc-length
- `y(Pᵢ) = socket_y + (cruise_y - socket_y) * ramp(sᵢ / S)` where sᵢ is cumulative arc-length, S is total length
- `_RAMP_FRACTION = 0.30`

Orientation: `up = (0, 1, 0)` (world up, gravity-aligned). `right = normalize(cross(up, end-start))`.

Corridor edge color: pure white `(1.0, 1.0, 1.0)`. Corridors are transit; the distance-dimming handles white→grey. Importance color belongs to rooms.

### §2.3 — Bridges and underpasses

Different corridors cruise at different `cruise_y` heights (from `height_level * height_delta_m`). Where two corridors cross in XZ, one is higher (bridge) and one is lower (underpass). `Floorplan.crossings` records: `over_corridor`, `under_corridor`, `at_xz`, `over_y`, `under_y`.

Because each corridor's box edges are drawn at their true ramp-interpolated heights, and because the shader uses depth test (no blend), the bridge corridor's edges at `over_y` automatically occlude the underpass corridor's edges at `under_y` where they cross. No crossing-specific code needed. Depth test handles it.

---

## §3 — FILES YOU CREATE AND MODIFY

### §3.1 — New file: `automap.py`

This is the main deliverable. Contains:

**`build_automap_mesh(fp: Floorplan) -> AutomapMesh`**

Takes the full `Floorplan`. For every room, builds a 3D wireframe box (12 edges) at `map_xz`. For every corridor, builds a chain of 3D wireframe boxes (12 edges per path segment) at ramp-interpolated heights. Returns all edges + colors.

```python
# Data class for the automap mesh
@dataclass
class AutomapMesh:
    edges: np.ndarray       # shape (N, 2, 3) — N edge segments, each [start_xyz, end_xyz]
    edge_colors: np.ndarray  # shape (N, 3) — per-edge RGB

_AUTOMAP_CORRIDOR_HEIGHT_M = 3.0
_AUTOMAP_ROOM_HEIGHT_M = 3.0
_RAMP_FRACTION = 0.30

def _ramp_y(u: float) -> float:
    if u < 0.0: u = 0.0
    if u > 1.0: u = 1.0
    return min(u / _RAMP_FRACTION, (1.0 - u) / _RAMP_FRACTION, 1.0)

def _box_edges(start, end, right, up, width, height) -> list:
    """Return 12 edge segments for one box as (N,2,3) numpy arrays."""
    hw, hh = width / 2.0, height / 2.0
    cs = [start + right*hw*sx + up*hh*sy for sx, sy in ((1,1),(1,-1),(-1,-1),(-1,1))]
    ce = [end   + right*hw*sx + up*hh*sy for sx, sy in ((1,1),(1,-1),(-1,-1),(-1,1))]
    edges = []
    for i in range(4):
        edges.append(np.array([cs[i], cs[(i+1)%4]], dtype=np.float32))  # start ring
    for i in range(4):
        edges.append(np.array([ce[i], ce[(i+1)%4]], dtype=np.float32))  # end ring
    for i in range(4):
        edges.append(np.array([cs[i], ce[i]], dtype=np.float32))         # rails
    return edges

def build_automap_mesh(fp: Floorplan) -> AutomapMesh:
    """Build complete 3D wireframe automap from floorplan data.
    
    Rooms: 3D boxes at map_xz, width/depth from map_radius_m, 
           height from RoomRuntime.dimensions_m or _AUTOMAP_ROOM_HEIGHT_M.
           Edges colored by map_color.
    Corridors: chain of 3D boxes along path_xz at ramp-interpolated heights.
           Edges white (dimming handles distance).
    """
    all_edges = []
    all_colors = []
    up = (0.0, 1.0, 0.0)
    
    # Room boxes
    for room in fp.rooms:
        cx, cz = room.map_xz[0], room.map_xz[1]
        r = room.map_radius_m
        sy = room.socket_y
        h = _AUTOMAP_ROOM_HEIGHT_M  # or from RoomRuntime if available
        
        # Room box: center at (cx, sy + h/2, cz), width=2r, height=h (floor at sy)
        # 8 corners of the box
        corners_bottom = [
            np.array([cx - r, sy,       cz - r]),
            np.array([cx + r, sy,       cz - r]),
            np.array([cx + r, sy,       cz + r]),
            np.array([cx - r, sy,       cz + r]),
        ]
        corners_top = [
            np.array([cx - r, sy + h,   cz - r]),
            np.array([cx + r, sy + h,   cz - r]),
            np.array([cx + r, sy + h,   cz + r]),
            np.array([cx - r, sy + h,   cz + r]),
        ]
        rgb = hex_to_rgb(room.map_color)
        for i in range(4):
            all_edges.append(np.array([corners_bottom[i], corners_bottom[(i+1)%4]], dtype=np.float32))
            all_colors.append(rgb)
            all_edges.append(np.array([corners_top[i], corners_top[(i+1)%4]], dtype=np.float32))
            all_colors.append(rgb)
            all_edges.append(np.array([corners_bottom[i], corners_top[i]], dtype=np.float32))
            all_colors.append(rgb)
    
    # Corridor box chains
    white = (1.0, 1.0, 1.0)
    for cor in fp.corridors:
        pts = cor.path_xz
        if len(pts) < 2:
            continue
        seg_lens = []
        for n in range(len(pts) - 1):
            seg_lens.append(math.hypot(pts[n+1][0] - pts[n][0], pts[n+1][1] - pts[n][1]))
        total_len = sum(seg_lens)
        if total_len < 1e-6:
            continue
        cumulative = [0.0]
        for sl in seg_lens:
            cumulative.append(cumulative[-1] + sl)
        y_vals = []
        for i in range(len(pts)):
            u = cumulative[i] / total_len
            ramp = _ramp_y(u)
            y_vals.append(cor.cruise_y * ramp)
        
        for n in range(len(pts) - 1):
            ax, az = pts[n][0], pts[n][1]
            bx, bz = pts[n+1][0], pts[n+1][1]
            dx, dz = bx - ax, bz - az
            seg_len = math.hypot(dx, dz)
            if seg_len < 1e-6:
                continue
            direction = np.array([dx / seg_len, 0.0, dz / seg_len])
            right_vec = np.cross(up, direction)
            right_norm = np.linalg.norm(right_vec)
            if right_norm < 1e-6:
                continue
            right_vec = right_vec / right_norm
            
            start = np.array([ax, y_vals[n], az])
            end = np.array([bx, y_vals[n+1], bz])
            
            edges = _box_edges(start, end, right_vec, up, cor.width_m, _AUTOMAP_CORRIDOR_HEIGHT_M)
            all_edges.extend(edges)
            all_colors.extend([white] * len(edges))
    
    edges_arr = np.stack(all_edges, 0).astype(np.float32) if all_edges else np.zeros((0, 2, 3), np.float32)
    colors_arr = np.array(all_colors, np.float32) if all_colors else np.zeros((0, 3), np.float32)
    return AutomapMesh(edges=edges_arr, edge_colors=colors_arr)
```

**`render_automap(ctx, window, view, proj, mesh: AutomapMesh)`**

Renders the automap mesh using the EXISTING `wire_quad_program` from `shaders.py`. The rendering is identical to how `render_wire._draw_wire` works — same shader, same uniforms, same depth test, same dimming. The only difference is the mesh source.

```python
def render_automap(ctx, window, view, proj, mesh: AutomapMesh):
    """Render the 3D automap using the existing wireframe shader."""
    if not HAVE_GL:
        return
    import moderngl
    from shaders import wire_quad_program, wire_quad_cpu_program
    
    ctx.enable(moderngl.DEPTH_TEST)
    ctx.depth_func = "<="
    ctx.depth_mask = True
    ctx.disable(moderngl.BLEND)
    ctx.disable(moderngl.CULL_FACE)
    
    prog = wire_quad_program(ctx)  # GS path; fall back to CPU if needed
    
    if mesh.edges.shape[0] == 0:
        return
    
    # Flatten edges for upload
    pos = mesh.edges.reshape(-1, 3).astype(np.float32)
    col = np.repeat(mesh.edge_colors, 2, axis=0).astype(np.float32)
    
    # Upload mesh to GPU (cache this per-mesh — rebuild only if mesh changes)
    vbo_p = ctx.buffer(pos.tobytes())
    vbo_c = ctx.buffer(col.tobytes())
    vao = ctx.vertex_array(prog, [(vbo_p, '3f', 'in_pos'), (vbo_c, '3f', 'in_color')], mode=moderngl.LINES)
    
    # Set uniforms
    mvp = np.ascontiguousarray(proj, np.float32) @ np.ascontiguousarray(view, np.float32)
    mvp_bytes = np.ascontiguousarray(mvp.T, np.float32).tobytes()
    try:
        prog['u_mvp'].write(mvp_bytes)
    except Exception:
        pass
    for nm, val in (('u_aspect', float(window.width / max(window.height, 1))),
                    ('u_half_px', 0.0025),
                    ('u_dim_near', 8.0),
                    ('u_dim_far', 220.0),
                    ('u_grey_floor', 0.22)):
        try:
            prog[nm].value = val
        except Exception:
            pass
    
    vao.render()
    try:
        vao.release()
    except Exception:
        pass
```

**`AutomapCamera` class** — free-fly camera for the automap. Similar to the existing `Camera` in `camera.py` but with:
- WASD movement in the direction the camera looks (forward/back/strafe)
- Shift = move faster, Ctrl = move slower
- Mouse look (yaw + pitch)
- No collision — free flight through the wireframe
- No roll
- Starts at the player's current position when the automap is toggled on

```python
class AutomapCamera:
    """Free-fly camera for the Descent-style 3D automap."""
    def __init__(self, start_pos: Vec3, start_heading: float, start_pitch: float):
        self.pos = list(start_pos)
        self.heading = start_heading
        self.pitch = start_pitch
        self.speed = 8.0  # m/s
    
    def update(self, dt: float, move_x: float, move_y: float, move_z: float,
               heading_delta: float, pitch_delta: float, fast: bool, slow: bool) -> ViewMatrix:
        """Update position and orientation. Returns 4x4 view matrix."""
        self.heading += heading_delta
        self.pitch += pitch_delta
        self.pitch = max(-1.5, min(1.5, self.pitch))  # clamp pitch
        
        spd = self.speed
        if fast: spd *= 3.0
        if slow: spd *= 0.3
        
        forward = np.array([math.cos(self.heading) * math.cos(self.pitch),
                            math.sin(self.pitch),
                            math.sin(self.heading) * math.cos(self.pitch)])
        right = np.array([math.sin(self.heading), 0.0, -math.cos(self.heading)])
        up = np.array([0.0, 1.0, 0.0])
        
        self.pos[0] += (forward[0] * move_y + right[0] * move_x + up[0] * move_z) * spd * dt
        self.pos[1] += (forward[1] * move_y + right[1] * move_x + up[1] * move_z) * spd * dt
        self.pos[2] += (forward[2] * move_y + right[2] * move_x + up[2] * move_z) * spd * dt
        
        # Build view matrix: look-at
        target = np.array(self.pos) + forward * 10.0
        world_up = np.array([0.0, 1.0, 0.0])
        z_axis = np.array(self.pos) - target
        z_axis = z_axis / np.linalg.norm(z_axis)
        x_axis = np.cross(world_up, z_axis)
        x_axis = x_axis / (np.linalg.norm(x_axis) + 1e-9)
        y_axis = np.cross(z_axis, x_axis)
        
        view = np.identity(4, dtype=np.float32)
        view[0, :3] = x_axis
        view[1, :3] = y_axis
        view[2, :3] = z_axis
        view[0, 3] = -np.dot(x_axis, self.pos)
        view[1, 3] = -np.dot(y_axis, self.pos)
        view[2, 3] = -np.dot(z_axis, self.pos)
        return view
```

### §3.2 — `app.py` changes

Add automap state and dispatch:

```python
# Module-level automap state
_automap_active = False
_automap_mesh = None
_automap_camera = None

# In the frame loop, before render dispatch, handle Tab toggle:
if not smoke and getattr(actions, 'automap_toggle', False):
    _automap_active = not _automap_active
    if _automap_active:
        # Build mesh on first toggle (or rebuild if floorplan changed)
        if _automap_mesh is None:
            from automap import build_automap_mesh
            _automap_mesh = build_automap_mesh(pack.floorplan)
        # Initialize automap camera at player's current position
        from automap import AutomapCamera
        _automap_camera = AutomapCamera(state.pos, state.heading_rad, state.pitch_rad)

# Render dispatch:
if _automap_active and _automap_mesh is not None:
    # Free-fly automap
    auto_actions = poll(window, None)  # poll automap-specific input
    auto_view = _automap_camera.update(
        dt,
        auto_actions.move_x, auto_actions.move_y, getattr(auto_actions, 'move_z', 0),
        auto_actions.heading_delta, auto_actions.pitch_delta,
        getattr(auto_actions, 'sprint', False), getattr(auto_actions, 'crouch', False)
    )
    proj = perspective(FOV_Y_DEG, w / max(h, 1), NEAR_M, FAR_M * 4)  # longer far plane for overview
    _gl_clear(ctx, 0.05, 0.06, 0.08, 1.0)
    from automap import render_automap
    render_automap(ctx, window, auto_view, proj, _automap_mesh)
else:
    # Normal game rendering (room or corridor mode)
    if state.mode == "corridor":
        # ... existing corridor dispatch ...
    else:
        # ... existing room dispatch ...
```

**Input binding for Tab:** Add `automap_toggle` to the DEFAULT_BINDINGS in `input_actions.py` mapped to `pyglet.window.key.TAB`. The input poll function should detect the key press and include it in the Actions dataclass as a boolean field `automap_toggle: bool = False`.

### §3.3 — `input_actions.py` changes

Add `automap_toggle` field to the `Actions` dataclass:

```python
@dataclass
class Actions:
    move_x: float = 0.0
    move_y: float = 0.0
    heading_delta: float = 0.0
    pitch_delta: float = 0.0
    aim_x: float = 0.0
    aim_y: float = 0.0
    fire: bool = False
    read_toggle: bool = False
    pause: bool = False
    automap_toggle: bool = False  # NEW
```

Add to DEFAULT_BINDINGS. If Tab is already bound, the automap overrides it.

---

## §4 — THE EXISTING SHADER (what you're feeding)

The wireframe shader for the automap is `wire_quad_program(ctx)` from `shaders.py` — the SAME shader used by the current `render_wire._draw_wire`. It is already compiled and working.

```glsl
// WIREQ_VS: takes in_pos (vec3), in_color (vec3). Outputs clip.w as g_wdist.
// WIREQ_GS: expands each line segment into 2 camera-facing tris. Uses u_aspect, u_half_px.
// WIREQ_FS: distance-dim via clip.w. t = (wdist - u_dim_near) / (u_dim_far - u_dim_near).
//           bright = mix(1.0, u_grey_floor, t). Outputs f_color * bright.
```

Uniforms to set:
- `u_mvp` — world-to-clip matrix (transpose(proj @ view) as byte buffer)
- `u_aspect` — window width / height
- `u_half_px` — 0.0025 (line half-thickness in NDC)
- `u_dim_near` — 8.0 (full white within this distance)
- `u_dim_far` — 220.0 (reaches grey floor by this distance)
- `u_grey_floor` — 0.22 (never pure black)

For colored room edges: the fragment shader multiplies `f_color * bright`. `f_color` is the per-vertex color. For rooms, `f_color` is the room's importance color (from `map_color`). For corridors, `f_color` is white `(1.0, 1.0, 1.0)`. The dimming is applied on top: a red room's edges at distance are dark red-grey, not pure red. This is correct — Descent does the same.

For the simple `wire_program(ctx)` (no GS, plain LINE_STRIP): use this for any simple line strips needed in the automap (axis indicators, labels, etc.). It has `u_mvp` only. No dimming — lines are always their full color.

---

## §5 — CONTRACTS & DATA (verbatim from raw_models.py)

```python
class FloorRoom(BaseModel):
    room_id: NodeId
    map_xz: Vec2
    importance: int = Field(ge=1, le=5)
    map_radius_m: float
    map_color: Hex
    socket_y: float = 0.0

class Corridor(BaseModel):
    corridor_id: str = Field(pattern=r"^edge\.[a-z0-9_]+\.to\.[a-z0-9_]+$")
    source: NodeId
    target: NodeId
    height_level: int
    cruise_y: float
    path_xz: list[Vec2]
    width_m: float

class Crossing(BaseModel):
    crossing_id: str
    over_corridor: str
    under_corridor: str
    at_xz: Vec2
    over_y: float
    under_y: float

class Floorplan(BaseModel):
    schema_version: Literal["1.0"]
    level_id: LevelId
    seed: int
    rooms: list[FloorRoom]
    corridors: list[Corridor]
    crossings: list[Crossing]
```

`path_xz[0]` = source room's `map_xz` exactly. `path_xz[-1]` = target room's `map_xz` exactly.

The Pack is loaded in `app.py` via `load_pack(PACK_DIR)`. `pack.floorplan` gives you the `Floorplan`. `pack.rooms` gives you `dict[NodeId, RoomRuntime]` with `RoomRuntime.dimensions_m` if you need room interior height.

---

## §6 — WHAT THE AUTOMAP SHARES WITH THE CORRIDOR TUNNEL

The automap and the corridor tunnel are the SAME geometry concept applied in two modes:

| Feature | Corridor Mode | Automap Mode |
|---------|---------------|--------------|
| Room geometry | Box at map_xz, 12 edges | Box at map_xz, 12 edges |
| Corridor geometry | Box chain along path_xz, 12 edges/segment | Box chain along path_xz, 12 edges/segment |
| Height | Ramp-interpolated per vertex | Ramp-interpolated per vertex |
| Shader | wire_quad_program | wire_quad_program |
| Depth test | LEQUAL, no blend | LEQUAL, no blend |
| Distance-dimming | White→grey via clip.w | White→grey via clip.w |
| Camera | Player body camera | Free-fly camera |
| View | Player position | Fly-anywhere |
| Collision | Box collision (walls/floor/ceiling) | None (free flight) |
| Guide-lines | Yes (on floor, arrowheads) | No |
| Target | Current room's nearest uncleared | None (all nodes visible) |

If the corridor tunnel mesh function exists in `render_wire.py` (e.g., `_build_tunnel_mesh`), your `build_automap_mesh` can call the same function to get corridor box edges. But write your function to be self-contained — don't assume the corridor mesh exists. Your automap works with just `Floorplan` data.

---

## §7 — EXISTING CODE THAT STAYS UNCHANGED

- `gameplay.py` — game logic. Unchanged.
- `state.py` — game state. Unchanged.
- `camera.py` — player camera. Unchanged (the automap camera is a separate class).
- `render_room.py` — room rendering. Unchanged.
- `render_wire.py` — wireframe renderer. Unchanged (you use the same shader, you don't modify this file).
- `shaders.py` — all shader sources and program factories. Unchanged.
- `raw_models.py` — all contracts. Unchanged.
- `nav_collision.py` — navigation. Unchanged.
- `guidelines.py` — guide-lines. Unchanged (automap has no guide-lines).
- `assets.py` — pack loading. Unchanged.
- `readmode.py` — read overlay. Unchanged.

---

## §8 — WHAT NOT TO DO

1. **Do NOT write a design document.** You write code. Python files. `automap.py`. Changes to `app.py`. Changes to `input_actions.py`.
2. **Do NOT make a 2D flat top-down map.** The existing `build_wire_mesh` draws circles and lines on XZ. You are NOT fixing that function. You are writing a NEW function that builds 3D boxes.
3. **Do NOT use alpha blending.** Depth test is the occlusion mechanism. The shader already does this correctly.
4. **Do NOT fill boxes with solid surfaces.** Wireframe edges only.
5. **Do NOT add floor guide-lines or arrowheads.** The automap has none.
6. **Do NOT add collision to the automap camera.** Free flight through the wireframe.
7. **Do NOT make edges fade to pure black.** The existing shader's `u_grey_floor = 0.22` handles this.
8. **Do NOT ask Nir questions the spec already answers.** Room color = map_color. Corridor color = white. Height = interpolated from cruise_y. Box orientation = gravity-aligned. All answered above.
9. **Do NOT surface questions to Nir that you should decide.** The room box height, the corridor box height, the ramp fraction — these are module constants. Nir can change them later if he doesn't like the look, but you pick reasonable defaults.
10. **Do NOT ask DeepSeek to confirm API signatures.** The shader signatures are pasted here. The Floorplan fields are pasted here. You confirm.
11. **Do NOT write "DeepSeek implements this."** You implement it.
12. **Do NOT claim you lost Nir's text and demand re-pastes.**

---

## §9 — ACCEPTANCE (what Nir verifies)

1. Press Tab → the screen switches from room/corridor view to the 3D wireframe automap.
2. Every room is a 3D wireframe box at its floorplan position, colored by importance.
3. Every corridor is a chain of white wireframe boxes connecting rooms, dipping and rising with the ramp.
4. Bridges and underpasses: where corridors cross, one box chain passes visibly OVER the other at different heights.
5. Free-fly camera: WASD moves in the look direction. Shift = faster. Mouse = look. No collision.
6. Distance-dimming: near boxes are bright and colorful, far boxes recede to dark grey. Never black.
7. Depth test: near edges occlude far edges. No alpha ghosting.
8. Press Tab again → return to normal game view at the player's position.
9. Works with the Principia pack (20 rooms, 28 corridors, 5 crossings).

---

## §10 — HOW TO GET MORE INFORMATION

Ask DeepSeek via Nir for exact verbatim sections. Files available:
- `quake/render_wire.py` — existing wireframe renderer (thick quads, dimming, bloom, `_draw_wire`, `render_mode_a`)
- `quake/shaders.py` — wire_quad_program, wire_program, all GLSL sources, all uniforms
- `quake/map/raw_models.py` — Floorplan, FloorRoom, Corridor, Crossing, BuildConfig
- `quake/camera.py` — existing Camera class (look-at view matrix, perspective projection)
- `quake/app.py` — render dispatch, frame loop, camera wiring, input polling
- `quake/input_actions.py` — Actions dataclass, poll(), DEFAULT_BINDINGS
- `quake/contracts.py` — shared type imports
- `quake/gfx_context.py` — window creation, GL context

---

## §11 — TALK FIRST

State your understanding, which files you will create and modify, what each will contain. **Wait for Nir's confirmation before writing code.**
