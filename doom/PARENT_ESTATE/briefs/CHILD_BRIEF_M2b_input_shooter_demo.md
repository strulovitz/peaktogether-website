Onward to M2b — the piece that makes it feel like a game: keyboard/mouse input → aim → raycast → and the panels you shoot now stay colored across sessions (real save/load via the WallStateManager we just built). This child delivers control/input.py + player/shooter.py + a real m2_demo.py.

I made the interactive conventions binding (mouse-look formulas borrowed from Ursina's known-good controller, edge-triggered shooting, decoupled dispatch handlers) and — importantly — pulled the testable logic into pure helpers so this child still ships meaningful headless tests despite being the most "live" module yet.

Copy everything between the markers into a fresh Opus chat. 🙂
=== BEGIN M2b CHILD PROMPT (control/input + player/shooter + m2_demo) ===
ROLE

You are an implementation child for the Principia Descent educational FPS engine (Python 3.11, Windows, Ursina/Panda3D). You implement two runtime modules + one demo, to their frozen contracts. You do not touch other modules and you do not change any frozen signature. Your memory is expendable — ask "Nir" for any file I didn't include before writing code.

Architecture rule: modules talk only through typed signatures and the pydantic contracts in principia/schema.py. Never import another module's internals.
YOUR TASK

Wire up the shoot-to-reveal loop with real input + a real shooter, persisting colored panels to disk. Produce:

    principia/control/input.py — InputManager (keyboard + mouse only; gamepad is M6).
    principia/player/shooter.py — Shooter (applies mouse-look to the camera, fires a raycast on shoot, dispatches the hit to registered handlers).
    m2_demo.py — standalone runnable: load fixture → build lemma1 room → register panels with WallStateManager → walk/look/shoot to colorize → progress %, with colors persisting across runs.

InputManager and Shooter may import ursina. Keep all non-Ursina logic in small pure helpers so it can be unit-tested headless.
FROZEN CONTRACTS

# control/input.py
class InputManager:
    def poll(self) -> None: ...                      # call ONCE per frame, BEFORE mover/shooter
    def move_axis(self) -> tuple[float, float]: ...   # (strafe, forward), each in [-1, 1]   (MOVER)
    def body_yaw_delta(self) -> float: ...            # M6 — return 0.0 for now
    def aim_delta(self) -> tuple[float, float]: ...   # (yaw_delta, pitch_delta) in degrees   (SHOOTER)
    def shoot_pressed(self) -> bool: ...              # edge-triggered (True only on the press frame)
    def toggle_map_pressed(self) -> bool: ...         # edge-triggered
    def read_mode_pressed(self) -> bool: ...          # edge-triggered
    def pause_pressed(self) -> bool: ...              # edge-triggered

# player/shooter.py
class Shooter:
    def __init__(self, camera, input_mgr: "InputManager") -> None: ...
    def update(self, dt: float) -> None: ...
    def register_hit_handlers(self, on_wall, on_demon, on_secret) -> None: ...

BINDING DECISIONS (do not deviate)
InputManager (keyboard + mouse)

    __init__ initializes previous-state flags to False. It must NOT touch any Ursina global (so it can be constructed in a headless test). Reading devices happens only in poll().
    Key/button map (M2b): move = W/A/S/D; shoot = left mouse button (mouse.left); pause = escape; map = m; read = r.
    poll() reads current device state and computes edges for shoot/pause/map/read using a module-level pure helper:

    def edge(prev: bool, cur: bool) -> bool:
        return bool(cur) and not bool(prev)

    Store
    cur as the new prev each poll. The *_pressed() methods just return the edge flags computed in the last poll().
    move_axis(): strafe = held_keys['d'] - held_keys['a'], forward = held_keys['w'] - held_keys['s']; return (strafe, forward).
    aim_delta(): use a pure helper scale_aim(vx, vy, sens) -> tuple[float,float]: return (vx*sens, vy*sens) applied to mouse.velocity[0], mouse.velocity[1] with sens = config.MOUSE_SENSITIVITY. Return (yaw_delta, pitch_delta).
    body_yaw_delta() returns 0.0 (M6).

Shooter

    __init__(camera, input_mgr): store both; set on_wall/on_demon/on_secret = None; init self._pitch = 0.0.
    register_hit_handlers(on_wall, on_demon, on_secret): store the three callbacks (any may be None). Signatures the demo/runtime will pass:
        on_wall(block_id: str)
        on_demon(entity, point)
        on_secret(door_id: str)
    update(dt) (assumes input_mgr.poll() was already called this frame — do not call poll yourself):
        Look: yaw, pitch = input_mgr.aim_delta(). Apply with the Ursina-proven mapping:

        self.camera.rotation_y += yaw
        self._pitch = clamp_pitch(self._pitch - pitch, config.PITCH_CLAMP_DEG)
        self.camera.rotation_x = self._pitch

        where
        clamp_pitch(p, limit) is a pure helper returning max(-limit, min(limit, p)).
        Shoot: if input_mgr.shoot_pressed(), do hit = raycast(self.camera.world_position, self.camera.forward, distance=config.SHOOT_RANGE, ignore=()); if hit.hit, call self._dispatch_hit(hit.entity, hit.point).
    _dispatch_hit(self, entity, point) — pure dispatch, no Ursina calls (testable with fakes):
        kind = getattr(entity, "kind", None)
        "panel" → if self.on_wall: self.on_wall(entity.block_id)
        "demon" → if self.on_demon: self.on_demon(entity, point)
        "secret" → if self.on_secret: self.on_secret(entity.door_id)
        anything else / handler None → do nothing (never crash).

m2_demo.py (standalone; throwaway glue allowed; not imported by anything)

    Imports: from principia.content.loader import load_level; from principia.assets.manager import AssetManager; from principia.world.builder import build_room; from principia.walls.state import WallStateManager; from principia.control.input import InputManager; from principia.player.shooter import Shooter; and principia.config.
    Build: level = load_level("content_packs/principia", "fixture"); find the lemma1 RoomCell in level.floorplan.rooms (it's a list, match by id); assets = AssetManager("content_packs/principia"); cell = build_room(room, level.rooms["lemma1"], assets).
    Wall state + persistence:
        wall_state = WallStateManager(assets)
        For each block_id, panel in cell.panels.items(): wall_state.register("lemma1", block_id, panel, panel.off_tex, panel.on_tex).
        wall_state.load(config.SAVE_FILE) after registering, so previously-colored panels come back colored. (Demonstrates persistence: shoot some, quit, relaunch → still colored.)
    Input + shooter:
        inp = InputManager(); shooter = Shooter(camera, inp).
        Define reveal(block_id): if not wall_state.state(block_id): wall_state.toggle(block_id); wall_state.save(config.SAVE_FILE). (Sticky on; persist on each reveal.)
        shooter.register_hit_handlers(on_wall=reveal, on_demon=None, on_secret=None).
    Camera/movement (manual — do not use FirstPersonController here, because Shooter owns the camera rotation):
        mouse.locked = True; add a small red crosshair on camera.ui.
        Start: camera.position = (6, config.EYE_HEIGHT, 2), camera.rotation = (0,0,0) (faces +Z toward the north wall's panels).
        In update() each frame: inp.poll(); if inp.pause_pressed(): application.quit(); shooter.update(time.dt); then a tiny inline mover:
            strafe, forward = inp.move_axis()
            flatten the camera basis to the XZ plane: take camera.forward and camera.right, zero their y, normalize; move = (right_flat*strafe + forward_flat*forward) * config.WALK_SPEED * time.dt
            new position = camera.position + move, clamp x,z to the room interior [0.6, 11.4]×[0.6, 11.4] (room rect is x0 z0 w12 d12), force y = config.EYE_HEIGHT.
        Show a HUD Text updated each frame: f"Read: {wall_state.progress('lemma1')*100:.0f}%   WASD move | mouse look | click = reveal | ESC quit".

TESTS YOU MUST WRITE (headless)

tests/test_input.py:

    edge(False, True) is True; edge(True, True) is False; edge(True, False) is False; edge(False, False) is False.
    scale_aim(0.1, -0.2, 40) == (4.0, -8.0).
    InputManager() constructs without Ursina, and before any poll() all of shoot_pressed(), pause_pressed(), toggle_map_pressed(), read_mode_pressed() return False, and body_yaw_delta() == 0.0. (Do not call poll() in tests — it reads live devices.)

tests/test_shooter.py (use fakes; no Ursina needed for these):

class FakeCam: pass
class FakeInput: pass
class FakePanel:  kind="panel";  block_id="b1"
class FakeDemon:  kind="demon"
class FakeSecret: kind="secret"; door_id="d1"

    clamp_pitch(100, 70) == 70; clamp_pitch(-100, 70) == -70; clamp_pitch(30, 70) == 30.
    Construct Shooter(FakeCam(), FakeInput()); register recording handlers; assert _dispatch_hit(FakePanel(), (0,0,0)) calls on_wall("b1"); FakeDemon() calls on_demon(entity, point); FakeSecret() calls on_secret("d1").
    An entity with kind=None (or no kind) → no handler called, no exception. With handlers left as None → _dispatch_hit must not crash.

OUTPUT FORMAT

First confirm in one line that you have everything (or ask for a missing file). Then output four separate copy-paste code blocks, each preceded by its bold file path: principia/control/input.py, principia/player/shooter.py, tests/test_input.py, tests/test_shooter.py, then m2_demo.py. End with one line for DeepSeek: the exact pytest command and how to run the demo.
REFERENCE FILES (already in the repo — do not rewrite)

principia/config.py (relevant constants):

EYE_HEIGHT: float = 1.6
WALK_SPEED: float = 4.0
PITCH_CLAMP_DEG: float = 70.0
MOUSE_SENSITIVITY: float = 40.0
SHOOT_RANGE: float = 25.0
CEILING_H: float = 3.0
SAVE_FILE: str = "savegame.json"

WallStateManager public interface (already implemented; just call it — note room_id in register):

class WallStateManager:
    def __init__(self, assets) -> None: ...
    def register(self, room_id: str, block_id: str, entity, off_tex, on_tex) -> None: ...
    def toggle(self, block_id: str) -> bool: ...
    def state(self, block_id: str) -> bool: ...
    def progress(self, room_id: str) -> float: ...
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...

world/builder.py outputs (already implemented): build_room(room, content, assets) -> CellEntities, where cell.panels is dict[block_id -> panel_entity], and each panel entity carries panel.kind == "panel", panel.block_id, panel.off_tex, panel.on_tex, panel.is_on, and has a box collider (so raycasts hit it).

content/loader.py: load_level(pack_dir, level_id) -> Level; level.floorplan.rooms is a list[RoomCell] (match lemma1 by .id); level.rooms is dict[room_id -> RoomContent].

Current stubs to replace:

# principia/control/input.py
from __future__ import annotations
class InputManager:
    def poll(self) -> None: raise NotImplementedError("M2")
    def move_axis(self) -> tuple[float, float]: raise NotImplementedError("M2")
    def body_yaw_delta(self) -> float: raise NotImplementedError("M6")
    def aim_delta(self) -> tuple[float, float]: raise NotImplementedError("M2")
    def shoot_pressed(self) -> bool: raise NotImplementedError("M2")
    def toggle_map_pressed(self) -> bool: raise NotImplementedError("M4")
    def read_mode_pressed(self) -> bool: raise NotImplementedError("M3")
    def pause_pressed(self) -> bool: raise NotImplementedError("M2")

# principia/player/shooter.py
from __future__ import annotations
from principia.control.input import InputManager
class Shooter:
    def __init__(self, camera, input_mgr: InputManager) -> None: raise NotImplementedError("M2")
    def update(self, dt: float) -> None: raise NotImplementedError("M2")
    def register_hit_handlers(self, on_wall, on_demon, on_secret) -> None: raise NotImplementedError("M2")

Ursina primitives you'll use: from ursina import Ursina, Entity, camera, color, mouse, held_keys, raycast, application, time, Text. (mouse.left = left button held; mouse.velocity[0/1] = per-frame look delta; held_keys['w'] etc. = 0/1; time.dt = frame time; entity.forward / entity.right are world-space basis vectors.)
=== END M2b CHILD PROMPT ===

Notes for you, Nir:

    After this lands, python m2_demo.py is the first build that's genuinely playable: walk with WASD, look with the mouse, click to colorize a proof step, watch the Read % climb — then quit and relaunch and your progress is still there. That persistence is the WallStateManager save-merge from M2a doing its job. 🎨
    I deliberately kept Shooter ignorant of WallStateManager — it only fires on_wall(block_id) callbacks. That decoupling is what lets M3 reuse the same shooter to also kill demons (on_demon) and M5 to open secret doors (on_secret) with zero changes to the shooter.

When DeepSeek reports green + a working demo, the headline milestone is M3 — the demon (sphere-circle creature + disintegration), the CeilingManager (blood-red equation reveal + spray), and ui/readmode.py (the crisp full-screen panel overlay from risk R3). That's the most fun milestone. Want me to draft M3 next, or pause so you can play M2b first? 🙂
