# 🌙 DEEPSEEK NIGHT HANDOFF — June 25, 2026 (near midnight Israel time)

> **WAKE-UP PROTOCOL:** On restart, the WORKFLOW will point here. Read this FIRST, then ask Nir what's next. You are DeepSeek V4 Pro in OpenCode on Nir's Windows desktop. You are the Runner/Integrator. Nir is the Boss.

---

## WHERE WE ARE RIGHT NOW (crystal clear)

**Both legs are frozen by Parent 2. We are building Leg 2 children — exactly like we built Leg 1 children.**

### Leg 1 (MAP) — COMPLETE ✅
All 9 modules built, integrated, tested. **94/94 green.**

### Leg 2 (WALLS) — COMPLETE ✅🎉
**ALL 8 modules built. 145/145 total tests green.**

| # | Module | File | Tests | Status |
|---|--------|------|-------|--------|
| C1 | palette_gen | `bake/palette_gen.py` | 4 | ✅ Done |
| C2 | recipe_validate | `bake/recipe_validate.py` | 6 | ✅ Done |
| C3 | prooffig_check | `bake/prooffig_check.py` | 6 | ✅ Done |
| C4 | asy_compile | `bake/asy_compile.py` | 4 | ✅ Done |
| C5 | _imageops | `bake/_imageops.py` | 11 | ✅ Done |
| C6 | baker_figure | `bake/baker_figure.py` | 5 | ✅ Done |
| C7 | baker_text | `bake/baker_text.py` | 6 | ✅ Done |
| C8 | overlay_diff | `tools/overlay_diff.py` | 9 | ✅ Done |

**LEG 2 IS COMPLETE!** 🎉🎉🎉 Both legs done. Parent 2 can receive the build report.

### parent 2 is waiting
Parent 2 is holding for a build report. He finished both frozen packages. He flagged one §E item (figure_id vs block_id for asset keys) — not blocking, DeedSeek must confirm at integration time.

---

## THE LEG 2 FROZEN BRIEFS (Parent 2's document)

File: `quake/BIBLE/QUAKE_LEG_2_WALLS_FROZEN_BY_OPUS_PARENT_2.md`

This is the authoritative spec for all 7 Leg 2 children. **DeepSeek's job:** for each child, craft a self-contained prompt (with all needed pydantic models verbatim), send it to a fresh OpenRouter Opus chat (the "child"), receive the code, save it, run tests, fix any issues, commit, push, then move to next child.

### MODELS ALREADY ADDED to raw_models.py:
DeepSeek already extended `map/raw_models.py` with Leg-2 models:
- GroupName, GroupColor, Palette (for C1)
- All Recipe op types: FreePoint, PointOn, Intersect, Midpoint, Foot, ReflectPoint, LineOp, Segment, RayOp, Parallel, Perpendicular, TangentAt, TangentFrom, Bisector, CircleCP, CircleCR, Circle3, Arc, EllipseFoci, EllipseAxes, ParabolaFD, HyperbolaFoci, Conic5, Polygon, Polyline, Series, AngleMark, FloatLabel, RecipeOp, StepGloss, Recipe, Draw, Label (for C2)
- TextBlock (for C7, already added)
- Vec3, FigureId, PairId, DrawBlockId, TextBlockId, EqId, OpName, Ref aliases

### MODELS STILL NEEDED (to add before relevant children):
- AsyResult, AsyConfig (for C4 — can be defined in asy_compile.py itself)
- AssetEntry, Manifest (for C5, C6, C7 — from Second Canon §4.6)
- BakerFigureConfig, BakerTextConfig (for C5, C6 — from parent's briefs)

---

## THE BUILD PROCESS (exactly how we do it)

1. Nir asks me to prep the prompt for next child
2. I craft a self-contained prompt with all needed types verbatim
3. Nir pastes it to a fresh OpenRouter Opus chat
4. The child returns code (module + test file)
5. I save both files, run `python -m pytest tests/ -q` from `quake/`
6. If tests fail, I diagnose and fix (usually small things: indentation, regex edge cases, type mismatches)
7. When all tests pass, I `git add -A; git commit -m "..." ; git push`
8. I report the new test count to Nir, then prep the next prompt

### COMMON FIXES I'VE HAD TO MAKE:
- **Indentation bugs**: children sometimes mis-indent code blocks. Check the for-loop body is properly indented (this bit C3).
- **Regex edge cases**: the child's regex for lbl() calls broke on `(0,0)` (commas in tuple). Fixed by using `[^"]*?` for at-arg.
- **Category mismatches**: `parallel.to` referencing a `segment` was flagged as TYPE_MISMATCH because segments weren't in CURVE_OPS. Added `parallel` and `perpendicular` to CURVE_OPS.
- **Unicode in test fixtures**: box-drawing characters `─` (U+2500) can't write via cp1252 on Windows. Replaced with ASCII `-`.
- **Hex validation**: `#111` is too short for Hex pattern (`^#[0-9a-fA-F]{6}$`). Use `#111111`.
- **Layer overflow**: `max_layer > layer_fail` with 0-indexed layers needed `>=` instead of `>`.

---

## FILE STRUCTURE

```
quake/
  map/                          ← Leg 1 modules
    __init__.py
    raw_models.py               ← ALL pydantic types (Leg 1 + Leg 2)
    page_map_adapter.py
    citation_normalize.py
    citation_extract.py
    merge.py
    sanity.py
    layout_force.py
    layout_height.py
    level_maker.py
  bake/                         ← Leg 2 modules
    __init__.py
    palette_gen.py              ✅ C1
    recipe_validate.py          ✅ C2
    prooffig_check.py           ✅ C3
  tests/
    test_raw_models.py
    test_page_map_adapter.py
    test_citation_normalize.py
    test_citation_extract.py
    test_merge.py
    test_sanity.py
    test_layout_force.py
    test_layout_height.py
    test_level_maker.py
    test_palette_gen.py         ✅
    test_recipe_validate.py     ✅
    test_prooffig_check.py      ✅
  BIBLE/
    QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md   ← THE MAP
    QUAKE_LEG_1_MAP_FROZEN_CHILD_BRIEFS_BY_OPUS_PARENT_2.md
    QUAKE_LEG_2_WALLS_FROZEN_BY_OPUS_PARENT_2.md  ← AUTHORITY
    ... (other scriptures)
  WORKFLOW.md                   ← points here on restart
```

---

## PARENT 2'S C4 BRIEF (verbatim, for prompt crafting)

Frozen signature:
```python
def compile(src: Path, out_stem: Path, params: dict[str, str], cfg: "AsyConfig") -> AsyResult
```

AsyResult: ok: bool, outputs: list[Path], stderr: str, stdout: str
AsyConfig: asy_binary: str = "asy", out_format: str = "png", dpi: int = 220, extra_flags: list[str] = []

Behavior: invoke asy binary with -u "k=v" flags (params sorted by key), format/DPI flags, src, out_stem. Capture stdout+stderr verbatim. Never raise on error — return ok=False with text. ok=True only on zero exit AND output file(s) present.

Tests: monkeypatch subprocess. Assert params appear as -u "k=v" tokens in sorted-key order. Non-zero exit → ok=False with stderr preserved. Zero exit + output file → ok=True. Zero exit but no output file → ok=False.

---

## NEXT ACTION ON WAKE:
Ask Nir: "Ready to continue Leg 2? Next is Child 4: `asy_compile.py`. Want the prompt?" 😊
