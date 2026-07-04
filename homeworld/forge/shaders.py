"""GLSL shader sources (NEW_TESTAMENT 1.5 and 1.6).

Two families:

1. The line ribbon shader: each line is expanded on the CPU into a
   camera-facing ribbon with a 'ribbon coordinate' u in [-1, 1] across
   its width. The fragment shader shades intensity = (1 - u^2)^2 so
   every line has a hot bright core and soft edges even before bloom.

2. The bloom pipeline shaders: a fullscreen triangle generated from
   gl_VertexID (no vertex buffer needed), a plain blit (downsample),
   a separable 9-tap Gaussian blur, and the final composite with a
   soft exposure tone map (refinement of NT 1.6's soft tone map:
   c -> 1 - exp(-c * exposure) keeps hot cores white while lifting
   the faint halos, which suits an emissive-on-black world).
"""

LINE_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec4 in_color;
in float in_u;
out vec4 v_color;
out float v_u;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_color = in_color;
    v_u = in_u;
}
"""

LINE_FRAG = """
#version 330
in vec4 v_color;
in float v_u;
out vec4 f_color;
void main() {
    float k = 1.0 - v_u * v_u;
    f_color = vec4(v_color.rgb * k * k * v_color.a, 1.0);
}
"""

# Fullscreen triangle from gl_VertexID: covers the screen with 3 vertices,
# uv spans [0,1] over the visible area. No vertex buffer required.
FULLSCREEN_VERT = """
#version 330
out vec2 v_uv;
void main() {
    vec2 pos = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
    v_uv = pos;
    gl_Position = vec4(pos * 2.0 - 1.0, 0.0, 1.0);
}
"""

BLIT_FRAG = """
#version 330
uniform sampler2D u_tex;
in vec2 v_uv;
out vec4 f_color;
void main() {
    f_color = vec4(texture(u_tex, v_uv).rgb, 1.0);
}
"""

# Separable Gaussian, 9 effective taps, sigma ~= 2.0 (weights sum to 1).
# Run twice: once with u_dir = (1/w, 0), once with u_dir = (0, 1/h).
BLUR_FRAG = """
#version 330
uniform sampler2D u_tex;
uniform vec2 u_dir;
in vec2 v_uv;
out vec4 f_color;
void main() {
    const float w[5] = float[5](
        0.2270270270, 0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
    );
    vec3 c = texture(u_tex, v_uv).rgb * w[0];
    for (int i = 1; i < 5; i++) {
        c += texture(u_tex, v_uv + u_dir * float(i)).rgb * w[i];
        c += texture(u_tex, v_uv - u_dir * float(i)).rgb * w[i];
    }
    f_color = vec4(c, 1.0);
}
"""

COMPOSITE_FRAG = """
#version 330
uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform float u_strength;
uniform float u_exposure;
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 c = texture(u_scene, v_uv).rgb
           + u_strength * texture(u_bloom, v_uv).rgb;
    c = vec3(1.0) - exp(-c * u_exposure);   // soft tone map
    f_color = vec4(c, 1.0);
}
"""
