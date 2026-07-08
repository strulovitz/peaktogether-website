"""
LOOM2 -- graphics/hud.py
Scenario text + equation + panel titles + quiz bar (A-D / OK / HINT) + win.
Homeworld-style moderngl 2D overlay (G3.7-A): ONE shader, ONE dynamic VBO,
painter's order, WINDOW-pixel coordinates, origin bottom-left.
Allowed imports: moderngl, numpy, os, config, core.types
(+ Pillow at atlas-build / set_scene time only). NO pyglet.

CONSTRUCTOR (blessed additive signature): Hud(window, renderer). The shared
moderngl context is renderer.ctx (renderer = boot step 2, Hud = boot step 6);
if renderer is None we fall back to moderngl.get_context().
Hud is constructible AND drawable BEFORE any set_scene (scene-less safe).

Hud draws LAST (frame step 7, after renderer.composite()) and sets its own
2D GL state every frame: DEPTH off, CULL off, BLEND on (SRC_ALPHA / 1-SRC_ALPHA).

SIZE NOTE (G1.1 rule 4): ~430 lines. The glyph/emoji atlas (~120 lines) is
the irreducible cost of the no-pyglet ruling; reported, not hidden.
"""
import os
import numpy as np
import moderngl
import config
from core.types import Mode

# ---- taste constants (mine by DeepSeek round-2 mandate; tweak freely) ----
WIN_BLINK_FRAMES = 30            # ~0.5 s on / 0.5 s off at the scheduled 60 fps.
                                 # Frame-counter blink: draw() receives no clock
                                 # and 'time' is not in the allowed imports.
BTN_FILL      = (30, 34, 44)     # quiz button fill
BTN_FILL_SEL  = (52, 74, 112)    # selected button fill
BTN_EDGE      = (108, 114, 126)  # button frame
BTN_EDGE_SEL  = (240, 244, 250)  # selected button frame
DIM_TEXT      = (168, 178, 192)  # encouragement line / dimmed OK
FEEDBACK_PX   = 16               # feedback text size (hint / explain)

_VERT = """
#version 330
uniform vec2 u_screen;
in vec2 in_pos; in vec2 in_uv; in vec4 in_color;
out vec2 v_uv; out vec4 v_color;
void main() {
    vec2 ndc = (in_pos / u_screen) * 2.0 - 1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_uv = in_uv; v_color = in_color;
}
"""
_FRAG = """
#version 330
uniform int u_mode;              // 0 = flat shape, 1 = textured (atlas / image)
uniform sampler2D u_tex;
in vec2 v_uv; in vec4 v_color;
out vec4 f_color;
void main() {
    if (u_mode == 0) f_color = v_color;
    else             f_color = texture(u_tex, v_uv) * v_color;
}
"""


class _GlyphAtlas:
    """Letters (white + baked black stroke, tinted at draw time) and color
    emojis (Segoe UI Emoji, drawn untinted) packed into ONE RGBA texture by a
    shelf packer. uv space matches the atlas image's top-left pixel space and
    quads map their TOP edge to the cell's top uv -- consistent, no flips."""
    SIZE = 1024
    BAKE_PX = 64                 # bake big, scale down at draw (linear filter)
    STROKE = 3
    PAD = 2

    def __init__(self, ctx):
        from PIL import Image, ImageDraw, ImageFont     # atlas-build time only
        self._img = Image.new("RGBA", (self.SIZE, self.SIZE), (0, 0, 0, 0))
        self._draw = ImageDraw.Draw(self._img)
        self._font = self._try_fonts(
            ImageFont, ("segoeuib.ttf", "arialbd.ttf",
                        "DejaVuSans-Bold.ttf", "arial.ttf"))
        if self._font is None:
            raise RuntimeError("hud: no usable system TTF font found")
        self._emoji_font = self._try_fonts(ImageFont, ("seguiemj.ttf",))
        asc, desc = self._font.getmetrics()
        self.line_h = float(asc + desc)
        self._x = self._y = self._row_h = 0
        self.glyphs = {}         # ch -> (u0,v0,u1,v1,w,h,ox,oy,adv,is_color)
        self.tex = ctx.texture((self.SIZE, self.SIZE), 4)
        self.tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self._dirty = True
        for code in range(32, 127):
            self.ensure(chr(code))

    @staticmethod
    def _try_fonts(ImageFont, names):
        for name in names:
            try:
                return ImageFont.truetype(name, _GlyphAtlas.BAKE_PX)
            except OSError:
                continue
        return None

    def ensure(self, ch):
        """Bake ch into the atlas if unseen. Unbakeable chars degrade to space."""
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
        w = max(1, box[2] - box[0]); h = max(1, box[3] - box[1])
        if self._x + w + self.PAD > self.SIZE:          # new shelf row
            self._x, self._y = 0, self._y + self._row_h + self.PAD
            self._row_h = 0
        if self._y + h + self.PAD > self.SIZE:          # atlas full: degrade
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
        if self._dirty:
            self.tex.write(self._img.tobytes())
            self._dirty = False


class Hud:
    def __init__(self, window, renderer=None):
        self._ctx = renderer.ctx if renderer is not None \
            else moderngl.get_context()
        self._W = float(config.WINDOW_W)
        self._H = float(config.WINDOW_H)
        self._quiz_h = float(int(config.WINDOW_H * config.QUIZ_BAR_FRAC))
        self._prog = self._ctx.program(vertex_shader=_VERT,
                                       fragment_shader=_FRAG)
        self._prog["u_screen"].value = (self._W, self._H)
        self._prog["u_tex"].value = 0
        self._vbo = self._ctx.buffer(reserve=64 * 1024, dynamic=True)
        self._vao = self._ctx.vertex_array(
            self._prog, [(self._vbo, "2f 2f 4f", "in_pos", "in_uv", "in_color")])
        self._atlas = _GlyphAtlas(self._ctx)
        self._spec = None
        self._eq_tex = None
        self._frame = 0
        self._runs = []          # painter's draw list: [texture|None, floats]
        # quiz-bar geometry (window pixels, bottom-left origin)
        self._btn = {}
        x = 20.0
        for lab in "ABCD":
            self._btn[lab] = (x, 18.0, x + 110.0, 70.0)
            x += 124.0
        self._btn["OK"] = (530.0, 18.0, 626.0, 70.0)
        self._btn["HINT"] = (642.0, 18.0, 762.0, 70.0)
        self._msg_x0, self._msg_x1 = 782.0, self._W - 14.0

    # ------------------------------------------------------------ contract
    def set_scene(self, spec) -> None:
        """Load title_lines, equation.png, question, options, hint_lines.
        Pre-bakes every glyph the scene can show (incl. emojis)."""
        self._spec = spec
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
            from PIL import Image                       # decode at load time only
            img = Image.open(path).convert("RGBA")
            self._eq_tex = self._ctx.texture(img.size, 4, img.tobytes())
            self._eq_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)

    def hit_test(self, mx: int, my: int) -> str:
        """Mouse -> 'A'|'B'|'C'|'D'|'OK'|'HINT'|'' (window px, bottom-left)."""
        for lab, (x0, y0, x1, y1) in self._btn.items():
            if x0 <= mx <= x1 and y0 <= my <= y1:
                return lab
        return ""

    def draw(self, mode, quiz_ui_state: dict) -> None:
        """quiz_ui_state comes from game_state; hud only DRAWS (G3.7)."""
        ui = quiz_ui_state or {}
        self._frame += 1
        self._runs = []
        spec = self._spec
        qh = self._quiz_h
        if spec is not None:
            # scenario lines, white+outline, across the TOP of the graphics
            y = self._H - 8.0
            for line in list(spec.title_lines)[:config.HUD_MAX_TEXT_LINES]:
                self._text(str(line), 12.0, y,
                           config.HUD_TEXT_PX, config.HUD_TEXT_RGB)
                y -= config.HUD_LINE_PITCH_PX
            # panel titles, 14 px, bottom of each panel (equation level)
            ty = qh + 4.0 + config.HUD_TITLE_PX
            self._text(config.PANEL_TITLE_LEFT, 10.0, ty,
                       config.HUD_TITLE_PX, config.HUD_TITLE_RGB)
            self._text(config.PANEL_TITLE_RIGHT, self._W - 10.0, ty,
                       config.HUD_TITLE_PX, config.HUD_TITLE_RGB, align="right")
            # equation image: centered on the panel seam, bottom of graphics
            if self._eq_tex is not None:
                iw, ih = self._eq_tex.size
                s = min(1.0, 44.0 / ih, (self._W * 0.44) / iw)
                w, h = iw * s, ih * s
                x0 = self._W / 2.0 - w / 2.0
                y0 = qh + 8.0
                self._image(self._eq_tex, x0, y0, x0 + w, y0 + h)
        # quiz bar
        if mode == Mode.SLICE:
            self._text("🔪 Glass Blade — WASD move · ◀▶ rotate · ▲▼ tilt · "
                       "Enter play · C exit",
                       self._W / 2.0, qh - 56.0, config.HUD_TEXT_PX,
                       config.HUD_HINT_RGB, align="center")
        elif spec is not None:
            self._quiz_bar(ui, spec)
        if ui.get("campaign_complete"):
            self._win(spec)
        self._flush()

    # ------------------------------------------------------------- layers
    def _quiz_bar(self, ui, spec):
        qh = self._quiz_h
        sel, playing = ui.get("selected"), ui.get("playing")
        self._text(spec.question, 20.0, qh - 6.0,
                   config.HUD_TEXT_PX, config.HUD_TEXT_RGB)
        self._text("🎧 Listen to all four — as many times as you like.",
                   20.0, qh - 34.0, 14, DIM_TEXT)      # UPANISHADS §3: UI says so
        for lab in ("A", "B", "C", "D", "OK", "HINT"):
            x0, y0, x1, y1 = self._btn[lab]
            is_sel = (lab == sel)
            self._rect(x0, y0, x1, y1, BTN_FILL_SEL if is_sel else BTN_FILL)
            self._frame_rect(x0, y0, x1, y1,
                             BTN_EDGE_SEL if is_sel else BTN_EDGE)
            col = DIM_TEXT if (lab == "OK" and sel is None) \
                else config.HUD_TEXT_RGB
            label = "💡HINT" if lab == "HINT" else lab
            cy = (y0 + y1) / 2.0 + config.HUD_TEXT_PX / 2.0
            self._text(label, (x0 + x1) / 2.0, cy,
                       config.HUD_TEXT_PX, col, align="center")
            if playing == lab:
                self._text("🔊", x1 - 8.0, cy, 18,
                           config.HUD_TEXT_RGB, align="right")
        # feedback area (right third): green hint above pink explanation
        my = qh - 8.0
        max_w = self._msg_x1 - self._msg_x0
        if ui.get("hint_open"):
            for line in spec.hint_lines:
                for wl in self._wrap(line, FEEDBACK_PX, max_w):
                    self._text(wl, self._msg_x0, my,
                               FEEDBACK_PX, config.HUD_HINT_RGB)
                    my -= 20.0
        if ui.get("explain"):                          # kind, pink, never red
            for wl in self._wrap(ui["explain"], FEEDBACK_PX, max_w):
                self._text(wl, self._msg_x0, my,
                           FEEDBACK_PX, config.HUD_WRONG_RGB)
                my -= 20.0
        if ui.get("success") and not ui.get("campaign_complete"):
            self._text("✅ Correct!", self._msg_x0, my, 18,
                       config.HUD_HINT_RGB)
            # celebration: success_text warm yellow over the graphics
            lines = self._wrap(spec.success_text, 24, self._W * 0.7)
            y = qh + (self._H - qh) * 0.45 + len(lines) * 14.0
            for wl in lines:
                self._text(wl, self._W / 2.0, y, 24,
                           config.HUD_EQUATION_RGB, align="center")
                y -= 28.0

    def _win(self, spec):
        cy = self._H * 0.58
        if (self._frame // WIN_BLINK_FRAMES) % 2 == 0:  # blink on-phase
            self._text("YOU WIN!!!", self._W / 2.0, cy, 72,
                       config.HUD_WIN_RGB, align="center")
        if spec is not None and spec.success_text:      # closing line: steady
            y = cy - 84.0
            for wl in self._wrap(spec.success_text, 20, self._W * 0.7):
                self._text(wl, self._W / 2.0, y, 20,
                           config.HUD_TEXT_RGB, align="center")
                y -= 24.0

    # -------------------------------------------------------- primitives
    def _emit(self, tex, verts):
        if self._runs and self._runs[-1][0] is tex:
            self._runs[-1][1].extend(verts)
        else:
            self._runs.append([tex, list(verts)])

    @staticmethod
    def _quad(x0, y0, x1, y1, u0, v0, u1, v1, r, g, b, a):
        # quad TOP edge carries the cell's top uv (atlas v runs top-down)
        return [x0, y1, u0, v0, r, g, b, a,  x0, y0, u0, v1, r, g, b, a,
                x1, y0, u1, v1, r, g, b, a,  x0, y1, u0, v0, r, g, b, a,
                x1, y0, u1, v1, r, g, b, a,  x1, y1, u1, v0, r, g, b, a]

    def _rect(self, x0, y0, x1, y1, rgb, a=1.0):
        r, g, b = (c / 255.0 for c in rgb)
        self._emit(None, self._quad(x0, y0, x1, y1, 0, 0, 0, 0, r, g, b, a))

    def _frame_rect(self, x0, y0, x1, y1, rgb, t=2.0):
        self._rect(x0, y1 - t, x1, y1, rgb)
        self._rect(x0, y0, x1, y0 + t, rgb)
        self._rect(x0, y0, x0 + t, y1, rgb)
        self._rect(x1 - t, y0, x1, y1, rgb)

    def _image(self, tex, x0, y0, x1, y1, a=1.0):
        self._emit(tex, self._quad(x0, y0, x1, y1, 0.0, 0.0, 1.0, 1.0,
                                   1.0, 1.0, 1.0, a))

    def _text_w(self, s, px):
        k = px / _GlyphAtlas.BAKE_PX
        w = 0.0
        for ch in str(s):
            self._atlas.ensure(ch)
            g = self._atlas.glyphs.get(ch)
            if g is not None:
                w += g[8] * k
        return w

    def _text(self, s, x, y_top, px, rgb, align="left"):
        """One line; (x, y_top) = anchor at the TOP of the line box."""
        k = px / _GlyphAtlas.BAKE_PX
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
                                  u0, v0, u1, v1, cr, cg, cb, 1.0))
            pen += adv * k

    def _wrap(self, s, px, max_w):
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

    # -------------------------------------------------------------- flush
    def _flush(self):
        if not self._runs:
            return
        self._atlas.upload()               # lazily-baked glyphs land pre-draw
        verts, spans, first = [], [], 0
        for tex, arr in self._runs:
            n = len(arr) // 8
            spans.append((tex, first, n))
            verts.extend(arr)
            first += n
        data = np.asarray(verts, dtype="f4").tobytes()
        if len(data) > self._vbo.size:
            self._vbo.orphan(len(data))    # same GL id: VAO stays valid
        else:
            self._vbo.orphan()
        self._vbo.write(data)
        ctx = self._ctx                    # own 2D state, set every frame
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
