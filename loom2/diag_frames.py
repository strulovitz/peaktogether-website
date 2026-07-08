"""
LOOM2 -- diag_frames.py  (DeepSeek diagnostic, 2026-07-08)
Fable's ROUND 2, Experiments C + D in one tool. Runs the FULL game with the
exact per-frame logic of main.frame(), but times EVERY stage and prints
avg/MAX per stage once per second, plus fps and the live underrun count.

RUN (from the loom2 folder):
    python -u diag_frames.py                 # Exp C: vsync ON, no sleep
    python -u diag_frames.py novsync         # vsync OFF
    python -u diag_frames.py novsync sleep3  # Exp D: vsync OFF + 3 ms yield/frame
    python -u diag_frames.py sleep3          # (any combination)

Watch the MAX column: a stage that occasionally spikes to tens of ms is the
villain. Also watch underruns= and listen for the screech.
Close the window (or press Esc) to quit.
"""
import sys
import time

import pyglet

import config
import main as loom
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

_args = [a.lower() for a in sys.argv[1:]]
VSYNC = not any(a in ("novsync", "off", "0") for a in _args)
SLEEP = 0.0
for a in _args:
    if a.startswith("sleep"):
        try:
            SLEEP = float(a[5:]) / 1000.0     # milliseconds -> seconds
        except ValueError:
            pass
print(f"[diag_frames] vsync={VSYNC}  sleep={SLEEP*1000:.1f}ms/frame")

_STAGES = ("dispatch", "input", "update", "snapshot", "terrain", "totem",
           "blade", "helix", "composite", "hud", "flip")


def build(vsync):
    first_id = scene.campaign_order()[0]
    spec0 = scene.load_scene(first_id)
    surface_fn = surfaces.get(spec0.surface_name)
    print("[diag_frames] loading the orchestra ...")
    library = SampleLibrary()
    window = pyglet.window.Window(
        width=config.WINDOW_W, height=config.WINDOW_H,
        caption=loom.WINDOW_CAPTION, resizable=False, vsync=vsync)
    renderer = Renderer(window)
    engine = AudioEngine(library)
    engine.start()
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
        "window": window, "renderer": renderer, "engine": engine,
        "camera": camera, "hud": hud, "state": state, "input": input_map,
        "terrain": terrain, "totem_visual": totem_visual,
        "helix_panel": helix_panel, "blade": blade,
        "surface_fn": surface_fn, "quit_requested": False,
    }


def run():
    objs = None
    try:
        objs = build(VSYNC)
        window = objs["window"]
        engine = objs["engine"]
        state = objs["state"]
        renderer = objs["renderer"]
        camera = objs["camera"]

        sums = {k: 0.0 for k in _STAGES}
        maxs = {k: 0.0 for k in _STAGES}
        nframes = 0
        last = time.perf_counter()
        report_t = last + 1.0
        pc = time.perf_counter

        while not window.has_exit and not objs["quit_requested"]:
            def timed(key, fn):
                t = pc()
                fn()
                dt_ms = (pc() - t) * 1000.0
                sums[key] += dt_ms
                if dt_ms > maxs[key]:
                    maxs[key] = dt_ms

            timed("dispatch", window.dispatch_events)

            now = pc()
            dt = min(now - last, loom.MAX_DT)
            last = now

            def _input():
                for action, value in objs["input"].poll():
                    state.handle_action(action, value)
            timed("input", _input)
            timed("update", lambda: state.update(dt))

            box = {}

            def _snap():
                box["snap"] = state.snapshot()
                box["phase"] = engine.get_measure_phase()
            timed("snapshot", _snap)
            snap = box["snap"]
            phase = box["phase"]
            objs["quit_requested"] = snap["quit"]
            if snap["scene_changed"]:
                loom._apply_scene(objs, snap["scene"])

            blade = objs["blade"]
            blade.update_plane(snap["slice_plane"])
            blade.set_walk_stop(snap["walk_stop"])

            terrain = objs["terrain"]
            vp_left = camera.view_proj_terrain()
            renderer.begin_panel('left')
            timed("terrain", lambda: terrain.draw(vp_left))
            timed("totem", lambda: objs["totem_visual"].draw(
                vp_left, snap["totem"], terrain.height_at, phase))

            def _blade():
                if snap["slice_plane"].visible:
                    blade.draw(vp_left, objs["surface_fn"])
            timed("blade", _blade)
            renderer.end_panel()

            renderer.begin_panel('right')
            timed("helix", lambda: objs["helix_panel"].draw(
                camera.view_proj_helix(), snap["voices"],
                engine.get_active_flashes(), phase))
            renderer.end_panel()

            timed("composite", renderer.composite)
            timed("hud", lambda: objs["hud"].draw(
                snap["mode"], state.quiz_ui_state()))
            timed("flip", window.flip)

            if SLEEP > 0.0:
                time.sleep(SLEEP)

            nframes += 1
            if pc() >= report_t:
                st = engine.get_status()
                n = max(1, nframes)
                parts = " | ".join(
                    f"{k}={sums[k]/n:.1f}/{maxs[k]:.1f}" for k in _STAGES)
                print(f"fps={nframes}  underruns={st['underruns']}  {parts}",
                      flush=True)
                sums = {k: 0.0 for k in _STAGES}
                maxs = {k: 0.0 for k in _STAGES}
                nframes = 0
                report_t = pc() + 1.0
    finally:
        if objs is not None:
            objs["engine"].stop()
            objs["window"].close()
            print("[diag_frames] clean shutdown.")


if __name__ == "__main__":
    run()
