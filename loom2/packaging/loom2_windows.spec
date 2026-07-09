# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for LOOM2 -- Sonifiquation (Peak Together, Game 5).
# Adapted from the shipped quake/packaging/quake_windows.spec and
# homeworld/packaging/homeworld_windows.spec.
#
# One-folder Windows build. All code is Python analyzed from main.py's imports;
# here we bundle only the runtime DATA root (data/), which holds every asset the
# frozen game loads by path: the campaign scenes (data/scenes/), instrument icons
# (data/icons/), GLSL shaders (data/shaders/), and the orchestra.
#
# AUDIO: we deliberately ship ONLY the pre-decoded sample cache
# (data/samples_cache/*.npy) plus data/samples/manifest.json, and DROP the 89
# source .mp3 files (excluded_suffixes below). The sampler loads the .npy buffers
# directly when the mp3 is absent, so the shipped game needs NO ffmpeg on the
# player's machine and boots instantly. Dev keeps the mp3s + rebuilds the cache.
#
# Dev-only folders/files never ship (HINDU scripture, tools, diag_*, the ear-test
# prototypes, WORKFLOW.md, build_sample_library.py -- all are non-imported .py or
# excluded below). Exe/folder name is the SHORT "LOOM2" (no spaces).
from pathlib import Path

# This spec lives in loom2/packaging/ ; its parent is the game folder loom2/.
GAME_DIR = Path(SPECPATH).resolve().parent
if not GAME_DIR.exists():
    raise SystemExit(f"Could not find game directory: {GAME_DIR}")

# Runtime data roots to bundle (relative to GAME_DIR).
DATA_ROOTS = ["data"]

excluded_dir_names = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                      "build", "dist", "release", ".venv-build", "build_env"}
# .mp3 dropped on purpose: we ship the .npy decode cache instead (see header).
excluded_suffixes = {".pyc", ".pyo", ".py", ".log", ".mp3"}
excluded_names = {".gitignore", "coverage_report.txt", "diag_offline.wav"}

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
    [str(GAME_DIR / "main.py")],
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
    name="LOOM2",
    debug=False,
    strip=False,
    upx=False,        # IMPORTANT: no UPX -> fewer antivirus false positives
    console=False,    # no terminal window for players
    icon=icon,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, upx_exclude=[],
    name="LOOM2",
    contents_directory=".",
)
