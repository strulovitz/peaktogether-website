"""input_actions.py — QUAKE runtime engine, M1 module #5.

The semantic action layer. Raw device events NEVER leak past this module.
Produces one Actions snapshot per frame for BOTH players (mover + shooter)
folded into a single frozen Actions struct.

STRUCTURE:
  - PURE CORE: RawSample, EdgeTracker, build_actions, _clamp.
      Plain dataclasses + functions on numbers. Zero pyglet/moderngl,
      zero file/window. This is the fully unit-tested path.
  - THIN SHELL: poll(window, bindings). Touches pyglet. Guarded so that
      importing this module headless (no GL context) never crashes; poll
      is simply not exercised in that case.

LOCKED INVARIANTS:
  - heading_delta / pitch_delta are MOVER-only.
  - aim_x / aim_y are SHOOTER-only.
  - The Shooter has NO yaw/pitch authority: build_actions never writes
    heading/pitch from shooter inputs (structural enforcement).
  - Edge fields (fire, read_toggle, interact, pause) are TRUE for exactly
    one frame on the False->True press transition.
"""

from __future__ import annotations

from dataclasses import dataclass

# RULE 1: import every shared type from contracts. NEVER redefine Actions.
from contracts import Actions

# --------------------------------------------------------------------------
# PINNED CONSTANTS
# --------------------------------------------------------------------------
DEFAULT_YAW_SENS = 2.2     # rad/s per unit input
DEFAULT_PITCH_SENS = 1.8

_DEFAULT_DT = 0.016        # ~60fps safe default for the first poll()


# --------------------------------------------------------------------------
# PURE CORE
# --------------------------------------------------------------------------
@dataclass
class RawSample:
    """What the shell extracts from devices this frame.

    Buttons here are CURRENT down-state (level, not edge). Edge detection is
    done downstream by EdgeTracker so the core stays pure & testable.
    """
    # mover
    mover_axis_x: float
    mover_axis_y: float
    mover_yaw_rate: float
    mover_pitch_rate: float
    # shooter
    shooter_aim_x: float
    shooter_aim_y: float
    shooter_fire_down: bool
    # shared buttons (current down-state, level not edge)
    read_down: bool
    interact_down: bool
    pause_down: bool


class EdgeTracker:
    """Holds previous down-states; .edges(sample) -> dict of bool edges.

    fire/read/interact/pause become True only on a False->True transition.
    Internally stores the previous down-state for each edge-tracked button.
    On first call, previous states are False so a button that starts
    held-down does NOT trigger an edge.
    """

    def __init__(self) -> None:
        self._prev_fire = False
        self._prev_read = False
        self._prev_interact = False
        self._prev_pause = False

    def edges(self, sample: RawSample) -> dict[str, bool]:
        """Return edge flags. True ONLY on the False->True transition."""
        fire = bool(sample.shooter_fire_down) and not self._prev_fire
        read = bool(sample.read_down) and not self._prev_read
        interact = bool(sample.interact_down) and not self._prev_interact
        pause = bool(sample.pause_down) and not self._prev_pause

        # Update stored previous down-states for next frame.
        self._prev_fire = bool(sample.shooter_fire_down)
        self._prev_read = bool(sample.read_down)
        self._prev_interact = bool(sample.interact_down)
        self._prev_pause = bool(sample.pause_down)

        return {
            "fire": fire,
            "read_toggle": read,
            "interact": interact,
            "pause": pause,
        }


def _clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def build_actions(
    sample: RawSample,
    prev: EdgeTracker,
    dt: float,
    cfg_yaw_sens: float,
    cfg_pitch_sens: float,
) -> Actions:
    """Build a frozen Actions from one frame's raw inputs.

    heading_delta / pitch_delta come EXCLUSIVELY from mover_yaw_rate /
    mover_pitch_rate. Shooter fields (shooter_aim_x/y) do NOT affect
    heading/pitch — that is the structural enforcement of
    'mover-owns-rotation'.
    """
    edges = prev.edges(sample)

    return Actions(
        # MOVER (owns the body) — rotation derives ONLY from mover rates.
        move_x=float(_clamp(sample.mover_axis_x, -1.0, 1.0)),
        move_y=float(_clamp(sample.mover_axis_y, -1.0, 1.0)),
        heading_delta=float(sample.mover_yaw_rate * cfg_yaw_sens * dt),
        pitch_delta=float(sample.mover_pitch_rate * cfg_pitch_sens * dt),
        # SHOOTER (owns the reticle) — NO yaw/pitch authority.
        aim_x=float(_clamp(sample.shooter_aim_x, -1.0, 1.0)),
        aim_y=float(_clamp(sample.shooter_aim_y, -1.0, 1.0)),
        fire=edges["fire"],
        fire_held=bool(sample.shooter_fire_down),
        # SHARED edges.
        read_toggle=edges["read_toggle"],
        interact=edges["interact"],
        pause=edges["pause"],
    )


# --------------------------------------------------------------------------
# BINDINGS CONVENTION (OUR frozen shape)
# --------------------------------------------------------------------------
DEFAULT_BINDINGS = {
    "mover": {
        "device": "keyboard",
        "axis_x": ["a", "d"],        # A=left(-1), D=right(+1)
        "axis_y": ["w", "s"],        # W=forward(+1), S=back(-1)
        "yaw": "mouse_dx",
        "pitch": "mouse_dy",
    },
    "shooter": {
        "device": "mouse",
        "aim_x": "mouse_dx",
        "aim_y": "mouse_dy",
        "fire": "mouse_left",
    },
    "shared": {
        "read": "r",
        "interact": "e",
        "pause": "escape",
        "ceiling": "c",
    },
}


# --------------------------------------------------------------------------
# THIN SHELL — isolated pyglet integration.
# Every uncertain external API call is wrapped behind ONE tiny function with
# an "INTEGRATION: confirm exact API" comment so the compile loop fixes it
# in exactly one place.
# --------------------------------------------------------------------------

# Module-owned shell state. The pure core is stateless w.r.t. this; tests
# never touch these.
_SHELL_TRACKER: EdgeTracker | None = None
_SHELL_LAST_TIME: float | None = None


def _now() -> float:
    """Monotonic seconds. Isolated for testability/substitution."""
    import time
    return time.perf_counter()


def _key_down(window, key_name: str) -> bool:
    """Is the named key currently held down?

    Uses manual _pressed: set[int] set on window._quake_keystate
    (pyglet 2.1.14 KeyStateHandler is broken on Windows).
    """
    try:
        import pyglet
        pressed = getattr(window, "_quake_keystate", None)
        if pressed is None:
            return False
        symbol = getattr(pyglet.window.key, key_name.upper(), None)
        if symbol is None:
            return False
        return symbol in pressed
    except Exception:
        return False


def _mouse_delta(window) -> tuple[float, float]:
    """Accumulated mouse (dx, dy) since last poll, then reset.

    Uses window._quake_mousedx() which returns (dx, dy) and resets internally.
    """
    try:
        fn = getattr(window, "_quake_mousedx", None)
        if fn is None:
            return (0.0, 0.0)
        return fn()
    except Exception:
        return (0.0, 0.0)


def _mouse_left_down(window) -> bool:
    """Is the left mouse button currently held?

    Uses window._quake_mouseleft() which returns bool.
    """
    try:
        fn = getattr(window, "_quake_mouseleft", None)
        if fn is None:
            return False
        return bool(fn())
    except Exception:
        return False


def _axis_pair(window, neg_key: str, pos_key: str) -> float:
    """Two keys → a [-1, 1] axis (neg=-1, pos=+1, both/neither=0)."""
    neg = 1.0 if _key_down(window, neg_key) else 0.0
    pos = 1.0 if _key_down(window, pos_key) else 0.0
    return pos - neg


def _read_raw_sample(window, bindings, gamepad=None) -> RawSample:
    mover = bindings.get("mover", {})
    shooter = bindings.get("shooter", {})
    shared = bindings.get("shared", {})

    # --- mover movement axes (keyboard default) ---
    ax = mover.get("axis_x", ["a", "d"])
    ay = mover.get("axis_y", ["w", "s"])
    mover_axis_x = _axis_pair(window, ax[0], ax[1])
    fwd = 1.0 if _key_down(window, ay[0]) else 0.0     # W=forward(+1)
    back = 1.0 if _key_down(window, ay[1]) else 0.0    # S=back(-1)
    mover_axis_y = fwd - back

    # --- mover look rates (mouse) ---
    mdx, mdy = _mouse_delta(window)
    mover_yaw_rate = mdx if mover.get("yaw") == "mouse_dx" else 0.0
    mover_pitch_rate = mdy if mover.get("pitch") == "mouse_dy" else 0.0

    # --- shooter aim (mouse delta by default) ---
    shooter_aim_x = mdx if shooter.get("aim_x") == "mouse_dx" else 0.0
    shooter_aim_y = mdy if shooter.get("aim_y") == "mouse_dy" else 0.0
    shooter_fire_down = _mouse_left_down(window) if shooter.get("fire") == "mouse_left" else False

    # --- controllers (ADDITIVE on top of keyboard/mouse; Parent 23) ---
    if gamepad is not None:
        try:
            g = gamepad.read()
            mover_axis_x += g.move_x
            mover_axis_y += g.move_y
            mover_yaw_rate += g.yaw_rate
            mover_pitch_rate += g.pitch_rate
            shooter_aim_x += g.aim_x
            shooter_aim_y += g.aim_y
            shooter_fire_down = shooter_fire_down or g.fire_down
        except Exception:
            pass  # any controller hiccup -> keyboard/mouse only, no crash

    # --- shared buttons (level down-state) ---
    read_down = _key_down(window, shared.get("read", "r"))
    interact_down = _key_down(window, shared.get("interact", "e"))
    pause_down = _key_down(window, shared.get("pause", "escape"))

    return RawSample(
        mover_axis_x=mover_axis_x, mover_axis_y=mover_axis_y,
        mover_yaw_rate=mover_yaw_rate, mover_pitch_rate=mover_pitch_rate,
        shooter_aim_x=shooter_aim_x, shooter_aim_y=shooter_aim_y,
        shooter_fire_down=shooter_fire_down,
        read_down=read_down, interact_down=interact_down, pause_down=pause_down,
    )


def poll(window, bindings, gamepad=None) -> Actions:
    global _SHELL_TRACKER, _SHELL_LAST_TIME
    if _SHELL_TRACKER is None:
        _SHELL_TRACKER = EdgeTracker()
    now = _now()
    if _SHELL_LAST_TIME is None:
        dt = _DEFAULT_DT
    else:
        dt = max(0.0, now - _SHELL_LAST_TIME)
    _SHELL_LAST_TIME = now
    if bindings is None:
        bindings = DEFAULT_BINDINGS
    sample = _read_raw_sample(window, bindings, gamepad)
    return build_actions(sample, _SHELL_TRACKER, dt, DEFAULT_YAW_SENS, DEFAULT_PITCH_SENS)
