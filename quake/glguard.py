"""
glguard.py — headless-safe probe for whether a real GL context can be made.

Engine render/window shells check `if not glguard.HAVE_GL: return` at the top of
any draw/context call so that:
  * importing any engine module on a headless CI machine never crashes, and
  * the smoke launch degrades gracefully instead of throwing.

This module performs the probe ONCE at import, swallowing every failure. It must
never raise on import.
"""
from __future__ import annotations


def _probe() -> bool:
    """Return True iff a moderngl context can be created right now.

    INTEGRATION: confirm the exact pyglet 2.1.x hidden-window + moderngl
    create_context incantation. The structure (try/except → bool) is fixed;
    only the two external calls inside may need their exact names confirmed.
    """
    try:
        import moderngl  # noqa: WPS433 (local import is intentional)
        # Preferred: a standalone context needs no visible window.
        # INTEGRATION: moderngl.create_context(standalone=True, require=330)
        ctx = moderngl.create_standalone_context(require=330)
        ok = ctx is not None
        try:
            ctx.release()
        except Exception:
            pass
        return ok
    except Exception:
        # Fall back to a hidden pyglet window + attached context.
        try:
            import pyglet  # noqa: WPS433
            import moderngl  # noqa: WPS433
            # INTEGRATION: confirm pyglet 2.1.x Window(visible=False) and that
            # moderngl.create_context() binds to the current pyglet GL context.
            win = pyglet.window.Window(width=8, height=8, visible=False)
            ctx = moderngl.create_context()
            ok = ctx is not None
            try:
                win.close()
            except Exception:
                pass
            return ok
        except Exception:
            return False


# Probe exactly once at import; never raise.
try:
    HAVE_GL: bool = _probe()
except Exception:  # pragma: no cover - belt and suspenders
    HAVE_GL = False
