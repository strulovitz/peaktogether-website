🌙 DEEPSEEK RESTART HANDOFF — BUILD PIPELINE PHASE — July 1, 2026

## ⚠️ ON RESTART: READ THIS FIRST, THEN WORKFLOW, THEN COMMENTARIES ⚠️

---

## 🏆 WHAT WE ACHIEVED TODAY (July 1, 2026)

**20/20 Principia rooms built and validated in ONE DAY!** 🔥👑

All .room spec files live in `quake/tests/room_specs/`:
- 11 lemmas: lemma_2,3,4,5,6,7,9,10,11,12 + law_1 (text), law_2 (equation)
- 9 propositions: prop_1,2,4,6,7,11,13,15
- 435/436 tests green (only pre-existing smoke test path issue)
- All validate GREEN against `room_from_spec.py` parser/validator

Children wrote .room files. DeepSeek fixed keyword syntax and integrated.
Nir paste children to/from fresh Opus 4.8 chats.

All child prompts saved: `quake/CHILD_PROMPT_{LEMMA,PROP}_*.md`

---

## 🎯 THE MISSION: BUILD THE LEVEL PACK 🎯

**Goal:** Turn all 20 .room files into the complete baked game data that `app.py` can load.

**Output directory:** `quake/levels/principia_bk1_inverse_square/`
**Currently:** Only lemma_2 has baked output (gold proof-of-concept).

### THE 20 ROOMS BY KIND

| Kind | Count | Rooms |
|------|-------|-------|
| **geometry** | 15 | lemma_2,3,4,5,6,7,9,10,11,12, prop_1,2,6,7,11,13 |
| **equation** | 3 | law_2, prop_4, prop_15 |
| **text** | 1 | law_1 |
| **equation/text** | 1 | (actually handled: law_1 is text, others are equation) |

Wait — let me be precise. From Parent 15 station map:
- 16 DIAGRAM rooms (geometry)
- 2 EQUATION rooms (prop_4, prop_15)  
- 1 TEXT room (law_1)
- 1 EQUATION/TEXT room (law_2 — treated as equation)

So: 16 geometry + 2 equation + 1 text + 1 equation/text = 20 ✓

### STAGE 1: Emit outputs from .room files

For EACH room, run `room_from_spec.py`:
```python
from pathlib import Path
from build.room_from_spec import build_room

out_root = Path("levels/principia_bk1_inverse_square")
for room_id in ALL_20_IDS:
    spec_text = (SPEC_DIR / f"{room_id}.room").read_text(encoding="utf-8")
    result = build_room(spec_text, out_root)
```

This writes:
- `recipes/<room_id>.f1.json` (None for text rooms)
- `figures/<room_id>.f1.asy`
- `room_sources/<room_id>.json`

SPEC_DIR = `tests/room_specs/`

### STAGE 2: Compile figures → PNGs

**Geometry rooms** (16): Use `baker_figure.bake()` with Asymptote compiler
- Module: `bake/baker_figure.py` — `bake(figure_asy, figure_id, n_steps, out_dir, palette, cfg, compile_fn)`
- Module: `bake/asy_compile.py` — `compile(src, out_stem, params, cfg)` 
- Invokes: `asy -u "highlight=-1" -f png -noV -render 4 -o <stem> <src.asy>` (OFF)
- Invokes: `asy -u "highlight=k" -f png -noV -render 4 -o <stem> <src.asy>` (ON for step k)
- Asymptote binary: `C:\Program Files\Asymptote\asy.exe`
- Ghostscript: `C:\Users\nir_s\gs\bin\gswin64c.exe` (env var ASYMPTOTE_GS)

**Equation rooms** (law_2, prop_4, prop_15): Use pdflatex+pdftocairo
- See reference: `C:\Users\nir_s\AppData\Local\Temp\opencode\build_law2.py`
- pdflatex: `C:\Users\nir_s\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe`
- pdftocairo: on PATH

**Text room** (law_1): Uses Asymptote for label-only rendering (no geometry, all `phrase` ops)
- `emit_recipe` returns None for text rooms
- The .asy file has phrase ops rendered as labels

### STAGE 3: Bake text panels → PNGs

Module: `bake/baker_text.py` — `bake(text_block, palette, out_dir, cfg, compile_fn)`
- Uses pdflatex+pdftocairo (Descent pattern, native transparency)
- OFF: strips `\textcolor{name}{...}` → all black
- ON: actual hex colors from colors_used
- Returns: `<block_id>.off.png`, `<block_id>.on.png` (+ @master variants)

### STAGE 4: Ceiling equations → PNGs

For each `ceiling_equation` in room_source:
- pdflatex+pdftocairo standalone template
- key_out_white + trim(padding=4)
- Returns: `<eq_id>.neutral.png` + `@master`

### STAGE 5: Assemble manifest + palette

- `Manifest(schema_version, level_id, assets={all_asset_entries})` from `map/raw_models.py`
- Palette from `palette.json` (already corrected — map-side only)
- Copy all PNGs to pack directory

### STAGE 6: Build room runtime

For each room:
```python
from build.room_maker import build_room_runtime
from build.portal_spec import portal_spec

portal = portal_spec(floorplan, concept_graph, room_id)
room_rt = build_room_runtime(room_source, portal, manifest, cfg)
```

### TOOL PATHS (hardcoded, Windows)

| Tool | Path |
|------|------|
| Asymptote | `C:\Program Files\Asymptote\asy.exe` |
| pdflatex | `C:\Users\nir_s\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe` |
| pdftocairo | on PATH |
| Ghostscript | `C:\Users\nir_s\gs\bin\gswin64c.exe` |
| Python | `python` (base conda — has pygame, PyOpenGL, numpy, matplotlib) |

### REFERENCE BUILD SCRIPTS (at %TEMP%\opencode\)

Study these for exact patterns:
- `build_full.py` — lemma_2 geometry room: full Asymptote + pdflatex text + ceiling + room_maker
- `build_law2.py` — law_2 equation room: pdflatex figure + text + ceiling + room_maker
- `build_lemma2_room.py` — lemma_2 geometry: Asymptote figure + placeholder text + room_maker

### EXISTING GOLD DATA (lemma_2 only)

`levels/principia_bk1_inverse_square/` already has:
- `recipes/lemma_2.f1.json`
- `figures/lemma_2.f1.asy`
- `room_sources/lemma_2.json`
- `concept_graph.json` (20 nodes, 30 edges — ALL rooms)
- `floorplan.json` (generated by `run_level_maker.py`)

### CONCEPT GRAPH + FLOORPLAN

Already built! Run `run_level_maker.py` → produces `floorplan.json` from `concept_graph.json`.
- 20 nodes, 30 edges (including external_citation sidecar entries)
- Layout: hierarchical force-directed (planets freeze, asteroids added)
- 5 natural crossings → bridges/underpasses in 3D

---

## 📋 STEP-BY-STEP BUILD PLAN (for fresh DeepSeek)

1. **Re-read context:** WORKFLOW.md, Commentaries, this handoff
2. **Study reference scripts:** Read `build_full.py` and `build_law2.py` from `%TEMP%\opencode\`
3. **Write the master build script:** `quake/build/build_all.py` that builds all 20 rooms:
   - Loop over all 20 room IDs
   - Stage 1: `build_room()` for each → emit recipe/asy/room_source
   - Stage 2: Compile figures (Asymptote for geometry, pdflatex for equation)
   - Stage 3: Bake text (pdflatex for all)
   - Stage 4: Ceiling equations (pdflatex)
   - Stage 5: Assemble manifest
   - Stage 6: build_room_runtime for each room
4. **Run build_all.py** — debug any failures
5. **Verify:** All PNGs generated, all JSONs valid, manifest complete
6. **Room viewer test:** Load a room in `tools/room_viewer.py` to visually verify
7. **Smoke test:** Run `app.py` with the full pack
8. **Commit + push** everything

---

## ⚠️ KNOWN GOTCHAS ⚠️

- **Asymptote 2.88 (MiKTeX bundled) is BROKEN** — use standalone Asy 3.12 at `C:\Program Files\Asymptote\asy.exe`
- **Asymptote 3.12 needs hex colors as DECIMAL integers** — `0xHH` hex literals don't work; use decimal
- **pdflatex needs `-interaction=nonstopmode`** flag
- **pdftocairo needs `-transp`** for native transparency, `-r 220` (with space)
- **Never use Ghostscript keyout** for text — use pdftocairo native transparency (Descent pattern)
- **Equation rooms** (law_2, prop_4, prop_15) have no geometry ops — their "figure" is the equation layout itself, rendered via pdflatex
- **Text room** (law_1) has `emit_recipe → None` but still has an .asy with phrase ops
- **Color system:** local per-station, never grey, current-step-only Stabilo hearts
- **`circle_cr` needs `radiusval <n>`** — not bare number
- **Cross-station references:** stations don't share geometry — every station re-defines all points/curves from scratch
- **Git push after every meaningful milestone**

---

## 🎯 END STATE

When done, `levels/principia_bk1_inverse_square/` should contain:
- `concept_graph.json` ✅ (already exists)
- `floorplan.json` ✅ (already exists)
- `palette.json` ✅ (already exists, corrected)
- `manifest.json` (all AssetEntries)
- `recipes/*.f1.json` (19 new + lemma_2)
- `figures/*.f1.asy` (19 new + lemma_2)
- `room_sources/*.json` (19 new + lemma_2)
- `assets/*.png` (all baked PNGs: off/on figures, off/on text, neutral ceilings)
- `room_runtime/room_*.json` (all 20)

And `app.py` should successfully load the pack and start the game with all 20 rooms!

---

## STANDING REMINDERS

- Nir is **Nir** — never "boss". Loves emojis 😊
- Normal prose, no pop-ups
- Never take decisions off Nir's plate
- 🛑 BREAKING CHANGE GUARD
- 📦 NEVER upgrade/overwrite working packages
- Build scripts: commit them to the repo
- Temp files: use `%TEMP%\opencode\`
- Commit + push frequently

---

*Written by DeepSeek at end of July 1, 2026 marathon session. 20/20 rooms done. Time to BUILD.* 🚀
