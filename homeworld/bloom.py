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

from shaders import FULLSCREEN_VERT, BLIT_FRAG, BLUR_FRAG, COMPOSITE_FRAG


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
