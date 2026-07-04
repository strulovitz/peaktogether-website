"""python -m forge.demo — the FULL forge acceptance demo (NT Part 6).

EXPECTED (plain words, for the project owner):
Everything from the previous build (glowing cyan grid, red/green/blue
origin axes, white arrow sweeping like a tilted clock hand, red dashed
line, green wire sphere, self-orbiting camera), PLUS:
- a white fading TRAIL behind the sweeping arrow's tip;
- floating text "The origin (0,0,0)" near the center, always facing you;
- a GREEN WIRE BOX that slowly flattens and un-flattens, with a live
  volume label counting down to "vol 0.00" exactly when the box is
  completely flat, then back up to ~27;
- a grayscale IMAGE PANEL that sharpens in visible steps (label counts
  "rank 1/32" ... "rank 32/32"), then loops back to blurry;
- a squashed magenta wire sphere (an Ellipsoid);
- an fps counter in the bottom-left corner (~60 fps);
- F1 toggles white debug text in the top-left corner;
- F12 still saves a screenshot; ESC still quits; resizing is safe.
"""

import json
import math
import os
import sys
import time
import traceback

import numpy as np

from .app import Forge
from .vobjects import (
    Arrow, DashedLine, Grid, WireSphere, SpannedBox, Ellipsoid,
    Trail, Label, ImagePanel,
)


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _test_image():
    """A recognizable 128x128 test picture: gradient + bright ring +
    diagonal bar. Rich enough that low SVD ranks look clearly blurry."""
    y, x = np.mgrid[0:128, 0:128] / 127.0
    img = 0.20 * x + 0.10 * y
    r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
    img = img + np.exp(-((r - 0.30) / 0.05) ** 2)
    img = img + 0.6 * (np.abs(x - y) < 0.05)
    return np.clip(img, 0.0, 1.0)


def _arrow_end(t):
    return np.array([
        8.0 * math.cos(0.40 * t),
        4.0 + 1.5 * math.sin(0.70 * t),
        8.0 * math.sin(0.40 * t),
    ])


def main():
    settings = _load_settings()
    forge = Forge(settings)
    print("forge demo running. ESC = quit, F12 = screenshot, F1 = debug text.")

    forge.add(Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1),
                   n=10, spacing=2.0))
    forge.add(Arrow((0, 0, 0), (3, 0, 0), head_size=0.6,
                    color=(1.0, 0.25, 0.25, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 3, 0), head_size=0.6,
                    color=(0.25, 1.0, 0.35, 1.0)))
    forge.add(Arrow((0, 0, 0), (0, 0, 3), head_size=0.6,
                    color=(0.35, 0.55, 1.0, 1.0)))

    first_vector = Arrow((0, 0, 0), (8, 4, 0), head_size=1.1,
                         color=(1.0, 1.0, 1.0, 1.0), glow=1.2)
    forge.add(first_vector)
    trail = Trail(max_points=80, color=(1.0, 1.0, 1.0, 0.7), width=0.05)
    forge.add(trail)

    forge.add(DashedLine((-9, 0.5, -9), (9, 3.5, 9), dash=0.7,
                         color=(1.0, 0.35, 0.30, 1.0)))
    forge.add(WireSphere((-7, 2.0, 5), 2.0, color=(0.35, 1.0, 0.55, 0.8)))
    forge.add(Ellipsoid((11, 3.0, 8),
                        [[2.0, 0.0, 0.0], [0.0, 0.8, 0.0], [0.0, 0.0, 1.2]],
                        color=(1.0, 0.4, 0.9, 0.8)))

    forge.add(Label("The origin (0,0,0)", (0, -1.6, 0), size=1.0,
                    color=(0.9, 0.95, 1.0, 0.9)))

    # The determinant-as-volume box (Bible 2.10 code path).
    box_origin = np.array([9.0, 0.0, -8.0])
    box = SpannedBox(box_origin, (3, 0, 0), (1, 0, 3), (1, 3, 1))
    forge.add(box)
    vol_label = Label("vol 0.00", box_origin + np.array([2.0, 4.8, 1.0]),
                      size=1.1, color=(0.6, 1.0, 0.7, 1.0))
    forge.add(vol_label)

    # The Guidestone code path: live SVD partial sums of a test image.
    G = _test_image()
    U, s, Vt = np.linalg.svd(G)
    ranks = [1, 2, 4, 8, 16, 32]

    def rank_image(k):
        return np.clip((U[:, :k] * s[:k]) @ Vt[:k], 0.0, 1.0)

    panel = ImagePanel(rank_image(1), pos=(-11.0, 6.0, -9.0), w=6.0, h=6.0)
    forge.add(panel)
    rank_label = Label("rank 1/32", (-11.0, 2.2, -9.0), size=0.9,
                       color=(0.8, 0.9, 1.0, 0.9))
    forge.add(rank_label)

    start = time.perf_counter()
    state = {"pulses": 0, "rank_idx": 0}

    def tick(dt):
        state["pulses"] += 1
        t = time.perf_counter() - start
        trail.push(_arrow_end(t))

    def frame(alpha):
        t = time.perf_counter() - start
        forge.camera.yaw = 0.8 + 0.12 * t
        forge.camera.pitch = 0.35 + 0.10 * math.sin(0.30 * t)

        first_vector.set_data((0.0, 0.0, 0.0), _arrow_end(t), head_size=1.1)

        # Box flattening: third vector's height sweeps 3 -> 0 -> 3;
        # |det| of the three column vectors is recomputed live by numpy.
        height = 3.0 * abs(math.sin(0.35 * t))
        v1, v2, v3 = (3, 0, 0), (1, 0, 3), (1, height, 1)
        box.set_data(box_origin, v1, v2, v3)
        volume = abs(np.linalg.det(np.column_stack([v1, v2, v3])))
        vol_label.set_text(f"vol {volume:.2f}")

        idx = int(t / 1.5) % len(ranks)
        if idx != state["rank_idx"]:
            state["rank_idx"] = idx
            k = ranks[idx]
            panel.set_image(rank_image(k))
            rank_label.set_text(f"rank {k}/32")

        forge.set_debug_lines([
            f"pulse {state['pulses']}",
            f"cam yaw {forge.camera.yaw:.2f} pitch {forge.camera.pitch:.2f}",
            "F1 hides this overlay",
        ])

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
