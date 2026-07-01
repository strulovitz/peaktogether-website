"""Headless tests for build/room_from_spec.py. No Asymptote/LaTeX executed -- pure text/JSON.
The lemma_2 round-trip is the anchor: spec -> recipe/room_source that deep-equal the gold,
and an .asy whose structure (pens, drawAll guards, label lines) matches the gold."""

import json
from pathlib import Path

import pytest

from build.room_from_spec import (
    build_room, parse, validate, emit_recipe, emit_asy, emit_room_source, SpecError,
)

SPEC_DIR = Path(__file__).parent / "room_specs"
GOLD_DIR = Path(__file__).parent.parent / "levels" / "principia_bk1_inverse_square"


def _spec(name):
    return (SPEC_DIR / f"{name}.room").read_text(encoding="utf-8")


# ---- ANCHOR: lemma_2 round-trip ----

def test_lemma_2_recipe_matches_gold():
    recipe = emit_recipe(parse(_spec("lemma_2")))
    got = json.loads(recipe.model_dump_json(exclude_none=True))
    gold = json.loads((GOLD_DIR / "recipes" / "lemma_2.f1.json").read_text())
    assert got["figure_id"] == gold["figure_id"]
    assert got["n_steps"] == gold["n_steps"]
    assert [o["name"] for o in got["ops"]] == [o["name"] for o in gold["ops"]]
    for go, ge in zip(got["ops"], gold["ops"]):
        assert go.get("op") == ge.get("op")
        assert go.get("draw", {}).get("local_color") == ge.get("draw", {}).get("local_color")
        assert go.get("draw", {}).get("step") == ge.get("draw", {}).get("step")
        assert go.get("draw", {}).get("is_heart", False) == ge.get("draw", {}).get("is_heart", False)


def test_lemma_2_room_source_matches_gold():
    room = emit_room_source(parse(_spec("lemma_2")))
    got = json.loads(room.model_dump_json(exclude_none=True))
    gold = json.loads((GOLD_DIR / "room_sources" / "lemma_2.json").read_text())
    assert got["node_id"] == gold["node_id"]
    assert got["final_pair_id"] == gold["final_pair_id"]
    assert [b["pair_id"] for b in got["blocks"]] == [b["pair_id"] for b in gold["blocks"]]
    for gb, eb in zip(got["blocks"], gold["blocks"]):
        gset = {(c["name"], c["hex"]) for c in gb["text"]["colors_used"]}
        eset = {(c["name"], c["hex"]) for c in eb["text"]["colors_used"]}
        assert gset == eset
    assert [e["eq_id"] for e in got["ceiling_equations"]] == \
           [e["eq_id"] for e in gold["ceiling_equations"]]


def test_lemma_2_asy_structure():
    asy = emit_asy(parse(_spec("lemma_2")))
    for pen in ("curveblue", "basegreen", "sideorange", "inscpurple", "circred"):
        assert f"pen {pen} = rgb(" in asy
    assert "pen BLACK = rgb(0,0,0)" in asy
    for k in (1, 2, 3):
        assert f"bool on{k} = (highlight=={k});" in asy
    assert "if (on1) draw(curve" in asy or "if (on1) " in asy
    assert "? curveblue : BLACK" in asy
    assert asy.strip().endswith("drawAll(highlight);")
    assert "usersetting();" in asy
    assert "0xFF" not in asy and "0x" not in asy


# ---- prop_4 equation room ----

def test_prop_4_equation():
    spec = parse(_spec("prop_4"))
    validate(spec)
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert all(o.op == "label" for o in recipe.ops)
    room = emit_room_source(spec)
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"forceorange", "velblue", "radgreen"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "import geometry;" in asy
    assert "_termpos_1_1" in asy


# ---- law_1 text room ----

def test_law_1_text():
    spec = parse(_spec("law_1"))
    validate(spec)
    assert emit_recipe(spec) is None
    room = emit_room_source(spec)
    assert len(room.blocks) == 4
    assert room.final_pair_id == "law_1.s4"
    names = {c.name for c in room.figures[0].colors_used}
    assert {"restblue", "motiongreen", "forceorange", "topblue", "dragred",
            "planetpurple", "freeteal", "projblue", "gravorange"} == names
    br = build_room(_spec("law_1"), Path("/tmp/quake_law1"), write=False)
    assert br.recipe_path is None


# ---- textcolor scan consistency ----

import re
_TC = re.compile(r"\\textcolor\{([^}]+)\}\{")


@pytest.mark.parametrize("name", ["lemma_2", "lemma_3", "lemma_4", "lemma_5", "lemma_6", "lemma_7", "lemma_9", "lemma_10", "lemma_11", "lemma_12", "prop_1", "prop_2", "prop_6", "prop_7", "prop_11", "prop_13", "prop_4", "law_1", "law_2"])
def test_textcolor_scan_consistency(name):
    room = emit_room_source(parse(_spec(name)))
    for b in room.blocks:
        in_latex = set(_TC.findall(b.text.latex))
        declared = {c.name for c in b.text.colors_used}
        assert in_latex == declared, f"{name} {b.block_id}: {in_latex} != {declared}"


# ---- law_2 equation room ----

def test_law_2_equation():
    spec = parse(_spec("law_2"))
    validate(spec)
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 2
    room = emit_room_source(spec)
    assert len(room.blocks) == 2
    assert room.final_pair_id == "law_2.s2"
    names = {c.name for c in room.figures[0].colors_used}
    assert {"motionblue", "forceorange", "dirgreen"} <= names
    assert len(room.ceiling_equations) == 2

# ---- lemma_5 geometry room ----

def test_lemma_5_geometry():
    spec = parse(_spec("lemma_5"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 2
    assert spec.final_step == 2
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 2
    room = emit_room_source(spec)
    assert len(room.blocks) == 2
    assert room.final_pair_id == "lemma_5.s2"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"simblue", "simgreen", "sideorange"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "import geometry;" in asy
    assert "pen simblue = rgb(" in asy
    assert "pen simgreen = rgb(" in asy
    assert "pen sideorange = rgb(" in asy
    assert "STABILO" in asy
    assert "usersetting();" in asy
    assert asy.strip().endswith("drawAll(highlight);")


# ---- lemma_6 geometry room ----

def test_lemma_6_geometry():
    spec = parse(_spec("lemma_6"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "lemma_6.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"arcblue", "chordgreen", "tanorange", "anglered"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen arcblue = rgb(" in asy
    assert "pen chordgreen = rgb(" in asy
    assert "pen tanorange = rgb(" in asy
    assert "pen anglered = rgb(" in asy
    assert "usersetting();" in asy


# ---- lemma_12 geometry room ----

def test_lemma_12_geometry():
    spec = parse(_spec("lemma_12"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 1
    assert spec.final_step == 1
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 1
    room = emit_room_source(spec)
    assert len(room.blocks) == 1
    assert room.final_pair_id == "lemma_12.s1"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"ellblue", "conjorange", "pargreen"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen ellblue = rgb(" in asy
    assert "pen conjorange = rgb(" in asy
    assert "pen pargreen = rgb(" in asy
    assert "usersetting();" in asy


# ---- lemma_3 geometry room ----

def test_lemma_3_geometry():
    spec = parse(_spec("lemma_3"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 2
    assert spec.final_step == 2
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 2
    room = emit_room_source(spec)
    assert len(room.blocks) == 2
    assert room.final_pair_id == "lemma_3.s2"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"stepblue", "basegreen", "boundred", "widthorange"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen stepblue = rgb(" in asy
    assert "pen boundred = rgb(" in asy


# ---- lemma_4 geometry room ----

def test_lemma_4_geometry():
    spec = parse(_spec("lemma_4"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "lemma_4.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"figaviolet", "figbteal", "corrorange"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen figaviolet = rgb(" in asy
    assert "pen figbteal = rgb(" in asy
    assert "pen corrorange = rgb(" in asy


# ---- lemma_7 geometry room ----

def test_lemma_7_geometry():
    spec = parse(_spec("lemma_7"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "lemma_7.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"arcblue", "auxpurple", "equalteal"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen arcblue = rgb(" in asy
    assert "pen auxpurple = rgb(" in asy
    assert "pen equalteal = rgb(" in asy
    assert "usersetting();" in asy


# ---- lemma_9 geometry room ----

def test_lemma_9_geometry():
    spec = parse(_spec("lemma_9"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "lemma_9.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"lineblue", "curvegreen", "ordorange", "auxpurple", "arearred"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen lineblue = rgb(" in asy
    assert "pen auxpurple = rgb(" in asy
    assert "pen arearred = rgb(" in asy


# ---- lemma_10 geometry room ----

def test_lemma_10_geometry():
    spec = parse(_spec("lemma_10"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 2
    assert spec.final_step == 2
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 2
    room = emit_room_source(spec)
    assert len(room.blocks) == 2
    assert room.final_pair_id == "lemma_10.s2"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"timeblue", "velgreen", "spacered"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen timeblue = rgb(" in asy
    assert "pen velgreen = rgb(" in asy
    assert "pen spacered = rgb(" in asy
    assert "usersetting();" in asy


# ---- lemma_11 geometry room ----

def test_lemma_11_geometry():
    spec = parse(_spec("lemma_11"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "lemma_11.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"tanblue", "arcgreen", "subred", "auxpurple", "relorange"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen tanblue = rgb(" in asy
    assert "pen subred = rgb(" in asy
    assert "pen relorange = rgb(" in asy
    assert "usersetting();" in asy


# ---- prop_1 geometry room ----

def test_prop_1_geometry():
    spec = parse(_spec("prop_1"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 4
    assert spec.final_step == 4
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 4
    room = emit_room_source(spec)
    assert len(room.blocks) == 4
    assert room.final_pair_id == "prop_1.s4"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"centerorange", "pathblue", "radigreen", "arearpurple", "impulsered"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen centerorange = rgb(" in asy
    assert "pen impulsered = rgb(" in asy
    assert "usersetting();" in asy


# ---- prop_2 geometry room ----

def test_prop_2_geometry():
    spec = parse(_spec("prop_2"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "prop_2.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"centerorange", "fanpurple", "deflectblue", "radialred"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen fanpurple = rgb(" in asy
    assert "pen deflectblue = rgb(" in asy
    assert "usersetting();" in asy


# ---- prop_6 geometry room ----

def test_prop_6_geometry():
    spec = parse(_spec("prop_6"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 4
    assert spec.final_step == 4
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 4
    room = emit_room_source(spec)
    assert len(room.blocks) == 4
    assert room.final_pair_id == "prop_6.s4"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"centerorange", "arcblue", "tangreen", "parblue", "perpred", "measpurple"} <= {n for n, _ in used}
    asy = emit_asy(spec)
    assert "pen measpurple = rgb(" in asy
    assert "pen tangreen = rgb(" in asy
    assert "usersetting();" in asy


# ---- prop_7 geometry room ----

def test_prop_7_geometry():
    spec = parse(_spec("prop_7"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 3
    assert spec.final_step == 3
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 3
    room = emit_room_source(spec)
    assert len(room.blocks) == 3
    assert room.final_pair_id == "prop_7.s3"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"circblue", "centerorange", "radgreen", "tanteal", "diampurple", "constred"} <= {n for n, _ in used}


# ---- prop_11 geometry room ----

def test_prop_11_geometry():
    spec = parse(_spec("prop_11"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 5
    assert spec.final_step == 5
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 5
    room = emit_room_source(spec)
    assert len(room.blocks) == 5
    assert room.final_pair_id == "prop_11.s5"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"ellblue", "fociorange", "radgreen", "equalpurple", "parteal", "latusred", "resultblue"} <= {n for n, _ in used}


# ---- prop_13 geometry room ----

def test_prop_13_geometry():
    spec = parse(_spec("prop_13"))
    validate(spec)
    assert spec.kind == "geometry"
    assert len(spec.stations) == 4
    assert spec.final_step == 4
    recipe = emit_recipe(spec)
    assert recipe is not None
    assert recipe.n_steps == 4
    room = emit_room_source(spec)
    assert len(room.blocks) == 4
    assert room.final_pair_id == "prop_13.s4"
    used = {(c.name, c.hex) for c in room.figures[0].colors_used}
    assert {"parabblue", "fociorange", "radgreen", "constpurple", "relgreen", "resultred"} <= {n for n, _ in used}


# ---- rejection tests ----

def test_reject_global_palette():
    bad = ("room x\nkind text\nimport e\ncaption c\nfinal 1\ncolor early #112233\nstation 1\n"
           "  gloss g\n  color a #445566\n  panel\n    phrase a \"w\" heart\n  text\n    {a|w}\n")
    with pytest.raises(SpecError) as ei:
        parse(bad)
    assert "before any `station`" in ei.value.msg


def test_reject_missing_heart():
    bad = ("room x\nkind text\nimport e\ncaption c\nfinal 1\nstation 1\n  gloss g\n"
           "  color a #445566\n  panel\n    phrase a \"w\"\n  text\n    {a|w}\n")
    with pytest.raises(SpecError) as ei:
        validate(parse(bad))
    assert "no `heart`" in ei.value.msg


def test_reject_undeclared_color():
    bad = ("room x\nkind text\nimport e\ncaption c\nfinal 1\nstation 1\n  gloss g\n"
           "  color a #445566\n  panel\n    phrase a \"w\" heart\n  text\n    {ghost|w}\n")
    with pytest.raises(SpecError) as ei:
        validate(parse(bad))
    assert "ghost" in ei.value.msg


def test_reject_unused_color():
    bad = ("room x\nkind text\nimport e\ncaption c\nfinal 1\nstation 1\n  gloss g\n"
           "  color a #445566\n  color spare #778899\n  panel\n    phrase a \"w\" heart\n"
           "  text\n    {a|w}\n")
    with pytest.raises(SpecError) as ei:
        validate(parse(bad))
    assert "spare" in ei.value.msg and "never used" in ei.value.msg


def test_reject_step_gap():
    bad = ("room x\nkind text\nimport e\ncaption c\nfinal 1\nstation 1\n  gloss g\n"
           "  color a #445566\n  panel\n    phrase a \"w\" heart\n  text\n    {a|w}\n"
           "station 3\n  gloss g\n  color b #112233\n  panel\n    phrase b \"x\" heart\n"
           "  text\n    {b|x}\n")
    with pytest.raises(SpecError) as ei:
        validate(parse(bad))
    assert "contiguous" in ei.value.msg or "expected 2" in ei.value.msg


def test_reject_bad_ref():
    bad = ("room x\nkind geometry\nimport e\ncaption c\nfinal 1\nstation 1\n  gloss g\n"
           "  color a #445566\n  panel\n    segment s X Y color=a heart\n  text\n    {a|w}\n")
    with pytest.raises(SpecError) as ei:
        validate(parse(bad))
    assert "undefined reference" in ei.value.msg


def test_ceiling_ids():
    spec = parse(_spec("lemma_2"))
    room = emit_room_source(spec)
    ids = [e.eq_id for e in room.ceiling_equations]
    assert ids == ["lemma_2.eq0", "lemma_2.eq1"]
