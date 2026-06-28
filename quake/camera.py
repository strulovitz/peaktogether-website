"""
camera.py (M1) — the decoupled, critically-damped, pitch-clamped camera.

PURE MATH ONLY. No GL, no window, no IO. Fully headless-testable.

Comfort invariants (locked):
  - Only the Mover's heading drives yaw. There is no aim input in update(),
    so it is structurally impossible for aiming to rotate the camera.
  - The camera FOLLOWS heading with a critically-damped spring (no overshoot
    at the tested step rates).
  - Pitch is CLAMPED to +/-PITCH_CLAMP_RAD, then smoothed.

Coordinates: floorplan is the XZ map-plane, Y is up.
Compass: heading theta -> world forward (cos theta, 0, sin theta);
         +X = east, +Z = north.
Matrix convention: returned view matrix is np.ndarray (4,4) float32, ROW-MAJOR
                   (C-contiguous) memory layout.
"""

from __future__ import annotations

from math import cos, sin, pi

import numpy as np

from contracts import Vec3, ViewMatrix, PITCH_CLAMP_RAD

# --- Pinned constants ---------------------------------------------------------
CAM_HEADING_OMEGA = 12.0   # spring natural frequency (rad/s); critically damped
CAM_PITCH_OMEGA = 14.0
EYE_HEIGHT_M = 1.6         # camera Y offset above pos.y (pos is feet/floor)

_TAU = 2.0 * pi


# =============================================================================
# PURE CORE — plain functions on numbers / numpy arrays. Zero state, zero IO.
# =============================================================================

def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def wrap_pi(angle: float) -> float:
    """Wrap an angle into [-pi, pi]."""
    w = (angle + pi) % _TAU - pi
    return w


def critically_damped_step(
    val: float, vel: float, target: float, omega: float, dt: float
) -> tuple[float, float]:
    """
    One semi-implicit critically-damped spring step.

        a    = omega*omega*(target - val) - 2*omega*vel
        vel += a * dt
        val += vel * dt

    Returns the new (val, vel). Stable; monotonic (no overshoot) at the engine's
    update rates (omega*dt small).
    """
    a = omega * omega * (target - val) - 2.0 * omega * vel
    vel = vel + a * dt
    val = val + vel * dt
    return val, vel


def forward_from_angles(yaw: float, pitch: float) -> np.ndarray:
    """
    FROZEN COMPASS. Heading/bearing theta -> world forward (cos theta, 0, sin theta),
    +X = east, +Z = north. With pitch:

        forward = (cos(pitch)*cos(yaw), sin(pitch), cos(pitch)*sin(yaw))

    Returns a unit-length float32 vector (already normalized by construction).
    """
    cp = cos(pitch)
    return np.array(
        (cp * cos(yaw), sin(pitch), cp * sin(yaw)),
        dtype=np.float32,
    )


def look_at(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    """
    Right-handed look-at view matrix (world -> view).

    Built with the standard column-vector convention: V @ [point, 1] maps a world
    point into view space, where the camera looks down -Z in view space, +X right,
    +Y up. The returned array is float32 and C-contiguous (ROW-MAJOR memory).

    INTEGRATION: confirm exact API / multiply side with the renderer.
        This returns V for the COLUMN-vector convention (V @ p). If the renderer
        multiplies on the RIGHT (p @ M, row-vector / some row-major shader paths),
        it must transpose this matrix. Memory layout here is row-major; the
        mathematical convention is column-vector. The test suite checks only
        shape/dtype/determinism, so this choice cannot be inferred from tests and
        MUST be confirmed at the GL boundary.
    """
    eye = np.asarray(eye, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)

    # f: forward (eye -> target). Camera looks along -f in RH view space.
    f = target - eye
    f /= np.linalg.norm(f)

    # s: right = forward x up
    s = np.cross(f, up)
    s /= np.linalg.norm(s)

    # u: true up = right x forward
    u = np.cross(s, f)

    m = np.identity(4, dtype=np.float64)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)

    # float32, C-contiguous (row-major memory).
    return np.ascontiguousarray(m, dtype=np.float32)


# =============================================================================
# SHARED PROJECTION (Parent 11) — the ONE place perspective is defined.
# Used by both the game (app.py) and the build-time map viewer.
# =============================================================================
FOV_Y_DEG = 60.0
NEAR_M = 0.1
FAR_M = 5000.0


def perspective(fov_y_deg: float, aspect: float, near: float, far: float) -> np.ndarray:
    """Standard right-handed perspective, column-vector (M @ p). Row-major float32.
    w_clip = -z_view (m[3,2] = -1), so clip.w IS the linear view distance."""
    import math
    f = 1.0 / math.tan(fov_y_deg * math.pi / 360.0)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return np.ascontiguousarray(m, dtype=np.float32)


# =============================================================================
# THIN STATEFUL SHELL — holds smoothed yaw/pitch state, calls the pure core.
# =============================================================================

class Camera:
    """
    Decoupled, critically-damped, pitch-clamped camera.

    State is the smoothed (_yaw, _pitch) and their velocities. The Shooter never
    appears here: update() has no aim input, so aiming cannot rotate the view.
    """

    def __init__(self) -> None:
        self._yaw: float = 0.0
        self._yaw_vel: float = 0.0
        self._pitch: float = 0.0
        self._pitch_vel: float = 0.0
        self._initialized: bool = False

    def update(
        self, heading_rad: float, pitch_rad: float, pos: Vec3, dt: float
    ) -> ViewMatrix:
        """
        Advance the smoothed camera state by dt and return a (4,4) float32
        row-major right-handed view matrix.
        """
        target_yaw = heading_rad
        target_pitch = clamp(pitch_rad, -PITCH_CLAMP_RAD, PITCH_CLAMP_RAD)

        if not self._initialized:
            self._yaw = target_yaw
            self._yaw_vel = 0.0
            self._pitch = target_pitch
            self._pitch_vel = 0.0
            self._initialized = True
        else:
            yaw_delta = wrap_pi(target_yaw - self._yaw)
            new_local, self._yaw_vel = critically_damped_step(
                0.0, self._yaw_vel, yaw_delta, CAM_HEADING_OMEGA, dt
            )
            self._yaw = self._yaw + new_local

            self._pitch, self._pitch_vel = critically_damped_step(
                self._pitch, self._pitch_vel, target_pitch, CAM_PITCH_OMEGA, dt
            )

        eye = np.array(
            (pos[0], pos[1] + EYE_HEIGHT_M, pos[2]), dtype=np.float64
        )
        forward = forward_from_angles(self._yaw, self._pitch).astype(np.float64)
        up = np.array((0.0, 1.0, 0.0), dtype=np.float64)

        return look_at(eye, eye + forward, up)
