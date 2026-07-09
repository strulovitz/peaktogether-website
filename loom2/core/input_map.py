"""
LOOM2 -- core/input_map.py
================================================================================
Device -> Action translation (SUTRAS Part 9). The ONLY place in the game that
knows what a keyboard or a mouse is; everything downstream speaks Action.

Allowed imports: pyglet, config, core.types.
NOTE: pyglet here is WINDOW EVENTS only -- the pyglet ban (G3.7-A) is on HUD
*rendering*. Keyboard/mouse event hooks are exactly what this module is for.

Child scope: keyboard + mouse fully implemented. Joystick/Xbox slots STAY
EMPTY (DeepSeek copies proven device code from the previous games).

FROZEN BINDINGS (G4.4 -- verbatim, untouchable):
    A/D -> TOTEM_X (-1/+1)  [boyfriend]     W/S -> TOTEM_Y (+1/-1)
    mouse vertical drag -> TOTEM_Y analog   [girlfriend]
    arrows -> ORBIT_AZ/ORBIT_EL   PgUp/PgDn -> ZOOM_IN/OUT
    Home -> CAM_RESET   C -> SLICE_TOGGLE   Enter -> CONFIRM/SLICE_PLAY
    1-4 -> ANSWER_A..D   H -> HINT   Esc -> QUIT

CONVENTIONS (verified with DeepSeek, 2026-07-08 -- design truth, not guesses):
  * game_state ZEROES every axis intent at the end of each frame. Therefore
    held axes are RE-EMITTED every poll(); releasing a key simply stops the
    emission -- no explicit zero is ever needed.
  * ORBIT_AZ / ORBIT_EL carry a unitless -1..+1 multiplier; game_state scales
    (azimuth 60 deg/s, elevation 40 deg/s, x dt). Nir's locked signs:
    RIGHT arrow -> ORBIT_AZ = +1 (world appears to slide left),
    UP arrow    -> ORBIT_EL = +1 (camera rises, scene appears to drop).
  * ZOOM_IN / ZOOM_OUT are discrete: re-emitted every frame while held;
    game_state ignores the value. Zoom NEVER touches audio (SUTRAS 3.1).
  * Enter emits CONFIRM only: game_state._route_slice accepts CONFIRM as
    SLICE_PLAY, so the blade needs no key of its own. Action.SLICE_PLAY
    remains in the enum for the future gamepad mapping.
  * Esc emits Action.QUIT through the normal path (game_state sets _quit;
    main reads snapshot()["quit"]). Our on_key_press returns True, so
    pyglet's default Esc-closes-the-window behavior never fires -- the game
    always shuts down through the engine-stopping path.
  * Mouse coordinates are WINDOW pixels, origin bottom-left -- the same
    space as hud.hit_test and the config screen regions. No conversions.

FEEL (mine to shape -- the values, not the bindings):
  * Digital keys get a short ATTACK RAMP: a held axis eases 0 -> full in a
    few frames, so the totem glides into motion instead of jerking -- but
    RELEASE IS INSTANT (emission just stops), because "stop" must feel like
    control, not like ice. Direction flips ramp smoothly through zero.
  * The mouse drag is a VIRTUAL JOYSTICK anchored at the press point: a few
    pixels of deadzone swallow click jitter, then a gentle response curve
    gives fine control near the center and full speed at the edge.
================================================================================
"""
import pyglet
from pyglet.window import key, mouse
import config
from core.types import Action

# ---------------------------------------------------------------- tuning --
# All feel-constants live here, documented, in one place. None are frozen;
# DeepSeek round 2: "drag sensitivity is yours -- put it at the top."

AXIS_ATTACK_FRAMES = 6      # frames for a held key's axis to ease 0 -> 1.
                            # Small on purpose: grace, not sluggishness.
                            # (Release is instant by design -- see header.)

DRAG_FULL_PX = 160.0        # vertical drag travel (from the press anchor)
                            # for full deflection |TOTEM_Y| = 1.0. ~160 px
                            # is a comfortable virtual joystick at 720p.

DRAG_DEADZONE_PX = 6.0      # drag must exceed this before the totem moves:
                            # a shaky click must never become a step.

DRAG_RESPONSE_EXP = 1.4     # response curve exponent. >1 = fine control
                            # near the anchor, full authority at the edge.
                            # 1.0 would be perfectly linear.

PAD_DEADZONE = 0.25         # analog-stick deadzone (0..1): swallow drift.
PAD_RESPONSE_EXP = 1.4      # same feel as the mouse virtual joystick.


def _pad_curve(v: float) -> float:
    """Deadzone + response curve for a raw stick axis in [-1, 1] -> shaped
    [-1, 1]. Below PAD_DEADZONE returns 0.0 (drift is silence)."""
    mag = abs(v)
    if mag <= PAD_DEADZONE:
        return 0.0
    t = min(1.0, (mag - PAD_DEADZONE) / (1.0 - PAD_DEADZONE))
    return (t ** PAD_RESPONSE_EXP) * (1.0 if v > 0.0 else -1.0)

# ------------------------------------------------------------- key tables --
# ONE-SHOT actions: buffered on key-press, delivered exactly once by poll().
# Both the number row and the numpad answer, both Enters confirm -- players
# should never discover that "the other Enter" does nothing.
_DISCRETE = {
    key._1: Action.ANSWER_A,     key.NUM_1: Action.ANSWER_A,
    key._2: Action.ANSWER_B,     key.NUM_2: Action.ANSWER_B,
    key._3: Action.ANSWER_C,     key.NUM_3: Action.ANSWER_C,
    key._4: Action.ANSWER_D,     key.NUM_4: Action.ANSWER_D,
    key.ENTER: Action.CONFIRM,   key.NUM_ENTER: Action.CONFIRM,
    key.C: Action.SLICE_TOGGLE,
    key.H: Action.HINT,
    key.HOME: Action.CAM_RESET,
    key.ESCAPE: Action.QUIT,
}

# HELD analog axes: (Action, negative-key, positive-key), re-emitted every
# poll while held, shaped by the attack ramp. Signs are the FROZEN ones:
# A=-1/D=+1, S=-1/W=+1, LEFT=-1/RIGHT=+1, DOWN=-1/UP=+1.
_AXES = (
    (Action.TOTEM_X, key.A, key.D),        # boyfriend's axis
    (Action.TOTEM_Y, key.S, key.W),        # keyboard fallback for Y
    (Action.ORBIT_AZ, key.LEFT, key.RIGHT),
    (Action.ORBIT_EL, key.DOWN, key.UP),
)

# HELD discrete actions: re-emitted every frame while the key is down;
# game_state ignores the value (verified A9).
_HELD_DISCRETE = (
    (Action.ZOOM_IN, key.PAGEUP),
    (Action.ZOOM_OUT, key.PAGEDOWN),
)

# Quiz-bar click resolution: hud.hit_test's vocabulary -> Actions.
_HIT_TO_ACTION = {
    "A": Action.ANSWER_A, "B": Action.ANSWER_B,
    "C": Action.ANSWER_C, "D": Action.ANSWER_D,
    "OK": Action.CONFIRM, "HINT": Action.HINT,
}

# Game-controller face/shoulder buttons -> one-shot Actions (pyglet Controller
# button names). Mirrors the keyboard one-shots so a pad player lacks nothing.
_PAD_BUTTON = {
    "a": Action.ANSWER_A, "b": Action.ANSWER_B,
    "x": Action.ANSWER_C, "y": Action.ANSWER_D,
    "start": Action.CONFIRM, "back": Action.QUIT,
    "leftshoulder": Action.HINT, "rightshoulder": Action.SLICE_TOGGLE,
    "guide": Action.CAM_RESET, "dpup": Action.ZOOM_IN, "dpdown": Action.ZOOM_OUT,
}


class InputMap:
    """Devices in, Actions out. Owns zero game logic: it does not know what
    a mode is, what a quiz is, or what the blade does -- game_state routes.
    It only promises: clean one-shots, honest analog values in [-1, +1],
    and the frozen bindings above, forever."""

    def __init__(self, window, hud):
        """Hook pyglet window handlers. hud.hit_test resolves quiz clicks --
        the ONE table both mouse and picture share, so the click and the
        drawn button can never disagree (dependency injected per G4.4;
        this module never imports graphics)."""
        self._window = window
        self._hud = hud
        self._down = set()          # currently-held key symbols
        self._buffer = []           # one-shot (Action, value) since last poll
        self._axis_val = {a: 0.0 for a, _, _ in _AXES}   # ramped axis state
        self._drag_anchor_y = None  # press-anchor y while dragging, else None
        self._drag_y = 0.0          # latest drag y (window pixels)
        self._quiz_h = int(config.WINDOW_H * config.QUIZ_BAR_FRAC)
        # controller slots (safe no-ops; filled by attach_joystick/attach_xbox)
        self._joystick = None          # pyglet.input.Joystick or None
        self._controller = None        # pyglet.input.Controller or None
        self._pad_prev = set()         # previous-frame held buttons (edge detect)
        window.push_handlers(
            on_key_press=self._on_key_press,
            on_key_release=self._on_key_release,
            on_mouse_press=self._on_mouse_press,
            on_mouse_release=self._on_mouse_release,
            on_mouse_drag=self._on_mouse_drag,
            on_deactivate=self._on_deactivate,
        )

    # ------------------------------------------------------ pyglet events --
    def _on_key_press(self, symbol, modifiers):
        if symbol in self._down:
            return True             # defensive auto-repeat guard: a key that
                                    # is already down cannot re-fire one-shots
        self._down.add(symbol)
        act = _DISCRETE.get(symbol)
        if act is not None:
            self._buffer.append((act, 1.0))
        return True                 # consume: blocks pyglet's default
                                    # Esc-close so QUIT always flows through
                                    # game_state -> snapshot()["quit"] -> main

    def _on_key_release(self, symbol, modifiers):
        self._down.discard(symbol)
        return True

    def _on_mouse_press(self, x, y, button, modifiers):
        if button != mouse.LEFT:
            return True
        if y < self._quiz_h:
            # Quiz bar: resolve on the PRESS region -- a click on a button
            # is a click, never the start of a totem drag (verified A10).
            act = _HIT_TO_ACTION.get(self._hud.hit_test(x, y))
            if act is not None:
                self._buffer.append((act, 1.0))
        else:
            # Graphics region: plant the virtual joystick's anchor here.
            self._drag_anchor_y = float(y)
            self._drag_y = float(y)
        return True

    def _on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._drag_anchor_y is not None and (buttons & mouse.LEFT):
            self._drag_y = float(y)   # only the LATEST y matters; poll()
        return True                   # converts it to a deflection

    def _on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self._drag_anchor_y = None
        return True

    def _on_deactivate(self):
        """Window lost focus (alt-tab): forget everything held. Without this,
        a key released while unfocused would be 'stuck down' forever -- the
        classic runaway-totem bug. Costs three lines; saves an evening."""
        self._down.clear()
        self._drag_anchor_y = None
        self._axis_val = {a: 0.0 for a in self._axis_val}
        return False                  # let others hear the event too

    # --------------------------------------------------------------- pump --
    def pump_controllers(self) -> None:
        """Service controller devices so their state is fresh before poll().

        In a pyglet manual-loop game (no pyglet.app.run()), controllers must
        be pumped explicitly every frame -- window.dispatch_events() services
        keyboard/mouse but NOT controller devices (Quake precedent, verified).
        Both calls are non-blocking and fully guarded.

        XInput (Xbox): background thread posts state; dispatch_posted_events()
          delivers it to the main thread so axes update AND button-push events
          fire (so _on_pad_button receives them).
        DirectInput (joystick): drain the device buffer directly so axis
          attributes (js.x etc.) reflect the latest readings.
        """
        # XInput (Xbox): deliver thread-posted state to main thread
        try:
            import pyglet
            pyglet.app.platform_event_loop.dispatch_posted_events()
        except Exception:
            pass
        # DirectInput (joystick): drain device buffer directly (non-blocking)
        if self._joystick is not None:
            try:
                dev = getattr(self._joystick, "device", None)
                disp = getattr(dev, "_dispatch_events", None)
                if disp is not None:
                    disp()
            except Exception:
                pass

    # --------------------------------------------------------------- poll --
    def poll(self) -> list:
        """Per frame -- main calls exactly once, before update(dt) (frozen
        frame order G4.5 step 1). Returns buffered one-shots followed by the
        current value of every live analog axis. Absence of an axis action
        means 'no intent' -- game_state zeroes intents each frame."""
        self.pump_controllers()               # fresh controller state FIRST
        out, self._buffer = self._buffer, []
        d = self._down

        # -- keyboard axes, with the attack ramp --
        step = 1.0 / float(AXIS_ATTACK_FRAMES)
        for action, neg_key, pos_key in _AXES:
            target = float((pos_key in d) - (neg_key in d))
            cur = self._axis_val[action]
            if target == 0.0:
                cur = 0.0             # release is INSTANT: stop means stop
            elif cur < target:
                cur = min(target, cur + step)   # ease toward +1 (or up to 0
            else:                               #   through a direction flip)
                cur = max(target, cur - step)   # ease toward -1
            self._axis_val[action] = cur
            if cur != 0.0:
                out.append((action, cur))

        # -- held discrete actions (zoom): re-emit while down --
        for action, k in _HELD_DISCRETE:
            if k in d:
                out.append((action, 1.0))

        # -- mouse virtual joystick: girlfriend's TOTEM_Y --
        if self._drag_anchor_y is not None:
            dy = self._drag_y - self._drag_anchor_y
            mag = abs(dy)
            if mag > DRAG_DEADZONE_PX:
                # deadzone-relative magnitude, clamped, then a gentle
                # response curve: fine control near the anchor, full
                # authority at DRAG_FULL_PX.
                t = min(1.0, (mag - DRAG_DEADZONE_PX)
                        / (DRAG_FULL_PX - DRAG_DEADZONE_PX))
                v = (t ** DRAG_RESPONSE_EXP) * (1.0 if dy > 0.0 else -1.0)
                out.append((Action.TOTEM_Y, v))
            # NOTE: W/S and a live drag may both emit TOTEM_Y in one poll;
            # game_state's zero-each-frame intent accumulation resolves it,
            # and solo players (one human, WASD only) are unaffected.

        # -- game controllers (best-effort; SAFE no-op without hardware) --
        # UNVERIFIED without a physical device; fully guarded so it can NEVER
        # break the keyboard/mouse game. Axis signs are best-effort (pyglet:
        # stick up = negative) and trivial to flip if a real pad reads mirrored.
        self._read_pads(out)

        return out

    def _read_pads(self, out: list) -> None:
        """Append controller-derived actions. Every read is guarded."""
        js = self._joystick
        if js is not None:
            try:
                jx = _pad_curve(float(js.x))         # boyfriend's x-axis
                if jx != 0.0:
                    out.append((Action.TOTEM_X, jx))
            except Exception:
                pass
        c = self._controller
        if c is not None:
            try:
                ly = _pad_curve(float(c.lefty))      # stick down → totem closer
                if ly != 0.0:
                    out.append((Action.TOTEM_Y, ly))
                rx = _pad_curve(float(c.rightx))     # right stick orbits
                if rx != 0.0:
                    out.append((Action.ORBIT_AZ, rx))
                ry = _pad_curve(-float(c.righty))
                if ry != 0.0:
                    out.append((Action.ORBIT_EL, ry))
            except Exception:
                pass

    # ---------------------------------------------- pre-wired empty slots --
    def attach_joystick(self) -> None:
        """Boyfriend's x-axis on a plugged-in joystick. Best-effort + fully
        guarded: a SAFE no-op if no device is present or the platform errors
        (keyboard always works). UNVERIFIED without hardware. DeepSeek, 7/8."""
        try:
            joysticks = pyglet.input.get_joysticks()
        except Exception:
            joysticks = []
        for js in joysticks or ():
            try:
                js.open(window=self._window)   # Quake precedent: needed for DirectInput
                self._joystick = js
                break
            except Exception:
                continue

    def attach_xbox(self) -> None:
        """Girlfriend's y-axis + face/shoulder buttons on a game controller
        (Xbox et al.). Left stick -> TOTEM_Y, right stick -> orbit, buttons ->
        answers/confirm/hint/slice (see _PAD_BUTTON). Best-effort + fully
        guarded SAFE no-op without hardware. UNVERIFIED. DeepSeek, 7/8."""
        try:
            controllers = pyglet.input.get_controllers()
        except Exception:
            controllers = []
        for c in controllers or ():
            try:
                c.open()
                c.push_handlers(on_button_press=self._on_pad_button)
                self._controller = c
                break
            except Exception:
                continue

    def _on_pad_button(self, controller, button) -> None:
        """Controller button press -> one-shot Action (edge, like a keypress)."""
        act = _PAD_BUTTON.get(button)
        if act is not None:
            self._buffer.append((act, 1.0))
