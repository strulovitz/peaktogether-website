I'm sorry, Nir. Plainly, first, unburied: I'm sorry. I echoed "visual only" back into the record instead of checking it against your words, and that's exactly the kind of drift I exist to prevent. And you're right about the audio question too — it should never have existed. The path is the path. However the players made it — tilt, turn, slide — the totem walks it and hears each neighborhood by the same rules as everywhere else. Your one sentence is the whole law, and it's now burned in.

No more menus, no more questions. Here is the work — all four files, complete.

## Canon signatures for core/slicing.py (DeepSeek: record these)

```
eval_heights(surface_fn, X, Y) -> np.ndarray          # vectorized-or-loop f
plane_anchor_z(surface_fn, plane) -> float            # z0 = f(cx, cy)
plane_normal(plane) -> (nx, ny, nz)                   # unit normal, tilted
plane_axes(plane) -> (d, up)                          # in-plane frame (pane geometry)
clip_hinge(plane, domain) -> (tmin, tmax) | None      # old slab clip, preserved
slice_components(surface_fn, plane, domain, grid_step=0.25) -> list  # [(points, closed)], primary first
resample_path(points, step) -> list                   # arc-length; exact endpoint kept
walk_path(surface_fn, plane, domain, step=config.RING_WIDTH, grid_step=0.25) -> list
```

`game_state._build_slice_path` becomes one line: `return slicing.walk_path(self._surface, self._plane, self._spec.domain)`.

## core/slicing.py

```python
"""
LOOM2 -- core/slicing.py
THE ONE TRUE CUT. Shared pure math for the Glass Blade: the intersection of
the (possibly tilted) slicing plane with z = f(x, y), as ordered ground paths.
Imported by BOTH core.game_state (the procession) and graphics.slice_mode
(the drawn curve) -- one implementation, byte-match by construction.
Blessed amendment, tilt ruling 2026-07-08: TILT IS REAL GEOMETRY.
Allowed imports: math, numpy, config, core.types. Nothing else.

Plane definition (canon):
  hinge  = horizontal line through (cx, cy) at heading yaw_deg
  anchor z0 = f(cx, cy)   -- the blade pivots on the ground point under it
  normal n  = (-sin(yaw)cos(tilt), cos(yaw)cos(tilt), sin(tilt)), unit
  cut    = zero level set of g(x,y) = n . ((x, y, f(x,y)) - (cx, cy, z0))
At tilt = 0, g is linear in the horizontal offset, so marching squares
reproduces the old straight vertical transect EXACTLY (regression guard).
"""
import math
import numpy as np
import config

_EPS = 1e-9
_KEY_DECIMALS = 6   # endpoint quantization for segment chaining

# marching-squares segment table: edges 0=bottom 1=right 2=top 3=left,
# case bit0..bit3 = (g00, g10, g11, g01) > 0. Cases 5/10 resolved by center.
_SEG_TABLE = {1: (3, 0), 2: (0, 1), 3: (3, 1), 4: (1, 2), 6: (0, 2),
              7: (3, 2), 8: (2, 3), 9: (0, 2), 11: (1, 2), 12: (3, 1),
              13: (0, 1), 14: (3, 0)}


def eval_heights(surface_fn, X, Y):
    """f over numpy arrays; per-point fallback if surface_fn is not
    vectorized ('vectorization allowed', never guaranteed)."""
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    try:
        Z = np.asarray(surface_fn(X, Y), dtype=np.float64)
        if Z.shape == X.shape:
            return Z
    except Exception:
        pass
    flat = [float(surface_fn(float(x), float(y)))
            for x, y in zip(X.ravel(), Y.ravel())]
    return np.array(flat, dtype=np.float64).reshape(X.shape)


def plane_anchor_z(surface_fn, plane) -> float:
    """z0 = f(cx, cy): the cut always passes through this ground point."""
    return float(eval_heights(surface_fn,
                              np.array([plane.cx]), np.array([plane.cy]))[0])


def plane_normal(plane):
    """Unit normal of the tilted plane (canon formula in the header)."""
    yaw, tilt = math.radians(plane.yaw_deg), math.radians(plane.tilt_deg)
    return (-math.sin(yaw) * math.cos(tilt),
            math.cos(yaw) * math.cos(tilt),
            math.sin(tilt))


def plane_axes(plane):
    """Orthonormal in-plane frame: d = horizontal hinge direction,
    up = tilted 'up'. Used for pane geometry, never for the path math."""
    yaw, tilt = math.radians(plane.yaw_deg), math.radians(plane.tilt_deg)
    d = (math.cos(yaw), math.sin(yaw), 0.0)
    up = (math.sin(yaw) * math.sin(tilt),
          -math.cos(yaw) * math.sin(tilt),
          math.cos(tilt))
    return d, up


def clip_hinge(plane, domain):
    """Slab-clip the hinge line to the domain rectangle. Returns
    (tmin, tmax) along d from (cx, cy), or None. (The old straight-transect
    clip, preserved: it is still the pane's horizontal extent.)"""
    xmin, xmax, ymin, ymax = domain
    dx = math.cos(math.radians(plane.yaw_deg))
    dy = math.sin(math.radians(plane.yaw_deg))
    tmin, tmax = -1e18, 1e18
    for c, d, lo, hi in ((plane.cx, dx, xmin, xmax),
                         (plane.cy, dy, ymin, ymax)):
        if abs(d) < _EPS:
            if not lo <= c <= hi:
                return None
            continue
        t0, t1 = (lo - c) / d, (hi - c) / d
        if t0 > t1:
            t0, t1 = t1, t0
        tmin, tmax = max(tmin, t0), min(tmax, t1)
    return None if tmax <= tmin else (tmin, tmax)


def _cell_segments(g, xs, ys):
    """Marching squares: line segments of the zero set of g, per grid cell."""
    pos = (g > 0.0)
    case = (pos[:-1, :-1].astype(np.int8) | (pos[:-1, 1:] << 1)
            | (pos[1:, 1:] << 2) | (pos[1:, :-1] << 3))
    segs = []
    for j, i in np.argwhere((case != 0) & (case != 15)):
        g00, g10 = g[j, i], g[j, i + 1]
        g01, g11 = g[j + 1, i], g[j + 1, i + 1]
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]

        def edge(e):
            if e == 0:
                t = g00 / (g00 - g10); return (x0 + t * (x1 - x0), y0)
            if e == 1:
                t = g10 / (g10 - g11); return (x1, y0 + t * (y1 - y0))
            if e == 2:
                t = g01 / (g01 - g11); return (x0 + t * (x1 - x0), y1)
            t = g00 / (g00 - g01)
            return (x0, y0 + t * (y1 - y0))

        c = int(case[j, i])
        if c in (5, 10):    # ambiguous saddle cell: center sign decides
            center = 0.25 * (g00 + g10 + g11 + g01)
            if c == 5:
                pairs = ((0, 1), (2, 3)) if center > 0 else ((3, 0), (1, 2))
            else:
                pairs = ((3, 0), (1, 2)) if center > 0 else ((0, 1), (2, 3))
        else:
            pairs = (_SEG_TABLE[c],)
        for ea, eb in pairs:
            segs.append((edge(ea), edge(eb)))
    return segs


def _chain(segs):
    """Chain segments into polylines. Returns [(points, closed)]."""
    def key(p):
        return (round(p[0], _KEY_DECIMALS), round(p[1], _KEY_DECIMALS))
    adj = {}
    for si, (a, b) in enumerate(segs):
        adj.setdefault(key(a), []).append((si, 0))
        adj.setdefault(key(b), []).append((si, 1))
    used = [False] * len(segs)

    def walk(si, start_end):
        used[si] = True
        a, b = segs[si]
        pts = [a, b] if start_end == 0 else [b, a]
        while True:
            candidates = [se for se in adj.get(key(pts[-1]), ())
                          if not used[se[0]]]
            if not candidates:
                return pts
            sj, e = candidates[0]
            used[sj] = True
            a2, b2 = segs[sj]
            pts.append(b2 if e == 0 else a2)

    paths = []
    for k, lst in adj.items():          # open curves first (degree-1 ends)
        if len(lst) == 1 and not used[lst[0][0]]:
            paths.append((walk(*lst[0]), False))
    for si in range(len(segs)):         # remaining: closed loops
        if not used[si]:
            pts = walk(si, 0)
            pts.append(pts[0])
            paths.append((pts, True))
    return paths


def slice_components(surface_fn, plane, domain, grid_step=0.25):
    """THE CUT. Ordered components, primary (walked) component FIRST --
    the one passing nearest the anchor (with z0 = f(cx,cy) it passes
    through it). Each component is an ordered [(x, y), ...]; closed loops
    repeat their first point last. [] if the blade misses the land."""
    xmin, xmax, ymin, ymax = domain
    nx = max(2, int(round((xmax - xmin) / grid_step)) + 1)
    ny = max(2, int(round((ymax - ymin) / grid_step)) + 1)
    xs, ys = np.linspace(xmin, xmax, nx), np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(xs, ys)
    Z = eval_heights(surface_fn, X, Y)
    z0 = plane_anchor_z(surface_fn, plane)
    nxv, nyv, nzv = plane_normal(plane)
    g = nxv * (X - plane.cx) + nyv * (Y - plane.cy) + nzv * (Z - z0)
    g = np.where(g == 0.0, 1e-12, g)     # no exact zeros: degeneracy guard
    segs = _cell_segments(g, xs, ys)
    if not segs:
        return []
    dxh = math.cos(math.radians(plane.yaw_deg))
    dyh = math.sin(math.radians(plane.yaw_deg))
    comps = []
    for pts, closed in _chain(segs):
        if len(pts) < 2:
            continue
        if closed:                       # start loops nearest the anchor
            ring = pts[:-1]
            k = min(range(len(ring)), key=lambda i:
                    (ring[i][0] - plane.cx) ** 2 + (ring[i][1] - plane.cy) ** 2)
            pts = ring[k:] + ring[:k] + [ring[k]]
            sx, sy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        else:
            sx, sy = pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]
        if sx * dxh + sy * dyh < 0.0:    # stable procession direction
            pts = pts[::-1]
        d2 = min((px - plane.cx) ** 2 + (py - plane.cy) ** 2 for px, py in pts)
        comps.append((d2, pts, closed))
    comps.sort(key=lambda t: t[0])
    return [(pts, closed) for _, pts, closed in comps]


def resample_path(points, step):
    """Arc-length resample in the ground plane: samples at 0, step, 2*step,
    ... and ALWAYS the exact final point (the old transect's endpoint rule)."""
    if len(points) < 2:
        return list(points)
    out = [points[0]]
    px, py = points[0]
    left = step
    for qx, qy in points[1:]:
        seg = math.hypot(qx - px, qy - py)
        while seg >= left - _EPS and seg > _EPS:
            f = left / seg
            px, py = px + f * (qx - px), py + f * (qy - py)
            out.append((px, py))
            seg = math.hypot(qx - px, qy - py)
            left = step
        left -= seg
        px, py = qx, qy
    if math.hypot(points[-1][0] - out[-1][0],
                  points[-1][1] - out[-1][1]) > 1e-6:
        out.append(points[-1])
    return out


def walk_path(surface_fn, plane, domain,
              step=config.RING_WIDTH, grid_step=0.25):
    """game_state's ONE call: the procession itinerary. Primary component,
    one stop per `step`, exact endpoint kept. [] if the blade misses.
    At tilt = 0: entry point, stops every step, exact exit -- the old law."""
    comps = slice_components(surface_fn, plane, domain, grid_step)
    return resample_path(comps[0][0], step) if comps else []
```

## data/shaders/glass.vert

```glsl
#version 330
// LOOM2 glass shader -- owned by graphics/slice_mode.py (Parent E)
uniform mat4 u_mvp;
in vec3 in_pos;
in vec2 in_aux;   // x = arc length along the curve, y = baked Gouraud light
out vec3 v_world;
out vec2 v_aux;
void main() {
    v_world = in_pos;
    v_aux = in_aux;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
```

## data/shaders/glass.frag

```glsl
#version 330
// modes: 0 pane (unlit A1/B1 tint) | 1 Fresnel rim (F4) | 2 ribbon solid (C1)
//        3 ribbon dashed (occluded pass) | 4 bead (Gouraud x breath)
//        5 bead ghost (occluded pass)
uniform int   u_mode;
uniform vec4  u_color;
uniform vec3  u_cam_pos;
uniform vec3  u_normal;
uniform float u_dash;
in vec3 v_world;
in vec2 v_aux;
out vec4 f_color;
void main() {
    if (u_mode == 1) {
        vec3  v  = normalize(u_cam_pos - v_world);
        float fr = pow(1.0 - abs(dot(v, normalize(u_normal))), 3.0);
        f_color = vec4(u_color.rgb * (0.25 + 0.75 * fr),
                       u_color.a * (0.30 + 0.70 * fr));
    } else if (u_mode == 3) {
        if (fract(v_aux.x / u_dash) > 0.5) discard;   // dashed where hidden
        f_color = u_color;
    } else if (u_mode >= 4) {
        f_color = vec4(u_color.rgb * v_aux.y, u_color.a);
    } else {
        f_color = u_color;                            // 0 pane, 2 ribbon
    }
}
```

## graphics/slice_mode.py

```python
"""
LOOM2 -- graphics/slice_mode.py
THE GLASS BLADE (SUTRAS Part 6; tilt ruling 2026-07-08: TILT IS REAL).
Visual + path math; NO audio calls.
Allowed imports: math, numpy, moderngl, config, core.types,
core.slicing (blessed shared-cut amendment).
# CONTRACT-NOTE: stdlib `time` imported for the bead's ~3 s emissive breath
# (mirrors the totem's un-synced breathing; draw() receives no clock).
Nir's locked look: A1 cool glass-cyan pane / B1 unlit tint / C1 warm HDR gold
ribbon / D2 ribbon, no fill / bead-on-the-wire (bored sphere threaded on the
ribbon, ~3 s breath, no drop-line) / F4 Fresnel rim frame / dashed curve where
terrain hides it + ghost bead when hidden / H2 constant pane height.
"""
import math
import time
import numpy as np
import config
from core.types import SlicePlane
from core import slicing

_LIFT = 0.05                 # Parent D's anti-z-fight lift for draped geometry
_FINE_STEP = 0.25            # fine sampling of the drawn curve
_RIBBON_W = 0.06
_DASH = 0.30                 # dash period (world units of arc length)
_PANE_RGBA = (0.55, 0.80, 0.90, 0.20)   # A1 cool glass-cyan, unlit (B1)
_RIM_RGBA = (0.70, 0.92, 1.00, 0.55)    # Fresnel-modulated in shader (F4)
_GOLD = (1.15, 0.95, 0.45, 1.00)        # C1: just above the 0.80 bloom pass
_GOLD_DIM = (0.55, 0.45, 0.22, 0.40)    # occluded/dashed pass
_BEAD_BASE = (0.85, 0.88, 0.95)
_BEAD_R = 0.10
_HOLE_ANG = 0.45             # hole half-angle (rad) bored around the wire axis
_BREATH_SEC = 3.0
_PANE_MARGIN = 0.4
_RIM_W = 0.12
_SUN = (0.45, 0.28, 0.85)    # Parent D's sun
_AMBIENT = 0.38


class GlassBlade:
    def __init__(self, renderer):
        self._ctx = renderer.ctx
        self._prog = renderer.program("glass")
        self._plane = None
        self._domain = None
        self._surface_fn = None
        self._walk_stop = None
        self._comps = []          # [(points, closed)] fine components
        self._stops = []          # coarse procession stops (bead positions)
        self._zrange = None       # (z_lo, z_hi) cached per domain (H2)
        self._cut_key = None
        self._vp_bytes = None
        self._vaos = {}           # name -> (vbo, vao, nverts)
        self._bead_dirty = True
        self._warned = False
        self._bead_v, self._bead_n = self._build_bead_local()

    # ---------------- contract methods ----------------

    def update_plane(self, plane: SlicePlane) -> None:
        """Store current plane pose (moved/rotated by input in SLICE mode)."""
        p = SlicePlane(plane.cx, plane.cy, plane.yaw_deg,
                       plane.tilt_deg, plane.visible)
        old = self._plane
        if (old is None or (old.cx, old.cy, old.yaw_deg, old.tilt_deg)
                != (p.cx, p.cy, p.yaw_deg, p.tilt_deg)):
            self._cut_key = None          # pose changed: geometry is stale
            self._bead_dirty = True
        self._plane = p

    def intersection_path(self, surface_fn, domain: tuple,
                          step: float = 0.25) -> list:
        """THE CONTRACT THE WHOLE FEATURE HANGS ON (tilt ruling applied):
        ordered [(x, y), ...] of the PRIMARY cut component -- the true
        intersection of the tilted plane with z=f(x,y), via core.slicing
        (the same math game_state walks). [] if the blade misses."""
        self._surface_fn = surface_fn
        self.set_domain(domain)
        if self._plane is None:
            return []
        comps = self._cut()
        return slicing.resample_path(comps[0][0], step) if comps else []

    def draw(self, view_proj, surface_fn) -> None:
        """Pane + Fresnel rim + glowing gold ribbon (dashed where terrain
        hides it) + breathing bead threaded on the wire (ghost where hidden)."""
        if self._plane is None or not self._plane.visible:
            return
        self._surface_fn = surface_fn
        if self._domain is None:
            if not self._warned:
                print("slice_mode: no domain set -- call set_domain()")
                self._warned = True
            return
        vp = np.asarray(view_proj, dtype=np.float64).reshape(4, 4)
        vp_bytes = vp.tobytes()
        cam = self._cam_pos(vp)
        if self._cut_key is None or vp_bytes != self._vp_bytes:
            self._rebuild_geometry(cam)
            self._vp_bytes = vp_bytes
        if self._bead_dirty:
            self._rebuild_bead()
        self._prog["u_mvp"].write(
            np.ascontiguousarray(vp.T, dtype="f4").tobytes())
        self._prog["u_cam_pos"].value = cam
        self._prog["u_normal"].value = slicing.plane_normal(self._plane)
        self._prog["u_dash"].value = _DASH

        ctx, fbo = self._ctx, self._ctx.fbo
        old_mask = fbo.depth_mask
        fbo.depth_mask = False
        ctx.depth_func = "<"
        self._pass("pane", 0, _PANE_RGBA)
        self._pass("rim", 1, _RIM_RGBA)
        ctx.depth_func = ">"                       # occluded-only passes
        self._pass("ribbon", 3, _GOLD_DIM)         # dashed where hidden
        ctx.depth_func = "<"
        self._pass("ribbon", 2, _GOLD)             # solid where seen
        if self._walk_stop is not None and self._stops:
            breath = 0.5 * (1.0 + math.sin(
                2.0 * math.pi * time.time() / _BREATH_SEC))
            k = 0.70 + 0.55 * breath               # peak crosses bloom pass
            solid = (_BEAD_BASE[0] * k, _BEAD_BASE[1] * k,
                     _BEAD_BASE[2] * k, 1.0)
            ghost = (_BEAD_BASE[0] * 0.8, _BEAD_BASE[1] * 0.8,
                     _BEAD_BASE[2] * 0.8, 0.35)
            ctx.depth_func = ">"
            self._pass("bead", 5, ghost)           # translucent where hidden
            ctx.depth_func = "<"
            fbo.depth_mask = True                  # bead self-occlusion
            self._pass("bead", 4, solid)
        fbo.depth_mask = old_mask                  # restore as found
        ctx.depth_func = "<"

    # ---------------- additive setters (blessed amendments) ----------------

    def set_domain(self, domain: tuple) -> None:
        """Scene domain (xmin,xmax,ymin,ymax); main wires at scene build."""
        if domain != self._domain:
            self._domain = domain
            self._zrange = None
            self._cut_key = None

    def set_walk_stop(self, index_or_none) -> None:
        """Current procession stop index (from game_state.snapshot via main)."""
        if index_or_none != self._walk_stop:
            self._walk_stop = index_or_none
            self._bead_dirty = True

    # ---------------- internals ----------------

    def _cut(self):
        key = (self._plane.cx, self._plane.cy, self._plane.yaw_deg,
               self._plane.tilt_deg, self._domain)
        if key != self._cut_key:
            self._comps = slicing.slice_components(
                self._surface_fn, self._plane, self._domain, _FINE_STEP)
            self._stops = (slicing.resample_path(
                self._comps[0][0], config.RING_WIDTH)
                if self._comps else [])
            self._cut_key = key
            self._bead_dirty = True
        return self._comps

    @staticmethod
    def _cam_pos(vp):
        """Eye point from the VP matrix: q = inv(VP) @ (0,0,1,0)."""
        try:
            q = np.linalg.inv(vp) @ np.array([0.0, 0.0, 1.0, 0.0])
            if abs(q[3]) > 1e-12:
                return (float(q[0] / q[3]), float(q[1] / q[3]),
                        float(q[2] / q[3]))
        except np.linalg.LinAlgError:
            pass
        return (0.0, -10.0, 10.0)

    def _make_vao(self, name, verts):
        """(re)build one '3f 2f' (in_pos, in_aux) triangle VAO."""
        if name in self._vaos:
            vbo, vao, _ = self._vaos.pop(name)
            vao.release(); vbo.release()
        if len(verts) == 0:
            return
        data = np.asarray(verts, dtype="f4")
        vbo = self._ctx.buffer(data.tobytes())
        vao = self._ctx.vertex_array(
            self._prog, [(vbo, "3f 2f", "in_pos", "in_aux")])
        self._vaos[name] = (vbo, vao, len(data) // 5)

    def _pass(self, name, mode, color):
        entry = self._vaos.get(name)
        if entry is None:
            return
        self._prog["u_mode"].value = mode
        self._prog["u_color"].value = color
        entry[1].render()

    def _rebuild_geometry(self, cam):
        self._cut()
        self._make_vao("pane", self._pane_verts())
        self._make_vao("rim", self._rim_verts())
        self._make_vao("ribbon", self._ribbon_verts(cam))

    def _z_range(self):
        """H2: constant pane height -- the scene's global z-range, cached."""
        if self._zrange is None:
            xmin, xmax, ymin, ymax = self._domain
            X, Y = np.meshgrid(np.linspace(xmin, xmax, 25),
                               np.linspace(ymin, ymax, 25))
            Z = slicing.eval_heights(self._surface_fn, X, Y)
            self._zrange = (float(Z.min()) - _PANE_MARGIN,
                            float(Z.max()) + _PANE_MARGIN)
        return self._zrange

    def _pane_corners(self):
        """4 corners (2x2 in (t, w) plane coords) or None if off-domain."""
        clip = slicing.clip_hinge(self._plane, self._domain)
        if clip is None:
            return None
        tmin, tmax = clip
        z_lo, z_hi = self._z_range()
        z0 = slicing.plane_anchor_z(self._surface_fn, self._plane)
        d, up = slicing.plane_axes(self._plane)
        ct = max(math.cos(math.radians(self._plane.tilt_deg)), 0.5)
        w_lo, w_hi = (z_lo - z0) / ct, (z_hi - z0) / ct
        p0 = np.array([self._plane.cx, self._plane.cy, z0])
        d, up = np.array(d), np.array(up)
        return [[p0 + t * d + w * up for w in (w_lo, w_hi)]
                for t in (tmin, tmax)], (tmin, tmax, w_lo, w_hi, p0, d, up)

    @staticmethod
    def _quad(a, b, c, d):
        """Two tris for quad a-b-d-c (aux zeros)."""
        z = (0.0, 0.0)
        return [*a, *z, *b, *z, *c, *z, *b, *z, *d, *z, *c, *z]

    def _pane_verts(self):
        pc = self._pane_corners()
        if pc is None:
            return []
        (c00, c01), (c10, c11) = pc[0]
        return self._quad(c00, c10, c01, c11)

    def _rim_verts(self):
        """Thick parallelogram circumference, inset _RIM_W, in the pane."""
        pc = self._pane_corners()
        if pc is None:
            return []
        _, (tmin, tmax, w_lo, w_hi, p0, d, up) = pc
        verts = []

        def P(t, w):
            return p0 + t * d + w * up
        ti, wi = min(_RIM_W, (tmax - tmin) / 2), min(_RIM_W, (w_hi - w_lo) / 2)
        edges = (((tmin, w_lo), (tmax, w_lo), (tmin, w_lo + wi), (tmax, w_lo + wi)),
                 ((tmin, w_hi - wi), (tmax, w_hi - wi), (tmin, w_hi), (tmax, w_hi)),
                 ((tmin, w_lo), (tmin + ti, w_lo), (tmin, w_hi), (tmin + ti, w_hi)),
                 ((tmax - ti, w_lo), (tmax, w_lo), (tmax - ti, w_hi), (tmax, w_hi)))
        for a, b, c, e in edges:
            verts += self._quad(P(*a), P(*b), P(*c), P(*e))
        return verts

    def _ribbon_verts(self, cam):
        """Camera-facing gold ribbon along EVERY cut component, draped at
        z = f + lift, with arc length baked for the dashed occluded pass."""
        cam = np.asarray(cam, dtype=np.float64)
        verts = []
        for pts, _closed in self._comps:
            P = np.asarray(pts, dtype=np.float64)
            if len(P) < 2:
                continue
            z = slicing.eval_heights(self._surface_fn, P[:, 0], P[:, 1]) + _LIFT
            pos = np.column_stack([P[:, 0], P[:, 1], z])
            seg = np.hypot(*(np.diff(pos[:, :2], axis=0).T))
            s = np.concatenate([[0.0], np.cumsum(seg)])
            T = np.gradient(pos, axis=0)
            T /= (np.linalg.norm(T, axis=1, keepdims=True) + 1e-12)
            side = np.cross(T, cam - pos)
            n = np.linalg.norm(side, axis=1, keepdims=True)
            side /= np.where(n < 1e-9, 1.0, n)
            a = pos + side * (_RIBBON_W * 0.5)
            b = pos - side * (_RIBBON_W * 0.5)
            for i in range(len(pos) - 1):
                si, sj = s[i], s[i + 1]
                verts += [*a[i], si, 1.0, *b[i], si, 1.0, *a[i + 1], sj, 1.0,
                          *b[i], si, 1.0, *b[i + 1], sj, 1.0, *a[i + 1], sj, 1.0]
        return verts

    @staticmethod
    def _build_bead_local():
        """A real bead: sphere with a cylindrical hole bored through its
        diameter (local +x = the wire axis). Returns (tri_verts, tri_normals)."""
        lat = np.linspace(_HOLE_ANG, math.pi - _HOLE_ANG, 7)
        lon = np.linspace(0.0, 2.0 * math.pi, 13)
        V, N = [], []

        def ring(theta):
            return [(_BEAD_R * math.cos(theta),
                     _BEAD_R * math.sin(theta) * math.cos(ph),
                     _BEAD_R * math.sin(theta) * math.sin(ph)) for ph in lon]

        def emit(r0, r1, n0, n1):
            for i in range(len(lon) - 1):
                V.extend([r0[i], r1[i], r0[i + 1], r1[i], r1[i + 1], r0[i + 1]])
                N.extend([n0[i], n1[i], n0[i + 1], n1[i], n1[i + 1], n0[i + 1]])

        rings = [ring(t) for t in lat]
        for k in range(len(rings) - 1):        # sphere bands
            n0 = [tuple(c / _BEAD_R for c in p) for p in rings[k]]
            n1 = [tuple(c / _BEAD_R for c in p) for p in rings[k + 1]]
            emit(rings[k], rings[k + 1], n0, n1)
        rh = _BEAD_R * math.sin(_HOLE_ANG)     # inner bore wall
        xh = _BEAD_R * math.cos(_HOLE_ANG)
        bore0 = [(xh, rh * math.cos(ph), rh * math.sin(ph)) for ph in lon]
        bore1 = [(-xh, rh * math.cos(ph), rh * math.sin(ph)) for ph in lon]
        nin = [(0.0, -math.cos(ph), -math.sin(ph)) for ph in lon]
        emit(bore0, bore1, nin, nin)
        return np.asarray(V, dtype=np.float64), np.asarray(N, dtype=np.float64)

    def _rebuild_bead(self):
        self._bead_dirty = False
        if self._walk_stop is None or not self._stops:
            self._make_vao("bead", [])
            return
        i = max(0, min(int(self._walk_stop), len(self._stops) - 1))
        x, y = self._stops[i]
        j0, j1 = max(0, i - 1), min(len(self._stops) - 1, i + 1)
        p0, p1 = self._stops[j0], self._stops[j1]
        zz = slicing.eval_heights(self._surface_fn,
                                  np.array([p0[0], p1[0], x]),
                                  np.array([p0[1], p1[1], y]))
        ax = np.array([p1[0] - p0[0], p1[1] - p0[1], zz[1] - zz[0]])
        ax /= (np.linalg.norm(ax) + 1e-12)     # wire axis at this stop
        ay = np.cross([0.0, 0.0, 1.0], ax)
        if np.linalg.norm(ay) < 1e-6:
            ay = np.array([1.0, 0.0, 0.0])
        ay /= np.linalg.norm(ay)
        az = np.cross(ax, ay)
        R = np.column_stack([ax, ay, az])
        C = np.array([x, y, zz[2] + _LIFT])
        Vw = self._bead_v @ R.T + C
        Nw = self._bead_n @ R.T
        sun = np.asarray(_SUN) / np.linalg.norm(_SUN)
        light = _AMBIENT + (1.0 - _AMBIENT) * np.clip(Nw @ sun, 0.0, None)
        verts = np.column_stack(
            [Vw, np.zeros(len(Vw)), light]).astype("f4").ravel().tolist()
        self._make_vao("bead", verts)
```

## Wiring notes for DeepSeek (the complete stitch list)

1. New module `core/slicing.py` — record the canon signatures above; amend the Gita (G3.6 + G4.3) with the tilt ruling.
2. `game_state`: replace `_build_slice_path` body with `return slicing.walk_path(self._surface, self._plane, self._spec.domain)`; remove `_WALK_STEP` and the tilt "visual only" comment.
3. `main`: at scene build `blade.set_domain(spec.domain)`; per frame `blade.update_plane(snap["slice_plane"])`, `blade.set_walk_stop(snap walk index or None)`, and in SLICE mode `blade.draw(vp_left, surface_fn)`. Totem hidden in SLICE (your job with Parent G, as ruled).
4. Bless the `time` import (CONTRACT-NOTE in the header) — the bead's breath needs a clock and draw() receives none.
5. `REQUIRED_SHADERS` unchanged — everything lives in the glass program.
6. Regression guard to verify on the repo: `walk_path` at `tilt_deg=0` must reproduce the old straight transect (entry point, stops every 0.8, exact exit point). It does by construction — marching squares is exact on the tilt-zero linear field — but test it against the old function before deleting it.

The Blade is forged the way you meant it, Nir — a real plane that really cuts, an honest curve at true heights, a bead you can trust. Test it against me as hard as you like.
