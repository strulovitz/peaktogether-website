"""
overlay2d.py — the crisp 2D screen-space UI layer (INTERFACES v1.1).

The ENTIRE UI vocabulary (per APOCRYPHA Part 3.1, owner-approved):
    Rect2D(x, y, w, h, color, filled=False)
    Line2D(x0, y0, x1, y1, color)
    Label2D(text, x, y, px=16, color=(1,1,1,1))
    Image2D(image, x, y, w, h)     # image: (H,W) float64 grayscale in [0,1]

Coordinates: window pixels, origin BOTTOM-LEFT (matches PointerState and
TextRenderer.draw_screen). Draw order = insertion order (painter's algorithm).
Blending: standard alpha (SRC_ALPHA, ONE_MINUS_SRC_ALPHA) — NOT the HUD's
additive — so opaque console panels are actually opaque.

WIRING (applied in forge.py — the Forge class file):
  1. In Forge.__init__, right after `self._panels = PanelRenderer(...)`:
         from overlay2d import Overlay2D          # (at top of file)
         self.overlay2d = Overlay2D(self.ctx, self._atlas)
  2. In Forge._render, right after `self._bloom.apply(self.ctx.screen, w, h)`
     and BEFORE the crisp HUD text block (so fps/F1 debug stays on top):
         self.overlay2d.draw(w, h)
     (overlay2d sets its own blend state; the HUD block below already re-sets
      its own additive state, so nothing else changes.)
"""

import math

import numpy as np
import moderngl


OVERLAY2D_VERT = """
#version 330
uniform vec2 u_screen;
in vec2 in_pos;
in vec2 in_uv;
in vec4 in_color;
out vec2 v_uv;
out vec4 v_color;
void main() {
    vec2 ndc = (in_pos / u_screen) * 2.0 - 1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_uv = in_uv;
    v_color = in_color;
}
"""

OVERLAY2D_FRAG = """
#version 330
uniform sampler2D u_tex;
uniform int u_mode;   // 0 = flat shape, 1 = text (atlas alpha), 2 = grayscale image
in vec2 v_uv;
in vec4 v_color;
layout(location = 0) out vec4 f_color;
void main() {
    if (u_mode == 0) {
        f_color = v_color;
    } else if (u_mode == 1) {
        float a = texture(u_tex, v_uv).r;
        f_color = vec4(v_color.rgb, v_color.a * a);
    } else {
        float g = texture(u_tex, v_uv).r;
        f_color = vec4(v_color.rgb * g, v_color.a);
    }
}
"""


# ---------------------------------------------------------------- items

class _Item2D:
    """Base for all 2D items: .visible, .color, .set_color(rgba)."""

    def __init__(self, color):
        self.visible = True
        self.color = tuple(color)

    def set_color(self, rgba):
        self.color = tuple(rgba)


class Rect2D(_Item2D):
    """Axis-aligned rectangle. filled=False draws a frame of .thickness px."""

    def __init__(self, x, y, w, h, color, filled=False):
        super().__init__(color)
        self.x = float(x); self.y = float(y)
        self.w = float(w); self.h = float(h)
        self.filled = bool(filled)
        self.thickness = 1.0          # outline thickness in px (frames only)

    def set_rect(self, x, y, w, h):
        self.x = float(x); self.y = float(y)
        self.w = float(w); self.h = float(h)


class Line2D(_Item2D):
    """Straight segment, .thickness px wide (default 1)."""

    def __init__(self, x0, y0, x1, y1, color):
        super().__init__(color)
        self.x0 = float(x0); self.y0 = float(y0)
        self.x1 = float(x1); self.y1 = float(y1)
        self.thickness = 1.0

    def set_points(self, x0, y0, x1, y1):
        self.x0 = float(x0); self.y0 = float(y0)
        self.x1 = float(x1); self.y1 = float(y1)


class Label2D(_Item2D):
    """Screen text; (x, y) is the BOTTOM-LEFT of the text, px is pixel height."""

    def __init__(self, text, x, y, px=16, color=(1.0, 1.0, 1.0, 1.0)):
        super().__init__(color)
        self.text = str(text)
        self.x = float(x); self.y = float(y)
        self.px = float(px)

    def set_text(self, text):
        self.text = str(text)

    def set_pos(self, x, y):
        self.x = float(x); self.y = float(y)


class Image2D(_Item2D):
    """Grayscale image panel: image is (H,W) float64 in [0,1] (Guidestone path).
    .color tints it (default white). Row 0 of the array is the TOP of the panel."""

    def __init__(self, image, x, y, w, h):
        super().__init__((1.0, 1.0, 1.0, 1.0))
        self.x = float(x); self.y = float(y)
        self.w = float(w); self.h = float(h)
        self.image = None
        self._tex = None
        self._dirty = True
        self.set_image(image)

    def set_image(self, image):
        img = np.asarray(image, dtype=np.float64)
        if img.ndim != 2:
            raise ValueError("Image2D expects a 2D (H,W) grayscale array, got shape %r" % (img.shape,))
        self.image = img
        self._dirty = True

    def set_pos(self, x, y):
        self.x = float(x); self.y = float(y)

    def set_rect(self, x, y, w, h):
        self.x = float(x); self.y = float(y)
        self.w = float(w); self.h = float(h)


# ---------------------------------------------------------------- geometry helpers

def _quad(x0, y0, x1, y1, u0, v0, u1, v1, color):
    """Two triangles for an axis-aligned quad; 6 vertices of 8 floats."""
    r, g, b, a = color
    return np.array([
        (x0, y0, u0, v0, r, g, b, a),
        (x1, y0, u1, v0, r, g, b, a),
        (x1, y1, u1, v1, r, g, b, a),
        (x0, y0, u0, v0, r, g, b, a),
        (x1, y1, u1, v1, r, g, b, a),
        (x0, y1, u0, v1, r, g, b, a),
    ], dtype=np.float32)


def _line_quad(x0, y0, x1, y1, thickness, color):
    """A segment as a thin quad perpendicular-offset by half the thickness."""
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return None
    t = max(1.0, float(thickness)) * 0.5
    nx = -dy / length * t
    ny = dx / length * t
    r, g, b, a = color
    return np.array([
        (x0 + nx, y0 + ny, 0.0, 0.0, r, g, b, a),
        (x0 - nx, y0 - ny, 0.0, 0.0, r, g, b, a),
        (x1 - nx, y1 - ny, 0.0, 0.0, r, g, b, a),
        (x0 + nx, y0 + ny, 0.0, 0.0, r, g, b, a),
        (x1 - nx, y1 - ny, 0.0, 0.0, r, g, b, a),
        (x1 + nx, y1 + ny, 0.0, 0.0, r, g, b, a),
    ], dtype=np.float32)


# ---------------------------------------------------------------- renderer

class Overlay2D:
    """Owns the draw list and one dynamic VBO. Draw order = insertion order;
    consecutive items sharing (mode, texture) are merged into one draw call."""

    def __init__(self, ctx, atlas):
        self._ctx = ctx
        self._atlas = atlas
        self._prog = ctx.program(vertex_shader=OVERLAY2D_VERT,
                                 fragment_shader=OVERLAY2D_FRAG)
        self._prog["u_tex"].value = 0
        self._white = ctx.texture((1, 1), 1, b"\xff", dtype="f1")
        self._vbo = ctx.buffer(reserve=1 << 16, dynamic=True)
        self._vao = self._make_vao()
        self._items = []

    # ---- public API -----------------------------------------------------

    def add(self, item):
        if item not in self._items:
            self._items.append(item)

    def remove(self, item):
        if item in self._items:
            self._items.remove(item)

    def clear(self):
        self._items.clear()

    def text_width(self, text, px):
        """On-screen width in pixels of `text` rendered at pixel height `px`."""
        _, _, total = self._atlas.layout(str(text))
        return float(total) * (float(px) / float(self._atlas.line_h))

    def draw(self, w, h):
        """Call once per frame, after the bloom composite (default framebuffer
        bound). Sets its own GL state; safe before the HUD text block."""
        chunks = []
        runs = []          # [mode, texture_or_None, first_vertex, vertex_count]
        last_key = None
        total = 0
        for item in self._items:
            if not item.visible:
                continue
            emitted = self._emit(item)
            if emitted is None:
                continue
            arr, mode, tex = emitted
            n = arr.shape[0]
            if n == 0:
                continue
            key = (mode, id(tex))
            if runs and key == last_key:
                runs[-1][3] += n
            else:
                runs.append([mode, tex, total, n])
                last_key = key
            chunks.append(arr)
            total += n
        if total == 0:
            return

        data = np.concatenate(chunks).tobytes()
        if len(data) > self._vbo.size:
            new_size = 1 << max(16, (len(data) - 1).bit_length() + 1)
            self._vbo.release()
            self._vao.release()
            self._vbo = self._ctx.buffer(reserve=new_size, dynamic=True)
            self._vao = self._make_vao()
        self._vbo.orphan()
        self._vbo.write(data)

        ctx = self._ctx
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        self._prog["u_screen"].value = (float(w), float(h))
        for mode, tex, first, count in runs:
            (tex if tex is not None else self._white).use(location=0)
            self._prog["u_mode"].value = int(mode)
            self._vao.render(moderngl.TRIANGLES, vertices=count, first=first)

    # ---- internals --------------------------------------------------------

    def _make_vao(self):
        return self._ctx.vertex_array(
            self._prog,
            [(self._vbo, "2f 2f 4f", "in_pos", "in_uv", "in_color")])

    def _emit(self, item):
        if isinstance(item, Label2D):
            arr = self._emit_label(item)
            return None if arr is None else (arr, 1, self._atlas.texture)
        if isinstance(item, Image2D):
            tex = self._image_texture(item)
            arr = _quad(item.x, item.y, item.x + item.w, item.y + item.h,
                        0.0, 1.0, 1.0, 0.0, item.color)
            return (arr, 2, tex)
        if isinstance(item, Rect2D):
            return (self._emit_rect(item), 0, None)
        if isinstance(item, Line2D):
            arr = _line_quad(item.x0, item.y0, item.x1, item.y1,
                             item.thickness, item.color)
            return None if arr is None else (arr, 0, None)
        return None

    def _emit_rect(self, item):
        x, y, w, h = item.x, item.y, item.w, item.h
        c = item.color
        if item.filled:
            return _quad(x, y, x + w, y + h, 0.0, 0.0, 0.0, 0.0, c)
        t = max(1.0, item.thickness)
        return np.concatenate([
            _quad(x, y, x + w, y + t, 0.0, 0.0, 0.0, 0.0, c),               # bottom
            _quad(x, y + h - t, x + w, y + h, 0.0, 0.0, 0.0, 0.0, c),       # top
            _quad(x, y + t, x + t, y + h - t, 0.0, 0.0, 0.0, 0.0, c),       # left
            _quad(x + w - t, y + t, x + w, y + h - t, 0.0, 0.0, 0.0, 0.0, c)  # right
        ])

    def _emit_label(self, item):
        if not item.text:
            return None
        corners, uvs, _total = self._atlas.layout(item.text)
        corners = np.asarray(corners, dtype=np.float64)
        uvs = np.asarray(uvs, dtype=np.float64)
        if corners.size == 0:
            return None
        n = corners.shape[0]
        scale = float(item.px) / float(self._atlas.line_h)
        xs = corners[:, :, 0] * scale + item.x
        ys = corners[:, :, 1] * scale + item.y
        us = uvs[:, :, 0]
        vs = uvs[:, :, 1]
        # Reconstruct each axis-aligned glyph quad from min/max so we never
        # depend on the atlas's corner ordering (uv follows the same corner).
        idx = np.arange(n)
        ix0 = xs.argmin(axis=1); ix1 = xs.argmax(axis=1)
        iy0 = ys.argmin(axis=1); iy1 = ys.argmax(axis=1)
        x0 = xs[idx, ix0]; x1 = xs[idx, ix1]
        y0 = ys[idx, iy0]; y1 = ys[idx, iy1]
        u0 = us[idx, ix0]; u1 = us[idx, ix1]
        v0 = vs[idx, iy0]; v1 = vs[idx, iy1]
        r, g, b, a = item.color
        out = np.empty((n, 6, 8), dtype=np.float32)
        out[:, :, 4] = r; out[:, :, 5] = g; out[:, :, 6] = b; out[:, :, 7] = a
        out[:, 0, 0] = x0; out[:, 0, 1] = y0; out[:, 0, 2] = u0; out[:, 0, 3] = v0
        out[:, 1, 0] = x1; out[:, 1, 1] = y0; out[:, 1, 2] = u1; out[:, 1, 3] = v0
        out[:, 2, 0] = x1; out[:, 2, 1] = y1; out[:, 2, 2] = u1; out[:, 2, 3] = v1
        out[:, 3] = out[:, 0]
        out[:, 4] = out[:, 2]
        out[:, 5, 0] = x0; out[:, 5, 1] = y1; out[:, 5, 2] = u0; out[:, 5, 3] = v1
        return out.reshape(-1, 8)

    def _image_texture(self, item):
        if item._tex is not None and not item._dirty:
            return item._tex
        img = np.clip(item.image, 0.0, 1.0)
        data = (img * 255.0 + 0.5).astype(np.uint8)
        h_px, w_px = data.shape
        if item._tex is not None and item._tex.size == (w_px, h_px):
            item._tex.write(data.tobytes())
        else:
            if item._tex is not None:
                item._tex.release()
            tex = self._ctx.texture((w_px, h_px), 1, data.tobytes(), dtype="f1")
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            item._tex = tex
        item._dirty = False
        return item._tex
