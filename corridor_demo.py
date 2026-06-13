"""
corridor_demo.py — standalone flythrough of ONE bent corridor.

Controls: WASD/RF translate, arrows pitch/yaw, Q/E roll, Shift boost
(handled inside ship.update via pygame keys). ESC quits.

Frame order (CRITICAL — matches engine contract):
  1. clear + apply_view
  2. opaque: corner glow, chevrons (enqueued as walls here for simplicity),
     robots (opaque hull)
  3. render.flush_walls(ship.pos)   <-- translucent walls sorted+drawn ONCE
  4. billboards: title + defeat plaques
"""

import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, K_ESCAPE
from OpenGL.GL import (
    glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClearColor,
)

import render
import palette as palette_mod
from content_parser import parse_corridor
from corridor_builder import build_corridor


def main(path="corridors/01_dummy.txt"):
    pygame.init()
    pygame.display.set_mode((1280, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("DESCENT QED — corridor demo")

    render.init_gl(1280, 800) if hasattr(render, "init_gl") else None
    render.set_fog()  # 40 -> 140 toward CLEAR_COLOR

    cc = palette_mod.CLEAR_COLOR
    glClearColor(cc[0], cc[1], cc[2], 1.0)

    data = parse_corridor(path)
    corridor = build_corridor(data, origin=(0, 0, 0), direction=(0, 0, -1))

    texcache = render.TexCache()
    ship = render.Ship(home_pos=(0.0, 0.0, 8.0))   # start just outside the mouth

    clock = pygame.time.Clock()
    # quick demo: defeat the first robot after 4s to show the museum plaque
    t_accum = 0.0
    defeated_first = False

    while True:
        dt = clock.tick(60) / 1000.0
        t_accum += dt
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                _quit()
            if ev.type == pygame.KEYDOWN and ev.key == K_ESCAPE:
                _quit()

        ship.update(dt, pygame.key.get_pressed())
        corridor.update(dt, tuple(ship.pos.tolist()))

        if not defeated_first and t_accum > 4.0:
            robs = corridor.get_robots()
            if robs:
                robs[0].play_defeat()
                defeated_first = True

        # ---- frame ----
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ship.apply_view()

        cam_right = render.ship_right(ship.q)
        cam_up    = render.ship_up(ship.q)

        # corridor.draw enqueues walls + draws robots (opaque) + queues chevrons/glow
        corridor.draw(cam_right, cam_up, texcache)

        # CRITICAL: flush translucent walls ONCE, after opaque/robots,
        # before billboards. (corridor.draw already drew title+plaques AFTER
        # its robots; for strict ordering we flush here so walls sit behind
        # the billboards correctly.)
        render.flush_walls(tuple(ship.pos.tolist()))

        pygame.display.flip()


def _quit():
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corridors/01_dummy.txt")