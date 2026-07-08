#version 330
// LOOM2 totem.frag -- owned by graphics/totem.py (Child D).
// Gouraud-lit emissive: breathing HDR gold (u_color, may exceed 1.0 for
// bloom) modulated by smoothly interpolated per-vertex light.
uniform vec4 u_color;
in float v_light;
out vec4 f_color;
void main() {
    f_color = vec4(u_color.rgb * v_light, u_color.a);
}
