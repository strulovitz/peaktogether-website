YESSS let's build it! 🎉 Below is everything, in two parts:

    PART A — the repo skeleton (every module as a frozen-interface stub, plus the real schema.py and config.py, a golden-fixture content pack, and tests that pass today).
    PART B — m0_demo.py, a single self-contained file you can run right now on Windows: a textured room, mouse-look, WASD, and the core "shoot-a-wall-to-colorize-it" verb + a sphere-demon you can disintegrate to reveal a blood-red ceiling equation.

    One architectural correction to tell DeepSeek: I renamed the planned io/ package to control/. The name io shadows Python's standard-library io module and would cause subtle, maddening bugs in a vibe-coding workflow. Everything else matches the Master Design Doc.

📋 Instructions for DeepSeek (paste this first)

    Create this exact folder structure in the repo. Files marked STUB are interface-only (they raise NotImplementedError and exist so children can implement them one at a time against frozen signatures). schema.py, config.py, the content_packs/principia/ JSON, the tests, and m0_demo.py are complete and real. After creating everything, run pip install -r requirements.txt, then pytest -q (the fixture tests must pass), then python m0_demo.py (a window should open with a walkable room).

principia-descent/
├── requirements.txt
├── README.md
├── m0_demo.py                      ← RUN THIS TODAY (Part B)
├── principia/
│   ├── __init__.py
│   ├── config.py                   ← REAL
│   ├── schema.py                   ← REAL (the data contracts)
│   ├── app.py                      ← STUB (full game, later)
│   ├── content/{__init__.py, loader.py}
│   ├── layout/{__init__.py, graph.py}
│   ├── world/{__init__.py, builder.py, rooms.py}
│   ├── control/{__init__.py, input.py}     (renamed from io/)
│   ├── player/{__init__.py, mover.py, shooter.py}
│   ├── walls/{__init__.py, state.py}
│   ├── ceiling/{__init__.py, equations.py}
│   ├── enemy/{__init__.py, demon.py}
│   ├── doors/{__init__.py, secret.py}
│   ├── ui/{__init__.py, mapmode.py, hud.py, readmode.py}
│   ├── assets/{__init__.py, manager.py}
│   ├── audio/{__init__.py, sound.py}
│   └── nav/{__init__.py, navigator.py}
├── tools/{bake.py, layout_render.py}
├── content_packs/principia/
│   ├── concept_graph.json
│   ├── floorplan.json
│   ├── manifest.json
│   └── rooms/lemma1.json
└── tests/{__init__.py, test_fixture.py}

PART A — REPO SKELETON
requirements.txt

ursina==7.0.0
panda3d>=1.10.13
pygame>=2.5.0
pillow>=10.0.0
numpy>=1.24
networkx>=3.0
pydantic>=2.5
pytest>=7.4

README.md

# Principia Descent

An open-source, two-player educational FPS that teaches Newton's *Principia*
(and other math books) by turning proofs into a walkable art-gallery dungeon.

- **Run the demo today:** `python m0_demo.py`
- **Run tests:** `pytest -q`
- License: code = MIT, content = CC-BY-SA 4.0

## How the code is organised
The runtime never needs to understand the math. It only loads pre-baked PNGs
+ JSON. Three worlds, kept separate:
1. CONTENT (book text/proofs)  -> authored by LLM "content children"
2. BUILD/OFFLINE (tools/)       -> bakes LaTeX/TikZ to PNG, lays out the graph
3. RUNTIME (principia/)         -> the game, loads baked assets only

Every module talks to others ONLY through the typed signatures in each file
and the pydantic data contracts in `principia/schema.py`. Do not import another
module's internals.

## Build order (each independently testable)
schema -> assets/manager -> content/loader -> layout/graph -> world/builder
-> world/rooms -> nav/navigator -> control/input -> player/mover
-> player/shooter -> walls/state -> enemy/demon -> ceiling/equations
-> doors/secret -> ui/* -> app

principia/config.py — REAL (constants & tunables)

"""
config.py — all engine constants and tunables in ONE place.

Children: import what you need from here. Do NOT hard-code magic numbers
in other modules. Anything a designer might want to tweak lives here.
"""
from __future__ import annotations

# ---------------------------------------------------------------- versioning
# Bump this when you make a breaking change to any data contract in schema.py.
# Every level JSON carries a schema_version; the loader asserts it matches.
SCHEMA_VERSION: str = "1.0"

# ---------------------------------------------------------------- world/space
CEILING_H: float = 3.0          # low ceiling so equations are readable overhead
EYE_HEIGHT: float = 1.6
WALL_THICKNESS: float = 0.2
DEFAULT_ROOM_SIZE: float = 12.0
DEFAULT_CORRIDOR_WIDTH: float = 3.0

# Room sizing from node importance (1..5):  side = base + k * importance
ROOM_SIZE_BASE: float = 8.0
ROOM_SIZE_PER_IMPORTANCE: float = 2.0

# ---------------------------------------------------------------- movement
WALK_SPEED: float = 4.0         # slow — this is a reading game
ACCEL_SMOOTHING: float = 8.0    # higher = snappier; lower = floatier (comfort)
PITCH_CLAMP_DEG: float = 70.0

# ---------------------------------------------------------------- camera/comfort
FOV: float = 75.0               # narrower FOV reduces motion sickness
TURN_SMOOTHING: float = 10.0
HEAD_BOB: bool = False          # OFF by default for comfort
VIGNETTE_ON_MOVE: bool = True

# ---------------------------------------------------------------- input
MOUSE_SENSITIVITY: float = 40.0
GAMEPAD_LOOK_SENS: float = 120.0
GAMEPAD_DEADZONE: float = 0.15

# ---------------------------------------------------------------- shooting
SHOOT_RANGE: float = 25.0

# ---------------------------------------------------------------- rendering
WALL_PX_PER_METER: int = 320    # baked-panel resolution target (R3: legibility)
EMISSIVE_PANELS: bool = True    # self-lit panels so text reads in any lighting
ANISOTROPY: int = 16

# ---------------------------------------------------------------- accessibility (R1)
# Okabe–Ito colour-blind-safe palette. Content children should pick group
# colours from here, AND always add a redundant cue (badge/dash/marker).
CVD_MODE: bool = False
OKABE_ITO: dict[str, str] = {
    "black":   "#000000",
    "orange":  "#E69F00",
    "skyblue": "#56B4E9",
    "green":   "#009E73",
    "yellow":  "#F0E442",
    "blue":    "#0072B2",
    "vermil":  "#D55E00",
    "purple":  "#CC79A7",
}

# ---------------------------------------------------------------- theme
BLOOD_RED = (0.7, 0.0, 0.0)     # ceiling equations after the demon dies
DEMON_BODY = "#FF7AB6"
DEMON_EYE = "#3B6BFF"
DEMON_TOOTH = "#FFFFFF"

# ---------------------------------------------------------------- paths
DEFAULT_PACK: str = "content_packs/principia"
SAVE_FILE: str = "savegame.json"

principia/schema.py — REAL (THE data contracts)

"""
schema.py — the single source of truth for all data that crosses module
boundaries. Every JSON file in a content pack validates against these
pydantic models. If it isn't defined here, modules must not pass it around.

Children: depend on these types. Never invent a parallel data shape.
"""
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


# ============================================================ concept graph
class ConceptNode(_Base):
    id: str
    name: str
    importance: int = Field(ge=1, le=5)
    summary: str = ""


class ConceptEdge(_Base):
    source: str
    target: str
    weight: float = 1.0
    kind: EdgeKind = "related"
    label: str = ""


class ConceptGraph(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    title: str = ""
    nodes: list[ConceptNode]
    edges: list[ConceptEdge] = Field(default_factory=list)


# ============================================================ floorplan
class Rect(_Base):
    x: float
    z: float
    w: float
    d: float


class Door(_Base):
    id: str
    room: str
    corridor: str
    position: Vec3
    facing: Facing
    width: float


class RoomCell(_Base):
    id: str
    rect: Rect
    center: Vec3
    name_tile: str = ""
    doors: list[str] = Field(default_factory=list)


class Corridor(_Base):
    id: str
    from_room: str = Field(alias="from")
    to_room: str = Field(alias="to")
    spline: list[Vec3]
    width: float
    guide_color: str = "#ffcc00"


class Floorplan(_Base):
    schema_version: str = SCHEMA_VERSION
    level_id: str
    ceiling_h: float
    rooms: list[RoomCell]
    corridors: list[Corridor] = Field(default_factory=list)
    doors: list[Door] = Field(default_factory=list)


# ============================================================ room content
class WallBlock(_Base):
    block_id: str
    type: BlockType
    off_png: str
    on_png: str
    colors: dict[str, str] = Field(default_factory=dict)  # group -> hex
    order: int = 0
    caption: str = ""


class Wall(_Base):
    wall_id: str
    facing: Facing
    blocks: list[WallBlock] = Field(default_factory=list)


class CeilingBand(_Base):
    band_id: str
    above_wall: str
    equation_png: str
    hidden_until_demon_dead: bool = True


class DemonCircle(_Base):
    offset: Vec3
    radius: float
    color: str
    role: str = "body"


class DemonSpec(_Base):
    demon_id: str
    position: Vec3
    hp: int = 3
    circles: list[DemonCircle] = Field(default_factory=list)
    spray_glyphs: list[str] = Field(default_factory=list)


class SecretDoorSpec(_Base):
    door_id: str
    wall_id: str
    tile_png: str
    position: Vec3
    boss: DemonSpec | None = None


class RoomContent(_Base):
    schema_version: str = SCHEMA_VERSION
    room_id: str
    walls: list[Wall] = Field(default_factory=list)
    ceiling_bands: list[CeilingBand] = Field(default_factory=list)
    demon: DemonSpec | None = None
    secret_door: SecretDoorSpec | None = None


# ============================================================ assets / save
class AssetEntry(_Base):
    off_png: str
    on_png: str
    w_px: int
    h_px: int


class Level(_Base):
    """Everything the runtime needs for one level, after loading."""
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

Golden-fixture content pack — REAL

content_packs/principia/concept_graph.json

{
  "schema_version": "1.0",
  "level_id": "fixture",
  "title": "Golden Fixture Level",
  "nodes": [
    { "id": "lemma1", "name": "Lemma I", "importance": 5,
      "summary": "Quantities tending continually to equality become ultimately equal." },
    { "id": "lemma2", "name": "Lemma II", "importance": 3,
      "summary": "Sum of inscribed and circumscribed figures approaches the curvilinear area." }
  ],
  "edges": [
    { "source": "lemma1", "target": "lemma2", "weight": 2,
      "kind": "depends_on", "label": "used by" }
  ]
}

content_packs/principia/floorplan.json

{
  "schema_version": "1.0",
  "level_id": "fixture",
  "ceiling_h": 3.0,
  "rooms": [
    { "id": "lemma1", "rect": { "x": 0, "z": 0, "w": 12, "d": 12 },
      "center": [6, 0, 6], "name_tile": "tiles/lemma1_name.png",
      "doors": ["door_l1_l2"] },
    { "id": "lemma2", "rect": { "x": 0, "z": 24, "w": 10, "d": 10 },
      "center": [5, 0, 29], "name_tile": "tiles/lemma2_name.png",
      "doors": ["door_l1_l2"] }
  ],
  "corridors": [
    { "id": "corr_l1_l2", "from": "lemma1", "to": "lemma2",
      "spline": [[6, 0, 12], [6, 0, 18], [5, 0, 24]],
      "width": 3.0, "guide_color": "#ffcc00" }
  ],
  "doors": [
    { "id": "door_l1_l2", "room": "lemma1", "corridor": "corr_l1_l2",
      "position": [6, 0, 12], "facing": "N", "width": 3.0 }
  ]
}

content_packs/principia/manifest.json

{
  "l1_step1": { "off_png": "png/l1_step1_off.png", "on_png": "png/l1_step1_on.png", "w_px": 1024, "h_px": 1024 },
  "l1_text1": { "off_png": "png/l1_text1_off.png", "on_png": "png/l1_text1_on.png", "w_px": 1024, "h_px": 1024 }
}

content_packs/principia/rooms/lemma1.json

{
  "schema_version": "1.0",
  "room_id": "lemma1",
  "walls": [
    {
      "wall_id": "w_lemma1_N", "facing": "N",
      "blocks": [
        { "block_id": "l1_step1", "type": "diagram", "order": 1,
          "off_png": "png/l1_step1_off.png", "on_png": "png/l1_step1_on.png",
          "colors": { "abc": "#0072B2", "bd": "#D55E00" },
          "caption": "Inscribed and circumscribed figures" },
        { "block_id": "l1_text1", "type": "text", "order": 2,
          "off_png": "png/l1_text1_off.png", "on_png": "png/l1_text1_on.png",
          "colors": { "abc": "#0072B2", "bd": "#D55E00" } }
      ]
    }
  ],
  "ceiling_bands": [
    { "band_id": "cb_l1_1", "above_wall": "w_lemma1_N",
      "equation_png": "png/eq_l1_1.png", "hidden_until_demon_dead": true }
  ],
  "demon": {
    "demon_id": "demon_lemma1", "position": [6, 1.2, 6], "hp": 3,
    "circles": [
      { "offset": [0, 0, 0], "radius": 0.6, "color": "#FF7AB6", "role": "body" },
      { "offset": [-0.2, 0.25, 0.55], "radius": 0.1, "color": "#3B6BFF", "role": "eye" },
      { "offset": [0.2, 0.25, 0.55], "radius": 0.1, "color": "#3B6BFF", "role": "eye" },
      { "offset": [0, -0.1, 0.6], "radius": 0.06, "color": "#FFFFFF", "role": "tooth" }
    ],
    "spray_glyphs": ["png/eq_l1_1.png"]
  },
  "secret_door": {
    "door_id": "qed_lemma1", "wall_id": "w_lemma1_S",
    "tile_png": "png/qed_halmos.png", "position": [6, 1.5, 0.05],
    "boss": { "demon_id": "boss_lemma1", "position": [6, 1.2, -3], "hp": 5,
              "circles": [], "spray_glyphs": [] }
  }
}

tests/test_fixture.py — REAL (passes today)

"""Validates the golden-fixture content pack against the frozen schema.

Runs WITHOUT any runtime modules implemented yet — it only needs schema.py.
This is your guard against silent interface drift between child chats.
"""
import json
from pathlib import Path

from principia import schema

PACK = Path("content_packs/principia")


def _load(name):
    return json.loads((PACK / name).read_text(encoding="utf-8"))


def test_concept_graph_validates():
    g = schema.ConceptGraph.model_validate(_load("concept_graph.json"))
    assert g.level_id == "fixture"
    assert {n.id for n in g.nodes} == {"lemma1", "lemma2"}


def test_floorplan_validates():
    fp = schema.Floorplan.model_validate(_load("floorplan.json"))
    assert fp.ceiling_h == 3.0
    assert fp.corridors[0].from_room == "lemma1"   # alias 'from' works
    assert fp.corridors[0].to_room == "lemma2"


def test_room_content_validates():
    rc = schema.RoomContent.model_validate(_load("rooms/lemma1.json"))
    assert rc.room_id == "lemma1"
    assert rc.demon.demon_id == "demon_lemma1"
    assert rc.secret_door.boss.hp == 5
    assert rc.walls[0].blocks[0].colors["abc"] == "#0072B2"


def test_manifest_validates():
    manifest = _load("manifest.json")
    entries = {k: schema.AssetEntry.model_validate(v) for k, v in manifest.items()}
    assert entries["l1_step1"].w_px == 1024


def test_schema_versions_match():
    for f in ["concept_graph.json", "floorplan.json", "rooms/lemma1.json"]:
        assert _load(f)["schema_version"] == schema.SCHEMA_VERSION

Module stubs (frozen interfaces)

Create an empty __init__.py in each of these directories:

principia/__init__.py
principia/content/__init__.py
principia/layout/__init__.py
principia/world/__init__.py
principia/control/__init__.py
principia/player/__init__.py
principia/walls/__init__.py
principia/ceiling/__init__.py
principia/enemy/__init__.py
principia/doors/__init__.py
principia/ui/__init__.py
principia/assets/__init__.py
principia/audio/__init__.py
principia/nav/__init__.py
tests/__init__.py

principia/content/loader.py — implemented in M1

"""Loads a content pack (JSON) into validated pydantic models."""
from __future__ import annotations
from principia.schema import Level, AssetEntry


def load_level(pack_dir: str, level_id: str) -> Level:
    """Read concept_graph/floorplan/rooms/*.json -> a validated Level."""
    raise NotImplementedError("M1")


def load_manifest(pack_dir: str) -> dict[str, AssetEntry]:
    """Read manifest.json -> {block_id: AssetEntry}."""
    raise NotImplementedError("M1")


def validate_pack(pack_dir: str) -> list[str]:
    """Return a list of human-readable error strings; [] means the pack is OK."""
    raise NotImplementedError("M1")

principia/assets/manager.py — implemented in M1

"""Turns manifest entries + png paths into engine textures (lazy, cached)."""
from __future__ import annotations


class AssetManager:
    def __init__(self, pack_dir: str) -> None:
        raise NotImplementedError("M1")

    def wall_textures(self, block_id: str):
        """Return (off_texture, on_texture) for a wall block."""
        raise NotImplementedError("M1")

    def equation_texture(self, eq_id: str):
        raise NotImplementedError("M3")

    def floor_map_texture(self, level_id: str):
        raise NotImplementedError("M4")

    def name_tile_texture(self, room_id: str):
        raise NotImplementedError("M4")

principia/layout/graph.py — implemented in M4

"""Concept graph -> spatial floorplan + baked floor-map image. Deterministic."""
from __future__ import annotations
from principia.schema import ConceptGraph, Floorplan


def layout_level(graph: ConceptGraph, seed: int = 0) -> Floorplan:
    """spring_layout -> room sizing -> de-overlap -> b-spline corridors -> doors."""
    raise NotImplementedError("M4")


def render_floor_map(floorplan: Floorplan, out_png: str, size_px: int = 4096) -> None:
    raise NotImplementedError("M4")


def make_guide_lines(floorplan: Floorplan):
    raise NotImplementedError("M4")

principia/world/builder.py — implemented in M1

"""Builds the Ursina entities for ONE cell (room or corridor)."""
from __future__ import annotations
from principia.schema import RoomCell, Corridor
from principia.assets.manager import AssetManager


def build_room(room: RoomCell, content, assets: AssetManager):
    """Return a CellEntities handle (has .destroy()) for one room."""
    raise NotImplementedError("M1")


def build_corridor(corr: Corridor, assets: AssetManager):
    raise NotImplementedError("M4")

principia/world/rooms.py — implemented in M4

"""Loads/unloads the current cell so only one room/corridor exists at a time."""
from __future__ import annotations
from principia.schema import Floorplan
from principia.assets.manager import AssetManager


class RoomManager:
    def __init__(self, floorplan: Floorplan, assets: AssetManager) -> None:
        raise NotImplementedError("M4")

    def enter_cell(self, cell_id: str) -> None:
        raise NotImplementedError("M4")

    def current_cell(self) -> str:
        raise NotImplementedError("M4")

    def cell_entities(self):
        raise NotImplementedError("M4")

principia/nav/navigator.py — implemented in M4

"""Detects which cell the players occupy and triggers door transitions."""
from __future__ import annotations
from principia.schema import Floorplan, Vec3


class Navigator:
    def __init__(self, floorplan: Floorplan, rooms) -> None:
        raise NotImplementedError("M4")

    def update(self, player_pos: Vec3) -> None:
        raise NotImplementedError("M4")

    def cell_at(self, pos: Vec3) -> str:
        raise NotImplementedError("M4")

principia/control/input.py — implemented in M2 (kb/mouse), M6 (gamepad split)

"""The ONLY module that touches input devices. Everything else asks here for
semantic actions, never raw keys. Mover = boyfriend; Shooter = girlfriend."""
from __future__ import annotations


class InputManager:
    def poll(self) -> None:
        """Call once per frame to refresh device state."""
        raise NotImplementedError("M2")

    # --- MOVER (boyfriend) ---
    def move_axis(self) -> tuple[float, float]:
        """(strafe, forward), each in [-1, 1]."""
        raise NotImplementedError("M2")

    def body_yaw_delta(self) -> float:
        raise NotImplementedError("M6")

    # --- SHOOTER (girlfriend) ---
    def aim_delta(self) -> tuple[float, float]:
        """(yaw_delta, pitch_delta)."""
        raise NotImplementedError("M2")

    def shoot_pressed(self) -> bool:
        """Edge-triggered: True on the frame the trigger goes down."""
        raise NotImplementedError("M2")

    # --- SHARED ---
    def toggle_map_pressed(self) -> bool:
        raise NotImplementedError("M4")

    def read_mode_pressed(self) -> bool:
        raise NotImplementedError("M3")

    def pause_pressed(self) -> bool:
        raise NotImplementedError("M2")

principia/player/mover.py — implemented in M2

"""Translates the shared body. Movement is relative to body heading (R2)."""
from __future__ import annotations
from principia.control.input import InputManager


class Mover:
    def __init__(self, camera, input_mgr: InputManager, nav) -> None:
        raise NotImplementedError("M2")

    def update(self, dt: float) -> None:
        raise NotImplementedError("M2")

principia/player/shooter.py — implemented in M2

"""Aims the reticle and fires a raycast; dispatches hits to registered handlers."""
from __future__ import annotations
from principia.control.input import InputManager


class Shooter:
    def __init__(self, camera, input_mgr: InputManager) -> None:
        raise NotImplementedError("M2")

    def update(self, dt: float) -> None:
        raise NotImplementedError("M2")

    def register_hit_handlers(self, on_wall, on_demon, on_secret) -> None:
        """on_wall(block_id), on_demon(demon, point), on_secret(door_id)."""
        raise NotImplementedError("M2")

principia/walls/state.py — implemented in M2

"""Off/On state per wall block (sticky). Tracks reading progress; saves/loads."""
from __future__ import annotations
from principia.assets.manager import AssetManager


class WallStateManager:
    def __init__(self, assets: AssetManager) -> None:
        raise NotImplementedError("M2")

    def register(self, block_id: str, entity, off_tex, on_tex) -> None:
        raise NotImplementedError("M2")

    def toggle(self, block_id: str) -> bool:
        """Return new state (True = on/colored)."""
        raise NotImplementedError("M2")

    def state(self, block_id: str) -> bool:
        raise NotImplementedError("M2")

    def progress(self, room_id: str) -> float:
        """Fraction of this room's blocks that are 'on' (0..1)."""
        raise NotImplementedError("M2")

    def save(self, path: str) -> None:
        raise NotImplementedError("M2")

    def load(self, path: str) -> None:
        raise NotImplementedError("M2")

principia/ceiling/equations.py — implemented in M3

"""Ceiling equation bands: hidden until the room's demon dies, then blood-red."""
from __future__ import annotations
from principia.schema import CeilingBand, Vec3
from principia.assets.manager import AssetManager


class CeilingManager:
    def __init__(self, assets: AssetManager) -> None:
        raise NotImplementedError("M3")

    def register_band(self, room_id: str, band: CeilingBand, entity) -> None:
        raise NotImplementedError("M3")

    def reveal(self, room_id: str) -> None:
        """Fade the room's equation bands in, tinted blood-red."""
        raise NotImplementedError("M3")

    def spray_from(self, origin: Vec3, glyph_texes: list) -> None:
        """Cosmetic: fling equation glyphs outward; they fade and vanish."""
        raise NotImplementedError("M3")

principia/enemy/demon.py — implemented in M3

"""Harmless demon made of coloured sprite circles. Death = disintegration."""
from __future__ import annotations
from principia.schema import DemonSpec, Vec3


class Demon:
    def __init__(self, spec: DemonSpec, position: Vec3) -> None:
        raise NotImplementedError("M3")

    def update(self, dt: float) -> None:
        raise NotImplementedError("M3")

    def hit(self, point: Vec3) -> None:
        raise NotImplementedError("M3")

    def is_dead(self) -> bool:
        raise NotImplementedError("M3")

    def on_death(self, callback) -> None:
        """callback() fires once; triggers ceiling reveal + equation spray."""
        raise NotImplementedError("M3")

principia/doors/secret.py — implemented in M5

"""The QED / Halmos-tombstone tile. Shooting it opens it and spawns a boss."""
from __future__ import annotations
from principia.schema import SecretDoorSpec


class SecretDoor:
    def __init__(self, spec: SecretDoorSpec) -> None:
        raise NotImplementedError("M5")

    def shoot(self) -> None:
        raise NotImplementedError("M5")

    def on_boss_killed(self, callback) -> None:
        raise NotImplementedError("M5")

principia/ui/mapmode.py — implemented in M4

"""2D wireframe automap overlay (Doom-style)."""
from __future__ import annotations
from principia.schema import Floorplan, Vec3


class MapMode:
    def __init__(self, floorplan: Floorplan, wall_state) -> None:
        raise NotImplementedError("M4")

    def toggle(self) -> None:
        raise NotImplementedError("M4")

    def update(self, player_pos: Vec3) -> None:
        raise NotImplementedError("M4")

principia/ui/hud.py — implemented in M2

"""Reticle, prompts, reading-progress indicator."""
from __future__ import annotations


class HUD:
    def update(self, ctx) -> None:
        raise NotImplementedError("M2")

principia/ui/readmode.py — implemented in M3 (the R3 legibility fix)

"""Crisp full-screen 2D overlay of a panel PNG (no perspective blur)."""
from __future__ import annotations


class ReadMode:
    def open(self, block_id: str, texture) -> None:
        raise NotImplementedError("M3")

    def close(self) -> None:
        raise NotImplementedError("M3")

    def is_open(self) -> bool:
        raise NotImplementedError("M3")

principia/audio/sound.py — implemented later

"""Sound effects (shoot, colorize, demon death, reveal). pygame.mixer."""
from __future__ import annotations


class Sound:
    def play(self, name: str) -> None:
        raise NotImplementedError("later")

principia/app.py — the full game; wired up across milestones

"""
app.py — full-game entry point (NOT the demo). Wires managers and drives the
per-frame update order. Implemented incrementally; run m0_demo.py for now.

Per-frame order: input.poll -> mover -> shooter -> navigator
                 -> demon/ceiling updates -> hud/map/readmode.
"""
from __future__ import annotations


def main(pack: str, level: str) -> None:
    raise NotImplementedError("Built across M1..M6; use m0_demo.py today.")


if __name__ == "__main__":
    main("content_packs/principia", "fixture")

tools/bake.py and tools/layout_render.py — offline tools, later

"""bake.py — compile TikZ/LaTeX wall sources twice (off/on) into PNGs + manifest."""
def main() -> None:
    raise NotImplementedError("M5/M7 offline pipeline")

if __name__ == "__main__":
    main()

"""layout_render.py — run layout_level + render_floor_map for a pack."""
def main() -> None:
    raise NotImplementedError("M4 offline pipeline")

if __name__ == "__main__":
    main()

PART B — m0_demo.py (RUN THIS TODAY)

This is fully self-contained — it generates its own panel/equation textures with Pillow at runtime (previewing the "baked PNG" idea), so you need no asset files. Walk with WASD, look with the mouse, left-click to colorize a wall panel or to shoot the demon, R to disintegrate the demon (reveals the blood-red ceiling equation), ESC to quit.

"""
m0_demo.py — Principia Descent, Milestone 0 walking demo.

A single textured room you can walk around. Demonstrates the CORE VERB:
  - left-click a black-and-white wall panel  -> it turns colourful ("on")
  - left-click the demon a few times          -> it disintegrates
  - on demon death, a blood-red equation appears on the ceiling

Controls:  WASD = move,  mouse = look,  left click = shoot,  ESC = quit.

This file is deliberately standalone and does NOT import the principia package;
it previews the look & feel while the real modules are built milestone by
milestone. Panel textures are drawn with Pillow at runtime to mimic the offline
"baked PNG" pipeline.
"""
from __future__ import annotations

import random
from PIL import Image, ImageDraw

from ursina import (
    Ursina, Entity, camera, color, mouse, raycast, held_keys,
    Text, Texture, destroy, application, time, Vec3, invoke,
)
from ursina.prefabs.first_person_controller import FirstPersonController

# --------------------------------------------------------------------- config
CEILING_H = 3.0
ROOM_W = 12.0
ROOM_D = 12.0
EYE = 1.6

app = Ursina(title="Principia Descent — M0 Walking Demo", borderless=False)
camera.fov = 75

# --------------------------------------------------------------- texture maker
def _hex(rgb_hex: str):
    rgb_hex = rgb_hex.lstrip("#")
    return tuple(int(rgb_hex[i:i + 2], 16) for i in (0, 2, 4))


def make_panel(title: str, on: bool) -> Texture:
    """Draw a placeholder proof-step panel. on=False -> grayscale ('off')."""
    S = 512
    img = Image.new("RGBA", (S, S), (248, 248, 244, 255))
    d = ImageDraw.Draw(img)

    abc = _hex("#0072B2") if on else (90, 90, 90)   # 'angle ABC' group (blue)
    bd = _hex("#D55E00") if on else (130, 130, 130)  # 'segment BD' group (orange)
    ink = (20, 20, 20)

    # frame
    d.rectangle([8, 8, S - 8, S - 8], outline=ink, width=4)
    # title bar
    d.rectangle([8, 8, S - 8, 64], fill=(230, 230, 224, 255))
    d.text((24, 26), title, fill=ink)

    # a little Newton-ish figure: triangle + inscribed arc
    A, B, C = (120, 420), (400, 420), (260, 160)
    d.line([A, B], fill=abc, width=6)          # base — group "abc" (badge ①)
    d.line([B, C], fill=ink, width=4)
    d.line([C, A], fill=ink, width=4)
    d.line([A, C[0], C[1]], fill=bd, width=6)  # (re-uses A) segment — group "bd" (badge ②)
    d.ellipse([235, 380, 285, 430], outline=bd, width=5)

    # redundant cues for colour-blind players (R1): numbered badges
    d.ellipse([90, 430, 118, 458], outline=abc, width=4); d.text((98, 437), "1", fill=abc)
    d.ellipse([250, 120, 278, 148], outline=bd, width=4); d.text((258, 127), "2", fill=bd)

    # a line of "text" referencing the same colours
    d.text((30, 470), "base AB = 1   |   apex C   |   arc 2", fill=ink)
    return Texture(img)


def make_equation(text: str) -> Texture:
    S = 512
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((40, S // 2 - 10), text, fill=(255, 255, 255, 255))
    return Texture(img)


def make_name_tile(text: str) -> Texture:
    S = 512
    img = Image.new("RGBA", (S, S), (15, 15, 20, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, S - 6, S - 6], outline=(120, 120, 140), width=6)
    d.text((S // 2 - 60, S // 2 - 10), text, fill=(220, 220, 235))
    return Texture(img)


# --------------------------------------------------------------------- room
# floor (walkable)
Entity(model="plane", scale=(ROOM_W, 1, ROOM_D), texture="white_cube",
       texture_scale=(ROOM_W, ROOM_D), color=color.rgb(60, 60, 70),
       collider="box", position=(0, 0, 0))

# big readable name tile in the centre of the floor
Entity(model="quad", texture=make_name_tile("LEMMA I"), rotation_x=90,
       scale=4, position=(0, 0.02, 0), double_sided=True)

# ceiling (low)
Entity(model="plane", scale=(ROOM_W, 1, ROOM_D), texture="white_cube",
       texture_scale=(ROOM_W, ROOM_D), color=color.rgb(30, 30, 36),
       position=(0, CEILING_H, 0), rotation=(180, 0, 0))

# four walls (thin boxes, with collision)
half_w, half_d = ROOM_W / 2, ROOM_D / 2
wall_kw = dict(model="cube", texture="brick", color=color.rgb(95, 80, 75),
               collider="box")
Entity(**wall_kw, scale=(ROOM_W, CEILING_H, 0.3), position=(0, CEILING_H / 2,  half_d))   # N
Entity(**wall_kw, scale=(ROOM_W, CEILING_H, 0.3), position=(0, CEILING_H / 2, -half_d))   # S
Entity(**wall_kw, scale=(0.3, CEILING_H, ROOM_D), position=( half_w, CEILING_H / 2, 0))   # E
Entity(**wall_kw, scale=(0.3, CEILING_H, ROOM_D), position=(-half_w, CEILING_H / 2, 0))   # W

# --------------------------------------------------------------- wall panels
panels = []


def add_panel(title, pos, rot):
    off_tex = make_panel(title, on=False)
    on_tex = make_panel(title, on=True)
    p = Entity(model="quad", texture=off_tex, scale=2.2,
               position=pos, rotation=rot, double_sided=True, collider="box")
    p.kind = "panel"
    p.is_on = False
    p.off_tex = off_tex
    p.on_tex = on_tex
    panels.append(p)
    return p


add_panel("STEP 1", (-2.4, 1.5,  half_d - 0.31), (0,   0, 0))   # N wall, left
add_panel("STEP 2", ( 2.4, 1.5,  half_d - 0.31), (0,   0, 0))   # N wall, right
add_panel("STEP 3", (-half_w + 0.31, 1.5, -2.4), (0,  90, 0))   # W wall
add_panel("QED",    ( half_w - 0.31, 1.5,  2.4), (0, -90, 0))   # E wall

# ------------------------------------------------------- ceiling equation (hidden)
equation = Entity(model="quad", texture=make_equation("q = m v"),
                  scale=3, position=(0, CEILING_H - 0.05, 3),
                  rotation=(90, 0, 0), double_sided=True,
                  color=color.rgb(180, 0, 0), enabled=False)

# ------------------------------------------------------------------- demon
demon_parts = []


def build_demon():
    demon_parts.clear()
    spec = [
        ((0, 0, 0),        0.6, "#FF7AB6"),  # body
        ((-0.2, 0.25, 0.5), 0.1, "#3B6BFF"),  # eye
        ((0.2, 0.25, 0.5),  0.1, "#3B6BFF"),  # eye
        ((0, -0.1, 0.55),   0.07, "#FFFFFF"),  # tooth
        ((-0.12, -0.1, 0.55), 0.06, "#FFFFFF"),
        ((0.12, -0.1, 0.55),  0.06, "#FFFFFF"),
    ]
    base = Vec3(6 - ROOM_W / 2, 1.2, 0)  # sit it off-centre in the room
    for off, r, hx in spec:
        part = Entity(model="sphere",
                      color=color.rgb(*_hex(hx)),
                      scale=r * 2,
                      position=base + Vec3(*off),
                      collider="sphere")
        part.kind = "demon"
        demon_parts.append(part)


build_demon()
demon_alive = {"hp": 3, "dead": False}


def disintegrate_demon():
    if demon_alive["dead"]:
        return
    demon_alive["dead"] = True
    for part in demon_parts:
        dir_ = Vec3(random.uniform(-1, 1), random.uniform(0.2, 1),
                    random.uniform(-1, 1)).normalized()
        part.animate_position(part.position + dir_ * 3, duration=0.6)
        part.animate_scale(0, duration=0.6)
        invoke(destroy, part, delay=0.65)
    demon_parts.clear()
    # the demonic algebra is released:
    equation.enabled = True
    equation.scale = 0.1
    equation.animate_scale(3, duration=0.5)


# ------------------------------------------------------------------- player
player = FirstPersonController(y=EYE, speed=4, position=(0, EYE, -4))
player.jump_height = 0          # no jumping (flat-world invariant)
player.cursor.visible = False

# crosshair (the girlfriend's reticle, conceptually)
Entity(parent=camera.ui, model="quad", scale=0.008,
       color=color.rgb(255, 60, 60), rotation_z=45)

hint = Text(
    "WASD move | mouse look | LEFT-CLICK = shoot | ESC = quit\n"
    "Shoot a panel to colour it. Shoot the demon to exorcise the room.",
    origin=(0, 0), y=-0.43, scale=0.7, color=color.azure,
)


def shoot():
    hit = raycast(camera.world_position, camera.forward,
                  distance=25, ignore=(player,))
    if not hit.hit:
        return
    e = hit.entity
    kind = getattr(e, "kind", None)
    if kind == "panel" and not e.is_on:
        e.texture = e.on_tex          # off -> on (sticky)
        e.is_on = True
    elif kind == "demon":
        demon_alive["hp"] -= 1
        for p in demon_parts:         # quick flash
            p.blink(color.white, duration=0.1)
        if demon_alive["hp"] <= 0:
            disintegrate_demon()


def input(key):
    if key == "escape":
        application.quit()
    if key == "left mouse down":
        shoot()
    if key == "r":                    # convenience: instant exorcism
        disintegrate_demon()


app.run()

✅ What you have now & how to use it

pip install -r requirements.txt
pytest -q                # fixture tests should pass (validates schema.py)
python m0_demo.py        # a window opens — walk, look, shoot to colorize

If Ursina complains about Panda3D on Windows, pip install --upgrade panda3d usually fixes it.

    Part A gives every future child a frozen target: implement one file against its signatures, nothing else. The fixture tests + schema_version checks are your early-warning system against the modules silently drifting apart across separate chats.
    Part B is a real, fun thing you can show a partner tonight — and it already demonstrates the soul of the game: walk up to a black-and-white proof step, shoot it, watch it bloom into color; exorcise the sphere-demon and the blood-red equation appears overhead.

Suggested next step (M1): I write the child prompt for assets/manager.py + content/loader.py (the first two real runtime modules), with the exact contract + fixture they must satisfy — so you can paste it straight into a fresh Opus child chat. Want me to generate that delegation prompt now? 🙂
