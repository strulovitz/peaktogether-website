"""
LOOM2 -- core/input_map.py
Device -> Action translation (SUTRAS Part 9). Allowed imports: pyglet,
config, core.types. Keyboard + mouse fully implemented; joystick/xbox slots
STAY EMPTY (DeepSeek copies device code from previous games).
NOTE: pyglet here is WINDOW EVENTS only -- the pyglet ban is on HUD rendering.

FROZEN BINDINGS (G4.4):
  A/D -> TOTEM_X (-1/+1)  [boyfriend]     W/S -> TOTEM_Y (+1/-1)
  mouse vertical drag -> TOTEM_Y analog   [girlfriend]
  arrows -> ORBIT_AZ/ORBIT_EL   PgUp/PgDn -> ZOOM_IN/OUT
  Home -> CAM_RESET   C -> SLICE_TOGGLE   Enter -> CONFIRM/SLICE_PLAY
  1-4 -> ANSWER_A..D   H -> HINT   Esc -> QUIT

Conventions verified with DeepSeek (2026-07-08):
- game_state ZEROES axis intents each frame: held axes are re-emitted every
  poll(); releasing a key simply stops emission (no explicit 0 needed).
- ORBIT_*: unitless +/-1 (RIGHT/UP = +1, Nir's locked signs); game_state
  scales (az 60 deg/s, el 40 deg/s, x dt). ZOOM_*: re-emitted while held,
  value ignored by game_state.
- Enter emits CONFIRM only: game_state._route_slice accepts CONFIRM as
  SLICE_PLAY, so SLICE_PLAY needs no key of its own.
- Esc emits Action.QUIT through the normal path (game_state sets _quit; main
  reads snapshot()["quit"]). Our on_key_press returns True, so pyglet's
  default Esc-close never fires.
- Mouse: bottom-left origin (matches hud.hit_test and the config regions).
  Press with my < quiz_h -> quiz-bar click (a click NEVER starts a drag);
  press in the graphics region -> virtual-joystick drag anchor for TOTEM_Y.
"""
import pyglet
from pyglet.window import key, mouse
import config
from core.types import Action

# Mouse drag sensitivity: pixels of vertical travel from the press anchor for
# full deflection |TOTEM_Y| = 1.0. Not frozen; DeepSeek round-2 suggested
# ~160 px as a comfortable virtual joystick on a 720p window. Tune by taste.
DRAG_FULL_PX = 160.0

_DISCRETE = {
    key._1: Action.ANSWER_A, key._2: Action.ANSWER_B,
    key._3: Action.ANSWER_C, key._4: Action.ANSWER_D,
    key.NUM_1: Action.ANSWER_A, key.NUM_2: Action.ANSWER_B,
    key.NUM_3: Action.ANSWER_C, key.NUM_4: Action.ANSWER_D,
    key.ENTER: Action.CONFIRM, key.NUM_ENTER: Action.CONFIRM,
    key.C: Action.SLICE_TOGGLE, key.H: Action.HINT,
    key.HOME: Action.CAM_RESET, key.ESCAPE: Action.QUIT,
}
_HIT_TO_ACTION = {
    "A": Action.ANSWER_A, "B": Action.ANSWER_B,
    "C": Action.ANSWER_C, "D": Action.ANSWER_D,
    "OK": Action.CONFIRM, "HINT": Action.HINT,
}


class InputMap:
    def __init__(self, window, hud):
        """Hook pyglet handlers. hud.hit_test resolves quiz clicks."""
        self._hud = hud
        self._down = set()            # currently-held key symbols
        self._buffer = []             # one-shot (Action, value) since last poll
        self._drag_anchor_y = None    # press-anchor y while dragging, else None
        self._drag_y = 0.0
        self._quiz_h = int(config.WINDOW_H * config.QUIZ_BAR_FRAC)
        window.push_handlers(
            on_key_press=self._on_key_press,
            on_key_release=self._on_key_release,
            on_mouse_press=self._on_mouse_press,
            on_mouse_release=self._on_mouse_release,
            on_mouse_drag=self._on_mouse_drag,
        )

    # ------------------------------------------------------ pyglet events
    def _on_key_press(self, symbol, modifiers):
        if symbol in self._down:      # defensive auto-repeat guard
            return True
        self._down.add(symbol)
        act = _DISCRETE.get(symbol)
        if act is not None:
            self._buffer.append((act, 1.0))
        return True                   # consume (blocks default Esc-close)

    def _on_key_release(self, symbol, modifiers):
        self._down.discard(symbol)
        return True

    def _on_mouse_press(self, x, y, button, modifiers):
        if button != mouse.LEFT:
            return True
        if y < self._quiz_h:          # quiz bar: resolve on press-region,
            act = _HIT_TO_ACTION.get(self._hud.hit_test(x, y))
            if act is not None:       # so a click never starts a drag
                self._buffer.append((act, 1.0))
        else:                         # graphics region: begin TOTEM_Y drag
            self._drag_anchor_y = float(y)
            self._drag_y = float(y)
        return True

    def _on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self._drag_anchor_y is not None and (buttons & mouse.LEFT):
            self._drag_y = float(y)
        return True

    def _on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            self._drag_anchor_y = None
        return True

    # -------------------------------------------------------------- poll
    def poll(self) -> list:
        """Per frame (main calls exactly once, before update): buffered
        one-shots + current values of every held analog axis."""
        out, self._buffer = self._buffer, []
        d = self._down
        ax = (key.D in d) - (key.A in d)
        if ax:
            out.append((Action.TOTEM_X, float(ax)))
        ay = (key.W in d) - (key.S in d)
        if ay:
            out.append((Action.TOTEM_Y, float(ay)))
        az = (key.RIGHT in d) - (key.LEFT in d)
        if az:
            out.append((Action.ORBIT_AZ, float(az)))
        el = (key.UP in d) - (key.DOWN in d)
        if el:
            out.append((Action.ORBIT_EL, float(el)))
        if key.PAGEUP in d:
            out.append((Action.ZOOM_IN, 1.0))
        if key.PAGEDOWN in d:
            out.append((Action.ZOOM_OUT, 1.0))
        if self._drag_anchor_y is not None:            # girlfriend's axis
            v = (self._drag_y - self._drag_anchor_y) / DRAG_FULL_PX
            out.append((Action.TOTEM_Y, max(-1.0, min(1.0, v))))
        return out

    # ------------------------------------------- pre-wired empty slots
    def attach_joystick(self) -> None:
        """EMPTY. DeepSeek fills from previous working games (P1 x-axis)."""
        pass

    def attach_xbox(self) -> None:
        """EMPTY. DeepSeek fills (P2 y-axis on left stick)."""
        pass
