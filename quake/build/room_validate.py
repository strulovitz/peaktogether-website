import math

from build.room_geometry import s_to_wall_along
from map.raw_models import BuildConfig, DoorRT, Manifest, RoomPortalSpec, RoomRuntime


def _wall_along_to_s(wall: str, along: float, W: float, D: float) -> float:
    if wall == "N":
        return along + W / 2.0
    if wall == "E":
        return W + (D / 2.0 - along)
    if wall == "S":
        return W + D + (W / 2.0 - along)
    if wall == "W":
        return 2.0 * W + D + (along + D / 2.0)
    raise ValueError(f"unknown wall {wall!r}")


def check_room(
    room: RoomRuntime,
    portals: RoomPortalSpec,
    manifest: Manifest,
    cfg: BuildConfig,
) -> list[str]:
    violations: list[str] = []

    W = room.dimensions_m[0]
    H = room.dimensions_m[1]
    D = room.dimensions_m[2]

    doors = room.doors
    incident = portals.incident

    # Rule 1
    degree = len(incident)
    if not (len(doors) == len(incident)):
        violations.append(
            f"Door count {len(doors)} != incident count {len(incident)} (node degree {degree})."
        )

    # Rule 2
    door_edge_ids = [d.edge_id for d in doors]
    incident_edge_ids = [e.edge_id for e in incident]
    door_set = set(door_edge_ids)
    incident_set = set(incident_edge_ids)

    if len(door_edge_ids) != len(door_set):
        dups = sorted({eid for eid in door_edge_ids if door_edge_ids.count(eid) > 1})
        violations.append(f"Duplicate door edge_id(s): {dups}.")
    if len(incident_edge_ids) != len(incident_set):
        dups = sorted({eid for eid in incident_edge_ids if incident_edge_ids.count(eid) > 1})
        violations.append(f"Duplicate incident edge_id(s): {dups}.")

    missing = incident_set - door_set
    extra = door_set - incident_set
    if missing:
        violations.append(f"Doors missing for incident edge(s): {sorted(missing)}.")
    if extra:
        violations.append(f"Extra door(s) with no incident edge: {sorted(extra)}.")

    # Rules 3 & 4
    def _ang_diff(a: float, b: float) -> float:
        return abs(math.atan2(math.sin(a - b), math.cos(a - b)))

    for d in doors:
        cx = d.center_xyz[0]
        cz = d.center_xyz[2]
        actual_dir = math.atan2(cz, cx)
        diff = _ang_diff(actual_dir, d.bearing_rad)
        if diff > cfg.door_nudge_tol_rad:
            violations.append(
                f"Door {d.edge_id} direction {actual_dir:.12f} "
                f"differs from bearing_rad {d.bearing_rad:.12f} (diff {diff:.3e} > tol {cfg.door_nudge_tol_rad})."
            )

    # Rule 5
    door_s: list[tuple[float, str]] = []
    perimeter = 2.0 * W + 2.0 * D
    for d in doors:
        wall = d.wall
        if wall in ("E", "W"):
            along = d.center_xyz[2]
        else:
            along = d.center_xyz[0]
        try:
            s = _wall_along_to_s(wall, along, W, D)
        except ValueError:
            violations.append(f"Door {d.edge_id} on unknown wall {wall!r}.")
            continue
        door_s.append((s, d.edge_id))

    corners = [0.0, W, W + D, 2.0 * W + D]
    clearance = cfg.corner_clearance_m + cfg.door_width_m / 2.0
    for s, eid in door_s:
        for cs in corners:
            dist = abs(s - cs)
            dist = min(dist, perimeter - dist)
            if dist < clearance:
                violations.append(
                    f"Door {eid} at s={s:.3f} too close to corner s={cs:.3f} "
                    f"(dist {dist:.3f} < required {clearance:.3f})."
                )
                break

    ordered = sorted(door_s, key=lambda t: t[0])
    n = len(ordered)
    if n >= 2:
        for i in range(n):
            s_a, id_a = ordered[i]
            s_b, id_b = ordered[(i + 1) % n]
            if i + 1 < n:
                gap = s_b - s_a
            else:
                gap = (perimeter - s_a) + s_b
            if gap < cfg.door_min_separation_m:
                violations.append(
                    f"Doors {id_a} and {id_b} separation {gap:.3f} "
                    f"< minimum {cfg.door_min_separation_m}."
                )

    # Rules 6 & 7
    slot_keys: list[tuple[str, int]] = []
    for p in room.panel_pairs:
        dp = p.drawing_placement
        tp = p.text_placement
        slot_keys.append((dp.wall, dp.slot_index))
        slot_keys.append((tp.wall, tp.slot_index))

        if dp.wall != tp.wall:
            violations.append(
                f"Pair {p.pair_id} panels on different walls ({dp.wall} vs {tp.wall})."
            )
        elif abs(dp.slot_index - tp.slot_index) != 1:
            violations.append(
                f"Pair {p.pair_id} panels not on consecutive slots "
                f"({dp.slot_index}, {tp.slot_index})."
            )

    if len(set(slot_keys)) != 2 * len(room.panel_pairs):
        seen = set()
        dups = []
        for k in slot_keys:
            if k in seen:
                dups.append(k)
            seen.add(k)
        violations.append(f"Duplicate panel (wall, slot_index): {sorted(set(dups))}.")

    # Rule 8
    if room.panel_pairs:
        max_pair = max(room.panel_pairs, key=lambda p: p.step_index)
        if room.final_pair_id != max_pair.pair_id:
            violations.append(
                f"final_pair_id {room.final_pair_id!r} != pair with max "
                f"step_index {max_pair.pair_id!r}."
            )

    # Rule 9
    final_pair = None
    for p in room.panel_pairs:
        if p.pair_id == room.final_pair_id:
            final_pair = p
            break
    if final_pair is not None:
        expected = final_pair.drawing_placement.wall_slot
        if room.hidden_door_wall_slot != expected:
            violations.append(
                f"hidden_door_wall_slot {room.hidden_door_wall_slot!r} != "
                f"final pair drawing wall_slot {expected!r}."
            )

    # Rule 10
    if W < cfg.room_min_w_m:
        violations.append(f"Room width {W} below minimum {cfg.room_min_w_m}.")
    if H < cfg.room_min_h_m:
        violations.append(f"Room height {H} below minimum {cfg.room_min_h_m}.")
    if D < cfg.room_min_d_m:
        violations.append(f"Room depth {D} below minimum {cfg.room_min_d_m}.")

    # Rule 11
    for p in room.panel_pairs:
        for placement, label in (
            (p.drawing_placement, "drawing"),
            (p.text_placement, "text"),
        ):
            top = placement.center_xyz[1] + placement.height_m / 2.0
            if top > H:
                violations.append(
                    f"Pair {p.pair_id} {label} panel top {top:.3f} exceeds ceiling {H}."
                )
    for d in doors:
        top = d.center_xyz[1] + d.height_m / 2.0
        if top > H:
            violations.append(f"Door {d.edge_id} top {top:.3f} exceeds ceiling {H}.")

    # Rule 12
    for p in room.panel_pairs:
        for aid in (
            p.drawing_off_asset,
            p.drawing_on_asset,
            p.text_off_asset,
            p.text_on_asset,
        ):
            if aid not in manifest.assets:
                violations.append(f"Pair {p.pair_id} references missing asset {aid!r}.")

    return violations
