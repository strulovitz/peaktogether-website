#version 330
// modes: 0 pane (unlit A1/B1 tint) | 1 Fresnel rim (F4) | 2 ribbon solid (C1)
//        3 ribbon dashed (occluded pass) | 4 bead (Gouraud x breath)
//        5 bead ghost (occluded pass)
uniform int   u_mode;
uniform vec4  u_color;
uniform vec3  u_cam_pos;
uniform vec3  u_normal;
uniform float u_dash;
in vec3 v_world;
in vec2 v_aux;
out vec4 f_color;
void main() {
    if (u_mode == 1) {
        vec3  v  = normalize(u_cam_pos - v_world);
        float fr = pow(1.0 - abs(dot(v, normalize(u_normal))), 3.0);
        f_color = vec4(u_color.rgb * (0.25 + 0.75 * fr),
                       u_color.a * (0.30 + 0.70 * fr));
    } else if (u_mode == 3) {
        if (fract(v_aux.x / u_dash) > 0.5) discard;   // dashed where hidden
        f_color = u_color;
    } else if (u_mode >= 4) {
        f_color = vec4(u_color.rgb * v_aux.y, u_color.a);
    } else {
        f_color = u_color;                            // 0 pane, 2 ribbon
    }
}
