# 🌅 DEEPSEEK RESTART — Parent 13 Launch / June 29, 2026

> Read AFTER WORKFLOW.md + the Commentaries. Then ask Nir what's next.

---

## WHERE WE ARE (June 29, 2026)

### The Quake game — what's built
- **Leg 1 (MAP):** 9 modules, 94 tests ✅
- **Leg 2 (WALLS):** 8 modules, 51 tests ✅
- **Leg 3 (ROOMS):** 5 modules, 41 tests ✅
- **Leg 4 (ENGINE):** 13 modules + app.py, 106 tests ✅
- **Layout hardening (Parent 8 Part A):** 50 new scale tests ✅
- **Hierarchical layout:** implemented, 5 crossings on 20-node graph ✅
- **Parent 11 renderers:** Mode A wireframe + bloom, lit Mode B, all integrated ✅
- **Total: 382/382 tests green** 🟢

### What's in the level already
- `levels/principia_bk1_inverse_square/concept_graph.json` — 20 nodes, 28 edges (Parent 7, FROZEN)
- `levels/principia_bk1_inverse_square/palette.json` — 5 color groups (Parent 7, FROZEN)
- `levels/principia_bk1_inverse_square/floorplan.json` — node positions, 5 crossings, 3 height layers (regenerated with hierarchical layout)
- Principia Book 1 text in `quake/principia/` (14 sections, all 1729 Motte from Wikisource)
- DIGESTED PRINCIPIA in `quake/principia/DIGESTED_PRINCIPIA.md` (343-line summary)

### Tools available
- `tools/map_viewer.py` — fly the 3D wireframe corridor map (Mode A)
- `tools/room_viewer.py` — fly inside one room (Mode B)
- `tools/_render_probe.py` — offscreen render-to-PNG (Mode B, boilerplate for future probes)

### Parent history
```
Parent 1:    DIED (context cliff)
Parent 2:    ✅ Legs 1+2 frozen child briefs
Parent 3:    ✅ Leg 3 / Room Maker v3
Parent 4:    ✅ Leg 4 engine briefs (13 modules)
Parent 5:    ✅ Golden Fixture Pack (38 PNGs + 6 JSONs)
Parent 6:    ✅ app.py wiring
Parent 7:    ✅ Frozen level design (20-node graph + palette + figure plan)
Parent 8:    ✅ Part A (engine hardening)
Parent 9:    ❌ CANCELLED (poisoned by DeepSeek's lemma_1 constraint)
Parent 10:   ❌ DIED (context overload — 2 missions + stale bug report + ~2000-line dump)
Parent 11:   ✅ Renderers (Mode A wireframe + bloom, lit Mode B)
Parent 12:   ❌ FAILED (polygon rooms — DeepSeek can't iterate on visual quality)
```

### The polygon room disaster (lesson burned in)
Regular-polygon rooms were designed, prototyped, rendered. Failed because DeepSeek cannot see images and thus cannot iterate on visual quality. Nir judged the output unusable. Box rooms (Wolfenstein-grade) remain the standard. Polygons archived for future image-capable AI. Key lesson: DeepSeek never does visual refinement. All visual work requires Nir as sole visual judge with rapid PNG turnaround.

### The 20-room content challenge
Parent 10 died trying to design all 42 content files in one chat. The new approach (Nir's direction, based on the successful Descent QED pattern):

1. **Parent 13 (NOW):** Build ONE room (lemma_2, the simplest figure) as a pipeline proof-of-concept. Proves: LaTeX panels render, Asymptote compiles with Stabilo highlighting, `\cg` color spans match figure elements, the full build pipeline works.
2. **Parent 14 (AFTER Parent 13 succeeds):** Design a text format for room specs + a Python tool (`build/room_from_spec.py`) that converts specs → recipe.json + figure.asy + room_source.json. One tool, run 20+ times.
3. **20 children (AFTER Parent 14):** One child per room fills in the format. DeepSeek runs the tool on each. No context death.

---

## PARENT 13 — LAUNCH PROTOCOL

### The handoff
File: `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_13_HANDOFF.md` (297 lines)

### Launch files (paste these to the fresh Opus chat, in this order):
1. **This Commentaries** — `quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` (the map of the BIBLE)
2. **Old Testament** — `quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md` (~459 lines, the Fusion master doctrine)
3. **Apocrypha** — `quake/BIBLE/QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md` (~180 lines, Room System v3)
4. **The Parent 13 handoff** — `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_13_HANDOFF.md`

Github raw URLs for copy-paste:
```
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_13_HANDOFF.md
```

### After launch — what DeepSeek does:
1. Parent 13 will state his plan, ask 1 batch of questions (what Principia text he needs, what the prooffig API is)
2. DeepSeek fetches the Principia text from `quake/principia/book_1/section_01.txt` (Lemma II text) and the prooffig interface from the codebase
3. Nir pastes answers
4. Parent 13 delivers 3 files: recipe.lemma_2.f1.json, figure.lemma_2.f1.asy, room_source.lemma_2.json
5. DeepSeek validates all 3 against pydantic schemas (raw_models.py)
6. DeepSeek runs the build pipeline: asy_compile → overlay_diff (Nir's eyes) → baker_figure + baker_text → room_maker → render offscreen → PNG for Nir

### Parent 13's chapter of the BIBLE
Parent 13 is the THIRTEENTH parent in the Quake Commentaries. His deliverable should be saved verbatim at:
`quake/BIBLE/QUAKE_PARENT_13_FROZEN_DELIVERABLE.md`

---

## PARENT 14 — DEFERRED (after Parent 13 succeeds)
File: `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_14_HANDOFF.md` (316 lines)
Mission: Design format + build `build/room_from_spec.py` tool. Do NOT launch until Parent 13's one-room proof passes Nir's visual inspection.

---

## KEY RULES (do not violate)
1. **Never freeze the easy option silently.** Surface tradeoffs to Nir.
2. **Render-and-look, don't just compile.** Offscreen render + PNG for Nir.
3. **Question-first material protocol.** Parents ask DeepSeek precise questions → verbatim excerpts. Whole files only for small files being rewritten.
4. **No "GO" on handoffs.** Talk-first rhythm.
5. **One mission per parent.** Don't bundle.
6. **Don't call him "boss"** — just Nir.
7. **Never add a hard constraint Nir didn't approve.**
8. **Never invent external-API names from memory** (Asymptote, etc.).
9. **Tables don't survive copy-paste.** Use fenced code blocks.
10. **382/382 tests must stay green.** Zero regressions.
11. **DeepSeek cannot do visual refinement.** All visual work = Nir's eyes + PNGs.
12. **Opus outputs saved VERBATIM** as "holy" scripture.

---

## IMMEDIATE NEXT STEP (on restart)
Ask Nir: "Launch Parent 13?" 🚀
