#version 330
// PLACEHOLDER -- graphics/slice_mode.py (Parent E) owns the real glass GLSL.
// Compilable stand-in so Renderer can load every REQUIRED_SHADERS stem during
// integration. Replace wholesale when Parent E delivers.
uniform mat4 u_mvp;
in vec3 in_pos;
void main() { gl_Position = u_mvp * vec4(in_pos, 1.0); }
