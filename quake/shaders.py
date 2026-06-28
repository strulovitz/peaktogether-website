"""QUAKE runtime — shaders.py (M0).

Authors OUR GLSL and compiles the three programs (wire / solid / blit),
all targeting GLSL 330 core.

SPLIT:
  * PURE CORE  — GLSL source string constants + tint_rgb(). No GL, no IO.
  * THIN SHELL — wire_program/solid_program/blit_program compile via ctx.program(...).
                 Guarded by HAVE_GL so the module imports headless and never crashes.

COORDINATES ARE LAW: floorplan is the XZ map-plane, Y up. Matrices are row-major
internally (contracts.ViewMatrix); transpose at the GL boundary if needed.
"""

from __future__ import annotations

from glguard import HAVE_GL

# We import shared types from contracts only to honour the "import shared types"
# rule; this module is GLSL-authoring + compilation and does not redefine any.
# (No shared dataclass is needed by the signatures here, but the dependency is
#  declared so we never accidentally redefine anything elsewhere.)
import contracts as _contracts  # noqa: F401  (kept for contract discipline)


# ============================================================================
# PURE CORE
# ============================================================================

def clamp01(x: float) -> float:
    """Clamp a float into [0.0, 1.0]. Pure."""
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def tint_rgb(red: float) -> tuple[float, float, float]:
    """Blood-red tint triple: (clamp01(red), 0.0, 0.0). Pure, unit-tested."""
    return (clamp01(red), 0.0, 0.0)


# ---------------------------------------------------------------------------
# GLSL SOURCE — inspectable as plain strings without a GL context.
# All target "#version 330 core".
# ---------------------------------------------------------------------------

# --- wire: Mode A lines (simple LINES, depth-tested) ------------------------
WIRE_VS = """#version 330 core

uniform mat4  u_mvp;

in vec3 in_pos;
in vec3 in_color;

out vec3 v_color;

void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_color = in_color;
}
"""

WIRE_FS = """#version 330 core

in vec3 v_color;

out vec4 frag_color;

void main() {
    frag_color = vec4(v_color, 1.0);
}
"""

# --- solid: Mode B textured panels / walls ---------------------------------
SOLID_VS = """#version 330 core

uniform mat4 u_mvp;

in vec3 in_pos;
in vec2 in_uv;

out vec2 v_uv;

void main() {
    v_uv = in_uv;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
"""

SOLID_FS = """#version 330 core

uniform sampler2D u_tex;
uniform vec3      u_tint;
uniform int       u_use_tint;   // 0 / 1

in vec2 v_uv;

out vec4 frag_color;

void main() {
    vec4 texel = texture(u_tex, v_uv);
    vec3 rgb = texel.rgb;
    if (u_use_tint == 1) {
        rgb *= u_tint;
    }
    frag_color = vec4(rgb, texel.a);  // respect alpha
}
"""

# --- blit: fullscreen textured quad (Read Mode + bloom composite) ----------
BLIT_VS = """#version 330 core

in vec2 in_pos;   // NDC position
in vec2 in_uv;

out vec2 v_uv;

void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

BLIT_FS = """#version 330 core

uniform sampler2D u_tex;
uniform float     u_zoom;
uniform vec2      u_pan;

in vec2 v_uv;

out vec4 frag_color;

void main() {
    vec2 uv = (v_uv - 0.5) / u_zoom + 0.5 + u_pan;
    frag_color = texture(u_tex, uv);
}
"""


# ============================================================================
# THIN SHELL — GL program compilation. Guarded by HAVE_GL.
# ============================================================================

def _compile_program(ctx, vertex_src: str, fragment_src: str):
    """Single isolated GL wrapper.

    INTEGRATION: confirm moderngl ctx.program(vertex_shader=..., fragment_shader=...)
    returns a compiled Program object.
    """
    return ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)


def wire_program(ctx):
    """Compile the Mode-A wire program. Returns a moderngl Program (or None headless)."""
    if not HAVE_GL or ctx is None:
        return None
    return _compile_program(ctx, WIRE_VS, WIRE_FS)


def solid_program(ctx):
    """Compile the Mode-B solid/textured program. Returns Program (or None headless)."""
    if not HAVE_GL or ctx is None:
        return None
    return _compile_program(ctx, SOLID_VS, SOLID_FS)


def blit_program(ctx):
    """Compile the fullscreen blit program. Returns Program (or None headless)."""
    if not HAVE_GL or ctx is None:
        return None
    return _compile_program(ctx, BLIT_VS, BLIT_FS)


def _set_uniform(prog, name: str, value) -> None:
    """Isolated uniform-set wrapper; silently ignores missing uniforms.

    INTEGRATION: confirm prog['name'].value = value is the moderngl uniform API,
    and that absent uniforms raise KeyError (which we swallow).
    """
    try:
        prog[name].value = value  # INTEGRATION: confirm exact API
    except (KeyError, Exception):  # noqa: BLE001 — tolerate missing/optimized-out uniforms
        # If the uniform was optimized out or the program is headless (None),
        # do not crash the runtime.
        pass


def ceiling_tint_uniform(prog, red: float) -> None:
    """Set the solid program's ceiling tint.

    u_tint   = tint_rgb(red)
    u_use_tint = 1 if red > 0 else 0
    """
    if prog is None:
        return
    rgb = tint_rgb(red)
    _set_uniform(prog, "u_tint", rgb)
    _set_uniform(prog, "u_use_tint", 1 if red > 0.0 else 0)
