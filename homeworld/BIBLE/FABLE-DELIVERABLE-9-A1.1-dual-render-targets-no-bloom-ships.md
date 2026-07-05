# FABLE DELIVERABLE 9 — Amendment A1.1: ships never bloom (dual render targets), dark mothership at origin, overlay axes

**From:** Claude Fable 5 (Parent 1)
**Date:** July 5, 2026
**Status:** VERBATIM — delivered to DeepSeek for drop-in

---

Both calls are exactly right, and both are now law:

1. The mothership IS the origin. She goes back to (0,0,0), painted dark slate, and the basis vectors e1,e2,e3 are drawn on top of her hull (a new "overlay hologram" pass that ignores depth for exactly these objects) — long bright arrows piercing out of a dark ship. Math is never sacrificed for looks.
2. No bloom on ships — ever. The proper fix is architectural, and it also fixes something you noticed ("details hidden"): I split rendering into two buffers. Ships render into a clean buffer that goes to screen untouched — no bloom, no tone-map wash, so every panel and shading gradient stays crisp, like real Homeworld hulls. Only the hologram layer (vectors, grids, ghosts, trails, labels) renders into the glow buffer that feeds bloom. Engine nozzles become dim lit lamps (like HW1 engine cones), not light sources.

## File 1 — forge/shaders.py (updated — replaces the whole file; dual render targets)

```python
"""GLSL shader sources.

Amendment A1.1 (owner): ships must NEVER bloom. The scene renders to
TWO color attachments:
    location 0 — SOLID buffer: lit ships, linear, untouched by bloom
                 or tone mapping (crisp panel detail).
    location 1 — GLOW buffer: holograms (lines, labels, panels),
                 additive; this buffer alone is blurred and tone
                 mapped, then added on top of the solid buffer.
Line/text shaders write 0 to the solid buffer (additive +0 = no-op);
the mesh shader writes 0 to the glow buffer.
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
layout(location = 0) out vec4 f_solid;
layout(location = 1) out vec4 f_glow;
void main() {
    float k = 1.0 - v_u * v_u;
    f_solid = vec4(0.0);
    f_glow = vec4(v_color.rgb * k * k * v_color.a, 1.0);
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
layout(location = 0) out vec4 f_solid;
layout(location = 1) out vec4 f_glow;
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
    float spec = pow(max(dot(n, h), 0.0), 44.0) * 0.45;
    float rim = pow(1.0 - max(dot(n, vdir), 0.0), 3.0) * 0.18;

    vec3 albedo = v_color.rgb;
    vec3 c = albedo * (AMBIENT + KEY_COL * dk + FILL_COL * df)
           + KEY_COL * spec + albedo * rim + v_emissive;
    f_solid = vec4(c, 1.0);
    f_glow = vec4(0.0);
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
uniform sampler2D u_scene;   // solid ships, linear — passed through
uniform sampler2D u_glow;    // hologram layer, full resolution
uniform sampler2D u_bloom;   // blurred hologram layer
uniform float u_strength;
uniform float u_exposure;
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 g = texture(u_glow, v_uv).rgb
           + u_strength * texture(u_bloom, v_uv).rgb;
    g = vec3(1.0) - exp(-g * u_exposure);   // tone map holograms ONLY
    vec3 c = texture(u_scene, v_uv).rgb + g;
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
layout(location = 0) out vec4 f_solid;
layout(location = 1) out vec4 f_glow;
void main() {
    float a = texture(u_tex, v_uv).r;
    f_solid = vec4(0.0);
    f_glow = vec4(v_color.rgb * a * v_color.a, 1.0);
}
"""
```

## File 2 — forge/bloom.py (updated — replaces the whole file; two color attachments, bloom reads only the glow buffer)

```python
"""Scene framebuffer + bloom (Amendment A1.1).

Scene FBO: two RGBA16F color attachments (solid ships / holograms)
sharing one depth buffer. Bloom downsamples and blurs ONLY the glow
attachment; the composite adds tone-mapped glow over the untouched
solid buffer. Ships can never bloom, by construction.
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
        self._solid_tex = None
        self._glow_tex = None
        self._scene_depth = None
        self._tex_b = None
        self._tex_c = None
        self._fbo_b = None
        self._fbo_c = None

    def ensure_size(self, w, h):
        if (w, h) == (self._w, self._h):
            return
        for obj in (self.scene_fbo, self._solid_tex, self._glow_tex,
                    self._scene_depth, self._fbo_b, self._fbo_c,
                    self._tex_b, self._tex_c):
            if obj is not None:
                obj.release()

        self._w, self._h = w, h
        self._bw = max(w // 4, 1)
        self._bh = max(h // 4, 1)

        self._solid_tex = self.ctx.texture((w, h), 4, dtype="f2")
        self._solid_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._glow_tex = self.ctx.texture((w, h), 4, dtype="f2")
        self._glow_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._scene_depth = self.ctx.depth_renderbuffer((w, h))
        self.scene_fbo = self.ctx.framebuffer(
            color_attachments=[self._solid_tex, self._glow_tex],
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

        # downsample the GLOW buffer only
        self._fbo_b.use()
        self._glow_tex.use(0)
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
        self._solid_tex.use(0)
        self._glow_tex.use(1)
        self._tex_b.use(2)
        self._comp["u_scene"].value = 0
        self._comp["u_glow"].value = 1
        self._comp["u_bloom"].value = 2
        self._comp["u_strength"].value = self.strength
        self._comp["u_exposure"].value = self.exposure
        self._vao_comp.render(moderngl.TRIANGLES, vertices=3)
```

## File 3 — forge/app.py (updated — replaces the whole file; adds the overlay-hologram pass for the origin axes)

```python
"""The Forge class: window, GL context, main loop.

Render pipeline (Amendment A1.1):
    scene FBO (solid buffer + glow buffer + depth):
        1. SOLID pass    — opaque lit ships, depth write, no blend
        2. GLOW pass     — additive holograms, depth test ON, write OFF
        3. OVERLAY pass  — holograms with vob.overlay == True, depth
                           test OFF (drawn on top of hulls: the origin
                           axes over the mothership)
    bloom (glow buffer only) -> composite -> screen -> crisp HUD text

Ships never bloom and are never tone mapped; holograms glow.
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

    def _draw_lines(self, vobs):
        data = build_vertices(vobs, self.camera.eye())
        if data.shape[0] == 0:
            return
        if data.nbytes > self._vbo.size:
            self._vbo.release()
            self._vbo = self.ctx.buffer(reserve=2 * data.nbytes,
                                        dynamic=True)
            self._vao = self._make_vao()
        self._vbo.write(data.tobytes())
        self._vao.render(mode=moderngl.TRIANGLES, vertices=data.shape[0])

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

        # ---- 1. SOLID pass ----
        solids = [v for v in self._vobjects
                  if isinstance(v, SolidMesh) and v.visible]
        if solids:
            self.ctx.enable(moderngl.DEPTH_TEST)
            self.ctx.disable(moderngl.BLEND)
            self._solid.draw(solids, mvp_t, self.camera.eye())

        # ---- 2. GLOW pass (depth-tested holograms) ----
        self.ctx.enable(moderngl.DEPTH_TEST)
        fbo.depth_mask = False
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        self._prog["u_mvp"].write(mvp_t)

        normal = [v for v in self._vobjects
                  if not getattr(v, "overlay", False)]
        overlay = [v for v in self._vobjects
                   if getattr(v, "overlay", False)]
        self._draw_lines(normal)

        panels = [v for v in self._vobjects
                  if isinstance(v, ImagePanel) and v.visible]
        labels_n = [v for v in normal
                    if isinstance(v, Label) and v.visible]
        labels_o = [v for v in overlay
                    if isinstance(v, Label) and v.visible]
        if panels:
            self._panels.draw(panels, view, mvp_t)
        if labels_n:
            self._text.draw_labels(labels_n, view, mvp_t)

        # ---- 3. OVERLAY pass (origin axes etc. — on top of hulls) ----
        self.ctx.disable(moderngl.DEPTH_TEST)
        self._prog["u_mvp"].write(mvp_t)
        self._draw_lines(overlay)
        if labels_o:
            self._text.draw_labels(labels_o, view, mvp_t)

        # ---- bloom (glow buffer only) -> screen ----
        self._bloom.apply(self.ctx.screen, w, h)

        # ---- crisp HUD overlay ----
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
```

## File 4 — content/shipwright.py (updated — replaces the whole file; dark mothership, lamp-like nozzles instead of light-emitting ones)

```python
"""shipwright — procedural solid-ship generator (Amendment A1.1).

Change log vs A1: NO ship part uses HDR emissive anymore — engine
nozzles, windows and intake maws are dim lit "lamps" (values <= 1)
in the solid buffer, which never blooms. The mothership hull is dark
slate (owner ruling: she carries the bright origin axes on her back,
so the hull must stay dark for contrast).
"""

import zlib

import numpy as np

ENGINE_CYAN = (0.20, 0.75, 0.95)
ENGINE_WARM = (0.85, 0.55, 0.22)
MAW_AMBER = (0.85, 0.50, 0.18)
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
    base = (0.155, 0.165, 0.195)            # dark slate — owner ruling:
    acc = (spec["color"][0] * 0.6,          # she carries the origin axes
           spec["color"][1] * 0.6,
           spec["color"][2] * 0.6, 1.0)
    rings = [_ring(z, rx, ry, 16, 0.65, y0) for z, rx, ry, y0 in [
        (7.20, 0.50, 0.45, 0.00), (5.60, 1.70, 1.25, 0.10),
        (3.60, 2.35, 1.80, 0.15), (1.20, 2.65, 2.10, 0.15),
        (-1.40, 2.70, 2.15, 0.15), (-3.80, 2.45, 2.00, 0.10),
        (-5.80, 1.70, 1.50, 0.00), (-7.00, 1.00, 0.95, 0.00)]]
    _loft(b, rings, base, rng, var=0.10)
    _box(b, (0.0, 2.55, 2.20), (1.10, 0.90, 1.80), _panel(base, rng))
    _box(b, (0.0, 3.25, 1.80), (0.70, 0.60, 1.00), _panel(base, rng))
    b.face([(-0.30, 3.30, 2.32), (0.30, 3.30, 2.32),
            (0.30, 3.50, 2.32), (-0.30, 3.50, 2.32)],
           (0.10, 0.10, 0.10, 1.0), (0.85, 0.60, 0.28))
    for s in (1, -1):
        b.face([(s * 2.74, -0.30, 2.50), (s * 2.74, -0.30, -2.50),
                (s * 2.74, 0.30, -2.50), (s * 2.74, 0.30, 2.50)],
               (0.08, 0.08, 0.09, 1.0), (0.70, 0.45, 0.18))
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
    if recipe is None:
        b, rng = Builder(), _rng(klass)
        base = _hull(spec.get("color", [0.6, 0.7, 0.8, 1.0]))
        rings = [_ring(z, r, r * 0.8, 12) for z, r in [
            (1.8, 0.05), (1.0, 0.5), (0.0, 0.7), (-1.0, 0.5), (-1.8, 0.2)]]
        _loft(b, rings, base, rng)
        _nozzle(b, 0.0, 0.0, -2.1, 0.18, ENGINE_CYAN)
        return b.result()
    return recipe(spec)
```

## File 5 — content/ships.json (updated)

```json
{
    "mothership": {
        "display_name": "Mothership",
        "signature": [1, 1, 1, 1, 1, 1],
        "cost": 0, "hp": 500, "trim_speed": 0.5,
        "mesh": "meshes/mothership.json", "scale": 1.6,
        "color": [0.45, 0.55, 0.7, 1.0]
    },
    "fighter": {
        "display_name": "Fighter",
        "signature": [2, 0, 0, 1, 0, 0],
        "cost": 40, "hp": 30, "trim_speed": 3.0,
        "mesh": "meshes/fighter.json", "scale": 1.0,
        "color": [0.55, 0.9, 1.0, 1.0]
    },
    "corvette": {
        "display_name": "Corvette",
        "signature": [0, 2, 0, 1, 0, 0],
        "cost": 60, "hp": 60, "trim_speed": 2.0,
        "mesh": "meshes/corvette.json", "scale": 1.1,
        "color": [1.0, 0.6, 0.3, 1.0]
    },
    "collector": {
        "display_name": "Resource Collector",
        "signature": [0, 0, 2, 0, 1, 0],
        "cost": 50, "hp": 40, "trim_speed": 1.5,
        "mesh": "meshes/collector.json", "scale": 1.2,
        "color": [0.5, 1.0, 0.6, 1.0],
        "special": "collector"
    },
    "frigate": {
        "display_name": "Frigate",
        "signature": [0, 0, 0, 2, 0, 1],
        "cost": 90, "hp": 100, "trim_speed": 1.0,
        "mesh": "meshes/frigate.json", "scale": 1.3,
        "color": [0.8, 0.6, 1.0, 1.0]
    }
}
```

## File 6 — app.py (partial — only changed blocks)

Fable says: "In app.py, replace the fleet-spawn block and the static-scene axes block with the following, leaving everything else unchanged"

```python
        self.sim = FleetSim(self.settings.get("seed", 1234), self.content)
        self.sim.spawn("mothership", (0.0, 0.0, 0.0))     # the ORIGIN.
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
            axis = Arrow((0, 0, 0), 10.0 * e, head_size=0.8, color=col,
                         glow=1.2)
            axis.overlay = True          # drawn ON TOP of the mothership
            self.forge.add(axis)
            tag = Label(name, 10.9 * e, size=0.9,
                        color=(col[0], col[1], col[2], 0.95))
            tag.overlay = True
            self.forge.add(tag)
```

## File 7 — settings.json

Bump "version" to "0.7.1" (everything else unchanged).
