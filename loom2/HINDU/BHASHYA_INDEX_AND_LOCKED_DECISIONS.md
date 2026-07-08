# LOOM2 — THE BHASHYA

## OPEN QUESTIONS / ENGINEERING ITEMS

### Awaiting a Nir decision

- 🟡 UPANISHADS scene 10 (Ocean Swell) format: keep the richer "match each groove" format or flatten to plain A/B/C/D. Nir's call, zero cost either way.
- 🟢 (optional, low priority) Quiz exit gesture — Fable's `game_state.py` chose **TOUCH THE TOTEM** to leave QUIZ_LISTEN (any totem move stops the option, land resumes; camera stays free while listening). Fable invites a veto by taste if Nir wants a different gesture. Already implemented; changing it is cheap.

### Decided by Nir (recently closed)

- 🔪 **PARENT E Q&A BATCH 1 — Nir's calls (July 8).** Full Q&A saved verbatim at `PARENT-E-QA-BATCH-1-NIR-DECISIONS.md`. **Q4 (bead) = OPTION 2, the ADDITIVE AMENDMENT** — expose walk index (+walking) in `game_state.snapshot()`, add `GlassBlade.set_walk_stop(idx_or_none)`, main wires it; Parent E draws a precise bead ON the curve. Nir authorized amending the frozen contracts + extra stitching. **PLUS a locked design directive: SUPPRESS/HIDE the tall totem in SLICE mode** — when concentrating on one path exact height is critical and the tall totem reads like a "margin of error" that confuses players; the precise glowing bead (at z=f(stop)) is the true position marker. (main/frame-order + maybe totem_visual job at Parent G — record as amendment when implemented.) **Q7 (look) = show Nir ALL options with tradeoffs, no pre-selection.** Standing note couriered: Fable may ask DeepSeek as many questions/rounds as needed.

- 🚫🔒 **IRON RULE — NO FLAT SHADING, EVER (Nir, absolute).** Every 3D surface/model in LOOM2 is **GOURAUD** shaded. Flat shading is FORBIDDEN in all of Nir's games — not a taste a parent may pick, propose, "park," or default to. If a contract/shader blocks it, amend the contract to make it Gouraud. Flat geometry = a BUG, never an acceptable delivery. (Parent D's totem helix shipped flat; being fixed to Gouraud July 8.)
- 📜🔧 **POLICY — AMEND THE ACTUAL SCRIPTURES (Nir, July 8).** When a Fable parent says to change/correct/add/remove anything in the frozen scriptures, DeepSeek inserts a clearly-enclosed amendment block IN THE ACTUAL SCRIPTURE FILE (at the end of the relevant section) — NOT only in this BHASHYA (nobody reads it but DeepSeek; future parents read the scriptures). Fence: `<<<<<<<<<< AMENDMENT <id> — added <date> >>>>>>>>>>` … `<<<<<<<<<< END AMENDMENT <id> >>>>>>>>>>`, stating WHAT/WHY/WHO-ORDERED (always Nir)/WHICH-PARENT/STATUS. Never rewrite a parent's original words — leave intact, append the block. (Applied July 8: Gita Pt2 G2.4-A/G2.5-A/G2.SEAM-A; Gita Pt3 G3.1-A/G3.2-A/G3.3-A/G3.4-A.)

- ✅ **A7 draped rings — APPROVED (July 8).** Gita G3.4 amended (Amendment #2 in WORKFLOW): `TotemVisual.draw` `ground_z: float` → `height_fn`; main passes `terrain.height_at`. Fable writes totem.py against it. **DeepSeek owes: wire main** (at Parent G).
- ✅ **Snow-bloom — KEEP the faint shimmer (July 8).** Peak-snow ≈0.82–0.84 gently exceeds the 0.80 bloom bright-pass; terrain stays as delivered (no matte rescale).

### DeepSeek build-time items (none block Nir)

- ✅ M0-equivalent ear test — DONE (July 7). sounddevice 0.5.5 installed; both prototypes run; invention validated by ear.
- ✅ Sample library (SUTRAS Part Ten) — DONE (July 7). loom2/samples/ = 89 notes, 13 instruments (86 exact, 3 resampled ≤±2 st: violin_A7←G7 +2, tuba_E1←F1 −1, trumpet_Fs5←F5 +1; 0 missing). + manifest.json + coverage_report.txt + build_sample_library.py.
- ✅ PATH RECONCILIATION — DONE (July 7). Decision: MOVE the library to match the FROZEN config (config.SAMPLES_DIR="data/samples"), never edit config. The 89 mp3 + manifest.json + coverage_report.txt now live at loom2/data/samples/ (git mv, history preserved; old loom2/samples/ removed). build_sample_library.py OUT_DIR updated to write to data/samples/ so the reproducible recipe stays consistent. (The ear-test prototypes read from Downloads/philharmonia, NOT loom2/samples/, so the move was safe.)
- ✅ config.py + core/types.py — DONE (July 7). Extracted verbatim from Gita Part 1 to loom2/config.py + loom2/core/types.py. Parent A's quantize.py self-test PASSES against them (89 notes round-trip clean).
- 🔧 Seams DeepSeek STILL owes (mostly blocked until the relevant parent writes its module): **wire `main` to pass `terrain.height_at` into `TotemVisual.draw`** (Amendment #2, draped rings — done at Parent G when main is written); create the empty shader files (REQUIRED_SHADERS) and paste working bloom/composite GLSL from Quake/Homeworld (needs Parent C's renderer.py); write tools/render_equations.py (LaTeX→PNG via MiKTeX, content-phase); fill the empty joystick/Xbox input slots from prior games (needs Parent F's input_map.py); enter scene JSON content (content-phase); PyInstaller EXE (ship-phase). Folder tree + __init__.py already exist for audio/core/graphics.
- 🎨 Nir-owned assets: the 13 instrument-icon cliparts (~128×128, transparent, "four emoji big") for data/icons/; a UI font for data/fonts/.


## CURRENT FRONTIER (July 7, 2026)

### 🔖 RESTART SNAPSHOT (July 8, 2026) — quick orientation

**🗓️ THIS SESSION (July 8): Parent D finished + handed off to Parent E.** In order: Parent D
delivered terrain.py (verbatim/extracted/pushed); Nir approved A7 draped-rings + KEEP snow-bloom;
Parent D delivered totem.py but FLAT → Nir caught it, IRON RULE (no flat shading ever) locked;
Parent D redelivered totem.py GOURAUD via a new 9th "totem" shader; Nir ordered the NEW POLICY to
amend the ACTUAL scriptures (applied Gita Pt2 G2.4-A/G2.5-A/G2.SEAM-A + Pt3 G3.1-A/G3.2-A/G3.3-A/
G3.4-A); Parent D's hand-off letter to Parent E saved verbatim; assignment verified vs Gita;
DeepSeek FACTS-ONLY info block appended + its "Q1–Q4" headers relabeled. **All pushed, tree clean.**

- **Progress:** Parents **A, B, C, D COMPLETE**. 🎉 Parent D delivered BOTH `graphics/terrain.py`
  (+ `terrain.vert`/`terrain.frag`) and `graphics/totem.py` (the breathing GOURAUD helix + the new
  `totem.vert`/`totem.frag`) — each saved verbatim, extracted, py_compile-clean, pushed.
- **⏭️ NEXT ACTION = BIRTH PARENT E** — chunk = `graphics/slice_mode.py` ("The Glass Blade" 🔪)
  + `glass.vert`/`glass.frag` (owned wholesale). **LAUNCH DOC ALREADY BUILT + PUSHED:**
  `HAND-OFF-PROMPT-FROM-FABLE-PARENT-D.md` (Parent D's verbatim letter + DeepSeek FACTS-ONLY info
  block at end, marked NOT Fable). Assignment already VERIFIED against Gita (G4.6 "Child E:
  slice_mode.py" + G3.6 GlassBlade). Nir opens a fresh Fable chat, pastes that whole file as msg #1,
  feeds scriptures one at a time in the letter's order, gives blob links. Keep
  `game_state._build_slice_path` in sync with `GlassBlade.intersection_path` (G3.6).
- **📐 TOTEM CANON (locked):** A7 signature LIVE = `TotemVisual.draw(self, view_proj, totem_state,
  height_fn, measure_phase)`; main step 4 = `totem_visual.draw(vp_left, snap_totem,
  terrain.height_at, phase)` — **DeepSeek owes wiring main at Parent G.** Uses the NEW `totem`
  Gouraud program for the helix surface + shared `flat` (`u_mvp`/`u_color`/`in_pos`) for LINES only.
  Breath clock unwraps measure_phase (no `time` import); ~3 s breath never locks to 2 s measure.
  Warm-gold ribbon helix (dark edge lines keep it readable, A6); rings
  n=1..min(NMAX_RING,⌊hr/RING_WIDTH⌋) static/calm (A5); circle+arm (A1 `90°−phase×360°`) DRAPED via
  height_fn, lifted 0.05. Flagged `release()`.
  🚫→✅ IRON RULE + FIX: NO FLAT SHADING EVER (everything Gouraud). Parent D's first totem
  shipped flat; **redelivered GOURAUD (July 8)** via a NEW 9th shader stem "totem"
  (`data/shaders/totem.vert/.frag`, owned by Child D) — `flat` now draws only LINES;
  `REQUIRED_SHADERS` 8→9. Saved verbatim (`LOOM2-PARENT-D-PART-2-TOTEM-GOURAUD-REDELIVERY-BY-FABLE.md`),
  py_compile OK, ACTUAL scriptures amended (G3.1-A + G3.4-A).
- **📐 TERRAIN CANON (locked):** shader IF `terrain.vert`= `mat4 u_mvp; vec3 in_pos; float
  in_light;` / `terrain.frag`= `vec3 u_band_colors[6]; float u_band_edges[5];`. HARD bands (per-
  fragment) × GOURAUD (per-vertex Lambert) = smooth shading + pixel-sharp level curves. Band edges
  (abs world z, all scenes) **(−1.5,−0.6,0,1.1,2.2)**; darkest abyss `COLOR_DEEP_WATER×0.55`. Land
  ≤1.0 except snowcaps ≈0.82–0.84 (Nir KEEPS faint bloom). `height_at` = numpy-capable passthrough.
- **✅ BOTH Parent-D items DECIDED (July 8):** A7 amendment APPROVED (Amendment #2 in WORKFLOW:
  `ground_z`→`height_fn`; Gita scripture kept pristine; DeepSeek owes wiring main); snow-bloom KEEP.
- **After D:** Parent E (slice_mode), Parent F (hud + input_map), Parent G (surfaces + scene +
  main), then DeepSeek stitches deferred seams + content.

### 🔖 PRIOR SNAPSHOT (July 8, 2026, terrain half) — quick orientation
- **Progress:** Parents **A, B, C COMPLETE**. **PARENT D IS IN FLIGHT** — a live Fable
  chat writing `graphics/terrain.py` + `graphics/totem.py`. He absorbed ALL scriptures,
  asked Q1–Q7, and got Nir's decisions (saved verbatim at
  `loom2/HINDU/PARENT-D-QA-BATCH-1-NIR-DECISIONS.md`).
- **⏭️ TOMORROW'S FIRST ACTION:** Nir re-opens the SAME Parent D chat and writes just
  **"continue"** (no re-paste — Fable holds the design in context). Fable delivers
  terrain.py + terrain.vert/.frag + numbered remarks, then totem.py. We stopped ~1 AM
  because the provider truncated Fable's replies twice (long-message choke). Nothing lost.
- **PARENT D LOCKED DECISIONS (all Nir's, couriered by DeepSeek):**
  A1 arm = `90°−measure_phase×360°` (clockwise; matches helix_panel:253).
  A2 **HARD** discrete color bands (crisp edges = level curves), not smooth.
  A3 **GOURAUD** shading (per-vertex), not flat.
  A4 **NO water plane** — below z=0 is the SAME mesh in hard BLUE bands darkening with
     depth (COLOR_SHALLOW→COLOR_DEEP_WATER); a calculus surface, not a sea; no water VBO.
  A5 LEFT terrain rings are **calm/static — NO pulsing**; draw only rings inside hearing
     radius (0.8/1.6/2.4 at default HEARING_R=2.5).
  A6 ALL totem parts **glow GENTLY** but stay readable (helix ≠ blinding white cylinder).
  A7 **DRAPED** ground rings (hug the surface, never flat/floating/clipping). 🔓 **Nir
     EXPLICITLY blesses unfreezing contracts / amending scripture** to do it cleanly —
     Fable raises a `# CONTRACT-ISSUE`, DeepSeek updates scripture + wires his choice.
- **⚠️ TWO CLEANUP TODOs (with Nir's OK, NOT done yet):** (1) delete the DeepSeek OPINION
  in `HAND-OFF-PROMPT-FROM-FABLE-PARENT-C.md` §5 (~L154–155: "…reads well; …is fine too.")
  — info blocks must be FACTS ONLY. (2) LOCKED LESSON: DeepSeek gives VERIFIED FACTS ONLY;
  every taste choice goes to NIR; DeepSeek never decides aesthetics. (Tonight DeepSeek
  wrongly said "flat shading" in chat — Nir wants GOURAUD; caught, never saved.)
- **After D:** Parent E (slice_mode), Parent F (hud + input_map), Parent G (surfaces +
  scene + main), then DeepSeek stitches deferred seams + content.

### 🔖 PRIOR SNAPSHOT (July 7, 2026, evening) — quick orientation
- **Progress:** Parents **A, B, C COMPLETE** → entire **audio package** (quantize, musicians,
  sampler, render_offline, engine) + **graphics camera.py & renderer.py** + **all 8 shader
  stems** delivered, extracted, py_compile-clean, pushed. config.py, core/types.py, 89-sample
  orchestra, core/game_state.py, graphics/helix_panel.py all done. Whole scripture canon +
  every hand-off letter saved verbatim.
- **⏭️ IMMEDIATE NEXT STEP = launch PARENT D** (`graphics/terrain.py` + `graphics/totem.py`).
  Launch doc READY = `HAND-OFF-PROMPT-FROM-FABLE-PARENT-C.md` (Parent C letter + DeepSeek info
  block at end). Paste it to a fresh Fable chat, then feed scriptures (Homepage+About →
  MAHABHARATA → VEDAS → UPANISHADS → SUTRAS → GITA 1-4; PURANAS declined). Give Nir blob links.
- **After D:** Parent E (slice_mode), Parent F (hud + input_map), Parent G (surfaces + scene +
  main), then DeepSeek stitches deferred seams + content.
- **DeepSeek TODO ledger:** ffmpeg-in-EXE (or swap sampler `_decode_mono`); render_offline live
  trial (after Parent G's surfaces.py); renderer GL smoke test (after a pyglet window);
  joystick/Xbox (after Parent F); render_equations (content phase); PyInstaller (ship phase).
- **When a parent replies:** save verbatim to `loom2/HINDU/` → extract code to package path →
  `py_compile` (+ any self-test) → update WORKFLOW + this BHASHYA → commit + push → blob links.
  Parents are smarter coders than DeepSeek; give info framed as info, never orders.

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
- ✅ **PARENT A COMPLETE (July 7, 2026)** — chunk = `audio/quantize.py` + `audio/musicians.py` (the pure-math Sonifiquation core). Both delivered by Fable Parent A, saved verbatim in HINDU/ (`LOOM2-PARENT-A-PART-1-QUANTIZE-BY-FABLE.md`, `LOOM2-PARENT-A-PART-2-MUSICIANS-BY-FABLE.md`) + extracted to code; **self-tests PASS** (`python -m audio.quantize` → 89 notes round-trip clean; `python -m audio.musicians` → 21 musicians seated, deterministic). Parent A's angle-convention bind check verified consistent across musicians/helix_panel/engine (all +x=0°, +y=90° CCW). His hand-off letter to Parent B saved verbatim at `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-A.md`.
- ✅ **DeepSeek seams done (July 7):** `config.py` + `core/types.py` extracted verbatim from Gita Part 1; **path reconciliation** — the 89-sample library + manifest.json + coverage_report.txt MOVED to `loom2/data/samples/` to match frozen `config.SAMPLES_DIR` (build recipe OUT_DIR updated); all 5 mp3 decoders (audioread, pydub, soundfile, librosa, scipy) installed + verified to decode the real samples.
- ⏭️ **CURRENT NEXT STEP = launch PARENT B** — chunk = `audio/sampler.py` + `audio/render_offline.py`. Launch document = `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-A.md` (Parent A's verbatim hand-off letter + a **DeepSeek information block appended at the END, marked "BY DEEPSEEK (NOT FABLE)"** = verified seam quotes, manifest schema, installed decoders, config constants — pure information, no suggestions/steering; Nir pastes the whole file to a fresh Fable chat). When Parent B replies: DeepSeek saves verbatim → extracts code → py_compile → update memory → commit/push → blob links. Parent's open questions reach DeepSeek via **Nir as courier**, in batches; parent may split long files and DeepSeek concatenates.
- ⚠️ **CONTEXT-WINDOW MERCY (POLICY — TRUE FOR EVERY PARENT, don't make Nir repeat it):** give a newborn worker-parent ONLY what he needs, never the whole prior canon (that is why Parent A survived "before he began"). In the DeepSeek info block at the end of each launch doc, name the big files we are NOT pasting in full (e.g. the 3 PURANAS = 444 + 417 + 335 lines of code) and tell him: ask DeepSeek through Nir for specific parts (verbatim) or send batched questions. BUT it is the parent's call each time — if he DOES want the whole code of something, Nir of course pastes it; he may spend his context window (memory of the conversation's start) if he judges it worth it. He does not truly "die" — we keep talking to the same Claude Fable in the next chat as **Parent N+1**. :-)
- ✅ **PARENT B COMPLETE (July 7, 2026)** — chunk = `audio/sampler.py` + `audio/render_offline.py`. Both delivered by Fable Parent B, saved verbatim (`LOOM2-PARENT-B-PART-1-SAMPLER-BY-FABLE.md`, `LOOM2-PARENT-B-PART-2-RENDER-OFFLINE-BY-FABLE.md`) + extracted (py_compile OK). `python -m audio.sampler` gauntlet PASSES (89 canon, peak/resample laws, parachute). Decoder = **pydub + ffmpeg** (verified present). `render_offline.py` is contract-clean; **live CLI trial is BLOCKED on Parent G's `core/surfaces.py`** (not yet written), so it will be trial-run once Parent G lands. **DeepSeek BLESSED Parent B's CONTRACT-NOTE** (render_option had no scene domain in its frozen signature; resolved additively: default = integer-cornered window around the hearing circle, plus optional per-option `domain`/`step`/`z_per_octave` keys in options.json — nothing frozen changed; content authors should include `domain` when a quiz spot sits near a scene edge). ⚠️ DeepSeek standing TODO: sampler ships in EXE → PyInstaller must bundle ffmpeg (or swap `_decode_mono`).
- ✅ **PARENT C COMPLETE (July 7, 2026)** — chunk = `graphics/camera.py` + `graphics/renderer.py`. Both delivered by Fable Parent C, saved verbatim (`LOOM2-PARENT-C-PART-1-CAMERA-BY-FABLE.md`, `LOOM2-PARENT-C-PART-2-RENDERER-BY-FABLE.md`) + extracted (py_compile OK). **camera.py** behavior-tested: default (az 0/el 35/zoom 1), 4x4 float32 VP, elevation clamps [5,85], zoom clamps [0.5,2.5], reset, and the **clock/pan seam verified** (world +y "brass" → screen-up = 12 o'clock at az 0). **📐 camera_limits DE-FACTO CONTRACT (locked by Parent C, first consumer — Parent G's `scene.py` validation + all scene.json must conform):** keys = `"target"` (3-list, default [0,0,0]), `"zoom_min"` (0.5), `"zoom_max"` (2.5), `"distance"` (OPTIONAL, default 14.0). Matrix: column vectors, clip = VP@p, uploaded transposed (matches helix_panel). Zoom factor>1 = zoom in; **confirmed consistent with game_state**. Helix uses FIXED distance (~16.1, bounding-sphere, elevation-proof); zoom applies to terrain only; the "one-sign spot" for mirrored-surround is `_eye_offset()`. **renderer.py**: public `self.ctx` (moderngl context), loads all 8 REQUIRED_SHADERS fail-loud, two HDR (RGBA16F 'f2') panel FBOs at (WINDOW_W//2, WINDOW_H*PANELS_FRAC) — 50/50 split enforced here only; bloom ping-pong (extract→downsample ¼ via `_BLOOM_DOWNSCALE=4`→blur H→blur V→composite) — **uniform names match** DeepSeek's shaders (extract u_tex/u_threshold; blur u_tex/u_dir; composite u_scene/u_bloom/u_strength/u_exposure); composite() clears whole screen black (strip + quiz bar stay black for hud), blits panels at y0=QUIZ_BAR_FRAC*H=144; begin_panel enables depth+alpha-blend by default. **Live GL smoke test DEFERRED to integration** (moderngl.create_context needs a live pyglet window / Parent G's main.py). No CONTRACT-ISSUEs.
- ✅ **PARENT D COMPLETE (July 8, 2026)** — chunk = `graphics/terrain.py` + `graphics/totem.py`. Both delivered by Fable Parent D, saved verbatim (`LOOM2-PARENT-D-PART-1-TERRAIN-BY-FABLE.md`, `LOOM2-PARENT-D-PART-2-TOTEM-BY-FABLE.md`) + extracted (py_compile OK) + real terrain GLSL overwrote the placeholders. **terrain.py:** A2 HARD per-fragment bands × A3 GOURAUD per-vertex Lambert simultaneously; A4 no water plane (blue bands darken with depth on same mesh). Canon shader IF: vert `mat4 u_mvp; vec3 in_pos; float in_light;` / frag `vec3 u_band_colors[6]; float u_band_edges[5];`. Band edges (−1.5,−0.6,0,1.1,2.2) abs world z; darkest abyss `COLOR_DEEP_WATER×0.55`; land ≤1.0 except snowcaps ≈0.82–0.84 (Nir KEEPS the faint bloom). `height_at`=pure passthrough (numpy-capable); flagged `release()`. **totem.py:** breathing warm-gold ribbon helix on shared `flat` program (`u_mvp`/`u_color`/`in_pos`, verified vs flat.{vert,frag}), dark edge lines keep it readable (A6); DRAPED rings/circle/arm via `height_fn` (Amendment #2 — `draw(self, view_proj, totem_state, height_fn, measure_phase)`); breath clock unwraps measure_phase (no `time` import, ~3 s breath never locks to 2 s measure); A1 arm `90°−phase×360°`; A5 calm static rings n=1..min(NMAX_RING,⌊hr/RING_WIDTH⌋). **DeepSeek OWES: wire main to pass `terrain.height_at` into `TotemVisual.draw`** (at Parent G). **✅ GOURAUD HELIX (iron rule honored):** first totem shipped flat; Parent D **redelivered GOURAUD (July 8)** via a NEW 9th shader stem "totem" (`data/shaders/totem.vert/.frag`) — `flat` draws only LINES; `REQUIRED_SHADERS` 8→9; saved verbatim (`LOOM2-PARENT-D-PART-2-TOTEM-GOURAUD-REDELIVERY-BY-FABLE.md`), py_compile OK, ACTUAL scriptures amended (G3.1-A + G3.4-A).
- ⏭️ **CURRENT NEXT STEP = launch PARENT E** — chunk = `graphics/slice_mode.py` ("The Glass Blade" 🔪). (Flat-helix blocker RESOLVED July 8 — Gouraud redelivered.) Build a launch doc (Parent D hand-off letter + FACTS-ONLY DeepSeek info block, marked NOT Fable), paste to a fresh Fable chat, feed scriptures in order, give Nir blob links. Keep `game_state._build_slice_path` in sync with `GlassBlade.intersection_path` (G3.6).
- ⏳ Then: Parents C–G write the rest; DeepSeek binds the remaining seams (shaders bloom/composite; joystick/Xbox; render_equations; PyInstaller — all mostly blocked until the relevant parent writes its module).
- ⏳ Then: content — the 12 scenes' JSON + hints + wrong-answer explanations (Fable drafts, Nir approves by taste), render option WAVs + equation PNGs; ship; add the subject to the website.
