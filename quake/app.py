"""
quake/app.py — M0 thin per-frame loop (STUB).

OWNS NO GAME LOGIC. This proves "the GPU path is ours": open a window, compile
our shaders, draw one shaded triangle + one wireframe line, run a few frames,
exit 0. It will grow across milestones (M1 -> M6 -> M7).

SPLIT:
  - PURE CORE: event_dispatch() — plain function, zero GL/window/IO.
  - THIN SHELL: main() — window/GL/loop. Guarded so import never needs a GL
    context; if HAVE_GL is False, main() returns 0 immediately (headless smoke).

COORDINATES ARE LAW: floorplan is the XZ map-plane, Y is up. Math is row-major
internally; we transpose only at the GL boundary if the call wants column-major.
"""

from __future__ import annotations

from typing import Any, List

import numpy as np

# Shared frozen contracts — never redefined here.
import contracts  # noqa: F401  (kept for parity; pure core uses no types yet)

# Frozen collaborator signatures (talk only through these).
from glguard import HAVE_GL
from gfx_context import make_window
from shaders import wire_program, solid_program


# ---------------------------------------------------------------------------
# PURE CORE (fully testable headless — no GL, no window, no IO)
# ---------------------------------------------------------------------------

def event_dispatch(events: List[Any], ctx: Any) -> list:
    """Dispatch input/events to game logic.

    M0: there is no game logic and nothing to dispatch yet. This is a typed
    placeholder for M1+ so the frame loop can already call it without changing
    its shape later. Returns the list of produced Actions (empty for M0).
    """
    return []


# ---------------------------------------------------------------------------
# Static M0 geometry (pure data — defined here, uploaded by the shell).
# Row-major / map convention: XZ is the floor plane, Y is up.
# Triangle laid flat-ish in front of the camera; positions in 3D + UVs.
# ---------------------------------------------------------------------------

def _solid_triangle_vertices() -> np.ndarray:
    """One flat triangle: 3 vertices of (pos.x, pos.y, pos.z, uv.u, uv.v).

    Pure: builds the interleaved vertex array. No GL involved.
    """
    return np.array(
        [
            # x      y      z      u     v
            [-0.6, -0.4,  0.0,   0.0,  0.0],
            [ 0.6, -0.4,  0.0,   1.0,  0.0],
            [ 0.0,  0.6,  0.0,   0.5,  1.0],
        ],
        dtype=np.float32,
    )


def _wire_line_vertices() -> np.ndarray:
    """One line: 2 endpoints of (pos.x, pos.y, pos.z). Pure data."""
    return np.array(
        [
            [-0.8, -0.8, 0.0],
            [ 0.8,  0.8, 0.0],
        ],
        dtype=np.float32,
    )


def _identity_view() -> np.ndarray:
    """Row-major 4x4 identity ViewMatrix used by the M0 stub (no camera yet)."""
    return np.eye(4, dtype=np.float32)


# ---------------------------------------------------------------------------
# INTEGRATION WRAPPERS — every uncertain external API is isolated here, one
# tiny function each. Do NOT assert these API names elsewhere as fact.
# ---------------------------------------------------------------------------

def _gl_clear(ctx: Any, r: float, g: float, b: float, a: float) -> None:
    # INTEGRATION: confirm exact API (ctx.clear(r,g,b,a) vs screen.color_mask+clear)
    ctx.clear(r, g, b, a)


def _gl_make_vbo(ctx: Any, data: np.ndarray) -> Any:
    # INTEGRATION: confirm exact API (moderngl ctx.buffer(data=bytes))
    return ctx.buffer(data.tobytes())


def _gl_make_vao(ctx: Any, program: Any, vbo: Any, fmt: str, attrs: list) -> Any:
    # INTEGRATION: confirm exact API
    # (moderngl ctx.vertex_array(program, [(vbo, fmt, *attr_names)]))
    return ctx.vertex_array(program, [(vbo, fmt, *attrs)])


def _gl_set_uniform_mvp(program: Any, mvp_row_major: np.ndarray) -> None:
    # INTEGRATION: confirm exact API + memory order.
    # GL programs commonly expect column-major; transpose at the boundary.
    try:
        program["u_mvp"].write(np.ascontiguousarray(mvp_row_major.T).tobytes())
    except KeyError:
        # Shader may not declare this uniform in the M0 stub; ignore safely.
        pass


def _gl_render_triangle(vao: Any) -> None:
    # INTEGRATION: confirm exact API (moderngl: vao.render(moderngl.TRIANGLES))
    import moderngl
    vao.render(moderngl.TRIANGLES)


def _gl_render_line(vao: Any) -> None:
    # INTEGRATION: confirm exact API (moderngl: vao.render(moderngl.LINES))
    import moderngl
    vao.render(moderngl.LINES)


def _window_should_close(window: Any) -> bool:
    # INTEGRATION: confirm exact API (pyglet: window.has_exit) — best-effort.
    return bool(getattr(window, "has_exit", False))


def _window_present(window: Any) -> None:
    # INTEGRATION: confirm exact API (pyglet: window.flip() + dispatch_events)
    if hasattr(window, "dispatch_events"):
        window.dispatch_events()
    if hasattr(window, "flip"):
        window.flip()


def _collect_events(window: Any) -> list:
    # INTEGRATION: M0 has no input pipeline; placeholder for M1+.
    return []


# ---------------------------------------------------------------------------
# THIN SHELL — main(). Skips all GL work headlessly; returns 0 cleanly.
# ---------------------------------------------------------------------------

# CI smoke mode: render this many frames then exit. Set <=0 to run until close.
_SMOKE_FRAMES = 60


def main() -> int:
    """M0 thin loop. Returns 0 on clean exit.

    Headless (no GL): returns 0 immediately — the smoke-launch path.
    """
    if not HAVE_GL:
        # Headless smoke-launch: prove the module imports and main() is callable.
        return 0

    # Local import so the module imports fine without moderngl installed.
    import moderngl  # noqa: F401  (used inside integration wrappers)

    window, ctx = _unpack_window(make_window(1280, 720, "QUAKE M0"))

    # Compile our shaders. gfx_context already set depth ON / blend OFF.
    solid_prog = solid_program(ctx)
    wire_prog = wire_program(ctx)

    # Build static geometry (pure) and upload (shell).
    tri = _solid_triangle_vertices()
    line = _wire_line_vertices()
    tri_vbo = _gl_make_vbo(ctx, tri)
    line_vbo = _gl_make_vbo(ctx, line)

    # INTEGRATION: confirm attribute names declared in shaders.py.
    # solid: position(3) + uv(2) interleaved -> moderngl format "3f 2f".
    tri_vao = _gl_make_vao(ctx, solid_prog, tri_vbo, "3f 2f", ["in_pos", "in_uv"])
    # wire: position(3) only -> "3f".
    line_vao = _gl_make_vao(ctx, wire_prog, line_vbo, "3f", ["in_pos"])

    view = _identity_view()  # row-major; no camera in M0.

    smoke = _SMOKE_FRAMES > 0
    frame = 0
    try:
        while True:
            if smoke and frame >= _SMOKE_FRAMES:
                break
            if not smoke and _window_should_close(window):
                break

            # (a) Clear — dark background.
            _gl_clear(ctx, 0.05, 0.06, 0.08, 1.0)

            # Events: pure dispatch placeholder for M1+.
            events = _collect_events(window)
            event_dispatch(events, ctx)

            # (b) Shaded triangle.
            _gl_set_uniform_mvp(solid_prog, view)
            _gl_render_triangle(tri_vao)

            # (c) Wireframe line.
            _gl_set_uniform_mvp(wire_prog, view)
            _gl_render_line(line_vao)

            # (e) Present.
            _window_present(window)
            frame += 1
    finally:
        _close_window(window)

    return 0


def _unpack_window(made: Any):
    """make_window may return (window, ctx) or a struct. Normalize here.

    INTEGRATION: confirm make_window's return shape in gfx_context.
    """
    if isinstance(made, tuple) and len(made) == 2:
        return made[0], made[1]
    # Fallback: object exposing .window and .ctx
    return getattr(made, "window", made), getattr(made, "ctx", made)


def _close_window(window: Any) -> None:
    # INTEGRATION: confirm exact API (pyglet: window.close()).
    if window is not None and hasattr(window, "close"):
        try:
            window.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
