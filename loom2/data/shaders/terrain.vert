#version 330
// PLACEHOLDER -- graphics/terrain.py (Parent D) owns the real terrain GLSL.
// Compilable stand-in so Renderer can load every REQUIRED_SHADERS stem during
// integration. Replace wholesale when Parent D delivers.
uniform mat4 u_mvp;
in vec3 in_pos;
in vec3 in_color;
out vec3 v_color;
void main() {
    v_color = in_color;
    gl_Position = u_mvp * vec4(in_pos, 1.0);
}
