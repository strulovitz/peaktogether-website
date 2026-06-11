#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
math_flyer.py — Two players, one computer, one screen, one 3D math world.
=========================================================================

PLAYER 2 ("Pilot", keyboard + T.16000M joystick) flies Descent-style with 6 DOF.
PLAYER 1 ("Manipulator", mouse + Xbox controller) drags sliders, like Manipulate[].

PAGE 1 (implemented): Harmonic series  H_N = 1 + 1/2 + 1/3 + ... + 1/N
  * Front row of bars  = the terms 1/n  (they shrink toward 0)
  * Translucent wall   = the partial sums H_n (they NEVER stop growing)
  * Amber curve        = ln(n) + gamma   (the growth law of H_n)

DEPENDENCIES:  pip install pygame PyOpenGL numpy matplotlib
RUN:           python math_flyer.py

ARCHITECTURE NOTES (for the coding agent extending this file):
  * Engine code (camera, UI, LaTeX textures) lives at the top. Do not break it.
  * To add a new demo page, copy `HarmonicSeriesPage`, decorate it with
    @register_page, implement __init__/draw_world/overlay_latex/overlay_info.
    Tab cycles pages automatically. See `TEMPLATE FOR FUTURE PAGES` at bottom.
  * Gamepad support goes ONLY inside `GamepadManager` (stub provided), which
    feeds the same `PilotCommand` / slider API used by keyboard & mouse.
"""

import io
import math
import sys
import colorsys

# ---------------------------------------------------------------- imports ---
try:
    import numpy as np
    import pygame
    from pygame.locals import (
        QUIT, KEYDOWN, VIDEORESIZE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION,
        K_ESCAPE, K_TAB, K_h, K_F1, K_i, K_r,
        K_w, K_s, K_a, K_d, K_z, K_x, K_q, K_e,
        K_UP, K_DOWN, K_LEFT, K_RIGHT, K_LSHIFT, K_RSHIFT,
        DOUBLEBUF, OPENGL, RESIZABLE,
    )
    from OpenGL.GL import *      # noqa: F401,F403  (fixed-function GL, max compat)
    from OpenGL.GLU import gluPerspective
    import matplotlib
    matplotlib.use("Agg")        # headless: we only rasterize LaTeX to images
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
except ImportError as exc:       # friendly message for the downloaders
    print("Missing dependency:", exc)
    print("Please run:  pip install pygame PyOpenGL numpy matplotlib")
    sys.exit(1)

GAMMA = 0.5772156649015329       # Euler–Mascheroni constant
CLEAR_COLOR = (0.045, 0.055, 0.10)

# =====================================================================
#  QUATERNION 6-DOF CAMERA  (the "hard part": no gimbal lock, true banking)
#  Quaternions stored as numpy arrays [w, x, y, z].
# =====================================================================

def quat_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw], dtype=float)

def quat_from_axis_angle(axis, angle):
    axis = np.asarray(axis, dtype=float)
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.array([1.0, 0, 0, 0])
    axis /= n
    h = 0.5 * angle
    return np.concatenate(([math.cos(h)], math.sin(h) * axis))

def quat_normalize(q):
    return q / np.linalg.norm(q)

def quat_rotate(q, v):
    """Rotate vector v by quaternion q (body -> world)."""
    w, x, y, z = q
    qv = np.array([x, y, z])
    t = 2.0 * np.cross(qv, v)
    return np.asarray(v, dtype=float) + w * t + np.cross(qv, t)

def quat_to_mat4(q):
    """4x4 rotation matrix R with v' = R @ v (row-major numpy convention)."""
    w, x, y, z = q
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y-w*z),   2*(x*z+w*y),   0],
        [2*(x*y+w*z),   1-2*(x*x+z*z), 2*(y*z-w*x),   0],
        [2*(x*z-w*y),   2*(y*z+w*x),   1-2*(x*x+y*y), 0],
        [0, 0, 0, 1]], dtype=np.float32)


class Ship:
    """Descent-style ship: position + orientation quaternion + inertia."""
    MAX_SPEED   = 18.0                 # units/s
    ACCEL       = 5.0                  # how snappy velocity follows input
    BOOST       = 3.0                  # Shift multiplier
    PITCH_YAW   = math.radians(95)     # rad/s from arrow keys
    ROLL_SPEED  = math.radians(140)    # rad/s from Q/E
    MOUSE_SENS  = 0.0022               # rad per mouse pixel (RMB held)

    HOME_POS = np.array([11.0, 4.0, 30.0])

    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = self.HOME_POS.copy()
        self.q   = np.array([1.0, 0, 0, 0])
        self.vel = np.zeros(3)

    def rotate_local(self, axis, angle):
        """Rotate about the ship's OWN axis -> correct banked flight."""
        if abs(angle) > 1e-9:
            self.q = quat_normalize(quat_mul(self.q, quat_from_axis_angle(axis, angle)))

    def update(self, dt, keys, mouse_dx, mouse_dy, mouse_look, invert_pitch, gp=None):
        # --- rotation -------------------------------------------------
        pitch = (keys[K_UP] - keys[K_DOWN]) * self.PITCH_YAW * dt
        yaw   = (keys[K_LEFT] - keys[K_RIGHT]) * self.PITCH_YAW * dt
        roll  = (keys[K_q] - keys[K_e]) * self.ROLL_SPEED * dt
        if mouse_look:
            yaw   += -mouse_dx * self.MOUSE_SENS
            mp     = -mouse_dy * self.MOUSE_SENS
            pitch += -mp if invert_pitch else mp
        if gp:                                       # gamepad axes (additive)
            pitch += gp.get('pitch', 0) * self.PITCH_YAW * dt
            yaw   += gp.get('yaw', 0)   * self.PITCH_YAW * dt
            roll  += gp.get('roll', 0)  * self.ROLL_SPEED * dt
        self.rotate_local([1, 0, 0], pitch)   # local X = pitch (nose up/down)
        self.rotate_local([0, 1, 0], yaw)     # local Y = yaw  (turn)
        self.rotate_local([0, 0, 1], roll)    # local Z = bank (Q/E)

        # --- translation (thrust in BODY frame, like Descent) ----------
        thrust = np.array([
            float(keys[K_d] - keys[K_a]),     # strafe right/left
            float(keys[K_z] - keys[K_x]),     # slide up/down  (Z up, X down)
            float(keys[K_s] - keys[K_w]),     # forward is -Z in OpenGL
        ])
        if gp:
            thrust += np.array(gp.get('thrust_xyz', (0, 0, 0)))  # gamepad additive
        n = np.linalg.norm(thrust)
        if n > 1e-9:
            thrust /= n
        boost = self.BOOST if (keys[K_LSHIFT] or keys[K_RSHIFT]) else 1.0
        target = quat_rotate(self.q, thrust) * self.MAX_SPEED * boost
        self.vel += (target - self.vel) * min(1.0, self.ACCEL * dt)  # inertia
        self.pos += self.vel * dt

    def apply_view(self):
        """Load the inverse (view) transform onto the GL modelview stack.
        Note: GL reads numpy memory column-major, i.e. as the TRANSPOSE of
        our row-major R — which is exactly the inverse rotation we need."""
        glLoadIdentity()
        glMultMatrixf(np.ascontiguousarray(quat_to_mat4(self.q)))
        glTranslatef(*(-self.pos))


# =====================================================================
#  LaTeX -> OpenGL texture pipeline (matplotlib mathtext, no LaTeX needed)
# =====================================================================

def latex_to_surface(latex, fontsize=15, color="#F2F4FA", dpi=140):
    """Rasterize a mathtext string to a transparent pygame surface.
    bbox_inches='tight' auto-measures the formula -> version-robust."""
    fig = Figure(figsize=(8, 2))
    fig.patch.set_alpha(0.0)
    FigureCanvasAgg(fig)
    fig.text(0.02, 0.5, latex, fontsize=fontsize, color=color, va="center")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=True,
                bbox_inches="tight", pad_inches=0.06)
    buf.seek(0)
    return pygame.image.load(buf, "latex.png").convert_alpha()

def surface_to_texture(surf):
    data = pygame.image.tostring(surf, "RGBA", True)   # flipped -> GL origin
    w, h = surf.get_size()
    tid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, data)
    return tid, w, h


class TexCache:
    """Caches rendered textures so LaTeX/text is rasterized only once."""
    LIMIT = 400

    def __init__(self):
        self.cache = {}
        self.fonts = {}

    def _font(self, size, bold):
        key = (size, bold)
        if key not in self.fonts:
            f = pygame.font.Font(None, size)
            f.set_bold(bold)
            self.fonts[key] = f
        return self.fonts[key]

    def _prune(self):
        if len(self.cache) > self.LIMIT:
            for tid, _, _ in self.cache.values():
                glDeleteTextures([tid])
            self.cache.clear()

    def latex(self, s, fontsize=15, color="#F2F4FA"):
        key = ("L", s, fontsize, color)
        if key not in self.cache:
            self._prune()
            self.cache[key] = surface_to_texture(
                latex_to_surface(s, fontsize, color))
        return self.cache[key]

    def text(self, s, size=20, color=(225, 228, 238), bold=False):
        key = ("T", s, size, color, bold)
        if key not in self.cache:
            self._prune()
            surf = self._font(size, bold).render(s, True, color)
            self.cache[key] = surface_to_texture(surf)
        return self.cache[key]


# ------------------------------ 2D overlay drawing helpers -----------------

def begin_2d(w, h):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, w, h, 0, -1, 1)                       # y-down = mouse coords
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_FOG)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

def end_2d():
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()
    glEnable(GL_DEPTH_TEST)

def draw_rect(x, y, w, h, color, alpha=1.0):
    glDisable(GL_TEXTURE_2D)
    glColor4f(color[0], color[1], color[2], alpha)
    glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x + w, y)
    glVertex2f(x + w, y + h); glVertex2f(x, y + h)
    glEnd()

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


def draw_latex_3d(tex, cx, y_bottom, z, height):
    """Draw a cached (tid, w, h) texture as a flat quad in the world's
    x-y plane: horizontally centered at cx, sitting on y_bottom.
    Used for labels INSIDE the 3D figure (call every frame, NOT inside
    display lists -- the texture cache may recycle texture ids)."""
    tid, w, h = tex
    ww = height * (w / float(h))
    x0 = cx - ww / 2.0
    glDisable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tid)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(x0, y_bottom, z)
    glTexCoord2f(1, 0); glVertex3f(x0 + ww, y_bottom, z)
    glTexCoord2f(1, 1); glVertex3f(x0 + ww, y_bottom + height, z)
    glTexCoord2f(0, 1); glVertex3f(x0, y_bottom + height, z)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)


# =====================================================================
#  Mouse UI: Manipulate-style sliders (Player 1)
# =====================================================================

class Slider:
    SLOT_H = 56

    def __init__(self, label, vmin, vmax, value, step=None, fmt=None):
        self.label, self.vmin, self.vmax, self.step = label, vmin, vmax, step
        self.fmt = fmt or ("{:.0f}" if step else "{:.2f}")
        self.track = pygame.Rect(0, 0, 10, 6)
        self.dragging = False
        self._value = value
        self.set_value(value)

    @property
    def value(self):
        return self._value

    def set_value(self, v):
        v = max(self.vmin, min(self.vmax, v))
        if self.step:
            v = self.vmin + round((v - self.vmin) / self.step) * self.step
            v = max(self.vmin, min(self.vmax, v))
        self._value = v

    def nudge(self, amount):
        """Hook for future gamepad: move slider by analog amount."""
        self.set_value(self._value + amount * (self.vmax - self.vmin))

    def press(self, pos):
        if self.track.inflate(14, 22).collidepoint(pos):
            self.dragging = True
            self.drag_to(pos[0])
            return True
        return False

    def drag_to(self, mx):
        frac = (mx - self.track.x) / max(1, self.track.w)
        self.set_value(self.vmin + max(0.0, min(1.0, frac)) * (self.vmax - self.vmin))


class UIPanel:
    WIDTH, PAD = 318, 16

    def __init__(self):
        self.sliders = []

    def set_sliders(self, sliders):
        self.sliders = sliders

    def layout(self, sw, sh):
        x = sw - self.WIDTH - 14
        y = 64
        for s in self.sliders:
            s.track.update(x + self.PAD, y + 34, self.WIDTH - 2 * self.PAD, 6)
            y += Slider.SLOT_H
        self.rect = pygame.Rect(sw - self.WIDTH - 14, 50, self.WIDTH,
                                len(self.sliders) * Slider.SLOT_H + 24)

    def handle_event(self, ev):
        """Returns True if the UI consumed the event (Player 1's mouse)."""
        if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
            return any(s.press(ev.pos) for s in self.sliders)
        if ev.type == MOUSEMOTION:
            hit = False
            for s in self.sliders:
                if s.dragging:
                    s.drag_to(ev.pos[0])
                    hit = True
            return hit
        if ev.type == MOUSEBUTTONUP and ev.button == 1:
            for s in self.sliders:
                s.dragging = False
        return False

    def draw(self, tex):
        draw_rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h,
                  (0.06, 0.07, 0.12), 0.78)
        draw_texture(tex.text("Manipulate  (Player 1: mouse)", 22, (140, 200, 255), True),
                     self.rect.x + self.PAD, self.rect.y + 4)
        for s in self.sliders:
            t = s.track
            draw_texture(tex.text(s.label, 21), t.x, t.y - 26)
            val = tex.text(s.fmt.format(s.value), 21, (255, 214, 120), True)
            draw_texture(val, t.right - val[1], t.y - 26)
            draw_rect(t.x, t.y, t.w, t.h, (0.30, 0.32, 0.40))           # track
            frac = (s.value - s.vmin) / (s.vmax - s.vmin)
            draw_rect(t.x, t.y, t.w * frac, t.h, (0.20, 0.65, 0.95))    # fill
            kx = t.x + t.w * frac
            draw_rect(kx - 6, t.y - 7, 12, 20,
                      (1, 1, 1) if s.dragging else (0.85, 0.88, 0.95))  # knob


# =====================================================================
#  3D drawing primitives
# =====================================================================

def draw_box(x0, y0, z0, x1, y1, z1):
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(x0, y1, z0); glVertex3f(x0, y1, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    glNormal3f(0, -1, 0)
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
    glNormal3f(0, 0, 1)
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    glNormal3f(0, 0, -1)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y0, z0)
    glNormal3f(1, 0, 0)
    glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x1, y0, z1)
    glNormal3f(-1, 0, 0)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    glEnd()

def draw_floor_grid(x_max=320.0):
    glDisable(GL_LIGHTING)
    glColor4f(0.22, 0.26, 0.36, 1.0)
    glBegin(GL_LINES)
    z0, z1, step = -36.0, 36.0, 4.0
    x = -24.0
    while x <= x_max:
        glVertex3f(x, 0, z0); glVertex3f(x, 0, z1)
        x += step
    z = z0
    while z <= z1:
        glVertex3f(-24.0, 0, z); glVertex3f(x_max, 0, z)
        z += step
    glEnd()
    glEnable(GL_LIGHTING)


# =====================================================================
#  PAGE SYSTEM — the extension point for all future demos
# =====================================================================

PAGES = []

def register_page(cls):
    PAGES.append(cls)
    return cls


class Page:
    """Base class. Subclass me for every new Wikipedia section."""
    TITLE = "Untitled page"

    def __init__(self):
        self.sliders = []

    def draw_world(self):            # 3D content (camera already applied)
        pass

    def overlay_latex(self):         # list of (mathtext_string, fontsize)
        return []

    def overlay_info(self):          # list of plain-text status lines
        return []


@register_page
class HarmonicSeriesPage(Page):
    """PAGE 1 — https://en.wikipedia.org/wiki/Harmonic_series_(mathematics)
    Definition and divergence."""
    TITLE = "Harmonic Series  —  Definition & Divergence"
    N_CAP = 2000

    def __init__(self):
        super().__init__()
        # partial[n] = H_n, with partial[0] = 0
        self.partial = np.concatenate(
            ([0.0], np.cumsum(1.0 / np.arange(1, self.N_CAP + 1))))
        self.s_n     = Slider("Terms  N", 1, 150, 12, step=1)
        self.s_sp    = Slider("Bar spacing", 0.8, 4.0, 1.6)
        self.s_wall  = Slider("Partial-sum wall opacity", 0.0, 1.0, 0.45)
        self.s_curve = Slider("Show  ln N + gamma  curve", 0, 1, 1, step=1)
        self.sliders = [self.s_n, self.s_sp, self.s_wall, self.s_curve]

    # ----------------------------------------------------------- 3D ---
    def draw_world(self):
        N, sp = int(self.s_n.value), self.s_sp.value
        draw_floor_grid(max(60.0, (N + 4) * sp))

        # Front row: the TERMS 1/n  (opaque, rainbow gradient)
        hw = 0.36 * sp
        for n in range(1, N + 1):
            hue = 0.58 - 0.50 * (n - 1) / max(1, N - 1)
            r, g, b = colorsys.hsv_to_rgb(hue % 1.0, 0.75, 0.95)
            glColor4f(r, g, b, 1.0)
            x = n * sp
            draw_box(x - hw, 0.0, -0.6, x + hw, 1.0 / n, 0.6)

        # Back row: the PARTIAL SUMS H_n (translucent wall, draw last)
        alpha = self.s_wall.value
        if alpha > 0.01:
            glDepthMask(GL_FALSE)
            glColor4f(0.25, 0.80, 1.0, 0.55 * alpha)
            for n in range(1, N + 1):
                x = n * sp
                draw_box(x - hw, 0.0, -4.4, x + hw, self.partial[n], -3.2)
            glDepthMask(GL_TRUE)

        # Growth law: y = ln(x) + gamma
        if self.s_curve.value >= 0.5 and N >= 2:
            glDisable(GL_LIGHTING)
            glLineWidth(3.0)
            glColor4f(1.0, 0.72, 0.20, 1.0)
            glBegin(GL_LINE_STRIP)
            for t in np.linspace(1.0, N, 160):
                glVertex3f(t * sp, math.log(t) + GAMMA, -3.8)
            glEnd()
            glLineWidth(1.0)
            glEnable(GL_LIGHTING)

    # ------------------------------------------------------ overlays ---
    def overlay_latex(self):
        N = int(self.s_n.value)
        H = self.partial[N]
        if N <= 7:
            terms = " + ".join(
                "1" if n == 1 else r"\frac{1}{%d}" % n for n in range(1, N + 1))
        else:
            terms = (r"1 + \frac{1}{2} + \frac{1}{3} + \frac{1}{4} + "
                     r"\cdots + \frac{1}{%d}" % N)
        return [
            (r"$H_N \,=\, \sum_{n=1}^{N} \frac{1}{n}"
             r" \,=\, 1+\frac{1}{2}+\frac{1}{3}+\frac{1}{4}+\frac{1}{5}+\cdots$", 16),
            (r"$H_{%d} \,=\, %s \,\approx\, %.4f$" % (N, terms, H), 14),
            (r"$H_N \to \infty \quad\mathrm{(divergent!)}\qquad"
             r" H_N \approx \ln N + \gamma,\;\; \gamma \approx 0.5772$", 13),
        ]

    def overlay_info(self):
        N = int(self.s_n.value)
        H = self.partial[N]
        law = math.log(N) + GAMMA if N >= 1 else 0.0
        return [
            "H_%d = %.4f      ln(N) + gamma = %.4f      error = %.4f"
            % (N, H, law, H - law),
            "Blue wall = partial sums: it grows FOREVER (slowly, like ln N).",
        ]


# =====================================================================
#  TEMPLATE FOR FUTURE PAGES  (for the coding agent — copy, rename, fill)
#  Planned future pages (one class each, same pattern):
#    IntegralTestPage, GrowthRatePage, DivisibilityPage, InterpolationPage,
#    RamanujanSummationPage, CrossingDesertPage, StackingBlocksPage,
#    CountingPrimesPage, CouponCollectorPage, AlgorithmAnalysisPage
# =====================================================================

@register_page
class ComparisonTestPage(Page):
    """PAGE 2 — Comparison test (Nicole Oresme, ~1350).
    Faithful 3D version of the Wikipedia figure for 'Harmonic series':
      * GREY adjacent bars of unit width: bar n spans x in (n-1, n], height 1/n,
        so the AREA of bar n equals the term 1/n.
      * BLUE outlined rectangles: rectangle j spans (2^(j-1), 2^j], height 1/2^j
        -> width * height = 2^(j-1) * 2^(-j) = 1/2. EVERY blue rectangle has
        area exactly 1/2, and the grey bars always poke above it.
      * RED curve y = 1/x, dashed gridlines at 1/2, 1/4, 1/8, ...,
        x-axis ticks at the powers of two.
    Wikipedia caption: 'There are infinite blue rectangles each with area 1/2,
    yet their total area is exceeded by that of the grey bars denoting the
    harmonic series.'

    ENGINE NOTE: geometry is compiled into a GL display list, rebuilt only
    when a slider changes (this page draws up to 256 bars). Future heavy
    pages should copy this trick.
    """
    TITLE = "Comparison Test (Oresme, ~1350)  —  Blue Rectangles of Area 1/2"
    K_MAX = 8                                   # up to 2^8 = 256 bars

    def __init__(self):
        super().__init__()
        n = np.arange(1, 2 ** self.K_MAX + 1)
        self.partial = np.concatenate(([0.0], np.cumsum(1.0 / n)))
        self.s_k    = Slider("Groups  k   (N = 2^k bars)", 1, self.K_MAX, 5, step=1)
        self.s_sp   = Slider("Horizontal scale", 0.5, 2.5, 1.2)
        self.s_fill = Slider("Blue fill opacity", 0.0, 1.0, 0.30)
        self.s_hl   = Slider("Highlight rectangle (0 = all)", 0, self.K_MAX, 0, step=1)
        self.sliders = [self.s_k, self.s_sp, self.s_fill, self.s_hl]
        self._cache_key = None
        self._dlist = None

    # ----------------------------------------------------------- 3D ---
    def draw_world(self):
        key = (int(self.s_k.value), round(self.s_sp.value, 3),
               round(self.s_fill.value, 2), int(self.s_hl.value))
        if key != self._cache_key:              # rebuild only on slider change
            if self._dlist is not None:
                glDeleteLists(self._dlist, 1)
            self._dlist = glGenLists(1)
            glNewList(self._dlist, GL_COMPILE)
            self._build_scene(*key)
            glEndList()
            self._cache_key = key
        glCallList(self._dlist)

    def _build_scene(self, k, sp, fill_alpha, hl):
        N = 2 ** k
        draw_floor_grid(max(60.0, (N + 4) * sp))
        gap = 0.04 * sp                          # thin gaps, as in the figure

        # --- GREY bars: bar n spans x in (n-1, n], height 1/n -------------
        glColor4f(0.78, 0.78, 0.81, 1.0)
        for n in range(1, N + 1):
            draw_box((n - 1) * sp + gap, 0.0, -0.6,
                     n * sp - gap, 1.0 / n, 0.6)

        # --- flat 'figure' elements: no lighting, like a drawing ----------
        glDisable(GL_LIGHTING)

        # axes (white) with ticks at the powers of two: 1, 2, 4, 8, ...
        glLineWidth(2.0)
        glColor4f(0.92, 0.92, 0.95, 1.0)
        glBegin(GL_LINES)
        glVertex3f(-0.6 * sp, 0.0, 0.65); glVertex3f((N + 1.5) * sp, 0.0, 0.65)
        glVertex3f(0.0, 0.0, 0.65);       glVertex3f(0.0, 1.65, 0.65)
        for j in range(0, k + 1):                # ticks at x = 2^j  (and x=1)
            x = (2 ** j) * sp
            glVertex3f(x, 0.0, 0.65); glVertex3f(x, -0.14, 0.65)
        glEnd()

        # dashed grey gridlines at y = 1/2, 1/4, ..., 1/2^k  (and y = 1)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(2, 0x00FF)
        glLineWidth(1.5)
        glColor4f(0.55, 0.55, 0.60, 0.9)
        glBegin(GL_LINES)
        for j in range(0, k + 1):
            y = 2.0 ** (-j)
            glVertex3f(0.0, y, 0.65); glVertex3f(N * sp, y, 0.65)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

        # RED curve  y = 1/x  (passes through the top-right corner of each bar)
        glLineWidth(3.0)
        glColor4f(0.93, 0.18, 0.12, 1.0)
        glBegin(GL_LINE_STRIP)
        for t in np.linspace(0.625, N + 1.0, 260):   # start where y = 1.6
            glVertex3f(t * sp, 1.0 / t, 0.7)
        glEnd()

        # --- BLUE rectangles: group j spans (2^(j-1), 2^j], height 1/2^j ---
        #     width * height = 2^(j-1) * 2^(-j) = 1/2   (EVERY one, area 1/2)
        def blue_of(j):
            if hl == 0 or j == hl:
                return (0.36, 0.36, 0.96)
            return (0.36 * 0.35, 0.36 * 0.35, 0.96 * 0.45)   # dimmed

        if fill_alpha > 0.01:                    # translucent fill, in front
            glDepthMask(GL_FALSE)
            for j in range(1, k + 1):
                r, g, b = blue_of(j)
                a = fill_alpha * (1.0 if (hl == 0 or j == hl) else 0.35)
                glColor4f(r, g, b, a)
                x0, x1 = (2 ** (j - 1)) * sp, (2 ** j) * sp
                y1 = 2.0 ** (-j)
                glBegin(GL_QUADS)
                glVertex3f(x0, 0.0, 0.72); glVertex3f(x1, 0.0, 0.72)
                glVertex3f(x1, y1, 0.72);  glVertex3f(x0, y1, 0.72)
                glEnd()
            glDepthMask(GL_TRUE)

        glLineWidth(3.5)                         # thick blue outlines
        for j in range(1, k + 1):
            glColor4f(*blue_of(j), 1.0)
            x0, x1 = (2 ** (j - 1)) * sp, (2 ** j) * sp
            y1 = 2.0 ** (-j)
            glBegin(GL_LINE_LOOP)
            glVertex3f(x0, 0.0, 0.74); glVertex3f(x1, 0.0, 0.74)
            glVertex3f(x1, y1, 0.74);  glVertex3f(x0, y1, 0.74)
            glEnd()

        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------ overlays ---
    def overlay_latex(self):
        k = int(self.s_k.value)
        N = 2 ** k
        H = self.partial[N]
        return [
            # Wikipedia line 1: replace each denominator by the next power of 2
            # (bold = the replaced ones; mathtext has no per-symbol color)
            (r"$1+\frac{1}{2}+\frac{1}{3}+\frac{1}{4}+\frac{1}{5}+\frac{1}{6}"
             r"+\frac{1}{7}+\frac{1}{8}+\frac{1}{9}+\cdots"
             r"\;\geq\;1+\frac{1}{2}+\frac{1}{\mathbf{4}}+\frac{1}{4}"
             r"+\frac{1}{\mathbf{8}}+\frac{1}{\mathbf{8}}+\frac{1}{\mathbf{8}}"
             r"+\frac{1}{8}+\frac{1}{\mathbf{16}}+\cdots$", 13),
            # Wikipedia line 2: grouping equal terms
            (r"$1+\left(\frac{1}{2}\right)+\left(\frac{1}{4}+\frac{1}{4}\right)"
             r"+\left(\frac{1}{8}+\frac{1}{8}+\frac{1}{8}+\frac{1}{8}\right)"
             r"+\left(\frac{1}{16}+\cdots+\frac{1}{16}\right)+\cdots"
             r"\;=\;1+\frac{1}{2}+\frac{1}{2}+\frac{1}{2}+\frac{1}{2}+\cdots$", 12),
            # Wikipedia line 3 (Oresme's bound), with live numbers
            (r"$\sum_{n=1}^{2^{%d}}\frac{1}{n} \;=\; H_{%d} \approx %.4f"
             r"\;\geq\;1+\frac{%d}{2} \;=\; %.1f$"
             % (k, N, H, k, 1.0 + 0.5 * k), 14),
        ]

    def overlay_info(self):
        k = int(self.s_k.value)
        N = 2 ** k
        lines = [
            "There are infinite blue rectangles each with area 1/2, yet their total",
            "area is exceeded by that of the grey bars denoting the harmonic series.",
            "Red curve: y = 1/x.   Original proof: Nicole Oresme, around 1350.",
        ]
        hl = int(self.s_hl.value)
        if hl:
            lines.append(
                "Blue rectangle %d: width %d  x  height 1/%d  =  area 1/2 exactly.%s"
                % (hl, 2 ** (hl - 1), 2 ** hl,
                   "" if hl <= k else "   (raise the k slider to see it!)"))
        return lines


@register_page
class IntegralTestPage(Page):
    """PAGE 3 — Integral test. Faithful 3D version of the Wikipedia figure:
    'Rectangles with area given by the harmonic series, and the hyperbola
    y = 1/x through the upper left corners of these rectangles.'
      * Cream rectangles, 1 unit wide, 1/n high, on white 'paper', with
        black outlines, black axes, black corner dots -- figure colors.
      * Crimson curve y = 1/x through the upper-LEFT corners (n, 1/n).
      * 'Shift rectangles left' slider: drag 0 -> 1 and the rectangles
        slide one unit left, dropping BELOW the curve. That slide IS the
        proof of:  integral(1..N+1) < H_N < integral(1..N) + 1.
    Geometry uses the standard display-list cache (rebuilt on slider change).
    """
    TITLE = "Integral Test  --  H_N Trapped Between Two Integrals"
    N_CAP = 80

    def __init__(self):
        super().__init__()
        self.tex = None                          # set by App (Patch C)
        n = np.arange(1, self.N_CAP + 1)
        self.partial = np.concatenate(([0.0], np.cumsum(1.0 / n)))
        self.s_n     = Slider("Rectangles  N", 1, self.N_CAP, 6, step=1)
        self.s_shift = Slider("Shift rectangles left", 0.0, 1.0, 0.0)
        self.s_sp    = Slider("Horizontal scale", 0.6, 2.5, 1.4)
        self.s_fill  = Slider("Rectangle fill opacity", 0.0, 1.0, 0.90)
        self.sliders = [self.s_n, self.s_shift, self.s_sp, self.s_fill]
        self._cache_key = None
        self._dlist = None

    # ----------------------------------------------------------- 3D ---
    def draw_world(self):
        N, sp = int(self.s_n.value), round(self.s_sp.value, 3)
        shift, fill = round(self.s_shift.value, 3), round(self.s_fill.value, 2)
        key = (N, sp, shift, fill)
        if key != self._cache_key:
            if self._dlist is not None:
                glDeleteLists(self._dlist, 1)
            self._dlist = glGenLists(1)
            glNewList(self._dlist, GL_COMPILE)
            self._build_scene(N, sp, shift, fill)
            glEndList()
            self._cache_key = key
        glCallList(self._dlist)

        # --- LaTeX labels, every frame (textures cached, quads are cheap) --
        if self.tex is None:
            return
        ink, crimson = "#1A1A1A", "#B5093D"
        for n in range(1, min(N, 5) + 1):        # term labels, as in figure
            lab = r"$1$" if n == 1 else r"$\frac{1}{%d}$" % n
            draw_latex_3d(self.tex.latex(lab, 16, ink),
                          (n + 0.5 - shift) * sp, 1.0 / n + 0.06, 0.8,
                          0.17 if n == 1 else 0.27)
        draw_latex_3d(self.tex.latex(r"$y=\frac{1}{x}$", 16, crimson),
                      1.7 * sp, 1.85, 0.8, 0.42)
        for i in range(0, min(N + 1, 8) + 1):    # x-axis numbers 0,1,2,...
            cx = -0.18 * sp if i == 0 else i * sp
            draw_latex_3d(self.tex.latex(r"$%d$" % i, 14, ink),
                          cx, -0.34, 0.8, 0.18)
        draw_latex_3d(self.tex.latex(r"$1$", 14, ink),    # y-axis tick label
                      -0.24 * sp, 0.92, 0.8, 0.18)
        draw_latex_3d(self.tex.latex(r"$x$", 16, ink),
                      (N + 1.55) * sp, -0.34, 0.8, 0.18)
        draw_latex_3d(self.tex.latex(r"$y$", 16, ink),
                      -0.26 * sp, 2.06, 0.8, 0.18)

    def _build_scene(self, N, sp, shift, fill):
        draw_floor_grid(max(60.0, (N + 4) * sp))

        glDisable(GL_LIGHTING)
        # white 'paper' behind the whole figure (so black ink works)
        glColor4f(0.965, 0.950, 0.915, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(-1.2 * sp, -0.45, -0.75); glVertex3f((N + 2) * sp, -0.45, -0.75)
        glVertex3f((N + 2) * sp, 2.30, -0.75); glVertex3f(-1.2 * sp, 2.30, -0.75)
        glEnd()

        # black axes with ticks at the integers
        glLineWidth(2.5)
        glColor4f(0.07, 0.07, 0.08, 1.0)
        glBegin(GL_LINES)
        glVertex3f(-0.6 * sp, 0.0, -0.7); glVertex3f((N + 1.7) * sp, 0.0, -0.7)
        glVertex3f(0.0, -0.3, -0.7);      glVertex3f(0.0, 2.15, -0.7)
        for i in range(1, N + 2):                 # x ticks
            glVertex3f(i * sp, 0.0, -0.7); glVertex3f(i * sp, -0.09, -0.7)
        glVertex3f(0.0, 1.0, -0.7); glVertex3f(-0.09 * sp, 1.0, -0.7)  # y tick
        glEnd()
        glEnable(GL_LIGHTING)

        # cream rectangles: rectangle n spans x in [n-shift, n+1-shift]
        if fill > 0.01:
            translucent = fill < 0.99
            if translucent:
                glDepthMask(GL_FALSE)
            glColor4f(0.99, 0.93, 0.76, fill)
            for n in range(1, N + 1):
                draw_box((n - shift) * sp, 0.0, -0.5,
                         (n + 1 - shift) * sp, 1.0 / n, 0.5)
            if translucent:
                glDepthMask(GL_TRUE)

        glDisable(GL_LIGHTING)
        # black outlines on the rectangle fronts (always visible)
        glLineWidth(2.5)
        glColor4f(0.07, 0.07, 0.08, 1.0)
        for n in range(1, N + 1):
            x0, x1 = (n - shift) * sp, (n + 1 - shift) * sp
            glBegin(GL_LINE_LOOP)
            glVertex3f(x0, 0.0, 0.55); glVertex3f(x1, 0.0, 0.55)
            glVertex3f(x1, 1.0 / n, 0.55); glVertex3f(x0, 1.0 / n, 0.55)
            glEnd()

        # crimson hyperbola y = 1/x
        glLineWidth(3.5)
        glColor4f(0.71, 0.04, 0.24, 1.0)
        glBegin(GL_LINE_STRIP)
        for t in np.linspace(0.45, N + 1.3, 280):
            glVertex3f(t * sp, 1.0 / t, 0.6)
        glEnd()

        # black dots on the curve at (n, 1/n) -- the upper-left corners
        glColor4f(0.05, 0.05, 0.06, 1.0)
        for n in range(1, N + 1):
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(n * sp, 1.0 / n, 0.62)
            for i in range(17):
                a = 2.0 * math.pi * i / 16
                glVertex3f(n * sp + 0.05 * math.cos(a),
                           1.0 / n + 0.05 * math.sin(a), 0.62)
            glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------ overlays ---
    def overlay_latex(self):
        N = int(self.s_n.value)
        H = self.partial[N]
        return [
            (r"$\int_{1}^{\infty}\frac{1}{x}\,dx \;=\; \infty"
             r"\qquad\Rightarrow\qquad \sum_{n=1}^{\infty}\frac{1}{n}"
             r"\;\mathrm{diverges}$", 15),
            (r"$\int_{1}^{N+1}\frac{1}{x}\,dx \;<\; \sum_{i=1}^{N}\frac{1}{i}"
             r" \;<\; \int_{1}^{N}\frac{1}{x}\,dx \,+\, 1$", 15),
            (r"$\ln %d = %.4f \;<\; H_{%d} = %.4f \;<\; 1+\ln %d = %.4f$"
             % (N + 1, math.log(N + 1), N, H, N, 1.0 + math.log(N)), 13),
        ]

    def overlay_info(self):
        s = self.s_shift.value
        lines = [
            "Rectangles with area given by the harmonic series, and the hyperbola",
            "y = 1/x through the upper left corners of these rectangles.  (Wikipedia)",
        ]
        if s < 0.05:
            lines.append("Curve BELOW the rectangle tops -> area under curve < sum."
                         "  But that integral is INFINITE -> the sum diverges!")
        elif s > 0.95:
            lines.append("Shifted left by 1 unit: rectangles now lie BELOW the curve"
                         " -> sum < integral + 1.  Together: the sandwich above.")
        else:
            lines.append("Sliding left... (%.2f of 1 unit)  Watch the rectangles"
                         " duck under the curve." % s)
        return lines


@register_page
class PartialSumsPage(Page):
    """PAGE 4 — Partial sums (harmonic numbers) + Growth rate.
    Faithful 3D version of Wikipedia's partial-sums TABLE: rows n = 1..20
    with H_n as an exact fraction, as a decimal, and as the grey
    'relative size' bar (length H_n). Exact fractions via fractions.Fraction.
    Growth rate (Euler-Maclaurin):  H_n = ln n + gamma + 1/(2n) - eps_n,
    with 0 <= eps_n <= 1/(8 n^2). The 'Approximation' slider overlays
    curves through the bar tips: 1 = ln n (red, misses all tips by the
    SAME gap), 2 = ln n + gamma (amber, the gap IS gamma), 3 = + 1/(2n)
    (cyan, nails them). Standard display-list cache; labels drawn per
    frame with draw_latex_3d (never inside the list).
    """
    TITLE = "Partial Sums  H_n  —  Growth Rate  ln n + gamma"
    N_MAX = 20
    RH = 0.55                                   # row height

    def __init__(self):
        super().__init__()
        from fractions import Fraction
        self.tex = None
        self.fracs, f = [], Fraction(0)
        for n in range(1, self.N_MAX + 1):
            f += Fraction(1, n)
            self.fracs.append(f)
        self.H = [float(f) for f in self.fracs]
        self.s_rows  = Slider("Table rows  n", 1, self.N_MAX, self.N_MAX, step=1)
        self.s_scale = Slider("Bar scale", 1.0, 3.0, 2.0)
        self.s_fit   = Slider("Approximation  (0=off 1=ln 2=+g 3=+1/2n)",
                              0, 3, 0, step=1)
        self.s_hl    = Slider("Highlight row (0 = none)", 0, self.N_MAX, 0, step=1)
        self.sliders = [self.s_rows, self.s_scale, self.s_fit, self.s_hl]
        self._cache_key = None
        self._dlist = None

    def _y(self, n):                            # row 1 on top, like the table
        return (self.N_MAX - n) * self.RH

    def _dec_str(self, n):                      # Wikipedia-style decimals
        d = self.fracs[n - 1].denominator
        while d % 2 == 0: d //= 2
        while d % 5 == 0: d //= 5
        if d == 1:                              # terminates: only n = 1, 2, 6
            return "%g" % self.H[n - 1]
        return "~%.5f" % self.H[n - 1]

    # ----------------------------------------------------------- 3D ---
    def draw_world(self):
        N, s = int(self.s_rows.value), round(self.s_scale.value, 3)
        mode, hl = int(self.s_fit.value), int(self.s_hl.value)
        key = (N, s, mode, hl)
        if key != self._cache_key:
            if self._dlist is not None:
                glDeleteLists(self._dlist, 1)
            self._dlist = glGenLists(1)
            glNewList(self._dlist, GL_COMPILE)
            self._build_scene(N, s, mode, hl)
            glEndList()
            self._cache_key = key
        glCallList(self._dlist)

        # ---- table text, every frame (textures cached) -------------------
        if self.tex is None:
            return
        ink = "#1A1A1A"
        for label, cx in (("n", -5.0), ("fraction", -3.6),
                          ("decimal", -1.3), ("relative size", 1.6)):
            draw_latex_3d(self.tex.text(label, 15, ink, True),
                          cx, self._y(1) + 0.62, 0.4, 0.24)
        for n in range(1, N + 1):
            y = self._y(n)
            draw_latex_3d(self.tex.text(str(n), 15, ink), -5.0, y, 0.4, 0.26)
            fr = self.fracs[n - 1]
            if n == 1:
                draw_latex_3d(self.tex.latex(r"$1$", 14, ink),
                              -3.6, y, 0.4, 0.26)
            else:
                draw_latex_3d(self.tex.latex(
                    r"$\frac{%d}{%d}$" % (fr.numerator, fr.denominator),
                    13, ink), -3.6, y - 0.05, 0.4, 0.40)
            draw_latex_3d(self.tex.text(self._dec_str(n), 15, ink),
                          -1.3, y, 0.4, 0.26)
        if mode >= 2:                           # the gap between red and amber
            draw_latex_3d(self.tex.latex(r"$\gamma$", 16, "#E8A33D"),
                          (math.log(N) + GAMMA / 2.0) * s,
                          self._y(N) - 0.42, 0.4, 0.30)

    def _build_scene(self, N, s, mode, hl):
        draw_floor_grid(40.0)
        top = self._y(1) + 1.05
        xr = max(self.H[self.N_MAX - 1] * s + 0.9, 8.0)

        glDisable(GL_LIGHTING)
        glColor4f(0.965, 0.950, 0.915, 1.0)     # paper
        glBegin(GL_QUADS)
        glVertex3f(-5.8, -0.7, -0.75); glVertex3f(xr, -0.7, -0.75)
        glVertex3f(xr, top, -0.75);    glVertex3f(-5.8, top, -0.75)
        glEnd()
        glLineWidth(1.5)                         # table grid, light grey
        glColor4f(0.72, 0.72, 0.74, 1.0)
        glBegin(GL_LINES)
        for n in range(1, N + 1):                # row separators
            glVertex3f(-5.6, self._y(n) - 0.12, -0.7)
            glVertex3f(xr - 0.2, self._y(n) - 0.12, -0.7)
        glVertex3f(-5.6, self._y(1) + 0.50, -0.7)        # header underline
        glVertex3f(xr - 0.2, self._y(1) + 0.50, -0.7)
        for cx in (-4.55, -2.50, -0.35):         # column separators
            glVertex3f(cx, self._y(N) - 0.12, -0.7)
            glVertex3f(cx, self._y(1) + 0.50, -0.7)
        glEnd()
        glEnable(GL_LIGHTING)

        for n in range(1, N + 1):                # grey 'relative size' bars
            if hl == 0 or n == hl:
                glColor4f(0.62, 0.62, 0.66, 1.0)
            else:
                glColor4f(0.80, 0.79, 0.77, 1.0)         # dimmed vs paper
            if n == hl:
                glColor4f(0.93, 0.62, 0.18, 1.0)         # highlighted: amber
            y0 = self._y(n)
            draw_box(0.0, y0, -0.18, self.H[n - 1] * s, y0 + 0.30, 0.18)

        glDisable(GL_LIGHTING)
        if mode >= 1:                            # approximation curves
            curves = [((0.85, 0.22, 0.18), lambda t: math.log(t))]
            if mode >= 2:
                curves.append(((1.00, 0.70, 0.20),
                               lambda t: math.log(t) + GAMMA))
            if mode >= 3:
                curves.append(((0.15, 0.78, 0.88),
                               lambda t: math.log(t) + GAMMA + 0.5 / t))
            glLineWidth(3.0)
            for col, f in curves:
                glColor4f(*col, 1.0)
                glBegin(GL_LINE_STRIP)
                for t in np.linspace(1.0, N, 240):
                    glVertex3f(f(t) * s, (self.N_MAX - t) * self.RH + 0.15, 0.3)
                glEnd()
            if mode >= 2:                        # gamma gap marker, bottom row
                yg = self._y(N) - 0.30
                glLineWidth(2.0)
                glColor4f(1.0, 0.70, 0.20, 1.0)
                glBegin(GL_LINES)
                glVertex3f(math.log(N) * s, yg, 0.3)
                glVertex3f((math.log(N) + GAMMA) * s, yg, 0.3)
                glEnd()
        glColor4f(0.05, 0.05, 0.06, 1.0)         # black dots on the bar tips
        for n in range(1, N + 1):
            x, y = self.H[n - 1] * s, self._y(n) + 0.15
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(x, y, 0.32)
            for i in range(17):
                a = 2.0 * math.pi * i / 16
                glVertex3f(x + 0.06 * math.cos(a), y + 0.06 * math.sin(a), 0.32)
            glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------ overlays ---
    def overlay_latex(self):
        N = int(self.s_rows.value)
        n = int(self.s_hl.value) or N
        fr = self.fracs[n - 1]
        out = [
            (r"$H_n = \sum_{k=1}^{n}\frac{1}{k}$", 16),
            (r"$H_n = \ln n + \gamma + \frac{1}{2n} - \varepsilon_n,"
             r"\qquad 0 \leq \varepsilon_n \leq \frac{1}{8n^2},"
             r"\qquad \gamma \approx 0.5772$", 14),
        ]
        if n == 1:
            out.append((r"$H_1 = 1$", 14))
        else:
            out.append((r"$H_{%d} = \frac{%d}{%d} \approx %.5f$"
                        % (n, fr.numerator, fr.denominator, self.H[n - 1]), 14))
        return out

    def overlay_info(self):
        N, mode = int(self.s_rows.value), int(self.s_fit.value)
        lines = [
            "Adding the first n terms produces a partial sum, called a harmonic",
            "number, H_n.  The grey bars are Wikipedia's 'relative size' column.",
            "Logarithmic crawl: to push H_n past 10 you need n = 12367 terms!",
        ]
        if mode >= 1:
            approx = [math.log(N), math.log(N) + GAMMA,
                      math.log(N) + GAMMA + 0.5 / N]
            txt = "At n=%d:  ln n = %.5f" % (N, approx[0])
            if mode >= 2: txt += "   +gamma = %.5f" % approx[1]
            if mode >= 3: txt += "   +1/(2n) = %.5f" % approx[2]
            lines.append(txt + "   vs  H_%d = %.5f" % (N, self.H[N - 1]))
        hl = int(self.s_hl.value)
        if hl:
            eps = math.log(hl) + GAMMA + 0.5 / hl - self.H[hl - 1]
            lines.append("Row %d:  eps_%d = %.6f  (bound 1/(8n^2) = %.6f).%s"
                         % (hl, hl, eps, 1.0 / (8.0 * hl * hl),
                            "  Terminating decimal!" if hl in (1, 2, 6) else ""))
        return lines


@register_page
class DivisibilityPage(Page):
    """PAGE 5 — Divisibility: no harmonic number except H_1 = 1 is an
    integer. ORIGINAL visualization (Wikipedia has no figure here):
    write H_n = sum_i (M/i)/M with M = lcm(1..n). Column i carries one
    blue cube per factor of 2 in the numerator M/i, i.e. nu2(M/i)
    = k - nu2(i) cubes, where 2^k is the highest power of two <= n.
    EXACTLY ONE column is cube-less (i = 2^k): the only ODD numerator
    (red wireframe). Sum of numerators = evens + one odd = ODD, over the
    EVEN denominator M -> never an integer. A 'Subtract H_m' slider
    shows the stronger fact: no two harmonic numbers differ by an
    integer (exact Fractions). Standard display-list cache.
    """
    TITLE = "Divisibility  —  No  H_n  Is an Integer (except H_1 = 1)"
    N_MAX = 20

    def __init__(self):
        super().__init__()
        from fractions import Fraction
        self.tex = None
        self.fracs, f = [], Fraction(0)
        for n in range(1, self.N_MAX + 1):
            f += Fraction(1, n)
            self.fracs.append(f)
        self.M = [1]                              # M[n-1] = lcm(1..n)
        for n in range(2, self.N_MAX + 1):
            m = self.M[-1]
            self.M.append(m * n // math.gcd(m, n))
        self.S = [sum(self.M[n - 1] // i for i in range(1, n + 1))
                  for n in range(1, self.N_MAX + 1)]   # numerator sums
        self.s_n  = Slider("Terms  n", 1, self.N_MAX, 10, step=1)
        self.s_dx = Slider("Column spacing", 0.8, 2.0, 1.2)
        self.s_m  = Slider("Subtract H_m (0 = off)", 0, self.N_MAX - 1, 0,
                           step=1)
        self.sliders = [self.s_n, self.s_dx, self.s_m]
        self._cache_key = None
        self._dlist = None

    @staticmethod
    def _nu2(x):                                  # factors of 2 in x
        c = 0
        while x % 2 == 0:
            x //= 2
            c += 1
        return c

    # ----------------------------------------------------------- 3D ---
    def draw_world(self):
        n, dx = int(self.s_n.value), round(self.s_dx.value, 3)
        key = (n, dx)
        if key != self._cache_key:
            if self._dlist is not None:
                glDeleteLists(self._dlist, 1)
            self._dlist = glGenLists(1)
            glNewList(self._dlist, GL_COMPILE)
            self._build_scene(n, dx)
            glEndList()
            self._cache_key = key
        glCallList(self._dlist)

        # ---- labels, every frame (light ink: open dark world, no paper) --
        if self.tex is None:
            return
        k = n.bit_length() - 1                   # 2^k = top power of two <= n
        M = self.M[n - 1]
        for i in range(1, n + 1):
            x = i * dx
            draw_latex_3d(self.tex.text(str(i), 14, "#D8DCE8"),
                          x, -0.50, 0.3, 0.24)   # index below column
            num = M // i
            col = "#FF6B5E" if num % 2 == 1 else "#7FD49A"
            top = (k - self._nu2(i)) * 0.45      # numerator above, staggered
            draw_latex_3d(self.tex.text(str(num), 12, col),
                          x, top + 0.22 + (i % 2) * 0.32, 0.3, 0.22)
        if n > 1:
            draw_latex_3d(self.tex.latex(r"$i = 2^{%d} = %d$" % (k, 2 ** k),
                                         14, "#FF6B5E"),
                          (2 ** k) * dx, -0.95, 0.3, 0.30)

    def _build_scene(self, n, dx):
        draw_floor_grid(max(30.0, (n + 2) * dx))
        k = n.bit_length() - 1
        glColor4f(0.16, 0.18, 0.26, 1.0)         # base tiles
        for i in range(1, n + 1):
            x = i * dx
            draw_box(x - 0.3, -0.08, -0.3, x + 0.3, 0.0, 0.3)
        glColor4f(0.42, 0.60, 0.95, 1.0)         # blue cubes = factors of 2
        for i in range(1, n + 1):
            x = i * dx
            for j in range(k - self._nu2(i)):
                draw_box(x - 0.2, j * 0.45, -0.2,
                         x + 0.2, j * 0.45 + 0.40, 0.2)
        # red wireframe on the unique cube-less column  i = 2^k
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
        glColor4f(1.0, 0.32, 0.25, 1.0)
        x = (2 ** k) * dx
        h = max(k * 0.45, 0.5)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x - 0.28, 0.0, 0.25); glVertex3f(x + 0.28, 0.0, 0.25)
        glVertex3f(x + 0.28, h, 0.25);   glVertex3f(x - 0.28, h, 0.25)
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------ overlays ---
    def overlay_latex(self):
        n = int(self.s_n.value)
        out = [(r"$H_n = \sum_{i=1}^{n}\frac{M/i}{M},"
                r"\qquad M = \mathrm{lcm}(1,\ldots,n)$", 15)]
        if n == 1:
            out.append((r"$H_1 = 1$"
                        r"\qquad \mathrm{(the\ only\ integer\ }H_n)$", 14))
        else:
            out.append((r"$M = %d\ \mathrm{(even)},\qquad"
                        r"\sum_{i=1}^{%d} M/i = %d\ \mathrm{(odd)}"
                        r"\qquad\Rightarrow\qquad"
                        r"H_{%d} = \frac{\mathrm{odd}}{\mathrm{even}}$"
                        % (self.M[n - 1], n, self.S[n - 1], n), 13))
        m = int(self.s_m.value)
        if 0 < m < n:
            d = self.fracs[n - 1] - self.fracs[m - 1]
            out.append((r"$H_{%d} - H_{%d} = \frac{%d}{%d}"
                        r"\;\neq\;\mathrm{integer}$"
                        % (n, m, d.numerator, d.denominator), 13))
        return out

    def overlay_info(self):
        n = int(self.s_n.value)
        k = n.bit_length() - 1
        lines = [
            "Each blue cube = one factor of 2 left in the numerator M/i.",
            "Exactly ONE column has no cubes: i = 2^%d = %d -> the only ODD"
            " numerator." % (k, 2 ** k),
            "Evens + one odd = odd sum, over even denominator M: never an"
            " integer.",
            "2nd proof: some prime n/2 < p <= n divides the denominator"
            " (Bertrand's postulate).",
            "Only H_1 = 1, H_2 = 1.5, H_6 = 2.45 terminate as decimals"
            " (remember page 4!).",
        ]
        m = int(self.s_m.value)
        if m >= n and m > 0:
            lines.append("Subtract slider: choose m < n to compare"
                         " (currently m = %d >= n = %d)." % (m, n))
        return lines


@register_page
class InterpolationPage(Page):
    """PAGE 6 — Interpolation (digamma) + Ramanujan summation.
    Exhibit 1: Wikipedia's digamma 'painting' — domain coloring of
      psi(z) over Re,Im in [-6,6]. Computed with numpy (recurrence
      psi(z) = psi(z+1) - 1/z until Re >= 15, then asymptotic series),
      hue = arg psi(z), uploaded ONCE as a page-owned GL texture
      (deliberately NOT in TexCache -> can never be recycled).
    Exhibit 2: white-paper graph of H_x = psi(x+1) + gamma (crimson)
      threading exactly through black dots (n, H_n); blue bead slider
      rides the curve (exact H_{1/2} = 2 - 2 ln 2 at x = 1/2).
      'Show ln x' toggle: the gap curve-minus-ln(x) shrinks toward
      gamma — the Ramanujan value of the divergent harmonic series.
    Standard display-list cache for the graph; painting drawn per frame
    (one textured quad, opacity slider stays live).
    """
    TITLE = "Interpolation (Digamma)  +  Ramanujan Summation"
    PS, PCX, PCY, PZ = 0.85, 3.1, 6.4, -3.0    # painting scale/center/z

    def __init__(self):
        super().__init__()
        self.tex = None
        self._painting = None                   # needs GL -> built lazily
        n = np.arange(1, 10)
        self.Hn = np.concatenate(([0.0], np.cumsum(1.0 / n)))   # H_0..H_9
        self.xs = np.linspace(0.0, 8.3, 320)
        self.ys = self._digamma(self.xs + 1.0).real + GAMMA
        self.s_x  = Slider("Marker x  (interpolated H_x)", 0.0, 8.0, 2.5)
        self.s_ln = Slider("Show ln x + gamma gap (0/1)", 0, 1, 0, step=1)
        self.s_op = Slider("Color plot opacity", 0.0, 1.0, 1.0)
        self.sliders = [self.s_x, self.s_ln, self.s_op]
        self._cache_key = None
        self._dlist = None

    # ------------------------------------------------- digamma maths ---
    @staticmethod
    def _digamma(z):
        """Vectorized complex digamma: recurrence + asymptotic series."""
        z = np.array(z, dtype=np.complex128, ndmin=1, copy=True)
        res = np.zeros_like(z)
        for _ in range(15):                     # psi(z) = psi(z+1) - 1/z
            m = z.real < 15.0
            if not m.any():
                break
            res[m] -= 1.0 / z[m]
            z[m] += 1.0
        inv = 1.0 / z
        i2 = inv * inv
        res += np.log(z) - 0.5 * inv \
               - i2 * (1.0/12.0 - i2 * (1.0/120.0 - i2 / 252.0))
        return res

    def _H(self, x):                            # H_x = psi(x+1) + gamma
        return float(self._digamma(np.array([x + 1.0]))[0].real) + GAMMA

    def _make_painting(self):
        from matplotlib.colors import hsv_to_rgb
        res = 512
        t = (np.arange(res) + 0.5) / res * 12.0 - 6.0    # pixel centers:
        Z = t[None, :] + 1j * (-t[:, None])              # never hits a pole
        W = self._digamma(Z)
        hue = (np.angle(W) / (2.0 * math.pi)) % 1.0
        one = np.ones_like(hue)
        rgb = (hsv_to_rgb(np.dstack([hue, one, one])) * 255).astype(np.uint8)
        surf = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
        return surface_to_texture(surf)

    # ----------------------------------------------------------- 3D ---
    def draw_world(self):
        x, ln_on = round(self.s_x.value, 3), int(self.s_ln.value)
        key = (x, ln_on)
        if key != self._cache_key:
            if self._dlist is not None:
                glDeleteLists(self._dlist, 1)
            self._dlist = glGenLists(1)
            glNewList(self._dlist, GL_COMPILE)
            self._build_scene(x, ln_on)
            glEndList()
            self._cache_key = key
        glCallList(self._dlist)

        # ---- the painting (page-owned texture, opacity slider live) -----
        if self._painting is None:
            self._painting = self._make_painting()       # one-time, ~0.5 s
        op = self.s_op.value
        hw = 6.0 * self.PS
        x0, x1 = self.PCX - hw, self.PCX + hw
        y0, y1 = self.PCY - hw, self.PCY + hw
        if op > 0.01:
            glDisable(GL_LIGHTING)
            glColor4f(0.97, 0.97, 0.97, op)              # white margins
            glBegin(GL_QUADS)
            glVertex3f(x0 - 0.9, y0 - 1.0, self.PZ - 0.05)
            glVertex3f(x1 + 0.5, y0 - 1.0, self.PZ - 0.05)
            glVertex3f(x1 + 0.5, y1 + 0.6, self.PZ - 0.05)
            glVertex3f(x0 - 0.9, y1 + 0.6, self.PZ - 0.05)
            glEnd()
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self._painting[0])
            glColor4f(1, 1, 1, op)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex3f(x0, y0, self.PZ)
            glTexCoord2f(1, 0); glVertex3f(x1, y0, self.PZ)
            glTexCoord2f(1, 1); glVertex3f(x1, y1, self.PZ)
            glTexCoord2f(0, 1); glVertex3f(x0, y1, self.PZ)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_LIGHTING)

        # ---- labels, every frame ----------------------------------------
        if self.tex is None:
            return
        ink = "#1A1A1A"
        if op > 0.3:                                     # painting ticks
            for v in (-6, -4, -2, 0, 2, 4, 6):
                draw_latex_3d(self.tex.text(str(v), 13, ink),
                              self.PCX + v * self.PS, y0 - 0.42,
                              self.PZ - 0.02, 0.26)
                draw_latex_3d(self.tex.text(str(v), 13, ink),
                              x0 - 0.45, self.PCY + v * self.PS - 0.12,
                              self.PZ - 0.02, 0.26)
            draw_latex_3d(self.tex.text("Re(z)", 13, ink),
                          self.PCX, y0 - 0.80, self.PZ - 0.02, 0.26)
            draw_latex_3d(self.tex.text("Im(z)", 13, ink),
                          x0 - 0.45, y1 + 0.18, self.PZ - 0.02, 0.26)
        for i in range(1, 9):                            # graph x ticks
            draw_latex_3d(self.tex.text(str(i), 13, ink),
                          float(i), -0.32, -0.5, 0.20)
        for n in range(1, 5):                            # a few dot labels
            draw_latex_3d(self.tex.latex(r"$H_%d$" % n, 13, ink),
                          float(n) - 0.30, self.Hn[n] + 0.10, -0.5, 0.24)
        if ln_on:
            draw_latex_3d(self.tex.latex(r"$\to \gamma$", 15, "#E8A33D"),
                          8.05, 0.5 * (math.log(7.6) + self._H(7.6)) - 0.12,
                          -0.45, 0.30)

    def _build_scene(self, x, ln_on):
        draw_floor_grid(40.0)
        glDisable(GL_LIGHTING)
        glColor4f(0.965, 0.950, 0.915, 1.0)              # graph paper
        glBegin(GL_QUADS)
        glVertex3f(-0.9, -0.7, -0.65); glVertex3f(9.0, -0.7, -0.65)
        glVertex3f(9.0, 3.4, -0.65);   glVertex3f(-0.9, 3.4, -0.65)
        glEnd()
        glLineWidth(2.5)                                 # black axes
        glColor4f(0.07, 0.07, 0.08, 1.0)
        glBegin(GL_LINES)
        glVertex3f(-0.5, 0.0, -0.6); glVertex3f(8.7, 0.0, -0.6)
        glVertex3f(0.0, -0.4, -0.6); glVertex3f(0.0, 3.2, -0.6)
        for i in range(1, 9):
            glVertex3f(float(i), 0.0, -0.6); glVertex3f(float(i), -0.09, -0.6)
        for j in (1, 2, 3):
            glVertex3f(0.0, float(j), -0.6); glVertex3f(-0.09, float(j), -0.6)
        glEnd()
        if ln_on:                                        # grey dashed ln x
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(2, 0x0F0F)
            glLineWidth(2.5)
            glColor4f(0.35, 0.40, 0.50, 1.0)
            glBegin(GL_LINE_STRIP)
            for t in self.xs[self.xs >= 0.62]:
                glVertex3f(t, math.log(t), -0.55)
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            glLineWidth(3.0)                             # amber gap at x=7.6
            glColor4f(1.0, 0.70, 0.20, 1.0)
            glBegin(GL_LINES)
            glVertex3f(7.6, math.log(7.6), -0.5)
            glVertex3f(7.6, self._H(7.6), -0.5)
            glEnd()
        glLineWidth(3.5)                                 # crimson H_x curve
        glColor4f(0.71, 0.04, 0.24, 1.0)
        glBegin(GL_LINE_STRIP)
        for t, yv in zip(self.xs, self.ys):
            glVertex3f(t, yv, -0.55)
        glEnd()
        glColor4f(0.05, 0.05, 0.06, 1.0)                 # dots (n, H_n)
        for n in range(0, 9):
            self._disk(float(n), self.Hn[n], -0.5, 0.06)
        bx, by = x, self._H(x)                           # blue bead + drop
        glColor4f(0.15, 0.35, 0.85, 1.0)
        self._disk(bx, by, -0.45, 0.10)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(1, 0x00FF)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex3f(bx, 0.0, -0.5); glVertex3f(bx, by, -0.5)
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    @staticmethod
    def _disk(cx, cy, z, r):
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(cx, cy, z)
        for i in range(17):
            a = 2.0 * math.pi * i / 16
            glVertex3f(cx + r * math.cos(a), cy + r * math.sin(a), z)
        glEnd()

    # ------------------------------------------------------ overlays ---
    def overlay_latex(self):
        x = self.s_x.value
        out = [
            (r"$\psi(x) = \frac{d}{dx}\ln\Gamma(x)"
             r" = \frac{\Gamma'(x)}{\Gamma(x)}$", 15),
            (r"$\psi(n) = H_{n-1} - \gamma \qquad\Rightarrow\qquad"
             r" H_x = \psi(x+1) + \gamma$", 14),
            (r"$\sum_{n \geq 1}^{\mathcal{R}} \frac{1}{n}"
             r" = \gamma \approx 0.57722$", 14),
        ]
        if abs(x - 0.5) < 0.03:
            out.append((r"$H_{1/2} = 2 - 2\ln 2 \approx 0.61371$", 14))
        elif abs(x - round(x)) < 0.02 and round(x) >= 1:
            n = int(round(x))
            out.append((r"$H_{%d} = %.5f$" % (n, self.Hn[n]), 14))
        else:
            out.append((r"$H_{%.2f} = \psi(%.2f) + \gamma = %.5f$"
                        % (x, x + 1.0, self._H(x)), 14))
        return out

    def overlay_info(self):
        lines = [
            '"The color representation of the Digamma function in a',
            ' rectangular region of the complex plane."  (Wikipedia)',
            "As Gamma interpolates factorials, digamma interpolates harmonic",
            "numbers: the crimson curve threads through EVERY dot (n, H_n).",
            "Painting: rainbow pinwheels = poles at 0, -1, -2, ...; the big",
            "swirl near 1.46163 is digamma's only positive real zero.",
        ]
        if int(self.s_ln.value):
            lines.append("Gap (curve minus ln x) sinks toward gamma = 0.57722"
                         " — the Ramanujan value of the divergent series!")
        return lines


@register_page
class JeepProblemPage(Page):
    """PAGE 7 — Applications: Crossing a desert (jeep problem).
    Faithful, ANIMATED version of Wikipedia's n=3 figure: white paper,
    black road, green jeep, blue-rimmed depot cylinders labeled with
    EXACT fuel fractions (Fraction arithmetic -> the figure's 2/3, 1/2,
    1/3, 1/6, 1/4 appear verbatim), blue double-arrow spacing labels
    1/(2n), 1/(2(n-1)), ..., 1/2 below the road.
    'Mission progress' scrubs the whole optimal mission: on each trip
    the jeep tops up s_i at depot i (outbound AND on return), drops
    1 - 2*s_k at the new depot k, and the final trip reaches
    (r/2) H_n -- every drop of fuel exactly consumed at the end.
    Light scene -> immediate drawing, no display list. Exact protocol
    verified against the figure's five snapshots.
    """
    TITLE = "Crossing a Desert  —  the Jeep Problem  (reach = r/2 * H_n)"

    def __init__(self):
        super().__init__()
        self.tex = None
        self._sims = {}
        self.s_n  = Slider("Fuel loads  n", 1, 6, 3, step=1)
        self.s_t  = Slider("Mission progress (scrub!)", 0.0, 1.0, 0.0)
        self.s_sc = Slider("Road scale", 6.0, 14.0, 10.0)
        self.sliders = [self.s_n, self.s_t, self.s_sc]

    # ------------------------------------------------ exact simulation ---
    def _sim(self, n):
        if n in self._sims:
            return self._sims[n]
        from fractions import Fraction as F
        s = [F(1, 2 * (n - i)) for i in range(n)]     # 1/(2n) ... 1/2
        P, acc = [], F(0)
        for sp in s:
            acc += sp
            P.append(acc)                             # depot / turnaround pos
        depots = [F(0)] * max(n - 1, 0)
        placed = [None] * max(n - 1, 0)
        evs, odo = [], F(0)                           # (odo,pos,fuel,depots,trip)
        def ev(pos, fuel, trip):
            evs.append((odo, pos, fuel, tuple(depots), trip))
        for k in range(1, n + 1):
            fuel, pos = F(1), F(0)
            ev(pos, fuel, k)                          # depart base, tank full
            for i in range(k):                        # ---- outbound
                odo += s[i]; pos = P[i]; fuel -= s[i]
                ev(pos, fuel, k)
                if i < k - 1:                         # top up s_i at depot i
                    depots[i] -= s[i]; fuel += s[i]
                    ev(pos, fuel, k)
                elif k < n:                           # place new depot k
                    drop = F(1) - 2 * s[k - 1]
                    depots[k - 1] += drop; fuel -= drop
                    placed[k - 1] = float(odo)
                    ev(pos, fuel, k)
            for i in range(k - 1, -1, -1):            # ---- return
                odo += s[i]
                pos = P[i - 1] if i > 0 else F(0)
                fuel -= s[i]
                ev(pos, fuel, k)
                if i > 0:                             # take s_(i-1) to go on
                    depots[i - 1] -= s[i - 1]; fuel += s[i - 1]
                    ev(pos, fuel, k)
        sim = {"evs": evs, "total": float(odo), "s": s, "P": P,
               "placed": placed}
        self._sims[n] = sim
        return sim

    @staticmethod
    def _state(sim, o):
        evs = sim["evs"]
        j = 0
        for i, e in enumerate(evs):
            if float(e[0]) <= o + 1e-12:
                j = i
        odo_j, pos_j, fuel_j, dep_j, trip = evs[j]
        if j == len(evs) - 1:
            return float(pos_j), float(fuel_j), dep_j, trip
        odo_k, pos_k = float(evs[j + 1][0]), float(evs[j + 1][1])
        d = o - float(odo_j)
        span = odo_k - float(odo_j)
        f = d / span if span > 1e-12 else 0.0
        pos = float(pos_j) + (pos_k - float(pos_j)) * f
        return pos, float(fuel_j) - d, dep_j, trip

    # ------------------------------------------------------------ 3D ---
    def draw_world(self):
        n, sc = int(self.s_n.value), self.s_sc.value
        sim = self._sim(n)
        o = self.s_t.value * sim["total"]
        pos, fuel, depots, trip = self._state(sim, o)
        end = float(sim["P"][-1]) * sc

        draw_floor_grid(max(30.0, end + 6.0))
        glDisable(GL_LIGHTING)
        glColor4f(0.965, 0.955, 0.935, 1.0)            # paper
        glBegin(GL_QUADS)
        glVertex3f(-2.0, -1.7, -0.8); glVertex3f(end + 2.0, -1.7, -0.8)
        glVertex3f(end + 2.0, 3.4, -0.8); glVertex3f(-2.0, 3.4, -0.8)
        glEnd()
        glLineWidth(5.0)                               # black road
        glColor4f(0.05, 0.05, 0.06, 1.0)
        glBegin(GL_LINES)
        glVertex3f(-0.8, 0.0, -0.4); glVertex3f(end + 0.8, 0.0, -0.4)
        glEnd()
        glLineWidth(2.0)                               # blue spacing arrows
        glColor4f(0.35, 0.55, 0.85, 1.0)
        x_prev = 0.0
        for i in range(n):
            x_i = float(sim["P"][i]) * sc
            glBegin(GL_LINES)
            glVertex3f(x_prev, -0.8, -0.4); glVertex3f(x_i, -0.8, -0.4)
            for xa, dr in ((x_prev, 1.0), (x_i, -1.0)):    # arrowheads
                glVertex3f(xa, -0.8, -0.4)
                glVertex3f(xa + 0.22 * dr, -0.66, -0.4)
                glVertex3f(xa, -0.8, -0.4)
                glVertex3f(xa + 0.22 * dr, -0.94, -0.4)
            glEnd()
            x_prev = x_i
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)
        glColor4f(0.30, 0.30, 0.34, 1.0)               # base marker
        draw_box(-0.30, 0.0, -0.3, 0.05, 1.0, 0.3)
        for i in range(n - 1):                         # depot cylinders
            if sim["placed"][i] is not None and o >= sim["placed"][i] - 1e-9:
                self._cylinder(float(sim["P"][i]) * sc, 0.42, 0.62)
        self._jeep(pos * sc)

        glDisable(GL_LIGHTING)                         # fuel gauge
        jx = pos * sc
        glColor4f(0.25, 0.25, 0.28, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(jx - 0.5, 1.05, 0.3); glVertex3f(jx + 0.5, 1.05, 0.3)
        glVertex3f(jx + 0.5, 1.23, 0.3); glVertex3f(jx - 0.5, 1.23, 0.3)
        glEnd()
        glColor4f(0.15, 0.62, 0.30, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(jx - 0.5, 1.05, 0.3)
        glVertex3f(jx - 0.5 + max(fuel, 0.0), 1.05, 0.3)
        glVertex3f(jx - 0.5 + max(fuel, 0.0), 1.23, 0.3)
        glVertex3f(jx - 0.5, 1.23, 0.3)
        glEnd()
        glEnable(GL_LIGHTING)

        if self.tex is None:
            return
        blue, ink = "#27457F", "#1A1A1A"
        draw_latex_3d(self.tex.text("%.2f" % max(fuel, 0.0), 13, ink),
                      jx, 1.32, 0.3, 0.24)             # jeep fuel number
        for i in range(n - 1):                         # depot fuel fractions
            if sim["placed"][i] is None or o < sim["placed"][i] - 1e-9:
                continue
            fr = depots[i]
            stx = "0" if fr == 0 else r"$\frac{%d}{%d}$" % (fr.numerator,
                                                            fr.denominator)
            t = self.tex.latex(stx, 14, blue) if fr else \
                self.tex.text("0", 13, blue)
            draw_latex_3d(t, float(sim["P"][i]) * sc, 0.78, 0.3, 0.34)
        x_prev = 0.0
        for i in range(n):                             # spacing fractions
            x_i = float(sim["P"][i]) * sc
            draw_latex_3d(self.tex.latex(
                r"$\frac{1}{%d}$" % sim["s"][i].denominator, 13, blue),
                (x_prev + x_i) / 2.0, -1.45, -0.4, 0.36)
            x_prev = x_i
        Hf = sim["P"][-1]                              # reach = H_n / 2
        draw_latex_3d(self.tex.latex(
            r"$\frac{r}{2}H_{%d} = \frac{%d}{%d}r$"
            % (n, Hf.numerator, Hf.denominator), 14, "#B5093D"),
            end, 1.85, 0.3, 0.42)

    def _cylinder(self, cx, r, h):
        segs = 18
        glColor4f(0.94, 0.94, 0.97, 1.0)
        glBegin(GL_QUAD_STRIP)
        for i in range(segs + 1):
            a = 2 * math.pi * i / segs
            nx, nz = math.cos(a), math.sin(a)
            glNormal3f(nx, 0.0, nz)
            glVertex3f(cx + r * nx, 0.0, r * nz)
            glVertex3f(cx + r * nx, h, r * nz)
        glEnd()
        glNormal3f(0.0, 1.0, 0.0)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(cx, h, 0.0)
        for i in range(segs + 1):
            a = 2 * math.pi * i / segs
            glVertex3f(cx + r * math.cos(a), h, r * math.sin(a))
        glEnd()
        glDisable(GL_LIGHTING)                         # blue rims
        glColor4f(0.16, 0.30, 0.55, 1.0)
        glLineWidth(2.0)
        for yy in (0.0, h):
            glBegin(GL_LINE_LOOP)
            for i in range(segs):
                a = 2 * math.pi * i / segs
                glVertex3f(cx + r * math.cos(a), yy, r * math.sin(a))
            glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def _jeep(self, x):
        glColor4f(0.15, 0.62, 0.30, 1.0)               # the famous green jeep
        draw_box(x - 0.55, 0.18, -0.22, x + 0.55, 0.52, 0.22)
        draw_box(x - 0.45, 0.52, -0.20, x + 0.05, 0.86, 0.20)
        glColor4f(0.08, 0.08, 0.09, 1.0)
        for wx in (x - 0.32, x + 0.32):
            draw_box(wx - 0.12, 0.0, -0.24, wx + 0.12, 0.20, 0.24)

    # ------------------------------------------------------- overlays ---
    def overlay_latex(self):
        n = int(self.s_n.value)
        Hf = self._sim(n)["P"][-1]
        return [
            (r"$\frac{r}{2n} + \frac{r}{2(n-1)} + \frac{r}{2(n-2)}"
             r" + \cdots = \frac{r}{2}H_n$", 15),
            (r"$\frac{1}{2}H_{%d} = \frac{%d}{%d} \approx %.4f"
             r" \qquad (r = 1)$" % (n, Hf.numerator, Hf.denominator,
                                    float(Hf)), 14),
            (r"$r = 30:\qquad \frac{30}{2}H_{%d} = %.2f"
             r"\;\mathrm{leucas}$" % (n, 30.0 * float(Hf)), 14),
        ]

    def overlay_info(self):
        n = int(self.s_n.value)
        sim = self._sim(n)
        o = self.s_t.value * sim["total"]
        _, fuel, _, trip = self._state(sim, o)
        return [
            '"Solution to the jeep problem for n = 3, showing the amount of',
            ' fuel in each depot and in the jeep at each step."  (Wikipedia)',
            "Alcuin's 9th-century camel version (30 measures, 1 per leuca,",
            "1 leuca ~ 2.3 km) had an INCORRECT solution!",
            "Divergence of H_n: any crossing distance is possible with",
            "enough fuel.   Trip %d of %d  |  odometer %.3f r  |  tank %.2f"
            % (trip, n, o, max(fuel, 0.0)),
        ]


@register_page
class BlockStackingPage(Page):
    """PAGE 8 — Applications: Stacking blocks (block-stacking problem).
    TRUE-3D recreation of Wikipedia's figure: wooden blocks (one per
    layer), block k from the top overhanging the one below by t/(2k)
    block lengths -> total overhang (t/2) H_n beyond the table edge.
    Reproduced from the figure: wood tones, left-staircase offset
    labels 1/2, 1/(2x2), ..., dot+arrow center-of-mass markers, dashed
    table-edge line, '1' length arrow, red overhang arrow.
    Physics slider t: COM of the top j blocks sits EXACTLY (1-t)/2
    lengths inside its supporting edge (uniform margin; t=1 = Wikipedia
    = marginally stable). ~45 boxes -> immediate drawing, no display
    list needed (under the 100-box standard).
    """
    TITLE = "Stacking Blocks  —  Overhang  =  (1/2) H_n   (no limit!)"
    L, H, D = 3.0, 0.5, 1.4                    # block length/height/depth
    WOODS = [(0.72, 0.50, 0.27), (0.85, 0.66, 0.42), (0.80, 0.55, 0.30),
             (0.88, 0.72, 0.50), (0.70, 0.42, 0.20), (0.82, 0.60, 0.35)]

    def __init__(self):
        super().__init__()
        self.tex = None
        self.Hn = np.concatenate(([0.0], np.cumsum(1.0 / np.arange(1, 41))))
        self.s_n   = Slider("Blocks  n", 1, 40, 9, step=1)
        self.s_t   = Slider("Offset factor  t  (1 = optimal limit)",
                            0.0, 1.0, 1.0)
        self.s_com = Slider("Center-of-mass arrows (0/1)", 0, 1, 1, step=1)
        self.sliders = [self.s_n, self.s_t, self.s_com]

    # ------------------------------------------------------------ 3D ---
    def draw_world(self):
        n, t = int(self.s_n.value), self.s_t.value
        L, H, D = self.L, self.H, self.D
        zf = D / 2.0 + 0.03                     # front annotation plane
        r = [0.0] * (n + 2)                     # right edges; r[n+1]=table=0
        r[n] = t * L / (2.0 * n)
        for j in range(n - 1, 0, -1):
            r[j] = r[j + 1] + t * L / (2.0 * j)

        draw_floor_grid(40.0)
        glColor4f(0.45, 0.30, 0.18, 1.0)        # the table
        draw_box(-7.0, -2.5, -1.1, 0.0, 0.0, 1.1)
        for j in range(1, n + 1):               # the stack (top block = j=1)
            glColor4f(*self.WOODS[(j * 5) % 6], 1.0)
            y0 = (n - j) * H
            draw_box(r[j] - L, y0, -D / 2, r[j], y0 + H, D / 2)

        glDisable(GL_LIGHTING)
        glEnable(GL_LINE_STIPPLE)               # dashed table-edge line
        glLineStipple(2, 0x0F0F)
        glLineWidth(2.0)
        glColor4f(0.30, 0.28, 0.26, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, zf); glVertex3f(0.0, n * H + 1.45, zf)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

        if int(self.s_com.value):               # COM dot+arrow markers
            glColor4f(0.25, 0.18, 0.12, 1.0)
            for j in range(1, n + 1):
                xa = r[j + 1] - (1.0 - t) * L / 2.0
                yt = (n - j) * H                # top of supporting layer
                glBegin(GL_TRIANGLE_FAN)        # the dot
                glVertex3f(xa, yt + 0.48, zf)
                for i in range(13):
                    a = 2 * math.pi * i / 12
                    glVertex3f(xa + 0.06 * math.cos(a),
                               yt + 0.48 + 0.06 * math.sin(a), zf)
                glEnd()
                glLineWidth(2.5)
                glBegin(GL_LINES)               # shaft + arrowhead
                glVertex3f(xa, yt + 0.44, zf); glVertex3f(xa, yt + 0.10, zf)
                glVertex3f(xa, yt + 0.10, zf)
                glVertex3f(xa - 0.07, yt + 0.22, zf)
                glVertex3f(xa, yt + 0.10, zf)
                glVertex3f(xa + 0.07, yt + 0.22, zf)
                glEnd()

        grey = (0.62, 0.64, 0.70)               # offset double-arrows (left)
        if t >= 0.99:
            for j in range(1, min(n, 9) + 1):
                self._harrow(r[j + 1] - L, r[j] - L,
                             (n - j) * H + 0.10, zf, grey)
        self._harrow(r[1] - L, r[1], n * H + 0.40, zf, grey)   # '1' arrow
        self._harrow(0.0, r[1], n * H + 1.05, zf, (1.0, 0.35, 0.30))
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

        # ---- labels -------------------------------------------------------
        if self.tex is None:
            return
        lt = "#D8DCE8"
        if t >= 0.99:
            for j in range(1, min(n, 9) + 1):
                stx = r"$\frac{1}{2}$" if j == 1 \
                      else r"$\frac{1}{2\times %d}$" % j
                draw_latex_3d(self.tex.latex(stx, 13, lt),
                              (r[j] + r[j + 1]) / 2.0 - L,
                              (n - j) * H + 0.22, zf, 0.42)
        draw_latex_3d(self.tex.text("1", 14, lt),
                      r[1] - L / 2.0, n * H + 0.52, zf, 0.28)
        over = t * self.Hn[n] / 2.0
        stx = (r"$\frac{1}{2}H_{%d} = %.3f$" % (n, over)) if t >= 0.99 \
              else (r"$%.3f$" % over)
        draw_latex_3d(self.tex.latex(stx, 14, "#FF5A4D"),
                      r[1] / 2.0, n * H + 1.18, zf, 0.42)

    @staticmethod
    def _harrow(x0, x1, y, z, col):             # double-headed arrow
        glColor4f(*col, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex3f(x0, y, z); glVertex3f(x1, y, z)
        for xa, dr in ((x0, 1.0), (x1, -1.0)):
            glVertex3f(xa, y, z); glVertex3f(xa + 0.16 * dr, y + 0.09, z)
            glVertex3f(xa, y, z); glVertex3f(xa + 0.16 * dr, y - 0.09, z)
        glEnd()

    # ------------------------------------------------------- overlays ---
    def overlay_latex(self):
        n, t = int(self.s_n.value), self.s_t.value
        out = [
            (r"$\frac{1}{2} + \frac{1}{2\cdot 2} + \frac{1}{2\cdot 3}"
             r" + \cdots + \frac{1}{2\cdot n} = \frac{1}{2}H_n$", 15),
            (r"$\mathrm{overhang} = \frac{t}{2}H_{%d} = %.4f"
             r"\;\mathrm{lengths}\qquad (t = %.2f)$"
             % (n, t * self.Hn[n] / 2.0, t), 14),
            (r"$\mathrm{stability\;margin} = \frac{1-t}{2} = %.3f$"
             % ((1.0 - t) / 2.0), 14),
        ]
        return out

    def overlay_info(self):
        t = self.s_t.value
        lines = [
            '"Blocks aligned according to the harmonic series can overhang',
            ' the edge of a table by the harmonic numbers."  (Wikipedia)',
            "Top block sticks out 1/2; the k-th from the top adds 1/(2k).",
            "Divergence => NO LIMIT on the overhang. H_n > 4 first at n=31:",
            "a 31-block stack overhangs 2 full block lengths!",
        ]
        if t >= 0.99:
            lines.append("t = 1: every group's center of mass sits EXACTLY"
                         " above an edge - marginally stable!")
        else:
            lines.append("t < 1: every COM arrow sits (1-t)/2 inside its"
                         " edge - a uniform safety margin.")
        lines.append("One block per layer is optimal; multi-block layers can"
                     " overhang much more (Wikipedia).")
        return lines


@register_page
class PrimesDivisorsPage(Page):
    """PAGE 9 — Counting primes and divisors. ORIGINAL design (no
    Wikipedia figure for this section).
    Exhibit A: harmonic bars with primes crimson / composites ghosted;
      translucent green wall = sum of 1/p over primes p <= x; amber
      Mertens curve ln ln x + M, M = 0.2614972... Divergence of the
      wall <=> infinitely many primes (Euler 1737).
    Exhibit B: Dirichlet hyperbola lattice on paper: dots (i,j) with
      i*j <= n in blue under the crimson hyperbola xy = n; column i
      holds exactly floor(n/i) dots, so blue count = sum floor(n/i)
      and average divisors ~ ln n + 2*gamma - 1 + O(1/sqrt n).
    Heavy (bars + up to 3600 dots) -> display-list standard.
    """
    TITLE = "Counting Primes & Divisors  —  Euler 1737, Mertens, Dirichlet"
    MERTENS = 0.2614972128476428
    N_TOP, S = 200, 2.2                          # prime range cap, y-scale

    def __init__(self):
        super().__init__()
        self.tex = None
        sieve = np.ones(self.N_TOP + 1, dtype=bool)
        sieve[:2] = False
        for i in range(2, int(self.N_TOP ** 0.5) + 1):
            if sieve[i]:
                sieve[i * i::i] = False
        self.is_prime = sieve
        self.psum = np.zeros(self.N_TOP + 1)     # sum of 1/p for p <= x
        run = 0.0
        for i in range(2, self.N_TOP + 1):
            if sieve[i]:
                run += 1.0 / i
            self.psum[i] = run
        self.s_N = Slider("Prime range  x", 10, self.N_TOP, 100, step=1)
        self.s_n = Slider("Hyperbola  n", 1, 60, 30, step=1)
        self.s_i = Slider("Highlight column i (0 = off)", 0, 60, 0, step=1)
        self.sliders = [self.s_N, self.s_n, self.s_i]
        self._cache_key = None
        self._dlist = None

    # ------------------------------------------------------------ 3D ---
    def draw_world(self):
        N, n = int(self.s_N.value), int(self.s_n.value)
        ih = int(self.s_i.value)
        key = (N, n, ih)
        if key != self._cache_key:
            if self._dlist is not None:
                glDeleteLists(self._dlist, 1)
            self._dlist = glGenLists(1)
            glNewList(self._dlist, GL_COMPILE)
            self._build_scene(N, n, ih)
            glEndList()
            self._cache_key = key
        glCallList(self._dlist)

        # ---- labels, every frame ------------------------------------------
        if self.tex is None:
            return
        lt, ink = "#D8DCE8", "#1A1A1A"
        for p in (2, 3, 5, 7, 11, 13):           # first prime bar labels
            if p <= N:
                draw_latex_3d(self.tex.text(str(p), 13, "#FF8090"),
                              self._xa(p, N), -0.42, 0.3, 0.24)
        draw_latex_3d(self.tex.text(
            "Sum of 1/p over primes  vs  ln ln x + M", 14, lt),
            -12.0, self.psum[N] * self.S + 1.0, 0.3, 0.34)
        draw_latex_3d(self.tex.text(
            "Lattice points under  xy = n", 14, lt),
            8.3, 13.0, 0.3, 0.34)
        u = lambda v: 2.6 + 11.0 * v / n
        py = lambda v: 0.4 + 11.0 * v / n
        draw_latex_3d(self.tex.text("1", 12, ink), u(1), 0.02, -0.65, 0.20)
        draw_latex_3d(self.tex.text(str(n), 12, ink), u(n), 0.02, -0.65, 0.20)
        draw_latex_3d(self.tex.text(str(n), 12, ink),
                      u(0) - 0.30, py(n) - 0.10, -0.65, 0.20)
        if 0 < ih <= n:
            draw_latex_3d(self.tex.latex(
                r"$\lfloor %d/%d \rfloor = %d$" % (n, ih, n // ih),
                13, "#C77B0F"),
                u(ih), py(n // ih) + 0.35, -0.65, 0.34)

    @staticmethod
    def _xa(i, N):                               # exhibit A bar position
        return -21.0 + 18.0 * i / N

    def _build_scene(self, N, n, ih):
        draw_floor_grid(40.0)
        S = self.S
        # ---------- Exhibit A: primes among the harmonic bars -------------
        bw = max(0.35 * 18.0 / N, 0.025)
        for i in range(2, N + 1):                # ghosts first (translucent)
            if not self.is_prime[i]:
                glColor4f(0.55, 0.58, 0.66, 0.18)
                x = self._xa(i, N)
                draw_box(x - bw, 0.0, -0.22, x + bw, S / i, 0.22)
        for i in range(2, N + 1):                # crimson primes
            if self.is_prime[i]:
                glColor4f(0.82, 0.16, 0.28, 1.0)
                x = self._xa(i, N)
                draw_box(x - bw, 0.0, -0.25, x + bw, S / i, 0.25)
        glDisable(GL_LIGHTING)
        glColor4f(0.20, 0.85, 0.45, 0.30)        # green wall: sum 1/p
        glBegin(GL_QUAD_STRIP)
        for i in range(2, N + 1):
            x = self._xa(i, N)
            glVertex3f(x, 0.0, -0.6)
            glVertex3f(x, self.psum[i] * S, -0.6)
        glEnd()
        glLineWidth(2.5)                         # wall top edge
        glColor4f(0.20, 0.85, 0.45, 0.9)
        glBegin(GL_LINE_STRIP)
        for i in range(2, N + 1):
            glVertex3f(self._xa(i, N), self.psum[i] * S, -0.58)
        glEnd()
        glLineWidth(3.0)                         # amber Mertens curve
        glColor4f(1.0, 0.70, 0.20, 1.0)
        glBegin(GL_LINE_STRIP)
        for x in np.linspace(2.3, N, 300):
            glVertex3f(self._xa(x, N),
                       (math.log(math.log(x)) + self.MERTENS) * S, -0.56)
        glEnd()
        # ---------- Exhibit B: Dirichlet hyperbola lattice -----------------
        glColor4f(0.965, 0.950, 0.915, 1.0)      # paper
        glBegin(GL_QUADS)
        glVertex3f(1.5, -1.0, -0.75); glVertex3f(15.3, -1.0, -0.75)
        glVertex3f(15.3, 12.6, -0.75); glVertex3f(1.5, 12.6, -0.75)
        glEnd()
        u = lambda v: 2.6 + 11.0 * v / n
        py = lambda v: 0.4 + 11.0 * v / n
        glLineWidth(2.0)                         # black axes
        glColor4f(0.07, 0.07, 0.08, 1.0)
        glBegin(GL_LINES)
        glVertex3f(u(0), py(0), -0.7); glVertex3f(u(0) + 11.6, py(0), -0.7)
        glVertex3f(u(0), py(0), -0.7); glVertex3f(u(0), py(0) + 11.6, -0.7)
        glEnd()
        d = min(0.15, 11.0 / n * 0.22)           # lattice dots (flat quads)
        glBegin(GL_QUADS)
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i == ih and i * j <= n:
                    glColor4f(0.95, 0.62, 0.15, 1.0)   # highlighted column
                    dd = d * 1.5
                elif i * j <= n:
                    glColor4f(0.16, 0.28, 0.62, 1.0)   # under hyperbola
                    dd = d
                else:
                    glColor4f(0.80, 0.80, 0.82, 1.0)   # above: ghost
                    dd = d * 0.6
                x, y = u(i), py(j)
                glVertex3f(x - dd, y - dd, -0.7)
                glVertex3f(x + dd, y - dd, -0.7)
                glVertex3f(x + dd, y + dd, -0.7)
                glVertex3f(x - dd, y + dd, -0.7)
        glEnd()
        if n > 1:                                # crimson hyperbola xy = n
            glLineWidth(3.0)
            glColor4f(0.71, 0.04, 0.24, 1.0)
            glBegin(GL_LINE_STRIP)
            for t in np.exp(np.linspace(0.0, math.log(n), 200)):
                glVertex3f(u(t), py(n / t), -0.68)
            glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------- overlays ---
    def overlay_latex(self):
        N, n = int(self.s_N.value), int(self.s_n.value)
        D = sum(n // i for i in range(1, n + 1))
        mert = math.log(math.log(N)) + self.MERTENS
        diri = math.log(n) + 2.0 * GAMMA - 1.0
        return [
            (r"$\sum_{i=1}^{\infty}\frac{1}{i}"
             r" = \prod_{p}\left(1 + \frac{1}{p} + \frac{1}{p^{2}}"
             r" + \cdots\right) = \prod_{p}\frac{1}{1 - 1/p}$", 14),
            (r"$\sum_{p \leq %d}\frac{1}{p} = %.4f,"
             r"\qquad \ln\ln %d + M = %.4f$" % (N, self.psum[N], N, mert),
             13),
            (r"$\frac{1}{n}\sum_{i=1}^{n}\left\lfloor\frac{n}{i}"
             r"\right\rfloor \leq \frac{1}{n}\sum_{i=1}^{n}\frac{n}{i}"
             r" = H_n$", 13),
            (r"$n = %d:\quad \frac{%d}{%d} = %.4f"
             r"\qquad \ln n + 2\gamma - 1 = %.4f$"
             % (n, D, n, D / n, diri), 13),
        ]

    def overlay_info(self):
        return [
            "Euler (1737): the harmonic series equals a product over primes",
            "(p runs over the primes P). If sum 1/p converged, the harmonic",
            "series would too -> sum 1/p DIVERGES -> infinitely many primes!",
            "Growth ~ ln ln x (Mertens): absurdly slow - ln ln(10^9) ~ 3.03.",
            "Right: blue dots = lattice points under xy <= n; column i has",
            "floor(n/i) dots. Average divisors = ln n + 2*gamma - 1 +",
            "O(1/sqrt(n)); sharpening the error term is an OPEN problem",
            "(Dirichlet's divisor problem).",
        ]


# =====================================================================
#  GAMEPAD MANAGER — T.16000M joystick (PILOT) + Xbox 360 pad (MANIPULATOR)
#  Built from verified axis maps in the Anniversary C++ project (Nir's HW).
#  Keyboard/mouse work SIMULTANEOUSLY with controllers (additive, not exclusive).
#  Startup calibration samples rest values for 60 frames (~1 sec at 60 fps).
# =====================================================================

class GamepadManager:
    """Full gamepad support: T.16000M -> PILOT, Xbox 360 -> MANIPULATOR.
    Deadzones: radial for 2D sticks (0.12), scalar for twist/throttle (0.08)."""

    CALIB_FRAMES    = 60
    STICK_DZ_RADIAL = 0.12
    SCALAR_DZ       = 0.08

    # T.16000M FCS axis mapping (verified on Nir's hardware via Anniversary project)
    AXIS_ROLL     = 0   # stick X
    AXIS_PITCH    = 1   # stick Y (forward push = axis negative = dive)
    AXIS_YAW      = 2   # stick Z twist
    AXIS_THROTTLE = 3   # throttle slider

    def __init__(self):
        pygame.joystick.init()
        self.pilot_joy = None
        self.manip_joy = None
        # Calibration state per joystick instance_id
        self._calib_sum    = {}
        self._calib_frames = {}
        self._calib_done   = {}
        self._calib_rest   = {}
        self._slider_idx = 0
        self._slider_switch_cooldown = 0.0
        self._detect()

    # ------------------------------------------------------- detection ---
    def _detect(self):
        """Assign connected devices: T.16000M -> pilot, Xbox gamepad -> manipulator."""
        count = pygame.joystick.get_count()
        for i in range(count):
            joy = pygame.joystick.Joystick(i)
            name = joy.get_name()
            is_t16  = "T.16000" in name or "Thrustmaster" in name
            is_xbox = "Xbox" in name or "360" in name or "XInput" in name

            if is_t16 and self.pilot_joy is None:
                joy.init()
                self.pilot_joy = joy
                self._start_calibration(joy)
                print("[gamepad] PILOT: %s (axes=%d, buttons=%d, hats=%d)" % (
                    name, joy.get_numaxes(), joy.get_numbuttons(), joy.get_numhats()))
            elif is_xbox and self.manip_joy is None:
                joy.init()
                self.manip_joy = joy
                self._start_calibration(joy)
                print("[gamepad] MANIPULATOR: %s (axes=%d, buttons=%d, hats=%d)" % (
                    name, joy.get_numaxes(), joy.get_numbuttons(), joy.get_numhats()))

    def _start_calibration(self, joy):
        jid = joy.get_instance_id()
        n = joy.get_numaxes()
        self._calib_sum[jid]    = np.zeros(n)
        self._calib_frames[jid] = 0
        self._calib_done[jid]   = False
        self._calib_rest[jid]   = np.zeros(n)

    # ---------------------------------------------------- deadzones ---
    @staticmethod
    def _clamp1(v):
        return max(-1.0, min(1.0, v))

    def _scalar_deadzone(self, v):
        if abs(v) < self.SCALAR_DZ:
            return 0.0
        sign = 1.0 if v > 0 else -1.0
        return sign * (abs(v) - self.SCALAR_DZ) / (1.0 - self.SCALAR_DZ)

    def _radial_deadzone(self, x, y):
        mag = math.sqrt(x * x + y * y)
        if mag < self.STICK_DZ_RADIAL:
            return 0.0, 0.0
        scale = ((mag - self.STICK_DZ_RADIAL) / (1.0 - self.STICK_DZ_RADIAL)) / mag
        return x * scale, y * scale

    # ------------------------------------------------- calibration ---
    def _calibrate(self, joy):
        """Run one calibration frame. Returns calibrated axes array or None if still calibrating."""
        jid = joy.get_instance_id()
        if self._calib_done.get(jid, False):
            rest = self._calib_rest[jid]
            return np.array([joy.get_axis(i) - rest[i] for i in range(joy.get_numaxes())])

        # Sample rest values during startup
        if jid in self._calib_sum:
            n = min(joy.get_numaxes(), len(self._calib_sum[jid]))
            for i in range(n):
                self._calib_sum[jid][i] += joy.get_axis(i)
            self._calib_frames[jid] += 1
            if self._calib_frames[jid] >= self.CALIB_FRAMES:
                self._calib_rest[jid] = self._calib_sum[jid] / self.CALIB_FRAMES
                self._calib_done[jid] = True
                rest_str = " ".join("a%d=%+.2f" % (i, self._calib_rest[jid][i])
                                   for i in range(n))
                print("[gamepad] %s calibrated: %s" % (joy.get_name(), rest_str))
        return None

    # -------------------------------------------------- pilot input ---
    def pilot_command(self):
        """Returns dict {pitch, yaw, roll, thrust_xyz} in -1..+1, or None if no pilot device.
        App.update() must ADD these to keyboard values (simultaneous use)."""
        joy = self.pilot_joy
        if joy is None:
            return None

        cal = self._calibrate(joy)
        if cal is None:
            return None  # still calibrating

        n = joy.get_numaxes()
        roll = pitch = yaw = 0.0
        thrust_xyz = [0.0, 0.0, 0.0]  # strafe, lift, forward

        # Stick X + Y -> roll + pitch with radial deadzone
        if n > max(self.AXIS_ROLL, self.AXIS_PITCH):
            sx = self._clamp1(cal[self.AXIS_ROLL])
            sy = self._clamp1(cal[self.AXIS_PITCH])
            sx, sy = self._radial_deadzone(sx, sy)
            roll  = sx
            pitch = sy   # forward push = axis negative = nose dive

        # Twist -> yaw with scalar deadzone
        if n > self.AXIS_YAW:
            yaw = self._scalar_deadzone(self._clamp1(cal[self.AXIS_YAW]))

        # Throttle -> forward/backward (scalar deadzone, inverted: slider fwd = axis neg = fly fwd)
        if n > self.AXIS_THROTTLE:
            t = self._scalar_deadzone(self._clamp1(cal[self.AXIS_THROTTLE]))
            thrust_xyz[2] = -t

        # POV hat -> lift + strafe
        if joy.get_numhats() >= 1:
            hx, hy = joy.get_hat(0)
            thrust_xyz[0] += float(hx)
            thrust_xyz[1] += float(hy)

        thrust_xyz = [self._clamp1(v) for v in thrust_xyz]

        return {'pitch': pitch, 'yaw': yaw, 'roll': roll, 'thrust_xyz': tuple(thrust_xyz)}

    # ---------------------------------------------- manipulator input ---
    def manipulator_update(self, sliders, dt):
        """Xbox D-pad/L-stick selects slider, L-stick X nudges value.
        Works simultaneously with mouse slider dragging."""
        joy = self.manip_joy
        if joy is None or not sliders:
            return

        # Slider selection with cooldown (D-pad Y or left stick Y)
        self._slider_switch_cooldown = max(0.0, self._slider_switch_cooldown - dt)
        if self._slider_switch_cooldown <= 0.0:
            if joy.get_numhats() >= 1:
                hx, hy = joy.get_hat(0)
                if hy != 0:
                    self._slider_idx = (self._slider_idx - hy) % len(sliders)
                    self._slider_switch_cooldown = 0.25
            if joy.get_numaxes() >= 2:
                ly = joy.get_axis(1)
                if abs(ly) > 0.6:
                    self._slider_idx = (self._slider_idx + (1 if ly > 0 else -1)) % len(sliders)
                    self._slider_switch_cooldown = 0.25

        # Left stick X nudges selected slider value
        if 0 <= self._slider_idx < len(sliders) and joy.get_numaxes() >= 1:
            lx = joy.get_axis(0)
            if abs(lx) > 0.15:
                sliders[self._slider_idx].nudge(lx * dt * 0.5)


# =====================================================================
#  APPLICATION
# =====================================================================

HELP_LINES = [
    "PLAYER 2 — PILOT (keyboard + T.16000M joystick):",
    "   W / S ........ forward / backward        A / D ........ strafe left / right",
    "   Z / X ........ slide up / down           Q / E ........ bank (roll) left / right",
    "   Arrow keys ... pitch & yaw               Shift ........ boost",
    "   T.16000M ...... stick=pitch/roll twist=yaw throttle=fwd/back hat=strafe/lift",
    "   HOLD RIGHT MOUSE BUTTON ... mouse-look (pitch/yaw),  I = invert pitch",
    "   R ............ reset ship to start position",
    "",
    "PLAYER 1 — MANIPULATOR (mouse + Xbox controller):",
    "   Drag the sliders on the right with the LEFT mouse button.",
    "   Xbox D-pad/L-stick Y ... select slider    L-stick X ... nudge value",
    "",
    "BOTH:   Tab = next page      H or F1 = toggle this help      Esc = quit",
]


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Math Flyer — Harmonic Series (2 players, 1 screen)")
        self.size = (1280, 760)
        pygame.display.set_mode(self.size, DOUBLEBUF | OPENGL | RESIZABLE)
        self.clock = pygame.time.Clock()
        self.tex = TexCache()
        self.ship = Ship()
        self.gamepads = GamepadManager()
        self.panel = UIPanel()
        self.pages = [cls() for cls in PAGES]
        for p in self.pages:
            p.tex = self.tex          # pages may draw cached textures in 3D
        self.page_idx = 0
        self.show_help = True
        self.invert_pitch = False
        self.mouse_look = False
        self._setup_gl()
        self._activate_page()

    # ------------------------------------------------------------ setup ---
    def _setup_gl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.85, 0.85, 0.85, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.35, 0.35, 0.40, 1.0))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogfv(GL_FOG_COLOR, (*CLEAR_COLOR, 1.0))
        glFogf(GL_FOG_START, 80.0)
        glFogf(GL_FOG_END, 420.0)
        glClearColor(*CLEAR_COLOR, 1.0)

    def _activate_page(self):
        self.panel.set_sliders(self.pages[self.page_idx].sliders)
        self.panel.layout(*self.size)

    # ----------------------------------------------------------- events ---
    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == QUIT:
                return False
            if ev.type == VIDEORESIZE:
                self.size = (max(640, ev.w), max(480, ev.h))
                glViewport(0, 0, *self.size)
                self.panel.layout(*self.size)
            elif ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    return False
                if ev.key == K_TAB:
                    self.page_idx = (self.page_idx + 1) % len(self.pages)
                    self._activate_page()
                if ev.key in (K_h, K_F1):
                    self.show_help = not self.show_help
                if ev.key == K_i:
                    self.invert_pitch = not self.invert_pitch
                if ev.key == K_r:
                    self.ship.reset()
            elif ev.type == MOUSEBUTTONDOWN and ev.button == 3:
                self.mouse_look = True          # Pilot borrows the mouse
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
                pygame.mouse.get_rel()          # flush stale delta
            elif ev.type == MOUSEBUTTONUP and ev.button == 3:
                self.mouse_look = False         # mouse returns to Player 1
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
            if not self.mouse_look:
                self.panel.handle_event(ev)     # Player 1's slider events
        return True

    # ----------------------------------------------------------- update ---
    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx, dy = pygame.mouse.get_rel() if self.mouse_look else (0, 0)
        gp = self.gamepads.pilot_command()
        self.ship.update(dt, keys, dx, dy, self.mouse_look, self.invert_pitch, gp)
        self.gamepads.manipulator_update(self.pages[self.page_idx].sliders, dt)

    # ----------------------------------------------------------- render ---
    def render(self):
        w, h = self.size
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # ---- 3D pass ----
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(62.0, w / float(h), 0.1, 3000.0)
        glMatrixMode(GL_MODELVIEW)
        self.ship.apply_view()
        glLightfv(GL_LIGHT0, GL_POSITION, (0.35, 1.0, 0.55, 0.0))  # sun
        glEnable(GL_FOG); glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
        self.pages[self.page_idx].draw_world()

        # ---- 2D overlay pass ----
        page = self.pages[self.page_idx]
        begin_2d(w, h)
        draw_texture(self.tex.text(
            "Page %d/%d   %s   [Tab = next page,  H = help]"
            % (self.page_idx + 1, len(self.pages), page.TITLE),
            24, (160, 215, 255), True), 14, 12)

        y = 48                                            # LaTeX formula panel
        latex_items = [(self.tex.latex(s, fs), s) for s, fs in page.overlay_latex()]
        if latex_items:
            pw = max(t[1] for t, _ in latex_items) * 0.5 + 28
            ph = sum(t[2] * 0.5 + 10 for t, _ in latex_items) + 18
            draw_rect(10, y, pw, ph, (0.05, 0.06, 0.11), 0.78)
            ty = y + 10
            for t, _ in latex_items:
                draw_texture(t, 24, ty, scale=0.5)
                ty += t[2] * 0.5 + 10

        self.panel.layout(w, h)                           # sliders (Player 1)
        self.panel.draw(self.tex)

        hud_y = h - 26 * (len(page.overlay_info()) + 1) - 10
        speed = float(np.linalg.norm(self.ship.vel))
        draw_texture(self.tex.text(
            "PILOT  pos(%.0f, %.0f, %.0f)  speed %.1f   mouse-look:%s  invert:%s"
            % (*self.ship.pos, speed,
               "ON (RMB)" if self.mouse_look else "off",
               "on" if self.invert_pitch else "off"),
            20, (150, 160, 180)), 14, hud_y)
        for i, line in enumerate(page.overlay_info()):
            draw_texture(self.tex.text(line, 21, (255, 224, 150)),
                         14, hud_y + 26 * (i + 1))

        if self.show_help:                                # help overlay
            bw, bh = 760, 30 * len(HELP_LINES) + 30
            bx, by = (w - bw) // 2, (h - bh) // 2
            draw_rect(bx, by, bw, bh, (0.03, 0.04, 0.08), 0.92)
            for i, line in enumerate(HELP_LINES):
                draw_texture(self.tex.text(line, 22, (220, 225, 235)),
                             bx + 24, by + 16 + 30 * i)
        end_2d()
        pygame.display.flip()

    # ------------------------------------------------------------- main ---
    def run(self):
        running = True
        while running:
            dt = min(0.05, self.clock.tick(60) / 1000.0)
            running = self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()


def main():
    try:
        App().run()
    except Exception:
        import traceback
        import datetime
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        with open("harmonic_series_mathematics.log", "a", encoding="utf-8") as f:
            f.write("\n=== CRASH %s ===\n" % datetime.datetime.now().isoformat())
            f.write(tb)
            f.write("=" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()