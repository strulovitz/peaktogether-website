# DEEPSEEK RESTART — Ceiling Equation Fix (July 3, 2026)

## STATE ON RESTART

**Game runs. 20/20 rooms built. 468/468 green. Golden door titles + floor names DONE. Asymptote translator fixed (20/20 figures). Ceiling equation POSITIONS fixed (each now near its station's wall).**

## WHAT WE'RE IN THE MIDDLE OF

**Adding per-station ceiling equations.** Each station needs its own ceiling equation.

### ALL 16 child rooms: DONE ✅ (verified by file count July 3, 2026)
Every child room has station-count == ceiling-count: lemma_3,4,5,6,7,9,10,11,12 + prop_1,2,6,7,11,13,15. Nothing missing here.

### DeepSeek-written rooms: 4 rooms need FULL REWRITE from scratch
These 4 rooms were written by DeepSeek, not children. All need a child to write a COMPLETE new .room file. Each station needs its own ceiling equation. The prompts (old name in git history, renamed to `*_NEW.md`):
- 🔴 `law_1` — `CHILD_PROMPT_LAW_1_NEW.md`
- 🔴 `law_2` — `CHILD_PROMPT_LAW_2_NEW.md`
- 🔴 `prop_4` — `CHILD_PROMPT_PROP_4_NEW.md`
- 🔴 `lemma_2` — `CHILD_PROMPT_LEMMA_2_NEW.md`

Children will write COMPLETE .room files from scratch — stations, panels, text, colors, AND ceiling equations. Each prompt gives: Newton source material + station descriptions + ROOMSPEC format reference + asks for complete .room file.

## TO DO ON RESTART

1. Ask Nir which child answered. He pastes the child's complete .room file (only 3 left: law_1, prop_4, lemma_2).
2. Replace the ENTIRE existing .room file in `tests/room_specs/<room>.room` with the child's file.
3. After ALL 3 are done:
   - Rebuild: run `python build/build_all.py` from `quake/` directory
   - Run `pytest quake/tests/` — must be 468+ green
   - Smoke test: `python -c "import sys; sys.path.insert(0,'quake'); from app import main; main(smoke_frames=1)"`
   - Update WORKFLOW.md and Commentaries
   - Push to GitHub
