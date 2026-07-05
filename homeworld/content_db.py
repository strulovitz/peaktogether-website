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
