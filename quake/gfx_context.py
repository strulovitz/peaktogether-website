"""QUAKE runtime — M0: window + GL context ownership and GPU capability check.

PURE CORE  : check_caps(...)  — judges queried GL numbers, zero GL/window/IO.
THIN SHELL : make_window(...) — pyglet window + moderngl context + state setup.

Coordinate / matrix conventions are not relevant to this module (no math here),
but the GL-state invariant (Mode-A) lives here: depth test on, LEQUAL, depth
write on, blend off.
"""

from __future__ import annotations

import sys

from contracts import Report
from glguard import HAVE_GL

# Thresholds (OT §11.4).
_MIN_GL_VERSION: tuple[int, int] = (3, 3)
_WARN_TEXTURE_SIZE: int = 4096
_FAIL_TEXTURE_SIZE: int = 2048


# --------------------------------------------------------------------------- #
# PURE CORE
# --------------------------------------------------------------------------- #
def _make_report(ok: bool, errors: list[str], warnings: list[str]) -> Report:
    """Construct a contracts.Report.

    Isolated so the exact constructor shape lives in exactly one place.
    INTEGRATION: confirm Report field names/order (assumed ok, errors, warnings).
    """
    return Report(ok=ok, errors=errors, warnings=warnings)


def check_caps(
    gl_version: tuple[int, int],
    max_texture_size: int,
    has_fbo: bool,
) -> Report:
    """Judge queried GPU capabilities against OT §11.4 requirements.

    Pure: the caller passes the numbers already queried from the context.

    FAIL if gl_version < (3, 3).
    FAIL if not has_fbo.
    FAIL if max_texture_size < 2048.
    WARN if 2048 <= max_texture_size < 4096 (master-DPI panels may exceed it).
    """
    errors: list[str] = []
    warnings: list[str] = []

    if tuple(gl_version) < _MIN_GL_VERSION:
        have = f"{gl_version[0]}.{gl_version[1]}"
        errors.append(
            f"OpenGL 3.3 or newer is required (this GPU reports OpenGL {have})."
        )

    if not has_fbo:
        errors.append(
            "Framebuffer objects (FBO) are required but not supported by this GPU."
        )

    if max_texture_size < _FAIL_TEXTURE_SIZE:
        errors.append(
            f"Maximum texture size is too small: {max_texture_size} "
            f"(need at least {_FAIL_TEXTURE_SIZE})."
        )
    elif max_texture_size < _WARN_TEXTURE_SIZE:
        warnings.append(
            f"Maximum texture size is {max_texture_size} (< {_WARN_TEXTURE_SIZE}); "
            "high-DPI master panels may exceed it and be downscaled."
        )

    return _make_report(ok=not errors, errors=errors, warnings=warnings)


# --------------------------------------------------------------------------- #
# THIN SHELL — GL / window / IO. Headless-safe to import; raises on run.
# --------------------------------------------------------------------------- #
def _create_pyglet_window(width: int, height: int, title: str):
    """INTEGRATION: confirm exact API — pyglet 2.1.x Window constructor args."""
    import pyglet  # local import: never required just to import this module

    win = pyglet.window.Window(
        width=width,
        height=height,
        caption=title,
        resizable=True,
        vsync=True,
    )

    # Manual key + mouse state (pyglet 2.1.14 KeyStateHandler broken on Windows)
    _pressed: set[int] = set()
    _mouse_dx: float = 0.0
    _mouse_dy: float = 0.0
    _mouse_left: bool = False

    @win.event
    def on_key_press(symbol, modifiers):
        _pressed.add(symbol)

    @win.event
    def on_key_release(symbol, modifiers):
        _pressed.discard(symbol)

    @win.event
    def on_mouse_motion(x, y, dx, dy):
        nonlocal _mouse_dx, _mouse_dy
        _mouse_dx += dx
        _mouse_dy += dy

    @win.event
    def on_mouse_press(x, y, button, modifiers):
        nonlocal _mouse_left
        if button == 1:
            _mouse_left = True

    @win.event
    def on_mouse_release(x, y, button, modifiers):
        nonlocal _mouse_left
        if button == 1:
            _mouse_left = False

    def _consume_mouse():
        nonlocal _mouse_dx, _mouse_dy
        dx, dy = _mouse_dx, _mouse_dy
        _mouse_dx = 0.0
        _mouse_dy = 0.0
        return dx, dy

    win._quake_keystate = _pressed
    win._quake_mousedx = _consume_mouse
    win._quake_mouseleft = lambda: _mouse_left

    win.set_exclusive_mouse(True)

    return win


def _create_gl_context():
    """INTEGRATION: confirm exact API — moderngl.create_context()."""
    import moderngl

    return moderngl.create_context()


def _query_caps(ctx) -> tuple[tuple[int, int], int, bool]:
    """Read (gl_version, max_texture_size, has_fbo) from a moderngl context.

    INTEGRATION: confirm exact API — moderngl context.info keys:
      'GL_VERSION' (string like '3.3.0 ...'), 'GL_MAX_TEXTURE_SIZE' (int).
    FBO support is implied by any GL >= 3.0 core context; we treat presence of
    the framebuffer interface as the signal.
    """
    info = ctx.info  # INTEGRATION: confirm 'info' attribute exists on context

    version_str = str(info.get("GL_VERSION", "0.0"))
    gl_version = _parse_gl_version(version_str)

    max_texture_size = int(info.get("GL_MAX_TEXTURE_SIZE", 0))

    # moderngl always exposes ctx.framebuffer / ctx.screen on a valid 3.x core
    # context; absence indicates a broken/legacy context.
    has_fbo = hasattr(ctx, "framebuffer") and hasattr(ctx, "screen")

    return gl_version, max_texture_size, has_fbo


def _parse_gl_version(version_str: str) -> tuple[int, int]:
    """Parse a GL_VERSION string ('3.3.0 NVIDIA ...') into (major, minor).

    Pure helper; kept private but trivially testable.
    """
    head = version_str.strip().split(" ")[0]  # drop vendor suffix
    parts = head.split(".")
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        return (0, 0)
    return (major, minor)


def _apply_mode_a_state(ctx) -> None:
    """Set the Mode-A GL invariant exactly once.

    Depth test ON, depth func LEQUAL, depth write ON, blend OFF.
    INTEGRATION: confirm exact API —
      ctx.enable(moderngl.DEPTH_TEST); ctx.depth_func = '<='; ctx.disable(moderngl.BLEND)
    """
    import moderngl

    ctx.enable(moderngl.DEPTH_TEST)
    ctx.depth_func = "<="          # LEQUAL
    ctx.depth_mask = True          # depth write ON
    ctx.disable(moderngl.BLEND)


def _show_fatal_error(message: str) -> None:
    """Surface a fatal capability error to the user before exiting.

    INTEGRATION: confirm exact API — a real pyglet label window or OS messagebox
    would be nicer; a printed error is an acceptable fallback per the brief.
    """
    sys.stderr.write("QUAKE: GPU capability check failed.\n")
    sys.stderr.write(message + "\n")
    sys.stderr.flush()


def make_window(width: int, height: int, title: str):
    """Create our window + GL context, validate capabilities, set Mode-A state.

    Returns (window, gl_context). Exits the process (1) if caps fail.
    Raises RuntimeError if no GL is available (cannot run headless).
    """
    if not HAVE_GL:
        raise RuntimeError(
            "make_window requires a GL context, but glguard.HAVE_GL is False "
            "(running headless). The pure check_caps() is available instead."
        )

    window = _create_pyglet_window(width, height, title)
    ctx = _create_gl_context()

    gl_version, max_texture_size, has_fbo = _query_caps(ctx)
    report = check_caps(gl_version, max_texture_size, has_fbo)

    if not report.ok:
        _show_fatal_error("\n".join(report.errors))
        sys.exit(1)

    _apply_mode_a_state(ctx)

    return (window, ctx)
