"""Tests for quake/app.py (M0 thin loop)."""

import app
from glguard import HAVE_GL

try:
    from conftest import skip_if_no_gl
except ImportError:  # pragma: no cover - conftest provides this fixture/marker
    import pytest
    skip_if_no_gl = pytest.mark.skipif(not HAVE_GL, reason="no GL context")


# ---------------------------------------------------------------------------
# PURE CORE tests (always run, fully headless)
# ---------------------------------------------------------------------------

def test_event_dispatch_returns_empty_list():
    """M0: nothing to dispatch yet — must return an empty list, never crash."""
    out = app.event_dispatch([], ctx=None)
    assert out == []
    assert isinstance(out, list)


def test_event_dispatch_ignores_input():
    """Placeholder must not consume/produce anything in M0."""
    assert app.event_dispatch(["fake", "events"], ctx=object()) == []


def test_solid_triangle_geometry_shape():
    tri = app._solid_triangle_vertices()
    assert tri.shape == (3, 5)          # 3 verts, pos(3)+uv(2)
    assert str(tri.dtype) == "float32"


def test_wire_line_geometry_shape():
    line = app._wire_line_vertices()
    assert line.shape == (2, 3)         # 2 endpoints, pos(3)
    assert str(line.dtype) == "float32"


def test_identity_view_is_row_major_4x4():
    import numpy as np
    view = app._identity_view()
    assert view.shape == (4, 4)
    assert str(view.dtype) == "float32"
    assert np.allclose(view, np.eye(4))


def test_main_headless_returns_zero(monkeypatch):
    """Force the headless path: main() must return 0 without touching GL."""
    monkeypatch.setattr(app, "HAVE_GL", False)
    assert app.main() == 0


# ---------------------------------------------------------------------------
# GPU smoke test (skipped when no GL context available)
# ---------------------------------------------------------------------------

@skip_if_no_gl
def test_m0_smoke():
    """main() opens a window, renders a few frames, and exits 0 cleanly."""
    assert app.main() == 0
