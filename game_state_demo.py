"""game_state_demo.py -- DESCENT QED, Brief #13 acceptance demo.

RUN:  python game_state_demo.py   (from repo root, same as app.py)

This is app.py's real init + canonical frame loop, VERBATIM, with the four
GameState wiring lines added (marked  # [GS]  ) and nothing else changed in
the loop. It exists so Nir can SEE the whole game working:

  1. Fly to a corridor's couple -> "HOSTAGES RESCUED" flashes, the two
     people DISAPPEAR (aboard ship), status shows RESCUED 1/N.
  2. Kill that corridor's robots -> the corridor is marked complete.
  3. Do it for every corridor -> "LEVEL COMPLETE" banner. No fail ever.
  4. Walls still present (the flush trap is untouched).
  5. Flying away after rescue does NOT un-rescue (the bit is sticky).

THE COUPLE-DISAPPEAR GUARD: in production this is a one-line sticky guard in
corridor_builder.CorridorGeometry.draw_robots (see the wiring lines). So Nir
can run THIS demo without editing corridor_builder.py, we install the SAME
guard at runtime here by wrapping each corridor's draw_robots once.

NO lose state anywhere. Win only.
"""

import sys

import pygame
from OpenGL.GL import (
    glClear, glClearColor, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
)

import render
import palette
import combat
from level_parser import load_level
from content_parser import ParseError
from hub_builder import build_hub

from game_state import GameState                      # [GS]


WIN_SIZE = (1280, 800)
LEVEL_MANIFEST = "levels/maxwell.txt"
FOG_START = 40
FOG_END = 140
SHOW_HUD = False


def _load_level_or_die(manifest_path):
    try:
        return load_level(manifest_path)
    except ParseError as e:
        print(f"[demo] cannot load level {manifest_path!r}: {e}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"[demo] cannot read level {manifest_path!r}: {e}", file=sys.stderr)
        sys.exit(2)


def _make_ship(hub):
    spawn_pos, _yaw_pitch = hub.spawn_pose()
    ship = render.Ship(spawn_pos)
    poses = hub.door_poses()
    if poses:
        _door_center, fwd = poses[0]
        ship.q = render.quat_look_along(fwd)
    return ship


def _install_rescue_draw_guard(hub):
    """Demo-only: wrap each corridor's draw_robots so its HOSTAGE loop is
    skipped once corridor.hostages_rescued is True. Reproduces the one-line
    production guard WITHOUT editing corridor_builder.py."""
    for corridor in hub.corridors:
        original = corridor.draw_robots

        def make_guarded(corr, orig):
            def guarded(cr, cu, texcache):
                if getattr(corr, "hostages_rescued", False):
                    saved = corr._hostages
                    corr._hostages = []
                    try:
                        orig(cr, cu, texcache)
                    finally:
                        corr._hostages = saved
                else:
                    orig(cr, cu, texcache)
            return guarded

        corridor.draw_robots = make_guarded(corridor, original)


def _draw_debug_hud(texcache, fps, ship):
    w, h = WIN_SIZE
    px, py, pz = float(ship.pos[0]), float(ship.pos[1]), float(ship.pos[2])
    line = r"\mathrm{fps}\ %d \quad \mathrm{pos}\ (%.0f,\ %.0f,\ %.0f)" % (
        int(fps), px, py, pz)
    render.begin_2d(w, h)
    render.draw_text_mathtext_2d(texcache, line, 12, 12,
                                 color=palette.WORLD_EDGE, fontsize=18)
    render.end_2d()


def main():
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("DESCENT QED -- GAME STATE DEMO (Brief #13)")

    render.init_gl(WIN_SIZE)
    texcache = render.TexCache()

    level = _load_level_or_die(LEVEL_MANIFEST)
    hub = build_hub(level, atrium_center=(0, 0, 0))

    _install_rescue_draw_guard(hub)                   # [GS] demo-only guard

    ship = _make_ship(hub)
    combat_state = combat.Combat()

    game_state = GameState(hub)                       # [GS] construct once

    from gamepad import GamepadManager
    from understanding import UnderstandingMode
    try:
        gamepads = GamepadManager()
    except Exception:
        gamepads = None
    umode = UnderstandingMode()

    render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)

    clock = pygame.time.Clock()
    running = True
    prev_keys = pygame.key.get_pressed()
    mouse_click_edge = False
    mouse_x = mouse_y = 0
    while running:
        dt = clock.tick(60) / 1000.0

        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and not umode.active:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_u and not umode.active:
                robot = combat.Combat.blocking_robot(hub)
                if robot is not None:
                    umode.open(robot._robot_data)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_click_edge = True
                mouse_x, mouse_y = ev.pos

        keys = pygame.key.get_pressed()

        if umode.active:
            umode.handle_input(events, keys, gamepads, dt)
        else:
            fire_edge  = keys[pygame.K_SPACE]          and not prev_keys[pygame.K_SPACE]
            prev_edge  = keys[pygame.K_LEFTBRACKET]    and not prev_keys[pygame.K_LEFTBRACKET]
            next_edge  = keys[pygame.K_RIGHTBRACKET]   and not prev_keys[pygame.K_RIGHTBRACKET]

        # ---- CANONICAL FRAME ORDER ----
        glClearColor(*palette.CLEAR_COLOR, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not umode.active:
            ship.update(dt, keys)
            ship.apply_view()
            render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)
            cr = render.ship_right(ship.q)
            cu = render.ship_up(ship.q)

            hub.update(dt, ship.pos)

            game_state.update(hub, ship.pos, dt)      # [GS] AFTER hub.update

            combat_state.handle_input(fire_edge, prev_edge, next_edge, ship, hub,
                                      mouse_click_edge, mouse_x, mouse_y, gamepads)
            combat_state.update(dt, ship, hub)
            mouse_click_edge = False

        if not umode.active:
            hub.draw_world(cr, cu, texcache)
            render.flush_walls(ship.pos)              # untouched flush trap
            hub.draw_robots(cr, cu, texcache)
            hub.draw_labels(cr, cu, texcache)
            combat_state.draw_projectile_3d(cr, cu, texcache)

        render.begin_2d(*WIN_SIZE)
        combat_state.draw_hud(texcache, WIN_SIZE)
        game_state.draw_hud(texcache, WIN_SIZE)       # [GS] HUD beat
        umode.draw(texcache, WIN_SIZE)

        if umode.active and gamepads is not None and gamepads.manip_joy is not None:
            j = gamepads.manip_joy
            dbg = "axes: " + " ".join("a%d=%+.2f" % (k, j.get_axis(k))
                                      for k in range(j.get_numaxes()))
            render.draw_text_mathtext_2d(texcache, dbg, 20, WIN_SIZE[1]-30,
                                         color=(0.6,0.9,0.6), fontsize=12)
        render.end_2d()

        if SHOW_HUD:
            _draw_debug_hud(texcache, clock.get_fps(), ship)

        pygame.display.flip()
        prev_keys = keys

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
