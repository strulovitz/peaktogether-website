# QUAKE — PARENT 4 FROZEN CHILD BRIEFS: THE RUNTIME ENGINE (M0–M7)

Architect: Claude Opus 4.8 (Parent 4). Status: FROZEN. Scope: the runtime engine that reads only baked JSON+PNG.

---

## RESOLUTIONS (decided by me, Parent 4, in favor of long-term quality)

**Conflict #1 — ModeSwitch.** The Apocrypha §3 is the latest scripture and it already settles this: ModeSwitch carries via_edge_id: str | None. The Apocrypha is dated identically but is the final batch and explicitly amends the Second Canon (§10 changelog: "Events: ModeSwitch.via_edge_id retained"). DECIDED: ModeSwitch(event, to, room_id, via_edge_id). The §5.1 three-field version is superseded.

**Conflict #3 — junction detection / GuidelinesRecomputed.** DECIDED: gameplay.step owns it (it holds nav, pos, dt, and emits all events). It emits GuidelinesRecomputed on (a) RoomCleared, or (b) corridor junction-crossing detected via nav. guidelines.select_targets stays a pure function; app.py calls it when it sees that event.

**Pin #1 — type aliases.** Now corrected: the canonical aliases live in quake/map/raw_models.py and are re-exported through the new contracts.py (PART 1.5). Children `from contracts import ...` only.

**Pin #4 — Mode A labels.** DECIDED: Pack does NOT gain ConceptGraph. Mode A v1 draws node rings from Floorplan only. No text labels in M1; labels are post-M7 polish via a future labels.json.

**Pin #6 — angular-nudge tolerance.** door_nudge_max_angle_rad = 0.18 (~10.3°) — build-side, in BuildConfig. Engine just reads baked DoorRT.

The unified-compass call, runtime-only pitch, and ceiling-hidden-until-cleared decisions stand as frozen in the briefs.

---

## PART 0 — UNIVERSAL PREAMBLE (paste at the top of EVERY child brief)

You are implementing exactly ONE single-file module for the QUAKE runtime engine.

ABSOLUTE RULES:
1. Import every shared type from contracts.py (it re-exports the canonical models
   from map/raw_models.py and defines the engine-only types — see PART 1.5).
   NEVER redefine Actions, Event, ViewMatrix, NavQuery, PanelHit, Ray, GameState,
   Pack, Floorplan, RoomRuntime, DoorRT, PanelPairRT, PanelPlacementRT, Manifest,
   AssetEntry, SaveGame, BuildConfig, Vec2, Vec3, Hex, NodeId, PairId, etc. They
   exist in contracts.py. Import them. NEVER import map.raw_models directly.
2. Do NOT import any other engine module's internals. Talk only through the frozen
   signatures in this brief.
3. Every JSON you load: use contracts.load_json(path, Model) (it asserts
   schema_version == "1.0"), or assert obj.schema_version == "1.0" yourself.
4. SPLIT YOUR MODULE: a PURE core (plain functions on numbers/arrays/dataclasses,
   zero pyglet, zero moderngl, zero file/window) and a THIN shell (the GL/window/IO).
   The pure core is fully unit-tested. The shell is guarded so it imports and runs
   headless without a GL context (skip the draw, never crash on import).
5. NEVER assert a moderngl/pyglet/GLSL API name as fact. Where you call an external
   API you are unsure of, isolate it behind one tiny wrapper function with a comment
   "INTEGRATION: confirm exact API", so DeepSeek's compile loop fixes it in one place.
6. COORDINATES ARE LAW: floorplan is the XZ map-plane, Y is up. Room-local axes are
   PARALLEL to map axes (global compass, NO rotation). Walls: N at z=+D/2 (inward
   normal -Z), S at z=-D/2 (+Z), E at x=+W/2 (-X), W at x=-W/2 (+X), floor y=0.
   Door direction is literal: a corridor at map-bearing θ has its door at room-local
   direction θ. NEVER rotate room-local space.
7. Math/matrix convention: ViewMatrix is np.ndarray shape (4,4), float32, ROW-MAJOR.
   When you hand it to GL, transpose at the boundary if the GL call wants column-major
   (INTEGRATION: confirm). Keep all your math row-major internally.
8. Provide the exact test names listed. GPU/window tests use the marker
   @skip_if_no_gl (provided by conftest.py — see PART 1.5; skips when no context).

The three infrastructure files referenced above (contracts.py, glguard.py, conftest.py) are defined fully in PART 1.5 and MUST exist on disk before any child is spun.

---

## PART 1 — DEPENDENCY-SORTED BUILD ORDER (the spine)

Build strictly in this order. Each milestone is independently runnable (OT §13).

```
M-1 (INFRASTRUCTURE — before any child; full files in PART 1.5):
      0. contracts.py        (re-exports map/raw_models + ALL engine-only types)
         glguard.py          (HAVE_GL probe; never crashes on import)
         conftest.py         (skip_if_no_gl marker)

M0  (prove the GPU path is ours):
      1. gfx_context.py      (window + GL context + GPU capability check)
      2. shaders.py          (wire/solid/blit programs + ceiling tint uniform)
      3. app.py  [M0 stub]   (one shaded triangle + one wireframe line; depth on, blend off)

M1  (walk a wireframe graph, comfortable):
      4. camera.py           (decoupled, damped, pitch-clamped ViewMatrix)
      5. input_actions.py    (semantic two-player actions; edge detection)
      6. render_wire.py       (Mode A: no-blend depth, distance-dim, line-quads, bloom)
      7. guidelines.py       (target selection §8.2 + guide-line draw)
      8. nav_collision.py    (corridor nav first; room nav + door_at added at M6)
      [app.py grows: Mode A loop]

M6  (enter a real room, read a panel):
      9. assets.py           (load baked JSON+PNG into Pack)
     10. render_room.py      (Mode B: walls-with-holes at bearings, panels, alcove, ceiling)
     11. readmode.py         (master-DPI pin-sharp Read Mode)
      [nav_collision.py grows: build_room_nav + door_at]
      [app.py grows: Mode B + Read + teleport-snap switch]

M7  (full loop, persisted, co-op):
     12. state.py            (new/load/save, atomic)
     13. gameplay.py         (step: shoot→flip→door→demon→clear→ceiling; god-mode; ModeSwitch)
      [app.py final: full wiring per §5.4]
```

Rationale for the order: the three infrastructure files (step 0) are the import foundation every child depends on — nothing compiles without them. gfx_context+shaders prove ownership of the pipeline before any content (M0 front-loaded per §8). camera+input are pure-math and unblock everything. render_wire needs only Floorplan (already built) → M1 is reachable with zero room work. Rooms (assets→render_room→readmode) form M6. state+gameplay close the loop at M7. nav_collision and app.py grow across milestones (noted inline).

---

## PART 1.5 — INFRASTRUCTURE (contracts.py + glguard.py + conftest.py)

These three files are step 0 of the build order. They do not implement engine behavior — they are the import foundation. DeepSeek creates them verbatim before spinning any child.

### Why contracts.py is a facade, not a rewrite

The canonical aliases and pydantic models already exist in quake/map/raw_models.py (516 lines; the 145+ green build-leg tests import from it). The runtime engine must (a) reuse those exact models — re-defining them would risk silent contract drift, the #1 failure mode (Iron Rule #2) — and (b) add the runtime-only types the 13 briefs need (Actions, the Event union, Ray, PanelHit, NavQuery, GameState, SaveGame, Pack, ViewMatrix, Report). So contracts.py re-exports everything from raw_models and defines the engine-only types in one place. Every child imports only from contracts, so the build/runtime boundary stays clean and there is a single source of truth.

### File: quake/contracts.py

```python
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
    NodeId, LevelId, PageLabel, Vec2, Vec3, Hex, GroupName,
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
    "NodeId", "LevelId", "PageLabel", "Vec2", "Vec3", "Hex", "GroupName",
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
```

### File: quake/glguard.py

```python
"""
glguard.py — headless-safe probe for whether a real GL context can be made.

Engine render/window shells check `if not glguard.HAVE_GL: return` at the top of
any draw/context call so that:
  * importing any engine module on a headless CI machine never crashes, and
  * the smoke launch degrades gracefully instead of throwing.

This module performs the probe ONCE at import, swallowing every failure. It must
never raise on import.
"""
from __future__ import annotations


def _probe() -> bool:
    """Return True iff a moderngl context can be created right now.

    INTEGRATION: confirm the exact pyglet 2.1.x hidden-window + moderngl
    create_context incantation. The structure (try/except → bool) is fixed;
    only the two external calls inside may need their exact names confirmed.
    """
    try:
        import moderngl  # noqa: WPS433 (local import is intentional)
        # Preferred: a standalone context needs no visible window.
        # INTEGRATION: moderngl.create_context(standalone=True, require=330)
        ctx = moderngl.create_standalone_context(require=330)
        ok = ctx is not None
        try:
            ctx.release()
        except Exception:
            pass
        return ok
    except Exception:
        # Fall back to a hidden pyglet window + attached context.
        try:
            import pyglet  # noqa: WPS433
            import moderngl  # noqa: WPS433
            # INTEGRATION: confirm pyglet 2.1.x Window(visible=False) and that
            # moderngl.create_context() binds to the current pyglet GL context.
            win = pyglet.window.Window(width=8, height=8, visible=False)
            ctx = moderngl.create_context()
            ok = ctx is not None
            try:
                win.close()
            except Exception:
                pass
            return ok
        except Exception:
            return False


# Probe exactly once at import; never raise.
try:
    HAVE_GL: bool = _probe()
except Exception:  # pragma: no cover - belt and suspenders
    HAVE_GL = False
```

### File: quake/conftest.py

```python
"""
conftest.py — pytest configuration shared by the whole QUAKE test suite.

Provides the `skip_if_no_gl` marker used by every GPU/window test. Pure-core
tests never use it and always run in headless CI.

Usage in a test module:
    from conftest import skip_if_no_gl   # or rely on pytest collecting it

    @skip_if_no_gl
    def test_programs_compile(...):
        ...
"""
from __future__ import annotations

import pytest

try:
    from glguard import HAVE_GL
except Exception:  # if even importing glguard fails, treat as no-GL
    HAVE_GL = False

# A ready-to-use decorator: @skip_if_no_gl
skip_if_no_gl = pytest.mark.skipif(
    not HAVE_GL,
    reason="No GL context available (headless); skipping GPU/window test.",
)


def pytest_configure(config: "pytest.Config") -> None:
    """Register the marker name so `-W error::pytest.PytestUnknownMarkWarning`
    stays clean and `pytest --markers` documents it."""
    config.addinivalue_line(
        "markers",
        "skip_if_no_gl: skip when no GL context can be created (headless CI).",
    )
```

---

## PART 2 — THE CHILD BRIEFS

Below, each brief is self-contained: signature (verbatim from the scriptures), the pure/shell split, the exact behavior, and the exact test list. Paste Part 0 + the relevant brief into each fresh child chat.

---

### BRIEF 1 — gfx_context.py (M0)

FROZEN SIGNATURE (Second Canon §5.3):
```python
def make_window(width: int, height: int, title: str): ...   # returns (window, gl_context)
```

PURPOSE: own our window + GL context; perform the OT §11.4 GPU capability check.

PURE CORE (testable headless):
```python
def check_caps(gl_version: tuple[int,int], max_texture_size: int, has_fbo: bool) -> Report:
    # Report from contracts (ok, errors, warnings).
    # FAIL if gl_version < (3,3); FAIL if not has_fbo;
    # WARN if max_texture_size < 4096 (our master-DPI panels may exceed it);
    # FAIL if max_texture_size < 2048.
    # Pure: caller passes the queried numbers; this just judges them.
```

SHELL (skips/handled headless):
```
make_window(width, height, title) -> (window, gl_context):
  1. Create a pyglet window (INTEGRATION: confirm pyglet 2.1.x Window args:
     width, height, caption, resizable, vsync). May bootstrap via moderngl-window
     for M0 ONLY, then we own it.
  2. Create the moderngl context (INTEGRATION: moderngl.create_context()).
  3. Query GL_VERSION major/minor, GL_MAX_TEXTURE_SIZE, FBO support
     (INTEGRATION: confirm moderngl context.info keys).
  4. report = check_caps(...); if not report.ok: show a PLAIN error window with
     report.errors joined, then exit(1). (INTEGRATION: simplest pyglet label or
     OS messagebox; a printed error + exit is an acceptable fallback.)
  5. Set GL state ONCE here: depth test ENABLED, depth func LEQUAL, depth write ON,
     BLEND DISABLED. (This is the Mode-A invariant; Mode B re-enables what it needs
     locally and restores.)  (INTEGRATION: ctx.enable(moderngl.DEPTH_TEST);
     ctx.depth_func = '<='; ctx.disable(moderngl.BLEND).)
  6. return (window, ctx).

If glguard.HAVE_GL is False, make_window must raise a clear RuntimeError
(it genuinely cannot run headless) — but check_caps and the module IMPORT
must work with no context.
```

TESTS:
```
test_caps_rejects_gl32         — (3,2) → ok False, error mentions OpenGL 3.3.
test_caps_rejects_no_fbo       — has_fbo False → ok False.
test_caps_warns_small_texture  — max_texture_size 3000 → ok True, one warning.
test_caps_fails_tiny_texture   — max_texture_size 1024 → ok False.
test_caps_accepts_good         — (3,3),8192,True → ok True, no errors.
@skip_if_no_gl test_make_window_smoke — make_window(320,240,"t") returns a
    2-tuple; context is not None.
```

---

### BRIEF 2 — shaders.py (M0)

FROZEN SIGNATURES (Second Canon §5.3):
```python
def wire_program(ctx): ...
def solid_program(ctx): ...
def blit_program(ctx): ...
def ceiling_tint_uniform(prog, red: float) -> None: ...
```

PURPOSE: author OUR GLSL and compile the three programs. You write the GLSL (locked
decision: we control the pipeline). All programs target GLSL 330 core.

You write three vertex/fragment program pairs. Define the GLSL as Python string
constants at module top so they are inspectable in tests without a GL context.

PROGRAM CONTRACTS (uniforms/attributes — these names are OUR convention, frozen here
so render_wire/render_room/readmode bind against them):

```
wire_program  — Mode A lines as camera-facing quads.
  uniforms:  u_mvp (mat4), u_dim_near (float), u_dim_far (float),
             u_color (vec3), u_depth_bias (float), u_viewport (vec2)
  in:        in_pos (vec3, line endpoint in world), in_side (vec2, quad expansion),
             in_color (vec3, per-vertex importance color)
  behavior:  expand line into a screen-facing quad of constant pixel width
             (INTEGRATION: pass viewport size as u_viewport vec2; expand in clip
             space); fragment color = mix(in_color, dark_grey, distance_factor)
             where distance_factor ramps view-space depth between u_dim_near and
             u_dim_far. NEVER output pure black: clamp the dim floor to dark grey
             (e.g. vec3(0.12)). Apply u_depth_bias to gl_Position.z to kill
             thin-line dropout at crossings.

solid_program — Mode B textured panels/walls.
  uniforms:  u_mvp (mat4), u_tex (sampler2D), u_tint (vec3),
             u_use_tint (int, 0/1)
  in:        in_pos (vec3), in_uv (vec2)
  behavior:  sample u_tex; if u_use_tint==1 multiply rgb by u_tint (ceiling blood-red
             post-kill); respect texture alpha (panels are transparent-keyed PNGs).
             (Mode B enables alpha blend locally for panels; walls are opaque.)

blit_program  — fullscreen textured quad (Read Mode + bloom composite).
  uniforms:  u_tex (sampler2D), u_zoom (float), u_pan (vec2)
  in:        in_pos (vec2 NDC), in_uv (vec2)
  behavior:  uv' = (in_uv - 0.5)/u_zoom + 0.5 + u_pan; sample; pass through.

ceiling_tint_uniform(prog, red):
   sets prog's u_tint = (red, 0.0, 0.0)  -> pure blood-red scaled by `red`
   and u_use_tint = 1 if red>0 else 0.
   (INTEGRATION: prog['u_tint'].value = (...); prog['u_use_tint'].value = ...)
   Uses tint_rgb() for the rgb triple.
```

PURE CORE (testable headless):
```
The GLSL source strings are module constants; expose:
  WIRE_VS, WIRE_FS, SOLID_VS, SOLID_FS, BLIT_VS, BLIT_FS  (str)
def tint_rgb(red: float) -> tuple[float,float,float]:  return (clamp01(red),0.0,0.0)
(ceiling_tint_uniform uses tint_rgb; tint_rgb is unit-tested.)
```

SHELL: wire_program/solid_program/blit_program compile via ctx.program(...)
    (INTEGRATION: confirm moderngl ctx.program(vertex_shader=…, fragment_shader=…)).
    Skip compile if not HAVE_GL.

TESTS:
```
test_glsl_constants_present    — all six *_VS/*_FS are non-empty str containing
                                 "#version 330".
test_tint_rgb_blood_red        — tint_rgb(1.0)==(1.0,0.0,0.0); tint_rgb(0.5)[0]==0.5;
                                 green/blue always 0.
test_tint_rgb_clamps           — tint_rgb(2.0)[0]==1.0; tint_rgb(-1)[0]==0.0.
@skip_if_no_gl test_programs_compile — wire/solid/blit_program(ctx) each return a
                                 program object (compiles cleanly).
```

---

### BRIEF 3 — camera.py (M1) — PURE, the comfort core

FROZEN SIGNATURE (Second Canon §5.3):
```python
class Camera:
    def update(self, heading_rad: float, pitch_rad: float, pos: Vec3, dt: float) -> ViewMatrix: ...
```

PURPOSE: the decoupled, critically-damped, pitch-clamped camera. This module is the
heart of co-op comfort (OT §10.2, R7). It is ENTIRELY PURE MATH — no GL, no window.
It must be fully unit-tested.

LOCKED COMFORT INVARIANTS (encode them here):
- Only the Mover's heading drives yaw. The Shooter NEVER appears in this signature.
  (Structurally impossible for aiming to rotate the camera — there is no aim input.)
- The camera FOLLOWS heading with a CRITICALLY-DAMPED spring (no overshoot).
- Pitch is CLAMPED then smoothed.

PINNED CONSTANTS (module-level):
```
CAM_HEADING_OMEGA   = 12.0    # spring natural frequency (rad/s); critically damped
CAM_PITCH_OMEGA     = 14.0
EYE_HEIGHT_M        = 1.6     # camera Y offset above pos.y (pos is feet/floor)
# PITCH_CLAMP_RAD is imported from contracts (== 1.2217, +/-70 deg) — single source.
```

BEHAVIOR:
```
Internal smoothed state: _yaw, _yaw_vel, _pitch, _pitch_vel (init to first target).
Each update:
  target_yaw   = heading_rad
  target_pitch = clamp(pitch_rad, -PITCH_CLAMP_RAD, +PITCH_CLAMP_RAD)
  Critically-damped spring step (semi-implicit, stable for any dt):
    for (val, vel, target, omega):
      a   = omega*omega*(target-val) - 2*omega*vel
      vel += a*dt
      val += vel*dt
  Shortest-arc for yaw: wrap (target_yaw - _yaw) into [-pi, pi] before the spring
  so it never spins the long way around.
  eye = (pos.x, pos.y + EYE_HEIGHT_M, pos.z)
  forward = ( cos(_pitch)*cos(_yaw), sin(_pitch), cos(_pitch)*sin(_yaw) )
    FROZEN COMPASS: a heading/bearing of θ → world forward (cos θ, 0, sin θ),
    with +X = east, +Z = north, matching bearing_rad = atan2(dz, dx). This single
    definition makes Mode A, doors (bearing), spawn (bearing+π), and the camera
    agree by construction.
  Build a right-handed look-at view matrix (eye, eye+forward, up=+Y).
  Return as np.ndarray (4,4) float32 ROW-MAJOR.
```

TESTS (all pure, no GL):
```
test_pitch_clamped         — feed pitch=10 rad; after many steps _pitch never
                             exceeds PITCH_CLAMP_RAD+epsilon.
test_heading_converges     — constant heading target; after ~1s of dt=1/60 steps,
                             _yaw within 1e-3 of target.
test_no_overshoot          — step heading from 0 to 1.0 rad; _yaw is monotonic
                             (never exceeds target) — critical damping.
test_yaw_shortest_arc      — heading target 3.0 rad while _yaw≈-3.0; it moves
                             through ±pi (delta wrapped), not the long way.
test_forward_compass       — yaw=0,pitch=0 → forward≈(1,0,0) (east = +X, bearing 0);
                             yaw=pi/2 → forward≈(0,0,1) (north=+Z).
test_matrix_shape_dtype    — update returns (4,4) float32.
test_deterministic         — same inputs from fresh Camera → identical matrices.
```

---

### BRIEF 4 — input_actions.py (M1, completed M4-feel)

FROZEN SIGNATURE (Second Canon §5.3):
```python
def poll(window, bindings) -> Actions: ...   # device-agnostic; two-player split
```

PURPOSE: the semantic action layer (OT §10.4). Raw device events NEVER leak past this
module. Produces one Actions snapshot per frame for BOTH players folded into one struct
(Actions already carries Mover fields + Shooter fields).

LOCKED: heading_delta/pitch_delta are MOVER-only; aim_x/aim_y are SHOOTER-only; the
Shooter has NO yaw/pitch authority (enforced by simply never writing heading/pitch from
shooter inputs). Edge fields (fire, read_toggle, interact, pause) are TRUE for exactly
one frame on the press transition.

PURE CORE (testable headless — this is most of the module):
```python
@dataclass
class RawSample:   # what the shell extracts from devices this frame
    # mover
    mover_axis_x: float; mover_axis_y: float
    mover_yaw_rate: float; mover_pitch_rate: float
    # shooter
    shooter_aim_x: float; shooter_aim_y: float
    shooter_fire_down: bool
    # shared buttons (current down-state, level not edge)
    read_down: bool; interact_down: bool; pause_down: bool

class EdgeTracker:
    # holds previous down-states; .edges(sample) -> dict of bool edges
    # fire/read/interact/pause become True only on False->True transition.

def build_actions(sample: RawSample, prev: EdgeTracker, dt: float,
                  cfg_yaw_sens: float, cfg_pitch_sens: float) -> Actions:
    # heading_delta = sample.mover_yaw_rate * cfg_yaw_sens * dt
    # pitch_delta   = sample.mover_pitch_rate * cfg_pitch_sens * dt
    # aim_x/aim_y   = clamp(shooter_aim_*, -1, 1)
    # move_x/move_y = clamp(mover_axis_*, -1, 1)
    # fire = edge(shooter_fire_down); fire_held = shooter_fire_down
    # read_toggle/interact/pause = edge(...)
    # returns a frozen Actions (contracts.Actions, frozen pydantic model).
```

PINNED CONSTANTS:
```
DEFAULT_YAW_SENS   = 2.2   # rad/s per unit input
DEFAULT_PITCH_SENS = 1.8
```

SHELL:
```
poll(window, bindings) -> Actions:
  Read pyglet keyboard/mouse + controllers via `bindings` (a dict mapping semantic
  names to device sources). Assemble a RawSample. (INTEGRATION: confirm pyglet
  keyboard state handler, mouse dx/dy, and controller axis reads for 2.1.x.)
  Maintain a module-level/owned EdgeTracker + dt clock. Call build_actions. Return.
  If not HAVE_GL/window: poll is not called in CI; build_actions is the tested path.

`bindings` shape (OUR convention, frozen): a dict with keys
  "mover": {device, axis_x, axis_y, yaw, pitch}, "shooter": {device, aim_x, aim_y,
  fire}, "shared": {read, interact, pause}. Default keyboard+mouse binding provided
  as DEFAULT_BINDINGS. Two players = two device entries; one player = same device,
  shooter aim on mouse, mover on WASD (a documented default).
```

TESTS (pure):
```
test_edge_fire_once        — fire_down goes F,T,T,F,T → fire edges True,False,
                             False,...,True; fire_held mirrors down-state.
test_edges_independent     — read/interact/pause edge independently.
test_mover_owns_rotation   — build_actions writes heading/pitch ONLY from mover_*;
                             set shooter aim huge → heading_delta/pitch_delta==0
                             when mover rates are 0.
test_aim_clamped           — shooter_aim_x=5 → aim_x==1.0.
test_scaling               — heading_delta == yaw_rate*sens*dt exactly.
test_actions_frozen        — returned Actions is frozen (assignment raises).
```

---

### BRIEF 5 — render_wire.py (M1) — Mode A

FROZEN SIGNATURE (Second Canon §5.3):
```python
def draw_graph(view: ViewMatrix, fp: Floorplan, state: GameState) -> None: ...
```

PURPOSE: Mode A wireframe corridor renderer. Reads ONLY Floorplan (+ state for the
"current section" dimming reference). Lines + node rings, depth-tested, NO BLEND,
distance-dimming white→dark-grey (NEVER black), crossings as TRUE 3D over/under,
camera-facing line-quads + depth bias (R9), screen-space bloom (NOT real blending).

GEOMETRY (PURE CORE — fully testable headless):
```
Build a renderable mesh from Floorplan:
  - For each Corridor: a polyline through path_xz, each vertex at y=cruise_y
    (ramp knees already in path_xz). PIN: corridors use neutral wire color
    WIRE_BASE=(1,1,1); node rings use their FloorRoom.map_color.
  - For each FloorRoom: a ring (circle) of map_radius_m in the XZ plane at
    y=socket_y, color = map_color.
  - Crossings render naturally because corridors carry their cruise_y and ramp
    knees; over_y>under_y guarantees visible separation. No special case needed
    in geometry — just honor the y values from the data.

def build_wire_mesh(fp: Floorplan) -> WireMesh:
    # WireMesh = dataclass(line_segments: np.ndarray (N,2,3) float32,
    #                      seg_colors: np.ndarray (N,3) float32,
    #                      ring_segments: np.ndarray (M,2,3), ring_colors (M,3))
    # Pure: deterministic, no GL. Rings tessellated to RING_SEGMENTS=48 chords.
    # Each line segment will be expanded to a camera-facing quad IN THE SHADER.

def hex_to_rgb(h: Hex) -> tuple[float,float,float]:  # "#rrggbb" -> 0..1 floats
```

PINNED CONSTANTS:
```
WIRE_BASE        = (1.0, 1.0, 1.0)
DIM_NEAR_M       = 6.0
DIM_FAR_M        = 90.0
DIM_FLOOR_GREY   = 0.12     # never-black horizon (R8)
WIRE_PX_WIDTH    = 2.5      # constant on-screen line width
DEPTH_BIAS       = 1e-4
RING_SEGMENTS    = 48
BLOOM_THRESHOLD  = 0.6
BLOOM_STRENGTH   = 0.5
```

SHELL (skips headless):
```
draw_graph(view, fp, state):
  if not HAVE_GL: return
  Lazily build+cache the WireMesh and its GL buffers for this fp (cache by id(fp)
  or fp.level_id). Upload line endpoints + the per-vertex 'side' expansion attribute
  (each segment → 2 triangles; emit the 4 corners with in_side in {-1,+1}).
  Bind wire_program; set u_mvp=view (TRANSPOSE at boundary if needed — INTEGRATION),
  u_dim_near=DIM_NEAR_M, u_dim_far=DIM_FAR_M, u_depth_bias=DEPTH_BIAS,
  u_viewport=(w,h). Draw segments then rings.
  Then run the screen-space bloom post-pass using blit_program twice (bright-extract
  threshold BLOOM_THRESHOLD, separable blur, additive composite). Bloom is a POST
  effect on the rendered color buffer; it is NOT alpha blending of the wires.
  (INTEGRATION: FBO ping-pong with moderngl framebuffers.)

DEPTH/BLEND STATE: depth test on, LEQUAL, write on, BLEND OFF (set in gfx_context;
do not change it here — Mode A is the no-blend mode).
```

TESTS (pure):
```
test_mesh_segment_count    — golden floorplan (2 rooms, 1 corridor of 3 pts) →
                             line_segments has exactly 2 segments (3-pt polyline).
test_ring_tessellation     — one room → ring_segments == RING_SEGMENTS.
test_ring_radius           — ring vertices lie at map_radius_m from room center
                             in XZ at y=socket_y (within 1e-4).
test_crossing_heights      — a floorplan with two corridors at cruise_y 0 and 4.5
                             → their segment y-values differ (over/under preserved).
test_hex_to_rgb            — "#ffffff"->(1,1,1); "#000000"->(0,0,0); "#ff8000"≈
                             (1,0.5,0).
test_deterministic_mesh    — build_wire_mesh twice → identical arrays.
@skip_if_no_gl test_draw_smoke — with a context + golden fp, draw_graph runs without
                             error (no assertion on pixels).
```

---

### BRIEF 6 — guidelines.py (M1/M3)

FROZEN SIGNATURES (Second Canon §5.3):
```python
def select_targets(fp: Floorplan, current: NodeId, cleared: set[NodeId], cfg: BuildConfig) -> list[NodeId]: ...
def draw_guidelines(view: ViewMatrix, fp: Floorplan, targets: list[NodeId]) -> None: ...
```

PURPOSE: choose ≤3 guide-line destinations (OT §8.2) and draw the Half-Life floor
guide-lines with arrowheads. select_targets is PURE and the comfort/navigation core.

SELECTION (PURE CORE — exact, flicker-free, OT §8.2):
```
Inputs: fp gives rooms (importance, map_xz) + corridors (graph edges).
Build an undirected graph from corridors. Compute graph_dist (BFS hop count) from
`current` to every uncleared room (room_id not in cleared, != current).
candidates = uncleared reachable rooms.
Slot 1 (always): min graph_dist; tie → lowest room_id. (nearest honored.)
Slots 2–3: from the remaining candidates, by descending
    score(r) = cfg.guide_w_imp * norm_imp(r) + cfg.guide_w_dist * norm_near(r)
  where norm_imp = (importance-1)/4,
        norm_near = 1 - (graph_dist-min_d)/(max_d-min_d)  (1.0 if max_d==min_d),
  tie → higher importance, then smaller graph_dist, then lower room_id.
Return up to cfg.guide_max_lines (=3) ids total (slot1 + up to 2 more). Fewer
candidates → fewer ids. NEVER invent ids.

HYSTERESIS is enforced by the CALLER (gameplay emits GuidelinesRecomputed only on
junction-cross or room-clear; app calls select_targets only then). select_targets
itself is pure/stateless and always returns the current best set.

def select_targets(...) -> list[NodeId]   # as above
# helper (exposed for tests):
def _graph_distances(fp, current) -> dict[NodeId,int]
```

PINNED: uses cfg.guide_w_imp(0.6), cfg.guide_w_dist(0.4), cfg.guide_max_lines(3) from
BuildConfig — DO NOT hardcode; read cfg.

DRAW (SHELL, skips headless):
```
draw_guidelines(view, fp, targets):
  if not HAVE_GL or not targets: return
  For each target, trace the actual corridor route current→target (the path_xz
  polylines along the BFS path) projected onto the felt floor (y = socket_y + small
  epsilon), draw as a colored strip (target's map_color) ending in an arrowhead.
  Uses wire_program or a small dedicated line draw (INTEGRATION). Routes are a
  navigation + vertigo-mitigation device (committed floor).
```

TESTS (pure):
```
test_slot1_is_nearest      — current with two uncleared neighbors at dist 1 and 2 →
                             slot1 is the dist-1 one; tie → lowest id.
test_excludes_cleared      — a cleared room never appears.
test_excludes_current      — current never in result.
test_score_orders_2_3      — construct importances/distances so a far high-importance
                             room beats a near low-importance one for slot 2.
test_max_three             — graph with 6 candidates → exactly 3 returned.
test_fewer_when_scarce     — 1 candidate → list of length 1.
test_unreachable_excluded  — a disconnected room is never selected.
test_deterministic         — same inputs → identical list.
```

---

### BRIEF 7 — nav_collision.py (M1 corridor; M6 room + door_at)

FROZEN SIGNATURES (Second Canon §5.3):
```python
def build_corridor_nav(fp: Floorplan) -> NavQuery: ...
def build_room_nav(room: RoomRuntime) -> NavQuery: ...
```

NavQuery Protocol (contracts):
```
resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3
nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None
door_at(self, point: Vec3) -> str | None    # returns edge_id or None
```

PURPOSE: collision + ray queries. Two builders return objects implementing NavQuery.
This is PURE geometry — no GL, fully testable. (No window, no textures.) The corridor
NavQuery's door_at always returns None (doors are a room-mode concept); the room
NavQuery implements the real door_at.

CORRIDOR NAV (build_corridor_nav):
```
From Floorplan corridors build a walkable volume: each corridor is a swept path
(path_xz polyline at cruise_y) of width_m with soft side boundaries + ramps (the
y changes along path_xz already encode ramps). Node sockets are walkable platforms
(disc of map_radius_m at socket_y). resolve_player_motion slides the player along
the floor: project the attempted delta, clamp to stay within corridor half-width of
the nearest path segment (soft nudge toward centerline — OT §8.3 rail assist), and
set y to the local floor height (interpolated along the segment / socket).
nearest_panel: corridors have NO panels → always returns None.
door_at: corridor nav → always None.
```

ROOM NAV (build_room_nav):
```
Axis-aligned box [-W/2,W/2]×[0,H]×[-D/2,D/2] from room.dimensions_m. Walls solid
EXCEPT door intervals: for each DoorRT, the opening on its wall (centered at
door.center_xyz, width door.width_m, up to door.height_m) is PASSABLE. The hidden
alcove (final pair drawing) is a shallow recess, NOT passable as transit.
resolve_player_motion: slide along floor, block at solid walls, allow passing
through door intervals (so stepping out a door triggers a ModeSwitch — gameplay
checks door_at).
nearest_panel(ray, max_dist): intersect ray with every panel quad (each PanelPairRT
has drawing_placement + text_placement: a rect at center_xyz, width_m×height_m,
facing yaw_rad inward). Return the nearest hit ≤ max_dist as PanelHit with:
  asset_on_id/asset_off_id = the on/off asset_ids for THAT panel (drawing or text),
  pair_id, is_drawing (True if the hit panel is the drawing), distance.
door_at(point): if point lies within a door's opening interval on its wall plane
  (within DOOR_TRIGGER_DEPTH_M of the wall and inside the opening width/height),
  return that door.edge_id; else None.
```

PURE HELPERS (exposed for tests):
```python
def ray_rect_hit(ray, center, width, height, yaw_rad) -> float | None  # distance
def point_in_door(point, door: DoorRT) -> bool
```

PINNED:
```
DOOR_TRIGGER_DEPTH_M = 0.25   # how close to the wall plane counts as "at the door"
CORRIDOR_SLIDE_SOFTNESS = 0.5 # rail-assist nudge factor
```

TESTS (pure):
```
test_corridor_keeps_on_floor   — motion across a ramp segment sets y to the ramp
                                 height (interpolated).
test_corridor_soft_boundary    — attempt to walk past half-width → clamped inside.
test_corridor_nearest_panel_none — always None.
test_corridor_door_at_none     — always None.
test_room_wall_blocks          — motion into a solid wall is blocked (start stays
                                 inside box).
test_room_door_passable        — motion through a door interval is allowed (final
                                 pos crosses the wall plane).
test_ray_hits_drawing_panel    — a ray aimed at a panel center returns its distance;
                                 PanelHit.is_drawing correct, asset ids match.
test_ray_misses                — ray pointing away → None.
test_nearest_of_two            — two panels in line → the closer one returned.
test_door_at_inside            — point in a door opening → its edge_id.
test_door_at_solid             — point on a solid wall stretch → None.
test_door_at_uses_bearing_placed_door — door at a non-cardinal bearing (landing on
                                 N or E wall per the ray rule) is found at its
                                 actual center_xyz, NOT a wall-center.
```

---

### BRIEF 8 — assets.py (M6)

FROZEN SIGNATURE (Second Canon §5.3):
```python
def load_pack(dir: str) -> Pack: ...   # asserts schema_version on every file
```

PURPOSE: load all baked content into a Pack (contracts):
```
Pack(floorplan, rooms: dict[NodeId,RoomRuntime], manifest, palette, asset_dir)
```

BEHAVIOR (mostly PURE + file IO; no GL):
```
Read from `dir` using contracts.load_json(path, Model) (asserts schema_version):
  floorplan.json            -> Floorplan
  room_runtime/room_*.json  -> RoomRuntime each (key by room_id)
  manifest.json             -> Manifest
  palette.json              -> Palette
asset_dir = the directory containing the PNGs referenced by manifest wall_path/
  master_path (relative to `dir`).
VALIDATE (fail loudly, ValueError with the offending id):
  - every room_id in rooms appears in floorplan.rooms (ID spine).
  - every asset_id referenced by any RoomRuntime (panel 4-tuple per pair,
    ceiling eq asset_id) EXISTS in manifest.assets.
  - every manifest wall_path & master_path file exists on disk under asset_dir.
DO NOT load PNG pixels here (that's render's job at GL-upload time); just verify
paths exist. (Pillow load happens in the render shells / readmode.)

Palette is the contracts.Palette model (re-exported from raw_models); assert the
reserved keys exist (grey_ink, grey_text, bg_key, map_importance.1..5) per §2.4.
(Palette already exists in raw_models — import it from contracts; do NOT redefine.)
```

TESTS:
```
test_loads_golden_pack     — the golden fixture pack loads; rooms dict keyed by id;
                             manifest non-empty.
test_asserts_schema        — a fixture with schema_version "0.9" → raises.
test_missing_asset_ref     — a room referencing an unknown asset_id → ValueError
                             naming it.
test_spine_mismatch        — a room_id not in floorplan → ValueError.
test_missing_png_path      — manifest path to nonexistent file → ValueError.
test_palette_reserved_keys — palette missing map_importance.3 → ValueError.
```

---

### BRIEF 9 — render_room.py (M6) — Mode B

FROZEN SIGNATURE (Second Canon §5.3):
```python
def draw_room(view: ViewMatrix, room: RoomRuntime, pack: Pack, state: GameState) -> None: ...
```

PURPOSE: Mode B solid first-person room. Build the box, walls-with-holes at the
bearing-placed DoorRT positions (recessed doorways via normal_yaw_rad), baked panels
(sample off OR on per panel state), hidden-door alcove at hidden_door_wall_slot,
ceiling equations hidden until enemy_defeated then blood-red via tint uniform.
(Apocrypha §7.)

GEOMETRY (PURE CORE — testable headless):
```python
def build_room_mesh(room: RoomRuntime) -> RoomMesh:
  RoomMesh = dataclass(
    wall_tris: np.ndarray (Nw,3,3),  wall_uvs (Nw,3,2),   # 4 walls + floor + ceiling,
                                                            # each wall a quad-set with a
                                                            # rectangular HOLE per DoorRT on it
    door_frame_tris: np.ndarray,                          # recessed doorway jambs per door
    panel_quads: list[PanelQuad],                          # one per panel (drawing+text)
    ceiling_quads: list[CeilingQuad],
    alcove_tris: np.ndarray)
  PanelQuad = dataclass(pair_id, is_drawing, off_asset_id, on_asset_id,
                        corners: np.ndarray (4,3), uv: np.ndarray (4,2))
    corners from PanelPlacementRT (center_xyz, width_m, height_m, yaw_rad);
    the quad's normal points inward (yaw_rad).
  Walls built from dimensions_m per the COORDINATE LAW (N at z=+D/2, etc.).
  For each wall, subtract every DoorRT whose .wall == this wall: cut a rectangular
  hole (door.center_xyz ± width_m/2 along the wall axis, 0..height_m in Y). Build
  the wall as quads around the hole (left/right/above the opening). Recessed jamb:
  short inward-facing quads around the opening using normal_yaw_rad.
  The hidden alcove is a shallow recess at hidden_door_wall_slot (the final pair's
  DRAWING panel position) — a box recessed inward, NOT a through-hole.

Pure: build_room_mesh is deterministic geometry; unit-test corner positions, hole
presence, panel count.

def panel_is_on(pair_id: PairId, lit: set[str], room: RoomRuntime) -> bool:
  # a pair is "on" iff any of its block_ids are in lit. (Pure; unit-tested.)
```

SHELL (skips headless):
```
draw_room(view, room, pack, state):
  if not HAVE_GL: return
  Build+cache RoomMesh + GL buffers (cache by room.room_id).
  Lazy-load & cache textures from pack.manifest wall_path PNGs (Pillow→GL texture),
  keyed by asset_id (INTEGRATION: moderngl texture from Pillow bytes).
  Bind solid_program; u_mvp=view (transpose at boundary if needed).
  Draw walls/floor/ceiling/jambs/alcove with a flat material color WALL_RGB
  (u_use_tint=0). (A wall texture is later polish.)
  For each PanelQuad: choose asset = on_asset_id if panel_is_on(...) ELSE off_asset_id.
  Draw opaque geometry first; then enable BLEND locally for panels (transparent
  PNGs), draw panels, then DISABLE blend and RESTORE the depth state. (INTEGRATION:
  ctx blend func one-minus-src-alpha.)
  Ceiling equations: ONLY drawn if room.room_id in state.cleared (hidden until the
  demon dies, OT §3.2). When drawn, set tint via ceiling_tint_uniform(solid_program,
  red=1.0) → blood-red, then draw each CeilingEqRT quad with its neutral asset.
```

PINNED:
```
WALL_RGB = (0.18,0.18,0.20)
DOOR_JAMB_DEPTH_M = 0.3
ALCOVE_DEPTH_M    = 0.4
PANEL_INSET_M     = 0.02   # panel sits just off the wall to avoid z-fight
```

TESTS (pure):
```
test_box_dimensions        — RoomMesh wall extents match dimensions_m.
test_door_hole_present     — a degree-1 room (one DoorRT on E wall) → the E wall
                             has a hole at door.center_xyz (no wall tris cover that
                             rect; the other walls are solid).
test_door_hole_at_bearing  — a DoorRT at a non-cardinal bearing placed on (say) N
                             wall at along-x = X → the hole is centered at X, NOT at
                             wall center.
test_panel_count           — N pairs → 2N PanelQuads (drawing+text).
test_panel_corners         — a panel's 4 corners are width_m×height_m around
                             center_xyz, normal per yaw_rad.
test_panel_on_off_select   — panel_is_on returns True when a pair's block is in lit,
                             False otherwise.
test_alcove_is_recess      — hidden_door_wall_slot yields an alcove recess, not a
                             through-hole.
@skip_if_no_gl test_draw_smoke — golden room draws without error.
```

---

### BRIEF 10 — readmode.py (M6)

FROZEN SIGNATURE (Second Canon §5.3):
```python
def draw_read(asset_master_path: str, zoom: float, pan: Vec2) -> None: ...
```

LOCKED RULE (Second Canon §5.3 commentary): the TARGET-selection (which asset to read)
is owned by gameplay/nav (raycast-hit ≤ READ_MAX_DIST, else nearest center within
READ_CONE_HALF_ANGLE_RAD ≤ READ_MAX_DIST, else no-op). Both constants are imported
from contracts (READ_MAX_DIST=6.0, READ_CONE_HALF_ANGLE_RAD=35°). draw_read only
RENDERS the chosen master PNG. World is paused by app. Read Mode does NOT flip state.

PURPOSE: render a pin-sharp, full-screen, flat 2D, zoomable/pannable image of the
master-DPI panel PNG. No perspective, no blur (R12 escape hatch).

PURE CORE (testable headless):
```python
def read_uv_transform(zoom: float, pan: Vec2) -> tuple[float, Vec2]:
    # validates/clamps: zoom in [1.0, MAX_ZOOM]; pan clamped so the image can't be
    # dragged fully off-screen given zoom. Returns (clamped_zoom, clamped_pan).
```

PINNED: MAX_ZOOM = 8.0; pan clamp = ±(1 - 1/zoom)*0.5 per axis.

SHELL (skips headless):
```
draw_read(asset_master_path, zoom, pan):
  if not HAVE_GL: return
  Load+cache the master PNG as a GL texture (Pillow → moderngl texture, keyed by
  path). Draw a fullscreen quad via blit_program with u_zoom, u_pan from
  read_uv_transform. Background = solid dark (the paused world is hidden; do NOT
  draw the 3D world this frame — app handles pause). (INTEGRATION: fullscreen NDC
  quad VBO.)
```

TESTS (pure):
```
test_zoom_clamped_low      — read_uv_transform(0.5,(0,0)) → zoom 1.0.
test_zoom_clamped_high     — zoom 100 → MAX_ZOOM.
test_pan_clamped           — at zoom 2, pan (5,5) clamps to within ±0.25.
test_pan_zero_at_zoom1     — zoom 1 → pan forced (0,0) (nothing to pan).
@skip_if_no_gl test_draw_smoke — a tiny master PNG fixture draws without error.
```

---

### BRIEF 11 — state.py (M7)

FROZEN SIGNATURES (Second Canon §5.3):
```python
def new_state(pack: Pack, profile_id: str = "default") -> GameState: ...
def load(path: str, pack: Pack) -> GameState: ...
def save(state: GameState, path: str) -> None: ...   # atomic
```

PURPOSE: own GameState (runtime, contracts) and its persistence as SaveGame
(disk, §4.7). Atomic writes.

```
GameState (runtime) fields: save:SaveGame, mode, current_room_id, pos:Vec3,
    heading_rad, pitch_rad, lit:set[str], cleared:set[NodeId].
SaveGame (disk) fields: schema_version, profile_id, levels:dict[LevelId,LevelProgress],
    player:PlayerSave.  (PlayerSave persists level_id, mode, current_room_id,
    position_xyz, heading_rad — NO pitch; pitch is runtime-only, resets to 0 on load.)
```

BEHAVIOR:
```
new_state(pack, profile_id):
  Start in corridor mode at the level's start. PIN: start position = the first
  FloorRoom's socket (lowest room_id) socket point (x, socket_y, z); heading_rad=0;
  pitch=0; lit=∅; cleared=∅. Build a fresh SaveGame with empty LevelProgress for the
  level (level_id from floorplan.level_id). current_room_id = None (in corridor).
save(state, path):
  Sync state→SaveGame via state_to_save (below). ATOMIC: write temp file in same
  dir → flush+fsync → os.replace(temp, path).
load(path, pack):
  Read+validate SaveGame (contracts.load_json asserts schema_version). Forward-
  compat: unknown room/level ids vs pack are DROPPED with a logged warning. Rebuild
  GameState via save_to_state.

IMPORTANT DIVISION OF LABOR: state.py does pure (de)serialization + atomic IO.
gameplay.py is the ONLY writer of progress semantics (it mutates state.save's
RoomProgress directly as the player acts). state.py never decides game rules.

Provide pure helpers (testable):
  def state_to_save(state: GameState) -> SaveGame
    # player block from state.pos/heading/mode/current_room_id; the levels dict is
    # taken from state.save (gameplay keeps it current). pitch NOT written.
  def save_to_state(save: SaveGame, pack: Pack) -> GameState
    # pos from player.position_xyz, heading from player.heading_rad, pitch=0,
    # mode/current_room_id from player; lit rebuilt from each RoomProgress.pairs_on
    # expanded to block_ids; cleared = rooms whose RoomProgress.room_cleared.
```

TESTS:
```
test_new_state_corridor    — new_state → mode "corridor", current_room_id None,
                             lit/cleared empty, pos at lowest-id room socket.
test_roundtrip             — state_to_save∘save_to_state preserves pos, heading,
                             mode, lit, cleared (set equality).
test_pitch_not_persisted   — pitch set to 0.5, save, load → pitch 0.0.
test_atomic_write          — save writes via temp+replace (monkeypatch os.replace,
                             assert a temp file was the source).
test_schema_assert         — loading schema_version "0.9" → raises.
test_forward_compat_drop   — a save with an unknown room id → loads, warns, drops it.
```

---

### BRIEF 12 — gameplay.py (M7) — the loop

FROZEN SIGNATURE (Second Canon §5.3):
```python
def step(state: GameState, actions: Actions, pack: Pack, nav: NavQuery, dt: float) -> list[Event]: ...
```

PURPOSE: the entire game-logic step. Pure-ish (mutates state, returns Events; no GL,
no window — fully testable headless). Owns: movement application, shooting resolution,
the door logic, demon spawn/kill, room clear, ceiling reveal, god-mode, mode switching,
guideline-recompute triggering. (OT §3.2 door logic; Apocrypha §7; co-op rules.)

PER-STEP BEHAVIOR (order matters):
```
1. APPLY MOTION (Mover owns it):
     state.heading_rad += actions.heading_delta
     state.pitch_rad    = clamp(state.pitch_rad + actions.pitch_delta, ±PITCH_CLAMP_RAD)
       (PITCH_CLAMP_RAD imported from contracts — same value as camera.)
     forward_xz = (cos(heading), sin(heading))    # FROZEN compass; matches camera
     strafe_xz  = (sin(heading), -cos(heading))
     delta = (forward_xz*move_y + strafe_xz*move_x) * WALK_SPEED_M_S * dt, y=0
     state.pos = nav.resolve_player_motion(state.pos, delta)

2. MODE-SWITCH CHECK:
     if state.mode == "room":
        eid = nav.door_at(state.pos)
        if eid is not None:  # stepped out a transit door
           emit ModeSwitch(to="corridor", room_id=state.current_room_id, via_edge_id=eid)
           set state.mode="corridor", current_room_id=None
           (app performs the teleport-snap: unload room, place player in corridor at
            that edge's mouth, heading = bearing (outward).)
     elif state.mode == "corridor":
        # entering a room: when pos enters a node socket disc (radius
        # SOCKET_ENTER_RADIUS_M) AND moving inward, emit
        # ModeSwitch(to="room", room_id=that node, via_edge_id=the corridor edge);
        # set state.mode="room", current_room_id=node; place player at
        # doors[edge].spawn_xyz with heading = doors[edge].spawn_heading_rad
        # (== bearing+π, zero snap).
        # ALSO: emit GuidelinesRecomputed(targets=[]) when a junction socket is crossed
        # (app fills targets by calling select_targets).

3. SHOOTING (Shooter owns it; only in room mode has targets):
     if actions.fire and state.mode == "room":
        ray = reticle_ray(eye, state.heading_rad, state.pitch_rad, actions.aim_x,
                          actions.aim_y)   # within AIM_CONE_RAD; Shooter NEVER rotates cam
        hit = nav.nearest_panel(ray, max_dist=SHOOT_MAX_DIST)
        room = pack.rooms[state.current_room_id]
        events, new_lit, new_hidden, new_hp, cleared = resolve_shot(
            room, hit, state.lit, hidden_open_for_room, demon_hp_for_room)
        apply deltas to state + state.save's RoomProgress for this room
        (pairs_on, hidden_door_open, enemy_defeated, room_cleared); if every room in the
        level is cleared → mark level_complete and emit LevelComplete.

     DOOR LOGIC inside resolve_shot (OT §3.2), PURE:
        - hit is final pair's panel AND final pair OFF → flip ON; PanelLit.
        - final pair ON AND hidden door CLOSED AND hit is the hidden-door alcove panel
          (final drawing) → open hidden door; spawn demon; DoorOpened + DemonSpawned.
        - demon alive AND ray hits demon billboard (center room.enemy.spawn_xyz, radius
          DEMON_RADIUS) → hp-=1 (god-mode; infinite ammo); DemonHit; if hp<=0 →
          DemonKilled + mark enemy_defeated + RoomCleared (ceiling reveal handled by
          render via state.cleared).
        - hit is any OTHER pair AND that pair OFF → flip ON; PanelLit.
        - else → no-op.

4. READ TOGGLE: if actions.read_toggle: emit ReadModeToggled(on=<new>,
     asset_id=<target asset under the §5.3 rule, or None>). Read does NOT flip state.

GOD-MODE: no player health, no death, no ammo. Never emit a player-damage event
(none exists in the union). Exactly one enemy per room. No level boss.
```

PINNED CONSTANTS:
```
WALK_SPEED_M_S = 2.4     # slow default walk (comfort)
AIM_CONE_RAD = 0.30
SHOOT_MAX_DIST = 50.0
DEMON_RADIUS = 0.6
SOCKET_ENTER_RADIUS_M = 1.0
# PITCH_CLAMP_RAD imported from contracts.
```

PURE HELPERS (exposed for tests):
```python
def reticle_ray(eye, heading, pitch, aim_x, aim_y) -> Ray
def resolve_shot(room, hit, lit, hidden_open, demon_hp)
    -> (events, new_lit, new_hidden_open, new_demon_hp, cleared_bool)
  (PURE: the entire door/demon decision table, no state mutation — returns the
   deltas. step() applies them. Makes the OT §3.2 table fully unit-testable.)
```

TESTS (pure, headless — the heart of the test suite):
```
test_door_logic_off_to_on  — final pair OFF + shot hits it → flips ON, PanelLit,
                             no demon yet.
test_door_logic_open_door  — final pair ON + closed + shot hits alcove → DoorOpened
                             + DemonSpawned.
test_door_logic_open_noop  — door already open + shot into empty → no door event.
test_demon_takes_5_hits    — 5 DemonHit then DemonKilled + RoomCleared; hp 5→0.
test_god_mode_no_death     — no event in any sequence is a player-damage type
                             (none in the union — assert by construction).
test_normal_panel_flip     — shot hits a non-final OFF pair → PanelLit, pair on.
test_already_on_noop       — shot hits an ON panel → no PanelLit re-emit.
test_mover_only_motion     — heading changes only by actions.heading_delta; aim
                             never changes heading/pitch.
test_walk_uses_nav         — resolve_player_motion called with the computed delta
                             (fake NavQuery; delta direction matches inputs).
test_modeswitch_out_of_room— in room, pos crosses a door → ModeSwitch(to corridor,
                             via_edge_id set).
test_modeswitch_into_room  — in corridor, entering a node socket → ModeSwitch(to
                             room, room_id, via_edge_id) and spawn heading == door
                             spawn_heading_rad (bearing+π).
test_read_toggle_no_flip   — read_toggle never adds to lit; emits ReadModeToggled.
test_level_complete        — clearing the last room → LevelComplete.
test_resolve_shot_pure     — resolve_shot returns deltas without mutating inputs.
test_deterministic_step    — same state+actions → same events (no RNG).
```

---

### BRIEF 13 — app.py (grows M0→M1→M6→M7) — the thin loop

FROZEN SIGNATURE (Second Canon §5.3):
```python
def main() -> int: ...
```

PURPOSE: the thin per-frame loop. OWNS NO GAME LOGIC. Wires modules in the §5.4 order.
Grows across milestones; deliver in stages but the final wiring is below.

M0 STUB (deliver first):
```
make_window(1280,720,"QUAKE M0"); compile shaders; each frame
clear, draw ONE shaded triangle (solid_program, flat) + ONE wireframe line
(wire_program), depth ON, blend OFF; present. Prove the GPU path is ours. Return 0
on clean exit. This stub is replaced as modules land. If not glguard.HAVE_GL, main
returns 0 immediately (headless smoke-launch path).
```

FINAL WIRING (§5.4 — authoritative order):
```
state init: pack = assets.load_pack(dir); state = state.new_state(pack) (or load).
nav: corridor_nav = nav_collision.build_corridor_nav(pack.floorplan); a room_nav is
     (re)built on entering each room. current_nav starts = corridor_nav.
per frame:
  actions = input_actions.poll(window, bindings)
  events  = gameplay.step(state, actions, pack, current_nav, dt)
  for ev in events: handle:
     ModeSwitch(to="room")    → room_nav = build_room_nav(pack.rooms[room_id]);
                                current_nav = room_nav; TELEPORT-SNAP (no blend).
     ModeSwitch(to="corridor")→ current_nav = corridor_nav; unload room; snap.
     GuidelinesRecomputed     → targets = guidelines.select_targets(
                                   pack.floorplan, current_node_or_nearest,
                                   state.cleared, cfg)
     ReadModeToggled(on)      → set read_active=on; resolve master path from
                                ev.asset_id via pack.manifest; zoom=1,pan=(0,0)
     (other events → optional SFX hooks; audio is a GAP, ~M8)
  view = camera.update(state.heading_rad, state.pitch_rad, state.pos, dt)
  if read_active:
      readmode.draw_read(master_path, zoom, pan)   # world PAUSED
  elif state.mode == "corridor":
      render_wire.draw_graph(view, pack.floorplan, state)
      guidelines.draw_guidelines(view, pack.floorplan, targets)
      (bloom is inside render_wire's post-pass)
  else:
      render_room.draw_room(view, pack.rooms[state.current_room_id], pack, state)
  present/swap
  debounced: state.save(state, save_path)  (at most every ~1.0s or on any
      progress event)

PIN (world pause during Read): while read_active, app does NOT call gameplay.step
except to consume the read_toggle that exits Read (app passes a zeroed/paused
Actions so the world does not advance). Keeps "world paused; shooting is the only
thing that flips off→on" — and Read never flips. gameplay stays pure; app gates it.

PIN (current_node_or_nearest for guidelines): app tracks the last node socket the
Mover passed (from ModeSwitch/junction events) as `current`. At level start it is
the start room id (lowest room_id).
```

TESTS:
```
@skip_if_no_gl test_m0_smoke    — main() M0 stub opens, renders a few frames, exits
                                  0. (Headless: main returns 0 via glguard without
                                  crashing the import.)
test_event_dispatch_pure        — a pure helper dispatch_events(events, ctx) (extract
                                  the event→command mapping as a pure function
                                  returning a small command list) is unit-tested:
                                  ModeSwitch→swap-nav command, ReadModeToggled→
                                  set-read command, GuidelinesRecomputed→recompute
                                  command, etc. (GL/window parts stay in the shell.)
```

---

## PART 3 — THE GOLDEN FIXTURE PACK (OT §12.5) + ANTI-REGRESSION

DeepSeek builds ONE golden pack under tests/golden_pack/ used by EVERY module's tests
and by the CI smoke launch. It is hand-authored baked output (NOT produced by the build
legs — it is a fixture), valid against all contracts:

CONTENTS (exactly OT §12.5, made concrete):
```
  floorplan.json   — 3 rooms (r_a, r_b, r_c), 3 corridors forming a path a-b-c plus one
                     extra edge a-c so there is 1 CROSSING → resolved as 1 bridge + 1
                     underpass (two corridors at cruise_y 0.0 and 4.5; a Crossing entry
                     with over_y>under_y). importances spread 5/3/1. map_colors from a
                     palette.
  palette.json     — includes the reserved keys (grey_ink, grey_text, bg_key,
                     map_importance.1..5) + a few groups; valid hex.
  manifest.json    — assets for: r_a has 2 step-pairs (a two-step room) → figure_off,
                     figure_on.1, figure_on.2, text off/on ×2; plus a ceiling_neutral.
                     Tiny real PNGs (e.g. 8×8) at wall_path & master_path so file-exists
                     checks pass and textures upload.
  room_runtime/room_r_a.json — dimensions_m, 2 panel_pairs with PanelPlacementRT,
                     final_pair_id=<r_a's s2>, hidden_door_wall_slot = s2 drawing's
                     wall_slot, enemy r_a.demon health 5, 1 ceiling eq, doors: DoorRT
                     list matching r_a's degree (a connects to b and c → 2 doors at
                     their true bearings; at least one NON-CARDINAL bearing so the
                     bearing-placement tests bite).
  room_runtime/room_r_b.json, room_r_c.json — minimal valid rooms (1 pair each, doors
                     per degree).

  This pack EXERCISES: 1 crossing (bridge+underpass), a two-step room, a demon, a ceiling
  equation, bearing-placed non-cardinal doors, the full clear→LevelComplete path.
```

ANTI-REGRESSION CLAUSE (FROZEN):
```
  - The golden pack's JSON files and their expected derived values (wire mesh segment
    counts, room mesh hole positions, select_targets output for a fixed `current`,
    resolve_shot decision sequence, save roundtrip) are committed as golden expectations.
  - Any change to a module that alters a golden expectation is a CONTRACT-LEVEL event:
    it requires an explicit architect note + a schema/contract version consideration. A
    child may NOT silently change a golden value to make a test pass. If a golden value
    looks wrong, STOP and flag it — do not edit the golden.
  - CI runs: all pure tests (must be green headless) + the @skip_if_no_gl tests (skip
    gracefully where no context) + a smoke launch of app.main() against the golden pack
    that runs N frames and exits 0 (skipped if no GL).
```

---

## PART 4 — ACCEPTANCE GATES (mapped to OT §13 milestones)

```
M0 ACCEPTANCE: app.py M0 stub opens a moderngl window and draws one shaded triangle +
   one wireframe line, depth ON, blend OFF. gfx_context.check_caps + shaders pure tests
   green. → "the GPU path is ours."

M1 ACCEPTANCE: you walk the golden floorplan in Mode A — wireframe, distance-dimming to
   dark grey (never black), crossings visibly over/under, ≤3 guide-lines with arrowheads,
   Mover-only heading, decoupled damped camera (no overshoot, pitch clamped). camera +
   input_actions + render_wire + guidelines + corridor nav pure tests green.

M6 ACCEPTANCE: enter golden room r_a through a bearing-correct door with ZERO heading-
   snap (spawn_heading == bearing+π), see baked panels (off grey) on walls at their
   placements, doors at true bearings as holes-with-recessed-jambs, press R → pin-sharp
   master-DPI Read of the targeted panel (the §5.3 rule). assets + render_room + readmode
   + room nav + door_at pure tests green.

M7 ACCEPTANCE: full loop on the golden pack — shoot a non-final panel OFF→ON (persisted
   atomically), shoot the lit final wall → hidden door OPENS → demon emerges → kill it
   (5 hits, god-mode, can't die) → ceiling equations appear BLOOD-RED → room cleared;
   clear all 3 rooms → LevelComplete. Co-op: Mover walks + turns, Shooter aims a reticle
   in a cone, camera NEVER lurches from aiming. gameplay + state pure tests green; CI
   smoke launch of the whole loop exits 0.
```

ACROSS ALL: every pure-logic core is unit-tested green in headless CI; GPU/window tests
skip gracefully without a context; the golden pack plays end-to-end in the smoke launch.

---

## PART 5 — HANDOFF NOTES & THE ONE REMAINING GAP

INFRASTRUCTURE (PART 1.5) — created FIRST, before any child:
```
  - contracts.py: re-exports every alias + model from map/raw_models.py and defines the
    engine-only types (Actions, Event union, Ray, PanelHit, NavQuery, GameState,
    SaveGame + progress models, Pack, ViewMatrix, Report) and the locked constants
    (READ_MAX_DIST, READ_CONE_HALF_ANGLE_RAD, PITCH_CLAMP_RAD). Children import ONLY
    from contracts; they NEVER touch map.raw_models. INTEGRATION: confirm the re-export
    name list against the real raw_models.py — any spelling delta is a one-line fix in
    contracts.py only.
  - glguard.py: HAVE_GL probe, never crashes on import; shells gate draws on it.
  - conftest.py: the skip_if_no_gl marker for GPU/window tests.
```

DECISIONS I MADE AND FROZE (so no one re-litigates):
```
  - Compass: heading/bearing θ → world forward (cosθ, 0, sinθ); +X east, +Z north.
    One definition unifies camera, doors (bearing), spawn (bearing+π), and Mode A.
  - ModeSwitch carries via_edge_id (Apocrypha §3 supersedes §5.1's 3-field form).
  - Junction detection + GuidelinesRecomputed + ModeSwitch emission live in gameplay.step
    (it has nav+pos+dt); guidelines.select_targets stays pure; app reacts to events.
  - Pack does NOT include ConceptGraph; Mode A draws rings from Floorplan only; no node
    text labels in v1 (labels are a post-M7 polish via a future labels.json — no Pack
    contract touch now).
  - pitch is runtime-only, never persisted (PlayerSave has no pitch field).
  - Ceiling equations are NOT drawn until cleared, then drawn blood-red (tint=1.0).
  - Walls are a flat material color in v1 (WALL_RGB); wall textures are later polish.
  - Actions is a FROZEN pydantic model (validates + satisfies test_actions_frozen).
  - PanelLit carries pair_id + room_id; DemonHit carries hp_remaining.
  - Locked constants centralized in contracts (READ_*, PITCH_CLAMP_RAD) — modules import
    them, never re-pin different values.
  - All other comfort/gameplay constants pinned per-module (CAM_*, WALK_SPEED, AIM_CONE,
    DIM_*, etc.) — children read pinned constants, do not invent.
```

INTEGRATION-LOOP ITEMS (external API names I REFUSE to assert from memory — DeepSeek's
compile loop confirms each in ONE isolated wrapper per module, per Iron Rule #3):
```
  - The contracts.py re-export name list vs the real map/raw_models.py spellings.
  - pyglet 2.1.x: Window construction args (incl. visible=False), keyboard/mouse/
    controller polling.
  - moderngl: create_context / create_standalone_context(require=330), program(),
    texture-from-Pillow, FBO/framebuffer for bloom, blend func, depth_func string,
    uniform assignment, mat4 row/column-major at the boundary (transpose if needed —
    each render shell has ONE transpose point).
```

THE ONE GENUINE GAP I CANNOT CLOSE FROM CONTRACTS (flagged, not invented):
```
  - AUDIO (OT §11.3, Commentaries §5 "deferred ~M8"): SFX hooks exist as event handlers
    in app (gunshot on fire, panel-flip on PanelLit, demon on DemonSpawned/Killed, glyph-
    spray on RoomCleared) but the actual sound assets + music/atmosphere are unspecified
    and explicitly deferred to ~M8. NOT blocking M0–M7. I leave clean event hooks; I do
    NOT invent sound design. When M8 comes, a `sfx.py` module subscribes to these events
    behind a frozen play(event)->None contract.
```

WHAT'S DONE WHEN M0–M7 PASS: see Part 4. Then M8 (one full real Principia level + audio)
and M9 (second pack) follow — but the ENGINE is M0–M7, and this package freezes it.

Pass it on when you're done. 🗝️
