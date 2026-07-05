"""shipwright — procedural solid-ship generator (Amendment A1).

Each class is BUILT, not hand-typed: lofted hull sections (rounded or
boxy cross-sections), slab wings/fins/masts, command towers, engine
nozzles with emissive exhaust discs, painted per-face hull panels
with deterministic per-class variation. Hundreds to ~1500 triangles
per ship. Deterministic: same class name -> identical mesh, always.

build_ship(klass, spec) -> (vertices (N,3), triangles (M,3),
colors (N,4), emissive (N,3)); spec is the ships.json entry (its
"color" drives the palette).
"""

import zlib

import numpy as np

ENGINE_CYAN = (0.5, 1.8, 2.4)
ENGINE_WARM = (2.0, 1.3, 0.55)
MAW_AMBER = (2.0, 1.15, 0.35)
DARK = (0.15, 0.16, 0.19, 1.0)


def _rng(name):
    return np.random.default_rng(zlib.crc32(name.encode()))


class Builder:
    def __init__(self):
        self.v, self.t, self.c, self.e = [], [], [], []

    def face(self, pts, color, emissive=(0.0, 0.0, 0.0)):
        i = len(self.v)
        pts = [tuple(map(float, p)) for p in pts]
        self.v += pts
        n = len(pts)
        self.c += [tuple(color)] * n
        self.e += [tuple(emissive)] * n
        for k in range(1, n - 1):
            self.t.append([i, i + k, i + k + 1])

    def result(self):
        return (np.asarray(self.v, dtype=np.float64),
                np.asarray(self.t, dtype=np.int64),
                np.asarray(self.c, dtype=np.float64),
                np.asarray(self.e, dtype=np.float64))


def _hull(rgb):
    return (0.42 * rgb[0] + 0.36, 0.42 * rgb[1] + 0.36,
            0.42 * rgb[2] + 0.36)


def _panel(base, rng, var=0.16):
    f = 1.0 - var * 0.5 + var * rng.random()
    return (base[0] * f, base[1] * f, base[2] * f, 1.0)


def _ring(z, rx, ry, n=14, p=1.0, y0=0.0):
    a = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    cs, sn = np.cos(a), np.sin(a)
    x = rx * np.sign(cs) * np.abs(cs) ** p
    y = ry * np.sign(sn) * np.abs(sn) ** p + y0
    return np.stack([x, y, np.full(n, z)], axis=1)


def _loft(b, rings, base, rng, var=0.16, cap0=True, cap1=True):
    for r0, r1 in zip(rings[:-1], rings[1:]):
        n = len(r0)
        for j in range(n):
            k = (j + 1) % n
            b.face([r0[j], r0[k], r1[k], r1[j]], _panel(base, rng, var))
    if cap0:
        b.face(list(rings[0][::-1]), _panel(base, rng, var))
    if cap1:
        b.face(list(rings[-1]), _panel(base, rng, var))


def _slab(b, outline, axis, th, color, emissive=(0.0, 0.0, 0.0)):
    o = np.asarray(outline, dtype=np.float64)
    off = np.asarray(axis, dtype=np.float64) * (th * 0.5)
    top, bot = o + off, o - off
    b.face(list(top), color, emissive)
    b.face(list(bot[::-1]), color, emissive)
    n = len(o)
    for j in range(n):
        k = (j + 1) % n
        b.face([top[j], top[k], bot[k], bot[j]], color, emissive)


def _box(b, center, size, color):
    cx, cy, cz = center
    sx, sy, sz = size
    rect = [(cx - sx / 2, cy, cz - sz / 2), (cx + sx / 2, cy, cz - sz / 2),
            (cx + sx / 2, cy, cz + sz / 2), (cx - sx / 2, cy, cz + sz / 2)]
    _slab(b, rect, (0, 1, 0), sy, color)


def _tube(b, x, y, z0, z1, r, n, color):
    off = np.array([x, y, 0.0])
    r0 = _ring(z0, r, r, n) + off
    r1 = _ring(z1, r, r, n) + off
    for j in range(n):
        k = (j + 1) % n
        b.face([r0[j], r0[k], r1[k], r1[j]], color)
    b.face(list(r0[::-1]), color)
    b.face(list(r1), color)


def _nozzle(b, x, y, z_rear, r, glow, n=10):
    off = np.array([x, y, 0.0])
    rf = _ring(z_rear + 2.4 * r, 0.8 * r, 0.8 * r, n) + off
    rr = _ring(z_rear, r, r, n) + off
    for j in range(n):
        k = (j + 1) % n
        b.face([rf[j], rf[k], rr[k], rr[j]], DARK)
    b.face(list(rr[::-1]), (0.05, 0.05, 0.06, 1.0), glow)


# ---- class recipes (forward = +z, up = +y) ----

def _fighter(spec):
    b, rng = Builder(), _rng("fighter")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 14, 1.0, y0) for z, rx, ry, y0 in [
        (1.95, 0.03, 0.03, 0.00), (1.50, 0.13, 0.11, 0.02),
        (0.95, 0.24, 0.19, 0.04), (0.35, 0.30, 0.25, 0.05),
        (-0.30, 0.29, 0.25, 0.05), (-0.95, 0.23, 0.21, 0.03),
        (-1.45, 0.16, 0.16, 0.00), (-1.80, 0.10, 0.11, 0.00)]]
    _loft(b, rings, base, rng)
    glass = (0.05, 0.09, 0.14, 1.0)
    canopy = [_ring(z, rx, ry, 10, 1.0, y0) for z, rx, ry, y0 in [
        (0.85, 0.02, 0.02, 0.24), (0.45, 0.10, 0.07, 0.33),
        (0.00, 0.11, 0.07, 0.34), (-0.35, 0.08, 0.05, 0.28)]]
    _loft(b, canopy, glass, rng, var=0.03)
    for s in (1, -1):
        wing = [(s * 0.28, 0.0, 0.55), (s * 1.85, -0.06, -0.60),
                (s * 1.90, -0.06, -1.05), (s * 0.28, 0.0, -0.80)]
        _slab(b, wing, (0, 1, 0), 0.07, acc)
    fin = [(0, 0.18, -0.75), (0, 0.85, -1.35), (0, 0.85, -1.60),
           (0, 0.14, -1.50)]
    _slab(b, fin, (1, 0, 0), 0.06, acc)
    for s in (1, -1):
        _nozzle(b, s * 0.30, 0.0, -2.05, 0.12, ENGINE_CYAN)
    return b.result()


def _corvette(spec):
    b, rng = Builder(), _rng("corvette")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 12, 0.55, y0) for z, rx, ry, y0 in [
        (2.30, 0.16, 0.14, 0.00), (1.60, 0.62, 0.42, 0.04),
        (0.60, 0.85, 0.58, 0.06), (-0.50, 0.85, 0.58, 0.06),
        (-1.50, 0.68, 0.50, 0.03), (-2.20, 0.42, 0.36, 0.00)]]
    _loft(b, rings, base, rng)
    for s in (1, -1):
        _tube(b, s * 0.40, 0.20, 1.20, 2.75, 0.08, 8, DARK)
        _box(b, (s * 1.05, 0.0, -1.10), (0.45, 0.42, 1.10),
             _panel(base, rng))
    _slab(b, [(0, 0.6, 0.4), (0, 1.1, -0.4), (0, 1.1, -0.8),
              (0, 0.55, -0.9)], (1, 0, 0), 0.07, acc)
    for s in (1, -1):
        _nozzle(b, s * 0.40, 0.0, -2.55, 0.17, ENGINE_CYAN)
    return b.result()


def _collector(spec):
    b, rng = Builder(), _rng("collector")
    base = _hull(spec["color"])
    rings = [_ring(z, rx, ry, 14, 1.0, y0) for z, rx, ry, y0 in [
        (2.10, 0.32, 0.32, 0.00), (1.50, 0.85, 0.72, -0.02),
        (0.50, 1.15, 0.98, -0.05), (-0.60, 1.15, 0.98, -0.05),
        (-1.60, 0.85, 0.75, -0.02), (-2.20, 0.40, 0.40, 0.00)]]
    _loft(b, rings, base, rng, cap0=False)
    b.face(list(rings[0][::-1]), (0.06, 0.05, 0.04, 1.0), MAW_AMBER)
    for s in (1, -1):
        _tube(b, s * 1.05, 0.15, 1.00, -1.40, 0.32, 10, _panel(base, rng))
    _nozzle(b, 0.0, 0.0, -2.60, 0.28, ENGINE_WARM)
    return b.result()


def _frigate(spec):
    b, rng = Builder(), _rng("frigate")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 14, 0.7, y0) for z, rx, ry, y0 in [
        (3.60, 0.13, 0.12, 0.00), (2.70, 0.50, 0.40, 0.03),
        (1.30, 0.72, 0.55, 0.05), (-0.40, 0.76, 0.60, 0.05),
        (-2.00, 0.62, 0.50, 0.03), (-3.20, 0.40, 0.35, 0.00)]]
    _loft(b, rings, base, rng)
    for s in (1, -1):
        prong = [(s * 0.28, 0.0, 2.60), (s * 0.50, 0.0, 4.10),
                 (s * 0.62, 0.0, 3.90), (s * 0.52, 0.0, 2.45)]
        _slab(b, prong, (0, 1, 0), 0.16, acc)
    mast = [(0, 0.70, -0.20), (0, 1.70, -0.90), (0, 1.70, -1.25),
            (0, 0.60, -1.30)]
    _slab(b, mast, (1, 0, 0), 0.08, acc)
    b.face([(-0.12, 1.72, -0.95), (0.12, 1.72, -0.95),
            (0.12, 1.72, -1.20), (-0.12, 1.72, -1.20)],
           (0.06, 0.06, 0.07, 1.0), ENGINE_CYAN)
    for x in (-0.5, 0.0, 0.5):
        _nozzle(b, x, 0.0, -3.55, 0.20, ENGINE_CYAN)
    return b.result()


def _mothership(spec):
    b, rng = Builder(), _rng("mothership")
    base = _hull(spec["color"])
    acc = (spec["color"][0] * 0.85, spec["color"][1] * 0.85,
           spec["color"][2] * 0.85, 1.0)
    rings = [_ring(z, rx, ry, 16, 0.65, y0) for z, rx, ry, y0 in [
        (7.20, 0.50, 0.45, 0.00), (5.60, 1.70, 1.25, 0.10),
        (3.60, 2.35, 1.80, 0.15), (1.20, 2.65, 2.10, 0.15),
        (-1.40, 2.70, 2.15, 0.15), (-3.80, 2.45, 2.00, 0.10),
        (-5.80, 1.70, 1.50, 0.00), (-7.00, 1.00, 0.95, 0.00)]]
    _loft(b, rings, base, rng, var=0.12)
    _box(b, (0.0, 2.55, 2.20), (1.10, 0.90, 1.80), _panel(base, rng))
    _box(b, (0.0, 3.25, 1.80), (0.70, 0.60, 1.00), _panel(base, rng))
    b.face([(-0.30, 3.30, 2.32), (0.30, 3.30, 2.32),
            (0.30, 3.50, 2.32), (-0.30, 3.50, 2.32)],
           (0.10, 0.10, 0.10, 1.0), (1.6, 1.1, 0.5))
    for s in (1, -1):
        b.face([(s * 2.74, -0.30, 2.50), (s * 2.74, -0.30, -2.50),
                (s * 2.74, 0.30, -2.50), (s * 2.74, 0.30, 2.50)],
               (0.08, 0.08, 0.09, 1.0), (1.3, 0.85, 0.35))
    _slab(b, [(0, 2.20, -3.00), (0, 3.40, -4.20), (0, 3.40, -4.80),
              (0, 2.00, -4.40)], (1, 0, 0), 0.09, acc)
    _nozzle(b, 0.0, 0.30, -7.40, 0.42, ENGINE_WARM, n=12)
    for s in (1, -1):
        _nozzle(b, s * 0.75, -0.25, -7.40, 0.40, ENGINE_WARM, n=12)
    return b.result()


_RECIPES = {
    "fighter": _fighter,
    "corvette": _corvette,
    "collector": _collector,
    "frigate": _frigate,
    "mothership": _mothership,
}


def build_ship(klass, spec):
    recipe = _RECIPES.get(klass)
    if recipe is None:                      # generic fallback hull
        b, rng = Builder(), _rng(klass)
        base = _hull(spec.get("color", [0.6, 0.7, 0.8, 1.0]))
        rings = [_ring(z, r, r * 0.8, 12) for z, r in [
            (1.8, 0.05), (1.0, 0.5), (0.0, 0.7), (-1.0, 0.5), (-1.8, 0.2)]]
        _loft(b, rings, base, rng)
        _nozzle(b, 0.0, 0.0, -2.1, 0.18, ENGINE_CYAN)
        return b.result()
    return recipe(spec)
