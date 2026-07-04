"""Text and textured quads (NEW_TESTAMENT 1.7).

GlyphAtlas: at startup, Pillow renders a monospace font into a single
single-channel texture covering ASCII 32..126 plus the frozen extra
glyph list. Font search order: content/fonts/mono.ttf (the bundled
font, when it exists), then Windows' Consolas / Courier New, then
PIL's built-in bitmap font as a last resort — so the game runs even
before content/ exists.

TextRenderer: draws billboarded 3D Labels (batched into one draw
call) and screen-space overlay text (fps corner, F1 debug lines).

PanelRenderer: draws billboarded grayscale ImagePanels, one small
draw call each, with texture caching + re-upload on set_image().
"""

import os

import numpy as np
import moderngl
from PIL import Image, ImageDraw, ImageFont

from .shaders import TEXT_VERT, TEXT_FRAG

EXTRA_GLYPHS = "×·⟂ΣΛσλθρε≈≤≥−→‖"
_FALLBACK_CHAR = "?"
_TRI = (0, 1, 2, 0, 2, 3)


def make_quad_program(ctx):
    return ctx.program(vertex_shader=TEXT_VERT, fragment_shader=TEXT_FRAG)


def _load_font(px):
    candidates = [
        os.path.join("content", "fonts", "mono.ttf"),
        "consola.ttf",          # Windows Consolas
        "cour.ttf",             # Windows Courier New
        "DejaVuSansMono.ttf",
    ]
    for cand in candidates:
        try:
            return ImageFont.truetype(cand, px)
        except Exception:
            continue
    return ImageFont.load_default()


class GlyphAtlas:
    def __init__(self, ctx, px=48):
        font = _load_font(px)
        chars = [chr(i) for i in range(32, 127)] + list(EXTRA_GLYPHS)
        try:
            ascent, descent = font.getmetrics()
        except Exception:
            ascent, descent = px, max(1, px // 4)
        self.line_h = ascent + descent

        probe = ImageDraw.Draw(Image.new("L", (8, 8)))
        adv = {}
        for ch in chars:
            try:
                adv[ch] = max(1.0, float(probe.textlength(ch, font=font)))
            except Exception:
                adv[ch] = px * 0.6
        cell_w = int(max(adv.values())) + 3
        cell_h = self.line_h + 2
        cols = 16
        rows = (len(chars) + cols - 1) // cols
        atlas_w, atlas_h = cols * cell_w, rows * cell_h

        img = Image.new("L", (atlas_w, atlas_h), 0)
        draw = ImageDraw.Draw(img)
        self.metrics = {}
        for i, ch in enumerate(chars):
            cx = (i % cols) * cell_w
            cy = (i // cols) * cell_h
            try:
                draw.text((cx + 1, cy + 1), ch, font=font, fill=255)
            except Exception:
                continue
            self.metrics[ch] = (
                cx / atlas_w,               # u0
                cy / atlas_h,               # v_top
                (cx + cell_w) / atlas_w,    # u1
                (cy + cell_h) / atlas_h,    # v_bottom
                adv[ch],                    # advance in atlas pixels
            )
        self.cell_w = float(cell_w)
        self.texture = ctx.texture((atlas_w, atlas_h), 1,
                                   img.tobytes(), dtype="f1")
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

    def layout(self, text):
        """Local text-space quads, y up (bottom=0, top=line_h), pixel
        units. Returns (corners (N,4,2), uvs (N,4,2), total_width)."""
        fallback = self.metrics.get(_FALLBACK_CHAR)
        corners, uvs = [], []
        pen = 0.0
        for ch in text:
            m = self.metrics.get(ch, fallback)
            if m is None:
                continue
            u0, vt, u1, vb, advance = m
            x0, x1 = pen, pen + self.cell_w
            y0, y1 = 0.0, float(self.line_h)
            corners.append([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
            uvs.append([[u0, vb], [u1, vb], [u1, vt], [u0, vt]])
            pen += advance
        if not corners:
            return (np.zeros((0, 4, 2)), np.zeros((0, 4, 2)), 0.0)
        return (np.array(corners), np.array(uvs), pen)


class TextRenderer:
    def __init__(self, ctx, atlas, program):
        self.ctx = ctx
        self.atlas = atlas
        self.prog = program
        self._vbo = ctx.buffer(reserve=1024 * 1024, dynamic=True)
        self._vao = self._make_vao()

    def _make_vao(self):
        return self.ctx.vertex_array(
            self.prog,
            [(self._vbo, "3f 2f 4f", "in_pos", "in_uv", "in_color")],
        )

    def draw_labels(self, labels, view, mvp_t_f32):
        """All 3D Labels in one draw call, billboarded via the camera's
        right (view row 0) and up (view row 1) axes."""
        right = view[0, :3]
        up = view[1, :3]
        verts = []
        for lab in labels:
            corners, uvs, total_w = self.atlas.layout(lab.text)
            if corners.shape[0] == 0:
                continue
            s = lab.size / self.atlas.line_h
            ox = -0.5 * total_w
            oy = -0.5 * self.atlas.line_h
            col = (lab.color[0] * lab.glow, lab.color[1] * lab.glow,
                   lab.color[2] * lab.glow, lab.color[3])
            for q in range(corners.shape[0]):
                world4 = [
                    lab.pos
                    + right * ((corners[q, i, 0] + ox) * s)
                    + up * ((corners[q, i, 1] + oy) * s)
                    for i in range(4)
                ]
                for i in _TRI:
                    verts.append([world4[i][0], world4[i][1], world4[i][2],
                                  uvs[q, i, 0], uvs[q, i, 1], *col])
        self._flush(verts, mvp_t_f32)

    def draw_screen(self, items, w, h):
        """Screen-space text. items: list of (text, x, y, px, color)
        with (x, y) the bottom-left corner in window pixels."""
        verts = []
        for text, x, y, px, color in items:
            corners, uvs, _ = self.atlas.layout(text)
            if corners.shape[0] == 0:
                continue
            s = px / self.atlas.line_h
            for q in range(corners.shape[0]):
                for i in _TRI:
                    verts.append([x + corners[q, i, 0] * s,
                                  y + corners[q, i, 1] * s, 0.0,
                                  uvs[q, i, 0], uvs[q, i, 1], *color])
        ortho = np.array([
            [2.0 / w, 0.0, 0.0, -1.0],
            [0.0, 2.0 / h, 0.0, -1.0],
            [0.0, 0.0, -0.001, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ])
        self._flush(verts, np.ascontiguousarray(ortho.T, dtype=np.float32))

    def _flush(self, verts, mvp_t_f32):
        if not verts:
            return
        data = np.asarray(verts, dtype=np.float32)
        if data.nbytes > self._vbo.size:
            self._vbo.release()
            self._vbo = self.ctx.buffer(reserve=2 * data.nbytes, dynamic=True)
            self._vao = self._make_vao()
        self._vbo.write(data.tobytes())
        self.prog["u_mvp"].write(mvp_t_f32)
        self.atlas.texture.use(0)
        self.prog["u_tex"].value = 0
        self._vao.render(moderngl.TRIANGLES, vertices=data.shape[0])


class PanelRenderer:
    def __init__(self, ctx, program):
        self.ctx = ctx
        self.prog = program
        self._vbo = ctx.buffer(reserve=6 * 9 * 4, dynamic=True)
        self._vao = ctx.vertex_array(
            program, [(self._vbo, "3f 2f 4f", "in_pos", "in_uv", "in_color")]
        )
        self._textures = {}   # id(panel) -> (texture, image shape)

    def draw(self, panels, view, mvp_t_f32):
        right = view[0, :3]
        up = view[1, :3]
        self.prog["u_mvp"].write(mvp_t_f32)
        self.prog["u_tex"].value = 0
        live = set()
        for p in panels:
            key = id(p)
            live.add(key)
            entry = self._textures.get(key)
            shape = p.image.shape
            if entry is None or entry[1] != shape or p._dirty:
                data = (p.image * 255.0).astype(np.uint8).tobytes()
                if entry is not None and entry[1] == shape:
                    entry[0].write(data)
                    tex = entry[0]
                else:
                    if entry is not None:
                        entry[0].release()
                    tex = self.ctx.texture((shape[1], shape[0]), 1,
                                           data, dtype="f1")
                    tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
                self._textures[key] = (tex, shape)
                p._dirty = False
            tex = self._textures[key][0]

            hw, hh = 0.5 * p.w, 0.5 * p.h
            bl = p.pos - right * hw - up * hh
            br = p.pos + right * hw - up * hh
            tr = p.pos + right * hw + up * hh
            tl = p.pos - right * hw + up * hh
            world4 = [bl, br, tr, tl]
            uv4 = [(0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
            col = (p.color[0] * p.glow, p.color[1] * p.glow,
                   p.color[2] * p.glow, p.color[3])
            verts = []
            for i in _TRI:
                verts.append([world4[i][0], world4[i][1], world4[i][2],
                              uv4[i][0], uv4[i][1], *col])
            self._vbo.write(np.asarray(verts, dtype=np.float32).tobytes())
            tex.use(0)
            self._vao.render(moderngl.TRIANGLES, vertices=6)
        for key in list(self._textures):
            if key not in live:
                self._textures[key][0].release()
                del self._textures[key]
