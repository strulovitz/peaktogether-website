"""robots.py -- Descent QED, Build Step 2: the robots appear.
Low-poly grey hulls + colored eye bands (the only color they own).
Claude wrote this module. DeepSeek tasks are marked TODO(DeepSeek)."""

import math
import numpy as np
from OpenGL.GL import *
import palette
import corridor

LIGHT_DIR = np.array([0.35, 0.80, 0.45])
LIGHT_DIR /= np.linalg.norm(LIGHT_DIR)
LOCK_RANGE = 60.0

# Per-robot tuning. block_r chosen so hull+margin seals its corridor:
# stations 1-2 are 8 wide (half=4): 3.6 + player 0.6 > 4 -> no way past.
# station 3 is 12 wide (half=6): 5.6 + 0.6 > 6 -> sealed.
# TODO(DeepSeek): tune sizes/spins ONLY after Nir's flight reports.
CFG = {
    "STATION-1": dict(kind="octa",  spin=40.0, lock_r=2.6, block_r=3.6,
                      band_r=1.75, band_y=(0.10, 0.55)),
    "STATION-2": dict(kind="prism4", spin=-55.0, lock_r=2.8, block_r=3.6,
                      band_r=2.15, band_y=(0.20, 0.70)),
    "STATION-3": dict(kind="boss",  spin=18.0, lock_r=4.2, block_r=5.6,
                      band_r=3.55, band_y=(-0.30, 0.45)),
}


# ---- geometry builders (all output triangles: (a, b, c) tuples) ----------

def _octa(rx, ry, rz, dy=0.0):
    top, bot = (0, ry + dy, 0), (0, -ry + dy, 0)
    eq = [(rx, dy, 0), (0, dy, -rz), (-rx, dy, 0), (0, dy, rz)]
    tris = []
    for i in range(4):
        a, b = eq[i], eq[(i + 1) % 4]
        tris.append((top, a, b))
        tris.append((bot, b, a))
    return tris


def _prism(n, rad, h, dy=0.0, phase=0.0):
    ring = [(rad * math.cos(2 * math.pi * i / n + phase),
             rad * math.sin(2 * math.pi * i / n + phase)) for i in range(n)]
    y0, y1 = -h / 2 + dy, h / 2 + dy
    tris = []
    for i in range(n):
        (xa, za), (xb, zb) = ring[i], ring[(i + 1) % n]
        a0, b0 = (xa, y0, za), (xb, y0, zb)
        a1, b1 = (xa, y1, za), (xb, y1, zb)
        tris += [(a0, b0, b1), (a0, b1, a1)]            # side
        tris += [((0, y1, 0), a1, b1), ((0, y0, 0), b0, a0)]  # caps
    return tris


def _band(n, rad, y0, y1):
    ring = [(rad * math.cos(2 * math.pi * i / n),
             rad * math.sin(2 * math.pi * i / n)) for i in range(n)]
    tris = []
    for i in range(n):
        (xa, za), (xb, zb) = ring[i], ring[(i + 1) % n]
        a0, b0 = (xa, y0, za), (xb, y0, zb)
        a1, b1 = (xa, y1, za), (xb, y1, zb)
        tris += [(a0, b0, b1), (a0, b1, a1)]
    return tris


def _hull_tris(kind):
    if kind == "octa":
        return _octa(1.6, 2.2, 1.6)
    if kind == "prism4":                       # diamond box (square, on edge)
        return _prism(4, 2.0, 2.6)
    if kind == "boss":
        return (_prism(6, 3.4, 2.2)
                + _octa(1.1, 1.6, 1.1, dy=2.6)
                + _octa(1.1, 1.6, 1.1, dy=-2.6))
    raise ValueError(kind)


def _shade(tri):
    a, b, c = (np.array(v, float) for v in tri)
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n)
    bright = 0.30 + 0.55 * abs(n.dot(LIGHT_DIR) / ln) if ln > 1e-9 else 0.35
    return tuple(ch * bright for ch in palette.ROBOT_HULL)


# ---- the robot -----------------------------------------------------------

class Robot:
    def __init__(self, sid, base_pos, phase):
        self.sid, self.cfg = sid, CFG[sid]
        self.base_pos = np.asarray(base_pos, float)
        self.eye = palette.ROBOT_EYE[sid]
        self.alive, self.yaw, self.bob, self.phase = True, 0.0, 0.0, phase
        tris = _hull_tris(self.cfg["kind"])
        self._hull_cols = [_shade(t) for t in tris]
        self._hull = np.array([v for t in tris for v in t], float)
        y0, y1 = self.cfg["band_y"]
        self._eyeband = np.array(
            [v for t in _band(12, self.cfg["band_r"], y0, y1) for v in t], float)

    @property
    def pos(self):
        return self.base_pos + np.array([0.0, self.bob, 0.0])

    def update(self, dt, t):
        self.yaw = (self.yaw + self.cfg["spin"] * dt) % 360.0
        self.bob = 0.35 * math.sin(t * 1.3 + self.phase)

    def _to_world(self, verts):
        c, s = math.cos(math.radians(self.yaw)), math.sin(math.radians(self.yaw))
        rot = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
        return verts @ rot.T + self.pos

    def draw(self, t, locked):
        w = self._to_world(self._hull)
        glBegin(GL_TRIANGLES)
        for i, col in enumerate(self._hull_cols):
            glColor3f(*col)
            for v in w[3 * i:3 * i + 3]:
                glVertex3f(*v)
        glEnd()
        pulse = 1.0 if locked else 0.70 + 0.30 * math.sin(t * 5.0 + self.phase)
        glColor3f(*(ch * pulse for ch in self.eye))
        wb = self._to_world(self._eyeband)
        glBegin(GL_TRIANGLES)
        for v in wb:
            glVertex3f(*v)
        glEnd()


ROBOTS = [Robot(sid, pos, i * 2.1)
          for i, (sid, pos) in enumerate(corridor.ROBOT_SLOTS.items())]


def update_all(dt, t):
    for r in ROBOTS:
        if r.alive:
            r.update(dt, t)


def draw_all(t, locked, cam_right, cam_up):
    for r in ROBOTS:
        if r.alive:
            r.draw(t, r is locked)
    if locked is not None and locked.alive:
        _brackets(locked, cam_right, cam_up, t)


def _brackets(rob, right, up, t):
    R = rob.cfg["lock_r"] * 1.25 * (1.0 + 0.06 * math.sin(t * 6.0))
    L = 0.45 * R
    glLineWidth(2.0)
    glColor4f(*rob.eye, 0.9)
    glBegin(GL_LINES)
    for sr in (1, -1):
        for su in (1, -1):
            corner = rob.pos + right * R * sr + up * R * su
            for inward in (-right * L * sr, -up * L * su):
                glVertex3f(*corner)
                glVertex3f(*(corner + inward))
    glEnd()


def find_lock(cam_pos, cam_dir):
    """Nearest live robot near the aim ray. NOTE: locks through walls for
    now -- line-of-sight gating arrives with the real ship step."""
    best, best_d = None, LOCK_RANGE
    for rob in ROBOTS:
        if not rob.alive:
            continue
        v = rob.pos - cam_pos
        d = float(v.dot(cam_dir))
        if 2.0 < d < best_d:
            perp = np.linalg.norm(v - d * np.asarray(cam_dir))
            if perp < rob.cfg["lock_r"] * 1.5:
                best, best_d = rob, d
    return best


def blocked(p, margin):
    return any(r.alive and
               np.linalg.norm(np.asarray(p) - r.pos) < r.cfg["block_r"] + margin
               for r in ROBOTS)


def neutralize(rob):
    if rob is not None and rob.alive:
        rob.alive = False
        print("DEBUG: %s neutralized -- passage open." % rob.sid)
