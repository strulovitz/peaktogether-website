"""robots_demo.py -- proof scene for MODULE: robots.

Flies render's DEMO-ONLY Ship camera around two robots built straight from
the real fixture, proving the data path: ledger -> palette.eye -> SCANNER
color against grey-metal hulls, with the real hologram PORTRAITS floating
above (copy the PNGs next to this file):
    Brook_Taylor-hologram.png
    Leonhard_Euler-hologram.png

Controls:
    flight  : render's demo Ship (reads keys directly via ship.update)
    K       : play_defeat() on the nearest live robot
    ESC     : quit
"""

import sys
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT, KEYDOWN, K_ESCAPE, K_k
from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

import content_parser
from palette import Palette
import render
from robots import Robot

WIN_SIZE = (1280, 800)


def main():
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("DESCENT QED -- robots demo")

    render.init_gl(WIN_SIZE)
    render.set_fog(start=render.DARKNESS_START, end=render.DARKNESS_END)

    # --- DATA PATH (end to end) ---
    corridor = content_parser.parse_corridor("corridors/01_dummy.txt")
    palette = Palette(corridor.ledger)

    pose_A = (-4.0, 0.0, -14.0)
    pose_B = (4.0, 0.0, -14.0)
    robots = [
        Robot(corridor.robots[0], palette, pose_A, size=1.4),
        Robot(corridor.robots[1], palette, pose_B, size=1.4),
    ]

    texcache = render.TexCache()
    ship = render.Ship(home_pos=(0.0, 0.0, 0.0))
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_k:
                    sp = ship.pos
                    live = [r for r in robots if not r.is_defeated()]
                    if live:
                        nearest = min(
                            live,
                            key=lambda r: float(
                                ((r._world_center() - sp) ** 2).sum()))
                        nearest.play_defeat()

        ship.update(dt, pygame.key.get_pressed())

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ship.apply_view()

        cam_r = render.ship_right(ship.q)
        cam_u = render.ship_up(ship.q)

        for r in robots:
            r.update(dt, ship.pos)
        for r in robots:
            r.draw(cam_r, cam_u, texcache)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
