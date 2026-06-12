"""corridor.py -- Descent QED, Build Step 1.2: "The Empty Mine".
Corridor EULER-1734: one continuous descending shaft. Robots get no
chambers -- they block the corridor at chevron-framed STATIONS.
v1.2: ELBOW rule, collision union, distance-sorted translucency.
Claude wrote the engine. DeepSeek tasks are marked TODO(DeepSeek)."""

import math
import numpy as np
from OpenGL.GL import *
import palette

BACK_EXTEND = 1.5   # overlap backwards to hide seams at pitch changes
TURN_EXTEND = 4.0   # overlap at turns; flush with ELBOW walls (half-width)
CHEVRON_T   = 0.8

# ---------------------------------------------------------------------------
# THE LAYOUT TABLE.
# TODO(DeepSeek): tune lengths/pitches ONLY after Nir's test flights.
# Editing rules:
#  - yaw_turn applies BEFORE the segment is laid (turn, then go).
#  - pitch tilts THIS segment (negative = descending).
#  - keep pitch == 0 on segments adjacent to a cross-section change.
#  - A TURN MAY ONLY FOLLOW A LEVEL SEGMENT whose half-width equals
#    TURN_EXTEND (use an 8x8x8 "ELBOW" cube, pitch 0, like below).
#   id           kind        w   h    L   pitch  yaw_turn
SEGMENTS = [
    ("MOUTH",     "tunnel",   8,  8,  30,    0,    0),
    ("RUN-1",     "tunnel",   8,  8,  26,   -8,    0),
    ("STATION-1", "station",  8,  8,  16,    0,    0),
    ("RUN-2",     "tunnel",   8,  8,  40,  -10,    0),
    ("STATION-2", "station",  8,  8,  16,    0,    0),
    ("RUN-3A",    "tunnel",   8,  8,  30,  -10,    0),
    ("ELBOW",     "tunnel",   8,  8,   8,    0,    0),
    ("RUN-3B",    "tunnel",   8,  8,  20,    0,  -90),   # the bend
    ("STATION-3", "station", 12, 10,  20,    0,    0),   # boss: wider
    ("RUN-4",     "tunnel",   8,  8,  16,    0,    0),
    ("GALLERY",   "gallery", 14, 10,  80,    0,    0),
]

wall_quads, cap_quads, edge_lines, chevron_quads = [], [], [], []
ROBOT_SLOTS, SIGN_SLOTS = {}, {}   # id -> np.array. Hooks for steps 2-3.
SEG_BOUNDS = []                    # (start, f, r, u, ext, L, hw, hh) collision


def _frame(yaw_deg, pitch_deg):
    """Right-handed frame: yaw=0 faces -Z; positive yaw turns left."""
    y, p = math.radians(yaw_deg), math.radians(pitch_deg)
    r  = np.array([math.cos(y), 0.0, -math.sin(y)])
    up = np.array([0.0, 1.0, 0.0])
    f  = np.array([-math.sin(y), 0.0, -math.cos(y)]) * math.cos(p) + up * math.sin(p)
    return f, r, np.cross(r, f)


def _box(start, end, r, u, w, h):
    hw, hh = w / 2.0, h / 2.0
    cs = [start + r * hw * s + u * hh * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    ce = [end   + r * hw * s + u * hh * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    quads = [(cs[i], cs[(i + 1) % 4], ce[(i + 1) % 4], ce[i]) for i in range(4)]
    return cs, ce, quads


def _striped_frame(center, r, u, w, h, t):
    """Hazard frame: 4 flat strips, alternating blocks.
    TODO(DeepSeek, OPTIONAL polish, last priority): true diagonal stripes."""
    def strip(p0, dlong, llen, dthick, blocks):
        for i in range(blocks):
            a = p0 + dlong * (llen * i / blocks)
            b = p0 + dlong * (llen * (i + 1) / blocks)
            col = palette.CHEVRON_A if i % 2 == 0 else palette.CHEVRON_B
            chevron_quads.append((col, (a, b, b + dthick * t, a + dthick * t)))
    hw, hh = w / 2.0, h / 2.0
    strip(center - r * hw + u * (hh - t), r, w, u, 9)
    strip(center - r * hw - u * hh,       r, w, u, 9)
    strip(center - r * hw - u * (hh - t), u, 2 * (hh - t), r, 5)
    strip(center + r * (hw - t) - u * (hh - t), u, 2 * (hh - t), r, 5)


def _collar(center, r, u, w_in, h_in, w_out, h_out):
    ci = [center + r * w_in / 2 * s + u * h_in / 2 * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    co = [center + r * w_out / 2 * s + u * h_out / 2 * t for s, t in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    for i in range(4):
        cap_quads.append((ci[i], ci[(i + 1) % 4], co[(i + 1) % 4], co[i]))


def _build():
    pos, yaw = np.zeros(3), 0.0
    prev = None              # (f, w, h) of previous segment, for collars
    prev_f, prev_L = None, 0.0
    for idx, (sid, kind, w, h, L, pitch, turn) in enumerate(SEGMENTS):
        if turn != 0:
            # PIVOT RULE (v1.3): a turn rotates around the CENTER of the
            # preceding elbow, not its end face. Retreat half its length;
            # the corner then becomes two tunnels sharing one exact cube:
            # the new tunnel's back face sits flush on the elbow's side
            # wall, its side wall sits flush on the elbow's far face.
            pos = pos - prev_f * (prev_L / 2.0)
        yaw += turn
        f, r, u = _frame(yaw, pitch)
        ext = 0.0 if idx == 0 else (TURN_EXTEND if turn else BACK_EXTEND)
        start, end = pos - f * ext, pos + f * L
        SEG_BOUNDS.append((pos.copy(), f, r, u, ext, L, w / 2.0, h / 2.0))
        cs, ce, quads = _box(start, end, r, u, w, h)
        wall_quads.extend(quads)
        for i in range(4):
            edge_lines.append((cs[i], ce[i]))
            edge_lines.append((cs[i], cs[(i + 1) % 4]))
            edge_lines.append((ce[i], ce[(i + 1) % 4]))
        if idx == 0:
            cap_quads.append(tuple(cs))
            SIGN_SLOTS[sid] = pos + f * 1.0
        if idx == len(SEGMENTS) - 1:
            # Cap ONLY the true dead end. A pre-turn cap is no longer
            # needed: the corner's far face is covered by the new
            # tunnel's wall (capping it too would double-layer the
            # plane and show as a darker patch).
            cap_quads.append(tuple(ce))
        if kind == "station":
            ROBOT_SLOTS[sid] = pos + f * (L / 2.0)
            _striped_frame(pos, r, u, w, h, CHEVRON_T)
            _striped_frame(end, r, u, w, h, CHEVRON_T)
        if kind == "gallery":
            SIGN_SLOTS[sid] = end - f * 2.0
        if prev is not None:
            pf, pw, ph = prev
            if np.allclose(pf, f) and (pw, ph) != (w, h):
                _collar(pos, r, u, min(pw, w), min(ph, h), max(pw, w), max(ph, h))
        prev, prev_f, prev_L = (f, w, h), f, L
        pos = end


_build()

# Baked once for the per-frame depth sort:
_fill_quads = wall_quads + cap_quads
_fill_centers = np.array([np.mean(np.array(q), axis=0) for q in _fill_quads])


def inside(p, margin=0.0):
    """True if p is inside the corridor union (shrunk by margin)."""
    p = np.asarray(p, dtype=float)
    for start, f, r, u, ext, L, hw, hh in SEG_BOUNDS:
        d = p - start
        if (-ext <= d.dot(f) <= L
                and abs(d.dot(r)) <= hw - margin
                and abs(d.dot(u)) <= hh - margin):
            return True
    return False


def draw(wall_alpha, cam_pos):
    # PASS 1: opaque hazard frames (the only color in the world)
    glBegin(GL_QUADS)
    for col, quad in chevron_quads:
        glColor3f(*col)
        for v in quad:
            glVertex3f(*v)
    glEnd()
    # PASS 2: white-grey edges, drawn twice = cheap glow (depth-written)
    for width, alpha in ((3.0, 0.25), (1.0, 1.0)):
        glLineWidth(width)
        glColor4f(*palette.WALL_EDGE, alpha)
        glBegin(GL_LINES)
        for a, b in edge_lines:
            glVertex3f(*a)
            glVertex3f(*b)
        glEnd()
    # PASS 3: translucent rock, SORTED far-to-near from the camera.
    # Unsorted alpha blending is order-dependent (Nir's outside-in bug).
    d2 = ((_fill_centers - np.asarray(cam_pos)) ** 2).sum(axis=1)
    order = np.argsort(-d2)
    glDepthMask(GL_FALSE)
    glColor4f(*palette.WALL_FILL, wall_alpha)
    glBegin(GL_QUADS)
    for i in order:
        for v in _fill_quads[i]:
            glVertex3f(*v)
    glEnd()
    glDepthMask(GL_TRUE)
