"""Pure-core unit tests for guidelines.py (no GPU/window needed)."""

from guidelines import select_targets, _graph_distances
from contracts import Floorplan, FloorRoom, Corridor, BuildConfig


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

def _room(rid: str, imp: int = 1, xz=(0.0, 0.0)) -> FloorRoom:
    return FloorRoom(
        room_id=rid,
        map_xz=xz,
        importance=imp,
        map_radius_m=2.0,
        map_color="#ffffff",
        socket_y=0.0,
    )


def _corr(src: str, tgt: str) -> Corridor:
    return Corridor(
        corridor_id=f"edge.{src}.to.{tgt}",
        source=src,
        target=tgt,
        height_level=0,
        cruise_y=2.0,
        path_xz=[(0.0, 0.0), (1.0, 0.0)],
        width_m=1.5,
    )


def _fp(rooms, corridors) -> Floorplan:
    return Floorplan(
        schema_version="1.0",
        level_id="lvl_test",
        seed=1,
        rooms=rooms,
        corridors=corridors,
        crossings=[],
    )


def _cfg() -> BuildConfig:
    return BuildConfig(guide_w_imp=0.6, guide_w_dist=0.4, guide_max_lines=3)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_slot1_is_nearest():
    # current -> a (dist 1), current -> a -> b (dist 2). slot1 == a.
    rooms = [_room("cur"), _room("a"), _room("b")]
    corrs = [_corr("cur", "a"), _corr("a", "b")]
    fp = _fp(rooms, corrs)
    out = select_targets(fp, "cur", cleared=set(), cfg=_cfg())
    assert out[0] == "a"

    # tie at dist 1 -> lowest id wins slot1.
    rooms2 = [_room("cur"), _room("zz"), _room("aa")]
    corrs2 = [_corr("cur", "zz"), _corr("cur", "aa")]
    fp2 = _fp(rooms2, corrs2)
    out2 = select_targets(fp2, "cur", cleared=set(), cfg=_cfg())
    assert out2[0] == "aa"


def test_excludes_cleared():
    rooms = [_room("cur"), _room("a"), _room("b")]
    corrs = [_corr("cur", "a"), _corr("cur", "b")]
    fp = _fp(rooms, corrs)
    out = select_targets(fp, "cur", cleared={"a"}, cfg=_cfg())
    assert "a" not in out
    assert "b" in out


def test_excludes_current():
    rooms = [_room("cur"), _room("a")]
    corrs = [_corr("cur", "a")]
    fp = _fp(rooms, corrs)
    # current is uncleared but must never appear.
    out = select_targets(fp, "cur", cleared=set(), cfg=_cfg())
    assert "cur" not in out


def test_score_orders_2_3():
    # slot1 will be the nearest (dist 1). For slots 2-3 a far high-importance
    # room should outscore a near low-importance room.
    #   cur -1- s1
    #   cur -1- near_low (imp 1)
    #   cur -1- s1 ... build distances:
    # Layout: cur connects to s1 (dist1), near_low (dist1)? We need slot1 fixed
    # and two competitors at differing dist/importance.
    rooms = [
        _room("cur"),
        _room("aslot1", imp=1),       # slot1 candidate (lowest id, dist1)
        _room("near_low", imp=1),     # dist 1, low importance
        _room("far_high", imp=5),     # dist 3, high importance
    ]
    rooms.append(_room("mid", imp=1))
    corrs = [
        _corr("cur", "aslot1"),
        _corr("cur", "near_low"),
        _corr("near_low", "mid"),
        _corr("mid", "far_high"),
    ]
    fp = _fp(rooms, corrs)
    out = select_targets(fp, "cur", cleared=set(), cfg=_cfg())
    # slot1 honored = aslot1 (dist1, lowest id among dist1 set).
    assert out[0] == "aslot1"
    # With w_imp=0.6 dominating, far_high (imp5) should be selected over
    # near_low (imp1) for slot 2.
    assert "far_high" in out
    # far_high should rank before near_low in the result order.
    assert out.index("far_high") < (out.index("near_low")
                                     if "near_low" in out else 99)


def test_max_three():
    rooms = [_room("cur")]
    corrs = []
    for i in range(6):
        rid = f"r{i}"
        rooms.append(_room(rid, imp=(i % 5) + 1))
        corrs.append(_corr("cur", rid))
    fp = _fp(rooms, corrs)
    out = select_targets(fp, "cur", cleared=set(), cfg=_cfg())
    assert len(out) == 3


def test_fewer_when_scarce():
    rooms = [_room("cur"), _room("only")]
    corrs = [_corr("cur", "only")]
    fp = _fp(rooms, corrs)
    out = select_targets(fp, "cur", cleared=set(), cfg=_cfg())
    assert len(out) == 1
    assert out == ["only"]


def test_unreachable_excluded():
    # 'island' has no corridor to the cur-connected graph.
    rooms = [_room("cur"), _room("a"), _room("island")]
    corrs = [_corr("cur", "a")]  # island disconnected
    fp = _fp(rooms, corrs)

    dist = _graph_distances(fp, "cur")
    assert "island" not in dist
    assert dist["cur"] == 0
    assert dist["a"] == 1

    out = select_targets(fp, "cur", cleared=set(), cfg=_cfg())
    assert "island" not in out
    assert "a" in out


def test_deterministic():
    rooms = [_room("cur")]
    corrs = []
    for i in range(6):
        rid = f"node{i}"
        rooms.append(_room(rid, imp=(i % 5) + 1))
        corrs.append(_corr("cur", rid))
    fp = _fp(rooms, corrs)
    cfg = _cfg()
    first = select_targets(fp, "cur", cleared=set(), cfg=cfg)
    for _ in range(20):
        again = select_targets(fp, "cur", cleared=set(), cfg=cfg)
        assert again == first
