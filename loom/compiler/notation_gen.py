"""
notation_gen.py — generates player/data/notation_table.json. [BONE]

Scripture: New Testament Addendum A: MIDI 36-96 -> display name, staff
step per clef, sharp flag. Runs ONCE per project (and on rule changes);
committed output. This is the single place music-notation knowledge
exists; the Player only ever looks the table up (core/notation.py).

FATTEN ME LIKE THIS (Compiler parent): plain deterministic generation,
sorted keys, then hand-check C4, Fs4, and the clef boundaries with a
screenshot for Nir's eye once bench_staff.py can draw.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("generate + write the table, deterministic")


if __name__ == "__main__":
    main()
