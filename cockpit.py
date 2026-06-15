"""
cockpit.py -- DESCENT QED: Descent-style cockpit HUD frame.

Resolution-independent 2D cockpit overlay drawn between render.begin_2d /
render.end_2d (top-left origin, y-down). Pure legacy immediate-mode polygons
for all structure; the ONLY textures are the mathematician face portraits.

LAYOUT (matches the reference + Nir's overrides):
  * straight angled struts framing the top corners (no curves)
  * a dark dashboard band across the bottom, peaked in the middle
  * LEFT box  : black, empty, bordered -- reserved for future text
  * CENTER    : glowing gauge housing with a big number (decoration + count)
  * RIGHT box : black, bordered -- holds the 3x3 face grid (the arsenal)

Everything is a fraction of the passed (W, H); layout() recomputes on any
size change, so the cockpit re-fits at any resolution with no code edits.

PRIME LAW: no math is interpreted, no color carries meaning. Faces are
presentation only.
"""

import math
from OpenGL.GL import (
    glBegin, glEnd, glColor4f, glVertex2f,
    GL_QUADS, GL_LINE_LOOP, GL_TRIANGLE_FAN, GL_LINES,
    glDisable, glEnable, GL_TEXTURE_2D,
)

from render import draw_texture, draw_plain_text_2d
from robots import load_portrait


# ---------------------------------------------------------------------------
# COLORS (decoration only -- PRIME LAW: none of these carry meaning)
# ---------------------------------------------------------------------------
_DASH_FILL   = (0.10, 0.11, 0.13)   # dark gray dashboard
_DASH_BEVEL  = (0.30, 0.33, 0.38)   # lighter beveled edge
_BOX_FILL    = (0.02, 0.02, 0.03)   # near-black box interior
_BOX_BORDER  = (0.34, 0.37, 0.43)   # box frame
_STRUT_FILL  = (0.12, 0.13, 0.15)
_STRUT_EDGE  = (0.32, 0.35, 0.40)
_GAUGE_RING  = (0.30, 0.85, 1.00)   # the one saturated glow
_GAUGE_FILL  = (0.04, 0.06, 0.09)
_GAUGE_NUM   = (0.80, 0.95, 1.00)
_NAME_COLOR  = (0.72, 0.74, 0.80)
_SEL_COLOR   = (1.00, 0.85, 0.20)   # selected-cell highlight

# ---------------------------------------------------------------------------
# LAYOUT FRACTIONS (single source of truth -- tune the look here)
# ---------------------------------------------------------------------------
_DASH_H_FRAC   = 0.30    # dashboard height as fraction of H
_DASH_PEAK     = 0.06    # extra rise in the middle, fraction of H
_BOX_W_FRAC    = 0.26    # each side box width, fraction of W
_BOX_INSET     = 0.018   # box inset from screen edges / dashboard, frac of W
_STRUT_DEPTH   = 0.22    # how far struts reach down the sides, frac of H
_STRUT_WIDTH   = 0.16    # strut width at the top edge, frac of W
_GRID_GAP_FRAC = 0.06    # grid gap, fraction of the right box inner width
_NAME_FRAC     = 0.26    # name-strip height as fraction of the photo side


# ===========================================================================
#  POLYGON HELPERS (implemented here, immediate-mode, like render.draw_wall)
# ===========================================================================

def _filled_rect(x, y, w, h, color):
    glDisable(GL_TEXTURE_2D)
    glColor4f(color[0], color[1], color[2], color[3] if len(color) > 3 else 1.0)
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
        glVertex2f(x + i,         y + i)
        glVertex2f(x + w - i,     y + i)
        glVertex2f(x + w - i,     y + h - i)
        glVertex2f(x + i,         y + h - i)
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


def _ring(cx, cy, r, color, segments=48, width=2):
    glDisable(GL_TEXTURE_2D)
    a = color[3] if len(color) > 3 else 1.0
    for k in range(max(1, int(width))):
        rr = r - k
        glColor4f(color[0], color[1], color[2], a)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            t = 2.0 * math.pi * i / segments
            glVertex2f(cx + rr * math.cos(t), cy + rr * math.sin(t))
        glEnd()


def _disc(cx, cy, r, color, segments=48):
    glDisable(GL_TEXTURE_2D)
    a = color[3] if len(color) > 3 else 1.0
    glColor4f(color[0], color[1], color[2], a)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        t = 2.0 * math.pi * i / segments
        glVertex2f(cx + r * math.cos(t), cy + r * math.sin(t))
    glEnd()


# ===========================================================================
#  COCKPIT
# ===========================================================================

class CockpitHUD:
    def __init__(self):
        self._W = self._H = -1          # last layout size (forces first layout)
        self._L = {}                    # computed layout dict
        self._face_cache = {}           # name -> (tid, w, h) | None

    # -- public: query which face cell (0..8) a pixel is over, else None ----
    def face_at_pixel(self, mx, my):
        for i, (x, y, s, _ns) in enumerate(self._L.get("cells", [])):
            if x <= mx <= x + s and y <= my <= y + s:
                return i
        return None

    def face_cell_rects(self):
        """List of (x, y, side) photo squares -- exposed for external use."""
        return [(x, y, s) for (x, y, s, _ns) in self._L.get("cells", [])]

    def left_box_inner(self):
        """(x, y, w, h) interior of the empty left box -- for future text."""
        return self._L.get("left_inner")

    # -- main draw ----------------------------------------------------------
    def draw(self, W, H, state):
        """Draw the cockpit. Call between render.begin_2d / render.end_2d.

        state keys (all optional; missing keys degrade gracefully):
          arsenal       : list of {"id","name","png"}  (<=9)
          loaded_slot   : int index into arsenal, or -1
          vulnerable    : str | None   -> shown above left/over dashboard
          loaded_name   : str | None
          path_clear    : bool
          gauge_number  : str | None   -> big number in center gauge
          fizzle_text   : str | None
          fizzle_alpha  : float 0..1
        """
        if W != self._W or H != self._H:
            self._layout(W, H)
            self._W, self._H = W, H

        self._draw_struts()
        self._draw_dashboard()
        self._draw_left_box()
        self._draw_center_gauge(state.get("gauge_number"))
        self._draw_right_box(state.get("arsenal", []),
                             state.get("loaded_slot", -1))
        self._draw_text_regions(state)

    # -----------------------------------------------------------------------
    #  LAYOUT -- every value derived from (W, H); recomputed on size change
    # -----------------------------------------------------------------------
    def _layout(self, W, H):
        L = {}
        dash_h = _DASH_H_FRAC * H
        dash_top = H - dash_h
        peak = _DASH_PEAK * H
        L["dash"] = (dash_top, dash_h, peak)

        inset = _BOX_INSET * W
        box_w = _BOX_W_FRAC * W
        box_top = dash_top + inset
        box_h = dash_h - 2 * inset

        # LEFT box
        lx = inset
        L["left"] = (lx, box_top, box_w, box_h)
        L["left_inner"] = (lx + 6, box_top + 6, box_w - 12, box_h - 12)

        # RIGHT box
        rx = W - inset - box_w
        L["right"] = (rx, box_top, box_w, box_h)

        # CENTER gauge (between the two boxes, peaked region)
        cx = W * 0.5
        gauge_top = dash_top - peak
        gauge_r = min(box_h * 0.42, (rx - (lx + box_w)) * 0.18)
        cy = gauge_top + gauge_r + inset
        L["gauge"] = (cx, cy, gauge_r)

        # 3x3 GRID inside the RIGHT box ------------------------------------
        ix = rx + 8
        iy = box_top + 8
        iw = box_w - 16
        ih = box_h - 16

        g_w = _GRID_GAP_FRAC * iw
        s_from_w = (iw - 4 * g_w) / 3.0
        s_from_h = (ih - 4 * g_w) / (3.0 * (1.0 + _NAME_FRAC))
        s = max(8.0, min(s_from_w, s_from_h))
        n = _NAME_FRAC * s
        g = g_w

        cell_total_h = s + n
        grid_w = 3 * s + 4 * g
        grid_h = 3 * cell_total_h + 4 * g
        ox = ix + (iw - grid_w) / 2.0 + g
        oy = iy + (ih - grid_h) / 2.0 + g

        cells = []
        for i in range(9):
            col = i % 3
            row = i // 3
            x = ox + col * (s + g)
            y = oy + row * (cell_total_h + g)
            cells.append((x, y, s, n))
        L["cells"] = cells
        L["grid_dims"] = (s, n, g)

        # struts
        sw = _STRUT_WIDTH * W
        sd = _STRUT_DEPTH * H
        L["strut_w"] = sw
        L["strut_d"] = sd

        # text anchors (kept clear of boxes/grid)
        L["txt_vuln"]   = (inset + 4, inset + 2)
        L["txt_loaded"] = (inset + 4, inset + 2 + _STATUS_LINE_H)
        L["txt_fizzle"] = (W * 0.5, dash_top - peak - 2 * _STATUS_LINE_H)

        self._L = L

    # -----------------------------------------------------------------------
    #  DRAW PARTS
    # -----------------------------------------------------------------------
    def _draw_struts(self):
        W, H = self._W, self._H
        sw = self._L["strut_w"]
        sd = self._L["strut_d"]
        left = [(0, 0), (sw, 0), (0, sd)]
        _filled_poly(left, _STRUT_FILL)
        _poly_outline(left, _STRUT_EDGE)
        right = [(W, 0), (W - sw, 0), (W, sd)]
        _filled_poly(right, _STRUT_FILL)
        _poly_outline(right, _STRUT_EDGE)

    def _draw_dashboard(self):
        W, H = self._W, self._H
        dash_top, dash_h, peak = self._L["dash"]
        x0, x1 = 0, W
        mid = W * 0.5
        hump_half = W * 0.22
        pts = [
            (x0, dash_top),
            (mid - hump_half, dash_top),
            (mid, dash_top - peak),
            (mid + hump_half, dash_top),
            (x1, dash_top),
            (x1, H),
            (x0, H),
        ]
        _filled_poly(pts, _DASH_FILL)
        _poly_outline(pts, _DASH_BEVEL)

    def _draw_left_box(self):
        x, y, w, h = self._L["left"]
        _filled_rect(x, y, w, h, _BOX_FILL)
        _rect_border(x, y, w, h, _BOX_BORDER, width=2)

    def _draw_center_gauge(self, number):
        cx, cy, r = self._L["gauge"]
        _disc(cx, cy, r * 1.18, _DASH_BEVEL)
        _disc(cx, cy, r * 1.05, _GAUGE_FILL)
        _ring(cx, cy, r, _GAUGE_RING, width=3)
        _ring(cx, cy, r * 0.72, (_GAUGE_RING[0], _GAUGE_RING[1],
                                 _GAUGE_RING[2], 0.5), width=2)
        _disc(cx, cy, r * 0.30, (_GAUGE_RING[0], _GAUGE_RING[1],
                                 _GAUGE_RING[2], 0.25))
        if number is not None:
            draw_plain_text_2d(str(number), int(cx), int(cy - r - 30),
                               size=34, color=_GAUGE_NUM, align="center")

    def _draw_right_box(self, arsenal, loaded_slot):
        x, y, w, h = self._L["right"]
        _filled_rect(x, y, w, h, _BOX_FILL)
        _rect_border(x, y, w, h, _BOX_BORDER, width=2)

        cells = self._L["cells"]
        for i, (cx0, cy0, s, n) in enumerate(cells):
            if i < len(arsenal):
                name = arsenal[i]["name"]
                tex = self._get_face(name)
                if tex is not None:
                    _tid, tw, th = tex
                    scale = s / max(tw, 1)
                    draw_texture(tex, int(cx0), int(cy0), scale=scale)
                draw_plain_text_2d(name, int(cx0 + s / 2),
                                   int(cy0 + s + n * 0.15),
                                   size=max(9, int(n * 0.45)),
                                   color=_NAME_COLOR, align="center")
            if i == loaded_slot:
                _rect_border(cx0 - 2, cy0 - 2, s + 4, s + 4, _SEL_COLOR, width=2)

    def _draw_text_regions(self, state):
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
