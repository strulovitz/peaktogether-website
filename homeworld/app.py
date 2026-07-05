"""app.py — the game shell of Homeworld: A Good Basis (NT Parts 4-5).

Owns nothing but the wiring: forge renders, helm inputs, fleet
simulates; app translates actions into orders, routes events, and
interpolates snapshots into visuals at 60 fps over the 10 Hz pulse.

Until campaign/ and bridge/ arrive, app hosts the SHAKEDOWN SCENARIO:
a mothership, three fighters in squad 1, and the Pilot's combination
console (Bible 2.1) driven entirely by the keyboard:

    W/S  A/D  R/F   edit the combination coefficients (c3, c1, c2)
    ENTER           commit: squad 1 flies  c1*e1 + c2*e2 + c3*e3
    X               toggle diagonal flight vs component-by-component
    BACKSPACE       reset coefficients to zero
    TAB / SHIFT+TAB select next / previous ship (white highlight)
    C               recenter the camera on the selected ship
    ARROWS, PGUP/DN orbit / zoom the camera
    P               pause        F1 debug text      F12 screenshot
    ESC             quit
"""

import json
import os
import sys
import time
import traceback

import numpy as np

# --- Quake-style path setup (RULE #0: run with `python app.py`, NEVER `-m`) ---
# forge/helm/fleet are sibling package folders using flat absolute imports.
# Put each on sys.path (ahead of this root folder) so their internal imports
# resolve, and so `from app import Forge` inside forge finds forge/app.py
# rather than this root app.py. This is DeepSeek's RULE #0 conversion of
# Fable's file (the only change from the verbatim BIBLE version).
_HERE = os.path.dirname(os.path.abspath(__file__))
for _pkg in ("forge", "helm", "fleet"):
    _dir = os.path.join(_HERE, _pkg)
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from forge import Forge, Grid, Arrow, DashedLine, Label, Trail, WireMesh
from helm import Helm
from fleet import FleetSim, MoveCombination

COEFF_RATE = 2.0          # coefficient units per second of held key
COEFF_SNAP = 0.5          # commit snaps coefficients to this grid

# ---- placeholder wireframes (until content/meshes/ arrives) ----

FIGHTER_VERTS = [
    [0.0, 0.0, 1.6],                      # nose
    [-1.1, 0.0, -1.0], [1.1, 0.0, -1.0],  # wingtips
    [0.0, 0.7, -0.9], [0.0, -0.35, -0.9], # fin, belly
    [0.0, 0.0, -1.2],                     # tail
]
FIGHTER_EDGES = [
    [0, 1], [0, 2], [0, 3], [0, 4],
    [1, 5], [2, 5], [3, 5], [4, 5],
    [1, 3], [3, 2], [2, 4], [4, 1],
]

MOTHERSHIP_VERTS = [
    [0.0, 0.0, 4.0], [0.0, 0.0, -4.0],
    [2.2, 0.0, 0.0], [0.0, 2.2, 0.0], [-2.2, 0.0, 0.0], [0.0, -2.2, 0.0],
]
MOTHERSHIP_EDGES = [
    [0, 2], [0, 3], [0, 4], [0, 5],
    [1, 2], [1, 3], [1, 4], [1, 5],
    [2, 3], [3, 4], [4, 5], [5, 2],
]

SHIP_STYLE = {
    "fighter": (FIGHTER_VERTS, FIGHTER_EDGES, 1.0, (0.55, 0.9, 1.0, 1.0)),
    "mothership": (MOTHERSHIP_VERTS, MOTHERSHIP_EDGES, 1.6,
                   (1.0, 0.85, 0.5, 1.0)),
}


def _aim_matrix(forward):
    """3x3 rotation whose columns (right, up, forward) map mesh-local
    axes (+z = nose) into world space."""
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


class ShipView:
    """The visual twin of one ship: wire mesh + fading trail."""

    def __init__(self, forge_, klass):
        verts, edges, scale, color = SHIP_STYLE.get(
            klass, SHIP_STYLE["fighter"])
        self.base = np.asarray(verts, dtype=np.float64) * scale
        self.edges = edges
        self.color = color
        self.mesh = WireMesh(self.base, edges, color=color, width=0.05)
        self.trail = Trail(max_points=60, color=(0.5, 0.8, 1.0, 0.45),
                           width=0.04)
        self.dir = np.array([0.0, 0.0, 1.0])
        forge_.add(self.mesh)
        forge_.add(self.trail)

    def update(self, pos, velocity, selected):
        if np.linalg.norm(velocity) > 1e-6:
            self.dir = velocity / np.linalg.norm(velocity)
        R = _aim_matrix(self.dir)
        self.mesh.set_data(self.base @ R.T + pos, self.edges)
        if selected:
            self.mesh.set_color((1.0, 1.0, 1.0, 1.0))
            self.mesh.glow = 1.5
        else:
            self.mesh.set_color(self.color)
            self.mesh.glow = 1.0

    def remove(self, forge_):
        forge_.remove(self.mesh)
        forge_.remove(self.trail)


class App:
    def __init__(self):
        with open("settings.json", "r", encoding="utf-8") as f:
            self.settings = json.load(f)

        self.forge = Forge(self.settings)
        self.helm = Helm(self.settings)
        self.helm.attach(self.forge.window)

        # ---- simulation + shakedown fleet ----
        self.sim = FleetSim(self.settings.get("seed", 1234))
        self.sim.spawn("mothership", (0.0, 0.0, 0.0))
        self.sim.spawn("fighter", (6.0, 0.0, 3.0), squad=1)
        self.sim.spawn("fighter", (8.0, 0.0, -2.0), squad=1)
        self.sim.spawn("fighter", (4.0, 0.0, -6.0), squad=1)

        # ---- static scene ----
        self.forge.add(Grid(center=(0, 0, 0), u=(1, 0, 0), v=(0, 0, 1),
                            n=12, spacing=2.0))
        basis_colors = [(1.0, 0.3, 0.3, 1.0), (0.3, 1.0, 0.4, 1.0),
                        (0.35, 0.55, 1.0, 1.0)]
        for e, col, name in zip(self.sim.engine_vectors, basis_colors,
                                ("e1", "e2", "e3")):
            self.forge.add(Arrow((0, 0, 0), 3.0 * e, head_size=0.5,
                                 color=col))
            self.forge.add(Label(name, 3.6 * e, size=0.8,
                                 color=(col[0], col[1], col[2], 0.9)))

        # ---- combination ghost (the order being composed) ----
        self.ghost_legs = [
            DashedLine((0, 0, 0), (0, 0, 0), dash=0.4, color=basis_colors[i])
            for i in range(3)
        ]
        self.ghost_diag = Arrow((0, 0, 0), (0, 0, 1), head_size=0.7,
                                color=(1.0, 1.0, 1.0, 0.9), glow=1.2)
        self.ghost_label = Label("", (0, 0, 0), size=0.8,
                                 color=(1.0, 1.0, 1.0, 0.9))
        for g in self.ghost_legs + [self.ghost_diag, self.ghost_label]:
            g.visible = False
            self.forge.add(g)

        # ---- state ----
        self.views = {}
        self.coeffs = np.zeros(3)
        self.diagonal = True
        self.sel_index = 0
        self.paused = False
        self.snap = self.sim.snapshot()
        self._sync_views()
        self._prev_frame = time.perf_counter()

        self.forge.camera.distance = 42.0
        self.forge.camera.set_orbit((0.0, 0.0, 0.0))

        print("Homeworld: A Good Basis — shakedown shell.")
        print("W/S A/D R/F edit coefficients | ENTER commit | X mode | "
              "BACKSPACE clear")
        print("TAB select | C recenter camera | arrows/PgUp/PgDn camera | "
              "P pause | F1 debug | ESC quit")

    # ---- helpers ----

    def _snapped(self):
        return np.round(self.coeffs / COEFF_SNAP) * COEFF_SNAP

    def _selected_id(self):
        if not self.snap.ship_ids:
            return None
        self.sel_index %= len(self.snap.ship_ids)
        return self.snap.ship_ids[self.sel_index]

    def _sync_views(self):
        alive = set(self.snap.ship_ids)
        for sid in list(self.views.keys()):
            if sid not in alive:
                self.views.pop(sid).remove(self.forge)
        for sid, klass in zip(self.snap.ship_ids, self.snap.klasses):
            if sid not in self.views:
                self.views[sid] = ShipView(self.forge, klass)

    # ---- the 10 Hz pulse ----

    def tick(self, dt):
        events, axes, pointer = self.helm.poll()
        for ev in events:
            if ev.value == 1.0:
                self._on_action(ev.action)
        if self.paused:
            return

        self.coeffs[0] += axes["TRIM_X"] * COEFF_RATE * dt
        self.coeffs[1] += axes["TRIM_Y"] * COEFF_RATE * dt
        self.coeffs[2] += axes["TRIM_Z"] * COEFF_RATE * dt

        for ev in self.sim.tick(dt):
            self._on_fleet_event(ev)
        self.snap = self.sim.snapshot()
        self._sync_views()
        for k, sid in enumerate(self.snap.ship_ids):
            self.views[sid].trail.push(self.snap.pos[k])

    def _on_action(self, action):
        if action == "SELECT_NEXT":
            self.sel_index += 1
        elif action == "SELECT_PREV":
            self.sel_index -= 1
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
                squad=1, coeffs=tuple(float(v) for v in c),
                diagonal=self.diagonal))
            terms = " + ".join(f"{c[i]:g}*e{i + 1}" for i in range(3)
                               if abs(c[i]) > 1e-9)
            print(f"ORDER: squad 1 <- {terms}  "
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
            axes["CAM_ZOOM"] * 0.9 * fdt,
        )

        snap = self.snap
        sel = self._selected_id()
        squad_positions = []
        for k, sid in enumerate(snap.ship_ids):
            p = snap.prev_pos[k] + (snap.pos[k] - snap.prev_pos[k]) * alpha
            v = snap.pos[k] - snap.prev_pos[k]
            self.views[sid].update(p, v, sid == sel)
            if snap.squad[k] == 1:
                squad_positions.append(p)

        self._update_ghost(squad_positions)

        c = self._snapped()
        klass = ""
        if sel is not None:
            klass = snap.klasses[snap.ship_ids.index(sel)]
        self.forge.set_debug_lines([
            f"pulse {snap.pulse}   fleet rank {snap.rank}",
            f"coeffs ({c[0]:+.1f}, {c[1]:+.1f}, {c[2]:+.1f})   "
            f"mode {'diagonal' if self.diagonal else 'staged'}",
            f"selected ship #{sel} ({klass})",
        ] + (["PAUSED"] if self.paused else []))

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
