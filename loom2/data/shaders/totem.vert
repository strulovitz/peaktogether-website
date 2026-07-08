#version 330
// LOOM2 totem.vert -- owned by graphics/totem.py (Child D). NEW ninth stem,
// added with Nir's blessing (Gouraud iron rule; 'flat' cannot shade).
// in_light = per-vertex Lambert baked from the ribbon's analytic normals
// (exact: the totem only translates, never rotates).
uniform mat4 u_mvp;
in vec3 in_pos;
in float in_light;
out float v_light;
void main() {
    v_light = in_light;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
