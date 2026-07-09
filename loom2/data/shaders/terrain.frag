#version 330
// LOOM2 terrain.frag -- owned by graphics/terrain.py (Child D).
// Hard hypsometric bands: color chosen per fragment from interpolated world
// height, so band edges are exact level curves. Gouraud light multiplies.
uniform vec3 u_band_colors[6];
uniform float u_band_edges[5];
uniform float u_fog;           // 0.0 = clear, 1.0 = fog finale (Scene 13)
in float v_light;
in float v_z;
out vec4 f_color;
void main() {
    vec3 c = u_band_colors[0];
    for (int i = 0; i < 5; i++) {
        if (v_z >= u_band_edges[i]) {
            c = u_band_colors[i + 1];
        }
    }
    f_color = vec4(c * v_light * mix(1.0, 0.10, u_fog), 1.0);
}
