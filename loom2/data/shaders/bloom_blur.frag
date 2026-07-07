#version 330
// Separable 9-tap Gaussian (proven verbatim from Homeworld: A Good Basis).
// Call twice: u_dir = (1/width, 0) horizontal, then (0, 1/height) vertical.
uniform sampler2D u_tex;
uniform vec2 u_dir;
in vec2 v_uv;
out vec4 f_color;
void main() {
    const float w[5] = float[5](
        0.2270270270, 0.1945945946, 0.1216216216, 0.0540540541, 0.0162162162
    );
    vec3 c = texture(u_tex, v_uv).rgb * w[0];
    for (int i = 1; i < 5; i++) {
        c += texture(u_tex, v_uv + u_dir * float(i)).rgb * w[i];
        c += texture(u_tex, v_uv - u_dir * float(i)).rgb * w[i];
    }
    f_color = vec4(c, 1.0);
}
