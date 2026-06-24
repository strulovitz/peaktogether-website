from principia.player.shooter import Shooter, clamp_pitch


class FakeCam:
    pass


class FakeInput:
    pass


class FakePanel:
    kind = "panel"
    block_id = "b1"


class FakeDemon:
    kind = "demon"


class FakeSecret:
    kind = "secret"
    door_id = "d1"


def test_clamp_pitch():
    assert clamp_pitch(100, 70) == 70
    assert clamp_pitch(-100, 70) == -70
    assert clamp_pitch(30, 70) == 30


def test_dispatch_hit_routes_correctly():
    calls = {}

    def on_wall(block_id):
        calls["wall"] = block_id

    def on_demon(entity, point):
        calls["demon"] = (entity, point)

    def on_secret(door_id):
        calls["secret"] = door_id

    s = Shooter(FakeCam(), FakeInput())
    s.register_hit_handlers(on_wall, on_demon, on_secret)

    s._dispatch_hit(FakePanel(), (0, 0, 0))
    assert calls["wall"] == "b1"

    demon = FakeDemon()
    s._dispatch_hit(demon, (1, 2, 3))
    assert calls["demon"] == (demon, (1, 2, 3))

    s._dispatch_hit(FakeSecret(), (0, 0, 0))
    assert calls["secret"] == "d1"


def test_dispatch_hit_unknown_kind_no_call():
    calls = {}

    def on_wall(block_id):
        calls["wall"] = block_id

    class FakeUnknown:
        kind = None

    class FakeNoKind:
        pass

    s = Shooter(FakeCam(), FakeInput())
    s.register_hit_handlers(on_wall, None, None)

    s._dispatch_hit(FakeUnknown(), (0, 0, 0))
    s._dispatch_hit(FakeNoKind(), (0, 0, 0))
    assert "wall" not in calls


def test_dispatch_hit_none_handlers_no_crash():
    s = Shooter(FakeCam(), FakeInput())
    # handlers default to None; must not crash
    s._dispatch_hit(FakePanel(), (0, 0, 0))
    s._dispatch_hit(FakeDemon(), (0, 0, 0))
    s._dispatch_hit(FakeSecret(), (0, 0, 0))
