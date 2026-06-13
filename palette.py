"""palette.py — DESCENT QED engine, Module: palette.

Turns abstract LEDGER KEYS into colors per the Kindergarten Mixing Law.
This module is MATHEMATICS-BLIND: it never knows what a key MEANS, only
its structural role (primary / blend / NEUTRAL) as recorded in the ledger.

Zero third-party dependencies. Pure-Python tuple math. Returns numbers
only — no pygame, no OpenGL, no numpy.

Kindergarten Mixing Law (structure this module serves):
  primaries  : red, yellow, blue          (max 3 per corridor; parser owns that)
  secondaries: orange = red+yellow
               green  = yellow+blue
               purple = red+blue
  A secondary may ONLY appear as a BLEND of its two parents.
  GLUE / lone constants -> NEUTRAL -> no backdrop.

The engine WORLD is achromatic; chroma is reserved for MEANING. This module
is therefore the SINGLE SOURCE of both the meaning-colors and the canonical
world greys. No other module should invent colors.
"""

from __future__ import annotations

# We import ColorLedger only for type clarity; we never inspect its internals
# beyond the documented public surface (primaries, blends, is_defined).
try:
    from content_parser import ColorLedger  # noqa: F401  (type reference)
except Exception:  # pragma: no cover - allows palette to be imported standalone
    ColorLedger = object  # type: ignore


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class PaletteError(Exception):
    """Raised for an UNDEFINED, non-neutral key, or an illegal blend request."""


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

# Base alpha for equation-segment backdrop tints. The reading_system scales
# the FINAL on-screen opacity by a user "backdrop_opacity" slider on top of this.
BACKDROP_BASE_ALPHA: float = 0.55

# Luminance threshold (Rec.709) above which text on a tint should be BLACK.
_TEXT_LUMA_THRESHOLD: float = 0.55

# Strength of the hue-agnostic "gamut deepening" applied during mixing so that
# kindergarten secondaries read vividly instead of as RGB-average mud.
_MIX_DEEPEN_K: float = 0.5

# How much brighter the emissive eye-glow is than the flat backdrop tint.
_EYE_BOOST: float = 1.25

# --- PRIMARY ANCHORS (concrete, documented RGB; tune via DeepSeek TODO) -----
# Clean & saturated; chosen so component-wise mixing -> correct secondaries.
_PRIMARY_RGB: dict[str, tuple[float, float, float]] = {
    "red":    (0.85, 0.12, 0.12),
    "yellow": (0.95, 0.85, 0.10),
    "blue":   (0.12, 0.30, 0.85),
}

# --- WORLD GREYS / ACHROMATIC + special meaning colors ----------------------
# THE ONLY place these are defined. Pull from here everywhere.
CLEAR_COLOR:     tuple[float, float, float]        = (0.045, 0.055, 0.10)
WORLD_WALL_FILL: tuple[float, float, float, float] = (0.16, 0.17, 0.20, 0.85)  # dark grey translucent
WORLD_EDGE:      tuple[float, float, float]        = (0.88, 0.90, 0.94)        # light grey/white wireframe

HOSTAGE_BLUE:    tuple[float, float, float]        = (0.30, 0.65, 1.00)        # bright rescue blue
HAZARD_YELLOW:   tuple[float, float, float]        = (0.98, 0.80, 0.05)        # chevron stripe A
HAZARD_BLACK:    tuple[float, float, float]        = (0.05, 0.05, 0.06)        # chevron stripe B

# Neutral bright grey used for a NEUTRAL eye-band (achromatic glow).
_NEUTRAL_EYE_GREY: tuple[float, float, float] = (0.80, 0.82, 0.86)


# ---------------------------------------------------------------------------
# Internal mixing helpers (hue-blind, deterministic, symmetric)
# ---------------------------------------------------------------------------
def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def _mix_rgb(a: tuple[float, float, float],
             b: tuple[float, float, float]) -> tuple[float, float, float]:
    """Mix two RGB colors per the documented law:

        c_i = mean(a_i, b_i) * (1 - k * |a_i - b_i|)

    Channels where the parents AGREE survive; channels where they disagree
    strongly are pulled toward 0 (mimics subtractive paint mixing). Symmetric
    in (a, b) and fully deterministic. Hue-AGNOSTIC: no color is special-cased.
    """
    out = []
    for ai, bi in zip(a, b):
        mean = 0.5 * (ai + bi)
        deepened = mean * (1.0 - _MIX_DEEPEN_K * abs(ai - bi))
        out.append(_clamp01(deepened))
    return (out[0], out[1], out[2])


def _luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _brighten_keep_hue(rgb: tuple[float, float, float],
                       boost: float) -> tuple[float, float, float]:
    """Brighten an RGB triple for an emissive glow WITHOUT shifting its hue.

    Naive per-channel (c*boost then clamp) clips the strongest channel and
    drags the hue toward that channel (e.g. orange -> red). Instead we scale
    all channels by the LARGEST factor that keeps the brightest channel <= 1,
    capped by `boost`. Hue ratios between channels are preserved exactly.
    """
    peak = max(rgb)
    if peak <= 0.0:
        return rgb
    safe = min(boost, 1.0 / peak)   # never let any channel exceed 1.0
    return (rgb[0] * safe, rgb[1] * safe, rgb[2] * safe)


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
class Palette:
    """Maps ledger KEYS -> colors. Knows nothing about what keys MEAN."""

    def __init__(self, ledger):
        self.ledger = ledger

    # -- internal: resolve a key (primary or blend) to a flat RGB triple ----
    def _key_rgb(self, key: str) -> tuple[float, float, float]:
        """Return the base RGB for a PRIMARY or BLEND key.

        NEUTRAL is handled by callers (it has no backdrop) and is NOT valid here.
        Undefined non-neutral keys raise PaletteError.
        """
        # PRIMARY?
        prim = self.ledger.primaries.get(key)
        if prim is not None:
            try:
                return _PRIMARY_RGB[prim]
            except KeyError:
                raise PaletteError(
                    f"key {key!r} maps to unknown primary name {prim!r} "
                    f"(expected one of {sorted(_PRIMARY_RGB)})"
                )
        # BLEND?
        parents = self.ledger.blends.get(key)
        if parents is not None:
            a_name, b_name = parents
            return self._parent_rgb(a_name, b_name, context=key)
        # Not primary, not blend, not NEUTRAL.
        raise PaletteError(
            f"key {key!r} is not defined as a primary or blend in the ledger"
        )

    def _parent_rgb(self, a_name: str, b_name: str,
                    context: str | None = None) -> tuple[float, float, float]:
        """Resolve two PRIMARY *keys* and mix them. Both must be primaries and
        must differ (a secondary is a mix of TWO distinct primaries)."""
        if a_name == b_name:
            where = f" (blend {context!r})" if context else ""
            raise PaletteError(
                f"illegal blend{where}: both parents are {a_name!r}; "
                f"a secondary needs two DIFFERENT primaries"
            )
        a_prim = self.ledger.primaries.get(a_name)
        b_prim = self.ledger.primaries.get(b_name)
        if a_prim is None or b_prim is None:
            where = f" (blend {context!r})" if context else ""
            bad = a_name if a_prim is None else b_name
            raise PaletteError(
                f"illegal blend{where}: parent {bad!r} is not a primary"
            )
        return _mix_rgb(_PRIMARY_RGB[a_prim], _PRIMARY_RGB[b_prim])

    # -- meaning colors (chroma) -------------------------------------------
    def tint(self, key: str) -> tuple[float, float, float, float]:
        """RGBA backdrop tint for an equation segment.

        NEUTRAL -> (0,0,0,0): caller draws NO backdrop quad.
        PRIMARY -> that primary's tint at BACKDROP_BASE_ALPHA.
        BLEND   -> blended tint of its two parents at BACKDROP_BASE_ALPHA.
        Undefined non-neutral key -> PaletteError.
        """
        if key == "NEUTRAL":
            return (0.0, 0.0, 0.0, 0.0)
        r, g, b = self._key_rgb(key)
        return (r, g, b, BACKDROP_BASE_ALPHA)

    def text_color_on(self, key: str) -> tuple[float, float, float]:
        """Black text on LIGHT tints, white text on dark tints (by luminance).
        NEUTRAL -> white (text floats on the dark world)."""
        if key == "NEUTRAL":
            return (1.0, 1.0, 1.0)
        rgb = self._key_rgb(key)
        if _luminance(rgb) > _TEXT_LUMA_THRESHOLD:
            return (0.0, 0.0, 0.0)  # light tint -> black text
        return (1.0, 1.0, 1.0)      # dark tint  -> white text

    def eye(self, key: str) -> tuple[float, float, float]:
        """Bright EMISSIVE glow RGB (no alpha) for a robot eye-band.
        Same HUE as tint(), brightened without hue shift. NEUTRAL -> bright grey."""
        if key == "NEUTRAL":
            return _NEUTRAL_EYE_GREY
        rgb = self._key_rgb(key)
        return _brighten_keep_hue(rgb, _EYE_BOOST)

    def blend_rgb(self, keyA: str, keyB: str) -> tuple[float, float, float]:
        """Mix two PRIMARY keys per the law (for combined expressions / door
        glows). Illegal if not both primaries or if the same key."""
        return self._parent_rgb(keyA, keyB, context=None)


# === DEEPSEEK TODO SUMMARY =================================================
# TODO(DeepSeek): After Nir sees colors on screen, fine-tune the three anchors
#   in _PRIMARY_RGB (named: "red","yellow","blue") and optionally _MIX_DEEPEN_K
#   so that orange/green/purple read crisply. ACCEPTANCE: in test_palette.py
#   output, delta(orange) has R>G>B with R high & B low; green mix has G as the
#   largest channel; purple mix has R≈B > G. Do NOT change formulas or signatures.
# No other mechanical leftovers — this module is color logic (brains).