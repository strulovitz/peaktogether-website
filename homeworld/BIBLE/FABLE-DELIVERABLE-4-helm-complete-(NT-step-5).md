> 🛑 **DEEPSEEK NOTE (July 5, 2026) — the code below was dropped in, but CONVERTED to Quake-style before use.** Fable wrote the helm files with **relative imports** (`from . import Helm`, `from .actions import ...`) and told Nir to run `python -m helm.demo`. **Nir never agreed to `-m` and hates it** — every Peak Together game runs with plain `python <file>.py`. So on drop-in I converted every helm/forge file to **flat absolute imports** (`from actions import ...`) and the demo now runs with **`python helm\demo.py`** (never `-m`). Fable's original text is preserved verbatim below for the record. Going forward, all Fable files are converted the same way. See WORKFLOW.md RULE #0.

---

Forge is DONE — the first module of the cathedral is complete and confirmed by your own eyes. 🎉 Now the next module: HELM (New Testament Part 2) — the input layer. This is what makes "Player 1 = keyboard, Player 2 = mouse" real, and it's the wall socket that joystick/Xbox support will plug into later without touching anything else.

Below are 8 complete files (7 new + 1 settings update). Send each to DeepSeek exactly as-is.

File 1 — helm/actions.py

"""THE FROZEN ACTION LIST (NEW_TESTAMENT 2.2, version 1).

Game logic imports these names and NEVER imports pyglet key codes.
Adding a new action later = allowed with a minor version bump.
Renaming or removing an action = forbidden without owner approval.
"""

from dataclasses import dataclass

ACTIONS_VERSION = 1

# ---- Pilot: continuous axes (value in [-1.0, +1.0], polled) ----
PILOT_AXES = [
    "CAM_YAW", "CAM_PITCH", "CAM_ZOOM",      # camera orbit control
    "TRIM_X", "TRIM_Y", "TRIM_Z",            # thruster trim (Bible 2.1)
]

# ---- Pilot: buttons (events: value 1.0 press / 0.0 release) ----
PILOT_BUTTONS = [
    "SELECT_NEXT", "SELECT_PREV",            # cycle ships
    "SQUAD_NEXT", "SQUAD_PREV",              # cycle squads
    "ORDER_CONFIRM", "ORDER_CANCEL",
    "ACTION_PRIMARY",                        # fire / execute (context action)
    "ACTION_SECONDARY",                      # context action 2 (e.g. dock)
    "FLIGHT_MODE_TOGGLE",                    # component vs diagonal (Bible 2.1)
    "CAM_MODE_CYCLE",                        # ORBIT -> FOLLOW -> POV
    "PAUSE",
]

# ---- System buttons (either player, always active) ----
SYSTEM_BUTTONS = [
    "DEBUG_OVERLAY",                         # F1
    "SCREENSHOT",                            # F12
]

ALL_BUTTONS = PILOT_BUTTONS + SYSTEM_BUTTONS


@dataclass(frozen=True)
class ActionEvent:
    action: str      # one of the names above
    value: float     # 1.0 press / 0.0 release


@dataclass(frozen=True)
class PointerState:
    x: float
    y: float                 # window pixels, origin bottom-left
    primary: bool
    secondary: bool
    wheel: float             # scroll delta accumulated since last poll

File 2 — helm/keyboard_map.py

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

from .actions import ActionEvent, PILOT_AXES, ALL_BUTTONS

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

File 3 — helm/mouse_map.py

"""MouseMapper: the Navigator's baseline device (NEW_TESTAMENT 2.2).

The pointer is the Navigator's ENTIRE interface: position in window
pixels (origin bottom-left, pyglet's native convention), primary and
secondary buttons, and accumulated wheel delta. The bridge module
consumes PointerState directly; there are no named Navigator buttons.
"""

from pyglet.window import mouse

from .actions import PointerState


class MouseMapper:
    def __init__(self, settings):
        self._x = 0.0
        self._y = 0.0
        self._primary = False
        self._secondary = False
        self._wheel = 0.0

    # ---- Mapper protocol ----

    def attach(self, window):
        window.push_handlers(
            on_mouse_motion=self._on_motion,
            on_mouse_drag=self._on_drag,
            on_mouse_press=self._on_press,
            on_mouse_release=self._on_release,
            on_mouse_scroll=self._on_scroll,
        )

    def poll_events(self):
        return []

    def poll_axes(self):
        return {}

    def poll_pointer(self):
        state = PointerState(
            x=self._x, y=self._y,
            primary=self._primary, secondary=self._secondary,
            wheel=self._wheel,
        )
        self._wheel = 0.0
        return state

    # ---- pyglet handlers ----

    def _on_motion(self, x, y, dx, dy):
        self._x, self._y = float(x), float(y)

    def _on_drag(self, x, y, dx, dy, buttons, modifiers):
        self._x, self._y = float(x), float(y)

    def _on_press(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            self._primary = True
        if button & mouse.RIGHT:
            self._secondary = True

    def _on_release(self, x, y, button, modifiers):
        if button & mouse.LEFT:
            self._primary = False
        if button & mouse.RIGHT:
            self._secondary = False

    def _on_scroll(self, x, y, scroll_x, scroll_y):
        self._wheel += float(scroll_y)

File 4 — helm/joystick_map.py

"""JoystickMapper — NOT IMPLEMENTED YET. Sanctioned future work for
DeepSeek (NEW_TESTAMENT 2.5). Implementation instructions, complete:

1. Enumerate devices with pyglet.input.get_joysticks(); call
   device.open(). The Thrustmaster T16000M exposes .x, .y, .rz
   (twist), .z (throttle slider) and a .buttons list.
2. Apply the dead-zone formula to every analog axis with d = 0.15:
       v' = sign(v) * max(0, (|v| - d) / (1 - d))
3. Suggested T16000M pilot mapping: x -> CAM_YAW, y -> CAM_PITCH,
   twist rz -> TRIM_X, throttle z -> CAM_ZOOM, trigger ->
   ACTION_PRIMARY, thumb button -> ORDER_CONFIRM, hat switch ->
   TRIM_Y / TRIM_Z.
4. Implement ONLY the Mapper protocol below (attach / poll_events /
   poll_axes / poll_pointer). DO NOT touch any file outside helm/.
   DO NOT rename any action. Test with: python -m helm.demo after
   setting settings.json input.pilot_device to "joystick".
"""


class JoystickMapper:
    def __init__(self, settings):
        raise NotImplementedError(
            "JoystickMapper is not implemented yet — see this file's "
            "docstring. Helm will fall back to the keyboard."
        )

File 5 — helm/gamepad_map.py

"""GamepadMapper — NOT IMPLEMENTED YET. Sanctioned future work for
DeepSeek (NEW_TESTAMENT 2.5). Implementation instructions, complete:

1. Enumerate with pyglet.input.get_controllers(); Xbox controllers
   expose named attributes (leftx, lefty, rightx, righty,
   lefttrigger, righttrigger, buttons a/b/x/y, bumpers, dpad, start).
2. Apply the dead-zone formula with d = 0.15 to every stick axis:
       v' = sign(v) * max(0, (|v| - d) / (1 - d))
3. Suggested Xbox PILOT mapping: leftx/lefty -> CAM_YAW/CAM_PITCH,
   rightx/righty -> TRIM_X/TRIM_Z, triggers -> CAM_ZOOM (RT - LT),
   A -> ORDER_CONFIRM, B -> ORDER_CANCEL, X -> ACTION_PRIMARY,
   Y -> FLIGHT_MODE_TOGGLE, bumpers -> SELECT_PREV/SELECT_NEXT,
   start -> PAUSE.
4. Xbox as NAVIGATOR device: left stick moves a virtual pointer
   (x += stick_x * speed * dt; synthesize PointerState), A = primary
   click, B = secondary, right stick vertical = wheel.
5. Implement ONLY the Mapper protocol (attach / poll_events /
   poll_axes / poll_pointer). DO NOT touch any file outside helm/.
   DO NOT rename any action. Test with: python -m helm.demo.
"""


class GamepadMapper:
    def __init__(self, settings):
        raise NotImplementedError(
            "GamepadMapper is not implemented yet — see this file's "
            "docstring. Helm will fall back to keyboard/mouse."
        )

File 6 — helm/__init__.py

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

File 7 — helm/demo.py

"""python -m helm.demo — the helm acceptance demo (NT Part 6).

EXPECTED (plain words, for the project owner):
A small dark window opens (it must have FOCUS — click it once). The
CONSOLE (the black text window behind it) then prints:
- every mapped key on press and release, e.g.
      ACTION ORDER_CONFIRM 1.0        (pressing Enter)
      ACTION ORDER_CONFIRM 0.0        (releasing Enter)
- holding W prints "AXIS TRIM_Z +1.00" ten times per second;
  holding W and S together prints nothing (they cancel to zero);
- moving the mouse prints "POINTER x=... y=..." lines;
- clicking prints "POINTER PRIMARY down/up" (left) and
  "POINTER SECONDARY down/up" (right);
- the mouse wheel prints "WHEEL +1.0" / "WHEEL -1.0" per notch;
- TAB prints SELECT_NEXT, SHIFT+TAB prints SELECT_PREV;
- pressing an UNMAPPED key (e.g. Z) prints nothing and nothing crashes.
ESC closes the window.
"""

import json
import os
import sys
import time
import traceback

import pyglet

from . import Helm


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    settings = _load_settings()
    window = pyglet.window.Window(
        width=640, height=360,
        caption="helm demo — click me, then press keys / move mouse",
    )
    helm = Helm(settings)
    helm.attach(window)
    print("helm demo running. Click the window to give it focus.")
    print("Press mapped keys, move/click/scroll the mouse. ESC quits.")

    last_x, last_y = None, None
    last_primary, last_secondary = False, False
    prev = time.perf_counter()
    accumulator = 0.0

    while not window.has_exit:
        window.dispatch_events()
        if window.has_exit:
            break
        now = time.perf_counter()
        accumulator += min(now - prev, 0.25)
        prev = now
        while accumulator >= 0.1:                 # the 10 Hz pulse
            accumulator -= 0.1
            events, axes, pointer = helm.poll()
            for ev in events:
                print(f"ACTION {ev.action} {ev.value:.1f}")
            for action, value in axes.items():
                if abs(value) > 1e-6:
                    print(f"AXIS {action} {value:+.2f}")
            if (last_x, last_y) != (pointer.x, pointer.y):
                last_x, last_y = pointer.x, pointer.y
                print(f"POINTER x={pointer.x:.0f} y={pointer.y:.0f}")
            if pointer.primary != last_primary:
                last_primary = pointer.primary
                print(f"POINTER PRIMARY {'down' if pointer.primary else 'up'}")
            if pointer.secondary != last_secondary:
                last_secondary = pointer.secondary
                print("POINTER SECONDARY "
                      f"{'down' if pointer.secondary else 'up'}")
            if abs(pointer.wheel) > 1e-6:
                print(f"WHEEL {pointer.wheel:+.1f}")
        window.clear()
        window.flip()
    window.close()


def run_with_crashlog(fn):
    try:
        fn()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("helm.demo crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)


if __name__ == "__main__":
    run_with_crashlog(main)

File 8 — settings.json (updated — adds the input section, version bump)

{
    "title": "Homeworld: A Good Basis",
    "version": "0.4.0",
    "width": 1280,
    "height": 720,
    "fullscreen": false,
    "vsync": true,
    "bloom_strength": 0.85,
    "exposure": 2.5,
    "seed": 1234,
    "input": {
        "pilot_device": "keyboard",
        "navigator_device": "mouse",
        "keyboard_overrides": {}
    }
}

📋 YOUR STEPS

    Send to DeepSeek: the 8 files, verbatim, commit message: NT step 5: helm complete (actions, keyboard+mouse mappers, joystick/gamepad stubs, demo) — and update COMMENTARIES.md.
    Run: open the project folder, click the address bar, type cmd, Enter, then run: python -m helm.demo
    (Not run.bat this time — run.bat still launches the forge demo; we want the console visible for this test.)

👀 WHAT YOU SHOULD SEE

A small dark window opens. Click it once to give it focus, then watch the black console window behind it:

    Press Enter → console prints ACTION ORDER_CONFIRM 1.0, release → ... 0.0. Try Space, Q, E, X, P, C, Backspace — each prints its action name.
    Hold W → AXIS TRIM_Z +1.00 printed ~10 times per second. Hold W and S together → they cancel, nothing prints. Arrow keys → CAM_YAW / CAM_PITCH lines.
    TAB → SELECT_NEXT; SHIFT+TAB → SELECT_PREV.
    Move the mouse over the window → POINTER x=... y=... lines. Left/right click → POINTER PRIMARY/SECONDARY down/up. Scroll → WHEEL +1.0 / -1.0.
    Press an unmapped key like Z → nothing prints, nothing crashes.
    ESC closes it.

📝 REPORT BACK

The usual! If all six behaviors match, helm is DONE — and the next package is the big one: fleet — the simulation core, where ships become matrix columns, the 10 Hz pulse starts beating, and referee.py re-proves the Bible's worked examples with its 12-line self-test (FLEET SELF-TEST PASSED (12/12) printed in plain English, for your eyes). After that, we wire all three modules together in app.py — and three ships fly their first combination order on your screen. 🚀❤️
