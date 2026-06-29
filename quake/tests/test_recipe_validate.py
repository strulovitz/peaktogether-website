"""Golden + targeted tests for bake.recipe_validate.validate_recipe.
⚠️ 2026-06-29 — updated for Nir's color model: local_color + is_heart.
"""

from map.raw_models import (
    Recipe,
    Palette,
    StepGloss,
    GroupColor,
    LocalColor,
    FreePoint,
    Segment,
    LineOp,
    Parallel,
    Intersect,
    Draw,
    Label,
)


# Helper: quick LocalColor
def _lc(name: str, hex: str = "#000000") -> LocalColor:
    return LocalColor(name=name, hex=hex)


VERBATIM_RECIPE = Recipe(
    schema_version="1.0",
    figure_id="prop_1.f1",
    node_id="prop_1",
    edition="Newton, Principia, trans. Andrew Motte, 1846 New York English ed.",
    caption="Equal areas swept in equal times: the polygonal path and the parallel construction Cc.",
    n_steps=3,
    steps=[
        StepGloss(index=1, gloss="The body's straight-line path through points A, B, C."),
        StepGloss(index=2, gloss="Radii drawn from the center of force S to A, B, C — the swept triangles."),
        StepGloss(index=3, gloss="Through C draw Cc parallel to SB; triangle SBc equals SAB, proving equal areas."),
    ],
    ops=[
        FreePoint(name="S", op="free_point", rough_xy=(0.0, -2.0),
                  draw=Draw(local_color=_lc("radius", "#1E6FE0"), step=2, is_heart=True,
                            label=Label(tex="$S$", placement="S"))),
        FreePoint(name="A", op="free_point", rough_xy=(-3.0, 2.0),
                  draw=Draw(local_color=_lc("path", "#E8A200"), step=1, is_heart=True,
                            label=Label(tex="$A$", placement="NW"))),
        FreePoint(name="B", op="free_point", rough_xy=(0.0, 2.6),
                  draw=Draw(local_color=_lc("path", "#E8A200"), step=1, is_heart=False,
                            label=Label(tex="$B$", placement="N"))),
        FreePoint(name="C", op="free_point", rough_xy=(3.0, 2.0),
                  draw=Draw(local_color=_lc("path", "#E8A200"), step=1, is_heart=False,
                            label=Label(tex="$C$", placement="NE"))),
        Segment(name="AB", op="segment", a="A", b="B",
                draw=Draw(local_color=_lc("path", "#E8A200"), step=1, is_heart=False)),
        Segment(name="BC", op="segment", a="B", b="C",
                draw=Draw(local_color=_lc("path", "#E8A200"), step=1, is_heart=False)),
        Segment(name="SA", op="segment", a="S", b="A",
                draw=Draw(local_color=_lc("radius", "#1E6FE0"), step=2, is_heart=False)),
        Segment(name="SB", op="segment", a="S", b="B",
                draw=Draw(local_color=_lc("radius", "#1E6FE0"), step=2, is_heart=False)),
        Segment(name="SC", op="segment", a="S", b="C",
                draw=Draw(local_color=_lc("radius", "#1E6FE0"), step=2, is_heart=False)),
        LineOp(name="lineAB", op="line", a="A", b="B"),
        Parallel(name="parC", op="parallel", through="C", to="SB"),
        Intersect(name="c", op="intersect", a="parC", b="lineAB", near=(-1.5, 2.3),
                  draw=Draw(local_color=_lc("construction", "#D81B60"), step=3, is_heart=True,
                            label=Label(tex="$c$", placement="NW"))),
        Segment(name="Cc", op="segment", a="C", b="c",
                draw=Draw(local_color=_lc("construction", "#D81B60"), step=3, is_heart=False)),
        Segment(name="Sc", op="segment", a="S", b="c",
                draw=Draw(local_color=_lc("construction", "#D81B60"), step=3, is_heart=False)),
    ],
)

VERBATIM_PALETTE = Palette(
    schema_version="1.0", pack_id="principia",
    groups={
        "path": GroupColor(hi="#FFE08A", ink="#E8A200"),
        "radius": GroupColor(hi="#A8D8FF", ink="#1E6FE0"),
        "construction": GroupColor(hi="#FFB3C7", ink="#D81B60"),
    },
    grey_ink="#7A7A7A", grey_text="#8A8A8A", bg_key="#FF00FF",
    map_importance={"1": "#111111", "2": "#222222", "3": "#333333", "4": "#444444", "5": "#555555"},
    map_node_default="#666666",
)


def test_golden_valid():
    from bake.recipe_validate import validate_recipe
    violations = validate_recipe(VERBATIM_RECIPE, VERBATIM_PALETTE)
    assert violations == []


def test_forward_ref():
    from bake.recipe_validate import validate_recipe
    r = Recipe(schema_version="1.0", figure_id="t.f1", node_id="t", edition="", caption="", n_steps=1,
               steps=[StepGloss(index=1, gloss="")],
               ops=[
                   Segment(name="AB", op="segment", a="A", b="B",
                           draw=Draw(local_color=_lc("r"), step=1, is_heart=True)),
                   FreePoint(name="A", op="free_point",
                             draw=Draw(local_color=_lc("r"), step=1, is_heart=False, label=Label(tex="A"))),
                   FreePoint(name="B", op="free_point",
                             draw=Draw(local_color=_lc("r"), step=1, is_heart=False, label=Label(tex="B"))),
               ])
    v = validate_recipe(r, VERBATIM_PALETTE)
    assert any("FORWARD_REF" in x for x in v)


def test_empty_step():
    from bake.recipe_validate import validate_recipe
    r = Recipe(schema_version="1.0", figure_id="t.f1", node_id="t", edition="", caption="", n_steps=2,
               steps=[StepGloss(index=1, gloss=""), StepGloss(index=2, gloss="")],
               ops=[
                   FreePoint(name="A", op="free_point",
                             draw=Draw(local_color=_lc("r"), step=1, is_heart=True, label=Label(tex="A"))),
               ])
    v = validate_recipe(r, VERBATIM_PALETTE)
    assert any("EMPTY_STEP" in x and "2" in x for x in v)


def test_missing_heart():
    """Every step must have at least one element with is_heart=True."""
    from bake.recipe_validate import validate_recipe
    r = Recipe(schema_version="1.0", figure_id="t.f1", node_id="t", edition="", caption="", n_steps=1,
               steps=[StepGloss(index=1, gloss="")],
               ops=[FreePoint(name="A", op="free_point",
                              draw=Draw(local_color=_lc("r"), step=1, is_heart=False, label=Label(tex="A")))])
    v = validate_recipe(r, VERBATIM_PALETTE)
    assert any("MISSING_HEART" in x for x in v)


def test_type_mismatch():
    from bake.recipe_validate import validate_recipe
    r = Recipe(schema_version="1.0", figure_id="t.f1", node_id="t", edition="", caption="", n_steps=1,
               steps=[StepGloss(index=1, gloss="")],
               ops=[
                   FreePoint(name="A", op="free_point",
                             draw=Draw(local_color=_lc("r"), step=1, is_heart=True, label=Label(tex="A"))),
                   FreePoint(name="P", op="free_point",
                             draw=Draw(local_color=_lc("r"), step=1, is_heart=False, label=Label(tex="P"))),
                   Parallel(name="par", op="parallel", through="P", to="A"),
               ])
    v = validate_recipe(r, VERBATIM_PALETTE)
    assert any("TYPE_MISMATCH" in x for x in v)


def test_unknown_ref():
    from bake.recipe_validate import validate_recipe
    r = Recipe(schema_version="1.0", figure_id="t.f1", node_id="t", edition="", caption="", n_steps=1,
               steps=[StepGloss(index=1, gloss="")],
               ops=[
                   Segment(name="S", op="segment", a="A", b="B",
                           draw=Draw(local_color=_lc("r"), step=1, is_heart=True)),
               ])
    v = validate_recipe(r, VERBATIM_PALETTE)
    assert any("UNKNOWN_REF" in x for x in v)
