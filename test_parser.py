# test_parser.py
# Quick smoke test for content_parser against the dummy fixture.
# Run from the repository root:
#   python test_parser.py
#
# Expected output is listed in the printout so Nir can eyeball-diff it.

from content_parser import discover_corridors, parse_value_arcs


def main():
    corrs = discover_corridors("corridors")
    if not corrs:
        print("FAIL: no corridors discovered")
        return

    for c in corrs:
        print(f"Corridor {c.number}  title={c.title!r}  flavor={c.flavor!r}")
        print(f"  ledger primaries: {sorted(c.ledger.primaries.items())}")
        print(f"  ledger blends:    {sorted(c.ledger.blends.items())}")
        print(f"  robots: {len(c.robots)}")
        for r in c.robots:
            print(f"    Robot {r.number}: {r.name!r}  eye={r.eye_color_key!r}")
            print(f"      briefing_hint: {r.briefing_hint!r}")
            print(f"      problem: {r.problem!r}")
            print(f"      explains: {sorted(r.explain.keys())}")
            print(f"      segments ({len(r.segments)}):",
                  [s.ledger_key for s in r.segments])
            print(f"      fizzles: {sorted(r.fizzles.keys())}")
            arcs = parse_value_arcs(r.explain["engineer"])
            print(f"      value arcs ({len(arcs)}):",
                  [(a.latex, a.value) for a in arcs])

    # Summary lines (easy to grep)
    print()
    print("=== SUMMARY ===")
    print(f"Total corridors: {len(corrs)}")
    total_robots = sum(len(c.robots) for c in corrs)
    print(f"Total robots:    {total_robots}")

    # Mark expected values so Nir can eyeball
    print()
    print("EXPECTED (for 01_dummy.txt): 1 corridor, 2 robots")
    print("  R1 eye=alpha, 3 segments [alpha, NEUTRAL, beta], fizzles BAR/BAZ, 2 value arcs")
    print("  R2 eye=delta, 5 segments [alpha, NEUTRAL, beta, NEUTRAL, delta], fizzles BAR, 1 value arc")


if __name__ == "__main__":
    main()
