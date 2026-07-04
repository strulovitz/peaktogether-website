"""CPU geometry expansion (NEW_TESTAMENT 1.5).

Every line segment becomes a camera-facing ribbon (two triangles).
For a segment p0 -> p1 with half-width w and camera eye e:
    side = normalize( (p1 - p0) x (e - p0) )
    quad corners: p0 -/+ w*side, p1 +/- w*side
Each vertex carries a ribbon coordinate u in [-1, +1] across the
width; the fragment shader turns that into a hot core + soft edge.

Everything is vectorized numpy over ALL segments at once. The walking
skeleton rebuilds all geometry every frame (a few thousand segments is
trivial); the static/dynamic batch split is a later optimization.

Output vertex format (float32): x, y, z, r, g, b, a, u  -> '3f 4f 1f'.
"""

import numpy as np

_U_PATTERN = np.array([-1.0, 1.0, 1.0, -1.0, 1.0, -1.0], dtype=np.float64)


def build_vertices(vobjects, eye):
    """Collect all visible vobjects and expand to a (M, 8) float32 array."""
    seg_list, col_list, wid_list = [], [], []
    for vob in vobjects:
        if not vob.visible:
            continue
        s = vob.segments()
        n = s.shape[0]
        if n == 0:
            continue
        seg_list.append(s)
        c = np.empty((n, 4), dtype=np.float64)
        c[:, 0] = vob.color[0] * vob.glow
        c[:, 1] = vob.color[1] * vob.glow
        c[:, 2] = vob.color[2] * vob.glow
        c[:, 3] = vob.color[3]
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
        # Segment points straight at the eye (or is degenerate):
        # fall back to any vector perpendicular to d.
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
