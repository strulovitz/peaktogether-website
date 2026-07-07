#version 330
uniform mat4 u_vp;
uniform float u_aspect;
in vec2 in_corner; in vec2 in_uv;
in vec3 in_center; in float in_size; in float in_icon;
in float in_alpha; in float in_glow;
out vec2 v_uv; out float v_alpha; out float v_glow;
void main() {
    vec4 clip = u_vp * vec4(in_center, 1.0);
    float s = in_size * (1.0 + 0.3 * in_glow);     // flash scale ~1.3x
    clip.xy += in_corner * vec2(s, s * u_aspect);  // divide by w => far=small
    gl_Position = clip;
    float col = mod(in_icon, 4.0), row = floor(in_icon / 4.0);
    v_uv = (in_uv + vec2(col, row)) * 0.25;
    v_alpha = in_alpha; v_glow = in_glow;
}
