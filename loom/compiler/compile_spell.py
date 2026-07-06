"""
compile_spell.py — Program A's front door. [BONE]

Scripture: New Testament Part I. Usage (authors' PCs only, NEVER ships):
    python compile_spell.py spec.py --library <philharmonia_dir>
        [--forged <forged_dir>] --out <pack_dir>

Orchestrates: pipeline.py (math) -> library_scan.py (real files) ->
emit.py (JSON + copied audio + preview.wav + compile_report.txt).
Determinism is LAW: same spec + same library = byte-identical JSON.
Errors are plain-language, paste-to-DeepSeek, with fix suggestions —
the Compiler NEVER silently degrades (New Testament par.I).

FATTEN ME LIKE THIS (Compiler parent): argparse + call the three
modules + print the report path. All intelligence lives in them.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Compiler milestone: see pipeline.py first")


if __name__ == "__main__":
    main()
