"""
LOOM2 -- diag_game.py  (DeepSeek diagnostic, 2026-07-08)
Runs the FULL game (graphics + audio, exactly like main.py) but:
  * lets you toggle vsync              -> Fable's Experiment A
  * prints engine.get_status() every ~1 s (underruns!) -> Fable's Experiment B
It reuses main.frame() so the frame logic is identical to the real game;
only the window's vsync flag and a per-second status print are added.

RUN (from the loom2 folder):
    python -u diag_game.py           # vsync ON  (default, like the real game)
    python -u diag_game.py novsync   # vsync OFF (Experiment A)

Listen for the screech AND watch the 'underruns=' number each second.
Close the window (or press Esc) to quit.
"""
import sys
import time

import pyglet

import config
import main as loom                      # reuse the REAL frame() logic
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

VSYNC = not (len(sys.argv) > 1 and sys.argv[1].lower() in ("novsync", "off", "0"))
print(f"[diag_game] vsync = {VSYNC}   (pass 'novsync' to turn it off)")


def build(vsync: bool) -> dict:
    first_id = scene.campaign_order()[0]
    spec0 = scene.load_scene(first_id)
    surface_fn = surfaces.get(spec0.surface_name)
    window = pyglet.window.Window(
        width=config.WINDOW_W, height=config.WINDOW_H,
        caption=loom.WINDOW_CAPTION, resizable=False, vsync=vsync)
    renderer = Renderer(window)
    library = SampleLibrary()
    engine = AudioEngine(library)
    engine.start()
    print("[diag_game] audio up:", engine.get_status())
    camera = OrbitCamera(spec0.camera_limits)
    hud = Hud(window, renderer)
    state = GameState(engine, camera, first_id)
    input_map = InputMap(window, hud)
    input_map.attach_joystick()
    input_map.attach_xbox()
    terrain = TerrainMesh(renderer, surface_fn, spec0.domain, spec0.mesh_step)
    totem_visual = TotemVisual(renderer)
    helix_panel = HelixPanel(renderer)
    blade = GlassBlade(renderer)
    blade.set_domain(spec0.domain)
    return {
        "window": window, "renderer": renderer, "library": library,
        "engine": engine, "camera": camera, "hud": hud, "state": state,
        "input": input_map, "terrain": terrain, "totem_visual": totem_visual,
        "helix_panel": helix_panel, "blade": blade,
        "surface_fn": surface_fn, "quit_requested": False,
    }


def run() -> None:
    objs = None
    try:
        objs = build(VSYNC)
        window = objs["window"]
        engine = objs["engine"]
        last = time.perf_counter()
        next_report = last + 1.0
        while not window.has_exit and not objs["quit_requested"]:
            window.dispatch_events()
            now = time.perf_counter()
            dt = min(now - last, loom.MAX_DT)
            last = now
            loom.frame(objs, dt)
            window.flip()
            if now >= next_report:
                next_report = now + 1.0
                st = engine.get_status()
                print(f"[diag_game] underruns={st['underruns']}  "
                      f"live_voices={st['live_voices']}  "
                      f"quiz_playing={st['quiz_playing']}  error={st['error']!r}",
                      flush=True)
    finally:
        if objs is not None:
            objs["engine"].stop()
            objs["window"].close()
            print("[diag_game] clean shutdown.")


if __name__ == "__main__":
    run()
