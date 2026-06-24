The fun one! 🎉 M3 is where it goes from "interactive gallery" to "game": you'll shoot a little sphere-demon, it disintegrates, and the room's equation blooms onto the ceiling in blood-red while glyphs spray out and fade. 😈🩸

Following our split pattern, I'm doing M3 in two children:

    M3a (this child): enemy/demon.py + ceiling/equations.py + m3_demo.py — the kill→reveal flourish (these two are tightly coupled by the death→reveal trigger).
    M3b (next): ui/readmode.py — the crisp full-screen panel overlay (risk R3), which is genuinely independent.

I kept module boundaries clean: M3a does not touch assets/manager.py (the demo makes its own placeholder equation texture with Pillow, so we don't have to implement equation_texture yet), and I pulled the demon's health/death logic into a pure _Health helper so the core "fires-once" behavior is CI-testable without a display.

Copy everything between the markers into a fresh Opus chat. 🙂
=== BEGIN M3a CHILD PROMPT (demon + ceiling + m3_demo) ===
ROLE

You are an implementation child for the Principia Descent educational FPS engine (Python 3.11, Windows, Ursina/Panda3D). You implement two runtime modules + one demo, to their frozen contracts. You do not touch other modules and you do not change any frozen signature (except the one explicit additive extension noted below). Your memory is expendable — ask "Nir" for any file I didn't include before writing code.

Architecture rule: modules talk only through typed signatures and the pydantic contracts in principia/schema.py. Never import another module's internals.
YOUR TASK

Build the demon and the ceiling-equation reveal, then wire the full shoot-the-demon → disintegrate → reveal blood-red equation + spray loop in a demo. Produce:

    principia/enemy/demon.py — Demon (sphere-circle creature; idle bob; takes hits; disintegrates on death; fires a one-shot death callback).
    principia/ceiling/equations.py — CeilingManager (register hidden equation bands; reveal them blood-red; cosmetic equation spray).
    m3_demo.py — standalone runnable extending the M2 demo: shoot panels to colorize and shoot the demon to exorcise the room (ceiling equation appears + sprays).

Demon and CeilingManager may import ursina. Keep all non-Ursina logic in small pure helpers so it can be unit-tested headless.
FROZEN CONTRACTS

# enemy/demon.py
class Demon:
    def __init__(self, spec: DemonSpec, position: Vec3, parent=None) -> None: ...  # parent: optional, additive
    def update(self, dt: float) -> None: ...
    def hit(self, point) -> None: ...          # may kill; ignored if already dead
    def is_dead(self) -> bool: ...
    def on_death(self, callback) -> None: ...  # store a single callback; fires exactly once on death

# ceiling/equations.py
class CeilingManager:
    def __init__(self, assets) -> None: ...                                   # 'assets' reserved/unused in M3
    def register_band(self, room_id: str, band: CeilingBand, entity) -> None: ...
    def reveal(self, room_id: str) -> None: ...                               # idempotent blood-red fade-in
    def spray_from(self, origin, glyph_texes: list) -> None: ...              # cosmetic; no-op if list empty

BINDING DECISIONS (do not deviate)
enemy/demon.py

    Pure health helper (module-level, fully testable, no Ursina):

    class _Health:
        def __init__(self, hp: int) -> None:
            self.hp = hp; self.dead = False
        def hit(self) -> bool:        # returns True ONLY on the lethal hit
            if self.dead: return False
            self.hp -= 1
            if self.hp <= 0:
                self.dead = True
                return True
            return False

    Pure position helper (module-level, testable):

    def add_offset(anchor, offset) -> tuple[float, float, float]:
        return (anchor[0]+offset[0], anchor[1]+offset[1], anchor[2]+offset[2])

    __init__(spec, position, parent=None):
        Create a root Entity at position (parent it to parent if given, so M4 can unload it with the cell).
        self._health = _Health(spec.hp); self._death_cb = None; self._t = 0.0; self._base_y = position[1].
        For each DemonCircle in spec.circles: create Entity(model='sphere', parent=root, position=offset, scale=radius*2, color=color.rgb(*hex_to_rgb(circle.color)), collider='sphere'). Tag each circle entity: c.kind = "demon" and c.demon = self (back-reference, so a generic shooter handler can do entity.demon.hit(point)). Provide a small hex_to_rgb("#RRGGBB") -> (r,g,b) (0–255) helper.
        Keep a list of the circle entities for disintegration.
    update(dt): gentle idle bob — self._t += dt; root.y = self._base_y + sin(self._t*2.0)*0.1. No-op if dead.
    hit(point): if is_dead(), return. Call self._health.hit(); if it returns True (lethal), call self._die().
    is_dead(): return self._health.dead.
    on_death(callback): store it (single callback).
    _die(): disintegrate — for each circle entity pick a random outward direction, c.animate_position(c.world_position + dir*3, duration=0.6), c.animate_scale(0, duration=0.6), destroy(c, delay=0.7). Then, once, if self._death_cb: call it. (The _Health.dead flag guarantees this can't fire twice even if hit is called again mid-animation.)

ceiling/equations.py

    This module's core (register/reveal) must work on plain entity-like objects (so it's testable with fakes). It sets entity.enabled, entity.color, and calls entity.fade_in(...) if that method exists.
    __init__(assets): store assets (unused in M3). Init self._bands: dict[str, list[tuple]], self._revealed: set[str], and self._red = color.rgb(178, 0, 0) (blood-red; importing ursina.color at module top is fine in CI).
    register_band(room_id, band, entity): append (band, entity) to self._bands[room_id]. If band.hidden_until_demon_dead is truthy, set entity.enabled = False, else entity.enabled = True. Set entity.color = self._red.
    reveal(room_id): idempotent — if room_id in self._revealed, return immediately. Mark revealed. For each registered band entity in that room: entity.enabled = True; entity.color = self._red; if hasattr(entity, "fade_in"), call entity.fade_in(duration=0.8).
    spray_from(origin, glyph_texes): if the list is empty, do nothing. Otherwise for each texture, create a billboarded quad at origin (Entity(model='quad', texture=tex, position=origin, scale=0.6, double_sided=True, billboard=True)), animate it outward in a random direction (~2.5 units, 0.8s), fade it out, and destroy(..., delay=0.9). (This is the celebratory "demonic algebra" spray; it is NOT traced to any final position.)

m3_demo.py (standalone; throwaway glue allowed; not imported by anything)

Extend the M2 demo pattern (manual camera + inline mover + input.poll() then shooter.update() each frame). You may read m2_demo.py for the exact camera/mover/input glue and reuse it. Then add:

    After building the lemma1 room and registering panels with WallStateManager (as in m2), also:
        Demon: spec = level.rooms["lemma1"].demon; demon = Demon(spec, tuple(spec.position)).
        Ceiling band: make a placeholder equation texture inline with Pillow (white "q = m v" on transparent → Texture(img)), create a ceiling quad for cb_l1_1 at (6, config.CEILING_H - 0.05, 10) with rotation=(90,0,0), double_sided=True, scale=3; create CeilingManager(assets); ceiling.register_band("lemma1", band, band_entity) (it starts hidden because hidden_until_demon_dead is True).
        Death wiring: demon.on_death(lambda: (ceiling.reveal("lemma1"), ceiling.spray_from(tuple(spec.position), [equation_tex]))).
        Shooter handlers: shooter.register_hit_handlers(on_wall=reveal_panel, on_demon=(lambda e, p: e.demon.hit(p)), on_secret=None) — note on_demon uses the entity.demon back-reference, so it works for any demon.
        In update(), also call demon.update(time.dt).
        HUD line: f"Read: {wall_state.progress('lemma1')*100:.0f}%  |  shoot the demon to reveal the equation  |  ESC quit".

TESTS YOU MUST WRITE (mostly headless)

tests/test_demon.py:

    Pure _Health (no Ursina): h = _Health(3); h.hit() False, False, then True on the 3rd; a 4th h.hit() returns False and h.dead stays True. _Health(1).hit() returns True immediately.
    add_offset((6,1.2,6), (-0.2,0.25,0.55)) == (5.8, 1.45, 6.55) (use pytest.approx).
    hex_to_rgb("#FF7AB6") == (255, 122, 182).
    Guarded live test (skip if no display): wrap in try/except + pytest.skip; load fixture, build a Demon from the lemma1 spec, register a recording death callback via on_death, call hit(None) hp times, assert is_dead() is True and the callback fired exactly once; call hit(None) again and assert it still fired only once.

tests/test_ceiling.py (headless with fakes):

class FakeBandEntity:
    def __init__(self): self.enabled = True; self.color = None; self.faded = False
    def fade_in(self, duration=1): self.faded = True

class FakeBand:  # stands in for schema.CeilingBand
    def __init__(self, hidden=True): self.hidden_until_demon_dead = hidden

    After register_band("r1", FakeBand(hidden=True), e), e.enabled is False and e.color is not None.
    After register_band("r1", FakeBand(hidden=False), e2), e2.enabled is True.
    reveal("r1") sets every registered entity enabled True, faded True. Reset a fake's faded=False, call reveal("r1") again, assert it stays False (idempotent — does not re-fire).
    spray_from((0,0,0), []) returns without error (no-op on empty list).

OUTPUT FORMAT

First confirm in one line that you have everything (or ask for a missing file). Then output five separate copy-paste code blocks, each preceded by its bold file path: principia/enemy/demon.py, principia/ceiling/equations.py, tests/test_demon.py, tests/test_ceiling.py, then m3_demo.py. End with one line for DeepSeek: the exact pytest command and how to run the demo.
REFERENCE FILES (already in the repo — do not rewrite)

principia/config.py (relevant constants):

CEILING_H: float = 3.0
EYE_HEIGHT: float = 1.6
WALK_SPEED: float = 4.0
SHOOT_RANGE: float = 25.0
SAVE_FILE: str = "savegame.json"
BLOOD_RED = (0.7, 0.0, 0.0)   # reference; in code use color.rgb(178, 0, 0)

principia/schema.py (types you need):

Vec3 = tuple[float, float, float]

class DemonCircle(_Base):
    offset: Vec3; radius: float; color: str; role: str = "body"

class DemonSpec(_Base):
    demon_id: str; position: Vec3; hp: int = 3
    circles: list[DemonCircle] = []
    spray_glyphs: list[str] = []

class CeilingBand(_Base):
    band_id: str; above_wall: str
    equation_png: str; hidden_until_demon_dead: bool = True

Fixture demon (in content_packs/principia/rooms/lemma1.json):

"demon": { "demon_id":"demon_lemma1", "position":[6,1.2,6], "hp":3, "circles":[
  {"offset":[0,0,0],"radius":0.6,"color":"#FF7AB6","role":"body"},
  {"offset":[-0.2,0.25,0.55],"radius":0.1,"color":"#3B6BFF","role":"eye"},
  {"offset":[0.2,0.25,0.55],"radius":0.1,"color":"#3B6BFF","role":"eye"},
  {"offset":[0,-0.1,0.6],"radius":0.06,"color":"#FFFFFF","role":"tooth"} ],
  "spray_glyphs":["png/eq_l1_1.png"] }

Interfaces you'll call in the demo (already implemented):

# content/loader.py
load_level(pack_dir, level_id) -> Level      # level.floorplan.rooms: list[RoomCell] (match lemma1 by .id)
                                             # level.rooms: dict[room_id -> RoomContent] (has .demon)
# assets/manager.py
AssetManager(pack_dir)                        # pass to CeilingManager; equation_texture() is still stubbed — don't use it
# world/builder.py
build_room(room, content, assets) -> CellEntities   # cell.panels: dict[block_id -> panel entity]
# walls/state.py
WallStateManager(assets); .register(room_id, block_id, entity, off_tex, on_tex); .toggle; .state; .progress; .save; .load
# control/input.py
InputManager(); .poll(); .move_axis(); .aim_delta(); .shoot_pressed(); .pause_pressed()
# player/shooter.py
Shooter(camera, input_mgr); .update(dt); .register_hit_handlers(on_wall, on_demon, on_secret)
#   on_demon is called as on_demon(entity, point)

Current stubs to replace:

# principia/enemy/demon.py
from __future__ import annotations
from principia.schema import DemonSpec, Vec3
class Demon:
    def __init__(self, spec: DemonSpec, position: Vec3) -> None: raise NotImplementedError("M3")
    def update(self, dt: float) -> None: raise NotImplementedError("M3")
    def hit(self, point: Vec3) -> None: raise NotImplementedError("M3")
    def is_dead(self) -> bool: raise NotImplementedError("M3")
    def on_death(self, callback) -> None: raise NotImplementedError("M3")

# principia/ceiling/equations.py
from __future__ import annotations
from principia.schema import CeilingBand, Vec3
from principia.assets.manager import AssetManager
class CeilingManager:
    def __init__(self, assets: AssetManager) -> None: raise NotImplementedError("M3")
    def register_band(self, room_id: str, band: CeilingBand, entity) -> None: raise NotImplementedError("M3")
    def reveal(self, room_id: str) -> None: raise NotImplementedError("M3")
    def spray_from(self, origin: Vec3, glyph_texes: list) -> None: raise NotImplementedError("M3")

Ursina primitives: from ursina import Entity, color, destroy, Vec3, Texture, camera, mouse, held_keys, raycast, application, time, Text; from math import sin; import random; from PIL import Image, ImageDraw (for the demo's placeholder equation). Entity helpers: animate_position, animate_scale, fade_in, fade_out, billboard=True, destroy(entity, delay=...).
=== END M3a CHILD PROMPT ===

Notes for you, Nir:

    After this lands, python m3_demo.py is the first build with the whole emotional arc of a room: read the proof (colorize panels), then exorcise the demon and watch the equation power surge onto the ceiling in blood-red. That on-death callback wiring is the same pattern M5's boss will use. 😈→🩸
    The entity.demon back-reference is a small but important decision: it means the Shooter's on_demon handler is totally generic (entity.demon.hit(point)), so when M4 puts many rooms with many demons in play, nothing about the shooter has to change.

When DeepSeek reports green, M3b is the quick, satisfying ui/readmode.py — walk up to a panel (or press R) and a pin-sharp full-screen image of that proof step pops up (no 3D blur), zoomable, press R/Esc to dismiss. That's the legibility guarantee from risk R3. Want me to draft M3b next, or pause to play M3a first? 🙂
