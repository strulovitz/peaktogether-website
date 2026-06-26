🗝️ QUAKE — FROZEN CHILD BRIEF: app.py (FULL §5.4 PER-FRAME WIRING)

Authored by Parent 6 (Claude Opus 4.8), June 26, 2026. This brief is self-contained. You — the child — write exactly one file: app.py. You may not see or import any project module's internals; every type and signature you need is inline below. You replace the current M0 stub (triangle + line) with the full per-frame loop wiring all 13 engine modules. Do not change any other file.
§0 — YOUR ONE MISSION

Write app.py. It wires 13 already-built, frozen engine modules into the authoritative §5.4 per-frame loop, consuming a Golden Fixture Pack at tests/golden_pack/. It must:

    Maintain a strict PURE/SHELL split: all GL/window/IO lives only inside main() and the small _gl_* / _window_* integration wrappers; everything else is pure, headless-testable functions.
    Run headlessly safe: if HAVE_GL is False, main() returns 0 immediately after imports — no window, no GL.
    Run a CI smoke launch: with GL available, open a window, load the golden pack, run 60 frames of the real loop (zero player input is fine — the loop ticks regardless), exit 0.
    Handle mode switching (corridor ↔ room), Read Mode toggle, and atomic save/load.
    Use only the frozen signatures in §3 — exact names, exact parameter counts. Mismatched signatures are the #1 integration failure.

You may import only: the project modules listed in §3, plus standard library, moderngl, pyglet, and numpy. Nothing else.
§1 — COORDINATE & CONVENTION LAW (frozen)

    XZ is the map floor plane; Y is up. Position is Vec3 = tuple[float, float, float].
    Heading is a float in radians; forward = (cos heading, 0, sin heading).
    Matrices are row-major internally; transpose only at the GL boundary (the existing _gl_set_uniform_mvp already does .T — preserve that pattern for any matrix write).
    PITCH_CLAMP_RAD = 1.2217 (±70°). Pitch is always clamped before being handed to the camera.
    READ_MAX_DIST = 6.0, READ_CONE_HALF_ANGLE_DEG = 35.0 (used by readmode/gameplay; you do not re-implement targeting — see §4).
    Every JSON the engine touches carries schema_version "1.0"; you do not validate this yourself — load_pack does.

§2 — TYPE DEFINITIONS (verbatim — these are ground truth from contracts.py)

You cannot import these from our codebase as definitions to copy, but they will be importable at runtime from contracts / the modules. They are reproduced here so you know their exact shape. Do not redefine them in app.py; import what you need (see §3). Treat the field names below as exact.

# ---- aliases ----
Vec3 = tuple[float, float, float]
Vec2 = tuple[float, float]
NodeId = str       # ^[a-z][a-z0-9_]*$
PairId = str       # ^[a-z][a-z0-9_]*\.s[0-9]+$
LevelId = str
ViewMatrix = "np.ndarray"   # shape (4,4), float32, row-major

# ---- co-op semantic actions (frozen dataclass; produced by input_actions.poll) ----
@dataclass(frozen=True)
class Actions:
    move_x: float           # [-1,1] strafe (right +)
    move_y: float           # [-1,1] forward (+) / back (-)
    heading_delta: float    # radians this frame (yaw). MOVER ONLY.
    pitch_delta: float      # radians this frame, pre-clamp. MOVER ONLY.
    aim_x: float            # [-1,1] reticle x within cone
    aim_y: float            # [-1,1] reticle y within cone
    fire: bool              # edge: true only on the frame fire is pressed
    fire_held: bool
    read_toggle: bool       # edge
    interact: bool          # edge
    pause: bool             # edge

# ---- events emitted by gameplay.step (GROUND TRUTH from built contracts.py) ----
class PanelLit(_Ev):
    event: Literal["panel_lit"] = "panel_lit"
    pair_id: PairId
    room_id: NodeId
    # NOTE: NO block_id field.

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
    hp_remaining: int       # NOTE: hp_remaining, NOT "hp".

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
    event: Literal["mode_switch"] = "mode_switch"
    to: Literal["corridor", "room"]
    room_id: NodeId | None = None
    via_edge_id: str | None = None      # per Apocrypha v3

class ReadModeToggled(_Ev):
    event: Literal["read_toggled"] = "read_toggled"
    on: bool
    asset_id: str | None

class GuidelinesRecomputed(_Ev):
    event: Literal["guides"] = "guides"
    targets: list[NodeId]

# Discriminated union, discriminator="event".
Event = PanelLit | DoorOpened | DemonSpawned | DemonHit | DemonKilled | \
        RoomCleared | LevelComplete | ModeSwitch | ReadModeToggled | GuidelinesRecomputed

# ---- geometry / runtime helpers ----
@dataclass(frozen=True)
class Ray:
    origin: Vec3
    direction: Vec3

@dataclass(frozen=True)
class PanelHit:
    asset_on_id: str
    asset_off_id: str
    pair_id: PairId
    is_drawing: bool
    distance: float

class NavQuery(Protocol):
    def resolve_player_motion(self, start: Vec3, delta: Vec3) -> Vec3: ...
    def nearest_panel(self, ray: Ray, max_dist: float) -> PanelHit | None: ...
    def door_at(self, point: Vec3) -> str | None: ...   # room nav only; corridor nav returns None

# ---- runtime state ----
@dataclass
class GameState:
    save: "SaveGame"
    mode: Literal["corridor", "room"]
    current_room_id: NodeId | None
    pos: Vec3
    heading_rad: float
    pitch_rad: float
    lit: set[str]            # block_ids turned on (mirrors save)
    cleared: set[NodeId]

@dataclass
class Pack:
    floorplan: "Floorplan"
    rooms: dict[NodeId, "RoomRuntime"]
    manifest: "Manifest"
    palette: "Palette"
    asset_dir: str

Floorplan, RoomRuntime, SaveGame, Manifest, Palette are pydantic models loaded by load_pack. You only ever access these attributes:

    Pack.floorplan (pass whole to render/nav/guidelines), Pack.floorplan.level_id (a LevelId str), Pack.rooms[room_id] → a RoomRuntime, Pack.asset_dir (str).
    RoomRuntime.room_id (NodeId), RoomRuntime.doors (list[DoorRT]), RoomRuntime.ceiling_equations (list; you do not index it — draw_room handles ceiling).
    DoorRT fields you read on a mode-switch-to-room: .edge_id (str), .spawn_xyz (Vec3), .spawn_heading_rad (float). (Full DoorRT shape is below for reference.)

class DoorRT(BaseModel):
    edge_id: str
    neighbor_id: NodeId
    bearing_rad: float
    wall: Literal["N", "E", "S", "W"]
    center_xyz: Vec3
    width_m: float
    height_m: float
    normal_yaw_rad: float
    spawn_xyz: Vec3              # stepped inward along bearing line
    spawn_heading_rad: float     # == bearing_rad + pi

GameState.save is a pydantic SaveGame; you never construct or mutate its internals directly. Progress is committed by calling state.save(...) (the module function — see §3). The dataclass fields you read/write directly are state.mode, state.current_room_id, state.pos, state.heading_rad, state.pitch_rad, state.lit, state.cleared.
§3 — FROZEN MODULE SIGNATURES (use exactly; never redefine)

# ── INFRASTRUCTURE ──
from glguard import HAVE_GL                       # bool
from gfx_context import make_window               # make_window(width, height, title) -> (window, ctx)
from shaders import wire_program, solid_program, blit_program, ceiling_tint_uniform
    # wire_program(ctx), solid_program(ctx), blit_program(ctx)
    # ceiling_tint_uniform(prog, red: float) -> None

# ── ASSETS / STATE ──
from assets import load_pack                       # load_pack(dir: str) -> Pack
from state import new_state, load as state_load, save as state_save
    # new_state(pack: Pack, profile_id: str = "default") -> GameState
    # state_load(path: str, pack: Pack) -> GameState
    # state_save(state: GameState, path: str) -> None    # atomic

# ── INPUT / CAMERA ──
from input_actions import poll                     # poll(window, bindings) -> Actions
from camera import Camera
    # Camera()  (constructor takes optional omega_* kwargs; use defaults)
    # camera.update(heading_rad: float, pitch_rad: float, pos: Vec3, dt: float) -> ViewMatrix

# ── NAV ──
from nav_collision import build_corridor_nav, build_room_nav
    # build_corridor_nav(fp: Floorplan) -> NavQuery
    # build_room_nav(room: RoomRuntime) -> NavQuery

# ── GAMEPLAY ──
from gameplay import step                          # step(state, actions, pack, nav, dt) -> list[Event]
    # (gameplay also exposes reticle_ray(...) but app.py does NOT call it;
    #  gameplay.step uses it internally. Do not call reticle_ray from app.)

# ── GUIDELINES (corridor only) ──
from guidelines import select_targets, draw_guidelines
    # select_targets(fp, current: NodeId, cleared: set[NodeId], cfg) -> list[NodeId]
    # draw_guidelines(view: ViewMatrix, fp, targets: list[NodeId]) -> None

# ── RENDER (modules own & cache their own meshes internally — app passes NO mesh) ──
from render_wire import draw_graph                 # draw_graph(view, fp, state) -> None
from render_room import draw_room                  # draw_room(view, room, pack, state) -> None

# ── READ MODE ──
from readmode import draw_read                     # draw_read(asset_master_path: str, zoom: float, pan: Vec2) -> None

Notes that are frozen reality (do not second-guess):

    render_wire.draw_graph and render_room.draw_room build and cache their own GPU meshes internally (keyed by fp.level_id/id(fp) and room_id). app.py builds NO meshes and passes NO mesh argument. Call them with exactly the signatures above.
    select_targets and the various cfg need a BuildConfig. You import it from contracts and instantiate with defaults: from contracts import BuildConfig; cfg = BuildConfig(). Pass that cfg to select_targets.
    make_window returns a 2-tuple (window, ctx). (Keep the defensive _unpack_window helper anyway.)

§4 — WHAT GAMEPLAY OWNS vs WHAT APP OWNS (read this carefully)

gameplay.step(state, actions, pack, nav, dt) is the single source of game logic. It internally:

    moves the player (using nav.resolve_player_motion), applies heading/pitch deltas to state,
    casts the reticle ray and resolves fire → panel flip → door open → demon spawn/hit/kill → room cleared → level complete,
    decides mode switches (corridor↔room) including reading nav.door_at(...),
    decides Read-Mode toggling and target selection (the §1 raycast-then-cone rule lives here),
    and returns a list[Event] describing everything that happened, and mutates state in place for position/heading/pitch/mode/current_room_id.

Therefore app.py does NOT:

    move the player, clamp pitch into state, cast rays, select read targets, or decide mode switches on its own.

App.py DOES (this is its whole job around step):

    Poll actions.
    Call step.
    Apply the returned events to the parts of state that mirror progress (state.lit, state.cleared) and to app-local UI state (read overlay on/off, zoom/pan; active nav swap on mode switch), then persist via state_save when a progress event occurred.
    Clamp pitch (defensively) and call camera.update.
    Branch on state.mode to call the right renderer.
    Draw the read overlay if active.
    Present.

step mutating state.pos/heading/pitch/mode/current_room_id and also app applying events is not a conflict: app only touches state.lit, state.cleared, and app-local UI/nav. The event-application table in §6 says exactly which field each event touches.
§5 — RESOLVED DESIGN DECISIONS (all of §7 from the handoff — frozen here)

A. Nav switching. Build corridor nav once at startup: corridor_nav = build_corridor_nav(pack.floorplan). Build room nav lazily on ModeSwitch(to="room") and cache by room_id in an app-local dict room_navs: dict[NodeId, NavQuery]. The variable nav passed to gameplay.step is whichever nav matches the current mode at the top of the frame: corridor_nav when state.mode == "corridor", else room_navs[state.current_room_id]. (Because step may itself switch modes mid-call, select nav from the pre-step mode; the switch takes effect next frame — this is correct and avoids a chicken-and-egg.)

B. Read Mode state. App-local only — a small dataclass ReadState defined in app.py, not persisted (it is transient UI, not progress). Initial values zoom=1.0, pan=(0.0, 0.0), active=False, master_path=None. Reset to these on every Read entry. Read zoom/pan are not driven this milestone (no zoom input wired yet) — they stay at defaults; the field exists so future input can drive it without reshaping the loop.

C. Save debounce. Event-driven, not frame-count. Call state_save(state, SAVE_PATH) at most once per frame, and only if a progress event fired this frame, where "progress event" ∈ {PanelLit, DoorOpened, DemonKilled, RoomCleared, LevelComplete, ModeSwitch}. (DemonSpawned, DemonHit, ReadModeToggled, GuidelinesRecomputed do not trigger a save.) This avoids disk thrash and saves exactly when persisted state changed. Plus one auto-save on shutdown (§8).

D. Spawn / initial position. state = new_state(pack) decides the corridor start position itself — app does not compute it. On ModeSwitch(to="room"), gameplay.step already sets state.pos/state.heading_rad from the door's spawn_xyz/spawn_heading_rad (Apocrypha v3); app does not recompute spawn. App only needs to ensure the room's nav is built/cached (decision A) so subsequent frames collide correctly.

E. Wireframe mesh. Built once, owned by render_wire internally (cached). App builds nothing. Confirmed.

F. Room meshes. Built lazily, owned by render_room internally (cached by room_id). App builds nothing. Confirmed.

G. Window close / ESC. In non-smoke mode, the loop breaks when _window_should_close(window) is true. Additionally, handle a pause action (the existing semantic action) as a graceful-exit request in non-smoke mode: if actions.pause is true, break the loop (then the finally block auto-saves and closes). (ESC itself is mapped by input_actions/bindings to pause or to the window's exit; app trusts the semantic layer, not raw keys.)

H. Frame timing. Manual dt via time.perf_counter() delta between frames, clamped to a max of MAX_DT = 1.0 / 20.0 (50 ms) to avoid a spiral-of-death after a stall. First frame uses dt = 1.0 / 60.0. In smoke mode use a fixed dt = 1.0 / 60.0 every frame (deterministic, no wall-clock dependence in CI).

I. Event loop. Keep the manual while loop with _window_present (dispatch_events + flip). Do not use pyglet.app.run(). This preserves the smoke-mode frame-count pattern and keeps full control. Identical loop shape to the M0 stub.

J. Error paths. Wrap startup (window/shaders/load_pack/nav build/new_state) in try/except Exception as e: → print a clear message to stderr (print(..., file=sys.stderr)) → return 1. A failure to load a save file falls back to new_state(pack) (resume is best-effort, never fatal). The per-frame loop is inside its own try/finally so shutdown (auto-save + close) always runs.
§6 — EVENT APPLICATION (exact, pure function)

Write a pure function (no GL, no IO) that consumes one frame's events and updates the mirror sets + reports what app-local follow-up is needed. Suggested shape (you may refine names, but keep it pure and headless-testable):

@dataclass
class FrameOutcome:
    progress_changed: bool          # -> triggers debounced save
    mode_switched_to: str | None    # "corridor" | "room" | None
    switched_room_id: NodeId | None
    read_now_active: bool | None    # True/False if a read_toggled event fired, else None
    read_asset_id: str | None       # asset_id from the read_toggled event (may be None)
    new_targets: list[NodeId] | None  # from GuidelinesRecomputed, else None

def apply_events(state: GameState, events: list[Event]) -> FrameOutcome:
    ...

Apply each event type as follows (this is the frozen §3.1 table, reconciled to ground-truth fields):

    PanelLit → progress changed. (Block-id mirroring: the built event has no block_id; state.lit is still the canonical mirror, but it is populated by gameplay.step itself when it flips the panel — app does not need a block_id from the event. App sets progress_changed = True.)
    DoorOpened → progress changed.
    DemonSpawned → no state change in app; (audio hook stub — a comment only; do not add audio). No save.
    DemonHit → no state change; read hp_remaining only if you want a debug print (optional, off by default). No save.
    DemonKilled → progress changed.
    RoomCleared → state.cleared.add(ev.room_id); progress changed. (This drives draw_room's blood-red ceiling tint, which draw_room reads from state.cleared.)
    LevelComplete → progress changed. (End sequence is a stub — a comment only.)
    ModeSwitch → set mode_switched_to = ev.to, switched_room_id = ev.room_id; progress changed. (App uses this to swap the active nav and ensure room nav is built/cached — see §7 loop. Note: gameplay.step has already set state.mode/state.current_room_id/state.pos/state.heading_rad; app does not re-set them.)
    ReadModeToggled → read_now_active = ev.on; read_asset_id = ev.asset_id. No save.
    GuidelinesRecomputed → new_targets = ev.targets. No save.

progress_changed is True if any of {PanelLit, DoorOpened, DemonKilled, RoomCleared, LevelComplete, ModeSwitch} appeared this frame.
§7 — THE PER-FRAME LOOP (authoritative §5.4 order, exact parameter passing)

Inside main()'s while loop, every frame, in this exact order:

# (0) timing
dt = FIXED_DT if smoke else clamp(perf_counter delta, ..., MAX_DT)

# (1) input
actions = poll(window, bindings)

# (2) graceful exit request (non-smoke): if actions.pause -> break

# (3) choose nav from the PRE-step mode
nav = corridor_nav if state.mode == "corridor" else room_navs[state.current_room_id]

# (4) advance game logic (mutates state.pos/heading/pitch/mode/current_room_id; returns events)
events = step(state, actions, pack, nav, dt)

# (5) apply events to mirror state + app-local UI/nav follow-ups (pure)
outcome = apply_events(state, events)

# (6) follow-ups from outcome:
#     - if outcome.mode_switched_to == "room" and outcome.switched_room_id not in room_navs:
#           room_navs[switched_room_id] = build_room_nav(pack.rooms[switched_room_id])
#     - if outcome.new_targets is not None: targets = outcome.new_targets
#     - if outcome.read_now_active is not None:
#           read_state.active = outcome.read_now_active
#           if read_state.active:
#               read_state.zoom = 1.0; read_state.pan = (0.0, 0.0)
#               read_state.master_path = _resolve_master_path(pack, outcome.read_asset_id)
#           else:
#               read_state.master_path = None

# (7) debounced save
#     if outcome.progress_changed: state_save(state, SAVE_PATH)

# (8) camera
view = camera.update(state.heading_rad, _clamp_pitch(state.pitch_rad), state.pos, dt)

# (9) clear the framebuffer (background)
_gl_clear(ctx, 0.05, 0.06, 0.08, 1.0)

# (10) render by mode
if state.mode == "corridor":
    draw_graph(view, pack.floorplan, state)
    draw_guidelines(view, pack.floorplan, targets)
else:
    room = pack.rooms[state.current_room_id]
    draw_room(view, room, pack, state)
    # ceiling tint: draw_room reads state.cleared internally for the blood-red.
    # If a separate tint uniform call is desired, it is OPTIONAL and must not
    # duplicate logic draw_room already does. Default: do nothing extra here.

# (11) read overlay (drawn over the world; world is logically paused by gameplay.step,
#      which simply emits no world-changing events while read is active)
if read_state.active and read_state.master_path is not None:
    draw_read(read_state.master_path, read_state.zoom, read_state.pan)

# (12) bloom: corridor-only post-pass. NOT REQUIRED this milestone. If shaders/render
#      do not expose a bloom hook, skip it (comment only). Do not invent a bloom pass.

# (13) present
_window_present(window)

# (14) frame bookkeeping (frame += 1; update last-time)

targets is initialized once before the loop (startup step 9 below) and only updated when a GuidelinesRecomputed event arrives (decision: app never calls select_targets itself inside the loop — gameplay.step decides when guidelines recompute and emits GuidelinesRecomputed; app just stores the result). However, you must call select_targets once at startup to seed targets for the first frames (see §8 step 9). This matches §5.4's "recompute on junction/clear event" — those recomputes come to app as events.

_resolve_master_path(pack, asset_id) — a pure helper: given the read event's asset_id (a string, may be None) and the pack, return the master PNG path for Read Mode. Look it up in pack.manifest (the manifest maps asset/block ids to master_path) and join with pack.asset_dir if the stored path is relative. If asset_id is None or not found, return None (Read becomes a no-op for that frame — draw_read is simply not called). Keep this pure and defensive; do not raise.
§8 — STARTUP SEQUENCE (inside main(), after the headless guard)

1. if not HAVE_GL: return 0          # headless smoke — FIRST line of main()
2. import moderngl                    # lazy, inside main() only
3. try:
4.     window, ctx = _unpack_window(make_window(1280, 720, "QUAKE — Golden Level"))
5.     wire_prog   = wire_program(ctx)
6.     solid_prog  = solid_program(ctx)
7.     blit_prog   = blit_program(ctx)        # compiled now even if only used by readmode
8.     pack = load_pack(PACK_DIR)             # PACK_DIR constant; default "tests/golden_pack/"
9.     corridor_nav = build_corridor_nav(pack.floorplan)
10.    cfg = BuildConfig()
11.    try:
           state = state_load(SAVE_PATH, pack)   # best-effort resume
       except Exception:
           state = new_state(pack)               # fresh start in corridor at the start room
12.    camera = Camera()
13.    room_navs = {}                            # lazily filled on mode switch
14.    read_state = ReadState()                  # active=False, zoom=1.0, pan=(0,0), master_path=None
15.    # seed guidelines for the first frames:
       current = state.current_room_id or _start_node(pack)   # see note
       targets = select_targets(pack.floorplan, current, state.cleared, cfg)
16. except Exception as e:
17.    print(f"[QUAKE] startup failed: {e}", file=sys.stderr)
18.    return 1
19. enter frame loop (§7), inside its own try/finally

Note on step 15 current: in corridor mode state.current_room_id may be None (you are between rooms). select_targets needs a current NodeId. Use state.current_room_id if set, else derive the nearest/start node. Keep a tiny pure helper _start_node(pack) that returns a deterministic node id — e.g. the first room id in pack.floorplan ordering — so startup never crashes. If select_targets itself can tolerate a sensible start node, this is enough; if it raises on a bad current, fall back to targets = [].

BuildConfig, Camera, ReadState are the only objects app constructs. ReadState is defined in app.py.
§9 — SHUTDOWN SEQUENCE

In the loop's finally block (always runs, even on exception inside the loop):

1. try: state_save(state, SAVE_PATH)   # auto-save on exit; never let this raise out
   except Exception as e: print(f"[QUAKE] save-on-exit failed: {e}", file=sys.stderr)
2. _close_window(window)               # the existing defensive helper
3. (return 0 is reached after the try/finally)

main() returns 0 on clean exit (smoke completion or window close), 1 only on startup failure.
§10 — PRESERVED M0 PATTERNS (keep these verbatim in shape)

    Module docstring updated to describe the full loop, keeping the COORDINATES ARE LAW paragraph.
    if not HAVE_GL: return 0 is the first statement of main().
    import moderngl is lazy (inside main()), never at module top.
    Keep these integration wrappers (extend the set as needed, same style — one tiny function each, isolating any uncertain external API):
        _gl_clear(ctx, r, g, b, a) — verbatim.
        _unpack_window(made) — verbatim.
        _close_window(window) — verbatim.
        _window_should_close(window) — verbatim (getattr(window, "has_exit", False)).
        _window_present(window) — verbatim (dispatch_events then flip if present).
    _SMOKE_FRAMES = 60 module constant + the smoke = _SMOKE_FRAMES > 0 branch.
    if __name__ == "__main__": raise SystemExit(main()) at the bottom — verbatim (matches the CI command exactly).
    Remove from the stub: _solid_triangle_vertices, _wire_line_vertices, _identity_view, event_dispatch, _collect_events, _gl_render_triangle, _gl_render_line, _gl_make_vbo, _gl_make_vao, _gl_set_uniform_mvp. (App no longer uploads raw geometry or sets MVP — the render modules own all of that. If you find you need a matrix write at the GL boundary, you do not: camera.update returns the view and the render modules consume it via their own programs.)

Module-level constants to add at the top:

PACK_DIR = "tests/golden_pack/"
SAVE_PATH = "savegame.json"
PITCH_CLAMP_RAD = 1.2217
MAX_DT = 1.0 / 20.0
FIXED_DT = 1.0 / 60.0
_SMOKE_FRAMES = 60

§11 — PURE / SHELL SPLIT (the testable boundary)

PURE (no GL, no window, no IO — unit-testable headlessly):

    apply_events(state, events) -> FrameOutcome
    _resolve_master_path(pack, asset_id) -> str | None
    _clamp_pitch(pitch) -> float
    _start_node(pack) -> NodeId
    ReadState / FrameOutcome dataclasses
    (Anything else logic-shaped you factor out — keep it pure.)

SHELL (GL / window / IO — only here):

    main()
    the _gl_* and _window_* integration wrappers
    the lazy import moderngl

A reviewer must be able to import app with HAVE_GL = False and call every PURE function with fabricated GameState/Pack/Event objects, with zero GL/window touched. main() under HAVE_GL = False returns 0 without importing moderngl or opening anything.
§12 — SMOKE TEST SPECIFICATION

The smoke test is the canonical proof. With HAVE_GL = True, main():

    opens the window, compiles all three shader programs,
    loads tests/golden_pack/ via load_pack,
    builds corridor nav, creates state (fresh or resumed),
    runs exactly 60 frames of the full §7 loop with poll returning whatever it returns (zero input is fine; the loop ticks),
    auto-saves and closes,
    returns 0.

CI invocation (must return exit code 0):

python -c "from app import main; raise SystemExit(main())"

Under headless CI (HAVE_GL = False), the same command returns 0 immediately after the guard.
§13 — ACCEPTANCE GATES (all must pass)

    Gate 1 — python -c "from app import main; raise SystemExit(main())" headless (HAVE_GL=False) returns 0, importing no GL.
    Gate 2 — Full existing test suite stays 283/283 green (you changed only app.py).
    Gate 3 — With HAVE_GL=True, main() opens a window, loads the golden pack, runs 60 frames, exits 0.
    Gate 4 — load_pack("tests/golden_pack/") is called from main() and succeeds.
    Gate 5 — No regressions in any per-module test.
    Gate 6 (PURE/SHELL) — Every PURE function (§11) is callable headlessly with fabricated inputs and touches no GL/window/IO.

§14 — HARD CONSTRAINTS / RISK FLAGS (do not violate)

    Write only app.py. Change no other file.
    Use the exact frozen signatures in §3 — exact names, exact parameter counts. The ground-truth event fields in §2 (hp_remaining, no block_id, via_edge_id, door_at) are correct; the older Second Canon design is not.
    App builds no meshes and passes no mesh to any draw call.
    App does not move the player, cast rays, clamp pitch into state, select read targets, or decide mode switches — gameplay.step owns all of that. App mirrors progress (lit, cleared), swaps nav, drives the read overlay, debounce-saves, and renders.
    Do not import anything outside: the §3 modules + contracts (for BuildConfig) + stdlib + moderngl + pyglet + numpy.
    Headless guard is sacred: import app and main() under HAVE_GL=False must do zero GL.
    Do not add audio, bloom, or an end-sequence — those are explicit stubs (comments only) this milestone.

This is the central nervous system. Wire it precisely, and the golden level lights up. 🧠⚡
