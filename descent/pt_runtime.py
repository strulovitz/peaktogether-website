from __future__ import annotations

import ctypes
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

_GAME_SLUG = "DescentQED"
_APPDATA_DIR: Path | None = None
_BASE_DIR: Path | None = None


def bootstrap(game_slug: str = "DescentQED") -> None:
    """Call once at the very start of app.py, before loading assets."""
    global _GAME_SLUG, _APPDATA_DIR, _BASE_DIR
    _GAME_SLUG = game_slug
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

    if getattr(sys, "frozen", False):
        # PyInstaller one-folder: bundled data lives in sys._MEIPASS (the
        # "_internal" folder), NOT next to the .exe. Point the asset base there
        # so the game's relative asset loads (levels/, baked/, *-hologram.png)
        # resolve correctly. Fall back to the exe folder if _MEIPASS is absent.
        _BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        _BASE_DIR = Path(__file__).resolve().parent

    os.chdir(_BASE_DIR)

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        _APPDATA_DIR = Path(local_appdata) / "PeakTogether" / _GAME_SLUG
    else:
        _APPDATA_DIR = Path.home() / ".peaktogether" / _GAME_SLUG
    _APPDATA_DIR.mkdir(parents=True, exist_ok=True)

    sys.excepthook = _handle_uncaught_exception


def base_dir() -> Path:
    if _BASE_DIR is None:
        bootstrap(_GAME_SLUG)
    assert _BASE_DIR is not None
    return _BASE_DIR


def appdata_dir() -> Path:
    if _APPDATA_DIR is None:
        bootstrap(_GAME_SLUG)
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

    message = "Descent QED crashed."
    if log_path is not None:
        message += f"\n\nA crash log was written here:\n{log_path}"
    message += "\n\nIf you'd like to help, please send this file to Peak Together."

    if getattr(sys, "frozen", False) and os.name == "nt":
        try:
            ctypes.windll.user32.MessageBoxW(None, message, "Descent QED", 0x00000010)
        except Exception:
            pass

    sys.__excepthook__(exc_type, exc_value, exc_tb)
