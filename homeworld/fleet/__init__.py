"""fleet — the simulation core of Homeworld: A Good Basis.

Ships as matrix columns, the 10 Hz pulse, orders, events, and the
Referee — the canonical NumPy verdict functions used by the whole
game (NEW_TESTAMENT Part 3). fleet imports nothing from forge, helm,
or bridge.
"""

import referee
from sim import FleetSim
from ships import Ship, BUILTIN_CLASSES
from events import Event
from snapshot import FleetSnapshot
from orders import (
    MoveCombination, Trim, SetIntake, FireSolution, LeastSquaresFire,
    GramSchmidtDrill, RowOperation, BackSubstitute, BuildShip,
    JamStation, AssignSquad,
)

__all__ = [
    "referee", "FleetSim", "Ship", "BUILTIN_CLASSES", "Event",
    "FleetSnapshot",
    "MoveCombination", "Trim", "SetIntake", "FireSolution",
    "LeastSquaresFire", "GramSchmidtDrill", "RowOperation",
    "BackSubstitute", "BuildShip", "JamStation", "AssignSquad",
]
