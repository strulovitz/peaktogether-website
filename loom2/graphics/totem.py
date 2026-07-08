"""
LOOM2 -- graphics/totem.py
The tiny cute polygonal helix totem + ground projections (SUTRAS Part 7).
Contract G3.4. Allowed imports: math, numpy, moderngl, config, core.types.

Design decisions (Nir, 2026-07-08, couriered by DeepSeek):
  A1  conductor's arm angle = 90 - measure_phase*360 degrees (clockwise seen
      from above; phase 0 = downbeat = 12 o'clock = world +y) -- verbatim
      match with helix_panel.py line 253.
  A5  rings on this (terrain) panel are CALM: steady static circles, no
      pulsing, no blinking; only rings inside the hearing radius are drawn.
  A6  gentle glow on ALL totem parts (HDR colors above 1.0 feed the bloom
      bright-pass at 0.80), but every shape stays readable -- the helix keeps
      dark polygon edge lines so it never becomes a blinding white cylinder.
  A7  the hearing circle, rhythm rings and conductor's arm are DRAPED over
      the terrain, hugging every bump and dip -- never floating flat disks.

# CONTRACT-ISSUE (RESOLVED BY NIR, 2026-07-08, answer A7): G3.4 froze
# draw(self, view_proj, totem_state, ground_z: float, measure_phase). Draping
# requires terrain height around the WHOLE circle, not one sample. With Nir's
# explicit blessing the signature is amended to:
#     draw(self, view_proj, totem_state, height_fn, measure_phase)
# where height_fn(x, y) -> z is TerrainMesh.height_at (a pure passthrough of
# the surface fn; accepts numpy arrays when the surface is vectorized).
# DeepSeek: please amend the Gita text and wire main to pass terrain.height_at.

Breath clock note: the emissive pulse (period ~3 s, sinusoidal, NOT synced to
the measure -- "it breathes, it does not tick") needs continuous time, but the
'time' module is not in the allowed imports. Solution: unwrap measure_phase
across frames into continuous seconds (phase delta * config.MEASURE_SEC).
Audio stays king of all clocks, and 3 s never locks to the 2 s measure grid.
"""

import math
import numpy as np
import moderngl
import config

# ---------- geometry tuning (Child D) ----------
_HELIX_SEGMENTS = 80        # ribbon steps -> 160 triangles (~200 budget)
_HELIX_COILS = 2.5
_HELIX_RADIUS = 0.16        # tiny and cute, standing on the land
_HELIX_RIBBON_H = 0.14      # vertical ribbon height
_HELIX_Z_BASE = 0.04
_HELIX_Z_TOP = 0.80
_EDGE_RUNG_EVERY = 8        # dark rung line every N segments

_CIRCLE_PTS = 96            # samples per draped circle
_ARM_PTS = 24               # samples along the draped arm
_LIFT = 0.05                # raise draped lines above ground (no z-fighting)

_BREATH_PERIOD_S = 3.0

# ---------- palette (A6: gentle glow, everything readable) ----------
_COL_HELIX_BASE = (1.00, 0.80, 0.48)      # warm gold, scaled by the breath
_BREATH_LO, _BREATH_HI = 0.65, 1.60       # emissive scale swing (modest HDR)
_COL_EDGE = (0.06, 0.05, 0.04, 1.0)       # dark polygon edges keep it a helix
_COL_RING = (0.42, 0.62, 0.85, 0.90)      # calm rings, below bloom threshold
_COL_CIRCLE = (0.95, 1.08, 1.22, 1.0)     # hearing circle: gentle cool glow
_COL_ARM = (1.30, 1.22, 1.05, 1.0)        # arm: slightly brighter warm glow


class TotemVisual:
    def __init__(self, renderer):
        """Small low-poly helix model (~200 triangles), no staff. Emissive
        material fed to bloom with a slow sinusoidal pulse (period ~3 s,
        NOT synced to the measure -- it breathes, it does not tick)."""
        self._ctx = renderer.ctx
        self._flat = renderer.program("flat")

        # ---- static helix ribbon: bottom edge + top edge point rows ----
        t = np.linspace(0.0, 1.0, _HELIX_SEGMENTS + 1)
        ang = 2.0 * math.pi * _HELIX_COILS * t
        cx = _HELIX_RADIUS * np.cos(ang)
        cy = _HELIX_RADIUS * np.sin(ang)
        zb = _HELIX_Z_BASE + (_HELIX_Z_TOP - _HELIX_Z_BASE) * t
        n_pts = _HELIX_SEGMENTS + 1
        verts = np.empty((2 * n_pts, 3), dtype=np.float32)
        verts[:n_pts, 0] = cx; verts[:n_pts, 1] = cy; verts[:n_pts, 2] = zb
        verts[n_pts:, 0] = cx; verts[n_pts:, 1] = cy
        verts[n_pts:, 2] = zb + _HELIX_RIBBON_H

        i = np.arange(_HELIX_SEGMENTS, dtype=np.uint32)
        T = np.uint32(n_pts)
        tris = np.empty((_HELIX_SEGMENTS, 6), dtype=np.uint32)
        tris[:, 0] = i;     tris[:, 1] = i + 1; tris[:, 2] = T + i
        tris[:, 3] = T + i; tris[:, 4] = i + 1; tris[:, 5] = T + i + 1

        # dark edge lines: bottom strip, top strip, rungs (LINES pairs)
        eb = np.stack([i, i + 1], axis=1)
        et = np.stack([T + i, T + i + 1], axis=1)
        r = np.arange(0, n_pts, _EDGE_RUNG_EVERY, dtype=np.uint32)
        er = np.stack([r, T + r], axis=1)
        edges = np.concatenate([eb, et, er]).astype(np.uint32)

        self._helix_vbo = self._ctx.buffer(verts.tobytes())
        self._helix_ibo = self._ctx.buffer(tris.tobytes())
        self._edge_ibo = self._ctx.buffer(edges.tobytes())
        self._helix_vao = self._ctx.vertex_array(
            self._flat, [(self._helix_vbo, "3f", "in_pos")], self._helix_ibo)
        self._edge_vao = self._ctx.vertex_array(
            self._flat, [(self._helix_vbo, "3f", "in_pos")], self._edge_ibo)

        # ---- dynamic buffer for draped overlays (rewritten every frame) ----
        max_pts = (config.NMAX_RING + 1) * (_CIRCLE_PTS + 1) + _ARM_PTS
        self._dyn_vbo = self._ctx.buffer(reserve=max_pts * 12)  # 3 x float32
        self._dyn_vao = self._ctx.vertex_array(
            self._flat, [(self._dyn_vbo, "3f", "in_pos")])

        # ---- breath clock (unwrapped from measure_phase) ----
        self._last_phase = 0.0
        self._time_s = 0.0

    def draw(self, view_proj, totem_state, height_fn, measure_phase: float
             ) -> None:
        """Draw at (x, y, height_fn(x,y)): the helix model; the DRAPED hearing
        circle; DRAPED rhythm rings at radii n*RING_WIDTH inside it; the
        DRAPED conductor's arm sweeping once per measure (12 o'clock at phase
        0 -- the downbeat, clockwise from above per A1). [Signature amended
        per A7 -- see CONTRACT-ISSUE in the module header.]"""
        # breath clock: accumulate continuous seconds from the audio phase
        dp = measure_phase - self._last_phase
        if dp < 0.0:
            dp += 1.0
        self._time_s += dp * config.MEASURE_SEC
        self._last_phase = measure_phase
        breath = 0.5 + 0.5 * math.sin(
            2.0 * math.pi * self._time_s / _BREATH_PERIOD_S)
        scale = _BREATH_LO + (_BREATH_HI - _BREATH_LO) * breath

        tx, ty = float(totem_state.x), float(totem_state.y)
        hr = float(totem_state.hearing_radius)
        gz = float(height_fn(tx, ty))
        vp = np.asarray(view_proj, dtype=np.float32)

        # ---- helix (model translated to the totem's ground spot) ----
        model = np.eye(4, dtype=np.float32)
        model[0, 3], model[1, 3], model[2, 3] = tx, ty, gz
        mvp = np.ascontiguousarray((vp @ model).T).tobytes()  # canon upload
        self._flat["u_mvp"].write(mvp)
        self._flat["u_color"].value = (
            _COL_HELIX_BASE[0] * scale, _COL_HELIX_BASE[1] * scale,
            _COL_HELIX_BASE[2] * scale, 1.0)
        self._helix_vao.render(moderngl.TRIANGLES)
        self._flat["u_color"].value = _COL_EDGE
        self._edge_vao.render(moderngl.LINES)

        # ---- draped overlays: rings, hearing circle, arm ----
        parts = []          # (point_count, color)
        chunks = []
        theta = np.linspace(0.0, 2.0 * math.pi, _CIRCLE_PTS + 1)
        n_rings = min(config.NMAX_RING,
                      int(math.floor((hr - 1e-6) / config.RING_WIDTH)))
        for n in range(1, n_rings + 1):
            rr = n * config.RING_WIDTH
            chunks.append(np.stack([tx + rr * np.cos(theta),
                                    ty + rr * np.sin(theta)], axis=1))
            parts.append((_CIRCLE_PTS + 1, _COL_RING))
        chunks.append(np.stack([tx + hr * np.cos(theta),
                                ty + hr * np.sin(theta)], axis=1))
        parts.append((_CIRCLE_PTS + 1, _COL_CIRCLE))

        arm_ang = math.radians(90.0 - measure_phase * 360.0)   # A1, verbatim
        arm_r = np.linspace(0.0, hr, _ARM_PTS)
        chunks.append(np.stack([tx + arm_r * math.cos(arm_ang),
                                ty + arm_r * math.sin(arm_ang)], axis=1))
        parts.append((_ARM_PTS, _COL_ARM))

        xy = np.concatenate(chunks)                       # (N, 2)
        z = self._heights(height_fn, xy[:, 0], xy[:, 1]) + _LIFT
        pts = np.column_stack([xy, z]).astype(np.float32)
        self._dyn_vbo.write(pts.tobytes())

        self._flat["u_mvp"].write(np.ascontiguousarray(vp.T).tobytes())
        self._ctx.line_width = 2.0
        first = 0
        for count, color in parts:
            self._flat["u_color"].value = color
            self._dyn_vao.render(moderngl.LINE_STRIP,
                                 vertices=count, first=first)
            first += count

    # ---------- private helpers ----------

    @staticmethod
    def _heights(height_fn, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
        """Drape helper: vectorized height_fn call with scalar fallback
        (same pattern as terrain._sample; SurfaceFn vectorization is allowed
        but not guaranteed)."""
        try:
            z = np.asarray(height_fn(xs, ys), dtype=np.float64)
            if z.shape != xs.shape:
                z = np.broadcast_to(z, xs.shape).copy()
            return z
        except Exception:
            return np.fromiter((float(height_fn(float(a), float(b)))
                                for a, b in zip(xs, ys)),
                               dtype=np.float64, count=xs.size)

    def release(self) -> None:
        """[ADDITION, same flag as terrain.release -- see remarks] Free GPU
        objects. Safe to never call."""
        for obj in (self._helix_vao, self._edge_vao, self._dyn_vao,
                    self._helix_vbo, self._helix_ibo, self._edge_ibo,
                    self._dyn_vbo):
            try:
                obj.release()
            except Exception:
                pass
