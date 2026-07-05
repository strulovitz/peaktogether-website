"""python helm/demo.py — the helm acceptance demo (NT Part 6).

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

from __init__ import Helm


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
