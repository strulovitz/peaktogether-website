"""
quake/app.py — full per-frame loop (the §5.4 central nervous system).

Replaces the M0 stub. OWNS NO GAME LOGIC: gameplay.step() is the single source
of truth for movement, firing, mode switches, demons, panels, and progress. This
file WIRES the 13 frozen engine modules into the authoritative §5.4 loop, mirrors
progress into state, swaps nav on mode switch, drives the Read-Mode overlay, and
debounce-saves on progress events.

SPLIT:
  - PURE CORE: apply_events / _resolve_master_path / _clamp_pitch / _start_node /
    ReadState / FrameOutcome / _read_toggle_pick — plain functions & dataclasses,
    zero GL/window/IO (headlessly unit-testable).
  - THIN SHELL: main() — window/GL/loop. Guarded so import never needs a GL
    context; if HAVE_GL is False, main() returns 0 immediately (headless smoke).

COORDINATES ARE LAW: floorplan is the XZ map-plane, Y is up. Math is row-major
internally; we transpose only at the GL boundary if a call wants column-major.
Heading forward = (cos h, 0, sin h). Eye is the player pos + EYE_HEIGHT_M on Y.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import numpy as np  # noqa: F401  (kept for parity / view-matrix typing at the boundary)

# Shared frozen contracts.
from contracts import BuildConfig

# Frozen collaborator signatures (talk only through these).
from glguard import HAVE_GL
from gfx_context import make_window
from shaders import wire_program, solid_program, blit_program
from assets import load_pack
from state import new_state, load as state_load, save as state_save
from input_actions import poll
from camera import Camera, perspective, FOV_Y_DEG, NEAR_M, FAR_M
from nav_collision import build_corridor_nav, build_room_nav
from gameplay import step, reticle_ray
from guidelines import select_targets, draw_guidelines
from render_wire import draw_graph, render_mode_a
from render_room import draw_room
from readmode import draw_read
from minimap import draw_minimap, marker_mood, MOVE_THRESHOLD_M
from logutil import log as _log


# ---------------------------------------------------------------------------
# MODULE CONSTANTS
# ---------------------------------------------------------------------------

PACK_DIR = str(Path(__file__).parent / "levels" / "principia_bk1_inverse_square" / "pack")
SAVE_PATH = str(Path(__file__).parent / "savegame.json")

PITCH_CLAMP_RAD = 1.2217          # ±70°
EYE_HEIGHT_M = 1.6
READ_MAX_DIST = 6.0

MAX_DT = 1.0 / 20.0               # clamp dt to avoid spiral-of-death after a stall
FIXED_DT = 1.0 / 60.0             # deterministic dt in smoke mode / first frame

WINDOW_W = 1280
WINDOW_H = 720
WINDOW_TITLE = "QUAKE — Golden Level"

_SMOKE_FRAMES = 0

# Events that change persisted progress -> trigger a debounced save.
_PROGRESS_EVENTS = frozenset(
    {"panel_lit", "door_opened", "demon_killed", "room_cleared",
     "level_complete", "mode_switch"}
)


# ---------------------------------------------------------------------------
# PURE CORE (fully testable headless — no GL, no window, no IO)
# ---------------------------------------------------------------------------

@dataclass
class ReadState:
    """Transient Read-Mode overlay UI state. NOT persisted (it is not progress)."""
    active: bool = False
    zoom: float = 1.0
    pan: tuple = (0.0, 0.0)            # Vec2; not driven this milestone
    master_path: Optional[str] = None


@dataclass
class FrameOutcome:
    """What one frame's events imply for app-local follow-ups (pure summary)."""
    progress_changed: bool = False
    mode_switched_to: Optional[str] = None      # "corridor" | "room" | None
    switched_room_id: Optional[str] = None
    travel_edge_id: Optional[str] = None        # when entering corridor via a specific door
    read_toggle_signaled: bool = False          # gameplay emitted read_toggled(on=True)
    recompute_guidelines: bool = False          # gameplay emitted GuidelinesRecomputed


def _clamp_pitch(pitch: float) -> float:
    """Clamp pitch into the legal look range. Pure."""
    if pitch > PITCH_CLAMP_RAD:
        return PITCH_CLAMP_RAD
    if pitch < -PITCH_CLAMP_RAD:
        return -PITCH_CLAMP_RAD
    return pitch


def _start_node(pack: Any) -> Optional[str]:
    """Deterministic fallback start node id. fp.rooms is list[FloorRoom];
    FloorRoom.room_id: NodeId. Pure & defensive."""
    fp = pack.floorplan
    rooms = getattr(fp, "rooms", None)
    if rooms and len(rooms) > 0:
        return getattr(rooms[0], "room_id", None)
    return None


def apply_events(state: Any, events: List[Any]) -> FrameOutcome:
    """Apply one frame's events to the progress-mirror fields of state and
    summarize app-local follow-ups. PURE: no GL, no IO.

    gameplay.step has ALREADY mutated state.pos / heading / pitch / mode /
    current_room_id; this function only touches state.lit, state.cleared, and
    reports follow-ups (nav swap, guideline recompute, read toggle, save)."""
    out = FrameOutcome()
    for ev in events:
        kind = ev.event
        if kind == "room_cleared":
            state.cleared.add(ev.room_id)
        elif kind == "mode_switch":
            out.mode_switched_to = ev.to
            out.switched_room_id = ev.room_id
            out.travel_edge_id = getattr(ev, "via_edge_id", None)
        elif kind == "read_toggled":
            # gameplay only ever emits on=True as a "the player pressed read"
            # signal; app owns the actual on/off toggle and panel resolution.
            if ev.on:
                out.read_toggle_signaled = True
        elif kind == "guides":
            # targets list is a signal (always []); app recomputes itself.
            out.recompute_guidelines = True
        # panel_lit / door_opened / demon_killed / level_complete: the mirror
        # sets (state.lit etc.) are maintained inside gameplay.step; app only
        # needs to know progress changed so it can debounce-save. demon_spawned
        # / demon_hit are transient and do NOT change persisted progress.

        if kind in _PROGRESS_EVENTS:
            out.progress_changed = True
    return out


def _resolve_master_path(pack: Any, asset_id: Optional[str]) -> Optional[str]:
    """Resolve a panel asset id to its high-res Read-Mode master PNG path.
    Returns an absolute-ish path (asset_dir joined with the manifest's relative
    master_path), or None if the lookup fails (Read becomes a safe no-op).
    PURE & defensive: never raises."""
    if not asset_id:
        return None
    try:
        entry = pack.manifest.assets.get(asset_id)
    except Exception:
        return None
    if entry is None:
        return None
    rel = getattr(entry, "master_path", None)
    if not rel:
        return None
    base = (pack.asset_dir or "").rstrip("/")
    if base:
        return base + "/" + str(rel).lstrip("/")
    return str(rel)


def _read_toggle_pick(read_state: ReadState, state: Any, actions: Any,
                      nav: Any, pack: Any) -> ReadState:
    """Apply a read-toggle press: flip active; on turn-ON, cast the reticle ray
    (byte-identical to the shoot ray) and resolve the looked-at panel's master.
    Returns the updated ReadState. PURE w.r.t. GL/IO (uses only the injected nav,
    gameplay.reticle_ray, and the pack/manifest; touches no GL or window)."""
    if read_state.active:
        # Second press -> turn OFF; clear the overlay.
        return ReadState(active=False, zoom=1.0, pan=(0.0, 0.0), master_path=None)

    # First press -> turn ON; pick the panel the reticle ray hits.
    eye = (state.pos[0], state.pos[1] + EYE_HEIGHT_M, state.pos[2])
    ray = reticle_ray(eye, state.heading_rad, state.pitch_rad,
                      actions.aim_x, actions.aim_y)
    master_path = None
    try:
        hit = nav.nearest_panel(ray, READ_MAX_DIST)
    except Exception:
        hit = None
    if hit is not None:
        master_path = _resolve_master_path(pack, hit.asset_on_id)

    if master_path is None:
        # Nothing readable in view -> Read stays a no-op (do not flip on).
        return ReadState(active=False, zoom=1.0, pan=(0.0, 0.0), master_path=None)

    return ReadState(active=True, zoom=1.0, pan=(0.0, 0.0), master_path=master_path)


# ---------------------------------------------------------------------------
# INTEGRATION WRAPPERS — every uncertain external API is isolated here, one
# tiny function each. Do NOT assert these API names elsewhere as fact.
# (Preserved verbatim from the M0 stub; raw-geometry wrappers removed.)
# ---------------------------------------------------------------------------

def _single_corridor_floorplan(fp, edge_id):
    """Build a minimal Floorplan with just the 2 rooms + 1 corridor for edge_id.
    Falls back to the full floorplan if the corridor is not found."""
    from map.raw_models import Floorplan as _FP
    corridor = None
    # Match by corridor_id, or by source/target pair from edge_id pattern
    parts = edge_id.split(".to.")
    src_cand = parts[0].replace("edge.", "") if len(parts) == 2 else None
    tgt_cand = parts[1] if len(parts) == 2 else None
    for c in fp.corridors:
        if c.corridor_id == edge_id:
            corridor = c
            break
        if src_cand and tgt_cand and (
            (c.source == src_cand and c.target == tgt_cand) or
            (c.source == tgt_cand and c.target == src_cand)
        ):
            corridor = c
            break
    if corridor is None:
        return fp
    src_room = None
    tgt_room = None
    for r in fp.rooms:
        if r.room_id == corridor.source:
            src_room = r
        if r.room_id == corridor.target:
            tgt_room = r
    return _FP(
        schema_version=fp.schema_version,
        level_id=fp.level_id,
        seed=fp.seed,
        rooms=[r for r in (src_room, tgt_room) if r is not None],
        corridors=[corridor],
        crossings=[],
    )

# Module-level active-corridor state (non-persisted, reset on room entry)
_active_corridor = [None, None]  # [floorplan, nav] — list to avoid global keyword

def _gl_clear(ctx: Any, r: float, g: float, b: float, a: float) -> None:
    ctx.clear(r, g, b, a)


def _unpack_window(made: Any):
    if isinstance(made, tuple) and len(made) == 2:
        return made[0], made[1]
    return getattr(made, "window", made), getattr(made, "ctx", made)


def _close_window(window: Any) -> None:
    if window is not None and hasattr(window, "close"):
        try:
            window.close()
        except Exception:
            pass


def _window_should_close(window: Any) -> bool:
    return bool(getattr(window, "has_exit", False))


def _window_present(window: Any) -> None:
    if hasattr(window, "dispatch_events"):
        window.dispatch_events()
    if hasattr(window, "flip"):
        window.flip()


# ---------------------------------------------------------------------------
# THIN SHELL — main(). Skips all GL work headlessly; returns 0 cleanly.
# ---------------------------------------------------------------------------

def main(smoke_frames: int = _SMOKE_FRAMES) -> int:
    """Full per-frame loop. Returns 0 on clean exit, 1 on startup failure.

    Headless (no GL): returns 0 immediately — the smoke-launch path.
    """
    if not HAVE_GL:
        _log("main: HAVE_GL=False, exiting (headless)")
        return 0

    _log("main: HAVE_GL=True, starting window+GL setup")
    import moderngl  # noqa: F401  (lazy: import must never need a GL context)

    # ---- STARTUP (any failure here -> stderr + return 1) ------------------
    try:
        _log("main: creating window")
        window, ctx = _unpack_window(make_window(WINDOW_W, WINDOW_H, WINDOW_TITLE))
        _log("main: window created OK")

        # Compile all three programs now (blit is used by the read overlay).
        _log("main: compiling shaders")
        wire_program(ctx)
        solid_program(ctx)
        blit_program(ctx)
        _log("main: shaders compiled OK")

        _log(f"main: loading pack from {PACK_DIR}")
        pack = load_pack(PACK_DIR)
        _log(f"main: pack loaded, {len(pack.floorplan.rooms)} rooms")
        corridor_nav = build_corridor_nav(pack.floorplan)
        _log("main: corridor nav built")
        cfg = BuildConfig()

        # Best-effort resume; a bad/absent save is never fatal.
        try:
            state = state_load(SAVE_PATH, pack)
            # If savegame has old corridor-mode state, restart in a room (keep progress)
            if state.mode != "room" or state.current_room_id is None:
                _log("main: stale savegame (corridor mode) — restarting in first room")
                fresh = new_state(pack)
                state.pos = fresh.pos
                state.heading_rad = fresh.heading_rad
                state.mode = fresh.mode
                state.current_room_id = fresh.current_room_id
            else:
                _log("main: save loaded")
        except Exception:
            state = new_state(pack)
            _log("main: fresh state created")

        camera = Camera()
        _log("main: entering frame loop")
        room_navs: dict = {}                  # lazily filled on ModeSwitch -> room

        # Start in a room directly — build its nav now.
        if state.mode == "room" and state.current_room_id is not None:
            room_data = pack.rooms.get(state.current_room_id)
            if room_data is not None:
                room_navs[state.current_room_id] = build_room_nav(room_data)
                _log(f"main: room nav built for {state.current_room_id}")

        read_state = ReadState()

        # Seed guidelines for the first frames. current_room_id may be None in
        # the corridor; fall back to the first room in floorplan order.
        bindings = None                       # poll handles None -> uses DEFAULT_BINDINGS
        current = state.current_room_id or _start_node(pack)
        try:
            targets = select_targets(pack.floorplan, current, state.cleared, cfg) \
                if current is not None else []
        except Exception:
            targets = []
    except Exception as e:
        import traceback
        _log(f"main: STARTUP CRASHED: {e}")
        traceback.print_exc(file=sys.stderr)
        return 1

    # ---- FRAME LOOP -------------------------------------------------------
    smoke = smoke_frames > 0
    frame = 0
    last_t = time.perf_counter()
    gcur = _start_node(pack)
    # Track where the player arrived (for the 'moved 1 m' marker mood).
    arrival_room = state.current_room_id
    arrival_pos = tuple(state.pos)

    try:
        while True:
            if smoke and frame >= smoke_frames:
                break
            if not smoke and _window_should_close(window):
                break

            # (0) timing
            if smoke:
                dt = FIXED_DT
            else:
                now = time.perf_counter()
                dt = now - last_t
                last_t = now
                if dt <= 0.0:
                    dt = FIXED_DT
                elif dt > MAX_DT:
                    dt = MAX_DT

            # (1) input
            try:
                actions = poll(window, bindings)
            except Exception as e:
                _log(f"frame {frame}: poll() crashed: {e}")
                raise

            # (2) graceful-exit request (non-smoke): semantic pause -> quit
            if not smoke and getattr(actions, "pause", False):
                _log(f"frame {frame}: pause/ESC — quitting")
                break

            # (3) choose nav from the PRE-step mode
            if state.mode == "corridor":
                nav = _active_corridor[1] if _active_corridor[1] is not None else corridor_nav
            else:
                nav = room_navs.get(state.current_room_id)
                if nav is None:
                    # Defensive: room nav should have been built on the switch,
                    # but ensure it exists before stepping.
                    nav = build_room_nav(pack.rooms[state.current_room_id])
                    room_navs[state.current_room_id] = nav

            # (4) advance game logic (mutates pos/heading/pitch/mode/room; -> events)
            try:
                events = step(state, actions, pack, nav, dt)
            except Exception as e:
                _log(f"frame {frame}: step() crashed: {e}")
                raise

            # (5) apply events to mirror state + summarize follow-ups (pure)
            outcome = apply_events(state, events)
            if outcome.mode_switched_to:
                _log(f"frame {frame}: mode switch -> {outcome.mode_switched_to} room={outcome.switched_room_id}")

            # (6) follow-ups
            # 6a) build/cache room nav on a switch into a room
            if outcome.mode_switched_to == "room" and outcome.switched_room_id is not None:
                if outcome.switched_room_id not in room_navs:
                    room_navs[outcome.switched_room_id] = \
                        build_room_nav(pack.rooms[outcome.switched_room_id])
                _active_corridor[0] = None
                _active_corridor[1] = None
                # Just teleported: reset the 'moved 1 m' arrival tracker.
                arrival_room = outcome.switched_room_id
                arrival_pos = tuple(state.pos)

            # 6d) entering corridor via a specific door -> build single-corridor fp
            if outcome.mode_switched_to == "corridor" and outcome.travel_edge_id is not None:
                _active_corridor[0] = _single_corridor_floorplan(
                    pack.floorplan, outcome.travel_edge_id)
                _active_corridor[1] = build_corridor_nav(_active_corridor[0])
                _log(f"frame {frame}: single-corridor mode for edge {outcome.travel_edge_id}")

            # 6b) recompute guidelines when signaled (gameplay sends targets=[])
            if outcome.recompute_guidelines:
                if state.mode == "corridor" and outcome.travel_edge_id is not None:
                    parts = outcome.travel_edge_id.split(".to.")
                    src_cand = parts[0].replace("edge.", "") if len(parts) == 2 else None
                    gcur = src_cand if src_cand else (state.current_room_id or _start_node(pack))
                else:
                    gcur = state.current_room_id or _start_node(pack)
                try:
                    targets = select_targets(pack.floorplan, gcur, state.cleared, cfg) \
                        if gcur is not None else []
                except Exception:
                    targets = []

            # 6c) read-mode toggle (app owns on/off + panel pick; uses CURRENT nav)
            if outcome.read_toggle_signaled:
                read_state = _read_toggle_pick(read_state, state, actions, nav, pack)

            # (7) debounced save (event-driven, at most once per frame)
            if outcome.progress_changed:
                try:
                    state_save(state, SAVE_PATH)
                except Exception as e:
                    print(f"[QUAKE] save failed: {e}", file=sys.stderr)

            # (8) camera -> pure view matrix
            view = camera.update(state.heading_rad, _clamp_pitch(state.pitch_rad),
                                 state.pos, dt)

            # (8b) projection (shared source of truth; live window size, resizable-safe)
            w = int(getattr(window, "width", WINDOW_W))
            h = int(getattr(window, "height", WINDOW_H))
            proj = perspective(FOV_Y_DEG, w / max(h, 1), NEAR_M, FAR_M)
            mvp = np.ascontiguousarray(proj @ view, dtype=np.float32)   # world->clip for Mode B

            # (10) render by mode
            try:
                if state.mode == "corridor":
                    render_fp = pack.floorplan
                    def _gl(v, p, aspect):
                        vp = np.ascontiguousarray(p @ v, dtype=np.float32)
                        draw_guidelines(vp, render_fp, targets, gcur)
                    render_mode_a(ctx, window, view, proj, render_fp, state,
                                  guidelines_fn=_gl, targets=targets)
                else:
                    _gl_clear(ctx, 0.05, 0.06, 0.08, 1.0)
                    room = pack.rooms[state.current_room_id]
                    draw_room(mvp, room, pack, state)
            except Exception as e:
                _log(f"frame {frame}: render crashed: {e}")
                raise

            # (11) read overlay (drawn over the world)
            if read_state.active and read_state.master_path is not None:
                draw_read(read_state.master_path, read_state.zoom, read_state.pan)

            # (11b) corner minimap HUD (flat pivot) — over the room, not in Read Mode
            if state.mode == "room" and not read_state.active:
                try:
                    if state.current_room_id == arrival_room:
                        ddx = state.pos[0] - arrival_pos[0]
                        ddz = state.pos[2] - arrival_pos[2]
                        moved = (ddx * ddx + ddz * ddz) > (MOVE_THRESHOLD_M ** 2)
                    else:
                        moved = False
                    mood = marker_mood(state, pack.floorplan.level_id,
                                       state.current_room_id, moved)
                    draw_minimap(pack.floorplan, state, pack.floorplan.level_id,
                                 w, h, mood)
                except Exception as e:
                    _log(f"frame {frame}: minimap crashed: {e}")

            # (12) bloom: corridor-only post-pass — deferred this milestone (no hook).

            # (13) present
            _window_present(window)

            # (14) bookkeeping
            frame += 1
    finally:
        _log("main: frame loop exited")
        # Auto-save on exit; never let shutdown raise out of main().
        try:
            state_save(state, SAVE_PATH)
            _log("main: auto-save OK")
        except Exception as e:
            _log(f"main: save-on-exit failed: {e}")
        _close_window(window)
        _log("main: window closed, returning")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
