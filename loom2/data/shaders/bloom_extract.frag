#version 330
// Bright-pass: keep only the energy above u_threshold; feeds the blur passes.
// (LOOM2 panels are LDR single-image, so we threshold here rather than using a
//  separate glow attachment as Homeworld did.)
uniform sampler2D u_tex;
uniform float u_threshold;     // e.g. 0.55 -- tune in renderer.py
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 c = texture(u_tex, v_uv).rgb;
    float l = max(max(c.r, c.g), c.b);
    float k = max(0.0, l - u_threshold) / max(1e-4, l);
    f_color = vec4(c * k, 1.0);
}
