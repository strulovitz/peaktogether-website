"""Camera: ORBIT mode + view/projection math (NEW_TESTAMENT 1.3).

All math is plain numpy, float64. Right-handed, Y up.
FOLLOW and POV modes will be added in a later package; the frozen
interface methods exist now so no caller ever changes.
"""

import numpy as np


def _normalize(v):
    n = np.linalg.norm(v)
    if n < 1e-12:
        return v
    return v / n


def look_at(eye, target, up):
    """Standard right-handed look-at view matrix (4x4 float64)."""
    eye = np.asarray(eye, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)
    f = _normalize(target - eye)          # forward
    s = _normalize(np.cross(f, up))       # right
    u = np.cross(s, f)                    # true up
    m = np.eye(4, dtype=np.float64)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -s @ eye
    m[1, 3] = -u @ eye
    m[2, 3] = f @ eye
    return m


def perspective(fov_y, aspect, near, far):
    """Standard OpenGL perspective projection matrix (4x4 float64)."""
    t = 1.0 / np.tan(fov_y * 0.5)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = t / aspect
    m[1, 1] = t
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


class Camera:
    def __init__(self):
        self.mode = "ORBIT"
        self.target = np.zeros(3, dtype=np.float64)
        self.yaw = 0.8          # radians
        self.pitch = 0.35       # radians, clamped to (-1.55, 1.55)
        self.distance = 32.0    # clamped to (2, 500)
        self.fov_y = 1.05       # ~60 degrees
        self.near = 0.1
        self.far = 2000.0

    # ---- frozen interface (NEW_TESTAMENT 1.3) ----

    def set_orbit(self, target):
        self.mode = "ORBIT"
        self.target = np.asarray(target, dtype=np.float64).copy()

    def orbit_input(self, d_yaw, d_pitch, d_zoom):
        self.yaw += d_yaw
        self.pitch = float(np.clip(self.pitch + d_pitch, -1.55, 1.55))
        self.distance = float(np.clip(self.distance * (1.0 + d_zoom), 2.0, 500.0))

    def eye(self):
        """Camera position: eye = target + d*(cos(p)sin(y), sin(p), cos(p)cos(y))."""
        cp = np.cos(self.pitch)
        offset = self.distance * np.array(
            [cp * np.sin(self.yaw), np.sin(self.pitch), cp * np.cos(self.yaw)],
            dtype=np.float64,
        )
        return self.target + offset

    def view(self):
        return look_at(self.eye(), self.target, np.array([0.0, 1.0, 0.0]))

    def proj(self, aspect):
        return perspective(self.fov_y, aspect, self.near, self.far)
