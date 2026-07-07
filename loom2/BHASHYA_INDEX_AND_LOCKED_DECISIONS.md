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

- ✅ The whole scripture canon is DOWN and pushed verbatim: VEDAS, MAHABHARATA, RAMAYANA, UPANISHADS, SUTRAS, BHAGAVAD GITA Parts 1–4, + the Parent 1→2 hand-off letter.
- ✅ The invention is real — ear-tested by Nir on both prototypes.
- ✅ The 89-sample orchestra is built and committed (canon in config.REGISTER_MAP).
- ✅ Architecture & every module contract are FROZEN (the Gita).
- 🏁 Fable "Parent 1" retired at the hand-off — his whole design is externalized into the repo; he can die with nothing lost.
- ⏳ NEXT: Fable "Parent 2" writes the PURANAS — the three heavy modules, audio first (audio/engine.py), delivered ONE COMPLETE FILE PER ANSWER (Nir says "continue" between them). Launch kit = the hand-off letter + the four ruling scriptures.
- ⏳ Then: DeepSeek scaffolds the package and the seven child chats fill the remaining contracts (the Gita's assignment plan); DeepSeek integrates, tests, packages the EXE, pushes.
- ⏳ Then: content — write the 12 scenes' JSON + hints + wrong-answer explanations (Fable drafts, Nir approves by taste), render option WAVs + equation PNGs; ship; add the subject to the website.
