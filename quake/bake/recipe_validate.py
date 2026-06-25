"""Validate a Recipe JSON against the Palette.

Pure, deterministic, no IO. Returns plain-English violation strings
(empty list = valid).
"""

from __future__ import annotations

from typing import get_args, get_origin, get_type_hints, Union

from map.raw_models import (
    Recipe,
    Palette,
    StepGloss,
    GroupName,
    FreePoint,
    PointOn,
    Intersect,
    Midpoint,
    Foot,
    ReflectPoint,
    LineOp,
    Segment,
    RayOp,
    Parallel,
    Perpendicular,
    TangentAt,
    TangentFrom,
    Bisector,
    CircleCP,
    CircleCR,
    Circle3,
    Arc,
    EllipseFoci,
    EllipseAxes,
    ParabolaFD,
    HyperbolaFoci,
    Conic5,
    Polygon,
    Polyline,
    Series,
    AngleMark,
    FloatLabel,
)


# ----------------------------------------------------------------------
# Op category sets (by the op discriminator value).
# ----------------------------------------------------------------------

POINT_OPS = {
    "free_point",
    "point_on",
    "intersect",
    "midpoint",
    "foot",
    "reflect_point",
}

LINE_OPS = {
    "line",
    "parallel",
    "perpendicular",
    "tangent_at",
    "tangent_from",
    "bisector",
    "ray",
}

CURVE_OPS = {
    "circle_cp",
    "circle_cr",
    "circle3",
    "arc",
    "ellipse_foci",
    "ellipse_axes",
    "parabola_fd",
    "hyperbola_foci",
    "conic5",
    "segment",
    "line",
    "parallel",
    "perpendicular",
    "ray",
    "polygon",
    "polyline",
}

CATEGORY_SETS = {
    "point": POINT_OPS,
    "line": LINE_OPS,
    "curve": CURVE_OPS,
}


# ----------------------------------------------------------------------
# ARG -> EXPECTED CATEGORY mapping (frozen).
# Keyed by op discriminator value, then by field name.
# ----------------------------------------------------------------------

ARG_CATEGORY: dict[str, dict[str, str]] = {
    "free_point": {},
    "point_on": {"path": "curve"},
    "intersect": {"a": "curve", "b": "curve"},
    "midpoint": {"a": "point", "b": "point"},
    "foot": {"point": "point", "line": "curve"},
    "reflect_point": {"point": "point", "over": "curve"},
    "line": {"a": "point", "b": "point"},
    "segment": {"a": "point", "b": "point"},
    "ray": {"a": "point", "b": "point"},
    "parallel": {"through": "point", "to": "curve"},
    "perpendicular": {"through": "point", "to": "curve"},
    "tangent_at": {"curve": "curve", "at": "point"},
    "tangent_from": {"curve": "curve", "frm": "point"},
    "bisector": {"a": "point", "vertex": "point", "b": "point"},
    "circle_cp": {"center": "point", "through": "point"},
    "circle_cr": {"center": "point", "radius_points": "point"},
    "circle3": {"a": "point", "b": "point", "c": "point"},
    "arc": {"center": "point", "frm": "point", "to": "point"},
    "ellipse_foci": {"f1": "point", "f2": "point", "through": "point"},
    "ellipse_axes": {"center": "point", "major_end": "point", "minor_end": "point"},
    "parabola_fd": {"focus": "point", "directrix": "curve"},
    "hyperbola_foci": {"f1": "point", "f2": "point", "through": "point"},
    "conic5": {"p1": "point", "p2": "point", "p3": "point", "p4": "point", "p5": "point"},
    "polygon": {"points": "point"},
    "polyline": {"points": "point"},
    "series": {"along": "curve", "to_curve": "curve"},
    "angle_mark": {"a": "point", "vertex": "point", "b": "point"},
    "float_label": {"at": "point"},
}


# Fields that are coordinate hints only — never checked.
IGNORED_FIELDS = {"rough_xy", "near", "offset", "t"}


def _iter_refs(op, arg_name: str):
    """Yield each ref string stored in op.<arg_name>.

    Handles scalar refs, list[ref], tuple[ref, ...], optional refs.
    Non-string / None entries are skipped.
    """
    if not hasattr(op, arg_name):
        return
    value = getattr(op, arg_name)
    if value is None:
        return
    if isinstance(value, str):
        yield value
    elif isinstance(value, (list, tuple)):
        for item in value:
            if isinstance(item, str):
                yield item


def validate_recipe(recipe: Recipe, palette: Palette) -> list[str]:
    """Return plain-English violation strings. Empty list = valid."""
    violations: list[str] = []

    n_steps = recipe.n_steps

    # ---- 1. FIGURE_ID PREFIX -----------------------------------------
    prefix = recipe.node_id + ".f"
    if not recipe.figure_id.startswith(prefix):
        violations.append(
            f"FIGURE_ID_MISMATCH: {recipe.figure_id} does not start with "
            f"{recipe.node_id}.f"
        )

    # ---- 2. STEPS CHECK ----------------------------------------------
    if len(recipe.steps) != n_steps:
        violations.append(
            f"STEP_COUNT_MISMATCH: steps has {len(recipe.steps)} entries "
            f"but n_steps={n_steps}"
        )
    sorted_indices = sorted(s.index for s in recipe.steps)
    if sorted_indices != list(range(1, n_steps + 1)):
        violations.append(
            f"STEP_INDEX_MISMATCH: expected indices 1..{n_steps}, "
            f"got {sorted_indices}"
        )

    # ---- 3. OP NAMES UNIQUE ------------------------------------------
    seen_names: set[str] = set()
    reported_dups: set[str] = set()
    for op in recipe.ops:
        if op.name in seen_names:
            if op.name not in reported_dups:
                violations.append(
                    f"DUPLICATE_OP_NAME: '{op.name}' appears more than once"
                )
                reported_dups.add(op.name)
        else:
            seen_names.add(op.name)

    # Index map: name -> first occurrence position; and name -> op.
    name_to_index: dict[str, int] = {}
    name_to_op: dict[str, object] = {}
    for i, op in enumerate(recipe.ops):
        if op.name not in name_to_index:
            name_to_index[op.name] = i
            name_to_op[op.name] = op

    # ---- 4/5/6. REFS: forward, existence, type ----------------------
    for i, op in enumerate(recipe.ops):
        op_kind = op.op
        arg_map = ARG_CATEGORY.get(op_kind, {})

        for arg_name in arg_map:
            if arg_name in IGNORED_FIELDS:
                continue
            for ref in _iter_refs(op, arg_name):
                # 5. existence
                if ref not in name_to_index:
                    violations.append(
                        f"UNKNOWN_REF: '{op.name}' references '{ref}' "
                        f"which is never defined"
                    )
                    continue
                # 4. forward ref forbidden
                if name_to_index[ref] >= i:
                    violations.append(
                        f"FORWARD_REF: '{op.name}' references '{ref}' "
                        f"which is defined later"
                    )
                    continue
                # 6. type compatibility
                ref_op = name_to_op[ref]
                expected_category = arg_map[arg_name]

                # series.along special rule
                if op_kind == "series" and arg_name == "along":
                    if ref_op.op not in ("segment", "arc"):
                        violations.append(
                            f"SERIES_ALONG_TYPE: '{op.name}.along' references "
                            f"'{ref}' ({ref_op.op}) but must be segment or arc"
                        )
                    continue

                allowed = CATEGORY_SETS[expected_category]
                if ref_op.op not in allowed:
                    violations.append(
                        f"TYPE_MISMATCH: '{op.name}.{arg_name}' references "
                        f"'{ref}' ({ref_op.op}) but needs a {expected_category}"
                    )

    # ---- 7. DRAWN OP STEP IN RANGE -----------------------------------
    for op in recipe.ops:
        draw = getattr(op, "draw", None)
        if draw is not None:
            if not (1 <= draw.step <= n_steps):
                violations.append(
                    f"STEP_OUT_OF_RANGE: '{op.name}' draw.step={draw.step} "
                    f"not in 1..{n_steps}"
                )

    # ---- 8. EVERY STEP HAS >=1 DRAWN OP ------------------------------
    drawn_steps: set[int] = set()
    for op in recipe.ops:
        draw = getattr(op, "draw", None)
        if draw is not None:
            drawn_steps.add(draw.step)
    for k in range(1, n_steps + 1):
        if k not in drawn_steps:
            violations.append(
                f"EMPTY_STEP: step {k} has no drawn element "
                f"(on_{k} would equal off)"
            )

    # ---- 9. CIRCLE_CR EXCLUSIVITY ------------------------------------
    for op in recipe.ops:
        if op.op == "circle_cr":
            has_points = getattr(op, "radius_points", None) is not None
            has_value = getattr(op, "radius_value", None) is not None
            if has_points == has_value:
                violations.append(
                    f"CIRCLECR_ARGS: '{op.name}' must have exactly one of "
                    f"radius_points/radius_value"
                )

    # ---- 10. FLOATLABEL HAS LABEL ------------------------------------
    for op in recipe.ops:
        if op.op == "float_label":
            draw = getattr(op, "draw", None)
            if draw is None or getattr(draw, "label", None) is None:
                violations.append(
                    f"FLOATLABEL_NO_LABEL: '{op.name}' has no label"
                )

    # ---- 11. EVERY DRAW.GROUP IN PALETTE -----------------------------
    for op in recipe.ops:
        draw = getattr(op, "draw", None)
        if draw is not None:
            if draw.group not in palette.groups:
                violations.append(
                    f"UNKNOWN_GROUP: '{op.name}' group='{draw.group}' "
                    f"not in palette"
                )

    # ---- 12. MARKER CHECK --------------------------------------------
    for op in recipe.ops:
        draw = getattr(op, "draw", None)
        if draw is not None:
            marker = getattr(draw, "marker", None)
            if marker is not None and marker not in ("none", "dot"):
                violations.append(
                    f"BAD_MARKER: '{op.name}' marker='{marker}' "
                    f"must be none or dot"
                )

    return violations
