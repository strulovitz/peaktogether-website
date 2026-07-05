# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for HOMEWORLD: A Good Basis (Peak Together, Game 4).
# Adapted from descent/packaging/descent_qed_windows.spec and
# quake/packaging/quake_windows.spec (both shipped).
#
# One-folder Windows build. Homeworld is FLAT: every game .py is a sibling in
# homeworld/ and is analyzed by PyInstaller from app.py's imports. Here we bundle
# only the runtime DATA that the game loads by path: settings.json (read via
# open("settings.json")) and the whole content/ tree (ContentDB("content")).
# Dev folders (BIBLE, algebra, notes, packaging, tests, caches) never ship.
# Exe/folder name is the SHORT "Homeworld" (no spaces).
from pathlib import Path

# This spec lives in homeworld/packaging/ ; its parent is the game folder homeworld/.
GAME_DIR = Path(SPECPATH).resolve().parent
if not GAME_DIR.exists():
    raise SystemExit(f"Could not find game directory: {GAME_DIR}")

excluded_dir_names = {
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "build", "dist", "release", ".venv-build", ".pyi-build", "build_env",
    # dev-only folders that must NOT ship to players:
    "BIBLE", "algebra", "notes", "packaging", "screenshots",
}
excluded_suffixes = {".pyc", ".pyo"}

# Bundle every non-.py, non-cache DATA file under homeworld/ (flat like Descent).
# This picks up settings.json and the entire content/ tree, preserving layout.
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
        "glcontext",            # moderngl's GL backend loader
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
    name="Homeworld",
    debug=False,
    strip=False,
    upx=False,        # IMPORTANT: no UPX -> fewer antivirus false positives
    console=False,    # no terminal window for players
    icon=icon,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name="Homeworld",
    contents_directory=".",
)
