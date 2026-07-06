"""
emit.py — stage 12: write everything the Player will ever see. [BONE]

Scripture: New Testament par.I.3 stage 12 + Addendum A. Outputs:
  - the spell JSON: stable key order, floats rounded to 6 decimals,
    byte-identical for identical inputs (golden tests depend on it);
  - the chosen audio files COPIED into <pack>/audio/ (originals never
    touched; forged WAVs count as originals here);
  - preview.wav — the whole melody rendered offline, for Nir's ear
    approval loop (his ONLY quality gate);
  - compile_report.txt — plain words: what was chosen and why.

FATTEN ME LIKE THIS (Compiler parent): json.dumps(sort_keys=True) +
a float-rounding pass; preview rendered by mixing decoded samples at
their beat offsets (offline numpy mixing is design-time, allowed).
"""

from __future__ import annotations


def emit_spell(pack_dir: str, spell: dict, chosen_samples: dict) -> str:
    raise NotImplementedError("write JSON + copy audio; return spell path")

def render_preview(pack_dir: str, spell: dict, chosen_samples: dict) -> str:
    raise NotImplementedError("offline mix -> preview.wav")

def write_report(pack_dir: str, lines: list) -> str:
    raise NotImplementedError("compile_report.txt, warm plain language")
