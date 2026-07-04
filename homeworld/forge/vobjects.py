"""VObjects: the primitive vocabulary (NEW_TESTAMENT 1.4).

Walking-skeleton set: Line, Arrow, DashedLine, Grid, WireSphere.
(SpannedBox, Ellipsoid, WireMesh, Trail, Label, ImagePanel arrive in
the next packages.)

Every primitive reduces itself to an array of line segments of shape
(N, 2, 3): N segments, each with two endpoints in 3D. set_data()
always copies its numpy inputs (no aliasing of caller memory).
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
            segs.append((end, ring[i]))                # pyramid edges to tip
            segs.append((ring[i], ring[(i + 1) % 4]))  # base ring
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
    """Plane grid spanned by vectors u and v — THIS is how 'span' is drawn.

    Lines run through center + i*spacing*v along direction u, and
    through center + i*spacing*u along direction v, for i in [-n, n].
    """

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
        for i in idx:  # lines along u
            segs.append((c + i * v - ext * u, c + i * v + ext * u))
        for i in idx:  # lines along v
            segs.append((c + i * u - ext * v, c + i * u + ext * v))
        self._segments = np.array(segs, dtype=np.float64)


class WireSphere(VObject):
    """Three orthogonal great circles."""

    def __init__(self, center, radius, seg=24, **kw):
        super().__init__(**kw)
        self.set_data(center, radius, seg)

    def set_data(self, center, radius, seg=24):
        c = np.asarray(center, dtype=np.float64).copy()
        t = np.linspace(0.0, 2.0 * np.pi, seg + 1)
        cos_t, sin_t = np.cos(t), np.sin(t)
        zeros = np.zeros_like(t)
        circles = [
            np.stack([cos_t, sin_t, zeros], axis=1),  # XY plane
            np.stack([zeros, cos_t, sin_t], axis=1),  # YZ plane
            np.stack([cos_t, zeros, sin_t], axis=1),  # XZ plane
        ]
        segs = []
        for pts in circles:
            p = c[None, :] + radius * pts
            segs.append(np.stack([p[:-1], p[1:]], axis=1))
        self._segments = np.concatenate(segs, axis=0)
