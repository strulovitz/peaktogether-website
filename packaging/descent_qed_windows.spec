# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
GAME_DIR = ROOT / "descent"
if not GAME_DIR.exists():
    raise SystemExit(f"Could not find game directory: {GAME_DIR}")

excluded_dir_names = {"__pycache__", ".pytest_cache", ".mypy_cache",
                      ".ruff_cache", "build", "dist", ".venv-build", "build_env"}
excluded_suffixes = {".pyc", ".pyo"}

datas = []
for path in GAME_DIR.rglob("*"):
    if not path.is_file():
        continue
    if any(part in excluded_dir_names for part in path.parts):
        continue
    if path.suffix.lower() in excluded_suffixes:
        continue
    if path.suffix.lower() == ".py":
        continue  # python is analyzed from imports; here we add only data/assets
    relative_parent = path.parent.relative_to(GAME_DIR)
    datas.append((str(path), str(relative_parent)))

icon_path = GAME_DIR / "icon.ico"
icon = str(icon_path) if icon_path.exists() else None

a = Analysis(
    [str(GAME_DIR / "app.py")],
    pathex=[str(GAME_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "OpenGL", "OpenGL.GL", "OpenGL.GLU",
        "OpenGL.arrays.numpymodule", "OpenGL.platform.win32",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "tkinter", "pytest", "IPython", "jupyter"],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="Descent QED",
    debug=False,
    strip=False,
    upx=False,        # IMPORTANT: no UPX -> fewer antivirus false positives
    console=False,    # no terminal window for players
    icon=icon,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name="Descent QED",
    contents_directory=".",
)
