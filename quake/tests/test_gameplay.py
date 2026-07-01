"""Tests for QUAKE gameplay module (M7 #13)."""
import math

from gameplay import step, resolve_shot, reticle_ray
import gameplay as gp
from contracts import (Actions, GameState, Pack, RoomRuntime, PanelPairRT,
    PanelPlacementRT, DoorRT, EnemyRT, Floorplan, FloorRoom, RoomProgress,
    LevelProgress, SaveGame, PlayerSave, Ray, PanelHit, NavQuery)


# ===================== FIXTURE HELPERS =====================

def _placement(wall, slot_idx, wall_slot, center, w=1.0, h=1.0, yaw=0.0):
    return PanelPlacementRT(
        wall=wall, slot_index=slot_idx, wall_slot=wall_slot,
        center_xyz=center, width_m=w, height_m=h, yaw_rad=yaw,
    )


def _pair(pid, step_idx, wall, d_center, yaw):
    dp = _placement(wall, 0, f"{wall}.0", d_center, yaw=yaw)
    tp = _placement(wall, 1, f"{wall}.1", d_center, yaw=yaw)
    return PanelPairRT(
        pair_id=pid, step_index=step_idx,
        drawing_off_asset=f"{pid}.d.off", drawing_on_asset=f"{pid}.d.on",
        text_off_asset=f"{pid}.t.off", text_on_asset=f"{pid}.t.on",
        drawing_placement=dp, text_placement=tp,
    )


def _room(final_pair_id, pairs, room_id="alpha"):
    door = DoorRT(
        edge_id="edge.alpha.to.beta", neighbor_id="beta",
        bearing_rad=0.0, wall="E", center_xyz=(5.0, 1.5, 0.0),
        width_m=1.2, height_m=2.4, normal_yaw_rad=0.0,
        spawn_xyz=(3.0, 0.0, 0.0), spawn_heading_rad=math.pi,
    )
    enemy = EnemyRT(enemy_id="boss.demon", spawn_xyz=(0.0, 0.0, 5.0), health=5)
    return RoomRuntime(
        schema_version="1.0", room_id=room_id, dimensions_m=(10.0, 3.0, 10.0),
        panel_pairs=pairs, final_pair_id=final_pair_id,
        hidden_door_wall_slot="N.0", doors=[door], enemy=enemy,
        ceiling_equations=[],
    )


def _floorroom(room_id, x, z, importance=3):
    return FloorRoom(
        room_id=room_id, map_xz=(x, z), importance=importance,
        map_radius_m=2.0, map_color="#ffffff", socket_y=0.0,
    )


def _stub_pack(room, extra_floor_rooms=None, extra_rooms=None):
    frooms = [_floorroom("a", 0.0, 0.0), _floorroom("b", 20.0, 0.0),
              _floorroom("c", 40.0, 0.0)]
    if extra_floor_rooms is not None:
        frooms = extra_floor_rooms
    fp = Floorplan(
        schema_version="1.0", level_id="lvl1", seed=1,
        rooms=frooms, corridors=[], crossings=[],
    )
    rooms = {room.room_id: room}
    if extra_rooms:
        rooms.update(extra_rooms)

    class _Manifest:
        pass

    class _Palette:
        pass

    return Pack(floorplan=fp, rooms=rooms, manifest=_Manifest(),
                palette=_Palette(), asset_dir="/tmp")


def _stub_state(mode="corridor", room_id=None, pos=(0.0, 0.0, 0.0)):
    save = SaveGame(
        schema_version="1.0", profile_id="p1", levels={},
        player=PlayerSave(level_id="lvl1", mode=mode,
                          current_room_id=room_id, position_xyz=pos,
                          heading_rad=0.0),
    )
    return GameState(
        save=save, mode=mode, current_room_id=room_id, pos=pos,
        heading_rad=0.0, pitch_rad=0.0, lit=set(), cleared=set(),
    )


class _StubNav:
    def __init__(self, hit=None, door=None):
        self._hit = hit
        self._door = door
        self.recorded_delta = None

    def resolve_player_motion(self, start, delta):
        self.recorded_delta = delta
        return start

    def nearest_panel(self, ray, max_dist):
        return self._hit

    def door_at(self, point):
        return self._door


def _stub_nav():
    return _StubNav()


def _stub_nav_with_hit(hit):
    return _StubNav(hit=hit)


def _stub_nav_with_door(edge_id):
    return _StubNav(door=edge_id)


def _hit(pair_id, is_drawing=True, dist=5.0):
    return PanelHit(
        asset_on_id=f"{pair_id}.on", asset_off_id=f"{pair_id}.off",
        pair_id=pair_id, is_drawing=is_drawing, distance=dist,
    )


# ===================== TESTS =====================

def test_door_logic_off_to_on():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0),
             _pair("r.s1", 1, "S", (0, 1.5, -5), math.pi)]
    room = _room("r.s1", pairs)
    hit = _hit("r.s1", is_drawing=True)
    evs, new_lit, new_hidden, new_hp, cleared = resolve_shot(
        room, hit, False, set(), False, 5)
    assert len(evs) == 1
    assert evs[0].event == "panel_lit"
    assert evs[0].pair_id == "r.s1"
    assert "r.s1" in new_lit
    assert new_hidden is False
    assert new_hp == 5
    assert cleared is False


def test_door_logic_open_door():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0),
             _pair("r.s1", 1, "S", (0, 1.5, -5), math.pi)]
    room = _room("r.s1", pairs)
    hit = _hit("r.s1", is_drawing=True)
    evs, new_lit, new_hidden, new_hp, cleared = resolve_shot(
        room, hit, False, {"r.s1"}, False, 5)
    kinds = [e.event for e in evs]
    assert "door_opened" in kinds
    assert "demon_spawned" in kinds
    assert new_hidden is True


def test_door_logic_open_noop():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0),
             _pair("r.s1", 1, "S", (0, 1.5, -5), math.pi)]
    room = _room("r.s1", pairs)
    hit = _hit("r.s1", is_drawing=True)
    evs, new_lit, new_hidden, new_hp, cleared = resolve_shot(
        room, hit, False, {"r.s1"}, True, 5)
    assert evs == []


def test_demon_takes_5_hits():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)]
    room = _room("r.s0", pairs)
    hp = 5
    expected = [4, 3, 2, 1, 0]
    for i, exp_hp in enumerate(expected):
        evs, _, _, new_hp, cleared = resolve_shot(room, None, True, set(), False, hp)
        assert evs[0].event == "demon_hit"
        assert evs[0].hp_remaining == exp_hp
        if exp_hp > 0:
            assert len(evs) == 1
            assert cleared is False
        else:
            kinds = [e.event for e in evs]
            assert "demon_killed" in kinds
            assert "room_cleared" in kinds
            assert cleared is True
        hp = new_hp


def test_god_mode_no_death():
    from contracts import (PanelLit, DoorOpened, DemonSpawned, DemonHit,
        DemonKilled, RoomCleared, LevelComplete, ModeSwitch,
        ReadModeToggled, GuidelinesRecomputed)
    event_types = [PanelLit, DoorOpened, DemonSpawned, DemonHit, DemonKilled,
                   RoomCleared, LevelComplete, ModeSwitch, ReadModeToggled,
                   GuidelinesRecomputed]
    for et in event_types:
        name = et.__name__.lower()
        assert "player" not in name
        assert "death" not in name
        assert "die" not in name


def test_normal_panel_flip():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0),
             _pair("r.s1", 1, "S", (0, 1.5, -5), math.pi)]
    room = _room("r.s1", pairs)
    hit = _hit("r.s0", is_drawing=True)
    evs, new_lit, new_hidden, new_hp, cleared = resolve_shot(
        room, hit, False, set(), False, 5)
    assert len(evs) == 1
    assert evs[0].event == "panel_lit"
    assert evs[0].pair_id == "r.s0"
    assert "r.s0" in new_lit
    assert new_hp == 5


def test_already_on_noop():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0),
             _pair("r.s1", 1, "S", (0, 1.5, -5), math.pi)]
    room = _room("r.s1", pairs)
    hit = _hit("r.s0", is_drawing=True)
    evs, new_lit, new_hidden, new_hp, cleared = resolve_shot(
        room, hit, False, {"r.s0"}, False, 5)
    assert evs == []


def test_mover_only_motion():
    state = _stub_state()
    room = _room("r.s1", [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)], room_id="a")
    frooms = [_floorroom("a", 100.0, 100.0)]
    pack = _stub_pack(room, extra_floor_rooms=frooms)
    nav = _stub_nav()
    h0 = state.heading_rad
    p0 = state.pitch_rad
    actions = Actions(aim_x=5.0, aim_y=5.0, heading_delta=0.0, pitch_delta=0.0)
    step(state, actions, pack, nav, 0.016)
    assert state.heading_rad == h0
    assert state.pitch_rad == p0


def test_walk_uses_nav():
    state = _stub_state()
    frooms = [_floorroom("a", 100.0, 100.0)]
    room = _room("r.s1", [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)], room_id="a")
    pack = _stub_pack(room, extra_floor_rooms=frooms)
    nav = _stub_nav()
    dt = 0.5
    actions = Actions(move_y=1.0, move_x=0.0)
    step(state, actions, pack, nav, dt)
    h = state.heading_rad
    exp_dx = math.cos(h) * gp.WALK_SPEED_M_S * dt
    exp_dz = math.sin(h) * gp.WALK_SPEED_M_S * dt
    assert nav.recorded_delta is not None
    assert math.isclose(nav.recorded_delta[0], exp_dx, abs_tol=1e-9)
    assert math.isclose(nav.recorded_delta[1], 0.0, abs_tol=1e-9)
    assert math.isclose(nav.recorded_delta[2], exp_dz, abs_tol=1e-9)


def test_modeswitch_out_of_room():
    # Player walks through a door: teleports directly to the neighbor room.
    room_alpha = _room("r.s1", [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)], room_id="alpha")
    # Neighbor room (beta) has a door leading back to alpha
    door_back = DoorRT(
        edge_id="edge.beta.to.alpha", neighbor_id="alpha",
        bearing_rad=3.14, wall="W", center_xyz=(-5.0, 1.5, 0.0),
        width_m=1.2, height_m=2.4, normal_yaw_rad=3.14,
        spawn_xyz=(-3.0, 0.0, 0.0), spawn_heading_rad=0.0,
    )
    room_beta = _room("r.s2", [_pair("r.s1", 0, "S", (0, 1.5, 5), 0.0)], room_id="beta")
    room_beta.doors = [door_back]
    state = _stub_state(mode="room", room_id="alpha", pos=(3.0, 0.0, 0.0))
    frooms = [_floorroom("alpha", 100.0, 100.0), _floorroom("beta", 200.0, 200.0)]
    pack = _stub_pack(room_alpha, extra_floor_rooms=frooms, extra_rooms={"beta": room_beta})
    nav = _stub_nav_with_door("edge.alpha.to.beta")
    evs = step(state, Actions(), pack, nav, 0.016)
    sw = [e for e in evs if e.event == "mode_switch"]
    assert len(sw) == 1
    assert sw[0].to == "room"            # stays in room mode
    assert sw[0].room_id == "beta"       # teleports to beta
    assert state.mode == "room"
    assert state.current_room_id == "beta"
    assert state.pos == (-3.0, 0.0, 0.0)  # beta's door spawn
    assert state.heading_rad == 0.0


def test_modeswitch_into_room():
    room = _room("r.s1", [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)], room_id="a")
    frooms = [_floorroom("a", 0.0, 0.0)]
    pack = _stub_pack(room, extra_floor_rooms=frooms)
    state = _stub_state(mode="corridor", pos=(0.0, 0.0, 0.0))
    nav = _stub_nav()
    evs = step(state, Actions(), pack, nav, 0.016)
    sw = [e for e in evs if e.event == "mode_switch"]
    assert len(sw) == 1
    assert sw[0].to == "room"
    assert state.mode == "room"
    door = room.doors[0]
    assert state.pos == door.spawn_xyz
    assert state.heading_rad == door.spawn_heading_rad


def test_read_toggle_no_flip():
    room = _room("r.s1", [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)], room_id="a")
    frooms = [_floorroom("a", 100.0, 100.0)]
    pack = _stub_pack(room, extra_floor_rooms=frooms)
    state = _stub_state(mode="corridor")
    lit_before = set(state.lit)
    mode_before = state.mode
    nav = _stub_nav()
    evs = step(state, Actions(read_toggle=True), pack, nav, 0.016)
    assert any(e.event == "read_toggled" for e in evs)
    assert state.lit == lit_before
    assert state.mode == mode_before


def test_level_complete():
    gp._demon_hp.clear()
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)]
    frooms = [_floorroom("a", 0.0, 0.0), _floorroom("b", 20.0, 0.0)]
    # Build room_b with demon at (0, 1.6, 15) — right at the check_dist=15 point
    enemy_b = EnemyRT(enemy_id="boss.demon", spawn_xyz=(0.0, 1.6, 15.0), health=5)
    door_b = DoorRT(
        edge_id="edge.b.to.c", neighbor_id="c",
        bearing_rad=0.0, wall="E", center_xyz=(5.0, 1.5, 0.0),
        width_m=1.2, height_m=2.4, normal_yaw_rad=0.0,
        spawn_xyz=(3.0, 0.0, 0.0), spawn_heading_rad=math.pi,
    )
    room_b = RoomRuntime(
        schema_version="1.0", room_id="b", dimensions_m=(10.0, 3.0, 10.0),
        panel_pairs=pairs, final_pair_id="r.s0",
        hidden_door_wall_slot="N.0", doors=[door_b], enemy=enemy_b,
        ceiling_equations=[],
    )
    room_a = _room("r.s0", pairs, room_id="a")
    pack = _stub_pack(room_b, extra_floor_rooms=frooms,
                      extra_rooms={"a": room_a})
    state = _stub_state(mode="room", room_id="b", pos=(0.0, 0.0, 0.0))
    state.cleared.add("a")
    lvl = state.save.levels.setdefault("lvl1", LevelProgress())
    lvl.rooms["a"] = RoomProgress(room_cleared=True, enemy_defeated=True)
    state.heading_rad = math.pi / 2  # forward = (0,0,1) +Z toward demon at (0,1.6,5)
    gp._demon_hp["b"] = 1
    nav = _stub_nav()
    evs = step(state, Actions(fire=True), pack, nav, 0.016)
    kinds = [e.event for e in evs]
    assert "level_complete" in kinds
    lc = [e for e in evs if e.event == "level_complete"][0]
    assert lc.level_id == pack.floorplan.level_id
    gp._demon_hp.clear()


def test_resolve_shot_pure():
    pairs = [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0),
             _pair("r.s1", 1, "S", (0, 1.5, -5), math.pi)]
    room = _room("r.s1", pairs)
    lit = {"r.s0"}
    hidden = False
    hp = 5
    hit = _hit("r.s1", is_drawing=True)
    resolve_shot(room, hit, False, lit, hidden, hp)
    assert lit == {"r.s0"}
    assert hidden is False
    assert hp == 5


def test_deterministic_step():
    gp._demon_hp.clear()
    room = _room("r.s1", [_pair("r.s0", 0, "N", (0, 1.5, 5), 0.0)], room_id="a")
    frooms = [_floorroom("a", 100.0, 100.0)]
    pack = _stub_pack(room, extra_floor_rooms=frooms)

    s1 = _stub_state(mode="corridor")
    s2 = _stub_state(mode="corridor")
    actions = Actions(move_y=1.0, read_toggle=True)
    nav1 = _stub_nav()
    nav2 = _stub_nav()
    e1 = step(s1, actions, pack, nav1, 0.5)
    e2 = step(s2, actions, pack, nav2, 0.5)
    assert len(e1) == len(e2)
    for a, b in zip(e1, e2):
        assert a == b
    gp._demon_hp.clear()
