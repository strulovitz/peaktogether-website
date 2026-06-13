COMPLETION REPORT — module palette — 2026-06-13

Project: DESCENT QED engine · Module: palette · Status: COMPLETE & VERIFIED ✅
For: DeepSeek (commit to /PARENT_ESTATE/reports/) + Parent
FILES CREATED

    palette.py — final, frozen. Pure Python, zero third-party dependencies.
    test_palette.py — runs clean against the real Module-1 fixture.

PUBLIC INTERFACES (verbatim final signatures)

class PaletteError(Exception): ...

class Palette:
    def __init__(self, ledger): ...
    def tint(self, key: str)         -> tuple[float,float,float,float]   # RGBA; NEUTRAL -> (0,0,0,0)
    def text_color_on(self, key: str)-> tuple[float,float,float]         # black on light, white on dark; NEUTRAL -> white
    def eye(self, key: str)          -> tuple[float,float,float]         # bright emissive glow, hue-preserving; NEUTRAL -> grey
    def blend_rgb(self, keyA, keyB)  -> tuple[float,float,float]         # mix two primary KEYS per the law

WORLD COLOR CONSTANTS (the SINGLE source for the whole engine)
Constant	Value
CLEAR_COLOR	(0.045, 0.055, 0.10)
WORLD_WALL_FILL	(0.16, 0.17, 0.20, 0.85) — dark grey, translucent
WORLD_EDGE	(0.88, 0.90, 0.94) — light grey/white wireframe
HOSTAGE_BLUE	(0.30, 0.65, 1.00)
HAZARD_YELLOW	(0.98, 0.80, 0.05)
HAZARD_BLACK	(0.05, 0.05, 0.06)
BACKDROP_BASE_ALPHA	0.55
KEY DECISIONS

    Primary anchors: red (0.85,0.12,0.12), yellow (0.95,0.85,0.10), blue (0.12,0.30,0.85).
    Secondaries — direct crayon anchors, pair-keyed (NOT formula-mixed): orange (0.95,0.45,0.05), green (0.15,0.70,0.25), purple (0.55,0.15,0.70). Keyed by frozenset of the two parent primary names, so a secondary is still structurally derived from its two parents (Prime Law intact) but renders vivid instead of muddy. Confirmed beautiful by Nir's eye.
    Text color: Rec.709 luminance, threshold 0.55 (yellow→black, red→white). Verified.
    Eye glow: hue-preserving proportional brighten (_EYE_BOOST = 1.25, clip-safe). Fixes the red-drift on orange. Verified.

TEST RESULTS

All ✅ against real fixture (parse_corridor("corridors/01_dummy.txt").ledger): orange tint reads correct; NEUTRAL fully transparent; yellow→black & red→white text; blend matches; both PaletteErrors raise. On-screen: red/yellow/blue/orange/green/purple all confirmed crisp by Nir.
DEVIATIONS FROM BRIEF

One, intentional and brief-sanctioned: secondaries are direct tuned anchors rather than a computed mix. The brief explicitly permitted this ("tune the anchor RGBs... ask Nir to eyeball them") and made Nir's eye the success criterion. Structural law fully preserved — the parent pair selects the color.
TRAPS DISCOVERED (next children / parent MUST know)

    Mixing-formula trap (the big one): averaging two saturated primaries mathematically drifts toward grey → muddy secondaries. Never compute secondaries from primaries; use the canonical pair-keyed anchor table. Any future color work inherits this.
    Glow hue-shift trap: brightening an emissive color by per-channel multiply + clamp shifts the hue toward whichever channel clips (orange → red). Always brighten by proportional scaling (_brighten_keep_hue).
    Parser entry point: it is parse_corridor(path).ledger, not parse_file. (Test harness corrected.)
    Text-vs-opacity: text_color_on judges the base tint luminance only; the reading_system owns final opacity compositing — if its backdrop-opacity slider is very low, black-on-near-transparent could read poorly. That module's concern.

OLD-CODE REUSE

None. Claude Fable's old code was not requested or used.
DEEPSEEK TODOS LEFT OPEN

    None blocking. Module is complete and verified.
    (Optional, future) on-screen anchor re-tune once the full scene renders — anchors named _PRIMARY_RGB and _SECONDARY_RGB in palette.py. Acceptance: secondaries still read as vivid orange/green/purple in context. Not required for sign-off.