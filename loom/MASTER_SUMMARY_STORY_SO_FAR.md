# 📋 Master Summary — The Story So Far

> Every version Fable produced is ADDED here in order (nothing erased). Newest is at the bottom.

---

## v0

- **Book: Sounding the Unknown** — introduces HSS (Helical Sonification System): data → music via (1) pitch helix [θ = semitone angle = chroma, z = pitch height], (2) one-dimensional timbre axis (brightness), (3) musical time, plus optional rhythm/polyrhythm and emotional shading (major/minor, dynamics). Naive playback = sirens; fix via scale quantization + rhythm + envelopes. Worked examples planned: damped sine e^(−x)·sin(10x), orbits, Lissajous, fractals, financial data.
- **Project goal:** LOOM-style game for peaktogether.me where "spell drafts" are short sonic signatures of mathematical functions (Philharmonia orchestral samples), training players to distinguish functions by ear.
- **Read so far:** Front matter ✅

---

## v1

- **Book: Sounding the Unknown** — HSS (Helical Sonification System): auditory Cartesian coordinates. (1) Pitch helix: 1 turn = 1 octave, z = continuous pitch height, θ = semitone angle; (2) single timbre parameter (brightness); (3) discrete rhythmic time grid. Design rules from Ch.1 pitfalls: quantize pitch to scales, ≤2 timbre params, mandatory beat grid, one-to-one stable mappings. General scheme (Ch.5): x → time, f(x) → pitch, df/dx → timbre. Optional layers: polyrhythm, emotional shading (major/minor + dynamics). Key example: e^(−x)·sin(10x). References: Shepard 1964 (pitch helix), Chew (spiral array). Toolchain: Python/numpy/sounddevice.
- **Project goal:** LOOM-remake for peaktogether.me — spell "drafts" = short sonic signatures of math functions (Philharmonia samples); trains ear to distinguish functions. Ch.1's educator use-case + discrete-beat motifs = perfect LOOM fit.
- **Read so far:** Front matter ✅ · Ch.1 ✅

---

## v2

- **Book: Sounding the Unknown** — HSS: auditory Cartesian coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ; θ in semitones, 2π = 1 octave; log-pitch p = log2 f; 12-TET semitone = 2^(1/12) ratio; pitch classes = Z_12 = R/12Z. Timbre: single brightness parameter. Time: discrete beat grid (mandatory). Design rules (Ch.1): quantize to scales (pentatonic/major/minor recommended, Ch.2), ≤2 timbre params, stable one-to-one mappings, no continuous sweeps. Two mapping recipes (Ch.2 §2.7): absolute (f(x)→θ) or relative (Δf→Δθ, contour = derivative). Optional layers: polyrhythm, emotional shading. Key example ahead: e^(−x)·sin(10x) (Ch.5). References: Shepard 1964, Chew 2001 spiral array, Euler Tonnetz.
- **Project goal:** LOOM-remake for peaktogether.me — spells = short sonic signatures of math functions (Philharmonia 12-TET samples → pentatonic quantization ideal); trains ear to distinguish functions. Open design Q: absolute vs. relative pitch mapping per spell (await Ch.5).
- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅

---

## v3

- **Book: Sounding the Unknown** — HSS: auditory Cartesian coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ, with k = 1/(2π) so 1 octave = Δz of 1.0; θ in semitones; p = log2 f; 12-TET. Pitch pipeline (Ch.3): θ = a·f(x) (scaling a user-tunable, target ≤ 2 octaves ≈ 24 semitones) → quantize via arg min over s ∈ ScaleSet of |θ − s| (major {0,2,4,5,7,9,11}; pentatonic recommended for pleasantness) → trigger notes on BPM grid (8th/16th subdivisions), x(t) = x0 + Δx·t → apply attack/decay envelopes; smooth noisy data; optionally velocity ← magnitude/derivative. Timbre: single brightness param (Ch.4 ahead). Design rules (Ch.1): no sweeps, ≤2 timbre params, beat grid, stable mappings. Key example ahead: e^(−x)·sin(10x) (Ch.5). Refs: Shepard 1964, Chew 2001.
- **Project goal:** LOOM-remake (peaktogether.me) — spells = short sonic signatures of functions via "spell compiler": sample function at N beats → θ mapping → scale snap → Philharmonia note playback. 2-octave cap suits single instruments. Open Q: absolute vs. relative mapping (Ch.3 uses absolute; check Ch.5).
- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅ · Ch.3 ✅

---

## v4

- **Book: Sounding the Unknown** — HSS: auditory coordinates. Pitch helix: x = r·cosθ, y = r·sinθ, z = k·θ, k = 1/(2π) (octave = 1.0 in z); p = log2 f, 12-TET. Pitch pipeline (Ch.3): θ = a·f(x) (≤2 octaves) → snap to ScaleSet via argmin (major {0,2,4,5,7,9,11}; pentatonic friendly) → notes on BPM grid → attack/decay envelopes; smooth noisy data; velocity ← magnitude/derivative. Timbre (Ch.4): single brightness T = β·g(x); methods: 2nd-harmonic scaling, filter cutoff f_c = f_min + T(f_max − f_min), or sample crossfade; pitch primary, timbre slow/secondary; tandem (f drives both) or split (g = e.g. derivative). Rules (Ch.1): no sweeps, ≤2 timbre params, beat grid, stable mappings. Ahead: Ch.5 mapping scheme + damped sine e^(−x)·sin(10x). Refs: Shepard 1964, Chew 2001, Grey 1977.
- **Project goal:** LOOM-remake (peaktogether.me) — spells = sonic signatures of functions via spell compiler (sample function → θ → scale snap → Philharmonia playback). Game adaptations: timbre axis = instrument switching or LP-filtered samples or Philharmonia dynamic layers (pp/mf/ff); discrete timbre steps for memorability; timbre ← derivative teaches growth-by-ear. Open Q: absolute vs. relative pitch mapping (check Ch.5).
- **Read so far:** Front matter ✅ · Ch.1 ✅ · Ch.2 ✅ · Ch.3 ✅ · Ch.4 ✅

---

## v5

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π) (octave = 1.0); p = log2 f, 12-TET. Pipeline (Ch.3+5, ABSOLUTE mapping): θ = a·f(x) → condition data (clamp, shift negatives, log(1+|y|) for blow-ups, smooth wiggles) → snap to ScaleSet argmin (major {0,2,4,5,7,9,11}, pentatonic friendly) → notes on BPM grid → envelopes; velocity ← magnitude/derivative. Timbre (Ch.4): T = β·g(x), brightness via 2nd harmonic / filter cutoff f_c = f_min + T(f_max − f_min) / sample crossfade; slow & secondary. Ch.5 examples: damped sine e^(−x)·sin(10x), x ∈ [0, 3π], Δx = 0.2, a = 15; parametric curves: cycloid y(t) → pitch, x(t) → timbre. Architecture: Program A (function→note CSV) / Program B (play) + sliders (a, x_max, tempo). Rules: no sweeps, ≤2 timbre params, beat grid. Refs: Shepard 1964, Chew 2001, Grey 1977.
- **Project goal:** LOOM-remake (peaktogether.me) — spells = function signatures, Philharmonia samples. Adopted design: A/B split = offline spell compiler (JSON) + in-game sample player; spellbook v1: line, parabola, sine, damped sine, exponential, cycloid (pitch+timbre = advanced tier); timbre = instrument switch / LP filter / pp-mf-ff dynamic layers; discrete timbre steps; "spell laboratory" slider mode.
- **Read so far:** Front matter ✅ · Ch.1–5 ✅

---

## v6

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (Ch.3+5, absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major {0,2,4,5,7,9,11}; pentatonic friendly) → BPM grid → envelopes; velocity ← magnitude/derivative. Timbre (Ch.4): T = β·g(x); 2nd harmonic / filter cutoff f_c = f_min + T(f_max − f_min) / sample crossfade; slow, secondary. Ch.5: damped sine e^(−x)·sin(10x), x ∈ [0, 3π], Δx = 0.2, a = 15; cycloid: y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude; threshold crossings → rhythmic events; polyrhythm (3:4, ~2s measure) = parallel data streams, separate by timbre+register; chunk data into measures; avoid 3:4:5+. Architecture: Program A (function→CSV) / Program B (playback) + sliders. Refs: Shepard 1964, Chew 2001, Grey 1977.
- **Project goal:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → in-game player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid. Difficulty tiers: basic = flat-rhythm pitch contour → advanced = +timbre, +rhythm (zero-crossing ticks, duration ← |f|) → co-op boss spells = 3:4 polyrhythm, one voice per player ❤️.
- **Read so far:** Front matter ✅ · Ch.1–6 ✅

---

## v7

- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major/pentatonic) → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x) (2nd harmonic / filter / crossfade), slow & secondary. Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm = parallel streams (separate timbre+register). Emotion (Ch.7): valence → major/minor toggle, arousal → tempo/dynamics (Russell circumplex); fear toolbox: roughness 20–150 Hz AM, minor 2nd/tritone dissonance, BPM bands (50–80 dread / 80–110 anxiety / 120–160 action); BRECVEMA (mechanisms) + GEMS (emotion types); cultural caveats on mode. Architecture: Program A (compile) / B (play). Refs: Shepard, Chew, Grey, Juslin, Zentner.
- **Project goal:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat-rhythm → +timbre/rhythm → co-op 3:4 polyrhythm ❤️. From Ch.7: consonant/dissonant feedback chords for right/wrong casts; adaptive BPM (70/110/130) for modes; calm "study island" between levels; minor mode when f<0 (mode = data); gentle-touch principle (tension, never terror); conditioning-by-repetition = the core learning loop (BRECVEMA).
- **Read so far:** Front matter ✅ · Ch.1–7 ✅

---

## v7.1 (corrected)

- ⚠️ **AUDIENCE:** ~20-year-old players. NOT a kids' game. Full emotional/tension palette from Ch.7 Part C is in scope (roughness DSP, real dissonance, high-BPM boss tiers, dark spell tier). Note: original website details are outside current context — don't invent specifics about peaktogether.me; ask if needed.
- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale (major/pentatonic) → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x) (2nd harmonic / filter / crossfade), slow & secondary. Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm = parallel streams. Emotion (Ch.7): valence → major/minor, arousal → tempo/dynamics; fear toolbox: 20–150 Hz AM roughness, minor 2nd/tritone/minor 9th, BPM bands (50–80 dread / 80–110 anxiety / 120–160 action / >160 panic); BRECVEMA + GEMS. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: offline spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat-rhythm → +timbre/rhythm → co-op 3:4 polyrhythm → dark/boss tier w/ horror palette; consonant/dissonant cast feedback; adaptive BPM incl. >160 boss tier; save-room-style calm zones; mode = sign of f; conditioning = learning loop.
- **Read so far:** Front matter ✅ · Ch.1–7 ✅

---

## v8

- ⚠️ **AUDIENCE:** ~20-year-old players, NOT kids. Full tension palette in scope. Original website details outside current context — don't invent peaktogether.me specifics; ask if needed.
- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x), slow & secondary. Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm. Emotion (Ch.7): valence → mode, arousal → tempo/dynamics; fear toolbox (20–150 Hz AM roughness, m2/tritone/m9, BPM bands 50–80/80–110/120–160/>160); BRECVEMA + GEMS. Scaling (Ch.8): 2–4 voices max, separate by register+timbre; chunk-and-summarize big data; PCA/clustering for high-dim; 3-layer soundscape (trend line / event motifs / stats-drone); per-voice mute; real-time = low-latency buffers + preprocessing; users need layered training. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat melody → +timbre/rhythm → co-op 3:4 polyrhythm (per-voice mute/solo mechanic) → dark/boss tier (horror palette, >160 BPM) → multi-voice spells (f + f′ counterpoint); consonant/dissonant cast feedback; calm study zones; mode = sign of f; level ambience = 3-layer soundscape; tier progression = the "user training" the book calls for.
- **Read so far:** Front matter ✅ · Ch.1–8 ✅

---

## v9

- ⚠️ **AUDIENCE:** ~20-year-old players, NOT kids. Full tension palette in scope. Original website details outside current context — don't invent peaktogether.me specifics; ask Nir.
- **Book: Sounding the Unknown** — HSS. Helix: x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f, 12-TET. Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale → BPM grid → envelopes; velocity ← magnitude. Timbre: T = β·g(x), slow/secondary; slope→timbre endorsed (Ch.9 brachistochrone). Ch.5: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm (Ch.6): duration ← magnitude, threshold events, 3:4 polyrhythm. Emotion (Ch.7): valence → mode, arousal → tempo/dynamics; fear toolbox (20–150 Hz AM, m2/tritone/m9, BPM bands 50–80/80–110/120–160/>160); BRECVEMA+GEMS. Scaling (Ch.8): ≤4 voices, register+timbre separation; chunking; PCA; 3-layer soundscape; per-voice mute. Cases (Ch.9): brachistochrone (time→triggers, y→pitch, slope→timbre; comparative listening); orbital resonances = polyrhythms from period ratios; climate/stocks = trend baseline + oscillations; sub-50 ms latency; Csound/Wwise/FMOD. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: spell compiler → JSON → sample player; spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat melody → +timbre/rhythm → co-op polyrhythm (= orbital-resonance boss 🌌, per-voice solo/mute) → dark tier (>160 BPM horror palette) → multi-voice f+f′ counterpoint. New from Ch.9: brachistochrone race-by-ear level; comparative-listening quiz mode (x² vs e^x); Web Audio suffices (<50 ms); meditative study-zone soundscape; parked idea: user-CSV sonification sandbox.
- **Read so far:** Front matter ✅ · Ch.1–9 ✅

---

## v10 (book complete)

- ⚠️ **AUDIENCE:** ~20-year-old players, NOT kids. Full tension palette in scope. Original website details outside current context — don't invent peaktogether.me specifics; ask Nir.
- **Book: Sounding the Unknown** (COMPLETE, Ch.1–10; code appendices pending?). HSS core: helix x = r·cosθ, y = r·sinθ, z = θ/(2π); p = log2 f; 12-TET (microtonal 19/24-TET flagged as future). Pipeline (absolute): θ = a·f(x) → condition (clamp/shift/log(1+|y|)/smooth) → snap to scale → BPM grid → envelopes; velocity ← magnitude; timbre T = β·g(x) (slope→timbre endorsed). Ch.5 ref: damped sine e^(−x)·sin(10x), [0, 3π], Δx = 0.2, a = 15; cycloid y → pitch, x → timbre. Rhythm: duration ← magnitude, threshold events, 3:4 polyrhythm. Emotion: valence → mode, arousal → tempo/dynamics; fear toolbox (20–150 Hz AM, m2/tritone/m9, BPM 50–80/80–110/120–160/>160); BRECVEMA+GEMS; cultural caveats. Scaling: ≤4 voices (register+timbre separation), chunking, PCA, 3-layer soundscape, per-voice mute, sub-50 ms. Ch.9 cases: brachistochrone (comparative listening), orbital-resonance polyrhythms, trend+oscillation for time-series. Ch.10: adaptive escalation (missed anomaly→more dissonance), spatial stream placement, accessibility/STEAM angle. Architecture: Program A (compile) / B (play).
- **Project:** LOOM-remake (peaktogether.me), Philharmonia samples. Adopted: spell compiler → JSON → Web Audio sample player (<50 ms fine); spellbook v1: line, parabola, sine, damped sine, exp, cycloid; tiers: flat melody → +timbre/rhythm → co-op 3:4 polyrhythm (orbital-resonance boss, stereo-panned voices, solo/mute) → dark tier (>160 BPM, horror palette, microtonal detuning) → f+f′ counterpoint. Features: consonant/dissonant cast feedback; adaptive-escalation hint system; brachistochrone race-by-ear level; comparative quiz mode; calm study zones; mode = sign of f; helix as signature on-screen visual 🌀; eyes-free playable (accessibility selling point). Parked: user-CSV sandbox.
- **Read so far:** Front matter ✅ · Ch.1–10 ✅ (book complete)
