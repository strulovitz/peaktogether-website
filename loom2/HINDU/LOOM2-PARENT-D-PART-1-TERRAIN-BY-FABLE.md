Third time's the charm — here it comes, whole. 🙂

First, the important part — Nir, you're right, and I'm sorry. My Q3 framed flat shading as a near-decision ("any objection?") instead of honestly presenting a choice the contract itself (G3.3 says "flat/Gouraud") left open, and my lean was implementation convenience — exactly the kind of quiet downgrade you caught. From now on: when a choice affects quality or looks, I present the options and tradeoffs, and YOU decide. And the good news: you get both of your decisions at full strength. Lighting is computed per vertex and smoothly interpolated (true Gouraud, A3), but the band color is chosen per fragment from the interpolated height — so the hard bands (A2) come out pixel-sharp, real level curves painted on the land, sharper than any vertex-color approach could ever make them. No compromise on either.

All answers absorbed: A1 arm =90°−phase×360° (clockwise from above, matching helix_panel verbatim). A2 hard bands, my thresholds as a starting point. A3 Gouraud. A4 no water sheet — same mesh, blue bands darkening with depth. A5 rings calm and static on the left panel, only rings inside the hearing radius. A6 gentle glow on all totem parts, everything stays readable. A7 draped rings, with your explicit blessing to amend the contract — I'll use it (details in remark 8 below).

One tuning fix on my own Q2 proposal: the bowl's minimum is exactly −1.0, so a deep-water threshold at −1.0 would never actually show deep blue in the lake. I moved it to −0.6 so the bowl gets a proper deep-blue heart inside a shallow-blue ring.

Here is graphics/terrain.py, complete:

"""
LOOM2 -- graphics/terrain.py
The raised-relief hypsometric map (LEFT panel). Contract G3.3.
Allowed imports: numpy, moderngl, config, core.types.
(Only numpy and config are actually needed: all GL objects are built through
the public renderer.ctx, so moderngl itself is never imported.)

Design decisions (Nir, 2026-07-08, couriered by DeepSeek):
  A2  HARD hypsometric bands -- sharp thresholds paint the level curves.
  A3  GOURAUD shading -- per-vertex Lambert lighting, smoothly interpolated.
  A4  NO separate water plane -- below z=0 is the same terrain mesh, hard
      blue bands darkening with depth.
How A2 and A3 coexist at full quality: lighting is computed per VERTEX and
interpolated across faces (true Gouraud), but the band color is chosen per
FRAGMENT from the interpolated world height, so band edges are pixel-sharp
level curves -- never blurred by vertex color interpolation.

This module OWNS data/shaders/terrain.vert / terrain.frag (delivered with it).
Final shader interface (canon, for DeepSeek's records):
  terrain.vert: uniform mat4 u_mvp; in vec3 in_pos; in float in_light;
  terrain.frag: uniform vec3 u_band_colors[6]; uniform float u_band_edges[5];
Terrain colors stay at or below 1.0 -- the land itself never blooms hard;
bloom is reserved for the totem and other glowing souls.
"""

import numpy as np
import config

# ---------- hypsometric band design (Child D, per A2/A4) ----------
# Six hard bands, low to high. Edges are ABSOLUTE world z, identical in every
# scene, so the shoreline is always A440 (z = 0) and a color means the same
# pitch everywhere. Tuned against the surface catalog (GITA G4.1):
#   bowl (min -1.0): deep-blue lake heart inside a shallow-blue ring
#   hill (peak 2.8): snow cap above 2.2, shallow moat at its far skirt
#   egg_carton (+-1.6): darkest-blue pits, upland crests
#   saddle at domain edges (+-5.76): the full palette, abyss to snow
_BAND_EDGES = (-1.5, -0.6, 0.0, 1.1, 2.2)
_DEEP_DARK_FACTOR = 0.55        # darkest abyss = COLOR_DEEP_WATER * this

# ---------- Gouraud lighting (baked per-vertex at build time) ----------
_LIGHT_DIR = (0.45, 0.28, 0.85)  # fixed sun: high, tilted so slopes shade
_AMBIENT = 0.38                  # floor so shadowed faces stay readable


def _band_colors() -> np.ndarray:
    """The 6 band colors, low to high, float32 0..1 (never above 1.0)."""
    deep = np.array(config.COLOR_DEEP_WATER, dtype=np.float32) / 255.0
    shallow = np.array(config.COLOR_SHALLOW, dtype=np.float32) / 255.0
    lowland = np.array(config.COLOR_LOWLAND, dtype=np.float32) / 255.0
    upland = np.array(config.COLOR_UPLAND, dtype=np.float32) / 255.0
    peak = np.array(config.COLOR_PEAK, dtype=np.float32) / 255.0
    return np.stack([deep * _DEEP_DARK_FACTOR, deep, shallow,
                     lowland, upland, peak]).astype(np.float32)


class TerrainMesh:
    def __init__(self, renderer, surface_fn, domain: tuple, mesh_step: float):
        """Build a triangle mesh of z = f(x,y) over the finite domain
        (SUTRAS Part 8). Per-vertex colors by height: config.COLOR_* bands
        (deep water < shallow < lowland < upland < peak), flat/Gouraud shaded
        demoscene look. Water plane at z=0, slightly glossy. Static VBO --
        built once per scene.
        [Implemented per Nir's decisions A2/A3/A4: Gouraud lighting, hard
        bands resolved per fragment, no separate water sheet -- the original
        water-plane sentence above is superseded by A4 and kept only so the
        contract text stays intact.]"""
        self._fn = surface_fn

        xmin, xmax, ymin, ymax = (float(v) for v in domain)
        step = float(mesh_step)
        nx = max(2, int(round((xmax - xmin) / step)) + 1)
        ny = max(2, int(round((ymax - ymin) / step)) + 1)
        xs = np.linspace(xmin, xmax, nx)
        ys = np.linspace(ymin, ymax, ny)
        gx, gy = np.meshgrid(xs, ys, indexing="ij")      # shape (nx, ny)
        gz = self._sample(gx, gy)

        # Per-vertex normals from central differences of the TRUE surface
        # (not the mesh), then Lambert light baked to one float per vertex.
        # Unnormalized normal of z=f(x,y) is (-fx, -fy, 1).
        h = 0.5 * step
        fx = (self._sample(gx + h, gy) - self._sample(gx - h, gy)) / (2.0 * h)
        fy = (self._sample(gx, gy + h) - self._sample(gx, gy - h)) / (2.0 * h)
        inv_len = 1.0 / np.sqrt(fx * fx + fy * fy + 1.0)
        light_dir = np.array(_LIGHT_DIR, dtype=np.float64)
        light_dir /= np.linalg.norm(light_dir)
        diffuse = np.clip((-fx * light_dir[0] - fy * light_dir[1]
                           + light_dir[2]) * inv_len, 0.0, None)
        light = _AMBIENT + (1.0 - _AMBIENT) * diffuse

        # Interleaved static vertex data: x, y, z, light  (4 x float32)
        verts = np.empty((nx * ny, 4), dtype=np.float32)
        verts[:, 0] = gx.ravel()
        verts[:, 1] = gy.ravel()
        verts[:, 2] = gz.ravel()
        verts[:, 3] = light.ravel()

        # Index buffer: two CCW-from-above triangles per grid cell.
        ii, jj = np.meshgrid(np.arange(nx - 1), np.arange(ny - 1),
                             indexing="ij")
        a = (ii * ny + jj).ravel()
        b = ((ii + 1) * ny + jj).ravel()
        c = ((ii + 1) * ny + (jj + 1)).ravel()
        d = (ii * ny + (jj + 1)).ravel()
        tris = np.empty((a.size, 6), dtype=np.uint32)
        tris[:, 0] = a; tris[:, 1] = b; tris[:, 2] = c
        tris[:, 3] = a; tris[:, 4] = c; tris[:, 5] = d

        ctx = renderer.ctx
        self._prog = renderer.program("terrain")
        self._prog["u_band_colors"].write(_band_colors().tobytes())
        self._prog["u_band_edges"].write(
            np.array(_BAND_EDGES, dtype=np.float32).tobytes())
        self._vbo = ctx.buffer(verts.tobytes())
        self._ibo = ctx.buffer(tris.tobytes())
        self._vao = ctx.vertex_array(
            self._prog, [(self._vbo, "3f 1f", "in_pos", "in_light")],
            self._ibo)

    def draw(self, view_proj) -> None:
        vp = np.ascontiguousarray(
            np.asarray(view_proj, dtype=np.float32).T).tobytes()
        self._prog["u_mvp"].write(vp)   # canon upload (helix_panel.py 228/248)
        self._vao.render()

    def height_at(self, x: float, y: float) -> float:
        """Exact f(x,y) passthrough -- used to plant the totem on the ground.
        [Pure passthrough: no mesh interpolation, no caching. Seam bonus:
        because it forwards to surface_fn unchanged, it also accepts numpy
        arrays when the surface is vectorized -- totem.py may exploit that
        to drape ring points efficiently.]"""
        return self._fn(x, y)

    # ---------- private helpers ----------

    def _sample(self, x, y):
        """Evaluate surface_fn on numpy grids. The SurfaceFn contract says
        'vectorization allowed', not guaranteed -- so try the fast vectorized
        call first and fall back to a scalar loop if the fn refuses arrays."""
        shape = np.shape(x)
        try:
            z = np.asarray(self._fn(x, y), dtype=np.float64)
            if z.shape != shape:                 # constant / semi-constant fn
                z = np.broadcast_to(z, shape).copy()
            return z
        except Exception:
            fx = np.ravel(x)
            fy = np.ravel(y)
            z = np.fromiter((float(self._fn(float(a), float(b)))
                             for a, b in zip(fx, fy)),
                            dtype=np.float64, count=fx.size)
            return z.reshape(shape)

    def release(self) -> None:
        """[ADDITION -- flagged, see remark 6] Free the GPU buffers. main
        rebuilds TerrainMesh on scene change; releasing the old one avoids
        leaking VBO/IBO/VAO. Safe to never call."""
        for obj in (self._vao, self._vbo, self._ibo):
            try:
                obj.release()
            except Exception:
                pass

data/shaders/terrain.vert (overwrites the placeholder — I own this GLSL):

#version 330
// LOOM2 terrain.vert -- owned by graphics/terrain.py (Child D).
// Gouraud: in_light is per-vertex Lambert lighting, interpolated by the GPU.
// v_z carries world height to the fragment stage for pixel-sharp hard bands.
uniform mat4 u_mvp;
in vec3 in_pos;
in float in_light;
out float v_light;
out float v_z;
void main() {
    v_light = in_light;
    v_z = in_pos.z;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}

data/shaders/terrain.frag (overwrites the placeholder):

#version 330
// LOOM2 terrain.frag -- owned by graphics/terrain.py (Child D).
// Hard hypsometric bands: color chosen per fragment from interpolated world
// height, so band edges are exact level curves. Gouraud light multiplies.
uniform vec3 u_band_colors[6];
uniform float u_band_edges[5];
in float v_light;
in float v_z;
out vec4 f_color;
void main() {
    vec3 c = u_band_colors[0];
    for (int i = 0; i < 5; i++) {
        if (v_z >= u_band_edges[i]) {
            c = u_band_colors[i + 1];
        }
    }
    f_color = vec4(c * v_light, 1.0);
}

Numbered remarks for DeepSeek:

    Three files: terrain.py to loom2/graphics/terrain.py; the two GLSL files overwrite the placeholders in data/shaders/. Final shader interface to record as canon: vert takes u_mvp (mat4), attributes in_pos (vec3) + in_light (float); frag takes u_band_colors (vec3[6]) + u_band_edges (float[5]).
    Band edges are (−1.5,−0.6,0.0,1.1,2.2) in absolute world z, identical in every scene, so the shoreline is always A440 and each color always means the same pitch. Darkest-abyss band = COLOR_DEEP_WATER ×0.55 (per A4's "darker with depth"). All tuning lives in the two constants at the top — trivial to retune after Nir sees it live.
    u_band_colors/u_band_edges are written once in __init__ (the terrain program has exactly one user, and every scene change rebuilds the mesh anyway); u_mvp is written per draw with the canonical transposed upload matching helix_panel.py.
    Index buffer is uint32 — moderngl's default index_element_size=4 matches; vao.render() with no args draws all indices as triangles.
    Normals come from central differences of the true surface_fn (not the mesh), so lighting quality is independent of mesh_step.
    Flagged addition: release() is not in the contract (bodies-only law), added because main rebuilds TerrainMesh per scene and moderngl objects don't free themselves. Nothing calls it; delete the method if unwanted, or better, call old_mesh.release() in main's scene-change path.
    No # CONTRACT-ISSUE needed: A4 supersedes the docstring's water-plane sentence; I kept the contract text intact and appended an implementation note rather than silently editing scripture.
    A7 heads-up for the next delivery: for draped rings, the cleanest amendment is changing TotemVisual.draw(self, view_proj, totem_state, ground_z: float, measure_phase: float) to draw(self, view_proj, totem_state, height_fn, measure_phase), where main passes terrain.height_at (the totem computes its own ground height and drapes every ring point through the same callable — one parameter swap, no new seams). Under Nir's explicit blessing I'll write totem.py against that signature unless you object before my next message; please amend the Gita and wire main accordingly.
    One small taste question for Nir (asking, not deciding!): peak-snow pixels land at brightness ≈0.82–0.84, a hair above the 0.80 bloom bright-pass — depending on your extract shader that gives the snowcaps a very faint shimmer-glow. Keep it (I think it's pretty), or should I scale the terrain to stay fully matte below 0.80? Either is a one-constant change.

totem.py comes next message — the little helix that breathes. 🧿🏔️🎻
