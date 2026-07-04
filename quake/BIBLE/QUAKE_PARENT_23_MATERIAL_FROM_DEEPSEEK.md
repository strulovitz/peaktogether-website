# QUAKE PARENT 23 — MATERIAL FROM DEEPSEEK (answers to your batched questions)

All confirmed on Nir's actual hardware this session. Verbatim code + live probe results.
**Bottom line up front: pyglet reads BOTH controllers perfectly (Option A confirmed).** The
Xbox arrives as a standardized XInput `Controller` with triggers that **rest at 0.0 and pull to
+1.0** — the -1.0 auto-fire trap does NOT exist in pyglet. Use a signed `> 0.5` test anyway.

---

## ANSWER #1 — `quake/input_actions.py` (verbatim: shell, helpers, module state, bindings)

Module imports at top are only `dataclass` + `from contracts import Actions`. **`pyglet` is
imported LAZILY inside `_key_down`** (not at module top), so the module is import-safe headless.

```python
DEFAULT_YAW_SENS = 2.2     # rad/s per unit input
DEFAULT_PITCH_SENS = 1.8
_DEFAULT_DT = 0.016        # ~60fps safe default for the first poll()

DEFAULT_BINDINGS = {
    "mover": {
        "device": "keyboard",
        "axis_x": ["a", "d"],        # A=left(-1), D=right(+1)
        "axis_y": ["w", "s"],        # W=forward(+1), S=back(-1)
        "yaw": "mouse_dx",
        "pitch": "mouse_dy",
    },
    "shooter": {
        "device": "mouse",
        "aim_x": "mouse_dx",
        "aim_y": "mouse_dy",
        "fire": "mouse_left",
    },
    "shared": {
        "read": "r", "interact": "e", "pause": "escape", "ceiling": "c",
    },
}

# Module-owned shell state (tests never touch these):
_SHELL_TRACKER: EdgeTracker | None = None
_SHELL_LAST_TIME: float | None = None

def _now() -> float:
    import time
    return time.perf_counter()

def _key_down(window, key_name: str) -> bool:
    """Is the named key currently held down? (pyglet 2.1.14 KeyStateHandler broken on Windows)"""
    try:
        import pyglet
        pressed = getattr(window, "_quake_keystate", None)
        if pressed is None:
            return False
        symbol = getattr(pyglet.window.key, key_name.upper(), None)
        if symbol is None:
            return False
        return symbol in pressed
    except Exception:
        return False

def _mouse_delta(window) -> tuple[float, float]:
    """Accumulated mouse (dx,dy) since last poll, then reset (window._quake_mousedx())."""
    try:
        fn = getattr(window, "_quake_mousedx", None)
        if fn is None:
            return (0.0, 0.0)
        return fn()
    except Exception:
        return (0.0, 0.0)

def _mouse_left_down(window) -> bool:
    try:
        fn = getattr(window, "_quake_mouseleft", None)
        if fn is None:
            return False
        return bool(fn())
    except Exception:
        return False

def _axis_pair(window, neg_key: str, pos_key: str) -> float:
    neg = 1.0 if _key_down(window, neg_key) else 0.0
    pos = 1.0 if _key_down(window, pos_key) else 0.0
    return pos - neg

def _read_raw_sample(window, bindings) -> RawSample:
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

def poll(window, bindings) -> Actions:
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
    sample = _read_raw_sample(window, bindings)
    return build_actions(sample, _SHELL_TRACKER, dt, DEFAULT_YAW_SENS, DEFAULT_PITCH_SENS)
```

Note the current `dt`: `build_actions` computes `heading_delta = mover_yaw_rate * DEFAULT_YAW_SENS
* dt` and `pitch_delta = mover_pitch_rate * DEFAULT_PITCH_SENS * dt`. So feeding a held analog
axis (e.g. twist in [-1,1]) into `mover_yaw_rate` gives a smooth rate-based turn. Feeding the
absolute stick into `mover_axis_x/y` and `shooter_aim_x/y` is direct [-1,1] (clamped in
`build_actions`).

---

## ANSWER #2 — `quake/app.py` frame-loop input section + window creation/hold (verbatim)

Window is created once and held in local `window`:
```python
# ~line 303, inside main():
window, ctx = _unpack_window(make_window(WINDOW_W, WINDOW_H, WINDOW_TITLE))
```
The frame loop calls `poll` once per frame:
```python
# ~lines 393-403, inside the `while True:` loop:
# (1) input
try:
    actions = poll(window, bindings)          # <-- bindings is `None` today -> DEFAULT_BINDINGS
except Exception as e:
    _log(f"frame {frame}: poll() crashed: {e}")
    raise
# (2) graceful-exit request (non-smoke): semantic pause -> quit
if not smoke and getattr(actions, "pause", False):
    break
```
`bindings` is set to `None` at ~line 352 (so `poll` uses `DEFAULT_BINDINGS`). Events/present each
frame (from `_window_present`, called near end of loop ~line 541):
```python
def _window_present(window) -> None:
    if hasattr(window, "dispatch_events"):
        window.dispatch_events()     # <-- pumps pyglet input every frame (incl. opened devices)
    if hasattr(window, "flip"):
        window.flip()
```
**Recommended wiring:** construct the controller manager ONCE right after the window is created
(~line 304), e.g. `gamepad = make_gamepad_manager(window)` (returns `None` if no devices / any
error), then pass it in: change the call to `poll(window, bindings, gamepad)`. Give `poll` and
`_read_raw_sample` a `gamepad=None` default so every existing caller/test still works unchanged.

The window is a pyglet `Window` created in `gfx_context.py` with `set_exclusive_mouse(True)` and
custom attrs `window._quake_keystate` / `._quake_mousedx()` / `._quake_mouseleft()`.

---

## ANSWER #3 — LIVE PROBE: T.16000M via `pyglet.input.get_joysticks()[0].open(window=win)`

Confirmed present and delivering. Mapped Joystick attributes (min..max observed as Nir moved
each control), plus the raw device controls (the ACTUAL names pyglet exposes):

```
Mapped attrs (range over run):
  x     : -1.000 .. +1.000     <- stick LEFT/RIGHT   (rest 0)   [normalized -1..1]
  y     : -1.000 .. +1.000     <- stick FORWARD/BACK (rest 0)   [normalized -1..1]
  z     : -1.000 .. +0.000     <- THROTTLE SLIDER (raw name 'Slider'); Nir only moved it partway
  rz    : -1.000 .. +1.000     <- TWIST  (raw name 'Z Rotation', rest 0)  [normalized -1..1]
  rx    :  0.000 ..  0.000     <- unused
  ry    :  0.000 ..  0.000     <- unused
  hat_x :  0.000 ..  0.000     <- HAT not tested this run (Nir didn't push it); see note
  hat_y :  0.000 ..  0.000     <- HAT not tested this run
  buttons pressed: [0, 1]      <- button index 0 = the index-finger TRIGGER

Raw device controls (pyglet Joystick.device.get_controls()):
  name='x'   raw_name='X Axis'      AbsoluteAxis
  name='y'   raw_name='Y Axis'      AbsoluteAxis
  name='z'   raw_name='Slider'      AbsoluteAxis   (throttle)
  name='rz'  raw_name='Z Rotation'  AbsoluteAxis   (twist)
  name='hat' raw_name='Hat Switch'  AbsoluteAxis   (value None at rest -> pyglet maps to hat_x/hat_y)
  Buttons 0..15 (16 buttons)        Button
```
So pyglet's mapped attribute names for the T.16000M are exactly: **`x`, `y`, `z` (throttle),
`rz` (twist), `hat_x`/`hat_y` (hat), and `buttons[0..15]`.** Axes are normalized to [-1, 1] with
rest ≈ 0 for the sticks/twist. **NOT tested this run: the hat (hat_x/hat_y) and full slider
range.** If you want to use the hat for pitch, DeepSeek can run a 20-second hat-only + slider-only
probe to confirm hat_x/hat_y take -1/0/+1 and the slider's rest value — just ask.

---

## ANSWER #4 — LIVE PROBE: Xbox via `pyglet.input.get_controllers()[0].open()`

Confirmed present and delivering as a standardized XInput `Controller` (name `XInput0`):
```
  leftx        : -1.000 .. +1.000   (rest 0)
  lefty        : -1.000 .. +1.000   (rest 0)
  rightx       : -1.000 .. +1.000   (rest 0)
  righty       : -1.000 .. +1.000   (rest 0)
  lefttrigger  :  0.000 .. +1.000   (REST 0.0, full pull +1.0)   <- clean, no -1 trap
  righttrigger :  0.000 .. +1.000   (REST 0.0, full pull +1.0)   <- clean, no -1 trap
  buttons seen : a, b, x, y, leftshoulder, rightshoulder
```
Attribute names confirmed present: `leftx, lefty, rightx, righty, lefttrigger, righttrigger`,
and boolean buttons `a, b, x, y, leftshoulder, rightshoulder` (also available in pyglet's
Controller API: `start, back, leftstick, rightstick, dpup, dpdown, dpleft, dpright, guide`).
**Trigger convention: rest 0.0 → +1.0 (no negative resting state)** — use `> 0.5`.
**Stick Y up/down sign was NOT isolated this run** (both showed full ±1 range). pyglet's Controller
convention is standard SDL: pushing a stick **up yields a NEGATIVE y**. So for `aim_y` (where
positive = look UP per gameplay), invert: `aim_y_from_stick = -righty`. Nir confirms by feel; if
it's backwards in-game, flip the sign.

---

## ANSWER #5 — `.open()` requirements + side-effects

- **Joystick:** must call `joystick.open(window=win)` before reading attributes. (Confirmed.)
- **Controller:** call `controller.open()` (no window arg needed). (Confirmed.)
- **Side-effects:** In the probe, opening both devices against a pyglet window with default
  handlers did **NOT** interfere with anything — device event streams are separate from the
  window's keyboard/mouse handlers. Opening them is expected to be **side-effect-free** with
  respect to `set_exclusive_mouse(True)` and Quake's existing `_quake_keystate`/mouse helpers
  (they are independent input paths; the exclusive-mouse setting affects only the mouse pointer).
  Recommend wrapping `get_joysticks()/get_controllers()/open()` in try/except and returning a
  "no controller" manager on any failure, so a device hiccup never breaks keyboard/mouse.
- Devices are pumped by the existing per-frame `window.dispatch_events()` — no new event loop.

---

## ANSWER #6 — headless / test-path safety

- **`input_actions.py` imports `pyglet` LAZILY** (inside `_key_down`), never at module top. Keep
  the same discipline for controller code: import `pyglet.input` lazily inside the manager's
  constructor/read functions, and guard with try/except.
- **`poll(...)` is never exercised headless.** `app.py`'s `main()` returns 0 immediately when
  `glguard.HAVE_GL` is False (before the window is created and before the frame loop). The 468
  tests import the pure core (`build_actions`, `RawSample`, `EdgeTracker`) and never call `poll`
  against a real window. So: put ALL controller reading in the shell (a new `quake/gamepad_pyglet.py`
  + additions to `_read_raw_sample`), keep the pure core untouched, and give `poll`/`_read_raw_sample`
  a `gamepad=None` default. Then the headless suite stays green with zero controller code running.
- The smoke test drives `main(smoke_frames=N)` with `HAVE_GL` gating; if it ever runs with GL in
  CI, the manager should construct to "no controller" cleanly when no devices are present.

---

## READY FOR YOU

You have: the exact seam (`_read_raw_sample`), the exact wiring point in `app.py`, and the
confirmed pyglet attribute names + ranges + trigger convention for BOTH devices. You can now
write `quake/gamepad_pyglet.py` (Descent behavior: 60-frame calibration, radial deadzone 0.12 /
scalar 0.08, signed trigger fire, additive) + the `_read_raw_sample` extension + the one-line
`app.py` wiring, all with a `gamepad=None` default so nothing regresses.

If you want the hat_x/hat_y + slider rest confirmed before you pick the pitch source, say so and
DeepSeek runs a focused 20s probe. Otherwise, propose your final mapping and write the code. 🎮
