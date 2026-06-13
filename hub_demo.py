"""
hub_demo.py — standalone flythrough of the DESCENT QED atrium hub.

Frame loop obeys the CANONICAL FRAME ORDER:
    clear -> set_fog -> hub.update(dt, ship.pos)
    -> hub.draw_world(cr,cu,tc)        # QUEUE walls
    -> render.flush_walls(ship.pos)    # EXACTLY ONCE, after draw_world
    -> hub.draw_robots(cr,cu,tc)
    -> hub.draw_labels(cr,cu,tc)
    -> flip

Fly with WASD / arrows (ship.update). Spawn at hub.spawn_pose() facing
the first doorway; fly out a door, down the bent corridor, to the blue
cavern, and back.

Set N below (1, 3, 7, 12) to verify door spread on the sphere. Only the
fixture corridors/01_dummy.txt exists, so we duplicate it to reach N>1.
"""

import sys
import math
import pygame
from OpenGL.GL import glClear, glClearColor, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT

import render
import palette
from content_parser import discover_corridors, parse_corridor
from hub_builder import build_hub

WIN_SIZE = (1280, 800)
N = 7   # try 1, 3, 7, 12


def load_n_corridors(n):
    """Return a list[CorridorData] of length n. Only 01_dummy.txt exists,
    so we reuse the discovered fixtures, cycling/duplicating to reach n."""
    found = discover_corridors("corridors")
    if not found:
        # Fallback: parse the known single fixture directly.
        found = [parse_corridor("corridors/01_dummy.txt")]
    out = []
    i = 0
    while len(out) < n:
        out.append(found[i % len(found)])
        i += 1
    return out


def main():
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption(f"DESCENT QED — hub_demo (N={N})")

    render.init_gl(WIN_SIZE)
    texcache = render.TexCache()

    level_data = load_n_corridors(N)
    hub = build_hub(level_data, atrium_center=(0, 0, 0))

    # Spawn at the atrium center, facing the first doorway.
    spawn_pos, _yawpitch = hub.spawn_pose()
    ship = render.Ship(spawn_pos)
    # NOTE: spawn_pose returns (yaw,pitch) for game_state's orientation.
    # render.Ship manages its own quaternion; we seat the ship at the
    # spawn position and let the player aim. (No quat_look_along exists.)

    render.set_fog(start=40, end=140, color=palette.CLEAR_COLOR)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        ship.update(dt, keys)

        # ---- CANONICAL FRAME ORDER ----
        glClearColor(*palette.CLEAR_COLOR, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        ship.apply_view()

        render.set_fog(start=40, end=140, color=palette.CLEAR_COLOR)

        cr = render.ship_right(ship.q)
        cu = render.ship_up(ship.q)

        hub.update(dt, ship.pos)
        hub.draw_world(cr, cu, texcache)         # QUEUE walls only
        render.flush_walls(ship.pos)             # flush EXACTLY ONCE
        hub.draw_robots(cr, cu, texcache)        # robots after flush
        hub.draw_labels(cr, cu, texcache)        # billboards last

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()