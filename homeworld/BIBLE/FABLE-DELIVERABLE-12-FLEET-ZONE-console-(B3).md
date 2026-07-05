The moment has arrived — B3, the two-player patch. Two files: console.py is new (the Bridge with the FLEET ZONE), and app.py is re-emitted whole, exactly as DeepSeek pasted it, with only the Bridge wiring added (four touch points: one import, one construction line, pointer feed in tick, draw call in frame — plus the pause restructure so the Navigator's mouse keeps working while the sim is paused). Every owner-approved feel number is untouched.

FILE 1 of 2 — console.py (new file, complete):

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

FILE 2 of 2 — app.py (re-emitted WHOLE; only Bridge wiring added):

"""app.py — the game shell of Homeworld: A Good Basis.

Amendment A1: ships are solid lit hulls (shipwright.py);
the math layer (basis arrows, combination ghost, trails, selection
ring) remains glowing holograms drawn over them.

    PILOT (keyboard):
    W/S  A/D  R/F   edit the combination coefficients (c3, c1, c2)
    ENTER commit | X diagonal/staged | BACKSPACE clear | Q/E squad
    TAB select ship | C recenter camera | arrows/PgUp/PgDn camera
    P pause | F1 debug | F12 screenshot | ESC quit

    NAVIGATOR (mouse): the bridge console on the right — the fleet
    matrix A live, ships as columns; the Pilot's TAB lights a column.
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
from orders import MoveCombination
from content_db import ContentDB
from shipwright import build_ship
from console import Bridge

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
        self.bridge = Bridge(self.forge.overlay2d)

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
        print("NAVIGATOR: mouse on the bridge console (right panel).")

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
        self.bridge.on_pulse(pointer, self.snap, self._selected_id())

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
        for k, sid in enumerate(snap.ship_ids):
            p = snap.prev_pos[k] + (snap.pos[k] - snap.prev_pos[k]) * alpha
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

        c = self._snapped()
        sel_name = ""
        if sel is not None:
            klass = snap.klasses[snap.ship_ids.index(sel)]
            sel_name = self.content.ship_class(klass)["display_name"]
        self.forge.set_debug_lines([
            f"pulse {snap.pulse}   fleet rank {snap.rank}",
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

FOR DEEPSEEK: save console.py (new) and app.py (whole replacement — diff it against the old one to verify my only changes are: docstring, the from console import Bridge import, the self.bridge = Bridge(...) line, the tick pause-restructure + bridge.on_pulse call, the bridge.on_frame block at the end of frame, and one print line). Then: run run.bat, and fleet_demo.py for the 12/12 ritual. Commit message: bridge: FLEET ZONE console (B3) - live fleet matrix with ships as columns, rank/resources readouts, TAB-follows selection; app.py wired for two players

WHAT YOU SHOULD SEE (Nir — double-click run.bat, and bring your partner):

    The game exactly as you know it — ships, ghost arrows, all Pilot controls unchanged — but now the right 30% is the bridge console: "BRIDGE - FLEET", and below it readouts: FLEET RANK 5 / 6, RESOURCES, SELECTED.
    The heart of it: a 6-row matrix, rows labeled K B M S J U, with 7 columns — one per ship (headers like MS, FT1, FT1, FT1, CV2, CL2, FG2). Look at the three FT1 columns: identical numbers. Seven ships, but rank only 5 — the fleet literally shows you its redundancy.
    The two-player moment: have the Pilot press TAB. A yellow frame jumps from column to column on the Navigator's console, and the SELECTED readout follows ("#2 FT squad 1"...). One player touches the keyboard, the other sees mathematics light up.
    Pause with P: the sim freezes but the console stays alive under the mouse.
    Resize: the panel re-sticks; the fps/F1 text stays on top.

REPORT BACK, please: (1) runs clean, no crashlog? (2) does the matrix read clearly — 7 columns comfortable at your window size? (3) does TAB→column-highlight feel like a conversation starter between the two seats? (4) anything on the console you instinctively tried to click and were disappointed? (that answer directly shapes B4 — the CONTEXT and BUILD zones with real buttons that spend resources and grow the matrix). 🚀
