# level_demo.py
# DESCENT QED engine — proof harness for the LEVEL layer.
#
# Proves the data pipeline:
#   load_level(manifest) -> Level   (ordered, DISTINCT corridors + title)
#   build_hub(level)      -> HubGeometry   (level is iterable of CorridorData)
#
# MATHEMATICS-BLIND: we print only STRUCTURE (titles, counts, poses). No math
# meaning, no color. No flythrough — that's app's job; we just prove hand-off.

from __future__ import annotations

import os
import sys

from level_parser import load_level, discover_levels
from hub_builder import build_hub


def main(manifest_path: str) -> int:
    print("=" * 64)
    print("LEVEL DEMO — load_level + build_hub hand-off")
    print("=" * 64)

    # --- discovery (optional convenience) --------------------------------
    levels_dir = os.path.dirname(manifest_path) or "levels"
    try:
        found = discover_levels(levels_dir)
        print(f"\ndiscover_levels({levels_dir!r}) ->")
        for p in found:
            print(f"   {p}")
    except Exception as e:  # noqa: BLE001  (demo: surface anything)
        print(f"\n[discover_levels skipped: {e}]")

    # --- load the level ---------------------------------------------------
    print(f"\nload_level({manifest_path!r}) ...")
    level = load_level(manifest_path)

    print(f"\nLEVEL TITLE : {level.title}")
    print(f"CORRIDOR COUNT : {len(level.corridors)}")
    print("CORRIDORS (in order):")
    for i, cd in enumerate(level, start=1):  # exercises Level.__iter__
        print(f"   [{i}] CORRIDOR {cd.number}  title={cd.title!r}")

    # Prove DISTINCT, not clones: all titles unique.
    titles = [cd.title for cd in level]
    assert len(set(titles)) == len(titles), "ABORT: duplicate corridor titles (clones!)"
    numbers = [cd.number for cd in level]
    assert len(set(numbers)) == len(numbers), "ABORT: duplicate CORRIDOR numbers (clones!)"
    print("\nDISTINCTNESS CHECK: all corridor titles & numbers unique. OK.")

    # --- hand-off to hub_builder (Level is iterable of CorridorData) ------
    print("\nbuild_hub(level)  [level iterates as CorridorData, build_hub reads .title]")
    hub = build_hub(level)  # works directly, zero changes to build_hub

    n_geo = len(hub.corridors)
    poses = hub.door_poses()
    print(f"   HubGeometry.corridors      -> {n_geo} CorridorGeometry")
    print(f"   HubGeometry.door_poses()   -> {len(poses)} door pose(s)")

    assert n_geo == len(level.corridors), (
        f"ABORT: build_hub produced {n_geo} corridors for {len(level.corridors)} input"
    )
    assert len(poses) == len(level.corridors), (
        f"ABORT: door_poses() count {len(poses)} != input {len(level.corridors)}"
    )

    print("\n   per-corridor hand-off (input title  ->  door mouth pose):")
    for i, (cd, pose) in enumerate(zip(level, poses), start=1):
        origin, normal = pose
        ox, oy, oz = origin
        nx, ny, nz = normal
        print(
            f"   [{i}] {cd.title!r:42}  mouth=({ox:+.2f},{oy:+.2f},{oz:+.2f}) "
            f"n=({nx:+.2f},{ny:+.2f},{nz:+.2f})"
        )

    print("\nHAND-OFF PROOF: build_hub received N DISTINCT corridors (titles above),")
    print("one CorridorGeometry and one door pose per input corridor. No clones.")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    mf = sys.argv[1] if len(sys.argv) > 1 else os.path.join("levels", "intro.txt")
    sys.exit(main(mf))