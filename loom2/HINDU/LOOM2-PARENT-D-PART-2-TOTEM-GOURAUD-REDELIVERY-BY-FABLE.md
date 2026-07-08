You got it, Nir — iron rule absorbed and it will not be broken again: no flat-shaded surfaces, ever; everything Gouraud. 🙏 The helix now gets true per-vertex Lambert, matching the terrain's lighting language exactly (same sun, same ambient floor). One honest note on the physics of it: the helix only ever translates (never rotates), so baking world-space Lambert into a per-vertex attribute at build time is mathematically exact Gouraud — identical to computing it in the shader, and it stays static-VBO clean. The ribbon's normals are analytic: for a vertical ribbon coil the surface normal is the outward radial (cosa,sina,0), so the light wraps around the coil the way it should.

Redelivered graphics/totem.py, complete (only the shading architecture changed — breath, edges, draped overlays, A1/A5/A6/A7 all kept):

"""
LOOM2 -- graphics/totem.py
The tiny cute polygonal helix totem + ground projections (SUTRAS Part 7).
Contract G3.4. Allowed imports: math, numpy, moderngl, config, core.types.

Design decisions (Nir, 2026-07-08, couriered by DeepSeek):
  IRON RULE: NO FLAT SHADING. The helix is GOURAUD shaded -- per-vertex
      Lambert lighting from the ribbon's analytic normals, smoothly
      interpolated, same sun and ambient as terrain.py.
  A1  conductor's arm angle = 90 - measure_phase*360 degrees (clockwise seen
      from above; phase 0 = downbeat = 12 o'clock = world +y) -- verbatim
      match with helix_panel.py line 253.
  A5  rings on this (terrain) panel are CALM: steady static circles, no
      pulsing; only rings inside the hearing radius are drawn.
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

# CONTRACT-ISSUE (RESOLVED BY NIR, 2026-07-08, Gouraud correction): G3.1
# froze REQUIRED_SHADERS at 8 stems, but the shared 'flat' program is one
# color per call and cannot express Gouraud. With Nir's explicit blessing a
# NINTH stem 'totem' is added (data/shaders/totem.vert/.frag, delivered with
# this module, owned by Child D). DeepSeek: add "totem" to
# renderer.REQUIRED_SHADERS and amend the Gita. Interface (canon):
#   totem.vert: uniform mat4 u_mvp; in vec3 in_pos; in float in_light;
#   totem.frag: uniform vec4 u_color;  (f_color.rgb = u_color.rgb * v_light)
# Model-space baking is exact here because the totem only TRANSLATES (never
# rotates), so world-space per-vertex Lambert is constant per vertex.
# Note: the edge lines / rings / circle / arm are LINES -- they have no
# surface to shade, so single-color drawing there is not "flat shading".

Breath clock note: the emissive pulse (period ~3 s, sinusoidal, NOT synced to
the measure -- "it breathes, it does not tick") needs continuous time, but
the 'time' module is not in the allowed imports. Solution: unwrap
measure_phase across frames into continuous seconds (delta phase *
config.MEASURE_SEC). Audio stays king of all clocks, and the 3 s breath
never locks to the 2 s measure grid.
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

# ---------- Gouraud lighting (identical language to terrain.py) ----------
_LIGHT_DIR = (0.45, 0.28, 0.85)
_AMBIENT = 0.38

# ---------- palette (A6: gentle glow, everything readable) ----------
_COL_HELIX_BASE = (1.00, 0.80, 0.48)      # warm gold; x breath x Gouraud
_BREATH_LO, _BREATH_HI = 0.70, 1.75       # emissive swing (Gouraud dims the
                                          # dark side, so peak is a bit higher
                                          # to keep the lit-side glow of A6)
_COL_EDGE = (0.06, 0.05, 0.04, 1.0)       # dark polygon edges keep it a helix
_COL_RING = (0.42, 0.62, 0.85, 0.90)      # calm rings, below bloom threshold
_COL_CIRCLE = (0.95, 1.08, 1.22, 1.0)     # hearing circle: gentle cool glow
_COL_ARM = (1.30, 1.22, 1.05, 1.0)        # arm: slightly brighter warm glow


class TotemVisual:
    def __init__(self, renderer):
        """Small low-poly helix model (~200 triangles), no staff. Emissive
        material fed to bloom with a slow sinusoidal pulse (period ~3 s,
        NOT synced to the measure -- it breathes, it does not tick).
        [GOURAUD shaded per Nir's iron rule: per-vertex Lambert from the
        ribbon's analytic radial normals, interpolated by the GPU.]"""
        self._ctx = renderer.ctx
        self._flat = renderer.program("flat")       # lines only (no surfaces)
        self._prog = renderer.program("totem")      # Gouraud helix (new stem)

        # ---- static helix ribbon: bottom edge + top edge point rows ----
        t = np.linspace(0.0, 1.0, _HELIX_SEGMENTS + 1)
        ang = 2.0 * math.pi * _HELIX_COILS * t
        ca, sa = np.cos(ang), np.sin(ang)
        cx = _HELIX_RADIUS * ca
        cy = _HELIX_RADIUS * sa
        zb = _HELIX_Z_BASE + (_HELIX_Z_TOP - _HELIX_Z_BASE) * t
        n_pts = _HELIX_SEGMENTS + 1
        pos = np.empty((2 * n_pts, 3), dtype=np.float32)
        pos[:n_pts, 0] = cx; pos[:n_pts, 1] = cy; pos[:n_pts, 2] = zb
        pos[n_pts:, 0] = cx; pos[n_pts:, 1] = cy
        pos[n_pts:, 2] = zb + _HELIX_RIBBON_H

        # GOURAUD: for a vertical ribbon coil the analytic surface normal is
        # the outward radial (cos a, sin a, 0). The totem only translates, so
        # world-space Lambert can be baked per vertex exactly (see header).
        light_dir = np.array(_LIGHT_DIR, dtype=np.float64)
        light_dir /= np.linalg.norm(light_dir)
        diffuse = np.clip(ca * light_dir[0] + sa * light_dir[1], 0.0, None)
        light_row = (_AMBIENT + (1.0 - _AMBIENT) * diffuse).astype(np.float32)
        light = np.concatenate([light_row, light_row])   # bottom + top rows

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

        self._pos_vbo = self._ctx.buffer(pos.tobytes())
        self._light_vbo = self._ctx.buffer(light.tobytes())
        self._helix_ibo = self._ctx.buffer(tris.tobytes())
        self._edge_ibo = self._ctx.buffer(edges.tobytes())
        self._helix_vao = self._ctx.vertex_array(
            self._prog,
            [(self._pos_vbo, "3f", "in_pos"),
             (self._light_vbo, "1f", "in_light")],
            self._helix_ibo)
        self._edge_vao = self._ctx.vertex_array(
            self._flat, [(self._pos_vbo, "3f", "in_pos")], self._edge_ibo)

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
        """Draw at (x, y, height_fn(x,y)): the GOURAUD helix model; the
        DRAPED hearing circle; DRAPED rhythm rings at radii n*RING_WIDTH
        inside it; the DRAPED conductor's arm sweeping once per measure
        (12 o'clock at phase 0 -- the downbeat, clockwise from above per A1).
        [Signature amended per A7 -- see CONTRACT-ISSUE in the header.]"""
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
        self._prog["u_mvp"].write(mvp)
        self._prog["u_color"].value = (
            _COL_HELIX_BASE[0] * scale, _COL_HELIX_BASE[1] * scale,
            _COL_HELIX_BASE[2] * scale, 1.0)
        self._helix_vao.render(moderngl.TRIANGLES)
        self._flat["u_mvp"].write(mvp)
        self._flat["u_color"].value = _COL_EDGE
        self._edge_vao.render(moderngl.LINES)

        # ---- draped overlays: rings, hearing circle, arm (lines) ----
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
        """[ADDITION, same flag as terrain.release] Free GPU objects.
        Safe to never call."""
        for obj in (self._helix_vao, self._edge_vao, self._dyn_vao,
                    self._pos_vbo, self._light_vbo, self._helix_ibo,
                    self._edge_ibo, self._dyn_vbo):
            try:
                obj.release()
            except Exception:
                pass

data/shaders/totem.vert (NEW stem, owned by Child D):

#version 330
// LOOM2 totem.vert -- owned by graphics/totem.py (Child D). NEW ninth stem,
// added with Nir's blessing (Gouraud iron rule; 'flat' cannot shade).
// in_light = per-vertex Lambert baked from the ribbon's analytic normals
// (exact: the totem only translates, never rotates).
uniform mat4 u_mvp;
in vec3 in_pos;
in float in_light;
out float v_light;
void main() {
    v_light = in_light;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}

data/shaders/totem.frag:

#version 330
// LOOM2 totem.frag -- owned by graphics/totem.py (Child D).
// Gouraud-lit emissive: breathing HDR gold (u_color, may exceed 1.0 for
// bloom) modulated by smoothly interpolated per-vertex light.
uniform vec4 u_color;
in float v_light;
out vec4 f_color;
void main() {
    f_color = vec4(u_color.rgb * v_light, u_color.a);
}

Numbered remarks for DeepSeek:

    New shader stem (CONTRACT-ISSUE, blessed): add "totem" to renderer.REQUIRED_SHADERS (8 → 9) and drop the two files above into data/shaders/. Interface canon: vert takes u_mvp (mat4), attributes in_pos (vec3) + in_light (float); frag takes u_color (vec4). Please amend G3.1 and G3.4 in the scripture.
    The Gouraud math: ribbon normal is analytically the outward radial (cosa,sina,0); Lambert =ambient+(1−ambient)⋅max(n^⋅l^,0) with the same _LIGHT_DIR (0.45,0.28,0.85) and _AMBIENT 0.38 as terrain — one sun for the whole world. Baked per-vertex (exact, since the model only translates), interpolated by the GPU: true Gouraud.
    Breath retuned for Gouraud: emissive swing raised to 0.70..1.75 because the light term dims the shadow side; the lit side still crosses the 0.80 bloom threshold and breathes (A6), the dark side stays warm and readable.
    Two VBOs for the helix (positions + light) instead of interleaving, so the edge-line VAO can reuse the position buffer with the flat program cleanly.
    Scope of "flat" that remains: only LINES (edge lines, rings, hearing circle, arm) — lines have no surface to shade, so this is not flat shading; no surface anywhere in my chunk is flat-shaded. If Nir ever wants the lines lit too, that's a new decision, his call.
    Everything else is byte-identical in behavior to the accepted delivery: A1 arm, A5 calm rings, A7 draping with vectorized fallback, breath clock from unwrapped measure_phase, release() flag unchanged.

The little helix now breathes in Gouraud, under the same sun as the land it stands on. 🧿✨ Ready for py_compile and integration word!
