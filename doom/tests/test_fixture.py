"""Validates the golden-fixture content pack against the frozen schema.

Runs WITHOUT any runtime modules implemented yet — it only needs schema.py.
This is your guard against silent interface drift between child chats.
"""
import json
from pathlib import Path

from principia import schema

PACK = Path("content_packs/principia")


def _load(name):
    return json.loads((PACK / name).read_text(encoding="utf-8"))


def test_concept_graph_validates():
    g = schema.ConceptGraph.model_validate(_load("concept_graph.json"))
    assert g.level_id == "fixture"
    assert {n.id for n in g.nodes} == {"lemma1", "lemma2"}


def test_floorplan_validates():
    fp = schema.Floorplan.model_validate(_load("floorplan.json"))
    assert fp.ceiling_h == 3.0
    assert fp.corridors[0].from_room == "lemma1"   # alias 'from' works
    assert fp.corridors[0].to_room == "lemma2"


def test_room_content_validates():
    rc = schema.RoomContent.model_validate(_load("rooms/lemma1.json"))
    assert rc.room_id == "lemma1"
    assert rc.demon.demon_id == "demon_lemma1"
    assert rc.secret_door.boss.hp == 5
    assert rc.walls[0].blocks[0].colors["abc"] == "#0072B2"


def test_manifest_validates():
    manifest = _load("manifest.json")
    entries = {k: schema.AssetEntry.model_validate(v) for k, v in manifest.items()}
    assert entries["l1_step1"].w_px == 1024


def test_schema_versions_match():
    for f in ["concept_graph.json", "floorplan.json", "rooms/lemma1.json"]:
        assert _load(f)["schema_version"] == schema.SCHEMA_VERSION
