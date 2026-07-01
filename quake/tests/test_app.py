"""Tests for quake/app.py (full §5.4 per-frame loop)."""

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

def test_clamp_pitch_in_range():
    assert app._clamp_pitch(0.0) == 0.0
    assert app._clamp_pitch(1.0) == 1.0
    assert app._clamp_pitch(-0.5) == -0.5


def test_clamp_pitch_above():
    assert app._clamp_pitch(2.0) == app.PITCH_CLAMP_RAD


def test_clamp_pitch_below():
    assert app._clamp_pitch(-2.0) == -app.PITCH_CLAMP_RAD


def test_clamp_pitch_boundary():
    assert app._clamp_pitch(app.PITCH_CLAMP_RAD) == app.PITCH_CLAMP_RAD
    assert app._clamp_pitch(-app.PITCH_CLAMP_RAD) == -app.PITCH_CLAMP_RAD


def test_read_state_defaults():
    rs = app.ReadState()
    assert rs.active is False
    assert rs.zoom == 1.0
    assert rs.pan == (0.0, 0.0)
    assert rs.master_path is None


def test_frame_outcome_defaults():
    fo = app.FrameOutcome()
    assert fo.progress_changed is False
    assert fo.mode_switched_to is None
    assert fo.switched_room_id is None
    assert fo.read_toggle_signaled is False
    assert fo.recompute_guidelines is False


def test_main_headless_returns_zero(monkeypatch):
    """Force the headless path: main() must return 0 without touching GL."""
    monkeypatch.setattr(app, "HAVE_GL", False)
    assert app.main() == 0


def test_progress_event_set_contains_expected():
    assert "panel_lit" in app._PROGRESS_EVENTS
    assert "door_opened" in app._PROGRESS_EVENTS
    assert "demon_killed" in app._PROGRESS_EVENTS
    assert "room_cleared" in app._PROGRESS_EVENTS
    assert "level_complete" in app._PROGRESS_EVENTS
    assert "mode_switch" in app._PROGRESS_EVENTS
    assert "demon_spawned" not in app._PROGRESS_EVENTS
    assert "demon_hit" not in app._PROGRESS_EVENTS


# ---------------------------------------------------------------------------
# GPU smoke test (skipped when no GL context available)
# ---------------------------------------------------------------------------

@skip_if_no_gl
def test_full_loop_smoke():
    """main() opens a window, loads the golden pack, runs 60 frames, exits 0."""
    assert app.main(smoke_frames=60) == 0
