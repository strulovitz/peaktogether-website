"""GLSL shader sources (NEW_TESTAMENT 1.6).

The line ribbon shader: each line is expanded on the CPU into a
camera-facing ribbon with a 'ribbon coordinate' u in [-1, 1] across
its width. The fragment shader shades intensity = (1 - u^2)^2 so
every line has a hot bright core and soft edges even before bloom.
"""

LINE_VERT = """
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
in vec4 in_color;
in float in_u;
out vec4 v_color;
out float v_u;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_color = in_color;
    v_u = in_u;
}
"""

LINE_FRAG = """
#version 330
in vec4 v_color;
in float v_u;
out vec4 f_color;
void main() {
    float k = 1.0 - v_u * v_u;
    f_color = vec4(v_color.rgb * k * k * v_color.a, 1.0);
}
"""
