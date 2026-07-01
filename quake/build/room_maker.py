import math

from build.room_geometry import bearing_to_wall_hit, s_to_wall_along
from build.room_pack import PairBlock, size_and_pack
from build.room_validate import check_room
from map.raw_models import (
    BuildConfig,
    CeilingEqRT,
    DoorRT,
    EnemyRT,
    Manifest,
    PanelPairRT,
    PanelPlacementRT,
    RoomPortalSpec,
    RoomRuntime,
    RoomSource,
)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _wrap_pi(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def _wall_yaw(wall):
    if wall == "N":
        return math.pi
    if wall == "S":
        return 0.0
    if wall == "E":
        return -math.pi / 2.0
    if wall == "W":
        return math.pi / 2.0
    raise ValueError(f"bad wall {wall!r}")


def build_room_runtime(
    room: RoomSource,
    portals: RoomPortalSpec,
    manifest: Manifest,
    cfg: BuildConfig,
) -> RoomRuntime:
    pairs = sorted(room.blocks, key=lambda b: b.step_index)

    # Step A — asset resolve (figure_id-keyed, per settled ruling)
    resolved = []
    for block in pairs:
        figure_id = block.drawing.figure_id
        highlight_step = block.drawing.highlight_step
        drawing_off = f"{figure_id}.off"
        drawing_on = f"{figure_id}.on.{highlight_step}"
        text_off = f"{block.text.block_id}.off"
        text_on = f"{block.text.block_id}.on"
        for aid in (drawing_off, drawing_on, text_off, text_on):
            if aid not in manifest.assets:
                raise ValueError(f"missing asset_id: {aid}")
        resolved.append(
            {
                "block": block,
                "drawing_off": drawing_off,
                "drawing_on": drawing_on,
                "text_off": text_off,
                "text_on": text_on,
            }
        )

    # Step B + C — px->m, PairBlocks
    pair_blocks = []
    for r in resolved:
        d_entry = manifest.assets[r["drawing_on"]]
        t_entry = manifest.assets[r["text_on"]]
        d_px_w, d_px_h = d_entry.px_w, d_entry.px_h
        t_px_w, t_px_h = t_entry.px_w, t_entry.px_h

        drawing_w = _clamp(d_px_w / cfg.room_px_per_m, cfg.panel_min_w_m, cfg.panel_max_w_m)
        drawing_h = drawing_w * (d_px_h / max(d_px_w, 1))
        tppm = getattr(cfg, "text_px_per_m", cfg.room_px_per_m)
        text_w = _clamp(t_px_w / tppm, cfg.panel_min_w_m, cfg.panel_max_w_m)
        text_h = text_w * (t_px_h / max(t_px_w, 1))

        block_w = drawing_w + cfg.panel_gap_m + text_w
        block_h = max(drawing_h, text_h)

        pb = PairBlock(
            pair_id=r["block"].pair_id,
            step_index=r["block"].step_index,
            block_w_m=block_w,
            block_h_m=block_h,
            drawing_w=drawing_w,
            drawing_h=drawing_h,
            text_w=text_w,
            text_h=text_h,
        )
        pair_blocks.append(pb)
        r["drawing_w"] = drawing_w
        r["drawing_h"] = drawing_h
        r["text_w"] = text_w
        r["text_h"] = text_h

    # Step D — doors_bearings
    incident = sorted(
        portals.incident,
        key=lambda e: (-e.neighbor_importance, e.edge_id),
    )
    doors_bearings = []
    for edge in incident:
        theta = edge.bearing_rad
        wall = bearing_to_wall_hit(theta, cfg.room_min_w_m, cfg.room_min_d_m).wall
        doors_bearings.append((wall, theta))

    # Step E — pack
    pack = size_and_pack(pair_blocks, doors_bearings, cfg)
    if not pack.converged:
        raise ValueError("RoomTooDense")

    W, D, H = pack.W, pack.D, pack.H

    # Step F — doors
    doors = []
    for i, edge in enumerate(incident):
        theta = edge.bearing_rad
        nudged_s = pack.doors_s[i % len(pack.doors_s)]
        wall_actual, along_nudged = s_to_wall_along(nudged_s, W, D)
        # compute center x,z from wall and along
        if wall_actual == "N":
            cx, cz = along_nudged, D / 2.0
        elif wall_actual == "S":
            cx, cz = along_nudged, -D / 2.0
        elif wall_actual == "E":
            cx, cz = W / 2.0, along_nudged
        else:  # W
            cx, cz = -W / 2.0, along_nudged
        y = cfg.door_height_m / 2.0
        center_xyz = (cx, y, cz)
        yaw = _wall_yaw(wall_actual)
        sx = cx + math.cos(theta + math.pi) * cfg.aisle_depth_m
        sz = cz + math.sin(theta + math.pi) * cfg.aisle_depth_m
        spawn_xyz = (sx, 0.0, sz)
        spawn_heading = _wrap_pi(theta + math.pi)
        doors.append(
            DoorRT(
                edge_id=edge.edge_id,
                neighbor_id=edge.neighbor_id,
                bearing_rad=theta,
                wall=wall_actual,
                center_xyz=center_xyz,
                width_m=cfg.door_width_m,
                height_m=cfg.door_height_m,
                normal_yaw_rad=yaw,
                spawn_xyz=spawn_xyz,
                spawn_heading_rad=spawn_heading,
            )
        )

    # Step G — panels
    wall_counters = {}
    placement_rts = []
    for slot in pack.placements:
        idx = wall_counters.get(slot.wall, 0)
        wall_counters[slot.wall] = idx + 1
        wall_slot = f"{slot.wall}-{idx}"
        # Convert from perimeter s-coordinate to wall-local along
        _, along = s_to_wall_along(slot.along_center, W, D)
        if slot.wall == "N":
            cx, cz = along, D / 2.0
        elif slot.wall == "S":
            cx, cz = along, -D / 2.0
        elif slot.wall == "E":
            cx, cz = W / 2.0, along
        else:  # W
            cx, cz = -W / 2.0, along
        y = min(
            max(cfg.panel_center_y_pref_m, slot.height_m / 2 + 0.15),
            H - slot.height_m / 2 - 0.15,
        )
        center_xyz = (cx, y, cz)
        yaw = _wall_yaw(slot.wall)
        placement_rts.append(
            PanelPlacementRT(
                wall=slot.wall,
                slot_index=idx,
                wall_slot=wall_slot,
                center_xyz=center_xyz,
                width_m=slot.width_m,
                height_m=slot.height_m,
                yaw_rad=yaw,
            )
        )

    panel_pairs = []
    for pi, r in enumerate(resolved):
        drawing_placement = placement_rts[pi * 2]
        text_placement = placement_rts[pi * 2 + 1]
        panel_pairs.append(
            PanelPairRT(
                pair_id=r["block"].pair_id,
                step_index=r["block"].step_index,
                drawing_off_asset=r["drawing_off"],
                drawing_on_asset=r["drawing_on"],
                text_off_asset=r["text_off"],
                text_on_asset=r["text_on"],
                drawing_placement=drawing_placement,
                text_placement=text_placement,
            )
        )

    # Step H — hidden door / demon
    final_idx = max(range(len(panel_pairs)), key=lambda i: panel_pairs[i].step_index)
    final_pair = panel_pairs[final_idx]
    hidden_door_wall_slot = final_pair.drawing_placement.wall_slot

    dp = final_pair.drawing_placement
    # inward normal: compute from yaw
    if dp.wall == "N":
        nx, nz = 0.0, -1.0
    elif dp.wall == "S":
        nx, nz = 0.0, 1.0
    elif dp.wall == "E":
        nx, nz = -1.0, 0.0
    else:  # W
        nx, nz = 1.0, 0.0
    dist = cfg.aisle_depth_m + cfg.demon_offset_m
    ex = dp.center_xyz[0] + nx * dist
    ez = dp.center_xyz[2] + nz * dist
    enemy = EnemyRT(
        enemy_id=f"{room.node_id}.demon",
        spawn_xyz=(ex, 0.1, ez),
        health=5,
    )

    # Step I — ceiling equations
    ceiling_rts = []
    eqs = list(room.ceiling_equations)
    n_eq = len(eqs)
    for i, eq in enumerate(eqs):
        x_offset = (i - (n_eq - 1) / 2.0) * 2.0
        ceiling_rts.append(
            CeilingEqRT(
                eq_id=eq.eq_id,
                asset_id=f"{eq.eq_id}.neutral",
                pos_xyz=(x_offset, H - 0.1, 0.0),
                size_m=(1.0, 0.5),
            )
        )

    # Step J — emit + validate
    room_rt = RoomRuntime(
        schema_version="1.0",
        room_id=room.node_id,
        dimensions_m=(W, H, D),
        panel_pairs=panel_pairs,
        final_pair_id=room.final_pair_id,
        hidden_door_wall_slot=hidden_door_wall_slot,
        doors=doors,
        enemy=enemy,
        ceiling_equations=ceiling_rts,
    )

    violations = check_room(room_rt, portals, manifest, cfg)
    if violations:
        raise ValueError("Room validation failed:\n" + "\n".join(violations))

    return room_rt
