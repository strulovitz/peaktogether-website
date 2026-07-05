"""
demo2d.py — acceptance demo for the 2D overlay (INTERFACES v1.1).

Run from the homeworld/ folder:   python demo2d.py

Requires the two wiring insertions described in overlay2d.py's header
(Forge.overlay2d + the draw call after the bloom composite).
"""

import json
import math
import os
import traceback

import numpy as np


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"width": 1280, "height": 720}


def _radial_image(n=96):
    yy, xx = np.mgrid[0:n, 0:n]
    c = (n - 1) / 2.0
    r = np.hypot(xx - c, yy - c) / c
    return np.clip(1.0 - r, 0.0, 1.0) ** 1.5


def _checker_image(n=96, k=8):
    yy, xx = np.mgrid[0:n, 0:n]
    return (((xx // k) + (yy // k)) % 2).astype(np.float64)


def main():
    from forge import Forge
    from vobjects import Grid, Arrow
    from overlay2d import Rect2D, Line2D, Label2D, Image2D

    settings = dict(_load_settings())
    settings["title"] = "OVERLAY2D demo"
    forge = Forge(settings)
    ov = getattr(forge, "overlay2d", None)
    if ov is None:
        raise SystemExit("Forge has no .overlay2d — apply the wiring in "
                         "overlay2d.py's header first.")

    # ---- a little 3D world, so the UI visibly floats OVER it --------------
    grid = Grid(np.array([0.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0.0, 0.0, 1.0]), n=10, spacing=2.0)
    grid.set_color((0.12, 0.42, 0.55, 0.4))
    arrow = Arrow(np.array([0.0, 0.0, 0.0]), np.array([4.0, 3.0, 2.0]))
    arrow.set_color((0.95, 0.95, 1.0, 1.0))
    forge.add(grid)
    forge.add(arrow)
    forge.camera.set_orbit(np.array([0.0, 0.0, 0.0]))
    forge.camera.distance = 28.0
    forge.camera.pitch = 0.45

    # ---- the 2D console mock-up (positions filled in by _relayout) --------
    cyan = (0.35, 0.75, 1.0, 0.9)
    panel_bg = Rect2D(0, 0, 10, 10, (0.05, 0.09, 0.13, 0.75), filled=True)
    panel_frame = Rect2D(0, 0, 10, 10, cyan, filled=False)
    title = Label2D("OVERLAY2D — CONSOLE DEMO", 0, 0, px=16,
                    color=(0.7, 0.95, 1.0, 1.0))
    divider = Line2D(0, 0, 0, 0, (0.35, 0.75, 1.0, 0.6))
    slider_track = Line2D(0, 0, 0, 0, (0.5, 0.8, 1.0, 0.8))
    slider_track.thickness = 2.0
    knob = Rect2D(0, 0, 10, 18, (1.0, 0.85, 0.3, 1.0), filled=True)
    readout = Label2D("c1 = +0.00", 0, 0, px=16, color=(1.0, 0.85, 0.3, 1.0))
    clock_frame = Rect2D(0, 0, 90, 90, cyan, filled=False)
    clock_hand = Line2D(0, 0, 0, 0, (1.0, 0.5, 0.4, 1.0))
    clock_hand.thickness = 2.0
    img_static = Image2D(_radial_image(), 0, 0, 96, 96)
    img_anim = Image2D(_checker_image(), 0, 0, 96, 96)
    img_caption = Label2D("IMAGE2D  static | animated", 0, 0, px=14,
                          color=(0.8, 0.8, 0.85, 0.9))
    version_tag = Label2D("INTERFACES v1.1", 0, 0, px=14,
                          color=(0.5, 0.6, 0.7, 0.9))
    hint = Label2D("UI floats over the world - try resizing the window", 0, 0,
                   px=14, color=(0.7, 0.7, 0.75, 0.8))

    for item in (panel_bg, panel_frame, title, divider, slider_track, knob,
                 readout, clock_frame, clock_hand, img_static, img_anim,
                 img_caption, version_tag, hint):
        ov.add(item)

    state = {"t": 0.0, "img_timer": 0.0, "img_k": 8}

    def _relayout(w, h):
        pw = int(w * 0.30)
        x0 = w - pw
        panel_bg.set_rect(x0, 0, pw, h)
        panel_frame.set_rect(x0 + 2, 2, pw - 4, h - 4)
        title.set_pos(x0 + (pw - ov.text_width(title.text, title.px)) / 2.0,
                      h - 34)
        divider.set_points(x0 + 12, h - 48, x0 + pw - 12, h - 48)

        # slider: knob position and readout driven by the 10 Hz tick
        c1 = 2.5 * math.sin(state["t"] * 0.7)
        tx0, tx1, ty = x0 + 24, x0 + pw - 24, h - 100
        slider_track.set_points(tx0, ty, tx1, ty)
        frac = (c1 + 2.5) / 5.0
        knob.set_rect(tx0 + frac * (tx1 - tx0) - 5, ty - 9, 10, 18)
        readout.set_text("c1 = %+.2f" % c1)
        readout.set_pos(tx0, ty - 36)

        # clock: a rotating Line2D inside a frame
        cx, cy = x0 + pw / 2.0, h - 220.0
        clock_frame.set_rect(cx - 45, cy - 45, 90, 90)
        ang = state["t"] * 1.5
        clock_hand.set_points(cx, cy, cx + 38 * math.cos(ang),
                              cy + 38 * math.sin(ang))

        # images along the panel bottom
        img_static.set_rect(x0 + 20, 60, 96, 96)
        img_anim.set_rect(x0 + pw - 20 - 96, 60, 96, 96)
        img_caption.set_pos(x0 + 20, 40)
        version_tag.set_pos(x0 + pw - 14 - ov.text_width(version_tag.text,
                                                         version_tag.px), 14)
        hint.set_pos(14, 14)

    def tick(dt):
        state["t"] += dt
        state["img_timer"] += dt
        if state["img_timer"] >= 1.0:
            state["img_timer"] = 0.0
            state["img_k"] = {8: 16, 16: 4, 4: 8}[state["img_k"]]
            img_anim.set_image(_checker_image(k=state["img_k"]))

    def frame(alpha):
        w, h = forge.window.get_framebuffer_size()
        if w > 0 and h > 0:
            _relayout(w, h)
        forge.camera.orbit_input(0.002, 0.0, 0.0)
        forge.set_debug_lines(["overlay2d demo", "items: 14",
                               "t = %.1f" % state["t"]])

    forge.run(tick, frame)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("OVERLAY2D DEMO CRASH\n\n" + traceback.format_exc())
        print("Something broke - please copy crashlog.txt to the team.")
        raise
