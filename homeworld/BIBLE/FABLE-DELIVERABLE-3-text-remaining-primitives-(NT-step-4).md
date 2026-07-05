Excellent taste — the defaults stay as they are (they're already the shipped values, so nothing to change). 🎉

Now the next package: TEXT + THE REMAINING PRIMITIVES (New Testament build step 4). This completes the entire forge primitive vocabulary — Label, WireMesh, SpannedBox, Ellipsoid, Trail, ImagePanel — plus the glyph atlas, the F1 debug overlay, and the fps corner counter. After this package, forge is feature-complete and we move on to helm and then ships.

Below are 8 complete files. Send each to DeepSeek exactly as-is.

File 1 — forge/shaders.py (updated — replaces the whole file)

```python
"""GLSL shader sources (NEW_TESTAMENT 1.5, 1.6, 1.7).

Three families:

1. Line ribbon shader: lines expanded on the CPU into camera-facing
   ribbons; fragment intensity = (1 - u^2)^2 gives a hot core and
   soft edges before bloom even runs.

2. Bloom pipeline: fullscreen triangle from gl_VertexID, blit,
   separable 9-tap Gaussian blur, composite with soft exposure
   tone map c -> 1 - exp(-c * exposure).

3. Textured quad shader: used for BOTH text (glyph atlas) and
   ImagePanels (grayscale textures). Single-channel texture; the
   fragment multiplies the vertex color by the texel value, so text
   and images glow like everything else in the world.
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
```

File 2 — forge/vobjects.py (updated — replaces the whole file; now the complete frozen vocabulary)

```python
"""VObjects: the complete primitive vocabulary (NEW_TESTAMENT 1.4).

Line, Arrow, DashedLine, Grid, WireSphere, WireMesh, SpannedBox,
Ellipsoid, Trail  -> segment-based (rendered as glowing ribbons).
Label, ImagePanel -> billboarded textured quads (rendered by text.py).

Every segment-based primitive reduces itself to an array of segments
of shape (N, 2, 3). set_data() always copies its numpy inputs.
segment_colors() may return per-segment RGBA (N, 4) to override the
object color (used by Trail for its fade); None means uniform color.
"""

import numpy as np


class VObject:
    def __init__(self, color=(0.5, 0.9, 1.0, 1.0), glow=1.0, width=0.06):
        self.visible = True
        self.color = tuple(color)
        self.glow = float(glow)
        self.width = float(width)   # ribbon HALF-width in world units
        self._segments = np.zeros((0, 2, 3), dtype=np.float64)

    def set_color(self, rgba):
        self.color = tuple(rgba)

    def segments(self):
        return self._segments

    def segment_colors(self):
        return None


class Line(VObject):
    """Polyline through N points. points: (N, 3)."""

    def __init__(self, points, **kw):
        super().__init__(**kw)
        self.set_data(points)

    def set_data(self, points):
        p = np.asarray(points, dtype=np.float64).reshape(-1, 3).copy()
        if p.shape[0] < 2:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        self._segments = np.stack([p[:-1], p[1:]], axis=1)


class Arrow(VObject):
    """THE vector: a shaft plus a 4-line pyramid head with a base ring."""

    def __init__(self, start, end, head_size=0.5, **kw):
        kw.setdefault("width", 0.09)
        super().__init__(**kw)
        self.set_data(start, end, head_size)

    def set_data(self, start, end, head_size=0.5):
        start = np.asarray(start, dtype=np.float64).copy()
        end = np.asarray(end, dtype=np.float64).copy()
        axis = end - start
        length = np.linalg.norm(axis)
        if length < 1e-9:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        d = axis / length
        head = min(head_size, 0.5 * length)
        ref = np.array([0.0, 1.0, 0.0])
        if abs(d @ ref) > 0.9:
            ref = np.array([1.0, 0.0, 0.0])
        u = ref - (ref @ d) * d
        u = u / np.linalg.norm(u)
        w = np.cross(d, u)
        base = end - d * head
        r = head * 0.4
        ring = [base + u * r, base + w * r, base - u * r, base - w * r]
        segs = [(start, end)]
        for i in range(4):
            segs.append((end, ring[i]))
            segs.append((ring[i], ring[(i + 1) % 4]))
        self._segments = np.array(segs, dtype=np.float64)


class DashedLine(VObject):
    """Straight line from start to end with equal dash/gap lengths."""

    def __init__(self, start, end, dash=0.5, **kw):
        super().__init__(**kw)
        self.set_data(start, end, dash)

    def set_data(self, start, end, dash=0.5):
        start = np.asarray(start, dtype=np.float64).copy()
        end = np.asarray(end, dtype=np.float64).copy()
        axis = end - start
        length = np.linalg.norm(axis)
        if length < 1e-9 or dash <= 0.0:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        n = max(1, int(np.ceil(length / (2.0 * dash))))
        k = np.arange(n, dtype=np.float64)
        t0 = np.minimum((2.0 * k) * dash / length, 1.0)
        t1 = np.minimum((2.0 * k + 1.0) * dash / length, 1.0)
        p0 = start[None, :] + t0[:, None] * axis[None, :]
        p1 = start[None, :] + t1[:, None] * axis[None, :]
        self._segments = np.stack([p0, p1], axis=1)


class Grid(VObject):
    """Plane grid spanned by vectors u and v — how 'span' is drawn."""

    def __init__(self, center, u, v, n=10, spacing=1.0, **kw):
        kw.setdefault("color", (0.10, 0.55, 0.65, 1.0))
        kw.setdefault("width", 0.035)
        super().__init__(**kw)
        self.set_data(center, u, v, n, spacing)

    def set_data(self, center, u, v, n=10, spacing=1.0):
        c = np.asarray(center, dtype=np.float64).copy()
        u = np.asarray(u, dtype=np.float64).copy()
        v = np.asarray(v, dtype=np.float64).copy()
        idx = np.arange(-n, n + 1, dtype=np.float64) * spacing
        ext = n * spacing
        segs = []
        for i in idx:
            segs.append((c + i * v - ext * u, c + i * v + ext * u))
        for i in idx:
            segs.append((c + i * u - ext * v, c + i * u + ext * v))
        self._segments = np.array(segs, dtype=np.float64)


class WireSphere(VObject):
    """Three orthogonal great circles."""

    def __init__(self, center, radius, seg=24, **kw):
        super().__init__(**kw)
        self.set_data(center, radius, seg)

    def set_data(self, center, radius, seg=24):
        c = np.asarray(center, dtype=np.float64).copy()
        self._segments = _sphere_segments(c, float(radius), int(seg), None)


def _sphere_segments(center, radius, seg, transform):
    """Shared by WireSphere and Ellipsoid: three great circles, with an
    optional 3x3 transform applied to the unit-sphere points (this IS
    the Ellipsoid: the unit sphere pushed through a matrix)."""
    t = np.linspace(0.0, 2.0 * np.pi, seg + 1)
    cos_t, sin_t = np.cos(t), np.sin(t)
    zeros = np.zeros_like(t)
    circles = [
        np.stack([cos_t, sin_t, zeros], axis=1),
        np.stack([zeros, cos_t, sin_t], axis=1),
        np.stack([cos_t, zeros, sin_t], axis=1),
    ]
    segs = []
    for pts in circles:
        if transform is not None:
            pts = pts @ transform.T
        p = center[None, :] + radius * pts
        segs.append(np.stack([p[:-1], p[1:]], axis=1))
    return np.concatenate(segs, axis=0)


class WireMesh(VObject):
    """Arbitrary wireframe: vertices (N, 3) + edges (M, 2) int pairs.
    Ships are WireMeshes loaded from content/meshes/."""

    def __init__(self, vertices, edges, **kw):
        super().__init__(**kw)
        self.set_data(vertices, edges)

    def set_data(self, vertices, edges):
        v = np.asarray(vertices, dtype=np.float64).reshape(-1, 3).copy()
        e = np.asarray(edges, dtype=np.int64).reshape(-1, 2).copy()
        if v.shape[0] == 0 or e.shape[0] == 0:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        self._segments = v[e]      # (M, 2, 3)


class SpannedBox(VObject):
    """Parallelogram of two vectors, or parallelepiped of three, from an
    origin corner. Serves Chapter 1 (span/independence) AND Chapter 5
    (the determinant as volume): when the vectors become dependent, the
    box visibly flattens to zero volume."""

    def __init__(self, origin, v1, v2, v3=None, **kw):
        kw.setdefault("color", (0.4, 1.0, 0.5, 0.9))
        super().__init__(**kw)
        self.set_data(origin, v1, v2, v3)

    def set_data(self, origin, v1, v2, v3=None):
        o = np.asarray(origin, dtype=np.float64).copy()
        a = np.asarray(v1, dtype=np.float64).copy()
        b = np.asarray(v2, dtype=np.float64).copy()
        if v3 is None:
            corners = [o, o + a, o + a + b, o + b]
            segs = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
            self._segments = np.array(segs, dtype=np.float64)
            return
        c = np.asarray(v3, dtype=np.float64).copy()
        segs = []
        for base in (o, o + c):                     # bottom & top faces
            quad = [base, base + a, base + a + b, base + b]
            for i in range(4):
                segs.append((quad[i], quad[(i + 1) % 4]))
        for corner in (o, o + a, o + a + b, o + b):  # vertical edges
            segs.append((corner, corner + c))
        self._segments = np.array(segs, dtype=np.float64)


class Ellipsoid(VObject):
    """The unit wire-sphere transformed by a 3x3 matrix M — the visual
    identity of quadratic-form shields (Bible 2.12) and warp fields
    (Bible 2.15): p -> center + M @ p."""

    def __init__(self, center, M, seg=24, **kw):
        super().__init__(**kw)
        self.set_data(center, M, seg)

    def set_data(self, center, M, seg=24):
        c = np.asarray(center, dtype=np.float64).copy()
        m = np.asarray(M, dtype=np.float64).reshape(3, 3).copy()
        self._segments = _sphere_segments(c, 1.0, int(seg), m)


class Trail(VObject):
    """Ring buffer of points; push(point) once per pulse. Alpha fades
    linearly from head (newest, bright) to tail (oldest, dim)."""

    def __init__(self, max_points=64, **kw):
        kw.setdefault("width", 0.05)
        super().__init__(**kw)
        self.max_points = int(max_points)
        self._pts = []

    def push(self, point):
        self._pts.append(np.asarray(point, dtype=np.float64).copy())
        if len(self._pts) > self.max_points:
            self._pts.pop(0)
        self._rebuild()

    def clear(self):
        self._pts = []
        self._rebuild()

    def _rebuild(self):
        if len(self._pts) < 2:
            self._segments = np.zeros((0, 2, 3), dtype=np.float64)
            return
        p = np.array(self._pts)
        self._segments = np.stack([p[:-1], p[1:]], axis=1)

    def segment_colors(self):
        n = self._segments.shape[0]
        if n == 0:
            return None
        c = np.empty((n, 4), dtype=np.float64)
        c[:, 0], c[:, 1], c[:, 2] = self.color[0], self.color[1], self.color[2]
        c[:, 3] = self.color[3] * (np.arange(1, n + 1) / n)   # tail -> head
        return c


class Label(VObject):
    """Billboarded text. size = world-space height of the text line.
    Rendered by text.TextRenderer, not by the line batcher."""

    def __init__(self, text, pos, size=1.0, **kw):
        kw.setdefault("color", (1.0, 1.0, 1.0, 1.0))
        super().__init__(**kw)
        self.text = str(text)
        self.pos = np.asarray(pos, dtype=np.float64).copy()
        self.size = float(size)

    def set_text(self, text):
        self.text = str(text)

    def set_data(self, pos=None, size=None):
        if pos is not None:
            self.pos = np.asarray(pos, dtype=np.float64).copy()
        if size is not None:
            self.size = float(size)


class ImagePanel(VObject):
    """Billboarded grayscale image (the Guidestone code path).
    image: (H, W) floats in [0, 1]. set_image() re-uploads the texture."""

    def __init__(self, image, pos, w, h, **kw):
        kw.setdefault("color", (1.0, 1.0, 1.0, 1.0))
        super().__init__(**kw)
        self.pos = np.asarray(pos, dtype=np.float64).copy()
        self.w = float(w)
        self.h = float(h)
        self.image = None
        self._dirty = True
        self.set_image(image)

    def set_image(self, image):
        img = np.clip(np.asarray(image, dtype=np.float64), 0.0, 1.0).copy()
        if img.ndim != 2:
            raise ValueError("ImagePanel expects a 2D grayscale array")
        self.image = img
        self._dirty = True
```

File 3 — forge/batches.py (updated — replaces the whole file; adds per-segment color support for Trail)

```python
"""CPU geometry expansion (NEW_TESTAMENT 1.5).

Every line segment becomes a camera-facing ribbon (two triangles).
For a segment p0 -> p1 with half-width w and camera eye e:
    side = normalize( (p1 - p0) x (e - p0) )
Each vertex carries a ribbon coordinate u in [-1, +1] across the
width; the fragment shader turns that into a hot core + soft edge.

Everything is vectorized numpy over ALL segments at once. The
walking-skeleton policy of rebuilding all geometry every frame stands
(a few thousand segments is trivial at 60 fps).

Output vertex format (float32): x, y, z, r, g, b, a, u  -> '3f 4f 1f'.
"""

import numpy as np

_U_PATTERN = np.array([-1.0, 1.0, 1.0, -1.0, 1.0, -1.0], dtype=np.float64)


def build_vertices(vobjects, eye):
    """Collect all visible segment-based vobjects, expand to (M, 8) f32.
    Objects whose segments() are empty (e.g. Label, ImagePanel) are
    skipped automatically."""
    seg_list, col_list, wid_list = [], [], []
    for vob in vobjects:
        if not vob.visible:
            continue
        s = vob.segments()
        n = s.shape[0]
        if n == 0:
            continue
        seg_list.append(s)
        sc = vob.segment_colors()
        c = np.empty((n, 4), dtype=np.float64)
        if sc is None:
            c[:, 0] = vob.color[0] * vob.glow
            c[:, 1] = vob.color[1] * vob.glow
            c[:, 2] = vob.color[2] * vob.glow
            c[:, 3] = vob.color[3]
        else:
            c[:, :3] = sc[:, :3] * vob.glow
            c[:, 3] = sc[:, 3]
        col_list.append(c)
        wid_list.append(np.full(n, vob.width, dtype=np.float64))
    if not seg_list:
        return np.zeros((0, 8), dtype=np.float32)
    segs = np.concatenate(seg_list, axis=0)
    cols = np.concatenate(col_list, axis=0)
    wids = np.concatenate(wid_list, axis=0)
    return _expand(segs, cols, wids, np.asarray(eye, dtype=np.float64))


def _expand(segs, cols, wids, eye):
    p0 = segs[:, 0, :]
    p1 = segs[:, 1, :]
    d = p1 - p0
    side = np.cross(d, eye[None, :] - p0)
    norms = np.linalg.norm(side, axis=1)
    bad = norms < 1e-9
    if np.any(bad):
        for i in np.where(bad)[0]:
            alt = np.cross(d[i], np.array([0.0, 1.0, 0.0]))
            if np.linalg.norm(alt) < 1e-9:
                alt = np.cross(d[i], np.array([1.0, 0.0, 0.0]))
            if np.linalg.norm(alt) < 1e-9:
                alt = np.array([1.0, 0.0, 0.0])
            side[i] = alt
            norms[i] = np.linalg.norm(alt)
    side = side / norms[:, None]
    off = side * wids[:, None]

    a = p0 - off
    b = p0 + off
    c = p1 + off
    e2 = p1 - off

    n = segs.shape[0]
    pos = np.empty((n, 6, 3), dtype=np.float64)
    pos[:, 0] = a
    pos[:, 1] = b
    pos[:, 2] = c
    pos[:, 3] = a
    pos[:, 4] = c
    pos[:, 5] = e2

    col = np.repeat(cols[:, None, :], 6, axis=1)
    u = np.broadcast_to(_U_PATTERN, (n, 6))[..., None]

    out = np.concatenate([pos, col, u], axis=2).astype(np.float32)
    return out.reshape(-1, 8)
```

File 4 — forge/text.py (new file)

```python
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
```

File 5 — forge/app.py (updated — replaces the whole file)

```python
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

from .camera import Camera
from .shaders import LINE_VERT, LINE_FRAG
from .batches import build_vertices
from .bloom import Bloom
from .text import GlyphAtlas, TextRenderer, PanelRenderer, make_quad_program
from .vobjects import Label, ImagePanel

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
```

File 6 — forge/__init__.py (updated — replaces the whole file)

```python
"""forge — the render engine of Homeworld: A Good Basis.

A real-time Manim: glowing vector graphics in modern OpenGL.
See NEW_TESTAMENT.md Part 1 for the full design. Feature-complete:
window + camera + bloom + the full frozen primitive vocabulary
(NT 1.4) + glyph-atlas text + screen overlay.
"""

from .app import Forge, PULSE_DT
from .camera import Camera
from .vobjects import (
    VObject, Line, Arrow, DashedLine, Grid, WireSphere,
    WireMesh, SpannedBox, Ellipsoid, Trail, Label, ImagePanel,
)

__all__ = [
    "Forge", "PULSE_DT", "Camera",
    "VObject", "Line", "Arrow", "DashedLine", "Grid", "WireSphere",
    "WireMesh", "SpannedBox", "Ellipsoid", "Trail", "Label", "ImagePanel",
]
```

File 7 — forge/demo.py (updated — replaces the whole file; now the full acceptance demo)

```python
"""python -m forge.demo — the FULL forge acceptance demo (NT Part 6).

EXPECTED (plain words, for the project owner):
Everything from the previous build (glowing cyan grid, red/green/blue
origin axes, white arrow sweeping like a tilted clock hand, red dashed
line, green wire sphere, self-orbiting camera), PLUS:
- a white fading TRAIL behind the sweeping arrow's tip;
- floating text "The origin (0,0,0)" near the center, always facing you;
- a GREEN WIRE BOX that slowly flattens and un-flattens, with a live
  volume label counting down to "vol 0.00" exactly when the box is
  completely flat, then back up to ~27;
- a grayscale IMAGE PANEL that sharpens in visible steps (label counts
  "rank 1/32" ... "rank 32/32"), then loops back to blurry;
- a squashed magenta wire sphere (an Ellipsoid);
- an fps counter in the bottom-left corner (~60 fps);
- F1 toggles white debug text in the top-left corner;
- F12 still saves a screenshot; ESC still quits; resizing is safe.
"""

import json
import math
import os
import sys
import time
import traceback

import numpy as np

from .app import Forge
from .vobjects import (
    Arrow, DashedLine, Grid, WireSphere, SpannedBox, Ellipsoid,
    Trail, Label, ImagePanel,
)


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _test_image():
    """A recognizable 128x128 test picture: gradient + bright ring +
    diagonal bar. Rich enough that low SVD ranks look clearly blurry."""
    y, x = np.mgrid[0:128, 0:128] / 127.0
    img = 0.20 * x + 0.10 * y
    r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
    img = img + np.exp(-((r - 0.30) / 0.05) ** 2)
    img = img + 0.6 * (np.abs(x - y) < 0.05)
    return np.clip(img, 0.0, 1.0)


def _arrow_end(t):
    return np.array([
        8.0 * math.cos(0.40 * t),
        4.0 + 1.5 * math.sin(0.70 * t),
        8.0 * math.sin(0.40 * t),
    ])


def main():
    settings = _load_settings()
    forge = Forge(settings)
    print("forge demo running. ESC = quit, F12 = screenshot, F1 = debug text.")

    forge.add(Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1),
                   n=10, spacing=2.0))
    forge.add(Arrow((0, 0, 0), (3, 0, 0), head_size=0.6,
                    color=(1.0, 0.25, 0.25, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 3, 0), head_size=0.6,
                    color=(0.25, 1.0, 0.35, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 0, 3), head_size=0.6,
                    color=(0.35, 0.55, 1.0, 1.0)))

    first_vector = Arrow((0, 0, 0), (8, 4, 0), head_size=1.1,
                         color=(1.0, 1.0, 1.0, 1.0), glow=1.2)
    forge.add(first_vector)
    trail = Trail(max_points=80, color=(1.0, 1.0, 1.0, 0.7), width=0.05)
    forge.add(trail)

    forge.add(DashedLine((-9, 0.5, -9), (9, 3.5, 9), dash=0.7,
                         color=(1.0, 0.35, 0.30, 1.0)))
    forge.add(WireSphere((-7, 2.0, 5), 2.0, color=(0.35, 1.0, 0.55, 0.8)))
    forge.add(Ellipsoid((11, 3.0, 8),
                        [[2.0, 0.0, 0.0], [0.0, 0.8, 0.0], [0.0, 0.0, 1.2]],
                        color=(1.0, 0.4, 0.9, 0.8)))

    forge.add(Label("The origin (0,0,0)", (0, -1.6, 0), size=1.0,
                    color=(0.9, 0.95, 1.0, 0.9)))

    # The determinant-as-volume box (Bible 2.10 code path).
    box_origin = np.array([9.0, 0.0, -8.0])
    box = SpannedBox(box_origin, (3, 0, 0), (1, 0, 3), (1, 3, 1))
    forge.add(box)
    vol_label = Label("vol 0.00", box_origin + np.array([2.0, 4.8, 1.0]),
                      size=1.1, color=(0.6, 1.0, 0.7, 1.0))
    forge.add(vol_label)

    # The Guidestone code path: live SVD partial sums of a test image.
    G = _test_image()
    U, s, Vt = np.linalg.svd(G)
    ranks = [1, 2, 4, 8, 16, 32]

    def rank_image(k):
        return np.clip((U[:, :k] * s[:k]) @ Vt[:k], 0.0, 1.0)

    panel = ImagePanel(rank_image(1), pos=(-11.0, 6.0, -9.0), w=6.0, h=6.0)
    forge.add(panel)
    rank_label = Label("rank 1/32", (-11.0, 2.2, -9.0), size=0.9,
                       color=(0.8, 0.9, 1.0, 0.9))
    forge.add(rank_label)

    start = time.perf_counter()
    state = {"pulses": 0, "rank_idx": 0}

    def tick(dt):
        state["pulses"] += 1
        t = time.perf_counter() - start
        trail.push(_arrow_end(t))

    def frame(alpha):
        t = time.perf_counter() - start
        forge.camera.yaw = 0.8 + 0.12 * t
        forge.camera.pitch = 0.35 + 0.10 * math.sin(0.30 * t)

        first_vector.set_data((0.0, 0.0, 0.0), _arrow_end(t), head_size=1.1)

        # Box flattening: third vector's height sweeps 3 -> 0 -> 3;
        # |det| of the three column vectors is recomputed live by numpy.
        height = 3.0 * abs(math.sin(0.35 * t))
        v1, v2, v3 = (3, 0, 0), (1, 0, 3), (1, height, 1)
        box.set_data(box_origin, v1, v2, v3)
        volume = abs(np.linalg.det(np.column_stack([v1, v2, v3])))
        vol_label.set_text(f"vol {volume:.2f}")

        idx = int(t / 1.5) % len(ranks)
        if idx != state["rank_idx"]:
            state["rank_idx"] = idx
            k = ranks[idx]
            panel.set_image(rank_image(k))
            rank_label.set_text(f"rank {k}/32")

        forge.set_debug_lines([
            f"pulse {state['pulses']}",
            f"cam yaw {forge.camera.yaw:.2f} pitch {forge.camera.pitch:.2f}",
            "F1 hides this overlay",
        ])

    forge.run(tick, frame)


def run_with_crashlog(fn):
    try:
        fn()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("forge.demo crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)


if __name__ == "__main__":
    run_with_crashlog(main)
```

File 8 — settings.json (version bump only)

```json
{
    "title": "Homeworld: A Good Basis",
    "version": "0.3.0",
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

    Send to DeepSeek: the 8 files, verbatim, commit message: NT step 4: text (glyph atlas) + remaining primitives — forge feature-complete — and update COMMENTARIES.md.
    Run: double-click run.bat (nothing to reinstall).

👀 WHAT YOU SHOULD SEE (new things, on top of the previous build)

    Text floating in space: "The origin (0,0,0)" near the center, always turning to face you as the camera orbits.
    The green wire box on the right slowly flattening like a collapsing tent, and its label counting "vol 27.00" down to exactly "vol 0.00" at the moment it's flat — you are watching a determinant die and resurrect. This is the Bible's Mission 12 mechanic, already alive.
    The grayscale picture panel on the left: starts as a blurry smear, then sharpens in visible steps as the label counts "rank 1/32 → 2 → 4 → 8 → 16 → 32", then loops. That's live SVD image compression — the Guidestone code path, within budget. 😉
    A white fading trail behind the sweeping arrow's tip, like a comet.
    A squashed magenta sphere (the Ellipsoid — future shields).
    fps counter in the bottom-left corner; F1 toggles debug text top-left; F12 / ESC / resizing all still work.

📝 REPORT BACK

The usual: exactly that / different (describe) / crashlog. Two specific things to glance at: (a) does the text look clean and readable (it uses your Windows Consolas font), and (b) does "vol 0.00" line up with the box being perfectly flat?

Once you confirm, forge is DONE — and the next package is helm (the input module: your keyboard-and-mouse action layer, plus its little demo where every keypress prints its action name). After that, fleet — and then ships fly. 🚀❤️
