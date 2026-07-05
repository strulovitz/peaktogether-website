The keyboard and mouse are alive! 🎉 Now the biggest package so far: FLEET — the simulation core (New Testament Part 3, build steps 6–7). This is where ships become matrix columns, the 10 Hz pulse starts beating, and — most importantly — referee.py is born: the mathematical conscience of the whole game. Its demo needs no window: it re-proves the Bible's worked examples through the game's own code and prints PASS/FAIL in plain English, so you can verify mathematical correctness forever with your own eyes.

Below are 8 complete files. Send each to DeepSeek exactly as-is.

File 1 — fleet/referee.py

"""THE REFEREE (NEW_TESTAMENT 3.6) — canonical verdict functions.

This file is the mathematical conscience of the game (Bible Iron
Rule 4: NumPy is the Referee). Every module that needs a structural
verdict imports THESE functions; nobody reimplements them. All
signatures are frozen (INTERFACES v1.0).

Tolerance doctrine: structural verdicts never use equality.
"""

import numpy as np

TOL_RANK = 1e-6        # relative, on singular values
TOL_RESIDUAL = 1e-4    # absolute; missions may override per-context
TOL_IMAG = 1e-9


def rank(A):
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    s = np.linalg.svd(A, compute_uv=False)
    if s.size == 0 or s[0] <= 0.0:
        return 0
    return int(np.sum(s > TOL_RANK * s[0]))


def is_solvable(A, b):
    """b is reachable iff appending it as a column does not raise the
    rank, i.e. b lies in C(A). (Strang Ch. 2/3.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    b = np.asarray(b, dtype=np.float64).reshape(-1, 1)
    return rank(A) == rank(np.column_stack([A, b]))


def residual(A, x, b):
    A = np.asarray(A, dtype=np.float64)
    x = np.asarray(x, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return float(np.linalg.norm(A @ x - b))


def least_squares(A, b):
    """Returns (x_hat, error_vector, error_norm). (Strang 4.2-4.3.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    b = np.asarray(b, dtype=np.float64)
    x_hat, *_ = np.linalg.lstsq(A, b, rcond=None)
    e = b - A @ x_hat
    return x_hat, e, float(np.linalg.norm(e))


def nullspace_basis(A):
    """Columns span N(A); empty (n, 0) array if the nullspace is {0}.
    From the SVD A = U S V^T: right singular vectors v_{r+1}..v_n
    satisfy A v_i = 0. (Strang 3.2.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    _, _, Vt = np.linalg.svd(A)
    r = rank(A)
    return Vt[r:].T


def in_nullspace(A, x, eps):
    """(is_inside, level) where level = ||A x|| feeds the alarm meter."""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    x = np.asarray(x, dtype=np.float64)
    level = float(np.linalg.norm(A @ x))
    return level < eps, level


def spanned_volume(V):
    """V is 3x3 (three column vectors) -> |det|; 3x2 -> parallelogram
    area via the cross product. (Strang Ch. 5.)"""
    V = np.atleast_2d(np.asarray(V, dtype=np.float64))
    if V.shape[1] == 3:
        return float(abs(np.linalg.det(V)))
    return float(np.linalg.norm(np.cross(V[:, 0], V[:, 1])))


def real_eigen_axis(T):
    """The real eigenvector (eigenvalue nearest 1) of a rotation-like
    3D matrix T — the docking axis (Bible 2.11)."""
    T = np.asarray(T, dtype=np.float64)
    w, V = np.linalg.eig(T)
    i = int(np.argmin(np.abs(w.imag) + np.abs(w.real - 1.0)))
    v = V[:, i].real
    return v / np.linalg.norm(v)


def weak_axis(S):
    """Symmetric S -> (unit eigenvector of the smallest eigenvalue,
    that eigenvalue). (Strang 6.3-6.4.)"""
    S = np.asarray(S, dtype=np.float64)
    w, Q = np.linalg.eigh(S)
    return Q[:, 0], float(w[0])


def gram_penalty(Q):
    """How far the columns of Q are from orthonormal: ||Q^T Q - I||_F^2.
    (Strang 4.4.)"""
    Q = np.atleast_2d(np.asarray(Q, dtype=np.float64))
    G = Q.T @ Q
    return float(np.sum((G - np.eye(G.shape[1])) ** 2))


def cr_factor(A):
    """A = C R by greedy independent-column selection using rank();
    returns (C, R, kept_indices). R is solved per column by least
    squares on C. Exact for book-sized fleets. (Strang 1.4.)"""
    A = np.atleast_2d(np.asarray(A, dtype=np.float64))
    kept = []
    for j in range(A.shape[1]):
        if rank(A[:, kept + [j]]) > len(kept):
            kept.append(j)
    C = A[:, kept].copy()
    R = np.zeros((len(kept), A.shape[1]))
    for j in range(A.shape[1]):
        x, *_ = np.linalg.lstsq(C, A[:, j], rcond=None)
        R[:, j] = x
    return C, R, kept


def svd_partial(G, k):
    """Rank-k image and captured energy fraction (the Guidestone,
    Bible 2.14): G_k = U_k S_k Vt_k; energy = sum(s_i^2, i<=k) / sum."""
    G = np.atleast_2d(np.asarray(G, dtype=np.float64))
    U, s, Vt = np.linalg.svd(G, full_matrices=False)
    k = max(1, min(int(k), s.size))
    G_k = (U[:, :k] * s[:k]) @ Vt[:k]
    total = float(np.sum(s ** 2))
    energy = float(np.sum(s[:k] ** 2) / total) if total > 0.0 else 1.0
    return G_k, energy

File 2 — fleet/orders.py

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

File 3 — fleet/events.py

"""THE FROZEN EVENT TYPES (NEW_TESTAMENT 3.4, version 1).

Frozen kind list (add = minor bump; rename/remove = forbidden):

RANK_CHANGED    {old, new}
SHIP_BUILT      {ship_id, klass, rank_increased}
SHIP_CAPTURED   {ship_id, rank_increased}
SHIELD_DOWN     {target_id}
SHIELD_PARTIAL  {target_id, residual_norm, error_vector}
ORDER_REJECTED  {order, reason, residual}
ALARM_LEVEL     {level, per_station}
GATE_VOLUME     {volume, ok}
DRILL_STEP      {squad, step_index, subtracted_component}
ROWOP_APPLIED   {matrix_after}
PIVOT_ZERO      {row}
SOLVED          {context_id}
RESOURCE_TICK   {amount, cos_theta}
DOCK_PROGRESS   {deviation_angle}
SHIP_LOST       {ship_id, cause}
MISSION_FLAG    {name, value}
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Event:
    kind: str
    data: dict = field(default_factory=dict)

File 4 — fleet/ships.py

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

File 5 — fleet/snapshot.py

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

File 6 — fleet/sim.py

"""FleetSim: the simulation core (NEW_TESTAMENT 3.5).

Fixed-order pulse (FROZEN — determinism depends on it):
  1. store prev_pos            2. ingest & validate orders
  3. movement (trim + plans)   4. drills (Gram-Schmidt steps)
  5. harvest                   6. combat (via the referee)
  7. sensors (nullspace alarm) 8. structure (rank, gate volume)
  9. emit events

Determinism: fleet owns the only RNG; logic never reads the wall
clock. Same seed + same order stream => bit-identical pulses.
"""

import json

import numpy as np

from . import referee
from .events import Event
from .ships import Ship, get_class
from .snapshot import FleetSnapshot, copy_context
from .orders import (
    MoveCombination, Trim, SetIntake, FireSolution, LeastSquaresFire,
    GramSchmidtDrill, RowOperation, BackSubstitute, BuildShip,
    JamStation, AssignSquad,
)

_CRUISE_FACTOR = 3.0     # cruise speed = trim_speed * this
_HARVEST_RHO = 5.0       # resource units/s at perfect intake alignment


class FleetSim:
    def __init__(self, seed, content=None):
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        self.content = content
        self.ships = {}                     # ship_id -> Ship
        self.resources = 0.0
        self.engine_vectors = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
        ]
        self.context = {}                   # installed by campaign
        self.pulse = 0
        self._next_id = 1
        self._queue = []
        self._plans = {}                    # ship_id -> [waypoints]
        self._drills = {}                   # squad -> {"steps": [...], "i": int}
        self._pending_fire = []
        self._last_rank = 0

    # ---- setup / helpers ----

    def spawn(self, klass, pos, squad=0, facing=(0.0, 0.0, 1.0)):
        cls = get_class(self.content, klass)
        ship_id = self._next_id
        self._next_id += 1
        p = np.asarray(pos, dtype=np.float64).copy()
        f = np.asarray(facing, dtype=np.float64)
        n = np.linalg.norm(f)
        f = f / n if n > 1e-9 else np.array([0.0, 0.0, 1.0])
        self.ships[ship_id] = Ship(
            ship_id=ship_id, klass=klass,
            signature=np.asarray(cls["signature"], dtype=np.float64).copy(),
            pos=p, prev_pos=p.copy(), facing=f,
            hp=float(cls["hp"]), squad=int(squad),
        )
        return ship_id

    def install_context(self, ctx):
        self.context = copy_context(ctx)
        aug = self.context.get("augmented")
        if aug is not None:
            aug = np.asarray(aug, dtype=np.float64)
            self.context["augmented"] = aug.copy()
            self.context["A0"] = aug[:, :-1].copy()
            self.context["b0"] = aug[:, -1].copy()

    def set_engine_vectors(self, vectors):
        self.engine_vectors = [
            np.asarray(v, dtype=np.float64).copy() for v in vectors
        ]

    def living(self):
        return [s for _, s in sorted(self.ships.items()) if s.alive]

    def _class(self, ship):
        return get_class(self.content, ship.klass)

    # ---- the two Bible matrices, assembled on demand ----

    def formation_matrix(self, ids):
        """P: columns are positions of the given ships, shape (3, k)."""
        cols = [self.ships[i].pos for i in ids]
        return np.column_stack(cols) if cols else np.zeros((3, 0))

    def fleet_matrix(self, ids=None):
        """A: columns are signatures (all living ships if ids is None)."""
        if ids is None:
            cols = [s.signature for s in self.living()]
        else:
            cols = [self.ships[i].signature for i in ids]
        return np.column_stack(cols) if cols else np.zeros((6, 0))

    # ---- frozen interface ----

    def submit(self, order):
        self._queue.append(order)

    def tick(self, dt):
        events = []
        self.pulse += 1

        # 1. prev_pos
        for s in self.ships.values():
            if s.alive:
                s.prev_pos = s.pos.copy()

        # 2. ingest & validate
        queue, self._queue = self._queue, []
        trims = []
        for order in queue:
            self._ingest(order, trims, events)

        # 3. movement: trims then flight plans
        for ship_id, direction in trims:
            s = self.ships.get(ship_id)
            if s is None or not s.alive:
                continue
            d = np.asarray(direction, dtype=np.float64)
            n = np.linalg.norm(d)
            if n > 1e-9:
                s.pos = s.pos + (d / n) * self._class(s)["trim_speed"] * dt
        for ship_id in list(self._plans.keys()):
            s = self.ships.get(ship_id)
            plan = self._plans.get(ship_id, [])
            if s is None or not s.alive or not plan:
                self._plans.pop(ship_id, None)
                continue
            step = self._class(s)["trim_speed"] * _CRUISE_FACTOR * dt
            target = plan[0]
            delta = target - s.pos
            dist = float(np.linalg.norm(delta))
            if dist <= step:
                s.pos = target.copy()
                plan.pop(0)
                if not plan:
                    self._plans.pop(ship_id, None)
            else:
                s.pos = s.pos + delta * (step / dist)

        # 4. drills
        self._tick_drills(events)

        # 5. harvest
        field_u = self.context.get("resource_field")
        if field_u is not None:
            u = np.asarray(field_u, dtype=np.float64)
            u = u / max(np.linalg.norm(u), 1e-12)
            for s in self.living():
                if s.klass == "collector":
                    cos_theta = max(0.0, float(s.facing @ u))
                    amount = _HARVEST_RHO * cos_theta * dt
                    self.resources += amount
                    events.append(Event("RESOURCE_TICK", {
                        "amount": amount, "cos_theta": cos_theta}))

        # 6. combat
        pending, self._pending_fire = self._pending_fire, []
        for group, target_id, throttles in pending:
            self._resolve_fire(group, target_id, throttles, events)

        # 7. sensors: nullspace alarm (Bible 2.7)
        grid = self.context.get("A_grid")
        if grid is not None:
            A = np.asarray(grid, dtype=np.float64)
            squad = self.context.get("cloaked_squad")
            eps = float(self.context.get("grid_eps", referee.TOL_RESIDUAL))
            per_station = np.zeros(A.shape[0])
            level = 0.0
            for s in self.living():
                if squad is not None and s.squad != squad:
                    continue
                _, lv = referee.in_nullspace(A, s.pos, eps)
                level += lv
                per_station += np.abs(A @ s.pos)
            events.append(Event("ALARM_LEVEL", {
                "level": level, "per_station": per_station.tolist()}))

        # 8. structure: fleet rank + gate volume
        r = referee.rank(self.fleet_matrix())
        if r != self._last_rank:
            events.append(Event("RANK_CHANGED",
                                {"old": self._last_rank, "new": r}))
            self._last_rank = r
        gate_ids = self.context.get("gate_frigates")
        if gate_ids is not None and all(
                i in self.ships and self.ships[i].alive for i in gate_ids):
            center = np.asarray(self.context.get("gate_center", (0, 0, 0)),
                                dtype=np.float64)
            V = self.formation_matrix(list(gate_ids)) - center[:, None]
            vol = referee.spanned_volume(V)
            ok = vol >= float(self.context.get("gate_min_volume", 1.0))
            events.append(Event("GATE_VOLUME", {"volume": vol, "ok": ok}))

        return events

    # ---- order ingest (phase 2) ----

    def _reject(self, events, order, reason, res=None):
        events.append(Event("ORDER_REJECTED", {
            "order": order, "reason": reason, "residual": res}))

    def _ingest(self, order, trims, events):
        if isinstance(order, Trim):
            trims.append((order.ship_id, order.direction))

        elif isinstance(order, MoveCombination):
            members = [s for s in self.living() if s.squad == order.squad]
            if not members:
                return self._reject(events, order,
                                    f"squad {order.squad} has no ships")
            E = self.engine_vectors
            if len(order.coeffs) > len(E):
                return self._reject(
                    events, order,
                    f"{len(order.coeffs)} coefficients but only "
                    f"{len(E)} engine vectors are unlocked")
            for s in members:
                if order.diagonal:
                    d = np.zeros(3)
                    for c, e in zip(order.coeffs, E):
                        d = d + float(c) * e
                    self._plans[s.ship_id] = [s.pos + d]
                else:
                    plan, cursor = [], s.pos.copy()
                    for c, e in zip(order.coeffs, E):
                        cursor = cursor + float(c) * e
                        plan.append(cursor.copy())
                    self._plans[s.ship_id] = plan

        elif isinstance(order, SetIntake):
            s = self.ships.get(order.ship_id)
            if s is None or not s.alive:
                return self._reject(events, order, "no such ship")
            f = np.asarray(order.facing, dtype=np.float64)
            n = np.linalg.norm(f)
            if n < 1e-9:
                return self._reject(events, order, "zero facing vector")
            s.facing = f / n

        elif isinstance(order, (FireSolution, LeastSquaresFire)):
            shield_b = self.context.get("shield_b")
            target_id = self.context.get("shield_target")
            if shield_b is None or target_id != order.target_id:
                return self._reject(events, order,
                                    "no shield context for that target")
            group = [i for i in order.group
                     if i in self.ships and self.ships[i].alive]
            if not group:
                return self._reject(events, order, "empty firing group")
            A_g = self.fleet_matrix(group)
            b = np.asarray(shield_b, dtype=np.float64)
            if isinstance(order, LeastSquaresFire):
                x_hat, _, _ = referee.least_squares(A_g, b)
                throttles = tuple(float(v) for v in x_hat)
            else:
                if len(order.throttles) != len(group):
                    return self._reject(
                        events, order,
                        f"{len(order.throttles)} throttles for "
                        f"{len(group)} ships")
                throttles = order.throttles
            self._pending_fire.append((group, order.target_id, throttles))

        elif isinstance(order, GramSchmidtDrill):
            members = [s.ship_id for s in self.living()
                       if s.squad == order.squad]
            if len(members) < 2:
                return self._reject(events, order,
                                    "drill needs at least 2 ships in squad")
            steps = [(i, j) for i in range(1, len(members))
                     for j in range(i)]
            self._drills[order.squad] = {
                "ids": members, "steps": steps, "i": 0}

        elif isinstance(order, RowOperation):
            aug = self.context.get("augmented")
            if aug is None:
                return self._reject(events, order, "no row-op context")
            m = aug.shape[0]
            if not (0 <= order.i < m and 0 <= order.j < m):
                return self._reject(events, order, "row index out of range")
            if order.kind == "subtract":
                aug[order.i] = aug[order.i] - order.multiplier * aug[order.j]
            elif order.kind == "swap":
                aug[[order.i, order.j]] = aug[[order.j, order.i]]
            elif order.kind == "scale":
                if abs(order.multiplier) < 1e-12:
                    return self._reject(events, order,
                                        "cannot scale a row by zero")
                aug[order.i] = aug[order.i] * order.multiplier
            else:
                return self._reject(events, order,
                                    f"unknown row operation {order.kind}")
            events.append(Event("ROWOP_APPLIED",
                                {"matrix_after": aug.copy()}))
            k = min(order.i, aug.shape[1] - 1)
            if abs(aug[order.i, k]) < referee.TOL_RESIDUAL:
                events.append(Event("PIVOT_ZERO", {"row": order.i}))

        elif isinstance(order, BackSubstitute):
            A0 = self.context.get("A0")
            b0 = self.context.get("b0")
            if A0 is None:
                return self._reject(events, order, "no system to solve")
            x = np.asarray(order.values, dtype=np.float64)
            if x.shape[0] != A0.shape[1]:
                return self._reject(events, order,
                                    f"need {A0.shape[1]} values")
            res = referee.residual(A0, x, b0)
            tol = float(self.context.get("tolerance",
                                         referee.TOL_RESIDUAL))
            if res < tol:
                events.append(Event("SOLVED", {
                    "context_id": self.context.get("id", "context")}))
            else:
                self._reject(events, order,
                             "those values do not solve the original "
                             "system", res)

        elif isinstance(order, BuildShip):
            try:
                cls = get_class(self.content, order.klass)
            except KeyError:
                return self._reject(events, order,
                                    f"unknown ship class {order.klass}")
            cost = float(cls["cost"])
            if cost > self.resources:
                return self._reject(
                    events, order,
                    f"needs {cost:.0f} resources, have "
                    f"{self.resources:.0f}")
            self.resources -= cost
            before = referee.rank(self.fleet_matrix())
            base = np.asarray(self.context.get("build_pos", (0, 0, 0)),
                              dtype=np.float64)
            i = self._next_id
            pos = base + np.array([2.0 + (i % 5), 0.0, 2.0 * (i // 5 % 5)])
            ship_id = self.spawn(order.klass, pos)
            after = referee.rank(self.fleet_matrix())
            events.append(Event("SHIP_BUILT", {
                "ship_id": ship_id, "klass": order.klass,
                "rank_increased": after > before}))

        elif isinstance(order, JamStation):
            grid = self.context.get("A_grid")
            if grid is None:
                return self._reject(events, order, "no sensor grid context")
            if not (0 <= order.station_id < grid.shape[0]):
                return self._reject(events, order, "no such station")
            self.context["A_grid"] = np.delete(grid, order.station_id,
                                               axis=0)
            events.append(Event("MISSION_FLAG", {
                "name": "jammed_station", "value": order.station_id}))

        elif isinstance(order, AssignSquad):
            for i in order.ship_ids:
                s = self.ships.get(i)
                if s is not None and s.alive:
                    s.squad = int(order.squad)

        else:
            self._reject(events, order,
                         f"unknown order type {type(order).__name__}")

    # ---- combat resolution (phase 6) ----

    def _resolve_fire(self, group, target_id, throttles, events):
        A_g = self.fleet_matrix(group)
        b = np.asarray(self.context.get("shield_b"), dtype=np.float64)
        x = np.asarray(throttles, dtype=np.float64)
        res = referee.residual(A_g, x, b)
        tol = float(self.context.get("tolerance", referee.TOL_RESIDUAL))
        if res < tol:
            events.append(Event("SHIELD_DOWN", {"target_id": target_id}))
        else:
            e = b - A_g @ x
            events.append(Event("SHIELD_PARTIAL", {
                "target_id": target_id, "residual_norm": res,
                "error_vector": e.copy()}))

    # ---- drills (phase 4) ----

    def _tick_drills(self, events):
        for squad in list(self._drills.keys()):
            d = self._drills[squad]
            if d["i"] >= len(d["steps"]):
                self._drills.pop(squad)
                continue
            ids = [i for i in d["ids"]
                   if i in self.ships and self.ships[i].alive]
            if len(ids) < 2:
                self._drills.pop(squad)
                continue
            centroid = np.mean([self.ships[i].pos for i in ids], axis=0)
            i_idx, j_idx = d["steps"][d["i"]]
            if i_idx >= len(ids) or j_idx >= len(ids):
                self._drills.pop(squad)
                continue
            v_i = self.ships[ids[i_idx]].pos - centroid
            q_j = self.ships[ids[j_idx]].pos - centroid
            n = np.linalg.norm(q_j)
            if n > 1e-9:
                q_j = q_j / n
                sub = float(v_i @ q_j)
                self.ships[ids[i_idx]].pos = centroid + (v_i - sub * q_j)
                events.append(Event("DRILL_STEP", {
                    "squad": squad, "step_index": d["i"],
                    "subtracted_component": abs(sub)}))
            d["i"] += 1

    # ---- snapshot / save / load ----

    def snapshot(self):
        living = self.living()
        n = len(living)
        pos = np.zeros((n, 3))
        prev = np.zeros((n, 3))
        fac = np.zeros((n, 3))
        hp = np.zeros(n)
        fuel = np.zeros(n)
        squad = np.zeros(n, dtype=np.int64)
        for k, s in enumerate(living):
            pos[k] = s.pos
            prev[k] = s.prev_pos
            fac[k] = s.facing
            hp[k] = s.hp
            fuel[k] = s.fuel
            squad[k] = s.squad
        return FleetSnapshot(
            pulse=self.pulse,
            ship_ids=tuple(s.ship_id for s in living),
            klasses=tuple(s.klass for s in living),
            pos=pos, prev_pos=prev, facing=fac, hp=hp, fuel=fuel,
            squad=squad, resources=self.resources,
            rank=referee.rank(self.fleet_matrix()),
            fleet_matrix=self.fleet_matrix(),
            engine_vectors=tuple(v.copy() for v in self.engine_vectors),
            context=copy_context(self.context),
        )

    def save(self, path):
        data = {
            "seed": self.seed, "pulse": self.pulse,
            "resources": self.resources,
            "engine_vectors": [v.tolist() for v in self.engine_vectors],
            "next_id": self._next_id,
            "ships": [{
                "ship_id": s.ship_id, "klass": s.klass,
                "signature": s.signature.tolist(),
                "pos": s.pos.tolist(), "facing": s.facing.tolist(),
                "hp": s.hp, "fuel": s.fuel, "squad": s.squad,
                "alive": s.alive,
            } for _, s in sorted(self.ships.items())],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def load(path, content=None):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        sim = FleetSim(data["seed"], content)
        sim.pulse = int(data["pulse"])
        sim.resources = float(data["resources"])
        sim.engine_vectors = [np.asarray(v, dtype=np.float64)
                              for v in data["engine_vectors"]]
        sim._next_id = int(data["next_id"])
        for rec in data["ships"]:
            p = np.asarray(rec["pos"], dtype=np.float64)
            sim.ships[rec["ship_id"]] = Ship(
                ship_id=rec["ship_id"], klass=rec["klass"],
                signature=np.asarray(rec["signature"], dtype=np.float64),
                pos=p, prev_pos=p.copy(),
                facing=np.asarray(rec["facing"], dtype=np.float64),
                hp=float(rec["hp"]), fuel=float(rec["fuel"]),
                squad=int(rec["squad"]), alive=bool(rec["alive"]),
            )
        sim._last_rank = referee.rank(sim.fleet_matrix())
        return sim

File 7 — fleet/__init__.py

"""fleet — the simulation core of Homeworld: A Good Basis.

Ships as matrix columns, the 10 Hz pulse, orders, events, and the
Referee — the canonical NumPy verdict functions used by the whole
game (NEW_TESTAMENT Part 3). fleet imports nothing from forge, helm,
or bridge.
"""

from . import referee
from .sim import FleetSim
from .ships import Ship, BUILTIN_CLASSES
from .events import Event
from .snapshot import FleetSnapshot
from .orders import (
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

File 8 — fleet/demo.py

"""python -m fleet.demo — the headless self-test (NT Part 6).

This is the project's regression suite: it recomputes the Bible's
worked examples through the REAL referee and simulation and prints
PASS/FAIL for human eyes. After ANY change to fleet or referee, this
must still print 12/12.
"""

import sys
import time
import traceback

import numpy as np

from . import referee
from .sim import FleetSim
from .orders import MoveCombination, Trim

_RESULTS = []


def check(label, ok):
    _RESULTS.append(bool(ok))
    print(f"{label} {'PASS' if ok else 'FAIL'}")


def close(a, b, tol=1e-9):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), atol=tol)


def same_direction(v, w, tol=1e-9):
    v = np.asarray(v, float); w = np.asarray(w, float)
    v = v / np.linalg.norm(v); w = w / np.linalg.norm(w)
    return abs(abs(v @ w) - 1.0) < tol


def _det_sim(seed):
    sim = FleetSim(seed)
    ids = [sim.spawn("fighter", (2.0 * i, 0.0, 0.0), squad=1)
           for i in range(3)]
    sim.submit(MoveCombination(squad=1, coeffs=(3.0, 2.0, 1.0),
                               diagonal=True))
    for k in range(100):
        if k % 10 == 0:
            sim.submit(Trim(ids[0], (1.0, 0.0, 0.0)))
        sim.tick(0.1)
    return np.concatenate([sim.ships[i].pos for i in ids])


def main():
    print("FLEET SELF-TEST — referee + simulation core")

    A = np.array([[2.0, 1.0, 3.0], [0.0, 3.0, 3.0]])
    check(" 1. rank of the 2x3 matrix with columns (2,0),(1,3),(3,3) == 2 .......",
          referee.rank(A) == 2)

    C, R, kept = referee.cr_factor(A)
    check(" 2. cr_factor keeps columns [0,1] and R's third column == (1,1) ......",
          kept == [0, 1] and close(R[:, 2], [1.0, 1.0], 1e-8))

    Ag = np.array([[2.0, 1.0], [0.0, 3.0]])
    x_hat, e, en = referee.least_squares(Ag, np.array([7.0, 6.0]))
    check(" 3. shield solve: A columns (2,0),(1,3), b=(7,6) -> x=(2.5,2.0) ......",
          close(x_hat, [2.5, 2.0], 1e-8) and en < 1e-8)

    N = referee.nullspace_basis(np.array([[1.0, 1.0, 0.0],
                                          [0.0, 1.0, 1.0]]))
    check(" 4. nullspace of rows (1,1,0),(0,1,1) is spanned by +-(1,-1,1)/sqrt3 .",
          N.shape == (3, 1) and same_direction(N[:, 0], [1.0, -1.0, 1.0], 1e-8))

    N2 = referee.nullspace_basis(np.array([[1.0, 1.0, 0.0]]))
    check(" 5. jamming row 2 grows nullspace dimension 1 -> 2 ...................",
          N.shape[1] == 1 and N2.shape[1] == 2)

    Als = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
    x_hat, e, en = referee.least_squares(Als, np.array([6.0, 0.0, 0.0]))
    check(" 6. least squares pings (0,6),(1,0),(2,0) -> (C,D)=(5,-3) ............",
          close(x_hat, [5.0, -3.0], 1e-8))

    V = np.column_stack([[2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [1.0, 1.0, 1.0]])
    check(" 7. det of columns (2,0,0),(0,3,0),(1,1,1) == 6 ......................",
          abs(referee.spanned_volume(V) - 6.0) < 1e-9)

    S = np.array([[0.8, 0.3], [0.2, 0.7]])
    w, Vec = np.linalg.eig(S)
    dom = Vec[:, int(np.argmax(w.real))].real
    check(" 8. swarm matrix [[0.8,0.3],[0.2,0.7]] dominant eigenvector ~ (3,2) ..",
          same_direction(dom, [3.0, 2.0], 1e-8))

    v, lam = referee.weak_axis(np.array([[5.0, 4.0], [4.0, 5.0]]))
    check(" 9. weak axis of [[5,4],[4,5]] is +-(1,-1)/sqrt2, eigenvalue 1 .......",
          abs(lam - 1.0) < 1e-9 and same_direction(v, [1.0, -1.0], 1e-8))

    rng = np.random.default_rng(7)
    G = rng.random((16, 16))
    energies = [referee.svd_partial(G, k)[1] for k in range(1, 17)]
    monotone = all(energies[i] <= energies[i + 1] + 1e-12
                   for i in range(15))
    check("10. svd_partial: energy fraction increases with k, reaches 1.0 .......",
          monotone and abs(energies[-1] - 1.0) < 1e-9)

    check("11. determinism: two sims, same seed+orders, identical after 100 ticks",
          np.array_equal(_det_sim(1234), _det_sim(1234)))

    sim = FleetSim(42)
    for i in range(20):
        sim.spawn("fighter", (float(i), 0.0, 0.0), squad=1)
    sim.submit(MoveCombination(squad=1, coeffs=(5.0, 3.0, 2.0),
                               diagonal=False))
    t0 = time.perf_counter()
    for _ in range(100):
        sim.tick(0.1)
    elapsed = time.perf_counter() - t0
    check("12. 100 pulses with 20 ships in < 0.5 s (performance floor) ..........",
          elapsed < 0.5)

    passed = sum(_RESULTS)
    total = len(_RESULTS)
    if passed == total:
        print(f"FLEET SELF-TEST PASSED ({passed}/{total})")
    else:
        print(f"FLEET SELF-TEST FAILED ({passed}/{total})")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        text = traceback.format_exc()
        with open("crashlog.txt", "w", encoding="utf-8") as f:
            f.write("fleet.demo crash\n")
            f.write(text)
        print("Something broke — please copy crashlog.txt to the team.")
        print(text)
        sys.exit(1)

📋 YOUR STEPS

    Send to DeepSeek: the 8 files, verbatim, commit message: NT steps 6-7: fleet core (referee, orders, events, sim, snapshot) + 12-line self-test — and update COMMENTARIES.md.
    Run: open the project folder, address bar → cmd → Enter, then: python -m fleet.demo

👀 WHAT YOU SHOULD SEE (no window this time — pure console)

FLEET SELF-TEST — referee + simulation core
 1. rank of the 2x3 matrix with columns (2,0),(1,3),(3,3) == 2 ....... PASS
 2. cr_factor keeps columns [0,1] and R's third column == (1,1) ...... PASS
 3. shield solve: A columns (2,0),(1,3), b=(7,6) -> x=(2.5,2.0) ...... PASS
 4. nullspace of rows (1,1,0),(0,1,1) is spanned by +-(1,-1,1)/sqrt3 . PASS
 5. jamming row 2 grows nullspace dimension 1 -> 2 ................... PASS
 6. least squares pings (0,6),(1,0),(2,0) -> (C,D)=(5,-3) ............ PASS
 7. det of columns (2,0,0),(0,3,0),(1,1,1) == 6 ...................... PASS
 8. swarm matrix [[0.8,0.3],[0.2,0.7]] dominant eigenvector ~ (3,2) .. PASS
 9. weak axis of [[5,4],[4,5]] is +-(1,-1)/sqrt2, eigenvalue 1 ....... PASS
10. svd_partial: energy fraction increases with k, reaches 1.0 ....... PASS
11. determinism: two sims, same seed+orders, identical after 100 ticks PASS
12. 100 pulses with 20 ships in < 0.5 s (performance floor) .......... PASS
FLEET SELF-TEST PASSED (12/12)

Twelve PASS lines and the final summary. Each line is a worked example from the book being re-proved by the game's own referee: line 3 is the shield mechanic, line 5 is the cloaking/jamming mechanic, line 7 is the hyperspace gate's determinant, line 9 is the weak-axis targeting... This little console printout is the mathematical heart of the project beating for the first time. ❤️
📝 REPORT BACK

Paste the console output (or just say "12/12"). If any line says FAIL, paste the whole output — that alone tells me exactly where to look.

Once confirmed, the next package is the wiring — app.py at the root, connecting forge + helm + fleet (New Testament build step 9): run.bat will launch the real game shell, and three glowing ships will fly a combination order across your screen, commanded by your own keyboard. That's the moment Mission 1 becomes buildable. 🚀
