"""Scene framebuffer + bloom (Amendment A1.1).

Scene FBO: two RGBA16F color attachments (solid ships / holograms)
sharing one depth buffer. Bloom downsamples and blurs ONLY the glow
attachment; the composite adds tone-mapped glow over the untouched
solid buffer. Ships can never bloom, by construction.
"""

import moderngl

from shaders import FULLSCREEN_VERT, BLIT_FRAG, BLUR_FRAG, COMPOSITE_FRAG


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
