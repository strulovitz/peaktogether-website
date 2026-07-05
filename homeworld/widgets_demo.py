"""
widgets_demo.py — acceptance demo for the widget kit (package B2).

Run from the homeworld/ folder:   python widgets_demo.py

Mouse only: click the buttons, drag the slider knob (wheel = fine step),
wheel/drag the yellow matrix cells. The RANK readout is computed live by the
real referee — edit the bottom row and watch the rank rise from 2 to 3.
The keyboard deliberately does nothing here (it belongs to the Pilot).
"""

import json
import os
import traceback

import numpy as np


def _load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"width": 1280, "height": 720}


def main():
    from forge import Forge
    from helm import Helm
    from vobjects import Grid, Arrow
    from overlay2d import Rect2D, Label2D
    from widgets import (WidgetManager, Button, Slider, MatrixGrid,
                         ValueReadout, HintCard)
    from referee import rank

    settings = dict(_load_settings())
    settings["title"] = "WIDGETS demo (B2)"
    forge = Forge(settings)
    helm = Helm(settings)
    helm.attach(forge.window)
    ov = forge.overlay2d

    # ---- backdrop: a little 3D world ------------------------------------
    grid3d = Grid(np.array([0.0, 0.0, 0.0]),
                  np.array([1.0, 0.0, 0.0]),
                  np.array([0.0, 0.0, 1.0]), n=10, spacing=2.0)
    grid3d.set_color((0.12, 0.42, 0.55, 0.4))
    arrow = Arrow(np.array([0.0, 0.0, 0.0]), np.array([4.0, 3.0, 2.0]))
    forge.add(grid3d)
    forge.add(arrow)
    forge.camera.set_orbit(np.array([0.0, 0.0, 0.0]))
    forge.camera.distance = 28.0
    forge.camera.pitch = 0.45

    # ---- panel chrome (plain overlay2d items, added BEFORE the widgets so
    #      the widgets paint on top) --------------------------------------
    panel_bg = Rect2D(0, 0, 10, 10, (0.05, 0.09, 0.13, 0.85), filled=True)
    panel_frame = Rect2D(0, 0, 10, 10, (0.35, 0.75, 1.0, 0.9), filled=False)
    title = Label2D("WIDGET KIT - B2", 0, 0, px=16, color=(0.7, 0.95, 1.0, 1.0))
    ov.add(panel_bg)
    ov.add(panel_frame)
    ov.add(title)

    # ---- the widgets ------------------------------------------------------
    manager = WidgetManager(ov)

    rank_ro = manager.add(ValueReadout("FLEET RANK", "%s"))
    mg = manager.add(MatrixGrid(3, 3, np.ones((3, 3), dtype=bool), None))
    mg.set_matrix(np.array([[2.0, 1.0, 3.0],
                            [0.0, 3.0, 3.0],
                            [0.0, 0.0, 0.0]]))

    def refresh_rank(*_):
        rank_ro.set_value("%d / 3" % rank(mg.matrix))
    mg.on_edit = refresh_rank
    refresh_rank()

    c1_ro = manager.add(ValueReadout("c1", "%s"))
    slider = manager.add(Slider("THROTTLE c1", -3.0, 3.0, 0.5,
                                lambda v: c1_ro.set_value("%+.2f" % v)))
    slider.set_value(0.0)
    c1_ro.set_value("%+.2f" % 0.0)

    state = {"built": 0}
    last_ro = manager.add(ValueReadout("LAST ORDER", "%s"))

    def on_build():
        state["built"] += 1
        last_ro.set_value("BUILD fighter #%d" % state["built"])
    build_btn = manager.add(Button("BUILD FIGHTER", on_build))

    ls_btn = manager.add(Button("LEAST SQUARES", lambda: None))
    ls_btn.enabled = False        # the greyed-out style (APOCRYPHA 3.4)

    hint = manager.add(HintCard(
        ["Yellow cells are editable:",
         "wheel = step 1, or click-drag",
         "up/down. Make the bottom row",
         "nonzero and watch RANK hit 3."],
        cite="widgets demo - B2"))

    def _relayout(w, h):
        pw = int(w * 0.30)
        x0 = w - pw
        panel_bg.set_rect(x0, 0, pw, h)
        panel_frame.set_rect(x0 + 2, 2, pw - 4, h - 4)
        title.set_pos(x0 + (pw - ov.text_width(title.text, title.px)) / 2.0,
                      h - 34)
        rank_ro.set_rect(x0 + 16, h - 66, pw - 32, 20)
        gw, gh = mg.rect[2], mg.rect[3]
        mg.set_rect(x0 + (pw - gw) / 2.0, h - 84 - gh, gw, gh)
        sy = h - 84 - gh - 66
        slider.set_rect(x0 + 16, sy, pw - 32, 44)
        c1_ro.set_rect(x0 + 16, sy - 24, pw - 32, 20)
        by = sy - 70
        build_btn.set_rect(x0 + 16, by, (pw - 42) / 2.0, 28)
        ls_btn.set_rect(x0 + 26 + (pw - 42) / 2.0, by, (pw - 42) / 2.0, 28)
        last_ro.set_rect(x0 + 16, by - 26, pw - 32, 20)
        hw, hh = hint.rect[2], hint.rect[3]
        hint.set_rect(x0 + (pw - min(hw, pw - 32)) / 2.0, 16,
                      min(hw, pw - 32), hh)

    def tick(dt):
        events, axes, pointer = helm.poll()
        manager.on_pointer(pointer)       # the entire Navigator input path

    def frame(alpha):
        w, h = forge.window.get_framebuffer_size()
        if w > 0 and h > 0:
            _relayout(w, h)
        manager.draw()
        forge.camera.orbit_input(0.002, 0.0, 0.0)
        forge.set_debug_lines(["widgets demo (B2)",
                               "rank readout via referee.rank"])

    forge.run(tick, frame)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("WIDGETS DEMO CRASH\n\n" + traceback.format_exc())
        print("Something broke - please copy crashlog.txt to the team.")
        raise
