from __future__ import annotations

import pytest

from principia.schema import Rect
from principia.world.builder import place_panels, PanelPlacement, PANEL_INSET


def test_place_panels_north():
    placements = place_panels(Rect(x=0, z=0, w=12, d=12), "N", ["a", "b"], 3.0)
    assert len(placements) == 2
    for p in placements:
        assert isinstance(p, PanelPlacement)
        assert p.rotation_y == 180
        # N wall at max Z, inset toward room interior.
        assert p.position[2] == pytest.approx(12 - PANEL_INSET)
        assert p.position[1] == pytest.approx(1.5)
    # X centers at slot*(i+0.5) = 6*0.5, 6*1.5 = 3.0, 9.0
    assert placements[0].position[0] == pytest.approx(3.0)
    assert placements[1].position[0] == pytest.approx(9.0)
    # Equal widths.
    assert placements[0].width == pytest.approx(placements[1].width)


def test_place_panels_east():
    placements = place_panels(Rect(x=0, z=0, w=12, d=12), "E", ["a", "b"], 3.0)
    assert len(placements) == 2
    for p in placements:
        assert p.rotation_y == 270
        # E wall at max X, inset toward room interior.
        assert p.position[0] == pytest.approx(12 - PANEL_INSET)
    # Z centers vary along the wall axis.
    assert placements[0].position[2] == pytest.approx(3.0)
    assert placements[1].position[2] == pytest.approx(9.0)
    assert placements[0].position[2] != placements[1].position[2]
    assert placements[0].width == pytest.approx(placements[1].width)


def test_place_panels_empty():
    assert place_panels(Rect(x=0, z=0, w=12, d=12), "N", [], 3.0) == []


def test_build_room_with_display():
    """Guarded full build; skips cleanly if no display / Ursina unavailable."""
    try:
        from ursina import Ursina  # noqa: F401
        from principia.content.loader import load_level
        from principia.assets.manager import AssetManager
        from principia.world.builder import build_room, CellEntities

        from ursina import Ursina as _U

        app = _U()  # may fail headless -> skip
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Ursina/display unavailable: {exc}")

    try:
        level = load_level("content_packs/principia", "fixture")
        room = next(r for r in level.floorplan.rooms if r.id == "lemma1")
        content = level.rooms["lemma1"]
        assets = AssetManager("content_packs/principia")

        cell = build_room(room, content, assets)

        assert isinstance(cell, CellEntities)
        assert len(cell.panels) == 2
        for panel in cell.panels.values():
            assert panel.kind == "panel"
            assert panel.is_on is False
            assert panel.off_tex is not None
            assert panel.on_tex is not None

        cell.destroy()  # must not raise
    finally:
        try:
            from ursina import application

            application.quit()
        except (Exception, SystemExit):
            pass
