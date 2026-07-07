# LOOM2 — THE BHASHYA

## OPEN QUESTIONS / ENGINEERING ITEMS

### Awaiting a Nir decision

- 🟡 UPANISHADS scene 10 (Ocean Swell) format: keep the richer "match each groove" format or flatten to plain A/B/C/D. Nir's call, zero cost either way.
- 🟢 (optional, low priority) Quiz exit gesture — Fable's `game_state.py` chose **TOUCH THE TOTEM** to leave QUIZ_LISTEN (any totem move stops the option, land resumes; camera stays free while listening). Fable invites a veto by taste if Nir wants a different gesture. Already implemented; changing it is cheap.

### DeepSeek build-time items (none block Nir)

- ✅ M0-equivalent ear test — DONE (July 7). sounddevice 0.5.5 installed; both prototypes run; invention validated by ear.
- ✅ Sample library (SUTRAS Part Ten) — DONE (July 7). loom2/samples/ = 89 notes, 13 instruments (86 exact, 3 resampled ≤±2 st: violin_A7←G7 +2, tuba_E1←F1 −1, trumpet_Fs5←F5 +1; 0 missing). + manifest.json + coverage_report.txt + build_sample_library.py.
- ✅ PATH RECONCILIATION — DONE (July 7). Decision: MOVE the library to match the FROZEN config (config.SAMPLES_DIR="data/samples"), never edit config. The 89 mp3 + manifest.json + coverage_report.txt now live at loom2/data/samples/ (git mv, history preserved; old loom2/samples/ removed). build_sample_library.py OUT_DIR updated to write to data/samples/ so the reproducible recipe stays consistent. (The ear-test prototypes read from Downloads/philharmonia, NOT loom2/samples/, so the move was safe.)
- ✅ config.py + core/types.py — DONE (July 7). Extracted verbatim from Gita Part 1 to loom2/config.py + loom2/core/types.py. Parent A's quantize.py self-test PASSES against them (89 notes round-trip clean).
- 🔧 Seams DeepSeek STILL owes (mostly blocked until the relevant parent writes its module): create the empty shader files (REQUIRED_SHADERS) and paste working bloom/composite GLSL from Quake/Homeworld (needs Parent C's renderer.py); write tools/render_equations.py (LaTeX→PNG via MiKTeX, content-phase); fill the empty joystick/Xbox input slots from prior games (needs Parent F's input_map.py); enter scene JSON content (content-phase); PyInstaller EXE (ship-phase). Folder tree + __init__.py already exist for audio/core/graphics.
- 🎨 Nir-owned assets: the 13 instrument-icon cliparts (~128×128, transparent, "four emoji big") for data/icons/; a UI font for data/fonts/.


## CURRENT FRONTIER (July 7, 2026)

- ⚖️ **AMENDMENT (approved by Nir):** `AudioEngine.set_quiz_wav(path)` added (path=None stops, 30 ms fade; loops the option WAV through the same mix/soft-clip/pan path, routes sensibly under 5.1/7.1, mutually exclusive with voices). The Gita's frozen API had no WAV wire for `_quiz_select` (G4.3); this is the sanctioned fix. **Audio seam is now 5 calls, not 4** (set_voices; set_camera_azimuth; set_quiz_wav; get_measure_phase; get_active_flashes).
- ✅ **PURANAS Part 1 of 3 = `audio/engine.py`** landed (Fable Parent 2): saved verbatim in HINDU/ + extracted to `loom2/audio/engine.py` (py_compile OK).
- ✅ **PURANAS Part 2 of 3 = `core/game_state.py`** landed (Fable Parent 2): saved verbatim in HINDU/ + extracted to `loom2/core/game_state.py` (py_compile OK). Fable's one open design call (Nir may veto by taste): **quiz exit gesture = TOUCH THE TOTEM** (any totem move in QUIZ_LISTEN stops the option, land resumes). Stitching note for DeepSeek: keep `game_state._build_slice_path` literally in sync with `GlassBlade.intersection_path` (G3.6) so drawn curve == walked road.
- ✅ **PURANAS Part 3 of 3 = `graphics/helix_panel.py`** landed (Fable Parent 2): saved verbatim in HINDU/ + extracted to `loom2/graphics/helix_panel.py` (py_compile OK). **🏔️ THE PURANAS ARE COMPLETE.** 4 GLSL shaders delivered by Fable, placed in `loom2/data/shaders/` (wire.vert, wire.frag, icon_billboard.vert, icon_billboard.frag). Three soft seams for DeepSeek to verify at stitch time: (1) `Renderer.ctx` exposed (else falls back to `moderngl.get_context()`); (2) matrix convention (assumes `clip = VP·p`, uploads transposed — flip if Child C uses row-vectors); (3) optionally `panel.z_per_octave = spec.z_per_octave` on scene change.

- ✅ The whole scripture canon is DOWN and pushed verbatim: VEDAS, MAHABHARATA, RAMAYANA, UPANISHADS, SUTRAS, BHAGAVAD GITA Parts 1–4, + the Parent 1→2 hand-off letter.
- ✅ The invention is real — ear-tested by Nir on both prototypes.
- ✅ The 89-sample orchestra is built and committed (canon in config.REGISTER_MAP).
- ✅ Architecture & every module contract are FROZEN (the Gita).
- 🏁 Fable "Parent 1" retired at the hand-off — his whole design is externalized into the repo; he can die with nothing lost.
- 🏔️ **THE PURANAS ARE COMPLETE** — all three heavy modules delivered by Fable Parent 2 (audio/engine.py, core/game_state.py, graphics/helix_panel.py), saved verbatim + extracted + committed. Parent 2's hand-off letter is saved verbatim at `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-2.md`.
- 🔁 **PLAN CHANGE (Nir, July 7, 2026) — worker-PARENTS, not children.** Parent 2's hand-off invented a supervisor "Parent 3" (arbitration + content) but **never assigned the actual writing of the remaining ~14 modules** — it just assumed they'd appear. Nir judged Parent 2 lost the plan (context) and that one chat can't do 7 children's work. **New plan:** a sequence of full worker-PARENTS (A, B, C, …), each doing ONE former Gita-G4.6 child chunk **as a parent** (full context/freedom/authority), not a sandboxed child. "Parent 3" as imagined is retired; supervision + content happen later. Full detail + the chunk list + the courier culture are in WORKFLOW §4.6.
- ⏭️ **CURRENT NEXT STEP = launch PARENT A** — chunk = `audio/quantize.py` + `audio/musicians.py`. Launch document = `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-2.md` (Parent 2's verbatim letter + Nir's inserted bridge + Parent A's note, all folded into one file after §5; Nir pastes the whole thing to a fresh Fable chat). When Parent A replies: DeepSeek saves verbatim → extracts code → py_compile → update memory → commit/push → blob links. Parent's open questions reach DeepSeek via **Nir as courier**, in batches; parent may split long files and DeepSeek concatenates.
- ⏳ Then: Parents B–G write the rest; DeepSeek binds the seams (folders/__init__ already partly done: audio/, core/, graphics/ exist with __init__.py; config.py + core/types.py still owed; path reconciliation; shaders bloom/composite; joystick/Xbox; render_equations; PyInstaller).
- ⏳ Then: content — the 12 scenes' JSON + hints + wrong-answer explanations (Fable drafts, Nir approves by taste), render option WAVs + equation PNGs; ship; add the subject to the website.
