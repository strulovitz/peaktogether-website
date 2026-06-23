"""
app.py — DESCENT QED engine: minimal integration entry point.

Launch:  python app.py   (no args, from repo root)

PURPOSE (integration proof, NOT gameplay):
    Load a LEVEL from a manifest, build the central atrium hub + its
    radiating corridors, spawn the ship facing the first doorway, and fly.

PRIME LAW — MATHEMATICS-BLIND:
    This module arranges nothing mathematical and assigns no color. It never
    constructs a Palette or a ColorLedger and never passes one anywhere. All
    color/meaning lives inside hub_builder/palette. app passes through ONLY
    the camera basis (cr, cu) and a TexCache to the three hub draw calls.

CANONICAL FRAME ORDER (obeyed verbatim; the cardinal trap is the flush):
     1. clear color + depth
     2. ship.update(dt, keys)        # movement (controls baked into render.Ship)
     3. ship.apply_view()            # load camera matrix
     4. render.set_fog(...)          # production fog values (from hub_demo.py)
     5. cr = render.ship_right(ship.q);  cu = render.ship_up(ship.q)
     6. hub.update(dt, ship.pos)
     7. hub.draw_world(cr, cu, tc)   # QUEUE walls only — NO flush inside
     8. render.flush_walls(ship.pos) # <-- EXACTLY ONCE, here, or walls never draw
     9. hub.draw_robots(cr, cu, tc)
    10. hub.draw_labels(cr, cu, tc)
    11. pygame.display.flip()

All window/GL/Ship/TexCache/fog scaffolding is copied verbatim from the
working hub_demo.py, with two deliberate, file-justified changes:
  * we load a real LEVEL via level_parser.load_level (the brief's path),
    instead of hub_demo's discover+duplicate shim;
  * we AIM the ship at door 0 via render.quat_look_along — hub_demo's stale
    comment "(No quat_look_along exists.)" predates render.py, which DOES
    define quat_look_along (verified in the pasted render API). The pasted
    file is law, so we use it. Result: ship spawns facing a doorway.
"""

# --- Peak Together bootstrap (must run before pygame / asset loading) ---
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pt_runtime import bootstrap
bootstrap("DescentQED")
# --- end bootstrap ---

import sys

import pygame
from OpenGL.GL import (
    glClear, glClearColor, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
)

import render
import palette
import combat                            # Brief #9
import containment                       # Brief #C1: ship collision/containment
from game_state import GameState          # Brief #13
from level_parser import load_level
from content_parser import ParseError
from hub_builder import build_hub


# ---------------------------------------------------------------------------
# Configuration (single source — no magic numbers buried in the loop)
# ---------------------------------------------------------------------------

WIN_SIZE = (1280, 800)          # verbatim from hub_demo.py
LEVEL_MANIFEST = "levels/basel.txt"

# Fog: production values, copied verbatim from hub_demo.py. These equal
# render.DARKNESS_START / DARKNESS_END, i.e. render's own defaults — not
# invented numbers.
FOG_START = 40
FOG_END = 140

# Optional tiny debug overlay (fps + ship pos). OFF: this is a bare
# integration proof with zero gameplay. Flip to True only for debugging;
# it uses render's existing 2D path (begin_2d / draw_text_mathtext_2d /
# end_2d) and adds no new infrastructure.
SHOW_HUD = False


# ---------------------------------------------------------------------------
# Level loading (clean failure, never a raw traceback for content problems)
# ---------------------------------------------------------------------------

def _load_level_or_die(manifest_path):
    """Load the level manifest. On any structural/content problem, print a
    single readable line and exit non-zero — a missing/broken manifest is a
    CONTENT issue, not a crash, and must not look like a GL failure."""
    try:
        return load_level(manifest_path)
    except ParseError as e:
        print(f"[app] cannot load level {manifest_path!r}: {e}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"[app] cannot read level {manifest_path!r}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Spawn (PATH 1: build-time aim via quat_look_along)
# ---------------------------------------------------------------------------

def _make_ship(hub):
    """Seat the ship at the atrium spawn position, facing the FIRST doorway.

    Position comes from hub.spawn_pose() (NOT hardcoded (0,0,0), so it
    survives any future atrium_center change). Forward direction is door 0's
    OUTWARD normal from hub.door_poses(). Orientation is set via the verified
    render.quat_look_along, which guarantees ship_forward(q) == normalize(d).

    Zero-corridor guard: if the level has no doors, door_poses() is empty;
    we leave the ship at render.Ship's default orientation (looks -Z).
    """
    spawn_pos, _yaw_pitch = hub.spawn_pose()
    ship = render.Ship(spawn_pos)

    poses = hub.door_poses()
    if poses:
        _door_center, fwd = poses[0]
        ship.q = render.quat_look_along(fwd)
    return ship


# ---------------------------------------------------------------------------
# Optional debug overlay (gameplay-free; behind SHOW_HUD)
# ---------------------------------------------------------------------------

def _draw_debug_hud(texcache, fps, ship):
    """Tiny non-gameplay overlay using render's existing 2D path."""
    w, h = WIN_SIZE
    px, py, pz = float(ship.pos[0]), float(ship.pos[1]), float(ship.pos[2])
    line = r"\mathrm{fps}\ %d \quad \mathrm{pos}\ (%.0f,\ %.0f,\ %.0f)" % (
        int(fps), px, py, pz)
    render.begin_2d(w, h)
    render.draw_text_mathtext_2d(texcache, line, 12, 12,
                                 color=palette.WORLD_EDGE, fontsize=18)
    render.end_2d()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # --- window + GL context (verbatim from hub_demo.py) ---
    pygame.init()
    # NOTE (macOS): if the window is solid black, it is the legacy GL profile
    # issue noted in render.py beside set_mode in render_demo.py. The flags
    # below are exactly what the working hub_demo.py uses.
    pygame.display.set_mode(WIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("DESCENT QED")

    render.init_gl(WIN_SIZE)
    texcache = render.TexCache()

    # --- build the world from the level manifest ---
    level = _load_level_or_die(LEVEL_MANIFEST)
    # build_hub iterates its argument (Level is iterable -> CorridorData) and
    # reads .title off each item; passing the Level directly is supported.
    hub = build_hub(level, atrium_center=(0, 0, 0))

    # --- spawn facing door 0 (PATH 1) ---
    ship = _make_ship(hub)

    # Brief #9: combat state (owns fire/match/HUD)
    combat_state = combat.Combat()

    # Brief #13: game state (rescue, corridor/level complete, HUD)
    game_state = GameState(hub)

    # Brief #11: Understanding Mode (4-layer depth panels)
    from gamepad import GamepadManager
    from understanding import UnderstandingMode
    try:
        gamepads = GamepadManager()
    except Exception:
        gamepads = None   # no controller -> mode runs on mouse+keyboard
    umode = UnderstandingMode()

    # Initial fog set (matches hub_demo.py, which sets it once at setup and
    # again every frame; we mirror that).
    render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)

    # -- Brief #J1B: T.16000M pilot button reader (digital buttons) --
    # Safe against: no controller, no pilot device, or fewer buttons than idx.
    # Used for the index-finger trigger (button 0 = FIRE). Read with the SAME
    # helper everywhere so the edge computation and the per-frame snapshot can
    # never drift apart.
    def _pilot_btn(idx):
        if gamepads is None:
            return False
        pj = getattr(gamepads, "pilot_joy", None)
        if pj is None or pj.get_numbuttons() <= idx:
            return False
        try:
            return bool(pj.get_button(idx))
        except Exception:
            return False

    clock = pygame.time.Clock()
    running = True
    prev_keys = pygame.key.get_pressed()   # Brief #9: rising-edge tracking
    prev_pilot_fire = _pilot_btn(0)        # Brief #J1B: trigger rising-edge state
    mouse_click_edge = False               # Brief #10: mouse selection
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
                robot = combat.Combat.robot_in_view(hub, ship)  # look-at selection, not combat gate
                if robot is not None:
                    umode.open(robot._robot_data)  # Brief #11: pass RobotData, not Robot
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mouse_click_edge = True            # Brief #10: face panel selection
                mouse_x, mouse_y = ev.pos

        keys = pygame.key.get_pressed()

        # Rising-edge detection — computed UNCONDITIONALLY every frame so edge
        # state never goes stale across Understanding Mode (this is what keeps
        # the trigger from phantom-firing the instant U-mode exits).
        #   fire_edge = SPACE (keyboard) OR pilot trigger (T.16000M button 0),
        #               each rising-edged and ADDITIVE.
        pilot_fire_now = _pilot_btn(0)
        fire_edge = bool((keys[pygame.K_SPACE] and not prev_keys[pygame.K_SPACE])
                         or (pilot_fire_now and not prev_pilot_fire))
        prev_edge = keys[pygame.K_LEFTBRACKET]  and not prev_keys[pygame.K_LEFTBRACKET]
        next_edge = keys[pygame.K_RIGHTBRACKET] and not prev_keys[pygame.K_RIGHTBRACKET]

        # Brief #11: gate world updates when Understanding Mode is active
        if umode.active:
            umode.handle_input(events, keys, gamepads, dt)

        # ---- CANONICAL FRAME ORDER ----
        # 1. clear
        glClearColor(*palette.CLEAR_COLOR, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not umode.active:
            # 2. movement (keyboard + analog joystick, ADDITIVE -- Brief #J1)
            prev_pos = ship.pos.copy()          # Brief #C1: last legal position
            # Brief #J1: read the T.16000M pilot stick (None = no device or the
            # ~1s startup calibration window; keyboard still flies meanwhile).
            cmd = gamepads.pilot_command() if gamepads is not None else None
            ship.update6dof(dt, keys, cmd)      # sets a TENTATIVE new ship.pos
            containment.resolve(ship, hub, prev_pos)  # Brief #C1: hard-stop+slide
                                                #   (corrects ship.pos/.vel in place,
                                                #    BEFORE the camera is built)

            # 3. camera matrix
            ship.apply_view()

            # 4. fog (production values)
            render.set_fog(start=FOG_START, end=FOG_END, color=palette.CLEAR_COLOR)

            # 5. camera basis for billboards/labels
            cr = render.ship_right(ship.q)
            cu = render.ship_up(ship.q)

            # 6. advance world animation / corridor state
            hub.update(dt, ship.pos)

            # Brief #13: game state (rescue trigger, progress)
            game_state.update(hub, ship.pos, dt)

            # Brief #9+10: combat (fire, auto-face, fizzle timer + face panel selection)
            combat_state.handle_input(fire_edge, prev_edge, next_edge, ship, hub,
                                      mouse_click_edge, mouse_x, mouse_y, gamepads)
            combat_state.update(dt, ship, hub)
            mouse_click_edge = False             # Brief #10: consume edge

        if not umode.active:
            # 7. QUEUE all walls (atrium shell + door frames + corridor walls)
            hub.draw_world(cr, cu, texcache)

            # 8. THE FLUSH — exactly once, after draw_world, before robots/labels.
            #    Omit/duplicate this and walls silently never draw (the cardinal trap).
            render.flush_walls(ship.pos)

            # 9. robots (immediate; after the wall flush)
            hub.draw_robots(cr, cu, texcache)

            # 10. labels / billboards (mathtext; last)
            hub.draw_labels(cr, cu, texcache)

            # Brief #10: 3D projectile (after flush, before 2D overlay)
            combat_state.draw_projectile_3d(cr, cu, texcache)

        # Brief #9: combat HUD (text only; between labels and flip)
        render.begin_2d(*WIN_SIZE)
        combat_state.draw_hud(texcache, WIN_SIZE)
        game_state.draw_hud(texcache, WIN_SIZE)    # Brief #13: rescue flash + status + level complete
        umode.draw(texcache, WIN_SIZE)                      # Brief #11

        # Brief #11: temporary right-stick axis picker (verify XBOX_RSTICK_X/Y)
        if umode.active and gamepads is not None and gamepads.manip_joy is not None:
            j = gamepads.manip_joy
            dbg = "axes: " + " ".join("a%d=%+.2f" % (k, j.get_axis(k))
                                      for k in range(j.get_numaxes()))
            render.draw_text_mathtext_2d(texcache, dbg, 20, WIN_SIZE[1]-30,
                                         color=(0.6,0.9,0.6), fontsize=12)
        render.end_2d()

        # optional debug overlay (off by default)
        if SHOW_HUD:
            _draw_debug_hud(texcache, clock.get_fps(), ship)

        # 11. present
        pygame.display.flip()

        # Snapshots for next frame's rising edges — BOTH unconditional, every
        # frame, so neither keyboard nor pilot-trigger edge state goes stale.
        prev_keys = keys
        prev_pilot_fire = _pilot_btn(0)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
