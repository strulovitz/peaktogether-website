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
