"""gamepad.py -- Brief #11: Xbox 360 controller support for Understanding Mode.
Verbatim GamepadManager from the working Bible code, with added right-stick method."""

import math
import numpy as np
import pygame


class GamepadManager:
    """Full gamepad support: T.16000M -> PILOT, Xbox 360 -> MANIPULATOR.
    Deadzones: radial for 2D sticks (0.12), scalar for twist/throttle (0.08)."""

    CALIB_FRAMES    = 60
    STICK_DZ_RADIAL = 0.12
    SCALAR_DZ       = 0.08

    # T.16000M FCS axis mapping (verified on Nir's hardware via Anniversary project)
    AXIS_ROLL     = 0   # stick X
    AXIS_PITCH    = 1   # stick Y (forward push = axis negative = dive)
    AXIS_YAW      = 2   # stick Z twist
    AXIS_THROTTLE = 3   # throttle slider

    # Xbox right-stick axis indices (SDL2 common mapping -- verify with
    # the runtime axis-picker: wiggle right stick, read live values)
    XBOX_RSTICK_X = 3
    XBOX_RSTICK_Y = 4

    def __init__(self):
        pygame.joystick.init()
        self.pilot_joy = None
        self.manip_joy = None
        # Calibration state per joystick instance_id
        self._calib_sum    = {}
        self._calib_frames = {}
        self._calib_done   = {}
        self._calib_rest   = {}
        self._slider_idx = 0
        self._slider_switch_cooldown = 0.0
        self._detect()

    # ------------------------------------------------------- detection ---
    def _detect(self):
        """Assign connected devices: T.16000M -> pilot, Xbox gamepad -> manipulator."""
        count = pygame.joystick.get_count()
        for i in range(count):
            joy = pygame.joystick.Joystick(i)
            name = joy.get_name()
            is_t16  = "T.16000" in name or "Thrustmaster" in name
            is_xbox = "Xbox" in name or "360" in name or "XInput" in name

            if is_t16 and self.pilot_joy is None:
                joy.init()
                self.pilot_joy = joy
                self._start_calibration(joy)
                print("[gamepad] PILOT: %s (axes=%d, buttons=%d, hats=%d)" % (
                    name, joy.get_numaxes(), joy.get_numbuttons(), joy.get_numhats()))
            elif is_xbox and self.manip_joy is None:
                joy.init()
                self.manip_joy = joy
                self._start_calibration(joy)
                print("[gamepad] MANIPULATOR: %s (axes=%d, buttons=%d, hats=%d)" % (
                    name, joy.get_numaxes(), joy.get_numbuttons(), joy.get_numhats()))

    def _start_calibration(self, joy):
        jid = joy.get_instance_id()
        n = joy.get_numaxes()
        self._calib_sum[jid]    = np.zeros(n)
        self._calib_frames[jid] = 0
        self._calib_done[jid]   = False
        self._calib_rest[jid]   = np.zeros(n)

    # ---------------------------------------------------- deadzones ---
    @staticmethod
    def _clamp1(v):
        return max(-1.0, min(1.0, v))

    def _scalar_deadzone(self, v):
        if abs(v) < self.SCALAR_DZ:
            return 0.0
        sign = 1.0 if v > 0 else -1.0
        return sign * (abs(v) - self.SCALAR_DZ) / (1.0 - self.SCALAR_DZ)

    def _radial_deadzone(self, x, y):
        mag = math.sqrt(x * x + y * y)
        if mag < self.STICK_DZ_RADIAL:
            return 0.0, 0.0
        scale = ((mag - self.STICK_DZ_RADIAL) / (1.0 - self.STICK_DZ_RADIAL)) / mag
        return x * scale, y * scale

    # ------------------------------------------------- calibration ---
    def _calibrate(self, joy):
        """Run one calibration frame. Returns calibrated axes array or None if still calibrating."""
        jid = joy.get_instance_id()
        if self._calib_done.get(jid, False):
            rest = self._calib_rest[jid]
            return np.array([joy.get_axis(i) - rest[i] for i in range(joy.get_numaxes())])

        # Sample rest values during startup
        if jid in self._calib_sum:
            n = min(joy.get_numaxes(), len(self._calib_sum[jid]))
            for i in range(n):
                self._calib_sum[jid][i] += joy.get_axis(i)
            self._calib_frames[jid] += 1
            if self._calib_frames[jid] >= self.CALIB_FRAMES:
                self._calib_rest[jid] = self._calib_sum[jid] / self.CALIB_FRAMES
                self._calib_done[jid] = True
                rest_str = " ".join("a%d=%+.2f" % (i, self._calib_rest[jid][i])
                                   for i in range(n))
                print("[gamepad] %s calibrated: %s" % (joy.get_name(), rest_str))
        return None

    # -------------------------------------------------- pilot input ---
    def pilot_command(self):
        """Returns dict {pitch, yaw, roll, thrust_xyz} in -1..+1, or None if no pilot device.
        App.update() must ADD these to keyboard values (simultaneous use)."""
        joy = self.pilot_joy
        if joy is None:
            return None

        cal = self._calibrate(joy)
        if cal is None:
            return None  # still calibrating

        n = joy.get_numaxes()
        roll = pitch = yaw = 0.0
        thrust_xyz = [0.0, 0.0, 0.0]

        if n > max(self.AXIS_ROLL, self.AXIS_PITCH):
            sx = self._clamp1(cal[self.AXIS_ROLL])
            sy = self._clamp1(cal[self.AXIS_PITCH])
            sx, sy = self._radial_deadzone(sx, sy)
            roll  = sx
            pitch = sy

        if n > self.AXIS_YAW:
            yaw = self._scalar_deadzone(self._clamp1(cal[self.AXIS_YAW]))

        if n > self.AXIS_THROTTLE:
            t = self._scalar_deadzone(self._clamp1(cal[self.AXIS_THROTTLE]))
            thrust_xyz[2] = -t

        if joy.get_numhats() >= 1:
            hx, hy = joy.get_hat(0)
            thrust_xyz[0] += float(hx)
            thrust_xyz[1] += float(hy)

        thrust_xyz = [self._clamp1(v) for v in thrust_xyz]
        return {'pitch': pitch, 'yaw': yaw, 'roll': roll, 'thrust_xyz': tuple(thrust_xyz)}

    # ---------------------------------------------- manipulator input ---
    def manipulator_update(self, sliders, dt):
        """Xbox D-pad/L-stick selects slider, L-stick X nudges value.
        Works simultaneously with mouse slider dragging."""
        joy = self.manip_joy
        if joy is None or not sliders:
            return

        self._slider_switch_cooldown = max(0.0, self._slider_switch_cooldown - dt)
        if self._slider_switch_cooldown <= 0.0:
            if joy.get_numhats() >= 1:
                hx, hy = joy.get_hat(0)
                if hy != 0:
                    self._slider_idx = (self._slider_idx - hy) % len(sliders)
                    self._slider_switch_cooldown = 0.25
            if joy.get_numaxes() >= 2:
                ly = joy.get_axis(1)
                if abs(ly) > 0.6:
                    self._slider_idx = (self._slider_idx + (1 if ly > 0 else -1)) % len(sliders)
                    self._slider_switch_cooldown = 0.25

        if 0 <= self._slider_idx < len(sliders) and joy.get_numaxes() >= 1:
            lx = joy.get_axis(0)
            if abs(lx) > 0.15:
                sliders[self._slider_idx].nudge(lx * dt * 0.5)

    # ---- Brief #11: right-stick for Understanding Mode panning ----
    def manipulator_right_stick(self):
        """Returns (rx, ry) calibrated + radial-deadzoned from Xbox right stick,
        or (0.0, 0.0) if no manipulator connected or still calibrating."""
        joy = self.manip_joy
        if joy is None:
            return (0.0, 0.0)

        cal = self._calibrate(joy)
        if cal is None:
            return (0.0, 0.0)  # still calibrating

        n = joy.get_numaxes()
        if n <= max(self.XBOX_RSTICK_X, self.XBOX_RSTICK_Y):
            return (0.0, 0.0)

        rx = self._clamp1(cal[self.XBOX_RSTICK_X])
        ry = self._clamp1(cal[self.XBOX_RSTICK_Y])
        rx, ry = self._radial_deadzone(rx, ry)
        return (rx, ry)
