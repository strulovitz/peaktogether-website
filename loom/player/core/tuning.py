"""
tuning.py — loads player/data/scrub_tuning.json into a frozen dataclass. [MEAT]

Scripture: New Testament par.II.3. Every "feel" constant lives in the JSON
file so DeepSeek can tune by ear with Nir WITHOUT touching code. Code
never hardcodes these numbers.

Imports: standard library ONLY.
"""

from __future__ import annotations

import json
from dataclasses import dataclass


class TuningLoadError(Exception):
    """Raised with a plain-language message."""


@dataclass(frozen=True)
class ScrubTuning:
    boundary_guard_fraction: float   # hysteresis inset, fraction of a region's width
    max_triggers_per_frame: int      # flurry cap: audio keeps only the LAST K crossings
    steal_fade_ms: int               # voice-steal fade (audio engine)
    retrigger_min_ms: int            # same note never refires sooner than this
    highlight_decay_ms: int          # visual afterglow (renderers, not Conductor)

    @staticmethod
    def default() -> "ScrubTuning":
        """The New Testament par.II.3 defaults — used by tests and as the
        template for player/data/scrub_tuning.json."""
        return ScrubTuning(
            boundary_guard_fraction=0.04,
            max_triggers_per_frame=4,
            steal_fade_ms=10,
            retrigger_min_ms=90,
            highlight_decay_ms=300,
        )


def load_tuning(path: str) -> ScrubTuning:
    """Load the tuning file. Every key must be present — a missing key is
    an error (silent defaults would hide a broken file from DeepSeek)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise TuningLoadError(f"Tuning file not found: {path}")
    except json.JSONDecodeError as e:
        raise TuningLoadError(f"Tuning file {path} is not valid JSON: {e}")
    try:
        return ScrubTuning(
            boundary_guard_fraction=float(data["boundary_guard_fraction"]),
            max_triggers_per_frame=int(data["max_triggers_per_frame"]),
            steal_fade_ms=int(data["steal_fade_ms"]),
            retrigger_min_ms=int(data["retrigger_min_ms"]),
            highlight_decay_ms=int(data["highlight_decay_ms"]),
        )
    except (KeyError, TypeError, ValueError) as e:
        raise TuningLoadError(
            f"Tuning file {path} is missing or has a bad value: {e}. "
            f"It must contain exactly the five keys of ScrubTuning.")
