"""Tests for quake/shaders.py."""

from __future__ import annotations

import pytest

from glguard import HAVE_GL

from shaders import (
    WIRE_VS, WIRE_FS,
    SOLID_VS, SOLID_FS,
    BLIT_VS, BLIT_FS,
    tint_rgb,
    wire_program,
    solid_program,
    blit_program,
    ceiling_tint_uniform,
)

try:
    from conftest import skip_if_no_gl
except ImportError:  # pragma: no cover
    skip_if_no_gl = pytest.mark.skipif(not HAVE_GL, reason="no GL context")


# --------------------------------------------------------------------------
# PURE CORE TESTS
# --------------------------------------------------------------------------

def test_glsl_constants_present():
    sources = {
        "WIRE_VS": WIRE_VS, "WIRE_FS": WIRE_FS,
        "SOLID_VS": SOLID_VS, "SOLID_FS": SOLID_FS,
        "BLIT_VS": BLIT_VS, "BLIT_FS": BLIT_FS,
    }
    for name, src in sources.items():
        assert isinstance(src, str), f"{name} must be str"
        assert src.strip(), f"{name} must be non-empty"
        assert "#version 330" in src, f"{name} must target GLSL 330"


def test_tint_rgb_blood_red():
    assert tint_rgb(1.0) == (1.0, 0.0, 0.0)
    assert tint_rgb(0.5)[0] == 0.5
    # green/blue always 0
    for r in (0.0, 0.5, 1.0, 2.0, -3.0):
        g, b = tint_rgb(r)[1], tint_rgb(r)[2]
        assert g == 0.0
        assert b == 0.0


def test_tint_rgb_clamps():
    assert tint_rgb(2.0)[0] == 1.0
    assert tint_rgb(-1)[0] == 0.0


# --------------------------------------------------------------------------
# GPU TESTS
# --------------------------------------------------------------------------

@skip_if_no_gl
def test_programs_compile():
    import moderngl  # INTEGRATION: confirm moderngl standalone context API
    ctx = moderngl.create_standalone_context()
    try:
        wp = wire_program(ctx)
        sp = solid_program(ctx)
        bp = blit_program(ctx)
        assert wp is not None
        assert sp is not None
        assert bp is not None
        # ceiling tint should not raise on a real program
        ceiling_tint_uniform(sp, 1.0)
        ceiling_tint_uniform(sp, 0.0)
    finally:
        ctx.release()
