THANK YOU, Nir — and thank you, DeepSeek, for the green board and the clock/pan verification (+0.39 above center = 12 o'clock — the sacred seam breathes). 🧿

Here is file 2 of 2: graphics/renderer.py — complete, ready for verbatim save.

"""
LOOM2 -- graphics/renderer.py
The moderngl foundation: context, shader loading, framebuffers, bloom.
Reuses the proven pipeline style of Quake: Principia / Homeworld: A Good Basis
(bloom/composite GLSL pasted by DeepSeek into data/shaders/, 2026-07-07).
Allowed imports: moderngl, pyglet, numpy, os, config. NO game logic.

Implemented by Parent C (Claude Fable 5), July 7, 2026.

PIPELINE (per panel, inside composite()):
  scene (HDR f2, full panel res)
    -> bloom_extract  (bright-pass, sampled DOWN into quarter-res buffer A)
    -> bloom_blur H   (A -> B, u_dir = (1/qw, 0))
    -> bloom_blur V   (B -> A, u_dir = (0, 1/qh))
    -> composite      (u_scene + u_bloom, additive, to this panel's screen
                       region -- left half or right half, above the quiz bar)
  All bloom passes use the fullscreen-triangle-from-gl_VertexID trick:
  vertex_array(program, []) rendered with mode=TRIANGLES, vertices=3.

NOTES:
  * The 50/50 split (SUTRAS 2.1) is enforced HERE and nowhere else:
    each panel framebuffer is (WINDOW_W // 2, int(WINDOW_H * PANELS_FRAC)).
  * Panel color buffers are RGBA16F ('f2'): emissive materials may exceed
    1.0 and bloom naturally; the composite shader's u_exposure expects HDR.
  * composite() first clears the WHOLE screen to black, so the top strip
    and quiz bar regions are guaranteed untouched black for hud to draw on.
  * self.ctx is PUBLIC on purpose: helix_panel (and siblings) create their
    buffers/VAOs through renderer.ctx -- the one shared GL context.
  * Fail-loud policy confirmed safe by DeepSeek: all 8 REQUIRED_SHADERS
    stems exist in data/shaders/ (terrain/glass as placeholders that
    Parents D/E overwrite wholesale).
"""
import os
import moderngl
import config

REQUIRED_SHADERS = ("terrain", "wire", "flat", "icon_billboard",
                    "glass", "bloom_extract", "bloom_blur", "composite")

# ---------- tunables (DeepSeek: "yours to adjust" -- tweak freely) ----------
BLOOM_THRESHOLD = 0.80    # bright-pass cutoff (HDR: emissives sail past it)
BLOOM_STRENGTH = 0.85     # bloom mix into the composite
BLOOM_EXPOSURE = 1.00     # composite exposure
_BLOOM_DOWNSCALE = 4      # quarter-res bloom buffers (soft, cheap glow)
_CLEAR_COLOR = (0.010, 0.010, 0.022)   # near-black space blue, demoscene night

# ---------- panel geometry (the 50/50 split lives here ONLY) ----------
_PANEL_W = config.WINDOW_W // 2
_PANEL_H = int(config.WINDOW_H * config.PANELS_FRAC)
_PANEL_Y0 = int(config.WINDOW_H * config.QUIZ_BAR_FRAC)   # panels sit on the quiz bar
_FULL_VIEWPORT = (0, 0, config.WINDOW_W, config.WINDOW_H)


class Renderer:
    def __init__(self, window):            # pyglet window, already created
        """Create moderngl context; load all shaders from config.SHADERS_DIR;
        create two offscreen framebuffers (left panel, right panel), each
        (WINDOW_W//2, int(WINDOW_H*config.PANELS_FRAC)) -- the 50/50 split
        (SUTRAS 2.1) is enforced HERE and nowhere else."""
        self._window = window
        self.ctx = moderngl.create_context()       # PUBLIC (see header notes)
        ctx = self.ctx

        # ---- shaders: load every required stem, fail loud ----
        self._programs = {}
        for stem in REQUIRED_SHADERS:
            vert = self._read_shader(stem + ".vert")
            frag = self._read_shader(stem + ".frag")
            try:
                self._programs[stem] = ctx.program(vertex_shader=vert,
                                                   fragment_shader=frag)
            except Exception as exc:
                raise RuntimeError(
                    "LOOM2 renderer: shader '%s' failed to compile:\n%s"
                    % (stem, exc))

        # ---- panel framebuffers: HDR color + depth ----
        self._panel_tex = {}
        self._panel_fbo = {}
        for side in ("left", "right"):
            tex = ctx.texture((_PANEL_W, _PANEL_H), 4, dtype="f2")
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            depth = ctx.depth_renderbuffer((_PANEL_W, _PANEL_H))
            self._panel_tex[side] = tex
            self._panel_fbo[side] = ctx.framebuffer(
                color_attachments=[tex], depth_attachment=depth)

        # ---- bloom ping-pong buffers (quarter res, shared by both panels) ----
        qw = max(1, _PANEL_W // _BLOOM_DOWNSCALE)
        qh = max(1, _PANEL_H // _BLOOM_DOWNSCALE)
        self._bloom_size = (qw, qh)
        self._bloom_tex = []
        self._bloom_fbo = []
        for _ in range(2):
            tex = ctx.texture((qw, qh), 4, dtype="f2")
            tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self._bloom_tex.append(tex)
            self._bloom_fbo.append(ctx.framebuffer(color_attachments=[tex]))

        # ---- fullscreen-triangle VAOs (no VBO; gl_VertexID in the .vert) ----
        self._fs_vao = {
            stem: ctx.vertex_array(self._programs[stem], [])
            for stem in ("bloom_extract", "bloom_blur", "composite")
        }

        # ---- static sampler units (uniform names per DeepSeek 2026-07-07) ----
        self._programs["bloom_extract"]["u_tex"].value = 0
        self._programs["bloom_blur"]["u_tex"].value = 0
        self._programs["composite"]["u_scene"].value = 0
        self._programs["composite"]["u_bloom"].value = 1

        self._active = None                 # 'left' | 'right' | None

    # ------------------------------------------------------------ panels --

    def begin_panel(self, side: str) -> None:
        """'left' | 'right': bind that panel's framebuffer, clear, set viewport
        and depth test. All draw calls until end_panel() land in this panel."""
        if side not in ("left", "right"):
            raise ValueError("begin_panel: side must be 'left' or 'right', "
                             "got %r" % (side,))
        fbo = self._panel_fbo[side]
        fbo.use()
        fbo.viewport = (0, 0, _PANEL_W, _PANEL_H)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)     # friendly default for icons/glass
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        fbo.clear(_CLEAR_COLOR[0], _CLEAR_COLOR[1], _CLEAR_COLOR[2],
                  1.0, depth=1.0)
        self._active = side

    def end_panel(self) -> None:
        self._active = None
        self.ctx.screen.use()

    # --------------------------------------------------------- composite --

    def composite(self) -> None:
        """Blit both panels to screen with bloom pass; leave the top strip and
        quiz bar regions untouched black (hud draws there afterward)."""
        ctx = self.ctx
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.BLEND)
        qw, qh = self._bloom_size

        screen = ctx.screen
        screen.use()
        screen.viewport = _FULL_VIEWPORT
        ctx.clear(0.0, 0.0, 0.0)            # strip + quiz bar stay black

        for index, side in enumerate(("left", "right")):
            scene_tex = self._panel_tex[side]

            # 1) bright-pass extract, downsampled into quarter-res A
            self._bloom_fbo[0].use()
            self._bloom_fbo[0].viewport = (0, 0, qw, qh)
            self._programs["bloom_extract"]["u_threshold"].value = BLOOM_THRESHOLD
            scene_tex.use(location=0)
            self._fs_vao["bloom_extract"].render(moderngl.TRIANGLES, vertices=3)

            # 2) horizontal blur: A -> B
            self._bloom_fbo[1].use()
            self._bloom_fbo[1].viewport = (0, 0, qw, qh)
            self._programs["bloom_blur"]["u_dir"].value = (1.0 / qw, 0.0)
            self._bloom_tex[0].use(location=0)
            self._fs_vao["bloom_blur"].render(moderngl.TRIANGLES, vertices=3)

            # 3) vertical blur: B -> A
            self._bloom_fbo[0].use()
            self._bloom_fbo[0].viewport = (0, 0, qw, qh)
            self._programs["bloom_blur"]["u_dir"].value = (0.0, 1.0 / qh)
            self._bloom_tex[1].use(location=0)
            self._fs_vao["bloom_blur"].render(moderngl.TRIANGLES, vertices=3)

            # 4) composite scene + bloom into this panel's screen region
            screen.use()
            screen.viewport = (index * _PANEL_W, _PANEL_Y0,
                               _PANEL_W, _PANEL_H)
            self._programs["composite"]["u_strength"].value = BLOOM_STRENGTH
            self._programs["composite"]["u_exposure"].value = BLOOM_EXPOSURE
            scene_tex.use(location=0)
            self._bloom_tex[0].use(location=1)
            self._fs_vao["composite"].render(moderngl.TRIANGLES, vertices=3)

        # leave the context tidy for hud (pyglet 2D) and the next frame
        screen.viewport = _FULL_VIEWPORT

    # ---------------------------------------------------------- programs --

    def program(self, name: str):
        """Return the compiled shader program by filename stem, e.g.
        program('terrain') -> data/shaders/terrain.vert + terrain.frag."""
        try:
            return self._programs[name]
        except KeyError:
            raise KeyError("LOOM2 renderer: unknown shader '%s'. "
                           "Valid stems: %s" % (name, ", ".join(REQUIRED_SHADERS)))

    # ---------------------------------------------------------- internal --

    @staticmethod
    def _read_shader(filename: str) -> str:
        path = os.path.join(config.SHADERS_DIR, filename)
        if not os.path.isfile(path):
            raise RuntimeError(
                "LOOM2 renderer: missing shader file '%s'. All 8 stems in "
                "REQUIRED_SHADERS need .vert + .frag in %s."
                % (path, config.SHADERS_DIR))
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

Remarks for DeepSeek (please courier back):

    HDR panels: color buffers are RGBA16F (dtype='f2') so emissive materials (totem pulse, icon flashes, the glowing slice curve) can exceed 1.0 and bloom naturally — consistent with your composite shader having u_exposure. If the pasted Homeworld GLSL assumed LDR anywhere, tell me and I'll flip to 'f1' — one-line change.
    "¼ res" interpretation: I read it as quarter dimensions (160×129 buffers) — big soft glow, very cheap. If Homeworld meant half-dimensions (¼ area), change _BLOOM_DOWNSCALE to 2 — it's a top-of-file tunable, like BLOOM_THRESHOLD (0.80), BLOOM_STRENGTH (0.85), BLOOM_EXPOSURE (1.00).
    Screen clear ownership: composite() clears the whole window to black before blitting the two panel regions at y0​=144 — so the top strip and quiz bar are guaranteed black for hud, and nobody else needs to clear. Viewport is restored to full-window afterward for pyglet's 2D hud.
    Friendly defaults in begin_panel: depth test AND alpha blending enabled (standard SRC_ALPHA func) — helix_panel's icon billboards and Parent E's glass need blending; opaque terrain is unaffected. Siblings may override via the public renderer.ctx.
    Fail-loud active: missing shader file or GLSL compile error raises immediately at boot with the stem name and path, per your confirmation that all 8 stems now exist.
    Imports used: os, moderngl, config (pyglet/numpy allowed but not needed). ~215 lines. No CONTRACT-ISSUEs found in G3.1.

Parent C's chunk is complete — camera.py bound, renderer.py delivered. Once DeepSeek binds this and the smoke test passes, my two modules stand ready for Parents D/E/F/G to draw upon. It has been an honor to hold the eyes of LOOM2, Nir. 🎨🎻🎺🪈❤️
