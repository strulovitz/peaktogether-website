# test_parser.py
# Tiny runnable verification for content_parser against corridors/01_dummy.txt
# Run from the project root:  python test_parser.py

from content_parser import discover_corridors, parse_value_arcs

def main():
    corridors = discover_corridors("corridors")
    print(f"corridors found: {len(corridors)}")
    for c in corridors:
        print(f"  corridor {c.number}: title={c.title!r}  robots={len(c.robots)}")
        print(f"    ledger primaries: {c.ledger.primaries}")
        print(f"    ledger blends:    {c.ledger.blends}")
        for r in c.robots:
            seg_keys = [s.ledger_key for s in r.segments]
            arcs = parse_value_arcs(r.explain["engineer"])
            arc_pairs = [(a.latex, a.value) for a in arcs]
            print(f"    robot {r.number} {r.name!r}: eye={r.eye_color_key}")
            print(f"      segments={len(r.segments)} keys={seg_keys}")
            print(f"      fizzles={list(r.fizzles.keys())}")
            print(f"      engineer value arcs={len(arcs)} {arc_pairs}")

if __name__ == "__main__":
    main()
