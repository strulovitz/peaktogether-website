"""GLSL shader sources.

Families: line ribbons (glow layer), bloom pipeline, textured quads
(text/panels), and — per Amendment A1 — the SOLID MESH shader:
per-pixel Blinn-Phong with a warm key light, cool fill light, rim
light and specular highlight. Vertices arrive pre-transformed to
world space; per-vertex color = painted hull panels; per-vertex
emissive = engine nozzles / windows (HDR values > 1 feed bloom).
Two-sided: normals are flipped for back faces, so procedural geometry
never suffers winding bugs.
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
out vec4 f_color;
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
    float spec = pow(max(dot(n, h), 0.0), 44.0) * 0.55;
    float rim = pow(1.0 - max(dot(n, vdir), 0.0), 3.0) * 0.22;

    vec3 albedo = v_color.rgb;
    vec3 c = albedo * (AMBIENT + KEY_COL * dk + FILL_COL * df)
           + KEY_COL * spec + albedo * rim + v_emissive;
    f_color = vec4(c, 1.0);
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
uniform sampler2D u_scene;
uniform sampler2D u_bloom;
uniform float u_strength;
uniform float u_exposure;
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 c = texture(u_scene, v_uv).rgb
           + u_strength * texture(u_bloom, v_uv).rgb;
    c = vec3(1.0) - exp(-c * u_exposure);
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
out vec4 f_color;
void main() {
    float a = texture(u_tex, v_uv).r;
    f_color = vec4(v_color.rgb * a * v_color.a, 1.0);
}
"""
