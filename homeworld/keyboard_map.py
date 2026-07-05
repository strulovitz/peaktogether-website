"""KeyboardMapper: the Pilot's baseline device (NEW_TESTAMENT 2.4).

Held keys produce digital axis values +1/-1 while held. Buttons emit
ActionEvents on press (1.0) and release (0.0). Default bindings are
frozen below; settings.json may override them via
settings['input']['keyboard_overrides'], e.g.:
    { "SPACE": "ORDER_CONFIRM", "K": ["TRIM_Y", 1.0] }
Keys are pyglet key names as strings. Unknown names produce a loud
console warning and are skipped — never a crash.
"""

from pyglet.window import key as pkey

from actions import ActionEvent, PILOT_AXES, ALL_BUTTONS

# key name -> (action, axis_value or None for buttons)
_DEFAULTS = {
    "LEFT":     ("CAM_YAW",   -1.0),
    "RIGHT":    ("CAM_YAW",   +1.0),
    "UP":       ("CAM_PITCH", +1.0),
    "DOWN":     ("CAM_PITCH", -1.0),
    "PAGEUP":   ("CAM_ZOOM",  -1.0),
    "PAGEDOWN": ("CAM_ZOOM",  +1.0),
    "W":        ("TRIM_Z",    +1.0),
    "S":        ("TRIM_Z",    -1.0),
    "A":        ("TRIM_X",    -1.0),
    "D":        ("TRIM_X",    +1.0),
    "R":        ("TRIM_Y",    +1.0),
    "F":        ("TRIM_Y",    -1.0),
    "C":        ("CAM_MODE_CYCLE",    None),
    "E":        ("SQUAD_NEXT",        None),
    "Q":        ("SQUAD_PREV",        None),
    "ENTER":    ("ORDER_CONFIRM",     None),
    "BACKSPACE": ("ORDER_CANCEL",     None),
    "SPACE":    ("ACTION_PRIMARY",    None),
    "LCTRL":    ("ACTION_SECONDARY",  None),
    "X":        ("FLIGHT_MODE_TOGGLE", None),
    "P":        ("PAUSE",             None),
    "F1":       ("DEBUG_OVERLAY",     None),
    "F12":      ("SCREENSHOT",        None),
    # TAB / SHIFT+TAB (SELECT_NEXT / SELECT_PREV) handled specially below.
}


class KeyboardMapper:
    def __init__(self, settings):
        bindings = dict(_DEFAULTS)
        overrides = settings.get("input", {}).get("keyboard_overrides", {})
        for key_name, spec in overrides.items():
            if isinstance(spec, str):
                action, value = spec, None
            else:
                action, value = spec[0], float(spec[1])
            if action in PILOT_AXES and value is None:
                print(f"helm WARNING: override for {key_name}: axis "
                      f"{action} needs a value, e.g. [\"{action}\", 1.0] "
                      f"— skipped.")
                continue
            if action not in PILOT_AXES and action not in ALL_BUTTONS:
                print(f"helm WARNING: override for {key_name}: unknown "
                      f"action {action} — skipped.")
                continue
            bindings[key_name.upper()] = (action, value)

        self._by_symbol = {}
        for key_name, binding in bindings.items():
            symbol = getattr(pkey, key_name, None)
            if symbol is None:
                print(f"helm WARNING: unknown key name {key_name} — skipped.")
                continue
            self._by_symbol[symbol] = binding

        self._pressed = set()      # held symbols (for axes + repeat guard)
        self._events = []
        self._tab_action = None    # which select action TAB is holding

    # ---- Mapper protocol ----

    def attach(self, window):
        window.push_handlers(
            on_key_press=self._on_press, on_key_release=self._on_release
        )

    def poll_events(self):
        out = self._events
        self._events = []
        return out

    def poll_axes(self):
        axes = {}
        for symbol in self._pressed:
            binding = self._by_symbol.get(symbol)
            if binding is None or binding[1] is None:
                continue
            action, value = binding
            axes[action] = max(-1.0, min(1.0, axes.get(action, 0.0) + value))
        return axes

    def poll_pointer(self):
        return None

    # ---- pyglet handlers (return None so defaults, e.g. ESC, survive) ----

    def _on_press(self, symbol, modifiers):
        if symbol == pkey.TAB:
            if self._tab_action is None:      # ignore auto-repeat
                self._tab_action = (
                    "SELECT_PREV" if (modifiers & pkey.MOD_SHIFT)
                    else "SELECT_NEXT"
                )
                self._events.append(ActionEvent(self._tab_action, 1.0))
            return
        if symbol in self._pressed:           # ignore auto-repeat
            return
        binding = self._by_symbol.get(symbol)
        if binding is None:
            return
        self._pressed.add(symbol)
        action, value = binding
        if value is None:
            self._events.append(ActionEvent(action, 1.0))

    def _on_release(self, symbol, modifiers):
        if symbol == pkey.TAB:
            if self._tab_action is not None:
                self._events.append(ActionEvent(self._tab_action, 0.0))
                self._tab_action = None
            return
        if symbol not in self._pressed:
            return
        self._pressed.discard(symbol)
        binding = self._by_symbol.get(symbol)
        if binding is not None and binding[1] is None:
            self._events.append(ActionEvent(binding[0], 0.0))
