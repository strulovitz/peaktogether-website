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

import referee
from events import Event
from ships import Ship, get_class
from snapshot import FleetSnapshot, copy_context
from orders import (
    MoveCombination, Trim, SetIntake, FireSolution, LeastSquaresFire,
    GramSchmidtDrill, RowOperation, BackSubstitute, BuildShip,
    JamStation, AssignSquad, ApplyTransform,
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

        elif isinstance(order, ApplyTransform):
            members = [s for s in self.living()
                       if order.squad == 0 or s.squad == order.squad]
            if not members:
                return self._reject(events, order,
                                    f"squad {order.squad} has no ships")
            M = np.asarray(order.matrix, dtype=np.float64)
            if M.shape != (3, 3) or not np.all(np.isfinite(M)):
                return self._reject(events, order,
                                    "transform must be a finite 3x3 matrix")
            for s in members:
                self._plans[s.ship_id] = [M @ s.pos]
            events.append(Event("TRANSFORM_APPLIED", {
                "squad": order.squad, "ships": len(members)}))

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
