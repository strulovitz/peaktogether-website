# render_demo.py
# =====================================================================
#  Descent QED -- RENDER DEMO
#  Stand-alone scene that exercises every render.py primitive so the
#  output can be screenshotted. Built "like Fable": same legacy-GL window
#  setup, quaternion Ship camera, [ ] wall-alpha control, 60 FPS loop.
#
#  DRAW ORDER (Fable's correct transparency ordering):
#    1. OPAQUE pass: edges, breadcrumbs, box wireframe, billboards
#    2. TRANSLUCENT pass: wall fills LAST, so opaque content shows through.
#
#  FOG: render.py owns distance-darkening as a PERMANENT engine feature
#  (render.DARKNESS_START -> render.DARKNESS_END). The room below is large
#  enough that the far end visibly darkens -- that is the engine's fog
#  doing its job, not a demo trick.
#
#  PORTABILITY: verified for Windows / Linux. On macOS the window may come
#  up BLACK -- see the macOS comment next to set_mode below for the fix.
# =====================================================================

import math
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *

import palette
import render

WIN_SIZE = (1280, 720)

# A large demo room (~120 units deep) so the engine fog
# (render.DARKNESS_START -> render.DARKNESS_END) visibly darkens the far
# end. The fog itself is production render behavior; the room is just big
# enough to show it.
ROOM_LO = (-10.0, -2.0, -120.0)
ROOM_HI = ( 10.0,  8.0,    2.0)


def room_walls():
    """Yield floor, ceiling, side walls + far wall as quads, near->far so
    the engine fog visibly bites the far ones."""
    x0, y0, z0 = ROOM_LO
    x1, y1, z1 = ROOM_HI
    yield [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)]  # floor
    yield [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]  # ceiling
    yield [(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)]  # left
    yield [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)]  # right
    yield [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)]  # far wall (z0)


def main():
    pygame.init()

    # ---- WINDOW / GL CONTEXT (Fable's exact approach) -------------------
    # macOS NOTE: this plain set_mode gives a legacy GL context on Windows
    # and Linux (which is what this fixed-function engine needs). On macOS
    # Apple deprecated legacy GL and this may produce a BLACK WINDOW. To
    # fix on macOS, add BEFORE this set_mode call:
    #     pygame.display.gl_set_attribute(GL_CONTEXT_PROFILE_MASK,
    #                                     GL_CONTEXT_PROFILE_COMPATIBILITY)
    #     pygame.display.gl_set_attribute(GL_CONTEXT_MAJOR_VERSION, 2)
    #     pygame.display.gl_set_attribute(GL_CONTEXT_MINOR_VERSION, 1)
    # (Harmless on Windows/Linux, zero performance cost; only macOS needs it.)
    pygame.display.set_mode(WIN_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Descent QED -- render demo")

    render.init_gl(WIN_SIZE)
    pygame.font.init()

    cache = render.TexCache()
    ship  = render.Ship(home_pos=(0.0, 3.0, 0.0))
    clock = pygame.time.Clock()

    wall_alpha = 0.45
    ALPHA_MIN, ALPHA_MAX, ALPHA_STEP = 0.0, 0.9, 0.05

    # billboards at increasing depth: the nearest is bright, the far one is
    # darkened by the engine's fog -- a direct visual proof fog is live.
    eqs = [
        (r"$\zeta(2)=\frac{\pi^2}{6}$",      np.array([ 0.0, 3.0, -15.0])),
        (r"$e^{i\pi}+1=0$",                  np.array([-4.0, 3.0, -45.0])),
        (r"$\int_0^\infty e^{-x^2}dx=\frac{\sqrt{\pi}}{2}$",
                                             np.array([ 4.0, 3.0, -90.0])),
    ]

    while True:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                pygame.quit(); return
            if ev.type == KEYDOWN and ev.key == K_LEFTBRACKET:
                wall_alpha = max(ALPHA_MIN, wall_alpha - ALPHA_STEP)
            if ev.type == KEYDOWN and ev.key == K_RIGHTBRACKET:
                wall_alpha = min(ALPHA_MAX, wall_alpha + ALPHA_STEP)

        ship.update(dt, pygame.key.get_pressed())

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ship.apply_view()

        cam_right = render.ship_right(ship.q)
        cam_up    = render.ship_up(ship.q)

        # ---------- PASS 1: OPAQUE (markers, box, billboards) -------------
        for i, lx in enumerate(np.linspace(-8, 8, 5)):
            render.draw_breadcrumb((lx, 0.2, -10.0 - 6 * i),
                                   palette.WORLD_EDGE)
        render.draw_box_edges((-2, 0, -25), (2, 4, -21), palette.WORLD_EDGE)
        for latex, pos in eqs:
            tex = cache.get_mathtext(latex, color=(0.95, 0.96, 0.98),
                                     fontsize=16)
            render.draw_billboard(tex, pos, cam_right, cam_up,
                                  scale=3.0, alpha=1.0)

        # ---------- PASS 2: TRANSLUCENT (wall fills LAST) -----------------
        for quad in room_walls():
            render.draw_wall(quad,
                             fill_color=palette.WORLD_WALL_FILL,
                             edge_color=palette.WORLD_EDGE,
                             fill_alpha=wall_alpha)

        # ---------- HUD (2D overlay, fog disabled inside begin_2d) --------
        render.begin_2d(*WIN_SIZE)
        render.draw_text_mathtext_2d(
            cache,
            r"$\mathrm{wall\ alpha}=%.2f\quad [\ ]\ \mathrm{adjust}$" % wall_alpha,
            10, 10, color=(0.7, 0.7, 0.7), fontsize=15)
        render.end_2d()

        pygame.display.flip()


if __name__ == "__main__":
    main()
