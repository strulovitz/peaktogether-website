"""
library_scan.py — a note becomes a real file, HERE and only here. [BONE]

Scripture: New Testament par.I.3 stages 8-9 + the on-the-record promise
(2026-07-06): the game plays REAL Philharmonia recordings (or their
FORGED uniform-duration derivatives), never synthesis. Filename grammar
(confirmed on Nir's disk): instrument_note_length_dynamic_articulation
.mp3; sharps use 's'; lengths 025/05/1/15 (NO "2"); long/very-long/
phrase are multi-attack gestures, NEVER eligible.

THE SELECTION LAW (Commentaries, 2026-07-06): lengths are chosen
UNIFORMLY per spell, never per-note independently. Preference: a
forged set (if --forged given) > longest COMMON numeric length.
If no uniform choice exists -> loud plain-language error naming the
Forge command that would fix it (see forge/forge_samples.py docstring).

FATTEN ME LIKE THIS (Compiler parent): port m1_demo's proven resolver
(uniform-length rule) here; add stage-9 gain analysis (decode via
pygame, RMS-match across the spell, clamp; per-note gain into JSON);
write library_profile.json for the Apocrypha's roster update.
"""

from __future__ import annotations


def scan_library(library_dir: str, forged_dir: str | None = None) -> dict:
    raise NotImplementedError("build the instrument/note/length availability map")

def choose_samples(scan: dict, spec: dict, notes) -> dict:
    raise NotImplementedError("stage 8: THE SELECTION LAW, uniform per spell")

def analyze_gains(chosen: dict) -> dict:
    raise NotImplementedError("stage 9: RMS loudness matching -> per-note gain")
