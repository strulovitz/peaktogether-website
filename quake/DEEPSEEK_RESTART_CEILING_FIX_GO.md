# DEEPSEEK RESTART — Ceiling Equation Fix (July 3, 2026)

## STATE ON RESTART

**Game runs. 20/20 rooms built. 468/468 green. Golden door titles + floor names DONE. Asymptote translator fixed (20/20 figures). Ceiling equation POSITIONS fixed (each now near its station's wall).**

## WHAT WE'RE IN THE MIDDLE OF

**Adding per-station ceiling equations.** The existing 20 `.room` files had only 1-2 ceiling equations per room. Each station should have its own ceiling equation (one per step).

### Progress so far (15/19 done):

All 16 child-created rooms are DONE with their ceiling fixes. Lemmas 5,12 and prop_15 were already correct.

### REMAINING (4 rooms, child prompts rewritten):

Each child prompt gives the Newton source material and asks for per-station ceiling equations — NO prior AI work is fed to the child. Files:

| File | Status |
|------|--------|
| `CHILD_PROMPT_PROP_4_CEILINGS.md` | ⏳ Paste to Opus |
| `CHILD_PROMPT_LAW_1_CEILINGS.md` | ⏳ Paste to Opus |
| `CHILD_PROMPT_LAW_2_CEILINGS.md` | ⏳ Paste to Opus |
| `CHILD_PROMPT_LEMMA_2_CEILING.md` | ⏳ Paste to Opus |

## TO DO ON RESTART

1. Ask Nir which child answered. He will paste the child's response.
2. Update the `.room` file:
   - `tests/room_specs/prop_4.room` — replace the 1 ceiling line with child's 2
   - `tests/room_specs/law_1.room` — replace the 1 ceiling line with child's 4
   - `tests/room_specs/law_2.room` — replace the 2 ceiling lines with child's 2
   - `tests/room_specs/lemma_2.room` — add child's eq2 as the third ceiling line
3. After ALL 4 are done:
   - Rebuild all `.room` files → `.asy` + `room_source` (run build_all.py or just stage 1 + stage 4 + stage 6)
   - Recompile ceiling equation PNGs (stage 4)
   - Rebuild room runtimes (stage 6)
   - Run `pytest quake/tests/` — must be 468+ green
   - Smoke test
   - Update WORKFLOW.md and Commentaries
   - Push to GitHub

## STANDING RULES (from WORKFLOW §10)
- NEVER add hard constraints Nir didn't approve
- Fix CENTRALLY, never per-room
- Test with actual game before declaring victory
- Ask before touching code
- Keep the emojis 😊
