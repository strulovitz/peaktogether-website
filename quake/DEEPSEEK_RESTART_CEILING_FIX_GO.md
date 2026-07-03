# DEEPSEEK RESTART — Ceiling Equation Fix (July 3, 2026)

## STATE ON RESTART

**Game runs. 20/20 rooms built. 468/468 green. Golden door titles + floor names DONE. Asymptote translator fixed (20/20 figures). Ceiling equation POSITIONS fixed (each now near its station's wall).**

## WHAT WE'RE IN THE MIDDLE OF

**Adding per-station ceiling equations.** Each station needs its own ceiling equation.

### 15/16 child rooms: ceiling lines FIXED
Children were re-contacted and provided per-station ceiling equations. Updated in `tests/room_specs/`. These files are child work.

### 4 DeepSeek-written rooms: FULL REWRITE needed
These rooms (law_1, law_2, prop_4, lemma_2) were originally written by DeepSeek, not children. Children will write COMPLETE .room files from scratch — stations, panels, text, colors, AND ceiling equations. Child prompts ready:

- `CHILD_PROMPT_PROP_4_CEILINGS.md` — prop_4 (equation, 2 stations)
- `CHILD_PROMPT_LAW_1_CEILINGS.md` — law_1 (text, 4 stations)
- `CHILD_PROMPT_LAW_2_CEILINGS.md` — law_2 (equation, 2 stations)
- `CHILD_PROMPT_LEMMA_2_CEILING.md` — lemma_2 (geometry, 3 stations)

Each prompt gives: Newton source material + station descriptions + ROOMSPEC format reference + asks for complete .room file.

## TO DO ON RESTART

1. Ask Nir which child answered. He pastes the child's complete .room file.
2. Replace the ENTIRE existing .room file in `tests/room_specs/<room>.room` with the child's file.
3. After ALL 4 are done:
   - Rebuild: run `python build/build_all.py` from `quake/` directory
   - Run `pytest quake/tests/` — must be 468+ green
   - Smoke test: `python -c "import sys; sys.path.insert(0,'quake'); from app import main; main(smoke_frames=1)"`
   - Update WORKFLOW.md and Commentaries
   - Push to GitHub
