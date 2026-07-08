"""
LOOM2 -- main.py
Entry point. THIN: builds everything, runs the loop, owns NO logic.
Allowed imports: pyglet, config, all project modules.
Child chat scope: implement all bodies. ~120 lines expected.

------------------------------------------------------------------------------
IMPLEMENTATION NOTES (Parent G, 2026-07-08)

THE LOOP (DeepSeek Q7, verified from the shipped quake/app.py precedent):
  A MANUAL loop -- window.dispatch_events() / frame() / window.flip() -- NOT
  pyglet.app.run(), NOT schedule_interval, and NO on_draw handler (so pyglet
  can never double-draw). input_map pushed its own key/mouse handlers at
  construction; dispatch_events() services them, and frame step 1 drains the
  resulting queue via input.poll(). vsync=True paces the loop at the display
  rate; dt is measured (perf_counter) and clamped by MAX_DT so a debugger
  pause or window drag can never teleport the totem.

WINDOW (Nir's rulings, 2026-07-08): 1280x720 from config, caption EXACTLY
  "LOOM2 — Sonifiquation", resizable=False (framebuffers are fixed-size;
  nothing can ever look stretched). NO set_exclusive_mouse -- the girlfriend's
  mouse y-axis and the hud hit-test need the real cursor (Q7). The BARE window
  is created first; Renderer(window) creates the moderngl context internally
  (Parent C) -- main never touches GL.

WIRING TRUTHS HONORED HERE (sources in brackets):
  * spec0 is loaded EARLY by main; GameState.__init__ reloads the same scene
    internally -- load_scene is pure, the double-load is sanctioned [Q1].
  * ONE OrbitCamera for the whole run. GameState stores the reference and
    drives it; rebuilding it would orphan that reference. When DeepSeek's
    additive OrbitCamera.set_limits() lands (the G3.2-A debt), the hasattr
    guard in _apply_scene starts calling it automatically [Q2b].
  * blade.update_plane + set_walk_stop EVERY frame (cheap state stores);
    blade.draw only in SLICE. snap["slice_plane"] always exists and its
    .visible is True exactly in SLICE mode -- that is the gate used here,
    so main never inspects the mode value's type [Q3].
  * snapshot() is called EXACTLY once per frame -- scene_changed is
    read-and-clear [G4.5]. GameState.__init__ sets scene_changed=True, so
    frame 1 deliberately runs the scene-change path: the boot terrain is
    released and rebuilt identically, and hud gets its first set_scene there
    (Hud is scene-less-safe by construction -- Parent F's guarantee).
  * main NEVER calls engine.set_camera_azimuth -- game_state's job [Q9].
  * helix_panel.z_per_octave (public attribute) is set on every scene change,
    including frame 1's [Q10].
  * hud.draw is LAST, always; hud sets its own 2D GL state [Parent F].

SHUTDOWN (Q8): snap["quit"] is the ONLY sanctioned in-game exit (Esc flows
  input_map -> game_state; pyglet's default Esc-close is deliberately blocked
  by input_map). The window's X button sets window.has_exit. BOTH paths break
  the same loop and reach the same try/finally: engine.stop() FIRST (audio
  must never die dirty; stop() is idempotent), then window.close().
------------------------------------------------------------------------------
"""

import time  # CONTRACT-ISSUE: the header allows only pyglet/config/project
             # modules, but the sanctioned manual loop (DeepSeek Q7, verified
             # quake/app.py precedent) requires time.perf_counter for dt.
             # Flagged, not hidden.

import pyglet

import config
from audio.engine import AudioEngine
from audio.sampler import SampleLibrary
from core import scene, surfaces
from core.game_state import GameState
from core.input_map import InputMap
from graphics.camera import OrbitCamera
from graphics.helix_panel import HelixPanel
from graphics.hud import Hud
from graphics.renderer import Renderer
from graphics.slice_mode import GlassBlade
from graphics.terrain import TerrainMesh
from graphics.totem import TotemVisual


WINDOW_CAPTION = "LOOM2 — Sonifiquation"   # Nir's exact string, 2026-07-08
MAX_DT = 0.1   # seconds; clamp so a stall (drag, debugger) can't teleport


# =============================================================================
# SCENE APPLICATION -- the one mutation main performs (used on scene_changed,
# including the deliberate frame-1 trigger). Full sequence verified [Q2a].
# =============================================================================

def _apply_scene(objs: dict, spec) -> None:
    """Rebuild/retune everything that is per-scene. Order matters: release
    the old mesh BEFORE building the new one (G3.3-A -- GPU buffers freed)."""
    surface_fn = surfaces.get(spec.surface_name)
    objs["terrain"].release()                                    # G3.3-A
    objs["terrain"] = TerrainMesh(objs["renderer"], surface_fn,
                                  spec.domain, spec.mesh_step)
    objs["surface_fn"] = surface_fn
    objs["blade"].set_domain(spec.domain)                        # G3.6-A
    objs["hud"].set_scene(spec)
    objs["helix_panel"].z_per_octave = spec.z_per_octave         # Q10, PURANAS
    if hasattr(objs["camera"], "set_limits"):                    # Q2b: future
        objs["camera"].set_limits(spec.camera_limits)            # G3.2-A debt


# =============================================================================
# BUILD -- boot order FROZEN (G4.5), calls amended per the reconciled truth
# =============================================================================

def build() -> dict:
    """Boot order (FROZEN):
      1. pyglet window (config.WINDOW_W/H)      2. Renderer(window)
      3. SampleLibrary()                        4. AudioEngine(library).start()
      5. OrbitCamera(scene limits)              6. Hud(window)
      7. GameState(engine, camera, first scene) 8. InputMap(window, hud)
      9. TerrainMesh / TotemVisual / HelixPanel / GlassBlade per scene
    Returns dict of all objects. On scene change GameState raises a
    'scene_changed' flag in snapshot(); main rebuilds TerrainMesh + hud.set_scene.

    (Parent G, beyond the frozen text: step 6 is Hud(window, renderer) per
    Parent F's blessed additive signature; step 0 loads the first SceneSpec
    early [Q1] so step 5 has real camera limits and step 9 has real domain/
    mesh_step. If anything fails AFTER the audio stream opens, the engine is
    stopped before the exception escapes -- the audio thread never leaks.)
    """
    # 0. Content first -- pure, double-load harmless [Q1]. Fails loud here
    #    (SceneError) before any device or window exists: best possible timing.
    first_id = scene.campaign_order()[0]
    spec0 = scene.load_scene(first_id)
    surface_fn = surfaces.get(spec0.surface_name)

    # 1. Bare window -- no GL context here; Renderer owns that [Q7].
    window = pyglet.window.Window(
        width=config.WINDOW_W, height=config.WINDOW_H,
        caption=WINDOW_CAPTION, resizable=False, vsync=True)

    # 2. Renderer creates the moderngl context + panel FBOs.
    renderer = Renderer(window)

    # 3.-4. The orchestra: samples, then the live engine.
    library = SampleLibrary()
    engine = AudioEngine(library)
    engine.start()
    try:
        status = engine.get_status()   # boot sanity print (Nir approved)
        print(f"[LOOM2] audio up: mode={status['mode']} "
              f"(requested {status['requested_mode']}), "
              f"device_channels={status['device_channels']}, "
              f"running={status['running']}, error={status['error']}")

        # 5. ONE camera for the whole run -- never rebuilt [Q2b].
        camera = OrbitCamera(spec0.camera_limits)

        # 6. Hud(window, renderer) -- Parent F's blessed additive signature.
        hud = Hud(window, renderer)

        # 7. The conductor. Loads first_id itself (sanctioned double-load),
        #    seats the grid, plants the totem, pushes initial voices,
        #    and sets scene_changed=True for frame 1.
        state = GameState(engine, camera, first_id)

        # 8. The hands. Pushes its own pyglet handlers; main only polls.
        input_map = InputMap(window, hud)
        input_map.attach_joystick()    # safe no-ops today, kind to call
        input_map.attach_xbox()        # (DeepSeek fills them later)

        # 9. Per-scene visuals (frame 1's scene_changed path re-applies these
        #    via _apply_scene -- contractually intended, harmless).
        terrain = TerrainMesh(renderer, surface_fn, spec0.domain, spec0.mesh_step)
        totem_visual = TotemVisual(renderer)
        helix_panel = HelixPanel(renderer)
        blade = GlassBlade(renderer)
        blade.set_domain(spec0.domain)                           # G3.6-A
    except Exception:
        engine.stop()   # never leak a live audio thread out of a failed boot
        raise

    return {
        "window": window, "renderer": renderer, "library": library,
        "engine": engine, "camera": camera, "hud": hud, "state": state,
        "input": input_map, "terrain": terrain, "totem_visual": totem_visual,
        "helix_panel": helix_panel, "blade": blade,
        "surface_fn": surface_fn, "quit_requested": False,
    }


# =============================================================================
# FRAME -- order FROZEN (G4.5), calls amended per the reconciled truth
# =============================================================================

def frame(objs: dict, dt: float) -> None:
    """FROZEN FRAME ORDER:
      1. for (a, v) in input.poll(): state.handle_action(a, v)
      2. state.update(dt)
      3. snap = state.snapshot(); phase = engine.get_measure_phase()
      4. renderer.begin_panel('left'):  terrain.draw; totem_visual.draw;
         (SLICE mode: blade.draw)       renderer.end_panel()
      5. renderer.begin_panel('right'): helix_panel.draw(voices,
         engine.get_active_flashes(), phase); renderer.end_panel()
      6. renderer.composite()
      7. hud.draw(snap mode, state.quiz_ui_state())

    (Parent G: the scene-change rebuild runs between steps 3 and 4 so frame 1
    draws a fully-dressed scene. snap["quit"] is mirrored into
    objs["quit_requested"] for main's loop condition -- this frame still
    draws; teardown happens in main, never mid-frame.)
    """
    state, engine = objs["state"], objs["engine"]
    renderer, camera = objs["renderer"], objs["camera"]

    # 1. Input -- polled exactly once, first.
    for action, value in objs["input"].poll():
        state.handle_action(action, value)

    # 2. Simulation.
    state.update(dt)

    # 3. The one snapshot (read-and-clear!) + the musical clock.
    snap = state.snapshot()
    phase = engine.get_measure_phase()
    objs["quit_requested"] = snap["quit"]

    # 3.5 Scene change (frame 1 always lands here by construction).
    if snap["scene_changed"]:
        _apply_scene(objs, snap["scene"])

    # Blade state EVERY frame -- cheap stores, self-guarding draw [Q3].
    blade = objs["blade"]
    blade.update_plane(snap["slice_plane"])
    blade.set_walk_stop(snap["walk_stop"])                       # G4.3-A/Q4

    # 4. LEFT panel -- the land.
    terrain = objs["terrain"]
    vp_left = camera.view_proj_terrain()
    renderer.begin_panel('left')
    terrain.draw(vp_left)
    objs["totem_visual"].draw(vp_left, snap["totem"],
                              terrain.height_at, phase)          # G3.4-A: fn!
    if snap["slice_plane"].visible:      # .visible is True exactly in SLICE [Q3]
        blade.draw(vp_left, objs["surface_fn"])
    renderer.end_panel()

    # 5. RIGHT panel -- SONIFIQUATION COORDINATES.
    renderer.begin_panel('right')
    objs["helix_panel"].draw(camera.view_proj_helix(), snap["voices"],
                             engine.get_active_flashes(), phase)
    renderer.end_panel()

    # 6. Composite the panels to the screen.
    renderer.composite()

    # 7. Hud LAST, always -- it sets its own 2D GL state.
    objs["hud"].draw(snap["mode"], state.quiz_ui_state())


# =============================================================================
# MAIN -- the manual loop [Q7] and the clean death [Q8]
# =============================================================================

def main() -> None:
    """build(); pyglet clock schedules frame at 60 fps; clean engine.stop()
    on exit.

    (Parent G: per DeepSeek Q7 the PROVEN shipped pattern is a manual loop --
    dispatch_events / frame / flip, vsync-paced -- not pyglet's scheduler; the
    frozen intent (60 fps frames, clean stop) is honored exactly. Exits on
    snap["quit"] OR the window's X button; either way the finally block stops
    the audio FIRST, then closes the window [Q8].)
    """
    objs = None
    try:
        objs = build()
        window = objs["window"]
        last = time.perf_counter()
        while not window.has_exit and not objs["quit_requested"]:
            window.dispatch_events()          # fires input_map's handlers
            now = time.perf_counter()
            dt = min(now - last, MAX_DT)      # stall-proof
            last = now
            frame(objs, dt)
            window.flip()
    finally:
        if objs is not None:
            objs["engine"].stop()             # audio first, always [Q8]
            objs["window"].close()
            print("[LOOM2] clean shutdown. The land is quiet. 🧿")


if __name__ == "__main__":
    main()
