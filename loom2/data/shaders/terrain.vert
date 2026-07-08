#version 330
// LOOM2 terrain.vert -- owned by graphics/terrain.py (Child D).
// Gouraud: in_light is per-vertex Lambert lighting, interpolated by the GPU.
// v_z carries world height to the fragment stage for pixel-sharp hard bands.
uniform mat4 u_mvp;
in vec3 in_pos;
in float in_light;
out float v_light;
out float v_z;
void main() {
    v_light = in_light;
    v_z = in_pos.z;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
