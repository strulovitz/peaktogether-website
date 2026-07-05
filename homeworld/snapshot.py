"""FleetSnapshot (NEW_TESTAMENT 3.5): the read-only view of the sim.

A frozen dataclass with COPIED numpy arrays. forge and bridge read
ONLY this; fleet never hands out live references to its state.
"""

from dataclasses import dataclass, field

import numpy as np


def copy_context(ctx):
    """Deep-ish copy of a mission context dict: numpy arrays copied,
    lists/tuples/scalars passed through by value."""
    out = {}
    for k, v in ctx.items():
        if isinstance(v, np.ndarray):
            out[k] = v.copy()
        elif isinstance(v, list):
            out[k] = list(v)
        elif isinstance(v, dict):
            out[k] = copy_context(v)
        else:
            out[k] = v
    return out


@dataclass(frozen=True)
class FleetSnapshot:
    pulse: int
    ship_ids: tuple                    # (n,) living ships, ascending id
    klasses: tuple
    pos: np.ndarray                    # (n, 3)
    prev_pos: np.ndarray               # (n, 3)
    facing: np.ndarray                 # (n, 3)
    hp: np.ndarray                     # (n,)
    fuel: np.ndarray                   # (n,)
    squad: np.ndarray                  # (n,) int
    resources: float
    rank: int                          # rank of the fleet matrix
    fleet_matrix: np.ndarray           # (6, n) signatures as columns
    engine_vectors: tuple              # tuple of (3,) arrays
    context: dict = field(default_factory=dict)
