"""
contracts.py — THE single import surface for the QUAKE runtime engine.

Re-exports the canonical aliases + pydantic models from map/raw_models.py
(the build-world source of truth, already covered by 145+ green tests) and
defines the runtime-only types the engine needs. Engine modules import ONLY
from here; they never import map.raw_models directly.

Conventions (bedrock): pydantic v2, ConfigDict(extra="forbid"),
schema_version == "1.0", IDs are Annotated[str, Field(pattern=...)].
"""
from __future__ import annotations

from typing import Annotated, Literal, Protocol, Union, runtime_checkable
from dataclasses import dataclass, field

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# 1. RE-EXPORT THE CANONICAL TYPES FROM map/raw_models.py
# =============================================================================
# INTEGRATION: these names mirror the verbatim alias block + model list DeepSeek
# reported from map/raw_models.py. If any spelling differs in raw_models, fix the
# import list HERE ONLY (the facade absorbs it) — never in a child module.
from map.raw_models import (  # noqa: F401  (re-exported)
    # --- type aliases ---
    NodeId, LevelId, PageLabel, Vec2, Vec3, Hex, GroupName, LocalColor,
    FigureId, PairId, DrawBlockId, TextBlockId, EqId,
    # --- Leg 1 (MAP) models ---
    Floorplan, FloorRoom, Corridor, Crossing,
    ConceptGraph, Node, Edge,
    # --- Leg 2 (WALLS) models ---
    Palette, GroupColor,
    Manifest, AssetEntry,
    RoomSource, FigureDecl, StepPair, DrawingBlock, TextBlock, CeilingEq,
    # --- shared build config + room runtime (Leg 3) ---
    BuildConfig,
    RoomRuntime, DoorRT, PanelPairRT, PanelPlacementRT, EnemyRT, CeilingEqRT,
    # --- helpers ---
    load_json,
)

# Defensive star-import so a name we forgot to list above is still reachable
# from contracts. (Explicit list above is the documented surface; this is a net.)
from map.raw_models import *  # noqa: F401,F403

# =============================================================================
# 2. RUNTIME-ONLY TYPES (do NOT exist in raw_models; defined here once)
# =============================================================================

# --- ViewMatrix: a 4x4 float32 row-major numpy array (alias for documentation) ---
ViewMatrix = np.ndarray  # shape (4,4), dtype float32, ROW-MAJOR by engine convention


# --- A generic build/runtime report (used by gfx_context.check_caps, etc.) ------
@dataclass(frozen=True)
class Report:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# --- Co-op semantic actions (one snapshot per frame; produced by input_actions) -
# Frozen so game logic cannot mutate the input snapshot mid-step.
class Actions(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    # MOVER (owns the body) ---------------------------------------------------
    move_x: float = 0.0          # [-1,1] strafe (right +)
    move_y: float = 0.0          # [-1,1] forward (+) / back (-)
    heading_delta: float = 0.0   # radians this frame (yaw). MOVER ONLY.
    pitch_delta: float = 0.0     # radians this frame, pre-clamp. MOVER ONLY.
    # SHOOTER (owns the reticle) ---------------------------------------------
    aim_x: float = 0.0           # [-1,1] reticle x within cone
    aim_y: float = 0.0           # [-1,1] reticle y within cone
    fire: bool = False           # edge: true only on the frame fire is pressed
    fire_held: bool = False
    # SHARED ------------------------------------------------------------------
    read_toggle: bool = False    # edge
    interact: bool = False       # edge
    pause: bool = False          # edge


# --- Geometry / runtime helpers ------------------------------------------------
@dataclass(frozen=True)
class Ray:
    origin: Vec3
    direction: Vec3              # need not be unit; consumers normalize if required


@dataclass(frozen=True)
class PanelHit:
    asset_on_id: str
    asset_off_id: str
    pair_id: PairId
    is_drawing: bool
    distance: float


# --- Events emitted by gameplay.step (typed, discriminated on `event`) ----------
class _Ev(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PanelLit(_Ev):
    event: Literal["panel_lit"] = "panel_lit"
    pair_id: PairId
    room_id: NodeId


class DoorOpened(_Ev):
    event: Literal["door_opened"] = "door_opened"
    room_id: NodeId


class DemonSpawned(_Ev):
    event: Literal["demon_spawned"] = "demon_spawned"
    enemy_id: str
    room_id: NodeId


class DemonHit(_Ev):
    event: Literal["demon_hit"] = "demon_hit"
    enemy_id: str
    hp_remaining: int


class DemonKilled(_Ev):
    event: Literal["demon_killed"] = "demon_killed"
    enemy_id: str
    room_id: NodeId


class RoomCleared(_Ev):
    event: Literal["room_cleared"] = "room_cleared"
    room_id: NodeId


class LevelComplete(_Ev):
    event: Literal["level_complete"] = "level_complete"
    level_id: LevelId


class ModeSwitch(_Ev):
    # Apocrypha §3 supersedes Second Canon §5.1: via_edge_id is carried.
    event: Literal["mode_switch"] = "mode_switch"
    to: Literal["corridor", "room"]
    room_id: NodeId | None = None
    via_edge_id: str | None = None


class ReadModeToggled(_Ev):
    event: Literal["read_toggled"] = "read_toggled"
    on: bool
    asset_id: str | None = None


class GuidelinesRecomputed(_Ev):
    event: Literal["guides"] = "guides"
    targets: list[NodeId] = Field(default_factory=list)


Event = Annotated[
    Union[
        PanelLit, DoorOpened, DemonSpawned, DemonHit, DemonKilled,
        RoomCleared, LevelComplete, ModeSwitch, ReadModeToggled,
        GuidelinesRecomputed,
    ],
    Field(discriminator="event"),
]


# --- Savegame (disk; written by state.save, atomic; Second Canon §4.7) ----------
class RoomProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pairs_on: list[PairId] = Field(default_factory=list)
    hidden_door_open: bool = False
    enemy_defeated: bool = False
    room_cleared: bool = False


class LevelProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rooms: dict[NodeId, RoomProgress] = Field(default_factory=dict)
    level_complete: bool = False


class PlayerSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    level_id: LevelId
    mode: Literal["corridor", "room"]
    current_room_id: NodeId | None = None
    position_xyz: Vec3
    heading_rad: float
    # NOTE: pitch is runtime-only and intentionally NOT persisted.


class SaveGame(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["1.0"] = "1.0"
    profile_id: str = "default"
    levels: dict[LevelId, LevelProgress] = Field(default_factory=dict)
    player: PlayerSave


# --- GameState (in-memory runtime state; NOT a pydantic model — mutable) --------
@dataclass
class GameState:
    save: SaveGame
    mode: Literal["corridor", "room"]
    current_room_id: NodeId | None
    pos: Vec3
    heading_rad: float
    pitch_rad: float
    lit: set[str]                 # block_ids turned on (mirrors save)
    cleared: set[NodeId]


# --- Pack (everything the runtime loads; assembled by assets.load_pack) ---------
@dataclass
class Pack:
    floorplan: Floorplan
    rooms: dict[NodeId, RoomRuntime]
    manifest: Manifest
    palette: Palette
    asset_dir: str
    room_names: dict[str, str] = field(default_factory=dict)


# --- NavQuery protocol (implemented by nav_collision builders) ------------------
@runtime_checkable
class NavQuery(Protocol):
    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3: ...
    def nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None: ...
    def door_at(self, point: Vec3) -> str | None: ...   # edge_id or None (room nav)


# =============================================================================
# 3. RUNTIME CONSTANTS that are part of the locked contract (shared by modules)
# =============================================================================
# Read-Mode target rule (Second Canon §5.3 commentary, LOCKED):
READ_MAX_DIST: float = 6.0              # metres
READ_CONE_HALF_ANGLE_RAD: float = 0.6108652  # 35 degrees in radians

# Shared comfort/camera clamp (camera.py and gameplay.py both reference this):
PITCH_CLAMP_RAD: float = 1.2217         # +/-70 degrees


__all__ = [
    # re-exported aliases
    "NodeId", "LevelId", "PageLabel", "Vec2", "Vec3", "Hex", "GroupName", "LocalColor",
    "FigureId", "PairId", "DrawBlockId", "TextBlockId", "EqId",
    # re-exported models
    "Floorplan", "FloorRoom", "Corridor", "Crossing",
    "ConceptGraph", "Node", "Edge",
    "Palette", "GroupColor", "Manifest", "AssetEntry",
    "RoomSource", "FigureDecl", "StepPair", "DrawingBlock", "TextBlock", "CeilingEq",
    "BuildConfig",
    "RoomRuntime", "DoorRT", "PanelPairRT", "PanelPlacementRT", "EnemyRT", "CeilingEqRT",
    "load_json",
    # engine-only types
    "ViewMatrix", "Report", "Actions", "Ray", "PanelHit",
    "PanelLit", "DoorOpened", "DemonSpawned", "DemonHit", "DemonKilled",
    "RoomCleared", "LevelComplete", "ModeSwitch", "ReadModeToggled",
    "GuidelinesRecomputed", "Event",
    "RoomProgress", "LevelProgress", "PlayerSave", "SaveGame",
    "GameState", "Pack", "NavQuery",
    # locked constants
    "READ_MAX_DIST", "READ_CONE_HALF_ANGLE_RAD", "PITCH_CLAMP_RAD",
]
