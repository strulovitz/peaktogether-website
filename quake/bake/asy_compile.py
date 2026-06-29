"""Subprocess isolate for invoking the Asymptote binary.

This is the ONLY module in the Quake codebase that runs an external process;
everything else is pure. Compilation never raises on compiler error — failures
are reported via ``AsyResult.ok=False`` with stderr/stdout preserved verbatim.

Asymptote flags used (traceability)
-----------------------------------
The following are the confirmed Asymptote command-line flags this module relies
on:

- ``-f <format>``   : output format (e.g. ``png``). Maps to ``cfg.out_format``.
- ``-render <n>``   : render resolution multiplier. Asymptote renders at
                      ``n × 72dpi``, so we compute ``n = ceil(dpi / 72)``.
- ``-u <k>=<v>``    : user-supplied parameter assignments, one ``-u`` per key.
- ``-o <stem>``     : output file stem (Asymptote appends the format suffix).

The source file is passed as a positional argument. Any ``cfg.extra_flags`` are
appended verbatim. We never use ``shell=True``.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class AsyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool
    outputs: list[Path]
    stderr: str
    stdout: str


class AsyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    asy_binary: str = "asy"
    out_format: str = "png"
    dpi: int = 220
    extra_flags: list[str] = []
    gs_path: str = ""  # Ghostscript path for Asymptote; set via ASYMPTOTE_GS env var if non-empty


def compile(
    src: Path, out_stem: Path, params: dict[str, str], cfg: AsyConfig
) -> AsyResult:
    """Compile an Asymptote source file via a subprocess.

    Returns an :class:`AsyResult`; never raises on compiler error.
    """
    render_factor = math.ceil(cfg.dpi / 72)

    args: list[str] = [cfg.asy_binary]

    # User params, sorted alphabetically by key, one -u per entry.
    for k in sorted(params):
        args += ["-u", f"{k}={params[k]}"]

    # Output format.
    args += ["-f", cfg.out_format]

    # Resolution: Asymptote renders at render_factor × 72dpi.
    args += ["-render", str(render_factor)]

    # Caller-supplied extra flags, verbatim.
    args += list(cfg.extra_flags)

    # Source file (positional) and output stem.
    args += [str(src)]
    args += ["-o", str(out_stem)]

    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=120,
        env={**__import__("os").environ, "ASYMPTOTE_GS": cfg.gs_path} if cfg.gs_path else None,
    )

    expected = out_stem.with_suffix(f".{cfg.out_format}")
    ok = proc.returncode == 0 and expected.exists()
    outputs = [expected] if ok else []

    return AsyResult(
        ok=ok,
        outputs=outputs,
        stderr=proc.stderr,
        stdout=proc.stdout,
    )
