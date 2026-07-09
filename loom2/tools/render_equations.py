r"""
tools/render_equations.py
Render LaTeX math equations as yellow-text-with-black-outline transparent PNGs
for LOOM2's in-game HUD overlay.

Uses the SAME proven toolchain as Descent/Quake:
  pdflatex (MiKTeX/TeX Live) -> pdftocairo (Poppler) -> transparent PNG
then PIL + scipy post-processes for yellow fill + black outline.

REQUIRES: MiKTeX or TeX Live on PATH (pdflatex, pdftocairo).

Usage:
    python tools/render_equations.py "z = x^2 - y^2" data/scenes/test_saddle/equation.png
    python tools/render_equations.py r"\frac{\partial f}{\partial x}" scene/eq.png --dpi 600
    python tools/render_equations.py --list equations.txt
"""

import os
import sys
import shutil
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from scipy.ndimage import maximum_filter
from PIL import Image


# -- toolchain check ---------------------------------------------------------

def _check_toolchain() -> dict:
    tools = {}
    for name, hint in [
        ("pdflatex", "Install MiKTeX or TeX Live: https://miktex.org/"),
        ("pdftocairo", "pdftocairo ships with MiKTeX / TeX Live (Poppler)."),
    ]:
        p = shutil.which(name)
        if not p:
            print(f"FATAL: '{name}' not found on PATH.\n       {hint}", file=sys.stderr)
            sys.exit(2)
        tools[name] = p
    return tools


# -- configurable defaults ---------------------------------------------------

DEFAULT_DPI = 600            # 600 for sharp math (matching Descent's default)
YELLOW = (255, 220, 50)     # warm yellow -- readable over any terrain
BLACK = (0, 0, 0)
OUTLINE_RADIUS = 3           # pixels (dilation radius; at 600 DPI ~3 px is nice)


# -- LaTeX document builder --------------------------------------------------

_LATEX_DOC = r"""\documentclass[border=4pt]{{standalone}}
\usepackage{{xcolor}}
\usepackage{{amsmath,amssymb}}
\begin{{document}}
\color{{black}}
$\displaystyle {equation}$
\end{{document}}
"""


def _build_tex(latex: str) -> str:
    """Wrap the LaTeX math string in a standalone document."""
    return _LATEX_DOC.format(equation=latex)


# -- core render -------------------------------------------------------------

def render_equation(latex: str, out_path: str,
                    dpi: int = DEFAULT_DPI) -> None:
    """Render LaTeX math to transparent PNG with yellow fill + black outline.
    Saves at out_path (parent directories created automatically)."""

    tools = _check_toolchain()

    # 1. LaTeX -> PDF -> transparent PNG (all in a temp directory)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tex_file = tmp / "eq.tex"
        tex_file.write_text(_build_tex(latex), encoding="utf-8")

        # pdflatex (twice for cross-references, though standalone rarely needs it)
        for _pass in range(2):
            p = subprocess.run(
                [tools["pdflatex"], "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", str(tmp), str(tex_file)],
                capture_output=True, text=True)
            pdf = tmp / "eq.pdf"
            if p.returncode != 0 or not pdf.exists():
                log = tmp / "eq.log"
                txt = log.read_text(encoding="utf-8", errors="ignore") if log.exists() else (p.stdout + p.stderr)
                print(f"  LaTeX ERROR:\n{txt[-2000:]}", file=sys.stderr)
                sys.exit(1)

        # pdftocairo: PDF -> transparent RGBA PNG
        png_stub = tmp / "eq"
        r = subprocess.run(
            [tools["pdftocairo"], "-png", "-transp",
             "-r", str(dpi), "-singlefile",
             str(pdf), str(png_stub)],
            capture_output=True, text=True)
        produced = tmp / "eq.png"
        if not produced.exists():
            print(f"  pdftocairo ERROR:\n{r.stdout}{r.stderr}", file=sys.stderr)
            sys.exit(1)

        # Load the clean black-text-on-transparent render
        rgba = np.array(Image.open(produced).convert("RGBA"))

    # 2. Post-process: yellow fill + black outline via alpha-channel dilation
    result = _composite_outlined(rgba, YELLOW, BLACK, OUTLINE_RADIUS)

    # 3. Save
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img = Image.fromarray(result, "RGBA")
    img.save(out_path, "PNG")
    print(f"  OK  {out_path}  ({img.width}x{img.height})")


def _composite_outlined(rgba: np.ndarray,
                        fill_rgb: tuple,
                        outline_rgb: tuple,
                        radius: int) -> np.ndarray:
    """Given RGBA image (black glyphs on transparent background),
    produce RGBA with fill_rgb text + outline_rgb outline.

    Alpha channel = glyph mask. Outline = dilated alpha minus original.
    """
    h, w = rgba.shape[:2]
    alpha = rgba[:, :, 3]

    footprint = np.ones((radius * 2 + 1, radius * 2 + 1), dtype=bool)
    dilated = maximum_filter(alpha, footprint=footprint)

    out = np.zeros((h, w, 4), dtype=np.uint8)

    outline_mask = (dilated > 0) & (alpha == 0)
    out[outline_mask, 0] = outline_rgb[0]
    out[outline_mask, 1] = outline_rgb[1]
    out[outline_mask, 2] = outline_rgb[2]
    out[outline_mask, 3] = dilated[outline_mask].astype(np.uint8)

    fill_mask = alpha > 0
    out[fill_mask, 0] = fill_rgb[0]
    out[fill_mask, 1] = fill_rgb[1]
    out[fill_mask, 2] = fill_rgb[2]
    out[fill_mask, 3] = alpha[fill_mask]

    return out


# -- batch mode --------------------------------------------------------------

def render_list(list_path: str) -> None:
    """Read a file of lines:  latex_string  ->  output_path
    Lines starting with # are comments; blank lines are skipped."""
    if not os.path.isfile(list_path):
        print(f"ERROR: file not found: {list_path}")
        sys.exit(1)
    with open(list_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" -> ")
            if len(parts) != 2:
                print(f"  SKIP line {lineno}: bad format (expected 'latex -> path')")
                continue
            latex, path = parts[0].strip(), parts[1].strip()
            try:
                render_equation(latex, path)
            except Exception as e:
                print(f"  FAIL line {lineno}: {e}")


# -- CLI ---------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--list":
        if len(sys.argv) < 3:
            print("usage: python tools/render_equations.py --list equations.txt")
            sys.exit(1)
        render_list(sys.argv[2])
    else:
        latex = sys.argv[1]
        out_path = sys.argv[2] if len(sys.argv) > 2 else "equation.png"
        dpi = DEFAULT_DPI
        # parse optional --dpi
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--dpi" and i + 1 < len(args):
                dpi = int(args[i + 1])
                i += 1
            elif not args[i].startswith("--") and i == 0:
                out_path = args[i]
            i += 1
        render_equation(latex, out_path, dpi=dpi)
