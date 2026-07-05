"""The Forge class: window, GL context, main loop (NEW_TESTAMENT 1.2).

Render pipeline per frame:
    scene pass into RGBA16F FBO (additive):
        line ribbons -> image panels -> labels
    bloom (downsample, blur, composite + tone map) -> screen
    screen overlay (crisp, after bloom): fps corner + F1 debug lines

Additive blending is order-independent: no sorting, ever.
"""

import datetime
import os
import time

import numpy as np
import moderngl
import pyglet
from pyglet.window import key

from camera import Camera
from shaders import LINE_VERT, LINE_FRAG
from batches import build_vertices
from bloom import Bloom
from text import GlyphAtlas, TextRenderer, PanelRenderer, make_quad_program
from vobjects import Label, ImagePanel

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

    # ---- frozen interface (NEW_TESTAMENT 1.2) ----

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
        """Main loop. tick_cb(dt) at exactly 10 Hz; frame_cb(alpha) per frame."""
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
            self._prog, [(self._vbo, "3f 4f 1f", "in_pos", "in_color", "in_u")]
        )

    def _render(self):
        w, h = self.window.get_framebuffer_size()
        if w <= 0 or h <= 0:
            return

        # ---- scene pass into the RGBA16F framebuffer ----
        self._bloom.ensure_size(w, h)
        self._bloom.scene_fbo.use()
        self._bloom.scene_fbo.clear(0.0, 0.0, 0.0, 1.0)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)

        view = self.camera.view()
        mvp = self.camera.proj(w / h) @ view
        mvp_t = np.ascontiguousarray(mvp.T, dtype=np.float32)
        self._prog["u_mvp"].write(mvp_t)

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

        # ---- crisp screen overlay, after bloom ----
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
                f"{self._caption_base} — {self._fps_value:.0f} fps"
            )
            self._fps_frames = 0
            self._fps_t0 = now
