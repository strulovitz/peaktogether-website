# 🌅 DEEPSEEK RESTART — Parent 13 Launch / June 29, 2026 (after color correction)

> Read AFTER WORKFLOW.md + the Commentaries. Then ask Nir what's next.

---

## WHAT WE DID TODAY (June 29, 2026)

### Session 1: Memory load + scratch file cleanup
- Read WORKFLOW + Commentaries + restart prompt. All caught up.
- Deleted 8 untracked scratch files (probe PNGs, _data_probe.py, _render_probe.py, savegame.json). Working tree clean.

### Session 2: Nir corrected the color/highlighting system
The old "frozen" model — global 5-group palette, cumulative `on_k` Stabilo, "grey" uncolored ink, `\cg{group}{text}`, same group same color everywhere — was a **misunderstanding** the AIs froze (same disease as the Wolfenstein box-room). Nir caught it and set the record straight.

**Nir's true color system (authoritative, overrides all scriptures):**
- **(1) Matching colors (word ↔ shape):** Per station (=one step-pair), important elements get distinct local colors; the matching words in the text share them. Colors are LOCAL — same concept can be different color or no color elsewhere. Uncolored ink = **black** (light bg) or **white** (dark bg) — **NEVER grey.**
- **(2) Stabilo bright highlighter:** ONLY the current step's heart(s) get a bright marker swipe (bright yellow/green/orange/pink/cyan), never cumulative. Marker colors also local.

### Session 3: Propagated color correction to EVERYWHERE except OT/NT

**Prose/docs corrected:**
- Parent 13 handoff — CORRECTION-FROM-NIR block at top + §3/§4/§6 correction banners
- Parent 14 handoff — CORRECTION-FROM-NIR block at top + §0.5/§2/§5/§6 correction banners
- Commentaries — §3 updated + §4 amendment added + old amendment marked superseded
- Second Canon — top banner noting color model superseded
- WORKFLOW.md — locked decisions + CURRENT SITUATION + restart section updated
- DEEPSEEK_RESTART_PARENT_13_GO.md — this file, rewritten

**Code contracts corrected:**
- `map/raw_models.py` — new `LocalColor` class; `Draw.group` → `Draw.local_color: LocalColor|None + is_heart: bool`; `TextBlock.colors_used: list[LocalColor]`; `FigureDecl.colors_used`; `Palette.groups/grey_ink/grey_text` → optional (backward compat)
- `contracts.py` — `LocalColor` added to re-exports
- `bake/palette_gen.py` — handles optional groups gracefully
- `bake/baker_text.py` — fully rewritten: `\textcolor{name}{text}` instead of `\cg{group}{text}`; OFF = black (000000); validates `\textcolor` spans against `colors_used`
- `bake/recipe_validate.py` — validates `local_color` + `is_heart`; every step needs >=1 heart
- Tests: `test_baker_text.py` rewritten, `test_recipe_validate.py` rewritten, `test_room_maker.py` updated
- `assets.py` — backward-compatible (optional Palette fields), no changes needed

### 382/382 TESTS GREEN 🟢
Runtime formats (RoomRuntime, Floorplan, Manifest) unchanged. Only build-time content formats corrected.

### Critical lesson burned in
"Frozen" exists ONLY to stop the AI assembly-line from drifting — it was **never** meant to bind Nir. Nir is the author; nothing is truly frozen against him. Same mistake as the box-room: AIs froze an easy-wrong option. Nir corrected it. We implemented it. Done.

---

## WHERE WE ARE (June 29, 2026 — end of day)

### What's built
- **Leg 1 (MAP):** 9 modules, 94 tests ✅
- **Leg 2 (WALLS):** 8 modules, 51 tests ✅ (content formats CORRECTED for Nir's color model)
- **Leg 3 (ROOMS):** 5 modules, 41 tests ✅
- **Leg 4 (ENGINE):** 13 modules + app.py, 106 tests ✅
- **Layout hardening (Parent 8 Part A):** 50 new scale tests ✅
- **Hierarchical layout:** implemented, 5 crossings on 20-node graph ✅
- **Parent 11 renderers:** Mode A wireframe + bloom, lit Mode B, all integrated ✅
- **Color system CORRECTED everywhere (Nir's model, June 29)** ✅
- **Total: 382/382 tests green** 🟢

### What's on disk
- `levels/principia_bk1_inverse_square/concept_graph.json` — 20 nodes, 28 edges (Parent 7, FROZEN)
- `levels/principia_bk1_inverse_square/palette.json` — OLD global-palette model (superseded by Nir's correction)
- `levels/principia_bk1_inverse_square/floorplan.json` — node positions, 5 crossings, 3 height layers (hierarchical layout)
- Principia Book 1 text in `quake/principia/` (14 sections, Wikisource)
- DIGESTED PRINCIPIA in `quake/principia/DIGESTED_PRINCIPIA.md`

### Tools available
- `tools/map_viewer.py` — fly the 3D wireframe corridor map (Mode A)
- `tools/room_viewer.py` — fly inside one room (Mode B)
- No `_render_probe.py` anymore (deleted as scratch — re-create if needed for offscreen renders)

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
Parent 10:   ❌ DIED (context overload)
Parent 11:   ✅ Renderers
Parent 12:   ❌ FAILED (polygon rooms — DeepSeek can't see images)
```

---

## PARENT 13 — LAUNCH PROTOCOL

### The handoff
File: `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_13_HANDOFF.md` (now ~340 lines after correction blocks)

### Launch files (paste these to the fresh Opus chat, in this order):
1. **Commentaries** — `quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md`
2. **Old Testament** — `quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md`
3. **New Testament** — `quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md` (has the Stabilo design + prooffig.asy convention + inscribed/circumscribed rects example for lemma_2)
4. **Apocrypha** — `quake/BIBLE/QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md`
5. **The Parent 13 handoff** — `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_13_HANDOFF.md`

GitHub raw URLs for copy-paste:
```
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/QUAKE_BIBLICAL_APOCRYPHA_ROOM_MAKER_V3_DOOR_BEARINGS_BY_OPUS.md
https://raw.githubusercontent.com/strulovitz/peaktogether-website/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_13_HANDOFF.md
```

### After launch — what DeepSeek does:
1. Parent 13 states his plan, asks 1 batch of questions (Principia text of Lemma II, prooffig convention)
2. DeepSeek fetches Lemma II text from `quake/principia/book_1/section_01.txt` and the current bake code (`bake/baker_figure.py`, `bake/prooffig_check.py`, `bake/palette_gen.py`) verbatim
3. Nir pastes answers
4. Parent 13 delivers 3 files: recipe.lemma_2.f1.json, figure.lemma_2.f1.asy, room_source.lemma_2.json
5. DeepSeek validates against raw_models.py (now using local_color + is_heart + colors_used)
6. DeepSeek runs the build pipeline: asy_compile → overlay_diff (Nir's eyes) → baker_figure + baker_text → room_maker → render offscreen → PNG for Nir

### Parent 13's deliverable saved at:
`quake/BIBLE/QUAKE_PARENT_13_FROZEN_DELIVERABLE.md`

---

## PARENT 14 — DEFERRED (after Parent 13 succeeds)
File: `quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_14_HANDOFF.md` (now ~370 lines after correction blocks)
Mission: Design format + build `build/room_from_spec.py` tool. Do NOT launch until Parent 13's one-room proof passes Nir's visual inspection.

---

## STANDING RULES (do not violate)
1. **Nir is the author. Nothing is frozen against him.** "Frozen" stops AI drift — never binds Nir.
2. **Never freeze the easy option silently.** Surface tradeoffs. The box-room is the cautionary tale.
3. **Render-and-look, don't just compile.** "Tests pass" means NOTHING for visual quality.
4. **Question-first material protocol.** Parents ask DeepSeek precise questions → verbatim excerpts.
5. **No "GO" on handoffs.** Talk-first rhythm.
6. **One mission per parent.** Don't bundle.
7. **Don't call him "boss"** — just Nir. Use PLENTY of emojis! 😊🎉✨💪
8. **Never add a hard constraint Nir didn't approve.**
9. **Never invent external-API names from memory.**
10. **Tables don't survive copy-paste.** Fenced code blocks only.
11. **382/382 tests must stay green.** Zero regressions.
12. **DeepSeek cannot do visual refinement.** All visual work = Nir's eyes + PNGs.
13. **Opus outputs saved VERBATIM** as "holy" scripture.
14. **Do NOT edit the Old Testament or New Testament.** They are fossils; corrections go in handoffs + Commentaries.

---

## IMMEDIATE NEXT STEP (on restart)
Ask Nir: "Launch Parent 13?" 🚀
