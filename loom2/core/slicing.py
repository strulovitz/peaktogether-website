"""
LOOM2 -- core/slicing.py
THE ONE TRUE CUT. Shared pure math for the Glass Blade: the intersection of
the (possibly tilted) slicing plane with z = f(x, y), as ordered ground paths.
Imported by BOTH core.game_state (the procession) and graphics.slice_mode
(the drawn curve) -- one implementation, byte-match by construction.
Blessed amendment, tilt ruling 2026-07-08: TILT IS REAL GEOMETRY.
Allowed imports: math, numpy, config, core.types. Nothing else.

Plane definition (canon):
  hinge  = horizontal line through (cx, cy) at heading yaw_deg
  anchor z0 = f(cx, cy)   -- the blade pivots on the ground point under it
  normal n  = (-sin(yaw)cos(tilt), cos(yaw)cos(tilt), sin(tilt)), unit
  cut    = zero level set of g(x,y) = n . ((x, y, f(x,y)) - (cx, cy, z0))
At tilt = 0, g is linear in the horizontal offset, so marching squares
reproduces the old straight vertical transect EXACTLY (regression guard).
"""
import math
import numpy as np
import config

_EPS = 1e-9
_KEY_DECIMALS = 6   # endpoint quantization for segment chaining

# marching-squares segment table: edges 0=bottom 1=right 2=top 3=left,
# case bit0..bit3 = (g00, g10, g11, g01) > 0. Cases 5/10 resolved by center.
_SEG_TABLE = {1: (3, 0), 2: (0, 1), 3: (3, 1), 4: (1, 2), 6: (0, 2),
              7: (3, 2), 8: (2, 3), 9: (0, 2), 11: (1, 2), 12: (3, 1),
              13: (0, 1), 14: (3, 0)}


def eval_heights(surface_fn, X, Y):
    """f over numpy arrays; per-point fallback if surface_fn is not
    vectorized ('vectorization allowed', never guaranteed)."""
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    try:
        Z = np.asarray(surface_fn(X, Y), dtype=np.float64)
        if Z.shape == X.shape:
            return Z
    except Exception:
        pass
    flat = [float(surface_fn(float(x), float(y)))
            for x, y in zip(X.ravel(), Y.ravel())]
    return np.array(flat, dtype=np.float64).reshape(X.shape)


def plane_anchor_z(surface_fn, plane) -> float:
    """z0 = f(cx, cy): the cut always passes through this ground point."""
    return float(eval_heights(surface_fn,
                              np.array([plane.cx]), np.array([plane.cy]))[0])


def plane_normal(plane):
    """Unit normal of the tilted plane (canon formula in the header)."""
    yaw, tilt = math.radians(plane.yaw_deg), math.radians(plane.tilt_deg)
    return (-math.sin(yaw) * math.cos(tilt),
            math.cos(yaw) * math.cos(tilt),
            math.sin(tilt))


def plane_axes(plane):
    """Orthonormal in-plane frame: d = horizontal hinge direction,
    up = tilted 'up'. Used for pane geometry, never for the path math."""
    yaw, tilt = math.radians(plane.yaw_deg), math.radians(plane.tilt_deg)
    d = (math.cos(yaw), math.sin(yaw), 0.0)
    up = (math.sin(yaw) * math.sin(tilt),
          -math.cos(yaw) * math.sin(tilt),
          math.cos(tilt))
    return d, up


def clip_hinge(plane, domain):
    """Slab-clip the hinge line to the domain rectangle. Returns
    (tmin, tmax) along d from (cx, cy), or None. (The old straight-transect
    clip, preserved: it is still the pane's horizontal extent.)"""
    xmin, xmax, ymin, ymax = domain
    dx = math.cos(math.radians(plane.yaw_deg))
    dy = math.sin(math.radians(plane.yaw_deg))
    tmin, tmax = -1e18, 1e18
    for c, d, lo, hi in ((plane.cx, dx, xmin, xmax),
                         (plane.cy, dy, ymin, ymax)):
        if abs(d) < _EPS:
            if not lo <= c <= hi:
                return None
            continue
        t0, t1 = (lo - c) / d, (hi - c) / d
        if t0 > t1:
            t0, t1 = t1, t0
        tmin, tmax = max(tmin, t0), min(tmax, t1)
    return None if tmax <= tmin else (tmin, tmax)


def _cell_segments(g, xs, ys):
    """Marching squares: line segments of the zero set of g, per grid cell."""
    pos = (g > 0.0)
    case = (pos[:-1, :-1].astype(np.int8) | (pos[:-1, 1:] << 1)
            | (pos[1:, 1:] << 2) | (pos[1:, :-1] << 3))
    segs = []
    for j, i in np.argwhere((case != 0) & (case != 15)):
        g00, g10 = g[j, i], g[j, i + 1]
        g01, g11 = g[j + 1, i], g[j + 1, i + 1]
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[j], ys[j + 1]

        def edge(e):
            if e == 0:
                t = g00 / (g00 - g10); return (x0 + t * (x1 - x0), y0)
            if e == 1:
                t = g10 / (g10 - g11); return (x1, y0 + t * (y1 - y0))
            if e == 2:
                t = g01 / (g01 - g11); return (x0 + t * (x1 - x0), y1)
            t = g00 / (g00 - g01)
            return (x0, y0 + t * (y1 - y0))

        c = int(case[j, i])
        if c in (5, 10):    # ambiguous saddle cell: center sign decides
            center = 0.25 * (g00 + g10 + g11 + g01)
            if c == 5:
                pairs = ((0, 1), (2, 3)) if center > 0 else ((3, 0), (1, 2))
            else:
                pairs = ((3, 0), (1, 2)) if center > 0 else ((0, 1), (2, 3))
        else:
            pairs = (_SEG_TABLE[c],)
        for ea, eb in pairs:
            segs.append((edge(ea), edge(eb)))
    return segs


def _chain(segs):
    """Chain segments into polylines. Returns [(points, closed)]."""
    def key(p):
        return (round(p[0], _KEY_DECIMALS), round(p[1], _KEY_DECIMALS))
    adj = {}
    for si, (a, b) in enumerate(segs):
        adj.setdefault(key(a), []).append((si, 0))
        adj.setdefault(key(b), []).append((si, 1))
    used = [False] * len(segs)

    def walk(si, start_end):
        used[si] = True
        a, b = segs[si]
        pts = [a, b] if start_end == 0 else [b, a]
        while True:
            candidates = [se for se in adj.get(key(pts[-1]), ())
                          if not used[se[0]]]
            if not candidates:
                return pts
            sj, e = candidates[0]
            used[sj] = True
            a2, b2 = segs[sj]
            pts.append(b2 if e == 0 else a2)

    paths = []
    for k, lst in adj.items():          # open curves first (degree-1 ends)
        if len(lst) == 1 and not used[lst[0][0]]:
            paths.append((walk(*lst[0]), False))
    for si in range(len(segs)):         # remaining: closed loops
        if not used[si]:
            pts = walk(si, 0)
            pts.append(pts[0])
            paths.append((pts, True))
    return paths


def slice_components(surface_fn, plane, domain, grid_step=0.25):
    """THE CUT. Ordered components, primary (walked) component FIRST --
    the one passing nearest the anchor (with z0 = f(cx,cy) it passes
    through it). Each component is an ordered [(x, y), ...]; closed loops
    repeat their first point last. [] if the blade misses the land."""
    xmin, xmax, ymin, ymax = domain
    nx = max(2, int(round((xmax - xmin) / grid_step)) + 1)
    ny = max(2, int(round((ymax - ymin) / grid_step)) + 1)
    xs, ys = np.linspace(xmin, xmax, nx), np.linspace(ymin, ymax, ny)
    X, Y = np.meshgrid(xs, ys)
    Z = eval_heights(surface_fn, X, Y)
    z0 = plane_anchor_z(surface_fn, plane)
    nxv, nyv, nzv = plane_normal(plane)
    g = nxv * (X - plane.cx) + nyv * (Y - plane.cy) + nzv * (Z - z0)
    g = np.where(g == 0.0, 1e-12, g)     # no exact zeros: degeneracy guard
    segs = _cell_segments(g, xs, ys)
    if not segs:
        return []
    dxh = math.cos(math.radians(plane.yaw_deg))
    dyh = math.sin(math.radians(plane.yaw_deg))
    comps = []
    for pts, closed in _chain(segs):
        if len(pts) < 2:
            continue
        if closed:                       # start loops nearest the anchor
            ring = pts[:-1]
            k = min(range(len(ring)), key=lambda i:
                    (ring[i][0] - plane.cx) ** 2 + (ring[i][1] - plane.cy) ** 2)
            pts = ring[k:] + ring[:k] + [ring[k]]
            sx, sy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        else:
            sx, sy = pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1]
        if sx * dxh + sy * dyh < 0.0:    # stable procession direction
            pts = pts[::-1]
        d2 = min((px - plane.cx) ** 2 + (py - plane.cy) ** 2 for px, py in pts)
        comps.append((d2, pts, closed))
    comps.sort(key=lambda t: t[0])
    return [(pts, closed) for _, pts, closed in comps]


def resample_path(points, step):
    """Arc-length resample in the ground plane: samples at 0, step, 2*step,
    ... and ALWAYS the exact final point (the old transect's endpoint rule)."""
    if len(points) < 2:
        return list(points)
    out = [points[0]]
    px, py = points[0]
    left = step
    for qx, qy in points[1:]:
        seg = math.hypot(qx - px, qy - py)
        while seg >= left - _EPS and seg > _EPS:
            f = left / seg
            px, py = px + f * (qx - px), py + f * (qy - py)
            out.append((px, py))
            seg = math.hypot(qx - px, qy - py)
            left = step
        left -= seg
        px, py = qx, qy
    if math.hypot(points[-1][0] - out[-1][0],
                  points[-1][1] - out[-1][1]) > 1e-6:
        out.append(points[-1])
    return out


def walk_path(surface_fn, plane, domain,
              step=config.RING_WIDTH, grid_step=0.25):
    """game_state's ONE call: the procession itinerary. Primary component,
    one stop per `step`, exact endpoint kept. [] if the blade misses.
    At tilt = 0: entry point, stops every step, exact exit -- the old law."""
    comps = slice_components(surface_fn, plane, domain, grid_step)
    return resample_path(comps[0][0], step) if comps else []
