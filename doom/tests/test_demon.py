import pytest


def test_health_lethal_on_third_hit():
    from principia.enemy.demon import _Health
    h = _Health(3)
    assert h.hit() is False
    assert h.hit() is False
    assert h.hit() is True
    assert h.hit() is False
    assert h.dead is True


def test_health_one_hp_lethal_immediately():
    from principia.enemy.demon import _Health
    assert _Health(1).hit() is True


def test_add_offset():
    from principia.enemy.demon import add_offset
    r = add_offset((6, 1.2, 6), (-0.2, 0.25, 0.55))
    assert r == pytest.approx((5.8, 1.45, 6.55))


def test_hex_to_rgb():
    from principia.enemy.demon import hex_to_rgb
    assert hex_to_rgb("#FF7AB6") == (255, 122, 182)


def test_demon_live_death_callback_once():
    try:
        from ursina import Ursina
        app = Ursina(window_type="offscreen")
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"no display / Ursina unavailable: {e}")

    from pathlib import Path
    from principia.content.loader import load_level
    from principia.enemy.demon import Demon

    pack_dir = Path("content_packs/principia")
    try:
        level = load_level(pack_dir, "fixture")   # FIX: level id is "fixture"
        spec = level.rooms["lemma1"].demon
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"fixture unavailable: {e}")

    demon = Demon(spec, tuple(spec.position))

    fired = {"n": 0}
    demon.on_death(lambda: fired.__setitem__("n", fired["n"] + 1))

    for _ in range(spec.hp):
        demon.hit(None)

    assert demon.is_dead() is True
    assert fired["n"] == 1

    demon.hit(None)
    assert fired["n"] == 1
