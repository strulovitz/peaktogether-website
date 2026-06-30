"""
build/room_from_spec.py -- Quake Parent 16 deliverable.

Turns ONE .room spec (keyword-block plain text) into the three validated content files:
  recipes/<node>.f1.json      (geometry + equation rooms; None for pure-text rooms)
  figures/<node>.f1.asy       (self-contained gold convention; every room)
  room_sources/<node>.json    (every room)

Pure core (parse / validate / emit_*) + a thin file-writing shell (build_room).
Output JSON is validated against map.raw_models before writing. The corrected local-color
model is structurally enforced: colors exist only inside stations; uncolored => black;
heart is per-step; colors_used is scanned, never authored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple, Optional

from map.raw_models import (
    SCHEMA_VERSION,
    LocalColor,
    Label,
    Draw,
    Recipe,
    StepGloss,
    TextBlock,
    FigureDecl,
    DrawingBlock,
    StepPair,
    CeilingEq,
    RoomSource,
    FreePoint, PointOn, Intersect, Midpoint, Foot, ReflectPoint,
    LineOp, Segment, RayOp, Parallel, Perpendicular, TangentAt, TangentFrom, Bisector,
    CircleCP, CircleCR, Circle3, Arc,
    EllipseFoci, EllipseAxes, ParabolaFD, HyperbolaFoci, Conic5,
    Polygon, Polyline, Series, AngleMark, FloatLabel,
)


class SpecError(Exception):
    """A malformed spec. Carries the 1-based source line and a plain-English message."""
    def __init__(self, line: int, msg: str):
        self.line = line
        self.msg = msg
        super().__init__(f"line {line}: {msg}")


class BuildResult(NamedTuple):
    node_id: str
    recipe_path: Optional[Path]
    asy_path: Path
    room_source_path: Path


# Internal Spec model (the parse target)

@dataclass
class ColorDecl:
    name: str
    hex: str
    line_no: int


@dataclass
class Attr:
    color: Optional[str] = None
    heart: bool = False
    label: Optional[str] = None
    at: str = "NE"
    marker: str = "none"
    stabilo: Optional[str] = None


@dataclass
class GeoOp:
    op: str
    name: str
    args: dict
    attr: Attr
    rough_xy: Optional[tuple] = None
    line_no: int = 0


@dataclass
class TermOp:
    color: Optional[str] = None
    latex: str = ""
    heart: bool = False
    stabilo: Optional[str] = None
    line_no: int = 0


@dataclass
class PhraseOp:
    color: Optional[str] = None
    words: str = ""
    heart: bool = False
    stabilo: Optional[str] = None
    line_no: int = 0


@dataclass
class Station:
    n: int
    gloss: str = ""
    colors: list = field(default_factory=list)
    geo_ops: list = field(default_factory=list)
    term_ops: list = field(default_factory=list)
    phrase_ops: list = field(default_factory=list)
    layout: Optional[str] = None
    text_raw: str = ""
    line_no: int = 0


@dataclass
class CeilingDecl:
    eq_label: str
    latex: str
    line_no: int = 0


@dataclass
class Spec:
    node_id: str = ""
    kind: str = ""
    edition: str = ""
    caption: str = ""
    final_step: int = 1
    ceilings: list = field(default_factory=list)
    stations: list = field(default_factory=list)


# Shared constants / regex

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_NODEID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_COLORNAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_SPAN_RE = re.compile(r"\{([a-z][a-z0-9_]*)\|((?:[^{}]|\{[^{}]*\})*)\}")
_TEXTCOLOR_RE = re.compile(r"\\textcolor\{([^}]+)\}\{")
_AT_DIRS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW", "center"}
_DEFAULT_STABILO = "#FFE000"


# STAGE 1 -- parse

def parse(spec_text: str) -> Spec:
    raw_lines = spec_text.splitlines()
    logical = _join_continuations(raw_lines)

    header = {"room": None, "kind": None, "import": None, "caption": None, "final": None}
    ceilings: list = []
    stations: list = []

    i = 0
    n = len(logical)

    while i < n:
        ln, text = logical[i]
        kw = text.split(None, 1)[0] if text.strip() else ""
        if kw == "station":
            break
        if kw == "color":
            raise SpecError(ln, "a `color` declaration appears before any `station` -- "
                                "colors are LOCAL to a station; there is no room-wide palette.")
        if kw in header:
            rest = text[len(kw):].strip()
            if kw == "final":
                if not rest.isdigit():
                    raise SpecError(ln, f"`final` expects a step number, got {rest!r}")
                header["final"] = int(rest)
            else:
                header[kw] = rest
        elif kw == "ceiling":
            rest = text[len("ceiling"):].strip()
            if "::" not in rest:
                raise SpecError(ln, "`ceiling` must be: ceiling <eq_label> :: <LaTeX>")
            lbl, latex = rest.split("::", 1)
            ceilings.append(CeilingDecl(lbl.strip(), latex.strip(), ln))
        elif kw == "":
            pass
        else:
            raise SpecError(ln, f"unknown header keyword {kw!r}")
        i += 1

    for key in ("room", "kind", "import", "caption", "final"):
        if header[key] is None:
            raise SpecError(1, f"missing required header keyword {key!r}")

    while i < n:
        ln, text = logical[i]
        kw = text.split(None, 1)[0]
        if kw != "station":
            raise SpecError(ln, f"expected `station`, got {kw!r}")
        rest = text[len("station"):].strip()
        if not rest.isdigit():
            raise SpecError(ln, f"`station` expects a number, got {rest!r}")
        st = Station(n=int(rest), line_no=ln)
        i += 1
        i = _parse_station_body(logical, i, n, st)
        stations.append(st)

    return Spec(
        node_id=header["room"],
        kind=header["kind"],
        edition=header["import"],
        caption=header["caption"],
        final_step=header["final"],
        ceilings=ceilings,
        stations=stations,
    )


def _join_continuations(raw_lines: list) -> list:
    out: list = []
    buf = ""
    start_ln = 0
    for idx, raw in enumerate(raw_lines, start=1):
        line = _strip_comment(raw)
        if buf == "":
            start_ln = idx
        if line.rstrip().endswith("\\"):
            buf += line.rstrip()[:-1] + " "
            continue
        buf += line
        if buf.strip() != "" or buf == "":
            out.append((start_ln, buf))
        buf = ""
    if buf.strip():
        out.append((start_ln, buf))
    return out


def _strip_comment(line: str) -> str:
    out = []
    in_math = False
    in_str = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "$" and not in_str:
            in_math = not in_math
            out.append(ch)
        elif ch == '"' and not in_math:
            in_str = not in_str
            out.append(ch)
        elif ch == "#" and not in_math and not in_str:
            rest = line[i+1:i+7]
            if len(rest) == 6 and all(c in '0123456789abcdefABCDEF' for c in rest):
                out.append(ch)
            else:
                break
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _parse_station_body(logical: list, i: int, n: int, st: Station) -> int:
    section = None
    text_lines: list = []
    while i < n:
        ln, text = logical[i]
        stripped = text.strip()
        kw = stripped.split(None, 1)[0] if stripped else ""

        if kw == "station":
            break

        if section is None:
            if kw == "gloss":
                st.gloss = stripped[len("gloss"):].strip()
            elif kw == "color":
                st.colors.append(_parse_color(stripped, ln))
            elif kw == "panel":
                section = "panel"
            elif kw == "text":
                section = "text"
            elif kw == "":
                pass
            else:
                raise SpecError(ln, f"unexpected keyword {kw!r} in station {st.n} header")
        elif section == "panel":
            if kw == "text":
                section = "text"
            elif kw == "":
                pass
            else:
                _parse_panel_op(stripped, ln, st)
        elif section == "text":
            text_lines.append(text.rstrip())
        i += 1

    st.text_raw = "\n".join(_l for _l in (t.strip() for t in text_lines)).strip()
    return i


def _parse_color(stripped: str, ln: int) -> ColorDecl:
    parts = stripped.split()
    if len(parts) != 3:
        raise SpecError(ln, "`color` must be: color <name> <#hex>")
    _, name, hexv = parts
    if not _COLORNAME_RE.match(name):
        raise SpecError(ln, f"color name {name!r} must match ^[a-z][a-z0-9_]*$")
    if not _HEX_RE.match(hexv):
        raise SpecError(ln, f"color hex {hexv!r} must be #RRGGBB")
    return ColorDecl(name, hexv, ln)


def _split_attrs(tokens: list, ln: int) -> tuple:
    pos: list = []
    attr = Attr()
    rough_xy = None
    for tok in tokens:
        if tok == "heart":
            attr.heart = True
        elif tok.startswith("color="):
            attr.color = tok[len("color="):]
        elif tok.startswith("label="):
            attr.label = tok[len("label="):]
        elif tok.startswith("at="):
            attr.at = tok[len("at="):]
            if attr.at not in _AT_DIRS:
                raise SpecError(ln, f"at={attr.at!r} not a valid placement")
        elif tok.startswith("marker="):
            attr.marker = tok[len("marker="):]
            if attr.marker not in ("none", "dot"):
                raise SpecError(ln, f"marker={attr.marker!r} must be none or dot")
        elif tok.startswith("stabilo="):
            attr.stabilo = tok[len("stabilo="):]
            if not _HEX_RE.match(attr.stabilo):
                raise SpecError(ln, f"stabilo={attr.stabilo!r} must be #RRGGBB")
        elif tok.startswith("@(") and tok.endswith(")"):
            body = tok[2:-1]
            try:
                x, y = (float(v) for v in body.split(","))
            except ValueError:
                raise SpecError(ln, f"rough position {tok!r} must be @(x,y)")
            rough_xy = (x, y)
        else:
            pos.append(tok)
    return pos, attr, rough_xy


def _tokenize_op(stripped: str) -> list:
    toks: list = []
    cur = ""
    in_math = False
    in_str = False
    for ch in stripped:
        if ch == "$":
            in_math = not in_math
            cur += ch
        elif ch == '"':
            in_str = not in_str
            cur += ch
        elif ch.isspace() and not in_math and not in_str:
            if cur:
                toks.append(cur)
                cur = ""
        else:
            cur += ch
    if cur:
        toks.append(cur)
    return toks


def _parse_panel_op(stripped: str, ln: int, st: Station) -> None:
    toks = _tokenize_op(stripped)
    op = toks[0]

    if op == "term":
        rest = toks[1:]
        color = None
        latex = None
        heart = False
        stabilo = None
        for t in rest:
            if t == "heart":
                heart = True
            elif t.startswith("stabilo="):
                stabilo = t[len("stabilo="):]
            elif t.startswith("$") and t.endswith("$"):
                latex = t
            elif color is None and _COLORNAME_RE.match(t):
                color = t
            else:
                raise SpecError(ln, f"unexpected token {t!r} in `term`")
        if latex is None:
            raise SpecError(ln, "`term` needs a $latex$ fragment")
        st.term_ops.append(TermOp(color, latex, heart, stabilo, ln))
        return
    if op == "phrase":
        rest = toks[1:]
        color = None
        words = None
        heart = False
        stabilo = None
        for t in rest:
            if t == "heart":
                heart = True
            elif t.startswith("stabilo="):
                stabilo = t[len("stabilo="):]
            elif t.startswith('"') and t.endswith('"'):
                words = t[1:-1]
            elif color is None and _COLORNAME_RE.match(t):
                color = t
            else:
                raise SpecError(ln, f"unexpected token {t!r} in `phrase`")
        if words is None:
            raise SpecError(ln, '`phrase` needs "quoted words"')
        st.phrase_ops.append(PhraseOp(color, words, heart, stabilo, ln))
        return
    if op == "layout":
        st.layout = stripped[len("layout"):].strip()
        return

    geo = _parse_geo_op(op, toks, ln)
    st.geo_ops.append(geo)


def _parse_geo_op(op: str, toks: list, ln: int) -> GeoOp:
    body = toks[1:]

    def need_name(b):
        if not b:
            raise SpecError(ln, f"`{op}` needs a <Name>")
        return b[0], b[1:]

    name, rest = need_name(body)
    pos, attr, rough_xy = _split_attrs(rest, ln)
    args: dict = {}

    def kw_index(kw, after=0):
        try:
            return pos.index(kw, after)
        except ValueError:
            return -1

    if op == "point":
        pass
    elif op == "point_on":
        j = kw_index("on")
        if j < 0:
            raise SpecError(ln, "`point_on` needs `on <path>`")
        args["path"] = pos[j + 1]
        for tok in pos[j + 2:]:
            if tok.startswith("t="):
                args["t"] = float(tok[2:])
            elif tok.startswith("near=(") and tok.endswith(")"):
                args["near"] = _parse_xy(tok[5:], ln)
    elif op == "intersect":
        j = kw_index("of")
        if j < 0 or len(pos) < j + 3:
            raise SpecError(ln, "`intersect` needs `of <pathA> <pathB>`")
        args["a"], args["b"] = pos[j + 1], pos[j + 2]
        for tok in pos[j + 3:]:
            if tok.startswith("near=(") and tok.endswith(")"):
                args["near"] = _parse_xy(tok[5:], ln)
    elif op == "midpoint":
        j = kw_index("of")
        args["a"], args["b"] = pos[j + 1], pos[j + 2]
    elif op == "foot":
        jf, jt = kw_index("from"), kw_index("to")
        args["point"], args["line"] = pos[jf + 1], pos[jt + 1]
    elif op == "reflect":
        jo = kw_index("over")
        if pos[0] == "of":
            args["point"] = pos[1]
        else:
            args["point"] = pos[0]
        args["over"] = pos[jo + 1]
    elif op in ("segment", "line", "ray"):
        if len(pos) < 2:
            raise SpecError(ln, f"`{op}` needs two endpoints")
        args["a"], args["b"] = pos[0], pos[1]
    elif op in ("parallel", "perp"):
        jt = kw_index("through")
        jto = kw_index("to")
        args["through"], args["to"] = pos[jt + 1], pos[jto + 1]
    elif op == "tangent_at":
        jc, ja = kw_index("on"), kw_index("at")
        args["curve"], args["at"] = pos[jc + 1], pos[ja + 1]
    elif op == "tangent_from":
        jc, jf = kw_index("to"), kw_index("from")
        args["curve"], args["frm"] = pos[jc + 1], pos[jf + 1]
        for tok in pos:
            if tok.startswith("near=(") and tok.endswith(")"):
                args["near"] = _parse_xy(tok[5:], ln)
    elif op == "bisector":
        args["a"], args["vertex"], args["b"] = pos[0], pos[1], pos[2]
    elif op == "circle_cp":
        jc, jt = kw_index("center"), kw_index("through")
        args["center"], args["through"] = pos[jc + 1], pos[jt + 1]
    elif op == "circle_cr":
        jc = kw_index("center")
        args["center"] = pos[jc + 1]
        jr, jv = kw_index("radius"), kw_index("radiusval")
        if jr >= 0:
            args["radius_points"] = (pos[jr + 1], pos[jr + 2])
        elif jv >= 0:
            args["radius_value"] = float(pos[jv + 1])
        else:
            raise SpecError(ln, "`circle_cr` needs `radius <A> <B>` or `radiusval <n>`")
    elif op == "circle_3":
        args["a"], args["b"], args["c"] = pos[0], pos[1], pos[2]
    elif op == "arc":
        jc, jf, jt = kw_index("center"), kw_index("from"), kw_index("to")
        args["center"], args["frm"], args["to"] = pos[jc + 1], pos[jf + 1], pos[jt + 1]
        args["direction"] = "cw" if "cw" in pos else "ccw"
    elif op == "ellipse_foci":
        jf, jt = kw_index("foci"), kw_index("through")
        args["f1"], args["f2"], args["through"] = pos[jf + 1], pos[jf + 2], pos[jt + 1]
    elif op == "ellipse_axes":
        jc, jma, jmi = kw_index("center"), kw_index("major"), kw_index("minor")
        args["center"], args["major_end"], args["minor_end"] = pos[jc + 1], pos[jma + 1], pos[jmi + 1]
    elif op == "parabola_fd":
        jf, jd = kw_index("focus"), kw_index("directrix")
        args["focus"], args["directrix"] = pos[jf + 1], pos[jd + 1]
    elif op == "hyperbola_foci":
        jf, jt = kw_index("foci"), kw_index("through")
        args["f1"], args["f2"], args["through"] = pos[jf + 1], pos[jf + 2], pos[jt + 1]
    elif op == "conic_5":
        args["p1"], args["p2"], args["p3"], args["p4"], args["p5"] = pos[:5]
    elif op in ("polygon", "polyline"):
        args["points"] = pos
    elif op == "series":
        ja, jt, jc, jk = (kw_index("along"), kw_index("to"),
                          kw_index("count"), kw_index("kind"))
        args["along"] = pos[ja + 1]
        args["to_curve"] = pos[jt + 1]
        args["count"] = int(pos[jc + 1])
        args["kind"] = pos[jk + 1]
    elif op == "angle":
        args["a"], args["vertex"], args["b"] = pos[0], pos[1], pos[2]
        args["right"] = "right" in pos
    else:
        raise SpecError(ln, f"unknown panel op {op!r}")

    return GeoOp(op=op, name=name, args=args, attr=attr, rough_xy=rough_xy, line_no=ln)


def _parse_xy(s: str, ln: int) -> tuple:
    body = s
    if body.startswith("("):
        body = body[1:]
    if body.endswith(")"):
        body = body[:-1]
    try:
        x, y = (float(v) for v in body.split(","))
    except ValueError:
        raise SpecError(ln, f"bad coordinate {s!r}")
    return (x, y)


# STAGE 2 -- validate

def validate(spec: Spec) -> None:
    if not _NODEID_RE.match(spec.node_id):
        raise SpecError(1, f"room id {spec.node_id!r} must match ^[a-z][a-z0-9_]*$")
    if spec.kind not in ("geometry", "equation", "text"):
        raise SpecError(1, f"kind {spec.kind!r} must be geometry|equation|text")
    if not spec.stations:
        raise SpecError(1, "room has no stations")

    for idx, st in enumerate(spec.stations, start=1):
        if st.n != idx:
            raise SpecError(st.line_no, f"station numbered {st.n}, expected {idx} "
                                        f"(stations must be contiguous from 1)")
    n_steps = len(spec.stations)
    if not (1 <= spec.final_step <= n_steps):
        raise SpecError(1, f"final={spec.final_step} out of range 1..{n_steps}")

    for c in spec.ceilings:
        if not c.latex:
            raise SpecError(c.line_no, "ceiling has empty LaTeX")

    for st in spec.stations:
        _validate_station(spec, st)


def _validate_station(spec: Spec, st: Station) -> None:
    decl: dict = {}
    for c in st.colors:
        if c.name in decl and decl[c.name] != c.hex:
            raise SpecError(c.line_no, f"color {c.name!r} redeclared with different hex")
        decl[c.name] = c.hex

    if spec.kind == "geometry":
        if st.phrase_ops:
            raise SpecError(st.line_no, "geometry room may not use `phrase`")
        if not st.geo_ops and not st.term_ops:
            raise SpecError(st.line_no, f"station {st.n}: geometry panel is empty")
    elif spec.kind == "equation":
        if st.geo_ops or st.phrase_ops:
            raise SpecError(st.line_no, "equation room panel uses only `term`/`layout`")
        if not st.term_ops:
            raise SpecError(st.line_no, f"station {st.n}: equation panel has no `term`")
    elif spec.kind == "text":
        if st.geo_ops or st.term_ops or st.layout:
            raise SpecError(st.line_no, "text room panel uses only `phrase`")
        if not st.phrase_ops:
            raise SpecError(st.line_no, f"station {st.n}: text panel has no `phrase`")

    hearts = (sum(1 for g in st.geo_ops if g.attr.heart)
              + sum(1 for t in st.term_ops if t.heart)
              + sum(1 for p in st.phrase_ops if p.heart))
    if hearts < 1:
        raise SpecError(st.line_no, f"station {st.n}: no `heart` -- every step needs "
                                    f"a current-step heart")

    used: set = set()
    for g in st.geo_ops:
        if g.attr.color:
            used.add(g.attr.color)
    for t in st.term_ops:
        if t.color:
            used.add(t.color)
    for p in st.phrase_ops:
        if p.color:
            used.add(p.color)
    used |= {m[0] for m in _SPAN_RE.findall(st.text_raw)}
    if st.layout:
        used |= {m[0] for m in _SPAN_RE.findall(st.layout)}

    for name in used:
        if name not in decl:
            raise SpecError(st.line_no, f"station {st.n}: color {name!r} used but not "
                                        f"declared with `color {name} #hex`")
    for c in st.colors:
        if c.name not in used:
            raise SpecError(c.line_no, f"declared color {c.name!r} is never used")

    defined: set = set()
    for st in spec.stations:
        for g in st.geo_ops:
            for ref in _refs_of(g):
                if ref not in defined:
                    raise SpecError(g.line_no, f"undefined reference {ref!r} (define it with an "
                                               f"earlier op in any station)")
            defined.add(g.name)

    for st in spec.stations:
        for g in st.geo_ops:
            if g.attr.marker == "dot" and g.op != "point":
                raise SpecError(g.line_no, "marker=dot only allowed on a `point` op")


def _refs_of(g: GeoOp) -> list:
    out: list = []
    a = g.args
    for k in ("path", "a", "b", "c", "point", "line", "over", "through", "to",
              "curve", "at", "frm", "vertex", "center", "f1", "f2",
              "focus", "directrix", "major_end", "minor_end", "along", "to_curve",
              "p1", "p2", "p3", "p4", "p5"):
        v = a.get(k)
        if isinstance(v, str):
            out.append(v)
    if "radius_points" in a:
        out.extend(a["radius_points"])
    if "points" in a:
        out.extend(a["points"])
    return out


# STAGE 3 -- emit_recipe

def emit_recipe(spec: Spec) -> Optional[Recipe]:
    has_geo = any(st.geo_ops or st.term_ops for st in spec.stations)
    if not has_geo:
        return None

    figure_id = f"{spec.node_id}.f1"
    ops: list = []
    decl_per_station = [{c.name: c.hex for c in st.colors} for st in spec.stations]

    for st, decl in zip(spec.stations, decl_per_station):
        for g in st.geo_ops:
            ops.append(_geo_op_to_recipe(g, st.n, decl))
        for ti, t in enumerate(st.term_ops, start=1):
            ops.append(_term_op_to_recipe(t, st.n, ti, decl))

    recipe = Recipe(
        schema_version=SCHEMA_VERSION,
        figure_id=figure_id,
        node_id=spec.node_id,
        edition=spec.edition,
        caption=spec.caption,
        n_steps=len(spec.stations),
        steps=[StepGloss(index=st.n, gloss=st.gloss) for st in spec.stations],
        ops=ops,
    )
    return recipe


def _draw_of(attr: Attr, step: int, decl: dict) -> Draw:
    lc = None
    if attr.color:
        lc = LocalColor(name=attr.color, hex=decl[attr.color])
    label = None
    if attr.label:
        label = Label(tex=attr.label, placement=attr.at)
    return Draw(
        local_color=lc,
        step=step,
        is_heart=attr.heart,
        label=label,
        marker=attr.marker,
    )


def _geo_op_to_recipe(g: GeoOp, step: int, decl: dict):
    draw = _draw_of(g.attr, step, decl)
    a = g.args
    op = g.op
    name = g.name
    if op == "point":
        return FreePoint(name=name, op="free_point", rough_xy=g.rough_xy, draw=draw)
    if op == "point_on":
        return PointOn(name=name, op="point_on", path=a["path"],
                       t=a.get("t"), near=a.get("near"), draw=draw)
    if op == "intersect":
        return Intersect(name=name, op="intersect", a=a["a"], b=a["b"],
                         near=a.get("near"), draw=draw)
    if op == "midpoint":
        return Midpoint(name=name, op="midpoint", a=a["a"], b=a["b"], draw=draw)
    if op == "foot":
        return Foot(name=name, op="foot", point=a["point"], line=a["line"], draw=draw)
    if op == "reflect":
        return ReflectPoint(name=name, op="reflect_point", point=a["point"],
                            over=a["over"], draw=draw)
    if op == "line":
        return LineOp(name=name, op="line", a=a["a"], b=a["b"], draw=draw)
    if op == "segment":
        return Segment(name=name, op="segment", a=a["a"], b=a["b"], draw=draw)
    if op == "ray":
        return RayOp(name=name, op="ray", a=a["a"], b=a["b"], draw=draw)
    if op == "parallel":
        return Parallel(name=name, op="parallel", through=a["through"], to=a["to"], draw=draw)
    if op == "perp":
        return Perpendicular(name=name, op="perpendicular", through=a["through"],
                             to=a["to"], draw=draw)
    if op == "tangent_at":
        return TangentAt(name=name, op="tangent_at", curve=a["curve"], at=a["at"], draw=draw)
    if op == "tangent_from":
        return TangentFrom(name=name, op="tangent_from", curve=a["curve"], frm=a["frm"],
                           near=a.get("near"), draw=draw)
    if op == "bisector":
        return Bisector(name=name, op="bisector", a=a["a"], vertex=a["vertex"],
                        b=a["b"], draw=draw)
    if op == "circle_cp":
        return CircleCP(name=name, op="circle_cp", center=a["center"],
                        through=a["through"], draw=draw)
    if op == "circle_cr":
        return CircleCR(name=name, op="circle_cr",
                        radius_points=a.get("radius_points"),
                        radius_value=a.get("radius_value"),
                        center=a["center"], draw=draw)
    if op == "circle_3":
        return Circle3(name=name, op="circle_3", a=a["a"], b=a["b"], c=a["c"], draw=draw)
    if op == "arc":
        return Arc(name=name, op="arc", center=a["center"], frm=a["frm"], to=a["to"],
                   direction=a["direction"], draw=draw)
    if op == "ellipse_foci":
        return EllipseFoci(name=name, op="ellipse_foci", f1=a["f1"], f2=a["f2"],
                           through=a["through"], draw=draw)
    if op == "ellipse_axes":
        return EllipseAxes(name=name, op="ellipse_axes", center=a["center"],
                           major_end=a["major_end"], minor_end=a["minor_end"], draw=draw)
    if op == "parabola_fd":
        return ParabolaFD(name=name, op="parabola_fd", focus=a["focus"],
                          directrix=a["directrix"], draw=draw)
    if op == "hyperbola_foci":
        return HyperbolaFoci(name=name, op="hyperbola_foci", f1=a["f1"], f2=a["f2"],
                             through=a["through"], draw=draw)
    if op == "conic_5":
        return Conic5(name=name, op="conic_5", p1=a["p1"], p2=a["p2"], p3=a["p3"],
                      p4=a["p4"], p5=a["p5"], draw=draw)
    if op == "polygon":
        return Polygon(name=name, op="polygon", points=a["points"], draw=draw)
    if op == "polyline":
        return Polyline(name=name, op="polyline", points=a["points"], draw=draw)
    if op == "series":
        return Series(name=name, op="series", along=a["along"], to_curve=a["to_curve"],
                      count=a["count"], kind=a["kind"], draw=draw)
    if op == "angle":
        return AngleMark(name=name, op="angle_mark", a=a["a"], vertex=a["vertex"],
                         b=a["b"], right=a["right"], draw=draw)
    raise SpecError(g.line_no, f"no recipe mapping for op {op!r}")


def _term_op_to_recipe(t: TermOp, step: int, idx: int, decl: dict):
    lc = LocalColor(name=t.color, hex=decl[t.color]) if t.color else None
    draw = Draw(local_color=lc, step=step, is_heart=t.heart,
                label=Label(tex=t.latex, placement="center"), marker="none")
    return FloatLabel(name=f"term_{step}_{idx}", op="label",
                      at=f"termpos_{step}_{idx}", draw=draw)


# STAGE 4 -- emit_asy

def emit_asy(spec: Spec) -> str:
    is_geometry = any(st.geo_ops for st in spec.stations)
    L: list = []
    node = spec.node_id

    L.append(f"// figure.{node}.f1.asy -- {spec.caption}")
    L.append(f'// Self-contained convention. Compile: asy -u "highlight=k" figure.{node}.f1.asy')
    L.append("// highlight=-1 => OFF (all black). highlight=k => step k colors + step k heart Stabilo.")
    L.append("")
    L.append("import geometry;")
    L.append("import graph;")
    L.append('settings.outformat = "png";')
    L.append("unitsize(1cm);")
    L.append("")
    L.append("int highlight = -1;")
    L.append("usersetting();")
    L.append("")

    L.append("// ---- palette (LOCAL; pure black when uncolored) ----")
    L.append("pen BLACK = rgb(0,0,0) + linewidth(1.0pt);")
    seen: dict = {}
    for st in spec.stations:
        for c in st.colors:
            if c.name not in seen:
                seen[c.name] = c.hex
                L.append(f"pen {c.name} = {_rgb(c.hex)} + linewidth(1.6pt);")
    L.append("")

    L.append("// ---- bright Stabilo markers (current-step heart only; laid UNDER the ink) ----")
    stabilo_names = _stabilo_pen_table(spec)
    for pen_name, hexv in stabilo_names["pens"]:
        L.append(f"pen {pen_name} = {_rgb(hexv)} + opacity(0.45) + linewidth(9pt) + squarecap;")
    L.append("")

    L.append("// ---- ZONE 2: construction ----")
    if is_geometry:
        L.extend(_emit_construction(spec))
    else:
        L.extend(_emit_label_layout(spec))
    L.append("")

    L.append("// ---- ZONE 4: render (highlight-driven) ----")
    L.append("void drawAll(int highlight) {")
    for st in spec.stations:
        L.append(f"  bool on{st.n} = (highlight=={st.n});")
    L.append("")
    L.extend(_emit_stabilo_underlay(spec, stabilo_names))
    L.append("")
    L.extend(_emit_ink_pass(spec, is_geometry))
    L.append("}")
    L.append("drawAll(highlight);")
    L.append("")
    return "\n".join(L)


def _rgb(hexv: str) -> str:
    s = hexv.lstrip("#")
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    return f"rgb({r}/255, {g}/255, {b}/255)"


def _stabilo_pen_table(spec: Spec) -> dict:
    pens: list = []
    by_elem: dict = {}
    for st in spec.stations:
        hi = 0
        for g in st.geo_ops:
            if g.attr.heart:
                hi += 1
                pen = f"STABILO_{st.n}_{hi}"
                hexv = g.attr.stabilo or _DEFAULT_STABILO
                pens.append((pen, hexv))
                by_elem[(st.n, "geo", g.name)] = pen
        for ti, t in enumerate(st.term_ops, start=1):
            if t.heart:
                hi += 1
                pen = f"STABILO_{st.n}_{hi}"
                pens.append((pen, t.stabilo or _DEFAULT_STABILO))
                by_elem[(st.n, "term", ti)] = pen
        for pi, p in enumerate(st.phrase_ops, start=1):
            if p.heart:
                hi += 1
                pen = f"STABILO_{st.n}_{hi}"
                pens.append((pen, p.stabilo or _DEFAULT_STABILO))
                by_elem[(st.n, "phrase", pi)] = pen
    return {"pens": pens, "by_elem": by_elem}


def _emit_construction(spec: Spec) -> list:
    out: list = []
    needs_series = any(g.op == "series" for st in spec.stations for g in st.geo_ops)
    series_curves: set = set()

    for st in spec.stations:
        for g in st.geo_ops:
            out.extend(_GEO_SNIPPET(g, series_curves))

    if needs_series:
        out.append("")
        out.extend(_emit_series_support(spec))
    return out


def _GEO_SNIPPET(g: GeoOp, series_curves: set) -> list:
    a = g.args
    op = g.op
    nm = g.name
    if op == "point":
        x, y = (g.rough_xy or (0.0, 0.0))
        return [f"pair {nm} = ({x},{y});"]
    if op == "point_on":
        t = a.get("t", 0.5)
        return [f"point {nm} = point({a['path']}, {t});"]
    if op == "intersect":
        return [f"pair {nm} = intersectionpoint({a['a']}, {a['b']});"]
    if op == "midpoint":
        return [f"point {nm} = midpoint(segment({a['a']}, {a['b']}));"]
    if op == "foot":
        return [f"point {nm} = foot({a['point']}, line({_line_pts(a['line'])}));"]
    if op == "reflect":
        return [f"transform _r_{nm} = reflect(line({_line_pts(a['over'])}));",
                f"pair {nm} = _r_{nm} * {a['point']};"]
    if op == "line":
        return [f"line {nm} = line({a['a']}, {a['b']});"]
    if op == "segment":
        return [f"path {nm} = {a['a']}--{a['b']};"]
    if op == "ray":
        return [f"ray {nm} = ray({a['a']}, {a['b']});"]
    if op == "parallel":
        return [f"line {nm} = parallel({a['through']}, {a['to']});"]
    if op == "perp":
        return [f"line {nm} = perpendicular({a['through']}, {a['to']});"]
    if op == "tangent_at":
        return [f"line {nm} = tangent({a['curve']}, {a['at']});"]
    if op == "tangent_from":
        return [f"line[] _t_{nm} = tangents({a['curve']}, {a['frm']});",
                f"line {nm} = _t_{nm}[0];"]
    if op == "bisector":
        return [f"line {nm} = bisector({a['a']}, {a['vertex']}, {a['b']});"]
    if op == "circle_cp":
        return [f"circle {nm} = circle({a['center']}, {a['through']});"]
    if op == "circle_cr":
        if a.get("radius_points"):
            p, q = a["radius_points"]
            return [f"circle {nm} = circle({a['center']}, abs({q}-{p}));"]
        return [f"circle {nm} = circle({a['center']}, {a['radius_value']});"]
    if op == "circle_3":
        return [f"circle {nm} = circle({a['a']}, {a['b']}, {a['c']});"]
    if op == "arc":
        d = a["direction"]
        return [
            f"real _r_{nm} = abs({a['frm']}-{a['center']});",
            f"path {nm} = arc({a['center']}, _r_{nm}, "
            f"degrees({a['frm']}-{a['center']}), degrees({a['to']}-{a['center']}), "
            f"{'CCW' if d == 'ccw' else 'CW'});",
        ]
    if op == "ellipse_foci":
        return [f"ellipse {nm} = ellipse({a['f1']}, {a['f2']}, {a['through']});"]
    if op == "ellipse_axes":
        return [f"ellipse {nm} = ellipse({a['center']}, {a['major_end']}, {a['minor_end']});"]
    if op == "parabola_fd":
        return [f"parabola {nm} = parabola({a['focus']}, {a['directrix']});"]
    if op == "hyperbola_foci":
        f1, f2, P = a["f1"], a["f2"], a["through"]
        return [f"hyperbola {nm} = hyperbola({f1}, {f2}, "
                f"abs(abs({P}-{f1})-abs({P}-{f2})), byfoci);"]
    if op == "conic_5":
        return [f"conic {nm} = conic({a['p1']}, {a['p2']}, {a['p3']}, "
                f"{a['p4']}, {a['p5']});"]
    if op == "polygon":
        pts = "--".join(a["points"]) + "--cycle"
        return [f"path {nm} = {pts};"]
    if op == "polyline":
        pts = "--".join(a["points"])
        return [f"path {nm} = {pts};"]
    if op == "series":
        series_curves.add((g.name, a["along"], a["to_curve"], a["count"], a["kind"]))
        return [f"// series {nm}: built in series-support block below"]
    if op == "angle":
        return [f"// angle {nm}: drawn via markangle in ZONE 4"]
    return [f"// (no construction snippet for {op})"]


def _line_pts(ref: str) -> str:
    return ref


def _emit_series_support(spec: Spec) -> list:
    out: list = ["// ---- series support (rect loops, gold lemma_2 pattern) ----"]
    polylines: dict = {}
    for st in spec.stations:
        for g in st.geo_ops:
            if g.op == "polyline":
                polylines[g.name] = g.args["points"]

    emitted_helper = False
    for st in spec.stations:
        for g in st.geo_ops:
            if g.op != "series":
                continue
            a = g.args
            curve = a["to_curve"]
            pts = polylines.get(curve)
            if pts is None:
                out.append(f"// series {g.name}: curve {curve} is not a polyline; "
                           f"using its path bounding ordinates")
                continue
            if not emitted_helper:
                out.extend(_curveY_helper(pts, suffix=""))
                emitted_helper = True
            xs = [f"{pts[i]}.x" for i in range(len(pts))]
            out.append(f"// rectangles for series {g.name} (kind={a['kind']}, count={a['count']})")
            out.append(f"path[] {g.name};")
            out.append(f"real[] _xs_{g.name} = {{{', '.join(f'{pts[i]}.x' for i in range(len(pts)))}}};")
            out.append(f"for (int i=0; i<_xs_{g.name}.length-1; ++i) {{")
            out.append(f"  real x0=_xs_{g.name}[i], x1=_xs_{g.name}[i+1];")
            if a["kind"] == "inscribed_rects":
                out.append("  real h = curveY(min(x0,x1));")
            elif a["kind"] == "circumscribed_rects":
                out.append("  real h = curveY(max(x0,x1));")
            elif a["kind"] == "ordinates":
                out.append("  real h = curveY(x1);")
            else:
                out.append("  real h = curveY(x1);")
            out.append(f"  {g.name}.push((x0,0)--(x1,0)--(x1,h)--(x0,h)--cycle);")
            out.append("}")
    return out


def _curveY_helper(pts: list, suffix: str) -> list:
    arr = ", ".join(pts)
    if suffix != "":
        return []
    return [
        f"pair[] _P{suffix} = {{{arr}}};",
        f"real curveY{suffix}(real x) {{",
        f"  for (int i=0; i<_P{suffix}.length-1; ++i) {{",
        f"    if (x >= _P{suffix}[i].x && x <= _P{suffix}[i+1].x) {{",
        f"      real t = (x - _P{suffix}[i].x)/(_P{suffix}[i+1].x - _P{suffix}[i].x);",
        f"      return _P{suffix}[i].y + t*(_P{suffix}[i+1].y - _P{suffix}[i].y);",
        f"    }}",
        f"  }}",
        f"  return _P{suffix}[_P{suffix}.length-1].y;",
        f"}}",
    ]


def _emit_label_layout(spec: Spec) -> list:
    out: list = []
    row_gap = 2.2
    for st in spec.stations:
        y = -(st.n - 1) * row_gap
        if st.term_ops:
            n = len(st.term_ops)
            for ti in range(1, n + 1):
                x = (ti - (n + 1) / 2.0) * 2.4
                out.append(f"pair _termpos_{st.n}_{ti} = ({x:.2f}, {y:.2f});")
        if st.phrase_ops:
            n = len(st.phrase_ops)
            for pi in range(1, n + 1):
                yy = y - (pi - 1) * 0.9
                out.append(f"pair _phrasepos_{st.n}_{pi} = (0, {yy:.2f});")
    return out


def _emit_stabilo_underlay(spec: Spec, stab: dict) -> list:
    out: list = ["  // STABILO underlay (current step's heart only)"]
    by = stab["by_elem"]
    for st in spec.stations:
        for g in st.geo_ops:
            if g.attr.heart:
                pen = by[(st.n, "geo", g.name)]
                out.extend(_draw_geom(g, on=f"on{st.n}", pen=pen, stabilo=True))
        for ti, t in enumerate(st.term_ops, start=1):
            if t.heart:
                pen = by[(st.n, "term", ti)]
                out.append(f"  if (on{st.n}) label({_tex_str(t.latex)}, "
                           f"_termpos_{st.n}_{ti}, {pen});")
        for pi, p in enumerate(st.phrase_ops, start=1):
            if p.heart:
                pen = by[(st.n, "phrase", pi)]
                out.append(f"  if (on{st.n}) label({_tex_str(p.words, raw=True)}, "
                           f"_phrasepos_{st.n}_{pi}, {pen});")
    return out


def _emit_ink_pass(spec: Spec, is_geometry: bool) -> list:
    out: list = ["  // ink pass"]

    if is_geometry:
        for st in reversed(spec.stations):
            on = f"on{st.n}"
            for g in st.geo_ops:
                pen = g.attr.color if g.attr.color else "BLACK"
                out.extend(_draw_geom(g, on=on, pen=pen, stabilo=False))
            for ti, t in enumerate(st.term_ops, start=1):
                pen = t.color if t.color else "BLACK"
                out.append(f"  label({_tex_str(t.latex)}, _termpos_{st.n}_{ti}, "
                           f"{on} ? {pen} : BLACK);")
        for st in spec.stations:
            for g in st.geo_ops:
                if g.attr.label:
                    out.append(f"  label({_tex_str(g.attr.label)}, {g.name}, "
                               f"{_align(g.attr.at)});")
    else:
        for st in spec.stations:
            on = f"on{st.n}"
            for ti, t in enumerate(st.term_ops, start=1):
                pen = t.color if t.color else "BLACK"
                out.append(f"  label({_tex_str(t.latex)}, _termpos_{st.n}_{ti}, "
                           f"{on} ? {pen} : BLACK);")
            for pi, p in enumerate(st.phrase_ops, start=1):
                pen = p.color if p.color else "BLACK"
                out.append(f"  label({_tex_str(p.words, raw=True)}, _phrasepos_{st.n}_{pi}, "
                           f"{on} ? {pen} : BLACK);")
    return out


def _draw_geom(g: GeoOp, on: str, pen: str, stabilo: bool) -> list:
    nm = g.name
    op = g.op
    if op == "point":
        if stabilo:
            return [f"  if ({on}) dot({nm}, {pen});"]
        if g.attr.marker == "dot":
            color = pen if pen != "BLACK" else "BLACK"
            return [f"  dot({nm}, {on} ? {color} : BLACK);"]
        return []
    if op == "series":
        if stabilo:
            return [f"  if ({on}) for (path _r : {nm}) draw(_r, {pen});"]
        if g.args["kind"] == "inscribed_rects":
            fill = "rgb(142/255,36/255,170/255)+opacity(0.12)"
            return [f"  for (path _r : {nm}) filldraw(_r, {fill}, {on} ? {pen} : BLACK);"]
        return [f"  for (path _r : {nm}) draw(_r, {on} ? {pen} : BLACK);"]
    if op == "angle":
        a = g.args
        if stabilo:
            return []
        return [f"  markangle(line({a['vertex']},{a['a']}), line({a['vertex']},{a['b']}), "
                f"radius=0.5cm, {on} ? {pen} : BLACK);"]
    if stabilo:
        return [f"  if ({on}) draw({nm}, {pen});"]
    return [f"  draw({nm}, {on} ? {pen} : BLACK);"]


def _tex_str(latex: str, raw: bool = False) -> str:
    s = latex
    if not raw and not (s.startswith("$") and s.endswith("$")):
        s = f"${s}$"
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def _align(at: str) -> str:
    return {"N": "N", "S": "S", "E": "E", "W": "W", "NE": "NE", "NW": "NW",
            "SE": "SE", "SW": "SW", "center": "Center"}.get(at, "NE")


# STAGE 5 -- emit_room_source

def emit_room_source(spec: Spec) -> RoomSource:
    node = spec.node_id
    figure_id = f"{node}.f1"
    has_recipe = any(st.geo_ops or st.term_ops for st in spec.stations)

    union: dict = {}
    for st in spec.stations:
        for c in st.colors:
            union[(c.name, c.hex)] = LocalColor(name=c.name, hex=c.hex)
    figure_colors = list(union.values())

    fig = FigureDecl(
        figure_id=figure_id,
        asy_path=f"figures/{figure_id}.asy",
        recipe_path=(f"recipes/{figure_id}.json" if has_recipe else f"figures/{figure_id}.asy"),
        n_steps=len(spec.stations),
        caption=spec.caption,
        colors_used=figure_colors,
    )

    blocks: list = []
    for st in spec.stations:
        decl = {c.name: c.hex for c in st.colors}
        expanded = _expand_text(st, decl)
        scanned = _scan_colors_used(expanded, decl, st)
        blocks.append(StepPair(
            pair_id=f"{node}.s{st.n}",
            step_index=st.n,
            drawing=DrawingBlock(block_id=f"{node}.s{st.n}.fig",
                                 figure_id=figure_id, highlight_step=st.n),
            text=TextBlock(block_id=f"{node}.s{st.n}.txt",
                           latex=expanded, colors_used=scanned),
        ))

    ceilings = [CeilingEq(eq_id=f"{node}.eq{i}", latex=c.latex)
                for i, c in enumerate(spec.ceilings)]

    room = RoomSource(
        schema_version=SCHEMA_VERSION,
        node_id=node,
        edition=spec.edition,
        figures=[fig],
        blocks=blocks,
        final_pair_id=f"{node}.s{spec.final_step}",
        ceiling_equations=ceilings,
    )
    return room


def _expand_text(st: Station, decl: dict) -> str:
    raw = st.text_raw
    if not raw:
        frags = []
        for p in st.phrase_ops:
            if p.color:
                frags.append(f"\\textcolor{{{p.color}}}{{{p.words}}}")
            else:
                frags.append(p.words)
        return " ".join(frags) if frags else ""
    return _SPAN_RE.sub(lambda m: f"\\textcolor{{{m.group(1)}}}{{{m.group(2)}}}", raw)


def _scan_colors_used(expanded_latex: str, decl: dict, st: Station) -> list:
    names = []
    for nm in _TEXTCOLOR_RE.findall(expanded_latex):
        if nm not in names:
            names.append(nm)
    out: list = []
    for nm in names:
        if nm not in decl:
            raise SpecError(st.line_no, f"text uses color {nm!r} not declared in station {st.n}")
        out.append(LocalColor(name=nm, hex=decl[nm]))
    return out


# SHELL -- build_room

def build_room(spec_text: str, out_root: Path, *, write: bool = True) -> BuildResult:
    spec = parse(spec_text)
    validate(spec)
    recipe = emit_recipe(spec)
    asy = emit_asy(spec)
    room = emit_room_source(spec)

    figure_id = f"{spec.node_id}.f1"
    out_root = Path(out_root)
    recipe_path = out_root / "recipes" / f"{figure_id}.json"
    asy_path = out_root / "figures" / f"{figure_id}.asy"
    room_path = out_root / "room_sources" / f"{spec.node_id}.json"

    if write:
        (out_root / "figures").mkdir(parents=True, exist_ok=True)
        (out_root / "room_sources").mkdir(parents=True, exist_ok=True)
        if recipe is not None:
            (out_root / "recipes").mkdir(parents=True, exist_ok=True)
            recipe_path.write_text(recipe.model_dump_json(indent=2, exclude_none=True),
                                   encoding="utf-8")
        asy_path.write_text(asy, encoding="utf-8")
        room_path.write_text(room.model_dump_json(indent=2, exclude_none=True),
                             encoding="utf-8")

    return BuildResult(
        node_id=spec.node_id,
        recipe_path=(recipe_path if recipe is not None else None),
        asy_path=asy_path,
        room_source_path=room_path,
    )
