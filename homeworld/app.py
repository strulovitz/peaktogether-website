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
    from pt_runtime import bootstrap
    bootstrap("Homeworld", "Homeworld: A Good Basis")
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
