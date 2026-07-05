"""helm — the input abstraction of Homeworld: A Good Basis.

Logical actions only: game logic never sees a key code or a device.
Keyboard (Pilot) + mouse (Navigator) are the always-working baseline
(Iron Rule 2); joystick and gamepad mappers are stubs awaiting their
sanctioned implementation (NEW_TESTAMENT 2.5). Any device may drive
either role via settings.json:

    "input": {
        "pilot_device": "keyboard",
        "navigator_device": "mouse",
        "keyboard_overrides": {}
    }

An unavailable device produces a loud console warning and falls back
to keyboard/mouse — never a crash.
"""

from .actions import (
    ACTIONS_VERSION, PILOT_AXES, PILOT_BUTTONS, SYSTEM_BUTTONS,
    ALL_BUTTONS, ActionEvent, PointerState,
)
from .keyboard_map import KeyboardMapper
from .mouse_map import MouseMapper
from .joystick_map import JoystickMapper
from .gamepad_map import GamepadMapper

_EMPTY_POINTER = PointerState(0.0, 0.0, False, False, 0.0)

_DEVICE_CLASSES = {
    "keyboard": KeyboardMapper,
    "mouse": MouseMapper,
    "joystick": JoystickMapper,
    "gamepad": GamepadMapper,
}


class Helm:
    def __init__(self, settings):
        inp = settings.get("input", {})
        self._pilot = self._make(
            inp.get("pilot_device", "keyboard"), "keyboard", settings
        )
        self._navigator = self._make(
            inp.get("navigator_device", "mouse"), "mouse", settings
        )

    def _make(self, name, fallback, settings):
        cls = _DEVICE_CLASSES.get(name)
        if cls is None:
            print(f"helm WARNING: unknown device '{name}', "
                  f"falling back to '{fallback}'.")
            return _DEVICE_CLASSES[fallback](settings)
        try:
            return cls(settings)
        except Exception as exc:
            print(f"helm WARNING: device '{name}' unavailable "
                  f"({exc}); falling back to '{fallback}'.")
            return _DEVICE_CLASSES[fallback](settings)

    # ---- frozen interface (NEW_TESTAMENT 2.3) ----

    def attach(self, window):
        self._pilot.attach(window)
        self._navigator.attach(window)

    def poll(self):
        """Once per PULSE. Returns (button events since last poll,
        current axis values for all PILOT_AXES, pointer state)."""
        events = self._pilot.poll_events() + self._navigator.poll_events()
        axes = {a: 0.0 for a in PILOT_AXES}
        axes.update(self._pilot.poll_axes())
        pointer = self._navigator.poll_pointer()
        if pointer is None:
            pointer = self._pilot.poll_pointer() or _EMPTY_POINTER
        return events, axes, pointer

    def poll_axes_only(self):
        """Once per FRAME, for smooth camera between pulses. Reads held
        state only — queued button events are NOT consumed."""
        axes = {a: 0.0 for a in PILOT_AXES}
        axes.update(self._pilot.poll_axes())
        return axes
