#version 330
// LOOM2 glass shader -- owned by graphics/slice_mode.py (Parent E)
uniform mat4 u_mvp;
in vec3 in_pos;
in vec2 in_aux;   // x = arc length along the curve, y = baked Gouraud light
out vec3 v_world;
out vec2 v_aux;
void main() {
    v_world = in_pos;
    v_aux = in_aux;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
