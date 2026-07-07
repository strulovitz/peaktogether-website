"""
LOOM2 -- graphics/camera.py
ONE camera state shared by BOTH panels (SUTRAS 3.2). Pure math, no GL calls.
Allowed imports: math, numpy, config, core.types.

Implemented by Parent C (Claude Fable 5), July 7, 2026.

CONVENTIONS (the sacred seam):
  * World is z-up. Angles in the xy-plane are MATH convention:
    +x = 0 deg, +y = 90 deg, counter-clockwise (matches FAMILY_ANGLE_DEG
    and audio/musicians.py stage angles).
  * Matrix convention: column vectors, clip = VP @ p. Consumers upload
    transposed (matrix.T.tobytes()) to moderngl -- same as helix_panel.
  * azimuth_deg = 0 places the eye due SOUTH of the target (world -y),
    looking toward +y. Therefore brass (world +y, math 90 deg) sits at
    screen 12 o'clock in the default view -- the clock reads correctly
    (SUTRAS 3.5). Increasing azimuth orbits the eye counter-clockwise
    (seen from above). If integration reveals the surround field is
    mirrored, the ONE-SIGN fix is in _eye_offset() below -- nowhere else.
  * zoom is magnification: distance = base_distance / zoom, so
    factor > 1 means closer. Zoom NEVER touches audio (SUTRAS 3.1).
  * view_proj_helix uses a FIXED distance (contract G3.2): the full
    orchestra helix is always framed whole; zoom applies to terrain only.

camera_limits keys read here (DE-FACTO CONTRACT, per DeepSeek 2026-07-07):
    "target"   : [x, y, z] world point the camera looks at (default [0,0,0])
    "zoom_min" : float, lower zoom clamp                    (default 0.5)
    "zoom_max" : float, upper zoom clamp                    (default 2.5)
    "distance" : OPTIONAL float, base eye distance at zoom=1 (default 14.0)
"""
import math
import numpy as np
import config
from core.types import CameraState

# ---------- panel aspect (the 50/50 split, from config alone) ----------
_PANEL_W = config.WINDOW_W // 2
_PANEL_H = int(config.WINDOW_H * config.PANELS_FRAC)
_ASPECT = _PANEL_W / _PANEL_H            # ~1.2355 at 1280x720

# ---------- helix framing constants ----------
# Mirrors graphics/helix_panel.py lines 44-56 (accepted code; verbatim
# values relayed by DeepSeek 2026-07-07). Panel space: 1.0 z per octave.
_HELIX_R = config.NMAX_RING * config.RING_WIDTH + 0.7   # _R_STACK = 4.7
_MIDI_LO, _MIDI_HI, _MIDI_A4 = 23, 96, 69               # B0 .. C7, A4 origin
_HELIX_Z_LO = (_MIDI_LO - _MIDI_A4) / 12.0              # ~ -3.833
_HELIX_Z_HI = (_MIDI_HI - _MIDI_A4) / 12.0              # ~ +2.250

# ---------- projection tuning ----------
_FOV_TERRAIN_DEG = 30.0   # narrow fov = flattened, isometric-feel (Ultima)
_FOV_HELIX_DEG = 45.0
_HELIX_MARGIN = 1.10      # 10% breathing room around the helix
_NEAR_FRAC = 0.05         # near plane as a fraction of eye distance
_FAR_MULT = 20.0          # far plane as a multiple of eye distance


def _perspective(fovy_deg: float, aspect: float,
                 near: float, far: float) -> np.ndarray:
    """Standard OpenGL perspective matrix (column-vector convention)."""
    f = 1.0 / math.tan(math.radians(fovy_deg) * 0.5)
    m = np.zeros((4, 4), dtype=np.float64)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def _look_at(eye: np.ndarray, target: np.ndarray,
             up: np.ndarray) -> np.ndarray:
    """Right-handed look-at view matrix (column-vector convention)."""
    fwd = target - eye
    fwd = fwd / np.linalg.norm(fwd)
    side = np.cross(fwd, up)
    side = side / np.linalg.norm(side)
    true_up = np.cross(side, fwd)
    m = np.identity(4, dtype=np.float64)
    m[0, :3] = side
    m[1, :3] = true_up
    m[2, :3] = -fwd
    m[0, 3] = -side.dot(eye)
    m[1, 3] = -true_up.dot(eye)
    m[2, 3] = fwd.dot(eye)
    return m


class OrbitCamera:
    def __init__(self, limits: dict):
        """limits from SceneSpec.camera_limits: zoom_min/max, target center.
        Start at config.CAM_DEFAULT."""
        limits = limits or {}
        self._target = np.array(limits.get("target", (0.0, 0.0, 0.0)),
                                dtype=np.float64)
        self._zoom_min = float(limits.get("zoom_min", 0.5))
        self._zoom_max = float(limits.get("zoom_max", 2.5))
        self._base_distance = float(limits.get("distance", 14.0))

        # Helix framing: fixed distance that keeps the WHOLE orchestra
        # cylinder (radius _HELIX_R, z in [_HELIX_Z_LO, _HELIX_Z_HI]) inside
        # the vertical fov at ANY elevation. Bounding-sphere framing is
        # elevation-proof: sphere radius from cylinder half-diagonal.
        half_span = 0.5 * (_HELIX_Z_HI - _HELIX_Z_LO)
        sphere_r = math.hypot(_HELIX_R, half_span)          # ~5.60
        self._helix_distance = (sphere_r * _HELIX_MARGIN /
                                math.sin(math.radians(_FOV_HELIX_DEG * 0.5)))
        self._helix_target = np.array(
            (0.0, 0.0, 0.5 * (_HELIX_Z_LO + _HELIX_Z_HI)), dtype=np.float64)

        self._azimuth_deg = 0.0
        self._elevation_deg = 0.0
        self._zoom = 1.0
        self.reset()

    def orbit(self, d_azimuth_deg: float, d_elevation_deg: float) -> None:
        """Elevation clamped to [CAM_ELEV_MIN_DEG, CAM_ELEV_MAX_DEG] -- the
        'forbidden top' is rounded (SUTRAS 3.5); azimuth wraps 0..360 and
        ALWAYS persists (it is the audio pan reference)."""
        self._azimuth_deg = (self._azimuth_deg + d_azimuth_deg) % 360.0
        self._elevation_deg = min(config.CAM_ELEV_MAX_DEG,
                                  max(config.CAM_ELEV_MIN_DEG,
                                      self._elevation_deg + d_elevation_deg))

    def zoom(self, factor: float) -> None:
        """Visual only. NEVER touches audio (SUTRAS 3.1)."""
        if factor <= 0.0:
            return                      # ignore nonsense, never explode
        self._zoom = min(self._zoom_max,
                         max(self._zoom_min, self._zoom * factor))

    def reset(self) -> None:
        self._azimuth_deg = float(config.CAM_DEFAULT["azimuth_deg"])
        self._elevation_deg = min(config.CAM_ELEV_MAX_DEG,
                                  max(config.CAM_ELEV_MIN_DEG,
                                      float(config.CAM_DEFAULT["elevation_deg"])))
        self._zoom = min(self._zoom_max,
                         max(self._zoom_min,
                             float(config.CAM_DEFAULT["zoom"])))

    def state(self) -> CameraState:
        return CameraState(azimuth_deg=self._azimuth_deg,
                           elevation_deg=self._elevation_deg,
                           zoom=self._zoom)

    # ---------- internals ----------

    def _eye_offset(self, distance: float) -> np.ndarray:
        """Offset from target to eye for the current azimuth/elevation.
        azimuth 0 -> eye due south (-y): horizontal math angle az - 90 deg.
        THE one-sign spot: if the surround field ever proves mirrored,
        flip the sign of az here and nowhere else."""
        az = math.radians(self._azimuth_deg)
        el = math.radians(self._elevation_deg)
        phi = az - 0.5 * math.pi
        horiz = distance * math.cos(el)
        return np.array((horiz * math.cos(phi),
                         horiz * math.sin(phi),
                         distance * math.sin(el)), dtype=np.float64)

    def _view_proj(self, target: np.ndarray, distance: float,
                   fov_deg: float) -> np.ndarray:
        eye = target + self._eye_offset(distance)
        view = _look_at(eye, target, np.array((0.0, 0.0, 1.0)))
        near = max(0.1, distance * _NEAR_FRAC)
        far = distance * _FAR_MULT
        proj = _perspective(fov_deg, _ASPECT, near, far)
        return (proj @ view).astype(np.float32)

    # ---------- the two panels: one camera, two windows ----------

    def view_proj_terrain(self) -> "np.ndarray":
        """4x4 view-projection for the LEFT panel (isometric-feel perspective,
        Ultima-style default angle)."""
        return self._view_proj(self._target,
                               self._base_distance / self._zoom,
                               _FOV_TERRAIN_DEG)

    def view_proj_helix(self) -> "np.ndarray":
        """4x4 for the RIGHT panel: same azimuth & elevation, fixed distance
        framing the full 6-octave helix. Rotating one rotates both."""
        return self._view_proj(self._helix_target,
                               self._helix_distance,
                               _FOV_HELIX_DEG)
