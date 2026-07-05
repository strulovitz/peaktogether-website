Wonderful news!!! 🎉 B1 confirmed on all fronts — and since you didn't flag the panel darkness, I'm keeping 0.75 translucency for now (it stays a one-number knob we can change any time; in today's package I use a slightly more solid 0.85 behind the matrix so numbers are easier to read — you'll see both and can tell me which feels better).

Now B2 — the widget kit: the five Navigator controls from the Apocrypha (Button, Slider, MatrixGrid, ValueReadout, HintCard), plus the WidgetManager that routes the mouse (hit-test topmost-first, drag capture until release, wheel to the hovered widget). Mouse only — the keyboard belongs to the Pilot and does nothing in a panel, by law. Both files are NEW — zero shared files touched — so nothing that works today is at risk.

The demo is a little linear-algebra playground on purpose: it shows a 3x3 matrix whose starting rank is 2, and editing the bottom row can raise it to 3 — with the rank verdict computed live by the real referee, never by the widget. That's the A = C @ R build-preview economy being born.

FILE 1 of 2 — widgets.py (new file, complete):

"""
widgets.py — the Navigator's mouse-only widget kit (APOCRYPHA 3.3, package B2).

The five widgets: Button, Slider, MatrixGrid, ValueReadout, HintCard.
Plus WidgetManager, which routes PointerState (10 Hz, from helm) to widgets:
hit-testing topmost-first (last added wins), a press inside a widget captures
the pointer until primary release, wheel goes to the hovered widget.

Built entirely on the overlay2d vocabulary (INTERFACES v1.1). Widgets are
retained: each creates its overlay2d items on first draw() and only updates
them afterwards. Coordinates: window pixels, origin BOTTOM-LEFT.

There is NO keyboard input to widgets, EVER (the keyboard belongs to the
Pilot), no focus system, and no scrolling layouts (APOCRYPHA 3.3).

DEEPSEEK: fix the import below to the house layout if needed.
"""

import numpy as np

from overlay2d import Rect2D, Line2D, Label2D

# ---- house palette ----------------------------------------------------------
CYAN = (0.35, 0.75, 1.0, 0.9)
CYAN_DIM = (0.35, 0.75, 1.0, 0.45)
TEXT = (0.85, 0.95, 1.0, 1.0)
TEXT_DIM = (0.55, 0.65, 0.75, 0.9)
ACCENT = (1.0, 0.85, 0.3, 1.0)           # yellow: live values, knobs, edits
BG = (0.05, 0.09, 0.13, 0.92)
BG_HOVER = (0.10, 0.17, 0.24, 0.95)
DISABLED = (0.4, 0.45, 0.5, 0.5)


class Widget:
    """Base widget. Lifecycle: construct -> set_rect(...) -> manager.add(...);
    the manager calls draw(overlay) once per frame and on_pointer(ps) once per
    pulse while the widget is hovered or captured."""

    def __init__(self):
        self.rect = (0.0, 0.0, 10.0, 10.0)   # x, y, w, h — px, bottom-left
        self.visible = True
        self.enabled = True
        self.hover = False
        self._items = []
        self._ov = None
        self._prev_primary = False

    def set_rect(self, x, y, w, h):
        self.rect = (float(x), float(y), float(w), float(h))

    def contains(self, px, py):
        x, y, w, h = self.rect
        return (x <= px <= x + w) and (y <= py <= y + h)

    def draw(self, overlay):
        if self._ov is None:
            self._ov = overlay
            self._build(overlay)
        for it in self._items:
            it.visible = self.visible
        if self.visible:
            self._layout(overlay)

    def detach(self):
        if self._ov is not None:
            for it in self._items:
                self._ov.remove(it)
        self._items = []
        self._ov = None

    def on_pointer(self, ps):
        """Returns True to capture the pointer until primary release."""
        pressed = ps.primary and not self._prev_primary
        released = (not ps.primary) and self._prev_primary
        self._prev_primary = ps.primary
        capture = False
        if pressed and self.enabled and self.contains(ps.x, ps.y):
            capture = bool(self._press(ps))
        elif ps.primary and self.enabled:
            self._drag(ps)
        if released:
            self._release(ps)
        if ps.wheel and self.enabled and self.contains(ps.x, ps.y):
            self._wheel(ps)
        return capture

    def on_pointer_idle(self):
        """Called by the manager when the pointer moves elsewhere."""
        self._prev_primary = False

    # -- subclass hooks --
    def _build(self, ov): pass
    def _layout(self, ov): pass
    def _press(self, ps): return False
    def _drag(self, ps): pass
    def _release(self, ps): pass
    def _wheel(self, ps): pass

    def _add(self, ov, item):
        ov.add(item)
        self._items.append(item)
        return item


class WidgetManager:
    """Owns the widget list; call on_pointer(ps) once per PULSE and draw()
    once per FRAME. Hit-tests topmost-first (reverse add order)."""

    def __init__(self, overlay):
        self._ov = overlay
        self._widgets = []
        self._captured = None
        self._hovered = None

    def add(self, widget):
        if widget not in self._widgets:
            self._widgets.append(widget)
        return widget

    def remove(self, widget):
        if widget in self._widgets:
            self._widgets.remove(widget)
        widget.detach()
        if self._captured is widget:
            self._captured = None
        if self._hovered is widget:
            self._hovered = None

    def on_pointer(self, ps):
        if self._captured is not None:
            self._captured.on_pointer(ps)
            if not ps.primary:
                self._captured = None
            return
        target = None
        for w in reversed(self._widgets):
            if w.visible and w.enabled is not None and w.contains(ps.x, ps.y):
                target = w
                break
        if self._hovered is not target:
            if self._hovered is not None:
                self._hovered.hover = False
                self._hovered.on_pointer_idle()
            self._hovered = target
            if target is not None:
                target.hover = True
        if target is not None and target.on_pointer(ps):
            self._captured = target

    def draw(self):
        for w in self._widgets:
            w.draw(self._ov)


class Button(Widget):
    """Click = fires on press. .enabled=False greys it out (APOCRYPHA 3.4:
    e.g. the LEAST SQUARES button is disabled when an exact solution exists)."""

    def __init__(self, label, on_click):
        super().__init__()
        self.label = str(label)
        self.on_click = on_click
        self.rect = (0.0, 0.0, 150.0, 28.0)

    def _build(self, ov):
        self._bg = self._add(ov, Rect2D(0, 0, 1, 1, BG, filled=True))
        self._frame = self._add(ov, Rect2D(0, 0, 1, 1, CYAN, filled=False))
        self._text = self._add(ov, Label2D(self.label, 0, 0, px=15, color=TEXT))

    def _layout(self, ov):
        x, y, w, h = self.rect
        self._bg.set_rect(x, y, w, h)
        self._bg.set_color(BG_HOVER if (self.hover and self.enabled) else BG)
        self._frame.set_rect(x, y, w, h)
        self._frame.set_color(CYAN if self.enabled else DISABLED)
        self._text.set_text(self.label)
        self._text.set_color(TEXT if self.enabled else DISABLED)
        tw = ov.text_width(self.label, 15)
        self._text.set_pos(x + (w - tw) / 2.0, y + (h - 15.0) / 2.0)

    def _press(self, ps):
        if self.on_click is not None:
            self.on_click()
        return False


class Slider(Widget):
    """Drag the knob (or click the track); wheel = one fine step (APOCRYPHA
    3.3). Calls on_change(value) whenever the value actually changes."""

    def __init__(self, label, lo, hi, step, on_change):
        super().__init__()
        self.label = str(label)
        self.lo = float(lo)
        self.hi = float(hi)
        self.step = float(step)
        self.on_change = on_change
        self.value = float(lo)
        self.rect = (0.0, 0.0, 220.0, 44.0)

    def set_value(self, v, fire=False):
        v = min(self.hi, max(self.lo, float(v)))
        if self.step > 0:
            v = self.lo + round((v - self.lo) / self.step) * self.step
            v = min(self.hi, max(self.lo, v))
        if v != self.value:
            self.value = v
            if fire and self.on_change is not None:
                self.on_change(v)

    def _build(self, ov):
        self._label = self._add(ov, Label2D(self.label, 0, 0, px=14, color=TEXT_DIM))
        self._val = self._add(ov, Label2D("", 0, 0, px=14, color=ACCENT))
        self._track = self._add(ov, Line2D(0, 0, 0, 0, CYAN_DIM))
        self._track.thickness = 2.0
        self._knob = self._add(ov, Rect2D(0, 0, 10, 16, ACCENT, filled=True))

    def _layout(self, ov):
        x, y, w, h = self.rect
        self._label.set_text(self.label)
        self._label.set_pos(x, y + h - 14)
        vtxt = "%+.2f" % self.value
        self._val.set_text(vtxt)
        self._val.set_pos(x + w - ov.text_width(vtxt, 14), y + h - 14)
        ty = y + 10.0
        self._track.set_points(x + 5, ty, x + w - 5, ty)
        span = (self.hi - self.lo) or 1.0
        frac = (self.value - self.lo) / span
        self._knob.set_rect(x + 5 + frac * (w - 10) - 5, ty - 8, 10, 16)
        self._knob.set_color(ACCENT if self.enabled else DISABLED)

    def _value_from_x(self, px):
        x, _, w, _ = self.rect
        frac = min(1.0, max(0.0, (px - (x + 5)) / max(1.0, w - 10)))
        self.set_value(self.lo + frac * (self.hi - self.lo), fire=True)

    def _press(self, ps):
        self._value_from_x(ps.x)
        return True                       # capture: keep dragging off-widget

    def _drag(self, ps):
        self._value_from_x(ps.x)

    def _wheel(self, ps):
        self.set_value(self.value + self.step * ps.wheel, fire=True)


class MatrixGrid(Widget):
    """Displays a numpy array; editable cells (mask) change by wheel or by
    click-dragging up/down, in steps of .step (default 1.0). Row 0 is displayed
    at the TOP (matrix convention). Calls on_edit(i, j, new_value)."""

    CELL_W = 56.0
    CELL_H = 24.0
    PAD = 8.0

    def __init__(self, rows, cols, editable_mask, on_edit):
        super().__init__()
        self.rows = int(rows)
        self.cols = int(cols)
        if editable_mask is None:
            editable_mask = np.zeros((self.rows, self.cols), dtype=bool)
        self.editable = np.array(editable_mask, dtype=bool).reshape(self.rows, self.cols)
        self.on_edit = on_edit
        self.matrix = np.zeros((self.rows, self.cols), dtype=np.float64)
        self.step = 1.0
        w = self.cols * self.CELL_W + 2 * self.PAD
        h = self.rows * self.CELL_H + 2 * self.PAD
        self.rect = (0.0, 0.0, w, h)
        self._hover_cell = None
        self._drag_cell = None
        self._drag_y0 = 0.0
        self._drag_v0 = 0.0

    def set_matrix(self, M):
        M = np.asarray(M, dtype=np.float64)
        if M.shape != (self.rows, self.cols):
            raise ValueError("MatrixGrid expects shape (%d,%d), got %r"
                             % (self.rows, self.cols, M.shape))
        self.matrix = M.copy()

    def _build(self, ov):
        self._bg = self._add(ov, Rect2D(0, 0, 1, 1, (0.03, 0.06, 0.09, 0.85), filled=True))
        self._frame = self._add(ov, Rect2D(0, 0, 1, 1, CYAN_DIM, filled=False))
        self._eframes = {}
        for i in range(self.rows):
            for j in range(self.cols):
                if self.editable[i, j]:
                    self._eframes[(i, j)] = self._add(
                        ov, Rect2D(0, 0, 1, 1, CYAN_DIM, filled=False))
        self._hover_rect = self._add(ov, Rect2D(0, 0, 1, 1, ACCENT, filled=False))
        self._labels = [[self._add(ov, Label2D("", 0, 0, px=14, color=TEXT))
                         for _ in range(self.cols)] for _ in range(self.rows)]

    def _cell_origin(self, i, j):
        x, y, _, _ = self.rect
        return (x + self.PAD + j * self.CELL_W,
                y + self.PAD + (self.rows - 1 - i) * self.CELL_H)

    def _layout(self, ov):
        x, y, w, h = self.rect
        self._bg.set_rect(x, y, w, h)
        self._frame.set_rect(x, y, w, h)
        for i in range(self.rows):
            for j in range(self.cols):
                cx, cy = self._cell_origin(i, j)
                lab = self._labels[i][j]
                txt = "%.4g" % self.matrix[i, j]
                lab.set_text(txt)
                lab.set_pos(cx + (self.CELL_W - ov.text_width(txt, 14)) / 2.0,
                            cy + (self.CELL_H - 14.0) / 2.0)
                lab.set_color(ACCENT if self.editable[i, j] else TEXT)
        for (i, j), fr in self._eframes.items():
            cx, cy = self._cell_origin(i, j)
            fr.set_rect(cx + 2, cy + 2, self.CELL_W - 4, self.CELL_H - 4)
        hc = self._hover_cell
        if hc is not None and self.editable[hc]:
            cx, cy = self._cell_origin(*hc)
            self._hover_rect.set_rect(cx + 2, cy + 2, self.CELL_W - 4, self.CELL_H - 4)
            self._hover_rect.visible = True
        else:
            self._hover_rect.visible = False

    def _cell_at(self, px, py):
        x, y, _, _ = self.rect
        j = int((px - x - self.PAD) // self.CELL_W)
        i = self.rows - 1 - int((py - y - self.PAD) // self.CELL_H)
        if 0 <= i < self.rows and 0 <= j < self.cols:
            return (i, j)
        return None

    def on_pointer(self, ps):
        self._hover_cell = self._cell_at(ps.x, ps.y)
        return super().on_pointer(ps)

    def on_pointer_idle(self):
        self._hover_cell = None
        super().on_pointer_idle()

    def _set_cell(self, cell, v):
        v = float(v)
        if v != self.matrix[cell]:
            self.matrix[cell] = v
            if self.on_edit is not None:
                self.on_edit(cell[0], cell[1], v)

    def _press(self, ps):
        cell = self._cell_at(ps.x, ps.y)
        if cell is not None and self.editable[cell]:
            self._drag_cell = cell
            self._drag_y0 = ps.y
            self._drag_v0 = self.matrix[cell]
            return True
        return False

    def _drag(self, ps):
        if self._drag_cell is not None:
            steps = round((ps.y - self._drag_y0) / 8.0)
            self._set_cell(self._drag_cell, self._drag_v0 + steps * self.step)

    def _release(self, ps):
        self._drag_cell = None

    def _wheel(self, ps):
        cell = self._cell_at(ps.x, ps.y)
        if cell is not None and self.editable[cell]:
            self._set_cell(cell, self.matrix[cell] + self.step * ps.wheel)


class ValueReadout(Widget):
    """One line: dim label on the left, bright value on the right.
    fmt is a %-format string applied to set_value's argument."""

    def __init__(self, label, fmt="%s"):
        super().__init__()
        self.label = str(label)
        self.fmt = fmt
        self.value = None
        self.rect = (0.0, 0.0, 200.0, 20.0)

    def set_value(self, v):
        self.value = v

    def _build(self, ov):
        self._lab = self._add(ov, Label2D(self.label, 0, 0, px=14, color=TEXT_DIM))
        self._val = self._add(ov, Label2D("", 0, 0, px=14, color=ACCENT))

    def _layout(self, ov):
        x, y, w, h = self.rect
        self._lab.set_text(self.label)
        self._lab.set_pos(x, y)
        if self.value is None:
            txt = ""
        else:
            try:
                txt = self.fmt % self.value
            except TypeError:
                txt = str(self.value)
        self._val.set_text(txt)
        self._val.set_pos(x + w - ov.text_width(txt, 14), y)


class HintCard(Widget):
    """Boxed multi-line text; optional citation line rendered small underneath
    (APOCRYPHA 3.3). The number of lines is fixed after first draw."""

    LINE_H = 20.0

    def __init__(self, text_lines, cite=""):
        super().__init__()
        self.lines = [str(t) for t in text_lines]
        self.cite = str(cite)
        w = 320.0
        h = 16.0 + self.LINE_H * len(self.lines) + (16.0 if self.cite else 0.0)
        self.rect = (0.0, 0.0, w, h)

    def _build(self, ov):
        self._bg = self._add(ov, Rect2D(0, 0, 1, 1, BG, filled=True))
        self._frame = self._add(ov, Rect2D(0, 0, 1, 1, CYAN_DIM, filled=False))
        self._labs = [self._add(ov, Label2D("", 0, 0, px=14, color=TEXT))
                      for _ in self.lines]
        self._cite = self._add(ov, Label2D(self.cite, 0, 0, px=11, color=TEXT_DIM))

    def _layout(self, ov):
        if len(self.lines) != len(self._labs):
            raise ValueError("HintCard line count is fixed after first draw; "
                             "create a new card instead.")
        x, y, w, h = self.rect
        self._bg.set_rect(x, y, w, h)
        self._frame.set_rect(x, y, w, h)
        for k, lab in enumerate(self._labs):
            lab.set_text(self.lines[k])
            lab.set_pos(x + 10, y + h - 26 - self.LINE_H * k)
        self._cite.set_text(self.cite)
        self._cite.set_pos(x + 10, y + 6)
        self._cite.visible = bool(self.cite) and self.visible

FILE 2 of 2 — widgets_demo.py (new file, complete):

"""
widgets_demo.py — acceptance demo for the widget kit (package B2).

Run from the repo root:   python widgets_demo.py

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
    from vobjects import Grid, Arrow      # DEEPSEEK: fix to house layout
    from overlay2d import Rect2D, Label2D
    from widgets import (WidgetManager, Button, Slider, MatrixGrid,
                         ValueReadout, HintCard)
    # DEEPSEEK: point this at the real referee module (the one with rank,
    # is_solvable, least_squares...). NEVER substitute np.linalg.matrix_rank.
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

FOR DEEPSEEK — tasks:

    Save both files at the repo root (flat layout, as I now understand from your run commands). Fix the marked import lines to the house names: the Forge class module, the vobjects module, the Helm module, and — most important — the real referee module for rank (never substitute a numpy re-implementation; the referee is the sole authority).
    No shared files are edited in B2, so no regression risk; a quick python fleet_demo.py sanity check is optional.
    Record in COMMENTARIES.md: "B2 shipped: widgets.py (Button, Slider, MatrixGrid, ValueReadout, HintCard + WidgetManager with drag capture, per APOCRYPHA 3.3) and widgets_demo.py. Widget constructors match the frozen APOCRYPHA signatures; positions set via set_rect after construction. MatrixGrid: wheel = step, click-drag vertical = step per 8 px, .step attr default 1.0."

Commit message: bridge: add widget kit (B2) - Button/Slider/MatrixGrid/ValueReadout/HintCard + WidgetManager, mouse-only per APOCRYPHA 3.3, with acceptance demo

WHAT YOU SHOULD SEE (Nir — run python widgets_demo.py from the repo root):

    The familiar backdrop (grid, arrow, slow camera) with a console panel on the right — slightly more solid than last time (0.85 vs 0.75; tell me which you prefer).
    Top: "FLEET RANK 2 / 3" and a 3x3 matrix of yellow numbers: top row 2 1 3, middle row 0 3 3, bottom row 0 0 0.
    The centerpiece: hover a matrix cell (a yellow box highlights it), roll the mouse wheel or click-drag up/down — the number changes in steps of 1. The moment you make the bottom row nonzero, RANK jumps to "3 / 3". Zero the bottom row again and it falls back to 2. The verdict comes from the game's real referee, live, every edit.
    A "THROTTLE c1" slider: drag the yellow knob (notice it snaps to halves: -3.00, -2.50, ...), or hover it and roll the wheel for one fine step at a time. The "c1" readout follows.
    Two buttons: "BUILD FIGHTER" lights up when hovered and each click updates "LAST ORDER: BUILD fighter #1, #2, ..."; "LEAST SQUARES" is grey and refuses to react — that's the disabled style the combat console will use.
    A hint card at the panel bottom with instructions and a small dim citation line.
    Keyboard: press anything — the panel must completely ignore it.
    Resize the window: everything re-sticks.

REPORT BACK, please: (1) runs without crashlog? (2) do the buttons/slider/matrix all feel responsive and pleasant with the mouse — especially: does the wheel-over-cell editing feel good, and is the click-drag-to-change-value discoverable/comfortable? (3) any lag between moving the mouse and the highlight following it? (be honest — the UI updates 10 times per second by design, and I want to know if that feels fine or sluggish) (4) panel darkness: 0.85 here vs 0.75 in demo2d — which do you like?

Next after your report: B3 — the console itself (console.py): the FLEET ZONE showing the real fleet matrix A with ships as columns, wired into the live game via the root app — the moment this game truly becomes two-player. That one WILL touch the shared root app.py, so I'll re-emit it whole, per doctrine. 🚀
