"""Ship dataclass + ship class definitions (NEW_TESTAMENT 3.2).

Signature channel order (frozen, Bible Part 1): K, B, M, S, J, U.
BUILTIN_CLASSES is a PLACEHOLDER table used while content/ships.json
does not exist yet; when the content module lands (Apocrypha 1.3),
FleetSim reads classes from there instead and this table becomes the
emergency fallback only.
"""

from dataclasses import dataclass, field

import numpy as np

BUILTIN_CLASSES = {
    "mothership": {"signature": [1, 1, 1, 1, 1, 1], "cost": 0,
                   "hp": 500.0, "trim_speed": 0.5},
    "fighter":    {"signature": [2, 0, 0, 1, 0, 0], "cost": 40,
                   "hp": 30.0, "trim_speed": 3.0},
    "corvette":   {"signature": [0, 2, 0, 1, 0, 0], "cost": 60,
                   "hp": 60.0, "trim_speed": 2.0},
    "collector":  {"signature": [0, 0, 2, 0, 1, 0], "cost": 50,
                   "hp": 40.0, "trim_speed": 1.5},
    "frigate":    {"signature": [0, 0, 0, 2, 0, 1], "cost": 90,
                   "hp": 100.0, "trim_speed": 1.0},
}


def get_class(content, klass):
    """Class definition dict for a klass name; content wins over the
    builtin placeholder table when available."""
    if content is not None:
        try:
            return content.ship_class(klass)
        except Exception:
            pass
    if klass not in BUILTIN_CLASSES:
        raise KeyError(f"unknown ship class: {klass}")
    return BUILTIN_CLASSES[klass]


@dataclass
class Ship:
    ship_id: int
    klass: str
    signature: np.ndarray                     # (6,) float64: K,B,M,S,J,U
    pos: np.ndarray                           # (3,) float64
    prev_pos: np.ndarray                      # (3,) for render interpolation
    facing: np.ndarray                        # (3,) unit vector
    hp: float
    fuel: float = 100.0
    squad: int = 0
    alive: bool = True
