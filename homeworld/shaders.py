"""GLSL shader sources.

Amendment A1.1 (owner): ships must NEVER bloom. The scene renders to
TWO color attachments:
    location 0 — SOLID buffer: lit ships, linear, untouched by bloom
                 or tone mapping (crisp panel detail).
    location 1 — GLOW buffer: holograms (lines, labels, panels),
                 additive; this buffer alone is blurred and tone
                 mapped, then added on top of the solid buffer.
Line/text shaders write 0 to the solid buffer (additive +0 = no-op);
the mesh shader writes 0 to the glow buffer.
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
layout(location = 0) out vec4 f_solid;
layout(location = 1) out vec4 f_glow;
void main() {
    float k = 1.0 - v_u * v_u;
    f_solid = vec4(0.0);
    f_glow = vec4(v_color.rgb * k * k * v_color.a, 1.0);
}
"""

MESH_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec3 in_normal;
in vec4 in_color;
in vec3 in_emissive;
out vec3 v_pos;
out vec3 v_normal;
out vec4 v_color;
out vec3 v_emissive;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_pos = in_pos;
    v_normal = in_normal;
    v_color = in_color;
    v_emissive = in_emissive;
}
"""

MESH_FRAG = """
#version 330
uniform vec3 u_eye;
in vec3 v_pos;
in vec3 v_normal;
in vec4 v_color;
in vec3 v_emissive;
layout(location = 0) out vec4 f_solid;
layout(location = 1) out vec4 f_glow;
void main() {
    vec3 KEY_DIR  = vec3(0.4581, 0.8144, 0.3563);
    vec3 KEY_COL  = vec3(1.05, 1.00, 0.92);
    vec3 FILL_DIR = vec3(-0.5582, -0.2791, -0.7814);
    vec3 FILL_COL = vec3(0.22, 0.30, 0.45);
    vec3 AMBIENT  = vec3(0.15, 0.17, 0.21);

    vec3 n = normalize(v_normal);
    if (!gl_FrontFacing) n = -n;
    vec3 vdir = normalize(u_eye - v_pos);

    float dk = max(dot(n, KEY_DIR), 0.0);
    float df = max(dot(n, FILL_DIR), 0.0);
    vec3 h = normalize(KEY_DIR + vdir);
    float spec = pow(max(dot(n, h), 0.0), 44.0) * 0.45;
    float rim = pow(1.0 - max(dot(n, vdir), 0.0), 3.0) * 0.18;

    vec3 albedo = v_color.rgb;
    vec3 c = albedo * (AMBIENT + KEY_COL * dk + FILL_COL * df)
           + KEY_COL * spec + albedo * rim + v_emissive;
    f_solid = vec4(c, 1.0);
    f_glow = vec4(0.0);
}
"""

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
uniform sampler2D u_scene;   // solid ships, linear — passed through
uniform sampler2D u_glow;    // hologram layer, full resolution
uniform sampler2D u_bloom;   // blurred hologram layer
uniform float u_strength;
uniform float u_exposure;
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 g = texture(u_glow, v_uv).rgb
           + u_strength * texture(u_bloom, v_uv).rgb;
    g = vec3(1.0) - exp(-g * u_exposure);   // tone map holograms ONLY
    vec3 c = texture(u_scene, v_uv).rgb + g;
    f_color = vec4(c, 1.0);
}
"""

TEXT_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec2 in_uv;
in vec4 in_color;
out vec2 v_uv;
out vec4 v_color;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_uv = in_uv;
    v_color = in_color;
}
"""

TEXT_FRAG = """
#version 330
uniform sampler2D u_tex;
in vec2 v_uv;
in vec4 v_color;
layout(location = 0) out vec4 f_solid;
layout(location = 1) out vec4 f_glow;
void main() {
    float a = texture(u_tex, v_uv).r;
    f_solid = vec4(0.0);
    f_glow = vec4(v_color.rgb * a * v_color.a, 1.0);
}
"""
