# render_demo.py
# =====================================================================
#  Descent QED -- RENDER DEMO  (corrected scene layout)
#  render.py is unchanged; this fixes the DEMO scene so wall color is
#  visible up close and the engine fog darkens the receding tunnel to
#  near-black at the far end.
# =====================================================================

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *

import palette
import render

WIN_SIZE = (1280, 720)

# A long corridor running down -Z. Cross-section is small (you're INSIDE
# it), so wall fills face the camera and show their color up close, while
# the far end recedes into the fog band (render.DARKNESS_START..END) and
# darkens to near-black.
HALF_W = 6.0      # corridor half-width / half-height
NEAR_Z = 5.0      # corridor starts just behind the camera
FAR_Z  = -160.0   # ...and runs well past DARKNESS_END so the far end is black
SEG    = 8.0      # spacing of ring segments down the corridor


def corridor_quads():
    """Yield wall quads of a square tube down -Z, segment by segment, so
    each ring is at a different depth and the fog gradient is smooth."""
    z = NEAR_Z
    while z > FAR_Z:
        z0, z1 = z, z - SEG
        h = HALF_W
        # floor, ceiling, left, right for this segment
        yield [(-h,-h,z0),( h,-h,z0),( h,-h,z1),(-h,-h,z1)]   # floor
        yield [(-h, h,z0),( h, h,z0),( h, h,z1),(-h, h,z1)]   # ceiling
        yield [(-h,-h,z0),(-h, h,z0),(-h, h,z1),(-h,-h,z1)]   # left
        yield [( h,-h,z0),( h, h,z0),( h, h,z1),( h,-h,z1)]   # right
        z -= SEG


def main():
    pygame.init()

    # macOS NOTE: plain set_mode gives a legacy GL context on Windows/Linux.
    # On macOS this may give a BLACK WINDOW; add BEFORE set_mode:
    #     pygame.display.gl_set_attribute(GL_CONTEXT_PROFILE_MASK,
    #                                     GL_CONTEXT_PROFILE_COMPATIBILITY)
    #     pygame.display.gl_set_attribute(GL_CONTEXT_MAJOR_VERSION, 2)
    #     pygame.display.gl_set_attribute(GL_CONTEXT_MINOR_VERSION, 1)
    pygame.display.set_mode(WIN_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Descent QED -- render demo")

    render.init_gl(WIN_SIZE)
    pygame.font.init()

    cache = render.TexCache()
    # Start the camera INSIDE the near end of the corridor, looking down -Z.
    ship  = render.Ship(home_pos=(0.0, 0.0, 0.0))
    clock = pygame.time.Clock()

    wall_alpha = 0.50
    ALPHA_MIN, ALPHA_MAX, ALPHA_STEP = 0.0, 0.9, 0.05

    # billboards spaced down the corridor: near = bright, far = fogged dark.
    eqs = [
        (r"$\zeta(2)=\frac{\pi^2}{6}$",  np.array([0.0, 0.0, -12.0])),
        (r"$e^{i\pi}+1=0$",              np.array([0.0, 0.0, -55.0])),
        (r"$\int_0^\infty e^{-x^2}dx=\frac{\sqrt{\pi}}{2}$",
                                         np.array([0.0, 0.0, -110.0])),
    ]

    quads = list(corridor_quads())

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

        # ---- PASS 1: OPAQUE (breadcrumbs, box, billboards) ----
        # Greyscale structure proves the world rule; these few SATURATED
        # breadcrumbs prove chroma CAN shine through grey walls (brief req).
        CHROMA = [
            (1.0, 0.25, 0.25),   # red
            (0.25, 1.0, 0.40),   # green
            (0.35, 0.55, 1.0),   # blue
            (1.0, 0.85, 0.20),   # amber
        ]
        for i in range(8):
            col = CHROMA[i % len(CHROMA)]
            render.draw_breadcrumb((0.0, -HALF_W + 0.3, -6.0 - i * 10.0),
                                   col, size=0.35)
        render.draw_box_edges((-2, -2, -35), (2, 2, -30), palette.WORLD_EDGE)

        # ---- PASS 2: ENQUEUE translucent walls (do NOT draw here) ----
        # Enqueue every corridor wall; also enqueue a couple of EXTRA
        # overlapping walls at different depths to prove the shared sort.
        for quad in quads:
            render.queue_wall(quad,
                              palette.WORLD_WALL_FILL,
                              palette.WORLD_EDGE,
                              wall_alpha)
        # two overlapping translucent slabs at different depths:
        render.queue_wall([(-4,-4,-25),(4,-4,-25),(4,4,-25),(-4,4,-25)],
                          palette.WORLD_WALL_FILL, palette.WORLD_EDGE, 0.5)
        render.queue_wall([(-4,-4,-40),(4,-4,-40),(4,4,-40),(-4,4,-40)],
                          palette.WORLD_WALL_FILL, palette.WORLD_EDGE, 0.5)

        # ---- SINGLE FLUSH: once per frame, after opaque+robots, ----
        # ---- before billboards. Camera position passed in. ----
        render.flush_walls(ship.pos)

        # ---- BILLBOARDS (after flush, per canonical order) ----
        for j, (latex, pos) in enumerate(eqs):
            tint = (1.0, 0.55, 0.30) if j == 0 else (0.95, 0.96, 0.98)
            tex = cache.get_mathtext(latex, color=tint, fontsize=16)
            render.draw_billboard(tex, pos, cam_right, cam_up,
                                  scale=2.5, alpha=1.0)

        # ---- HUD ----
        render.begin_2d(*WIN_SIZE)
        render.draw_text_mathtext_2d(
            cache,
            r"$\mathrm{wall\ alpha}=%.2f\quad [\ ]\ \mathrm{adjust}$" % wall_alpha,
            10, 10, color=(0.7, 0.7, 0.7), fontsize=15)
        render.end_2d()

        pygame.display.flip()


if __name__ == "__main__":
    main()
