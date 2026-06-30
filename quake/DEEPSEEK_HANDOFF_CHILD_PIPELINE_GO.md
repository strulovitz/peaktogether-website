🌙 DEEPSEEK RESTART HANDOFF — June 30, 2026 (late evening)

## WHERE WE ARE

Parent 16 COMPLETE — delivered COMPLETE RUNNABLE `build/room_from_spec.py` (parser +
validator + emit_recipe + emit_asy + emit_room_source + shell). 402/402 tests green
(385 old + 17 new room_from_spec tests).

The CHILD PIPELINE WORKS: child writes .room → tool validates → emits recipe.json +
figure.asy + room_source.json → full bake pipeline → playable room in room_viewer.

## WHAT WE DID TODAY (this session)

1. **Parent 16 launched + delivered v2 (COMPLETE CODE).**
   - v1 had an "honest gap" (Asymptote snippet library deferred to DeepSeek). Nir
     rightfully rejected this — if DeepSeek codes it, why pay Opus?
   - DeepSeek fetched complete Asymptote docs from internet, pasted to parent.
   - Parent delivered FULL runnable Python — all 28 RecipeOps mapped, 0 gaps, 0 TODOs.
   - Frozen deliverable at `QUAKE_PARENT_16_FROZEN_DELIVERABLE.md`.

2. **DeepSeek dropped code into repo + tests.**
   - `build/room_from_spec.py` — 1,280-line tool
   - `tests/test_room_from_spec.py` — 17 tests (anchor round-trips + rejection battery)
   - `tests/room_specs/` — 4 .room fixture files (lemma_2, prop_4, law_1, law_2)
   - Two bugs found + fixed at integration:
     a) `#` comment stripping ate hex colors (`#1E6FE0` → `#` was comment) — fixed
        with hex-aware comment detection
     b) Cross-station geometry references rejected — fixed to accumulate `defined`
        across stations

3. **layout rendering fix** — emit_asy now uses `layout` keyword from .room files.
   When present, renders the layout as a single properly-formatted equation label
   instead of scattered individual term labels. Uses `_layout_to_plain()` to strip
   `{name|text}` spans to plain LaTeX.

4. **First child test: law_2 room END-TO-END.**
   - Child wrote law_2.room (2-step equation room, 3 colors)
   - Tool parsed + validated + emitted all 3 output files
   - Figure baking: switched from Asymptote to pdflatex+pdftocairo for equation rooms
     (same crisp pipeline as text panels, no Asymptote for text rendering)
   - Build script at `%TEMP%\opencode\build_law2.py` reworked 3 times — final version
     uses pdftocairo for everything, transparent background
   - Room plays in room_viewer ✅

## CURRENT STATE

- 402/402 tests green 🟢
- 4 .room files done: lemma_2, prop_4, law_1, law_2
- Build pipeline for law_2: `python %TEMP%\opencode\build_law2.py`
- View: `python -m tools.room_viewer law_2 "%TEMP%\opencode\law2_room\pack"`
- 16 more rooms to go

## KNOWN BUGS FIXED IN room_from_spec.py (don't re-introduce)

1. `_strip_comment` — `#` followed by 6 hex digits is a color, not a comment.
2. `_refs_of` check in `validate` — accumulated across ALL stations, not per-station.
3. `_emit_label_layout` — `row_gap = 3.5` (increased from 2.2 for better spacing).
4. Equation rooms with `layout` get a single label rendered (via `_layoutpos_` pair),
   not individual term labels. Stabilo is a filled `box()` rectangle behind text.
5. Recipe `at` field for term ops uses `termpos_` prefix (must start with letter
   for OpName pattern `^[A-Za-z]`).

## TOOL ARCHITECTURE (room_from_spec.py)

```
parse(spec_text) → Spec            # line-oriented keyword parser
validate(Spec) → None              # cross-checks, SpecError on violation
emit_recipe(Spec) → Recipe|None    # None for pure-text rooms
emit_asy(Spec) → str               # self-contained gold .asy convention
emit_room_source(Spec) → RoomSource # scans \textcolor for colors_used
build_room(text, out, write) → BuildResult  # shell: writes 3 files
```

The .rooom format has three kinds:
- `geometry` — construction ops (point, segment, circle, ellipse, series, ...)
- `equation` — `term` ops + optional `layout`
- `text` — `phrase` ops

All three are FigureDecls via .asy (Decision A.1). Equation/text rooms emit
label-only .asy with auto-positioned layout labels.

## BUILD PIPELINE (the law_2 build script pattern)

For equation rooms, the figure panel IS text → use pdflatex+pdftocairo (NOT Asymptote):
```
layout → strip {name|text} → wrap in \textcolor{name}{text} → pdflatex → pdftocairo -transp → PNG
```
The text panels use `baker_text.py` (same pdflatex+pdftocairo pipeline).
Ceiling equations: red text on transparent bg via pdflatex+pdftocairo + key_out_white.

## NEXT: 16 MORE CHILDREN

The child pipeline is proven. On restart, DeepSeek writes child prompts one-by-one
for the remaining rooms, following dependency order. Each child gets:
1. ROOMSPEC.md (the format)
2. That room's station map (from Parent 15 wave deliverables)
3. The Newton source text for that room
4. Instructions

Child returns .room file → DeepSeek drops in tests/room_specs/ → validates with
build_room → adds test → pushes. DO NOT rebuild full pack for every child (too slow).
Build all 20 rooms at once after all .room files are done.

Remaining rooms by dependency order (foundations first, then up the graph):
1. lemma_5 (diagram, 2 steps, no deps)
2. lemma_6 (diagram, 3 steps, no deps)
3. lemma_12 (diagram, 1 step, no deps — simplest diagram room!)
4. lemma_3 (diagram, 2 steps, depends on lemma_2 ✅)
5. lemma_4 (diagram, 3 steps, depends on lemma_3)
6. lemma_7 (diagram, 3 steps, depends on lemma_6)
7. lemma_9 (diagram, 3 steps, depends on lemma_5)
8. lemma_10 (diagram, 2 steps, depends on lemma_9)
9. lemma_11 (diagram, 3 steps, depends on lemma_6/7)
10. prop_1 (diagram, 4 steps, depends on law_1/2 ✅, lemma_5)
11. prop_2 (diagram, 3 steps, depends on law_1/2 ✅, prop_1)
12. prop_6 (diagram, 4 steps, depends on prop_1, lemma_2 ✅, lemma_10)
13. prop_7 (diagram, 3 steps, depends on prop_6)
14. prop_11 (diagram, 5 steps, depends on prop_6, lemma_7, lemma_12)
15. prop_13 (diagram, 4 steps, depends on lemma_7, prop_6)
16. prop_15 (equation, 2 steps, depends on prop_11, prop_4 ✅)

Already done: lemma_2, prop_4, law_1, law_2 ✅

## GITHUB URLs (for child prompts, if needed)

The commentaires + scriptures:
https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md
https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md
https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md

Parent 15 station map:
https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_PARENT_15_FROZEN_WAVE_1_DELIVERABLE.md
https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_PARENT_15_FROZEN_WAVE_2_DELIVERABLE.md

Principia text:
https://github.com/strulovitz/peaktogether-website/blob/master/quake/principia/

## STANDING REMINDERS

- Nir is the BOSS; ask before taking initiative
- Normal prose, NO multiple-choice pop-ups
- Keep the emojis even when upset
- Never take decisions off Nir's plate
- Check for residue by MEANING, not by label
- 📦 NEVER upgrade/overwrite working packages
- 🛑 BREAKING CHANGE GUARD — ask before breaking things
- Children: one per room, cheap/fast, zero context needed
- After building: run pytest, commit+push, give Nir blob URLs
