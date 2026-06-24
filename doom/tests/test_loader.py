from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from principia.content.loader import load_level, load_manifest, validate_pack

PACK = "content_packs/principia"


def test_load_level_basic() -> None:
    level = load_level(PACK, "fixture")
    assert level.level_id == "fixture"
    assert level.floorplan.ceiling_h == 3.0
    assert "lemma1" in level.rooms
    assert level.rooms["lemma1"].demon is not None
    assert level.rooms["lemma1"].demon.demon_id == "demon_lemma1"


def test_load_level_robust_to_missing_room_file() -> None:
    # floorplan lists lemma2 but there is no rooms/lemma2.json; must not crash.
    level = load_level(PACK, "fixture")
    assert "lemma2" not in level.rooms


def test_load_level_wrong_level_id_raises() -> None:
    with pytest.raises(ValueError):
        load_level(PACK, "not_the_fixture")


def test_load_manifest() -> None:
    manifest = load_manifest(PACK)
    assert "l1_step1" in manifest
    assert manifest["l1_step1"].w_px == 1024


def test_validate_pack_only_complains_about_missing_room() -> None:
    # The shipped fixture intentionally lacks rooms/lemma2.json, so the only
    # permitted error is the missing-room report for lemma2.
    errors = validate_pack(PACK)
    for err in errors:
        assert "lemma2" in err, f"unexpected error: {err}"


def test_validate_pack_reports_ghost_room(tmp_path: Path) -> None:
    dst = tmp_path / "pack"
    shutil.copytree(PACK, dst)

    fp_path = dst / "floorplan.json"
    fp = json.loads(fp_path.read_text(encoding="utf-8"))
    fp["rooms"].append(
        {
            "id": "ghost",
            "rect": {"x": 0, "z": 100, "w": 4, "d": 4},
            "center": [2, 0, 102],
            "name_tile": "",
            "doors": [],
        }
    )
    fp_path.write_text(json.dumps(fp), encoding="utf-8")

    errors = validate_pack(str(dst))
    assert errors
    assert any("ghost" in e for e in errors)
