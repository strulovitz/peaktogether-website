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