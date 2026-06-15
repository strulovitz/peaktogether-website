"""hostages_demo.py -- DESCENT QED: SEE the two hostages NOW.

Nir RUNS this. It reuses app.py's window/GL/fog/ship/hub scaffolding
VERBATIM (minus gameplay: no combat / understanding / gamepad), loads a
real level, spawns facing door 0, and runs the CANONICAL frame loop with
flush_walls EXACTLY ONCE in slot 8.

Because corridor_builder is NOT wired yet (the parent will add that), the
DEMO itself builds + updates + draws the two hostages per corridor in the
draw_robots slot -- exactly where the parent will later wire them -- so Nir
can SEE them today.

Controls (from render.Ship): W/S fwd/back, A/D strafe, R/F up/down,
arrows pitch/yaw, Q/E roll, SHIFT boost, ESC quit.

ACCEPTANCE: fly to a blue cavern -> TWO glowing 3D PEOPLE standing together,
facing you, recognizable bodies, popping against the blue; exactly two per
cavern; gentle idle life; no black screen; a NEAR line prints when close.
"""

import sys

import pygame
from OpenGL.GL import (
    glClear, glClearColor, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
)

import render
import palette
from level_parser import load_level
from content_parser import ParseError
from hub_builder import build_hub

import hostages


# --- config (verbatim from app.py) ---
WIN_SIZE = (1280, 800)
LEVEL_MANIFEST = "levels/maxwell.txt"   # swap to levels/intro.txt if preferred
FOG_START = 40
FOG_END = 140


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
    """Seat the ship at spawn, facing door 0 -- copied from app._make_ship."""
    spawn_pos, _yaw_pitch = hub.spawn_pose()
    ship = render.Ship(spawn_pos)
    poses = hub.door_poses()
    if poses:
        _door_center, fwd = poses[0]
        ship.q = render.quat_look_along(fwd)
    return ship


def main():
    # --- window + GL (verbatim from app.py) ---
    pygame.init()
    pygame.display.set_mode(WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("DESCENT QED -- HOSTAGES DEMO")

    render.init_gl(WIN_SIZE)
    texcache = render.TexCache()

    level = _load_level_or_die(LEVEL_MANIFEST)
    hub = build_hub(level, atrium_center=(0, 0, 0))
    ship = _make_ship(hub)

    # Build the couple for EVERY corridor up front (the demo owns them since
    # corridor_builder isn't wired yet). Stored parallel to hub.corridors.
    couples = [hostages.build_hostages(c) for c in hub.corridors]
    total = sum(len(c) for c in couples)
    print("[demo] built %d hostages across %d corridors (%d per cavern)"
          % (total, len(hub.corridors),
             (len(couples[0]) if couples else 0)))

    render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)

    clock = pygame.time.Clock()
    running = True
    _near_latch = False   # so we print the NEAR line on enter/leave, not every frame

    while running:
        dt = clock.tick(60) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()

        # ---- CANONICAL FRAME ORDER (app.py slots 1-11) ----
        # 1. clear
        glClearColor(*palette.CLEAR_COLOR, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 2. movement
        ship.update(dt, keys)

        # 3. camera matrix
        ship.apply_view()

        # 4. fog
        render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)

        # 5. camera basis
        cr = render.ship_right(ship.q)
        cu = render.ship_up(ship.q)

        # 6. world update (corridors/robots) + our hostages' idle life
        hub.update(dt, ship.pos)
        for couple in couples:
            for h in couple:
                h.update(dt)

        # 7. QUEUE walls only -- NO flush inside
        hub.draw_world(cr, cu, texcache)

        # 8. THE FLUSH -- EXACTLY ONCE, after draw_world, before robots/labels.
        render.flush_walls(ship.pos)

        # 9. robots (after flush) ... and OUR hostages in the same slot,
        #    exactly where the parent will wire corridor.draw_hostages().
        hub.draw_robots(cr, cu, texcache)
        for couple in couples:
            for h in couple:
                h.draw(cr, cu, texcache)

        # 10. labels
        hub.draw_labels(cr, cu, texcache)

        # ---- NEAR status (pure geometry via near_hostages); print on edges ----
        near_any = any(hostages.near_hostages(couple, ship.pos)
                       for couple in couples)
        if near_any and not _near_latch:
            print("[demo] NEAR the couple -- within rescue radius.")
            _near_latch = True
        elif not near_any and _near_latch:
            print("[demo] left the couple -- flying away.")
            _near_latch = False

        # 11. present
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
