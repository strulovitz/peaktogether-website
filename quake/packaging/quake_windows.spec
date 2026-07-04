# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for QUAKE (Peak Together, Game 3).
# Adapted from descent/packaging/descent_qed_windows.spec.
# One-folder Windows build. Bundles only the runtime data roots (levels/ + hud/);
# all code is Python analyzed from imports, dev folders (BIBLE, principia, tests,
# tools, bake, docs) never ship.
from pathlib import Path

# This spec lives in quake/packaging/ ; its parent is the game folder quake/.
GAME_DIR = Path(SPECPATH).resolve().parent
if not GAME_DIR.exists():
    raise SystemExit(f"Could not find game directory: {GAME_DIR}")

# Runtime data roots to bundle (relative to GAME_DIR). Everything the frozen game
# loads at runtime: the baked level pack + concept graph, and the HUD emoji PNGs.
DATA_ROOTS = ["levels", "hud"]

excluded_dir_names = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                      "build", "dist", ".venv-build", "build_env"}
excluded_suffixes = {".pyc", ".pyo", ".py", ".log"}
excluded_names = {"savegame.json", ".gitignore"}

datas = []
for root in DATA_ROOTS:
    root_dir = GAME_DIR / root
    if not root_dir.exists():
        continue
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded_dir_names for part in path.parts):
            continue
        if path.suffix.lower() in excluded_suffixes:
            continue
        if path.name in excluded_names:
            continue
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
        "glcontext",            # moderngl's GL backend loader
        "pydantic",
        "pydantic_core",
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
    name="Quake",
    debug=False,
    strip=False,
    upx=False,        # IMPORTANT: no UPX -> fewer antivirus false positives
    console=False,    # no terminal window for players
    icon=icon,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name="Quake",
    contents_directory=".",
)
