# ⚡ DEEPSEEK RESTART — PARENT 14 LAUNCH (June 30, 2026)

## STATE ON RESTART
- 385/385 tests GREEN 🟢
- Engine + renderers DONE · Color system CORRECTED · Box rooms intact
- Parent 13 DONE (lemma_2 pipeline proof-of-concept)
- Parent 14 handoff v2 CLEAN REWRITE — matched to actual `raw_models.py` code

## RESTART PROTOCOL
1. Read `quake/WORKFLOW.md` — project memory
2. Read `quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md` — the Commentaries
3. Ask Nir what's next

## PARENT 14 LAUNCH — Files to give Nir (GitHub URLs for copy-paste)

Nir pastes these 4 files into a FRESH Opus 4.8 chat:

**Baseline (always):**
1. Commentaries: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_COMMENTARIES_BIBLE_INDEX_AND_LOCKED_DECISIONS.md
2. Old Testament: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_DOCTRINE_BY_FUSION.md
3. New Testament: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/QUAKE_NEW_TESTAMENT_TWO_LEGS_BY_OPUS.md

**The mission:**
4. Parent 14 handoff v2: https://github.com/strulovitz/peaktogether-website/blob/master/quake/BIBLE/PROMPT_TO_OPUS_QUAKE_PARENT_14_HANDOFF.md

## STANDING RULES (remind Nir)
- Nir pastes the 4 files → Parent states approach + questions → DeepSeek answers → Parent builds
- Talk-first rhythm (no "GO")
- Parent 14 has no internet — if it asks for files, DeepSeek fetches from disk, Nir pastes
- Never paste tables (they die on copy-paste) — use fenced code blocks
- One mission, one deliverable: format spec + `build/room_from_spec.py`

## RECENT ENGINE FIXES (Parent 14 doesn't need these, but we know they work)
- Wall collision in room_viewer.py
- Per-wall ceiling UV (N/S/E/W correct orientation)
- Ceiling text sizing from actual PNG dimensions
