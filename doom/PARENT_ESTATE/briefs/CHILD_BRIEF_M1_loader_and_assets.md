Perfect! 🎉 So glad the demo works and feels right!

Now, as the parent, my job is to write a tight, self-contained prompt that a fresh child chat can execute without seeing our whole conversation. M1's first two runtime modules are content/loader.py (turns the JSON pack into validated Level objects) and assets/manager.py (turns the manifest + PNGs — or auto-generated placeholders, since we have no baker yet — into engine textures).

I made a few binding decisions for the child so it doesn't have to guess: missing PNGs become labeled placeholder textures (so rooms render before any baking exists), AssetManager must not import the loader (it's earlier in the build order), and the image layer must be testable without Ursina (so CI stays green).

Copy everything between the two markers into a brand-new Opus chat. 🙂
=== BEGIN M1 CHILD PROMPT ===
ROLE

You are an implementation child for the Principia Descent educational FPS engine (Python 3.11, runs on Windows; built on Ursina/Panda3D). You implement exactly two runtime modules to their frozen contracts, plus their tests. You do not touch any other module, and you do not change any frozen signature. Your memory is expendable — if you need a file I didn't include, ask "Nir" for it before writing code.

The architecture rule that governs everything: modules communicate only through the typed signatures below and the pydantic data contracts in principia/schema.py. Never import another module's internals.
YOUR TASK (Milestone M1)

Implement these two files so a data-driven room can be loaded from the content pack and given textures, even though no real PNGs exist yet (the offline baker is a later milestone):

    principia/content/loader.py — load + validate a content pack into a Level.
    principia/assets/manager.py — read the manifest and provide wall textures (real PNG if present, otherwise an auto-generated placeholder).

Also produce: tests/test_loader.py and tests/test_assets.py.
BINDING DECISIONS (do not deviate)

    A pack directory holds ONE level. Its files are concept_graph.json, floorplan.json, manifest.json, and rooms/<room_id>.json (one per room). load_level(pack_dir, level_id) reads these and cross-checks that the files' level_id equals the requested level_id.
    Missing PNGs are NOT errors. When a PNG referenced by the manifest does not exist on disk, AssetManager generates a placeholder texture (grayscale for the off state, colored for the on state) labeled with the block id and state. This lets rooms render before anything is baked. (Use Pillow exactly as the existing m0_demo.py does — Texture(pil_image).)
    assets/manager.py must NOT import content/loader.py. It is earlier in the build order. It reads manifest.json itself with json + principia.schema.AssetEntry.
    The image layer must be testable without Ursina. Put the load-PNG-or-make-placeholder logic in a private helper that returns a PIL.Image.Image (no Ursina needed). The public wall_textures() is then a thin wrapper that converts those images to Ursina Texture objects and caches them. Guard any test that constructs a Texture with a try/except + pytest.skip so headless CI passes.
    Scope discipline: In AssetManager, implement __init__ and wall_textures fully. Leave equation_texture, floor_map_texture, and name_tile_texture raising NotImplementedError("M3") / ("M4") exactly as in the stub — those belong to later milestones.
    Add from __future__ import annotations to both modules. Use type hints everywhere. Cache textures so repeated calls return the same objects.
    Paths in the manifest are relative to pack_dir (e.g. "png/l1_step1_off.png" → <pack_dir>/png/l1_step1_off.png). Placeholder size = the manifest entry's w_px×h_px if present, else 1024×1024.

REQUIRED BEHAVIOR — content/loader.py

def load_level(pack_dir: str, level_id: str) -> Level: ...
def load_manifest(pack_dir: str) -> dict[str, AssetEntry]: ...
def validate_pack(pack_dir: str) -> list[str]: ...   # [] means OK

    load_level: read & validate concept_graph.json (→ ConceptGraph), floorplan.json (→ Floorplan), and every rooms/*.json (→ RoomContent); assemble a Level(level_id=..., floorplan=..., rooms={room_id: RoomContent}). Raise a clear ValueError (with a useful message) if validation fails or level_id doesn't match.
    load_manifest: read manifest.json → {block_id: AssetEntry} (validated).
    validate_pack: return a list of human-readable error strings (do not raise). It must catch at least:
        any JSON file that fails pydantic validation,
        any schema_version that ≠ principia.config.SCHEMA_VERSION,
        any room in floorplan.rooms with no matching rooms/<id>.json,
        any RoomContent.room_id not present in floorplan.rooms,
        any door id referenced by a room that isn't in floorplan.doors,
        any corridor from/to that isn't an existing room id.
        (Missing PNG files are not reported as errors.)

REQUIRED BEHAVIOR — assets/manager.py

class AssetManager:
    def __init__(self, pack_dir: str) -> None: ...
    def wall_textures(self, block_id: str): ...   # -> (off_texture, on_texture), cached
    def equation_texture(self, eq_id: str): raise NotImplementedError("M3")
    def floor_map_texture(self, level_id: str): raise NotImplementedError("M4")
    def name_tile_texture(self, room_id: str): raise NotImplementedError("M4")

    __init__: store pack_dir, load manifest.json (json + AssetEntry), init caches.
    wall_textures(block_id): look up the manifest entry; resolve its off_png and on_png to images via your private helper (real PNG if it exists, else placeholder); convert to Texture; cache and return (off, on). If block_id is missing from the manifest, generate placeholders anyway (label them with the block id) so the room still renders — do not crash.
    Recommended private helper (not frozen, just keep it testable): _resolve_image(self, rel_path: str, label: str, on: bool) -> PIL.Image.Image.

TESTS YOU MUST WRITE

tests/test_loader.py:

    load_level("content_packs/principia", "fixture") returns a Level with level_id == "fixture", floorplan.ceiling_h == 3.0, and "lemma1" in level.rooms, and level.rooms["lemma1"].demon.demon_id == "demon_lemma1".
    load_manifest(...) returns a dict whose "l1_step1" entry has w_px == 1024.
    validate_pack("content_packs/principia") returns [].
    A negative test using tmp_path: copy the fixture, then add a floorplan room "ghost" with no rooms/ghost.json; assert validate_pack returns a non-empty list mentioning ghost.

tests/test_assets.py:

    Test _resolve_image (or equivalent) without Ursina: it returns a PIL.Image.Image of the expected size for a missing PNG, and the off image differs from the on image (e.g. grayscale vs colored — assert they're not byte-identical).
    Guarded texture test: try to create the AssetManager and call wall_textures("l1_step1"); if Ursina/Texture creation raises (no display in CI), pytest.skip(...). When it works, assert two distinct objects are returned and that calling again returns the same cached objects.

OUTPUT FORMAT

First confirm in one line that you have everything you need (or ask for a missing file). Then output four separate copy-paste code blocks, each preceded by its file path in bold:

    principia/content/loader.py
    principia/assets/manager.py
    tests/test_loader.py
    tests/test_assets.py

End with one line telling DeepSeek how to verify: the exact pytest command and what "pass" looks like.
REFERENCE FILES (already in the repo — do not rewrite them)

principia/config.py (relevant constants):

SCHEMA_VERSION: str = "1.0"
WALL_PX_PER_METER: int = 320
DEFAULT_PACK: str = "content_packs/principia"

principia/schema.py (the data contracts — import from here):

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from principia.config import SCHEMA_VERSION

Vec3 = tuple[float, float, float]
Facing = Literal["N", "E", "S", "W"]
EdgeKind = Literal["depends_on", "generalizes", "example_of", "related"]
BlockType = Literal["diagram", "text"]

class _Base(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

class ConceptNode(_Base):
    id: str; name: str; importance: int = Field(ge=1, le=5); summary: str = ""

class ConceptEdge(_Base):
    source: str; target: str; weight: float = 1.0
    kind: EdgeKind = "related"; label: str = ""

class ConceptGraph(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str; title: str = ""
    nodes: list[ConceptNode]
    edges: list[ConceptEdge] = Field(default_factory=list)

class Rect(_Base):
    x: float; z: float; w: float; d: float

class Door(_Base):
    id: str; room: str; corridor: str
    position: Vec3; facing: Facing; width: float

class RoomCell(_Base):
    id: str; rect: Rect; center: Vec3
    name_tile: str = ""; doors: list[str] = Field(default_factory=list)

class Corridor(_Base):
    id: str
    from_room: str = Field(alias="from")
    to_room: str = Field(alias="to")
    spline: list[Vec3]; width: float; guide_color: str = "#ffcc00"

class Floorplan(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str; ceiling_h: float
    rooms: list[RoomCell]
    corridors: list[Corridor] = Field(default_factory=list)
    doors: list[Door] = Field(default_factory=list)

class WallBlock(_Base):
    block_id: str; type: BlockType
    off_png: str; on_png: str
    colors: dict[str, str] = Field(default_factory=dict)
    order: int = 0; caption: str = ""

class Wall(_Base):
    wall_id: str; facing: Facing
    blocks: list[WallBlock] = Field(default_factory=list)

class CeilingBand(_Base):
    band_id: str; above_wall: str
    equation_png: str; hidden_until_demon_dead: bool = True

class DemonCircle(_Base):
    offset: Vec3; radius: float; color: str; role: str = "body"

class DemonSpec(_Base):
    demon_id: str; position: Vec3; hp: int = 3
    circles: list[DemonCircle] = Field(default_factory=list)
    spray_glyphs: list[str] = Field(default_factory=list)

class SecretDoorSpec(_Base):
    door_id: str; wall_id: str; tile_png: str
    position: Vec3; boss: DemonSpec | None = None

class RoomContent(_Base):
    schema_version: str = SCHEMA_VERSION
    room_id: str
    walls: list[Wall] = Field(default_factory=list)
    ceiling_bands: list[CeilingBand] = Field(default_factory=list)
    demon: DemonSpec | None = None
    secret_door: SecretDoorSpec | None = None

class AssetEntry(_Base):
    off_png: str; on_png: str; w_px: int; h_px: int

class Level(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    floorplan: Floorplan
    rooms: dict[str, RoomContent]

class SaveGame(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    blocks_on: list[str] = Field(default_factory=list)
    demons_dead: list[str] = Field(default_factory=list)
    secrets_open: list[str] = Field(default_factory=list)

Current stub principia/content/loader.py (replace with your implementation):

from __future__ import annotations
from principia.schema import Level, AssetEntry

def load_level(pack_dir: str, level_id: str) -> Level:
    raise NotImplementedError("M1")
def load_manifest(pack_dir: str) -> dict[str, AssetEntry]:
    raise NotImplementedError("M1")
def validate_pack(pack_dir: str) -> list[str]:
    raise NotImplementedError("M1")

Current stub principia/assets/manager.py (replace; keep the later-milestone methods as NotImplementedError):

from __future__ import annotations

class AssetManager:
    def __init__(self, pack_dir: str) -> None:
        raise NotImplementedError("M1")
    def wall_textures(self, block_id: str):
        raise NotImplementedError("M1")
    def equation_texture(self, eq_id: str):
        raise NotImplementedError("M3")
    def floor_map_texture(self, level_id: str):
        raise NotImplementedError("M4")
    def name_tile_texture(self, room_id: str):
        raise NotImplementedError("M4")

The fixture pack you must work against — content_packs/principia/:

concept_graph.json

{ "schema_version": "1.0", "level_id": "fixture", "title": "Golden Fixture Level",
  "nodes": [
    { "id": "lemma1", "name": "Lemma I", "importance": 5, "summary": "Quantities tending continually to equality become ultimately equal." },
    { "id": "lemma2", "name": "Lemma II", "importance": 3, "summary": "Sum of figures approaches the curvilinear area." }],
  "edges": [ { "source": "lemma1", "target": "lemma2", "weight": 2, "kind": "depends_on", "label": "used by" } ] }

floorplan.json

{ "schema_version": "1.0", "level_id": "fixture", "ceiling_h": 3.0,
  "rooms": [
    { "id": "lemma1", "rect": { "x": 0, "z": 0, "w": 12, "d": 12 }, "center": [6, 0, 6], "name_tile": "tiles/lemma1_name.png", "doors": ["door_l1_l2"] },
    { "id": "lemma2", "rect": { "x": 0, "z": 24, "w": 10, "d": 10 }, "center": [5, 0, 29], "name_tile": "tiles/lemma2_name.png", "doors": ["door_l1_l2"] }],
  "corridors": [
    { "id": "corr_l1_l2", "from": "lemma1", "to": "lemma2", "spline": [[6,0,12],[6,0,18],[5,0,24]], "width": 3.0, "guide_color": "#ffcc00" }],
  "doors": [
    { "id": "door_l1_l2", "room": "lemma1", "corridor": "corr_l1_l2", "position": [6,0,12], "facing": "N", "width": 3.0 } ] }

manifest.json

{ "l1_step1": { "off_png": "png/l1_step1_off.png", "on_png": "png/l1_step1_on.png", "w_px": 1024, "h_px": 1024 },
  "l1_text1": { "off_png": "png/l1_text1_off.png", "on_png": "png/l1_text1_on.png", "w_px": 1024, "h_px": 1024 } }

rooms/lemma1.json

{ "schema_version": "1.0", "room_id": "lemma1",
  "walls": [ { "wall_id": "w_lemma1_N", "facing": "N", "blocks": [
    { "block_id": "l1_step1", "type": "diagram", "order": 1, "off_png": "png/l1_step1_off.png", "on_png": "png/l1_step1_on.png", "colors": { "abc": "#0072B2", "bd": "#D55E00" }, "caption": "Inscribed and circumscribed figures" },
    { "block_id": "l1_text1", "type": "text", "order": 2, "off_png": "png/l1_text1_off.png", "on_png": "png/l1_text1_on.png", "colors": { "abc": "#0072B2", "bd": "#D55E00" } } ] } ],
  "ceiling_bands": [ { "band_id": "cb_l1_1", "above_wall": "w_lemma1_N", "equation_png": "png/eq_l1_1.png", "hidden_until_demon_dead": true } ],
  "demon": { "demon_id": "demon_lemma1", "position": [6,1.2,6], "hp": 3, "circles": [
    { "offset": [0,0,0], "radius": 0.6, "color": "#FF7AB6", "role": "body" },
    { "offset": [-0.2,0.25,0.55], "radius": 0.1, "color": "#3B6BFF", "role": "eye" },
    { "offset": [0.2,0.25,0.55], "radius": 0.1, "color": "#3B6BFF", "role": "eye" },
    { "offset": [0,-0.1,0.6], "radius": 0.06, "color": "#FFFFFF", "role": "tooth" } ],
    "spray_glyphs": ["png/eq_l1_1.png"] },
  "secret_door": { "door_id": "qed_lemma1", "wall_id": "w_lemma1_S", "tile_png": "png/qed_halmos.png", "position": [6,1.5,0.05],
    "boss": { "demon_id": "boss_lemma1", "position": [6,1.2,-3], "hp": 5, "circles": [], "spray_glyphs": [] } } }

    Note: the fixture's floorplan.json lists lemma2, but there is currently no rooms/lemma2.json. Decide how to handle this: load_level should still succeed for rooms that exist, but validate_pack must report the missing rooms/lemma2.json as an error string. Make your load_level robust — load whatever room files exist, and don't crash on lemma2 being absent. (Your negative test for ghost is the same mechanism.)

=== END M1 CHILD PROMPT ===

A couple of notes for you, Nir:

    I deliberately left the missing rooms/lemma2.json in the fixture — it's a realistic "half-authored pack," and it forces validate_pack to actually prove it catches the gap (your safety net against drift). The child is told exactly how to handle it.
    After the child returns the four files and DeepSeek confirms pytest -q is green, the natural next child task is world/builder.py — turning a loaded RoomContent + AssetManager into the actual Ursina room entities (replacing the hardcoded room in m0_demo.py with a data-driven one).

Want me to draft that world/builder.py child prompt next, or would you rather first run M1 through DeepSeek and confirm the tests pass before we proceed? 🙂
