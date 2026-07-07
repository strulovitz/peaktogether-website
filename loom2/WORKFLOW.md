# LOOM2 — PROJECT WORKFLOW & MEMORY (for DeepSeek / OpenCode)

> ⭐ **ON RESTART, READ THIS FIRST.** LOOM2 is the reboot of the sonification game.
> LOOM (v1, folder `loom/`) is **deprecated but kept** — do NOT build on it; its
> design flattened the book into a 1D pitch melody. LOOM2 restores the true vision
> of Nir's book *Sounding the Unknown* (the Helical Sonification System, HSS).
>
> Scripture lives in `loom2/HINDU/` (Hindu-themed names, Nir's choice, "to amuse
> himself"). Save every Fable output **VERBATIM**. Commit + push after each step.
> Give Nir GitHub **blob (view)** links. Emojis + warmth always. He is "Nir".

---

## 0. WHAT LOOM2 IS (in one breath)

A two-player, one-screen game where players **hear multivariable calculus**. A
mathematical surface z = f(x, y) becomes music via the **Helical Sonification
System (HSS)**. The core invention (the UPANISHADS/MAHABHARATA breakthrough): **a
surface is not a melody — it is an ORCHESTRA.** You plant a **Listening Totem** in
the landscape; every "musician" seated on the grid inside its hearing circle plays
at once, so you hear a whole *neighborhood* as one chord/groove — never a 1D siren
sweep. Moving the totem re-orchestrates the whole song.

The HSS mapping (Nir's true vision, restored):
- **height z → pitch** (A4 = 440 Hz at z = 0; the helix is centered on the origin,
  so valleys sound BELOW the reference — negative numbers are first-class).
- **angle θ → timbre** (the orchestra circle: brass at 12 o'clock, strings at 4,
  woodwinds at 8; continuous Fourier-recipe morph between families).
- **radius r → rhythm** (concentric rings: ring n = n pulses per measure; the axis
  = one calm sustained tone; fractional radius crossfades adjacent rings).

Peak Together lineage (each game teaches a foundational topic as a '90s co-op
remake): Descent QED (Basel), Quake: Principia (Calculus), Homeworld: A Good Basis
(Linear Algebra), **LOOM2 (Multivariable Calculus)**.

---

## 1. THE SCRIPTURE (`loom2/HINDU/`, all by Claude Fable, saved VERBATIM)

- **`LOOM2-VEDAS-BY-FABLE.md`** — the foundational vision (identity, the mountain =
  multivariable calculus, the HSS three-coordinate system, players, spells, screen,
  tech, what-it-is-NOT, open questions).
- **`LOOM2-MAHABHARATA-BY-FABLE.md`** — the breakthrough: *a surface is an
  orchestra*; the **Listening Totem**; why it teaches the math (level curves =
  unison; critical points = chord quality; gradient = transposition); feasibility
  guardrails. *(Originally saved as "UPANISHADS", renamed at Nir's request —
  "UPANISHADS" is reserved for a later document Fable will give.)*
- **`LOOM2-RAMAYANA-BY-FABLE.md`** — the **Listening Prototype** ("The Listening
  Totem"): the complete one-file ear-test program + how to run it + tomorrow's
  ear checklist. The code is also extracted to a runnable file (see §3).
- **`LOOM2-SUTRAS-BY-FABLE.md`** — the **consolidated Amendments I & II** (v1.0,
  July 7, 2026). Supersedes UPANISHADS §2/§3 and the ±3-octave rule. Locks: the
  **full 13-instrument orchestra** each played by its real register members (strings
  = double bass/cello/viola/violin; woodwinds = contrabassoon/bassoon/clarinet/oboe/
  flute; brass = tuba/trombone/french horn/trumpet); the **full ~6-octave orchestral
  range** (never resample across registers); the **50/50 "Sonifiquation" screen**
  (Cartesian left, Sonifiquation-coordinates helix right); camera orbit = surround
  panning (rotating changes your *seat*, not the song); instrument-icon billboards in
  the helix; **Slice Mode "the Glass Blade"** 🔪; pre-rendered quiz-option WAVs; and
  **Part Ten = the DEEPSEEK TASK** to build the sample library (DONE — see §3).
- **`LOOM2-BHAGAVAD-GITA-PART-1..4-BY-FABLE.md`** — the **modular architecture &
  frozen contracts** (v1.0, July 7, 2026), 4 parts:
  - **Part 1** — Foundation & Map: the Laws of the Gita (children fill bodies only;
    signatures/constants frozen), the full project tree, and the COMPLETE `config.py`
    (all frozen constants incl. the 89-sample REGISTER_MAP baked in as canon) +
    `core/types.py` (Voice, SceneSpec, CameraState, Mode/Action enums — the vocabulary
    of every seam).
  - **Part 2** — Audio contracts: `audio/{quantize,sampler,musicians,engine,
    render_offline}.py` (empty-body skeletons). Seam = 4 calls (build_voices →
    set_voices; set_camera_azimuth; get_measure_phase; get_active_flashes).
  - **Part 3** — Graphics contracts: `graphics/{renderer,camera,terrain,totem,
    helix_panel,slice_mode,hud}.py`. One shared OrbitCamera drives both panels.
  - **Part 4** — Core & main contracts: `core/{surfaces,scene,game_state,input_map}.py`
    + `main.py` (frozen boot & frame order). Ends with the **child-chat assignment
    plan** (see §6) and what DeepSeek owes (folders, __init__.py, shaders, joystick/
    xbox fill-in, scene JSON, PyInstaller).

- **`LOOM2-PURANAS-PART-1-AUDIO-ENGINE-BY-FABLE.md`** — **PART 1 of 3 of the PURANAS**
  (Fable "Parent 2", July 7, 2026): the KING module `audio/engine.py`, delivered
  complete + saved verbatim. The runnable code is also extracted to
  `loom2/audio/engine.py` (syntax-verified via py_compile). Keystone trick: since
  MEASURE_SAMPLES = 88200 divides exactly by every ring 1..5, all pulse positions are a
  pure function of the global sample counter — so voice continuity, shared downbeats,
  and byte-identical offline rendering all fall out of one design (ONE mixer `_mix`, two
  callers: `_callback` + `render_block_offline`). Implements the approved amendment (see
  below). ✅ Done.
- **`LOOM2-PURANAS-PART-2-GAME-STATE-BY-FABLE.md`** — **PART 2 of 3 of the PURANAS**
  (Fable "Parent 2", July 7, 2026): `core/game_state.py`, THE CONDUCTOR OF EVERYTHING
  (mode state machine EXPLORE/QUIZ_LISTEN/SLICE/SCENE_TRANSITION, totem motion, quiz
  flow, slice auto-walk). Delivered complete + saved verbatim; runnable code extracted
  to `loom2/core/game_state.py` (py_compile OK). Key design calls: the **intent
  pattern** (handle_action records, update enacts smooth analog motion); the **quiz
  exit gesture = TOUCH THE TOTEM** (Fable's one open design choice — Nir may veto by
  taste); slice walk = one `RING_WIDTH` stop per measure (a procession, never a siren);
  `_build_slice_path` must stay literally in sync with `GlassBlade.intersection_path`
  (G3.6). Next: **Part 3 = `graphics/helix_panel.py`** (say "continue" to Fable).
- **`LOOM2-PURANAS-PART-3-HELIX-PANEL-BY-FABLE.md`** — **PART 3 of 3 of the PURANAS**
  (Fable "Parent 2", July 7, 2026): `graphics/helix_panel.py`, THE SONIFIQUATION
  COORDINATES panel (the soul on screen — wireframe coil B0..C7, instrument-icon
  billboards at cylindrical (r,θ,z) with perspective scaling, register stacks, strike
  glows feeding bloom, conductor's arm). Delivered complete + saved verbatim; runnable
  code extracted to `loom2/graphics/helix_panel.py` (py_compile OK). Fable also delivered
  **4 GLSL shaders** — placed in `loom2/data/shaders/` (`wire.vert`, `wire.frag`,
  `icon_billboard.vert`, `icon_billboard.frag`). **🏔️ THE PURANAS ARE COMPLETE — all
  three heavy modules delivered.** Fable's 3 soft seams to verify at stitch time:
  (1) `Renderer.ctx` should exist (else falls back to `moderngl.get_context()`);
  (2) matrix convention (assumes `clip = VP·p`, uploads transposed — flip if Child C's
  camera uses row-vectors); (3) optionally set `panel.z_per_octave = spec.z_per_octave`
  on scene change.

Naming: Fable's docs get Hindu scripture names. Lineage: **VEDAS → MAHABHARATA →
RAMAYANA → UPANISHADS → SUTRAS → BHAGAVAD GITA → PURANAS** (COMPLETE). The PURANAS
(the heavy modules — audio/engine.py ✅, core/game_state.py ✅, graphics/helix_panel.py ✅ —
written by a fresh Fable "Parent 2") were delivered ONE COMPLETE FILE PER ANSWER. 🏔️

Two **non-scripture** docs also live in `loom2/HINDU/` (hand-offs, not Fable canon):
- **`HAND-OFF-PROMPT-FROM-FABLE-PARENT-2.md`** — Fable Parent 2's letter to the next
  Fable, saved verbatim, PLUS **Nir's inserted bridge + Parent A's launch note folded in
  right after §5** (Parent 2 lost the plan to a full context window and mis-scoped the
  successor as a supervisor "Parent 3"; Nir's bridge overrides that and gives Parent A his
  real mission). **This whole file is the Parent A launch document** — Nir pastes it as the
  first message of the fresh Parent A chat, then feeds the scriptures. See §4.6 for the
  full story.

### ⚖️ CONTRACT AMENDMENT (approved by Nir, July 7, 2026)
The Gita's `game_state._quiz_select` (G4.3) must play the quiz option WAV "looping,
THROUGH THE ENGINE", but the frozen `AudioEngine` API had no method taking a WAV — a
missing wire. Nir arbitrated and **approved adding ONE method: `AudioEngine.set_quiz_wav(path)`**
(`path=None` stops, 30 ms fade). It loops the pre-rendered stereo WAV through the SAME
mix/soft-clip/pan path (routes sensibly under 5.1/7.1), mutually exclusive with live
voices by game_state's discipline. Nothing else in the contract changed. **Consequence:
the audio↔world seam is now 5 calls, not 4** (build_voices→set_voices; set_camera_azimuth;
**set_quiz_wav**; get_measure_phase; get_active_flashes).

---

## 2. LOCKED DECISIONS / NIR'S ANSWERS (July 6, 2026)

- **Tech stack (Nir overrides the VEDAS "no OpenGL"):** **use OpenGL** —
  **moderngl + pyglet** (the modern shader stack of Quake & Homeworld: moderngl
  5.12.0 / pyglet 2.1.14), NOT pure-software, NOT PyOpenGL (that was Descent's older
  flavor). **Audio is KING: real-time additive synthesis on numpy buffers via
  `sounddevice`** (PortAudio callback), fully independent of graphics. Rationale in
  full: pygame.mixer is a file-player, primitive for real-time synthesis; sounddevice
  is the correct tool; input→shared-state→audio is our own code, not a library
  feature; pyglet already handles all controllers (proven in Quake/Homeworld).
- **Reference note:** **A4 = 440 Hz at z = 0** (universal, mathematically clean:
  f(z) = 440·2^(z/z_oct); octaves = exact doublings). NOT middle C. **Pitch range:
  clamp to ±3 octaves** (~55–3520 Hz), soft-limit beyond.
- **Title = LOOM2** (no subtitle). **No mountain:** multivariable calculus is
  foundational bedrock shared beneath many mountains — present it as a foundational
  subject on the website, not a single peak.
- **Curriculum order:** (1) functions of two variables / surfaces → (2) level
  curves / contour maps → (3) partial derivatives → (4) directional derivatives &
  gradient → (5) critical points (max/min/saddle) → (6) second-derivative test →
  (7) optimization by ear. **Double integrals / volume DROPPED** (no good way to
  hear volume without cacophony — Nir agreed).
- **Spells (seed for plot):** each mastered concept grants a spell that reshapes /
  crosses the landscape (gradient spell points uphill; saddle spell opens a pass;
  optimization spell reveals the summit). Spell = both the ear-test AND the means of
  progressing. Full plot → the UPANISHADS.
- **Measure length / tempo:** **fixed 2.0 s per measure (120 BPM, four beats),
  constant during play.** Grounded in all three families (strings' slow attack
  stays clean at ≥0.33 s/pulse up to ~5–6 rings; the calm center = a 2.0 s whole
  note). The old LOOM "1.3 s" was a per-note *sample* length (Forge), never a
  measure — and LOOM2 synthesizes, so note length is uncapped. Optional global
  tempo slider for accessibility, but fixed within a level.
- **Guardrails (from the MAHABHARATA):** ~12–30 musicians in the hearing circle
  (not hundreds — the ear tops out); heights snap to **pentatonic** (chords stay
  beautiful); ≤ ~4 occupied rhythm rings at once; **build the Listening Prototype
  FIRST** and validate by ear before anything else.

---

## 3. CURRENT SITUATION (July 7, 2026)

- ✅ **PURANAS COMPLETE + Parent 2 retired:** all 3 heavy modules written by Fable
  "Parent 2", saved verbatim in `loom2/HINDU/` and extracted to real code
  (`loom2/audio/engine.py`, `loom2/core/game_state.py`, `loom2/graphics/helix_panel.py`,
  all py_compile-clean) + 4 GLSL shaders in `loom2/data/shaders/`.   His hand-off letter is
  saved. **NEXT STEP = launch Parent A** (see §4.6) by pasting
  `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-2.md` (Parent 2's letter + Nir's bridge +
  Parent A's note, folded together) to a fresh Fable chat.
- ✅ **LOOM2 folder created;** LOOM (v1) left intact but deprecated.
- ✅ **Scripture saved verbatim + pushed — THE WHOLE CANON IS DOWN:** VEDAS,
  MAHABHARATA, RAMAYANA, UPANISHADS, **SUTRAS**, and **BHAGAVAD GITA Parts 1–4**
  (architecture & frozen contracts). Next scripture = the **PURANAS** (heavy modules),
  still to come from a fresh Fable "Parent 2".
- ✅ **The Listening Prototype PASSED THE EAR TEST.** `sounddevice` installed
  (0.5.5, 2026-07-07). Nir ran `loom2/listening_totem.py` on headphones — the
  invention works: he can hear Bowl vs. Saddle, level curves, partials, negatives.
- ✅ **PHILHARMONIA EDITION built + pushed (July 7, 2026):**
  **`loom2/listening_totem_philharmonia.py`** — a copy of the prototype that swaps
  the synthesized wavetables for **real Philharmonia recordings** (Brass = trumpet,
  Strings = violin, Woodwinds = flute). Octave-accurate: each note is resampled to
  the EXACT target pitch (height→pitch preserved, negatives included); per-pulse
  retrigger of the real sample per rhythm ring; equal-ish family crossfade by angle;
  persistent per-musician playback across audio blocks; ~1.2% of the realtime CPU
  budget. **Nir's verdict: "it actually sounds like I'm creating MUSIC, not just
  sounds"** — this validated the sample-based orchestra Fable then locked into the
  UPANISHADS §2. Run: `python loom2/listening_totem_philharmonia.py`.
- ✅ **SAMPLE LIBRARY BUILT (SUTRAS Part Ten, DeepSeek, July 7, 2026):**
  `loom2/build_sample_library.py` scanned `Downloads\philharmonia` and produced
  the library = **89 pentatonic notes (A/B/Cs/E/Fs) across all 13 orchestra
  instruments**, in their real register bands. **86 exact, 3 resampled (≤±2 st:
  violin_A7←G7 +2, tuba_E1←F1 −1, trumpet_Fs5←F5 +1), 0 missing.** ~1.8 MB total.
  Plus `manifest.json` (per-note source/duration/dynamic/articulation/resample)
  + `coverage_report.txt`. Committed to git (Fable's ruling: 1.8 MB is nothing,
  players should hear music on clone; the build script stays as the reproducible
  recipe). These 89 notes are now CANON — baked into the Gita's `config.REGISTER_MAP`.
  **📍 LOCATION (reconciled July 7): now at `loom2/data/samples/` to match the FROZEN
  `config.SAMPLES_DIR="data/samples"` (moved via git mv; old `loom2/samples/` removed).**
- ✅ **SEAMS SCAFFOLDED (DeepSeek, July 7, 2026):** `loom2/config.py` + `loom2/core/types.py`
  extracted verbatim from Gita Part 1; **Parent A's `quantize.py` self-test now PASSES**
  (`python -m audio.quantize` → "all sanity checks passed -- 89 notes round-trip clean").
- 📋 **Orchestra roster finalized with Nir (for Fable), from the Philharmonia folders:**
  STRINGS = violin(high)/viola(med)/cello(low)/double bass(very low); WOODWINDS =
  flute(high)/oboe(med-high)/clarinet(med)/bass clarinet+bassoon(low)/contrabassoon
  (very low); BRASS = trumpet(high)/french horn+trombone(med)/tuba(low). Deliberately
  DROPPED (not orchestral / distracting): banjo, guitar, mandolin, saxophone, cor
  anglais, percussion. (The prototype uses violin+trumpet+flute — one per family.)

### 🎧 EAR TEST — PASSED (was the make-or-break of the whole invention)
The Listening Prototype checklist (Bowl vs Saddle, Ridge partials, Ramp transpose,
negative lake) all confirmed by Nir on headphones. The invention is real. ✅

---

## 4. WHAT'S STILL NEEDED (the road ahead)

1. ✅ **Ear test** — PASSED (synth + Philharmonia editions).
2. ✅ **UPANISHADS + SUTRAS + BHAGAVAD GITA (Parts 1–4)** — all landed, saved verbatim,
   pushed. Architecture & every module contract are now FROZEN.
3. ✅ **Sample library (SUTRAS Part Ten)** — DONE (89 notes, 13 instruments; see §3).
4. 🟡 **One OPEN item still awaiting Nir:** UPANISHADS scene 10 (Ocean Swell) format —
   keep the richer "match each groove" or flatten to plain A/B/C/D (Nir's call, zero
   cost either way).
5. ✅ **THE PURANAS — COMPLETE** 🏔️ (fresh Fable "Parent 2"): the three HEAVY modules,
   all verbatim in `loom2/HINDU/` + extracted to real code (py_compile OK): `audio/engine.py`,
   `core/game_state.py`, `graphics/helix_panel.py` (+ 4 GLSL shaders in `loom2/data/shaders/`).
   Parent 2's hand-off letter is saved verbatim at
   `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-2.md`.

6. 🧵 **THE WORKER-PARENTS PLAN — THE SITUATION & THE PLAN CHANGE (read this).**

   **What happened:** Parent 2's hand-off letter defined a single successor called
   "Parent 3" whose mission was **supervision + content** (arbitrate `# CONTRACT-ISSUE`
   escalations, review children's modules, write scene JSON / hints / explanations, tune
   constants). **But that letter did NOT assign the biggest remaining job at all** —
   actually WRITING the other ~14 modules the Gita (G4.6) had parked with "children A–G".
   It passively assumed those modules would just appear ("review children's modules if
   Nir pastes them"). Nir judged that Parent 2 lost the plan (context window) and that
   **one chat cannot do the work of 7 children.**

   **Nir's decision (the new plan):** drop the sandboxed-children model. Instead use a
   **sequence of full worker-PARENTS** — Parent A, B, C, … — each taking ONE former
   child's chunk **as a parent** (full context, full freedom, full authority), not as a
   walled-off child. "Parent 3" as Parent 2 imagined it is **retired/ignored**; the
   supervision + content work simply happens later, across these parents, or in a
   dedicated pass Nir chooses.

   **The chunks (former Gita G4.6 child assignments, now parent assignments):**
   - ✅ **Parent A** — `audio/quantize.py` + `audio/musicians.py`  ← **COMPLETE** (both
     files delivered, extracted, self-tests pass, pushed; hand-off letter saved)
   - 🟡 **Parent B** — `audio/sampler.py` ✅ **DONE** (delivered, extracted to
     `loom2/audio/sampler.py`, py_compile OK, `python -m audio.sampler` gauntlet PASSES —
     "89 canon samples loaded, resample law verified, parachute armed"; saved verbatim to
     `loom2/HINDU/LOOM2-PARENT-B-PART-1-SAMPLER-BY-FABLE.md`). Decoder = **pydub + ffmpeg**
     (both verified present). ⏭️ **NEXT: say "continue" to Parent B for `audio/render_offline.py`**
     (Part 2 of 2). ⚠️ Standing DeepSeek TODO: sampler.py ships in the EXE → PyInstaller must
     bundle ffmpeg (or swap `_decode_mono`) at packaging time.
   - Parent C — `graphics/renderer.py` + `graphics/camera.py`
   - Parent D — `graphics/terrain.py` + `graphics/totem.py`
   - Parent E — `graphics/slice_mode.py`
   - Parent F — `graphics/hud.py` + `core/input_map.py`
   - Parent G — `core/surfaces.py` + `core/scene.py` + `main.py`

   **How Nir runs a worker-parent (the culture he set — DO NOT micromanage them):**
   - The launch document for Parent B is `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-A.md`
     — Parent A's verbatim hand-off letter with a **DeepSeek information block appended at
     the END, clearly marked "BY DEEPSEEK (NOT FABLE)"** (verified seam quotes, manifest
     schema, installed decoders, config constants — pure information, no suggestions). It
     gives the parent its chunk + the relevant specs DeepSeek gathered — framed as
     INFORMATION, never orders. (Each future parent gets its own analogous hand-off +
     DeepSeek info block. The pattern started with Parent A, whose launch doc was
     `HAND-OFF-PROMPT-FROM-FABLE-PARENT-2.md` = Parent 2's letter + Nir's bridge + note.)
   - The parent is told (explicitly, by Nir): **you are much smarter than DeepSeek, the
     best coder in the world; trust your own judgement and previous Fable sessions; take
     DeepSeek's info with a grain of salt.**
   - The parent's **open questions go to DeepSeek**, with **Nir as courier** (copy-paste
     both ways). Questions may come **in batches**.
   - **Delivery:** if a file is too long, the parent splits it into parts and **DeepSeek
     concatenates/combines** them per the parent's instructions (NOT forced "one file per
     answer").
   - **⚠️ CONTEXT-WINDOW MERCY — GIVE A PARENT ONLY WHAT HE NEEDS (EVERY TIME).** Do NOT
     dump the whole prior canon on a newborn parent. In the DeepSeek info block at the end
     of each parent's launch doc, list the big files we are deliberately NOT pasting in full
     (e.g. the three PURANAS = 444 + 417 + 335 lines of code) and say: if he wants specific
     parts he asks DeepSeek through Nir, and we copy-paste them verbatim or answer batched
     questions. AND make clear: if he DOES want the whole code of something, of course Nir
     will paste it — **it is the parent's call each time.** He may sacrifice his context
     window (his memory of the start of the conversation) if he decides to; that is OK,
     sometimes he really needs the exact full code. It is not like he truly "dies" — we keep
     talking to the same Claude Fable in the next chat as **Parent N+1**. This policy is
     TRUE FOR EVERY PARENT — do not make Nir repeat it. (This is why Parent A worked: he was
     given only what he needed and did not "die before he began".)
   - When a parent delivers: DeepSeek saves verbatim to `loom2/HINDU/`, extracts the real
     code to its package path, `py_compile`s, updates memory, commits + pushes, gives blob
     links — exactly as done for the PURANAS.
7. 🔧 **WHAT DEEPSEEK OWES (the seams, per the Gita):** ✅ folders + `__init__.py` (done);
   ✅ `config.py` + `core/types.py` verbatim from Gita Part 1 (done, July 7); ✅ **PATH
   RECONCILIATION done** — library MOVED to `loom2/data/samples/` to match FROZEN
   `config.SAMPLES_DIR="data/samples"` (89 mp3 + manifest.json + coverage_report.txt;
   `build_sample_library.py` OUT_DIR updated; old `loom2/samples/` removed). STILL owed
   (mostly blocked until the relevant parent writes its module): empty shader files
   (REQUIRED_SHADERS) + working bloom/composite GLSL from Quake/Homeworld (needs Parent C's
   `renderer.py`); joystick/Xbox slots (needs Parent F's `input_map.py`); `tools/render_equations.py`
   (LaTeX→PNG via MiKTeX, content-phase); scene JSON content (content-phase); PyInstaller EXE.
8. 🏗️ **Build stack:** `moderngl + pyglet + numpy + sounddevice` (+ Pillow, PyInstaller).
   Reuse Quake/Homeworld's software-3D + bloom + EXE recipe.
9. 🌐 **Website:** add multivariable calculus as a foundational subject (NOT a single
   mountain) once the game ships.

---

## 5. RESTART PROTOCOL

1. Read this file first, then `HINDU/BHASHYA_INDEX_AND_LOCKED_DECISIONS.md` (the BHASHYA
   now lives in the bible folder `loom2/HINDU/`, since it is commentary on the scriptures).
2. **Where we are:** the whole scripture canon is down; the PURANAS (3 heavy modules)
   are complete and in real code. **PARENT A is COMPLETE** (`audio/quantize.py` +
   `audio/musicians.py` — both delivered, extracted, self-tests PASS, pushed). **The
   current step is launching PARENT B** (`audio/sampler.py` + `audio/render_offline.py`);
   its launch document is `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-A.md` (Parent A's
   verbatim hand-off letter + a DeepSeek information block appended at the end, clearly
   marked NOT Fable — paste the whole file to a fresh Fable chat).
3. **Your job when a worker-parent replies** (Parent A, B, …): save the answer VERBATIM
   to `loom2/HINDU/`, extract the real code to its package path (`loom2/<pkg>/<file>.py`),
   `python -m py_compile` it, update this WORKFLOW + the BHASHYA, commit + push, give Nir
   GitHub blob links. If the parent split a file into parts, concatenate per its
   instructions.
4. **Culture (important):** worker-parents are treated as smarter coders than DeepSeek;
   do NOT micromanage them. Their open questions come to DeepSeek via **Nir as courier**
   (in batches). Give **information, framed as information, taken with a grain of salt** —
   never orders.
5. Read scripture in `loom2/HINDU/` as needed (VEDAS → MAHABHARATA → RAMAYANA →
   UPANISHADS → SUTRAS → BHAGAVAD GITA 1–4 → PURANAS 1–3). Sanity checks:
   `python -m py_compile loom2/listening_totem.py loom2/listening_totem_philharmonia.py`
   and `loom2/audio/engine.py loom2/core/game_state.py loom2/graphics/helix_panel.py`
   should all pass; also (run from inside `loom2/`) `python -m audio.quantize` and
   `python -m audio.musicians` self-tests pass; `sounddevice` (0.5.5) is installed. The
   89-file library is in `loom2/data/samples/` (path reconciled to match config.SAMPLES_DIR).
6. **The source book** *Sounding the Unknown* is at `loom/book/chapter_00.txt …
   chapter_10.txt` — the authoritative HSS reference (LOOM v1 lost its soul by
   planning from summaries; LOOM2 must stay grounded in the book + Nir's true helix
   in `loom/HELIX_AND_REBOOT_NIRS_TRUE_VISION.md`).
7. ⚠️ AGENTS.md still routes startup to older games AND still points at the BHASHYA's
   OLD path (`loom2\BHASHYA_INDEX_AND_LOCKED_DECISIONS.md`); the BHASHYA has MOVED to
   `loom2\HINDU\BHASHYA_INDEX_AND_LOCKED_DECISIONS.md` (it is commentary on the scriptures,
   so it belongs in the bible folder). LOOM2's authoritative memory is THIS file. Never
   modify AGENTS.md. Save Fable outputs VERBATIM; commit + push every meaningful step;
   GitHub blob links; emojis + warmth; he is "Nir".
