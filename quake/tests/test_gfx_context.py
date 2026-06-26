"""Tests for M0 gfx_context — pure caps logic + a guarded window smoke test."""

import pytest

from gfx_context import check_caps, make_window
from conftest import skip_if_no_gl  # provided by conftest.py


def test_caps_rejects_gl32():
    report = check_caps((3, 2), 8192, True)
    assert report.ok is False
    assert any("3.3" in e or "OpenGL" in e for e in report.errors)


def test_caps_rejects_no_fbo():
    report = check_caps((3, 3), 8192, False)
    assert report.ok is False
    assert report.errors  # at least one error


def test_caps_warns_small_texture():
    report = check_caps((3, 3), 3000, True)
    assert report.ok is True
    assert report.errors == []
    assert len(report.warnings) == 1


def test_caps_fails_tiny_texture():
    report = check_caps((3, 3), 1024, True)
    assert report.ok is False
    assert report.errors


def test_caps_accepts_good():
    report = check_caps((3, 3), 8192, True)
    assert report.ok is True
    assert report.errors == []


@skip_if_no_gl
def test_make_window_smoke():
    result = make_window(320, 240, "t")
    assert isinstance(result, tuple)
    assert len(result) == 2
    window, ctx = result
    assert ctx is not None
