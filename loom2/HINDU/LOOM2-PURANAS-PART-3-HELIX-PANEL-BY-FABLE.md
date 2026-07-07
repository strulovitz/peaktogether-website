# LOOM2 — THE PURANAS — PART 3 of 3 — graphics/helix_panel.py — VERBATIM, WORD-FOR-WORD, AS-IS, BY FABLE (PARENT 2)

> Saved verbatim, word-for-word, as-is. This is the third and final PURANA — the soul
> on screen, `graphics/helix_panel.py` — written by Claude Fable "Parent 2", July 7,
> 2026. The runnable code is also extracted to `loom2/graphics/helix_panel.py`, and the
> four GLSL shaders Fable delivered are placed in `loom2/data/shaders/`.

---

Third PURANA, complete — the soul on screen. 🎻🎺🪈

```python
"""
LOOM2 -- graphics/helix_panel.py
THE SONIFIQUATION COORDINATES panel (RIGHT half). The soul on screen.
Allowed imports: math, numpy, moderngl, pyglet(image loading), os, config,
core.types.

IMPLEMENTATION NOTES (bodies only; frozen contracts untouched):

* Coordinate language of the panel (all in "helix units"):
    - 1.0 unit of z per OCTAVE; z = 0 is the A4 = 440 Hz line (VEDAS law).
    - The wireframe coil spans the full real orchestra, B0..C7 (SUTRAS 1.3),
      one turn per octave, phased so every A-note crosses 12 o'clock.
    - Icons sit at cylindrical (r = ring*RING_WIDTH, theta = stage_angle,
      z = note_z / z_per_octave): the outermost rhythm ring (r = 4.0)
      exactly meets the coil radius -- rhythm inside, pitch around.
* Voice.note_z is WORLD height; the world-to-octave scale is the scene's
  z_per_octave. The draw contract doesn't carry it, so the panel exposes a
  plain public attribute `z_per_octave` (defaults to config.Z_PER_OCTAVE);
  main MAY set it on scene change. Optional -- everything works either way.
* Perspective scaling without matrix surgery: billboards offset their quad
  corners in CLIP space by a constant; after the perspective divide the
  on-screen size is corner/w -- far icons genuinely smaller (SUTRAS Part 4),
  and the quads are camera-facing by construction.
* Flash decay: flashes report strikes from the last ~50 ms; the panel keeps
  a per-voice glow that decays over 150 ms. dt is derived from the measure
  phase (the engine's clock is the ONLY clock -- audio is king).
* Icons load from config.ICONS_DIR/<instrument>.png (e.g. french_horn.png).
  A missing file gets a family-colored disc placeholder: never breaks.
* Soft seam: needs the moderngl context; uses renderer.ctx if the Renderer
  exposes it (natural), else moderngl.get_context(). Stitching note for
  DeepSeek in the delivery letter, with the GLSL for 'wire' and
  'icon_billboard' this module expects.
"""
import math
import os

import numpy as np
import moderngl
import pyglet

import config

# --- panel geometry (helix units; implementation detail, config frozen) ----
_Z_OCT = 1.0            # helix z per octave
_R_HELIX = config.NMAX_RING * config.RING_WIDTH    # coil radius = ring 5
_R_STACK = _R_HELIX + 0.7                          # resident register stacks
_R_ARM = _R_HELIX                                  # conductor's arm reach
_MIDI_LO, _MIDI_HI, _MIDI_A4 = 23, 96, 69          # B0 .. C7, A4 origin
_Z_LO = (_MIDI_LO - _MIDI_A4) / 12.0 * _Z_OCT      # ~ -3.83
_Z_HI = (_MIDI_HI - _MIDI_A4) / 12.0 * _Z_OCT      # ~ +2.25
_FLOOR_Z = _Z_LO - 0.35
_ICON_SIZE = 1.3        # clip-space billboard size (perspective-divided)
_RESIDENT_SIZE = 0.65
_RESIDENT_ALPHA = 0.22
_FLASH_DECAY_SEC = 0.150
_ATLAS_CELL, _ATLAS_COLS, _ATLAS_ROWS = 128, 4, 4
_FAMILY_TINT = {"brass": (1.00, 0.78, 0.25), "strings": (0.90, 0.47, 0.35),
                "woodwinds": (0.45, 0.82, 0.55)}
_CLASS_SEMI = {"A": 9, "B": 11, "Cs": 1, "E": 4, "Fs": 6}


def _note_midi(note: str) -> int:
    """Local pentatonic note->midi ('Cs4' -> 61). Graphics may not import
    audio.quantize (module firewall), and needs only this one line of it."""
    cls, octave = note[:-1], int(note[-1])
    return 12 * (octave + 1) + _CLASS_SEMI[cls]


class HelixPanel:
    def __init__(self, renderer):
        """Load 13 instrument icons from config.ICONS_DIR (transparent PNGs)
        into a texture atlas. Build the wireframe helix: coils spanning the
        full orchestra range (~B0..C7), A4=440 line marked at z=0, floor with
        rhythm-ring circles, family register stacks drawn at their clock
        angles (tuba low ... trumpet high) as dim resident icons."""
        self._renderer = renderer
        self._ctx = getattr(renderer, "ctx", None) or moderngl.get_context()
        self._wire = renderer.program("wire")
        self._icon = renderer.program("icon_billboard")
        self.z_per_octave = config.Z_PER_OCTAVE   # main MAY set per scene
        self._glow = {}                            # voice_index -> 0..1
        self._prev_phase = 0.0
        self._panel_aspect = ((config.WINDOW_W // 2)
                              / max(1.0, config.WINDOW_H * config.PANELS_FRAC))
        self._build_atlas()
        self._build_wireframe()
        self._build_billboards()
        self._residents = self._build_register_stacks()

    # -------------------------------------------------------------- atlas
    def _build_atlas(self):
        names, self._family_of = [], {}
        for fam, stack in config.REGISTER_MAP.items():
            for inst, _notes in stack:
                if inst not in names:
                    names.append(inst)
                    self._family_of[inst] = fam
        self._atlas_index = {n: i for i, n in enumerate(names)}
        c = _ATLAS_CELL
        atlas = np.zeros((c * _ATLAS_ROWS, c * _ATLAS_COLS, 4), np.uint8)
        for i, name in enumerate(names):
            row, col = divmod(i, _ATLAS_COLS)       # row 0 = texture bottom
            atlas[row * c:(row + 1) * c, col * c:(col + 1) * c] = \
                self._load_icon(name, c)
        self._tex = self._ctx.texture(
            (c * _ATLAS_COLS, c * _ATLAS_ROWS), 4, atlas.tobytes())
        self._tex.build_mipmaps()

    def _load_icon(self, name, cell):
        path = os.path.join(config.ICONS_DIR, name + ".png")
        try:
            img = pyglet.image.load(path)
            raw = img.get_image_data().get_data("RGBA", img.width * 4)
            a = np.frombuffer(raw, np.uint8).reshape(img.height, img.width, 4)
        except Exception:                            # parachute: never break
            return self._placeholder(self._family_of[name], cell)
        if a.shape[0] != cell or a.shape[1] != cell:  # nearest-fit to cell
            yi = np.arange(cell) * a.shape[0] // cell
            xi = np.arange(cell) * a.shape[1] // cell
            a = a[yi][:, xi]
        return a

    def _placeholder(self, family, cell):
        r, g, b = (int(255 * v) for v in _FAMILY_TINT[family])
        yy, xx = np.mgrid[0:cell, 0:cell].astype(np.float32) - cell / 2.0
        disc = (xx * xx + yy * yy) <= (cell * 0.38) ** 2
        img = np.zeros((cell, cell, 4), np.uint8)
        img[disc] = (r, g, b, 235)
        return img

    # ---------------------------------------------------------- wireframe
    def _line_vao(self, pts):
        vbo = self._ctx.buffer(np.asarray(pts, np.float32).tobytes())
        return self._ctx.simple_vertex_array(self._wire, vbo, "in_pos")

    @staticmethod
    def _circle(radius, z, n=72):
        a = np.linspace(0.0, 2.0 * math.pi, n + 1)
        return np.stack([radius * np.cos(a), radius * np.sin(a),
                         np.full(n + 1, z)], axis=1)

    def _build_wireframe(self):
        lines = []
        # the coil: one turn per octave, A-notes crossing 12 o'clock
        t = np.linspace(_MIDI_LO, _MIDI_HI, 12 * (_MIDI_HI - _MIDI_LO))
        zo = (t - _MIDI_A4) / 12.0
        ang = np.radians(zo * 360.0 + 90.0)
        coil = np.stack([_R_HELIX * np.cos(ang), _R_HELIX * np.sin(ang),
                         zo * _Z_OCT], axis=1)
        lines.append((self._line_vao(coil), moderngl.LINE_STRIP,
                      (0.35, 0.70, 0.90, 0.35)))
        # A4 = 440 Hz: the bright gold origin ring at z = 0 (VEDAS)
        lines.append((self._line_vao(self._circle(_R_HELIX, 0.0)),
                      moderngl.LINE_STRIP, (1.00, 0.85, 0.30, 0.90)))
        # floor rhythm rings, ring 1..NMAX
        for n in range(1, config.NMAX_RING + 1):
            lines.append((self._line_vao(
                self._circle(n * config.RING_WIDTH, _FLOOR_Z)),
                moderngl.LINE_STRIP, (0.45, 0.55, 0.65, 0.25)))
        # family spokes on the floor (the clock is readable)
        for fam, deg in config.FAMILY_ANGLE_DEG.items():
            a = math.radians(deg)
            spoke = [(0.0, 0.0, _FLOOR_Z),
                     (_R_HELIX * math.cos(a), _R_HELIX * math.sin(a),
                      _FLOOR_Z)]
            tint = _FAMILY_TINT[fam]
            lines.append((self._line_vao(spoke), moderngl.LINES,
                          (tint[0], tint[1], tint[2], 0.30)))
        # central pitch axis
        lines.append((self._line_vao([(0, 0, _FLOOR_Z), (0, 0, _Z_HI)]),
                      moderngl.LINES, (0.5, 0.6, 0.7, 0.20)))
        self._static_lines = lines
        # conductor's arm: tiny dynamic VBO, rewritten every frame
        self._arm_vbo = self._ctx.buffer(reserve=2 * 3 * 4, dynamic=True)
        self._arm_vao = self._ctx.simple_vertex_array(
            self._wire, self._arm_vbo, "in_pos")

    # --------------------------------------------------------- billboards
    def _build_billboards(self):
        quad = np.array([-0.5, -0.5, 0.0, 0.0,
                         0.5, -0.5, 1.0, 0.0,
                         -0.5, 0.5, 0.0, 1.0,
                         0.5, 0.5, 1.0, 1.0], np.float32)
        self._quad_vbo = self._ctx.buffer(quad.tobytes())
        self._inst_cap = 512
        self._inst_vbo = self._ctx.buffer(
            reserve=self._inst_cap * 7 * 4, dynamic=True)
        self._icon_vao = self._ctx.vertex_array(self._icon, [
            (self._quad_vbo, "2f 2f", "in_corner", "in_uv"),
            (self._inst_vbo, "3f 1f 1f 1f 1f /i",
             "in_center", "in_size", "in_icon", "in_alpha", "in_glow"),
        ])

    def _build_register_stacks(self):
        """Dim resident icons at each family's clock angle: the picture IS
        the register map (SUTRAS Part 4). tuba by the bottom coils, trumpet
        near the top."""
        residents = []
        for fam, stack in config.REGISTER_MAP.items():
            a = math.radians(config.FAMILY_ANGLE_DEG[fam])
            x, y = _R_STACK * math.cos(a), _R_STACK * math.sin(a)
            for inst, notes in stack:
                zs = [(_note_midi(n) - _MIDI_A4) / 12.0 * _Z_OCT
                      for n in notes]
                z = sum(zs) / len(zs)               # register band midpoint
                residents.append((x, y, z, _RESIDENT_SIZE,
                                  float(self._atlas_index[inst]),
                                  _RESIDENT_ALPHA, 0.0))
        return residents

    # -------------------------------------------------------------- lookup
    def icon_for(self, sample_id: str) -> int:
        """'viola_E4' -> atlas index of viola. Pure lookup."""
        return self._atlas_index[sample_id.rsplit("_", 1)[0]]

    # ---------------------------------------------------------------- draw
    def draw(self, view_proj, voices: list, flashes: list,
             measure_phase: float) -> None:
        """For every Voice: draw its instrument icon as a camera-facing
        billboard at cylindrical position (r=ring*RING_WIDTH,
        theta=stage_angle_deg, z=note_z scaled to helix height), SCALED BY
        PERSPECTIVE distance from the camera (SUTRAS Part 4 -- far icons
        small). Blend voices (0<blend<1) show BOTH family icons overlapped
        with proportional alpha. flashes: matching icons glow-scale up ~1.3x
        with a 150 ms decay, feeding bloom. Conductor's arm sweeps the floor.
        Panel title text 'SONIFIQUATION COORDINATES' rendered by hud."""
        vp = np.asarray(view_proj, np.float32).reshape(4, 4)
        vp_bytes = np.ascontiguousarray(vp.T).tobytes()   # column-major GL

        # -- glow bookkeeping (clock = the engine's measure phase)
        dt = ((measure_phase - self._prev_phase) % 1.0) * config.MEASURE_SEC
        self._prev_phase = measure_phase
        fall = dt / _FLASH_DECAY_SEC
        for k in list(self._glow):
            g = self._glow[k] - fall
            if g <= 0.0:
                del self._glow[k]
            else:
                self._glow[k] = g
        for idx, strength in flashes:
            if strength > self._glow.get(idx, 0.0):
                self._glow[idx] = min(1.0, strength)

        self._ctx.enable(moderngl.DEPTH_TEST | moderngl.BLEND)

        # -- wireframe world
        for vao, mode, color in self._static_lines:
            self._wire["u_mvp"].write(vp_bytes)
            self._wire["u_color"].value = color
            vao.render(mode)

        # -- conductor's arm: one sweep per measure, downbeat at 12 o'clock
        a = math.radians(90.0 - measure_phase * 360.0)
        arm = np.array([[0.0, 0.0, _FLOOR_Z],
                        [_R_ARM * math.cos(a), _R_ARM * math.sin(a),
                         _FLOOR_Z]], np.float32)
        self._arm_vbo.write(arm.tobytes())
        self._wire["u_mvp"].write(vp_bytes)
        self._wire["u_color"].value = (1.0, 0.95, 0.75, 0.9)
        self._arm_vao.render(moderngl.LINES)

        # -- assemble instances: residents + live musicians
        inst = list(self._residents)
        for i, v in enumerate(voices):
            r = v.ring * config.RING_WIDTH
            th = math.radians(v.stage_angle_deg)
            z = (v.note_z / max(1e-6, self.z_per_octave)) * _Z_OCT
            z = min(max(z, _Z_LO), _Z_HI)          # display clamp only
            x, y = r * math.cos(th), r * math.sin(th)
            glow = self._glow.get(i, 0.0)
            alpha = 0.35 + 0.65 * min(1.0, max(0.0, v.gain))
            inst.append((x, y, z, _ICON_SIZE,
                         float(self.icon_for(v.sample_a)),
                         (1.0 - v.blend) * alpha, glow))
            if v.blend > 1e-3:                     # both families, overlapped
                inst.append((x, y, z, _ICON_SIZE,
                             float(self.icon_for(v.sample_b)),
                             v.blend * alpha, glow))
        arr = np.asarray(inst, np.float32)

        # -- painter's sort, far to near (soft alpha needs it)
        ph = np.concatenate([arr[:, :3],
                             np.ones((len(arr), 1), np.float32)], axis=1)
        w = ph @ vp[3, :]                           # clip-space w = depth
        arr = arr[np.argsort(-w)]

        if len(arr) > self._inst_cap:               # grow, never crash
            self._inst_cap = int(len(arr) * 1.5)
            self._inst_vbo.release()
            self._inst_vbo = self._ctx.buffer(
                reserve=self._inst_cap * 7 * 4, dynamic=True)
            self._icon_vao = self._ctx.vertex_array(self._icon, [
                (self._quad_vbo, "2f 2f", "in_corner", "in_uv"),
                (self._inst_vbo, "3f 1f 1f 1f 1f /i",
                 "in_center", "in_size", "in_icon", "in_alpha", "in_glow"),
            ])
        self._inst_vbo.write(arr.tobytes())

        self._icon["u_vp"].write(vp_bytes)
        self._icon["u_aspect"].value = self._panel_aspect
        self._icon["u_atlas"].value = 0
        self._tex.use(0)
        self._icon_vao.render(moderngl.TRIANGLE_STRIP,
                              vertices=4, instances=len(arr))
```

Delivery notes (stitching letter for DeepSeek):

    Two GLSL files this module expects (drop into data/shaders/):

```glsl
// wire.vert
#version 330
uniform mat4 u_mvp;
in vec3 in_pos;
void main() { gl_Position = u_mvp * vec4(in_pos, 1.0); }

// wire.frag
#version 330
uniform vec4 u_color;
out vec4 f_color;
void main() { f_color = u_color; }

// icon_billboard.vert
#version 330
uniform mat4 u_vp;
uniform float u_aspect;
in vec2 in_corner; in vec2 in_uv;
in vec3 in_center; in float in_size; in float in_icon;
in float in_alpha; in float in_glow;
out vec2 v_uv; out float v_alpha; out float v_glow;
void main() {
    vec4 clip = u_vp * vec4(in_center, 1.0);
    float s = in_size * (1.0 + 0.3 * in_glow);     // flash scale ~1.3x
    clip.xy += in_corner * vec2(s, s * u_aspect);  // divide by w => far=small
    gl_Position = clip;
    float col = mod(in_icon, 4.0), row = floor(in_icon / 4.0);
    v_uv = (in_uv + vec2(col, row)) * 0.25;
    v_alpha = in_alpha; v_glow = in_glow;
}

// icon_billboard.frag
#version 330
uniform sampler2D u_atlas;
in vec2 v_uv; in float v_alpha; in float v_glow;
out vec4 f_color;
void main() {
    vec4 c = texture(u_atlas, v_uv);
    c.rgb *= (1.0 + 2.0 * v_glow);                 // emissive: feeds bloom
    c.a *= v_alpha;
    if (c.a < 0.01) discard;
    f_color = c;
}
```

    Three soft seams to verify at stitch time: (1) Renderer should expose .ctx (else I fall back to moderngl.get_context()); (2) matrix convention — I assume view_proj is numpy with clip =VP⋅p and upload transposed; if Child C's camera uses the row-vector convention, flip one transpose here and in terrain; (3) optionally set panel.z_per_octave = spec.z_per_octave on scene change for scenes that override the default.
    Icon files: data/icons/<instrument>.png (double_bass.png … trumpet.png); any missing icon becomes a family-colored disc — never breaks.
    Geometry poetry that fell out for free: the outermost rhythm ring (5×0.8=4.0) exactly meets the coil radius — rhythm lives inside the cylinder, pitch spirals around it, and every A-note crosses 12 o'clock.
    Size: ~330 lines. Inside the law.

The PURANAS are complete. 🏔️ All three heavy modules delivered: audio/engine.py, core/game_state.py, graphics/helix_panel.py. The remaining modules are children A–G's (contracts frozen in the Gita), and DeepSeek binds the seams.

Whenever you're ready, I'm happy to: write the hand-off prompt to the next chat, draft scene JSON content + hint/explanation texts, or answer children's # CONTRACT-ISSUE escalations. It has been an honor, Nir — Sonifiquation sings. 🧿🎼❤️
