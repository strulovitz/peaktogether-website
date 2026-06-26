"""
conftest.py — pytest configuration shared by the whole QUAKE test suite.

Provides the `skip_if_no_gl` marker used by every GPU/window test. Pure-core
tests never use it and always run in headless CI.

Usage in a test module:
    from conftest import skip_if_no_gl   # or rely on pytest collecting it

    @skip_if_no_gl
    def test_programs_compile(...):
        ...
"""
from __future__ import annotations

import pytest

try:
    from glguard import HAVE_GL
except Exception:  # if even importing glguard fails, treat as no-GL
    HAVE_GL = False

# A ready-to-use decorator: @skip_if_no_gl
skip_if_no_gl = pytest.mark.skipif(
    not HAVE_GL,
    reason="No GL context available (headless); skipping GPU/window test.",
)


def pytest_configure(config: "pytest.Config") -> None:
    """Register the marker name so `-W error::pytest.PytestUnknownMarkWarning`
    stays clean and `pytest --markers` documents it."""
    config.addinivalue_line(
        "markers",
        "skip_if_no_gl: skip when no GL context can be created (headless CI).",
    )
