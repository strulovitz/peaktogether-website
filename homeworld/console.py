"""
console.py — the Navigator's bridge console (package B3).

B3 scope: the FLEET ZONE (APOCRYPHA 3.4, zone 1): the live fleet matrix A with
SHIPS AS COLUMNS (channel rows labeled K,B,M,S,J,U), a RANK readout, a
RESOURCES readout, and the selected ship's column highlighted — the selection
follows the Pilot's TAB key. Shared state, one forced conversation.

Wiring contract (root app):
    bridge = Bridge(forge.overlay2d)
    bridge.on_pulse(pointer, snap, selected_id)   # once per 10 Hz pulse
    bridge.on_frame(w, h)                         # once per display frame

The Bridge never mutates fleet state; it reads snapshots only. Mouse only.
"""

import numpy as np

from overlay2d import Rect2D, Label2D
from widgets import (WidgetManager, MatrixGrid, ValueReadout,
                     CYAN, TEXT_DIM, ACCENT)

ROW_NAMES = ("K", "B", "M", "S", "J", "U")

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
    """The Navigator's console. Owns the right panel and a WidgetManager."""

    PANEL_FRAC = 0.30

    def __init__(self, overlay):
        self._ov = overlay
        self._manager = WidgetManager(overlay)

        # panel chrome first, so all widgets paint over it
        self._panel_bg = Rect2D(0, 0, 10, 10, (0.05, 0.09, 0.13, 0.85),
                                filled=True)
        self._panel_frame = Rect2D(0, 0, 10, 10, CYAN, filled=False)
        self._title = Label2D("BRIDGE - FLEET", 0, 0, px=16,
                              color=(0.7, 0.95, 1.0, 1.0))
        overlay.add(self._panel_bg)
        overlay.add(self._panel_frame)
        overlay.add(self._title)

        self._rank_ro = self._manager.add(ValueReadout("FLEET RANK", "%s"))
        self._res_ro = self._manager.add(ValueReadout("RESOURCES", "%.0f"))
        self._sel_ro = self._manager.add(ValueReadout("SELECTED", "%s"))

        self._mg = None            # the fleet MatrixGrid (read-only)
        self._ids = None           # ship id tuple the grid was built for
        self._pw = -1              # panel width the grid was built for
        self._snap = None
        self._selected = None
        self._chrome = []          # row labels + column headers + highlight
        self._row_labels = []
        self._col_headers = []
        self._sel_col_rect = None

    # ---- once per pulse ---------------------------------------------------

    def on_pulse(self, pointer, snap, selected_id):
        self._snap = snap
        self._selected = selected_id
        if snap is not None:
            self._rank_ro.set_value("%d / 6" % snap.rank)
            self._res_ro.set_value(snap.resources)
            ids = tuple(snap.ship_ids)
            txt = "-"
            if selected_id in ids:
                j = ids.index(selected_id)
                sq = int(snap.squad[j])
                txt = "#%d %s%s" % (selected_id, _abbrev(snap.klasses[j]),
                                    ("  squad %d" % sq) if sq > 0 else "")
            self._sel_ro.set_value(txt)
        self._manager.on_pointer(pointer)

    # ---- once per frame ---------------------------------------------------

    def on_frame(self, w, h):
        pw = int(w * self.PANEL_FRAC)
        x0 = w - pw
        self._panel_bg.set_rect(x0, 0, pw, h)
        self._panel_frame.set_rect(x0 + 2, 2, pw - 4, h - 4)
        self._title.set_pos(
            x0 + (pw - self._ov.text_width(self._title.text, 16)) / 2.0,
            h - 34)

        snap = self._snap
        if snap is None:
            self._manager.draw()
            return

        ids = tuple(snap.ship_ids)
        if ids != self._ids or abs(pw - self._pw) > 1:
            self._rebuild(len(ids), pw)
            self._ids = ids
            self._pw = pw

        self._rank_ro.set_rect(x0 + 16, h - 64, pw - 32, 20)
        self._res_ro.set_rect(x0 + 16, h - 86, pw - 32, 20)
        self._sel_ro.set_rect(x0 + 16, h - 108, pw - 32, 20)

        mg = self._mg
        if mg is not None:
            gw, gh = mg.rect[2], mg.rect[3]
            mg.set_rect(x0 + 40.0, h - 150.0 - gh, gw, gh)
            if len(ids) == mg.cols and snap.fleet_matrix.shape == (6, mg.cols):
                mg.set_matrix(snap.fleet_matrix)

        self._manager.draw()       # builds/updates widget items
        self._update_chrome()      # then chrome, so it paints on top

    # ---- internals ----------------------------------------------------------

    def _rebuild(self, n, pw):
        if self._mg is not None:
            self._manager.remove(self._mg)
            self._mg = None
        self._remove_chrome()
        if n == 0:
            return
        mg = MatrixGrid(6, n, None, None)   # no editable cells: read-only
        mg.CELL_W = max(28.0, min(44.0, (pw - 88.0) / n))
        mg.CELL_H = 22.0
        mg.rect = (0.0, 0.0,
                   n * mg.CELL_W + 2 * mg.PAD,
                   6 * mg.CELL_H + 2 * mg.PAD)
        self._mg = self._manager.add(mg)

    def _remove_chrome(self):
        for it in self._chrome:
            self._ov.remove(it)
        self._chrome = []
        self._row_labels = []
        self._col_headers = []
        self._sel_col_rect = None

    def _update_chrome(self):
        mg = self._mg
        snap = self._snap
        if mg is None or snap is None:
            return
        ids = tuple(snap.ship_ids)
        n = len(ids)
        if not self._chrome:
            self._sel_col_rect = Rect2D(0, 0, 1, 1, ACCENT, filled=False)
            self._sel_col_rect.thickness = 2.0
            self._ov.add(self._sel_col_rect)
            self._chrome.append(self._sel_col_rect)
            for name in ROW_NAMES:
                lab = Label2D(name, 0, 0, px=14, color=TEXT_DIM)
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
            cy = gy + mg.PAD + (5 - i) * mg.CELL_H + (mg.CELL_H - 14.0) / 2.0
            lab.set_pos(gx - 16.0, cy)

        sel_j = ids.index(self._selected) if self._selected in ids else None
        for j, lab in enumerate(self._col_headers):
            sq = int(snap.squad[j])
            txt = _abbrev(snap.klasses[j]) + (str(sq) if sq > 0 else "")
            lab.set_text(txt)
            cx = gx + mg.PAD + j * mg.CELL_W
            lab.set_pos(cx + (mg.CELL_W - self._ov.text_width(txt, 12)) / 2.0,
                        gy + gh + 6.0)
            lab.set_color(ACCENT if j == sel_j else TEXT_DIM)

        if sel_j is None:
            self._sel_col_rect.visible = False
        else:
            self._sel_col_rect.visible = True
            self._sel_col_rect.set_rect(
                gx + mg.PAD + sel_j * mg.CELL_W + 1.0, gy + mg.PAD,
                mg.CELL_W - 2.0, 6 * mg.CELL_H)
