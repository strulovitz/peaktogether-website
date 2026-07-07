# LOOM2 — THE BHASHYA

## OPEN QUESTIONS / ENGINEERING ITEMS

### Awaiting a Nir decision

- 🟡 UPANISHADS scene 10 (Ocean Swell) format: keep the richer "match each groove" format or flatten to plain A/B/C/D. Nir's call, zero cost either way.

### DeepSeek build-time items (none block Nir)

- ✅ M0-equivalent ear test — DONE (July 7). sounddevice 0.5.5 installed; both prototypes run; invention validated by ear.
- ✅ Sample library (SUTRAS Part Ten) — DONE (July 7). loom2/samples/ = 89 notes, 13 instruments (86 exact, 3 resampled ≤±2 st: violin_A7←G7 +2, tuba_E1←F1 −1, trumpet_Fs5←F5 +1; 0 missing). + manifest.json + coverage_report.txt + build_sample_library.py.
- ⚠️ PATH RECONCILIATION (at scaffolding time): the Gita's config.py expects the library at data/samples/ (SAMPLES_DIR="data/samples"), but DeepSeek's built library currently lives at loom2/samples/. When scaffolding the package, either move it to loom2/data/samples/ or adjust config paths — pick one and record it here.
- 🔧 Seams DeepSeek owes (per Gita, before/around child work): create the folder tree + __init__.py; commit config.py + core/types.py verbatim from Gita Part 1; create the empty shader files (REQUIRED_SHADERS) and paste working bloom/composite GLSL from Quake/Homeworld; write tools/render_equations.py (LaTeX→PNG via MiKTeX); fill the empty joystick/Xbox input slots from prior games; enter scene JSON content; PyInstaller EXE.
- 🎨 Nir-owned assets: the 13 instrument-icon cliparts (~128×128, transparent, "four emoji big") for data/icons/; a UI font for data/fonts/.


## CURRENT FRONTIER (July 7, 2026)

- ⚖️ **AMENDMENT (approved by Nir):** `AudioEngine.set_quiz_wav(path)` added (path=None stops, 30 ms fade; loops the option WAV through the same mix/soft-clip/pan path, routes sensibly under 5.1/7.1, mutually exclusive with voices). The Gita's frozen API had no WAV wire for `_quiz_select` (G4.3); this is the sanctioned fix. **Audio seam is now 5 calls, not 4** (set_voices; set_camera_azimuth; set_quiz_wav; get_measure_phase; get_active_flashes).
- ✅ **PURANAS Part 1 of 3 = `audio/engine.py`** landed (Fable Parent 2): saved verbatim in HINDU/ + extracted to `loom2/audio/engine.py` (py_compile OK). ⏳ Part 2 = `core/game_state.py`, ⏳ Part 3 = `graphics/helix_panel.py` (one file per answer; Nir says "continue").

- ✅ The whole scripture canon is DOWN and pushed verbatim: VEDAS, MAHABHARATA, RAMAYANA, UPANISHADS, SUTRAS, BHAGAVAD GITA Parts 1–4, + the Parent 1→2 hand-off letter.
- ✅ The invention is real — ear-tested by Nir on both prototypes.
- ✅ The 89-sample orchestra is built and committed (canon in config.REGISTER_MAP).
- ✅ Architecture & every module contract are FROZEN (the Gita).
- 🏁 Fable "Parent 1" retired at the hand-off — his whole design is externalized into the repo; he can die with nothing lost.
- ⏳ NEXT: Fable "Parent 2" continues the PURANAS — Part 2 = `core/game_state.py`, then Part 3 = `graphics/helix_panel.py`, delivered ONE COMPLETE FILE PER ANSWER (Nir says "continue" between them). Launch kit = the hand-off letter + the four ruling scriptures.
- ⏳ Then: DeepSeek scaffolds the package and the seven child chats fill the remaining contracts (the Gita's assignment plan); DeepSeek integrates, tests, packages the EXE, pushes.
- ⏳ Then: content — write the 12 scenes' JSON + hints + wrong-answer explanations (Fable drafts, Nir approves by taste), render option WAVs + equation PNGs; ship; add the subject to the website.
