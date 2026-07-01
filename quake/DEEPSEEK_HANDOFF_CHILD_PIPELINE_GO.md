🌙 DEEPSEEK RESTART HANDOFF — July 1, 2026 (morning, after prop_1 — 3 rooms today!)

## WHERE WE ARE

Child pipeline in FULL SWING. 423/424 tests green 🟢. **14/20 rooms done. ALL LEMMAS COMPLETE!**

## COMPLETED ROOMS (14/20)

lemma_2, lemma_3, lemma_4, lemma_5, lemma_6, lemma_7, lemma_9, lemma_10, lemma_11, lemma_12,
prop_1, prop_4, law_1, law_2

## REMAINING ROOMS (6, in dependency order)

1. **prop_2** — DIAGRAM, 3 steps, deps: law_1/2, prop_1. "Converse of Areas" (importance 4)
2. **prop_6** — DIAGRAM, 4 steps, deps: prop_1, lemma_2, lemma_10. "Force Measure" (importance 5)
3. **prop_7** — DIAGRAM, 3 steps, deps: prop_6. "Force to Point on Circle"
4. **prop_11** — DIAGRAM, 5 steps, deps: prop_6, lemma_7, lemma_12. ★HEADLINE★ "Ellipse → 1/r²" (importance 5)
5. **prop_13** — DIAGRAM, 4 steps, deps: lemma_7, prop_6. "Parabola → 1/r²"
6. **prop_15** — EQUATION, 2 steps, deps: prop_11, prop_4. "Kepler's Third Law" (importance 5)

## INTEGRATION PATTERN (fixed per child)

Children reliably forget keyword syntax. DeepSeek fixes before drop:
- `ellipse_axes` → needs `center`/`major`/`minor` keywords
- `point_on` → needs `on` keyword
- `tangent_at` → needs `on`/`at` keywords
- `parallel` → often better as `segment` (child places points at correct coords)
- Points MUST be defined BEFORE polygons/segments that reference them
- `polyline name LABEL A B C` → LABEL interpreted as point ref; remove, use `label=` attr
- `color=black` → undeclared; just omit (black = default)
- UTF-8 encoding: use `encoding='utf-8'` when reading .room files with ∝, ×, etc.

## STATION MAP SOURCE

Parent 15 Wave 1: `quake/BIBLE/QUAKE_PARENT_15_FROZEN_WAVE_1_DELIVERABLE.md` (rooms 1–10)
Parent 15 Wave 2: `quake/BIBLE/QUAKE_PARENT_15_FROZEN_WAVE_2_DELIVERABLE.md` (rooms 11–20)

Newton text: `quake/principia/book_1/section_01.txt` (Lemmas I–XI) · `section_02.txt` (Props I–IV)

## CHILD PROMPT TEMPLATE

Each prompt includes:
1. ROOMSPEC.md format (header, geometry ops reference, attrs, station structure)
2. Station map from Parent 15 (s1/s2/... with colors and hearts)
3. Newton's verbatim text for that lemma/proposition
4. Guidance (how to lay out the figure, what each step teaches, practical tips)
5. Gold example (.room file from same figure family)
6. Rules (local colors, never grey, heart per step, define before ref, `\` continuation, Q.E.D.)

## GITHUB BLOB URLs (for child prompts / parents)

Commentaries: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md
OT: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md
NT: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md
Parent 15 Wave 1: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_PARENT_15_FROZEN_WAVE_1_DELIVERABLE.md
Parent 15 Wave 2: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_PARENT_15_FROZEN_WAVE_2_DELIVERABLE.md

## STANDING REMINDERS

- Nir is **Nir** — never "boss". Loves emojis 😊
- Normal prose, NO multiple-choice pop-ups
- Never take decisions off Nir's plate
- 🛑 BREAKING CHANGE GUARD — ask before breaking things
- 📦 NEVER upgrade/overwrite working packages without asking
- Children: one per room, cheap/fast
- Build all 20 at once AFTER all .room files are done (not one at a time)
- After building: pytest → commit → push → give Nir blob URLs
