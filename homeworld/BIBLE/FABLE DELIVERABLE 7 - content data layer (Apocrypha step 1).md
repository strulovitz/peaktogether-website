> 🛑 **DEEPSEEK NOTE (July 5, 2026) — FLATTENED per RULE #0.** Fable delivered this as a `content/` **package** (content/__init__.py + content/db.py + content/demo.py) with a relative import and a `python -m content.demo` run command. Nir never agreed to `-m` / packages. So on drop-in I flattened the **Python code**: `content/db.py` → **`content_db.py`** (root, unchanged — no relative imports), `content/demo.py` → **`content_demo.py`** (root; `from .db import` → `from content_db import`; run `python content_demo.py`, never `-m`), and I dropped `content/__init__.py` (package re-export, not needed flat). `app.py`'s `from content import ContentDB` → `from content_db import ContentDB`.
>
> The **`content/` folder is KEPT as a pure DATA directory** (ships.json + meshes/ + narrator/ + book/) — exactly like Quake's `levels/`/`hud/` data folders. Data folders are fine; only Python **code** must be flat. `ContentDB("content")` reads this data tree by path. Fable's text is preserved verbatim below.

---

The shell flies! 🎉 Next package: CONTENT (Apocrypha build step 1) — the data layer. Ship classes move out of hardcoded placeholders into content/ships.json, five hand-authored wireframe meshes give each class its own silhouette, the narrator's first lines are seeded, and the book placeholder ledger begins. Plus a small treat: app.py now spawns a corvette, a collector, and a frigate as squad 2, and Q/E switches which squad you command.

Below are 13 complete files (mostly small JSON). Send each to DeepSeek exactly as-is.

File 1 — content/__init__.py

"""content — the data layer of Homeworld: A Good Basis (APOCRYPHA Part 1).

All game data lives here as JSON: ship classes, wireframe meshes,
narrator lines, book excerpts (verbatim, pasted by the owner),
missions. ContentDB loads and VALIDATES everything at startup and
fails loudly on schema errors — a typo in a data file must never
become a silent in-game mystery.
"""

from .db import ContentDB, ContentError

__all__ = ["ContentDB", "ContentError"]

File 2 — content/db.py

"""ContentDB: load + validate the entire content/ tree (APOCRYPHA 1.1-1.4).

Validation doctrine: fail LOUDLY and PRECISELY. Every error message
names the file, the entry, and the rule violated, so the owner can
paste it to the team and the fix is obvious.
"""

import json
import os

import numpy as np


class ContentError(Exception):
    pass


def _load_json(path):
    if not os.path.exists(path):
        raise ContentError(f"missing file: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ContentError(f"{path}: invalid JSON — {e}")


class ContentDB:
    def __init__(self, root="content"):
        self.root = root
        self._ships = {}
        self._meshes = {}        # rel path -> (vertices (N,3), edges list)
        self._narrator = {}      # file stem -> list of line dicts
        self._excerpts = {}      # excerpt id -> dict
        self._missions = {}      # mission id -> dict
        self._placeholders = []  # (file, excerpt id) still awaiting the book
        self._load_ships()
        self._load_narrator()
        self._load_book()
        self._load_missions()

    def _path(self, *parts):
        return os.path.join(self.root, *parts)

    # ---- loading + validation ----

    def _load_ships(self):
        data = _load_json(self._path("ships.json"))
        for name, spec in data.items():
            where = f"content/ships.json: {name}"
            sig = spec.get("signature")
            if (not isinstance(sig, list) or len(sig) != 6
                    or not all(isinstance(x, (int, float)) for x in sig)):
                raise ContentError(
                    f"{where}: signature must be a list of 6 numbers "
                    f"(channel order K,B,M,S,J,U)")
            for field in ("cost", "hp", "trim_speed"):
                if not isinstance(spec.get(field), (int, float)):
                    raise ContentError(f"{where}: {field} must be a number")
            mesh_rel = spec.get("mesh")
            if not isinstance(mesh_rel, str):
                raise ContentError(f"{where}: mesh must be a path string")
            self._load_mesh(mesh_rel)
            spec.setdefault("display_name", name)
            spec.setdefault("scale", 1.0)
            spec.setdefault("color", [0.55, 0.9, 1.0, 1.0])
            if (not isinstance(spec["color"], list)
                    or len(spec["color"]) != 4):
                raise ContentError(f"{where}: color must be [r, g, b, a]")
            self._ships[name] = spec

    def _load_mesh(self, rel):
        if rel in self._meshes:
            return
        path = self._path(rel)
        data = _load_json(path)
        verts = data.get("vertices")
        edges = data.get("edges")
        if not isinstance(verts, list) or not all(
                isinstance(v, list) and len(v) == 3 for v in verts):
            raise ContentError(f"{path}: vertices must be a list of "
                               f"[x, y, z] triples")
        if not isinstance(edges, list) or not all(
                isinstance(e, list) and len(e) == 2 for e in edges):
            raise ContentError(f"{path}: edges must be a list of "
                               f"[i, j] index pairs")
        n = len(verts)
        for e in edges:
            if not (0 <= e[0] < n and 0 <= e[1] < n):
                raise ContentError(f"{path}: edge {e} references a vertex "
                                   f"outside 0..{n - 1}")
        if not (1 <= len(edges) <= 500):
            raise ContentError(f"{path}: {len(edges)} edges — expected "
                               f"1..500 (target aesthetic is 20-60)")
        self._meshes[rel] = (np.asarray(verts, dtype=np.float64),
                             [[int(e[0]), int(e[1])] for e in edges])

    def _load_narrator(self):
        d = self._path("narrator")
        if not os.path.isdir(d):
            return
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            lines = _load_json(os.path.join(d, fn))
            if not isinstance(lines, list):
                raise ContentError(f"content/narrator/{fn}: must be a "
                                   f"JSON list of line objects")
            seen = set()
            for ln in lines:
                where = (f"content/narrator/{fn}: "
                         f"line '{ln.get('id', '<no id>')}'")
                for req in ("id", "text"):
                    if not ln.get(req):
                        raise ContentError(f"{where}: '{req}' is required")
                if ln["id"] in seen:
                    raise ContentError(f"{where}: duplicate id")
                seen.add(ln["id"])
                if len(ln["text"]) > 140:
                    raise ContentError(f"{where}: text is "
                                       f"{len(ln['text'])} chars — max 140 "
                                       f"(tone rule 3, Apocrypha 4.4)")
                if "teach" in ln.get("tags", []) and not ln.get("cite"):
                    raise ContentError(f"{where}: teach lines require a "
                                       f"non-empty cite (tone rule 2)")
            self._narrator[fn[:-5]] = lines

    def _load_book(self):
        d = self._path("book")
        if not os.path.isdir(d):
            return
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            entries = _load_json(os.path.join(d, fn))
            if not isinstance(entries, list):
                raise ContentError(f"content/book/{fn}: must be a JSON list")
            for e in entries:
                where = (f"content/book/{fn}: "
                         f"entry '{e.get('id', '<no id>')}'")
                for req in ("id", "kind", "cite", "text"):
                    if not e.get(req):
                        raise ContentError(f"{where}: '{req}' is required")
                if e["kind"] not in ("quote", "example", "exercise"):
                    raise ContentError(f"{where}: kind must be quote, "
                                       f"example, or exercise")
                if e["id"] in self._excerpts:
                    raise ContentError(f"{where}: duplicate excerpt id")
                if "PLACEHOLDER" in e["cite"]:
                    self._placeholders.append((f"book/{fn}", e["id"]))
                self._excerpts[e["id"]] = e

    def _load_missions(self):
        d = self._path("missions")
        if not os.path.isdir(d):
            return
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            m = _load_json(os.path.join(d, fn))
            for req in ("id", "title", "setup", "phases"):
                if req not in m:
                    raise ContentError(f"content/missions/{fn}: "
                                       f"'{req}' is required")
            self._missions[m["id"]] = m

    # ---- accessors ----

    def ship_class(self, klass):
        if klass not in self._ships:
            raise KeyError(f"unknown ship class: {klass}")
        return self._ships[klass]

    def ship_classes(self):
        return sorted(self._ships)

    def mesh_for_class(self, klass):
        spec = self.ship_class(klass)
        verts, edges = self._meshes[spec["mesh"]]
        return verts * float(spec["scale"]), [list(e) for e in edges]

    def color_for_class(self, klass):
        return tuple(self.ship_class(klass)["color"])

    def narrator_lines(self, name):
        return list(self._narrator.get(name, []))

    def excerpt(self, excerpt_id):
        if excerpt_id not in self._excerpts:
            raise KeyError(f"unknown book excerpt: {excerpt_id}")
        return self._excerpts[excerpt_id]

    def excerpt_ids(self):
        return sorted(self._excerpts)

    def placeholders(self):
        return list(self._placeholders)

    def mission(self, mission_id):
        if mission_id not in self._missions:
            raise KeyError(f"unknown mission: {mission_id}")
        return self._missions[mission_id]

    def missions(self):
        return sorted(self._missions)

File 3 — content/demo.py

"""python -m content.demo — validate the whole content/ tree.

EXPECTED: a short PASS report listing classes, mesh edge counts,
narrator lines, and the PLACEHOLDER ledger (book excerpts the owner
still needs to paste). Any schema error prints one precise FAIL line
naming file + entry + rule.
"""

import sys
import traceback

from .db import ContentDB, ContentError


def main():
    print("CONTENT CHECK — content/ data layer")
    try:
        db = ContentDB("content")
    except ContentError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    classes = db.ship_classes()
    print(f"ships.json ........... {len(classes)} classes OK "
          f"({', '.join(classes)})")
    counts = [len(db.mesh_for_class(k)[1]) for k in classes]
    print(f"meshes ............... {len(classes)} meshes OK "
          f"({min(counts)}-{max(counts)} edges each)")
    core = db.narrator_lines("core")
    print(f"narrator/core.json ... {len(core)} lines OK")
    ph = db.placeholders()
    print(f"book ................. {len(db.excerpt_ids())} excerpts, "
          f"{len(ph)} PLACEHOLDER")
    for fname, eid in ph:
        print(f"                       PLACEHOLDER: {fname} :: {eid}")
    print(f"missions ............. {len(db.missions())} files")
    print("CONTENT CHECK PASSED")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
        sys.exit(1)

File 4 — content/ships.json

{
    "mothership": {
        "display_name": "Mothership",
        "signature": [1, 1, 1, 1, 1, 1],
        "cost": 0, "hp": 500, "trim_speed": 0.5,
        "mesh": "meshes/mothership.json", "scale": 1.6,
        "color": [1.0, 0.85, 0.5, 1.0]
    },
    "fighter": {
        "display_name": "Fighter",
        "signature": [2, 0, 0, 1, 0, 0],
        "cost": 40, "hp": 30, "trim_speed": 3.0,
        "mesh": "meshes/fighter.json", "scale": 1.0,
        "color": [0.55, 0.9, 1.0, 1.0]
    },
    "corvette": {
        "display_name": "Corvette",
        "signature": [0, 2, 0, 1, 0, 0],
        "cost": 60, "hp": 60, "trim_speed": 2.0,
        "mesh": "meshes/corvette.json", "scale": 1.1,
        "color": [1.0, 0.6, 0.3, 1.0]
    },
    "collector": {
        "display_name": "Resource Collector",
        "signature": [0, 0, 2, 0, 1, 0],
        "cost": 50, "hp": 40, "trim_speed": 1.5,
        "mesh": "meshes/collector.json", "scale": 1.2,
        "color": [0.5, 1.0, 0.6, 1.0],
        "special": "collector"
    },
    "frigate": {
        "display_name": "Frigate",
        "signature": [0, 0, 0, 2, 0, 1],
        "cost": 90, "hp": 100, "trim_speed": 1.0,
        "mesh": "meshes/frigate.json", "scale": 1.3,
        "color": [0.8, 0.6, 1.0, 1.0]
    }
}

File 5 — content/meshes/mothership.json

{
    "vertices": [
        [0.0, 0.0, 4.5], [0.0, 0.0, -4.5],
        [1.8, 0.0, 1.5], [0.0, 1.8, 1.5], [-1.8, 0.0, 1.5], [0.0, -1.8, 1.5],
        [2.2, 0.0, -1.5], [0.0, 2.2, -1.5], [-2.2, 0.0, -1.5], [0.0, -2.2, -1.5],
        [0.0, 2.6, -0.3]
    ],
    "edges": [
        [0, 2], [0, 3], [0, 4], [0, 5],
        [2, 3], [3, 4], [4, 5], [5, 2],
        [2, 6], [3, 7], [4, 8], [5, 9],
        [6, 7], [7, 8], [8, 9], [9, 6],
        [1, 6], [1, 7], [1, 8], [1, 9],
        [3, 10], [7, 10]
    ]
}

File 6 — content/meshes/fighter.json

{
    "vertices": [
        [0.0, 0.0, 1.8],
        [0.0, 0.35, 0.5],
        [-1.3, 0.0, -0.8], [1.3, 0.0, -0.8],
        [0.0, 0.85, -1.0], [0.0, -0.3, -0.7],
        [0.0, 0.0, -1.3],
        [-0.55, 0.0, 0.3], [0.55, 0.0, 0.3]
    ],
    "edges": [
        [0, 7], [7, 2], [2, 6],
        [0, 8], [8, 3], [3, 6],
        [0, 1], [1, 4], [4, 6],
        [0, 5], [5, 6],
        [7, 8], [2, 5], [3, 5], [2, 4], [3, 4]
    ]
}

File 7 — content/meshes/corvette.json

{
    "vertices": [
        [0.0, 0.0, 1.5],
        [0.8, 0.5, 0.3], [-0.8, 0.5, 0.3], [-0.8, -0.5, 0.3], [0.8, -0.5, 0.3],
        [0.6, 0.4, -1.2], [-0.6, 0.4, -1.2], [-0.6, -0.4, -1.2], [0.6, -0.4, -1.2]
    ],
    "edges": [
        [0, 1], [0, 2], [0, 3], [0, 4],
        [1, 2], [2, 3], [3, 4], [4, 1],
        [1, 5], [2, 6], [3, 7], [4, 8],
        [5, 6], [6, 7], [7, 8], [8, 5]
    ]
}

File 8 — content/meshes/collector.json

{
    "vertices": [
        [0.0, 0.0, 1.6],
        [0.7, 0.7, 0.9], [-0.7, 0.7, 0.9], [-0.7, -0.7, 0.9], [0.7, -0.7, 0.9],
        [0.0, 0.0, -1.6],
        [1.1, 0.0, 0.0], [0.0, 1.1, 0.0], [-1.1, 0.0, 0.0], [0.0, -1.1, 0.0]
    ],
    "edges": [
        [0, 1], [0, 2], [0, 3], [0, 4],
        [1, 2], [2, 3], [3, 4], [4, 1],
        [1, 6], [1, 7], [2, 7], [2, 8],
        [3, 8], [3, 9], [4, 9], [4, 6],
        [6, 5], [7, 5], [8, 5], [9, 5]
    ]
}

File 9 — content/meshes/frigate.json

{
    "vertices": [
        [0.0, 0.0, 2.8],
        [0.7, 0.35, 1.2], [-0.7, 0.35, 1.2], [-0.7, -0.35, 1.2], [0.7, -0.35, 1.2],
        [0.9, 0.5, -1.6], [-0.9, 0.5, -1.6], [-0.9, -0.5, -1.6], [0.9, -0.5, -1.6],
        [0.0, 0.0, -2.6],
        [0.0, 1.2, -0.4]
    ],
    "edges": [
        [0, 1], [0, 2], [0, 3], [0, 4],
        [1, 2], [2, 3], [3, 4], [4, 1],
        [1, 5], [2, 6], [3, 7], [4, 8],
        [5, 6], [6, 7], [7, 8], [8, 5],
        [5, 9], [6, 9], [7, 9], [8, 9],
        [10, 1], [10, 2], [10, 5], [10, 6]
    ]
}

File 10 — content/narrator/core.json

[
    {
        "id": "reject_outside_colspace",
        "on": {"event": "ORDER_REJECTED"},
        "text": "Admiral, that combination lies outside our column space. Suggest adding an independent vessel.",
        "cite": "BIBLE.md 2.3 canonical rejection; concept: Strang 6e, Section 3.1",
        "tags": ["reject", "teach"],
        "cooldown_s": 20,
        "once": false
    },
    {
        "id": "rank_up",
        "on": {"event": "RANK_CHANGED"},
        "text": "Fleet rank has grown, Command. We can reach places we could not reach before.",
        "cite": "concept: Strang 6e, Section 1.4 — PLACEHOLDER, replace with book quote",
        "tags": ["teach"],
        "cooldown_s": 30,
        "once": false
    },
    {
        "id": "ship_built_independent",
        "on": {"event": "SHIP_BUILT"},
        "text": "New vessel online — an independent column. The fleet reaches in a new direction.",
        "cite": "concept: Strang 6e, Section 1.3 — PLACEHOLDER, replace with book quote",
        "tags": ["teach"],
        "cooldown_s": 30,
        "once": false
    },
    {
        "id": "shield_down",
        "on": {"event": "SHIELD_DOWN"},
        "text": "Shield channels zeroed. Target defenses are down, Command.",
        "cite": "",
        "tags": ["story"],
        "cooldown_s": 10,
        "once": false
    },
    {
        "id": "pivot_zero",
        "on": {"event": "PIVOT_ZERO"},
        "text": "A dead pylon in the pivot position, Command. We must exchange rows.",
        "cite": "concept: Strang 6e, Section 2.7 — PLACEHOLDER, replace with book quote",
        "tags": ["teach"],
        "cooldown_s": 30,
        "once": false
    },
    {
        "id": "solved",
        "on": {"event": "SOLVED"},
        "text": "Codes accepted. The system is solved. Well done, Command.",
        "cite": "",
        "tags": ["story"],
        "cooldown_s": 10,
        "once": false
    },
    {
        "id": "harvest_flavor",
        "on": {"event": "RESOURCE_TICK"},
        "text": "Collectors report steady intake.",
        "cite": "",
        "tags": ["flavor"],
        "cooldown_s": 60,
        "once": false
    }
]

File 11 — content/book/ch1_excerpts.json

[
    {
        "id": "ch1_placeholder_combination",
        "kind": "example",
        "cite": "PLACEHOLDER — replace with book example (Strang 6e, Section 1.1)",
        "text": "PLACEHOLDER: linear combination c1*v + c2*w. The owner will paste the verbatim book example here.",
        "matrices": {"v": [1, 0, 0], "w": [0, 0, 1]},
        "notes": "used by mission m01 waypoint teaching beats"
    },
    {
        "id": "ch1_placeholder_freighter",
        "kind": "exercise",
        "cite": "PLACEHOLDER — replace with solved exercise (Strang 6e, Section 1.1 or 1.2)",
        "text": "PLACEHOLDER: express a given point as a combination of the basis vectors.",
        "matrices": {"target": [2, 0, 3]},
        "solution": {"c": [2, 3]},
        "notes": "m01 finale: damaged freighter sits at 2*e1 + 3*e3"
    }
]

File 12 — app.py (updated — replaces the whole file)

"""app.py — the game shell of Homeworld: A Good Basis (NT Parts 4-5).

Owns nothing but the wiring: forge renders, helm inputs, fleet
simulates, content supplies data; app translates actions into orders,
routes events, and interpolates snapshots into visuals at 60 fps.

SHAKEDOWN SCENARIO (until campaign/ and bridge/ arrive):
mothership + three fighters (squad 1) + corvette, collector, frigate
(squad 2). All ship classes and meshes come from content/ships.json.

    W/S  A/D  R/F   edit the combination coefficients (c3, c1, c2)
    ENTER           commit: the squad flies  c1*e1 + c2*e2 + c3*e3
    X               toggle diagonal flight vs component-by-component
    BACKSPACE       reset coefficients        Q / E  switch squad
    TAB / SHIFT+TAB select next / previous ship (white highlight)
    C               recenter the camera on the selected ship
    ARROWS, PGUP/DN orbit / zoom     P pause    F1 debug    F12 shot
"""

import json
import os
import sys
import time
import traceback

import numpy as np

from forge import Forge, Grid, Arrow, DashedLine, Label, Trail, WireMesh
from helm import Helm
from fleet import FleetSim, MoveCombination
from content import ContentDB

COEFF_RATE = 2.0          # coefficient units per second of held key
COEFF_SNAP = 0.5          # commit snaps coefficients to this grid


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
    """The visual twin of one ship: content-defined wire mesh + trail."""

    def __init__(self, forge_, klass, content):
        self.base, self.edges = content.mesh_for_class(klass)
        self.color = content.color_for_class(klass)
        self.mesh = WireMesh(self.base, self.edges, color=self.color,
                             width=0.05)
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

        self.content = ContentDB("content")
        self.forge = Forge(self.settings)
        self.helm = Helm(self.settings)
        self.helm.attach(self.forge.window)

        # ---- simulation + shakedown fleet ----
        self.sim = FleetSim(self.settings.get("seed", 1234), self.content)
        self.sim.spawn("mothership", (0.0, 0.0, 0.0))
        self.sim.spawn("fighter", (6.0, 0.0, 3.0), squad=1)
        self.sim.spawn("fighter", (8.0, 0.0, -2.0), squad=1)
        self.sim.spawn("fighter", (4.0, 0.0, -6.0), squad=1)
        self.sim.spawn("corvette", (-8.0, 0.0, 5.0), squad=2)
        self.sim.spawn("collector", (-11.0, 0.0, -1.0), squad=2)
        self.sim.spawn("frigate", (-6.0, 0.0, -8.0), squad=2)

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
        self.cmd_squad = 1
        self.paused = False
        self.snap = self.sim.snapshot()
        self._sync_views()
        self._prev_frame = time.perf_counter()

        self.forge.camera.distance = 42.0
        self.forge.camera.set_orbit((0.0, 0.0, 0.0))

        print("Homeworld: A Good Basis — shakedown shell.")
        print("W/S A/D R/F edit coefficients | ENTER commit | X mode | "
              "BACKSPACE clear | Q/E squad")
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
            axes["CAM_ZOOM"] * 0.9 * fdt,
        )

        snap = self.snap
        sel = self._selected_id()
        squad_positions = []
        for k, sid in enumerate(snap.ship_ids):
            p = snap.prev_pos[k] + (snap.pos[k] - snap.prev_pos[k]) * alpha
            v = snap.pos[k] - snap.prev_pos[k]
            self.views[sid].update(p, v, sid == sel)
            if snap.squad[k] == self.cmd_squad:
                squad_positions.append(p)

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

File 13 — settings.json (version bump)

{
    "title": "Homeworld: A Good Basis",
    "version": "0.6.0",
    "width": 1280,
    "height": 720,
    "fullscreen": false,
    "vsync": true,
    "bloom_strength": 0.85,
    "exposure": 2.5,
    "seed": 1234,
    "input": {
        "pilot_device": "keyboard",
        "navigator_device": "mouse",
        "keyboard_overrides": {}
    }
}

📋 YOUR STEPS

    Send to DeepSeek: the 13 files, verbatim, commit message: Apocrypha step 1: content data layer (ContentDB, ships.json, 5 meshes, narrator core, book placeholders) + app wiring — and update COMMENTARIES.md.
    Check the data layer: from the root folder, cmd, then: python -m content.demo
    Run the game: double-click run.bat.

👀 WHAT YOU SHOULD SEE

Step 2 (console):

CONTENT CHECK — content/ data layer
ships.json ........... 5 classes OK (collector, corvette, fighter, frigate, mothership)
meshes ............... 5 meshes OK (16-24 edges each)
narrator/core.json ... 7 lines OK
book ................. 2 excerpts, 2 PLACEHOLDER
                       PLACEHOLDER: book/ch1_excerpts.json :: ch1_placeholder_combination
                       PLACEHOLDER: book/ch1_excerpts.json :: ch1_placeholder_freighter
missions ............. 0 files
CONTENT CHECK PASSED

(That PLACEHOLDER ledger is the list of book excerpts waiting for you to paste from Strang — it will follow us until Mission 1 ships.)

Step 3 (the game): same scene as before, but now with five distinct ship silhouettes: the golden mothership, cyan dart fighters — and on the other side, an orange boxy corvette, a green pot-bellied collector (its intake ring faces forward), and a violet long-hulled frigate with a dorsal mast. Press F1: fleet rank now reads 5 (five independent signature columns!). Press Q or E: console says commanding squad 2 — compose a combination and press ENTER, and the other squad flies it, each ship at its own class speed (the frigate lumbering, the corvette brisk). TAB now cycles through all seven ships.
📝 REPORT BACK

The usual for both steps. Also: any mesh you find ugly — say so, they're two-minute JSON edits.

Next package: BRIDGE — the forge 2D overlay (INTERFACES v1.1) + the widget kit + the console FLEET ZONE. The Navigator picks up the mouse, sees the fleet matrix A live with ships as columns, and your partner officially joins the crew. 🚀❤️
