from map.raw_models import Palette, GroupColor

TEST_PALETTE = Palette(
    schema_version="1.0", pack_id="test",
    groups={
        "path": GroupColor(hi="#FFE08A", ink="#E8A200"),
        "radius": GroupColor(hi="#A8D8FF", ink="#1E6FE0"),
        "construction": GroupColor(hi="#FFB3C7", ink="#D81B60"),
    },
    grey_ink="#7A7A7A", grey_text="#8A8A8A", bg_key="#FF00FF",
    map_importance={"1": "#111111", "2": "#222222", "3": "#333333",
                    "4": "#444444", "5": "#555555"},
    map_node_default="#666666",
)

VALID_ASY = """// figure.prop_1.f1.asy
import prooffig;

// --------- ZONE 1: settings (fixed) ---------
int highlight=-1;
size(12cm);

// --------- ZONE 2: construction ---------
pair S=(0,-2), A=(-3,2), B=(0,2.6), C=(3,2);

// --------- ZONE 3: registration ---------
elem((path)(A--B), "path", 1);    elem((path)(B--C), "path", 1);
lbl("$A$", A, "path", 1, NW);     lbl("$B$", B, "path", 1, N);   lbl("$C$", C, "path", 1, NE);
elem((path)(S--A), "radius", 2);  elem((path)(S--B), "radius", 2);  elem((path)(S--C), "radius", 2);
lbl("$S$", S, "radius", 2, S);
elem((path)(C--c), "construction", 3);  elem((path)(S--c), "construction", 3);
lbl("$c$", c, "construction", 3, NW);

// --------- ZONE 4: render (fixed) ---------
drawAll(highlight);
"""


def test_valid_file(tmp_path):
    from bake.prooffig_check import lint
    p = tmp_path / "fig.asy"
    p.write_text(VALID_ASY)
    v = lint(p, TEST_PALETTE, n_steps=3)
    assert v == []


def test_missing_import(tmp_path):
    from bake.prooffig_check import lint
    asy = VALID_ASY.replace("import prooffig;", "// no import")
    p = tmp_path / "fig.asy"
    p.write_text(asy)
    v = lint(p, TEST_PALETTE, n_steps=2)
    assert any("MISSING_IMPORT" in x for x in v)


def test_missing_drawall(tmp_path):
    from bake.prooffig_check import lint
    asy = VALID_ASY.replace("drawAll(highlight);", "// missing")
    p = tmp_path / "fig.asy"
    p.write_text(asy)
    v = lint(p, TEST_PALETTE, n_steps=2)
    assert any("MISSING_DRAWALL" in x for x in v)


def test_unknown_group(tmp_path):
    from bake.prooffig_check import lint
    asy = VALID_ASY.replace('"path"', '"ghost"')
    p = tmp_path / "fig.asy"
    p.write_text(asy)
    v = lint(p, TEST_PALETTE, n_steps=2)
    assert any("UNKNOWN_GROUP" in x and "ghost" in x for x in v)


def test_step_gap(tmp_path):
    from bake.prooffig_check import lint
    asy = VALID_ASY.replace('"radius", 2', '"radius", 3')
    p = tmp_path / "fig.asy"
    p.write_text(asy)
    v = lint(p, TEST_PALETTE, n_steps=3)
    assert any("STEP_GAP" in x and "2" in x for x in v)


def test_series_ok(tmp_path):
    from bake.prooffig_check import lint
    asy = """// fig.asy
import prooffig;
// --------- ZONE 1: settings ---------
int highlight=-1;
size(12cm);
// --------- ZONE 2: construction ---------
// --------- ZONE 3: registration ---------
elem((path)(A--B), "swept_area", 3);  elem((path)(C--D), "swept_area", 3);
lbl("$A$", (0,0), "path", 1, N);
lbl("$B$", (0,0), "path", 2, N);
// --------- ZONE 4: render ---------
drawAll(highlight);
"""
    p2 = Palette(
        schema_version="1.0", pack_id="test",
        groups={
            "path": GroupColor(hi="#FFE08A", ink="#E8A200"),
            "swept_area": GroupColor(hi="#E1BEE7", ink="#8E24AA"),
        },
        grey_ink="#7A7A7A", grey_text="#8A8A8A", bg_key="#FF00FF",
        map_importance={"1": "#111111", "2": "#222222", "3": "#333333",
                        "4": "#444444", "5": "#555555"},
        map_node_default="#666666",
    )
    p = tmp_path / "fig.asy"
    p.write_text(asy)
    v = lint(p, p2, n_steps=3)
    assert v == []
