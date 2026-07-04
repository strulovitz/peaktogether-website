# QUAKE PARENT 23 — FROZEN DELIVERABLE (VERBATIM)

> Saved word-for-word as delivered by Claude Opus 4.8 (Parent 23). Mission: add joystick +
> Xbox controller support to Quake (pyglet-native / Option A). Integrated by DeepSeek.

---

Understood. One important detail from your answer #2 that I'm baking in: the throttle slider z must NOT be rest-calibrated — its absolute center-0 is the neutral, so if I subtracted a captured "rest" it would break. Everything else (sticks, twist) gets the 60-frame rest-capture; the slider is read raw with only a deadzone. My calibration code will explicitly exclude the slider axis from the rest-capture subtraction.

## Final mapping (confirmed)

Joystick T.16000M — MOVER, no pitch:

    x → move_x (strafe) — rest-calibrated, radial deadzone with y
    y → move_y (forward = -y) — rest-calibrated, radial deadzone with x
    rz twist → mover_yaw_rate — rest-calibrated, scalar deadzone 0.08
    z throttle slider → adds to move_y as a speed throttle — NOT rest-calibrated, scalar deadzone around absolute center 0, scaled so full deflection is clearly faster than walk
    hat, buttons → nothing

Xbox — mirrors the mouse (girlfriend: Mover-look + Shooter-reticle + fire):

    right stick X → mover_yaw_rate += rightx and shooter_aim_x += rightx
    right stick Y → mover_pitch_rate += -righty and shooter_aim_y += -righty
    right trigger > 0.5 OR A → shooter_fire_down
    all rest-calibrated + radial deadzone 0.12

Slider-to-move_y honesty note: move_y is clamped to [-1,1] in build_actions, and gameplay multiplies it by WALK_SPEED_M_S. So the slider can't make you go faster than walk speed through move_y alone if it's clamped at 1.0. To make the slider genuinely faster for crossing big rooms, I add a separate move_y_boost that gets applied as an extra forward push — but since I must not touch the pure core or the Actions contract, I instead scale the slider's contribution and let it ride within the clamp, plus overdrive move_y before the clamp so full stick+slider still saturates at the fast end. Given the clamp, the cleanest honest approach: the slider contributes up to SLIDER_GAIN (e.g. 1.5) into move_y before build_actions clamps to [-1,1]. That means slider-alone gives full-speed walk (clamped to 1.0) — not faster than walk.

I have to be honest: with the frozen [-1,1] clamp and fixed WALK_SPEED_M_S, I cannot exceed walk speed without touching the core or gameplay. So I'm flagging this: the slider will give easy, hands-free full-speed forward/back (which does help cross rooms without holding W), but "clearly faster than normal walk" requires either (a) raising WALK_SPEED_M_S, or (b) a new sprint field in the core. Both touch frozen code. My code below implements the honest version (slider = hands-free full-speed throttle, clamped to walk speed) and I flag the tradeoff for you to decide. If you want true faster-than-walk, tell me and I'll propose the minimal core change (a sprint multiplier) separately.

Here's the full code.

## quake/gamepad_pyglet.py (new file)

```python
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
```

## quake/input_actions.py — replace _read_raw_sample and poll

Full drop-in replacements (both gain a gamepad=None default; the rest of the file is untouched):

```python
def _read_raw_sample(window, bindings, gamepad=None) -> RawSample:
    mover = bindings.get("mover", {})
    shooter = bindings.get("shooter", {})
    shared = bindings.get("shared", {})

    # --- mover movement axes (keyboard default) ---
    ax = mover.get("axis_x", ["a", "d"])
    ay = mover.get("axis_y", ["w", "s"])
    mover_axis_x = _axis_pair(window, ax[0], ax[1])
    fwd = 1.0 if _key_down(window, ay[0]) else 0.0     # W=forward(+1)
    back = 1.0 if _key_down(window, ay[1]) else 0.0    # S=back(-1)
    mover_axis_y = fwd - back

    # --- mover look rates (mouse) ---
    mdx, mdy = _mouse_delta(window)
    mover_yaw_rate = mdx if mover.get("yaw") == "mouse_dx" else 0.0
    mover_pitch_rate = mdy if mover.get("pitch") == "mouse_dy" else 0.0

    # --- shooter aim (mouse delta by default) ---
    shooter_aim_x = mdx if shooter.get("aim_x") == "mouse_dx" else 0.0
    shooter_aim_y = mdy if shooter.get("aim_y") == "mouse_dy" else 0.0
    shooter_fire_down = _mouse_left_down(window) if shooter.get("fire") == "mouse_left" else False

    # --- controllers (ADDITIVE on top of keyboard/mouse; Parent 23) ---
    if gamepad is not None:
        try:
            g = gamepad.read()
            mover_axis_x += g.move_x
            mover_axis_y += g.move_y
            mover_yaw_rate += g.yaw_rate
            mover_pitch_rate += g.pitch_rate
            shooter_aim_x += g.aim_x
            shooter_aim_y += g.aim_y
            shooter_fire_down = shooter_fire_down or g.fire_down
        except Exception:
            pass  # any controller hiccup -> keyboard/mouse only, no crash

    # --- shared buttons (level down-state) ---
    read_down = _key_down(window, shared.get("read", "r"))
    interact_down = _key_down(window, shared.get("interact", "e"))
    pause_down = _key_down(window, shared.get("pause", "escape"))

    return RawSample(
        mover_axis_x=mover_axis_x, mover_axis_y=mover_axis_y,
        mover_yaw_rate=mover_yaw_rate, mover_pitch_rate=mover_pitch_rate,
        shooter_aim_x=shooter_aim_x, shooter_aim_y=shooter_aim_y,
        shooter_fire_down=shooter_fire_down,
        read_down=read_down, interact_down=interact_down, pause_down=pause_down,
    )


def poll(window, bindings, gamepad=None) -> Actions:
    global _SHELL_TRACKER, _SHELL_LAST_TIME
    if _SHELL_TRACKER is None:
        _SHELL_TRACKER = EdgeTracker()
    now = _now()
    if _SHELL_LAST_TIME is None:
        dt = _DEFAULT_DT
    else:
        dt = max(0.0, now - _SHELL_LAST_TIME)
    _SHELL_LAST_TIME = now
    if bindings is None:
        bindings = DEFAULT_BINDINGS
    sample = _read_raw_sample(window, bindings, gamepad)
    return build_actions(sample, _SHELL_TRACKER, dt, DEFAULT_YAW_SENS, DEFAULT_PITCH_SENS)
```

## quake/app.py — two edits

Edit 1 — construct the manager once, right after the window is created (~line 304, just after the make_window unpack):

```python
    window, ctx = _unpack_window(make_window(WINDOW_W, WINDOW_H, WINDOW_TITLE))
    # --- controllers (Parent 23): open once; None if no devices -> keyboard+mouse only ---
    try:
        from gamepad_pyglet import make_gamepad_manager
        gamepad = make_gamepad_manager(window)
    except Exception as e:
        _log(f"gamepad init skipped: {e}")
        gamepad = None
```

Edit 2 — thread it into the per-frame poll (~line 395):

```python
    # (1) input
    try:
        actions = poll(window, bindings, gamepad)
    except Exception as e:
        _log(f"frame {frame}: poll() crashed: {e}")
        raise
```

(If app.py uses from input_actions import poll — which it does — no import change is needed; poll just takes the extra positional arg. Match the from gamepad_pyglet import ... style to however app.py imports its siblings — if it uses from quake.gamepad_pyglet import ..., use that form. DeepSeek: please match the existing sibling-import convention.)

## Notes for DeepSeek / Nir (honest)

    Zero regression: gamepad=None everywhere by default; the 468 headless tests never build a window and never pass a gamepad, so the pure core and all tests are untouched. pyglet.input is lazy-imported and fully try/except-guarded.
    The slider caveat (please read): as written, the throttle gives hands-free full-speed forward/back but, because move_y is clamped to [-1,1] and WALK_SPEED_M_S is fixed in the frozen core, it cannot exceed normal walk speed. If Nir wants the slider to be genuinely faster for crossing big rooms, that needs a small core change (a sprint multiplier applied in gameplay.py) — I did not make it, because it touches frozen code. Tell me and I'll propose that minimal change separately for approval.
    Two things only Nir's hands can confirm: (1) twist→yaw and stick sensitivity feel (tune DEFAULT_YAW_SENS / the raw stick scale); (2) the Y-inversion signs on the Xbox stick and joystick forward — if any axis feels backwards in-game, it's a single sign flip. I flagged each inversion inline.

Ready for the play-test. If the slider needs true sprint, say the word and I'll write the core-change proposal. 🎮
