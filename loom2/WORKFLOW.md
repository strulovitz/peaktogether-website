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

### ⚖️ CONTRACT AMENDMENT #1 (approved by Nir, July 7, 2026)
The Gita's `game_state._quiz_select` (G4.3) must play the quiz option WAV "looping,
THROUGH THE ENGINE", but the frozen `AudioEngine` API had no method taking a WAV — a
missing wire. Nir arbitrated and **approved adding ONE method: `AudioEngine.set_quiz_wav(path)`**
(`path=None` stops, 30 ms fade). It loops the pre-rendered stereo WAV through the SAME
mix/soft-clip/pan path (routes sensibly under 5.1/7.1), mutually exclusive with live
voices by game_state's discipline. Nothing else in the contract changed. **Consequence:
the audio↔world seam is now 5 calls, not 4** (build_voices→set_voices; set_camera_azimuth;
**set_quiz_wav**; get_measure_phase; get_active_flashes).

### ⚖️ CONTRACT AMENDMENT #2 — G3.4 TotemVisual.draw (approved by Nir, July 8, 2026)
Nir's decision A7 requires **DRAPED** ground rings (hearing circle + rhythm rings hug the
terrain, following every bump/dip — never flat/floating/clipping disks). The frozen
`TotemVisual.draw(self, view_proj, totem_state, ground_z: float, measure_phase)` passes only
a scalar `ground_z` — not enough to sample terrain height all around each ring. Nir gave
explicit blessing to unfreeze the contract. **THE CHANGE (one param swap, no new seams):**
`ground_z: float` → `height_fn` (a callable `z = height_fn(x, y)`; `main` passes
`terrain.height_at`, which is a numpy-capable pure passthrough, so the totem drapes every ring
point efficiently). Fable "Parent D" writes `totem.py` against this NEW signature. **DeepSeek
owes:** wire `main` to pass `terrain.height_at` into `TotemVisual.draw`. The Gita Part 3
scripture file stays VERBATIM/pristine — this amendment is the new canon (same discipline as
Amendment #1). Locked with it: **A1 arm = `90° − measure_phase×360°`** (clockwise from above,
matching helix_panel.py:253), superseding the "measure_phase*360" wording in the verbatim G3.4
docstring. **SNOW-BLOOM DECISION (Nir, July 8): KEEP the faint snowcap shimmer** — peak pixels
at ≈0.82–0.84 gently exceed the 0.80 bloom bright-pass; terrain stays exactly as delivered (no
matte rescale).

---

## 2. LOCKED DECISIONS / NIR'S ANSWERS (July 6, 2026)

- **🏗️ PARENT G IN FLIGHT — MODULE 1/3 `core/surfaces.py` LANDED (July 8).** The last parent is
  building his three files, one per answer. DeepSeek answered his 12-question batch from the live repo
  (verified facts) + relayed Nir's two calls: window caption = **"LOOM2 — Sonifiquation"** (no emoji);
  cannon_range `k` delegated to Parent G as a coding/visual-fit decision (Nir: fit the whole parabola/
  battlefield on screen — NOT a taste call). Parent G delivered `core/surfaces.py` (all 9 surfaces +
  REGISTRY + `get()`), saved verbatim (`LOOM2-PARENT-G-PART-1-SURFACES-BY-FABLE.md`) + extracted.
  **His self-test `python -m core.surfaces` PASSES** (15 value checks + 9 surfaces × 4 shape mixes +
  registry error msg); py_compile OK. He baked `K_CANNON = 0.03` (domain v∈[0,10], θ∈[0,90°] → peak
  z=+3.0) as a named constant with full reasoning. Boot decisions he locked: resizable=False, strict
  validation, boot sanity print. No `# CONTRACT-ISSUE`.
  **MODULE 2/3 `core/scene.py` LANDED (July 8):** saved verbatim
  (`LOOM2-PARENT-G-PART-2-SCENE-BY-FABLE.md`) + extracted; **self-test `python -m core.scene` PASSES**
  (loads real campaign.json + test_saddle, all validators green), py_compile OK. THE DOOR = STRICT
  (Nir's option-a): all 13 fields required; camera_limits keys the only defaultable spot (G3.2-A/Q5
  option b); unknown keys rejected at all 3 levels except G2.5-A per-option extras (tolerated, not
  stored); `SceneError(ValueError)`; UTF-8; 0-byte + 2M-vertex freeze guards; exactly-4-options/
  1-correct. No `# CONTRACT-ISSUE`. ⏭️ NEXT & FINAL: Parent G module 3 = `main.py` (the heartbeat).
  **🏁 MODULE 3/3 `main.py` LANDED — PARENT G COMPLETE, THE GAME IS ASSEMBLED (July 8):** saved
  verbatim (`LOOM2-PARENT-G-PART-3-MAIN-BY-FABLE.md`) + extracted to `loom2/main.py`. Both self-tests
  still PASS; `main.py` py_compiles; **`python -c "import main"` resolves EVERY module** (full wiring
  import-clean). THIN main = build()/frame()/main() with the frozen boot + frame orders and all amended
  calls (G3.2-A hasattr set_limits, G3.3-A release, G3.4-A height_fn, G3.6-A set_domain; manual loop
  dispatch_events/frame/flip vsync-paced + MAX_DT clamp; try/finally engine.stop-first-then-close). ONE
  benign `# CONTRACT-ISSUE` (flagged): `import time` for perf_counter (Q7 loop needs it). ⏭️ REMAINING =
  DeepSeek stitching (OrbitCamera.set_limits; joystick/Xbox; **live `python main.py` GL run**;
  render_offline live trial; PyInstaller+ffmpeg) + content (12 scenes JSON/hints/equation PNGs/quiz WAVs).

- **🗣️❌ RETRACTION + IRON BEHAVIOR RULE (Nir, July 8) — NEVER PUT WORDS IN NIR'S MOUTH; NEVER
  STRIP HIM OF A CHOICE.** DeepSeek's `COURIER-TO-PARENT-F-ROUND-2.md` had written "Nir does NOT
  want more decisions ... just DO IT" under a header falsely labeled **"NIR'S MESSAGE TO YOU"** —
  DeepSeek's OWN words, NOT Nir's. Parent F then canonized it in the Parent G hand-off letter §3 as a
  "direct ruling." Nir was rightly furious (his analogy: saying "no thanks, I already ate" once does
  not mean you never deserve to eat again). **FIXED July 8:** both files corrected in place (original
  wording quoted inside a `[CORRECTED …]` bracket + retracted); logged in the BHASHYA. **TWO NEW HARD
  RULES in AGENTS.md:** (1) never write anything under a "Nir says/message/ruling/decided" label unless
  it is Nir's LITERAL words — DeepSeek's wording is labeled as DeepSeek's; (2) ALWAYS bring genuine
  design/taste/aesthetic decisions to Nir (his role, his joy) — batch questions to respect his time,
  but never turn "batch your questions" into "stop asking." Declining one menu once ≠ forfeiting all
  future choices.

- **🚫🔒 IRON RULE — NO FLAT SHADING, EVER. GOURAUD EVERYWHERE (Nir, absolute).**
  Every 3D surface/model in LOOM2 — terrain, the helix totem, the wireframe helix panel,
  ANY future geometry — is **GOURAUD shaded** (smoothly interpolated per-vertex lighting).
  Flat shading is FORBIDDEN in all of Nir's games. This is NOT a taste choice a parent may
  make, propose, "park," or default to for convenience — it is a hard, pre-decided
  requirement. If a frozen contract or shader stands in the way, **amend the contract** to
  make it Gouraud; do NOT ship flat. Any module that renders geometry flat is a BUG to fix,
  never an acceptable delivery. (History: Parent D's `totem.py` shipped a flat-colored helix
  and DeepSeek wrongly "parked" it — corrected July 8; totem is being made Gouraud.)

- **📜🔧 POLICY — AMEND THE ACTUAL SCRIPTURES, NOT JUST THE BHASHYA (Nir, July 8).**
  When a Fable parent says to change/correct/add/remove anything from the frozen
  scriptures (the VEDAS…GITA…PURANAS files in `loom2/HINDU/`), DeepSeek MUST insert a
  clearly-enclosed amendment block **in the actual scripture file**, at the end of the
  relevant paragraph/section — NOT only here or in the BHASHYA (nobody reads those but
  DeepSeek; future parents read the scriptures). Format: a block fenced by
  `<<<<<<<<<< AMENDMENT <id> — added <date> >>>>>>>>>>` … `<<<<<<<<<< END AMENDMENT <id> >>>>>>>>>>`,
  stating WHAT changed, WHY, WHO ORDERED it (always Nir) and WHICH PARENT requested it,
  and STATUS. Never silently rewrite a parent's original words — leave them intact and
  append the amendment block right after. (Applied July 8 to Gita Part 2 [G2.4-A quiz WAV,
  G2.5-A render_option domain, G2.SEAM-A 5-call seam] and Part 3 [G3.1-A 9th "totem" shader,
  G3.2-A camera_limits, G3.3-A Gouraud/hard-bands/no-water terrain, G3.4-A draped rings +
  Gouraud helix + arm direction].)

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

### 🔖 RESTART SNAPSHOT — READ THIS FIRST (updated July 8, 2026)

**🏁 CURRENT STATE (July 8, 2026, late) — READY TO START PARENT G, THE LAST PARENT 🏁**

Parents **A, B, C, D, E, F are ALL COMPLETE**. The whole audio package, all graphics
(camera / renderer / terrain / totem / helix_panel / slice_mode / **hud**), all core
(game_state / slicing / **input_map**), every shader, config, core/types, the 89-sample
orchestra, the **13 instrument icons** (`data/icons/`), and a **test scene**
(`data/scenes/test_saddle/`) are in place, py_compile-clean, and pushed. **Only ONE parent
remains — Parent G** = `core/surfaces.py` + `core/scene.py` + `main.py` (the pieces that make
the game actually RUN).

**THIS SESSION did (newest last):**
- **Layout + HUD overhaul (Nir):** screen = 80% graphics (576 px) / 20% quiz (144 px), NO text
  strip; scenario text painted OVER the graphics, white glyphs with a baked BLACK outline; **HUD
  render tech = Homeworld-style moderngl 2D overlay, NOT pyglet.** `config.py` edited
  (`PANELS_FRAC` 0.72→0.80, `TOP_STRIP_FRAC`→0.0, + a `HUD_*` constants block). Scriptures
  amended: **SUTRAS-2-A**, **Gita G3.7-A**, **Gita1-SCREEN-A**.
- **Nir made + delivered the 13 instrument icons** (128×128 RGBA transparent) → `data/icons/`.
- Equation = a math PNG rendered **yellow + black outline**, centered on the panel seam at the
  BOTTOM of the graphics. Panel titles 14 px bottom L/R. Wrong = bright pink, hint = bright green,
  **YOU WIN!!! = light blue (120,205,255)** blinking. Emojis allowed in HUD text (baked from
  Windows Segoe UI Emoji). Arrow signs locked (RIGHT→ORBIT_AZ +1, UP→ORBIT_EL +1).
- **Parent F COMPLETE** (`graphics/hud.py` + `core/input_map.py`): delivered first as a one-shot,
  then (Nir's request) **REDELIVERED one module per answer, deeper + more beautiful**. Both saved
  verbatim + extracted + py_compile OK. Canonical verbatim files:
  `LOOM2-PARENT-F-HUD-REDELIVERY-BY-FABLE.md` + `LOOM2-PARENT-F-INPUT-MAP-REDELIVERY-BY-FABLE.md`
  (these SUPERSEDE the one-shot `LOOM2-PARENT-F-HUD-INPUT-BY-FABLE.md`).
- Prepared **`MATERIAL-FOR-PARENT-G-HANDOFF.md`** — Parent G's verbatim Gita mission
  (G4.6 assignment + G4.1 surfaces.py + G4.2 scene.py + G4.5 main.py) + the list of whole Gita
  files he needs (Parts 1–4 amended) + verbatim PURANAS public-API excerpts (engine / game_state /
  helix_panel signatures + docstrings + the two game_state return dicts; bodies omitted).
- **Parent F's hand-off letter to Parent G** → ✅ **SAVED VERBATIM** as
  `HAND-OFF-PROMPT-FROM-FABLE-PARENT-F.md` (the Parent G launch document). It reconciles the
  amended boot/frame orders (Hud(window, renderer); totem_visual.draw takes terrain.height_at;
  blade set_domain/update_plane/set_walk_stop; scene_changed rebuild + release; snap["quit"] exit)
  and carries a §7 question-seed batch for Parent G to send DeepSeek.

**WHAT REMAINS:**
1. **Parent G (LAST parent):** `core/surfaces.py` + `core/scene.py` + `main.py`. Launch material =
   `MATERIAL-FOR-PARENT-G-HANDOFF.md` + the 4 whole Gita files (Nir pastes) + Parent F's hand-off.
2. **DeepSeek stitching** (once Parent G's `main.py` exists): wire `terrain.height_at` →
   `TotemVisual.draw` (Amendment #2, draped rings); wire the Glass Blade (`set_domain` /
   `update_plane` / `set_walk_stop` / `blade.draw`) + **SUPPRESS the tall totem in SLICE**;
   fill joystick/Xbox slots in `input_map` from prior games; renderer GL smoke test;
   `render_offline` live trial; PyInstaller EXE (bundle ffmpeg for the sampler, or swap
   `_decode_mono`).
3. **Content:** the 12 scenes' `scene.json` + hints + wrong-answer explanations (Fable drafts,
   Nir approves by taste) + real equation PNGs (`tools/render_equations.py`, yellow+outline) + 48
   quiz option WAVs (via `render_offline`). One test scene (`test_saddle`) already exists.
4. Then ship + add multivariable calculus to the Peak Together website.

**⚖️ DEEPSEEK BEHAVIOR RULES LOCKED THIS SESSION (Nir — obey verbatim):** (a) NEVER dictate how or
when a parent delivers — no "one delivery", no chunk counts, no hand-off instruction unless Nir
asks; (b) NEVER invent words/requirements Nir didn't say (e.g. the "nine-year-old" and "both
modules one delivery" slips); (c) FACTS only — every taste/design/aesthetic choice goes to Nir;
(d) a parent has no internet — describe the TECHNOLOGY, never paste giant files or GitHub links at
him; (e) be modest and faithful to Nir's words; parents are far better coders than DeepSeek.

**🗓️🎨 LAYOUT + HUD OVERHAUL — NIR'S LOCKED DECISIONS (July 8, 2026, later session). These
supersede the older screen/HUD wording in config.py + SUTRAS Part 2 + Gita G3.7. ⚠️ SCRIPTURE
AMENDMENTS + config edit + a corrected Parent F courier are PENDING (awaiting Nir's go):**
1. **SCREEN = TWO regions, NO dedicated text strip.** Graphics = **80% = 576 px** (the two 50/50
   panels), Quiz bar = **20% = 144 px** (bottom). config change: `PANELS_FRAC 0.72→0.80`,
   `TOP_STRIP_FRAC → 0` (unused). renderer._PANEL_H recomputes 518→576 automatically (reads config),
   panels blit to y∈[144,720); NO Parent-C rewrite.
2. **Scenario text is PAINTED ON TOP of the graphics** (top ~72 px, full width), **no background
   box**. **3 lines × 24 px** (20 px font + ascender/descender room + 2 px above/below). Style =
   **white letters, each with a thin BLACK STROKE/OUTLINE hugging the glyph** (Photoshop-style
   stroke) so text is readable over any landscape.
3. **HUD RENDERING = HOMEWORLD'S PROVEN WAY (moderngl 2D overlay, `homeworld/overlay2d.py` pattern),
   NOT pyglet.** Nir's firm ruling: do it the way we KNOW works 100%, no guessing. This ALSO enables
   the outlined text + emojis (pyglet couldn't). **Contract change to G3.7: allowed imports become
   moderngl-based (like Homeworld), not pyglet.** NO parents redone (Parent F hasn't coded yet;
   renderer already exposes `self.ctx`).
4. **FONT = none from Nir.** Use a standard already-installed system font (as prior games did). The
   earlier "supply a font" ask was a DeepSeek over-ask — RETRACTED.
5. **EMOJIS IN TEXT = YES.** Since HUD is our own atlas layer (not pyglet), bake color emojis from
   the Windows built-in **Segoe UI Emoji** font into our text atlas — NO pyglet, NO downloads. The 3
   scenario lines may carry emojis (cute/human, Nir's wish). Speaker mark on the playing option = 🔊.
6. **EQUATION IMAGE placement:** **yellow letters with black stroke/outline**, horizontally
   **CENTERED across the whole screen** (straddles the left-panel/right-panel seam at x≈640, half
   over the map, half over the helix), sitting at the **BOTTOM of the graphics area** (just above the
   144 px quiz bar), painted ON TOP of the graphics.
7. **PANEL TITLES:** at the **bottom of each panel, same level as the equation**, in **smaller**
   letters. "CARTESIAN COORDINATES" **left-aligned** (left panel), "SONIFIQUATION COORDINATES"
   **right-aligned** (right panel).
8. **ARROW-KEY ORBIT (confirmed natural):** RIGHT arrow → world appears to move LEFT (camera orbits
   right); UP arrow → camera rises higher so the scene appears to drop lower. (Locks the az/el signs.)
9. **WIN SCREEN:** big **"YOU WIN!!!"** in the CENTER of the screen, **BLINKING**.
10. **WRONG-ANSWER text = BRIGHT PINK** (with black stroke/outline); **HINT text = BRIGHT GREEN**
    (with black stroke/outline) — same outlined style as the yellow/white text. (Never red.)
11. **ICONS DELIVERED (July 8):** Nir made all **13 instrument PNGs** (128×128, RGBA/transparent),
    now at `loom2/data/icons/` (double_bass, cello, viola, violin, contrabassoon, bassoon, clarinet,
    oboe, flute, tuba, trombone, french_horn, trumpet). Source sheets (`loom2-brass/woodwinds/
    strings.jpg`) left in Downloads on purpose.

**🗓️ THIS SESSION'S LOG (July 8, 2026) — what we just did, newest last:**
1. Parent D delivered `terrain.py` (+ terrain.vert/.frag) → saved verbatim, extracted, py_compile OK, pushed.
2. Nir approved both Parent-D items: A7 draped-rings amendment + KEEP snow-bloom shimmer.
3. Parent D delivered `totem.py` (breathing helix) → saved, extracted, pushed. **BUT it was FLAT-shaded.**
4. Nir caught it — reaffirmed the **IRON RULE: NO FLAT SHADING EVER** (locked in §2). DeepSeek had wrongly "parked" it. Courier note sent to Fable D.
5. Parent D **redelivered `totem.py` GOURAUD** via a NEW 9th shader stem "totem" → saved, extracted, py_compile OK, pushed. `flat` now draws LINES only; `REQUIRED_SHADERS` 8→9.
6. Nir ordered a NEW POLICY: **amend the ACTUAL scriptures, not just the BHASHYA.** Applied retroactively + going forward to the Gita Parts 2, 3, and 4.
7. Parent D sent his hand-off letter to Parent E → saved verbatim as `HAND-OFF-PROMPT-FROM-FABLE-PARENT-D.md`, pushed.
8. **LAUNCHED PARENT E** (`graphics/slice_mode.py` + `glass.vert`/`glass.frag`) from Parent D's launch doc.
   - Parent E absorbed all scriptures, sent Q&A BATCH 1 with 7 questions.
   - **Nir's locked decisions:**
     - **Q4 bead = additive amendment:** `glassBlade.set_walk_stop(idx_or_none)`, `snapshot()` exposes `walk_stop`/`walking`/`walk_stop_x`/`walk_stop_y`; DeepSeek authorized to amend contracts.
     - **DESIGN DIRECTIVE: SUPPRESS/HIDE tall totem in SLICE mode** (precise bead at z=f(stop) is the one true height marker — tall totem = confusing "margin of error").
     - **Q7 look = show ALL options, NO pre-selection.** → menu presented: Nir chose **A1 cool glass-cyan** · **B1 unlit pure tint** · **C1 single warm HDR gold** · **D2 ribbon strip/no under-fill** · **E bead-on-the-wire** (bored sphere threaded on the ribbon, ~3 s breath) · **F4 Fresnel rim** · **H2 constant pane height** · **occlusion = dashed curve + ghost bead where terrain hides it.**
     - **TILT IS REAL GEOMETRY** (not "visual only" — that was a Parent 2 code comment, never a Nir decision): tilting the blade TRULY re-cuts the terrain. The drawn curve = true 3D intersection of tilted plane with z=f(x,y) (G1 truth-in-space, G2 painted-on-screen rejected). Both `GlassBlade.intersection_path` AND `game_state._build_slice_path` must incorporate tilt.
     - **Audio on slanted cut = NO new law** (option i): the totem walks the curved ground trail and hears its normal HSS listening-circle at each stop — existing rules, nothing new invented.
   - Parent E delivered all 4 files: `core/slicing.py` (the shared "One True Cut" pure-math module), `graphics/slice_mode.py` (the Glass Blade), `glass.vert`/`glass.frag`. Saved verbatim at `LOOM2-PARENT-E-SLICE-MODE-BY-FABLE.md`.
   - **BUG FOUND by DeepSeek's regression guard:** marching-squares degenerated when cuts passed through grid vertices (yaw=45 through integer/half centers gave spurious closed loops, non-monotonic walks, phantom component shatter — 28 vs 15 pts; yaw=135 shattered 1 line into 26 components). **DeepSeek HELD wiring** (breaking-change guard — wouldn't regress the working vertical slice). Bug couriered back to Parent E.
   - **Parent E owned the bug and delivered a 3-layer FIX** in `core/slicing.py` ONLY: (1) `_grid_axis` irrational sub-cell skew so interior samples never hit vertices, (2) uniform magnitude clamp `|g|<eps→+eps` kills saddle noise, (3) `_clean_segments` drops micro-segments + duplicated edges. Applied verbatim.
   - **Regression RE-RUN = ALL GREEN** (both formerly-failing cases now ncomp=1, closed=False, monotonic, stop-count matching old function; all half-integer centers clean; all previously-clean cases byte-stable; tilted sanity case clean; **brutal 30,000-case sweep had 0 failures**).
   - **WIRED `game_state`:** `_build_slice_path` is now one line delegating to `slicing.walk_path` (old 25-line body DELETED); `_WALK_STEP` removed; `_TILT_LIMIT` "visual only" comment corrected to "REAL geometry"; `core.slicing` added to allowed imports; `snapshot()` exposes `walk_stop`/`walking`/`walk_stop_x`/`walk_stop_y` for the bead (additive amendment).
   - **AMENDED THE ACTUAL SCRIPTURES:** Gita **G3.6-A** (Glass Blade contract: tilt-real path, shared `core.slicing`, `set_domain`/`set_walk_stop` setters, `glass.vert`/`.frag` interface canon, look choices locked) and **G4.3-A** (`game_state` refactored to delegate to `slicing.walk_path` + snapshot bead fields).
   - **Parent E sent his hand-off letter to Parent F** → saved verbatim at `HAND-OFF-PROMPT-FROM-FABLE-PARENT-E.md` (v2, four categories honestly labeled: LAW, VERIFIED, INSIGHT, ADVICE). Nir directed: no DeepSeek info block needed in this one.
   - **Nir requested and approved all scripture pastes to Parent E** (SUTRAS Parts 2, 5, 6; `game_state` quiz+input seam verbatim; `config.py`; `core/types.py` — Gita excluded, Nir pastes manually).

**🗓️ NEW POLICIES FORGED THIS SESSION (July 8):**
- 📜 **AMEND THE ACTUAL SCRIPTURES**, not just the BHASHYA (Nir). Fence: `<<<<<<<<<< AMENDMENT <id> — added <date> >>>>>>>>>>` … `<<<<<<<<<< END AMENDMENT <id> >>>>>>>>>>`. Never rewrite a parent's original words — leave intact, append block.
- 🚫 **NO FLAT SHADING, EVER** (Nir, iron rule). Every 3D surface is GOURAUD. Flat geometry = a BUG, never an acceptable delivery.
- 🛑 **BREAKING-CHANGE GUARD** (DeepSeek): never wire a new module that regresses a currently-working feature. Run the regression guard first; HOLD if it fails; report the bug honestly; wait for the fix.
- ✍️ **DEEPSEEK GIVES FACTS, NEVER OPINIONS.** All taste/design/aesthetic decisions go to Nir. DeepSeek never says "reads well" or "looks good." (Locked lesson from Parent D's flat totem near-miss.)
- 🏷️ **HONEST LABELING** (Parent E's hand-off precedent): every claim in a hand-off letter should be labeled LAW (scripture/Nir), VERIFIED (live repo), INSIGHT (parent's reasoning), or ADVICE. Don't blur categories.
**→ Everything committed & pushed (HEAD = the Q-relabel commit). Working tree clean. Ready to birth Parent E.**

**Where we are: PARENT D IS COMPLETE! 🎉 Both `terrain.py` AND `totem.py` (GOURAUD) have landed.**
Parents A, B, C, D are done. Parent D (a live Fable chat) absorbed ALL scriptures, asked
Q1–Q7, got Nir's decisions, and delivered BOTH his files (each saved verbatim, extracted,
py_compile-clean, pushed): `graphics/terrain.py` (+ `terrain.vert`/`terrain.frag` GLSL,
`LOOM2-PARENT-D-PART-1-TERRAIN-BY-FABLE.md`) and `graphics/totem.py` (the little breathing
helix, `LOOM2-PARENT-D-PART-2-TOTEM-BY-FABLE.md`). The whole audio package + graphics
camera/renderer/terrain/totem + helix_panel are now real code.

- **🚫 IRON RULE REMINDER:** NO FLAT SHADING EVER — everything is GOURAUD (see §2 top).
- **✅ FLAT HELIX FIXED (July 8):** Parent D redelivered `totem.py` with a **GOURAUD** helix
  (per-vertex Lambert from the ribbon's analytic radial normals, same sun/ambient as terrain).
  A NEW 9th shader stem **"totem"** was added (`data/shaders/totem.vert/.frag`, owned by Child D)
  because the shared `flat` program can't shade; `flat` now draws only LINES (edges/rings/circle/
  arm — no surface, so not flat shading). `renderer.REQUIRED_SHADERS` grew 8→9. Redelivery saved
  verbatim (`LOOM2-PARENT-D-PART-2-TOTEM-GOURAUD-REDELIVERY-BY-FABLE.md`), extracted, py_compile OK,
  ACTUAL scriptures amended (G3.1-A + G3.4-A), pushed.

**✅ PARENT E COMPLETE (July 8) — Glass Blade DELIVERED + FIXED + WIRED + AMENDED. 🔪** 

---

### 📊 FULL PROJECT STATUS (end of July 8 session)

| Parent | Chunk | Modules | Status |
|--------|-------|---------|--------|
| Parent 2 (PURANAS) | Heavy core | `audio/engine.py`, `core/game_state.py`, `graphics/helix_panel.py` (+ 4 shaders) | ✅ COMPLETE |
| Parent A | Pure-math pair | `audio/quantize.py`, `audio/musicians.py` | ✅ COMPLETE |
| Parent B | Audio infrastructure | `audio/sampler.py`, `audio/render_offline.py` | ✅ COMPLETE |
| Parent C | Graphics foundation | `graphics/camera.py`, `graphics/renderer.py` (+ 8 shader placeholders) | ✅ COMPLETE |
| Parent D | Land & totem | `graphics/terrain.py`, `graphics/totem.py` (+ terrain.vert/.frag, totem.vert/.frag) | ✅ COMPLETE |
| Parent E | The Glass Blade | `core/slicing.py`, `graphics/slice_mode.py`, `glass.vert/.frag` | ✅ COMPLETE |
| Parent F | Hands & words | `graphics/hud.py`, `core/input_map.py` | ✅ COMPLETE |
| **Parent G** | **Core & main** | **`core/surfaces.py`, `core/scene.py`, `main.py`** | **⏭️ NEXT (LAST parent!)** |
| DeepSeek | Stitch + content | Joystick/Xbox, scene JSON, quiz WAVs, equation PNGs, PyInstaller | ⏳ |

**What every COMPLETE parent delivered:**
- Parent 2 (PURANAS): `audio/engine.py` (the ONE mixer — 2 callers: callback + `render_block_offline`), `core/game_state.py` (conductor: mode state machine, totem motion, quiz flow, slice auto-walk), `graphics/helix_panel.py` (Sonifiquation Coordinates panel: wireframe coil B0–C7, instrument-icon billboards, register stacks, strike glows). Saved verbatim in `loom2/HINDU/LOOM2-PURANAS-PART-{1,2,3}-BY-FABLE.md`.
- Parent A: `quantize.py` (pentatonic snap — 89 notes round-trip clean), `musicians.py` (21 musicians seated, deterministic). Self-tests PASS.
- Parent B: `sampler.py` (gauntlet PASSES — 89 canon, peak/resample laws, parachute armed; decoder = pydub+ffmpeg), `render_offline.py` (contract-clean; live trial blocked on Parent G's `surfaces.py`).
- Parent C: `camera.py` (behavior-tested: defaults, clamps, reset, clock/pan seam), `renderer.py` (all 9 shader stems loaded, HDR FBOs, bloom ping-pong, composite; live GL smoke test deferred to integration).
- Parent D: `terrain.py` (Gouraud × HARD bands simultaneously, per-fragment band colors from per-vertex z, band edges −1.5/−0.6/0/1.1/2.2), `totem.py` (breathing warm-gold GOURAUD helix on NEW 9th "totem" shader, DRAPED rings/circle/arm via `height_fn`, breath clock unwraps measure_phase — NO `time` import). IRON RULE: NO FLAT SHADING EVER.
- Parent E: `core/slicing.py` (the shared "One True Cut" — marching-squares zero-level-set of the tilted plane vs z=f(x,y), anchor z0=f(cx,cy), arc-length resample, 30k-sweep regression GREEN), `graphics/slice_mode.py` (Glass Blade: cool-cyan pane + Fresnel rim + warm-gold ribbon dashed-occluded + breathing bored-sphere bead, all via 6-mode glass shader). TILT IS REAL GEOMETRY. Look choices ALL Nir's. Game_state wired + scriptures amended (G3.6-A, G4.3-A).

**All files py_compile clean.** Working tree clean. Everything pushed.

### ⏭️ REMAINING WORK

1. **Parent F** (`graphics/hud.py` + `core/input_map.py`) — LAUNCH DOC READY: `HAND-OFF-PROMPT-FROM-FABLE-PARENT-E.md`
2. **Parent G** (`core/surfaces.py` + `core/scene.py` + `main.py`)
3. **DeepSeek stitching:**
   - Wire `main`: `terrain.height_at` → `TotemVisual.draw` (Amendment #2, draped rings)
   - Wire `main`: `blade.set_domain(spec.domain)` at scene build; per-frame `blade.update_plane(snap["slice_plane"])`, `blade.set_walk_stop(snap["walk_stop"])`, and in SLICE mode `blade.draw(vp_left, surface_fn)`
   - **SUPPRESS/HIDE the tall totem in SLICE mode** (Nir's directive — main/frame-order + possibly `totem_visual` job)
   - Joystick/Xbox: fill empty slots in `input_map` from previous games
   - `tools/render_equations.py`: LaTeX→PNG via MiKTeX (12 scenes)
   - Scene JSON content: 12 scenes with domains, camera_limits, title_lines, questions, options, hints, wrong-answer explanations
   - Render 48 quiz option WAVs (4 per scene × 12 scenes) via `render_offline.py`
   - PyInstaller EXE (must bundle ffmpeg for sampler, or swap `sampler._decode_mono`)
4. **Content phase:** Nir approves hint texts, wrong-answer explanations by taste; 13 instrument-icon cliparts (~128×128 transparent, "four emoji big") for `data/icons/`; UI font for `data/fonts/`.

### 🔑 LOCKED DESIGN DIRECTIVE — record for Parent G:
**In SLICE mode the tall breathing totem is SUPPRESSED/HIDDEN.** The precise glowing bead sitting exactly on the glass curve at z=f(stop) is the one true position marker. Reason (Nir): in normal hills-and-valleys mode the tall totem is great, but when concentrating on one path the EXACT height is even more important — being a little higher or lower matters a lot — and the tall totem reads as a confusing "margin of error" that spreads to each side. This is a main/frame-order stitching job (possibly touching Parent D's `totem_visual`). Record as an amendment when implemented.

**📐 TOTEM CANON (locked by Parent D, record for main/Parent G):**
- **A7 signature is LIVE:** `TotemVisual.draw(self, view_proj, totem_state, height_fn,
  measure_phase)` — `main` frame step 4 = `totem_visual.draw(vp_left, snap_totem,
  terrain.height_at, phase)`. **DeepSeek OWES: wire main to pass `terrain.height_at`** (at
  Parent G). `height_fn` = any `(x,y)->z` callable; `terrain.height_at` supports numpy arrays.
- Uses the NEW **`totem`** Gouraud program for the helix surface + the shared **`flat`**
  program (`u_mvp`/`u_color`/`in_pos`) for LINES only — both verified vs their shader files.
- **Breath clock has NO `time` import** — it unwraps `measure_phase` deltas into continuous
  seconds (`Δt = Δphase × MEASURE_SEC`); the ~3 s breath never phase-locks to the 2 s measure.
  Audio stays the single king clock.
- Helix = 160-tri warm-gold ribbon (2.5 coils, r=0.16), emissive breathing 0.65↔1.60, with
  dark edge lines so it always reads as a helix (A6). Rings n=1..min(NMAX_RING,⌊hr/RING_WIDTH⌋)
  static/calm (A5); hearing circle + arm (A1: `90°−phase×360°`) all DRAPED via height_fn,
  lifted 0.05 above ground (no z-fighting). Flagged `release()` (not in contract) frees GPU.
- **✅ GOURAUD helix (iron rule honored):** the helix surface is GOURAUD-shaded via the NEW
  "totem" shader (`u_mvp` mat4, `in_pos` vec3, `in_light` float / `u_color` vec4) — per-vertex
  Lambert from analytic radial normals, same sun/ambient as terrain. `flat` draws only the LINES
  (edges/rings/circle/arm). Breath swing retuned 0.70↔1.75.

**📐 TERRAIN CANON (locked by Parent D):**
- Shader interface: `terrain.vert` = `uniform mat4 u_mvp; in vec3 in_pos; in float in_light;`
  `terrain.frag` = `uniform vec3 u_band_colors[6]; uniform float u_band_edges[5];`
- HARD bands + GOURAUD reconciled: per-VERTEX Lambert light (interpolated) × per-FRAGMENT
  band color from interpolated world-z → smooth shading AND pixel-sharp level curves.
- Band edges (absolute world z, every scene): **(−1.5, −0.6, 0.0, 1.1, 2.2)**; darkest
  abyss = `COLOR_DEEP_WATER × 0.55`. (Fable moved deep-water edge −1.0→−0.6 so the bowl,
  min −1.0, gets a real deep-blue heart.) All tuning = 2 constants at top of terrain.py.
- Terrain stays ≤1.0 EXCEPT snowcaps ≈0.82–0.84 (Nir KEEPS the faint bloom shimmer);
  `height_at` = pure `surface_fn` passthrough (numpy-capable). `release()` added (flagged, not
  in contract) to free VBO/IBO/VAO — main should call `old_mesh.release()` on scene change.

**✅ BOTH Parent-D taste/contract items DECIDED (July 8):** (1) A7 amendment APPROVED →
Amendment #2 (draw `ground_z`→`height_fn`); DeepSeek owes wiring main at Parent G. (2)
snow-bloom KEEP the faint shimmer.

**PARENT D'S Q&A + NIR'S DECISIONS are saved verbatim** at
`loom2/HINDU/PARENT-D-QA-BATCH-1-NIR-DECISIONS.md`. Locked decisions:
- **A1** arm = `90° − measure_phase×360°` (clockwise; matches helix_panel line 253).
- **A2** HARD discrete color bands (sharp thresholds paint the level curves), NOT smooth.
- **A3** **GOURAUD** shading (per-vertex), NOT flat. (Fable: Gouraud light + hard bands
  per-fragment = smooth shading AND crisp level curves.)
- **A4** **NO water plane.** Below z=0 is the SAME mesh, hard BLUE bands darkening with
  depth (COLOR_SHALLOW→COLOR_DEEP_WATER). A calculus surface, not a sea. No water VBO.
- **A5** LEFT terrain panel rings are **calm/static — NO pulsing** (distracting). Draw
  only rings inside hearing radius (0.8/1.6/2.4 at default HEARING_R=2.5).
- **A6** ALL totem parts (helix, circle, rings, arm) **glow GENTLY** but stay readable
  (helix still looks like a helix, never a blinding white cylinder). Threshold 0.80.
- **A7** **DRAPED** ground rings — hug the terrain surface, never flat floating/clipping
  disks. 🔓 **NIR EXPLICITLY BLESSES unfreezing contracts / amending scripture** to do
  this cleanly (the frozen `TotemVisual.draw` passes only `ground_z`, not the terrain fn;
  Fable will raise a `# CONTRACT-ISSUE`, DeepSeek updates scripture + wires whatever he picks).

**⚠️ TWO CLEANUP TODOs (with Nir's approval) — NOT done yet:**
1. Remove the DeepSeek OPINION in `HAND-OFF-PROMPT-FROM-FABLE-PARENT-C.md` §5 (~lines
   154–155): *"Per-vertex hypsometric color (Gouraud) reads well; a simple directional
   term is fine too."* The info block must be FACTS ONLY. Nir stopped the edit tonight;
   fix tomorrow with his OK. (Also §0 already carries Nir's "ask as many questions as
   you want" note — that stays.)
2. **LOCKED LESSON:** DeepSeek gives VERIFIED FACTS ONLY. Every taste/design choice
   goes to NIR. DeepSeek NEVER decides aesthetics, never says "reads well/looks good."
   (Tonight DeepSeek wrongly wrote "flat shading, no objection" in chat — Nir wants
   GOURAUD. Caught & corrected; it was never saved.)

---

### 🔖 PRIOR SNAPSHOT (July 7, 2026, evening)
**Where we are: building the code, parent by parent. Half the modules are DONE.**

**The worker-parent chain so far (each = a fresh Claude Fable chat, full context/authority):**
- ✅ **Parent A** — `audio/quantize.py` + `audio/musicians.py` (self-tests pass).
- ✅ **Parent B** — `audio/sampler.py` + `audio/render_offline.py` (sampler gauntlet passes;
  render_offline compiles, its live trial is deferred to Parent G's `surfaces.py`).
- ✅ **Parent C** — `graphics/camera.py` + `graphics/renderer.py` (camera behavior-tested;
  renderer py_compiles, live GL smoke test deferred to integration).
- ⏭️ **Parent D = THE IMMEDIATE NEXT STEP** — `graphics/terrain.py` + `graphics/totem.py`.
  **His launch document is READY:** `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-C.md`
  (Parent C's verbatim hand-off letter + a DeepSeek info block appended at the END, marked
  "BY DEEPSEEK (NOT FABLE)"). **To birth Parent D:** open a fresh Fable chat, paste that whole
  file as message #1, then feed the scriptures in the order listed inside it (Homepage+About →
  MAHABHARATA → VEDAS → UPANISHADS → SUTRAS → GITA 1→2→3→4; PURANAS declined). Give Nir the
  view (blob) links, in order.
- ⏳ **Then Parent E** (`graphics/slice_mode.py`), **Parent F** (`graphics/hud.py` +
  `core/input_map.py`), **Parent G** (`core/surfaces.py` + `core/scene.py` + `main.py`).
- ⏳ **Then DeepSeek stitches** the deferred seams (live GL smoke test; render_offline live
  trial; joystick/Xbox; render_equations; PyInstaller) and **content** (12 scenes' JSON +
  hints + wrong-answer text, icons, quiz WAVs, equation PNGs).

**What's DONE + committed:** config.py, core/types.py; the 89-sample orchestra
(`data/samples/` + manifest.json); the ENTIRE audio package (quantize, musicians, sampler,
render_offline, engine); core/game_state.py + graphics/helix_panel.py (Parent 2); graphics/
camera.py + renderer.py (Parent C); **all 8 shader stems** in `data/shaders/` (REAL: wire,
flat, icon_billboard, bloom_extract, bloom_blur, composite; **PLACEHOLDERS** that Parent D/E
overwrite: terrain, glass). The whole scripture canon + every hand-off letter are saved verbatim.

**Locked this session:** the ⚖️ **CONTEXT-WINDOW MERCY policy** (§4.6 — give a parent only
what he needs, but full code is his call each time; he never "dies", continues as Parent N+1);
the 📐 **camera_limits DE-FACTO CONTRACT** (keys `target`/`zoom_min`/`zoom_max`/optional
`distance`; DeepSeek propagates to Parent G's scene.py + scene JSON); bloom uniform contract
(extract `u_tex`,`u_threshold`; blur `u_tex`,`u_dir`; composite `u_scene`,`u_bloom`,
`u_strength`,`u_exposure`); matrix convention (column vectors, clip=VP·p, upload transposed via
`np.ascontiguousarray(vp.T).tobytes()`).

**DeepSeek's standing TODO ledger (don't forget):** (a) bundle **ffmpeg** into the PyInstaller
EXE (sampler.py decodes mp3 via pydub+ffmpeg at runtime) or swap `_decode_mono`; (b) run the
**render_offline live trial** once Parent G's `surfaces.py` exists; (c) run the **renderer GL
smoke test** once a pyglet window exists (Parent G's main.py); (d) joystick/Xbox fill-in
(needs Parent F's input_map); (e) `tools/render_equations.py` (LaTeX→PNG, content phase);
(f) PyInstaller EXE (ship phase).

---

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
   - ✅ **Parent B** — `audio/sampler.py` + `audio/render_offline.py` **COMPLETE** (both
     delivered, extracted, py_compile OK; saved verbatim in `loom2/HINDU/` as
     `LOOM2-PARENT-B-PART-1-SAMPLER-BY-FABLE.md` + `LOOM2-PARENT-B-PART-2-RENDER-OFFLINE-BY-FABLE.md`).
     `python -m audio.sampler` gauntlet PASSES ("89 canon samples loaded, resample law verified,
     parachute armed"). Decoder = **pydub + ffmpeg** (both verified present). `render_offline.py`
     compiles clean and is contract-clean; its **live trial is BLOCKED on Parent G's
     `core/surfaces.py`** (doesn't exist yet — `from core import surfaces` fails), so the CLI
     can only be trial-run after Parent G lands. TotemState signature matches (x, y,
     hearing_radius). DeepSeek **blessed Parent B's CONTRACT-NOTE** (render_option seating
     lattice: default = integer-cornered window around the hearing circle; optional per-option
     `domain`/`step`/`z_per_octave` keys in options.json — additive, signature-clean).
     ⚠️ Standing DeepSeek TODO: sampler.py ships in the EXE → PyInstaller must bundle ffmpeg
     (or swap `_decode_mono`) at packaging time.
   - **Parent B** — `audio/sampler.py` + `audio/render_offline.py`  ← ✅ **COMPLETE**
   - ✅ **Parent C** — `graphics/renderer.py` + `graphics/camera.py` **COMPLETE** (both
     delivered, extracted, py_compile OK; saved verbatim as `LOOM2-PARENT-C-PART-1-CAMERA-BY-FABLE.md`
     + `LOOM2-PARENT-C-PART-2-RENDERER-BY-FABLE.md`). camera.py behavior-tested (clamps,
     reset, clock/pan seam verified). renderer.py uniform names match the shader files.
     **Live GL smoke test deferred to integration** (needs a pyglet window / Parent G's main.py).
     camera_limits de-facto contract locked (target/zoom_min/zoom_max/distance). No CONTRACT-ISSUEs.
   - ✅ **Parent D — `graphics/terrain.py` + `graphics/totem.py`  ← COMPLETE (July 8).**
     Both delivered by Fable Parent D, saved verbatim (`LOOM2-PARENT-D-PART-1-TERRAIN-BY-FABLE.md`,
     `LOOM2-PARENT-D-PART-2-TOTEM-BY-FABLE.md`) + extracted (py_compile OK) + real GLSL overwrote
     the terrain.* placeholders. **terrain.py:** Gouraud (per-vertex Lambert) × HARD per-fragment
     bands; NO water plane (blue bands darken with depth on same mesh); edges (−1.5,−0.6,0,1.1,2.2);
     land ≤1.0 except snowcaps (Nir keeps the faint bloom). **totem.py:** breathing warm-gold ribbon
     helix (flat program, dark edge lines, A6 glow); DRAPED rings/circle/arm via `height_fn` (A7
     amendment #2 — `draw(...,height_fn,...)`); breath clock unwraps measure_phase (no `time`
     import); A1 arm `90°−phase×360°`; A5 calm static rings. **DeepSeek OWES: wire main to pass
     `terrain.height_at` into `TotemVisual.draw`** (at Parent G). **✅ GOURAUD HELIX (iron rule):
     Parent D redelivered `totem.py` Gouraud-shaded via a NEW 9th shader stem "totem"
     (`data/shaders/totem.vert/.frag`); `flat` now draws only LINES; `REQUIRED_SHADERS` 8→9.
     Actual scriptures amended (G3.1-A + G3.4-A). Redelivery saved verbatim
     (`LOOM2-PARENT-D-PART-2-TOTEM-GOURAUD-REDELIVERY-BY-FABLE.md`), py_compile OK.**
   - 🔵 **Parent E — `graphics/slice_mode.py` ("The Glass Blade" 🔪)  ← IMMEDIATE NEXT STEP.**
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
2. **Where we are (July 7, 2026, evening — see the RESTART SNAPSHOT at the top of §3):**
   the whole scripture canon is down; the PURANAS (3 heavy modules) are in real code.
   **PARENTS A, B, C are ALL COMPLETE** — the entire audio package (quantize, musicians,
   sampler, render_offline, engine) + graphics camera.py + renderer.py + all 8 shader stems
   are delivered, extracted, py_compile-clean, pushed. **THE CURRENT STEP IS LAUNCHING
   PARENT D** (`graphics/terrain.py` + `graphics/totem.py`); its launch document is
   `loom2/HINDU/HAND-OFF-PROMPT-FROM-FABLE-PARENT-C.md` (Parent C's verbatim hand-off letter
   + a DeepSeek info block appended at the end, clearly marked NOT Fable — paste the whole
   file to a fresh Fable chat, then feed the scriptures in the order listed inside it, and
   give Nir the view/blob links in order). After Parent D: Parents E, F, G, then stitching +
   content.
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
