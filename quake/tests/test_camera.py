"""Headless unit tests for camera.py (M1). Pure math; no GL, no window."""

from math import pi

import numpy as np

from camera import (
    Camera,
    forward_from_angles,
    PITCH_CLAMP_RAD,
    CAM_HEADING_OMEGA,
)

DT = 1.0 / 60.0
ORIGIN = (0.0, 0.0, 0.0)


def test_pitch_clamped():
    """Feed an absurd pitch; smoothed _pitch never exceeds the clamp (+eps)."""
    cam = Camera()
    eps = 1e-6
    for _ in range(100):
        cam.update(heading_rad=0.0, pitch_rad=10.0, pos=ORIGIN, dt=DT)
        assert cam._pitch <= PITCH_CLAMP_RAD + eps
        assert cam._pitch >= -PITCH_CLAMP_RAD - eps
    assert cam._pitch > PITCH_CLAMP_RAD - 1e-3


def test_heading_converges():
    """Constant heading target; after ~1s _yaw is within 1e-3 of target."""
    cam = Camera()
    target = 0.8
    cam.update(heading_rad=0.0, pitch_rad=0.0, pos=ORIGIN, dt=DT)
    for _ in range(60):
        cam.update(heading_rad=target, pitch_rad=0.0, pos=ORIGIN, dt=DT)
    assert abs(cam._yaw - target) < 1e-3


def test_no_overshoot():
    """Step heading 0 -> 1.0; _yaw is monotonic and never exceeds the target."""
    cam = Camera()
    target = 1.0
    cam.update(heading_rad=0.0, pitch_rad=0.0, pos=ORIGIN, dt=DT)
    prev = cam._yaw
    for _ in range(240):
        cam.update(heading_rad=target, pitch_rad=0.0, pos=ORIGIN, dt=DT)
        assert cam._yaw >= prev - 1e-9
        assert cam._yaw <= target + 1e-9
        prev = cam._yaw
    assert abs(cam._yaw - target) < 1e-3


def test_yaw_shortest_arc():
    """From _yaw ~= -3.0 toward target 3.0: travel through +/-pi, not the long way."""
    cam = Camera()
    cam.update(heading_rad=-3.0, pitch_rad=0.0, pos=ORIGIN, dt=DT)
    assert abs(cam._yaw - (-3.0)) < 1e-12

    cam.update(heading_rad=3.0, pitch_rad=0.0, pos=ORIGIN, dt=DT)
    assert cam._yaw < -3.0

    for _ in range(240):
        cam.update(heading_rad=3.0, pitch_rad=0.0, pos=ORIGIN, dt=DT)
    assert abs(cam._yaw - (3.0 - 2.0 * pi)) < 1e-3


def test_forward_compass():
    """FROZEN COMPASS: yaw=0 -> +X (east); yaw=pi/2 -> +Z (north)."""
    f0 = forward_from_angles(yaw=0.0, pitch=0.0)
    assert np.allclose(f0, np.array([1.0, 0.0, 0.0], dtype=np.float32), atol=1e-6)

    f1 = forward_from_angles(yaw=pi / 2.0, pitch=0.0)
    assert np.allclose(f1, np.array([0.0, 0.0, 1.0], dtype=np.float32), atol=1e-6)


def test_matrix_shape_dtype():
    """update() returns ndarray shape (4,4) dtype float32."""
    cam = Camera()
    m = cam.update(heading_rad=0.3, pitch_rad=0.1, pos=(1.0, 2.0, 3.0), dt=DT)
    assert isinstance(m, np.ndarray)
    assert m.shape == (4, 4)
    assert m.dtype == np.float32


def test_deterministic():
    """Same input sequence from fresh Cameras -> identical matrices."""
    headings = [0.0, 0.5, 0.5, 1.0, -0.7, 2.5, 2.5]
    pitches = [0.0, 0.2, -0.3, 0.1, 0.4, -10.0, 0.0]
    positions = [(float(i), float(i) * 0.5, float(i) * -0.25) for i in range(7)]

    def run() -> list:
        cam = Camera()
        out = []
        for h, p, pos in zip(headings, pitches, positions):
            out.append(cam.update(heading_rad=h, pitch_rad=p, pos=pos, dt=DT))
        return out

    a = run()
    b = run()
    for ma, mb in zip(a, b):
        assert np.array_equal(ma, mb)
