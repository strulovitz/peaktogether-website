"""
cockpit.py -- DESCENT QED: simple Descent-style cockpit HUD.

Resolution-independent 2D overlay drawn between render.begin_2d /
render.end_2d (top-left origin, y-down). Pure legacy immediate-mode
polygons for structure; the ONLY textures are the mathematician faces.

LAYOUT (Nir's redesign):
  * ONE flat black horizontal dashboard bar across the bottom (no peak)
  * faces in ONE ROW, big, evenly spaced across the bar
  * plain-text name centered under each face
  * optional angled struts framing the top corners (STRUTS_ON to toggle)
  NO side boxes. NO gauge. NO peak.

Everything is a fraction of the passed (W, H); layout() recomputes on any
size change, so the cockpit re-fits at any resolution with no code edits.

PRIME LAW: no math interpreted, no color carries meaning. Faces are
presentation only.
"""

from OpenGL.GL import (
    glBegin, glEnd, glColor4f, glVertex2f,
    GL_QUADS, GL_LINE_LOOP, GL_TRIANGLE_FAN,
    glDisable, GL_TEXTURE_2D,
)

from render import draw_texture, draw_plain_text_2d
from robots import load_portrait


# ---------------------------------------------------------------------------
# TOGGLES
# ---------------------------------------------------------------------------
STRUTS_ON = True          # set False to remove the canopy beams entirely

# ---------------------------------------------------------------------------
# COLORS (decoration only -- none carry meaning)
# ---------------------------------------------------------------------------
_BAR_FILL    = (0.05, 0.05, 0.06)
_BAR_BORDER  = (0.30, 0.33, 0.38)
_STRUT_FILL  = (0.42, 0.44, 0.48)   # grey canopy beam
_STRUT_EDGE  = (0.58, 0.60, 0.65)   # lighter grey highlight edge
_NAME_COLOR  = (0.78, 0.80, 0.86)
_SEL_COLOR   = (1.00, 0.85, 0.20)

# ---------------------------------------------------------------------------
# CANOPY BEAM FRACTIONS (tune the look here)
# ---------------------------------------------------------------------------
_BEAM_TOP_DROP   = 0.04    # how far below the top edge the beams start, frac of H
_BEAM_TOP_THICK  = 0.07    # beam thickness at the top (lateral end), frac of W
_BEAM_FOOT_THICK = 0.05    # beam thickness where it meets the bar, frac of W

# ---------------------------------------------------------------------------
# LAYOUT FRACTIONS (tune the look here)
# ---------------------------------------------------------------------------
_BAR_H_FRAC    = 0.22    # dashboard bar height as fraction of H
_BAR_PAD_FRAC  = 0.015   # inner padding of the bar, fraction of H
_NAME_FRAC     = 0.22    # name-strip height as fraction of the face side
_GAP_FRAC      = 0.5     # horizontal gap between faces, as fraction of a face


# ===========================================================================
#  POLYGON HELPERS (immediate-mode, like render.draw_wall)
# ===========================================================================

def _filled_rect(x, y, w, h, color):
    glDisable(GL_TEXTURE_2D)
    a = color[3] if len(color) > 3 else 1.0
    glColor4f(color[0], color[1], color[2], a)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def _rect_border(x, y, w, h, color, width=1):
    glDisable(GL_TEXTURE_2D)
    a = color[3] if len(color) > 3 else 1.0
    glColor4f(color[0], color[1], color[2], a)
    for i in range(max(1, int(width))):
        glBegin(GL_LINE_LOOP)
        glVertex2f(x + i,     y + i)
        glVertex2f(x + w - i, y + i)
        glVertex2f(x + w - i, y + h - i)
        glVertex2f(x + i,     y + h - i)
        glEnd()


def _filled_poly(pts, color):
    glDisable(GL_TEXTURE_2D)
    a = color[3] if len(color) > 3 else 1.0
    glColor4f(color[0], color[1], color[2], a)
    glBegin(GL_TRIANGLE_FAN)
    for px, py in pts:
        glVertex2f(px, py)
    glEnd()


def _poly_outline(pts, color):
    glDisable(GL_TEXTURE_2D)
    a = color[3] if len(color) > 3 else 1.0
    glColor4f(color[0], color[1], color[2], a)
    glBegin(GL_LINE_LOOP)
    for px, py in pts:
        glVertex2f(px, py)
    glEnd()


# ===========================================================================
#  COCKPIT
# ===========================================================================

class CockpitHUD:
    def __init__(self):
        self._W = self._H = -1
        self._L = {}
        self._face_cache = {}

    # -- which face cell a pixel is over (0..n-1) or None -------------------
    def face_at_pixel(self, mx, my):
        for i, (x, y, s, _n) in enumerate(self._L.get("cells", [])):
            if x <= mx <= x + s and y <= my <= y + s:
                return i
        return None

    def face_cell_rects(self):
        return [(x, y, s) for (x, y, s, _n) in self._L.get("cells", [])]

    # -- main draw ----------------------------------------------------------
    def draw(self, W, H, state):
        """Call between render.begin_2d / render.end_2d.
        state keys (all optional):
          arsenal      : list of {"id","name",...}
          loaded_slot  : int | -1
          vulnerable   : str | None
          loaded_name  : str | None
          path_clear   : bool
          fizzle_text  : str | None
          fizzle_alpha : float
        """
        arsenal = state.get("arsenal", [])
        ncount = max(1, len(arsenal))
        if W != self._W or H != self._H or ncount != self._L.get("n", -1):
            self._layout(W, H, ncount)
            self._W, self._H = W, H

        if STRUTS_ON:
            self._draw_struts()
        self._draw_bar()
        self._draw_faces(arsenal, state.get("loaded_slot", -1))
        self._draw_text(state)

    # -----------------------------------------------------------------------
    #  LAYOUT -- single horizontal row of faces inside one flat bar
    # -----------------------------------------------------------------------
    def _layout(self, W, H, n):
        L = {"n": n}

        bar_h = _BAR_H_FRAC * H
        bar_top = H - bar_h
        L["bar"] = (0.0, bar_top, float(W), bar_h)

        pad = _BAR_PAD_FRAC * H
        inner_x = pad
        inner_y = bar_top + pad
        inner_w = W - 2 * pad
        inner_h = bar_h - 2 * pad

        s_from_w = inner_w / (n + (n + 1) * _GAP_FRAC)
        s_from_h = inner_h / (1.0 + _NAME_FRAC)
        s = max(8.0, min(s_from_w, s_from_h))
        n_strip = _NAME_FRAC * s
        gap = _GAP_FRAC * s

        row_w = n * s + (n + 1) * gap
        cell_h = s + n_strip
        ox = inner_x + (inner_w - row_w) / 2.0 + gap
        oy = inner_y + (inner_h - cell_h) / 2.0

        cells = []
        for i in range(n):
            x = ox + i * (s + gap)
            cells.append((x, oy, s, n_strip))
        L["cells"] = cells
        L["face_side"] = s

        # text anchors (above the bar so they never overlap the faces)
        L["txt_vuln"]   = (pad + 4, 12)
        L["txt_loaded"] = (pad + 4, 12 + _STATUS_LINE_H)
        L["txt_fizzle"] = (W * 0.5, bar_top - 3 * _STATUS_LINE_H)

        self._L = L

    # -----------------------------------------------------------------------
    #  DRAW PARTS
    # -----------------------------------------------------------------------
    def _draw_struts(self):
        """Two grey canopy beams. Tops flush to the screen sides (x=0 and
        x=W, a little below the top edge); feet land on the bar top at
        W/4 and 3W/4. Each beam is a thick slanted quad."""
        W = self._W
        _bx, bar_top, _bw, _bh = self._L["bar"]

        drop   = _BEAM_TOP_DROP * self._H
        t_top  = _BEAM_TOP_THICK * W
        t_foot = _BEAM_FOOT_THICK * W

        # --- LEFT beam: top outer at x=0, foot inner at x=W/4 ---
        l_top_out  = (0.0,        drop)
        l_top_in   = (t_top,      drop)
        l_foot_in  = (W * 0.25,           bar_top)
        l_foot_out = (W * 0.25 - t_foot,  bar_top)
        left = [l_top_out, l_top_in, l_foot_in, l_foot_out]
        _filled_poly(left, _STRUT_FILL)
        _poly_outline(left, _STRUT_EDGE)

        # --- RIGHT beam: mirror (top outer at x=W, foot inner at x=3W/4) ---
        r_top_out  = (W,          drop)
        r_top_in   = (W - t_top,  drop)
        r_foot_in  = (W * 0.75,           bar_top)
        r_foot_out = (W * 0.75 + t_foot,  bar_top)
        right = [r_top_out, r_top_in, r_foot_in, r_foot_out]
        _filled_poly(right, _STRUT_FILL)
        _poly_outline(right, _STRUT_EDGE)

    def _draw_bar(self):
        x, y, w, h = self._L["bar"]
        _filled_rect(x, y, w, h, _BAR_FILL)
        _rect_border(x, y, w, h, _BAR_BORDER, width=2)

    def _draw_faces(self, arsenal, loaded_slot):
        for i, (cx0, cy0, s, n_strip) in enumerate(self._L["cells"]):
            if i < len(arsenal):
                name = arsenal[i]["name"]
                tex = self._get_face(name)
                if tex is not None:
                    _tid, tw, _th = tex
                    scale = s / max(tw, 1)
                    draw_texture(tex, int(cx0), int(cy0), scale=scale)
                else:
                    _rect_border(cx0, cy0, s, s, _BAR_BORDER, width=1)
                draw_plain_text_2d(name, int(cx0 + s / 2),
                                   int(cy0 + s + n_strip * 0.15),
                                   size=max(10, int(n_strip * 0.5)),
                                   color=_NAME_COLOR, align="center")
            if i == loaded_slot:
                _rect_border(cx0 - 2, cy0 - 2, s + 4, s + 4, _SEL_COLOR, width=2)

    def _draw_text(self, state):
        L = self._L
        if state.get("path_clear"):
            x, y = L["txt_vuln"]
            draw_plain_text_2d("PATH CLEAR", int(x), int(y),
                               size=18, color=(0.6, 0.95, 0.6))
        else:
            vuln = state.get("vulnerable")
            if vuln:
                x, y = L["txt_vuln"]
                draw_plain_text_2d("VULNERABLE TO: " + vuln, int(x), int(y),
                                   size=18, color=(0.85, 0.85, 0.90))
        loaded = state.get("loaded_name")
        if loaded:
            x, y = L["txt_loaded"]
            draw_plain_text_2d("LOADED: " + loaded, int(x), int(y),
                               size=18, color=(0.95, 0.85, 0.55))

        ftext = state.get("fizzle_text")
        if ftext:
            x, y = L["txt_fizzle"]
            fa = state.get("fizzle_alpha", 1.0)
            draw_plain_text_2d("That technique fizzled harmlessly:",
                               int(x), int(y), size=16,
                               color=(0.95, 0.7, 0.6), align="center", alpha=fa)
            yy = y + 22
            for line in _wrap(ftext, 60):
                draw_plain_text_2d(line, int(x), int(yy), size=15,
                                   color=(0.9, 0.85, 0.8),
                                   align="center", alpha=fa)
                yy += 22

    # -----------------------------------------------------------------------
    #  FACE CACHE (load each portrait once)
    # -----------------------------------------------------------------------
    def _get_face(self, name):
        if name not in self._face_cache:
            try:
                self._face_cache[name] = load_portrait(name)
            except Exception:
                self._face_cache[name] = None
        return self._face_cache[name]


# ---------------------------------------------------------------------------
_STATUS_LINE_H = 26


def _wrap(text, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= width:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines
