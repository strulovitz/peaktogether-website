# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

# The demo .py lives in a deep folder; its parent is the base-camp folder.
ENTRY_POINT = Path(r"C:\Users\nir_s\peaktogether-website\mathematics\Riemann_hypothesis\Analytical_Path_Classical_and_Modern_Analytic_Number_Theory\harmonic_series_mathematics.py")
if not ENTRY_POINT.exists():
    raise SystemExit(f"Could not find entry point: {ENTRY_POINT}")

# No assets to collect — the demo is a single .py with no image/sound folders.
datas = []

a = Analysis(
    [str(ENTRY_POINT)],
    pathex=[str(ENTRY_POINT.parent)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "OpenGL", "OpenGL.GL", "OpenGL.GLU",
        "OpenGL.arrays.numpymodule", "OpenGL.platform.win32",
        "matplotlib", "matplotlib.backends.backend_agg",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "IPython", "jupyter"],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="HarmonicSeriesDemo",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon=None,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name="HarmonicSeriesDemo",
    contents_directory=".",
)
