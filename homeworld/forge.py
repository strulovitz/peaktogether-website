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

from camera import Camera
from shaders import LINE_VERT, LINE_FRAG
from batches import build_vertices
from bloom import Bloom
from solid import SolidMesh, SolidRenderer
from text import GlyphAtlas, TextRenderer, PanelRenderer, make_quad_program
from vobjects import Label, ImagePanel
from overlay2d import Overlay2D

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
        self.overlay2d = Overlay2D(self.ctx, self._atlas)

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

        # ---- 2D UI overlay (INTERFACES v1.1) — before HUD so fps/F1 stay on top ----
        self.overlay2d.draw(w, h)

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
