#version 330
// Final add: untouched scene + blurred bloom. Adapted from Homeworld's
// COMPOSITE_FRAG (the hologram tone-map is left optional/off here since LOOM2
// panels are LDR; enable it in renderer.py by feeding u_exposure > 0).
uniform sampler2D u_scene;     // the panel image, passed through
uniform sampler2D u_bloom;     // blurred bright-pass
uniform float u_strength;      // bloom add strength, e.g. 0.85
uniform float u_exposure;      // 0.0 = plain add; >0 = exp tone-map the sum
in vec2 v_uv;
out vec4 f_color;
void main() {
    vec3 scene = texture(u_scene, v_uv).rgb;
    vec3 bloom = u_strength * texture(u_bloom, v_uv).rgb;
    vec3 c = scene + bloom;
    if (u_exposure > 0.0) {
        c = vec3(1.0) - exp(-c * u_exposure);
    }
    f_color = vec4(c, 1.0);
}
