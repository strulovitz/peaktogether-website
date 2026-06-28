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

# --- solid: Mode B textured panels / walls (LIT — Parent 11) ----------------
SOLID_VS = """
#version 330 core
uniform mat4 u_mvp;
in vec3 in_pos;
in vec2 in_uv;
in vec3 in_normal;          // flat face normal (world space)
out vec2 v_uv;
out vec3 v_normal;
void main() {
    v_uv = in_uv;
    v_normal = in_normal;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
"""

SOLID_FS = """
#version 330 core
uniform sampler2D u_tex;
uniform vec3  u_tint;        // for untextured surfaces: base color; for ceiling: blood-red
uniform int   u_use_tint;    // 0 = textured panel, 1 = tint multiplies texel, 2 = solid base color (lit, untextured)
uniform vec3  u_light_dir;   // normalized, world space, points FROM surface TO light
uniform float u_ambient;     // ambient floor (e.g. 0.35)
in vec2 v_uv;
in vec3 v_normal;
out vec4 frag_color;
void main() {
    if (u_use_tint == 2) {
        // untextured lit surface: u_tint is the base color
        vec3 N = normalize(v_normal);
        float ndl = max(dot(N, u_light_dir), 0.0);
        float lit = u_ambient + (1.0 - u_ambient) * ndl;
        frag_color = vec4(u_tint * lit, 1.0);
    } else {
        vec4 texel = texture(u_tex, v_uv);
        vec3 rgb = texel.rgb;
        if (u_use_tint == 1) { rgb *= u_tint; }   // ceiling tint multiplies
        frag_color = vec4(rgb, texel.a);
    }
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


# ---- Mode A: camera-facing line-quads via GEOMETRY SHADER (primary path) ----
WIREQ_VS = """
#version 330 core
uniform mat4 u_mvp;
in vec3 in_pos;
in vec3 in_color;
out vec3 g_color;
out float g_wdist;          // view-distance proxy = clip.w
void main() {
    vec4 clip = u_mvp * vec4(in_pos, 1.0);
    g_color = in_color;
    g_wdist = clip.w;
    gl_Position = clip;
}
"""

WIREQ_GS = """
#version 330 core
layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;
uniform float u_aspect;     // width/height
uniform float u_half_px;    // half-thickness in NDC-Y units
in  vec3  g_color[];
in  float g_wdist[];
out vec3  f_color;
out float f_wdist;
void main() {
    // perspective divide to NDC
    vec2 p0 = gl_in[0].gl_Position.xy / gl_in[0].gl_Position.w;
    vec2 p1 = gl_in[1].gl_Position.xy / gl_in[1].gl_Position.w;
    // direction in aspect-corrected space so thickness is uniform on screen
    vec2 d = normalize((p1 - p0) * vec2(u_aspect, 1.0));
    vec2 n = vec2(-d.y, d.x);                 // screen-space normal
    vec2 off = vec2(n.x / u_aspect, n.y) * u_half_px;
    vec4 c0 = gl_in[0].gl_Position;
    vec4 c1 = gl_in[1].gl_Position;
    // expand each endpoint; multiply offset by w to keep it in clip space
    gl_Position = c0 + vec4(off * c0.w, 0.0, 0.0); f_color=g_color[0]; f_wdist=g_wdist[0]; EmitVertex();
    gl_Position = c0 - vec4(off * c0.w, 0.0, 0.0); f_color=g_color[0]; f_wdist=g_wdist[0]; EmitVertex();
    gl_Position = c1 + vec4(off * c1.w, 0.0, 0.0); f_color=g_color[1]; f_wdist=g_wdist[1]; EmitVertex();
    gl_Position = c1 - vec4(off * c1.w, 0.0, 0.0); f_color=g_color[1]; f_wdist=g_wdist[1]; EmitVertex();
    EndPrimitive();
}
"""

WIREQ_FS = """
#version 330 core
uniform float u_dim_near;   // distance at/under which lines are full white
uniform float u_dim_far;    // distance at which lines reach the grey floor
uniform float u_grey_floor; // minimum brightness (NEVER 0 -> never pure black)
in vec3  f_color;
in float f_wdist;
out vec4 frag_color;
void main() {
    float t = clamp((f_wdist - u_dim_near) / max(u_dim_far - u_dim_near, 1e-3), 0.0, 1.0);
    float bright = mix(1.0, u_grey_floor, t);   // 1.0 near -> grey_floor far
    frag_color = vec4(f_color * bright, 1.0);
}
"""

# ---- CPU-billboard fallback (no GS): vertices already pre-expanded on CPU ----
WIREQ_CPU_VS = """
#version 330 core
uniform mat4 u_mvp;
in vec3 in_pos;
in vec3 in_color;
out vec3 f_color;
out float f_wdist;
void main() {
    vec4 clip = u_mvp * vec4(in_pos, 1.0);
    f_color = in_color;
    f_wdist = clip.w;
    gl_Position = clip;
}
"""
# CPU fallback reuses WIREQ_FS as its fragment shader (same dimming uniforms).

# ---- Bloom: bright extract ----
BRIGHT_FS = """
#version 330 core
uniform sampler2D u_tex;
uniform float u_threshold;   // luminance below this contributes nothing
in vec2 v_uv;
out vec4 frag_color;
void main() {
    vec3 c = texture(u_tex, v_uv).rgb;
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    float k = max(l - u_threshold, 0.0) / max(1.0 - u_threshold, 1e-3);
    frag_color = vec4(c * k, 1.0);
}
"""

# ---- Bloom: separable Gaussian (5-tap, run twice = H then V) ----
BLUR_FS = """
#version 330 core
uniform sampler2D u_tex;
uniform vec2 u_dir;          // (1/w, 0) horizontal  or  (0, 1/h) vertical
in vec2 v_uv;
out vec4 frag_color;
void main() {
    float w0 = 0.227027, w1 = 0.316216, w2 = 0.070270;
    vec3 c = texture(u_tex, v_uv).rgb * w0;
    c += texture(u_tex, v_uv + u_dir * 1.3846).rgb * w1;
    c += texture(u_tex, v_uv - u_dir * 1.3846).rgb * w1;
    c += texture(u_tex, v_uv + u_dir * 3.2308).rgb * w2;
    c += texture(u_tex, v_uv - u_dir * 3.2308).rgb * w2;
    frag_color = vec4(c, 1.0);
}
"""

# ---- Bloom: additive composite (scene + glow) to screen ----
COMPOSITE_FS = """
#version 330 core
uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform float u_bloom_gain;
in vec2 v_uv;
out vec4 frag_color;
void main() {
    vec3 scene = texture(u_scene, v_uv).rgb;
    vec3 bloom = texture(u_bloom, v_uv).rgb;
    frag_color = vec4(scene + bloom * u_bloom_gain, 1.0);
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


# ---- Parent 11: Mode-A quad + bloom program factories (each COMPILES FRESH; caller caches) ----
def wire_quad_program(ctx):
    if not HAVE_GL or ctx is None:
        return None
    return ctx.program(vertex_shader=WIREQ_VS, geometry_shader=WIREQ_GS, fragment_shader=WIREQ_FS)


def wire_quad_cpu_program(ctx):
    if not HAVE_GL or ctx is None:
        return None
    return ctx.program(vertex_shader=WIREQ_CPU_VS, fragment_shader=WIREQ_FS)


def bright_program(ctx):
    if not HAVE_GL or ctx is None:
        return None
    return ctx.program(vertex_shader=BLIT_VS, fragment_shader=BRIGHT_FS)


def blur_program(ctx):
    if not HAVE_GL or ctx is None:
        return None
    return ctx.program(vertex_shader=BLIT_VS, fragment_shader=BLUR_FS)


def composite_program(ctx):
    if not HAVE_GL or ctx is None:
        return None
    return ctx.program(vertex_shader=BLIT_VS, fragment_shader=COMPOSITE_FS)


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
