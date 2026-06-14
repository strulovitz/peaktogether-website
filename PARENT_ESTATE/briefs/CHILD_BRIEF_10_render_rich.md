================================================================
BRIEF #10 — THE RICH-TEXT SPINE (render_rich)

This is the most important piece in the project. It is the core primitive that all
explanation surfaces depend on. Build it carefully, but it does NOT need to be
perfect — it needs to EXIST and WORK. Stay in render.py. Do not touch combat, hub,
app, or fixtures.

WHAT YOU ARE BUILDING
A function render_rich(...) in render.py that takes a string of mixed prose + inline
math (and optional value-arcs) and produces a GL texture the rest of the engine can
blit, scale, fade, and blur. This is the foundation for "Understanding Mode" (built
later, not now).

You will build THREE functions:
  1. rich_to_surface(...)  — mixed string -> pygame Surface (the rasterizer).
  2. array_to_texture(...) — RGBA bytes -> GL texture (uploader for blurred panels).
  3. render_rich(...)      — convenience: cache + blit, mirroring draw_text_mathtext_2d.
Plus one helper: blur_surface(...) — Gaussian-blur a Surface via Pillow.

GROUND TRUTH (verbatim — do not paraphrase, reuse these exactly)

  The existing rasterizer you will mirror (render.py:407-420):

    def latex_to_surface(latex, color=(0.95, 0.96, 0.98), fontsize=15, dpi=140):
        fig = Figure(figsize=(8, 2))
        fig.patch.set_alpha(0.0)
        FigureCanvasAgg(fig)
        fig.text(0.02, 0.5, latex, fontsize=fontsize,
                 color=_rgb_to_hex(color), va="center")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, transparent=True,
                    bbox_inches="tight", pad_inches=0.06)
        buf.seek(0)
        return pygame.image.load(buf, "latex.png").convert_alpha()

  CONFIRMED FACT: matplotlib's fig.text() already renders mixed strings correctly —
  prose outside $...$ is upright text, math inside $...$ is inline, as ONE image, with
  spaces/commas/periods/apostrophes/parentheses/hyphens all surviving. The string
  "the rate of change of $\frac{dB}{dt}$ is small" produced one correct 576x69 image.
  So latex_to_surface ALREADY handles mixed prose+math. Your job is mostly arcs +
  multi-line + blur + the array uploader.

  The texture uploader (render.py:423-434):

    def surface_to_texture(surf):
        data = pygame.image.tostring(surf, "RGBA", True)     # flip Y for GL
        w, h = surf.get_size()
        tid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, data)
        return tid, w, h

  The blit helper (render.py, reuse as-is, do NOT modify):

    def draw_texture(tex, x, y, scale=1.0, alpha=1.0):
        tid, w, h = tex
        w *= scale; h *= scale
        glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, tid)
        glColor4f(1, 1, 1, alpha)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        return w, h

  Confirmed environment: numpy YES, Pillow YES, scipy NO (do NOT import scipy). No FBO
  exists — rasterize on CPU and upload, exactly like latex_to_surface already does.

TASK 1 — rich_to_surface: mixed string -> Surface, with multi-line + arcs
Rasterize a full panel (possibly many lines, possibly value-arcs) to one pygame
Surface. Do NOT word-wrap — authored lines stay as authored (panning handles overflow
later). Split lines on '\n' only.

    def rich_to_surface(text, color=(0.95, 0.96, 0.98), fontsize=15, dpi=140):
        """Rasterize mixed prose+math (with optional value-arcs) to a Surface.
        - Lines split on '\n' only. NO word-wrapping (authored layout is sacred).
        - Prose outside $...$ upright; math inside $...$ inline (fig.text does this).
        - Value-arc syntax: [[ $expr$ | value ]] -> render $expr$ with a downward
          parabola above it and `value` written above the arc.
        Returns a pygame Surface (RGBA, convert_alpha)."""

  Implementation guidance (keep it simple, make it EXIST):

  Multi-line: PREFER stacking. Render each line to its own Surface via latex_to_surface,
  then blit them onto a parent Surface top-to-bottom (parent height = sum of line
  heights; parent width = widest line; blit each at increasing y). Stacking is robust
  and lets you measure each line's pixel box (needed for arcs).

  Value-arcs ([[ $expr$ | value ]]): pre-parse each line with regex
  \[\[\s*(.*?)\s*\|\s*(.*?)\s*\]\]. For each match:
    1. Render the $expr$ part to its own Surface via latex_to_surface -> you know its
       pixel width ew and its x-position in the line.
    2. Render the value text wrapped as math (e.g. "$1.333$") to a small Surface.
    3. Draw a downward parabola (sad-mouth arc) spanning the expr's width, in a band of
       extra vertical space reserved ABOVE the line. Sample with pygame.draw.lines: for
       t in [0..1], px = x0 + t*ew, py = arc_top + arc_height*(4*(t-0.5)**2) so the
       mouth opens DOWNWARD (ends high, center low). Blit the value Surface centered
       horizontally over the arc.
    4. Arcs do NOT nest. One arc per [[...]]. Multiple non-overlapping arcs per line ok.
    Reserve a fixed vertical pad (e.g. arc_band = fontsize*2 px) above any line with an
    arc so the parabola+value have room.

  IF arcs prove too fiddly: ship lines+stacking first and leave a clear "# TODO arc".
  The spine (mixed text, multi-line, blur, upload) is what matters most. Arcs are
  engineer-panel-only and can land in a fast follow-up. Do NOT let arcs block the rest.

  The expr inside [[...]] is already substituted (fixtures provide e.g.
  [[ $\frac{2^3}{3!}$ | 1.333 ]]). You do NOT compute values. Just draw the arc + the
  given value string. No math evaluation in render.py.

TASK 2 — array_to_texture: the missing uploader
We must blur panels (Pillow gives back an image/bytes) then upload. Mirror
surface_to_texture but accept raw RGBA bytes:

    def array_to_texture(rgba_bytes, w, h):
        """Upload raw RGBA bytes (already Y-flipped for GL) as a GL texture.
        Returns (tid, w, h). Mirrors surface_to_texture's GL calls exactly."""
        tid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, rgba_bytes)
        return tid, w, h

TASK 3 — blur_surface: Gaussian blur via Pillow

    def blur_surface(surf, radius):
        """Gaussian-blur a pygame Surface using Pillow. radius=0 returns unchanged.
        Returns a NEW pygame Surface (RGBA)."""

  - Surface -> PIL: data = pygame.image.tostring(surf, "RGBA"); then
    Image.frombytes("RGBA", surf.get_size(), data).
  - from PIL import ImageFilter; img = img.filter(ImageFilter.GaussianBlur(radius)).
  - PIL -> Surface: data = img.tobytes(); then
    pygame.image.frombuffer(data, surf.get_size(), "RGBA").convert_alpha().
  - REAL Gaussian blur is required — it carries the "misty / I-don't-understand-this-
    yet" meaning. Do NOT fake it by dropping pixels.

TASK 4 — render_rich: the convenience twin of draw_text_mathtext_2d

    def render_rich(cache, text, x, y, color=(0.95, 0.96, 0.98),
                    fontsize=15, scale=1.0, alpha=1.0, blur=0.0):
        """Render mixed prose+math (and value-arcs) and blit at (x, y).
        blur > 0 applies a Gaussian blur (for out-of-focus panels).
        Must be called between begin_2d / end_2d. Returns drawn (w, h)."""

  - Add a cache method get_rich(self, text, color, fontsize, blur) to TexCache, keyed on
    (text, fontsize, color, round(blur, 1)), mirroring get_mathtext:
      * rasterize via rich_to_surface,
      * if blur > 0, blur_surface(...) it,
      * upload via surface_to_texture (it accepts a Surface).
  - Then: return draw_texture(tex, x, y, scale, alpha).
  - Build array_to_texture (Task 2) anyway; it costs nothing and Understanding Mode
    needs it later (for numpy-composited panels).

CONSTRAINTS
  - render.py ONLY. No edits to combat, hub, app, fixtures.
  - No scipy. Pillow for blur.
  - No word-wrap. Split on '\n' only.
  - Do NOT modify latex_to_surface, surface_to_texture, draw_texture,
    TexCache.get_mathtext. Add new functions/methods alongside them.
  - Reuse latex_to_surface for individual lines — it already handles mixed prose+math.
  - Cache respects the existing LIMIT/_prune pattern.

DEFINITION OF DONE
  1. render_rich(cache, "Faraday's law: $\\nabla \\times \\mathbf{E} = -\\frac{\\partial
     \\mathbf{B}}{\\partial t}$, which means a changing field induces a current.", 50, 50)
     draws ONE image: prose upright, math inline, apostrophe and comma intact.
  2. A two-line string with '\n' stacks correctly.
  3. render_rich(..., blur=4.0) visibly blurs the same text (misty, present-but-unreadable).
  4. A line with [[ $\\frac{2^3}{3!}$ | 1.333 ]] draws the expression with a downward arc
     above it and 1.333 above the arc. (Or, if deferred: clear "# TODO arc", rest working.)
  5. array_to_texture exists and uploads RGBA bytes to a drawable texture.
  6. Nothing else changed; the existing mathtext HUD still works.

FOLLOW-UPS QUEUED (do NOT start them now):
  - Understanding Mode: fullscreen 4-panel depth compositor with focus/fog, free 2D pan,
    CTRL engineer-unlock, forgiving auto lock-in/exit — built on top of render_rich.
  - Retire _mt() in combat.py -> call render_rich instead (one-line swap), once this lands.
================================================================
