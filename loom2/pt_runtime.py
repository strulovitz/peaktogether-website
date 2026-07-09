"""pt_runtime.py - Peak Together frozen-exe bootstrap for LOOM2.

Adapted from the shipped Descent QED / Quake: Principia / Homeworld pt_runtime.py.
Call bootstrap(...) at the very top of main.main(), BEFORE loading any assets
(the campaign scene JSON, the sample library, shaders, icons):
  - LOOM2 uses BARE RELATIVE data paths (see config.py: DATA_DIR="data",
    SAMPLES_DIR="data/samples", SCENES_DIR="data/scenes", ...). So we chdir to
    the game's base directory ALWAYS (like Descent), which makes those relative
    loads resolve no matter where the game was launched from.
  - When frozen by PyInstaller (one-folder), bundled data lives in sys._MEIPASS,
    so the base dir points there; otherwise it is the folder holding this file.
  - Saves, logs and the crash log go to %LOCALAPPDATA%\\PeakTogether\\LOOM2 so the
    game works even if installed in a read-only location.
  - Uncaught exceptions in the SHIPPED exe are written to a crash log and shown
    in a message box (never overridden during dev/tests).
This module keeps LOOM2 runnable both as `python main.py` and as LOOM2.exe.
"""
from __future__ import annotations

import ctypes
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

_GAME_SLUG = "LOOM2"
_GAME_TITLE = "LOOM2 — Sonifiquation"
_APPDATA_DIR: Path | None = None
_BASE_DIR: Path | None = None


def bootstrap(game_slug: str = "LOOM2",
              game_title: str = "LOOM2 — Sonifiquation") -> None:
    """Call once at the very start of main.main(), before loading assets."""
    global _GAME_SLUG, _GAME_TITLE, _APPDATA_DIR, _BASE_DIR
    _GAME_SLUG = game_slug
    _GAME_TITLE = game_title

    if getattr(sys, "frozen", False):
        # PyInstaller one-folder: bundled data lives in sys._MEIPASS. Point the
        # asset base there so the CWD-relative loads (config.py's "data/...")
        # resolve. Fall back to the exe folder if _MEIPASS is absent.
        _BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        # Player-facing crash handling only in the shipped exe; never override
        # the interpreter's excepthook during dev/tests.
        sys.excepthook = _handle_uncaught_exception
    else:
        _BASE_DIR = Path(__file__).resolve().parent

    # ALWAYS chdir to the base dir: LOOM2's data paths are all bare-relative, so
    # this is what makes `python main.py` work from ANY directory and keeps the
    # .npy sample cache landing in <base>/data/samples_cache regardless of CWD.
    os.chdir(_BASE_DIR)

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        _APPDATA_DIR = Path(local_appdata) / "PeakTogether" / _GAME_SLUG
    else:
        _APPDATA_DIR = Path.home() / ".peaktogether" / _GAME_SLUG
    _APPDATA_DIR.mkdir(parents=True, exist_ok=True)


def base_dir() -> Path:
    if _BASE_DIR is None:
        bootstrap(_GAME_SLUG, _GAME_TITLE)
    assert _BASE_DIR is not None
    return _BASE_DIR


def appdata_dir() -> Path:
    if _APPDATA_DIR is None:
        bootstrap(_GAME_SLUG, _GAME_TITLE)
    assert _APPDATA_DIR is not None
    return _APPDATA_DIR


def asset_path(*parts: str) -> str:
    """Prefer this for asset loading in new/future code."""
    return str(base_dir().joinpath(*parts))


def user_path(*parts: str) -> str:
    """Use for settings, saves, logs, controller bindings."""
    return str(appdata_dir().joinpath(*parts))


def _handle_uncaught_exception(exc_type, exc_value, exc_tb) -> None:
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log_path = None
    try:
        log_path = appdata_dir() / "crash-log.txt"
        with log_path.open("a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(datetime.now().isoformat(timespec="seconds") + "\n")
            f.write(text + "\n")
    except Exception:
        log_path = None

    message = f"{_GAME_TITLE} crashed."
    if log_path is not None:
        message += f"\n\nA crash log was written here:\n{log_path}"
    message += "\n\nIf you'd like to help, please send this file to Peak Together."

    if getattr(sys, "frozen", False) and os.name == "nt":
        try:
            ctypes.windll.user32.MessageBoxW(None, message, _GAME_TITLE, 0x00000010)
        except Exception:
            pass

    sys.__excepthook__(exc_type, exc_value, exc_tb)
