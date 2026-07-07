#version 330
uniform sampler2D u_atlas;
in vec2 v_uv; in float v_alpha; in float v_glow;
out vec4 f_color;
void main() {
    vec4 c = texture(u_atlas, v_uv);
    c.rgb *= (1.0 + 2.0 * v_glow);                 // emissive: feeds bloom
    c.a *= v_alpha;
    if (c.a < 0.01) discard;
    f_color = c;
}
