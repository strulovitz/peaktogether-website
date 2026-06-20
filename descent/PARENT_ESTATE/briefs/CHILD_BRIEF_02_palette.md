===========================================================
CHILD BRIEF #2 — MODULE: palette
Project: DESCENT QED engine. You are a CHILD chat.
===========================================================

WHO YOU ARE
A fresh Claude chat assigned ONE module: palette. You design and
write its code in full. DeepSeek (Nir's builder, agentic in
OpenCode, reliable on mechanical tasks, less clever than you)
commits your verbatim code to GitHub and works a copy until it
passes. Nir is courier and tester: not technical, very smart,
runs code and sends output. You have no memory of other chats.
Everything you need is here. When done you DIE with a Completion
Report (template at end).

THE PRIME LAW (never violate)
The engine is MATHEMATICS-BLIND. palette turns abstract LEDGER
KEYS into colors. It must NEVER know what a key MEANS (it never
knows "alpha is the harmonic series"). It only knows the
Kindergarten Mixing Law structure: primaries are red/yellow/blue,
blends are mixes of two primaries, NEUTRAL has no backdrop.

CONTEXT — WHAT ALREADY EXISTS (Module 1, DONE)
content_parser.py is built and frozen. It produces a ColorLedger:

  class ColorLedger:
      primaries: dict[str, str]   # key -> "red" | "yellow" | "blue"
      blends:    dict[str, tuple[str, str]]  # key -> (parentA, parentB)
      def is_defined(self, key: str) -> bool   # True for any primary,
                                               # any blend, or "NEUTRAL"

You will EXTEND/CONSUME this. Do NOT modify content_parser. You
import ColorLedger from it (or accept a ColorLedger instance).

THE KINDERGARTEN MIXING LAW (the design canon you implement)
(Verbatim intent from the project doctrine — implement faithfully.)
- Per corridor, each CORE INGREDIENT concept gets a PRIMARY:
  red, yellow, or blue (max 3).
- SECONDARIES are RESERVED and DERIVED, never independent:
    orange = red + yellow
    green  = yellow + blue
    purple = red + blue
  A secondary may ONLY appear as a BLEND of its two parents.
- Color mixing is a SEMANTIC DIMENSION, not decoration.
- GLUE symbols (=, parentheses, \cdots, lone constants) are
  NEUTRAL: no backdrop at all.
- Shades within one family are allowed as EMPHASIS (light blue is
  still "blue").
- This module does NOT enforce per-corridor consistency (the
  parser/author own that); palette just MAPS keys -> colors for
  whatever ledger it is given.

THE GREYSCALE-WORLD / SATURATED-GLOW RULE (also yours to serve)
The game WORLD is achromatic: walls dark grey, edges white/light
grey, background near-black CLEAR_COLOR = (0.045, 0.055, 0.10).
CHROMA is reserved for MEANING. palette therefore also provides
the few canonical world greys and the meaning-colors, so other
modules pull ALL colors from ONE place. No module should invent
its own colors.

YOUR GOAL — implement palette.py with this public interface:

  class Palette:
      def __init__(self, ledger: ColorLedger): ...

      # --- meaning colors (chroma) ---
      def tint(self, key: str) -> tuple[float,float,float,float]:
          # Returns an RGBA backdrop tint for an equation segment.
          # - "NEUTRAL" (or unknown-but-neutral) -> fully transparent
          #   (0,0,0,0): caller draws NO backdrop quad.
          # - a PRIMARY key -> that primary's tint.
          # - a BLEND key   -> the blended tint of its two parents.
          # Alpha here is a BASE alpha; the final on-screen opacity is
          # scaled later by a user "backdrop_opacity" slider in the
          # reading_system. Pick a sensible base (e.g. ~0.55) and make
          # it a module constant BACKDROP_BASE_ALPHA.
          # Raise or return NEUTRAL-transparent for keys the ledger
          # does not define? -> RAISE a clear PaletteError for an
          # UNDEFINED non-neutral key (mirrors parser strictness),
          # but treat "NEUTRAL" as valid and transparent.

      def text_color_on(self, key: str) -> tuple[float,float,float]:
          # White text on dark tints; black text on LIGHT tints
          # (e.g. yellow / light family). Decide by luminance of the
          # tint: luminance > threshold -> black text, else white.
          # NEUTRAL -> white (text floats on the dark world).

      def eye(self, key: str) -> tuple[float,float,float]:
          # The robot eye-band color = the FULL-SATURATION glow of the
          # concept the robot guards. Same hue logic as tint() but
          # RETURNED AS A BRIGHT EMISSIVE RGB (no alpha), suitable for
          # a glowing quad. NEUTRAL eye -> a neutral bright grey.

      def blend_rgb(self, keyA: str, keyB: str)
                                  -> tuple[float,float,float]:
          # Public helper: mix two PRIMARY keys per the law. Used when
          # a combined expression is shown, or for door glows. If the
          # two keys do not form a legal secondary (not both primaries,
          # or same key) -> PaletteError.

      # --- world greys (achromatic) ---
      # Provide as constants or methods; your choice, but DOCUMENT:
      #   WORLD_WALL_FILL   -> dark grey RGBA (translucent fill)
      #   WORLD_EDGE        -> light grey/white RGB (wireframe edges)
      #   CLEAR_COLOR       -> (0.045, 0.055, 0.10)
      #   HOSTAGE_BLUE      -> the bright blue for hostage figures
      #   HAZARD_YELLOW / HAZARD_BLACK -> chevron stripes
      # These are the ONLY place these world colors are defined.

COLOR MIXING — HOW TO ACTUALLY MIX
Define the three primaries as concrete RGB anchors (pick clean,
readable values; document them), e.g. red, yellow, blue. Mix a
blend as the simple average (or a perceptually-pleasant mix you
justify in one line) of its two parents. Keep it deterministic:
the same blend key always yields the same color. Secondaries
should LOOK like their kindergarten result:
   red+yellow -> orange, yellow+blue -> green, red+blue -> purple.
Tune the anchor RGBs until those three mixes read correctly to the
eye (you may state proposed values and ask Nir to eyeball them).

NO RENDERING HERE
palette returns numbers only. It imports NO pygame, NO OpenGL, NO
matplotlib. numpy is allowed ONLY if convenient for mixing (a
plain tuple average needs no numpy; prefer zero deps). Document
any dep you add.

WHAT YOU MUST NOT DO
- Do NOT know the meaning of any key.
- Do NOT use a secondary color as a standalone/base color.
- Do NOT enforce per-corridor consistency or the max-3 rule
  (the parser already validates ledger structure; you trust it).
- Do NOT modify content_parser.py. Import from it.
- Do NOT redesign the interface. Ambiguity -> most literal
  reading + a "trap discovered" note.

REFERENCE-ONLY CLAUSE
A previous architect (Claude Fable, now unavailable) wrote earlier
code. ASK NIR to paste it ONLY IF you think old color logic helps,
and treat it as REFERENCE ONLY — it predates this interface and
its rules. Most likely you need none of it. Note any reuse.

DEEPSEEK-HANDOFF CLAUSE
Mark any genuinely mechanical leftover inline:
  # TODO(DeepSeek): <exact recipe> | ACCEPTANCE: <check>
and repeat at file end under  # === DEEPSEEK TODO SUMMARY === .
Likely there are none (this is brains: color logic). Say so if so.
A plausible exception: final RGB tuning after Nir sees the colors
on screen -> that can be a DeepSeek tuning TODO with anchors named.

TEST PLAN (how Nir verifies — no graphics needed)
Provide a tiny test script test_palette.py that:
  1. Builds a ColorLedger by parsing corridors/01_dummy.txt via
     content_parser (ask Nir to confirm that fixture exists; it
     was committed in Module 1). Its ledger is:
        primaries: alpha=red, beta=yellow, gamma=blue
        blends:    delta = (alpha, beta)   # red+yellow -> orange
  2. Constructs Palette(ledger) and PRINTS:
        - tint("alpha"), tint("beta"), tint("gamma")
        - tint("delta")   # must read as ORANGE-ish
        - tint("NEUTRAL") # must be (0,0,0,0)
        - text_color_on("beta")  # yellow tint -> expect BLACK text
        - text_color_on("alpha") # red tint   -> expect WHITE text
        - eye("gamma")    # bright blue emissive rgb
        - eye("delta")    # bright orange emissive rgb
        - eye("NEUTRAL")  # neutral bright grey
        - blend_rgb("alpha","beta")  # orange
        - the world constants (WALL_FILL, EDGE, CLEAR_COLOR, etc.)
  3. Demonstrate a PaletteError on tint("does_not_exist").
EXPECTED (state in your report so Nir can eyeball):
  - delta and blend_rgb(alpha,beta) are visibly orange (R high,
    G mid, B low).
  - beta (yellow) -> black text; alpha (red) -> white text.
  - NEUTRAL tint fully transparent.
  - undefined key raises PaletteError.

SUCCESS CRITERIA
- palette.py imports with no third-party deps (or only justified).
- All Palette methods behave as specified against the dummy ledger.
- The three kindergarten mixes look right to Nir's eye.
- Every color the rest of the engine needs is defined HERE.

WHEN DONE — COMPLETION REPORT (one page):
  COMPLETION REPORT — module palette — <date>
  FILES CREATED:
  PUBLIC INTERFACES (verbatim final signatures + the world
     color constants and their RGB values):
  KEY DECISIONS: primary RGB anchors chosen; mix formula;
     luminance threshold for black/white text; BACKDROP_BASE_ALPHA.
  DEVIATIONS FROM BRIEF: none / list.
  TRAPS DISCOVERED: anything next children / parent must know.
  OLD-CODE REUSE: none / what.
  DEEPSEEK TODOS LEFT OPEN: none / list (e.g. RGB tuning).
Nir carries this back to the parent; DeepSeek commits it to
/PARENT_ESTATE/reports/.
===========================================================
END CHILD BRIEF #2
===========================================================