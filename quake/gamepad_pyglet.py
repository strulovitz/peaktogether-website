"""Controller shell for Quake (Parent 23).

pyglet-native reading of two controllers, ADDITIVE with keyboard/mouse:
  - Thrustmaster T.16000M (DirectInput Joystick) -> MOVER  (mirrors/extends keyboard; NO pitch)
  - Xbox 360 (XInput Controller)                 -> mirrors the MOUSE (Mover-look + Shooter-reticle + fire)

Behavior ported from Descent's known-good gamepad.py:
  - 60-frame startup rest calibration (sticks + twist only; NOT the throttle slider)
  - radial deadzone 0.12 for 2D sticks, scalar deadzone 0.08 for twist/slider
  - signed trigger test (> 0.5), never abs() -- no auto-fire
  - everything lazy-imported + try/except guarded; absence/failure -> None manager (no regression)

The pure core of input_actions.py is untouched. This module only produces a small additive
contribution that _read_raw_sample folds into the RawSample.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# --- tuning constants (feel; Nir tunes) --------------------------------------
CALIB_FRAMES = 60
STICK_DZ_RADIAL = 0.12
SCALAR_DZ = 0.08
SLIDER_DZ = 0.10        # deadzone around the throttle's absolute center 0
SLIDER_GAIN = 1.5       # slider contribution into move_y (pre-clamp); >1 so full slider saturates
TRIGGER_TH = 0.5        # signed trigger fire threshold


@dataclass
class GamepadContribution:
    """Additive deltas to fold into RawSample. All zero when nothing is touched."""
    move_x: float = 0.0
    move_y: float = 0.0
    yaw_rate: float = 0.0
    pitch_rate: float = 0.0
    aim_x: float = 0.0
    aim_y: float = 0.0
    fire_down: bool = False


def _clamp1(v: float) -> float:
    return max(-1.0, min(1.0, v))


def _scalar_deadzone(v: float, dz: float = SCALAR_DZ) -> float:
    if abs(v) < dz:
        return 0.0
    sign = 1.0 if v > 0 else -1.0
    return sign * (abs(v) - dz) / (1.0 - dz)


def _radial_deadzone(x: float, y: float, dz: float = STICK_DZ_RADIAL) -> tuple[float, float]:
    mag = math.sqrt(x * x + y * y)
    if mag < dz:
        return 0.0, 0.0
    scale = ((mag - dz) / (1.0 - dz)) / mag
    return x * scale, y * scale


class _Calib:
    """Per-device rest calibration over CALIB_FRAMES. Captures rest for named axes only.

    The throttle slider is deliberately EXCLUDED (its absolute center 0 is neutral; subtracting
    a captured rest would break it)."""

    def __init__(self, axis_names: tuple[str, ...]):
        self._names = axis_names
        self._sum = {n: 0.0 for n in axis_names}
        self._frames = 0
        self._done = False
        self._rest = {n: 0.0 for n in axis_names}

    def feed(self, values: dict) -> bool:
        """Accumulate one frame of raw readings. Returns True once calibration is done."""
        if self._done:
            return True
        for n in self._names:
            self._sum[n] += float(values.get(n, 0.0))
        self._frames += 1
        if self._frames >= CALIB_FRAMES:
            for n in self._names:
                self._rest[n] = self._sum[n] / CALIB_FRAMES
            self._done = True
        return self._done

    @property
    def done(self) -> bool:
        return self._done

    def rest(self, name: str) -> float:
        return self._rest.get(name, 0.0)


class GamepadManager:
    """Owns the opened pyglet devices and produces an additive GamepadContribution each frame.

    Constructed via make_gamepad_manager(window). If no devices / any error -> returns None there,
    so callers pass gamepad=None and the game runs on keyboard+mouse exactly as before.
    """

    def __init__(self, joystick=None, controller=None):
        self._joy = joystick          # T.16000M (or None)
        self._ctrl = controller       # Xbox (or None)
        # calibrate sticks/twist only; slider ('z') excluded on purpose
        self._joy_calib = _Calib(("x", "y", "rz"))
        self._ctrl_calib = _Calib(("rightx", "righty"))

    # -- reading helpers (guarded; pyglet attrs are plain floats) --------------
    @staticmethod
    def _get(obj, name: str) -> float:
        try:
            return float(getattr(obj, name, 0.0) or 0.0)
        except Exception:
            return 0.0

    @staticmethod
    def _getb(obj, name: str) -> bool:
        try:
            return bool(getattr(obj, name, False))
        except Exception:
            return False

    def pump(self) -> None:
        """Service the controller devices each frame BEFORE read().

        A pyglet manual-loop game (no pyglet.app.run()) must pump device input itself;
        window.dispatch_events() does NOT do it. Both calls below are non-blocking and never
        touch the window message queue (so keyboard/mouse are unaffected):
          - XInput (Xbox): its background thread posts state -> dispatch_posted_events() delivers it.
          - DirectInput (joystick): drain the device's buffered data directly (non-blocking).
        """
        # XInput (Xbox): deliver thread-posted controller state to the main thread.
        try:
            import pyglet
            pyglet.app.platform_event_loop.dispatch_posted_events()
        except Exception:
            pass
        # DirectInput (T.16000M): drain the device buffer directly (non-blocking, no msg pump).
        if self._joy is not None:
            try:
                dev = getattr(self._joy, "device", None)
                disp = getattr(dev, "_dispatch_events", None)
                if disp is not None:
                    disp()
            except Exception:
                pass

    def read(self) -> GamepadContribution:
        c = GamepadContribution()

        # --- T.16000M -> MOVER (no pitch) ---
        if self._joy is not None:
            raw = {
                "x": self._get(self._joy, "x"),
                "y": self._get(self._joy, "y"),
                "rz": self._get(self._joy, "rz"),
                "z": self._get(self._joy, "z"),   # throttle slider (NOT calibrated)
            }
            if self._joy_calib.feed(raw):
                jx = _clamp1(raw["x"] - self._joy_calib.rest("x"))
                jy = _clamp1(raw["y"] - self._joy_calib.rest("y"))
                jx, jy = _radial_deadzone(jx, jy)
                c.move_x += jx
                c.move_y += -jy                    # push forward = -y = forward(+)
                twist = _clamp1(raw["rz"] - self._joy_calib.rest("rz"))
                c.yaw_rate += _scalar_deadzone(twist)
                # throttle slider: absolute center-0, NOT calibrated, deadzone then gain into move_y
                slider = _scalar_deadzone(_clamp1(raw["z"]), SLIDER_DZ)
                c.move_y += slider * SLIDER_GAIN   # pre-clamp; build_actions clamps to [-1,1]

        # --- Xbox -> mirrors the MOUSE (Mover-look + Shooter-reticle + fire) ---
        if self._ctrl is not None:
            raw = {
                "rightx": self._get(self._ctrl, "rightx"),
                "righty": self._get(self._ctrl, "righty"),
            }
            if self._ctrl_calib.feed(raw):
                rx = _clamp1(raw["rightx"] - self._ctrl_calib.rest("rightx"))
                ry = _clamp1(raw["righty"] - self._ctrl_calib.rest("righty"))
                rx, ry = _radial_deadzone(rx, ry)
                # right stick drives BOTH the mover look-rates AND the shooter reticle,
                # exactly as the single mouse does today (§3.2 / UPDATE #2).
                c.yaw_rate += rx
                c.pitch_rate += -ry        # up on stick (negative) -> look up (positive rate)
                c.aim_x += rx
                c.aim_y += -ry             # aim_y positive = look UP
            # fire: signed trigger test (> 0.5) OR the A button; never abs()
            rt = self._get(self._ctrl, "righttrigger")   # rest 0.0 -> +1.0
            a_btn = self._getb(self._ctrl, "a")
            if rt > TRIGGER_TH or a_btn:
                c.fire_down = True

        return c


def make_gamepad_manager(window):
    """Open the T.16000M (joystick) and Xbox (controller) via pyglet, guarded.

    Returns a GamepadManager, or None if no devices / any failure -> keyboard+mouse only.
    Lazy-imports pyglet.input so the module stays import-safe headless.
    """
    joystick = None
    controller = None
    try:
        import pyglet  # noqa: F401
        from pyglet import input as pyglet_input
    except Exception:
        return None

    # --- T.16000M via get_joysticks() (DirectInput; needs window) ---
    try:
        joys = pyglet_input.get_joysticks()
        for j in joys:
            name = getattr(j, "device", None)
            dev_name = getattr(name, "name", "") if name is not None else ""
            if "T.16000" in dev_name or "Thrustmaster" in dev_name:
                try:
                    j.open(window=window)
                    joystick = j
                    break
                except Exception:
                    joystick = None
        # fallback: if exactly one joystick and none matched by name, take it
        if joystick is None and len(joys) == 1:
            try:
                joys[0].open(window=window)
                joystick = joys[0]
            except Exception:
                joystick = None
    except Exception:
        joystick = None

    # --- Xbox via get_controllers() (XInput; standardized) ---
    try:
        ctrls = pyglet_input.get_controllers()
        if ctrls:
            try:
                ctrls[0].open()
                controller = ctrls[0]
            except Exception:
                controller = None
    except Exception:
        controller = None

    if joystick is None and controller is None:
        return None
    return GamepadManager(joystick=joystick, controller=controller)
