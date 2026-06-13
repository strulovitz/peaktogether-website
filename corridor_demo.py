"""
corridor_demo.py — standalone flythrough of ONE bent corridor.

Controls (via ship.update + pygame keys): WASD/RF translate, arrows pitch/yaw,
Q/E roll, Shift boost. ESC quits.

Frame order (CONTRACT — flush walls BEFORE billboards):
  1. clear + apply_view
  2. corridor.draw_world(...)        # walls queued + opaque robots
  3. render.flush_walls(ship.pos)    # translucent walls sorted + drawn ONCE
  4. corridor.draw_labels(...)       # title + defeat plaques (billboards)
"""

import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, K_ESCAPE
from OpenGL.GL import (
    glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glClearColor,
)

import render
import palette
from content_parser import parse_corridor
from corridor_builder import build_corridor


def main(path="corridors/01_dummy.txt"):
    pygame.init()
    pygame.display.set_mode((1280, 800), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("DESCENT QED — corridor demo")

    render.init_gl((1280, 800))          # ONE tuple (Bug 6)
    render.set_fog()                     # 40 -> 140 toward CLEAR_COLOR

    cc = palette.CLEAR_COLOR
    glClearColor(cc[0], cc[1], cc[2], 1.0)

    data = parse_corridor(path)
    corridor = build_corridor(data, origin=(0, 0, 0), direction=(0, 0, -1))

    texcache = render.TexCache()
    ship = render.Ship(home_pos=(0.0, 0.0, 8.0))   # just outside the mouth

    clock = pygame.time.Clock()
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

        # demo: defeat first robot after 4s to show the museum plaque
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

        corridor.draw_world(cam_right, cam_up, texcache)    # 1. queue walls + chevrons
        render.flush_walls(tuple(ship.pos.tolist()))        # 2. draw walls
        corridor.draw_robots(cam_right, cam_up, texcache)   # 3. robots AFTER walls (hologram safe)
        corridor.draw_labels(cam_right, cam_up, texcache)   # 4. title + plaques

        pygame.display.flip()


def _quit():
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "corridors/01_dummy.txt")