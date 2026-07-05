WONDERFUL!!! 🎉 The skeleton walks! Now we give it the soul — Package: BLOOM (New Testament build step 3). This is the pass that turns "nice glowing lines" into the Homeworld-of-wireframes look: real halos around every line, hot white cores, crossings that flare. It also gives you your first feel knob: bloom_strength in settings.json — you can tune the glow yourself, no code needed.

Below are 4 complete files (2 updated, 1 new, 1 settings bump). Send each to DeepSeek exactly as-is.

File 1 — forge/shaders.py (updated — replaces the whole file)

```python
"""GLSL shader sources (NEW_TESTAMENT 1.5 and 1.6).

Two families:

1. The line ribbon shader: each line is expanded on the CPU into a
   camera-facing ribbon with a 'ribbon coordinate' u in [-1, 1] across
   its width. The fragment shader shades intensity = (1 - u^2)^2 so
   every line has a hot bright core and soft edges even before bloom.

2. The bloom pipeline shaders: a fullscreen triangle generated from
   gl_VertexID (no vertex buffer needed), a plain blit (downsample),
   a separable 9-tap Gaussian blur, and the final composite with a
   soft exposure tone map (refinement of NT 1.6's soft tone map:
   c -> 1 - exp(-c * exposure) keeps hot cores white while lifting
   the faint halos, which suits an emissive-on-black world).
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

# Fullscreen triangle from gl_VertexID: covers the screen with 3 vertices,
# uv spans [0,1] over the visible area. No vertex buffer required.
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

# Separable Gaussian, 9 effective taps, sigma ~= 2.0 (weights sum to 1).
# Run twice: once with u_dir = (1/w, 0), once with u_dir = (0, 1/h).
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
    c = vec3(1.0) - exp(-c * u_exposure);   // soft tone map
    f_color = vec4(c, 1.0);
}
"""
```

File 2 — forge/bloom.py (new file)

```python
"""Bloom pipeline (NEW_TESTAMENT 1.6): three-FBO classic bloom.

1. The scene renders into a full-resolution RGBA16F framebuffer.
   Since the world is emissive-on-black, no bright-pass filter is
   needed -- the scene IS the bright pass.
2. Downsample to 1/4 resolution (hardware linear filtering).
3. Separable Gaussian blur: horizontal pass, then vertical pass.
4. Composite to screen: final = scene + strength * blurred, then a
   soft exposure tone map.

All passes draw one fullscreen triangle generated in the vertex
shader from gl_VertexID -- no vertex buffers involved.
"""

import moderngl

from .shaders import FULLSCREEN_VERT, BLIT_FRAG, BLUR_FRAG, COMPOSITE_FRAG


class Bloom:
    def __init__(self, ctx, strength=0.85, exposure=2.5):
        self.ctx = ctx
        self.strength = float(strength)
        self.exposure = float(exposure)

        self._blit = ctx.program(
            vertex_shader=FULLSCREEN_VERT, fragment_shader=BLIT_FRAG
        )
        self._blur = ctx.program(
            vertex_shader=FULLSCREEN_VERT, fragment_shader=BLUR_FRAG
        )
        self._comp = ctx.program(
            vertex_shader=FULLSCREEN_VERT, fragment_shader=COMPOSITE_FRAG
        )
        self._vao_blit = ctx.vertex_array(self._blit, [])
        self._vao_blur = ctx.vertex_array(self._blur, [])
        self._vao_comp = ctx.vertex_array(self._comp, [])

        self._w = 0
        self._h = 0
        self._bw = 0
        self._bh = 0
        self.scene_fbo = None
        self._scene_tex = None
        self._tex_b = None
        self._tex_c = None
        self._fbo_b = None
        self._fbo_c = None

    def ensure_size(self, w, h):
        """(Re)create framebuffers when the window size changes."""
        if (w, h) == (self._w, self._h):
            return
        for obj in (self.scene_fbo, self._scene_tex, self._fbo_b,
                    self._fbo_c, self._tex_b, self._tex_c):
            if obj is not None:
                obj.release()

        self._w, self._h = w, h
        self._bw = max(w // 4, 1)
        self._bh = max(h // 4, 1)

        self._scene_tex = self.ctx.texture((w, h), 4, dtype="f2")
        self._scene_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.scene_fbo = self.ctx.framebuffer(
            color_attachments=[self._scene_tex]
        )

        self._tex_b = self.ctx.texture((self._bw, self._bh), 4, dtype="f2")
        self._tex_b.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._fbo_b = self.ctx.framebuffer(color_attachments=[self._tex_b])

        self._tex_c = self.ctx.texture((self._bw, self._bh), 4, dtype="f2")
        self._tex_c.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._fbo_c = self.ctx.framebuffer(color_attachments=[self._tex_c])

    def apply(self, screen_fbo, w, h):
        """Downsample -> blur H -> blur V -> composite onto screen_fbo."""
        ctx = self.ctx
        ctx.disable(moderngl.BLEND)

        # 1. downsample scene -> B (quarter resolution)
        self._fbo_b.use()
        self._scene_tex.use(0)
        self._blit["u_tex"].value = 0
        self._vao_blit.render(moderngl.TRIANGLES, vertices=3)

        # 2. blur horizontal: B -> C
        self._fbo_c.use()
        self._tex_b.use(0)
        self._blur["u_tex"].value = 0
        self._blur["u_dir"].value = (1.0 / self._bw, 0.0)
        self._vao_blur.render(moderngl.TRIANGLES, vertices=3)

        # 3. blur vertical: C -> B
        self._fbo_b.use()
        self._tex_c.use(0)
        self._blur["u_dir"].value = (0.0, 1.0 / self._bh)
        self._vao_blur.render(moderngl.TRIANGLES, vertices=3)

        # 4. composite to screen
        screen_fbo.viewport = (0, 0, w, h)
        screen_fbo.use()
        self._scene_tex.use(0)
        self._tex_b.use(1)
        self._comp["u_scene"].value = 0
        self._comp["u_bloom"].value = 1
        self._comp["u_strength"].value = self.strength
        self._comp["u_exposure"].value = self.exposure
        self._vao_comp.render(moderngl.TRIANGLES, vertices=3)
```

File 3 — forge/app.py (updated — replaces the whole file)

```python
"""The Forge class: window, GL context, main loop (NEW_TESTAMENT 1.2).

Owns the pyglet window, the moderngl context, the fixed-timestep
accumulator (10 Hz pulses -> tick_cb; every display frame -> frame_cb
with interpolation alpha), and the render pipeline:

    scene pass (additive line ribbons, into an RGBA16F framebuffer)
      -> bloom (downsample, Gaussian blur, composite + tone map)
        -> screen

Additive blending is order-independent, so no sorting is ever needed --
overlapping glow simply gets brighter.
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

PULSE_DT = 0.1                        # 10 Hz logic pulse (frozen)
_INITIAL_VBO_BYTES = 4 * 1024 * 1024  # room for ~20k segments


class Forge:
    def __init__(self, settings):
        self._settings = dict(settings)
        width = int(settings.get("width", 1280))
        height = int(settings.get("height", 720))
        title = settings.get("title", "Homeworld: A Good Basis")
        version = settings.get("version", "0.0.0")
        self._caption_base = f"{title} — forge v{version}"

        config = pyglet.gl.Config(
            double_buffer=True, major_version=3, minor_version=3, depth_size=24
        )
        self.window = pyglet.window.Window(
            width=width,
            height=height,
            caption=self._caption_base,
            resizable=True,
            config=config,
            vsync=bool(settings.get("vsync", True)),
            fullscreen=bool(settings.get("fullscreen", False)),
        )
        self.window.switch_to()
        self.ctx = moderngl.create_context()

        self._prog = self.ctx.program(
            vertex_shader=LINE_VERT, fragment_shader=LINE_FRAG
        )
        self._vbo = self.ctx.buffer(reserve=_INITIAL_VBO_BYTES, dynamic=True)
        self._vao = self._make_vao()

        self._bloom = Bloom(
            self.ctx,
            strength=float(settings.get("bloom_strength", 0.85)),
            exposure=float(settings.get("exposure", 2.5)),
        )

        self.camera = Camera()
        self._vobjects = []
        self._debug_lines = []
        self._want_screenshot = False

        # F12 = screenshot (system button). push_handlers keeps pyglet's
        # default handler alive, so ESC still closes the window.
        def _on_key_press(symbol, modifiers):
            if symbol == key.F12:
                self._want_screenshot = True

        self.window.push_handlers(on_key_press=_on_key_press)

        # fps counter shown in the window title once per second
        self._fps_frames = 0
        self._fps_t0 = time.perf_counter()

    # ---- frozen interface (NEW_TESTAMENT 1.2) ----

    def add(self, vob):
        if vob not in self._vobjects:
            self._vobjects.append(vob)

    def remove(self, vob):
        if vob in self._vobjects:
            self._vobjects.remove(vob)

    def set_debug_lines(self, lines):
        # Text rendering arrives with forge/text.py in a later package.
        # The interface exists now so callers never change.
        self._debug_lines = list(lines)

    def screenshot(self, path=None):
        os.makedirs("screenshots", exist_ok=True)
        if path is None:
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join("screenshots", f"{stamp}.png")
        pyglet.image.get_buffer_manager().get_color_buffer().save(path)
        return path

    def run(self, tick_cb, frame_cb):
        """Main loop. tick_cb(dt) at exactly 10 Hz; frame_cb(alpha) per frame."""
        prev = time.perf_counter()
        accumulator = 0.0
        while not self.window.has_exit:
            self.window.dispatch_events()
            if self.window.has_exit:
                break
            now = time.perf_counter()
            real_dt = min(now - prev, 0.25)  # clamp to survive hitches
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
            self._prog, [(self._vbo, "3f 4f 1f", "in_pos", "in_color", "in_u")]
        )

    def _render(self):
        w, h = self.window.get_framebuffer_size()
        if w <= 0 or h <= 0:
            return

        # ---- scene pass: line ribbons into the RGBA16F framebuffer ----
        self._bloom.ensure_size(w, h)
        self._bloom.scene_fbo.use()
        self._bloom.scene_fbo.clear(0.0, 0.0, 0.0, 1.0)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)  # additive glow

        mvp = self.camera.proj(w / h) @ self.camera.view()
        self._prog["u_mvp"].write(np.ascontiguousarray(mvp.T, dtype=np.float32))

        data = build_vertices(self._vobjects, self.camera.eye())
        if data.shape[0] > 0:
            if data.nbytes > self._vbo.size:
                self._vbo.release()
                self._vbo = self.ctx.buffer(
                    reserve=2 * data.nbytes, dynamic=True
                )
                self._vao = self._make_vao()
            self._vbo.write(data.tobytes())
            self._vao.render(mode=moderngl.TRIANGLES, vertices=data.shape[0])

        # ---- bloom: downsample, blur, composite + tone map to screen ----
        self._bloom.apply(self.ctx.screen, w, h)

    def _count_fps(self):
        self._fps_frames += 1
        now = time.perf_counter()
        if now - self._fps_t0 >= 1.0:
            fps = self._fps_frames / (now - self._fps_t0)
            self.window.set_caption(f"{self._caption_base} — {fps:.0f} fps")
            self._fps_frames = 0
            self._fps_t0 = now
```

File 4 — settings.json (updated — two new knobs, version bump)

```json
{
    "title": "Homeworld: A Good Basis",
    "version": "0.2.0",
    "width": 1280,
    "height": 720,
    "fullscreen": false,
    "vsync": true,
    "bloom_strength": 0.85,
    "exposure": 2.5,
    "seed": 1234
}
```

📋 YOUR STEPS

    Send to DeepSeek: the 4 files above, verbatim, with the commit message: NT step 3: bloom (RGBA16F scene FBO, gaussian blur, composite + tone map) — and have it update COMMENTARIES.md.
    Run: double-click run.bat (nothing to reinstall).

👀 WHAT YOU SHOULD SEE

The same scene as before, but alive: every line now wears a soft halo that bleeds into the black around it; the white arrow's core stays hot white while its glow trails off gently; where lines cross, the glow flares; the whole grid looks like it's made of light instead of chalk. The window title should still say ~60 fps.

🎛️ YOUR FIRST FEEL KNOBS (play with them!)

Open settings.json in Notepad and try:

    "bloom_strength": 0.0 → glow off (should look like yesterday's build)
    "bloom_strength": 2.0 → heavy dreamy glow
    "exposure": 1.2 → dimmer, moodier / "exposure": 4.0 → blazing

Set them to whatever the two of you find most beautiful — your taste is now literally a project parameter. Tell me which numbers you settled on and I'll make them the project defaults.

📝 REPORT BACK

Same as before: "I saw exactly that" / "something different: ..." / paste crashlog.txt. One extra thing worth checking: resize the window with the mouse (drag the corner) — the glow should adapt instantly with no crash (that exercises the framebuffer-recreation code).

Next package after your confirmation: text + the remaining primitives (Label, WireMesh, SpannedBox, Ellipsoid, Trail, ImagePanel) — which completes the forge acceptance demo from the New Testament, including the flattening green box whose volume counts down to 0.00. Then helm, then ships. 🚀❤️
