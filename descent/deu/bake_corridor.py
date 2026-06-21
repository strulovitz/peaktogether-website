#!/usr/bin/env python3
"""
DEU — Descent Editing Utility :: bake_corridor.py  (full stain+thread model)
============================================================================
Offline image baker. ONE corridor .txt -> transparent, colored, sharp PNGs,
one per (robot, explanation-layer). No intelligence, no game dependencies.
Trusts nothing: compiles each layer in isolation, reports failures precisely.

TWO COLOR SYSTEMS (see DESIGN HANDOFF):
  * STAINS  (background) : MACRO, SACRED, span the whole corridor, never altered.
  * THREADS (foreground) : MICRO, page-local; same id => same hue on that page,
                           distinct ids => distinct hues; AUTO-coloured; legibility
                           yields to the stain it sits on.

TOOLCHAIN (install once): TeX Live (full) -> pdflatex, dvisvgm, standalone,
xcolor, soul ;  and  pip install pillow.

USAGE:
    python deu/bake_corridor.py corridors/maxwell.txt --out baked/maxwell --dpi 600
"""

from __future__ import annotations
import argparse, colorsys, re, shutil, subprocess, sys, tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("FATAL: Pillow not installed.  Run:  pip install pillow", file=sys.stderr)
    sys.exit(2)

LAYERS = ("mathematician", "physicist", "biologist", "engineer")


# ----------------------------------------------------------------------------
# 0. Toolchain
# ----------------------------------------------------------------------------
def _require(tool: str, hint: str) -> str:
    p = shutil.which(tool)
    if not p:
        print(f"FATAL: '{tool}' not found on PATH.\n       {hint}", file=sys.stderr)
        sys.exit(2)
    return p

def check_toolchain() -> dict[str, str]:
    tools = {
        "pdflatex": _require("pdflatex",
            "Install TeX Live (full) or MiKTeX: https://www.tug.org/texlive/"),
    }
    # Preferred PDF->PNG: pdftocairo (Poppler; ships with MiKTeX & most TeX installs)
    pc = shutil.which("pdftocairo")
    if pc:
        tools["pdftocairo"] = pc
    # Fallback rasteriser
    dv = shutil.which("dvisvgm")
    if dv:
        tools["dvisvgm"] = dv
    if "pdftocairo" not in tools and "dvisvgm" not in tools:
        print("FATAL: need either 'pdftocairo' (Poppler) or 'dvisvgm' on PATH.\n"
              "       Both ship with full TeX Live / MiKTeX.", file=sys.stderr)
        sys.exit(2)
    return tools


# ----------------------------------------------------------------------------
# 1. Lenient corridor parsing (baker-owned; separate from the game's parser)
# ----------------------------------------------------------------------------
_STAIN_LINE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*=\s*([01]?\.?\d+)\s+([01]?\.?\d+)\s+([01]?\.?\d+)\s*(?:#.*)?$"
)

def _grab_block(text: str, keyword: str, start: int = 0) -> tuple[str | None, int]:
    """Return (body, end_index) for `KEYWORD { ... }`, brace-counting LaTeX braces."""
    m = re.compile(rf"{keyword}\s*\{{").search(text, start)
    if not m:
        return None, start
    i = m.end(); depth = 1; body_start = i
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[body_start:i].strip(), i + 1
        i += 1
    return None, len(text)  # unbalanced

@dataclass
class RobotEntry:
    number: int
    name: str
    explains: dict[str, str] = field(default_factory=dict)

@dataclass
class CorridorEntry:
    title: str
    stains: dict[str, tuple[float, float, float]]
    robots: list[RobotEntry]

def parse_corridor(path: Path) -> CorridorEntry:
    raw = path.read_text(encoding="utf-8")

    stains: dict[str, tuple[float, float, float]] = {}
    body, _ = _grab_block(raw, "STAINS")
    if body:
        for line in body.splitlines():
            m = _STAIN_LINE.match(line)
            if m:
                stains[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))

    tbody, _ = _grab_block(raw, "TITLE")
    title = (tbody or path.stem).strip()

    robots: list[RobotEntry] = []
    chunks = re.split(r"^\s*ROBOT:\s*(\d+)\s*$", raw, flags=re.MULTILINE)
    for i in range(1, len(chunks), 2):
        number = int(chunks[i])
        rbody = chunks[i + 1] if i + 1 < len(chunks) else ""
        nbody, _ = _grab_block(rbody, "NAME")
        entry = RobotEntry(number=number, name=(nbody or f"robot{number}").strip())
        for layer in LAYERS:
            blk, _ = _grab_block(rbody, f"EXPLAIN_{layer.upper()}")
            if blk is not None:
                entry.explains[layer] = blk
        robots.append(entry)

    return CorridorEntry(title=title, stains=stains, robots=robots)


# ----------------------------------------------------------------------------
# 2. Marker scanning + nested span tree  (\stain{key}{...}, \thread{id}{...})
# ----------------------------------------------------------------------------
_MARKER = re.compile(r"\\(stain|thread)\{([A-Za-z_]\w*)\}\{")

def _collect_thread_ids(latex: str) -> list[str]:
    """Distinct \thread ids in document order (page-local)."""
    seen: list[str] = []
    for m in _MARKER.finditer(latex):
        if m.group(1) == "thread" and m.group(2) not in seen:
            seen.append(m.group(2))
    return seen


_ARC_RE = re.compile(r"\[\[\s*(.*?)\s*\|\s*(.*?)\s*\]\]")

_VALUEARC_CMD = r"""\newcommand{\valuearc}[2]{%
  \begin{tikzpicture}[baseline=(X.base)]%
    \node[inner sep=2pt] (X) {#1};%
    \draw[color=descentprose, line width=0.8pt]%
      ([yshift=2pt]X.north west) %
      .. controls ($(X.north west)!0.5!(X.north east)+(0,10pt)$) .. %
      ([yshift=2pt]X.north east);%
    \node[above=8pt, font=\scriptsize, text=descentprose] %
      at ($(X.north west)!0.5!(X.north east)$) {\textbf{#2}};%
  \end{tikzpicture}%
}"""

def expand_arcs(latex: str) -> tuple[str, bool]:
    """Replace [[ expr | value ]] with \\valuearc{expr}{value}."""
    matches = list(_ARC_RE.finditer(latex))
    if not matches:
        return latex, False
    result: list[str] = []
    cursor = 0
    for m in matches:
        result.append(latex[cursor:m.start()])
        expr = m.group(1).strip()
        value = m.group(2).strip()
        result.append(rf"\valuearc{{{expr}}}{{{value}}}")
        cursor = m.end()
    result.append(latex[cursor:])
    return "".join(result), True


# ----------------------------------------------------------------------------
# 3. Thread auto-colouring — distinct from siblings, legible on any stain.
#    Thread colour is NOT sacred (which hue is free); only same-id==same-hue,
#    distinct-id==distinct-hue, and legibility matter. We choose evenly-spaced
#    hues and clamp lightness so letters read on dark stains AND on transparency.
# ----------------------------------------------------------------------------
def assign_thread_colors(ids: list[str]) -> dict[str, tuple[float, float, float]]:
    """Evenly spaced, vivid-but-light hues so they read on dark stains/transparency."""
    out: dict[str, tuple[float, float, float]] = {}
    n = max(len(ids), 1)
    for k, tid in enumerate(ids):
        hue = (k / n)                       # spread around the wheel -> distinct
        # light & saturated: sits on dark stains (red/blue/purple) and on the world
        r, g, b = colorsys.hls_to_rgb(hue, 0.72, 0.85)
        out[tid] = (round(r, 4), round(g, 4), round(b, 4))
    return out


# ----------------------------------------------------------------------------
# 4. Expand markers -> real LaTeX (xcolor). Brace-matched, nesting-safe.
#    STAIN  -> \colorbox{key}{ ... }          (sacred background wash)
#    THREAD -> {\color{thread__id} ... }      (foreground letters)
#    \colorbox handles display math (unlike soul's \hl).
# ----------------------------------------------------------------------------
def expand_markers(latex: str,
                   stains: dict[str, tuple[float, float, float]],
                   thread_colors: dict[str, tuple[float, float, float]],
                   unknown_stains: list[str]) -> str:
    """Brace-matched, nesting-safe expansion of \stain{} and \thread{}."""
    def expand(s: str) -> str:
        res, i = [], 0
        while i < len(s):
            m = _MARKER.search(s, i)
            if not m:
                res.append(s[i:]); break
            res.append(s[i:m.start()])
            kind, key = m.group(1), m.group(2)
            depth, b, bs = 1, m.end(), m.end()
            while b < len(s) and depth > 0:
                if s[b] == "{": depth += 1
                elif s[b] == "}": depth -= 1
                b += 1
            body = expand(s[bs:b - 1])   # recurse -> nesting works
            if kind == "thread":
                res.append(rf"{{\color{{thread__{key}}} {body}}}")
            else:  # stain (sacred); unknown -> uncoloured + reported
                if key in stains:
                    # \colorbox handles display math (unlike soul's \hl).
                    # We re-assert the prose colour inside so letters stay light on the stain.
                    res.append(rf"{{\colorbox{{{key}}}{{\color{{descentprose}}{body}}}}}")
                else:
                    unknown_stains.append(key)
                    res.append(body)
            i = b
        return "".join(res)
    return expand(latex)


# ----------------------------------------------------------------------------
# 5. Build standalone LaTeX document
# ----------------------------------------------------------------------------
def build_document(explanation: str,
                   stains: dict[str, tuple[float, float, float]],
                   unknown_stains: list[str]) -> str:
    thread_ids = _collect_thread_ids(explanation)
    thread_colors = assign_thread_colors(thread_ids)

    defs = []
    for k, (r, g, b) in stains.items():
        defs.append(rf"\definecolor{{{k}}}{{rgb}}{{{r},{g},{b}}}")
    for tid, (r, g, b) in thread_colors.items():
        defs.append(rf"\definecolor{{thread__{tid}}}{{rgb}}{{{r},{g},{b}}}")
    color_defs = "\n".join(defs)

    body = expand_markers(explanation, stains, thread_colors, unknown_stains)
    body, has_arcs = expand_arcs(body)

    tikz_preamble = ""
    arc_command = ""
    if has_arcs:
        tikz_preamble = "\\usepackage{lmodern}\n\\usepackage{tikz}\n\\usetikzlibrary{calc}"
        arc_command = _VALUEARC_CMD

    return rf"""\documentclass[border=10pt,varwidth=14cm]{{standalone}}
\usepackage{{amsmath,amssymb}}
\usepackage{{xcolor}}            % provides \colorbox for the stain wash
\usepackage[T1]{{fontenc}}
{tikz_preamble}
{color_defs}
\definecolor{{descentprose}}{{rgb}}{{0.93,0.95,0.98}}  % neutral light prose
{arc_command}
\begin{{document}}
\color{{descentprose}}
\sffamily
{body}
\end{{document}}
"""


# ----------------------------------------------------------------------------
# 6. Compile one doc -> transparent PNG
# ----------------------------------------------------------------------------
@dataclass
class BakeResult:
    ok: bool
    out_png: Path | None
    error: str = ""

_ERR_RE = re.compile(r"^! (.*)$", re.MULTILINE)
def _extract_latex_error(log: str) -> str:
    if _ERR_RE.search(log):
        lines = [ln for ln in log.splitlines() if ln.startswith(("! ", "l."))]
        return "\n".join(lines[:14]) or log[-1200:]
    return log[-1200:]

def bake_one(tex: str, out_png: Path, dpi: int, tools: dict[str, str]) -> BakeResult:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "doc.tex").write_text(tex, encoding="utf-8")

        # 1) pdflatex -> PDF
        p = subprocess.run(
            [tools["pdflatex"], "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory", str(tmp), str(tmp / "doc.tex")],
            capture_output=True, text=True)
        pdf = tmp / "doc.pdf"
        if p.returncode != 0 or not pdf.exists():
            log = tmp / "doc.log"
            txt = log.read_text(encoding="utf-8", errors="ignore") if log.exists() else (p.stdout + p.stderr)
            return BakeResult(False, None, _extract_latex_error(txt))

        # 2) PDF -> transparent PNG, preferring pdftocairo (clean, build-independent)
        out_stub = tmp / "out"   # pdftocairo appends .png
        if tools.get("pdftocairo"):
            r = subprocess.run(
                [tools["pdftocairo"], "-png", "-transp", "-r", str(dpi),
                 "-singlefile", str(pdf), str(out_stub)],
                capture_output=True, text=True)
            produced = tmp / "out.png"
        else:
            # Fallback: dvisvgm PDF->SVG, then SVG->PNG (no --png flag used)
            svg = tmp / "out.svg"
            subprocess.run([tools["dvisvgm"], "--pdf", "-o", str(svg), str(pdf)],
                           capture_output=True, text=True)
            r = subprocess.run([tools["dvisvgm"], f"--png:dpi={dpi}",
                                "-o", str(tmp / "out.png"), str(svg)],
                               capture_output=True, text=True)
            produced = tmp / "out.png"

        if not produced.exists():
            cands = sorted(tmp.glob("out*.png"))
            if not cands:
                return BakeResult(False, None,
                                  "PDF->PNG failed:\n" + (r.stdout + r.stderr)[-1500:])
            produced = cands[0]

        Image.open(produced).convert("RGBA").save(out_png)
        return BakeResult(True, out_png)


# ----------------------------------------------------------------------------
# 7. Orchestrate corridor
# ----------------------------------------------------------------------------
def bake_corridor(corridor_path: Path, out_dir: Path, dpi: int) -> int:
    tools = check_toolchain()
    corridor = parse_corridor(corridor_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    rep = [f"CORRIDOR: {corridor.title}", f"SOURCE  : {corridor_path}",
           f"STAINS  : " + (", ".join(corridor.stains) or "(NONE!)"),
           f"DPI     : {dpi}", ""]
    failures = 0
    for robot in corridor.robots:
        rep.append(f"--- ROBOT {robot.number}: {robot.name} ---")
        if not robot.explains:
            rep.append("  (no EXPLAIN_* blocks found)"); failures += 1
        for layer in LAYERS:
            text = robot.explains.get(layer)
            tag = f"robot{robot.number}_{layer}"
            if text is None:
                rep.append(f"  [skip ] {layer:<13} (missing EXPLAIN_{layer.upper()})"); continue
            unknown: list[str] = []
            doc = build_document(text, corridor.stains, unknown)
            res = bake_one(doc, out_dir / f"{tag}.png", dpi, tools)
            if res.ok:
                note = f"   WARNING unknown stain keys (uncoloured): {sorted(set(unknown))}" if unknown else ""
                rep.append(f"  [ OK  ] {layer:<13} -> {tag}.png{note}")
            else:
                failures += 1
                rep.append(f"  [FAIL ] {layer:<13}")
                rep += [f"          {ln}" for ln in res.error.splitlines()]
        rep.append("")
    rep.append(f"DONE. {failures} failure(s).")
    txt = "\n".join(rep)
    (out_dir / "_report.txt").write_text(txt, encoding="utf-8")
    print(txt)
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="DEU baker: corridor .txt -> transparent colored PNGs.")
    ap.add_argument("corridor", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dpi", type=int, default=600)
    a = ap.parse_args()
    if not a.corridor.exists():
        print(f"FATAL: corridor file not found: {a.corridor}", file=sys.stderr); return 2
    return bake_corridor(a.corridor, a.out, a.dpi)

if __name__ == "__main__":
    raise SystemExit(main())
