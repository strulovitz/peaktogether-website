"""The Forge class: window, GL context, main loop (NEW_TESTAMENT 1.2).

Owns the pyglet window, the moderngl context, the fixed-timestep
accumulator (10 Hz pulses -> tick_cb; every display frame -> frame_cb
with interpolation alpha), and the render pipeline.

Walking skeleton: single scene pass with additive blending; bloom FBOs
arrive in the next package. Additive blending is order-independent, so
no sorting is ever needed — overlapping glow simply gets brighter.
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

PULSE_DT = 0.1                       # 10 Hz logic pulse (frozen)
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

        self.camera = Camera()
        self._vobjects = []
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
        self.ctx.viewport = (0, 0, w, h)
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.ONE, moderngl.ONE)  # additive glow

        mvp = self.camera.proj(w / h) @ self.camera.view()
        self._prog["u_mvp"].write(np.ascontiguousarray(mvp.T, dtype=np.float32))

        data = build_vertices(self._vobjects, self.camera.eye())
        if data.shape[0] == 0:
            return
        if data.nbytes > self._vbo.size:
            self._vbo.release()
            self._vbo = self.ctx.buffer(reserve=2 * data.nbytes, dynamic=True)
            self._vao = self._make_vao()
        self._vbo.write(data.tobytes())
        self._vao.render(mode=moderngl.TRIANGLES, vertices=data.shape[0])

    def _count_fps(self):
        self._fps_frames += 1
        now = time.perf_counter()
        if now - self._fps_t0 >= 1.0:
            fps = self._fps_frames / (now - self._fps_t0)
            self.window.set_caption(f"{self._caption_base} — {fps:.0f} fps")
            self._fps_frames = 0
            self._fps_t0 = now
