from principia.ceiling.equations import CeilingManager


class FakeBandEntity:
    def __init__(self):
        self.enabled = True
        self.color = None
        self.faded = False

    def fade_in(self, duration=1):
        self.faded = True


class FakeBand:  # stands in for schema.CeilingBand
    def __init__(self, hidden=True):
        self.hidden_until_demon_dead = hidden


def _mgr():
    return CeilingManager(assets=None)


def test_register_hidden_band():
    cm = _mgr()
    e = FakeBandEntity()
    cm.register_band("r1", FakeBand(hidden=True), e)
    assert e.enabled is False
    assert e.color is not None


def test_register_visible_band():
    cm = _mgr()
    e2 = FakeBandEntity()
    cm.register_band("r1", FakeBand(hidden=False), e2)
    assert e2.enabled is True


def test_reveal_and_idempotent():
    cm = _mgr()
    e = FakeBandEntity()
    cm.register_band("r1", FakeBand(hidden=True), e)

    cm.reveal("r1")
    assert e.enabled is True
    assert e.faded is True

    e.faded = False
    cm.reveal("r1")
    assert e.faded is False  # idempotent, did not re-fire


def test_spray_empty_noop():
    cm = _mgr()
    cm.spray_from((0, 0, 0), [])  # must not raise
