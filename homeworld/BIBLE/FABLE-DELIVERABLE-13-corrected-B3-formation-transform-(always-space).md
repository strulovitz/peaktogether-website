Building it now — the corrected B3, grounded in §2.1/M1/M8/M10. Five deliverables: a tiny referee addition, orders.py re-emitted whole (I have it verbatim now), an exact sim branch for DeepSeek to insert, and full rewrites of console.py and app.py.

PIECE 1 — append to referee.py (DeepSeek: add this function; referee stays the sole authority):

def determinant(M):
    """Signed determinant of a square matrix: the volume factor of the
    transform, with orientation (negative = reflection). Raw value — the
    tolerance doctrine applies to VERDICTS made from it, not to the number."""
    M = np.asarray(M, dtype=np.float64)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("determinant needs a square matrix, got %r" % (M.shape,))
    return float(np.linalg.det(M))

PIECE 2 — orders.py, whole file (unchanged except the new order + one docstring line):

"""THE FROZEN ORDER TYPES (NEW_TESTAMENT 3.3, version 1).

Both players feed one queue: the Pilot's controller and the
Navigator's console both translate their inputs into these orders
and submit them to FleetSim. Orders are validated at tick time;
invalid orders produce ORDER_REJECTED events that explain and
suggest — never punish (Iron Rule 3).

Owner-approved addition (corrected B3): ApplyTransform — Part 2
"always space": a matrix that moves the whole formation at once.
"""

from dataclasses import dataclass


@dataclass(frozen=True)                     # Bible 2.1
class MoveCombination:
    squad: int
    coeffs: tuple                            # one scalar per engine vector
    diagonal: bool                           # True: fly the diagonal;
                                             # False: component-by-component


@dataclass(frozen=True)                     # continuous, from TRIM axes
class Trim:
    ship_id: int
    direction: tuple                         # (dx, dy, dz), normalized inside


@dataclass(frozen=True)                     # Bible 2.2
class SetIntake:
    ship_id: int
    facing: tuple


@dataclass(frozen=True)                     # Bible 2.3 regimes 1 and 3
class FireSolution:
    group: tuple                             # firing ship ids
    target_id: int
    throttles: tuple                         # x: one throttle per group ship


@dataclass(frozen=True)                     # Bible 2.3 regime 2
class LeastSquaresFire:
    group: tuple
    target_id: int


@dataclass(frozen=True)                     # Bible 2.8
class GramSchmidtDrill:
    squad: int


@dataclass(frozen=True)                     # Bible 2.5 / 2.6 row-op missions
class RowOperation:
    kind: str                                # "subtract" | "swap" | "scale"
    i: int
    j: int
    multiplier: float                        # row_i <- row_i - m * row_j


@dataclass(frozen=True)
class BackSubstitute:
    values: tuple                            # the Navigator's x


@dataclass(frozen=True)
class BuildShip:
    klass: str


@dataclass(frozen=True)                     # Bible 2.7: deletes a grid row
class JamStation:
    station_id: int


@dataclass(frozen=True)
class AssignSquad:
    ship_ids: tuple
    squad: int


@dataclass(frozen=True)                     # Part 2 "always space" (M8/M10):
class ApplyTransform:                        # positions p -> M @ p, about the
    squad: int                               # origin (Mom). squad 0 = ALL ships
    matrix: tuple                            # 3x3, row-major tuple of tuples

PIECE 3 — sim.py insertion (DeepSeek: add ApplyTransform to sim's orders import, and add this branch inside _ingest, after the MoveCombination branch, same indentation):

        elif isinstance(order, ApplyTransform):
            members = [s for s in self.living()
                       if order.squad == 0 or s.squad == order.squad]
            if not members:
                return self._reject(events, order,
                                    f"squad {order.squad} has no ships")
            M = np.asarray(order.matrix, dtype=np.float64)
            if M.shape != (3, 3) or not np.all(np.isfinite(M)):
                return self._reject(events, order,
                                    "transform must be a finite 3x3 matrix")
            for s in members:
                self._plans[s.ship_id] = [M @ s.pos]
            events.append(Event("TRANSFORM_APPLIED", {
                "squad": order.squad, "ships": len(members)}))

PIECE 4 — console.py, whole file (full rewrite):

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

PIECE 5 — app.py, re-emitted whole:

"""app.py — the game shell of Homeworld: A Good Basis.

Amendment A1: ships are solid lit hulls (shipwright.py);
the math layer (basis arrows, combination ghost, trails, selection
ring) remains glowing holograms drawn over them.

Corrected B3 (Part 2 §2.1 / M1 / M8 / M10 — always space): the
Navigator's console carries the live FORMATION matrix, the shared
coefficient sliders, and the TRANSFORM matrix p -> M p, ghost-
previewed in space and fired with APPLY.

    PILOT (keyboard):
    W/S  A/D  R/F   edit the combination coefficients (c3, c1, c2)
    ENTER commit | X diagonal/staged | BACKSPACE clear | Q/E squad
    TAB select ship | C recenter camera | arrows/PgUp/PgDn camera
    P pause | F1 debug | F12 screenshot | ESC quit

    NAVIGATOR (mouse): sliders drive the same ghost construction the
    Pilot sees; the TRANSFORM grid reshapes the whole formation at once.
"""

import json
import math
import os
import sys
import time
import traceback

import numpy as np

from forge import Forge
from vobjects import Grid, Arrow, DashedLine, Label, Line, Trail
from solid import SolidMesh
from helm import Helm
from sim import FleetSim
from orders import MoveCombination, ApplyTransform
from content_db import ContentDB
from shipwright import build_ship
from console import Bridge
from referee import real_eigen_axis

COEFF_RATE = 2.0
COEFF_SNAP = 0.5
_MESH_CACHE = {}


def _aim_matrix(forward):
    f = np.asarray(forward, dtype=np.float64)
    n = np.linalg.norm(f)
    f = f / n if n > 1e-9 else np.array([0.0, 0.0, 1.0])
    up = np.array([0.0, 1.0, 0.0])
    if abs(f @ up) > 0.98:
        up = np.array([1.0, 0.0, 0.0])
    r = np.cross(up, f)
    r = r / np.linalg.norm(r)
    u = np.cross(f, r)
    return np.column_stack([r, u, f])


def _circle_points(center, radius, n=40):
    a = np.linspace(0.0, 2.0 * np.pi, n + 1)
    return np.stack([center[0] + radius * np.cos(a),
                     np.full(n + 1, center[1]),
                     center[2] + radius * np.sin(a)], axis=1)


class ShipView:
    """Solid lit hull + holographic trail."""

    def __init__(self, forge_, klass, content):
        if klass not in _MESH_CACHE:
            _MESH_CACHE[klass] = build_ship(klass, content.ship_class(klass))
        verts, tris, colors, emissive = _MESH_CACHE[klass]
        self.solid = SolidMesh(verts, tris, colors, emissive)
        self.radius = max(1.0, 1.2 * float(
            np.max(np.linalg.norm(verts[:, [0, 2]], axis=1))))
        self.trail = Trail(max_points=60, color=(0.5, 0.8, 1.0, 0.45),
                           width=0.04)
        self.dir = np.array([0.0, 0.0, 1.0])
        forge_.add(self.solid)
        forge_.add(self.trail)

    def update(self, pos, velocity, selected):
        if np.linalg.norm(velocity) > 1e-6:
            self.dir = velocity / np.linalg.norm(velocity)
        self.solid.set_highlight(selected)
        self.solid.set_transform(_aim_matrix(self.dir), pos)

    def remove(self, forge_):
        forge_.remove(self.solid)
        forge_.remove(self.trail)


class App:
    def __init__(self):
        with open("settings.json", "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        self.content = ContentDB("content")
        self.forge = Forge(self.settings)
        self.helm = Helm(self.settings)
        self.helm.attach(self.forge.window)
        self.bridge = Bridge(self.forge.overlay2d,
                             on_coeff=self._nav_coeff,
                             on_transform=self._nav_transform)

        self.sim = FleetSim(self.settings.get("seed", 1234), self.content)
        self.sim.spawn("mothership", (0.0, 0.0, 0.0))     # the ORIGIN.
        self.sim.spawn("fighter", (6.0, 0.0, 3.0), squad=1)
        self.sim.spawn("fighter", (8.0, 0.0, -2.0), squad=1)
        self.sim.spawn("fighter", (4.0, 0.0, -6.0), squad=1)
        self.sim.spawn("corvette", (-8.0, 0.0, 5.0), squad=2)
        self.sim.spawn("collector", (-11.0, 0.0, -1.0), squad=2)
        self.sim.spawn("frigate", (-6.0, 0.0, -8.0), squad=2)

        self.forge.add(Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1),
                            n=12, spacing=2.0))
        basis_colors = [(1.0, 0.3, 0.3, 1.0), (0.3, 1.0, 0.4, 1.0),
                        (0.35, 0.55, 1.0, 1.0)]
        for e, col, name in zip(self.sim.engine_vectors, basis_colors,
                                ("e1", "e2", "e3")):
            axis = Arrow((0, 0, 0), 10.0 * e, head_size=0.8, color=col,
                         glow=1.2)
            axis.overlay = True          # drawn ON TOP of the mothership
            self.forge.add(axis)
            tag = Label(name, 10.9 * e, size=0.9,
                        color=(col[0], col[1], col[2], 0.95))
            tag.overlay = True
            self.forge.add(tag)

        self.ghost_legs = [
            DashedLine((0, 0, 0), (0, 0, 0), dash=0.4, color=basis_colors[i])
            for i in range(3)]
        self.ghost_diag = Arrow((0, 0, 0), (0, 0, 1), head_size=0.7,
                                color=(1.0, 1.0, 1.0, 0.9), glow=1.2)
        self.ghost_label = Label("", (0, 0, 0), size=0.8,
                                 color=(1.0, 1.0, 1.0, 0.9))
        for g in self.ghost_legs + [self.ghost_diag, self.ghost_label]:
            g.visible = False
            self.forge.add(g)

        self.sel_ring = Line(_circle_points((0, 0, 0), 1.0),
                             color=(1.0, 1.0, 1.0, 0.8), glow=1.3,
                             width=0.05)
        self.sel_ring.visible = False
        self.forge.add(self.sel_ring)

        # transform preview: dashed ghosts p -> M p, plus the fixed axis
        self.tr_ghost_pool = []
        self.axis_line = Line(np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
                              color=(1.0, 0.8, 0.4, 0.5), glow=1.0, width=0.04)
        self.axis_line.overlay = True
        self.axis_line.visible = False
        self.forge.add(self.axis_line)

        self.views = {}
        self.coeffs = np.zeros(3)
        self.diagonal = True
        self.sel_index = 0
        self.cmd_squad = 1
        self.paused = False
        self.snap = self.sim.snapshot()
        self._sync_views()
        self._prev_frame = time.perf_counter()

        self.forge.camera.distance = 42.0
        self.forge.camera.set_orbit((0.0, 0.0, 0.0))

        print("Homeworld: A Good Basis — shakedown shell (solid ships).")
        print("W/S A/D R/F coefficients | ENTER commit | X mode | "
              "BACKSPACE clear | Q/E squad")
        print("TAB select | C recenter | arrows/PgUp/PgDn camera | "
              "P pause | F1 debug | ESC quit")
        print("NAVIGATOR: mouse — sliders fly the ghost, TRANSFORM reshapes "
              "the formation.")

    # ---- console callbacks ----

    def _nav_coeff(self, i, v):
        self.coeffs[i] = float(v)

    def _nav_transform(self, matrix, scope_all):
        squad = 0 if scope_all else self.cmd_squad
        self.sim.submit(ApplyTransform(squad=squad, matrix=matrix))
        print(f"ORDER: transform "
              f"{'whole fleet' if scope_all else f'squad {squad}'} <- M")

    # ---- helpers ----

    def _snapped(self):
        return np.round(self.coeffs / COEFF_SNAP) * COEFF_SNAP

    def _selected_id(self):
        if not self.snap.ship_ids:
            return None
        self.sel_index %= len(self.snap.ship_ids)
        return self.snap.ship_ids[self.sel_index]

    def _squads(self):
        squads = sorted({int(s) for s in self.snap.squad if s > 0})
        return squads if squads else [1]

    def _sync_views(self):
        alive = set(self.snap.ship_ids)
        for sid in list(self.views.keys()):
            if sid not in alive:
                self.views.pop(sid).remove(self.forge)
        for sid, klass in zip(self.snap.ship_ids, self.snap.klasses):
            if sid not in self.views:
                self.views[sid] = ShipView(self.forge, klass, self.content)

    # ---- the 10 Hz pulse ----

    def tick(self, dt):
        events, axes, pointer = self.helm.poll()
        for ev in events:
            if ev.value == 1.0:
                self._on_action(ev.action)
        if not self.paused:
            self.coeffs[0] += axes["TRIM_X"] * COEFF_RATE * dt
            self.coeffs[1] += axes["TRIM_Y"] * COEFF_RATE * dt
            self.coeffs[2] += axes["TRIM_Z"] * COEFF_RATE * dt

            for ev in self.sim.tick(dt):
                self._on_fleet_event(ev)
            self.snap = self.sim.snapshot()
            self._sync_views()
            for k, sid in enumerate(self.snap.ship_ids):
                self.views[sid].trail.push(self.snap.pos[k])
        self.bridge.on_pulse(pointer, self.snap, {
            "selected": self._selected_id(),
            "coeffs": self._snapped(),
            "squad": self.cmd_squad,
            "diagonal": self.diagonal,
        })

    def _on_action(self, action):
        if action == "SELECT_NEXT":
            self.sel_index += 1
        elif action == "SELECT_PREV":
            self.sel_index -= 1
        elif action in ("SQUAD_NEXT", "SQUAD_PREV"):
            squads = self._squads()
            if self.cmd_squad in squads:
                i = squads.index(self.cmd_squad)
                step = 1 if action == "SQUAD_NEXT" else -1
                self.cmd_squad = squads[(i + step) % len(squads)]
            else:
                self.cmd_squad = squads[0]
            print(f"commanding squad {self.cmd_squad}")
        elif action == "ORDER_CANCEL":
            self.coeffs[:] = 0.0
        elif action == "FLIGHT_MODE_TOGGLE":
            self.diagonal = not self.diagonal
            print(f"flight mode: "
                  f"{'diagonal' if self.diagonal else 'component-by-component'}")
        elif action == "CAM_MODE_CYCLE":
            sid = self._selected_id()
            if sid is not None:
                k = self.snap.ship_ids.index(sid)
                self.forge.camera.set_orbit(self.snap.pos[k])
        elif action == "PAUSE":
            self.paused = not self.paused
            print("paused" if self.paused else "unpaused")
        elif action == "ORDER_CONFIRM":
            c = self._snapped()
            if np.linalg.norm(c) < 1e-9:
                print("FLEET: nothing to commit — coefficients are zero")
                return
            self.sim.submit(MoveCombination(
                squad=self.cmd_squad,
                coeffs=tuple(float(v) for v in c),
                diagonal=self.diagonal))
            terms = " + ".join(f"{c[i]:g}*e{i + 1}" for i in range(3)
                               if abs(c[i]) > 1e-9)
            print(f"ORDER: squad {self.cmd_squad} <- {terms}  "
                  f"({'diagonal' if self.diagonal else 'staged'})")
            self.coeffs[:] = 0.0

    def _on_fleet_event(self, ev):
        if ev.kind == "ORDER_REJECTED":
            print(f"FLEET: order rejected — {ev.data['reason']}")
        elif ev.kind == "RANK_CHANGED":
            print(f"FLEET: fleet rank {ev.data['old']} -> {ev.data['new']}")
        elif ev.kind == "SHIP_BUILT":
            print(f"FLEET: built {ev.data['klass']} "
                  f"(rank {'up' if ev.data['rank_increased'] else 'same'})")
        elif ev.kind == "TRANSFORM_APPLIED":
            print(f"FLEET: transform applied to {ev.data['ships']} ships")

    # ---- every display frame ----

    def frame(self, alpha):
        now = time.perf_counter()
        fdt = min(now - self._prev_frame, 0.1)
        self._prev_frame = now

        axes = self.helm.poll_axes_only()
        self.forge.camera.orbit_input(
            axes["CAM_YAW"] * 1.8 * fdt,
            axes["CAM_PITCH"] * 1.2 * fdt,
            axes["CAM_ZOOM"] * 0.9 * fdt)

        snap = self.snap
        sel = self._selected_id()
        squad_positions = []
        positions = {}
        for k, sid in enumerate(snap.ship_ids):
            p = snap.prev_pos[k] + (snap.pos[k] - snap.prev_pos[k]) * alpha
            positions[sid] = p
            v = snap.pos[k] - snap.prev_pos[k]
            self.views[sid].update(p, v, sid == sel)
            if sid == sel:
                self.sel_ring.visible = True
                self.sel_ring.set_data(_circle_points(
                    p - np.array([0.0, 0.4, 0.0]), self.views[sid].radius))
            if snap.squad[k] == self.cmd_squad:
                squad_positions.append(p)
        if sel is None:
            self.sel_ring.visible = False

        self._update_ghost(squad_positions)
        self._update_transform_ghosts(positions)

        c = self._snapped()
        sel_name = ""
        if sel is not None:
            klass = snap.klasses[snap.ship_ids.index(sel)]
            sel_name = self.content.ship_class(klass)["display_name"]
        self.forge.set_debug_lines([
            f"pulse {snap.pulse}",
            f"coeffs ({c[0]:+.1f}, {c[1]:+.1f}, {c[2]:+.1f})   "
            f"mode {'diagonal' if self.diagonal else 'staged'}   "
            f"squad {self.cmd_squad}",
            f"selected ship #{sel} ({sel_name})",
        ] + (["PAUSED"] if self.paused else []))

        w, h = self.forge.window.get_framebuffer_size()
        if w > 0 and h > 0:
            self.bridge.on_frame(w, h)

    def _update_ghost(self, squad_positions):
        c = self._snapped()
        active = len(squad_positions) > 0 and np.linalg.norm(c) > 1e-9
        for g in self.ghost_legs + [self.ghost_diag, self.ghost_label]:
            g.visible = active
        if not active:
            return
        base = np.mean(squad_positions, axis=0)
        cursor = base.copy()
        for i, e in enumerate(self.sim.engine_vectors):
            nxt = cursor + c[i] * e
            self.ghost_legs[i].set_data(cursor, nxt, dash=0.4)
            self.ghost_legs[i].visible = abs(c[i]) > 1e-9
            cursor = nxt
        self.ghost_diag.set_data(base, cursor, head_size=0.7)
        self.ghost_label.set_data(pos=cursor + np.array([0.0, 1.0, 0.0]))
        self.ghost_label.set_text(
            f"({c[0]:+.1f}, {c[1]:+.1f}, {c[2]:+.1f})")

    def _update_transform_ghosts(self, positions):
        if not self.bridge.transform_active():
            for g in self.tr_ghost_pool:
                g.visible = False
            self.axis_line.visible = False
            return
        M = self.bridge.transform_matrix()
        snap = self.snap
        pairs = []
        for k, sid in enumerate(snap.ship_ids):
            if self.bridge.scope_all or snap.squad[k] == self.cmd_squad:
                a = positions[sid]
                b = M @ a
                if np.linalg.norm(b - a) > 1e-6:
                    pairs.append((a, b))
        while len(self.tr_ghost_pool) < len(pairs):
            g = DashedLine((0, 0, 0), (0, 0, 0), dash=0.5,
                           color=(0.9, 0.9, 1.0, 0.7))
            self.forge.add(g)
            self.tr_ghost_pool.append(g)
        for g, (a, b) in zip(self.tr_ghost_pool, pairs):
            g.set_data(a, b, dash=0.5)
            g.visible = True
        for g in self.tr_ghost_pool[len(pairs):]:
            g.visible = False
        axis = real_eigen_axis(M)
        self.axis_line.visible = False
        if axis is not None:
            a = np.asarray(axis, dtype=np.float64)
            n = np.linalg.norm(a)
            if n > 1e-9:
                a = a / n * 14.0
                self.axis_line.set_data(np.stack([-a, a]))
                self.axis_line.visible = True

    def run(self):
        self.forge.run(self.tick, self.frame)


def main():
    App().run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("app crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)

FOR DEEPSEEK: apply pieces 1 and 3 (referee append; sim import + _ingest branch), save pieces 2, 4, 5 whole. Verify real_eigen_axis(M)'s return shape matches my use (a 3-vector or None) and fix my call site if it differs. Run run.bat and fleet_demo.py (sim/referee touched — the 12/12 must stay green). Commit: corrected B3: always space - formation matrix, shared coefficient sliders, ApplyTransform with ghost preview, det/rank/axis readouts

WHAT YOU SHOULD SEE (Nir):

    FORMATION P: three colored rows (e1 red, e2 green, e3 blue), one column per ship of your commanded squad. Fly with W/A/S/D — watch the columns stream in real time. The matrix IS the ships.
    Drag slider c1 with the mouse: the SAME ghost construction the keyboard makes appears in space, live, leg by leg, and ENTER flies it. Under the sliders: "FUEL legs 7.0 | diag 5.0" — the diagonal is never more expensive. Never announced. Just there.
    TRANSFORM: wheel the 3x3. Try rotation about the vertical: top row 0 0 1, middle 0 1 0, bottom -1 0 0 — dashed ghosts swing every ship of the squad around Mom, DET reads +1.00, and an amber axis line appears — the axis the rotation leaves alone. APPLY: the formation flies to it. Try 2 on the whole diagonal: DET +8.00 (double size = eight times the volume). Zero out a row: "COLLAPSE TO A PLANE" in red, and the ghosts visibly flatten. A minus one: DET -1.00 — a mirror.

REPORT BACK: (1) clean run? (2) is THIS the instant matrix↔space link you meant? (3) what's wrong with it — sizes, speeds, feel, anything.
