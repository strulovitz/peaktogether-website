"""QUAKE runtime engine — M7 module #13: gameplay.

The brain of the game: pure, headless, deterministic game-logic step.
NO GL, NO window, NO IO, NO RNG. All shared types imported from contracts.
"""
from math import cos, sin, sqrt

from contracts import (Actions, GameState, Pack, NavQuery, Event, PanelLit,
    DoorOpened, DemonSpawned, DemonHit, DemonKilled, RoomCleared, LevelComplete,
    ModeSwitch, ReadModeToggled, GuidelinesRecomputed, Ray, PanelHit,
    RoomRuntime, DoorRT, PanelPairRT, RoomProgress, LevelProgress, PlayerSave,
    SaveGame, Floorplan, FloorRoom,
    PITCH_CLAMP_RAD, Vec3, NodeId, PairId, LevelId)

# ===== PINNED CONSTANTS =====
WALK_SPEED_M_S = 2.4
AIM_CONE_RAD = 0.30
SHOOT_MAX_DIST = 50.0
DEMON_RADIUS = 0.6
SOCKET_ENTER_RADIUS_M = 1.0
EYE_HEIGHT_M = 1.6
# PITCH_CLAMP_RAD imported from contracts (1.2217, +/-70 degrees)

# ===== DEMON HP TRACKING (module-level mutable) =====
_demon_hp: dict[NodeId, int] = {}


def reticle_ray(eye: Vec3, heading: float, pitch: float,
                aim_x: float, aim_y: float) -> Ray:
    """Build a shot ray from the player's eye through the reticle.

    FROZEN COMPASS: heading theta -> world forward = (cos theta, 0, sin theta).
    +X = east, +Z = north. aim_y positive = look UP -> subtract from Y.
    """
    forward = (cos(pitch) * cos(heading), sin(pitch), cos(pitch) * sin(heading))
    right = (sin(heading), 0.0, -cos(heading))  # perpendicular in XZ plane
    ptch_up = (0.0, 1.0, 0.0)

    direction = (
        forward[0] + aim_x * AIM_CONE_RAD * right[0] - aim_y * AIM_CONE_RAD * ptch_up[0],
        forward[1] + aim_x * AIM_CONE_RAD * right[1] - aim_y * AIM_CONE_RAD * ptch_up[1],
        forward[2] + aim_x * AIM_CONE_RAD * right[2] - aim_y * AIM_CONE_RAD * ptch_up[2],
    )
    return Ray(origin=eye, direction=direction)


def resolve_shot(room: RoomRuntime, hit: PanelHit | None, demon_hit: bool,
                 lit: set[str], hidden_open: bool, demon_hp: int
                 ) -> tuple[list[Event], set[str], bool, int, bool]:
    """OT S3.2 door/demon decision table. PURE, never mutates inputs.

    Returns: (events, new_lit, new_hidden_open, new_demon_hp, cleared)
    """
    events: list[Event] = []
    new_lit = set(lit)
    new_hidden = hidden_open
    new_hp = demon_hp
    cleared = False

    # 1. DEMON HIT (demon_hit=True AND demon alive)
    if demon_hit and new_hp > 0:
        new_hp -= 1
        events.append(DemonHit(enemy_id=room.enemy.enemy_id, hp_remaining=new_hp))
        if new_hp <= 0:
            events.append(DemonKilled(enemy_id=room.enemy.enemy_id, room_id=room.room_id))
            events.append(RoomCleared(room_id=room.room_id))
            cleared = True
        return (events, new_lit, new_hidden, new_hp, cleared)

    # 2. MISS
    if hit is None:
        return (events, new_lit, new_hidden, new_hp, cleared)

    # 3. FINAL PAIR OFF -> flip ON (no demon yet)
    if hit.pair_id == room.final_pair_id and hit.pair_id not in lit:
        new_lit.add(hit.pair_id)
        events.append(PanelLit(pair_id=hit.pair_id, room_id=room.room_id))
        return (events, new_lit, new_hidden, new_hp, cleared)

    # 4. FINAL PAIR ON + hidden door CLOSED + hit is the DRAWING panel -> OPEN
    if (hit.pair_id == room.final_pair_id and hit.pair_id in lit
            and not hidden_open and hit.is_drawing):
        new_hidden = True
        events.append(DoorOpened(room_id=room.room_id))
        events.append(DemonSpawned(enemy_id=room.enemy.enemy_id, room_id=room.room_id))
        return (events, new_lit, new_hidden, new_hp, cleared)

    # 5. OTHER PAIR OFF -> flip ON
    if hit.pair_id != room.final_pair_id and hit.pair_id not in lit:
        new_lit.add(hit.pair_id)
        events.append(PanelLit(pair_id=hit.pair_id, room_id=room.room_id))
        return (events, new_lit, new_hidden, new_hp, cleared)

    # 6. No-op (already ON, or door already open, etc.)
    return (events, new_lit, new_hidden, new_hp, cleared)


def step(state: GameState, actions: Actions, pack: Pack,
         nav: NavQuery, dt: float) -> list[Event]:
    """Per-frame game logic. Mutates state in place. Returns emitted Events.

    The Shooter NEVER affects heading/pitch -- structurally enforced because only
    actions.heading_delta and actions.pitch_delta (Mover fields) drive rotation;
    aim_x/aim_y only feed reticle_ray.
    """
    events: list[Event] = []

    # ==== MOTION ====
    state.heading_rad += actions.heading_delta

    # Pitch clamp
    raw_pitch = state.pitch_rad + actions.pitch_delta
    if raw_pitch > PITCH_CLAMP_RAD:
        state.pitch_rad = PITCH_CLAMP_RAD
    elif raw_pitch < -PITCH_CLAMP_RAD:
        state.pitch_rad = -PITCH_CLAMP_RAD
    else:
        state.pitch_rad = raw_pitch

    # Forward and strafe in XZ (FROZEN COMPASS)
    fwd_x = cos(state.heading_rad)
    fwd_z = sin(state.heading_rad)
    str_x = sin(state.heading_rad)   # right strafe = rotate forward +90deg in XZ
    str_z = -cos(state.heading_rad)

    dx = (fwd_x * actions.move_y + str_x * actions.move_x) * WALK_SPEED_M_S * dt
    dz = (fwd_z * actions.move_y + str_z * actions.move_x) * WALK_SPEED_M_S * dt
    state.pos = nav.resolve_player_motion(state.pos, (dx, 0.0, dz))

    # ==== MODE-SWITCH ====
    level_id = pack.floorplan.level_id

    if state.mode == "room":
        eid = nav.door_at(state.pos)
        if eid is not None:
            from logutil import log as _log
            _log(f"gameplay: exiting room {state.current_room_id} via door {eid}")
            events.append(ModeSwitch(to="corridor", room_id=state.current_room_id,
                                     via_edge_id=eid))
            state.mode = "corridor"
            state.current_room_id = None
    elif state.mode == "corridor":
        for room in pack.floorplan.rooms:
            dx_sock = state.pos[0] - room.map_xz[0]
            dz_sock = state.pos[2] - room.map_xz[1]
            dist_sock = sqrt(dx_sock * dx_sock + dz_sock * dz_sock)
            if dist_sock <= SOCKET_ENTER_RADIUS_M:
                room_data = pack.rooms.get(room.room_id)
                if room_data is None:
                    continue
                spawn_pos = room_data.enemy.spawn_xyz  # fallback
                spawn_heading = 0.0
                if room_data.doors:
                    spawn_pos = room_data.doors[0].spawn_xyz
                    spawn_heading = room_data.doors[0].spawn_heading_rad
                from logutil import log as _log
                _log(f"gameplay: entering room {room.room_id}")
                events.append(ModeSwitch(to="room", room_id=room.room_id, via_edge_id=None))
                state.mode = "room"
                state.current_room_id = room.room_id
                state.pos = spawn_pos
                state.heading_rad = spawn_heading
                events.append(GuidelinesRecomputed(targets=[]))
                if room.room_id not in _demon_hp:
                    _demon_hp[room.room_id] = room_data.enemy.health
                break

    # ==== SHOOTING (only in room mode) ====
    if actions.fire and state.mode == "room" and state.current_room_id is not None:
        room = pack.rooms.get(state.current_room_id)
        if room is not None:
            eye = (state.pos[0], state.pos[1] + EYE_HEIGHT_M, state.pos[2])
            ray = reticle_ray(eye, state.heading_rad, state.pitch_rad,
                              actions.aim_x, actions.aim_y)
            hit = nav.nearest_panel(ray, SHOOT_MAX_DIST)

            # Demon hit detection: ray passing near the demon spawn?
            demon_hit = False
            dir_len = sqrt(ray.direction[0] ** 2 + ray.direction[1] ** 2
                           + ray.direction[2] ** 2)
            if dir_len > 0:
                check_dist = 15.0
                ux = ray.direction[0] / dir_len
                uy = ray.direction[1] / dir_len
                uz = ray.direction[2] / dir_len
                hit_x = eye[0] + ux * check_dist
                hit_y = eye[1] + uy * check_dist
                hit_z = eye[2] + uz * check_dist
                dx_d = hit_x - room.enemy.spawn_xyz[0]
                dy_d = hit_y - room.enemy.spawn_xyz[1]
                dz_d = hit_z - room.enemy.spawn_xyz[2]
                demon_hit = sqrt(dx_d * dx_d + dy_d * dy_d + dz_d * dz_d) <= DEMON_RADIUS

            # Current room progress
            lvl_prog = state.save.levels.setdefault(level_id, LevelProgress())
            rp = lvl_prog.rooms.setdefault(state.current_room_id, RoomProgress())

            # Current demon HP
            curr_hp = _demon_hp.get(state.current_room_id, room.enemy.health)

            # Resolve the shot
            evs, new_lit, new_hidden, new_hp, cleared = resolve_shot(
                room, hit, demon_hit, state.lit, rp.hidden_door_open, curr_hp)

            # Apply deltas
            state.lit = new_lit
            rp.hidden_door_open = new_hidden
            _demon_hp[state.current_room_id] = new_hp

            # Sync pairs_on from lit (only pair_ids belonging to this room)
            valid_pids = {p.pair_id for p in room.panel_pairs}
            rp.pairs_on = sorted([pid for pid in new_lit if pid in valid_pids])

            if cleared:
                state.cleared.add(state.current_room_id)
                rp.room_cleared = True
                rp.enemy_defeated = True

            # LevelComplete: all floorplan rooms have room_cleared?
            all_cleared = True
            for fr in pack.floorplan.rooms:
                lprog = state.save.levels.get(level_id, LevelProgress())
                rprog = lprog.rooms.get(fr.room_id)
                if rprog is None or not rprog.room_cleared:
                    all_cleared = False
                    break
            if all_cleared:
                rp_level = state.save.levels.setdefault(level_id, LevelProgress())
                rp_level.level_complete = True
                events.append(LevelComplete(level_id=level_id))

            events.extend(evs)

    # ==== READ TOGGLE ====
    if actions.read_toggle:
        events.append(ReadModeToggled(on=True, asset_id=None))

    return events
