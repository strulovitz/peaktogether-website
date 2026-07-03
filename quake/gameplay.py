"""QUAKE runtime engine — M7 module #13: gameplay.

The brain of the game: pure, headless, deterministic game-logic step.
NO GL, NO window, NO IO, NO RNG. All shared types imported from contracts.
"""
from math import cos, sin, sqrt, atan2

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
# Demon body hit-sphere (matches demon.py: body blob ~1.2 m across, centered
# ~0.6 m above spawn_xyz). Generous radius so the visible demon is easy to hit.
DEMON_BODY_CENTER_DY = 0.6
DEMON_HIT_RADIUS = 0.9
SOCKET_ENTER_RADIUS_M = 1.0
EYE_HEIGHT_M = 1.6
# PITCH_CLAMP_RAD imported from contracts (1.2217, +/-70 degrees)

# ===== DEMON HP TRACKING (module-level mutable) =====
_demon_hp: dict[NodeId, int] = {}


def _ray_hits_demon(eye: Vec3, direction: Vec3, spawn_xyz: Vec3) -> bool:
    """Ray-vs-sphere against the demon body (sphere at spawn_xyz raised by
    DEMON_BODY_CENTER_DY, radius DEMON_HIT_RADIUS). True if the shot ray hits
    within SHOOT_MAX_DIST. PURE."""
    cx = spawn_xyz[0]
    cy = spawn_xyz[1] + DEMON_BODY_CENTER_DY
    cz = spawn_xyz[2]
    dlen = sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
    if dlen <= 0.0:
        return False
    ux, uy, uz = direction[0] / dlen, direction[1] / dlen, direction[2] / dlen
    mx, my, mz = eye[0] - cx, eye[1] - cy, eye[2] - cz
    b = mx * ux + my * uy + mz * uz
    c = mx * mx + my * my + mz * mz - DEMON_HIT_RADIUS * DEMON_HIT_RADIUS
    if c > 0.0 and b > 0.0:      # origin outside sphere and pointing away
        return False
    disc = b * b - c
    if disc < 0.0:
        return False
    t = -b - sqrt(disc)
    if t < 0.0:
        t = 0.0
    return t <= SHOOT_MAX_DIST


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


def _teleport_through_door(state: GameState, pack: Pack, eid: str,
                           events: list) -> None:
    """FLAT design: a door teleports the player straight into the connected
    room, arriving at that room's matching door (as if stepping out the far
    side). No corridors, no walking between rooms. Mutates state; appends events.
    """
    from logutil import log as _log

    src_room = pack.rooms.get(state.current_room_id)
    if src_room is None:
        return

    # Which room does this door lead to?
    dest_room_id = None
    for d in src_room.doors:
        if d.edge_id == eid:
            dest_room_id = d.neighbor_id
            break
    if dest_room_id is None:
        return

    dest_room = pack.rooms.get(dest_room_id)
    if dest_room is None:
        return

    # Arrive at the destination room's door that shares this edge.
    spawn_pos = None
    spawn_heading = 0.0
    for d in dest_room.doors:
        if d.edge_id == eid:
            spawn_pos = d.spawn_xyz
            spawn_heading = d.spawn_heading_rad
            break
    if spawn_pos is None and dest_room.doors:
        spawn_pos = dest_room.doors[0].spawn_xyz
        spawn_heading = dest_room.doors[0].spawn_heading_rad
    if spawn_pos is None:
        return

    _log(f"gameplay: teleport {state.current_room_id} -> {dest_room_id} via {eid}")
    state.current_room_id = dest_room_id
    state.pos = spawn_pos
    state.heading_rad = spawn_heading
    # Keep the persisted mirror correct so a save resumes in the right room.
    state.save.player.current_room_id = dest_room_id
    state.save.player.mode = "room"
    events.append(ModeSwitch(to="room", room_id=dest_room_id, via_edge_id=None))
    events.append(GuidelinesRecomputed(targets=[]))
    if dest_room_id not in _demon_hp:
        _demon_hp[dest_room_id] = dest_room.enemy.health


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
    str_x = -sin(state.heading_rad)   # right strafe (D=+1 -> right, A=-1 -> left)
    str_z = cos(state.heading_rad)

    dx = (fwd_x * actions.move_y + str_x * actions.move_x) * WALK_SPEED_M_S * dt
    dz = (fwd_z * actions.move_y + str_z * actions.move_x) * WALK_SPEED_M_S * dt
    state.pos = nav.resolve_player_motion(state.pos, (dx, 0.0, dz))

    # ==== MODE-SWITCH ====
    level_id = pack.floorplan.level_id

    # FLAT design: doors teleport between rooms; there is no corridor mode.
    if state.mode == "room":
        eid = nav.door_at(state.pos)
        if eid is not None:
            _teleport_through_door(state, pack, eid, events)

    # ==== SHOOTING (only in room mode) ====
    if actions.fire and state.mode == "room" and state.current_room_id is not None:
        room = pack.rooms.get(state.current_room_id)
        if room is not None:
            eye = (state.pos[0], state.pos[1] + EYE_HEIGHT_M, state.pos[2])
            ray = reticle_ray(eye, state.heading_rad, state.pitch_rad,
                              actions.aim_x, actions.aim_y)
            hit = nav.nearest_panel(ray, SHOOT_MAX_DIST)

            # Current room progress
            lvl_prog = state.save.levels.setdefault(level_id, LevelProgress())
            rp = lvl_prog.rooms.setdefault(state.current_room_id, RoomProgress())

            # Demon hit: proper ray-vs-sphere against the demon's body, but ONLY
            # once the hidden door has opened (i.e. the demon has appeared).
            demon_hit = False
            if rp.hidden_door_open:
                demon_hit = _ray_hits_demon(eye, ray.direction, room.enemy.spawn_xyz)

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
