# PARENT 21 — MISSION: REAL 3D WIREFRAME CORRIDORS BETWEEN ROOMS

> **Role:** You are a fresh Opus 4.8 architect. **You write code.** Not a document. Not a design spec that DeepSeek implements. Actual Python code, drop-in ready. You are the implementer.

> **Launch files (4, pasted by Nir):**
> 1. The Commentaries (`QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`)
> 2. Old Testament (`QUAKE_DOCTRINE_BY_FUSION.md`)
> 3. New Testament (`QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md`)
> 4. **This handoff (the mission brief)**

---

## §0 — WHO YOU ARE AND WHY YOU ARE HERE

### §0.1 — What happened before you

Two parents before you failed this exact mission:

**Parent 18** (fired) was asked to build real 3D corridor tunnels. He reinterpreted the mission into "fix the 2D wireframe map" — added Y-disambiguation, ramp waypoints, a `corridor_height.py` module. He never built a single tunnel box. He never connected a door to a door. He delivered a wireframe graph improvement and called it "corridors." Every line of his code was reverted. The codebase is clean.

**Parent 20** (fired) was given the exact same mission with corrected instructions. He wrote a 10-section prose document titled "CORRIDOR DESIGN" and ended with "This is ready for DeepSeek to implement." He deferred collision to "a follow-up" — a corridor with no walls you can't walk inside. He wanted to render all 28 corridors at once as a panorama. He asked DeepSeek to confirm shader signatures that were already pasted to him. He wrote zero lines of Python.

Both parents shared the same failure mode: they reinterpreted "build corridors" into whatever was easier (fix a graph, write a document) instead of writing code that produces a 3D box tunnel the player walks through.

### §0.2 — You will not do that

Your deliverable is **Python files**. You write the code. You are the implementer. DeepSeek integrates and tests and pushes to git. Nir plays the game and judges the result with his own eyes. There is no middle step of "DeepSeek implements the design." The design IS the code you write.

---

## §1 — THE CURRENT FAILURE (what's wrong today)

When the player exits a room door today, the game switches to "corridor mode" and shows a 2D flat top-down wireframe map — circles (room rings) and lines (corridor centerlines) drawn on the XZ plane. The player walks on this flat plane toward another room's circle, enters it when within 1.0m, and teleports into the next room. There is no corridor. There is no tunnel. There is no feeling of being inside anything. Nir calls this "the ugly map."

The code responsible lives in `render_wire.py` function `build_wire_mesh(fp)`. It currently:

```python
for cor in fp.corridors:
    y = float(cor.cruise_y)   # ONE flat height per corridor
    pts = cor.path_xz
    for n in range(len(pts)-1):
        ax, az = float(pts[n][0]), float(pts[n][1])
        bx, bz = float(pts[n+1][0]), float(pts[n+1][1])
        seg_list.append(np.array([[ax, y, az], [bx, y, bz]], dtype=np.float32))
        seg_col_list.append((1.0, 1.0, 1.0))
```

This draws ONE centerline segment per corridor segment at ONE flat height. It draws a graph. It does not draw a tunnel.

The corridor-mode render dispatch in `app.py` (line ~468–476) currently:

```python
if state.mode == "corridor":
    render_fp = _active_corridor[0] if _active_corridor[0] is not None else pack.floorplan
    def _gl(v, p, aspect):
        vp = np.ascontiguousarray(p @ v, dtype=np.float32)
        draw_guidelines(vp, render_fp, targets)
    render_mode_a(ctx, window, view, proj, render_fp, state,
                  guidelines_fn=_gl, targets=targets)
```

It passes a filtered floorplan (2 rooms + 1 corridor via `_single_corridor_floorplan()`) to `render_mode_a`. The renderer draws those 2 room rings and 1 flat corridor centerline. This is the "ugly map."

---

## §2 — WHAT A CORRIDOR IS (the spec you must build)

### §2.1 — Verbatim from the Old Testament §3.1

> *"The player walks the concept graph as a live, glowing, see-through 3D map. Pure transit: no enemies, no panels, no shooting targets, no reading."*

> *"Wireframe only. Lines and node rings; no shaded polygons. 'Transparent' here means empty faces with visible edges, not alpha translucency."*

> *"Depth-tested, NO alpha blending. Depth test on, depth write on, blend off, depthFunc = LEQUAL. Near geometry occludes far. This is the single most important rendering decision."*

> *"Distance-dimming in the line shader: the current section renders near pure white, fading with view-space distance toward dark grey — never pure black."*

> *"Crossings visible as true 3D over/under passes."*

> *"~3 floor guide-lines (Half-Life style), procedural, on the felt floor, with arrowheads, pointing to the selected destinations."*

### §2.2 — What this means in practice

A corridor IS:
- A chain of 3D rectangular boxes placed end-to-end along the corridor's `path_xz` polyline
- One box per path segment (path_xz has N points → N-1 boxes)
- Each box sits in floorplan world coordinates at its correct Y height (ramping from socket_y=0 at room ends up to cruise_y in the middle and back down)
- Each box has 12 edges drawn as wireframe (4 floor edges, 4 ceiling edges, 4 vertical rails)
- All edges drawn via the existing wire_quad_program (thick camera-facing quads, distance-dimming white→grey, depth-tested, no blend)
- The distant graph (other corridor tunnels, room rings) shows faintly THROUGH the transparent wireframe box the player stands inside
- Crossings: depth test handles bridges (tunnel at higher cruise_y) and underpasses (tunnel at lower cruise_y) automatically — the whole point of true-3D Quake

A corridor is NOT:
- A 2D flat top-down map of circles and lines
- One single box (one box per segment, multiple boxes per corridor)
- A swept or extruded mesh (discrete boxes, not continuous geometry)
- Filled solid surfaces

### §2.3 — The Descent QED box pattern (the model you follow)

Descent QED builds corridors the exact same way: one box per segment, multiple segments end-to-end. The pattern is:

```python
def _box(start, end, right, up, width, height):
    """One rectangular box prism between start and end. Returns 4 start corners, 4 end corners."""
    hw, hh = width / 2.0, height / 2.0
    cs = [start + right * hw * s + up * hh * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    ce = [end   + right * hw * s + up * hh * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    return cs, ce
```

For Quake wireframe, you take the 8 corner vertices (4 from `cs`, 4 from `ce`) and produce 12 edge segments:

```
Floor edges:   cs[0]→cs[1], cs[1]→cs[2], cs[2]→cs[3], cs[3]→cs[0]
Ceiling edges: (same pattern with cs[i] + up * height, ce[i] + up * height)
               ce[0]→ce[1], ce[1]→ce[2], ce[2]→ce[3], ce[3]→ce[0]
               (but using cs+up and ce+up)
Vertical rails: cs[0]→cs[0]+up*height, cs[1]→cs[1]+up*height,
                cs[2]→cs[2]+up*height, cs[3]→cs[3]+up*height
```

Wait — the boxes use the Descent convention. Let me be precise about the 12 edges:

For each box with 4 start corners `cs[0..3]` and 4 end corners `ce[0..3]`:
- 4 "start-ring" edges: `cs[i] → cs[(i+1)%4]` for i=0..3 (the box's cross-section at the near end, forming the floor)
- 4 "end-ring" edges: `ce[i] → ce[(i+1)%4]` for i=0..3 (cross-section at the far end, forming the ceiling extension)
- 4 "rail" edges: `cs[i] → ce[i]` for i=0..3 (the four long rails connecting the two cross-sections: two at the bottom = floor rails, two at the top = ceiling rails)

Each edge is one `(2, 3)` float32 numpy array appended to the `WireMesh.line_segments` array. Per box = 12 edges. A corridor with K segments contributes 12K edge segments.

Adjacent boxes share a cross-section at their shared vertex. The "start-ring" of box i+1 draws the same edges as the "end-ring" of box i. This is harmless (same edges, same depth, no visible artifact) and simpler. Leave it in.

### §2.4 — Height interpolation (the ramp)

Heights are NOT precomputed per path vertex. You derive them.

A corridor gives you:
- `cruise_y`: the corridor's cruising height (already set by `level_maker.py`, equals `height_level * height_delta_m`)
- `path_xz`: list of (x, z) world coordinates. First point = source room's `map_xz`. Last point = target room's `map_xz`.
- `socket_y` = 0.0 (from `FloorRoom` — the room floor is at Y=0 in floorplan space)

You compute a Y for each path_xz vertex with a symmetric ramp:

```
Ramp rule:
- The floor rises from socket_y (0.0) at the first vertex (room A center)
  to cruise_y over the first stretch
- Holds cruise_y across the middle
- Falls back to socket_y at the last vertex (room B center)
```

Concrete algorithm: for a corridor with vertices P₀...Pₖ, compute cumulative arc-length sᵢ along the polyline (sum of XZ segment lengths from P₀ to Pᵢ), with total length S = sₖ. Then:

```
y(Pᵢ) = socket_y + (cruise_y - socket_y) * ramp(sᵢ / S)
```

Where `ramp(u)` is a symmetric trapezoid clamped to [0, 1]:

```
ramp(u) = clamp( min(u, 1-u) / ramp_fraction, 0, 1 )
```

`ramp_fraction` is the fraction of the corridor's total length spent ramping up on each end. Pin this as a module constant `_RAMP_FRACTION = 0.30` in `render_wire.py`. A short corridor where both ramps overlap simply peaks below cruise_y — correct and self-consistent.

Each box for segment i spans Pᵢ→Pᵢ₊₁. Its start corners use y(Pᵢ), its end corners use y(Pᵢ₊₁). Because adjacent boxes share the height at their shared vertex, the chain is continuous. The "step up" the player sees is the discrete tilt of each box.

### §2.5 — Box orientation

`up` = world up `(0, 1, 0)`. Boxes are gravity-aligned, not perpendicular to the sloped path segment. A corridor is a chain of level box sections at progressively higher Y, not a tilted tube. This matches the design principle: discrete boxes at different heights. The ramp is the step between adjacent boxes.

`right` = `normalize(cross(up, direction))` where `direction = normalize(end - start)`.

If `end == start` in XZ (zero-length segment), skip that box.

`width` = `corridor.width_m`.

`height` = pin as module constant `_CORRIDOR_HEIGHT_M = 3.0` in `render_wire.py`. Player eye height is 1.6m. 3.0m ceiling clears it comfortably.

### §2.6 — Color

Every corridor box edge is pure white `(1.0, 1.0, 1.0)`. The existing shader's distance-dimming handles the white→grey-with-distance effect automatically — the box you're standing inside is bright white up close; distant tunnel boxes recede to dark grey (never black, `u_grey_floor = 0.22`).

Room rings keep their per-room importance color (unchanged from the current `build_wire_mesh` — rings are built from `fp.rooms` with `hex_to_rgb(room.map_color)`).

### §2.7 — What the player sees (the "see-through" promise)

The player stands INSIDE a corridor box chain. The 12 box edges of the section they're in are bright white up close. Looking forward, the next boxes in the chain dim gradually with distance down the tunnel.

Beyond the tunnel walls — visible through the empty faces of the wireframe box — the rest of the graph glows faintly: other corridor tunnels as their box edges, room rings as their colored circles. All depth-tested. All at their true heights.

This is achieved by passing the FULL floorplan to the renderer — all 28 corridors as box chains, all 20 room rings. The player is just inside one of them. Near edges occlude far edges via depth test. The visual result matches the Old Testament description: "the player walks the concept graph as a live, glowing, see-through 3D map."

### §2.8 — Bridges and underpasses (crossings)

`Floorplan.crossings` already records every crossing. Each `Crossing` has: `over_corridor` (bridge), `under_corridor` (underpass), `at_xz` (where they cross), `over_y` (bridge height), `under_y` (underpass height). Assertion from the build pipeline: `over_y > under_y`.

Because each corridor's box edges are drawn at their true heights (using `cruise_y` which equals `height_level * height_delta_m`), and because the shader uses depth test with no blend, the bridge corridor's edges at `over_y` automatically occlude the underpass corridor's edges at `under_y` where they cross. No crossing-specific code. No XZ overlap detection. No manual occlusion logic. The depth test handles it because the 3D positions are correct.

This is the ENTIRE reason Quake is true-3D instead of flat Doom.

---

## §3 — COLLISION: THE PLAYER WALKS INSIDE THE BOX

The player currently walks in floorplan-world coordinates in corridor mode. The existing `_CorridorNav` in `nav_collision.py` does a soft cylindrical rail-assist toward the nearest corridor centerline. This is wrong for box tunnels — the player should be confined inside the rectangular box walls, floor, and ceiling.

### §3.1 — Box collision model (modeled on _RoomNav)

The room navigation class `_RoomNav` in `nav_collision.py` does exactly what we need — just for a room box instead of corridor boxes. Study it:

```python
class _RoomNav:
    def __init__(self, room: RoomRuntime):
        self._room = room
        w, h, d = room.dimensions_m
        self._w = w    # width (X)
        self._h = h    # height (Y)
        self._d = d    # depth (Z)
        self._doors = list(room.doors)

    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3:
        w2 = self._w / 2.0
        d2 = self._d / 2.0
        sx, sy, sz = start
        tx = sx + delta[0]
        ty = sy + delta[1]
        tz = sz + delta[2]

        # Y clamp to box (floor..ceiling)
        if ty < 0.0: ty = 0.0
        if ty > self._h: ty = self._h

        # X axis: walls at +w2 and -w2
        # Pass through if there's a door opening at the crossing point
        if tx > w2:
            if not self._crosses_door_x(+w2, sy, sz, tz, ty): tx = w2
        elif tx < -w2:
            if not self._crosses_door_x(-w2, sy, sz, tz, ty): tx = -w2

        # Z axis: walls at +d2 and -d2
        if tz > d2:
            if not self._crosses_door_z(+d2, sy, sx, tx, ty): tz = d2
        elif tz < -d2:
            if not self._crosses_door_z(-d2, sy, sx, tx, ty): tz = -d2

        return (tx, ty, tz)
```

The room nav works because:
- The room box is axis-aligned (walls N/E/S/W)
- `dimensions_m` = `(W, H, D)` — width along X, height along Y, depth along Z
- Doors are rectangular openings on specific walls — the `_crosses_door_*` helpers check if the player is passing through a door opening rather than hitting a solid wall
- The room's origin is at its center in XZ, floor at Y=0

### §3.2 — Corridor box nav

A corridor is a chain of boxes, not one box. But each segment box is also axis-aligned (walls N/E/S/W, box oriented along the segment direction). The challenge is that each segment box has a different orientation (it runs along its path_xz segment direction, not fixed to world axes).

However: since the boxes are built with `right = normalize(cross(up, direction))` where `direction` points along the segment, each box IS aligned to its own local frame. The box is the space between two rings at different path points.

Here is the collision approach:

**Corridor nav** = a list of segment boxes. Each segment box has:
- `start_xz`, `end_xz` — the two path points in XZ
- `y_start`, `y_end` — floor Y at start and end (from ramp interpolation)
- `width` = `corridor.width_m`
- `height` = `_CORRIDOR_HEIGHT_M`
- `forward` = normalized `(end_xz - start_xz)` in XZ
- `right` = perpendicular to forward in XZ: `(-forward_z, forward_x)`

For collision, transform the player's position into the segment box's local frame:

```
local_x = dot(player_xz - start_xz, right_vec)
local_z = dot(player_xz - start_xz, forward_vec)   # distance along the segment
local_y = player_y - floor_y_at_local_z             # where floor_y is interpolated
```

Clamp `local_x` to `[-width/2, +width/2]`. Clamp `local_y` to `[0, height]`. For `local_z`, it is NOT clamped (the player walks forward through segments). If `local_z < 0`, the player is before this segment (still in the previous one). If `local_z > segment_length`, the player is past this segment (entering the next one).

Transform back to world coords after clamping X and Y.

**Door passage between boxes:** Adjacent boxes share a face at their shared vertex. The box at segment i has its far face at the shared vertex; the box at segment i+1 has its near face at the same shared vertex. The player passes freely between adjacent boxes because the collision is per-box and boxes share vertices — no gap, no wall between them.

**Entering/exiting the corridor:** The first box starts at the source room's `map_xz`. The last box ends at the target room's `map_xz`. The existing `door_at` in `gameplay.py` doesn't handle corridor nav — corridors have no `door_at`. Instead, the existing socket-entry code in `gameplay.py` (line 166-190) already handles corridor-to-room transition: walking within `SOCKET_ENTER_RADIUS_M` (1.0m) of the target room's `map_xz` teleports into that room. Since the last box ends exactly at the target room's `map_xz`, this already works.

### §3.3 — Implementation in nav_collision.py

Replace `_CorridorNav` with a new class `_CorridorNav` that:
- Stores a list of segment box bounds (one per path_xz segment across ALL corridors, or builds them on the fly)
- `resolve_player_motion(start, delta)` — finds which corridor the player is in, which segment of that corridor, clamps X and Y to that box, returns the clamped position
- `nearest_panel(ray, max_dist)` — returns `None` (corridors have no panels)
- `door_at(point)` — returns `None` (socket-entry handles arrival; corridor boxes have no doors on their sides)

`build_corridor_nav(fp)` returns this new `_CorridorNav`.

---

## §4 — GUIDE-LINES ON THE FLOOR

### §4.1 — What exists today

The guideline logic in `guidelines.py` is fully functional:

```python
def select_targets(fp, current, cleared, cfg) -> list[NodeId]:
    """Choose <=3 guide-line destinations. Pure, tested, works. 8 passing tests."""
    # Uses BFS distances, importance weighting, returns sorted list of NodeIds

def _route_xz(fp, current, target) -> list[Vec2]:
    """BFS shortest-path corridor route as XZ polyline. Pure, tested, works."""

def _arrowhead_xz(p_prev, p_tip, size) -> list[Vec2]:
    """Build arrowhead barb points. Pure, tested, works."""

def draw_guidelines(view, fp, targets):
    """Draw Half-Life-style floor guide-lines. Calls _gl_draw_strip per route."""
    # Works for logic — resolves routes, builds 3D points, calls _gl_draw_strip
```

The ONLY broken piece is `_gl_draw_strip`:

```python
def _gl_draw_strip(view: ViewMatrix, points_xyz: list[Vec3],
                   color_rgb: Vec3, alpha: float) -> None:
    """Draw a polyline/ribbon strip on the floor.

    INTEGRATION: confirm exact API. Simplest path: feed `points_xyz` to
    shaders.wire_program as a line strip (or thin ribbon of line-quads).
    This wrapper is the single place that touches moderngl/pyglet; it is
    never reached headless (HAVE_GL gate in draw_guidelines).
    """
    # INTEGRATION: confirm exact API — pseudocode below.
    # INTEGRATION: GL strip draw not yet wired — silently skip guide-line
    # rendering rather than crashing. Guidelines are visual polish only.
    return
```

### §4.2 — What you must do

Implement `_gl_draw_strip` to actually draw the polyline to the GPU.

The function receives: `view` (4×4 view-projection matrix as numpy array), `points_xyz` (list of Vec3 world points forming the polyline), `color_rgb` (Vec3 color from the target room's map_color), `alpha` (float, 0.65).

Use the simple `wire_program(ctx)` (NOT `wire_quad_program`). The simple wire program uses:

```glsl
// WIRE_VS
#version 330 core
uniform mat4 u_mvp;
in vec3 in_pos;
in vec3 in_color;
out vec3 v_color;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_color = in_color;
}

// WIRE_FS
#version 330 core
in vec3 v_color;
out vec4 frag_color;
void main() {
    frag_color = vec4(v_color, 1.0);
}
```

Draw as `LINE_STRIP` with depth test ON (so guide-lines are occluded by nearer tunnel walls). The color is the target room's importance `map_color` — set it per-strip.

The arrowhead: `_arrowhead_xz` returns 3 points: left barb, tip, right barb. Draw two segments: tip→left and tip→right (or a short LINE_STRIP of the 3 points).

**Height:** Guide-lines must ride the corridor floor inside the tunnel. Currently `draw_guidelines` lifts all XZ route points to `y = _gl_floor_y(room)` which is `room.socket_y + 0.02` = 0.02m. This is wrong for corridors — the floor is at the ramp height, not at y=0.

Fix: in `draw_guidelines`, when converting each route point from XZ to XYZ, compute its Y using the same ramp height interpolation that the corridor box geometry uses. For each route point, find which corridor it lies on, which segment, and compute the interpolated floor Y at that point. Add a small epsilon (0.02m) so the line sits just above the floor. The guide-line rides the ramping floor.

### §4.3 — Target selection in corridor mode

In room mode, `current` = the player's current room (from `state.current_room_id`). In corridor mode, the player is between rooms. Use the corridor's source room as `current` for `select_targets`. The source room is obtained from the corridor the player is traveling — either from `travel_edge_id` (the door they exited through) or from the nearest corridor.

The targets list is computed in `app.py` where it currently assembles `targets` for `render_mode_a`. Update that assembly to pass the corridor's source room as `current`.

---

## §5 — FILES YOU MODIFY

### §5.1 — `render_wire.py`

**New function `_build_tunnel_mesh(fp)`** — replaces the current `build_wire_mesh(fp)` as the mesh builder for corridor mode. (Keep the old function for backward compat or rename it — your call.)

Takes the full `Floorplan`. For every corridor, for every adjacent pair of `path_xz` points, builds one box via the Descent `_box` pattern, extracts 12 edge segments, appends them to `line_segments`. Room rings are built the same way as before (from `fp.rooms`, colored by importance).

Returns `WireMesh(line_segments, seg_colors, ring_segments, ring_colors)`.

```python
_CORRIDOR_HEIGHT_M = 3.0
_RAMP_FRACTION = 0.30

def _ramp_y(u: float) -> float:
    """Symmetric trapezoid ramp: 0 at ends, 1 in middle.
    u in [0, 1] is normalized arc-length along corridor."""
    if u < 0.0: u = 0.0
    if u > 1.0: u = 1.0
    return min(u / _RAMP_FRACTION, (1.0 - u) / _RAMP_FRACTION, 1.0)

def _box_segment_edges(start: Vec3, end: Vec3, right: Vec3, up: Vec3, width: float, height: float) -> list:
    """Return 12 edge segments ((2,3) numpy arrays) for one box."""
    hw, hh = width / 2.0, height / 2.0
    cs = [start + right*hw*sx + up*hh*sy for sx, sy in ((1,1),(1,-1),(-1,-1),(-1,1))]
    ce = [end   + right*hw*sx + up*hh*sy for sx, sy in ((1,1),(1,-1),(-1,-1),(-1,1))]
    edges = []
    # start ring (4 edges)
    for i in range(4):
        edges.append(np.array([cs[i], cs[(i+1)%4]], dtype=np.float32))
    # end ring (4 edges)
    for i in range(4):
        edges.append(np.array([ce[i], ce[(i+1)%4]], dtype=np.float32))
    # rails (4 edges)
    for i in range(4):
        edges.append(np.array([cs[i], ce[i]], dtype=np.float32))
    return edges

def _build_tunnel_mesh(fp: Floorplan) -> WireMesh:
    seg_list = []
    seg_col_list = []
    base_color = (1.0, 1.0, 1.0)
    up = (0.0, 1.0, 0.0)  # world up

    for cor in fp.corridors:
        pts = cor.path_xz
        if len(pts) < 2:
            continue
        # Compute arc-lengths and total length
        seg_lens = []
        for n in range(len(pts) - 1):
            dx = pts[n+1][0] - pts[n][0]
            dz = pts[n+1][1] - pts[n][1]
            seg_lens.append(math.hypot(dx, dz))
        total_len = sum(seg_lens)
        cumulative = [0.0]
        for sl in seg_lens:
            cumulative.append(cumulative[-1] + sl)

        # Compute Y at each vertex
        y_vals = []
        for i in range(len(pts)):
            u = cumulative[i] / total_len if total_len > 0 else 0.0
            ramp = _ramp_y(u)
            # ramp goes 0→1 at start, 1 in middle, 1→0 at end
            y_vals.append(cor.cruise_y * ramp)  # socket_y=0 so just cruise_y * ramp

        # Build boxes
        for n in range(len(pts) - 1):
            ax, az = pts[n][0], pts[n][1]
            bx, bz = pts[n+1][0], pts[n+1][1]
            start_y = y_vals[n]
            end_y = y_vals[n+1]

            direction = np.array([bx - ax, 0.0, bz - az])
            length = np.linalg.norm(direction)
            if length < 1e-6:
                continue
            direction = direction / length
            right_vec = np.cross(up, direction)
            right_norm = np.linalg.norm(right_vec)
            if right_norm < 1e-6:
                continue
            right_vec = right_vec / right_norm

            start = np.array([ax, start_y, az])
            end = np.array([bx, end_y, bz])

            edges = _box_segment_edges(start, end, right_vec, up, cor.width_m, _CORRIDOR_HEIGHT_M)
            seg_list.extend(edges)
            seg_col_list.extend([base_color] * len(edges))

    # Ring segments (unchanged from original build_wire_mesh)
    ring_list = []
    ring_col_list = []
    angles = (2.0 * math.pi) * (np.arange(RING_SEGMENTS, dtype=np.float64) / float(RING_SEGMENTS))
    next_angles = (2.0 * math.pi) * ((np.arange(RING_SEGMENTS, dtype=np.float64) + 1.0) / float(RING_SEGMENTS))
    for room in fp.rooms:
        cx, cz = float(room.map_xz[0]), float(room.map_xz[1])
        r = float(room.map_radius_m)
        y = float(room.socket_y)
        rgb = hex_to_rgb(room.map_color)
        for k in range(RING_SEGMENTS):
            t0, t1 = angles[k], next_angles[k]
            ring_list.append(np.array(
                [[cx + r * math.cos(t0), y, cz + r * math.sin(t0)],
                 [cx + r * math.cos(t1), y, cz + r * math.sin(t1)]], dtype=np.float32))
            ring_col_list.append(rgb)

    line_segments = np.stack(seg_list, 0).astype(np.float32) if seg_list else np.zeros((0, 2, 3), np.float32)
    seg_colors = np.array(seg_col_list, np.float32) if seg_col_list else np.zeros((0, 3), np.float32)
    ring_segments = np.stack(ring_list, 0).astype(np.float32) if ring_list else np.zeros((0, 2, 3), np.float32)
    ring_colors = np.array(ring_col_list, np.float32) if ring_col_list else np.zeros((0, 3), np.float32)

    return WireMesh(line_segments, seg_colors, ring_segments, ring_colors)
```

**Change in `_get_wire_resources`:** When building resources, call `_build_tunnel_mesh(fp)` instead of `build_wire_mesh(fp)`.

### §5.2 — `nav_collision.py`

**Replace `_CorridorNav`** with a new implementation that does box collision per segment.

```python
_CORRIDOR_HEIGHT_M = 3.0  # must match render_wire.py

class _CorridorNav:
    def __init__(self, fp: Floorplan):
        self._corridors = list(fp.corridors)
        self._rooms = {r.room_id: r for r in fp.rooms}
        # Pre-compute segment box bounds for fast collision lookup
        self._segments = []  # list of (corridor, seg_idx, start_xz, end_xz, y_start, y_end, forward_xz, right_xz, width, height)
        for cor in self._corridors:
            pts = cor.path_xz
            if len(pts) < 2:
                continue
            # Arc-lengths and Y heights (same as render_wire's _build_tunnel_mesh)
            seg_lens = []
            for n in range(len(pts) - 1):
                dx = pts[n+1][0] - pts[n][0]
                dz = pts[n+1][1] - pts[n][1]
                seg_lens.append(math.hypot(dx, dz))
            total_len = sum(seg_lens)
            cumulative = [0.0]
            for sl in seg_lens:
                cumulative.append(cumulative[-1] + sl)
            y_vals = []
            for i in range(len(pts)):
                u = cumulative[i] / total_len if total_len > 0 else 0.0
                ramp = min(u / 0.30, (1.0 - u) / 0.30, 1.0) if u <= 1.0 else 1.0
                y_vals.append(cor.cruise_y * max(0.0, min(1.0, ramp)))
            for n in range(len(pts) - 1):
                ax, az = pts[n][0], pts[n][1]
                bx, bz = pts[n+1][0], pts[n+1][1]
                dx, dz = bx - ax, bz - az
                seg_len = math.hypot(dx, dz)
                if seg_len < 1e-6:
                    continue
                forward = (dx / seg_len, dz / seg_len)
                right = (-forward[1], forward[0])
                self._segments.append((
                    cor, n, (ax, az), (bx, bz),
                    y_vals[n], y_vals[n+1],
                    forward, right, cor.width_m, _CORRIDOR_HEIGHT_M
                ))

    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3:
        tx = start[0] + delta[0]
        ty = start[1] + delta[1]
        tz = start[2] + delta[2]

        # Find the segment the player's target position is closest to
        best = None
        best_dist = float('inf')
        for seg in self._segments:
            cor, seg_idx, s_xz, e_xz, y_s, y_e, fwd, rgt, w, h = seg
            # Project target onto segment centerline
            px, pz = tx, tz
            ax, az = s_xz; bx, bz = e_xz
            dx, dz = bx - ax, bz - az
            seg_len2 = dx*dx + dz*dz
            if seg_len2 < 1e-9:
                t_param = 0.0
            else:
                t_param = ((px-ax)*dx + (pz-az)*dz) / seg_len2
                t_param = max(0.0, min(1.0, t_param))
            cx = ax + dx * t_param
            cz = az + dz * t_param
            dist = math.hypot(px - cx, pz - cz)
            if dist < best_dist:
                best_dist = dist
                best = (cor, seg_idx, s_xz, e_xz, y_s, y_e, fwd, rgt, w, h, t_param)

        if best is None:
            return (tx, ty, tz)

        cor, seg_idx, s_xz, e_xz, y_s, y_e, fwd, rgt, w, h, t_param = best
        ax, az = s_xz; bx, bz = e_xz

        # Compute centerline point and floor Y at that point
        cx = ax + (bx - ax) * t_param
        cz = az + (bz - az) * t_param
        floor_y = y_s + (y_e - y_s) * t_param

        # Clamp X (lateral distance from centerline)
        lateral = (tx - cx) * rgt[0] + (tz - cz) * rgt[1]
        half_w = w / 2.0
        if lateral > half_w:
            clamped_lat = half_w
        elif lateral < -half_w:
            clamped_lat = -half_w
        else:
            clamped_lat = lateral

        # Clamp Y
        clamped_y = ty
        if clamped_y < floor_y:
            clamped_y = floor_y
        if clamped_y > floor_y + h:
            clamped_y = floor_y + h

        # Z is NOT clamped — player walks freely forward/back through the chain
        # Reconstruct world position from clamped lateral
        fx = cx + clamped_lat * rgt[0]
        fz = cz + clamped_lat * rgt[1]

        return (fx, clamped_y, fz)

    def nearest_panel(self, ray, max_dist):
        return None  # corridors have no panels

    def door_at(self, point):
        return None  # socket-entry handles room arrival; boxes have no side doors
```

### §5.3 — `guidelines.py`

**Implement `_gl_draw_strip`:**

```python
def _gl_draw_strip(view: ViewMatrix, points_xyz: list[Vec3],
                   color_rgb: Vec3, alpha: float) -> None:
    if not HAVE_GL or len(points_xyz) < 2:
        return
    try:
        import moderngl
        ctx = moderngl.get_context()
    except Exception:
        return

    from shaders import wire_program
    prog = wire_program(ctx)
    if prog is None:
        return

    pts = np.array(points_xyz, dtype=np.float32)
    vbo = ctx.buffer(pts.tobytes())
    vao = ctx.vertex_array(prog, [(vbo, '3f', 'in_pos')])

    ctx.enable(moderngl.DEPTH_TEST)
    ctx.depth_func = "<="
    ctx.depth_mask = True
    ctx.disable(moderngl.BLEND)

    try:
        vp = np.ascontiguousarray(view, dtype=np.float32).T
        prog['u_mvp'].write(vp.tobytes())
    except Exception:
        pass

    # Set per-strip color via a uniform. If the simple wire_program doesn't
    # have a u_color uniform, set the vertex color attribute for the whole strip.
    # For LINE_STRIP with no per-vertex color input, we need a uniform.
    # The simple WIRE_FS outputs v_color which comes from in_color via the VS.
    # We can't set a uniform for color in the simple shader. 
    # Instead, duplicate the color per vertex and upload as in_color:
    colors = np.tile(np.array([*color_rgb], dtype=np.float32), (len(pts), 1))
    vbo_c = ctx.buffer(colors.tobytes())
    vao_colored = ctx.vertex_array(prog, [
        (vbo, '3f', 'in_pos'),
        (vbo_c, '3f', 'in_color')
    ])

    try:
        vp = np.ascontiguousarray(view, dtype=np.float32).T
        prog['u_mvp'].write(vp.tobytes())
    except Exception:
        pass

    vao_colored.render(mode=moderngl.LINE_STRIP)

    try:
        vao_colored.release()
    except Exception:
        pass
```

**Fix guide-line floor height** in `draw_guidelines`: Instead of using `_gl_floor_y(room)` which returns `socket_y + 0.02`, compute the corridor floor Y at each route point using the same ramp interpolation as the box geometry. Add 0.02m epsilon so the line sits just above the floor.

```python
def _compute_floor_y_at_xz(fp: Floorplan, x: float, z: float) -> float:
    """Find which corridor segment contains (x,z) and return its floor Y."""
    for cor in fp.corridors:
        pts = cor.path_xz
        if len(pts) < 2:
            continue
        # Compute arc-lengths (simplified; prefer matching render_wire exactly)
        seg_lens = []
        for n in range(len(pts) - 1):
            dx = pts[n+1][0] - pts[n][0]
            dz = pts[n+1][1] - pts[n][1]
            seg_lens.append(math.hypot(dx, dz))
        total_len = sum(seg_lens)
        if total_len < 1e-6:
            continue
        cumulative = [0.0]
        for sl in seg_lens:
            cumulative.append(cumulative[-1] + sl)

        for n in range(len(pts) - 1):
            ax, az = pts[n][0], pts[n][1]
            bx, bz = pts[n+1][0], pts[n+1][1]
            dx, dz = bx - ax, bz - az
            seg_len2 = dx*dx + dz*dz
            if seg_len2 < 1e-9:
                continue
            # Project (x,z) onto segment
            t = ((x-ax)*dx + (z-az)*dz) / seg_len2
            if t < -0.1 or t > 1.1:  # not on this segment (with tolerance)
                continue
            t = max(0.0, min(1.0, t))
            # Cumulative arc-length at the projected point
            arc = cumulative[n] + t * seg_lens[n]
            u = arc / total_len
            ramp = min(u / 0.30, (1.0 - u) / 0.30, 1.0)
            ramp = max(0.0, min(1.0, ramp))
            return cor.cruise_y * ramp
    return 0.0  # fallback: socket_y
```

Then in `draw_guidelines`, use this for route point Y:
```python
route3d = [(x, _compute_floor_y_at_xz(fp, x, z) + 0.02, z) for (x, z) in route2d]
```

### §5.4 — `app.py`

**Corridor dispatch changes:**

```python
if state.mode == "corridor":
    # Render the FULL floorplan with tunnel mesh — not the single-corridor filter
    render_fp = pack.floorplan
    def _gl(v, p, aspect):
        vp = np.ascontiguousarray(p @ v, dtype=np.float32)
        draw_guidelines(vp, render_fp, targets)
    render_mode_a(ctx, window, view, proj, render_fp, state,
                  guidelines_fn=_gl, targets=targets)
```

**Target selection for guide-lines in corridor mode:** Use the corridor's source room as `current` for `select_targets`. Determine the corridor the player is traveling from `travel_edge_id`:

```python
# Near where targets is computed (~line 440):
if outcome.recompute_guidelines or state.mode == "corridor":
    if state.mode == "corridor" and outcome.travel_edge_id is not None:
        # Player just entered corridor — use source room as current
        parts = outcome.travel_edge_id.split(".to.")
        src_cand = parts[0].replace("edge.", "") if len(parts) == 2 else None
        gcur = src_cand if src_cand else _start_node(pack)
    else:
        gcur = state.current_room_id or _start_node(pack)
    try:
        targets = select_targets(pack.floorplan, gcur, state.cleared, cfg) \
            if gcur is not None else []
    except Exception:
        targets = []
```

Keep `_single_corridor_floorplan` and `_active_corridor` plumbing for corridor nav (the nav still uses the single corridor), but stop using them as the render source.

---

## §6 — THE SHADER (what you're feeding)

The wireframe shader you feed edge segments to is `wire_quad_program(ctx)` from `shaders.py`. It uses:

**Vertex shader (WIREQ_VS):** Inputs `in vec3 in_pos`, `in vec3 in_color`. Outputs `g_wdist = clip.w` (view-space distance) and `g_color`.

**Geometry shader (WIREQ_GS):** Takes `lines` input, emits `triangle_strip` (max 4 vertices). Expands each 2-point line segment into 2 camera-facing triangles. Uses uniforms: `u_mvp` (mat4, world→clip), `u_aspect` (float, window width/height), `u_half_px` (float, 0.0025).

**Fragment shader (WIREQ_FS):** Distance-dimming. `t = clamp((f_wdist - u_dim_near) / (u_dim_far - u_dim_near), 0, 1)`. `bright = mix(1.0, u_grey_floor, t)`. Outputs `f_color * bright`.

Uniforms set in `_draw_wire`:
- `u_mvp` = byte buffer of `transpose(proj @ view)` — world-to-clip matrix
- `u_aspect` = window width/height
- `u_half_px` = 0.0025
- `u_dim_near` = 8.0 (full white within this view-distance)
- `u_dim_far` = 220.0 (reaches grey floor by here)
- `u_grey_floor` = 0.22 (never pure black)

**The segment format you feed:** `(N, 2, 3)` float32 numpy array — N line segments, each is [start_xyz, end_xyz]. Plus `(N, 3)` RGB colors per segment. All white `(1.0, 1.0, 1.0)` for corridor box edges.

**The simple wire_program(ctx)** for guide-lines: `WIRE_VS` + `WIRE_FS`. Inputs `in_pos` (vec3), `in_color` (vec3). Draw as `LINE_STRIP`. Has `u_mvp` uniform. No dimming. Bright, solid color.

---

## §7 — THE CAMERA (you don't touch this)

The camera is untouched. On room exit, `gameplay.py` places `state.pos` in floorplan world coordinates 2m toward the corridor's far end. The existing `camera.update(state.heading_rad, pitch, state.pos, dt)` in `app.py` (line 459) builds the view matrix from that position. The `perspective()` call (line 465) builds the projection matrix. Together they produce the world-to-clip transform that the wireframe shader uses.

Because the corridor box edges are placed in floorplan world coordinates at true heights, and the camera renders from the player's world position, the player is inside the box chain immediately on exit.

---

## §8 — EXISTING CODE THAT STAYS UNCHANGED

- `gameplay.py` — door exit (places player at map_xz + 2m toward far end), door entry (socket detection within 1.0m of target room's map_xz). All unchanged.
- `state.py` — game state. Unchanged.
- `camera.py` — view matrix. Unchanged.
- `render_room.py` — room rendering. Unchanged.
- `shaders.py` — all shader sources. Unchanged (you use the existing programs).
- `raw_models.py` — all contracts. Unchanged.
- `assets.py` — pack loading. Unchanged.
- `readmode.py` — read overlay. Unchanged.

---

## §9 — WHAT NOT TO DO

1. **Do NOT write a design document.** You write code. Python files.
2. **Do NOT defer collision.** The player walks inside solid boxes with walls, floor, and ceiling. If you write a tunnel renderer with no collision, you are Parent 20.
3. **Do NOT render a flat 2D map.** The tunnel is a 3D box chain. If your output looks like circles and lines on a plane, you are Parent 18.
4. **Do NOT render only one box.** Multiple boxes per corridor, end-to-end.
5. **Do NOT ask DeepSeek to confirm things already pasted to you.** The shader source, the contract fields, the existing functions — they are all in this handoff and the launch files.
6. **Do NOT offer Nir menus of options.** The spec is the spec. Read it and build what it says.
7. **Do NOT claim you lost Nir's text and demand re-pastes.**
8. **Do NOT invent new contracts or change frozen data models.** You work within the existing `WireMesh`, `Floorplan`, `Corridor`, `FloorRoom`, `DoorRT` contracts. If you need a new function, add it. If you need a new field on a frozen model, you don't — use module constants.
9. **Do NOT write "DeepSeek integrates this" or "DeepSeek confirms the API."** You confirm the API. You write the code that compiles. You are the implementer.
10. **Do NOT make guide-lines sit at y=0.02 on the flat ground plane.** They ride the corridor floor inside the tunnel.

---

## §10 — ACCEPTANCE (what Nir verifies)

1. Exit a room door → player stands inside a 3D wireframe box tunnel.
2. The tunnel is a chain of white box edges, bright up close, dimming to grey down the tunnel.
3. Looking around: box edges form a rectangular section — floor edges below, ceiling edges above, vertical rails on the sides. The empty faces show the distant graph through them.
4. The floor has ≤3 colored guide-lines with arrowheads pointing to destinations.
5. Walking forward: the player moves through the box chain toward the far end.
6. At the far end: walking within 1.0m of the target room's `map_xz` triggers room entry.
7. Crossing corridors: one box chain at `over_y` (higher), another at `under_y` (lower) — depth-test makes the bridge occlude the underpass correctly.
8. Works for any connected room pair in the Principia pack.

---

## §11 — HOW TO GET MORE INFORMATION

Ask DeepSeek via Nir for exact verbatim sections. Files available:
- `quake/render_wire.py` — full wireframe renderer
- `quake/render_room.py` — solid room rendering (reference for box geometry)
- `quake/guidelines.py` — select_targets, _route_xz, _arrowhead_xz, draw_guidelines, _gl_draw_strip
- `quake/nav_collision.py` — _RoomNav and _CorridorNav, box collision
- `quake/map/raw_models.py` — Corridor, Crossing, Floorplan, FloorRoom, DoorRT, BuildConfig
- `quake/gameplay.py` — door exit/entry transitions
- `quake/app.py` — render dispatch and camera wiring
- `quake/shaders.py` — wire_quad_program, wire_program, all GLSL sources
- `quake/contracts.py` — shared type imports

---

## §12 — TALK FIRST

State your understanding of the problem, which files you will write, what each file will contain. **Wait for Nir's confirmation before writing code.**
