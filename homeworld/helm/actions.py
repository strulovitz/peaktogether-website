"""THE FROZEN ACTION LIST (NEW_TESTAMENT 2.2, version 1).

Game logic imports these names and NEVER imports pyglet key codes.
Adding a new action later = allowed with a minor version bump.
Renaming or removing an action = forbidden without owner approval.
"""

from dataclasses import dataclass

ACTIONS_VERSION = 1

# ---- Pilot: continuous axes (value in [-1.0, +1.0], polled) ----
PILOT_AXES = [
    "CAM_YAW", "CAM_PITCH", "CAM_ZOOM",      # camera orbit control
    "TRIM_X", "TRIM_Y", "TRIM_Z",            # thruster trim (Bible 2.1)
]

# ---- Pilot: buttons (events: value 1.0 press / 0.0 release) ----
PILOT_BUTTONS = [
    "SELECT_NEXT", "SELECT_PREV",            # cycle ships
    "SQUAD_NEXT", "SQUAD_PREV",              # cycle squads
    "ORDER_CONFIRM", "ORDER_CANCEL",
    "ACTION_PRIMARY",                        # fire / execute (context action)
    "ACTION_SECONDARY",                      # context action 2 (e.g. dock)
    "FLIGHT_MODE_TOGGLE",                    # component vs diagonal (Bible 2.1)
    "CAM_MODE_CYCLE",                        # ORBIT -> FOLLOW -> POV
    "PAUSE",
]

# ---- System buttons (either player, always active) ----
SYSTEM_BUTTONS = [
    "DEBUG_OVERLAY",                         # F1
    "SCREENSHOT",                            # F12
]

ALL_BUTTONS = PILOT_BUTTONS + SYSTEM_BUTTONS


@dataclass(frozen=True)
class ActionEvent:
    action: str      # one of the names above
    value: float     # 1.0 press / 0.0 release


@dataclass(frozen=True)
class PointerState:
    x: float
    y: float                 # window pixels, origin bottom-left
    primary: bool
    secondary: bool
    wheel: float             # scroll delta accumulated since last poll
