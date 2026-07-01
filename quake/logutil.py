"""
logutil.py — write timestamped events to quake.log so crashes/stalls leave a trail.
"""
import atexit
import sys
import time
from pathlib import Path

_LOG_PATH = Path(__file__).parent / "quake.log"
_fh = None


def _open():
    global _fh
    if _fh is None:
        _fh = open(str(_LOG_PATH), "a", encoding="utf-8")
        atexit.register(_close)
    return _fh


def _close():
    global _fh
    if _fh:
        _fh.close()
        _fh = None


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        fh = _open()
        fh.write(line)
        fh.flush()
    except Exception:
        pass
    # Also print to stderr so the console sees it
    print(f"[QUAKE] {msg}", file=sys.stderr, flush=True)
