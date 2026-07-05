"""python content_demo.py — validate the whole content/ tree.

EXPECTED: a short PASS report listing classes, mesh edge counts,
narrator lines, and the PLACEHOLDER ledger (book excerpts the owner
still needs to paste). Any schema error prints one precise FAIL line
naming file + entry + rule.
"""

import sys
import traceback

from content_db import ContentDB, ContentError


def main():
    print("CONTENT CHECK — content/ data layer")
    try:
        db = ContentDB("content")
    except ContentError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    classes = db.ship_classes()
    print(f"ships.json ........... {len(classes)} classes OK "
          f"({', '.join(classes)})")
    counts = [len(db.mesh_for_class(k)[1]) for k in classes]
    print(f"meshes ............... {len(classes)} meshes OK "
          f"({min(counts)}-{max(counts)} edges each)")
    core = db.narrator_lines("core")
    print(f"narrator/core.json ... {len(core)} lines OK")
    ph = db.placeholders()
    print(f"book ................. {len(db.excerpt_ids())} excerpts, "
          f"{len(ph)} PLACEHOLDER")
    for fname, eid in ph:
        print(f"                       PLACEHOLDER: {fname} :: {eid}")
    print(f"missions ............. {len(db.missions())} files")
    print("CONTENT CHECK PASSED")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(traceback.format_exc())
        sys.exit(1)
