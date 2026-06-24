Onward to M3b — the small-but-crucial legibility guarantee from risk R3. No matter how blurry a panel looks on an angled 3D wall, the player can press R (or shoot/approach) and get a pin-sharp, full-screen, flat UI image of that proof step — because UI-space rendering bypasses all the perspective/mipmap softening. This is what makes Newton's dense diagrams actually readable. 📖✨

This is a clean single-module child. I structured ReadMode so its entire open/close state machine is testable headless (entity creation is isolated behind two tiny private methods you can monkeypatch), and bundled a full m3b_demo.py that's now the most complete playable build: room + panels + demon + ceiling reveal + read mode.

Copy everything between the markers into a fresh Opus chat. 🙂
=== BEGIN M3b CHILD PROMPT (ui/readmode.py) ===
ROLE

You are an implementation child for the Principia Descent educational FPS engine (Python 3.11, Windows, Ursina/Panda3D). You implement one runtime module + one demo, to its frozen contract. You do not touch other modules and you do not change any frozen signature. Your memory is expendable — ask "Nir" for any file I didn't include before writing code.

Architecture rule: modules talk only through typed signatures and the pydantic contracts in principia/schema.py. Never import another module's internals.
YOUR TASK

Implement principia/ui/readmode.py: a full-screen 2D overlay that shows a panel's texture flat in UI space (no perspective, no mipmap blur) so the player can read a proof step crisply, with scroll-to-zoom and a dismiss hint. Then wire it into a demo. Produce:

    principia/ui/readmode.py
    tests/test_readmode.py
    m3b_demo.py — standalone runnable: the full M3 build plus read mode (press R while looking at a panel to read it full-screen; R/Esc to dismiss).

ReadMode may import ursina, but __init__ must not create any entities (so it can be constructed headless), and all entity creation/teardown must live in two tiny private methods so the state machine is unit-testable.
FROZEN CONTRACT

class ReadMode:
    def open(self, block_id: str, texture) -> None: ...   # 'texture' is the panel's current Ursina Texture
    def close(self) -> None: ...
    def is_open(self) -> bool: ...

BINDING DECISIONS (do not deviate)

State + isolation (this is what makes it testable):

    __init__: set self._open = False, self._entities = [], self._block_id = None. No Ursina calls here.
    _build(self, texture) -> list: the ONLY method that creates Ursina entities. Returns the list of created UI entities.
    _destroy(self, entities) -> None: tears down a list of entities (calls ursina.destroy on each; robust to fakes/strings — wrap each in try/except so it never raises).
    open(block_id, texture): if already open, call self.close() first (replace). Then self._entities = self._build(texture); self._open = True; self._block_id = block_id.
    close(): if not open, return (safe no-op). self._destroy(self._entities); self._entities = []; self._open = False; self._block_id = None.
    is_open(): return self._open.

What _build(texture) creates (real overlay, parented to camera.ui):

    A dim backdrop covering the screen: Entity(parent=camera.ui, model='quad', scale=(2, 2), color=color.rgba(8, 8, 12, 235), z=1) (so the 3D world is dimmed/hidden behind it).
    The panel image, crisp and large, centered: use a small zoomable Entity subclass (see below), parent=camera.ui, model='quad', texture=texture, scale=(0.8, 0.8), position=(0,0,0), z=0.
    A hint Text(parent=camera.ui, text="[R] / Esc to close   ·   scroll to zoom", origin=(0,0), y=-0.46, scale=0.8, color=color.azure, z=-1).
    Return [backdrop, image, hint].

Scroll-to-zoom (bonus, self-contained): define a module-level class _ZoomImage(Entity) whose input(self, key) multiplies its own scale by 1.1 on 'scroll up' and 0.9 on 'scroll down', clamped to a sensible range (e.g. scale magnitude in [0.3, 2.5]). Use _ZoomImage for the panel image in _build. (Defining the class at import time needs no display; only instantiation does, inside _build.)
DEMO — m3b_demo.py (standalone; throwaway glue allowed; not imported by anything)

The most complete demo yet. Reuse the M3 demo pattern (manual camera, inline mover, input.poll() then update). You may read m3_demo.py for the camera/mover/shooter/demon/ceiling glue and extend it. Build: load fixture → build_room("lemma1") → register panels with WallStateManager (load config.SAVE_FILE) → build Demon → ceiling band (inline Pillow placeholder equation) + CeilingManager + death wiring (reveal + spray) → Shooter with on_wall=reveal_panel, on_demon=lambda e,p: e.demon.hit(p). Then add read mode:

    Create read_mode = ReadMode().
    In update() each frame, after input.poll():
        If read_mode.is_open(): the world is frozen for reading. If input.read_mode_pressed() or input.pause_pressed(), call read_mode.close(). Do not run the mover or shooter.update() this frame (so the camera doesn't drift while reading). return early.
        Else (normal play):
            If input.pause_pressed(): application.quit().
            If input.read_mode_pressed(): raycast from camera.world_position along camera.forward (distance=config.SHOOT_RANGE); if it hits an entity with kind == "panel", call read_mode.open(hit.entity.block_id, hit.entity.texture) (pass the panel's current texture — colored if already revealed, B&W otherwise).
            Otherwise run the usual shooter.update(time.dt), demon.update(time.dt), and the inline mover.
    HUD line: f"Read: {wall_state.progress('lemma1')*100:.0f}%  |  click=reveal  ·  shoot demon=exorcise  ·  R=read panel  ·  ESC quit".

TESTS YOU MUST WRITE — tests/test_readmode.py (fully headless via monkeypatch)

    ReadMode() constructs and is_open() is False.
    open/close state machine: monkeypatch the instance's _build to return ["bg","img","hint"] and _destroy to append to a destroyed list. open("l1_step1", "TEX") → is_open() True and _block_id == "l1_step1". close() → is_open() False, _block_id is None, and destroyed == ["bg","img","hint"].
    open-while-open replaces: monkeypatch _build to return ["a"] (then ["b"] doesn't matter), _destroy records. open("b1","T") then open("b2","T") → _block_id == "b2", is_open() True, and the first overlay ("a") is in destroyed (old torn down before new built).
    close is idempotent: ReadMode().close() then .close() again — no exception, is_open() stays False.

(No live/display test is required; the monkeypatch tests fully cover the state machine, and the demo provides visual verification.)
OUTPUT FORMAT

First confirm in one line that you have everything (or ask for a missing file). Then output three separate copy-paste code blocks, each preceded by its bold file path: principia/ui/readmode.py, tests/test_readmode.py, then m3b_demo.py. End with one line for DeepSeek: the exact pytest command and how to run the demo.
REFERENCE FILES (already in the repo — do not rewrite)

principia/config.py (relevant constants):

EYE_HEIGHT: float = 1.6
WALK_SPEED: float = 4.0
CEILING_H: float = 3.0
SHOOT_RANGE: float = 25.0
SAVE_FILE: str = "savegame.json"

Interfaces you'll call in the demo (already implemented):

# content/loader.py:   load_level(pack_dir, level_id) -> Level
#   level.floorplan.rooms : list[RoomCell] (match "lemma1" by .id)
#   level.rooms : dict[room_id -> RoomContent]  (.demon present)
# assets/manager.py:   AssetManager(pack_dir)
# world/builder.py:    build_room(room, content, assets) -> CellEntities
#   cell.panels : dict[block_id -> panel entity]; each panel has .kind=="panel", .block_id, .off_tex, .on_tex, .texture, box collider
# walls/state.py:      WallStateManager(assets); .register(room_id, block_id, entity, off_tex, on_tex); .toggle; .state; .progress; .save; .load
# control/input.py:    InputManager(); .poll(); .move_axis(); .aim_delta(); .shoot_pressed(); .read_mode_pressed(); .pause_pressed()
#   (read_mode_pressed and pause_pressed are edge-triggered: True only on the press frame)
# player/shooter.py:   Shooter(camera, input_mgr); .update(dt); .register_hit_handlers(on_wall, on_demon, on_secret)
# enemy/demon.py:      Demon(spec, position[, parent]); .update(dt); .hit(point); .is_dead(); .on_death(cb)
#   each demon circle entity carries .kind=="demon" and .demon (back-ref); use on_demon=lambda e,p: e.demon.hit(p)
# ceiling/equations.py: CeilingManager(assets); .register_band(room_id, band, entity); .reveal(room_id); .spray_from(origin, glyph_texes)

Current stub to replace — principia/ui/readmode.py:

from __future__ import annotations
class ReadMode:
    def open(self, block_id: str, texture) -> None: raise NotImplementedError("M3")
    def close(self) -> None: raise NotImplementedError("M3")
    def is_open(self) -> bool: raise NotImplementedError("M3")

Ursina primitives: from ursina import Ursina, Entity, camera, color, mouse, held_keys, raycast, application, time, Text, Texture, destroy, Vec3; from math import sin; import random; from PIL import Image, ImageDraw (demo placeholder equation). UI entities are parented to camera.ui; color.rgba(r, g, b, a) takes 0–255; an Entity subclass that defines input(self, key) receives input events including 'scroll up' / 'scroll down'.
=== END M3b CHILD PROMPT ===

Notes for you, Nir:

    After this lands, python m3b_demo.py is a genuinely complete single-room experience: read each proof step crisply (press R), colorize it, then exorcise the demon to unlock the equation overhead. That's the entire "one room" loop — which means the next milestone is about scale.
    The _build/_destroy isolation trick here is a reusable pattern: any future UI panel (the map, the HUD, a comprehension-prompt popup from risk R4) can use the same shape to stay headless-testable.

When DeepSeek reports green, the big one is M4 — multi-room: layout/graph.py (concept graph → floorplan via spring layout + room sizing + de-overlap + b-spline corridors), world/rooms.py (RoomManager load/unload so only the current cell exists), nav/navigator.py (door-crossing detection), and ui/mapmode.py (the 2D automap). That's the milestone that turns one room into a walkable dungeon of ideas. It's substantial, so I'll likely split it into 2–3 children. Want me to start drafting M4 next, or pause to play M3b first? 🙂
