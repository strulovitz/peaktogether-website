"""python -m forge.demo — the walking-skeleton acceptance demo.

EXPECTED (plain words, for the project owner):
A black window titled "Homeworld: A Good Basis — forge v0.1.0 — 60 fps".
A glowing cyan grid plane seen at an angle. At the grid's center, three
small arrows (red = X, green = Y, blue = Z) mark the origin. One larger
WHITE ARROW sweeps slowly around the origin like a clock hand tilted in
3D — this is the first vector, drawn live from numpy. A red dashed line
crosses the scene. A soft green wire sphere sits to one side. The camera
orbits slowly by itself and gently bobs up and down. Lines are bright in
the middle with soft edges; where lines cross, they get brighter.
ESC closes the window. F12 saves a screenshot into screenshots/ and
prints the path in the console. Any crash writes crashlog.txt.
"""

import json
import math
import os
import sys
import time
import traceback

import numpy as np

from .app import Forge
from .vobjects import Arrow, DashedLine, Grid, WireSphere


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    settings = _load_settings()
    forge = Forge(settings)
    print("forge demo running. ESC = quit, F12 = screenshot.")

    # The reference plane: span of e1=(1,0,0) and e3=(0,0,1) through origin.
    grid = Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1), n=10, spacing=2.0)
    forge.add(grid)

    # Origin axes: x red, y green, z blue.
    forge.add(Arrow((0, 0, 0), (3, 0, 0), head_size=0.6,
                    color=(1.0, 0.25, 0.25, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 3, 0), head_size=0.6,
                    color=(0.25, 1.0, 0.35, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 0, 3), head_size=0.6,
                    color=(0.35, 0.55, 1.0, 1.0)))

    # THE first vector from the origin — animated every frame.
    first_vector = Arrow((0, 0, 0), (8, 4, 0), head_size=1.1,
                         color=(1.0, 1.0, 1.0, 1.0), glow=1.2)
    forge.add(first_vector)

    forge.add(DashedLine((-9, 0.5, -9), (9, 3.5, 9), dash=0.7,
                         color=(1.0, 0.35, 0.30, 1.0)))
    forge.add(WireSphere((-7, 2.0, 5), 2.0,
                         color=(0.35, 1.0, 0.55, 0.8)))

    start = time.perf_counter()
    pulse_count = [0]

    def tick(dt):
        # 10 Hz logic pulse. Nothing to simulate yet — fleet comes later.
        pulse_count[0] += 1

    def frame(alpha):
        t = time.perf_counter() - start
        # Self-orbiting camera with a gentle vertical bob.
        forge.camera.yaw = 0.8 + 0.12 * t
        forge.camera.pitch = 0.35 + 0.10 * math.sin(0.30 * t)
        # The first vector sweeps around the origin, tilting as it goes.
        end = np.array([
            8.0 * math.cos(0.40 * t),
            4.0 + 1.5 * math.sin(0.70 * t),
            8.0 * math.sin(0.40 * t),
        ])
        first_vector.set_data((0.0, 0.0, 0.0), end, head_size=1.1)

    forge.run(tick, frame)


def run_with_crashlog(fn):
    try:
        fn()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("forge.demo crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)


if __name__ == "__main__":
    run_with_crashlog(main)
