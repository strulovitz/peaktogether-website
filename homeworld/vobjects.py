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
