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
