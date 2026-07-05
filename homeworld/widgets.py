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
