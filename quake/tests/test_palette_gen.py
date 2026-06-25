from map.raw_models import Palette, GroupColor

VERBATIM_PALETTE = Palette(
    schema_version="1.0",
    pack_id="principia",
    groups={
        "path":         GroupColor(hi="#FFE08A", ink="#E8A200"),
        "radius":       GroupColor(hi="#A8D8FF", ink="#1E6FE0"),
        "construction": GroupColor(hi="#FFB3C7", ink="#D81B60"),
        "tangent":      GroupColor(hi="#B9F6CA", ink="#00A35A"),
        "swept_area":   GroupColor(hi="#E1BEE7", ink="#8E24AA"),
    },
    grey_ink="#7A7A7A",
    grey_text="#8A8A8A",
    bg_key="#FF00FF",
    map_importance={"1": "#4F6D7A", "2": "#3FA796", "3": "#E6B800", "4": "#E8743B", "5": "#F5F2E8"},
    map_node_default="#9AA0A6",
)


def test_palette_asy_content(tmp_path):
    from bake.palette_gen import gen

    asy = tmp_path / "palette.asy"
    tex = tmp_path / "palette.tex"
    gen(VERBATIM_PALETTE, asy, tex)

    asy_text = asy.read_text()

    # greyInk present
    assert "pen greyInk = rgb(122/255, 122/255, 122/255)" in asy_text   # #7A7A7A
    # hi function for each group
    assert 'hi(string g)' in asy_text
    # ink function for each group
    assert 'ink(string g)' in asy_text
    # Each group has hi + ink branches
    for group_name in VERBATIM_PALETTE.groups:
        assert f'if (g == "{group_name}")' in asy_text
    # abort on unknown group
    assert 'abort(' in asy_text


def test_palette_tex_content(tmp_path):
    from bake.palette_gen import gen

    asy = tmp_path / "palette.asy"
    tex = tmp_path / "palette.tex"
    gen(VERBATIM_PALETTE, asy, tex)

    tex_text = tex.read_text()

    # xcolor package
    assert r"\usepackage{xcolor}" in tex_text
    # Each group's ink color defined
    assert r"\definecolor{radius}{HTML}{1E6FE0}" in tex_text
    assert r"\definecolor{path}{HTML}{E8A200}" in tex_text
    assert r"\definecolor{construction}{HTML}{D81B60}" in tex_text
    # grey_text
    assert r"\definecolor{grey_text}{HTML}{8A8A8A}" in tex_text
    # \cg macro
    assert r"\newcommand{\cg}[2]{{\color{#1}#2}}" in tex_text


def test_single_group(tmp_path):
    from bake.palette_gen import gen
    from map.raw_models import Palette, GroupColor

    p = Palette(
        schema_version="1.0", pack_id="test",
        groups={"solo": GroupColor(hi="#ABCDEF", ink="#123456")},
        grey_ink="#999999", grey_text="#AAAAAA", bg_key="#FF00FF",
        map_importance={"1":"#111111","2":"#222222","3":"#333333","4":"#444444","5":"#555555"},
        map_node_default="#666666",
    )
    asy = tmp_path / "p.asy"
    tex = tmp_path / "p.tex"
    gen(p, asy, tex)

    asy_text = asy.read_text()
    assert 'abort(' in asy_text  # unknown group handler present

    tex_text = tex.read_text()
    assert r"\definecolor{solo}{HTML}{123456}" in tex_text


def test_deterministic(tmp_path):
    from bake.palette_gen import gen

    asy1 = tmp_path / "a1.asy"; tex1 = tmp_path / "a1.tex"
    asy2 = tmp_path / "a2.asy"; tex2 = tmp_path / "a2.tex"

    gen(VERBATIM_PALETTE, asy1, tex1)
    gen(VERBATIM_PALETTE, asy2, tex2)

    assert asy1.read_text() == asy2.read_text()
    assert tex1.read_text() == tex2.read_text()
