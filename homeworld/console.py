"""
console.py — the Navigator's bridge console (corrected B3).

Part 2 §2.1 / M1 / M8 / M10: ALWAYS SPACE. Three zones:

  FORMATION P — the commanded squad's positions as a live matrix: one column
      per ship, rows e1/e2/e3 colored like the basis arrows. Column j IS
      ship j's position, measured from Mom at the origin. Updates every pulse.
  ORDER — the §2.1 coefficient sliders c1,c2,c3, wired to the SAME shared
      coefficients the Pilot's keys edit; dragging them moves the ghost
      construction in space. Fuel line: staged legs cost vs diagonal cost
      (the triangle inequality as an economy).
  TRANSFORM M — an editable 3x3 (starts identity). Non-identity M is ghost-
      previewed in space as p -> M @ p; readouts: det (volume factor,
      collapse warning), rank. APPLY fires ApplyTransform; RESET restores I;
      SCOPE toggles squad / whole fleet.

The console reads snapshots and shared UI state; it submits nothing directly —
it calls the two callbacks the shell provides (on_coeff, on_transform).
"""

import numpy as np

from overlay2d import Rect2D, Label2D
from widgets import (WidgetManager, MatrixGrid, Slider, Button, ValueReadout,
                     CYAN, TEXT_DIM, ACCENT)
from referee import rank, determinant

BASIS_COLORS = [(1.0, 0.3, 0.3, 1.0), (0.3, 1.0, 0.4, 1.0),
                (0.35, 0.55, 1.0, 1.0)]
ROW_NAMES = ("e1", "e2", "e3")
WARN = (1.0, 0.45, 0.35, 1.0)

KLASS_ABBREV = {
    "mothership": "MS",
    "fighter": "FT",
    "corvette": "CV",
    "collector": "CL",
    "frigate": "FG",
}


def _abbrev(klass):
    return KLASS_ABBREV.get(klass, str(klass)[:2].upper())


class Bridge:
    """The Navigator's console. on_coeff(i, value) and
    on_transform(matrix_tuple, scope_all) are provided by the shell."""

    PANEL_FRAC = 0.30

    def __init__(self, overlay, on_coeff=None, on_transform=None):
        self._ov = overlay
        self._on_coeff = on_coeff
        self._on_transform = on_transform
        self._manager = WidgetManager(overlay)
        self._snap = None
        self._ui = None
        self._scope_all = False

        # ---- static chrome (under the widgets) ----
        self._panel_bg = Rect2D(0, 0, 10, 10, (0.05, 0.09, 0.13, 0.85),
                                filled=True)
        self._panel_frame = Rect2D(0, 0, 10, 10, CYAN, filled=False)
        self._title = Label2D("BRIDGE", 0, 0, px=16, color=(0.7, 0.95, 1.0, 1.0))
        self._lab_p = Label2D("FORMATION P", 0, 0, px=13, color=TEXT_DIM)
        self._lab_o = Label2D("ORDER  c1*e1 + c2*e2 + c3*e3", 0, 0, px=13,
                              color=TEXT_DIM)
        self._lab_m = Label2D("TRANSFORM  p -> M p", 0, 0, px=13, color=TEXT_DIM)
        self._warn = Label2D("", 0, 0, px=12, color=WARN)
        for it in (self._panel_bg, self._panel_frame, self._title,
                   self._lab_p, self._lab_o, self._lab_m, self._warn):
            overlay.add(it)

        # ---- ORDER zone widgets ----
        self._sliders = []
        for i in range(3):
            cb = (lambda i_: lambda v: self._coeff_changed(i_, v))(i)
            self._sliders.append(self._manager.add(
                Slider("c%d * e%d" % (i + 1, i + 1), -4.0, 4.0, 0.5, cb)))
        self._cost_ro = self._manager.add(ValueReadout("FUEL", "%s"))

        # ---- TRANSFORM zone widgets ----
        self._mg_m = self._manager.add(
            MatrixGrid(3, 3, np.ones((3, 3), dtype=bool), None))
        self._mg_m.step = 0.5
        self._mg_m.set_matrix(np.eye(3))
        self._det_ro = self._manager.add(ValueReadout("DET M", "%s"))
        self._rank_ro = self._manager.add(ValueReadout("RANK M", "%s"))
        self._apply_btn = self._manager.add(
            Button("APPLY TRANSFORM", self._apply))
        self._reset_btn = self._manager.add(Button("RESET", self._reset))
        self._scope_btn = self._manager.add(
            Button("SCOPE: SQUAD 1", self._toggle_scope))

        # ---- FORMATION zone (rebuilt when the squad's members change) ----
        self._mg_p = None
        self._members = None       # tuple of ship ids shown as columns
        self._pw = -1
        self._chrome = []          # P-grid row labels, col headers, highlight
        self._row_labels = []
        self._col_headers = []
        self._sel_col_rect = None
        self._warn_visible = False

    # ---- shell-facing API ---------------------------------------------------

    @property
    def scope_all(self):
        return self._scope_all

    def transform_matrix(self):
        return self._mg_m.matrix.copy()

    def transform_active(self):
        return not np.allclose(self._mg_m.matrix, np.eye(3), atol=1e-12)

    # ---- once per pulse -------------------------------------------------------

    def on_pulse(self, pointer, snap, ui):
        self._snap = snap
        self._ui = ui
        if snap is not None and ui is not None:
            coeffs = ui["coeffs"]
            for i, s in enumerate(self._sliders):
                if i < len(coeffs):
                    s.set_value(float(coeffs[i]))
            E = [np.asarray(e, dtype=np.float64) for e in snap.engine_vectors]
            k = min(len(coeffs), len(E))
            legs = sum(abs(float(coeffs[i])) * float(np.linalg.norm(E[i]))
                       for i in range(k))
            d = np.zeros(3)
            for i in range(k):
                d = d + float(coeffs[i]) * E[i]
            diag = float(np.linalg.norm(d))
            mode = "diagonal" if ui["diagonal"] else "staged"
            self._cost_ro.set_value("legs %.1f | diag %.1f  (%s)"
                                    % (legs, diag, mode))

            M = self._mg_m.matrix
            det = determinant(M)
            r = rank(M)
            self._det_ro.set_value("%+.2f" % det)
            self._rank_ro.set_value("%d / 3" % r)
            if r == 3:
                self._warn_visible = False
                self._warn.set_text("")
            else:
                self._warn_visible = True
                target = {2: "A PLANE", 1: "A LINE", 0: "THE ORIGIN"}[r]
                self._warn.set_text("COLLAPSE TO %s" % target)

            self._apply_btn.enabled = self.transform_active()
            self._scope_btn.label = ("SCOPE: ALL" if self._scope_all
                                     else "SCOPE: SQUAD %d" % ui["squad"])
            self._lab_p.set_text("FORMATION P - %s"
                                 % ("FLEET" if self._scope_all
                                    else "SQUAD %d" % ui["squad"]))
        self._manager.on_pointer(pointer)

    # ---- once per frame -------------------------------------------------------

    def on_frame(self, w, h):
        pw = int(w * self.PANEL_FRAC)
        x0 = w - pw
        self._panel_bg.set_rect(x0, 0, pw, h)
        self._panel_frame.set_rect(x0 + 2, 2, pw - 4, h - 4)
        self._title.set_pos(
            x0 + (pw - self._ov.text_width(self._title.text, 16)) / 2.0, h - 34)

        snap, ui = self._snap, self._ui
        if snap is None or ui is None:
            self._manager.draw()
            return

        members = self._member_indices(snap, ui)
        ids = tuple(int(snap.ship_ids[j]) for j in members)
        if ids != self._members or abs(pw - self._pw) > 1:
            self._rebuild_p(len(ids), pw)
            self._members = ids
            self._pw = pw

        # FORMATION zone
        y = h - 56
        self._lab_p.set_pos(x0 + 16, y)
        gy_p = y
        if self._mg_p is not None:
            gw, gh = self._mg_p.rect[2], self._mg_p.rect[3]
            gy_p = y - 26 - gh
            self._mg_p.set_rect(x0 + 44, gy_p, gw, gh)
            if len(members) == self._mg_p.cols:
                P = snap.pos[list(members)].T   # 3 x n: columns are ships
                self._mg_p.set_matrix(P)
        y = gy_p - 28

        # ORDER zone
        self._lab_o.set_pos(x0 + 16, y)
        for i, s in enumerate(self._sliders):
            s.set_rect(x0 + 16, y - 50 - i * 48, pw - 32, 44)
        cost_y = y - 50 - 2 * 48 - 26
        self._cost_ro.set_rect(x0 + 16, cost_y, pw - 32, 20)
        y = cost_y - 30

        # TRANSFORM zone
        self._lab_m.set_pos(x0 + 16, y)
        gh_m = self._mg_m.rect[3]
        gy_m = y - 10 - gh_m
        self._mg_m.set_rect(x0 + 16, gy_m, self._mg_m.rect[2], gh_m)
        self._det_ro.set_rect(x0 + 210, gy_m + 56, pw - 226, 20)
        self._rank_ro.set_rect(x0 + 210, gy_m + 34, pw - 226, 20)
        self._warn.set_pos(x0 + 210, gy_m + 12)
        self._warn.visible = self._warn_visible
        by = gy_m - 36
        self._apply_btn.set_rect(x0 + 16, by, 160, 28)
        self._reset_btn.set_rect(x0 + 184, by, 80, 28)
        self._scope_btn.set_rect(x0 + 16, by - 34, 248, 26)

        self._manager.draw()
        self._update_p_chrome(snap, ui, members)

    # ---- internals -----------------------------------------------------------

    def _coeff_changed(self, i, v):
        if self._on_coeff is not None:
            self._on_coeff(i, float(v))

    def _apply(self):
        if self._on_transform is not None and self.transform_active():
            M = tuple(tuple(float(v) for v in row) for row in self._mg_m.matrix)
            self._on_transform(M, self._scope_all)
            self._mg_m.set_matrix(np.eye(3))

    def _reset(self):
        self._mg_m.set_matrix(np.eye(3))

    def _toggle_scope(self):
        self._scope_all = not self._scope_all

    def _member_indices(self, snap, ui):
        if self._scope_all:
            return tuple(range(len(snap.ship_ids)))
        return tuple(j for j in range(len(snap.ship_ids))
                     if int(snap.squad[j]) == int(ui["squad"]))

    def _rebuild_p(self, n, pw):
        if self._mg_p is not None:
            self._manager.remove(self._mg_p)
            self._mg_p = None
        self._remove_p_chrome()
        if n == 0:
            return
        mg = MatrixGrid(3, n, None, None)   # read-only: positions ARE the ships
        mg.CELL_W = max(30.0, min(64.0, (pw - 92.0) / n))
        mg.CELL_H = 22.0
        mg.rect = (0.0, 0.0, n * mg.CELL_W + 2 * mg.PAD,
                   3 * mg.CELL_H + 2 * mg.PAD)
        self._mg_p = self._manager.add(mg)

    def _remove_p_chrome(self):
        for it in self._chrome:
            self._ov.remove(it)
        self._chrome = []
        self._row_labels = []
        self._col_headers = []
        self._sel_col_rect = None

    def _update_p_chrome(self, snap, ui, members):
        mg = self._mg_p
        if mg is None:
            return
        n = len(members)
        if not self._chrome:
            self._sel_col_rect = Rect2D(0, 0, 1, 1, ACCENT, filled=False)
            self._sel_col_rect.thickness = 2.0
            self._ov.add(self._sel_col_rect)
            self._chrome.append(self._sel_col_rect)
            for i, name in enumerate(ROW_NAMES):
                lab = Label2D(name, 0, 0, px=13, color=BASIS_COLORS[i])
                self._ov.add(lab)
                self._chrome.append(lab)
                self._row_labels.append(lab)
            for _ in range(n):
                lab = Label2D("", 0, 0, px=12, color=TEXT_DIM)
                self._ov.add(lab)
                self._chrome.append(lab)
                self._col_headers.append(lab)

        gx, gy, gw, gh = mg.rect
        for i, lab in enumerate(self._row_labels):
            cy = gy + mg.PAD + (2 - i) * mg.CELL_H + (mg.CELL_H - 13.0) / 2.0
            lab.set_pos(gx - 24.0, cy)

        selected = ui["selected"]
        sel_j = None
        for jj, j in enumerate(members):
            sid = int(snap.ship_ids[j])
            if sid == selected:
                sel_j = jj
            lab = self._col_headers[jj]
            txt = "%s%d" % (_abbrev(snap.klasses[j]), sid)
            lab.set_text(txt)
            cx = gx + mg.PAD + jj * mg.CELL_W
            lab.set_pos(cx + (mg.CELL_W - self._ov.text_width(txt, 12)) / 2.0,
                        gy + gh + 6.0)
            lab.set_color(ACCENT if jj == sel_j else TEXT_DIM)

        if sel_j is None:
            self._sel_col_rect.visible = False
        else:
            self._sel_col_rect.visible = True
            self._sel_col_rect.set_rect(gx + mg.PAD + sel_j * mg.CELL_W + 1.0,
                                        gy + mg.PAD,
                                        mg.CELL_W - 2.0, 3 * mg.CELL_H)
