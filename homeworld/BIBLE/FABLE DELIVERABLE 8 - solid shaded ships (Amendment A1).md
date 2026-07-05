> 🛑 **DEEPSEEK NOTE (July 5, 2026) — FLATTENED per RULE #0.** Fable delivered this in package folders (forge/shaders.py, forge/solid.py, forge/bloom.py, forge/app.py, forge/__init__.py, content/shipwright.py) with relative imports. Homeworld is FLAT. So on drop-in: `forge/shaders.py`→`shaders.py`, `forge/solid.py`→`solid.py` (`from .shaders`→`from shaders`, `from .vobjects`→`from vobjects`), `forge/bloom.py`→`bloom.py` (`from .shaders`→`from shaders`), `forge/app.py`→`forge.py` (all `from .x`→`from x`), `content/shipwright.py`→`shipwright.py` (code, no relative imports). Dropped `forge/__init__.py` (re-export). `app.py` imports flattened: `from forge import Forge` + `from vobjects import Grid, Arrow, DashedLine, Label, Line, Trail` + `from solid import SolidMesh` + `from sim import FleetSim` + `from orders import MoveCombination` + `from content_db import ContentDB` + `from shipwright import build_ship`. The art-direction note lives at `notes/amendment_a1_art_direction.md` (docs folder, fine). NOTE: run.bat was deleted (Nir's choice) — run with `python app.py`. Fable's text verbatim below.

---

You are right, and thank you for saying it straight. Let me be honest about what happened, because you deserve the true picture:

    Nothing technical forced this. We have full modern OpenGL through moderngl — depth buffers, per-pixel lighting, HDR, everything a 2026 NVIDIA card eats for breakfast. The wireframe look was an art-direction choice I made in the design docs ("holographic blackboard" aesthetic), and the 10-vertex meshes were my hand-authored placeholders. Both were my calls. Your reaction is exactly the feedback the Bible's own First Law ("gaming first — would a gamer choose to play this?") exists to catch. The current ships fail that law. Case closed.
    The "transparency" is additive blending — lines add light instead of covering things. Great for math holograms, wrong for hulls. Real ships are opaque.
    The demoscene comparison is fair. Second Reality's shaded solids read better than sparse wireframes because filled, lit surfaces are what our brains parse as objects. So that's what we build — and with per-pixel Blinn-Phong, rim lighting and HDR bloom, we'll be past 1993, not chasing it.

The amended art direction (your decision, now law): ships are solid, opaque, lit 3D models — hundreds of shaded panels, painted hull plates, dark canopies, glowing engine nozzles. The math layer (arrows, grids, ghost vectors, trails) stays glowing-holographic on top — that contrast will actually look better: solid warships inside a luminous mathematical space. And a road to even more: the engine below supports arbitrary triangle meshes, so later we can load Blender/OBJ models with thousands of polys.

Below: the solid-shading engine + a procedural shipwright that generates each class from lofted hull sections, wings, towers, nozzles (roughly 400–1500 triangles per ship instead of 16 edges). 9 files — send each to DeepSeek exactly as-is.

File 1 — notes/amendment_a1_art_direction.md

AMENDMENT A1 — ART DIRECTION (owner decision, July 2026)

The owner has ruled: glowing wireframe ships FAIL Bible Law 1 (gaming
first). Amended visual identity, binding on all future work:

1. SHIPS are solid, opaque, lit triangle meshes: per-pixel Blinn-Phong
   (key + fill + rim + specular), flat-shaded paneled hulls with
   per-face color variation, emissive engine nozzles/windows feeding
   bloom. Hundreds to thousands of triangles per class. Never
   see-through. Meshes come from content/shipwright.py (procedural)
   today; OBJ import from Blender is a sanctioned future path.
2. THE MATH LAYER (arrows, grids, spans, ghosts, trails, labels)
   remains glowing holographic vector graphics, drawn additively OVER
   the solid world with depth testing (occluded correctly by hulls).
3. The render pipeline is: solid pass (depth write) -> glow pass
   (depth test, no write) -> bloom -> crisp overlay.
4. "It must look like a game a gamer would choose" outranks any
   aesthetic theory in any design document. The owner is the arbiter.

File 2 — forge/shaders.py (updated — replaces the whole file; adds the mesh lighting shaders)

"""GLSL shader sources.

Families: line ribbons (glow layer), bloom pipeline, textured quads
(text/panels), and — per Amendment A1 — the SOLID MESH shader:
per-pixel Blinn-Phong with a warm key light, cool fill light, rim
light and specular highlight. Vertices arrive pre-transformed to
world space; per-vertex color = painted hull panels; per-vertex
emissive = engine nozzles / windows (HDR values > 1 feed bloom).
Two-sided: normals are flipped for back faces, so procedural geometry
never suffers winding bugs.
"""

LINE_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec4 in_color;
in float in_u;
out vec4 v_color;
out float v_u;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_color = in_color;
    v_u = in_u;
}
"""

LINE_FRAG = """
#version 330
in vec4 v_color;
in float v_u;
out vec4 f_color;
void main() {
    float k = 1.0 - v_u * v_u;
    f_color = vec4(v_color.rgb * k * k * v_color.a, 1.0);
}
"""

MESH_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec3 in_normal;
in vec4 in_color;
in vec3 in_emissive;
out vec3 v_pos;
out vec3 v_normal;
out vec4 v_color;
out vec3 v_emissive;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_pos = in_pos;
    v_normal = in_normal;
    v_color = in_color;
    v_emissive = in_emissive;
}
"""

MESH_FRAG = """
#version 330
uniform vec3 u_eye;
in vec3 v_pos;
in vec3 v_normal;
in vec4 v_color;
in vec3 v_emissive;
out vec4 f_color;
void main() {
    vec3 KEY_DIR  = vec3(0.4581, 0.8144, 0.3563);
    vec3 KEY_COL  = vec3(1.05, 1.00, 0.92);
    vec3 FILL_DIR = vec3(-0.5582, -0.2791, -0.7814);
    vec3 FILL_COL = vec3(0.22, 0.30, 0.45);
    vec3 AMBIENT  = vec3(0.15, 0.17, 0.21);

    vec3 n = normalize(v_normal);
    if (!gl_FrontFacing) n = -n;
    vec3 vdir = normalize(u_eye - v_pos);

    float dk = max(dot(n, KEY_DIR), 0.0);
    float df = max(dot(n, FILL_DIR), 0.0);
    vec3 h = normalize(KEY_DIR + vdir);
    float spec = pow(max(dot(n, h), 0.0), 44.0) * 0.55;
    float rim = pow(1.0 - max(dot(n, vdir), 0.0), 3.0) * 0.22;

    vec3 albedo = v_color.rgb;
    vec3 c = albedo * (AMBIENT + KEY_COL * dk + FILL_COL * df)
           + KEY_COL * spec + albedo * rim + v_emissive;
    f_color = vec4(c, 1.0);
}
"""

FULLSCREEN_VERT = """
#version 330
out vec2 v_uv;
void main() {
    vec2 pos = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
    v_uv = pos;
    gl_Position = vec4(pos * 2.0 - 1.0, 0.0, 1.0);
}
"""

BLIT_FRAG = """
#version 330
uniform sampler2D u_tex;
in vec2 v_uv;
out vec4 f_color;
void main() {
    f_color = vec4(texture(u_tex, v_uv).rgb, 1.0);
}
"""

BLUR_FRAG = """
#version 330
uniform sampler2D u_tex;
uniform vec2 u_dir;
in vec2 v_uv;
out vec4 f_color;
void main() {
    const float w[5] = float[5](
        0.2270270270, 0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
    );
    vec3 c = texture(u_tex, v_uv).rgb * w[0];
    for (int i = 1; i < 5; i++) {
        c += texture(u_tex, v_uv + u_dir * float(i)).rgb * w[i];
        c += texture(u_tex, v_uv - u_dir * float(i)).rgb * w[i];
    }
    f_color = vec4(c, 1.0);
}
"""

COMPOSITE_FRAG = """
#version 330
uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform float u_strength;
uniform float u_exposure;
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 c = texture(u_scene, v_uv).rgb
           + u_strength * texture(u_bloom, v_uv).rgb;
    c = vec3(1.0) - exp(-c * u_exposure);
    f_color = vec4(c, 1.0);
}
"""

TEXT_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec2 in_uv;
in vec4 in_color;
out vec2 v_uv;
out vec4 v_color;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_uv = in_uv;
    v_color = in_color;
}
"""

TEXT_FRAG = """
#version 330
uniform sampler2D u_tex;
in vec2 v_uv;
in vec4 v_color;
out vec4 f_color;
void main() {
    float a = texture(u_tex, v_uv).r;
    f_color = vec4(v_color.rgb * a * v_color.a, 1.0);
}
"""

File 3 — forge/solid.py (new file)

"""Solid shaded meshes (Amendment A1).

SolidMesh: an opaque triangle mesh vobject — base geometry + painted
per-vertex colors + per-vertex emissive. set_transform(R, pos) places
it in the world each frame. Flat shading falls out naturally because
the shipwright emits duplicated vertices per face.

SolidRenderer: batches every visible SolidMesh into one draw call
with depth testing and no blending — ships are NOT transparent.
"""

import numpy as np
import moderngl

from .shaders import MESH_VERT, MESH_FRAG
from .vobjects import VObject


def compute_normals(verts, tris):
    n = np.zeros_like(verts)
    v0 = verts[tris[:, 0]]
    v1 = verts[tris[:, 1]]
    v2 = verts[tris[:, 2]]
    fn = np.cross(v1 - v0, v2 - v0)
    for k in range(3):
        np.add.at(n, tris[:, k], fn)
    length = np.linalg.norm(n, axis=1, keepdims=True)
    length[length < 1e-12] = 1.0
    return n / length


class SolidMesh(VObject):
    def __init__(self, vertices, triangles, colors, emissive=None, **kw):
        super().__init__(**kw)
        self._base_v = np.asarray(vertices, dtype=np.float64).copy()
        self._tris = np.asarray(triangles, dtype=np.int64).reshape(-1, 3)
        self._base_n = compute_normals(self._base_v, self._tris)
        self._colors = np.asarray(colors, dtype=np.float64).copy()
        if emissive is None:
            emissive = np.zeros((self._base_v.shape[0], 3))
        self._emissive = np.asarray(emissive, dtype=np.float64).copy()
        self._flat = self._tris.reshape(-1)
        self._hl = 0.0
        self._soup = np.zeros((0, 13), dtype=np.float32)
        self.set_transform(np.eye(3), (0.0, 0.0, 0.0))

    def set_highlight(self, on):
        self._hl = 0.30 if on else 0.0

    def set_transform(self, R, pos):
        R = np.asarray(R, dtype=np.float64)
        pos = np.asarray(pos, dtype=np.float64)
        wv = self._base_v @ R.T + pos
        wn = self._base_n @ R.T
        f = self._flat
        soup = np.concatenate(
            [wv[f], wn[f], self._colors[f], self._emissive[f] + self._hl],
            axis=1)
        self._soup = soup.astype(np.float32)

    def segments(self):
        return np.zeros((0, 2, 3), dtype=np.float64)   # not a line object


class SolidRenderer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.prog = ctx.program(vertex_shader=MESH_VERT,
                                fragment_shader=MESH_FRAG)
        self._vbo = ctx.buffer(reserve=4 * 1024 * 1024, dynamic=True)
        self._vao = self._make_vao()

    def _make_vao(self):
        return self.ctx.vertex_array(
            self.prog,
            [(self._vbo, "3f 3f 4f 3f",
              "in_pos", "in_normal", "in_color", "in_emissive")],
        )

    def draw(self, meshes, mvp_t_f32, eye):
        soups = [m._soup for m in meshes if m._soup.shape[0] > 0]
        if not soups:
            return
        data = np.concatenate(soups, axis=0)
        if data.nbytes > self._vbo.size:
            self._vbo.release()
            self._vbo = self.ctx.buffer(reserve=2 * data.nbytes,
                                        dynamic=True)
            self._vao = self._make_vao()
        self._vbo.write(data.tobytes())
        self.prog["u_mvp"].write(mvp_t_f32)
        self.prog["u_eye"].value = tuple(float(v) for v in eye)
        self._vao.render(moderngl.TRIANGLES, vertices=data.shape[0])

File 4 — forge/bloom.py (updated — replaces the whole file; the scene framebuffer gains a depth buffer)

"""Bloom pipeline + the scene framebuffer (Amendment A1 update).

The scene FBO is now RGBA16F color + a DEPTH buffer, because solid
ships need depth testing. The bloom chain itself is unchanged:
downsample to 1/4, separable Gaussian blur, composite with soft
exposure tone map. Emissive mesh parts (engine nozzles, windows) and
the glow layer both feed bloom naturally.
"""

import moderngl

from .shaders import FULLSCREEN_VERT, BLIT_FRAG, BLUR_FRAG, COMPOSITE_FRAG


class Bloom:
    def __init__(self, ctx, strength=0.85, exposure=2.5):
        self.ctx = ctx
        self.strength = float(strength)
        self.exposure = float(exposure)

        self._blit = ctx.program(
            vertex_shader=FULLSCREEN_VERT, fragment_shader=BLIT_FRAG)
        self._blur = ctx.program(
            vertex_shader=FULLSCREEN_VERT, fragment_shader=BLUR_FRAG)
        self._comp = ctx.program(
            vertex_shader=FULLSCREEN_VERT, fragment_shader=COMPOSITE_FRAG)
        self._vao_blit = ctx.vertex_array(self._blit, [])
        self._vao_blur = ctx.vertex_array(self._blur, [])
        self._vao_comp = ctx.vertex_array(self._comp, [])

        self._w = 0
        self._h = 0
        self._bw = 0
        self._bh = 0
        self.scene_fbo = None
        self._scene_tex = None
        self._scene_depth = None
        self._tex_b = None
        self._tex_c = None
        self._fbo_b = None
        self._fbo_c = None

    def ensure_size(self, w, h):
        if (w, h) == (self._w, self._h):
            return
        for obj in (self.scene_fbo, self._scene_tex, self._scene_depth,
                    self._fbo_b, self._fbo_c, self._tex_b, self._tex_c):
            if obj is not None:
                obj.release()

        self._w, self._h = w, h
        self._bw = max(w // 4, 1)
        self._bh = max(h // 4, 1)

        self._scene_tex = self.ctx.texture((w, h), 4, dtype="f2")
        self._scene_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._scene_depth = self.ctx.depth_renderbuffer((w, h))
        self.scene_fbo = self.ctx.framebuffer(
            color_attachments=[self._scene_tex],
            depth_attachment=self._scene_depth)

        self._tex_b = self.ctx.texture((self._bw, self._bh), 4, dtype="f2")
        self._tex_b.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._fbo_b = self.ctx.framebuffer(color_attachments=[self._tex_b])

        self._tex_c = self.ctx.texture((self._bw, self._bh), 4, dtype="f2")
        self._tex_c.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._fbo_c = self.ctx.framebuffer(color_attachments=[self._tex_c])

    def apply(self, screen_fbo, w, h):
        ctx = self.ctx
        ctx.disable(moderngl.BLEND)
        ctx.disable(moderngl.DEPTH_TEST)

        self._fbo_b.use()
        self._scene_tex.use(0)
        self._blit["u_tex"].value = 0
        self._vao_blit.render(moderngl.TRIANGLES, vertices=3)

        self._fbo_c.use()
        self._tex_b.use(0)
        self._blur["u_tex"].value = 0
        self._blur["u_dir"].value = (1.0 / self._bw, 0.0)
        self._vao_blur.render(moderngl.TRIANGLES, vertices=3)

        self._fbo_b.use()
        self._tex_c.use(0)
        self._blur["u_dir"].value = (0.0, 1.0 / self._bh)
        self._vao_blur.render(moderngl.TRIANGLES, vertices=3)

        screen_fbo.viewport = (0, 0, w, h)
        screen_fbo.use()
        self._scene_tex.use(0)
        self._tex_b.use(1)
        self._comp["u_scene"].value = 0
        self._comp["u_bloom"].value = 1
        self._comp["u_strength"].value = self.strength
        self._comp["u_exposure"].value = self.exposure
        self._vao_comp.render(moderngl.TRIANGLES, vertices=3)

File 5 — forge/app.py (updated — replaces the whole file; new render order: solids → glow → bloom → overlay)

"""The Forge class: window, GL context, main loop.

Render pipeline per frame (Amendment A1):
    scene FBO (RGBA16F + depth):
        1. SOLID pass  — opaque lit ships, depth test + write, no blend
        2. GLOW pass   — additive lines/panels/labels, depth test ON,
                         depth write OFF (holograms occluded by hulls)
    bloom (downsample, blur, composite + tone map) -> screen
    crisp screen overlay (fps corner, F1 debug lines)
"""

import datetime
import os
import time

import numpy as np
import moderngl
import pyglet
from pyglet.window import key

from .camera import Camera
from .shaders import LINE_VERT, LINE_FRAG
from .batches import build_vertices
from .bloom import Bloom
from .solid import SolidMesh, SolidRenderer
from .text import GlyphAtlas, TextRenderer, PanelRenderer, make_quad_program
from .vobjects import Label, ImagePanel

PULSE_DT = 0.1
_INITIAL_VBO_BYTES = 4 * 1024 * 1024


class Forge:
    def __init__(self, settings):
        self._settings = dict(settings)
        width = int(settings.get("width", 1280))
        height = int(settings.get("height", 720))
        title = settings.get("title", "Homeworld: A Good Basis")
        version = settings.get("version", "0.0.0")
        self._caption_base = f"{title} — forge v{version}"

        config = pyglet.gl.Config(
            double_buffer=True, major_version=3, minor_version=3,
            depth_size=24)
        self.window = pyglet.window.Window(
            width=width, height=height, caption=self._caption_base,
            resizable=True, config=config,
            vsync=bool(settings.get("vsync", True)),
            fullscreen=bool(settings.get("fullscreen", False)))
        self.window.switch_to()
        self.ctx = moderngl.create_context()

        self._prog = self.ctx.program(
            vertex_shader=LINE_VERT, fragment_shader=LINE_FRAG)
        self._vbo = self.ctx.buffer(reserve=_INITIAL_VBO_BYTES, dynamic=True)
        self._vao = self._make_vao()

        self._bloom = Bloom(
            self.ctx,
            strength=float(settings.get("bloom_strength", 0.85)),
            exposure=float(settings.get("exposure", 2.5)))
        self._solid = SolidRenderer(self.ctx)

        self._quad_prog = make_quad_program(self.ctx)
        self._atlas = GlyphAtlas(self.ctx, px=48)
        self._text = TextRenderer(self.ctx, self._atlas, self._quad_prog)
        self._panels = PanelRenderer(self.ctx, self._quad_prog)

        self.camera = Camera()
        self._vobjects = []
        self._debug_lines = []
        self._show_debug = False
        self._want_screenshot = False
        self._fps_value = 0.0

        def _on_key_press(symbol, modifiers):
            if symbol == key.F12:
                self._want_screenshot = True
            elif symbol == key.F1:
                self._show_debug = not self._show_debug

        self.window.push_handlers(on_key_press=_on_key_press)

        self._fps_frames = 0
        self._fps_t0 = time.perf_counter()

    # ---- frozen interface ----

    def add(self, vob):
        if vob not in self._vobjects:
            self._vobjects.append(vob)

    def remove(self, vob):
        if vob in self._vobjects:
            self._vobjects.remove(vob)

    def set_debug_lines(self, lines):
        self._debug_lines = list(lines)

    def screenshot(self, path=None):
        os.makedirs("screenshots", exist_ok=True)
        if path is None:
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join("screenshots", f"{stamp}.png")
        pyglet.image.get_buffer_manager().get_color_buffer().save(path)
        return path

    def run(self, tick_cb, frame_cb):
        prev = time.perf_counter()
        accumulator = 0.0
        while not self.window.has_exit:
            self.window.dispatch_events()
            if self.window.has_exit:
                break
            now = time.perf_counter()
            real_dt = min(now - prev, 0.25)
            prev = now
            accumulator += real_dt
            while accumulator >= PULSE_DT:
                tick_cb(PULSE_DT)
                accumulator -= PULSE_DT
            frame_cb(accumulator / PULSE_DT)
            self._render()
            if self._want_screenshot:
                self._want_screenshot = False
                saved = self.screenshot()
                print(f"screenshot saved: {saved}")
            self.window.flip()
            self._count_fps()
        self.window.close()

    # ---- internals ----

    def _make_vao(self):
        return self.ctx.vertex_array(
            self._prog, [(self._vbo, "3f 4f 1f", "in_pos", "in_color", "in_u")])

    def _render(self):
        w, h = self.window.get_framebuffer_size()
        if w <= 0 or h <= 0:
            return

        self._bloom.ensure_size(w, h)
        fbo = self._bloom.scene_fbo
        fbo.depth_mask = True
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 1.0, depth=1.0)

        view = self.camera.view()
        mvp = self.camera.proj(w / h) @ view
        mvp_t = np.ascontiguousarray(mvp.T, dtype=np.float32)

        # ---- 1. SOLID pass: opaque lit ships ----
        solids = [v for v in self._vobjects
                  if isinstance(v, SolidMesh) and v.visible]
        if solids:
            self.ctx.enable(moderngl.DEPTH_TEST)
            self.ctx.disable(moderngl.BLEND)
            self._solid.draw(solids, mvp_t, self.camera.eye())

        # ---- 2. GLOW pass: additive holograms, occluded by hulls ----
        self.ctx.enable(moderngl.DEPTH_TEST)
        fbo.depth_mask = False
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)

        self._prog["u_mvp"].write(mvp_t)
        data = build_vertices(self._vobjects, self.camera.eye())
        if data.shape[0] > 0:
            if data.nbytes > self._vbo.size:
                self._vbo.release()
                self._vbo = self.ctx.buffer(reserve=2 * data.nbytes,
                                            dynamic=True)
                self._vao = self._make_vao()
            self._vbo.write(data.tobytes())
            self._vao.render(mode=moderngl.TRIANGLES, vertices=data.shape[0])

        panels = [v for v in self._vobjects
                  if isinstance(v, ImagePanel) and v.visible]
        labels = [v for v in self._vobjects
                  if isinstance(v, Label) and v.visible]
        if panels:
            self._panels.draw(panels, view, mvp_t)
        if labels:
            self._text.draw_labels(labels, view, mvp_t)

        # ---- bloom -> screen ----
        self._bloom.apply(self.ctx.screen, w, h)

        # ---- crisp overlay ----
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        items = [(f"{self._fps_value:.0f} fps", 10, 10, 18,
                  (0.5, 0.85, 1.0, 0.9))]
        if self._show_debug:
            y = h - 34
            for line in self._debug_lines:
                items.append((line, 10, y, 20, (0.9, 0.9, 0.9, 0.95)))
                y -= 26
        self._text.draw_screen(items, w, h)

    def _count_fps(self):
        self._fps_frames += 1
        now = time.perf_counter()
        if now - self._fps_t0 >= 1.0:
            self._fps_value = self._fps_frames / (now - self._fps_t0)
            self.window.set_caption(
                f"{self._caption_base} — {self._fps_value:.0f} fps")
            self._fps_frames = 0
            self._fps_t0 = now

File 6 — forge/__init__.py (updated)

"""forge — the render engine of Homeworld: A Good Basis.

Solid lit ships (Amendment A1) + glowing holographic math layer +
bloom + text. moderngl + pyglet + numpy + Pillow, nothing else.
"""

from .app import Forge, PULSE_DT
from .camera import Camera
from .solid import SolidMesh
from .vobjects import (
    VObject, Line, Arrow, DashedLine, Grid, WireSphere,
    WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel,
)

__all__ = [
    "Forge", "PULSE_DT", "Camera", "SolidMesh",
    "VObject", "Line", "Arrow", "DashedLine", "Grid", "WireSphere",
    "WireMesh", "SpannedBox", "Ellipsoid", "Trail", "Label", "ImagePanel",
]

File 7 — content/shipwright.py (new file — the procedural ship builder)

"""shipwright — procedural solid-ship generator (Amendment A1).

Each class is BUILT, not hand-typed: lofted hull sections (rounded or
boxy cross-sections), slab wings/fins/masts, command towers, engine
nozzles with emissive exhaust discs, painted per-face hull panels
with deterministic per-class variation. Hundreds to ~1500 triangles
per ship. Deterministic: same class name -> identical mesh, always.

build_ship(klass, spec) -> (vertices (N,3), triangles (M,3),
colors (N,4), emissive (N,3)); spec is the ships.json entry (its
"color" drives the palette).
"""

import zlib

import numpy as np

ENGINE_CYAN = (0.5, 1.8, 2.4)
ENGINE_WARM = (2.0, 1.3, 0.55)
MAW_AMBER = (2.0, 1.15, 0.35)
DARK = (0.15, 0.16, 0.19, 1.0)


def _rng(name):
    return np.random.default_rng(zlib.crc32(name.encode()))


class Builder:
    def __init__(self):
        self.v, self.t, self.c, self.e = [], [], [], []

    def face(self, pts, color, emissive=(0.0, 0.0, 0.0)):
        i = len(self.v)
        pts = [tuple(map(float, p)) for p in pts]
        self.v += pts
        n = len(pts)
        self.c += [tuple(color)] * n
        self.e += [tuple(emissive)] * n
        for k in range(1, n - 1):
            self.t.append([i, i + k, i + k + 1])

    def result(self):
        return (np.asarray(self.v, dtype=np.float64),
                np.asarray(self.t, dtype=np.int64),
                np.asarray(self.c, dtype=np.float64),
                np.asarray(self.e, dtype=np.float64))


def _hull(rgb):
    return (0.42 * rgb[0] + 0.36, 0.42 * rgb[1] + 0.36,
            0.42 * rgb[2] + 0.36)


def _panel(base, rng, var=0.16):
    f = 1.0 - var * 0.5 + var * rng.random()
    return (base[0] * f, base[1] * f, base[2] * f, 1.0)


def _ring(z, rx, ry, n=14, p=1.0, y0=0.0):
    a = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    cs, sn = np.cos(a), np.sin(a)
    x = rx * np.sign(cs) * np.abs(cs) ** p
    y = ry * np.sign(sn) * np.abs(sn) ** p + y0
    return np.stack([x, y, np.full(n, z)], axis=1)


def _loft(b, rings, base, rng, var=0.16, cap0=True, cap1=True):
    for r0, r1 in zip(rings[:-1], rings[1:]):
        n = len(r0)
        for j in range(n):
            k = (j + 1) % n
            b.face([r0[j], r0[k], r1[k], r1[j]], _panel(base, rng, var))
    if cap0:
        b.face(list(rings[0][::-1]), _panel(base, rng, var))
    if cap1:
        b.face(list(rings[-1]), _panel(base, rng, var))


def _slab(b, outline, axis, th, color, emissive=(0.0, 0.0, 0.0)):
    o = np.asarray(outline, dtype=np.float64)
    off = np.asarray(axis, dtype=np.float64) * (th * 0.5)
    top, bot = o + off, o - off
    b.face(list(top), color, emissive)
    b.face(list(bot[::-1]), color, emissive)
    n = len(o)
    for j in range(n):
        k = (j + 1) % n
        b.face([top[j], top[k], bot[k], bot[j]], color, emissive)


def _box(b, center, size, color):
    cx, cy, cz = center
    sx, sy, sz = size
    rect = [(cx - sx / 2, cy, cz - sz / 2), (cx + sx / 2, cy, cz - sz / 2),
            (cx + sx / 2, cy, cz + sz / 2), (cx - sx / 2, cy, cz + sz / 2)]
    _slab(b, rect, (0, 1, 0), sy, color)


def _tube(b, x, y, z0, z1, r, n, color):
    off = np.array([x, y, 0.0])
    r0 = _ring(z0, r, r, n) + off
    r1 = _ring(z1, r, r, n) + off
    for j in range(n):
        k = (j + 1) % n
        b.face([r0[j], r0[k], r1[k], r1[j]], color)
    b.face(list(r0[::-1]), color)
    b.face(list(r1), color)


def _nozzle(b, x, y, z_rear, r, glow, n=10):
    off = np.array([x, y, 0.0])
    rf = _ring(z_rear + 2.4 * r, 0.8 * r, 0.8 * r, n) + off
    rr = _ring(z_rear, r, r, n) + off
    for j in range(n):
        k = (j + 1) % n
        b.face([rf[j], rf[k], rr[k], rr[j]], DARK)
    b.face(list(rr[::-1]), (0.05, 0.05, 0.06, 1.0), glow)


# ---- class recipes (forward = +z, up = +y) ----

def _fighter(spec):
    b, rng = Builder(), _rng("fighter")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 14, 1.0, y0) for z, rx, ry, y0 in [
        (1.95, 0.03, 0.03, 0.00), (1.50, 0.13, 0.11, 0.02),
        (0.95, 0.24, 0.19, 0.04), (0.35, 0.30, 0.25, 0.05),
        (-0.30, 0.29, 0.25, 0.05), (-0.95, 0.23, 0.21, 0.03),
        (-1.45, 0.16, 0.16, 0.00), (-1.80, 0.10, 0.11, 0.00)]]
    _loft(b, rings, base, rng)
    glass = (0.05, 0.09, 0.14, 1.0)
    canopy = [_ring(z, rx, ry, 10, 1.0, y0) for z, rx, ry, y0 in [
        (0.85, 0.02, 0.02, 0.24), (0.45, 0.10, 0.07, 0.33),
        (0.00, 0.11, 0.07, 0.34), (-0.35, 0.08, 0.05, 0.28)]]
    _loft(b, canopy, glass, rng, var=0.03)
    for s in (1, -1):
        wing = [(s * 0.28, 0.0, 0.55), (s * 1.85, -0.06, -0.60),
                (s * 1.90, -0.06, -1.05), (s * 0.28, 0.0, -0.80)]
        _slab(b, wing, (0, 1, 0), 0.07, acc)
    fin = [(0, 0.18, -0.75), (0, 0.85, -1.35), (0, 0.85, -1.60),
           (0, 0.14, -1.50)]
    _slab(b, fin, (1, 0, 0), 0.06, acc)
    for s in (1, -1):
        _nozzle(b, s * 0.30, 0.0, -2.05, 0.12, ENGINE_CYAN)
    return b.result()


def _corvette(spec):
    b, rng = Builder(), _rng("corvette")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 12, 0.55, y0) for z, rx, ry, y0 in [
        (2.30, 0.16, 0.14, 0.00), (1.60, 0.62, 0.42, 0.04),
        (0.60, 0.85, 0.58, 0.06), (-0.50, 0.85, 0.58, 0.06),
        (-1.50, 0.68, 0.50, 0.03), (-2.20, 0.42, 0.36, 0.00)]]
    _loft(b, rings, base, rng)
    for s in (1, -1):
        _tube(b, s * 0.40, 0.20, 1.20, 2.75, 0.08, 8, DARK)
        _box(b, (s * 1.05, 0.0, -1.10), (0.45, 0.42, 1.10),
             _panel(base, rng))
    _slab(b, [(0, 0.6, 0.4), (0, 1.1, -0.4), (0, 1.1, -0.8),
              (0, 0.55, -0.9)], (1, 0, 0), 0.07, acc)
    for s in (1, -1):
        _nozzle(b, s * 0.40, 0.0, -2.55, 0.17, ENGINE_CYAN)
    return b.result()


def _collector(spec):
    b, rng = Builder(), _rng("collector")
    base = _hull(spec["color"])
    rings = [_ring(z, rx, ry, 14, 1.0, y0) for z, rx, ry, y0 in [
        (2.10, 0.32, 0.32, 0.00), (1.50, 0.85, 0.72, -0.02),
        (0.50, 1.15, 0.98, -0.05), (-0.60, 1.15, 0.98, -0.05),
        (-1.60, 0.85, 0.75, -0.02), (-2.20, 0.40, 0.40, 0.00)]]
    _loft(b, rings, base, rng, cap0=False)
    b.face(list(rings[0][::-1]), (0.06, 0.05, 0.04, 1.0), MAW_AMBER)
    for s in (1, -1):
        _tube(b, s * 1.05, 0.15, 1.00, -1.40, 0.32, 10, _panel(base, rng))
    _nozzle(b, 0.0, 0.0, -2.60, 0.28, ENGINE_WARM)
    return b.result()


def _frigate(spec):
    b, rng = Builder(), _rng("frigate")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 14, 0.7, y0) for z, rx, ry, y0 in [
        (3.60, 0.13, 0.12, 0.00), (2.70, 0.50, 0.40, 0.03),
        (1.30, 0.72, 0.55, 0.05), (-0.40, 0.76, 0.60, 0.05),
        (-2.00, 0.62, 0.50, 0.03), (-3.20, 0.40, 0.35, 0.00)]]
    _loft(b, rings, base, rng)
    for s in (1, -1):
        prong = [(s * 0.28, 0.0, 2.60), (s * 0.50, 0.0, 4.10),
                 (s * 0.62, 0.0, 3.90), (s * 0.52, 0.0, 2.45)]
        _slab(b, prong, (0, 1, 0), 0.16, acc)
    mast = [(0, 0.70, -0.20), (0, 1.70, -0.90), (0, 1.70, -1.25),
            (0, 0.60, -1.30)]
    _slab(b, mast, (1, 0, 0), 0.08, acc)
    b.face([(-0.12, 1.72, -0.95), (0.12, 1.72, -0.95),
            (0.12, 1.72, -1.20), (-0.12, 1.72, -1.20)],
           (0.06, 0.06, 0.07, 1.0), ENGINE_CYAN)
    for x in (-0.5, 0.0, 0.5):
        _nozzle(b, x, 0.0, -3.55, 0.20, ENGINE_CYAN)
    return b.result()


def _mothership(spec):
    b, rng = Builder(), _rng("mothership")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 16, 0.65, y0) for z, rx, ry, y0 in [
        (7.20, 0.50, 0.45, 0.00), (5.60, 1.70, 1.25, 0.10),
        (3.60, 2.35, 1.80, 0.15), (1.20, 2.65, 2.10, 0.15),
        (-1.40, 2.70, 2.15, 0.15), (-3.80, 2.45, 2.00, 0.10),
        (-5.80, 1.70, 1.50, 0.00), (-7.00, 1.00, 0.95, 0.00)]]
    _loft(b, rings, base, rng, var=0.12)
    _box(b, (0.0, 2.55, 2.20), (1.10, 0.90, 1.80), _panel(base, rng))
    _box(b, (0.0, 3.25, 1.80), (0.70, 0.60, 1.00), _panel(base, rng))
    b.face([(-0.30, 3.30, 2.32), (0.30, 3.30, 2.32),
            (0.30, 3.50, 2.32), (-0.30, 3.50, 2.32)],
           (0.10, 0.10, 0.10, 1.0), (1.6, 1.1, 0.5))
    for s in (1, -1):
        b.face([(s * 2.74, -0.30, 2.50), (s * 2.74, -0.30, -2.50),
                (s * 2.74, 0.30, -2.50), (s * 2.74, 0.30, 2.50)],
               (0.08, 0.08, 0.09, 1.0), (1.3, 0.85, 0.35))
    _slab(b, [(0, 2.20, -3.00), (0, 3.40, -4.20), (0, 3.40, -4.80),
              (0, 2.00, -4.40)], (1, 0, 0), 0.09, acc)
    _nozzle(b, 0.0, 0.30, -7.40, 0.42, ENGINE_WARM, n=12)
    for s in (1, -1):
        _nozzle(b, s * 0.75, -0.25, -7.40, 0.40, ENGINE_WARM, n=12)
    return b.result()


_RECIPES = {
    "fighter": _fighter,
    "corvette": _corvette,
    "collector": _collector,
    "frigate": _frigate,
    "mothership": _mothership,
}


def build_ship(klass, spec):
    recipe = _RECIPES.get(klass)
    if recipe is None:                      # generic fallback hull
        b, rng = Builder(), _rng(klass)
        base = _hull(spec.get("color", [0.6, 0.7, 0.8, 1.0]))
        rings = [_ring(z, r, r * 0.8, 12) for z, r in [
            (1.8, 0.05), (1.0, 0.5), (0.0, 0.7), (-1.0, 0.5), (-1.8, 0.2)]]
        _loft(b, rings, base, rng)
        _nozzle(b, 0.0, 0.0, -2.1, 0.18, ENGINE_CYAN)
        return b.result()
    return recipe(spec)

File 8 — app.py (updated — replaces the whole file; ships are now solid, with a glowing selection ring)

"""app.py — the game shell of Homeworld: A Good Basis.

Amendment A1: ships are solid lit hulls (content/shipwright.py);
the math layer (basis arrows, combination ghost, trails, selection
ring) remains glowing holograms drawn over them.

    W/S  A/D  R/F   edit the combination coefficients (c3, c1, c2)
    ENTER commit | X diagonal/staged | BACKSPACE clear | Q/E squad
    TAB select ship | C recenter camera | arrows/PgUp/PgDn camera
    P pause | F1 debug | F12 screenshot | ESC quit
"""

import json
import math
import os
import sys
import time
import traceback

import numpy as np

from forge import (Forge, Grid, Arrow, DashedLine, Label, Line, Trail,
                   SolidMesh)
from helm import Helm
from fleet import FleetSim, MoveCombination
from content import ContentDB
from content.shipwright import build_ship

COEFF_RATE = 2.0
COEFF_SNAP = 0.5
_MESH_CACHE = {}


def _aim_matrix(forward):
    f = np.asarray(forward, dtype=np.float64)
    n = np.linalg.norm(f)
    f = f / n if n > 1e-9 else np.array([0.0, 0.0, 1.0])
    up = np.array([0.0, 1.0, 0.0])
    if abs(f @ up) > 0.98:
        up = np.array([1.0, 0.0, 0.0])
    r = np.cross(up, f)
    r = r / np.linalg.norm(r)
    u = np.cross(f, r)
    return np.column_stack([r, u, f])


def _circle_points(center, radius, n=40):
    a = np.linspace(0.0, 2.0 * np.pi, n + 1)
    return np.stack([center[0] + radius * np.cos(a),
                     np.full(n + 1, center[1]),
                     center[2] + radius * np.sin(a)], axis=1)


class ShipView:
    """Solid lit hull + holographic trail."""

    def __init__(self, forge_, klass, content):
        if klass not in _MESH_CACHE:
            _MESH_CACHE[klass] = build_ship(klass, content.ship_class(klass))
        verts, tris, colors, emissive = _MESH_CACHE[klass]
        self.solid = SolidMesh(verts, tris, colors, emissive)
        self.radius = max(1.0, 1.2 * float(
            np.max(np.linalg.norm(verts[:, [0, 2]], axis=1))))
        self.trail = Trail(max_points=60, color=(0.5, 0.8, 1.0, 0.45),
                           width=0.04)
        self.dir = np.array([0.0, 0.0, 1.0])
        forge_.add(self.solid)
        forge_.add(self.trail)

    def update(self, pos, velocity, selected):
        if np.linalg.norm(velocity) > 1e-6:
            self.dir = velocity / np.linalg.norm(velocity)
        self.solid.set_highlight(selected)
        self.solid.set_transform(_aim_matrix(self.dir), pos)

    def remove(self, forge_):
        forge_.remove(self.solid)
        forge_.remove(self.trail)


class App:
    def __init__(self):
        with open("settings.json", "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        self.content = ContentDB("content")
        self.forge = Forge(self.settings)
        self.helm = Helm(self.settings)
        self.helm.attach(self.forge.window)

        self.sim = FleetSim(self.settings.get("seed", 1234), self.content)
        self.sim.spawn("mothership", (0.0, 0.0, -12.0))
        self.sim.spawn("fighter", (6.0, 0.0, 3.0), squad=1)
        self.sim.spawn("fighter", (8.0, 0.0, -2.0), squad=1)
        self.sim.spawn("fighter", (4.0, 0.0, -6.0), squad=1)
        self.sim.spawn("corvette", (-8.0, 0.0, 5.0), squad=2)
        self.sim.spawn("collector", (-11.0, 0.0, -1.0), squad=2)
        self.sim.spawn("frigate", (-6.0, 0.0, -8.0), squad=2)

        self.forge.add(Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1),
                            n=12, spacing=2.0))
        basis_colors = [(1.0, 0.3, 0.3, 1.0), (0.3, 1.0, 0.4, 1.0),
                        (0.35, 0.55, 1.0, 1.0)]
        for e, col, name in zip(self.sim.engine_vectors, basis_colors,
                                ("e1", "e2", "e3")):
            self.forge.add(Arrow((0, 0, 0), 3.0 * e, head_size=0.5,
                                 color=col))
            self.forge.add(Label(name, 3.6 * e, size=0.8,
                                 color=(col[0], col[1], col[2], 0.9)))

        self.ghost_legs = [
            DashedLine((0, 0, 0), (0, 0, 0), dash=0.4, color=basis_colors[i])
            for i in range(3)]
        self.ghost_diag = Arrow((0, 0, 0), (0, 0, 1), head_size=0.7,
                                color=(1.0, 1.0, 1.0, 0.9), glow=1.2)
        self.ghost_label = Label("", (0, 0, 0), size=0.8,
                                 color=(1.0, 1.0, 1.0, 0.9))
        for g in self.ghost_legs + [self.ghost_diag, self.ghost_label]:
            g.visible = False
            self.forge.add(g)

        self.sel_ring = Line(_circle_points((0, 0, 0), 1.0),
                             color=(1.0, 1.0, 1.0, 0.8), glow=1.3,
                             width=0.05)
        self.sel_ring.visible = False
        self.forge.add(self.sel_ring)

        self.views = {}
        self.coeffs = np.zeros(3)
        self.diagonal = True
        self.sel_index = 0
        self.cmd_squad = 1
        self.paused = False
        self.snap = self.sim.snapshot()
        self._sync_views()
        self._prev_frame = time.perf_counter()

        self.forge.camera.distance = 42.0
        self.forge.camera.set_orbit((0.0, 0.0, 0.0))

        print("Homeworld: A Good Basis — shakedown shell (solid ships).")
        print("W/S A/D R/F coefficients | ENTER commit | X mode | "
              "BACKSPACE clear | Q/E squad")
        print("TAB select | C recenter | arrows/PgUp/PgDn camera | "
              "P pause | F1 debug | ESC quit")

    # ---- helpers ----

    def _snapped(self):
        return np.round(self.coeffs / COEFF_SNAP) * COEFF_SNAP

    def _selected_id(self):
        if not self.snap.ship_ids:
            return None
        self.sel_index %= len(self.snap.ship_ids)
        return self.snap.ship_ids[self.sel_index]

    def _squads(self):
        squads = sorted({int(s) for s in self.snap.squad if s > 0})
        return squads if squads else [1]

    def _sync_views(self):
        alive = set(self.snap.ship_ids)
        for sid in list(self.views.keys()):
            if sid not in alive:
                self.views.pop(sid).remove(self.forge)
        for sid, klass in zip(self.snap.ship_ids, self.snap.klasses):
            if sid not in self.views:
                self.views[sid] = ShipView(self.forge, klass, self.content)

    # ---- the 10 Hz pulse ----

    def tick(self, dt):
        events, axes, pointer = self.helm.poll()
        for ev in events:
            if ev.value == 1.0:
                self._on_action(ev.action)
        if self.paused:
            return

        self.coeffs[0] += axes["TRIM_X"] * COEFF_RATE * dt
        self.coeffs[1] += axes["TRIM_Y"] * COEFF_RATE * dt
        self.coeffs[2] += axes["TRIM_Z"] * COEFF_RATE * dt

        for ev in self.sim.tick(dt):
            self._on_fleet_event(ev)
        self.snap = self.sim.snapshot()
        self._sync_views()
        for k, sid in enumerate(self.snap.ship_ids):
            self.views[sid].trail.push(self.snap.pos[k])

    def _on_action(self, action):
        if action == "SELECT_NEXT":
            self.sel_index += 1
        elif action == "SELECT_PREV":
            self.sel_index -= 1
        elif action in ("SQUAD_NEXT", "SQUAD_PREV"):
            squads = self._squads()
            if self.cmd_squad in squads:
                i = squads.index(self.cmd_squad)
                step = 1 if action == "SQUAD_NEXT" else -1
                self.cmd_squad = squads[(i + step) % len(squads)]
            else:
                self.cmd_squad = squads[0]
            print(f"commanding squad {self.cmd_squad}")
        elif action == "ORDER_CANCEL":
            self.coeffs[:] = 0.0
        elif action == "FLIGHT_MODE_TOGGLE":
            self.diagonal = not self.diagonal
            print(f"flight mode: "
                  f"{'diagonal' if self.diagonal else 'component-by-component'}")
        elif action == "CAM_MODE_CYCLE":
            sid = self._selected_id()
            if sid is not None:
                k = self.snap.ship_ids.index(sid)
                self.forge.camera.set_orbit(self.snap.pos[k])
        elif action == "PAUSE":
            self.paused = not self.paused
            print("paused" if self.paused else "unpaused")
        elif action == "ORDER_CONFIRM":
            c = self._snapped()
            if np.linalg.norm(c) < 1e-9:
                print("FLEET: nothing to commit — coefficients are zero")
                return
            self.sim.submit(MoveCombination(
                squad=self.cmd_squad,
                coeffs=tuple(float(v) for v in c),
                diagonal=self.diagonal))
            terms = " + ".join(f"{c[i]:g}*e{i + 1}" for i in range(3)
                               if abs(c[i]) > 1e-9)
            print(f"ORDER: squad {self.cmd_squad} <- {terms}  "
                  f"({'diagonal' if self.diagonal else 'staged'})")
            self.coeffs[:] = 0.0

    def _on_fleet_event(self, ev):
        if ev.kind == "ORDER_REJECTED":
            print(f"FLEET: order rejected — {ev.data['reason']}")
        elif ev.kind == "RANK_CHANGED":
            print(f"FLEET: fleet rank {ev.data['old']} -> {ev.data['new']}")
        elif ev.kind == "SHIP_BUILT":
            print(f"FLEET: built {ev.data['klass']} "
                  f"(rank {'up' if ev.data['rank_increased'] else 'same'})")

    # ---- every display frame ----

    def frame(self, alpha):
        now = time.perf_counter()
        fdt = min(now - self._prev_frame, 0.1)
        self._prev_frame = now

        axes = self.helm.poll_axes_only()
        self.forge.camera.orbit_input(
            axes["CAM_YAW"] * 1.8 * fdt,
            axes["CAM_PITCH"] * 1.2 * fdt,
            axes["CAM_ZOOM"] * 0.9 * fdt)

        snap = self.snap
        sel = self._selected_id()
        squad_positions = []
        for k, sid in enumerate(snap.ship_ids):
            p = snap.prev_pos[k] + (snap.pos[k] - snap.prev_pos[k]) * alpha
            v = snap.pos[k] - snap.prev_pos[k]
            self.views[sid].update(p, v, sid == sel)
            if sid == sel:
                self.sel_ring.visible = True
                self.sel_ring.set_data(_circle_points(
                    p - np.array([0.0, 0.4, 0.0]), self.views[sid].radius))
            if snap.squad[k] == self.cmd_squad:
                squad_positions.append(p)
        if sel is None:
            self.sel_ring.visible = False

        self._update_ghost(squad_positions)

        c = self._snapped()
        sel_name = ""
        if sel is not None:
            klass = snap.klasses[snap.ship_ids.index(sel)]
            sel_name = self.content.ship_class(klass)["display_name"]
        self.forge.set_debug_lines([
            f"pulse {snap.pulse}   fleet rank {snap.rank}",
            f"coeffs ({c[0]:+.1f}, {c[1]:+.1f}, {c[2]:+.1f})   "
            f"mode {'diagonal' if self.diagonal else 'staged'}   "
            f"squad {self.cmd_squad}",
            f"selected ship #{sel} ({sel_name})",
        ] + (["PAUSED"] if self.paused else []))

    def _update_ghost(self, squad_positions):
        c = self._snapped()
        active = len(squad_positions) > 0 and np.linalg.norm(c) > 1e-9
        for g in self.ghost_legs + [self.ghost_diag, self.ghost_label]:
            g.visible = active
        if not active:
            return
        base = np.mean(squad_positions, axis=0)
        cursor = base.copy()
        for i, e in enumerate(self.sim.engine_vectors):
            nxt = cursor + c[i] * e
            self.ghost_legs[i].set_data(cursor, nxt, dash=0.4)
            self.ghost_legs[i].visible = abs(c[i]) > 1e-9
            cursor = nxt
        self.ghost_diag.set_data(base, cursor, head_size=0.7)
        self.ghost_label.set_data(pos=cursor + np.array([0.0, 1.0, 0.0]))
        self.ghost_label.set_text(
            f"({c[0]:+.1f}, {c[1]:+.1f}, {c[2]:+.1f})")

    def run(self):
        self.forge.run(self.tick, self.frame)


def main():
    App().run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("app crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)

File 9 — settings.json (version bump)

{
    "title": "Homeworld: A Good Basis",
    "version": "0.7.0",
    "width": 1280,
    "height": 720,
    "fullscreen": false,
    "vsync": true,
    "bloom_strength": 0.85,
    "exposure": 2.5,
    "seed": 1234,
    "input": {
        "pilot_device": "keyboard",
        "navigator_device": "mouse",
        "keyboard_overrides": {}
    }
}

📋 YOUR STEPS

    DeepSeek: the 9 files, verbatim, commit: AMENDMENT A1: solid shaded ships — mesh shader, depth pipeline, procedural shipwright — update COMMENTARIES.md.
    Run run.bat.

👀 WHAT YOU SHOULD SEE

Opaque, lit, paneled warships. The fighter is a real fuselage with a dark glass canopy, swept colored wings, a tail fin, and two cyan-glowing engine nozzles. The mothership is a 14-unit-long plated hull with a command tower, lit bridge windows, glowing amber hangar strips down her flanks, and three warm engine bells. Light falls on them from above-right; there's a specular sheen and a faint rim glow on silhouette edges; hull plates vary in tone like riveted panels. Nothing is transparent — ships hide the grid behind them, and the holographic ghost arrows pass behind hulls correctly. Selection is a glowing ring under the ship + a subtle white emissive pulse on the hull. Fly a combination order and watch lit hulls bank across the grid with engines blooming.
📝 REPORT BACK — as art director this time

You now hold the taste-knobs, and I want specifics: (a) which ship looks best / worst, (b) too dark or too bright overall, (c) panel variation — nice or noisy, (d) engine glow — more or less. Every one of these is a one-number change. We iterate until you would want to play it — that's the law now, and it's written in notes/amendment_a1_art_direction.md. 🚀
