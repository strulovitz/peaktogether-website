#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
void main() { gl_Position = u_mvp * vec4(in_pos, 1.0); }
