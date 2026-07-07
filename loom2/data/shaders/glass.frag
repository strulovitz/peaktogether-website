#version 330
// PLACEHOLDER -- graphics/slice_mode.py (Parent E) owns the real glass GLSL.
uniform vec4 u_color;    // expects an alpha < 1 for the semi-transparent pane
out vec4 f_color;
void main() { f_color = u_color; }
