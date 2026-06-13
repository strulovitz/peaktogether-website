# test_palette.py — verifies Palette against the Module-1 dummy ledger.
#
# Requires: corridors/01_dummy.txt (committed in Module 1) with ledger:
#   primaries: alpha=red, beta=yellow, gamma=blue
#   blends:    delta = (alpha, beta)   # red+yellow -> orange
#
# NOTE TO NIR: if content_parser's entry point isn't `parse_file`, tell me the
# real function name and I'll patch this one line. Everything else is fixed.

from content_parser import parse_corridor  # was: parse_file
from palette import (
    Palette, PaletteError,
    CLEAR_COLOR, WORLD_WALL_FILL, WORLD_EDGE,
    HOSTAGE_BLUE, HAZARD_YELLOW, HAZARD_BLACK,
    BACKDROP_BASE_ALPHA,
)


def fmt(t):
    return "(" + ", ".join(f"{x:.3f}" for x in t) + ")"


def main():
    ledger = parse_corridor("corridors/01_dummy.txt").ledger   # was: parse_file(...)
    pal = Palette(ledger)

    print("=== MEANING TINTS (RGBA) ===")
    print("tint(alpha)  red    ->", fmt(pal.tint("alpha")))
    print("tint(beta)   yellow ->", fmt(pal.tint("beta")))
    print("tint(gamma)  blue   ->", fmt(pal.tint("gamma")))
    print("tint(delta)  ORANGE ->", fmt(pal.tint("delta")))
    print("tint(NEUTRAL)       ->", fmt(pal.tint("NEUTRAL")), " (must be all 0)")

    print("\n=== TEXT COLOR (RGB) ===")
    print("text_on(beta)  yellow -> expect BLACK ->", fmt(pal.text_color_on("beta")))
    print("text_on(alpha) red    -> expect WHITE ->", fmt(pal.text_color_on("alpha")))
    print("text_on(NEUTRAL)      -> expect WHITE ->", fmt(pal.text_color_on("NEUTRAL")))

    print("\n=== EYE GLOW (emissive RGB) ===")
    print("eye(gamma)   bright blue   ->", fmt(pal.eye("gamma")))
    print("eye(delta)   bright orange ->", fmt(pal.eye("delta")))
    print("eye(NEUTRAL) bright grey   ->", fmt(pal.eye("NEUTRAL")))

    print("\n=== BLEND HELPER ===")
    print("blend_rgb(alpha,beta) ORANGE ->", fmt(pal.blend_rgb("alpha", "beta")))

    print("\n=== WORLD CONSTANTS ===")
    print("CLEAR_COLOR     :", fmt(CLEAR_COLOR))
    print("WORLD_WALL_FILL :", fmt(WORLD_WALL_FILL))
    print("WORLD_EDGE      :", fmt(WORLD_EDGE))
    print("HOSTAGE_BLUE    :", fmt(HOSTAGE_BLUE))
    print("HAZARD_YELLOW   :", fmt(HAZARD_YELLOW))
    print("HAZARD_BLACK    :", fmt(HAZARD_BLACK))
    print("BACKDROP_BASE_ALPHA :", BACKDROP_BASE_ALPHA)

    print("\n=== ERROR PATH ===")
    try:
        pal.tint("does_not_exist")
        print("FAIL: expected PaletteError, none raised")
    except PaletteError as e:
        print("OK   PaletteError raised:", e)

    # Bonus: illegal blend (same key) must also raise.
    try:
        pal.blend_rgb("alpha", "alpha")
        print("FAIL: expected PaletteError on same-key blend")
    except PaletteError as e:
        print("OK   PaletteError on same-key blend:", e)


if __name__ == "__main__":
    main()
