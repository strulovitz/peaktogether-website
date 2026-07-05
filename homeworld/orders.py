"""THE FROZEN ORDER TYPES (NEW_TESTAMENT 3.3, version 1).

Both players feed one queue: the Pilot's controller and the
Navigator's console both translate their inputs into these orders
and submit them to FleetSim. Orders are validated at tick time;
invalid orders produce ORDER_REJECTED events that explain and
suggest — never punish (Iron Rule 3).
"""

from dataclasses import dataclass


@dataclass(frozen=True)                     # Bible 2.1
class MoveCombination:
    squad: int
    coeffs: tuple                            # one scalar per engine vector
    diagonal: bool                           # True: fly the diagonal;
                                             # False: component-by-component


@dataclass(frozen=True)                     # continuous, from TRIM axes
class Trim:
    ship_id: int
    direction: tuple                         # (dx, dy, dz), normalized inside


@dataclass(frozen=True)                     # Bible 2.2
class SetIntake:
    ship_id: int
    facing: tuple


@dataclass(frozen=True)                     # Bible 2.3 regimes 1 and 3
class FireSolution:
    group: tuple                             # firing ship ids
    target_id: int
    throttles: tuple                         # x: one throttle per group ship


@dataclass(frozen=True)                     # Bible 2.3 regime 2
class LeastSquaresFire:
    group: tuple
    target_id: int


@dataclass(frozen=True)                     # Bible 2.8
class GramSchmidtDrill:
    squad: int


@dataclass(frozen=True)                     # Bible 2.5 / 2.6 row-op missions
class RowOperation:
    kind: str                                # "subtract" | "swap" | "scale"
    i: int
    j: int
    multiplier: float                        # row_i <- row_i - m * row_j


@dataclass(frozen=True)
class BackSubstitute:
    values: tuple                            # the Navigator's x


@dataclass(frozen=True)
class BuildShip:
    klass: str


@dataclass(frozen=True)                     # Bible 2.7: deletes a grid row
class JamStation:
    station_id: int


@dataclass(frozen=True)
class AssignSquad:
    ship_ids: tuple
    squad: int
