"""
LOOM2 -- graphics/hud.py
================================================================================
Scenario text + equation + panel titles + quiz bar (A-D / OK / HINT) + win
screen. A Homeworld-style moderngl 2D overlay (G3.7-A): ONE shader program,
ONE dynamic VBO refilled per frame, painter's order, WINDOW-pixel coordinates,
origin bottom-left (matching the mouse and the config regions).

Allowed imports: moderngl, numpy, os, config, core.types
(+ Pillow at atlas-build / set_scene time only).  NO pyglet anywhere.

CONSTRUCTOR (blessed additive signature): Hud(window, renderer).
The shared moderngl context is renderer.ctx (renderer = boot step 2, Hud =
boot step 6); if renderer is None we fall back to moderngl.get_context().
Hud is constructible AND drawable BEFORE any set_scene (scene-less safe).

Hud draws LAST (frozen frame step 7, after renderer.composite()) and sets its
own 2D GL state every frame: DEPTH off, CULL off, BLEND on with
(SRC_ALPHA, ONE_MINUS_SRC_ALPHA). It binds no framebuffer -- it paints onto
whatever composite() left bound (ctx.screen, full viewport).

SCREEN MAP (1280 x 720, y up; regions derived from config like the renderer):

    720 +----------------------------------------------------------------+
        |  title line 1   (white + outline, 20 px, emojis welcome)       |
        |  title line 2                                                  |
        |  title line 3                    GRAPHICS  (both panels)       |
        |                                                                |
        |                        [ equation.png ]     <- yellow, centered|
        | CARTESIAN COORDINATES                SONIFIQUATION COORDINATES |
    144 +----------------------------------------------------------------+
        | Question text ...................................  | hint      |
        | 🎧 Listen to all four — as many times as you like. | (green)   |
        | [ A ] [ B ] [ C ] [ D ]    [ OK ] [ 💡HINT ]       | explain   |
      0 +----------------------------------------------------|-(pink)----+
                                                          SEP_X

LOCKED LOOK (config.py + G3.7-A -- honored verbatim, never restyled here):
  white+outline scenario text over the graphics top; yellow equation image
  centered on the panel seam at the bottom of the graphics; 14 px panel
  titles at the same level (left/right aligned); bright PINK wrong-answer
  text (never red); bright GREEN hint text; blinking light-blue "YOU WIN!!!".

SIZE NOTE (G1.1 rule 4): ~540 lines. The glyph/emoji atlas and the quiz-bar
polish are the honest cost of the no-pyglet ruling and of doing the bar
justice; reported, not hidden.
================================================================================
"""
import os
import numpy as np
import moderngl
import config
from core.types import Mode

# ============================================================ taste block ==
# Everything in this block is MINE to tune (DeepSeek round 2: "the quiz bar's
# internal layout is yours -- make it beautiful"). Locked values stay in
# config.py and are read from there at draw time.

WIN_BLINK_FRAMES = 30        # ~0.5 s on / 0.5 s off at the scheduled 60 fps.
                             # Frame-counter blink: draw() receives no clock
                             # and 'time' is not in the allowed imports.

# --- quiz-bar geometry (window pixels, bottom-left origin) ---
BTN_Y0, BTN_Y1   = 18.0, 70.0          # button row: 52 px tall
BTN_X0           = 20.0                # first answer button's left edge
BTN_W, BTN_GAP   = 110.0, 14.0         # answer buttons A-D
OK_X0,   OK_W    = 530.0, 96.0         # OK button
HINT_X0, HINT_W  = 642.0, 120.0        # HINT button, beside OK (SUTRAS 5.1)
SEP_X            = 774.0               # hairline between buttons & feedback
MSG_X0           = 792.0               # feedback text column (right third)
ACCENT_W         = 3.0                 # colored accent bar beside feedback

QUESTION_PX      = None                # None -> config.HUD_TEXT_PX (20)
ENCOURAGE_PX     = 14                  # the "listen to all four" line
FEEDBACK_PX      = 16                  # hint / explanation text size
FEEDBACK_PITCH   = 20.0                # line pitch for feedback text

# --- palette (fills/frames only -- all TEXT colors come from config) ---
BAR_TOP_RGB      = (28, 32, 42)        # quiz-bar backdrop, gradient top
BAR_BOT_RGB      = (11, 12, 17)        #   "        "       gradient bottom
BAR_EDGE_RGB     = (96, 118, 150)      # steel hairline atop the quiz bar
BTN_TOP,     BTN_BOT     = (46, 52, 66),  (24, 27, 35)    # idle button
BTN_SEL_TOP, BTN_SEL_BOT = (64, 92, 140), (36, 50, 84)    # selected button
OK_ARM_TOP,  OK_ARM_BOT  = (44, 88, 58),  (20, 42, 28)    # OK when armed
BTN_EDGE         = (106, 112, 124)     # idle button frame
BTN_EDGE_SEL     = (235, 241, 250)     # selected button frame (glows)
SEP_RGB          = (58, 66, 82)        # vertical separator hairline
DIM_TEXT         = (168, 178, 192)     # encouragement line / disarmed OK
SHADOW_ALPHA     = 0.35                # soft drop shadow under buttons
WIN_DIM_ALPHA    = 0.45                # full-screen dim behind the win text
FADE_FRAMES      = 18                  # gentle fade-in for feedback/success

# ============================================================== shaders ====
_VERT = """
#version 330
uniform vec2 u_screen;
in vec2 in_pos; in vec2 in_uv; in vec4 in_color;
out vec2 v_uv; out vec4 v_color;
void main() {
    vec2 ndc = (in_pos / u_screen) * 2.0 - 1.0;   // pixels -> clip, y up
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_uv = in_uv; v_color = in_color;
}
"""
_FRAG = """
#version 330
uniform int u_mode;            // 0 = flat shape, 1 = textured (atlas / image)
uniform sampler2D u_tex;
in vec2 v_uv; in vec4 v_color;
out vec4 f_color;
void main() {
    if (u_mode == 0) f_color = v_color;
    else             f_color = texture(u_tex, v_uv) * v_color;
}
"""


# ========================================================== glyph atlas ====
class _GlyphAtlas:
    """Every glyph the HUD can show, packed once into ONE RGBA texture.

    * Letters are baked WHITE with a baked BLACK stroke (Nir's outline rule),
      then tinted per-vertex at draw time -- white text, yellow equation
      captions, pink/green feedback are all the same cells, just tinted.
    * Emojis are baked as full-color cells from Segoe UI Emoji and drawn
      untinted (tint forced to white), so 🔊 💡 🎧 ✅ keep their real colors.
    * Cells are baked at 64 px and scaled at draw time (linear filtering both
      ways) -- one bake serves 14 px titles and the 72 px win banner alike.
    * Lazy: any character ever passed to Hud text methods is baked on first
      sight, so emojis Nir types into scene JSON later Just Work.
    * uv space equals the atlas image's top-left pixel space, and every quad
      maps its TOP edge to its cell's top uv -- one consistent convention,
      no image flips anywhere.
    """
    SIZE = 1024                  # atlas texture is SIZE x SIZE RGBA
    BAKE_PX = 64                 # bake size (font size) for every glyph
    STROKE = 3                   # baked black outline thickness at bake size
    PAD = 2                      # spacing between cells (bleed guard)

    def __init__(self, ctx):
        from PIL import Image, ImageDraw, ImageFont   # atlas-build time only
        self._img = Image.new("RGBA", (self.SIZE, self.SIZE), (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._img)
        self._font = self._try_fonts(
            ImageFont, ("segoeuib.ttf", "arialbd.ttf",
                        "DejaVuSans-Bold.ttf", "arial.ttf"))
        if self._font is None:
            raise RuntimeError("hud: no usable system TTF font found")
        self._emoji_font = self._try_fonts(ImageFont, ("seguiemj.ttf",))
        self._x = self._y = self._row_h = 0           # shelf-packer cursor
        # ch -> (u0, v0, u1, v1, w, h, off_x, off_y, advance, is_color)
        self.glyphs = {}
        self.tex = ctx.texture((self.SIZE, self.SIZE), 4)
        self.tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._dirty = True
        for code in range(32, 127):                   # ASCII pre-bake
            self.ensure(chr(code))

    @staticmethod
    def _try_fonts(ImageFont, names):
        """First loadable font wins; None if none load (emoji font may be
        absent on non-Windows boxes -- letters then stand in for emojis)."""
        for name in names:
            try:
                return ImageFont.truetype(name, _GlyphAtlas.BAKE_PX)
            except OSError:
                continue
        return None

    def ensure(self, ch):
        """Bake ch if unseen. Unbakeable characters degrade to the space
        glyph rather than crashing mid-scene -- the game never breaks."""
        if ch in self.glyphs or ch in ("\n", "\r"):
            return
        is_emoji = ord(ch) >= 0x2190 and self._emoji_font is not None
        font = self._emoji_font if is_emoji else self._font
        stroke = 0 if is_emoji else self.STROKE
        try:
            box = self._draw.textbbox((0, 0), ch, font=font,
                                      stroke_width=stroke,
                                      embedded_color=is_emoji)
            adv = float(font.getlength(ch))
        except Exception:
            self.glyphs[ch] = self.glyphs.get(" ")
            return
        w = max(1, box[2] - box[0])
        h = max(1, box[3] - box[1])
        if self._x + w + self.PAD > self.SIZE:        # start a new shelf row
            self._x = 0
            self._y += self._row_h + self.PAD
            self._row_h = 0
        if self._y + h + self.PAD > self.SIZE:        # atlas full: degrade
            self.glyphs[ch] = self.glyphs.get(" ")
            return
        x, y = self._x, self._y
        self._draw.text((x - box[0], y - box[1]), ch, font=font,
                        fill=(255, 255, 255, 255), stroke_width=stroke,
                        stroke_fill=(0, 0, 0, 255), embedded_color=is_emoji)
        s = float(self.SIZE)
        self.glyphs[ch] = (x / s, y / s, (x + w) / s, (y + h) / s,
                           float(w), float(h), float(box[0]), float(box[1]),
                           adv, is_emoji)
        self._x += w + self.PAD
        self._row_h = max(self._row_h, h)
        self._dirty = True

    def upload(self):
        """(Re)upload if any glyph was baked since the last draw. Called by
        Hud._flush() right before rendering, so glyphs baked lazily earlier
        in the SAME frame are already in video memory when they're drawn."""
        if self._dirty:
            self.tex.write(self._img.tobytes())
            self._dirty = False


# ================================================================== Hud ====
class Hud:
    """The 2D voice of the game: scenario, equation, titles, quiz, win.

    quiz_ui_state (verbatim from game_state, DeepSeek A2):
      {"selected": str|None, "playing": str|None, "hint_open": bool,
       "explain": str ("" = none), "success": bool, "campaign_complete": bool}

    Draw order inside one frame (painter's algorithm, later = on top):
      1. quiz-bar backdrop (gradient + steel hairline)
      2. over-graphics layer: title lines, panel titles, equation image
      3. quiz-bar content (EXPLORE/QUIZ_LISTEN/SCENE_TRANSITION)
         or the Glass-Blade help line (SLICE)
      4. success celebration (fades in, rises gently)
      5. win screen (full-screen dim + blinking banner) -- above everything
    """

    def __init__(self, window, renderer=None):
        self._ctx = (renderer.ctx if renderer is not None
                     else moderngl.get_context())
        self._W = float(config.WINDOW_W)
        self._H = float(config.WINDOW_H)
        self._quiz_h = float(int(config.WINDOW_H * config.QUIZ_BAR_FRAC))
        self._prog = self._ctx.program(vertex_shader=_VERT,
                                       fragment_shader=_FRAG)
        self._prog["u_screen"].value = (self._W, self._H)
        self._prog["u_tex"].value = 0
        self._vbo = self._ctx.buffer(reserve=128 * 1024, dynamic=True)
        self._vao = self._ctx.vertex_array(
            self._prog,
            [(self._vbo, "2f 2f 4f", "in_pos", "in_uv", "in_color")])
        self._atlas = _GlyphAtlas(self._ctx)
        self._spec = None                  # scene-less until set_scene
        self._eq_tex = None
        self._frame = 0
        self._runs = []                    # [[texture|None, [floats]], ...]
        # animation edge-trackers (frame at which a state appeared, or None)
        self._succ_f0 = None
        self._expl_f0 = None
        self._expl_prev = ""
        # single source of truth for BOTH drawing and hit_test
        self._btn = {}
        x = BTN_X0
        for lab in "ABCD":
            self._btn[lab] = (x, BTN_Y0, x + BTN_W, BTN_Y1)
            x += BTN_W + BTN_GAP
        self._btn["OK"] = (OK_X0, BTN_Y0, OK_X0 + OK_W, BTN_Y1)
        self._btn["HINT"] = (HINT_X0, BTN_Y0, HINT_X0 + HINT_W, BTN_Y1)

    # ------------------------------------------------------- contract API --
    def set_scene(self, spec) -> None:
        """Load title_lines, equation.png, question, options, hint_lines.
        Pre-bakes every glyph the scene can show (incl. all emojis) so the
        first frame of a new scene pays no mid-frame bake cost."""
        self._spec = spec
        self._succ_f0 = self._expl_f0 = None
        self._expl_prev = ""
        for s in (list(spec.title_lines) + list(spec.hint_lines) +
                  [spec.question, spec.success_text] +
                  [o.label for o in spec.options] +
                  [o.explain for o in spec.options]):
            for ch in str(s):
                self._atlas.ensure(ch)
        if self._eq_tex is not None:
            self._eq_tex.release()
            self._eq_tex = None
        path = spec.equation_png
        if path and os.path.isfile(path):
            from PIL import Image            # image decode at load time only
            img = Image.open(path).convert("RGBA")
            self._eq_tex = self._ctx.texture(img.size, 4, img.tobytes())
            self._eq_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)

    def hit_test(self, mx: int, my: int) -> str:
        """Mouse -> 'A'|'B'|'C'|'D'|'OK'|'HINT'|'' (window px, bottom-left).
        Tests the same rectangles the buttons are drawn from -- the picture
        and the click can never disagree."""
        for lab, (x0, y0, x1, y1) in self._btn.items():
            if x0 <= mx <= x1 and y0 <= my <= y1:
                return lab
        return ""

    def draw(self, mode, quiz_ui_state: dict) -> None:
        """quiz_ui_state comes from game_state; hud only DRAWS (G3.7)."""
        ui = quiz_ui_state or {}
        self._frame += 1
        self._track_edges(ui)
        self._runs = []
        self._bar_backdrop()
        if self._spec is not None:
            self._layer_scene_text()
        if mode == Mode.SLICE:
            self._layer_slice_help()
        elif self._spec is not None:
            self._layer_quiz_bar(ui)
            if ui.get("success") and not ui.get("campaign_complete"):
                self._layer_success()
        if ui.get("campaign_complete"):
            self._layer_win()
        self._flush()

    # --------------------------------------------------- animation edges --
    def _track_edges(self, ui):
        """Record the frame on which 'success' / a new explanation appeared,
        so those texts can fade in gently instead of popping."""
        if ui.get("success"):
            if self._succ_f0 is None:
                self._succ_f0 = self._frame
        else:
            self._succ_f0 = None
        expl = ui.get("explain", "")
        if expl:
            if expl != self._expl_prev:
                self._expl_f0 = self._frame
        else:
            self._expl_f0 = None
        self._expl_prev = expl

    def _fade(self, f0):
        """0..1 ease-out ramp over FADE_FRAMES since frame f0."""
        if f0 is None:
            return 1.0
        t = min(1.0, (self._frame - f0) / float(FADE_FRAMES))
        return t * (2.0 - t)                            # ease-out quad

    # ------------------------------------------------------------ layers --
    def _bar_backdrop(self):
        """Quiz-bar backdrop: a quiet dark gradient (design, not dead black)
        crowned by a steel hairline that separates world from interface."""
        qh = self._quiz_h
        self._rect_grad(0.0, 0.0, self._W, qh - 2.0, BAR_TOP_RGB, BAR_BOT_RGB)
        self._rect(0.0, qh - 2.0, self._W, qh - 1.0, BAR_EDGE_RGB, a=0.85)
        self._rect(0.0, qh - 1.0, self._W, qh, (8, 9, 12), a=0.9)
        # vertical hairline between the button zone and the feedback zone
        self._rect(SEP_X, 12.0, SEP_X + 1.0, qh - 12.0, SEP_RGB, a=0.9)

    def _layer_scene_text(self):
        """Everything painted OVER the graphics: scenario lines across the
        top, panel titles + equation image along the bottom seam."""
        spec, qh = self._spec, self._quiz_h
        y = self._H - 8.0
        for line in list(spec.title_lines)[:config.HUD_MAX_TEXT_LINES]:
            self._text(str(line), 12.0, y,
                       config.HUD_TEXT_PX, config.HUD_TEXT_RGB)
            y -= config.HUD_LINE_PITCH_PX
        ty = qh + 4.0 + config.HUD_TITLE_PX
        self._text(config.PANEL_TITLE_LEFT, 10.0, ty,
                   config.HUD_TITLE_PX, config.HUD_TITLE_RGB)
        self._text(config.PANEL_TITLE_RIGHT, self._W - 10.0, ty,
                   config.HUD_TITLE_PX, config.HUD_TITLE_RGB, align="right")
        if self._eq_tex is not None:
            iw, ih = self._eq_tex.size
            s = min(1.0, config.HUD_EQUATION_MAX_H_PX / ih, (self._W * 0.44) / iw)
            w, h = iw * s, ih * s
            x0 = self._W / 2.0 - w / 2.0        # centered on the panel seam
            self._image(self._eq_tex, x0, qh + 8.0, x0 + w, qh + 8.0 + h)

    def _layer_quiz_bar(self, ui):
        """Question, encouragement, the six buttons, and the feedback column."""
        spec, qh = self._spec, self._quiz_h
        q_px = QUESTION_PX or config.HUD_TEXT_PX
        sel, playing = ui.get("selected"), ui.get("playing")
        self._text(spec.question, 20.0, qh - 6.0, q_px, config.HUD_TEXT_RGB)
        # UPANISHADS §3: the UI itself encourages listening to all four
        self._text("🎧 Listen to all four — as many times as you like.",
                   20.0, qh - 34.0, ENCOURAGE_PX, DIM_TEXT)
        for lab in ("A", "B", "C", "D", "OK", "HINT"):
            self._button(lab, ui, sel, playing)
        self._feedback_column(ui)

    def _button(self, lab, ui, sel, playing):
        """One quiz button: soft shadow, vertical-gradient fill, frame,
        optical glow when selected, pulsing 🔊 when its sound is looping."""
        x0, y0, x1, y1 = self._btn[lab]
        is_sel = (lab == sel)
        armed_ok = (lab == "OK" and sel is not None)
        # soft drop shadow (offset dark quad -- reads as depth, costs nothing)
        self._rect(x0 + 2.0, y0 - 3.0, x1 + 2.0, y0, (0, 0, 0), a=SHADOW_ALPHA)
        top, bot = ((BTN_SEL_TOP, BTN_SEL_BOT) if is_sel else
                    (OK_ARM_TOP, OK_ARM_BOT) if armed_ok else
                    (BTN_TOP, BTN_BOT))
        self._rect_grad(x0, y0, x1, y1, top, bot)
        # glassy highlight strip along the button's upper edge
        self._rect(x0 + 2.0, y1 - 8.0, x1 - 2.0, y1 - 3.0,
                   (255, 255, 255), a=0.07)
        self._frame_rect(x0, y0, x1, y1,
                         BTN_EDGE_SEL if is_sel else BTN_EDGE)
        if is_sel:                       # breathing outer glow, selection color
            pulse = 0.5 + 0.5 * float(np.sin(self._frame * 0.09))
            self._frame_rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2,
                             BTN_EDGE_SEL, t=2.0, a=0.20 + 0.15 * pulse)
            self._frame_rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4,
                             BTN_EDGE_SEL, t=2.0, a=0.08 + 0.06 * pulse)
        label = "💡HINT" if lab == "HINT" else lab
        col = (DIM_TEXT if (lab == "OK" and sel is None)
               else config.HUD_TEXT_RGB)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        self._text_centered(label, cx, cy, config.HUD_TEXT_PX, col)
        if playing == lab:               # the looping option sings, visibly
            pulse = 0.65 + 0.35 * float(np.sin(self._frame * 0.18))
            self._text_centered("🔊", x1 - 16.0, cy, 18,
                                config.HUD_TEXT_RGB, a=pulse)

    def _feedback_column(self, ui):
        """Right third of the bar: green hint lines above the pink
        wrong-answer explanation, each with a colored accent bar and a
        gentle fade-in. Kindness rule: soft colors, generous spacing."""
        spec, qh = self._spec, self._quiz_h
        max_w = self._W - 14.0 - MSG_X0
        my = qh - 8.0
        if ui.get("hint_open"):
            top = my
            for line in spec.hint_lines:
                for wl in self._wrap(line, FEEDBACK_PX, max_w):
                    self._text(wl, MSG_X0, my, FEEDBACK_PX,
                               config.HUD_HINT_RGB)
                    my -= FEEDBACK_PITCH
            self._rect(MSG_X0 - ACCENT_W - 6.0, my + FEEDBACK_PITCH - 14.0,
                       MSG_X0 - 6.0, top, config.HUD_HINT_RGB, a=0.8)
            my -= 6.0
        expl = ui.get("explain", "")
        if expl:
            a = self._fade(self._expl_f0)
            top = my
            for wl in self._wrap(expl, FEEDBACK_PX, max_w):
                self._text(wl, MSG_X0, my, FEEDBACK_PX,
                           config.HUD_WRONG_RGB, a=a)
                my -= FEEDBACK_PITCH
            self._rect(MSG_X0 - ACCENT_W - 6.0, my + FEEDBACK_PITCH - 14.0,
                       MSG_X0 - 6.0, top, config.HUD_WRONG_RGB, a=0.8 * a)
        if ui.get("success"):
            self._text("✅ Correct!", MSG_X0, my, 18,
                       config.HUD_HINT_RGB, a=self._fade(self._succ_f0))

    def _layer_success(self):
        """SCENE_TRANSITION celebration: the scene's success_text in warm
        yellow, wrapped and centered over the graphics, fading in and rising
        a few pixels as the winning groove loops underneath."""
        spec, qh = self._spec, self._quiz_h
        a = self._fade(self._succ_f0)
        rise = (1.0 - a) * 12.0
        lines = self._wrap(spec.success_text, 24, self._W * 0.7)
        y = qh + (self._H - qh) * 0.45 + len(lines) * 14.0 - rise
        for wl in lines:
            self._text(wl, self._W / 2.0, y, 24,
                       config.HUD_EQUATION_RGB, align="center", a=a)
            y -= 28.0

    def _layer_win(self):
        """Campaign complete: dim the whole world, blink 'YOU WIN!!!' in
        light blue (locked), keep the final closing line steady beneath it,
        and let the little orchestra take its bow."""
        self._rect(0.0, 0.0, self._W, self._H, (0, 0, 0), a=WIN_DIM_ALPHA)
        cy = self._H * 0.58
        if (self._frame // WIN_BLINK_FRAMES) % 2 == 0:   # blink on-phase
            self._text("YOU WIN!!!", self._W / 2.0, cy, 72,
                       config.HUD_WIN_RGB, align="center")
        y = cy - 84.0
        if self._spec is not None and self._spec.success_text:
            for wl in self._wrap(self._spec.success_text, 20, self._W * 0.7):
                self._text(wl, self._W / 2.0, y, 20,
                           config.HUD_TEXT_RGB, align="center")
                y -= 24.0
        self._text("🎺 🎻 🪈", self._W / 2.0, y - 8.0, 24,
                   config.HUD_TEXT_RGB, align="center")

    def _layer_slice_help(self):
        """SLICE mode: the bar rests, one calm green help line takes over."""
        qh = self._quiz_h
        self._text("🔪 Glass Blade", self._W / 2.0, qh - 30.0,
                   config.HUD_TEXT_PX, config.HUD_HINT_RGB, align="center")
        self._text("WASD move · ◀▶ rotate · ▲▼ tilt · Enter play · C exit",
                   self._W / 2.0, qh - 62.0, 14, DIM_TEXT, align="center")

    # -------------------------------------------------------- primitives --
    def _emit(self, tex, verts):
        """Append to the draw list, merging consecutive same-texture items
        into one span (fewer draw calls; flat shapes share the None-span)."""
        if self._runs and self._runs[-1][0] is tex:
            self._runs[-1][1].extend(verts)
        else:
            self._runs.append([tex, list(verts)])

    @staticmethod
    def _quad(x0, y0, x1, y1, u0, v0, u1, v1, r, g, b, a):
        """Two triangles; the quad's TOP edge carries the cell's TOP uv
        (atlas v runs top-down -- one convention, no flips)."""
        return [x0, y1, u0, v0, r, g, b, a,   x0, y0, u0, v1, r, g, b, a,
                x1, y0, u1, v1, r, g, b, a,   x0, y1, u0, v0, r, g, b, a,
                x1, y0, u1, v1, r, g, b, a,   x1, y1, u1, v0, r, g, b, a]

    def _rect(self, x0, y0, x1, y1, rgb, a=1.0):
        r, g, b = (c / 255.0 for c in rgb)
        self._emit(None, self._quad(x0, y0, x1, y1, 0, 0, 0, 0, r, g, b, a))

    def _rect_grad(self, x0, y0, x1, y1, top_rgb, bot_rgb, a=1.0):
        """Vertical gradient fill -- per-vertex color is free in this shader."""
        tr, tg, tb = (c / 255.0 for c in top_rgb)
        br, bg, bb = (c / 255.0 for c in bot_rgb)
        self._emit(None, [
            x0, y1, 0, 0, tr, tg, tb, a,   x0, y0, 0, 0, br, bg, bb, a,
            x1, y0, 0, 0, br, bg, bb, a,   x0, y1, 0, 0, tr, tg, tb, a,
            x1, y0, 0, 0, br, bg, bb, a,   x1, y1, 0, 0, tr, tg, tb, a])

    def _frame_rect(self, x0, y0, x1, y1, rgb, t=2.0, a=1.0):
        self._rect(x0, y1 - t, x1, y1, rgb, a)          # top
        self._rect(x0, y0, x1, y0 + t, rgb, a)          # bottom
        self._rect(x0, y0 + t, x0 + t, y1 - t, rgb, a)  # left
        self._rect(x1 - t, y0 + t, x1, y1 - t, rgb, a)  # right

    def _image(self, tex, x0, y0, x1, y1, a=1.0):
        self._emit(tex, self._quad(x0, y0, x1, y1, 0.0, 0.0, 1.0, 1.0,
                                   1.0, 1.0, 1.0, a))

    # ------------------------------------------------------------- text ---
    def _text_w(self, s, px):
        """Width in pixels of s at size px (bakes unseen glyphs on the way)."""
        k = px / float(_GlyphAtlas.BAKE_PX)
        w = 0.0
        for ch in str(s):
            self._atlas.ensure(ch)
            g = self._atlas.glyphs.get(ch)
            if g is not None:
                w += g[8] * k
        return w

    def _text(self, s, x, y_top, px, rgb, align="left", a=1.0):
        """One line of text. (x, y_top) anchors the TOP of the line box.
        Letters are tinted rgb; color-emoji cells are drawn untinted."""
        k = px / float(_GlyphAtlas.BAKE_PX)
        w = self._text_w(s, px)
        if align == "center":
            x -= w / 2.0
        elif align == "right":
            x -= w
        r, gc, b = (c / 255.0 for c in rgb)
        pen = x
        for ch in str(s):
            g = self._atlas.glyphs.get(ch)
            if g is None:
                continue
            u0, v0, u1, v1, gw, gh, ox, oy, adv, is_color = g
            cr, cg, cb = (1.0, 1.0, 1.0) if is_color else (r, gc, b)
            gx = pen + ox * k
            gy1 = y_top - oy * k
            self._emit(self._atlas.tex,
                       self._quad(gx, gy1 - gh * k, gx + gw * k, gy1,
                                  u0, v0, u1, v1, cr, cg, cb, a))
            pen += adv * k
        return w

    def _text_centered(self, s, cx, cy, px, rgb, a=1.0):
        """Optically centered text: measures the string's true ink box from
        the glyph records and centers THAT on (cx, cy) -- so button labels
        sit exactly in the middle, not 'roughly, by font metrics'."""
        k = px / float(_GlyphAtlas.BAKE_PX)
        top, bot = None, None
        for ch in str(s):
            self._atlas.ensure(ch)
            g = self._atlas.glyphs.get(ch)
            if g is None:
                continue
            top = g[7] if top is None else min(top, g[7])
            bot = g[7] + g[5] if bot is None else max(bot, g[7] + g[5])
        if top is None:
            return
        ink_h = (bot - top) * k
        y_top = cy + ink_h / 2.0 + top * k
        self._text(s, cx, y_top, px, rgb, align="center", a=a)

    def _wrap(self, s, px, max_w):
        """Greedy word wrap by real rendered width (not character count)."""
        words = str(s).split()
        lines, cur = [], ""
        for wd in words:
            t = wd if not cur else cur + " " + wd
            if not cur or self._text_w(t, px) <= max_w:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    # ------------------------------------------------------------- flush --
    def _flush(self):
        """Upload the frame's vertices once, then render span by span.
        Sets the overlay's own 2D GL state every frame (composite() leaves
        depth/blend off and ctx.screen bound -- we take it from there)."""
        if not self._runs:
            return
        self._atlas.upload()          # lazily-baked glyphs land before use
        verts, spans, first = [], [], 0
        for tex, arr in self._runs:
            n = len(arr) // 8
            spans.append((tex, first, n))
            verts.extend(arr)
            first += n
        data = np.asarray(verts, dtype="f4").tobytes()
        if len(data) > self._vbo.size:
            self._vbo.orphan(len(data))     # same GL id: the VAO stays valid
        else:
            self._vbo.orphan()
        self._vbo.write(data)
        ctx = self._ctx
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.disable(moderngl.CULL_FACE)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        for tex, start, count in spans:
            if tex is None:
                self._prog["u_mode"].value = 0
            else:
                self._prog["u_mode"].value = 1
                tex.use(location=0)
            self._vao.render(moderngl.TRIANGLES, first=start, vertices=count)
        self._runs = []
