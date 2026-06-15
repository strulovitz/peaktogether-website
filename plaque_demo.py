"""
plaque_demo.py -- Brief #16. Verbatim app.py frame loop, plus ONE addition:
auto-defeat the blocking robot through the REAL combat path, so you can fly
up and read the full wrapped proof plaque. Run: python plaque_demo.py
"""
import sys
import pygame
from OpenGL.GL import (glClear, glClearColor,
                       GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT)

import render
import palette
import combat
from game_state import GameState
from level_parser import load_level
from content_parser import ParseError
from hub_builder import build_hub

WIN_SIZE = (1280, 800)
LEVEL_MANIFEST = "levels/maxwell.txt"
FOG_START, FOG_END = 40, 140


def _load_level_or_die(path):
    try:
        return load_level(path)
    except (ParseError, OSError) as e:
        print(f"[plaque_demo] cannot load level {path!r}: {e}", file=sys.stderr)
        sys.exit(2)


def _make_ship(hub):
    spawn_pos, _ = hub.spawn_pose()
    ship = render.Ship(spawn_pos)
    poses = hub.door_poses()
    if poses:
        _c, fwd = poses[0]
        ship.q = render.quat_look_along(fwd)
    return ship


def main():
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("DESCENT QED -- PLAQUE DEMO")
    render.init_gl(WIN_SIZE)
    texcache = render.TexCache()

    level = _load_level_or_die(LEVEL_MANIFEST)
    hub = build_hub(level, atrium_center=(0, 0, 0))
    ship = _make_ship(hub)

    combat_state = combat.Combat()
    game_state = GameState(hub)
    render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)

    clock = pygame.time.Clock()
    running = True
    autodef_timer = 0.0

    while running:
        dt = clock.tick(60) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False
        keys = pygame.key.get_pressed()

        glClearColor(*palette.CLEAR_COLOR, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        ship.update(dt, keys)
        ship.apply_view()
        render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)
        cr = render.ship_right(ship.q)
        cu = render.ship_up(ship.q)
        hub.update(dt, ship.pos)
        game_state.update(hub, ship.pos, dt)

        # DEMO ONLY: defeat the blocking robot via the real combat path
        autodef_timer += dt
        if autodef_timer < 4.0:
            combat_state.handle_input(True, False, False, ship, hub,
                                      False, 0, 0, None)
        combat_state.update(dt, ship, hub)

        hub.draw_world(cr, cu, texcache)
        render.flush_walls(ship.pos)
        hub.draw_robots(cr, cu, texcache)
        hub.draw_labels(cr, cu, texcache)
        combat_state.draw_projectile_3d(cr, cu, texcache)

        render.begin_2d(*WIN_SIZE)
        combat_state.draw_hud(texcache, WIN_SIZE)
        game_state.draw_hud(texcache, WIN_SIZE)
        render.end_2d()

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
